return policy.checkAddSharedObject(fromID, toID, getID(), desc);

/*******************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.provider.generic;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.NotSerializableException;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.io.Serializable;
import java.security.AccessController;
import java.security.PrivilegedAction;
import java.util.Enumeration;
import java.util.Iterator;
import java.util.Map;
import java.util.Vector;
import org.eclipse.core.runtime.Platform;
import org.eclipse.ecf.core.ContainerConnectException;
import org.eclipse.ecf.core.IOSGIService;
import org.eclipse.ecf.core.ISharedObject;
import org.eclipse.ecf.core.ISharedObjectConfig;
import org.eclipse.ecf.core.ISharedObjectContainer;
import org.eclipse.ecf.core.ISharedObjectContainerConfig;
import org.eclipse.ecf.core.ISharedObjectContainerListener;
import org.eclipse.ecf.core.ISharedObjectContainerTransaction;
import org.eclipse.ecf.core.ISharedObjectManager;
import org.eclipse.ecf.core.SharedObjectAddException;
import org.eclipse.ecf.core.SharedObjectDescription;
import org.eclipse.ecf.core.SharedObjectInitException;
import org.eclipse.ecf.core.comm.AsynchConnectionEvent;
import org.eclipse.ecf.core.comm.ConnectionEvent;
import org.eclipse.ecf.core.comm.DisconnectConnectionEvent;
import org.eclipse.ecf.core.comm.IAsynchConnection;
import org.eclipse.ecf.core.comm.IConnection;
import org.eclipse.ecf.core.comm.ISynchAsynchConnectionEventHandler;
import org.eclipse.ecf.core.comm.SynchConnectionEvent;
import org.eclipse.ecf.core.events.IContainerEvent;
import org.eclipse.ecf.core.events.SharedObjectContainerDisconnectedEvent;
import org.eclipse.ecf.core.events.SharedObjectContainerDisposeEvent;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.core.identity.Namespace;
import org.eclipse.ecf.core.security.IConnectContext;
import org.eclipse.ecf.core.security.ISharedObjectPolicy;
import org.eclipse.ecf.core.util.Event;
import org.eclipse.ecf.core.util.IClassLoaderMapper;
import org.eclipse.ecf.core.util.IQueueEnqueue;
import org.eclipse.ecf.core.util.IdentifiableObjectInputStream;
import org.eclipse.ecf.core.util.IdentifiableObjectOutputStream;
import org.eclipse.ecf.provider.ProviderPlugin;
import org.eclipse.ecf.provider.Trace;
import org.eclipse.ecf.provider.generic.gmm.Member;

public abstract class SOContainer implements ISharedObjectContainer {
	class LoadingSharedObject implements ISharedObject {
		Object credentials;

		SharedObjectDescription description;

		Thread runner = null;

		ID fromID = null;

		LoadingSharedObject(ID fromID, SharedObjectDescription sd,
				Object credentials) {
			this.fromID = fromID;
			this.description = sd;
			this.credentials = credentials;
		}

		/*
		 * (non-Javadoc)
		 * 
		 * @see org.eclipse.ecf.core.ISharedObject#dispose(org.eclipse.ecf.core.identity.ID)
		 */
		public void dispose(ID containerID) {
		}

		/*
		 * (non-Javadoc)
		 * 
		 * @see org.eclipse.ecf.core.ISharedObject#getAdapter(java.lang.Class)
		 */
		public Object getAdapter(Class clazz) {
			return null;
		}

		ID getHomeID() {
			return description.getHomeID();
		}

		ID getID() {
			return description.getID();
		}

		Thread getThread() {
			return new Thread(loadingThreadGroup, new Runnable() {
				public void run() {
					try {
						if (Thread.currentThread().isInterrupted()
								|| isClosing())
							throw new InterruptedException(
									"Loading interrupted for object "
											+ getID().getName());
						// First load object
						ISharedObject obj = load(description);
						// Create wrapper object and move from loading to active
						// list.
						SOWrapper wrap = makeRemoteSharedObjectWrapper(fromID,
								description, obj);

						wrap.init();
						// Check to make sure thread has not been
						// interrupted...if it has, throw
						if (Thread.currentThread().isInterrupted()
								|| isClosing())
							throw new InterruptedException(
									"Loading interrupted for object "
											+ getID().getName());
						// Finally, we move from loading to active, and then the
						// object is done
						SOContainer.this.moveFromLoadingToActive(wrap);
					} catch (Exception e) {
						dumpStack("Exception loading object ", e);
						SOContainer.this.removeFromLoading(getID());
						try {
							sendCreateResponse(getHomeID(), getID(), e,
									description.getIdentifier());
						} catch (Exception e1) {
							dumpStack(
									"Exception sending create response from LoadingSharedObject.run",
									e1);
						}
					}
				}
			}, getID().getName() + ":load");
		}

		/*
		 * (non-Javadoc)
		 * 
		 * @see org.eclipse.ecf.core.ISharedObject#handleEvent(org.eclipse.ecf.core.util.Event)
		 */
		public void handleEvent(Event event) {
		}

		/*
		 * (non-Javadoc)
		 * 
		 * @see org.eclipse.ecf.core.ISharedObject#handleEvents(org.eclipse.ecf.core.util.Event[])
		 */
		public void handleEvents(Event[] events) {
		}

		/*
		 * (non-Javadoc)
		 * 
		 * @see org.eclipse.ecf.core.ISharedObject#init(org.eclipse.ecf.core.ISharedObjectConfig)
		 */
		public void init(ISharedObjectConfig initData)
				throws SharedObjectInitException {
		}

		void start() {
			if (runner == null) {
				runner = (Thread) AccessController
						.doPrivileged(new PrivilegedAction() {
							public Object run() {
								return getThread();
							}
						});
				runner.setDaemon(true);
				runner.start();
			}
		}
	}

	class MessageReceiver implements ISynchAsynchConnectionEventHandler {
		/*
		 * (non-Javadoc)
		 * 
		 * @see org.eclipse.ecf.internal.comm.IConnectionEventHandler#getAdapter(java.lang.Class)
		 */
		public Object getAdapter(Class clazz) {
			return null;
		}

		/*
		 * (non-Javadoc)
		 * 
		 * @see org.eclipse.ecf.internal.comm.IAsynchConnectionEventHandler#handleAsynchEvent(org.eclipse.ecf.internal.comm.AsynchConnectionEvent)
		 */
		public void handleAsynchEvent(AsynchConnectionEvent event)
				throws IOException {
			processAsynch(event);
		}

		/*
		 * (non-Javadoc)
		 * 
		 * @see org.eclipse.ecf.internal.comm.IConnectionEventHandler#handleDisconnectEvent(org.eclipse.ecf.internal.comm.ConnectionEvent)
		 */
		public void handleDisconnectEvent(DisconnectConnectionEvent event) {
			processDisconnect(event);
		}

		/*
		 * (non-Javadoc)
		 * 
		 * @see org.eclipse.ecf.internal.comm.IConnectionEventHandler#handleSuspectEvent(org.eclipse.ecf.internal.comm.ConnectionEvent)
		 */
		public boolean handleSuspectEvent(ConnectionEvent event) {
			return false;
		}

		/*
		 * (non-Javadoc)
		 * 
		 * @see org.eclipse.ecf.internal.comm.ISynchConnectionEventHandler#handleSynchEvent(org.eclipse.ecf.internal.comm.SynchConnectionEvent)
		 */
		public Object handleSynchEvent(SynchConnectionEvent event)
				throws IOException {
			return processSynch(event);
		}

		public ID getEventHandlerID() {
			return getID();
		}
	}

	static Trace debug = Trace.create("container");

	public static final String DEFAULT_OBJECT_ARG_KEY = SOContainer.class
			.getName()
			+ ".sharedobjectargs";

	public static final String DEFAULT_OBJECT_ARGTYPES_KEY = SOContainer.class
			.getName()
			+ ".sharedobjectargs";

	protected ISharedObjectContainerConfig config = null;

	protected SOContainerGMM groupManager = null;

	protected boolean isClosing = false;

	private Vector listeners = null;

	protected ThreadGroup loadingThreadGroup = null;

	protected MessageReceiver receiver;

	private long sequenceNumber = 0L;

	protected SOManager sharedObjectManager = null;

	protected ISharedObjectPolicy policy = null;

	protected ThreadGroup sharedObjectThreadGroup = null;

	public SOContainer(ISharedObjectContainerConfig config) {
		if (config == null)
			throw new InstantiationError("config must not be null");
		this.config = config;
		groupManager = new SOContainerGMM(this, new Member(config.getID()));
		sharedObjectManager = new SOManager(this);
		loadingThreadGroup = makeLoadingThreadGroup();
		sharedObjectThreadGroup = getSharedObjectThreadGroup();
		listeners = new Vector();
		receiver = new MessageReceiver();
		debug("<init>");
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.ISharedObjectContainer#addListener(org.eclipse.ecf.core.ISharedObjectContainerListener,
	 *      java.lang.String)
	 */
	public void addListener(ISharedObjectContainerListener l, String filter) {
		synchronized (listeners) {
			listeners.add(new ContainerListener(l, filter));
		}
	}

	protected void setRemoteAddPolicy(ISharedObjectPolicy policy) {
		synchronized (getGroupMembershipLock()) {
			this.policy = policy;
		}
	}

	protected boolean addNewRemoteMember(ID memberID, Object data) {
		debug("addNewRemoteMember:" + memberID);
		return groupManager.addMember(new Member(memberID, data));
	}

	protected ISharedObjectContainerTransaction addSharedObject0(
			SharedObjectDescription sd, ISharedObject s) throws Exception {
		return addSharedObjectWrapper(makeSharedObjectWrapper(sd, s));
	}

	protected void addSharedObjectAndWait(SharedObjectDescription sd,
			ISharedObject s) throws Exception {
		if (sd.getID() == null || s == null) {
			throw new SharedObjectAddException(
					"Object id is null, or instance is null");
		}
		ISharedObjectContainerTransaction t = addSharedObject0(sd, s);
		// Wait right here until committed
		if (t != null)
			t.waitToCommit();
	}

	protected ISharedObjectContainerTransaction addSharedObjectWrapper(
			SOWrapper wrapper) throws Exception {
		if (wrapper == null)
			return null;
		ID id = wrapper.getObjID();
		ISharedObjectContainerTransaction transaction = null;
		synchronized (getGroupMembershipLock()) {
			Object obj = groupManager.getFromAny(id);
			if (obj != null) {
				throw new SharedObjectAddException("SharedObject with id "
						+ id.getName() + " already in container");
			}
			// Call initialize. If this throws it halts everything
			wrapper.init();
			// Call getAdapter(ISharedObjectContainerTransaction)
			transaction = (ISharedObjectContainerTransaction) wrapper.sharedObject
					.getAdapter(ISharedObjectContainerTransaction.class);
			// Put in table
			groupManager.addSharedObjectToActive(wrapper);
		}
		return transaction;
	}

	protected boolean addToLoading(LoadingSharedObject lso) {
		return groupManager.addLoadingSharedObject(lso);
	}

	/**
	 * Check remote creation of shared objects. This method is called by the
	 * remote shared object creation message handler, to verify that the shared
	 * object from container 'fromID' to container 'toID' with description
	 * 'desc' is to be allowed to be created within the current container. If
	 * this method throws, a failure (and exception will be sent back to caller
	 * If this method returns null, the create message is ignored. If this
	 * method returns a non-null object, the creation is allowed to proceed. The
	 * default implementation is to return a non-null object
	 * 
	 * @param fromID
	 *            the ID of the container sending us this create request
	 * @param toID
	 *            the ID (or null) of the container intended to receive this
	 *            request
	 * @param desc
	 *            the SharedObjectDescription that describes the shared object
	 *            to be created
	 * 
	 * @return Object null if the create message is to be ignored, non-null if
	 *         the creation should continue
	 * 
	 * @throws Exception
	 *             may throw any Exception to communicate back (via
	 *             sendCreateResponse) to the sender that the creation has
	 *             failed
	 */
	protected Object checkRemoteCreate(ID fromID, ID toID,
			SharedObjectDescription desc) throws Exception {
		debug("checkRemoteCreate(" + fromID + "," + toID + "," + desc + ")");
		if (policy != null) {
			policy.checkAddSharedObject(fromID, toID, getID(), desc);
		}
		return desc;
	}

	protected void debug(String msg) {
		if (Trace.ON && debug != null) {
			debug.msg(msg + ":" + config.getID());
		}
	}

	protected boolean destroySharedObject(ID sharedObjectID) {
		return groupManager.removeSharedObject(sharedObjectID);
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.ISharedObjectContainer#dispose(long)
	 */
	public void dispose() {
		debug("dispose()");
		isClosing = true;
		// notify listeners
		fireContainerEvent(new SharedObjectContainerDisposeEvent(getID()));
		// Clear group manager
		if (groupManager != null) {
			groupManager.removeAllMembers();
		}
		// Clear shared object manager
		if (sharedObjectManager != null) {
			sharedObjectManager.dispose();
			sharedObjectManager = null;
		}
		/*
		 * if (sharedObjectThreadGroup != null) {
		 * sharedObjectThreadGroup.interrupt(); sharedObjectThreadGroup = null; }
		 */
		if (loadingThreadGroup != null) {
			loadingThreadGroup.interrupt();
			loadingThreadGroup = null;
		}
	}

	protected void dumpStack(String msg, Throwable e) {
		if (Trace.ON && debug != null) {
			debug.dumpStack(e, msg + ":" + config.getID());
		}
	}

	protected void fireContainerEvent(IContainerEvent event) {
		synchronized (listeners) {
			for (Iterator i = listeners.iterator(); i.hasNext();) {
				ContainerListener l = (ContainerListener) i.next();
				l.handleEvent(event);
			}
		}
	}

	protected final void forward(ID fromID, ID toID, ContainerMessage data)
			throws IOException {
		if (toID == null) {
			forwardExcluding(fromID, fromID, data);
		} else {
			forwardToRemote(fromID, toID, data);
		}
	}

	abstract protected void forwardExcluding(ID from, ID excluding,
			ContainerMessage data) throws IOException;

	abstract protected void forwardToRemote(ID from, ID to,
			ContainerMessage data) throws IOException;

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.ISharedObjectContainer#getAdapter(java.lang.Class)
	 */
	public Object getAdapter(Class adapter) {
		if (adapter.isInstance(this)) {
			return this;
		} else {
			return Platform.getAdapterManager().getAdapter(this, adapter);
		}
	}

	/**
	 * @param sd
	 * @return Object []
	 */
	public Object[] getArgsFromProperties(SharedObjectDescription sd) {
		if (sd == null)
			return null;
		Map aMap = sd.getProperties();
		if (aMap == null)
			return null;
		Object obj = aMap.get(DEFAULT_OBJECT_ARG_KEY);
		if (obj == null)
			return null;
		if (obj instanceof Object[]) {
			Object[] ret = (Object[]) obj;
			aMap.remove(DEFAULT_OBJECT_ARG_KEY);
			return ret;
		} else
			return null;
	}

	/**
	 * @param sd
	 * @return String []
	 */
	public String[] getArgTypesFromProperties(SharedObjectDescription sd) {
		if (sd == null)
			return null;
		Map aMap = sd.getProperties();
		if (aMap == null)
			return null;
		Object obj = aMap.get(DEFAULT_OBJECT_ARGTYPES_KEY);
		if (obj == null)
			return null;
		if (obj instanceof String[]) {
			String[] ret = (String[]) obj;
			aMap.remove(DEFAULT_OBJECT_ARGTYPES_KEY);
			return ret;
		} else
			return null;
	}

	protected byte[] serializeObject(Serializable obj) throws IOException {
		ByteArrayOutputStream bos = new ByteArrayOutputStream();
		ObjectOutputStream oos = new ObjectOutputStream(bos);
		oos.writeObject(obj);
		return bos.toByteArray();
	}

	protected ClassLoader getClassLoaderForContainer() {
		return this.getClass().getClassLoader();
	}

	/**
	 * @param sd
	 * @return ClassLoader
	 */
	protected ClassLoader getClassLoaderForSharedObject(
			SharedObjectDescription sd) {
		if (sd != null) {
			ClassLoader cl = sd.getClassLoader();
			if (cl != null)
				return cl;
			else
				return getClassLoaderForContainer();
		} else
			return getClassLoaderForContainer();
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.ISharedObjectContainer#getConfig()
	 */
	public ISharedObjectContainerConfig getConfig() {
		return config;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.ISharedObjectContainer#getGroupID()
	 */
	public abstract ID getConnectedID();

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.ISharedObjectContainer#getGroupMemberIDs()
	 */
	public ID[] getGroupMemberIDs() {
		return groupManager.getMemberIDs();
	}

	protected Object getGroupMembershipLock() {
		return groupManager;
	}

	public ID getID() {
		return config.getID();
	}

	protected int getMaxGroupMembers() {
		return groupManager.getMaxMembers();
	}

	protected Thread getNewSharedObjectThread(ID sharedObjectID,
			Runnable runnable) {
		return new Thread(sharedObjectThreadGroup, runnable, sharedObjectID
				.getName()
				+ ":run");
	}

	protected long getNextSequenceNumber() {
		if (sequenceNumber == Long.MAX_VALUE) {
			sequenceNumber = 0;
			return sequenceNumber;
		} else
			return sequenceNumber++;
	}

	protected ContainerMessage deserializeContainerMessage(byte[] bytes)
			throws IOException {
		ByteArrayInputStream bis = new ByteArrayInputStream(bytes);
		ObjectInputStream ois = new ObjectInputStream(bis);
		Object obj = null;
		try {
			obj = ois.readObject();
		} catch (ClassNotFoundException e) {
			e.printStackTrace(System.err);
			dumpStack("class not found for message", e);
			return null;
		}
		if (obj instanceof ContainerMessage) {
			return (ContainerMessage) obj;
		} else {
			System.out.println("message is not a containermessage " + obj);
			debug("message received is not containermessage:" + obj);
			return null;
		}
	}

	protected IOSGIService getOSGIServiceInterface() {
		return null;
	}

	public ID[] getOtherMemberIDs() {
		return groupManager.getOtherMemberIDs();
	}

	protected ISynchAsynchConnectionEventHandler getReceiver() {
		return receiver;
	}

	protected ISharedObject getSharedObject(ID id) {
		SOWrapper wrap = getSharedObjectWrapper(id);
		if (wrap == null)
			return null;
		else
			return wrap.getSharedObject();
	}

	protected ID[] getSharedObjectIDs() {
		return groupManager.getSharedObjectIDs();
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.ISharedObjectContainer#getSharedObjectManager()
	 */
	public ISharedObjectManager getSharedObjectManager() {
		return sharedObjectManager;
	}

	protected ThreadGroup getSharedObjectThreadGroup() {
		return new ThreadGroup(getID() + ":SOs");
	}

	protected SOWrapper getSharedObjectWrapper(ID id) {
		return groupManager.getFromActive(id);
	}

	protected void handleAsynchIOException(IOException except,
			AsynchConnectionEvent e) {
		// If we get IO Exception, we'll disconnect...if we can
		killConnection(e.getConnection());
	}

	protected void handleCreateMessage(ContainerMessage mess)
			throws IOException {
		debug("handleCreateMessage:" + mess);
		ContainerMessage.CreateMessage create = (ContainerMessage.CreateMessage) mess
				.getData();
		SharedObjectDescription desc = (SharedObjectDescription) create
				.getData();
		ID fromID = mess.getFromContainerID();
		ID toID = mess.getToContainerID();
		Object checkCreateResult = null;
		ID sharedObjectID = desc.getID();
		// Check to make sure that the remote creation is allowed.
		// If this method throws, a failure (and exception will be sent back to
		// caller
		// If this method returns null, the create message is ignored. If this
		// method
		// returns a non-null object, the creation is allowed to proceed
		try {
			checkCreateResult = checkRemoteCreate(fromID, toID, desc);
		} catch (Exception e) {
			SharedObjectAddException addException = new SharedObjectAddException(
					"shared object " + sharedObjectID
							+ " rejected by container " + getID(), e);
			dumpStack("Exception in checkRemoteCreate", addException);
			try {
				sendCreateResponse(fromID, sharedObjectID, addException, desc
						.getIdentifier());
			} catch (IOException except) {
				logException(
						"Exception from sendCreateResponse in handleCreateResponse",
						except);
			}
			return;
		}
		// Then if result from check is non-null, we continue. If null, we
		// ignore
		if (checkCreateResult != null) {
			LoadingSharedObject lso = new LoadingSharedObject(fromID, desc,
					checkCreateResult);
			synchronized (getGroupMembershipLock()) {
				if (!addToLoading(lso)) {
					try {
						sendCreateResponse(fromID, sharedObjectID,
								new SharedObjectAddException("shared object "
										+ sharedObjectID
										+ " already exists in container "
										+ getID()), desc.getIdentifier());
					} catch (IOException e) {
						logException(
								"Exception in handleCreateMessage.sendCreateResponse",
								e);
					}
				}
				forward(fromID, toID, mess);
				return;
			}
		}
		synchronized (getGroupMembershipLock()) {
			forward(fromID, toID, mess);
		}
	}

	protected void handleCreateResponseMessage(ContainerMessage mess)
			throws IOException {
		debug("handleCreateResponseMessage:" + mess);
		ID fromID = mess.getFromContainerID();
		ID toID = mess.getToContainerID();
		ContainerMessage.CreateResponseMessage resp = (ContainerMessage.CreateResponseMessage) mess
				.getData();
		if (toID != null && toID.equals(getID())) {
			ID sharedObjectID = resp.getSharedObjectID();
			SOWrapper sow = getSharedObjectWrapper(sharedObjectID);
			if (sow != null) {
				sow.deliverCreateResponse(fromID, resp);
			} else {
				log("handleCreateResponseMessage...wrapper not found for "
						+ sharedObjectID);
			}
		} else {
			forwardToRemote(fromID, toID, mess);
		}
	}

	/**
	 * @param mess
	 */
	protected abstract void handleLeaveGroupMessage(ContainerMessage mess);

	protected void handleSharedObjectDisposeMessage(ContainerMessage mess)
			throws IOException {
		debug("handleSharedObjectDisposeMessage:" + mess);
		ID fromID = mess.getFromContainerID();
		ID toID = mess.getToContainerID();
		ContainerMessage.SharedObjectDisposeMessage resp = (ContainerMessage.SharedObjectDisposeMessage) mess
				.getData();
		ID sharedObjectID = resp.getSharedObjectID();
		synchronized (getGroupMembershipLock()) {
			if (groupManager.isLoading(sharedObjectID)) {
				groupManager.removeSharedObjectFromLoading(sharedObjectID);
			} else {
				groupManager.removeSharedObject(sharedObjectID);
			}
			forward(fromID, toID, mess);
		}
	}

	protected boolean verifyToIDForSharedObjectMessage(ID toID) {
		if (toID == null || toID.equals(getID())) {
			return true;
		}
		return false;
	}
	protected void handleSharedObjectMessage(ContainerMessage mess)
			throws IOException {
		debug("handleSharedObjectMessage:" + mess);
		ID fromID = mess.getFromContainerID();
		ID toID = mess.getToContainerID();
		ContainerMessage.SharedObjectMessage resp = (ContainerMessage.SharedObjectMessage) mess
				.getData();
		synchronized (getGroupMembershipLock()) {
			if (verifyToIDForSharedObjectMessage(toID)) {
				SOWrapper sow = getSharedObjectWrapper(resp
						.getFromSharedObjectID());
				if (sow != null) {
					try {
						sow
								.deliverSharedObjectMessage(
										fromID,
										(Serializable) deserializeSharedObjectMessage((byte[]) resp
												.getData()));
					} catch (ClassNotFoundException e) {
						dumpStack(
								"ClassNotFoundException in handleSharedObjectMessage",
								e);
						e.printStackTrace(System.err);
					}
				}
			}
			forward(fromID, toID, mess);
		}
	}

	protected void handleUnidentifiedMessage(ContainerMessage mess)
			throws IOException {
		// do nothing
	}

	protected abstract void handleViewChangeMessage(ContainerMessage mess)
			throws IOException;

	protected boolean isClosing() {
		return isClosing;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.ISharedObjectContainer#isGroupManager()
	 */
	public abstract boolean isGroupManager();

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.ISharedObjectContainer#connect(org.eclipse.ecf.core.identity.ID,
	 *      org.eclipse.ecf.core.security.IConnectContext)
	 */
	public abstract void connect(ID groupID, IConnectContext connectContext)
			throws ContainerConnectException;

	protected void killConnection(IConnection conn) {
		try {
			if (conn != null && conn.isConnected()) {
				debug("killconnection("+conn+")");
				conn.disconnect();
			}
		} catch (IOException e) {
			logException("Exception in killConnection", e);
		}
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.ISharedObjectContainer#leaveGroup()
	 */
	public abstract void disconnect();

	protected ISharedObject load(SharedObjectDescription sd) throws Exception {
		return sharedObjectManager.loadSharedObject(sd);
	}

	protected void log(String msg) {
		debug(msg);
	}

	protected void logException(String msg, Throwable e) {
		dumpStack(msg, e);
	}

	protected ThreadGroup makeLoadingThreadGroup() {
		return new ThreadGroup(getID() + ":load");
	}

	protected SOConfig makeSharedObjectConfig(SharedObjectDescription sd,
			ISharedObject obj) {
		ID homeID = sd.getHomeID();
		if (homeID == null)
			homeID = getID();
		return new SOConfig(sd.getID(), homeID, this, sd.getProperties());
	}

	protected SOConfig makeRemoteSharedObjectConfig(ID fromID,
			SharedObjectDescription sd, ISharedObject obj) {
		ID homeID = sd.getHomeID();
		if (homeID == null)
			homeID = fromID;
		return new SOConfig(sd.getID(), homeID, this, sd.getProperties());
	}

	protected SOContext makeSharedObjectContext(SOConfig soconfig,
			IQueueEnqueue queue) {
		return new SOContext(soconfig.getSharedObjectID(), soconfig
				.getHomeContainerID(), this, soconfig.getProperties(), queue);
	}

	protected SOContext makeRemoteSharedObjectContext(SOConfig soconfig,
			IQueueEnqueue queue) {
		return new SOContext(soconfig.getSharedObjectID(), soconfig
				.getHomeContainerID(), this, soconfig.getProperties(), queue);
	}

	protected SOWrapper makeSharedObjectWrapper(SharedObjectDescription sd,
			ISharedObject s) {
		SOConfig newConfig = makeSharedObjectConfig(sd, s);
		return new SOWrapper(newConfig, s, this);
	}

	protected SOWrapper makeRemoteSharedObjectWrapper(ID fromID,
			SharedObjectDescription sd, ISharedObject s) {
		SOConfig newConfig = makeRemoteSharedObjectConfig(fromID, sd, s);
		return new SOWrapper(newConfig, s, this);
	}

	protected void memberLeave(ID target, IConnection conn) {
		if (target == null)
			return;
		if (groupManager.removeMember(target)) {
			try {
				forwardExcluding(getID(), target, ContainerMessage
						.makeViewChangeMessage(getID(), null,
								getNextSequenceNumber(), new ID[] { target },
								false, null));
			} catch (IOException e) {
				logException("Exception in memberLeave.forwardExcluding", e);
			}
		}
		if (conn != null)
			killConnection(conn);
	}

	protected void moveFromLoadingToActive(SOWrapper wrap) {
		groupManager.moveSharedObjectFromLoadingToActive(wrap);
	}

	protected void notifySharedObjectActivated(ID sharedObjectID) {
		groupManager.notifyOthersActivated(sharedObjectID);
	}

	protected void notifySharedObjectDeactivated(ID sharedObjectID) {
		groupManager.notifyOthersDeactivated(sharedObjectID);
	}

	protected ContainerMessage validateContainerMessage(Object mess) {
		// Message must not be null
		if (mess == null) {
			debug("Ignoring null ContainerMessage");
			return null;
		}
		if (mess instanceof ContainerMessage) {
			ContainerMessage contmess = (ContainerMessage) mess;
			ID fromID = contmess.getFromContainerID();
			if (fromID == null) {
				debug("Ignoring ContainerMessage from null sender...ignoring");
				return null;
			}
			// OK..let it continue on it's journey
			return contmess;
		} else {
			debug("Ignoring invalid ContainerMessage:" + mess);
			return null;
		}

	}

	protected void processAsynch(AsynchConnectionEvent e) {
		debug("processAsynch("+e+")");
		try {
			Object obj = e.getData();
			if (obj == null) {
				System.out.println("CONTAINER="+getID()+":NULL DATA IN EVENT="+e);
				debug("Ignoring null data in event " + e);
				return;
			}
			if (!(obj instanceof byte[])) {
				debug("Ignoring event without valid data " + e);
				System.out.println("CONTAINER"+getID()+":NOT BYTE[] DATA IN EVENT="+e+":DATA="+obj);
				return;
			}
			ContainerMessage mess = validateContainerMessage(deserializeContainerMessage((byte[]) obj));
			if (mess == null) {
				System.out.println("EVENT NOT VALIDATED: "+e);
				return;
			}
			Serializable submess = mess.getData();
			if (submess != null) {
				if (submess instanceof ContainerMessage.CreateMessage) {
					handleCreateMessage(mess);
				} else if (submess instanceof ContainerMessage.CreateResponseMessage) {
					handleCreateResponseMessage(mess);
				} else if (submess instanceof ContainerMessage.SharedObjectDisposeMessage) {
					handleSharedObjectDisposeMessage(mess);
				} else if (submess instanceof ContainerMessage.SharedObjectMessage) {
					handleSharedObjectMessage(mess);
				} else if (submess instanceof ContainerMessage.ViewChangeMessage) {
					handleViewChangeMessage(mess);
				} else {
					handleUnidentifiedMessage(mess);
				}
			} else {
				handleUnidentifiedMessage(mess);
			}
		} catch (IOException except) {
			handleAsynchIOException(except, e);
		}
	}

	protected abstract ID getIDForConnection(IAsynchConnection connection);

	protected void processDisconnect(DisconnectConnectionEvent e) {
		debug("processDisconnect[" +Thread.currentThread().getName()+"]");
		try {
			// Get connection responsible for disconnect event
			IAsynchConnection conn = (IAsynchConnection) e.getConnection();
			if (!conn.isConnected())
				return;
			ID fromID = null;
			synchronized (getGroupMembershipLock()) {
				fromID = getIDForConnection(conn);
				memberLeave(fromID, conn);
			}
			if (fromID != null)
				fireContainerEvent(new SharedObjectContainerDisconnectedEvent(
						getID(), fromID));
		} catch (Exception except) {
			logException("Exception in processDisconnect ", except);
		}
	}

	protected Serializable processSynch(SynchConnectionEvent e)
			throws IOException {
		debug("processSynch:" + e);
		ContainerMessage mess = deserializeContainerMessage((byte[]) e
				.getData());
		Serializable data = mess.getData();
		// Must be non null
		if (data != null && data instanceof ContainerMessage.LeaveGroupMessage) {
			handleLeaveGroupMessage(mess);
		}
		return null;
	}

	abstract protected void queueContainerMessage(ContainerMessage mess)
			throws IOException;

	protected void removeFromLoading(ID id) {
		groupManager.removeSharedObjectFromLoading(id);
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.ISharedObjectContainer#removeListener(org.eclipse.ecf.core.ISharedObjectContainerListener)
	 */
	public void removeListener(ISharedObjectContainerListener l) {
		synchronized (listeners) {
			for (Enumeration e = listeners.elements(); e.hasMoreElements();) {
				ContainerListener list = (ContainerListener) e.nextElement();
				if (list.isListener(l)) {
					// found it...so remove
					listeners.remove(list);
				}
			}
		}
	}

	protected boolean removeRemoteMember(ID remoteMember) {
		return groupManager.removeMember(remoteMember);
	}

	protected ISharedObject removeSharedObject(ID id) {
		synchronized (getGroupMembershipLock()) {
			SOWrapper wrap = groupManager.getFromActive(id);
			if (wrap == null)
				return null;
			groupManager.removeSharedObject(id);
			return wrap.getSharedObject();
		}
	}

	protected void sendCreate(ID sharedObjectID, ID toContainerID,
			SharedObjectDescription sd) throws IOException {
		sendCreateSharedObjectMessage(toContainerID, sd);
	}

	protected void sendCreateResponse(ID homeID, ID sharedObjectID,
			Throwable t, long identifier) throws IOException {
		sendCreateResponseSharedObjectMessage(homeID, sharedObjectID, t,
				identifier);
	}

	protected void sendCreateResponseSharedObjectMessage(ID toContainerID,
			ID fromSharedObject, Throwable t, long ident) throws IOException {
		sendMessage(ContainerMessage.makeSharedObjectCreateResponseMessage(
				getID(), toContainerID, getNextSequenceNumber(),
				fromSharedObject, t, ident));
	}

	protected ID[] sendCreateSharedObjectMessage(ID toContainerID,
			SharedObjectDescription sd) throws IOException {
		ID[] returnIDs = null;
		if (toContainerID == null) {
			synchronized (getGroupMembershipLock()) {
				// Send message to all
				sendMessage(ContainerMessage.makeSharedObjectCreateMessage(
						getID(), toContainerID, getNextSequenceNumber(), sd));
				returnIDs = getOtherMemberIDs();
			}
		} else {
			// If the create msg is directed to this space, no msg will be sent
			if (getID().equals(toContainerID)) {
				returnIDs = new ID[0];
			} else {
				sendMessage(ContainerMessage.makeSharedObjectCreateMessage(
						getID(), toContainerID, getNextSequenceNumber(), sd));
				returnIDs = new ID[1];
				returnIDs[0] = toContainerID;
			}
		}
		return returnIDs;
	}

	protected void sendDispose(ID toContainerID, ID sharedObjectID)
			throws IOException {
		sendDisposeSharedObjectMessage(toContainerID, sharedObjectID);
	}

	protected void sendDisposeSharedObjectMessage(ID toContainerID,
			ID fromSharedObject) throws IOException {
		sendMessage(ContainerMessage.makeSharedObjectDisposeMessage(getID(),
				toContainerID, getNextSequenceNumber(), fromSharedObject));
	}

	protected void sendMessage(ContainerMessage data) throws IOException {
		synchronized (getGroupMembershipLock()) {
			ID ourID = getID();
			// We don't send to ourselves
			if (!ourID.equals(data.getToContainerID())) {
				debug("sendcontainermessage:" + data);
				queueContainerMessage(data);
			}
		}
	}

	protected byte[] serializeSharedObjectMessage(ID sharedObjectID,
			Object message) throws IOException {
		if (!(message instanceof Serializable))
			throw new NotSerializableException("sharedobjectmessage " + message
					+ " not serializable");
		ByteArrayOutputStream bouts = new ByteArrayOutputStream();
		IdentifiableObjectOutputStream ioos = new IdentifiableObjectOutputStream(
				sharedObjectID.getName(), bouts);
		ioos.writeObject(message);
		return bouts.toByteArray();
	}

	protected Object deserializeSharedObjectMessage(byte[] bytes)
			throws IOException, ClassNotFoundException {
		ByteArrayInputStream bins = new ByteArrayInputStream(bytes);
		IdentifiableObjectInputStream iins = new IdentifiableObjectInputStream(
				new IClassLoaderMapper() {
					public ClassLoader mapNameToClassLoader(String name) {
						ISharedObjectManager manager = getSharedObjectManager();
						ID[] ids = manager.getSharedObjectIDs();
						ID found = null;
						for (int i = 0; i < ids.length; i++) {
							ID id = ids[i];
							if (name.equals(id.getName())) {
								found = id;
								break;
							}
						}
						if (found == null)
							return null;
						ISharedObject obj = manager.getSharedObject(found);
						if (obj == null)
							return null;
						return obj.getClass().getClassLoader();
					}

				}, bins);
		Object obj = iins.readObject();
		return obj;
	}

	protected void sendMessage(ID toContainerID, ID sharedObjectID,
			Object message) throws IOException {
		if (message == null)
			return;
		byte[] sendData = serializeSharedObjectMessage(sharedObjectID, message);
		sendSharedObjectMessage(toContainerID, sharedObjectID, sendData);
	}

	protected void sendSharedObjectMessage(ID toContainerID,
			ID fromSharedObject, Serializable data) throws IOException {

		sendMessage(ContainerMessage.makeSharedObjectMessage(getID(),
				toContainerID, getNextSequenceNumber(), fromSharedObject, data));
	}

	protected void setIsClosing() {
		isClosing = true;
	}

	protected void setMaxGroupMembers(int max) {
		groupManager.setMaxMembers(max);
	}
	public Namespace getConnectNamespace() {
		// We expect StringIDs for the generic server
		return IDFactory.getDefault().getNamespaceByName(ProviderPlugin.getDefault().getNamespaceIdentifier());
	}
}
 No newline at end of file