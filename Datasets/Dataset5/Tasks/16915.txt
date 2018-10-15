package org.eclipse.ecf.provider.datashare;

/*******************************************************************************
 * Copyright (c) 2004 Composent, Inc., Peter Nehrer, Boris Bokowski. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.ds.impl;

import java.io.Serializable;

import org.eclipse.ecf.core.ISharedObjectTransactionConfig;
import org.eclipse.ecf.core.events.IContainerConnectedEvent;
import org.eclipse.ecf.core.events.IContainerDisconnectedEvent;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.sharedobject.SharedObjectMsgEvent;
import org.eclipse.ecf.core.sharedobject.TransactionSharedObject;
import org.eclipse.ecf.core.util.ECFException;
import org.eclipse.ecf.core.util.Event;
import org.eclipse.ecf.core.util.IEventProcessor;
import org.eclipse.ecf.ds.IChannel;
import org.eclipse.ecf.ds.IChannelListener;
import org.eclipse.ecf.ds.events.IChannelEvent;
import org.eclipse.ecf.ds.events.IChannelGroupDepartEvent;
import org.eclipse.ecf.ds.events.IChannelGroupJoinEvent;
import org.eclipse.ecf.ds.events.IChannelInitializeEvent;
import org.eclipse.ecf.ds.events.IChannelMessageEvent;

public class ChannelImpl extends TransactionSharedObject implements IChannel {

	class ChannelMsg implements Serializable {
		private static final long serialVersionUID = -6752722047308362941L;
		byte [] channelData = null;
		
		ChannelMsg() {}
		ChannelMsg(byte [] data) {
			this.channelData = data;
		}
		byte [] getData() {
			return channelData;
		}
	}

	protected IChannelListener listener;
	
	protected void setChannelListener(IChannelListener l) {
		this.listener = l;
	}
	/**
	 * Host implementation of channel class constructor
	 * @param config the ISharedObjectTransactionConfig associated with this new host instance
	 * @param listener the listener associated with this channel instance
	 */
	public ChannelImpl(ISharedObjectTransactionConfig config, IChannelListener listener) {
		super(config);
		setChannelListener(listener);
	}
	/**
	 * Replica implementation of channel class constructor
	 *
	 */
	public ChannelImpl() {
		super();
	}
	
	protected void handleReplicaChannelEvent(IChannelEvent event) {
		System.out.println("handleReplicaChannelEvent("+getID()+":"+event);
	}
	protected void initialize() {
		super.initialize();
		
		// For the replicas, setup a channel listener that calls handleReplicaChannelEvent
		if (!isPrimary()) {
			setChannelListener(new IChannelListener() {
				public void handleChannelEvent(IChannelEvent event) {
					handleReplicaChannelEvent(event);
				}
			});
		}
		addEventProcessor(new IEventProcessor() {
			public boolean acceptEvent(Event event) {
				if (event instanceof IContainerConnectedEvent) {
					return true;
				} else if (event instanceof IContainerDisconnectedEvent) {
					return true;
				}
				return false;
			}
			public Event processEvent(Event event) {
				if (event instanceof IContainerConnectedEvent) {
					ChannelImpl.this.listener.handleChannelEvent(createChannelGroupJoinEvent(true,((IContainerConnectedEvent)event).getTargetID()));
				} else if (event instanceof IContainerDisconnectedEvent) {
					ChannelImpl.this.listener.handleChannelEvent(createChannelGroupDepartEvent(true,((IContainerDisconnectedEvent)event).getTargetID()));
				}
				return event;
			}
		});
		listener.handleChannelEvent(new IChannelInitializeEvent() {
			public ID[] getGroupMembers() {
				return getContext().getGroupMemberIDs();
			}
			public ID getChannelID() {
				return getID();
			}});
	}
	
	protected IChannelGroupJoinEvent createChannelGroupJoinEvent(final boolean hasJoined,final ID targetID) {
		return new IChannelGroupJoinEvent() {
			private static final long serialVersionUID = -1085237280463725283L;
			public ID getTargetID() {
				return targetID;
			}
			public ID getChannelID() {
				return getID();
			}
		};
	}
	protected IChannelGroupDepartEvent createChannelGroupDepartEvent(final boolean hasJoined,final ID targetID) {
		return new IChannelGroupDepartEvent() {
			private static final long serialVersionUID = -1085237280463725283L;
			public ID getTargetID() {
				return targetID;
			}
			public ID getChannelID() {
				return getID();
			}
		};
	}
    protected Event handleSharedObjectMsgEvent(final SharedObjectMsgEvent event) {
    	Object data = event.getData();
    	ChannelMsg channelData = null;
    	if (data instanceof ChannelMsg) {
    		channelData = (ChannelMsg) data;
    	}
    	if (channelData != null) {
    		listener.handleChannelEvent(new IChannelMessageEvent() {
				private static final long serialVersionUID = -2270885918818160970L;
				public ID getFromID() {
					return event.getSenderSharedObjectID();
				}
				public byte[] getData() {
					return (byte []) event.getData();
				}
				public ID getChannelID() {
					return getID();
				}});
    		// Discontinue processing of this event...we are it
    		return null;
    	}
    	return event;
    }
	
	public void sendMessage(byte[] message) throws ECFException {
		sendMessage(null,message);
	}

	public void sendMessage(ID receiver, byte[] message) throws ECFException {
		try {
			getContext().sendMessage(receiver, new ChannelMsg(message));
		} catch (Exception e) {
			throw new ECFException("send message exception",e);
		}
	}

}