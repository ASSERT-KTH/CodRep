String threadGroupName = "RSRegistry Dispatcher for containerID=" + containerID; //$NON-NLS-1$

/*******************************************************************************
 * Copyright (c) 2010 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.provider.remoteservice.generic;

import java.io.IOException;
import java.io.Serializable;
import java.lang.reflect.InvocationTargetException;
import java.security.*;
import java.util.*;
import org.eclipse.core.runtime.*;
import org.eclipse.core.runtime.jobs.Job;
import org.eclipse.ecf.core.ContainerConnectException;
import org.eclipse.ecf.core.events.*;
import org.eclipse.ecf.core.identity.*;
import org.eclipse.ecf.core.jobs.JobsExecutor;
import org.eclipse.ecf.core.security.IConnectContext;
import org.eclipse.ecf.core.sharedobject.*;
import org.eclipse.ecf.core.sharedobject.events.ISharedObjectActivatedEvent;
import org.eclipse.ecf.core.status.SerializableStatus;
import org.eclipse.ecf.core.util.*;
import org.eclipse.ecf.internal.provider.remoteservice.Activator;
import org.eclipse.ecf.internal.provider.remoteservice.IRemoteServiceProviderDebugOptions;
import org.eclipse.ecf.remoteservice.*;
import org.eclipse.ecf.remoteservice.Constants;
import org.eclipse.ecf.remoteservice.events.*;
import org.eclipse.equinox.concurrent.future.*;
import org.eclipse.osgi.framework.eventmgr.*;
import org.osgi.framework.*;

public class RegistrySharedObject extends BaseSharedObject implements IRemoteServiceContainerAdapter {
	/**
	 * registry impl for local remote service registrations
	 */
	protected RemoteServiceRegistryImpl localRegistry;
	/**
	 * map of registry impls for remote registrys  key:  ID (identifier of remote container), value: RemoteServiceRegistryImpl (copy of remote service registry for remote container
	 */
	protected final Map remoteRegistrys = Collections.synchronizedMap(new HashMap());
	/**
	 * List of remote service listeners (added to/removed from by addRemoteServiceListener/removeRemoteServiceListener
	 */
	protected final List serviceListeners = new ArrayList();
	/**
	 * Local remote service registrations.  key:  ID (identifier of remote container), value:  List (instances of RemoteServiceRegistrationImpl for remote container)
	 */
	protected final Map localServiceRegistrations = new HashMap();
	/**
	 * Map of add registration requests.  key:  Integer (unique Request id), value: AddRegistrationRequest
	 */
	protected Map addRegistrationRequests = new Hashtable();
	/**
	 * Add registration request default timeout
	 * @since 3.0
	 */
	protected int addRegistrationRequestTimeout = ADD_REGISTRATION_REQUEST_TIMEOUT;
	/**
	 * List of invocation requests...instances of Request
	 */
	protected List requests = Collections.synchronizedList(new ArrayList());

	/**
	 * Connect context to be used for connect.
	 * @since 3.0
	 */
	protected IConnectContext connectContext;
	/**
	 * @since 3.3
	 */
	protected final Object rsConnectLock = new Object();
	/**
	 * Whether or not we are connected
	 * @since 3.3
	 */
	protected boolean rsConnected = false;
	/**
	 * Add registration request default timeout.
	 * @since 3.3
	 */
	protected int rsConnectTimeout = ADD_REGISTRATION_REQUEST_TIMEOUT;
	/**
	 * ListenerQueue for asynchronously dispatching remote service registration/unregistration
	 * events
	 * @since 3.3
	 */
	private ListenerQueue rsListenerDispatchQueue;
	/**
	 * Queue lock so that rsListenerDispatchQueue above can be lazily instantiated
	 * @since 3.3
	 */
	private final Object rsQueueLock = new Object();

	/**
	 * EventManager for the rsListenerDispatchEventManager
	 * @since 3.3
	 */
	private EventManager rsListenerDispatchEventManager;

	public RegistrySharedObject() {
		//
	}

	/**
	 * @since 3.3
	 */
	protected int getRSConnectTimeout() {
		return rsConnectTimeout;
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.core.sharedobject.BaseSharedObject#dispose(org.eclipse.ecf.core.identity.ID)
	 */
	public void dispose(ID containerID) {
		super.dispose(containerID);
		unregisterAllServiceRegistrations();
		remoteRegistrys.clear();
		serviceListeners.clear();
		localServiceRegistrations.clear();
		addRegistrationRequests.clear();
		requests.clear();
		pendingUpdateContainers.clear();
		synchronized (rsQueueLock) {
			if (rsListenerDispatchEventManager != null) {
				rsListenerDispatchEventManager.close();
				rsListenerDispatchEventManager = null;
				rsListenerDispatchQueue = null;
			}
		}
	}

	/* Begin implementation of IRemoteServiceContainerAdapter public interface */
	/* (non-Javadoc)
	 * @see org.eclipse.ecf.remoteservice.IRemoteServiceContainerAdapter#addRemoteServiceListener(org.eclipse.ecf.remoteservice.IRemoteServiceListener)
	 */
	public void addRemoteServiceListener(IRemoteServiceListener listener) {
		synchronized (serviceListeners) {
			serviceListeners.add(listener);
		}
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.remoteservice.IRemoteServiceContainerAdapter#removeRemoteServiceListener(org.eclipse.ecf.remoteservice.IRemoteServiceListener)
	 */
	public void removeRemoteServiceListener(IRemoteServiceListener listener) {
		synchronized (serviceListeners) {
			serviceListeners.remove(listener);
		}
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.remoteservice.IRemoteServiceContainerAdapter#getRemoteService(org.eclipse.ecf.remoteservice.IRemoteServiceReference)
	 */
	public IRemoteService getRemoteService(IRemoteServiceReference reference) {
		Trace.entering(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_ENTERING, this.getClass(), "getRemoteService", reference); //$NON-NLS-1$
		final RemoteServiceRegistrationImpl registration = getRemoteServiceRegistrationImpl(reference);
		if (registration == null)
			return null;
		final RemoteServiceImpl remoteService = new RemoteServiceImpl(this, registration);
		Trace.exiting(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_EXITING, this.getClass(), "getRemoteService", remoteService); //$NON-NLS-1$
		return remoteService;
	}

	private void addReferencesFromRemoteRegistrys(ID[] idFilter, String clazz, IRemoteFilter remoteFilter, List referencesFound) {
		synchronized (remoteRegistrys) {
			if (idFilter == null) {
				final ArrayList registrys = new ArrayList(remoteRegistrys.values());
				for (final Iterator i = registrys.iterator(); i.hasNext();) {
					final RemoteServiceRegistryImpl registry = (RemoteServiceRegistryImpl) i.next();
					// Add IRemoteServiceReferences from each remote registry
					addReferencesFromRegistry(clazz, remoteFilter, registry, referencesFound);
				}
			} else {
				for (int i = 0; i < idFilter.length; i++) {
					final RemoteServiceRegistryImpl registry = (RemoteServiceRegistryImpl) remoteRegistrys.get(idFilter[i]);
					if (registry != null) {
						addReferencesFromRegistry(clazz, remoteFilter, registry, referencesFound);
					}
				}
			}
		}
	}

	/**
	 * @since 3.0
	 */
	protected int getAddRegistrationRequestTimeout() {
		return addRegistrationRequestTimeout;
	}

	/**
	 * @since 3.0
	 */
	public IRemoteServiceReference[] getAllRemoteServiceReferences(String clazz, String filter) throws InvalidSyntaxException {
		Trace.entering(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_ENTERING, this.getClass(), "getAllRemoteServiceReferences", new Object[] {clazz, filter}); //$NON-NLS-1$
		final IRemoteServiceReference[] result = getRemoteServiceReferences((ID[]) null, clazz, filter);
		Trace.exiting(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_EXITING, this.getClass(), "getAllRemoteServiceReferences", result); //$NON-NLS-1$
		if (result == null)
			return null;
		return (result.length == 0) ? null : result;
	}

	/**
	 * @since 3.0
	 */
	public IRemoteServiceReference[] getRemoteServiceReferences(ID targetID, String clazz, String filter) throws InvalidSyntaxException, ContainerConnectException {
		Trace.entering(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_ENTERING, this.getClass(), "getRemoteServiceReferences", new Object[] {targetID, clazz, filter}); //$NON-NLS-1$
		// If no target specified, just search for all available references
		if (targetID == null) {
			final IRemoteServiceReference[] result = getRemoteServiceReferences((ID[]) null, clazz, filter);
			Trace.exiting(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_EXITING, this.getClass(), "getRemoteServiceReferences", result); //$NON-NLS-1$
			return result;
		}
		// If we're not already connected, then connect to targetID
		connectToRemoteServiceTarget(targetID);

		// Now we're connected (or already were connected), so we look for remote service references for target
		final IRemoteServiceReference[] result = getRemoteServiceReferences((ID[]) null, clazz, filter);
		Trace.exiting(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_EXITING, this.getClass(), "getRemoteServiceReferences", result); //$NON-NLS-1$
		return result;
	}

	/**
	 * @since 3.3 for preventing issues like bug https://bugs.eclipse.org/bugs/show_bug.cgi?id=304427
	 */
	protected void connectToRemoteServiceTarget(ID targetID) throws ContainerConnectException {
		// This code cannot be reentrant.
		synchronized (rsConnectLock) {
			ISharedObjectContext context = getContext();
			// If we don't have a context we can't connect and we throw a container connect exception
			if (context == null)
				throw new ContainerConnectException("Cannot connect without context"); //$NON-NLS-1$
			ID connectedID = context.getConnectedID();
			// If we're already connected to something then we don't need to connect...and we return
			if (connectedID != null)
				return;
			// else we just try to connect to target
			context.connect(targetID, connectContext);
			// wait to receive connected event
			waitForConnectedEvent(context, targetID);
			// Wait for pending registry updates after connect
			waitForPendingUpdatesAfterConnect(getAddRegistrationRequestTimeout());
		}
	}

	private void waitForConnectedEvent(ISharedObjectContext context, ID targetID) throws ContainerConnectException {
		// Wait until we receive the IContainerConnectedEvent on the shared object thread
		long startTime = System.currentTimeMillis();
		int rsTimeout = getRSConnectTimeout();
		long endTime = startTime + rsTimeout;
		while (!rsConnected && (endTime >= System.currentTimeMillis())) {
			try {
				rsConnectLock.wait(rsTimeout / 10);
			} catch (InterruptedException e) {
				throw new ContainerConnectException("No notification of registry connect complete for targetID=" + targetID); //$NON-NLS-1$
			}
		}
		if (!rsConnected) {
			context.disconnect();
			throw new ContainerConnectException("Could not complete registry connect for targetID=" + targetID); //$NON-NLS-1$
		}
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.remoteservice.IRemoteServiceContainerAdapter#getRemoteServiceReferences(org.eclipse.ecf.core.identity.ID[], java.lang.String, java.lang.String)
	 */
	public IRemoteServiceReference[] getRemoteServiceReferences(ID[] idFilter, String clazz, String filter) throws InvalidSyntaxException {
		Trace.entering(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_ENTERING, this.getClass(), "getRemoteServiceReferences", new Object[] {idFilter, clazz, filter}); //$NON-NLS-1$
		final IRemoteFilter remoteFilter = (filter == null) ? null : new RemoteFilterImpl(filter);
		// If the idFilter is not null, then wait for updates from listed IDs given in idFilter
		if (idFilter != null)
			waitForPendingUpdates(idFilter, getAddRegistrationRequestTimeout());
		// Lookup from remote registrys...add to given references List
		final List references = new ArrayList();
		addReferencesFromRemoteRegistrys(idFilter, clazz, remoteFilter, references);
		ID localContainerID = getLocalContainerID();
		if (idFilter == null || Arrays.asList(idFilter).contains(localContainerID)) {
			synchronized (localRegistry) {
				// Add any from local registry
				addReferencesFromRegistry(clazz, remoteFilter, localRegistry, references);
			}
		}
		final IRemoteServiceReference[] result = (IRemoteServiceReference[]) references.toArray(new IRemoteServiceReference[references.size()]);
		Trace.exiting(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_EXITING, this.getClass(), "getRemoteServiceReferences", result); //$NON-NLS-1$
		return (result.length == 0) ? null : result;
	}

	protected Serializable getAddRegistrationRequestCredentials(AddRegistrationRequest request) {
		return null;
	}

	protected ID[] getTargetsFromProperties(Dictionary properties) {
		if (properties == null)
			return null;
		List results = new ArrayList();
		Object o = properties.get(Constants.SERVICE_REGISTRATION_TARGETS);
		if (o != null) {
			if (o instanceof ID)
				results.add(o);
			if (o instanceof ID[]) {
				ID[] targets = (ID[]) o;
				for (int i = 0; i < targets.length; i++)
					results.add(targets[i]);
			}
		}
		if (results.size() == 0)
			return null;
		return (ID[]) results.toArray(new ID[] {});
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.remoteservice.IRemoteServiceContainerAdapter#registerRemoteService(java.lang.String[], java.lang.Object, java.util.Dictionary)
	 */
	public IRemoteServiceRegistration registerRemoteService(String[] clazzes, Object service, Dictionary properties) {
		Trace.entering(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_ENTERING, this.getClass(), "registerRemoteService", new Object[] {clazzes, service, properties}); //$NON-NLS-1$
		if (service == null) {
			throw new NullPointerException("service cannot be null"); //$NON-NLS-1$
		}
		final int size = clazzes.length;

		if (size == 0) {
			throw new IllegalArgumentException("service classes list is empty"); //$NON-NLS-1$
		}

		final String[] copy = new String[clazzes.length];
		for (int i = 0; i < clazzes.length; i++) {
			copy[i] = new String(clazzes[i].getBytes());
		}
		clazzes = copy;

		final String invalidService = checkServiceClass(clazzes, service);
		if (invalidService != null) {
			throw new IllegalArgumentException("Service=" + invalidService + " is invalid"); //$NON-NLS-1$ //$NON-NLS-2$
		}

		final RemoteServiceRegistrationImpl reg = new RemoteServiceRegistrationImpl();
		reg.publish(this, localRegistry, service, clazzes, properties);

		final ID[] targets = getTargetsFromProperties(properties);
		if (targets == null)
			sendAddRegistrations(null, null, new RemoteServiceRegistrationImpl[] {reg});
		else
			for (int i = 0; i < targets.length; i++)
				sendAddRegistrations(targets[i], null, new RemoteServiceRegistrationImpl[] {reg});

		fireRemoteServiceListeners(createRegisteredEvent(reg));
		Trace.exiting(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_EXITING, this.getClass(), "registerRemoteService", reg); //$NON-NLS-1$
		return reg;
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.remoteservice.IRemoteServiceContainerAdapter#ungetRemoteService(org.eclipse.ecf.remoteservice.IRemoteServiceReference)
	 */
	public boolean ungetRemoteService(IRemoteServiceReference ref) {
		IRemoteServiceID serviceID = ref.getID();
		if (serviceID == null)
			return false;
		synchronized (localRegistry) {
			RemoteServiceRegistrationImpl registry = localRegistry.findRegistrationForRemoteServiceId(serviceID);
			if (registry != null)
				return true;
		}
		synchronized (remoteRegistrys) {
			final RemoteServiceRegistryImpl registry = (RemoteServiceRegistryImpl) remoteRegistrys.get(serviceID.getContainerID());
			if (registry != null) {
				return true;
			}
		}
		return false;
	}

	protected ISharedObjectContext getSOContext() {
		return super.getContext();
	}

	/* End implementation of IRemoteServiceContainerAdapter public interface */

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.core.sharedobject.BaseSharedObject#initialize()
	 */
	public void initialize() throws SharedObjectInitException {
		super.initialize();
		Trace.entering(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_ENTERING, this.getClass(), "initialize"); //$NON-NLS-1$
		localRegistry = new RemoteServiceRegistryImpl(getLocalContainerID());
		super.addEventProcessor(new IEventProcessor() {
			public boolean processEvent(Event arg0) {
				if (arg0 instanceof IContainerConnectedEvent) {
					handleContainerConnectedEvent((IContainerConnectedEvent) arg0);
				} else if (arg0 instanceof IContainerDisconnectedEvent) {
					handleContainerDisconnectedEvent((IContainerDisconnectedEvent) arg0);
				} else if (arg0 instanceof IContainerEjectedEvent) {
					handleContainerEjectedEvent((IContainerEjectedEvent) arg0);
				} else if (arg0 instanceof ISharedObjectActivatedEvent) {
					if (getSOContext().getConnectedID() != null) {
						// We're already connected, so add exiting members
						// to expected set and send request for update
						addPendingContainers(getGroupMemberIDs());
						sendRegistryUpdateRequest();
						setRegistryConnected(true);
					}
				}
				return false;
			}
		});
		Trace.exiting(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_EXITING, this.getClass(), "initialize"); //$NON-NLS-1$
	}

	/**
	 * @since 3.3
	 */
	protected void handleContainerEjectedEvent(IContainerEjectedEvent arg0) {
		handleTargetGoneEvent(arg0.getTargetID());
	}

	private void handleTargetGoneEvent(ID targetID) {
		RemoteServiceRegistrationImpl registrations[] = null;
		synchronized (remoteRegistrys) {
			final RemoteServiceRegistryImpl registry = getRemoteRegistry(targetID);
			if (registry != null) {
				removeRemoteRegistry(targetID);
				registrations = registry.getRegistrations();
				if (registrations != null) {
					for (int i = 0; i < registrations.length; i++) {
						registry.unpublishService(registrations[i]);
						unregisterServiceRegistrationsForContainer(registrations[i].getContainerID());
					}
				}
			}
		}
		// Remove from pending updates
		removePendingContainers(targetID);
		if (getConnectedID() == null)
			setRegistryConnected(false);
		// Do notification outside synchronized block
		if (registrations != null) {
			for (int i = 0; i < registrations.length; i++) {
				fireRemoteServiceListeners(createUnregisteredEvent(registrations[i]));
			}
		}
	}

	/**
	 * @since 3.3
	 */
	protected void setRegistryConnected(boolean connected) {
		synchronized (rsConnectLock) {
			rsConnected = connected;
			rsConnectLock.notify();
		}
	}

	protected void handleContainerDisconnectedEvent(IContainerDisconnectedEvent event) {
		Trace.entering(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_ENTERING, this.getClass(), "handleContainerDisconnectedEvent", event); //$NON-NLS-1$
		handleTargetGoneEvent(event.getTargetID());
		Trace.exiting(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_EXITING, this.getClass(), "handleContainerDisconnectedEvent"); //$NON-NLS-1$
	}

	protected void sendRegistryUpdate(ID targetContainerID) {
		synchronized (localRegistry) {
			final RemoteServiceRegistrationImpl registrations[] = localRegistry.getRegistrations();
			sendAddRegistrations(targetContainerID, null, registrations);
		}
	}

	private Hashtable pendingUpdateContainers = new Hashtable();

	private void addPendingContainers(ID[] ids) {
		if (ids == null)
			return;
		synchronized (pendingUpdateContainers) {
			for (int i = 0; i < ids.length; i++) {
				if (!ids[i].equals(getLocalContainerID())) {
					pendingUpdateContainers.put(ids[i], ids[i]);
					Trace.trace(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.DEBUG, this.getClass(), getLocalContainerID() + ".addPendingContainers", "added containerIDs=" + ((ids == null) ? "null" : Arrays.asList(ids).toString()) + ",pendingUpdateContainer=" + pendingUpdateContainers); //$NON-NLS-1$ //$NON-NLS-2$ //$NON-NLS-3$ //$NON-NLS-4$
				}
			}
		}
	}

	private boolean removePendingContainers(ID id) {
		if (id == null)
			return false;
		synchronized (pendingUpdateContainers) {
			Object result = pendingUpdateContainers.remove(id);
			Trace.trace(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.DEBUG, this.getClass(), getLocalContainerID() + ".removePendingContainers", "removed containerID=" + id + ",pendingUpdateContainer=" + pendingUpdateContainers); //$NON-NLS-1$ //$NON-NLS-2$ //$NON-NLS-3$
			pendingUpdateContainers.notify();
			return result != null;
		}
	}

	private boolean anyPending(ID[] containerIDs) {
		if (containerIDs == null)
			return pendingUpdateContainers.size() > 0;
		for (int i = 0; i < containerIDs.length; i++) {
			if (pendingUpdateContainers.containsKey(containerIDs[i]))
				return true;
		}
		return false;
	}

	private void waitForPendingUpdatesAfterConnect(long timeout) {
		waitForPendingUpdates(null, timeout);
	}

	private void waitForPendingUpdates(ID[] containerIDs, long timeout) {
		Trace.entering(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_ENTERING, this.getClass(), getLocalContainerID() + ".waitForPendingUpdates", new Object[] {containerIDs, new Long(timeout), pendingUpdateContainers}); //$NON-NLS-1$
		long startTime = System.currentTimeMillis();
		long endTime = startTime + timeout;
		synchronized (pendingUpdateContainers) {
			while (anyPending(containerIDs) && (endTime >= System.currentTimeMillis())) {
				try {
					Trace.trace(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.DEBUG, this.getClass(), "waitForPendingUpdates", "waiting containerIDs=" + ((containerIDs == null) ? "null" : Arrays.asList(containerIDs).toString()) + ",pendingUpdateContainer=" + pendingUpdateContainers); //$NON-NLS-1$ //$NON-NLS-2$ //$NON-NLS-3$ //$NON-NLS-4$
					pendingUpdateContainers.wait(timeout / 10);
				} catch (InterruptedException e) {
					// just return
					return;
				}
			}
		}
		Trace.exiting(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_EXITING, this.getClass(), "waitForPendingUpdates", new Object[] {containerIDs, new Long(timeout), pendingUpdateContainers}); //$NON-NLS-1$
	}

	protected void handleContainerConnectedEvent(IContainerConnectedEvent event) {
		Trace.entering(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_ENTERING, this.getClass(), "handleContainerConnectedEvent", event); //$NON-NLS-1$
		// If we're a group manager or the newly connected container is the
		// group manager
		ID targetID = event.getTargetID();
		// Add the target to the set of pending update containers.  These are the ones we expect
		// to hear from about their registry contents
		addPendingContainers(new ID[] {targetID});
		// And send a registry update to the given target
		sendRegistryUpdate(targetID);
		// If we are now connected, then set our registry connected
		ID connectedID = getConnectedID();
		if (connectedID != null && connectedID.equals(targetID))
			setRegistryConnected(true);
		Trace.exiting(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_EXITING, this.getClass(), "handleContainerConnectedEvent"); //$NON-NLS-1$
	}

	private Request createRequest(RemoteServiceRegistrationImpl remoteRegistration, IRemoteCall call, IRemoteCallListener listener) {
		final RemoteServiceReferenceImpl refImpl = (RemoteServiceReferenceImpl) remoteRegistration.getReference();
		return new Request(this.getLocalContainerID(), remoteRegistration.getServiceId(), RemoteCallImpl.createRemoteCall(refImpl.getRemoteClass(), call.getMethod(), call.getParameters(), call.getTimeout()), listener);
	}

	void doFireRemoteServiceListeners(IRemoteServiceEvent event) {
		List entries;
		synchronized (serviceListeners) {
			entries = new ArrayList(serviceListeners);
		}
		for (final Iterator i = entries.iterator(); i.hasNext();) {
			final IRemoteServiceListener l = (IRemoteServiceListener) i.next();
			l.handleServiceEvent(event);
		}
	}

	protected void fireRemoteServiceListeners(IRemoteServiceEvent event) {
		synchronized (rsQueueLock) {
			if (rsListenerDispatchQueue == null) {
				ID containerID = getLocalContainerID();
				String threadGroupName = "RSRegistry Dispatcher for " + containerID.getName(); //$NON-NLS-1$
				ThreadGroup eventGroup = new ThreadGroup(threadGroupName);
				eventGroup.setDaemon(true);
				rsListenerDispatchEventManager = new EventManager(threadGroupName, eventGroup);
				rsListenerDispatchQueue = new ListenerQueue(rsListenerDispatchEventManager);
				CopyOnWriteIdentityMap listeners = new CopyOnWriteIdentityMap();
				listeners.put(this, this);

				rsListenerDispatchQueue.queueListeners(listeners.entrySet(), new EventDispatcher() {
					public void dispatchEvent(Object eventListener, Object listenerObject, int eventAction, Object eventObject) {
						doFireRemoteServiceListeners((IRemoteServiceEvent) eventObject);
					}
				});
			}
		}
		rsListenerDispatchQueue.dispatchEventAsynchronous(0, event);
	}

	private RemoteServiceRegistrationImpl getRemoteServiceRegistrationImpl(IRemoteServiceReference reference) {
		if (reference instanceof RemoteServiceReferenceImpl) {
			final RemoteServiceReferenceImpl ref = (RemoteServiceReferenceImpl) reference;
			if (!ref.isActive()) {
				return null;
			}
			return ref.getRegistration();
		}
		return null;
	}

	private void addReferencesFromRegistry(String clazz, IRemoteFilter remoteFilter, RemoteServiceRegistryImpl registry, List references) {
		final IRemoteServiceReference[] rs = registry.lookupServiceReferences(clazz, remoteFilter);
		if (rs != null) {
			for (int j = 0; j < rs.length; j++) {
				references.add(rs[j]);
			}
		}
	}

	protected Object callSynch(RemoteServiceRegistrationImpl registration, IRemoteCall call) throws ECFException {
		Trace.entering(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_ENTERING, this.getClass(), "callSynch", new Object[] {registration, call}); //$NON-NLS-1$
		boolean doneWaiting = false;
		Response response = null;
		try {
			// First send request
			final Request request = sendCallRequest(registration, call);
			long requestId = request.getRequestId();
			Trace.trace(Activator.PLUGIN_ID, "callSync request sent with requestid=" + requestId); //$NON-NLS-1$
			// Then get the specified timeout and calculate when we should
			// timeout in real time
			final long timeout = call.getTimeout() + System.currentTimeMillis();
			// Now loop until timeout time has elapsed
			while ((timeout - System.currentTimeMillis()) > 0 && !doneWaiting) {
				synchronized (request) {
					if (request.isDone()) {
						Trace.trace(Activator.PLUGIN_ID, "callSynch.request/response done for requestId=" + requestId); //$NON-NLS-1$
						doneWaiting = true;
						response = request.getResponse();
						if (response == null)
							throw new ECFException("Invalid response for requestId=" + requestId); //$NON-NLS-1$
					} else {
						Trace.trace(Activator.PLUGIN_ID, "Waiting " + RESPONSE_WAIT_INTERVAL + " for response to request: " + requestId); //$NON-NLS-1$ //$NON-NLS-2$
						request.wait(RESPONSE_WAIT_INTERVAL);
					}
				}
			}
			if (!doneWaiting)
				throw new ECFException("Request timed out after " + Long.toString(call.getTimeout()) + "ms", new TimeoutException(call.getTimeout())); //$NON-NLS-1$ //$NON-NLS-2$
		} catch (final IOException e) {
			log(CALL_REQUEST_ERROR_CODE, CALL_REQUEST_ERROR_MESSAGE, e);
			throw new ECFException("Error sending request", e); //$NON-NLS-1$
		} catch (final InterruptedException e) {
			log(CALL_REQUEST_TIMEOUT_ERROR_CODE, CALL_REQUEST_TIMEOUT_ERROR_MESSAGE, e);
			throw new ECFException("Wait for response interrupted", e); //$NON-NLS-1$
		}
		// Success...now get values and return
		Object result = null;
		if (response.hadException())
			throw new ECFException("Exception in remote call", response.getException()); //$NON-NLS-1$
		result = response.getResponse();

		Trace.exiting(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_EXITING, this.getClass(), "callSynch", result); //$NON-NLS-1$
		return result;

	}

	protected void fireCallStartEvent(IRemoteCallListener listener, final long requestId, final IRemoteServiceReference reference, final IRemoteCall call) {
		if (listener != null) {
			listener.handleEvent(new IRemoteCallStartEvent() {
				public long getRequestId() {
					return requestId;
				}

				public IRemoteCall getCall() {
					return call;
				}

				public IRemoteServiceReference getReference() {
					return reference;
				}

				public String toString() {
					final StringBuffer buf = new StringBuffer("IRemoteCallStartEvent["); //$NON-NLS-1$
					buf.append(";reference=").append(reference).append(";call=").append(call).append("]"); //$NON-NLS-1$ //$NON-NLS-2$ //$NON-NLS-3$
					return buf.toString();
				}
			});
		}
	}

	protected void fireCallCompleteEvent(IRemoteCallListener listener, final long requestId, final Object response, final boolean hadException, final Throwable exception) {
		if (listener != null) {
			listener.handleEvent(new IRemoteCallCompleteEvent() {
				public long getRequestId() {
					return requestId;
				}

				public Throwable getException() {
					return exception;
				}

				public Object getResponse() {
					return response;
				}

				public boolean hadException() {
					return hadException;
				}

				public String toString() {
					final StringBuffer buf = new StringBuffer("IRemoteCallCompleteEvent["); //$NON-NLS-1$
					buf.append(";response=").append(response).append(";hadException=").append(hadException).append(";exception=").append(exception).append("]"); //$NON-NLS-1$ //$NON-NLS-2$ //$NON-NLS-3$ //$NON-NLS-4$
					return buf.toString();
				}
			});
		}
	}

	static String checkServiceClass(final String[] clazzes, final Object serviceObject) {
		final ClassLoader cl = (ClassLoader) AccessController.doPrivileged(new PrivilegedAction() {
			public Object run() {
				return serviceObject.getClass().getClassLoader();
			}
		});
		for (int i = 0; i < clazzes.length; i++) {
			try {
				final Class serviceClazz = cl == null ? Class.forName(clazzes[i]) : cl.loadClass(clazzes[i]);
				if (!serviceClazz.isInstance(serviceObject)) {
					return clazzes[i];
				}
			} catch (final ClassNotFoundException e) {
				// This check is rarely done
				if (extensiveCheckServiceClass(clazzes[i], serviceObject.getClass())) {
					return clazzes[i];
				}
			}
		}
		return null;
	}

	private static boolean extensiveCheckServiceClass(String clazz, Class serviceClazz) {
		if (clazz.equals(serviceClazz.getName())) {
			return false;
		}
		final Class[] interfaces = serviceClazz.getInterfaces();
		for (int i = 0; i < interfaces.length; i++) {
			if (!extensiveCheckServiceClass(clazz, interfaces[i])) {
				return false;
			}
		}
		final Class superClazz = serviceClazz.getSuperclass();
		if (superClazz != null) {
			if (!extensiveCheckServiceClass(clazz, superClazz)) {
				return false;
			}
		}
		return true;
	}

	/**
	 * Message send and handlers
	 */
	private static final String FIRE_REQUEST = "handleFireRequest"; //$NON-NLS-1$

	private static final String FIRE_REQUEST_ERROR_MESSAGE = "exception sending fire request message"; //$NON-NLS-1$

	private static final int FIRE_REQUEST_ERROR_CODE = 202;

	private static final String CALL_REQUEST = "handleCallRequest"; //$NON-NLS-1$

	private static final String CALL_REQUEST_ERROR_MESSAGE = "exception sending call request message"; //$NON-NLS-1$

	private static final int CALL_REQUEST_ERROR_CODE = 203;

	private static final String CALL_REQUEST_TIMEOUT_ERROR_MESSAGE = "timeout for remote call"; //$NON-NLS-1$

	private static final int CALL_REQUEST_TIMEOUT_ERROR_CODE = 204;

	private static final String UNREGISTER = "handleUnregister"; //$NON-NLS-1$

	private static final String UNREGISTER_ERROR_MESSAGE = "exception sending service unregister message"; //$NON-NLS-1$

	private static final int UNREGISTER_ERROR_CODE = 206;

	private static final int MSG_INVOKE_ERROR_CODE = 207;

	private static final int SERVICE_INVOKE_ERROR_CODE = 208;

	private static final String CALL_RESPONSE = "handleCallResponse"; //$NON-NLS-1$

	private static final String CALL_RESPONSE_ERROR_MESSAGE = "Exception sending response"; //$NON-NLS-1$

	private static final int CALL_RESPONSE_ERROR_CODE = 210;

	private static final String REQUEST_NOT_FOUND_ERROR_MESSAGE = "request not found for response"; //$NON-NLS-1$

	private static final int REQUEST_NOT_FOUND_ERROR_CODE = 211;

	private static final long RESPONSE_WAIT_INTERVAL = 5000;

	private static final String ADD_REGISTRATION = "handleAddRegistration"; //$NON-NLS-1$

	private static final String ADD_REGISTRATIONS = "handleAddRegistrations"; //$NON-NLS-1$

	private static final String ADD_REGISTRATION_ERROR_MESSAGE = "exception sending add service registration message"; //$NON-NLS-1$

	private static final int ADD_REGISTRATION_ERROR_CODE = 212;

	private static final String ADD_REGISTRATION_REFUSED = "handleAddRegistrationRefused"; //$NON-NLS-1$

	private static final String ADD_REGISTRATION_REFUSED_ERROR_MESSAGE = "Error sending addRegistration refused"; //$NON-NLS-1$

	private static final int ADD_REGISTRATION_REFUSED_ERROR_CODE = 214;

	private static final String REQUEST_SERVICE = "handleRequestService"; //$NON-NLS-1$

	private static final int REQUEST_SERVICE_ERROR_CODE = 213;

	private static final String REQUEST_SERVICE_ERROR_MESSAGE = "Error sending requestServiceReference"; //$NON-NLS-1$

	private static final String REGISTRY_UPDATE_REQUEST = "handleRegistryUpdateRequest"; //$NON-NLS-1$

	/**
	 * @since 3.3
	 */
	protected static final int ADD_REGISTRATION_REQUEST_TIMEOUT = new Integer(System.getProperty("ecf.addregistrationrequest.timeout", "7000")).intValue(); //$NON-NLS-1$ //$NON-NLS-2$

	protected void sendRegistryUpdateRequest() {
		Trace.entering(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_ENTERING, this.getClass(), "sendRegistryUpdateRequest"); //$NON-NLS-1$
		try {
			sendSharedObjectMsgTo(null, SharedObjectMsg.createMsg(REGISTRY_UPDATE_REQUEST, getLocalContainerID()));
		} catch (final IOException e) {
			log(CALL_RESPONSE_ERROR_CODE, CALL_RESPONSE_ERROR_MESSAGE, e);
		}
		Trace.exiting(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_EXITING, this.getClass(), "sendRegistryUpdateRequest"); //$NON-NLS-1$
	}

	protected void handleRegistryUpdateRequest(ID remoteContainerID) {
		Trace.entering(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_ENTERING, this.getClass(), REGISTRY_UPDATE_REQUEST);
		ID localContainerID = getLocalContainerID();
		if (remoteContainerID == null || localContainerID == null || localContainerID.equals(remoteContainerID)) {
			return;
		}
		sendRegistryUpdate(remoteContainerID);
		Trace.exiting(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_EXITING, this.getClass(), REGISTRY_UPDATE_REQUEST);
	}

	protected AddRegistrationRequest sendAddRegistrationRequest(ID receiver, AddRegistrationRequest request, Serializable credentials) {
		Trace.entering(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_ENTERING, this.getClass(), "sendAddRegistrationRequest", new Object[] {receiver, request, credentials}); //$NON-NLS-1$
		Assert.isNotNull(receiver);
		Assert.isNotNull(request);
		try {
			sendSharedObjectMsgTo(receiver, SharedObjectMsg.createMsg(null, REQUEST_SERVICE, new Object[] {getLocalContainerID(), request, request.getId(), credentials}));
		} catch (final IOException e) {
			log(REQUEST_SERVICE_ERROR_CODE, REQUEST_SERVICE_ERROR_MESSAGE, e);
		}
		Trace.exiting(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_EXITING, this.getClass(), "sendAddRegistrationRequest"); //$NON-NLS-1$
		return request;
	}

	protected void checkRequestServiceAuthorization(ID remoteContainerID, AddRegistrationRequest request, Serializable credentials) throws AccessControlException {
		Trace.entering(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_ENTERING, this.getClass(), "checkRequestServiceAuthorization", new Object[] {remoteContainerID, request, credentials}); //$NON-NLS-1$
		return;
	}

	protected void handleRequestService(ID remoteContainerID, AddRegistrationRequest request, Integer requestId, Serializable credentials) {
		Trace.entering(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_ENTERING, this.getClass(), "handleRequestServiceReference", new Object[] {remoteContainerID, request, requestId, credentials}); //$NON-NLS-1$
		if (remoteContainerID == null || requestId == null)
			return;
		if (request == null)
			return;
		IRemoteFilter rf = null;
		try {
			rf = (request.getFilter() == null) ? null : new RemoteFilterImpl(request.getFilter());
		} catch (InvalidSyntaxException e) {
			// log and set rf to null and ignore
			log("handleRequestService invalid syntax exception for filter", e); //$NON-NLS-1$
			rf = null;
		}
		try {
			checkRequestServiceAuthorization(remoteContainerID, request, credentials);
		} catch (AccessControlException e) {
			// Log and return...i.e. do nothing
			log("handleRequestService. checkRequestServiceAuthorization exception", e); //$NON-NLS-1$
			sendAddRegistrationRequestRefused(remoteContainerID, requestId, e);
			return;
		}
		String service = request.getService();
		synchronized (localRegistry) {
			RemoteServiceRegistrationImpl[] regs = null;
			if (service == null) {
				regs = localRegistry.getRegistrations();
			} else {
				RemoteServiceReferenceImpl[] srs = (RemoteServiceReferenceImpl[]) localRegistry.lookupServiceReferences(request.getService(), rf);
				List regsList = new ArrayList();
				if (srs != null && srs.length > 0) {
					for (int i = 0; i < srs.length; i++) {
						RemoteServiceRegistrationImpl impl = getRemoteServiceRegistrationImpl(srs[i]);
						if (impl != null)
							regsList.add(impl);
					}
				}
				if (regsList.size() > 0) {
					regs = (RemoteServiceRegistrationImpl[]) regsList.toArray(new RemoteServiceRegistrationImpl[] {});
				}
			}
			sendAddRegistrations(remoteContainerID, requestId, regs);
		}
		Trace.exiting(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_EXITING, this.getClass(), "handleRequestService"); //$NON-NLS-1$
	}

	protected void sendAddRegistration(ID receiver, RemoteServiceRegistrationImpl reg) {
		sendAddRegistration(receiver, null, reg);
	}

	protected void sendAddRegistration(ID receiver, Integer requestId, RemoteServiceRegistrationImpl reg) {
		Trace.entering(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_ENTERING, this.getClass(), "sendAddRegistration", new Object[] {receiver, requestId, reg}); //$NON-NLS-1$
		try {
			sendSharedObjectMsgTo(receiver, SharedObjectMsg.createMsg(null, ADD_REGISTRATION, getLocalContainerID(), requestId, reg));
		} catch (final IOException e) {
			log(ADD_REGISTRATION_ERROR_CODE, ADD_REGISTRATION_ERROR_MESSAGE, e);
		}
		Trace.exiting(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_EXITING, this.getClass(), "sendAddRegistration"); //$NON-NLS-1$
	}

	/**
	 * @since 3.3
	 */
	protected void sendAddRegistrations(ID receiver, Integer requestId, RemoteServiceRegistrationImpl[] regs) {
		Trace.entering(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_ENTERING, this.getClass(), "sendAddRegistrations", new Object[] {receiver, requestId, regs}); //$NON-NLS-1$
		try {
			sendSharedObjectMsgTo(receiver, SharedObjectMsg.createMsg(null, ADD_REGISTRATIONS, getLocalContainerID(), requestId, regs));
		} catch (final IOException e) {
			log(ADD_REGISTRATION_ERROR_CODE, ADD_REGISTRATION_ERROR_MESSAGE, e);
		}
		Trace.exiting(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_EXITING, this.getClass(), "sendAddRegistrations"); //$NON-NLS-1$
	}

	protected void sendAddRegistrationRequestRefused(ID receiver, Integer requestId, Exception except) {
		Trace.entering(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_ENTERING, this.getClass(), "sendAddRegistrationRequestRefused", new Object[] {receiver, except}); //$NON-NLS-1$
		try {
			sendSharedObjectMsgTo(receiver, SharedObjectMsg.createMsg(null, ADD_REGISTRATION_REFUSED, getLocalContainerID(), requestId, except));
		} catch (final IOException e) {
			log(ADD_REGISTRATION_REFUSED_ERROR_CODE, ADD_REGISTRATION_REFUSED_ERROR_MESSAGE, e);
		}
		Trace.exiting(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_EXITING, this.getClass(), "sendAddRegistrationRequestRefused"); //$NON-NLS-1$
	}

	protected void handleAddRegistrationRequestRefused(ID remoteContainerID, Integer requestId, AccessControlException e) {
		if (remoteContainerID == null || requestId == null)
			return;
		// else lookup AddRegistrationRequest and notify
		notifyAddRegistrationResponse(remoteContainerID, requestId, e);
	}

	protected void handleAddRegistration(ID remoteContainerID, final RemoteServiceRegistrationImpl registration) {
		handleAddRegistration(remoteContainerID, null, registration);
	}

	/**
	 * @since 3.3
	 */
	protected void handleAddRegistrations(ID remoteContainerID, Integer requestId, final RemoteServiceRegistrationImpl[] registrations) {
		Trace.entering(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_ENTERING, this.getClass(), ADD_REGISTRATIONS, new Object[] {remoteContainerID, registrations});
		ID localContainerID = getLocalContainerID();
		if (remoteContainerID == null || localContainerID == null || localContainerID.equals(remoteContainerID)) {
			return;
		}
		List addedRegistrations = new ArrayList();
		if (registrations != null && registrations.length > 0) {
			synchronized (remoteRegistrys) {
				// Find registry for remoteContainer
				RemoteServiceRegistryImpl registry = getRemoteRegistry(remoteContainerID);
				// If there's not one already then lazily make one and add it
				if (registry == null) {
					registry = new RemoteServiceRegistryImpl(remoteContainerID);
					addRemoteRegistry(registry);
				}
				for (int i = 0; i < registrations.length; i++) {
					RemoteServiceRegistrationImpl[] regs = registry.getRegistrations();
					List regList = Arrays.asList(regs);
					if (!regList.contains(registrations[i])) {
						addedRegistrations.add(registrations[i]);
						registry.publishService(registrations[i]);
						localRegisterService(registrations[i]);
					}
				}
			}
		}
		// Outside synchronized block do notification
		if (requestId != null)
			notifyAddRegistrationResponse(remoteContainerID, requestId, null);

		// remove pending containers
		removePendingContainers(remoteContainerID);

		for (Iterator i = addedRegistrations.iterator(); i.hasNext();) {
			fireRemoteServiceListeners(createRegisteredEvent((RemoteServiceRegistrationImpl) i.next()));
		}
		Trace.exiting(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_EXITING, this.getClass(), ADD_REGISTRATIONS);
	}

	protected void handleAddRegistration(ID remoteContainerID, Integer requestId, final RemoteServiceRegistrationImpl registration) {
		Trace.entering(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_ENTERING, this.getClass(), ADD_REGISTRATION, new Object[] {remoteContainerID, registration});
		ID localContainerID = getLocalContainerID();
		if (remoteContainerID == null || localContainerID == null || localContainerID.equals(remoteContainerID)) {
			return;
		}
		boolean added = false;
		synchronized (remoteRegistrys) {
			// Find registry for remoteContainer
			RemoteServiceRegistryImpl registry = getRemoteRegistry(remoteContainerID);
			// If there's not one already then lazily make one and add it
			if (registry == null) {
				registry = new RemoteServiceRegistryImpl(remoteContainerID);
				addRemoteRegistry(registry);
			}
			// publish service in this registry. At this point it's ready to go
			RemoteServiceRegistrationImpl[] regs = registry.getRegistrations();
			List regList = Arrays.asList(regs);
			if (!regList.contains(registration)) {
				added = true;
				registry.publishService(registration);
				localRegisterService(registration);
			}
			notifyAddRegistrationResponse(remoteContainerID, requestId, null);
		}
		// notify IRemoteServiceListeners
		if (added)
			fireRemoteServiceListeners(createRegisteredEvent(registration));
		Trace.exiting(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_EXITING, this.getClass(), ADD_REGISTRATION);
	}

	/**
	 * @param requestId
	 * @since 3.2
	 */
	protected void notifyAddRegistrationResponse(ID remoteContainerID, Integer requestId, AccessControlException exception) {
		if (remoteContainerID == null)
			return;
		if (requestId == null)
			return;
		AddRegistrationRequest request = (AddRegistrationRequest) addRegistrationRequests.get(requestId);
		if (request != null)
			request.notifyResponse(exception);
	}

	/**
	 * @since 3.2
	 */
	protected void localRegisterService(RemoteServiceRegistrationImpl registration) {
		final Object localServiceRegistrationValue = registration.getProperty(org.eclipse.ecf.remoteservice.Constants.AUTOREGISTER_REMOTE_PROXY);
		if (localServiceRegistrationValue != null) {
			final BundleContext context = Activator.getDefault().getContext();
			if (context == null)
				return;
			final RemoteServiceImpl remoteServiceImpl = new RemoteServiceImpl(this, registration);
			Object service;
			try {
				service = remoteServiceImpl.getProxy();
			} catch (final ECFException e) {
				e.printStackTrace();
				log("localRegisterService", e); //$NON-NLS-1$
				return;
			}
			final Hashtable properties = new Hashtable();
			final String[] keys = registration.getPropertyKeys();
			for (int i = 0; i < keys.length; i++) {
				final Object value = registration.getProperty(keys[i]);
				if (value != null) {
					properties.put(keys[i], value);
				}
			}
			final ID remoteContainerID = registration.getContainerID();
			properties.put(org.eclipse.ecf.remoteservice.Constants.SERVICE_CONTAINER_ID, remoteContainerID.getName());
			final ServiceRegistration serviceRegistration = context.registerService(registration.getClasses(), service, properties);
			addLocalServiceRegistration(remoteContainerID, serviceRegistration);
		}
	}

	/**
	 * @since 3.2
	 */
	protected void addLocalServiceRegistration(ID remoteContainerID, ServiceRegistration registration) {
		List containerRegistrations = (List) localServiceRegistrations.get(remoteContainerID);
		if (containerRegistrations == null) {
			containerRegistrations = new ArrayList();
			localServiceRegistrations.put(remoteContainerID, containerRegistrations);
		}
		containerRegistrations.add(registration);
	}

	protected Request sendCallRequest(RemoteServiceRegistrationImpl remoteRegistration, final IRemoteCall call) throws IOException {
		Trace.entering(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_ENTERING, this.getClass(), "sendCallRequest", new Object[] {remoteRegistration, call}); //$NON-NLS-1$
		final Request request = createRequest(remoteRegistration, call, null);
		addRequest(request);
		try {
			sendSharedObjectMsgTo(remoteRegistration.getContainerID(), SharedObjectMsg.createMsg(CALL_REQUEST, request));
		} catch (final IOException e) {
			removeRequest(request);
			throw e;
		}
		Trace.exiting(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_EXITING, this.getClass(), "sendCallRequest", request); //$NON-NLS-1$
		return request;
	}

	// system property allowing the executorType to be configured.  Currently types are:  jobs, threads, immediate.
	private static final String DEFAULT_EXECUTOR_TYPE = System.getProperty("org.eclipse.ecf.provider.remoteservice.executorType", "jobs"); //$NON-NLS-1$ //$NON-NLS-2$

	private IExecutor requestExecutor;

	private IExecutor getRequestExecutor(Request request) {
		if (requestExecutor == null) {
			requestExecutor = createRequestExecutor(request);
		}
		return requestExecutor;
	}

	private IExecutor createRequestExecutor(final Request request) {
		IExecutor executor = null;
		if (DEFAULT_EXECUTOR_TYPE.equals("jobs")) { //$NON-NLS-1$
			executor = new JobsExecutor("Remote Request Handler") { //$NON-NLS-1$
				protected String createJobName(String executorName, int jobCounter, IProgressRunnable runnable) {
					return executorName + " - " + request.getCall().getMethod() + ":" + request.getRequestId(); //$NON-NLS-1$ //$NON-NLS-2$
				}
			};
		} else if (DEFAULT_EXECUTOR_TYPE.equals("immediate")) { //$NON-NLS-1$
			executor = new ImmediateExecutor();
		} else if (DEFAULT_EXECUTOR_TYPE.equals("threads")) { //$NON-NLS-1$
			executor = new ThreadsExecutor() {
				protected String createThreadName(IProgressRunnable runnable) {
					return "Remote Request Handler - " + request.getCall().getMethod() + ":" + request.getRequestId(); //$NON-NLS-1$ //$NON-NLS-2$
				}
			};
		}
		return executor;
	}

	private void executeRequest(IExecutor executor, final Request request, final ID responseTarget, final RemoteServiceRegistrationImpl localRegistration, final boolean respond) {
		IProgressRunnable runnable = new IProgressRunnable() {
			public Object run(IProgressMonitor monitor) throws Exception {
				final RemoteCallImpl call = request.getCall();
				Response response = null;
				Object result = null;
				try {
					result = localRegistration.callService(call);
					response = new Response(request.getRequestId(), result);
					// Invocation target exception happens if the local method being invoked throws (cause)
				} catch (InvocationTargetException e) {
					Throwable cause = e.getCause();
					response = new Response(request.getRequestId(), getSerializableException(cause));
					logRemoteCallException("Invocation target exception invoking remote service.  Remote request=" + request, cause); //$NON-NLS-1$
					// This is to catch most other problems
				} catch (Exception e) {
					response = new Response(request.getRequestId(), getSerializableException(e));
					logRemoteCallException("Unexpected exception invoking remote service.  Remote request=" + request, e); //$NON-NLS-1$
				} catch (NoClassDefFoundError e) {
					response = new Response(request.getRequestId(), getSerializableException(e));
					logRemoteCallException("No class def found error invoking remote service.  Remote request=" + request, e); //$NON-NLS-1$
				}
				// Now send response back to responseTarget (original requestor)
				if (respond)
					sendCallResponse(responseTarget, response);
				return null;
			}
		};
		// Now actually execute the runnable asynchronously using the executor
		executor.execute(runnable, new NullProgressMonitor());
	}

	private void sendErrorResponse(ID responseTarget, long requestId, String message, Throwable e) {
		logRemoteCallException(message, e);
		Response response = new Response(requestId, e);
		sendCallResponse(responseTarget, response);
	}

	protected void handleCallRequest(Request request) {
		Trace.entering(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_ENTERING, this.getClass(), "handleCallRequest", request); //$NON-NLS-1$
		// If request is null, it's bogus, give up/do not respond
		if (request == null) {
			log("handleCallRequest", new NullPointerException("Request cannot be null")); //$NON-NLS-1$//$NON-NLS-2$
			return;
		}

		final ID responseTarget = request.getRequestContainerID();
		// If response target is null then the request is bogus and we give up/do not respond
		if (responseTarget == null) {
			log("handleCallRequest", new NullPointerException("Response target cannot be null")); //$NON-NLS-1$ //$NON-NLS-2$
			return;
		}

		final RemoteServiceRegistrationImpl localRegistration = getLocalRegistrationForRequest(request);
		// If localRegistration not found for request, then it's a bogus request and we respond with NPE
		if (localRegistration == null) {
			sendErrorResponse(responseTarget, request.getRequestId(), "handleCallRequest", new NullPointerException("local service registration not found for remote request=" + request)); //$NON-NLS-1$ //$NON-NLS-2$
			return;
		}

		IExecutor executor = getRequestExecutor(request);
		if (executor == null) {
			sendErrorResponse(responseTarget, request.getRequestId(), "handleCallRequest", new NullPointerException("request executor is not available and so no requests can be processed")); //$NON-NLS-1$ //$NON-NLS-2$
			return;
		}

		// Else we've got a local service and we execute it using executor
		executeRequest(executor, request, responseTarget, localRegistration, true);

		Trace.exiting(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_EXITING, this.getClass(), "handleCallRequest"); //$NON-NLS-1$
	}

	private void logRemoteCallException(String message, Throwable e) {
		Activator.getDefault().log(new Status(IStatus.ERROR, Activator.PLUGIN_ID, SERVICE_INVOKE_ERROR_CODE, message, e));
	}

	private Throwable getSerializableException(Throwable e) {
		// Just use the SerializableStatus
		SerializableStatus ss = new SerializableStatus(0, Activator.PLUGIN_ID, null, e);
		return ss.getException();
	}

	protected void sendCallRequestWithListener(RemoteServiceRegistrationImpl remoteRegistration, IRemoteCall call, IRemoteCallListener listener) {
		Trace.entering(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_ENTERING, this.getClass(), "sendCallRequestWithListener", new Object[] {remoteRegistration, call, listener}); //$NON-NLS-1$
		final Request request = createRequest(remoteRegistration, call, listener);
		fireCallStartEvent(listener, request.getRequestId(), remoteRegistration.getReference(), call);
		try {
			addRequest(request);
			sendSharedObjectMsgTo(remoteRegistration.getContainerID(), SharedObjectMsg.createMsg(CALL_REQUEST, request));
		} catch (final IOException e) {
			log(CALL_REQUEST_ERROR_CODE, CALL_REQUEST_ERROR_MESSAGE, e);
			removeRequest(request);
			fireCallCompleteEvent(listener, request.getRequestId(), null, true, e);
		}
		Trace.exiting(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_EXITING, this.getClass(), "sendCallRequestWithListener"); //$NON-NLS-1$
	}

	protected void log(int code, String method, Throwable e) {
		Activator.getDefault().log(new Status(IStatus.ERROR, Activator.PLUGIN_ID, code, method, e));
	}

	protected void sendCallResponse(ID responseTarget, Response response) {
		Trace.entering(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_ENTERING, this.getClass(), "sendCallResponse", new Object[] {responseTarget, response}); //$NON-NLS-1$
		try {
			sendSharedObjectMsgTo(responseTarget, SharedObjectMsg.createMsg(CALL_RESPONSE, response));
		} catch (final IOException e) {
			log(CALL_RESPONSE_ERROR_CODE, CALL_RESPONSE_ERROR_MESSAGE, e);
			// Also print to standard error, just in case
			e.printStackTrace(System.err);
		}
		Trace.exiting(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_EXITING, this.getClass(), "sendCallResponse"); //$NON-NLS-1$
	}

	protected void handleCallResponse(Response response) {
		Trace.entering(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_ENTERING, this.getClass(), CALL_RESPONSE, new Object[] {response});
		final Request request = getRequest(response.getRequestId());
		if (request == null) {
			log(REQUEST_NOT_FOUND_ERROR_CODE, REQUEST_NOT_FOUND_ERROR_MESSAGE, new NullPointerException());
			return;
		}
		removeRequest(request);
		final IRemoteCallListener listener = request.getListener();
		if (listener != null) {
			fireCallCompleteEvent(listener, request.getRequestId(), response.getResponse(), response.hadException(), response.getException());
			return;
		}
		synchronized (request) {
			request.setResponse(response);
			request.setDone(true);
			request.notify();
		}
		Trace.exiting(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_EXITING, this.getClass(), CALL_RESPONSE);
	}

	protected Request sendFireRequest(RemoteServiceRegistrationImpl remoteRegistration, IRemoteCall call) throws ECFException {
		Trace.entering(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_ENTERING, this.getClass(), "sendFireRequest", new Object[] {remoteRegistration, call}); //$NON-NLS-1$
		final Request request = createRequest(remoteRegistration, call, null);
		try {
			sendSharedObjectMsgTo(remoteRegistration.getContainerID(), SharedObjectMsg.createMsg(FIRE_REQUEST, request));
		} catch (final IOException e) {
			log(FIRE_REQUEST_ERROR_CODE, FIRE_REQUEST_ERROR_MESSAGE, e);
			throw new ECFException("IOException sending fire request", e); //$NON-NLS-1$
		}
		Trace.exiting(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_EXITING, this.getClass(), "sendFireRequest", request); //$NON-NLS-1$
		return request;
	}

	protected void handleFireRequest(Request request) {
		Trace.entering(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_ENTERING, this.getClass(), FIRE_REQUEST, new Object[] {request});

		// If request is null, it's bogus, give up/do not respond
		if (request == null) {
			log("handleFireRequest", new NullPointerException("Request cannot be null")); //$NON-NLS-1$//$NON-NLS-2$
			return;
		}

		final ID responseTarget = request.getRequestContainerID();
		// If response target is null then the request is bogus and we give up/do not respond
		if (responseTarget == null) {
			log("handleFireRequest", new NullPointerException("Response target cannot be null")); //$NON-NLS-1$ //$NON-NLS-2$
			return;
		}

		final RemoteServiceRegistrationImpl localRegistration = getLocalRegistrationForRequest(request);
		// If localRegistration not found for request, then it's a bogus request and we respond with NPE
		if (localRegistration == null) {
			sendErrorResponse(responseTarget, request.getRequestId(), "handleFireRequest", new NullPointerException("local service registration not found for remote request=" + request)); //$NON-NLS-1$ //$NON-NLS-2$
			return;
		}

		IExecutor executor = getRequestExecutor(request);
		if (executor == null) {
			sendErrorResponse(responseTarget, request.getRequestId(), "handleFireRequest", new NullPointerException("request executor is not available and so no requests can be processed")); //$NON-NLS-1$ //$NON-NLS-2$
			return;
		}

		// Else we've got a local service and we execute it using executor
		executeRequest(executor, request, responseTarget, localRegistration, false);

		Trace.exiting(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_EXITING, this.getClass(), FIRE_REQUEST);
	}

	protected void sendUnregister(RemoteServiceRegistrationImpl serviceRegistration) {
		Trace.entering(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_ENTERING, this.getClass(), "sendUnregister", new Object[] {serviceRegistration}); //$NON-NLS-1$
		synchronized (localRegistry) {
			localRegistry.unpublishService(serviceRegistration);
			final ID containerID = serviceRegistration.getContainerID();
			final Long serviceId = new Long(serviceRegistration.getServiceId());
			// Get targetIds from serviceRegistration properties
			ID[] targetIds = getTargetsFromProperties(serviceRegistration.properties);
			// If none/null, then send unregister message to all group members
			if (targetIds == null) {
				try {
					this.sendSharedObjectMsgTo(null, SharedObjectMsg.createMsg(UNREGISTER, new Object[] {containerID, serviceId}));
				} catch (final IOException e) {
					log(UNREGISTER_ERROR_CODE, UNREGISTER_ERROR_MESSAGE, e);
				}
			} else
				// Send an unregister message to all targetIds
				for (int i = 0; i < targetIds.length; i++) {
					try {
						this.sendSharedObjectMsgTo(targetIds[i], SharedObjectMsg.createMsg(UNREGISTER, new Object[] {containerID, serviceId}));
					} catch (final IOException e) {
						log(UNREGISTER_ERROR_CODE, UNREGISTER_ERROR_MESSAGE, e);
					}
				}
		}
		fireRemoteServiceListeners(createUnregisteredEvent(serviceRegistration));
		Trace.exiting(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_EXITING, this.getClass(), "sendUnregister"); //$NON-NLS-1$
	}

	/**
	 * @since 3.2
	 */
	protected void unregisterServiceRegistrationsForContainer(ID containerID) {
		if (containerID == null)
			return;
		final List containerRegistrations = (List) localServiceRegistrations.remove(containerID);
		if (containerRegistrations != null) {
			for (final Iterator i = containerRegistrations.iterator(); i.hasNext();) {
				final ServiceRegistration serviceRegistration = (ServiceRegistration) i.next();
				try {
					serviceRegistration.unregister();
				} catch (Exception e) {
					// Simply log
					log("unregister", e); //$NON-NLS-1$
				}
			}
		}
	}

	/**
	 * @since 3.2
	 */
	protected void unregisterAllServiceRegistrations() {
		synchronized (remoteRegistrys) {
			for (final Iterator i = localServiceRegistrations.keySet().iterator(); i.hasNext();) {
				unregisterServiceRegistrationsForContainer((ID) i.next());
			}
		}
	}

	protected void handleUnregister(ID containerID, Long serviceId) {
		Trace.entering(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_ENTERING, this.getClass(), "handleUnregister", new Object[] {containerID, serviceId}); //$NON-NLS-1$
		RemoteServiceRegistrationImpl registration = null;
		synchronized (remoteRegistrys) {
			// get registry for given containerID
			final RemoteServiceRegistryImpl serviceRegistry = (RemoteServiceRegistryImpl) remoteRegistrys.get(containerID);
			if (serviceRegistry != null) {
				registration = serviceRegistry.findRegistrationForServiceId(serviceId.longValue());
				if (registration != null) {
					serviceRegistry.unpublishService(registration);
					unregisterServiceRegistrationsForContainer(registration.getContainerID());
				}
			}
		}
		if (registration != null)
			fireRemoteServiceListeners(createUnregisteredEvent(registration));
		Trace.exiting(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_EXITING, this.getClass(), "handleUnregister"); //$NON-NLS-1$
	}

	protected IRemoteServiceUnregisteredEvent createUnregisteredEvent(final RemoteServiceRegistrationImpl registration) {
		return new IRemoteServiceUnregisteredEvent() {

			public String[] getClazzes() {
				return registration.getClasses();
			}

			public ID getLocalContainerID() {
				return RegistrySharedObject.this.getLocalContainerID();
			}

			public ID getContainerID() {
				return registration.getContainerID();
			}

			public IRemoteServiceReference getReference() {
				return registration.getReference();
			}

			public String toString() {
				final StringBuffer buf = new StringBuffer("RemoteServiceUnregisteredEvent["); //$NON-NLS-1$
				buf.append("localContainerID=").append(getLocalContainerID()); //$NON-NLS-1$
				buf.append(";containerID=").append(registration.getContainerID()); //$NON-NLS-1$
				buf.append(";clazzes=").append(Arrays.asList(registration.getClasses())); //$NON-NLS-1$
				buf.append(";reference=").append(registration.getReference()).append("]"); //$NON-NLS-1$ //$NON-NLS-2$
				return buf.toString();
			}
		};
	}

	protected IRemoteServiceRegisteredEvent createRegisteredEvent(final RemoteServiceRegistrationImpl registration) {
		return new IRemoteServiceRegisteredEvent() {

			public ID getLocalContainerID() {
				return RegistrySharedObject.this.getLocalContainerID();
			}

			public String[] getClazzes() {
				return registration.getClasses();
			}

			public ID getContainerID() {
				return registration.getContainerID();
			}

			public IRemoteServiceReference getReference() {
				return registration.getReference();
			}

			public String toString() {
				final StringBuffer buf = new StringBuffer("RemoteServiceRegisteredEvent["); //$NON-NLS-1$
				buf.append("localContainerID=").append(getLocalContainerID()); //$NON-NLS-1$
				buf.append(";containerID=").append(registration.getContainerID()); //$NON-NLS-1$
				buf.append(";clazzes=").append(Arrays.asList(registration.getClasses())); //$NON-NLS-1$
				buf.append(";reference=").append(registration.getReference()).append("]"); //$NON-NLS-1$ //$NON-NLS-2$
				return buf.toString();
			}
		};
	}

	/**
	 * End message send/handlers
	 */

	protected RemoteServiceRegistryImpl addRemoteRegistry(RemoteServiceRegistryImpl registry) {
		return (RemoteServiceRegistryImpl) remoteRegistrys.put(registry.getContainerID(), registry);
	}

	protected RemoteServiceRegistryImpl getRemoteRegistry(ID containerID) {
		return (RemoteServiceRegistryImpl) remoteRegistrys.get(containerID);
	}

	protected RemoteServiceRegistryImpl removeRemoteRegistry(ID containerID) {
		return (RemoteServiceRegistryImpl) remoteRegistrys.remove(containerID);
	}

	/**
	 *
	 * @since 3.2
	 */
	protected RemoteServiceRegistrationImpl getLocalRegistrationForRequest(Request request) {
		synchronized (localRegistry) {
			return localRegistry.findRegistrationForServiceId(request.getServiceId());
		}
	}

	/**
	 * @since 3.2
	 */
	protected boolean addRequest(Request request) {
		return requests.add(request);
	}

	/**
	 * @since 3.2
	 */
	protected Request getRequest(long requestId) {
		synchronized (requests) {
			for (final Iterator i = requests.iterator(); i.hasNext();) {
				final Request req = (Request) i.next();
				final long reqId = req.getRequestId();
				if (reqId == requestId) {
					return req;
				}
			}
		}
		return null;
	}

	/**
	 * @since 3.2
	 */
	protected boolean removeRequest(Request request) {
		return requests.remove(request);
	}

	protected void logException(int code, String message, Throwable e) {
		Activator.getDefault().log(new Status(IStatus.ERROR, Activator.PLUGIN_ID, code, message, e));
	}

	protected boolean handleSharedObjectMsg(SharedObjectMsg msg) {
		try {
			msg.invoke(this);
			return true;
		} catch (final Exception e) {
			logException(MSG_INVOKE_ERROR_CODE, "Exception invoking shared object message=" + msg, e); //$NON-NLS-1$
		}
		return false;
	}

	IProgressMonitor progressMonitor = Job.getJobManager().createProgressGroup();

	/**
	 * @since 3.0
	 */
	public IFuture asyncGetRemoteServiceReferences(final ID[] idFilter, final String clazz, final String filter) {
		IExecutor executor = new JobsExecutor("asyncGetRemoteServiceReferences"); //$NON-NLS-1$
		return executor.execute(new IProgressRunnable() {
			public Object run(IProgressMonitor monitor) throws Exception {
				return getRemoteServiceReferences(idFilter, clazz, filter);
			}
		}, null);
	}

	/**
	 * @since 3.0
	 */
	public IFuture asyncGetRemoteServiceReferences(final ID target, final String clazz, final String filter) {
		IExecutor executor = new JobsExecutor("asyncGetRemoteServiceReferences"); //$NON-NLS-1$
		return executor.execute(new IProgressRunnable() {
			public Object run(IProgressMonitor monitor) throws Exception {
				return getRemoteServiceReferences(target, clazz, filter);
			}
		}, null);
	}

	/**
	 * @since 3.0
	 */
	public Namespace getRemoteServiceNamespace() {
		return IDFactory.getDefault().getNamespaceByName(RemoteServiceNamespace.NAME);
	}

	/**
	 * @since 3.0
	 */
	public IRemoteFilter createRemoteFilter(String filter) throws InvalidSyntaxException {
		return new RemoteFilterImpl(filter);
	}

	/**
	 * @since 3.0
	 */
	public IRemoteServiceReference getRemoteServiceReference(IRemoteServiceID serviceId) {
		ID containerID = serviceId.getContainerID();
		RemoteServiceRegistrationImpl registration = null;
		waitForPendingUpdates(new ID[] {serviceId.getContainerID()}, getAddRegistrationRequestTimeout());
		if (this.localRegistry.containerID.equals(containerID)) {
			synchronized (localRegistry) {
				registration = localRegistry.findRegistrationForServiceId(serviceId.getContainerRelativeID());
				if (registration != null)
					return registration.getReference();
			}
		} else {
			synchronized (remoteRegistrys) {
				final ArrayList registrys = new ArrayList(remoteRegistrys.values());
				for (final Iterator i = registrys.iterator(); i.hasNext();) {
					final RemoteServiceRegistryImpl registry = (RemoteServiceRegistryImpl) i.next();
					registration = registry.findRegistrationForServiceId(serviceId.getContainerRelativeID());
				}
			}
		}
		return (registration == null) ? null : registration.getReference();
	}

	/**
	 * @since 3.0
	 */
	public IRemoteServiceID getRemoteServiceID(ID containerId, long containerRelativeId) {
		if (containerId == null)
			return null;
		synchronized (localRegistry) {
			if (localRegistry.containerID.equals(containerId)) {
				RemoteServiceRegistrationImpl reg = localRegistry.findRegistrationForServiceId(containerRelativeId);
				if (reg != null)
					return reg.getID();
			}
		}
		synchronized (remoteRegistrys) {
			final ArrayList registrys = new ArrayList(remoteRegistrys.values());
			for (final Iterator i = registrys.iterator(); i.hasNext();) {
				final RemoteServiceRegistryImpl registry = (RemoteServiceRegistryImpl) i.next();
				RemoteServiceRegistrationImpl reg = registry.findRegistrationForServiceId(containerRelativeId);
				if (reg != null)
					return reg.getID();
			}
		}
		return null;
	}

	/**
	 * @since 3.0
	 */
	public void setConnectContextForAuthentication(IConnectContext connectContext) {
		this.connectContext = connectContext;
	}

}