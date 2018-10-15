import org.eclipse.ecf.internal.example.collab.Trace;

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

package org.eclipse.ecf.example.collab.share;

import java.util.Hashtable;
import java.util.Vector;

import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.sharedobject.ISharedObjectContainerTransaction;
import org.eclipse.ecf.core.sharedobject.SharedObjectAddAbortException;
import org.eclipse.ecf.example.collab.Trace;

public class TransactionSharedObject extends GenericSharedObject implements ISharedObjectContainerTransaction {

    static Trace tsotrace = Trace.create("transactionsharedobject");

    // If the "replicaCommit" method name is changed, the name of this variable should
    // change
    public static final String REPLICA_COMMIT_METHOD = "replicaCommit";

    public static int DEFAULT_TIMEOUT = 30000;
    // Dummy inner class to provide lock
    static final class Lock {}

    // Timeout value associated with this object's replication 
    protected int timeout;
    // Replication state this object is currently in.
    protected byte state;
    // A lock variable
    protected Lock lock;
    protected Vector participantIDs;
    protected Hashtable failedParticipants;

    public TransactionSharedObject(int timeout)
    {
        this.timeout = timeout;
        init();
    }
    public TransactionSharedObject()
    {
        this(DEFAULT_TIMEOUT);
    }

    protected void traceDump(String msg, Throwable t) {
        if (Trace.ON && tsotrace != null) {
        	tsotrace.dumpStack(t, msg);
        }
    }
    protected void init()
    {
        state = ISharedObjectContainerTransaction.ACTIVE;
        lock = new Lock();
        participantIDs = new Vector();
        failedParticipants = new Hashtable();
        trace("TransactionSharedObject.init() with timeout: "+timeout);
    }
    public void activated(ID [] others)
    {
        if (Trace.ON && tsotrace != null) {
        	tsotrace.msg("activated() on "+getID());
        }
        // No other state changes while this is going on
        synchronized (lock) {
            if (isHost()) {
                replicate(null);
                addRemoteParticipants(getContext().getGroupMemberIDs());
                state = ISharedObjectContainerTransaction.VOTING;
            // Clients
            } else {
                try {
                    // Try to respond with create success message back to host
                    getContext().sendCreateResponse(getHomeContainerID(), null, getIdentifier());
                    // If above succeeds, we're now in prepared state
                    state = ISharedObjectContainerTransaction.PREPARED;
                } catch (Exception e) {
                    // If throws exception, we're doomed
                    state = ISharedObjectContainerTransaction.ABORTED;
                    traceDump("unable to send create response to "+getHomeContainerID(),e);
                }
            }
            // Notify any threads waiting on state change
            lock.notifyAll();
        }
    }

    public void memberAdded(ID member)
    {
        if (isHost()) {
            // If we are currently in VOTING state, then add the new member to list of participants
            // and send replicate message.  If not in voting state, just send replicate message
            synchronized (lock) {
                replicate(member);
                if (getTransactionState() == ISharedObjectContainerTransaction.VOTING) addRemoteParticipants(new ID[] { member});
                else replicate(member);
            }
        }
    }

    protected void addRemoteParticipants(ID ids[])
    {
        if (ids != null && participantIDs != null) {
            for(int i=0; i < ids.length; i++) {
                if (!getHomeContainerID().equals(ids[i])) participantIDs.addElement(ids[i]);
            }
        }
        trace("addRemoteParticipants(participants="+participantIDs+")");
    }

    protected void removeRemoteParticipant(ID id)
    {
        if (id != null && participantIDs != null) {
            int index = participantIDs.indexOf(id);
            if (index != -1) participantIDs.removeElementAt(index);
        }
        trace("removeRemoteParticipant("+id+",after removal participants="+participantIDs+")");
    }

    protected void addRemoteParticipantFailed(ID remote, Throwable failure)
    {
        if (remote != null && failure != null && failedParticipants != null) {
            failedParticipants.put(remote, failure);
        }
    }
    public void handleCreateResponse(ID fromID, Throwable e, Long identifier)
    {
    	System.out.println("handleCreateResponse("+fromID+","+e+","+identifier+"on:"+getID());
        // If no exception, remove
        synchronized (lock) {
            if (state == ISharedObjectContainerTransaction.VOTING) {
                if (e == null) {
                    removeRemoteParticipant(fromID);
                } else {
                    addRemoteParticipantFailed(fromID, e);
                }
            } else {
                handleVotingCompletedCreateResponse(fromID, e, identifier);
            }
            lock.notifyAll();
        }
    }

