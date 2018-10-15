result = IDFactory.getDefault().makeID(XMPPID.PROTOCOL, new Object[] { name });

/*******************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.provider.xmpp.container;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Vector;

import org.eclipse.ecf.core.ISharedObject;
import org.eclipse.ecf.core.ISharedObjectConfig;
import org.eclipse.ecf.core.ISharedObjectContext;
import org.eclipse.ecf.core.SharedObjectInitException;
import org.eclipse.ecf.core.events.ISharedObjectActivatedEvent;
import org.eclipse.ecf.core.events.ISharedObjectContainerDepartedEvent;
import org.eclipse.ecf.core.events.ISharedObjectContainerJoinedEvent;
import org.eclipse.ecf.core.events.ISharedObjectDeactivatedEvent;
import org.eclipse.ecf.core.events.ISharedObjectMessageEvent;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.core.util.ECFException;
import org.eclipse.ecf.core.util.Event;
import org.eclipse.ecf.presence.IAccountManager;
import org.eclipse.ecf.presence.IMessageListener;
import org.eclipse.ecf.presence.IPresence;
import org.eclipse.ecf.presence.IPresenceListener;
import org.eclipse.ecf.presence.IRosterEntry;
import org.eclipse.ecf.presence.IRosterGroup;
import org.eclipse.ecf.presence.ISharedObjectMessageListener;
import org.eclipse.ecf.presence.ISubscribeListener;
import org.eclipse.ecf.provider.xmpp.Trace;
import org.eclipse.ecf.provider.xmpp.events.IQEvent;
import org.eclipse.ecf.provider.xmpp.events.MessageEvent;
import org.eclipse.ecf.provider.xmpp.events.PresenceEvent;
import org.eclipse.ecf.provider.xmpp.identity.XMPPID;
import org.jivesoftware.smack.AccountManager;
import org.jivesoftware.smack.Roster;
import org.jivesoftware.smack.RosterEntry;
import org.jivesoftware.smack.RosterGroup;
import org.jivesoftware.smack.XMPPConnection;
import org.jivesoftware.smack.XMPPException;
import org.jivesoftware.smack.packet.IQ;
import org.jivesoftware.smack.packet.Message;
import org.jivesoftware.smack.packet.Presence;
import org.jivesoftware.smack.packet.RosterPacket;
import org.jivesoftware.smack.packet.Presence.Mode;
import org.jivesoftware.smack.packet.Presence.Type;

/**
 * @author slewis
 * 
 */
public class XMPPPresenceSharedObject implements ISharedObject, IAccountManager {
    
    public static Trace trace = Trace.create("xmpppresencesharedobject");
    ISharedObjectConfig config = null;
    XMPPConnection connection = null;
	AccountManager accountManager = null;
    Vector messageListeners = new Vector();
    Vector presenceListeners = new Vector();
    Vector sharedObjectMessageListeners = new Vector();
    Vector subscribeListeners = new Vector();
	
    protected void addPresenceListener(IPresenceListener listener) {
        presenceListeners.add(listener);
    }
    protected void removePresenceListener(IPresenceListener listener) {
        presenceListeners.remove(listener);
    }
    protected void addMessageListener(IMessageListener listener) {
        messageListeners.add(listener);
    }
    protected void removeMessageListener(IMessageListener listener) {
        messageListeners.add(listener);
    }
    protected void addSharedObjectMessageListener(ISharedObjectMessageListener listener) {
        sharedObjectMessageListeners.add(listener);
    }
    protected void removeSharedObjectMessageListener(ISharedObjectMessageListener listener) {
        sharedObjectMessageListeners.remove(listener);
    }
	protected void addSubscribeListener(ISubscribeListener listener) {
		subscribeListeners.add(listener);
	}
	protected void removeSubscribeListener(ISubscribeListener listener) {
		subscribeListeners.remove(listener);
	}
    protected String canonicalizePresenceFrom(String from) {
        if (from == null)
            return null;
        int index = from.indexOf("/");
        if (index > 0) {
            return from.substring(0, index);
        } else
            return from;
    }

    protected void debug(String msg) {
        if (Trace.ON && trace != null) {
            trace.msg(config.getSharedObjectID() + ":" + msg);
        }
    }

    protected void disconnect() {
        ISharedObjectContext context = getContext();
        if (context != null) {
            context.leaveGroup();
        }
    }

    /*
     * (non-Javadoc)
     * 
     * @see org.eclipse.ecf.core.ISharedObject#dispose(org.eclipse.ecf.core.identity.ID)
     */
    public void dispose(ID containerID) {
        config = null;
		accountManager = null;
    }

