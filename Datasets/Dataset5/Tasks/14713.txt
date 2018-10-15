return getSharedObject().getPrimaryContainerID();

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
package org.eclipse.ecf.core.sharedobject;

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
import org.eclipse.ecf.core.events.ISharedObjectContainerDisconnectedEvent;
import org.eclipse.ecf.core.events.ISharedObjectContainerConnectedEvent;
import org.eclipse.ecf.core.events.ISharedObjectCreateResponseEvent;
import org.eclipse.ecf.core.events.ISharedObjectMessageEvent;
import org.eclipse.ecf.core.events.SharedObjectCommitEvent;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.util.Event;
import org.eclipse.ecf.core.util.IEventProcessor;
import org.eclipse.ecf.internal.core.Trace;

/**
 * Implementation of two-phase commit for transactional replication of shared objects.
 *
 */
public class TwoPhaseCommitEventProcessor implements IEventProcessor,
		ISharedObjectContainerTransaction {
	public static final Trace trace = Trace.create("twophasecommiteventprocessor");
	AbstractSharedObject sharedObject = null;
	byte transactionState = ISharedObjectContainerTransaction.ACTIVE;
	Object lock = new Object();
	List participants = new Vector();
	Map failed = new HashMap();
	int timeout = ITransactionConfiguration.DEFAULT_TIMEOUT;
	int minFailedToAbort = 0;
	long identifier = 0;
	ITransactionParticipantsFilter participantsFilter = null;
	
	public TwoPhaseCommitEventProcessor(AbstractSharedObject bse, ITransactionConfiguration config) {
		this.sharedObject = bse;
		if (config == null) {
			config = new TransactionSharedObjectConfiguration();
		}
		this.timeout = config.getTimeout();
		this.participantsFilter = config.getParticipantsFilter();
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
	protected AbstractSharedObject getSharedObject() {
		return sharedObject;
	}
	protected ID getHomeID() {
		return getSharedObject().getHomeID();
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
	 * for AbstractSharedObject method dispatch to call
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
			handleActivated((ISharedObjectActivatedEvent) event);
		} else if (event instanceof ISharedObjectContainerConnectedEvent) {
			handleJoined((ISharedObjectContainerConnectedEvent) event);
		} else if (event instanceof ISharedObjectCreateResponseEvent) {
			handleCreateResponse((ISharedObjectCreateResponseEvent) event);
		} else if (event instanceof ISharedObjectContainerDisconnectedEvent) {
			handleDeparted((ISharedObjectContainerDisconnectedEvent) event);
		} else if (event instanceof ISharedObjectMessageEvent) {
			ISharedObjectMessageEvent some = (ISharedObjectMessageEvent) event;
			Object data = some.getData();
			if (data instanceof ISharedObjectCommitEvent) localCommitted();
		}
		// Let other event processors have a shot at this event
		return event;
	}
	protected void handleActivated(ISharedObjectActivatedEvent event) {
		trace("handleActivated(" + event + ")");
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
	protected void replicateTo(ID[] remotes) {
		if (remotes == null) {
			trace("replicateTo(null)");
		} else {
			trace("replicateTo("+Arrays.asList(remotes)+")");
		}
		try {
			// Get current group membership
			ISharedObjectContext context = getSharedObject().getContext();
			if (context == null)
				return;
			ID[] group = context.getGroupMemberIDs();
			if (group == null || group.length < 1) {
				// we're done
				return;
			}
			SharedObjectDescription[] createInfos = getSharedObject()
					.getReplicaDescriptions(remotes);
			if (createInfos != null) {
				if (createInfos.length == 1) {
					context.sendCreate((remotes == null) ? null : remotes[0],
							createInfos[0]);
				} else {
					for (int i = 0; i < remotes.length; i++) {
						context.sendCreate(remotes[i], createInfos[i]);
					}
				}
			}
		} catch (IOException e) {
			if (remotes == null) traceStack("Exception in replicateTo(null)",e);
			else traceStack("Exception in replicateTo(" + Arrays.asList(remotes)
					+ ")", e);
			return;
		}
	}
	protected void handlePrimaryActivated(ISharedObjectActivatedEvent event) {
		trace("handlePrimaryActivated("+event+")");
		// First get current group membership
		ID[] groupMembers = getContext().getGroupMemberIDs();
		// Now get participants
		ID[] transactionParticipants = null;
		// If there is a participants filter specified then use it and ask it to return an ID [] of participants (given
		// the current group membership
		if (participantsFilter != null) {
			transactionParticipants = participantsFilter.filterParticipants(groupMembers);
		}
		// replicate
		if (transactionParticipants == null) {
			// This means that all current group members should be included as participants
			replicateTo(null);
			transactionParticipants = groupMembers;
		} else {
			// This means the participants filter provided us with an ID [] and so we replicate only to that ID []
			replicateTo(transactionParticipants);
		}
		
		// Add participants to the collection
		addParticipants(transactionParticipants);
		// Now set transaction state to VOTING
		setTransactionState(ISharedObjectContainerTransaction.VOTING);
	}
	private long getNextIdentifier() {
		return identifier++;
	}
	protected void handleReplicaActivated(ISharedObjectActivatedEvent event) {
		trace("handleReplicaActivated("+event+")");
		try {
			// Try to respond with create success message back to host
			getContext().sendCreateResponse(getHomeID(), null,
					getNextIdentifier());
			// If above succeeds, we're now in prepared state
			setTransactionState(ISharedObjectContainerTransaction.PREPARED);
		} catch (Exception except) {
			// If throws exception, we're doomed
			traceStack("handleReplicaActivated(" + event + ")", except);
			setTransactionState(ISharedObjectContainerTransaction.ABORTED);
		}
	}
	protected void handleJoined(ISharedObjectContainerConnectedEvent event) {
		trace("handleJoined(" + event + ")");
		if (isPrimary()) {
			synchronized (lock) {
				// First send replicate message *no matter what state we are in*
				ID newMember = event.getTargetID();
				replicateTo(new ID[] { newMember });
				// Then if in voting state add participants to transaction
				if (getTransactionState() == ISharedObjectContainerTransaction.VOTING)
					addParticipants(new ID[] { newMember });
			}
		} else {
			// we don't care as we are not transaction monitor
		}
	}
	protected void handleCreateResponse(ISharedObjectCreateResponseEvent event) {
		trace("handleCreateResponse(" + event + ")");
		if (isPrimary()) {
			synchronized (lock) {
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
	protected void handleDeparted(ISharedObjectContainerDisconnectedEvent event) {
		trace("handleDeparted(" + event + ")");
		if (isPrimary()) {
			ID remoteID = event.getTargetID();
			synchronized (lock) {
				if (getTransactionState() == ISharedObjectContainerTransaction.VOTING) {
					addFailed(remoteID, new Exception("Container " + remoteID
							+ " left"));
				}
				lock.notifyAll();
			}
		} else {
			// we don't care as we are not transaction monitor
		}
	}
	protected void handleVotingCompletedCreateResponse(ID fromID, Throwable e,
			long identifier) {
		trace("handleVotingCompletedCreateResponse(" + fromID + ","+e+","+identifier+")");
		// If remote creation was successful, simply send commit message back.
		if (e == null) {
			try {
				getSharedObject().getContext().sendMessage(fromID,
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
			getContext().sendMessage(null,
					new SharedObjectCommitEvent(getSharedObject().getID()));
		} catch (Exception e2) {
			doTMAbort(new SharedObjectAddAbortException(
					"Exception sending commit message", e2, getTimeout()));
		}
	}
	public byte getTransactionState() {
		synchronized (lock) {
			return transactionState;
		}
	}
	protected void setTransactionState(byte state) {
		synchronized (lock) {
			transactionState = state;
		}
	}
	public void waitToCommit() throws SharedObjectAddAbortException {
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
						throw new SharedObjectAddAbortException(
								"Timeout adding " + getSharedObject().getID()
										+ " to " + getHomeID(),
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
		trace("doTMAbort:" + except);
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
		trace("doTMCommit");
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
		trace("localCommitted()");
		// Set state variable to committed.
		setTransactionState(ISharedObjectContainerTransaction.COMMITTED);
		getSharedObject().creationCompleted();
	}
	protected boolean isVotingCompleted() throws SharedObjectAddAbortException {
		// The test here is is we've received any indication of failed
		// participants in the transaction. If so, we throw.
		if (failed.size() > getMinFailedToAbort()) {
			// Abort!
			trace("isVotingCompleted:aborting:failed>"
					+ getMinFailedToAbort() + ":failed=" + failed);
			throw new SharedObjectAddAbortException("Abort received",
					participants, failed, getTimeout());
			// If no problems, and the number of participants to here from is 0,
			// then we're done
		} else if (getTransactionState() == ISharedObjectContainerTransaction.VOTING
				&& participants.size() == 0) {
			// Success!
			trace("isVotingCompleted() returning true");
			return true;
		}
		// Else continue waiting
		trace("isVotingCompleted:false");
		return false;
	}
}