    protected void handleVotingCompletedCreateResponse(ID fromID, Throwable e, Long identifier)
    {
        // If remote creation was successful, simply send commit message back.
        if (e == null) {
            // send commit message right back.
            try {
                forwardMsgTo(fromID, SharedObjectMsg.createMsg((String) null,REPLICA_COMMIT_METHOD));
            } catch (Exception except) {
                traceDump("Exception sending commit message to "+fromID,except);
            }
        }
    }

    public void memberRemoved(ID member)
    {
        // We only care about this if we are the host.
        if (isHost()) {
            synchronized (lock) {
                if (state == ISharedObjectContainerTransaction.VOTING) {
                    addRemoteParticipantFailed(member, new Exception("Member "+member+" left"));
                }
                lock.notifyAll();
            }
        }
    }
    public void waitToCommit() throws SharedObjectAddAbortException
    {
        synchronized (lock) {
            long end = System.currentTimeMillis() + timeout;
            try {
                while (!votingCompleted()) {
                    long wait = end - System.currentTimeMillis();
                    trace("waitForFinish waiting "+wait+"ms on "+getID());
                    if (wait <= 0L) throw new SharedObjectAddAbortException("Timeout waiting for create responses");
                    // Actually wait right here
                    lock.wait(wait);
                }
            } catch (InterruptedException e) {
                throw new SharedObjectAddAbortException("Wait interrupted");
            } catch (SharedObjectAddAbortException e1) {
                // Aborted for some reason.  Clean up.
                doAbort(e1);
            }
            // Success.  Send commit to remotes and clean up before returning.
            doCommit();
        }
    }

    public byte getTransactionState()
    {
        synchronized (lock) {
            return state;
        }
    }

    protected void doAbort(SharedObjectAddAbortException e) throws SharedObjectAddAbortException
    {
        trace("doAbort().  Commit ABORTED on "+getID()+" with exception "+e);
        // Send destroy message here so all remotes get destroyed, and we remove
        // ourselves from local space as well.
        destroySelf();
        // Set our own state variable to ABORTED
        state = ISharedObjectContainerTransaction.ABORTED;
        // throw so caller gets exception and can deal with it
        throw e;
    }

    public void doCommit() throws SharedObjectAddAbortException
    {
        // Get current membership
        int others = 0;
            others = getContext().getGroupMemberIDs().length;
        // Only forward commit message if the participantIDs array is not yet null,
        // and the current membership is > 0 (we're connected to something)
        if (participantIDs != null && others > 0) {
            // Send replicaCommit message to all remote clients
            try {
                forwardMsgTo(null, SharedObjectMsg.createMsg((String) null,REPLICA_COMMIT_METHOD));
            } catch (Exception e2) {
                doAbort(new SharedObjectAddAbortException("Exception sending commit message", e2));
            }
        }
        // Set state variable to committed.
        state = ISharedObjectContainerTransaction.COMMITTED;
        // Call local committed message
        committed();
        participantIDs = null;
        failedParticipants = null;
    }

    protected void execMsgInvoke(SharedObjectMsg msg, ID fromID, Object o)
        throws Exception
    {
	if (o == this)
	{
	    // Object[] args = msg.getArgs();
	    String name = msg.getMethodName();
	    if (name.equals("replicaCommit"))
	    {
		replicaCommit();
		return;
	    }
	}
	super.execMsgInvoke(msg, fromID, o);
    }

    public final void replicaCommit()
    {
        synchronized (lock) {
            state = COMMITTED;
            lock.notifyAll();
            participantIDs = null;
            failedParticipants = null;
        }
        // Call subclass overrideable method
        committed();
    }

    protected void committed()
    {
        trace("committed()");
        // Subclasses may override as appropriate
    }

    protected boolean votingCompleted() throws SharedObjectAddAbortException
    {
        // The test here is is we've received any indication of failed participants in
        // the transaction.  If so, we throw.
        if (failedParticipants != null && failedParticipants.size() > 0) {
            ID remoteID = (ID) failedParticipants.keys().nextElement();
            Exception e = (Exception) failedParticipants.get(remoteID);
            trace("failed participant "+remoteID+" causing abort");
            // Abort!
            throw new SharedObjectAddAbortException("Abort received "+remoteID, e);
            // If no problems, and the number of participants to here from is 0, then we're done
        } else if (state == ISharedObjectContainerTransaction.VOTING && participantIDs.size() == 0) {
            // Success!
            trace("votingCompleted");
            return true;
        }
        // Else continue waiting
        return false;
    }
}