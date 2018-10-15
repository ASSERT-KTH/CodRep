debug("handleCreateMessage(from=" + fromID + ",to=" + toID + ",this=" + getID() + ",desc=" + desc + ")"); //$NON-NLS-1$ //$NON-NLS-2$ //$NON-NLS-3$ //$NON-NLS-4$ //$NON-NLS-5$

/*******************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.provider.generic;

import java.io.*;
import java.security.AccessController;
import java.security.PrivilegedAction;
import java.util.HashMap;
import java.util.Map;
import org.eclipse.core.runtime.*;
import org.eclipse.ecf.core.AbstractContainer;
import org.eclipse.ecf.core.ContainerConnectException;
import org.eclipse.ecf.core.events.IContainerEvent;
import org.eclipse.ecf.core.identity.*;
import org.eclipse.ecf.core.security.IConnectContext;
import org.eclipse.ecf.core.sharedobject.*;
import org.eclipse.ecf.core.sharedobject.events.*;
import org.eclipse.ecf.core.sharedobject.security.ISharedObjectPolicy;
import org.eclipse.ecf.core.sharedobject.util.IQueueEnqueue;
import org.eclipse.ecf.core.util.*;
import org.eclipse.ecf.internal.provider.*;
import org.eclipse.ecf.internal.provider.Messages;
import org.eclipse.ecf.provider.comm.*;
import org.eclipse.ecf.provider.generic.gmm.Member;
import org.eclipse.ecf.provider.util.*;
import org.eclipse.osgi.util.NLS;

public abstract class SOContainer extends AbstractContainer implements ISharedObjectContainer {
	class LoadingSharedObject implements ISharedObject {
		final ReplicaSharedObjectDescription description;
		private Thread runner = null;
		ID fromID = null;

		LoadingSharedObject(ID fromID, ReplicaSharedObjectDescription sd) {
			this.fromID = fromID;
			this.description = sd;
		}

		public void dispose(ID containerID) {
			// nothing to do
		}

		public Object getAdapter(Class clazz) {
			return null;
		}

		ID getHomeID() {
			final ID homeID = description.getHomeID();
			if (homeID == null)
				return getID();
			return homeID;
		}

		ID getID() {
			return description.getID();
		}

		public void handleEvent(Event event) {
			// nothing to do
		}

		public void handleEvents(Event[] events) {
			// nothing to do
		}

		/**
		 * @param initData
		 * @throws SharedObjectInitException not thrown in this implementation.
		 */
		public void init(ISharedObjectConfig initData) throws SharedObjectInitException {
			// nothing to do
		}

		void start() {
			if (runner == null) {
				runner = (Thread) AccessController.doPrivileged(new PrivilegedAction() {
					public Object run() {
						return new Thread(loadingThreadGroup, new Runnable() {
							public void run() {
								try {
									if (Thread.currentThread().isInterrupted() || isClosing())
										throw new InterruptedException(Messages.SOContainer_Loading_Interrupted + getID().getName());
									// First load object
									final ISharedObject obj = load(description);
									// Create wrapper object and
									// move from loading to
									// active
									// list.
									final SOWrapper wrap = createRemoteSharedObjectWrapper(fromID, description, obj);
									wrap.init();
									// Check to make sure thread
									// has not been
									// interrupted...if it has,
									// throw
									if (Thread.currentThread().isInterrupted() || isClosing())
										throw new InterruptedException(Messages.SOContainer_Loading_Interrupted + getID().getName());
									// Finally, we move from
									// loading to active, and
									// then the
									// object is done
									SOContainer.this.moveFromLoadingToActive(wrap);
								} catch (final Exception e) {
									traceStack("Exception loading:" + description, e); //$NON-NLS-1$
									SOContainer.this.removeFromLoading(getID());
									try {
										sendCreateResponse(getHomeID(), getID(), e, description.getIdentifier());
									} catch (final Exception e1) {
										traceStack("Exception sending create response from LoadingSharedObject.run:" //$NON-NLS-1$
												+ description, e1);
									}
								}
							}
						}, getID().getName() + ":loading"); //$NON-NLS-1$
					}
				});
				runner.setDaemon(true);
				runner.start();
			}
		}
	}

	public static final String DEFAULT_OBJECT_ARG_KEY = SOContainer.class.getName() + ".sharedobjectargs"; //$NON-NLS-1$
	public static final String DEFAULT_OBJECT_ARGTYPES_KEY = SOContainer.class.getName() + ".sharedobjectargtypes"; //$NON-NLS-1$

	private long sequenceNumber = 0L;

	protected ISharedObjectContainerConfig config = null;

	protected SOContainerGMM groupManager = null;

	protected boolean isClosing = false;

	protected ThreadGroup loadingThreadGroup = null;

	protected SOManager sharedObjectManager = null;

	protected ISharedObjectPolicy policy = null;

	protected ThreadGroup sharedObjectThreadGroup = null;

	protected ISynchAsynchEventHandler receiver = new ISynchAsynchEventHandler() {
		public Object handleSynchEvent(SynchEvent event) throws IOException {
			return processSynch(event);
		}

		public ID getEventHandlerID() {
			return getID();
		}

		public void handleConnectEvent(ConnectionEvent event) {
			// nothing to do
		}

		public void handleDisconnectEvent(DisconnectEvent event) {
			processDisconnect(event);
		}

		public void handleAsynchEvent(AsynchEvent event) throws IOException {
			processAsynch(event);
		}
	};

	public SOContainer(ISharedObjectContainerConfig config) {
		Assert.isNotNull(config, Messages.SOContainer_Exception_Config_Not_Null);
		this.config = config;
		groupManager = new SOContainerGMM(this, new Member(config.getID()));
		sharedObjectManager = new SOManager(this);
		loadingThreadGroup = new ThreadGroup(getID() + ":loading"); //$NON-NLS-1$
		sharedObjectThreadGroup = new ThreadGroup(getID() + ":SOs"); //$NON-NLS-1$
	}

	// Implementation of IIdentifiable

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.identity.IIdentifiable#getID()
	 */
	public ID getID() {
		return config.getID();
	}

	// Implementation of IContainer

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.ISharedObjectContainer#connect(org.eclipse.ecf.core.identity.ID,
	 *      org.eclipse.ecf.core.security.IConnectContext)
	 */
	public abstract void connect(ID groupID, IConnectContext connectContext) throws ContainerConnectException;

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.ISharedObjectContainer#getGroupID()
	 */
	public abstract ID getConnectedID();

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.ISharedObjectContainer#leaveGroup()
	 */
	public abstract void disconnect();

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.IContainer#getConnectNamespace()
	 */
	public Namespace getConnectNamespace() {
		// We expect StringIDs for the generic server
		return IDFactory.getDefault().getNamespaceByName(ProviderPlugin.getDefault().getNamespaceIdentifier());
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.ISharedObjectContainer#dispose(long)
	 */
	public void dispose() {
		isClosing = true;
		// Clear group manager
		if (groupManager != null)
			groupManager.removeAllMembers();
		// Clear shared object manager
		if (sharedObjectManager != null) {
			sharedObjectManager.dispose();
			sharedObjectManager = null;
		}
		if (loadingThreadGroup != null) {
			loadingThreadGroup.interrupt();
			loadingThreadGroup = null;
		}
		super.dispose();
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.ISharedObjectContainer#getAdapter(java.lang.Class)
	 */
	public Object getAdapter(Class adapter) {
		if (adapter.isInstance(this)) {
			return this;
		}
		final IAdapterManager adapterManager = ProviderPlugin.getDefault().getAdapterManager();
		if (adapterManager == null)
			return null;
		return adapterManager.loadAdapter(this, adapter.getName());
	}

	// Impl of ISharedObjectContainer
	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.ISharedObjectContainer#getSharedObjectManager()
	 */
	public ISharedObjectManager getSharedObjectManager() {
		return sharedObjectManager;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.ISharedObjectContainer#getGroupMemberIDs()
	 */
	public ID[] getGroupMemberIDs() {
		return groupManager.getMemberIDs();
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
	 * @see org.eclipse.ecf.core.ISharedObjectContainer#isGroupManager()
	 */
	public abstract boolean isGroupManager();

	// End of ISharedObjectContainer

	protected void setRemoteAddPolicy(ISharedObjectPolicy policy) {
		synchronized (getGroupMembershipLock()) {
			this.policy = policy;
		}
	}

	protected boolean addNewRemoteMember(ID memberID, Object data) {
		return groupManager.addMember(new Member(memberID, data));
	}

	protected ISharedObjectContainerTransaction addSharedObject0(ID id, ISharedObject s, Map props) throws Exception {
		return addSharedObjectWrapper(createSharedObjectWrapper(id, s, props));
	}

	protected void addSharedObjectAndWait(ID id, ISharedObject s, Map properties) throws Exception {
		if (id == null || s == null) {
			throw new SharedObjectAddException(Messages.SOContainer_Exception_Add_Object);
		}
		final ISharedObjectContainerTransaction t = addSharedObject0(id, s, properties);
		// Wait right here until committed
		if (t != null)
			t.waitToCommit();
	}

	protected ISharedObjectContainerTransaction addSharedObjectWrapper(SOWrapper wrapper) throws Exception {
		if (wrapper == null)
			return null;
		final ID id = wrapper.getObjID();
		ISharedObjectContainerTransaction transaction = null;
		synchronized (getGroupMembershipLock()) {
			final Object obj = groupManager.getFromAny(id);
			if (obj != null) {
				throw new SharedObjectAddException(Messages.SOContainer_Exception_Object_With_ID + id.getName() + Messages.SOContainer_Exception_Already_In_Container);
			}
			// Call initialize. If this throws it halts everything
			wrapper.init();
			// Call getAdapter(ISharedObjectContainerTransaction)
			transaction = (ISharedObjectContainerTransaction) wrapper.sharedObject.getAdapter(ISharedObjectContainerTransaction.class);
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
	protected Object checkRemoteCreate(ID fromID, ID toID, ReplicaSharedObjectDescription desc) throws Exception {
		if (policy != null) {
			return policy.checkAddSharedObject(fromID, toID, getID(), desc);
		}
		return desc;
	}

	protected void debug(String msg) {
		Trace.trace(ProviderPlugin.PLUGIN_ID, ECFProviderDebugOptions.CONTAINER, msg + ":" + config.getID()); //$NON-NLS-1$
	}

	protected void traceStack(String msg, Throwable e) {
		Trace.catching(ProviderPlugin.PLUGIN_ID, ECFProviderDebugOptions.EXCEPTIONS_CATCHING, SOContainer.class, config.getID() + ":" + msg, e); //$NON-NLS-1$
	}

	protected boolean destroySharedObject(ID sharedObjectID) {
		return groupManager.removeSharedObject(sharedObjectID);
	}

	protected final void forward(ID fromID, ID toID, ContainerMessage data) throws IOException {
		if (toID == null)
			forwardExcluding(fromID, fromID, data);
		else
			forwardToRemote(fromID, toID, data);
	}

	abstract protected void forwardExcluding(ID from, ID excluding, ContainerMessage data) throws IOException;

	abstract protected void forwardToRemote(ID from, ID to, ContainerMessage data) throws IOException;

	/**
	 * @param sd
	 * @return Object []
	 */
	protected Object[] getArgsFromProperties(SharedObjectDescription sd) {
		if (sd == null)
			return null;
		final Map aMap = sd.getProperties();
		if (aMap == null)
			return null;
		final Object obj = aMap.get(DEFAULT_OBJECT_ARG_KEY);
		if (obj == null)
			return null;
		if (obj instanceof Object[]) {
			final Object[] ret = (Object[]) obj;
			aMap.remove(DEFAULT_OBJECT_ARG_KEY);
			return ret;
		}
		return null;
	}

	/**
	 * @param sd
	 * @return String []
	 */
	protected String[] getArgTypesFromProperties(SharedObjectDescription sd) {
		if (sd == null)
			return null;
		final Map aMap = sd.getProperties();
		if (aMap == null)
			return null;
		final Object obj = aMap.get(DEFAULT_OBJECT_ARGTYPES_KEY);
		if (obj == null)
			return null;
		if (obj instanceof String[]) {
			final String[] ret = (String[]) obj;
			aMap.remove(DEFAULT_OBJECT_ARGTYPES_KEY);
			return ret;
		}
		return null;
	}

	public static byte[] serialize(Serializable obj) throws IOException {
		final ByteArrayOutputStream bos = new ByteArrayOutputStream();
		final ObjectOutputStream oos = new ObjectOutputStream(bos);
		oos.writeObject(obj);
		return bos.toByteArray();
	}

	protected ClassLoader getClassLoaderForContainer() {
		// Use classloader from SOContainer class (and buddy's as specified
		// by ECF generic provider plugin org.eclipse.ecf.provider's buddy
		// policy (currently set to 'global').
		return this.getClass().getClassLoader();
	}

	/**
	 * @param sd
	 * @return ClassLoader
	 */
	protected ClassLoader getClassLoaderForSharedObject(SharedObjectDescription sd) {
		return getClassLoaderForContainer();
	}

	protected Object getGroupMembershipLock() {
		return groupManager;
	}

	protected int getMaxGroupMembers() {
		return groupManager.getMaxMembers();
	}

	protected Thread getNewSharedObjectThread(ID sharedObjectID, Runnable runnable) {
		return new Thread(sharedObjectThreadGroup, runnable, sharedObjectID.getName() + ":run"); //$NON-NLS-1$
	}

	protected long getNextSequenceNumber() {
		if (sequenceNumber == Long.MAX_VALUE) {
			sequenceNumber = 0;
			return sequenceNumber;
		}
		return sequenceNumber++;
	}

	public static ContainerMessage deserializeContainerMessage(byte[] bytes) throws IOException {
		final ByteArrayInputStream bis = new ByteArrayInputStream(bytes);
		final ObjectInputStream ois = new ObjectInputStream(bis);
		Object obj = null;
		try {
			obj = ois.readObject();
		} catch (final ClassNotFoundException e) {
			ProviderPlugin.getDefault().log(new Status(IStatus.ERROR, ProviderPlugin.PLUGIN_ID, Messages.SOContainer_EXCEPTION_CLASS_NOT_FOUND, e));
			printToSystemError("deserializeContainerMessage class not found", e); //$NON-NLS-1$
			return null;
		} catch (final InvalidClassException e) {
			ProviderPlugin.getDefault().log(new Status(IStatus.ERROR, ProviderPlugin.PLUGIN_ID, Messages.SOContainer_EXCEPTION_INVALID_CLASS, e));
			printToSystemError("deserializeContainerMessage invalid class", e); //$NON-NLS-1$
			return null;
		}
		if (obj instanceof ContainerMessage)
			return (ContainerMessage) obj;
		ProviderPlugin.getDefault().log(new Status(IStatus.ERROR, ProviderPlugin.PLUGIN_ID, Messages.SOContainer_EXCEPTION_NOT_CONTAINER_MESSAGE, null));
		printToSystemError("deserializeContainerMessage invalid container message ", new InvalidObjectException("object " + obj + " not appropriate type")); //$NON-NLS-1$ //$NON-NLS-2$ //$NON-NLS-3$
		return null;
	}

	/**
	 * @since 2.0
	 */
	protected static void printToSystemError(String message, Throwable t) {
		System.err.println(message);
		t.printStackTrace(System.err);
	}

	protected ID[] getOtherMemberIDs() {
		return groupManager.getOtherMemberIDs();
	}

	protected ISynchAsynchEventHandler getReceiver() {
		return receiver;
	}

	protected ISharedObject getSharedObject(ID id) {
		final SOWrapper wrap = getSharedObjectWrapper(id);
		return (wrap == null) ? null : wrap.getSharedObject();
	}

	protected ID[] getSharedObjectIDs() {
		return groupManager.getSharedObjectIDs();
	}

	protected SOWrapper getSharedObjectWrapper(ID id) {
		return groupManager.getFromActive(id);
	}

	protected void handleAsynchIOException(IOException except, AsynchEvent e) {
		// If we get IO Exception, we'll disconnect...if we can
		disconnect(e.getConnection());
	}

	protected void handleCreateMessage(ContainerMessage mess) throws IOException {
		final ContainerMessage.CreateMessage create = (ContainerMessage.CreateMessage) mess.getData();
		if (create == null)
			throw new IOException(Messages.SOContainer_Exception_Bad_Container_Message);
		final ReplicaSharedObjectDescription desc = (ReplicaSharedObjectDescription) create.getData();
		if (desc == null)
			throw new IOException(Messages.SOContainer_Exception_Bad_Description);
		final ID fromID = mess.getFromContainerID();
		final ID toID = mess.getToContainerID();
		Object checkCreateResult = null;
		final ID sharedObjectID = desc.getID();
		if (sharedObjectID == null)
			throw new IOException(Messages.SOContainer_Exception_ObjectID_Is_Null);
		// Check to make sure that the remote creation is allowed.
		// If this method throws, a failure (and exception will be sent back to
		// caller
		// If this method returns null, the create message is ignored. If this
		// method
		// returns a non-null object, the creation is allowed to proceed
		debug("handleCreateMessage(from=" + fromID + ",to=" + toID + "," + desc + ")"); //$NON-NLS-1$ //$NON-NLS-2$ //$NON-NLS-3$ //$NON-NLS-4$
		try {
			checkCreateResult = checkRemoteCreate(fromID, toID, desc);
		} catch (final Exception e) {
			final SharedObjectAddException addException = new SharedObjectAddException(Messages.SOContainer_Shared_Object + sharedObjectID + Messages.SOContainer_Rejected_By_Container + getID(), e);
			traceStack("Exception in checkRemoteCreate:" + desc, addException); //$NON-NLS-1$
			try {
				sendCreateResponse(fromID, sharedObjectID, addException, desc.getIdentifier());
			} catch (final IOException except) {
				traceStack("Exception from sendCreateResponse in handleCreateResponse", //$NON-NLS-1$
						except);
			}
			return;
		}
		// Then if result from check is non-null, we continue. If null, we
		// ignore
		if (checkCreateResult != null) {
			final LoadingSharedObject lso = new LoadingSharedObject(fromID, desc);
			synchronized (getGroupMembershipLock()) {
				if (!addToLoading(lso)) {
					try {
						sendCreateResponse(fromID, sharedObjectID, new SharedObjectAddException(Messages.SOContainer_Shared_Object + sharedObjectID + Messages.SOContainer_Exception_Already_Exists_In_Container + getID()), desc.getIdentifier());
					} catch (final IOException e) {
						traceStack("Exception in handleCreateMessage.sendCreateResponse", //$NON-NLS-1$
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

	protected void handleCreateResponseMessage(ContainerMessage mess) throws IOException {
		final ID fromID = mess.getFromContainerID();
		final ID toID = mess.getToContainerID();
		final ContainerMessage.CreateResponseMessage resp = (ContainerMessage.CreateResponseMessage) mess.getData();
		if (toID != null && toID.equals(getID())) {
			final ID sharedObjectID = resp.getSharedObjectID();
			final SOWrapper sow = getSharedObjectWrapper(sharedObjectID);
			if (sow != null) {
				debug("handleCreateResponseMessage(from=" + fromID + ",to=" + toID + ")"); //$NON-NLS-1$ //$NON-NLS-2$ //$NON-NLS-3$
				sow.deliverCreateResponse(fromID, resp);
			} else {
				debug("handleCreateResponseMessage...wrapper not found for " //$NON-NLS-1$
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

	protected void handleSharedObjectDisposeMessage(ContainerMessage mess) throws IOException {
		final ID fromID = mess.getFromContainerID();
		final ID toID = mess.getToContainerID();
		final ContainerMessage.SharedObjectDisposeMessage resp = (ContainerMessage.SharedObjectDisposeMessage) mess.getData();
		final ID sharedObjectID = resp.getSharedObjectID();
		debug("handleSharedObjectDisposeMessage(from=" + fromID + ",to=" + toID + ")"); //$NON-NLS-1$ //$NON-NLS-2$ //$NON-NLS-3$
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
		if (toID == null || toID.equals(getID()))
			return true;
		return false;
	}

	protected void handleSharedObjectMessage(ContainerMessage mess) throws IOException {
		final ID fromID = mess.getFromContainerID();
		final ID toID = mess.getToContainerID();
		final ContainerMessage.SharedObjectMessage resp = (ContainerMessage.SharedObjectMessage) mess.getData();
		final ID sharedObjectID = resp.getFromSharedObjectID();
		SOWrapper sow = null;
		Serializable obj = null;
		debug("handleSharedObjectMessage(from=" + fromID + ",to=" + toID + ",sharedObject=" + sharedObjectID + ")"); //$NON-NLS-1$ //$NON-NLS-2$ //$NON-NLS-3$ //$NON-NLS-4$
		synchronized (getGroupMembershipLock()) {
			sow = getSharedObjectWrapper(sharedObjectID);
			if (sow != null) {
				try {
					obj = (Serializable) deserializeSharedObjectMessage((byte[]) resp.getData());
					// Actually deliver event to shared object asynchronously
					sow.deliverSharedObjectMessage(fromID, obj);
				} catch (final ClassNotFoundException e) {
					Trace.catching(ProviderPlugin.PLUGIN_ID, ECFProviderDebugOptions.EXCEPTIONS_CATCHING, this.getClass(), "handleSharedObjectMessage", e); //$NON-NLS-1$
					printToSystemError("Class not found sharedObjectID=" + sharedObjectID + " containerID=" + fromID, e); //$NON-NLS-1$ //$NON-NLS-2$
				}
			}
			forward(fromID, toID, mess);
		}
		// Fire container event notifying container listeners about
		// receiving event.
		if (sow != null)
			fireContainerEvent(new ContainerSharedObjectMessageReceivingEvent(getID(), fromID, sharedObjectID, obj));
	}

	/**
	 * @param mess
	 * @throws IOException not thrown by this implementation.
	 */
	protected void handleUnidentifiedMessage(ContainerMessage mess) throws IOException {
		// do nothing
		ProviderPlugin.getDefault().log(new Status(IStatus.ERROR, ProviderPlugin.PLUGIN_ID, IStatus.ERROR, NLS.bind("unidentified message {0}", mess), null)); //$NON-NLS-1$
		debug("received unidentified message: " + mess); //$NON-NLS-1$
	}

	protected abstract void handleViewChangeMessage(ContainerMessage mess) throws IOException;

	protected boolean isClosing() {
		return isClosing;
	}

	protected void disconnect(IConnection conn) {
		if (conn != null && conn.isConnected())
			conn.disconnect();
	}

	protected ISharedObject load(SharedObjectDescription sd) throws Exception {
		return sharedObjectManager.loadSharedObject(sd);
	}

	/**
	 * @param id
	 * @param obj
	 * @param props
	 * @return SOConfig a non-<code>null</code> instance.
	 * @throws ECFException not thrown by this implementation.
	 */
	protected SOConfig createSharedObjectConfig(ID id, ISharedObject obj, Map props) throws ECFException {
		return new SOConfig(id, getID(), this, props);
	}

	protected SOConfig createRemoteSharedObjectConfig(ID fromID, ReplicaSharedObjectDescription sd, ISharedObject obj) {
		ID homeID = sd.getHomeID();
		if (homeID == null)
			homeID = fromID;
		return new SOConfig(sd.getID(), homeID, this, sd.getProperties());
	}

	protected SOContext createSharedObjectContext(SOConfig soconfig, IQueueEnqueue queue) {
		return new SOContext(soconfig.getSharedObjectID(), soconfig.getHomeContainerID(), this, soconfig.getProperties(), queue);
	}

	protected SOContext createRemoteSharedObjectContext(SOConfig soconfig, IQueueEnqueue queue) {
		return new SOContext(soconfig.getSharedObjectID(), soconfig.getHomeContainerID(), this, soconfig.getProperties(), queue);
	}

	protected SOWrapper createSharedObjectWrapper(ID id, ISharedObject s, Map props) throws ECFException {
		final SOConfig newConfig = createSharedObjectConfig(id, s, props);
		return new SOWrapper(newConfig, s, this);
	}

	protected SOWrapper createRemoteSharedObjectWrapper(ID fromID, ReplicaSharedObjectDescription sd, ISharedObject s) {
		final SOConfig newConfig = createRemoteSharedObjectConfig(fromID, sd, s);
		return new SOWrapper(newConfig, s, this);
	}

	protected void handleLeave(ID leftID, IConnection conn) {
		if (leftID == null)
			return;
		if (groupManager.removeMember(leftID)) {
			try {
				forwardExcluding(getID(), leftID, ContainerMessage.createViewChangeMessage(getID(), null, getNextSequenceNumber(), new ID[] {leftID}, false, null));
			} catch (final IOException e) {
				traceStack("Exception in memberLeave.forwardExcluding", e); //$NON-NLS-1$
			}
		}
		if (conn != null)
			disconnect(conn);
	}

	protected void moveFromLoadingToActive(SOWrapper wrap) {
		groupManager.moveSharedObjectFromLoadingToActive(wrap);
	}

	protected void notifySharedObjectActivated(ID sharedObjectID) {
		synchronized (getGroupMembershipLock()) {
			groupManager.notifyOthersActivated(sharedObjectID);
			fireContainerEvent(new SharedObjectActivatedEvent(getID(), sharedObjectID));
		}
	}

	protected void notifySharedObjectDeactivated(ID sharedObjectID) {
		synchronized (getGroupMembershipLock()) {
			groupManager.notifyOthersDeactivated(sharedObjectID);
			fireContainerEvent(new SharedObjectDeactivatedEvent(getID(), sharedObjectID));
		}
	}

	protected ContainerMessage validateContainerMessage(Object mess) {
		// Message must not be null
		if (mess == null)
			return null;
		if (mess instanceof ContainerMessage) {
			final ContainerMessage contmess = (ContainerMessage) mess;
			final ID fromID = contmess.getFromContainerID();
			if (fromID == null)
				return null;
			// OK..let it continue on it's journey
			return contmess;
		}
		return null;
	}

	/**
	 * @param event
	 * @throws IOException not thrown by this implementation.
	 */
	protected void processAsynch(AsynchEvent event) throws IOException {
		try {
			final Object obj = event.getData();
			if (obj == null) {
				debug("Ignoring null data in event " + event); //$NON-NLS-1$
				return;
			}
			if (!(obj instanceof byte[])) {
				debug("Ignoring event without valid data " + event); //$NON-NLS-1$
				return;
			}
			final ContainerMessage mess = validateContainerMessage(deserializeContainerMessage((byte[]) obj));
			if (mess == null) {
				debug("event not validated: " + event); //$NON-NLS-1$
				return;
			}
			final Serializable submess = mess.getData();
			if (submess == null) {
				debug("submess is null: " + event); //$NON-NLS-1$
				return;
			}
			if (submess instanceof ContainerMessage.CreateMessage)
				handleCreateMessage(mess);
			else if (submess instanceof ContainerMessage.CreateResponseMessage)
				handleCreateResponseMessage(mess);
			else if (submess instanceof ContainerMessage.SharedObjectDisposeMessage)
				handleSharedObjectDisposeMessage(mess);
			else if (submess instanceof ContainerMessage.SharedObjectMessage)
				handleSharedObjectMessage(mess);
			else if (submess instanceof ContainerMessage.ViewChangeMessage)
				handleViewChangeMessage(mess);
			else
				handleUnidentifiedMessage(mess);

		} catch (final IOException except) {
			handleAsynchIOException(except, event);
		}
	}

	protected abstract ID getIDForConnection(IAsynchConnection connection);

	protected abstract void processDisconnect(DisconnectEvent event);

	protected Serializable processSynch(SynchEvent e) throws IOException {
		final ContainerMessage mess = deserializeContainerMessage((byte[]) e.getData());
		final Serializable data = mess.getData();
		// Must be non null
		if (data != null && data instanceof ContainerMessage.LeaveGroupMessage)
			handleLeaveGroupMessage(mess);
		return null;
	}

	abstract protected void queueContainerMessage(ContainerMessage mess) throws IOException;

	protected void removeFromLoading(ID id) {
		groupManager.removeSharedObjectFromLoading(id);
	}

	protected boolean removeRemoteMember(ID remoteMember) {
		return groupManager.removeMember(remoteMember);
	}

	protected ISharedObject removeSharedObject(ID id) {
		synchronized (getGroupMembershipLock()) {
			final SOWrapper wrap = groupManager.getFromActive(id);
			if (wrap == null)
				return null;
			groupManager.removeSharedObject(id);
			return wrap.getSharedObject();
		}
	}

	protected void sendCreate(ID sharedObjectID, ID toContainerID, SharedObjectDescription sd) throws IOException {
		sendCreateSharedObjectMessage(toContainerID, sd);
	}

	protected void sendCreateResponse(ID homeID, ID sharedObjectID, Throwable t, long identifier) throws IOException {
		sendCreateResponseSharedObjectMessage(homeID, sharedObjectID, t, identifier);
	}

	protected void sendCreateResponseSharedObjectMessage(ID toContainerID, ID fromSharedObject, Throwable t, long ident) throws IOException {
		sendMessage(ContainerMessage.createSharedObjectCreateResponseMessage(getID(), toContainerID, getNextSequenceNumber(), fromSharedObject, t, ident));
	}

	protected ID[] sendCreateSharedObjectMessage(ID toContainerID, SharedObjectDescription sd) throws IOException {
		ID[] returnIDs = null;
		if (toContainerID == null) {
			synchronized (getGroupMembershipLock()) {
				// Send message to all
				sendMessage(ContainerMessage.createSharedObjectCreateMessage(getID(), toContainerID, getNextSequenceNumber(), sd));
				returnIDs = getOtherMemberIDs();
			}
		} else {
			// If the create msg is directed to this space, no msg will be sent
			if (getID().equals(toContainerID)) {
				returnIDs = new ID[0];
			} else {
				sendMessage(ContainerMessage.createSharedObjectCreateMessage(getID(), toContainerID, getNextSequenceNumber(), sd));
				returnIDs = new ID[1];
				returnIDs[0] = toContainerID;
			}
		}
		return returnIDs;
	}

	protected Map createContainerPropertiesForSharedObject(ID sharedObjectID) {
		return new HashMap();
	}

	protected void sendDispose(ID toContainerID, ID sharedObjectID) throws IOException {
		sendDisposeSharedObjectMessage(toContainerID, sharedObjectID);
	}

	protected void sendDisposeSharedObjectMessage(ID toContainerID, ID fromSharedObject) throws IOException {
		sendMessage(ContainerMessage.createSharedObjectDisposeMessage(getID(), toContainerID, getNextSequenceNumber(), fromSharedObject));
	}

	protected void sendMessage(ContainerMessage data) throws IOException {
		synchronized (getGroupMembershipLock()) {
			final ID ourID = getID();
			// We don't send to ourselves
			if (!ourID.equals(data.getToContainerID()))
				queueContainerMessage(data);
		}
	}

	protected byte[] serializeSharedObjectMessage(ID sharedObjectID, Object message) throws IOException {
		if (!(message instanceof Serializable))
			throw new NotSerializableException(Messages.SOContainer_Shared_Object_Message + message + Messages.SOContainer_Not_Serializable);
		final ByteArrayOutputStream bouts = new ByteArrayOutputStream();
		final IdentifiableObjectOutputStream ioos = new IdentifiableObjectOutputStream(sharedObjectID.getName(), bouts);
		ioos.writeObject(message);
		return bouts.toByteArray();
	}

	protected Object deserializeSharedObjectMessage(byte[] bytes) throws IOException, ClassNotFoundException {
		final ByteArrayInputStream bins = new ByteArrayInputStream(bytes);
		Object obj = null;
		try {
			// First try normal classloading. In Eclipse environment this will
			// use
			// buddy classloading
			final ObjectInputStream oins = new ObjectInputStream(bins);
			obj = oins.readObject();
		} catch (final ClassNotFoundException e) {
			// first reset stream
			bins.reset();
			// Now try with shared object classloader
			final IdentifiableObjectInputStream iins = new IdentifiableObjectInputStream(new IClassLoaderMapper() {
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
					ISharedObject obj1 = manager.getSharedObject(found);
					if (obj1 == null)
						return null;
					return obj1.getClass().getClassLoader();
				}
			}, bins);
			obj = iins.readObject();
		}
		return obj;
	}

	protected void sendMessage(ID toContainerID, ID sharedObjectID, Object message) throws IOException {
		if (message == null)
			return;
		// fire IContainerSharedObjectMessageSendingEvent
		fireContainerEvent(new ContainerSharedObjectMessageSendingEvent(getID(), toContainerID, sharedObjectID, message));
		final byte[] sendData = serializeSharedObjectMessage(sharedObjectID, message);
		sendSharedObjectMessage(toContainerID, sharedObjectID, sendData);
	}

	protected void sendSharedObjectMessage(ID toContainerID, ID fromSharedObject, Serializable data) throws IOException {
		sendMessage(ContainerMessage.createSharedObjectMessage(getID(), toContainerID, getNextSequenceNumber(), fromSharedObject, data));
	}

	protected void setMaxGroupMembers(int max) {
		groupManager.setMaxMembers(max);
	}

	/**
	 * @param containerEvent
	 */
	protected void fireDelegateContainerEvent(IContainerEvent containerEvent) {
		super.fireContainerEvent(containerEvent);

	}

}
 No newline at end of file