    protected void dumpStack(String msg, Throwable e) {
        if (Trace.ON && trace != null) {
            trace.dumpStack(e, config.getSharedObjectID() + ":" + msg);
        }
    }

    protected void fireContainerDeparted(ID departed) {
        for (Iterator i = presenceListeners.iterator(); i.hasNext();) {
            IPresenceListener l = (IPresenceListener) i.next();
            l.handleContainerDeparted(departed);
        }
    }

    protected void fireContainerJoined(ID containerJoined) {
        for (Iterator i = presenceListeners.iterator(); i.hasNext();) {
            IPresenceListener l = (IPresenceListener) i.next();
            l.handleContainerJoined(containerJoined);
        }
    }

    protected void fireMessage(ID from, ID to, IMessageListener.Type type,
            String subject, String body) {
        for (Iterator i = messageListeners.iterator(); i.hasNext();) {
            IMessageListener l = (IMessageListener) i.next();
            l.handleMessage(from, to, type, subject, body);
        }
    }

    protected void firePresence(ID fromID, IPresence presence) {
        for (Iterator i = presenceListeners.iterator(); i.hasNext();) {
            IPresenceListener l = (IPresenceListener) i.next();
            l.handlePresence(fromID, presence);
        }
    }

    protected void fireSubscribe(ID fromID, IPresence presence) {
        for (Iterator i = subscribeListeners.iterator(); i.hasNext();) {
            ISubscribeListener l = (ISubscribeListener) i.next();
			if (presence.getType().equals(IPresence.Type.SUBSCRIBE)) {
				l.handleSubscribeRequest(fromID,presence);
			} else if (presence.getType().equals(IPresence.Type.SUBSCRIBED)) {
				l.handleSubscribed(fromID,presence);
			} else if (presence.getType().equals(IPresence.Type.UNSUBSCRIBE)) {
				l.handleUnsubscribeRequest(fromID,presence);
			} else if (presence.getType().equals(IPresence.Type.UNSUBSCRIBED)) {
				l.handleUnsubscribed(fromID,presence);
			}
        }
    }

    protected void fireSetRosterEntry(IRosterEntry entry) {
        for (Iterator i = presenceListeners.iterator(); i.hasNext();) {
            IPresenceListener l = (IPresenceListener) i.next();
            l.handleSetRosterEntry(entry);
        }
    }
    protected void fireRosterEntry(IRosterEntry entry) {
        for (Iterator i = presenceListeners.iterator(); i.hasNext();) {
            IPresenceListener l = (IPresenceListener) i.next();
            l.handleRosterEntry(entry);
        }
    }

    protected void fireSharedObjectMessage(ISharedObjectMessageEvent event) {
        for (Iterator i = sharedObjectMessageListeners.iterator(); i.hasNext();) {
            ISharedObjectMessageListener l = (ISharedObjectMessageListener) i.next();
            l.handleSharedObjectMessage(event);
        }
    }

    /*
     * (non-Javadoc)
     * 
     * @see org.eclipse.ecf.core.ISharedObject#getAdapter(java.lang.Class)
     */
    public Object getAdapter(Class clazz) {
        return null;
    }

    protected XMPPConnection getConnection() {
        return connection;
    }

    protected ISharedObjectContext getContext() {
        return config.getContext();
    }

    protected String getUserNameFromXMPPAddress(XMPPID userID) {
        return userID.getUsername();
    }

    protected void handleContainerDepartedEvent(
            ISharedObjectContainerDepartedEvent event) {
        ID departedID = event.getDepartedContainerID();
        if (departedID != null) {
            fireContainerDeparted(departedID);
        }
    }

    protected void handleDeactivatedEvent(ISharedObjectDeactivatedEvent event) {
        debug("Got deactivated event: " + event);
    }

    /*
     * (non-Javadoc)
     * 
     * @see org.eclipse.ecf.core.ISharedObject#handleEvent(org.eclipse.ecf.core.util.Event)
     */
    public void handleEvent(Event event) {
        debug("handleEvent(" + event + ")");
        if (event instanceof ISharedObjectActivatedEvent) {
        } else if (event instanceof ISharedObjectContainerJoinedEvent) {
            handleJoin((ISharedObjectContainerJoinedEvent) event);
        } else if (event instanceof IQEvent) {
            handleIQEvent((IQEvent) event);
        } else if (event instanceof MessageEvent) {
            handleMessageEvent((MessageEvent) event);
        } else if (event instanceof PresenceEvent) {
            handlePresenceEvent((PresenceEvent) event);
        } else if (event instanceof ISharedObjectDeactivatedEvent) {
            handleDeactivatedEvent((ISharedObjectDeactivatedEvent) event);
        } else if (event instanceof ISharedObjectContainerDepartedEvent) {
            handleContainerDepartedEvent((ISharedObjectContainerDepartedEvent) event);
        } else if (event instanceof ISharedObjectMessageEvent) {
            fireSharedObjectMessage((ISharedObjectMessageEvent) event);
        } else {
            debug("unrecognized event " + event);
        }
    }

