public ID[] getGroupMemberIDs() {

package org.eclipse.ecf.internal.impl.standalone;

import java.io.IOException;
import java.io.Serializable;
import java.lang.reflect.Constructor;
import java.net.URL;
import java.net.URLClassLoader;
import java.security.AccessController;
import java.security.Permissions;
import java.security.PrivilegedAction;
import java.security.PrivilegedActionException;
import java.security.PrivilegedExceptionAction;
import java.util.Enumeration;
import java.util.Map;
import java.util.Vector;

import org.eclipse.ecf.core.ISharedObject;
import org.eclipse.ecf.core.ISharedObjectConfig;
import org.eclipse.ecf.core.ISharedObjectConnector;
import org.eclipse.ecf.core.ISharedObjectContainer;
import org.eclipse.ecf.core.ISharedObjectContainerConfig;
import org.eclipse.ecf.core.ISharedObjectContainerListener;
import org.eclipse.ecf.core.ISharedObjectContainerTransaction;
import org.eclipse.ecf.core.ISharedObjectContext;
import org.eclipse.ecf.core.SharedObjectAddException;
import org.eclipse.ecf.core.SharedObjectConnectException;
import org.eclipse.ecf.core.SharedObjectContainerJoinException;
import org.eclipse.ecf.core.SharedObjectCreateException;
import org.eclipse.ecf.core.SharedObjectDescription;
import org.eclipse.ecf.core.SharedObjectDisconnectException;
import org.eclipse.ecf.core.SharedObjectInitException;
import org.eclipse.ecf.core.SharedObjectNotFoundException;
import org.eclipse.ecf.core.events.ContainerEvent;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.util.AbstractFactory;
import org.eclipse.ecf.core.util.Event;
import org.eclipse.ecf.internal.comm.AsynchConnectionEvent;
import org.eclipse.ecf.internal.comm.ConnectionEvent;
import org.eclipse.ecf.internal.comm.DisconnectConnectionEvent;
import org.eclipse.ecf.internal.comm.IAsynchConnection;
import org.eclipse.ecf.internal.comm.IAsynchConnectionEventHandler;
import org.eclipse.ecf.internal.comm.ISynchConnectionEventHandler;
import org.eclipse.ecf.internal.comm.SynchConnectionEvent;
import org.eclipse.ecf.internal.impl.standalone.gmm.Item;
import org.eclipse.ecf.internal.util.queue.SimpleQueueImpl;

public abstract class SharedObjectContainer implements ISharedObjectContainer {
	public static Debug debug =
		Debug.create(SharedObjectContainer.class.getName());
	// Messages
	public static final String CONTAINERCLOSING = "space is closing";
	public static final String BADPARAMDATA = "invalid parameter";
	public static final String BADDATA = "invalid data";
	public static final String JOINFAIL = "join fail";
	public static final String NOTCONNECTED = "not connected";
	public static final String CONNECTEDFAIL = "currently connected";
	public static final String CONNECTINGFAIL = "currently connecting";
	public static final String CONNECTLOCALLYREFUSED = "join fail locally";
	public static final String SHAREDOBJECTALREADYEXISTS =
		"shared object already exists: ";

    protected static final Object[] nullArgs = new Object[0];
    protected static final Class[] nullTypes = new Class[0];

	ISharedObjectContainerConfig config;
	protected SharedObjectContainerManager sharedObjectContainerManager;
	long sequenceNumber;
	MsgReceiver msgReceiver;
	boolean isClosing = false;
	ThreadGroup sharedObjectLoadingThreadGroup;
	ThreadGroup sharedObjectThreadGroup;
	
	public SharedObjectContainer(ISharedObjectContainerConfig config) throws SecurityException {
	    this.config = config;
		sharedObjectContainerManager = new SharedObjectContainerManager(this, new Item(config.getID()));
		sequenceNumber = 0;
		msgReceiver = new MsgReceiver();
		sharedObjectLoadingThreadGroup = getParentLoadingTG();
		sharedObjectThreadGroup = getParentSharedObjectTG();
	}
	protected ThreadGroup getParentLoadingTG() {
		return new ThreadGroup(getID() + ":LoadingThreads");
	}
	protected ThreadGroup getParentSharedObjectTG() {
		return new ThreadGroup(getID() + ":SharedObjectThreads");
	}
	public final ID getID() {
		return config.getID();
	}
	public ISharedObjectContainerConfig getConfig() {
	    return config;
	}
	public final int getItemSize() {
		return sharedObjectContainerManager.getSize();
	}
	public final int getMaxItems() {
		return sharedObjectContainerManager.getMaxItems();
	}
	public final int setMaxItems(int max) {
		return sharedObjectContainerManager.setMaxItems(max);
	}
	public final ID[] getOtherItemsIDs() {
		return sharedObjectContainerManager.getOtherItemIDs();
	}
	public final ID[] getActiveObjIDs() {
		return sharedObjectContainerManager.getActiveKeys();
	}
	public final boolean isClosing() {
		return isClosing;
	}
	public abstract boolean isServer();
	public abstract boolean isManager();
	/*
	public ID createRepObject(
		ID newID,
		String className,
		URL[] codeBase,
		String[] argTypes,
		Object[] params)
		throws Exception {
		if (isClosing)
			throw new IllegalStateException(CONTAINERCLOSING);
		if (newID == null || className == null)
			throw new IllegalAccessError(BADPARAMDATA);
		SharedObjectDescription info =
			new SharedObjectDescription(
				getID(),
				className,
				codeBase,
				argTypes,
				params,
				0L);
		info.setObjID(newID);
		logSpaceEvent(LOGLOCALCREATE, info);
		addLocalAndWait(info, load(info));
		return newID;
	}
	*/
	/*
	public ID addRepObject(ID objID, URL[] codeBase, ISharedObject obj)
		throws RepObjectException, AbortException, IllegalAccessException {
		if (isClosing)
			throw new IllegalStateException(CONTAINERCLOSING);
		if (objID == null || obj == null)
			throw new IllegalAccessException(BADPARAMDATA);
		if (Debug.ON && debug != null) {
			debug.msg(
				"addRepObject(" + objID + ", " + codeBase + ", " + obj);
		}
		// First, create init data for this object
		SharedObjectDescription info =
			new SharedObjectDescription(
				getID(),
				obj.getClass().getName(),
				codeBase,
				null,
				0L);
		info.setObjID(objID);
		logSpaceEvent(LOGLOCALADD, info);
		// Do the real work
		addLocalAndWait(info, obj);
		return objID;
	}
	protected void addLocalAndWait(SharedObjectDescription info, ISharedObject obj)
		throws IllegalAccessException, RepObjectException, AbortException {
		addLocal(info, obj);
		// If object implements TransactionRepObject interface, call waitForCompleted method
		if (obj instanceof TransactionRepObject
			&& getID().equals(info.myHomeID)) {
			if (Debug.ON && debug != null) {
				debug.msg(
					"addLocalAndWait.  Waiting on TransactionRepObject "
						+ obj
						+ " for completion");
			}
			// Wait as defined by object
			 ((TransactionRepObject) obj).waitForCommitted();
		}
	}
	*/
	/*
	protected void addLocal(SharedObjectDescription info, ISharedObject obj)
		throws IllegalAccessException, RepObjectException {
		RepObjConfig aConfig = makeRepObjConfig(info, null);
		// Log that this is happening
		logSpaceEvent(LOGINIT, aConfig);
		// Call init
		try {
			obj.init(aConfig);
			boolean res =
				sharedObjectContainerManager.addRepObj(
					new SharedObjectWrapper(
						aConfig,
						obj,
						this,
						getRepObjectThreadGroup(info, aConfig)));
			if (!res)
				throw new RepObjectException(
					SHAREDOBJECTALREADYEXISTS + aConfig.getID());
			;
		} catch (RepObjectException e) {
			logSpaceException(LOGCREATEEXCEPTION, e, info);
			throw e;
		}
		// Create SharedObjectWrapper, and add to local membership manager
		logSpaceEvent(LOGACTIVATE, aConfig);
	}
	*/
	protected ISharedObject load(final SharedObjectDescription info)
		throws Exception {
		ClassLoader contextClassLoader = Thread.currentThread().getContextClassLoader();
		if (contextClassLoader == null) contextClassLoader = SharedObjectContainer.class.getClassLoader();
	    Map dict = info.getProperties();
	    String [] constructorArgTypes = null;
	    Object [] constructorArgs = null;
	    if (dict != null) {
	        constructorArgTypes = (String []) dict.get("constructorArgTypes");
	        constructorArgs = (Object []) dict.get("constructorArgs");
	    }
		final ClassLoader cl = getClassLoader(contextClassLoader,info);
		Class argTypes[] = AbstractFactory.getClassesForTypes(constructorArgTypes,constructorArgs,cl);
		final Class[] types = argTypes;

		Object [] args = constructorArgs;
		if (args == null)
			args = new Object[0];
		
		final Object [] theArgs = args;
		final Class newClass = Class.forName(info.getClassname(), true, cl);
		Object newObject = null;
		try {
			newObject =
				AccessController.doPrivileged(new PrivilegedExceptionAction() {
				public Object run() throws Exception {
					Constructor aConstructor = newClass.getConstructor(types);
					logContainerEvent(null, info);
					aConstructor.setAccessible(true);
					Thread.currentThread().setContextClassLoader(cl);
					return aConstructor.newInstance(theArgs);
				}
			});
		} catch (java.security.PrivilegedActionException e) {
			logContainerException(null, e.getException(), info);
			throw e.getException();
		}
		return verifyRepObjType(info, newObject);
	}
	public abstract void joinSpace(ID remoteSpace, Serializable data)
		throws IOException;
	public abstract void leaveSpace();

	protected void destroyItems(boolean includeLocal) {
		synchronized (sharedObjectContainerManager) {
			Object[] members = sharedObjectContainerManager.getItems();
			for (int i = 0; i < members.length; i++) {
				ID id = (ID) ((Item) members[i]).getID();
				if (includeLocal || !id.equals(getID())) {
					memberLeave(
						id,
						(IAsynchConnection) ((Item) members[i]).getData());
				}
			}
		}
	}
	public final void terminate(long timeout) throws SecurityException {
		if (Debug.ON && debug != null) {
			debug.msg("terminate(" + timeout + ")");
		}
		// First, check to see that caller thread has permission to access
		// the two thread groups.
		sharedObjectLoadingThreadGroup.checkAccess();
		sharedObjectThreadGroup.checkAccess();
		if (Debug.ON && debug != null) {
			debug.msg(
				"terminate.  Caller thread has access to terminating threads.");
		}
		logContainerEvent(null, new Long(timeout));
		// No group member or replicated object changes while the member removal is going on
		synchronized (sharedObjectContainerManager) {
			// First, set closing flag.  This prevents other threads from doing things to
			// prevent shutdown.  Once this is set, this space is a goner.
			if (isClosing) {
				if (Debug.ON && debug != null) {
					debug.msg(
						"terminate.  Space already terminated.");
				}
				return;
			} else
				isClosing = true;
			// Allow subclasses to run termination code.
			subclassOverrideableTerminate();

			// Then destroy all members.  This will forcibly close all connections to remote spaces,
			// destroy client replications, and also destroy host replications if includeHosts is true
			if (Debug.ON && debug != null) {
				debug.msg("terminate.  Calling destroyMembers...");
			}
			destroyItems(true);
			if (Debug.ON && debug != null) {
				debug.msg("terminate.  DestroyMembers complete.");
			}
		}
		if (Debug.ON && debug != null) {
			debug.msg("terminate.  Calling loading group interrupt.");
		}
		try {
			// If any loading threads, just interrupt them...they don't get a chance to complete
			sharedObjectLoadingThreadGroup.interrupt();
			synchronized (this) {
				notifyAll();
			}
		} catch (Exception e) {
		}

		long endTime = System.currentTimeMillis() + timeout;
		// Everything should now be going away.
		// Before we forcibly interrupt executing threads, however, we will wait timeout ms
		try {
			while (checkForRunningThreads()
				&& System.currentTimeMillis() < endTime) {
				if (Debug.ON && debug != null) {
					debug.msg(
						"terminate.  Waiting for " + timeout / 10 + "ms");
				}
				synchronized (this) {
					wait(timeout / 10);
				}
			}
		} catch (InterruptedException e) {
		} finally {
			// Do the nasty
			interruptThreads();
			logContainerEvent(null, getID());
			if (Debug.ON && debug != null) {
				debug.msg("termination complete for " + getID());
			}
		}
	}
	protected boolean checkForRunningThreads() {
		int activeCount = sharedObjectThreadGroup.activeCount();
		int activeGroupCount = sharedObjectThreadGroup.activeGroupCount();
		if (Debug.ON && debug != null) {
			debug.msg(
				"checkForRunningThreads().  Active is "
					+ activeCount
					+ ".  ActiveGroup is "
					+ activeGroupCount);
		}
		return ((activeCount + activeGroupCount) > 0);
	}

	protected void subclassOverrideableTerminate() {
		// Allow subclasses to provide termination code
	}

	protected void interruptThreads() {
		if (Debug.ON && debug != null) {
			debug.msg("interruptThreads()");
		}
		try {
			// Interrupt replicated object threads
			sharedObjectThreadGroup.interrupt();
			synchronized (this) {
				notifyAll();
			}
		} catch (Exception e) {
		}
	}

	protected void sendMsg(ID toID, byte msg, Serializable data)
		throws IOException {
		synchronized (sharedObjectContainerManager) {
			ID ourID = getID();
			if (!ourID.equals(toID))
				queuePacket(new ContainerPacket(ourID, toID, getSeqNumber(), msg, data));
		}
	}
	protected ID[] sendCreateMsg(ID toID, SharedObjectDescription createInfo)
		throws IOException {
		ID[] ids = null;
		if (toID == null) {
			synchronized (sharedObjectContainerManager) {
				// Send message to all
			    // XXX TODO
				//sendMsg(null, ContainerMessage.CREATE_REPOBJ, createInfo);
				ids = getOtherItemsIDs();
			}
		} else {
			if (getID().equals(toID)) {
				ids = new ID[0];
			} else {
			    // XXX TODO
				//sendMsg(toID, ContainerMessage.CREATE_REPOBJ, createInfo);
				ids = new ID[1];
				ids[0] = toID;
			}
		}
		return ids;
	}
	protected void deliverEventToSharedObject(ID fromID, ID target, Event msg)
		throws SharedObjectNotFoundException {
		if (target == null)
			throw new SharedObjectNotFoundException();
		synchronized (sharedObjectContainerManager) {
			SharedObjectWrapper aMeta = sharedObjectContainerManager.getFromActive(target);
			if (aMeta == null)
				throw new SharedObjectNotFoundException(target.getName());
			// Deliver message
			aMeta.deliverEventFromSharedObject(fromID, msg);
		}
	}
	protected void deliverEventToSharedObjects(ID fromID, ID[] targets, Event msg) {
		synchronized (sharedObjectContainerManager) {
			if (targets == null)
				targets = sharedObjectContainerManager.getActiveKeys();
			for (int i = 0; i < targets.length; i++) {
				try {
					if (!fromID.equals(targets[i])) {
						deliverEventToSharedObject(
							fromID,
							targets[i],
							null
							/*
							new SharedObjectEvent(
								msg.getClassName(),
								msg.getMethodName(),
								msg.getArgs())
								*/
							);
								
					}
				} catch (SharedObjectNotFoundException e) {
					logContainerException(
						null,
						e,
						targets[i]);
				}
			}
		}
	}
	abstract protected void queuePacket(ContainerPacket packet) throws IOException;
	abstract protected void forwardToRemote(
		ID from,
		ID to,
		byte msg,
		Serializable data)
		throws IOException;
	abstract protected void forwardExcluding(
		ID from,
		ID excluding,
		byte msg,
		Serializable data)
		throws IOException;
	protected final void forward(
		ID fromID,
		ID toID,
		byte msg,
		Serializable data)
		throws IOException {
		if (toID == null) {
			forwardExcluding(fromID, fromID, msg, data);
		} else {
			forwardToRemote(fromID, toID, msg, data);
		}
	}

	protected void handleAsynchEvent(AsynchConnectionEvent evt)
		throws IOException, IllegalAccessException {
		if (isClosing)
			throw new IllegalStateException(CONTAINERCLOSING);
		processAsynchPacket(verifyPacket((Serializable) evt.getOData()));
	}
	protected void processAsynchPacket(ContainerPacket p) throws IOException, IllegalAccessException {
		switch (p.msg) {
			case ContainerMessage.CHANGE :
				handleChangeMsg(p.fromID, p.toID, p.sequence, p.theData);
				break;
			case ContainerMessage.CREATE_REPOBJ :
				handleCreateMsg(p.fromID, p.toID, p.sequence, p.theData);
				break;
			case ContainerMessage.CREATE_REPOBJ_RESP :
				handleCreateRespMsg(p.fromID, p.toID, p.sequence, p.theData);
				break;
			case ContainerMessage.REPOBJ_MSG :
				handleSharedObjectEvent(p.fromID, p.toID, p.sequence, p.theData);
				break;
			case ContainerMessage.DESTROY_REPOBJ :
				handleDestroyMsg(p.fromID, p.toID, p.sequence, p.theData);
				break;
			default :
				if (Debug.ON && debug != null) {
					debug.msg("UNRECOGNIZED MESSAGE...throwing");
				}
				IllegalAccessException e =
					new IllegalAccessException(
						BADDATA
							+ ":"
							+ p.fromID
							+ ":"
							+ p.toID
							+ ":"
							+ p.sequence
							+ ":"
							+ p.msg);
				logContainerException(null, e, null);
				throw e;
		}
	}

	protected ContainerPacket verifyPacket(Serializable data) throws IOException, IllegalAccessException {
		ContainerPacket p = null;
		try {
			p = (ContainerPacket) data;
		} catch (ClassCastException e) {
			throw new IllegalAccessException(BADDATA + ":" + data);
		}
		return p;
	}

	protected Serializable handleSynchEvent(SynchConnectionEvent evt)
		throws IOException, IllegalAccessException {
		if (isClosing)
			throw new IllegalStateException(CONTAINERCLOSING);
		return processSynchPacket((IAsynchConnection) evt.getConnection(), verifyPacket((Serializable) evt.getOData()));
	}
	protected Serializable processSynchPacket(
		IAsynchConnection conn,
		ContainerPacket aPacket)
		throws IOException {
		if (aPacket.fromID == null) {
			IllegalAccessException e =
				new IllegalAccessException(
					BADDATA + ":" + aPacket.fromID + ":" + aPacket.toID);
			logContainerException(null, e, aPacket);
		}
		if (aPacket.msg == ContainerMessage.LEAVE) {
			handleSpaceLeave(aPacket);
			synchronized (sharedObjectContainerManager) {
				memberLeave(aPacket.fromID, conn);
			}
		}
		return null;
	}

	protected Serializable getLeaveData(ID leaveReceiver) {
	    /*
		RepSpaceLeaveListener l = null;
		synchronized (myLeaveListenerLock) {
			l = myLeaveListener;
		}
		Serializable result = null;
		if (l != null) {
			result = l.getLeaveData(getID(), leaveReceiver);
		}
		if (Debug.ON && debug != null) {
			debug.msg(
				"getLeaveData(" + leaveReceiver + ") returns " + result);
		}
		return result;
		*/
	    return null;
	}
	protected void handleSpaceLeave(ContainerPacket aPacket) {
		if (aPacket == null)
			return;
		if (Debug.ON && debug != null) {
			debug.msg(
				"handleSpaceLeave("
					+ aPacket.fromID
					+ ","
					+ aPacket.theData
					+ ")");
		}
		/*
		RepSpaceLeaveListener l = null;
		synchronized (myLeaveListenerLock) {
			l = myLeaveListener;
		}
		if (l != null) {
			l.handleSpaceLeave(getID(), aPacket.fromID, aPacket.theData);
		}
		*/
	}
	protected void handleDisconnectEvent(DisconnectConnectionEvent evt) {
		processDisconnect((IAsynchConnection) evt.getConnection(), evt.getException(), (SimpleQueueImpl) evt.getData());
	}
	protected void processDisconnect(
		IAsynchConnection conn,
		Throwable e,
		SimpleQueueImpl unsent) {
		// Get GMM lock (no group membership changes during this)
		synchronized (sharedObjectContainerManager) {
			if (e != null) {
				ID memID = getIDForConnection(conn);
				if (memID != null) {
					memberLeave(memID, conn);
				}
			}
			handleUnsent(unsent, e);
		}
	}
	protected abstract void handleChangeMsg(
		ID fromID,
		ID toID,
		long seqNum,
		Serializable data)
		throws IOException;
	protected void handleCreateMsg(
		ID fromID,
		ID toID,
		long seqNum,
		Serializable data)
		throws IOException, IllegalAccessException {
		SharedObjectDescription createInfo = null;
		try {
			createInfo = (SharedObjectDescription) data;
			if (fromID == null
				|| createInfo == null
				|| createInfo.getID() == null
				|| createInfo.getHomeID() == null
				|| createInfo.getClassname() == null)
				throw new Exception();
		} catch (Exception e) {
			IllegalAccessException t =
				new IllegalAccessException(
					BADDATA
						+ ":"
						+ fromID
						+ ":"
						+ toID
						+ ":"
						+ seqNum
						+ ":"
						+ ContainerMessage.CREATE_REPOBJ);
			logContainerException(null, t, data);
			throw t;
		}
		Object obj = checkCreateObject(fromID, toID, seqNum, createInfo);
		if (obj != null && (toID == null || toID.equals(getID()))) {
			// Then check to see if returned object was permissions object...if so, then
			// pass along to LoadingRepObject
			LoadingSharedObject newObj =
				new LoadingSharedObject(createInfo, handleObjectCheckResult(obj));
			synchronized (sharedObjectContainerManager) {
				// Put into membership manager.  This starts thread for retrieving class bytes, etc.
				if (!sharedObjectContainerManager.addToLoading(newObj)) {
					// Instance of object already there.  Send failure msg back.
					try {
						sendMsg(
							fromID,
							ContainerMessage.CREATE_REPOBJ_RESP,
							new ContainerMessage.CreateResponse(
								createInfo.getID(),
								new SharedObjectAddException(
									createInfo.getID() + " already present"),
								createInfo.getIdentifier()));
					} catch (Exception e1) {
						// If an exception is thrown by this, disconnection has already occurred,
						// so no need to rethrow
						if (Debug.ON && debug != null) {
							debug.dumpStack(
								e1,
								"Exception sending create failure message back to "
									+ fromID);
						}
						logContainerException(null, e1, null);
					}
				}
				// Forward to other remote repspace instances and return.  This only has
				// effect if this repspace is a server.
				forward(fromID, toID, ContainerMessage.CREATE_REPOBJ, data);
				return;
			}
		}
		// Even if we don't create the object, if we're a server, we'll forward the message
		// to others.  Servers can prevent this by throwing an ioexception from checkCreateObject.
		synchronized (sharedObjectContainerManager) {
			forward(fromID, toID, ContainerMessage.CREATE_REPOBJ, data);
		}
	}
	protected Permissions handleObjectCheckResult(Object obj) {
		if (obj == null)
			return null;
		Permissions p = null;
		if (obj instanceof Vector) {
			Vector v = (Vector) obj;
			for (java.util.Enumeration e = v.elements();
				e.hasMoreElements();
				) {
				Object o = e.nextElement();
				if (o instanceof java.security.Permission) {
					if (p == null)
						p = new Permissions();
					p.add((java.security.Permission) o);
				}
			}
		}
		return p;
	}
	protected Object checkCreateObject(
		ID fromID,
		ID toID,
		long seqNum,
		SharedObjectDescription constructor)
		throws IOException {
		if (Debug.ON && debug != null) {
			debug.msg(
				"checkCreateObject("
					+ fromID
					+ ", "
					+ toID
					+ ", "
					+ seqNum
					+ ", "
					+ constructor);
		}
		/*
		synchronized (myCreateHandlerLock) {
			if (checkCreateHandler != null) {
				logSpaceEvent(LOGCHECKCREATE, constructor);
				return checkCreateHandler.checkCreateObject(
					fromID,
					toID,
					seqNum,
					constructor);
			} else
				// By default, allow the object to be created by returning reference to self
				return this;
		}
		*/
		return this;
	}
	protected void handleCreateRespMsg(
		ID fromID,
		ID toID,
		long seqNum,
		Serializable data)
		throws IOException, IllegalAccessException {
		ContainerMessage.CreateResponse resp = null;
		try {
			resp = (ContainerMessage.CreateResponse) data;
			if (fromID == null || toID == null || resp == null)
				throw new Exception();
		} catch (Exception e) {
			IllegalAccessException t =
				new IllegalAccessException(
					BADDATA
						+ ":"
						+ fromID
						+ ":"
						+ toID
						+ ":"
						+ seqNum
						+ ":"
						+ ContainerMessage.CREATE_REPOBJ_RESP);
			logContainerException(null, t, data);
			throw t;
		}
		synchronized (sharedObjectContainerManager) {
			if (toID != null && toID.equals(getID())) {
				// Get SharedObjectWrapper from local membership manager
				SharedObjectWrapper aMeta =
					sharedObjectContainerManager.getFromActive(resp.myObjID);
				if (aMeta == null) {
					// Not found...just log;
					logContainerException(
						null,
						new SharedObjectNotFoundException(resp.myObjID.getName()),
						null);
					return;
				}
				// Otherwise, deliver message locally
				aMeta.createMsgResp(fromID, resp);
			} else {
				forwardToRemote(
					fromID,
					toID,
					ContainerMessage.CREATE_REPOBJ_RESP,
					data);
			}
		}
	}
	protected void handleSharedObjectEvent(
		ID fromID,
		ID toID,
		long seqNum,
		Serializable data)
		throws IOException, IllegalAccessException {
		ContainerMessage.SharedObjectPacket aPacket = null;
		try {
			aPacket = (ContainerMessage.SharedObjectPacket) data;
			if (fromID == null || aPacket == null || aPacket.myFromID == null)
				throw new Exception();
		} catch (Exception e) {
			IllegalAccessException t =
				new IllegalAccessException(
					BADDATA
						+ ":"
						+ fromID
						+ ":"
						+ toID
						+ ":"
						+ seqNum
						+ ":"
						+ ContainerMessage.REPOBJ_MSG);
			logContainerException(null, t, null);
			throw t;
		}
		synchronized (sharedObjectContainerManager) {
			if (toID == null || toID.equals(getID())) {
				SharedObjectWrapper aMeta =
					sharedObjectContainerManager.getFromActive(aPacket.myFromID);
				if (aMeta == null) {
					// Not found...just log;
					logContainerException(
						null,
						new SharedObjectNotFoundException(aPacket.myFromID.getName()),
						null);
				} else
					aMeta.deliverObjectFromRemote(fromID, aPacket.myData);
			}
			// forward on in either case
			forward(fromID, toID, ContainerMessage.REPOBJ_MSG, data);
		}
	}
	protected void handleDestroyMsg(
		ID fromID,
		ID toID,
		long seqNum,
		Serializable data)
		throws IOException, IllegalAccessException {
		ContainerMessage.SharedObjectDestroyInfo info = null;
		try {
			info = (ContainerMessage.SharedObjectDestroyInfo) data;
			if (fromID == null || info == null || info.myObjID == null)
				throw new Exception();
		} catch (Exception e) {
			IllegalAccessException t =
				new IllegalAccessException(
					BADDATA
						+ ":"
						+ fromID
						+ ":"
						+ toID
						+ ":"
						+ seqNum
						+ ":"
						+ ContainerMessage.DESTROY_REPOBJ);
			logContainerException(null, t, null);
			throw t;
		}
		synchronized (sharedObjectContainerManager) {
			if (sharedObjectContainerManager.isLoading(info.myObjID)) {
				sharedObjectContainerManager.removeSharedObjectFromLoading(info.myObjID);
			} else {
				try {
					sharedObjectContainerManager.destroySharedObject(info.myObjID);
				} catch (Exception e) {
					logContainerException(
						null,
						e,
						info.myObjID);
				}
			}
			// forward on
			forward(fromID, toID, ContainerMessage.DESTROY_REPOBJ, data);
		}
	}
	protected void handleUnsent(SimpleQueueImpl unsent, Throwable e) {
		Object[] msgs = unsent.flush();
		if (msgs != null) {
			for (int i = 0; i < msgs.length; i++) {
				try {
					ContainerPacket p = (ContainerPacket) msgs[i];
					if (p.msg == ContainerMessage.REPOBJ_MSG) {
						ContainerMessage.SharedObjectPacket repPacket =
							(ContainerMessage.SharedObjectPacket) p.theData;
						SharedObjectWrapper aMeta =
							sharedObjectContainerManager.getFromActive(
								repPacket.myFromID);
						if (aMeta != null) {
							aMeta.deliverRemoteMessageFailed(
								p.toID,
								repPacket.myData,
								e);
						}
					}
				} catch (ClassCastException except) {
					// Ignore...wrong type of message
				}
			}
		}
	}
	protected abstract ID getIDForConnection(IAsynchConnection conn);

	protected ClassLoader getClassLoader(final ClassLoader contextClassLoader, final SharedObjectDescription aConfig) {
		final URL[] urls = null;
		return (
			ClassLoader) AccessController.doPrivileged(new PrivilegedAction() {
			public Object run() {
				ClassLoader loader = null;
				if (urls == null) {
					// Use same classloader that was used to load this class
					loader = contextClassLoader;
				} else {
					loader =
						new URLClassLoader(urls, contextClassLoader);
				}
				return loader;
			}
		});
	}
	protected ISharedObject verifyRepObjType(
		SharedObjectDescription config,
		Object newObject)
		throws ClassCastException {
		return (ISharedObject) newObject;
	}
	protected ISharedObjectConfig makeRepObjConfig(
		SharedObjectDescription aConfig,
		Permissions perms)
		throws IllegalAccessException {
	    // XXX TODO
		//return new RepObjConfig(aConfig, makeReference(aConfig, perms));
	    return null;
	}
	protected ISharedObjectContext makeReference(
		SharedObjectDescription aConfig,
		Permissions perms)
		throws IllegalAccessException {
		if (Debug.ON && debug != null) {
			debug.msg(
				"makeReference(" + aConfig + ", " + perms + ")");
		}
		// XXX TODO
		//return new RepSpaceReference(this, aConfig.myObjID, perms);
		return null;
	}
	protected ThreadGroup getLoadingThreadGroup(SharedObjectDescription createData) {
		// Return null.  Subclasses may override as desired.
		return sharedObjectLoadingThreadGroup;
	}
	protected ThreadGroup getSharedObjectThreadGroup(
		SharedObjectDescription info,
		ISharedObjectConfig config) {
		// Return null.  Subclasses may override as desired.
		return sharedObjectThreadGroup;
	}
	protected Thread getSharedObjectThread(
		ID identity,
		ThreadGroup tg,
		Runnable run,
		String name) {
		return new Thread(tg, run, name);
	}
	protected void logContainerEvent(String msg, Object param) {
	}
	protected void logContainerException(String msg, Exception e, Object param) {
	}
	protected void logSharedObjectEvent(ID repobjID, String msg, Object param) {
	}
	protected void logSharedObjectException(
		ID repobjID,
		String msg,
		Exception e,
		Object param) {
	}

	protected void moveFromLoadingToActive(SharedObjectWrapper ro)
		throws SharedObjectNotFoundException {
		sharedObjectContainerManager.moveFromLoadingToActive(ro);
	}

	protected void removeFromLoading(ID id) {
		sharedObjectContainerManager.removeSharedObjectFromLoading(id);
	}

	synchronized final long getSeqNumber() {
		return sequenceNumber++;
	}
	protected boolean addNewRemoteItem(ID itemID) {
		return addNewRemoteItem(itemID, null);
	}
	protected boolean addNewRemoteItem(ID itemID, Object data) {
		return sharedObjectContainerManager.addItem(new Item(itemID, data));
	}
	protected boolean removeRemoteItem(ID itemID) {
		logContainerEvent(null, itemID);
		return sharedObjectContainerManager.removeItem(itemID);
	}
	protected void memberLeave(ID leaveID, IAsynchConnection conn) {
		// No changes to group membership while this is happening
		if (removeRemoteItem(leaveID)) {
			try {
				forwardExcluding(
					getID(),
					leaveID,
					ContainerMessage.CHANGE,
					new ContainerMessage.ContainerItemChange(leaveID, false));
			} catch (IOException e) {
				if (Debug.ON && debug != null) {
					debug.dumpStack(
						e,
						"memberLeave.  Exception calling forwardExcluding");
				}
				logContainerException(null, e, null);

			}
		}
		// disconnect connection
		killConnection(conn);
	}
	protected final void killConnection(IAsynchConnection conn) {
		try {
			if (conn != null)
				conn.disconnect();
		} catch (IOException e) {
			if (Debug.ON && debug != null) {
				debug.dumpStack(e, "Exception disconnecting " + conn);
			}
			logContainerException(null, e, conn);
		}
	}
	public ISharedObject getSharedObject(ID objID) {
		if (objID == null) return null;
		SharedObjectWrapper meta = sharedObjectContainerManager.getFromActive(objID);
		if (meta == null) return null;
		return meta.sharedObject;
	}

	public ISharedObject getSharedObjectFromAny(ID objID)
		throws SharedObjectNotFoundException {
		if (objID == null)
			throw new SharedObjectNotFoundException();
		return sharedObjectContainerManager.getFromAny(objID).sharedObject;
	}
	public void destroySharedObject(ID id) throws SharedObjectNotFoundException {
		if (id == null)
			throw new SharedObjectNotFoundException();
		logContainerEvent(null, id);
		sharedObjectContainerManager.destroySharedObject(id);
	}
	public void destroySharedObjectSelf(ID id) throws SharedObjectNotFoundException {
		if (id == null)
			throw new SharedObjectNotFoundException();
		SharedObjectWrapper meta = sharedObjectContainerManager.getFromActive(id);
		if (meta == null)
			throw new SharedObjectNotFoundException();
		meta.destroySelf();
	}
	protected void notifySharedObjectActivated(ID obj) {
		logContainerEvent(null, obj);
		sharedObjectContainerManager.notifyOthersActivated(obj);
	}
	protected void notifySharedObjectDeactivated(ID obj) {
		logContainerEvent(null, obj);
		sharedObjectContainerManager.notifyOthersDeactivated(obj);
	}
	protected final class MsgReceiver implements IAsynchConnectionEventHandler, ISynchConnectionEventHandler {

		public void handleDisconnectEvent(ConnectionEvent evt) {
			SharedObjectContainer.this.handleDisconnectEvent(
				(DisconnectConnectionEvent) evt);
		}
		public boolean handleSuspectEvent(ConnectionEvent event) {
			// Do nothing
			// Returning true indicates that further processing of this
			// event should continue
			return true;
		}
		public ClassLoader getClassLoaderForID(ID id) {
			return this.getClass().getClassLoader();
		}
		public void handleAsynchEvent(ConnectionEvent evt) throws IOException {
			// Pass to handler
		    try {
		        SharedObjectContainer.this.handleAsynchEvent((AsynchConnectionEvent) evt);
		    } catch (IllegalAccessException e) {
		        throw new IOException("Illegal data access handling event "+evt);
		    }
		}
		public Object handleSynchEvent(ConnectionEvent evt)
			throws IOException {
			// Handle synch packet
		    try {
				return SharedObjectContainer.this.handleSynchEvent((SynchConnectionEvent) evt);
		    } catch (IllegalAccessException e) {
		        throw new IOException("Illegal data access handling event "+evt);
		    }
		}
		
		public Object getAdapter(Class clazz) {
		    return null;
		}
	}
	protected final class LoadingSharedObject implements ISharedObject {
		Thread runnerThread;
		SharedObjectDescription sharedObjectDescription;
		Permissions loadingPerms;

		LoadingSharedObject(SharedObjectDescription create) {
			sharedObjectDescription = create;
		}

		LoadingSharedObject(SharedObjectDescription create, Permissions perms) {
			sharedObjectDescription = create;
			loadingPerms = perms;
		}

		void start() {
			if (runnerThread == null) {
				runnerThread =
					(
						Thread) AccessController
							.doPrivileged(new PrivilegedAction() {
					public Object run() {
						return getThread();
					}
				});
				runnerThread.start();
			}
		}
		Thread getThread() {
			return new Thread(getLoadingThreadGroup(sharedObjectDescription), new Runnable() {
				public void run() {
					try {
						if (Debug.ON && debug != null) {
							debug.msg(
								"Starting loading of object "
									+ sharedObjectDescription.getID());
						}
						// Check to make sure thread has not been interrupted and space is not closing...if it has, throw
						if (Thread.currentThread().isInterrupted()
							|| isClosing)
							throw new InterruptedException("Interrupted");
						logContainerEvent(null, sharedObjectDescription);
						// First load given object
						ISharedObject obj = load(sharedObjectDescription);
						if (Debug.ON && debug != null) {
							debug.msg(
								"Calling init for object " + sharedObjectDescription.getID());
						}
						// Get config info for new object
						ISharedObjectConfig aConfig =
							makeRepObjConfig(sharedObjectDescription, loadingPerms);
						// Log that this is happening
						logContainerEvent(null, aConfig);
						// Call init method on new object.
						obj.init(aConfig);
						// Check to make sure thread has not been interrupted...if it has, throw
						if (Thread.currentThread().isInterrupted()
							|| isClosing)
							throw new InterruptedException("Interrupted");

						if (Debug.ON && debug != null) {
							debug.msg(
								"Putting object "
									+ sharedObjectDescription.getID()
									+ " in local membership manager");
						}
						// If not currently *on* loading list, does nothing.
						logContainerEvent(null, aConfig);
						// Create meta object and move from loading to active list.
						SharedObjectContainer.this.moveFromLoadingToActive(
							new SharedObjectWrapper(
								aConfig,
								obj,
								SharedObjectContainer.this,
								getSharedObjectThreadGroup(sharedObjectDescription, aConfig)));
					} catch (Exception e) {
						if (Debug.ON && debug != null) {
							debug.dumpStack(
								e,
								"Exception loading new object "
									+ sharedObjectDescription.getID());
						}
						SharedObjectContainer.this.removeFromLoading(sharedObjectDescription.getID());
						try {
							SharedObjectContainer.this.sendMsg(
								sharedObjectDescription.getID(),
								ContainerMessage.CREATE_REPOBJ_RESP,
								new ContainerMessage.CreateResponse(
									sharedObjectDescription.getID(),
									e,
									sharedObjectDescription.getIdentifier()));
						} catch (Exception e1) {
							logContainerException(null, e1, null);
							// If this message send fails, we're doomed anyway
							if (Debug.ON && debug != null) {
								debug.dumpStack(
									e1,
									"Exception sending create failure message for object "
										+ sharedObjectDescription.getID());
							}
						}
						logContainerException(
							"loadingRunner.  Exception loading for "
								+ sharedObjectDescription.getID(),
							e,
							null);
					}
				}
			}, "LoadingRunner for " + sharedObjectDescription.getID());
		}
		// ISharedObject
		public void init(ISharedObjectConfig aConfig) throws SharedObjectInitException {
			// Not relevant for this class
		}
		public void handleEvent(Event msg) {
			// Not relevant for this class...might want to handle a remote destroy message eventually.
		}
		public void handleEvents(Event [] msgs) {
			// Not relevant for this class...might want to handle a remote destroy message eventually.
		}
		public void dispose(ID spaceID) {
			// Not relevant for this class
		}
		public Object getAdapter(Class clazz) {
		    return null;
		}
		public ID getID() {
			return sharedObjectDescription.getID();
		}
		public ID getHomeID() {
			return sharedObjectDescription.getHomeID();
		}
	}

	
    Vector listeners = new Vector();

    /*
     * (non-Javadoc)
     * 
     * @see org.eclipse.ecf.core.ISharedObjectContainer#addPeerListener(org.eclipse.ecf.core.ISharedObjectContainerListener)
     */
    public void addListener(ISharedObjectContainerListener l) {
        listeners.add(l);
    }

    /*
     * (non-Javadoc)
     * 
     * @see org.eclipse.ecf.core.ISharedObjectContainer#removePeerListener(org.eclipse.ecf.core.ISharedObjectContainerListener)
     */
    public void removeListener(ISharedObjectContainerListener l) {
        listeners.remove(l);
    }
    protected void fireListeners(ContainerEvent evt) {
        for (Enumeration e = listeners.elements(); e.hasMoreElements();) {
            ISharedObjectContainerListener l = (ISharedObjectContainerListener) e
                    .nextElement();
            l.handleEvent(evt);
        }
    }

    /*
     * (non-Javadoc)
     * 
     * @see org.eclipse.ecf.core.ISharedObjectContainer#terminatePeer(long)
     */
    public void dispose(long waittime) {
        // TODO Auto-generated method stub

    }

    /*
     * (non-Javadoc)
     * 
     * @see org.eclipse.ecf.core.ISharedObjectContainer#joinGroup(org.eclipse.ecf.identity.ID,
     *      java.lang.Object)
     */
    public void joinGroup(ID groupID, Object loginData)
            throws SharedObjectContainerJoinException {
        try {
            joinSpace(groupID,(Serializable)loginData);
        } catch (IOException e) {
            throw new SharedObjectContainerJoinException("IOException joining",e);
        }
    }

    /*
     * (non-Javadoc)
     * 
     * @see org.eclipse.ecf.core.ISharedObjectContainer#leaveGroup()
     */
    public void leaveGroup() {
        leaveSpace();
    }

    /*
     * (non-Javadoc)
     * 
     * @see org.eclipse.ecf.core.ISharedObjectContainer#getGroupID()
     */
    public ID getGroupID() {
        return null;
    }

    /*
     * (non-Javadoc)
     * 
     * @see org.eclipse.ecf.core.ISharedObjectContainer#getGroupMembership()
     */
    public ID[] getGroupMembership() {
        return getOtherItemsIDs();
    }

    /*
     * (non-Javadoc)
     * 
     * @see org.eclipse.ecf.core.ISharedObjectContainer#isGroupManager()
     */
    public boolean isGroupManager() {
        return isManager();
    }

    /*
     * (non-Javadoc)
     * 
     * @see org.eclipse.ecf.core.ISharedObjectContainer#isGroupServer()
     */
    public boolean isGroupServer() {
        return isServer();
    }

    /*
     * (non-Javadoc)
     * 
     * @see org.eclipse.ecf.core.ISharedObjectContainer#getAdapter(java.lang.Class)
     */
    public Object getAdapter(Class clazz) {
        return null;
    }

    /*
     * (non-Javadoc)
     * 
     * @see org.eclipse.ecf.core.ISharedObjectContainer#getSharedObjectIDs()
     */
    public ID[] getSharedObjectIDs() {
        return getActiveObjIDs();
    }

    protected static Object loadObject(final ClassLoader cl, String className,
            String[] argTypes, Object[] a) throws Exception {
        final Class[] types = AbstractFactory.getClassesForTypes(argTypes, a,
                cl);
        final Object[] args = (a == null) ? nullArgs : a;
        // Load RepObject class(es), after getting appropriate classloader
        final Class newClass = Class.forName(className, true, cl);
        Object newObject = null;
        try {
            // Do privileged operation. Get appropriate constructor from new
            // class,
            // and create new instance.
            newObject = AccessController
                    .doPrivileged(new PrivilegedExceptionAction() {
                        public Object run() throws Exception {
                            Constructor aConstructor = newClass
                                    .getConstructor(types);
                            aConstructor.setAccessible(true);
                            // Now actually create the object.
                            return aConstructor.newInstance(args);
                        }
                    });
        } catch (PrivilegedActionException e) {
            throw e.getException();
        }
        return newObject;
    }
    /*
     * (non-Javadoc)
     * 
     * @see org.eclipse.ecf.core.ISharedObjectContainer#createSharedObject(org.eclipse.ecf.core.SharedObjectDescription)
     */
    public ID createSharedObject(SharedObjectDescription sd,
            ISharedObjectContainerTransaction trans)
            throws SharedObjectCreateException {
        // TODO Auto-generated method stub
        return null;
    }

    /*
     * (non-Javadoc)
     * 
     * @see org.eclipse.ecf.core.ISharedObjectContainer#addSharedObject(org.eclipse.ecf.identity.ID,
     *      org.eclipse.ecf.core.ISharedObject, java.util.Map,
     *      org.eclipse.ecf.core.ISharedObjectContainerTransaction)
     */
    public ID addSharedObject(ID sharedObjectID, ISharedObject sharedObject,
            Map dict, ISharedObjectContainerTransaction trans)
            throws SharedObjectAddException {
        // TODO Auto-generated method stub
        return null;
    }

    /*
     * (non-Javadoc)
     * 
     * @see org.eclipse.ecf.core.ISharedObjectContainer#getSharedObjectAdapter(org.eclipse.ecf.identity.ID,
     *      java.lang.Class)
     */
    public Object getSharedObjectAdapter(ID sharedObjectID, Class adapterClass)
            throws SharedObjectNotFoundException {
        synchronized (sharedObjectContainerManager) {
            ISharedObject so = getSharedObject(sharedObjectID);
            if (so == null) throw new SharedObjectNotFoundException("shared object "+sharedObjectID.getName()+ " not found");
            return so.getAdapter(adapterClass);
        }
    }

    /*
     * (non-Javadoc)
     * 
     * @see org.eclipse.ecf.core.ISharedObjectContainer#removeSharedObject(org.eclipse.ecf.identity.ID)
     */
    public ISharedObject removeSharedObject(ID sharedObjectID) {
        synchronized (sharedObjectContainerManager) {
            ISharedObject so = getSharedObject(sharedObjectID);
            if (so == null) return null;
            try {
                destroySharedObject(sharedObjectID);
            } catch (SharedObjectNotFoundException e) {
                return null;
            }
            return so;
        }
    }

    /*
     * (non-Javadoc)
     * 
     * @see org.eclipse.ecf.core.ISharedObjectContainer#connectSharedObjects(org.eclipse.ecf.identity.ID,
     *      org.eclipse.ecf.identity.ID[])
     */
    public ISharedObjectConnector connectSharedObjects(ID sharedObjectFrom,
            ID[] sharedObjectsTo) throws SharedObjectConnectException {
        // TODO Auto-generated method stub
        return null;
    }

    /*
     * (non-Javadoc)
     * 
     * @see org.eclipse.ecf.core.ISharedObjectContainer#disconnectSharedObjects(org.eclipse.ecf.core.ISharedObjectConnector)
     */
    public void disconnectSharedObjects(ISharedObjectConnector connector)
            throws SharedObjectDisconnectException {
        // TODO Auto-generated method stub
    }


}