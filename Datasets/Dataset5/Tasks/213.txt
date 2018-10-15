throw new SharedObjectAddAbortException("Abort received", participants, failed,

/****************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Composent, Inc. - initial API and implementation
 *****************************************************************************/

package org.eclipse.ecf.provider.generic.sobject;

import java.io.IOException;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Vector;

import org.eclipse.ecf.core.ISharedObjectContainerTransaction;
import org.eclipse.ecf.core.ISharedObjectContext;
import org.eclipse.ecf.core.SharedObjectAddAbortException;
import org.eclipse.ecf.core.SharedObjectDescription;
import org.eclipse.ecf.core.events.ISharedObjectActivatedEvent;
import org.eclipse.ecf.core.events.ISharedObjectCommitEvent;
import org.eclipse.ecf.core.events.ISharedObjectContainerDepartedEvent;
import org.eclipse.ecf.core.events.ISharedObjectContainerJoinedEvent;
import org.eclipse.ecf.core.events.ISharedObjectCreateResponseEvent;
import org.eclipse.ecf.core.events.ISharedObjectMessageEvent;
import org.eclipse.ecf.core.events.SharedObjectCommitEvent;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.util.Event;
import org.eclipse.ecf.core.util.IEventProcessor;
import org.eclipse.ecf.provider.Trace;

/**
 * @author slewis
 * 
 */
public class TPCommitEventProcessor implements IEventProcessor {

	public static final Trace trace = Trace.create("transactioneventprocessor");
	public static final int DEFAULT_TIMEOUT = 30000;

	ISharedObjectInternal sharedObject = null;

	byte transactionState = ISharedObjectContainerTransaction.ACTIVE;
	Object lock = new Object();
	List participants = new Vector();
	Map failed = new HashMap();
	int timeout = DEFAULT_TIMEOUT;
	int minFailedToAbort = 0;
	long identifier = 0;
	ID [] exceptions;
	
	public TPCommitEventProcessor(ISharedObjectInternal bse, int timeout, ID [] except) {
		this.sharedObject= bse;
		this.timeout = timeout;
		this.exceptions = except;
	}
	public TPCommitEventProcessor(ISharedObjectInternal bse, int timeout) {
		this(bse,timeout,null);
	}

	public TPCommitEventProcessor(ISharedObjectInternal bse) {
		this(bse, DEFAULT_TIMEOUT);
	}

	protected void trace(String msg) {
		if (Trace.ON && trace != null) {
			trace.msg(getSharedObject().getID() + ":"
					+ (getSharedObject().isPrimary() ? "primary:" : "replica:")
					+ msg);
		}
	}

	protected void traceStack(String msg, Throwable t) {
		if (Trace.ON && trace != null) {
			trace.dumpStack(t, sharedObject.getID() + ":"
					+ (getSharedObject().isPrimary() ? "primary" : "replica")
					+ msg);
		}
	}

	protected int getTimeout() {
		return timeout;
	}

	protected int getMinFailedToAbort() {
		return minFailedToAbort;
	}

	protected boolean isPrimary() {
		return getSharedObject().isPrimary();
	}

	protected ISharedObjectInternal getSharedObject() {
		return sharedObject;
	}

	protected ID getHomeID() {
		return getSharedObject().getHomeID();
	}

	protected ID [] filter(ID [] ids) {
		if (exceptions == null) return ids;
		List aList = Arrays.asList(ids);
		for(int i=0; i < exceptions.length; i++) {
			aList.remove(exceptions[i]);
		}
		return (ID []) aList.toArray(new ID[] {});
	}
	protected void addParticipants(ID[] ids) {
		if (ids != null) {
			for (int i = 0; i < ids.length; i++) {
				trace("addParticipant(" + ids[i] + ")");
				if (!getHomeID().equals(ids[i]))
					participants.add(ids[i]);
			}
		}
	}

	protected void removeParticipant(ID id) {
		if (id != null) {
			trace("removeParticipant(" + id + ")");
			participants.remove(id);
		}
	}

	protected void addFailed(ID remote, Throwable failure) {
		if (remote != null && failure != null) {
			trace("addFailed(" + remote + "," + failure + ")");
			failed.put(remote, failure);
		}
	}

	protected ISharedObjectContext getContext() {
		return getSharedObject().getContext();
	}

	/*
	 * Implementation of IEventProcessor. These methods are entry point methods
	 * for BaseSharedObject method dispatch to call
	 */
	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.util.IEventProcessor#acceptEvent(org.eclipse.ecf.core.util.Event)
	 */
	public boolean acceptEvent(Event event) {
		return true;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.util.IEventProcessor#processEvent(org.eclipse.ecf.core.util.Event)
	 */
	public Event processEvent(Event event) {
		if (event instanceof ISharedObjectActivatedEvent) {
			trace("handleActivated(" + event + ")");
			handleActivated((ISharedObjectActivatedEvent) event);
			return event;
		} else if (event instanceof ISharedObjectContainerJoinedEvent) {
			trace("handleJoined(" + event + ")");
			handleJoined((ISharedObjectContainerJoinedEvent) event);
			return event;
		} else if (event instanceof ISharedObjectCreateResponseEvent) {
			trace("handleCreateResponse(" + event + ")");
			handleCreateResponse((ISharedObjectCreateResponseEvent) event);
			return event;
		} else if (event instanceof ISharedObjectContainerDepartedEvent) {
			trace("handleDeparted(" + event + ")");
			handleDeparted((ISharedObjectContainerDepartedEvent) event);
			return event;
		} else if (event instanceof ISharedObjectMessageEvent) {
			ISharedObjectMessageEvent some = (ISharedObjectMessageEvent) event;
			Object data = some.getData();
			if (data instanceof ISharedObjectCommitEvent) {
				trace("localCommitted(" + event + ")");
				localCommitted();
				return event;
			}
		}
		return event;
	}

	protected void handleActivated(ISharedObjectActivatedEvent event) {
		// No other state changes while this is going on
		synchronized (lock) {
			if (isPrimary()) {
				// Primary
				handlePrimaryActivated(event);
			} else {
				handleReplicaActivated(event);
			}
			// Notify any threads waiting on state change
			lock.notifyAll();
		}

	}
    protected void replicateTo(ID [] remotes) {
        try {
            // Get current group membership
            ISharedObjectContext context = getSharedObject().getContext();
            if (context == null) return;
            ID[] group = context.getGroupMemberIDs();
            if (group == null || group.length < 1) {
                // we're done
                return;
            }
            SharedObjectDescription[] createInfos = getSharedObject().getReplicaDescriptions(remotes);
            if (createInfos != null) {
            	if (createInfos.length == 1) {
            		context.sendCreate((remotes==null)?null:remotes[0],createInfos[0]);
            	} else {
            		for(int i=0; i < remotes.length; i++) {
            			context.sendCreate(remotes[i],createInfos[i]);
            		}
            	}
            }
        } catch (IOException e) {
            traceStack("Exception in replicateTo("+Arrays.asList(remotes)+")", e);
            return;
        }
    }

	protected void handlePrimaryActivated(ISharedObjectActivatedEvent event) {
		// if we don't have any exceptions replicate to all remotes
		ID [] groupMembers = getContext().getGroupMemberIDs();
		ID [] replicaContainers = groupMembers;
		if (exceptions == null) {
			replicateTo(null);
		} else {
			// We do have some exceptions, so filter these out
			replicaContainers = filter(groupMembers);
			replicateTo(replicaContainers);
		}
		addParticipants(replicaContainers);
		setTransactionState(ISharedObjectContainerTransaction.VOTING);
	}

	protected void handleReplicaActivated(ISharedObjectActivatedEvent event) {
		try {
			// Try to respond with create success message back to host
			getContext().sendCreateResponse(getHomeID(), null,
					BaseSharedObject.getNextIdentifier());
			// If above succeeds, we're now in prepared state
			setTransactionState(ISharedObjectContainerTransaction.PREPARED);
		} catch (Exception except) {
			// If throws exception, we're doomed
			traceStack("handleReplicaActivated(" + event + ")", except);
			setTransactionState(ISharedObjectContainerTransaction.ABORTED);
		}
	}

	protected void handleJoined(ISharedObjectContainerJoinedEvent event) {
		if (isPrimary()) {
			// If we are currently in VOTING state, then add the new member to
			// list of participants
			// and send replicate message. If not in voting state, just send
			// replicate message
			synchronized (lock) {
				ID newMember = event.getJoinedContainerID();
				replicateTo(new ID[] { newMember });
				if (getTransactionState() == ISharedObjectContainerTransaction.VOTING)
					addParticipants(new ID[] { newMember });
			}
		} else {
			// we don't care as we are note transaction monitor
		}
	}

	protected void handleCreateResponse(ISharedObjectCreateResponseEvent event) {
		if (isPrimary()) {
			synchronized (lock) {
				trace("handleCreateResponse(" + event + ")");
				Throwable except = event.getException();
				ID remoteID = event.getRemoteContainerID();
				long ident = event.getSequence();
				if (getTransactionState() == ISharedObjectContainerTransaction.VOTING) {
					if (except == null) {
						removeParticipant(remoteID);
					} else {
						addFailed(remoteID, except);
					}
				} else {
					handleVotingCompletedCreateResponse(remoteID, except, ident);
				}
				lock.notifyAll();
			}
		} else {
			// we don't care as we are note transaction monitor
		}
	}

	protected void handleDeparted(ISharedObjectContainerDepartedEvent event) {
		if (isPrimary()) {
			ID remoteID = event.getDepartedContainerID();
			synchronized (lock) {
				if (getTransactionState() == ISharedObjectContainerTransaction.VOTING) {
					addFailed(remoteID, new Exception("Container " + remoteID
							+ " left"));
				}
				lock.notifyAll();
			}
		} else {
			// we don't care as we are note transaction monitor
		}
	}

	protected void handleVotingCompletedCreateResponse(ID fromID, Throwable e,
			long identifier) {
		// If remote creation was successful, simply send commit message back.
		if (e == null) {
			try {
				getSharedObject().getContext().sendMessage(
						fromID,
						new SharedObjectCommitEvent(getSharedObject().getID()));
			} catch (Exception e2) {
				traceStack("Exception in sendCommit to " + fromID, e2);
			}
		} else {
			// Too late to vote no
			handlePostCommitFailure(fromID, e, identifier);
		}
	}

	protected void handlePostCommitFailure(ID fromID, Throwable e,
			long identifier) {
		// Do nothing but report
		trace("handlePostCommitFailure(" + fromID + "," + e + "," + identifier
				+ ")");
	}

	protected void sendCommit() throws SharedObjectAddAbortException {
		try {
			getContext().sendMessage(
					null,
					new SharedObjectCommitEvent(getSharedObject().getID()));
		} catch (Exception e2) {
			doTMAbort(new SharedObjectAddAbortException(
					"Exception sending commit message", e2, getTimeout()));
		}
	}

	protected byte getTransactionState() {
		synchronized (lock) {
			return transactionState;
		}
	}

	protected void setTransactionState(byte state) {
		synchronized (lock) {
			transactionState = state;
		}
	}

	protected void waitToCommit() throws SharedObjectAddAbortException {
		if (getTransactionState() == ISharedObjectContainerTransaction.COMMITTED)
			return;
		synchronized (lock) {
			long end = System.currentTimeMillis() + getTimeout();
			try {
				while (!isVotingCompleted()) {
					long wait = end - System.currentTimeMillis();
					trace("waitForFinish waiting " + wait + "ms on "
							+ getSharedObject().getID());
					if (wait <= 0L)
						throw new SharedObjectAddAbortException("Timeout adding "+getSharedObject().getID()+" to "+getHomeID(),
								(Throwable) null, getTimeout());
					// Wait right here
					lock.wait(wait);
				}
			} catch (Exception except) {
				// Aborted for some reason. Clean up and throw
				doTMAbort(except);
			}
			// Success. Send commit to remotes and clean up before returning.
			doTMCommit();
		}
	}

	protected void doTMAbort(Throwable except)
			throws SharedObjectAddAbortException {
		trace("ABORTED:" + except);
		// Set our own state variable to ABORTED
		setTransactionState(ISharedObjectContainerTransaction.ABORTED);
		// Send destroy message here so all remotes get destroyed, and we remove
		// ourselves from local space as well.
		getSharedObject().destroySelf();
		// throw so caller gets exception and can deal with it
		if (except instanceof SharedObjectAddAbortException)
			throw (SharedObjectAddAbortException) except;
		else
			throw new SharedObjectAddAbortException("Aborted", except,
					getTimeout());
	}

	protected void doTMCommit() throws SharedObjectAddAbortException {
		// Only forward commit message if the participantIDs array is not yet
		// null,
		// and the current membership is > 0 (we're connected to something)
		if (getSharedObject().getContext().getGroupMemberIDs().length > 0) {
			sendCommit();
		}
		// Call local committed message
		localCommitted();
	}

	protected void localCommitted() {
		// Set state variable to committed.
		setTransactionState(ISharedObjectContainerTransaction.COMMITTED);
		trace("COMMITTED!!!");
	}

	protected boolean isVotingCompleted() throws SharedObjectAddAbortException {
		// The test here is is we've received any indication of failed
		// participants in
		// the transaction. If so, we throw.
		if (failed.size() > getMinFailedToAbort()) {
			// Abort!
			trace("isVotingCompleted() aborting: failed > "
					+ getMinFailedToAbort() + ":failed=" + failed);
			throw new SharedObjectAddAbortException("Abort received", failed,
					getTimeout());
			// If no problems, and the number of participants to here from is 0,
			// then we're done
		} else if (getTransactionState() == ISharedObjectContainerTransaction.VOTING
				&& participants.size() == 0) {
			// Success!
			trace("isVotingCompleted() returning true");
			return true;
		}
		// Else continue waiting
		trace("isVotingCompleted() returning false");
		return false;
	}

}