    /*
     * (non-Javadoc)
     * 
     * @see org.eclipse.ecf.core.ISharedObject#handleEvents(org.eclipse.ecf.core.util.Event[])
     */
    public void handleEvents(Event[] events) {
        for (int i = 0; i < events.length; i++) {
            handleEvent(events[i]);
        }
    }

    protected void handleIQEvent(IQEvent evt) {
        IQ iq = evt.getIQ();
        if (iq instanceof RosterPacket) {
            // Roster packet...report to UI
            RosterPacket rosterPacket = (RosterPacket) iq;
			if (rosterPacket.getType() == IQ.Type.SET || rosterPacket.getType() == IQ.Type.RESULT) {
            for (Iterator i = rosterPacket.getRosterItems(); i.hasNext();) {
                IRosterEntry entry = makeRosterEntry((RosterPacket.Item) i
                        .next());
                fireSetRosterEntry(entry);
            }
			}
        } else {
            debug("Received unknown IQ message: " + iq.toXML());
        }
    }

    protected void handleJoin(ISharedObjectContainerJoinedEvent event) {
        fireContainerJoined(event.getJoinedContainerID());
    }

    protected void handleMessageEvent(MessageEvent evt) {
        Message msg = evt.getMessage();
        String from = msg.getFrom();
        String to = msg.getTo();
        String body = msg.getBody();
        String subject = msg.getSubject();
        ID fromID = makeIDFromName(canonicalizePresenceFrom(from));
        ID toID = makeIDFromName(canonicalizePresenceFrom(to));
        fireMessage(fromID, toID, makeMessageType(msg.getType()), subject, body);
    }

    protected void handlePresenceEvent(PresenceEvent evt) {
        Presence xmppPresence = evt.getPresence();
        String from = canonicalizePresenceFrom(xmppPresence.getFrom());
        IPresence newPresence = makeIPresence(xmppPresence);
        ID fromID = makeIDFromName(from);
		if (newPresence.getType().equals(IPresence.Type.SUBSCRIBE) || 
				newPresence.getType().equals(IPresence.Type.UNSUBSCRIBE) ||
				newPresence.getType().equals(IPresence.Type.SUBSCRIBED) ||
				newPresence.getType().equals(IPresence.Type.UNSUBSCRIBED)) {
			fireSubscribe(fromID,newPresence);
		} else firePresence(fromID, newPresence);
    }

    protected void handleRoster(Roster roster) {
        for (Iterator i = roster.getEntries(); i.hasNext();) {
            IRosterEntry entry = makeRosterEntry((RosterEntry) i.next());
            fireRosterEntry(entry);
        }
    }

    /*
     * (non-Javadoc)
     * 
     * @see org.eclipse.ecf.core.ISharedObject#init(org.eclipse.ecf.core.ISharedObjectConfig)
     */
    public void init(ISharedObjectConfig initData)
            throws SharedObjectInitException {
        this.config = initData;
    }

    protected ID makeIDFromName(String name) {
        ID result = null;
        try {
            result = IDFactory.makeID(XMPPID.PROTOCOL, new Object[] { name });
            return result;
        } catch (Exception e) {
            dumpStack("Exception in makeIDFromName", e);
            return null;
        }
    }

    protected IRosterEntry.InterestType makeInterestType(
            RosterPacket.ItemType itemType) {
        if (itemType == RosterPacket.ItemType.BOTH) {
            return IRosterEntry.InterestType.BOTH;
        } else if (itemType == RosterPacket.ItemType.FROM) {
            return IRosterEntry.InterestType.BOTH;
        } else if (itemType == RosterPacket.ItemType.NONE) {
            return IRosterEntry.InterestType.NONE;
        } else if (itemType == RosterPacket.ItemType.REMOVE) {
            return IRosterEntry.InterestType.REMOVE;
        } else if (itemType == RosterPacket.ItemType.TO) {
            return IRosterEntry.InterestType.TO;
        } else
            return IRosterEntry.InterestType.BOTH;
    }

    protected IMessageListener.Type makeMessageType(Message.Type type) {
        if (type == null)
            return IMessageListener.Type.NORMAL;
        if (type == Message.Type.CHAT) {
            return IMessageListener.Type.CHAT;
        } else if (type == Message.Type.NORMAL) {
            return IMessageListener.Type.NORMAL;
        } else if (type == Message.Type.GROUP_CHAT) {
            return IMessageListener.Type.GROUP_CHAT;
        } else if (type == Message.Type.HEADLINE) {
            return IMessageListener.Type.HEADLINE;
        } else if (type == Message.Type.HEADLINE) {
            return IMessageListener.Type.HEADLINE;
        } else
            return IMessageListener.Type.NORMAL;
    }

    protected IPresence makeIPresence(Presence xmppPresence) {
        int priority = xmppPresence.getPriority();
        String status = xmppPresence.getStatus();
        IPresence newPresence = new org.eclipse.ecf.presence.impl.Presence(
                makeIPresenceType(xmppPresence), priority, status,
                makeIPresenceMode(xmppPresence));
        return newPresence;
    }

    protected Presence makePresence(IPresence ipresence) {
        int priority = ipresence.getPriority();
        String status = ipresence.getStatus();
        Presence newPresence = new Presence(
                makePresenceType(ipresence), status, priority,
                makePresenceMode(ipresence));
        return newPresence;
    }

    protected IPresence.Mode makeIPresenceMode(Presence xmppPresence) {
        if (xmppPresence == null)
            return IPresence.Mode.AVAILABLE;
        Mode mode = xmppPresence.getMode();
        if (mode == Presence.Mode.AVAILABLE) {
            return IPresence.Mode.AVAILABLE;
        } else if (mode == Presence.Mode.AWAY) {
            return IPresence.Mode.AWAY;
        } else if (mode == Presence.Mode.CHAT) {
            return IPresence.Mode.CHAT;
        } else if (mode == Presence.Mode.DO_NOT_DISTURB) {
            return IPresence.Mode.DND;
        } else if (mode == Presence.Mode.EXTENDED_AWAY) {
            return IPresence.Mode.EXTENDED_AWAY;
        } else if (mode == Presence.Mode.INVISIBLE) {
            return IPresence.Mode.INVISIBLE;
        }
        return IPresence.Mode.AVAILABLE;
    }

    protected Presence.Mode makePresenceMode(IPresence ipresence) {
        if (ipresence == null)
            return Presence.Mode.AVAILABLE;
        IPresence.Mode mode = ipresence.getMode();
        if (mode == IPresence.Mode.AVAILABLE) {
            return Presence.Mode.AVAILABLE;
        } else if (mode == IPresence.Mode.AWAY) {
            return Presence.Mode.AWAY;
        } else if (mode == IPresence.Mode.CHAT) {
            return Presence.Mode.CHAT;
        } else if (mode == IPresence.Mode.DND) {
            return Presence.Mode.DO_NOT_DISTURB;
        } else if (mode == IPresence.Mode.EXTENDED_AWAY) {
            return Presence.Mode.EXTENDED_AWAY;
        } else if (mode == IPresence.Mode.INVISIBLE) {
            return Presence.Mode.INVISIBLE;
        }
        return Presence.Mode.AVAILABLE;
    }

    protected IPresence.Type makeIPresenceType(Presence xmppPresence) {
        if (xmppPresence == null)
            return IPresence.Type.AVAILABLE;
        Type type = xmppPresence.getType();
        if (type == Presence.Type.AVAILABLE) {
            return IPresence.Type.AVAILABLE;
        } else if (type == Presence.Type.ERROR) {
            return IPresence.Type.ERROR;
        } else if (type == Presence.Type.SUBSCRIBE) {
            return IPresence.Type.SUBSCRIBE;
        } else if (type == Presence.Type.SUBSCRIBED) {
            return IPresence.Type.SUBSCRIBED;
        } else if (type == Presence.Type.UNSUBSCRIBE) {
            return IPresence.Type.UNSUBSCRIBE;
        } else if (type == Presence.Type.UNSUBSCRIBED) {
            return IPresence.Type.UNSUBSCRIBED;
        } else if (type == Presence.Type.UNAVAILABLE) {
            return IPresence.Type.UNAVAILABLE;
        }
        return IPresence.Type.AVAILABLE;
    }

    protected Presence.Type makePresenceType(IPresence ipresence) {
        if (ipresence == null)
            return Presence.Type.AVAILABLE;
        IPresence.Type type = ipresence.getType();
        if (type == IPresence.Type.AVAILABLE) {
            return Presence.Type.AVAILABLE;
        } else if (type == IPresence.Type.ERROR) {
            return Presence.Type.ERROR;
        } else if (type == IPresence.Type.SUBSCRIBE) {
            return Presence.Type.SUBSCRIBE;
        } else if (type == IPresence.Type.SUBSCRIBED) {
            return Presence.Type.SUBSCRIBED;
        } else if (type == IPresence.Type.UNSUBSCRIBE) {
            return Presence.Type.UNSUBSCRIBE;
        } else if (type == IPresence.Type.UNSUBSCRIBED) {
            return Presence.Type.UNSUBSCRIBED;
        } else if (type == IPresence.Type.UNAVAILABLE) {
            return Presence.Type.UNAVAILABLE;
        }
        return Presence.Type.AVAILABLE;
    }

    protected IRosterEntry makeRosterEntry(RosterEntry entry) {
        try {
            ID userID = makeIDFromName(entry.getUser());
            String name = entry.getName();
            RosterPacket.ItemType itemType = entry.getType();
            IRosterEntry.InterestType iType = makeInterestType(itemType);
            IRosterEntry newEntry = new org.eclipse.ecf.presence.impl.RosterEntry(
                    userID, name, iType);
            Iterator grps = entry.getGroups();
            for (; grps.hasNext();) {
                RosterGroup grp = (RosterGroup) grps.next();
                IRosterGroup localGrp = makeRosterGroup(grp);
                newEntry.add(localGrp);
            }
            return newEntry;
        } catch (Exception e) {
            dumpStack("Exception in makeRosterEntry", e);
        }
        return null;
    }

    protected IRosterEntry makeRosterEntry(RosterPacket.Item entry) {
        try {
            ID userID = makeIDFromName(entry.getUser());
            String name = entry.getName();
            RosterPacket.ItemType itemType = entry.getItemType();
            IRosterEntry.InterestType iType = makeInterestType(itemType);
            IRosterEntry newEntry = new org.eclipse.ecf.presence.impl.RosterEntry(
                    userID, name, iType);
            Iterator grps = entry.getGroupNames();
            for (; grps.hasNext();) {
                String grp = (String) grps.next();
                IRosterGroup localGrp = makeRosterGroup(grp);
                newEntry.add(localGrp);
            }
            return newEntry;
        } catch (Exception e) {
            dumpStack("Exception in makeRosterEntry", e);
        }
        return null;
    }

    protected IRosterGroup makeRosterGroup(RosterGroup grp) {
        return new org.eclipse.ecf.presence.impl.RosterGroup(grp.getName());
    }

    protected IRosterGroup makeRosterGroup(String grp) {
        return new org.eclipse.ecf.presence.impl.RosterGroup(grp);
    }

    protected void setConnection(XMPPConnection connection) {
        this.connection = connection;
		if (connection != null) {
			accountManager = new AccountManager(connection);
		}
    }
	public void changePassword(String newpassword) throws ECFException {
		if (accountManager == null) throw new ECFException("not connected");
		try {
			accountManager.changePassword(newpassword);
		} catch (XMPPException e) {
			dumpStack("server exception changing password",e);
			throw new ECFException("server exception changing password",e);
		}
	}
	public void createAccount(String username, String password, Map attributes) throws ECFException {
		if (accountManager == null) throw new ECFException("not connected");
		try {
			accountManager.createAccount(username,password,attributes);
		} catch (XMPPException e) {
			dumpStack("server exception creating account for "+username,e);
			throw new ECFException("server exception creating account for "+username,e);
		}
	}
	public void deleteAccount() throws ECFException {
		if (accountManager == null) throw new ECFException("not connected");
		try {
			accountManager.deleteAccount();
		} catch (XMPPException e) {
			dumpStack("server exception deleting account",e);
			throw new ECFException("server exception deleting account",e);
		}
	}
	public String getAccountInstructions() {
		if (accountManager == null) return null;
		return accountManager.getAccountInstructions();
	}
	public String[] getAccountAttributeNames() {
		if (accountManager == null) return null;
		Iterator i = accountManager.getAccountAttributes();
		List l = new ArrayList();
		for(; i.hasNext(); ) {
			l.add(i.next());
		}
		return (String []) l.toArray(new String[] {});
	}
	public Object getAccountAttribute(String name) {
		if (accountManager == null) return null;
		return accountManager.getAccountAttribute(name);
	}
	
	public boolean supportsCreation() {
		if (accountManager == null) return false;
		return accountManager.supportsAccountCreation();
	}

}