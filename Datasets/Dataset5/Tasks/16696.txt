Integer serviceRanking = (Integer) props.get(org.eclipse.ecf.remoteservice.Constants.SERVICE_RANKING);

/*******************************************************************************
 * Copyright (c) 2008 Jan S. Rellermeyer, and others
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     Jan S. Rellermeyer - initial API and implementation
 ******************************************************************************/

package org.eclipse.ecf.internal.provider.r_osgi;

import ch.ethz.iks.r_osgi.*;
import java.io.IOException;
import java.util.*;
import org.eclipse.core.runtime.Assert;
import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.ecf.core.*;
import org.eclipse.ecf.core.events.*;
import org.eclipse.ecf.core.identity.*;
import org.eclipse.ecf.core.security.IConnectContext;
import org.eclipse.ecf.provider.r_osgi.identity.*;
import org.eclipse.ecf.remoteservice.*;
import org.eclipse.ecf.remoteservice.events.IRemoteServiceRegisteredEvent;
import org.eclipse.ecf.remoteservice.events.IRemoteServiceUnregisteredEvent;
import org.eclipse.equinox.concurrent.future.*;
import org.osgi.framework.*;
import org.osgi.framework.Constants;
import org.osgi.util.tracker.ServiceTracker;
import org.osgi.util.tracker.ServiceTrackerCustomizer;

/**
 * The R-OSGi remote service container adapter. Implements the adapter and the
 * container interface.
 * 
 * @author Jan S. Rellermeyer, ETH Zurich
 */
final class R_OSGiRemoteServiceContainer implements IRemoteServiceContainerAdapter, IContainer, RemoteServiceListener {

	// the bundle context.
	private BundleContext context;

	// the R-OSGi remote service instance.
	private RemoteOSGiService remoteService;

	// the list of subscribed container listeners.
	private final List containerListeners = new ArrayList(0);

	// the ID of this container.
	R_OSGiID containerID;

	// the ID of the remote peer to which the container is connected to, or
	// null, if not yet connected.
	private R_OSGiID connectedID;

	// tracks the lifecycle of remote services.
	private ServiceTracker remoteServicesTracker;

	// service reference -> service registration
	private Map remoteServicesRegs = new HashMap(0);

	// the map of remote service listeners. Maps the listener to the service
	// registration of the internal R-OSGi remote service listener service.
	private Map remoteServiceListeners = new HashMap(0);

	// Connect context to use for connect calls
	private IConnectContext connectContext;

	public R_OSGiRemoteServiceContainer(RemoteOSGiService service, final ID containerID) throws IDCreateException {
		Assert.isNotNull(service);
		Assert.isNotNull(containerID);
		context = Activator.getDefault().getContext();
		remoteService = service;
		if (containerID instanceof StringID) {
			this.containerID = new R_OSGiID(((StringID) containerID).getName());
		} else if (containerID instanceof R_OSGiID) {
			this.containerID = (R_OSGiID) containerID;
		} else {
			throw new IDCreateException("Incompatible ID " + containerID); //$NON-NLS-1$
		}
		startRegTracker();
	}

	private void startRegTracker() {
		try {
			final String filter = "(" + org.eclipse.ecf.remoteservice.Constants.SERVICE_CONTAINER_ID + "=" + containerID + ")"; //$NON-NLS-1$ //$NON-NLS-2$ //$NON-NLS-3$
			remoteServicesTracker = new ServiceTracker(context, context.createFilter(filter), new ServiceTrackerCustomizer() {

				public Object addingService(ServiceReference reference) {
					return reference;
				}

				public void modifiedService(ServiceReference reference, Object service) {
					// service got modified
					return;
				}

				public void removedService(ServiceReference reference, Object service) {
					// service got removed
				}
			});
			remoteServicesTracker.open();
		} catch (InvalidSyntaxException e) {
			e.printStackTrace();
		}
	}

	/**
	 * add a remote service listener. This method accepts an ECF remote service
	 * listener and registers a R-OSGi listener service as an adapter.
	 * 
	 * @param listener
	 *            the ECF remote service listener.
	 * 
	 * @see org.eclipse.ecf.remoteservice.IRemoteServiceContainerAdapter#addRemoteServiceListener(org.eclipse.ecf.remoteservice.IRemoteServiceListener)
	 */
	public void addRemoteServiceListener(final IRemoteServiceListener listener) {
		Assert.isNotNull(listener);

		final RemoteServiceListener l = new RemoteServiceListener() {
			public void remoteServiceEvent(final RemoteServiceEvent event) {
				switch (event.getType()) {
					case RemoteServiceEvent.REGISTERED :
						listener.handleServiceEvent(new IRemoteServiceRegisteredEvent() {

							IRemoteServiceReference reference = new RemoteServiceReferenceImpl(createRemoteServiceID(event.getRemoteReference()), event.getRemoteReference());

							public String[] getClazzes() {
								return event.getRemoteReference().getServiceInterfaces();
							}

							public ID getContainerID() {
								return getReference().getContainerID();
							}

							public IRemoteServiceReference getReference() {
								return reference;
							}

							public String toString() {
								return "RemoteServiceRegisteredEvent(" + containerID + "," + getReference(); //$NON-NLS-1$ //$NON-NLS-2$
							}

							public ID getLocalContainerID() {
								return getID();
							}
						});
						return;
					case RemoteServiceEvent.UNREGISTERING :
						listener.handleServiceEvent(new IRemoteServiceUnregisteredEvent() {
							IRemoteServiceReference reference = new RemoteServiceReferenceImpl(createRemoteServiceID(event.getRemoteReference()), event.getRemoteReference());

							public String[] getClazzes() {
								return event.getRemoteReference().getServiceInterfaces();
							}

							public ID getContainerID() {
								return containerID;
							}

							public IRemoteServiceReference getReference() {
								return reference;
							}

							public String toString() {
								return "RemoteServiceUnregisteredEvent(" + containerID + "," + getReference(); //$NON-NLS-1$ //$NON-NLS-2$
							}

							public ID getLocalContainerID() {
								return getID();
							}
						});
						return;
				}
			}
		};
		// register the listener as a service (whiteboard pattern)
		final ServiceRegistration reg = context.registerService(RemoteServiceListener.class.getName(), l, null);
		// keep track of the listener so that it can be removed when requested.
		remoteServiceListeners.put(listener, reg);
	}

	/**
	 * get a remote service by its remote service reference.
	 * 
	 * @param reference
	 *            the remote service reference.
	 * @return the IRemoteService object, encapsulating the service proxy and
	 *         additional methods for asynchronous and other access methods.
	 * @see org.eclipse.ecf.remoteservice.IRemoteServiceContainerAdapter#getRemoteService(org.eclipse.ecf.remoteservice.IRemoteServiceReference)
	 */
	public IRemoteService getRemoteService(final IRemoteServiceReference reference) {
		Assert.isNotNull(reference);
		if (!(reference instanceof RemoteServiceReferenceImpl))
			return null;
		final RemoteServiceReferenceImpl impl = (RemoteServiceReferenceImpl) reference;
		return new RemoteServiceImpl(impl, remoteService.getRemoteService(impl.getR_OSGiServiceReference()));
	}

	/**
	 * get remote service references.
	 * 
	 * @param idFilter
	 *            a filter that limits the results to services registered by one
	 *            of the IDs.
	 * @param clazz
	 *            the interface name of the remote service.
	 * @param filter
	 *            LDAP filter string that is matched against the service
	 *            properties.
	 * @return the matching remote service references.
	 * @throws InvalidSyntaxException
	 * @see org.eclipse.ecf.remoteservice.IRemoteServiceContainerAdapter#getRemoteServiceReferences(org.eclipse.ecf.core.identity.ID[],
	 *      java.lang.String, java.lang.String)
	 */
	public IRemoteServiceReference[] getRemoteServiceReferences(final ID[] idFilter, final String clazz, final String filter) throws InvalidSyntaxException {
		if (clazz == null)
			return null;
		IRemoteFilter remoteFilter = (filter == null) ? null : createRemoteFilter(filter);
		if (idFilter == null)
			return (IRemoteServiceReference[]) getRemoteServiceReferencesConnected(clazz, remoteFilter).toArray(new IRemoteServiceReference[] {});
		synchronized (this) {
			List results = new ArrayList();
			for (int i = 0; i < idFilter.length; i++) {
				results.addAll(connectAndGetRemoteServiceReferencesForTarget(getConnectedID(), idFilter[i], clazz, remoteFilter));
			}
			return (IRemoteServiceReference[]) results.toArray(new IRemoteServiceReference[] {});
		}
	}

	public IRemoteServiceReference[] getRemoteServiceReferences(ID targetID, String clazz, String filter) throws InvalidSyntaxException, ContainerConnectException {
		if (clazz == null)
			return null;
		IRemoteFilter remoteFilter = (filter == null) ? null : createRemoteFilter(filter);
		synchronized (this) {
			List results = new ArrayList();
			connect(targetID, connectContext);
			results = getRemoteServiceReferencesConnected(clazz, remoteFilter);
			return (IRemoteServiceReference[]) results.toArray(new IRemoteServiceReference[] {});
		}
	}

	public IRemoteServiceReference[] getAllRemoteServiceReferences(String clazz, String filter) throws InvalidSyntaxException {
		List results = new ArrayList();
		// Get remote service references from locally registered services first
		synchronized (remoteServicesRegs) {
			for (Iterator i1 = remoteServicesRegs.keySet().iterator(); i1.hasNext();) {
				ServiceReference ref = (ServiceReference) i1.next();
				Dictionary refProperties = prepareProperties(ref);
				if (clazz == null) {
					results.add(createLocalRemoteServiceReference(ref));
				} else {
					IRemoteFilter rf = createRemoteFilter(filter != null ? "(&" + filter + "(" //$NON-NLS-1$ //$NON-NLS-2$
							+ Constants.OBJECTCLASS + "=" + clazz + "))" : "(" //$NON-NLS-1$ //$NON-NLS-2$ //$NON-NLS-3$
							+ Constants.OBJECTCLASS + "=" + clazz + ")"); //$NON-NLS-1$//$NON-NLS-2$
					if (rf.match(refProperties)) {
						results.add(createLocalRemoteServiceReference(ref));
					}
				}

			}
		}
		IRemoteFilter remoteFilter = (filter == null) ? null : createRemoteFilter(filter);
		if (getConnectedID() != null) {
			final RemoteServiceReference[] refs = remoteService.getRemoteServiceReferences(connectedID.getURI(), clazz, remoteFilter);
			if (refs != null)
				for (int i = 0; i < refs.length; i++)
					results.add(new RemoteServiceReferenceImpl(createRemoteServiceID(refs[i]), refs[i]));
		}
		return (IRemoteServiceReference[]) results.toArray(new IRemoteServiceReference[] {});
	}

	private IRemoteServiceReference createLocalRemoteServiceReference(ServiceReference ref) {
		return new LocalRemoteServiceReferenceImpl(createRemoteServiceID(containerID, (Long) ref.getProperty(Constants.SERVICE_ID)), ref);
	}

	private List /*IRemoteServiceReference*/connectAndGetRemoteServiceReferencesForTarget(ID currentlyConnectedID, ID targetID, String clazz, IRemoteFilter remoteFilter) {
		List results = new ArrayList();
		if (currentlyConnectedID != null) {
			if (targetID.equals(currentlyConnectedID))
				results.addAll(getRemoteServiceReferencesConnected(clazz, remoteFilter));
			else {
				disconnect();
				results.addAll(connectAndGetRemoteServiceReferencesForTarget(targetID, clazz, remoteFilter, true));
				// try to reconnect to original
				try {
					connect(currentlyConnectedID, connectContext);
				} catch (ContainerConnectException e) {
					logException("connectAndGetRemoteServiceReferencesForTarget.  Could not reconnect to " + currentlyConnectedID, e); //$NON-NLS-1$
				}
			}
		} else {
			results.addAll(connectAndGetRemoteServiceReferencesForTarget(targetID, clazz, remoteFilter, false));
		}
		return results;
	}

	private List /*IRemoteServiceReference[]*/connectAndGetRemoteServiceReferencesForTarget(ID targetID, String clazz, IRemoteFilter remoteFilter, boolean doDisconnect) {
		List results = new ArrayList();
		try {
			// we first connect
			connect(targetID, connectContext);
			// get remote services references...assuming we're connected
			results.addAll(getRemoteServiceReferencesConnected(clazz, remoteFilter));
			// then disconnect
			if (doDisconnect)
				disconnect();
		} catch (ContainerConnectException e) {
			logException("connectAndGetRemoteServiceReferencesForTarget=" + targetID + ",class=" + clazz + ",remoteFilter=" + remoteFilter, e); //$NON-NLS-1$ //$NON-NLS-2$ //$NON-NLS-3$
		}
		return results;
	}

	private void logException(String message, Throwable e) {
		System.err.println(message);
		if (e != null)
			e.printStackTrace(System.err);
	}

	private synchronized List getRemoteServiceReferencesConnected(final String clazz, IRemoteFilter filter) {
		List results = new ArrayList();
		final RemoteServiceReference[] refs = remoteService.getRemoteServiceReferences(connectedID.getURI(), clazz, filter);
		if (refs == null)
			return results;
		for (int i = 0; i < refs.length; i++)
			results.add(new RemoteServiceReferenceImpl(createRemoteServiceID(refs[i]), refs[i]));
		return results;
	}

	IRemoteServiceID createRemoteServiceID(R_OSGiID cID, Long l) {
		return (IRemoteServiceID) IDFactory.getDefault().createID(getRemoteServiceNamespace(), new Object[] {cID, l});
	}

	IRemoteServiceID createRemoteServiceID(RemoteServiceReference rref) {
		return createRemoteServiceID(new R_OSGiID(rref.getURI().toString()), (Long) rref.getProperty(Constants.SERVICE_ID));
	}

	/**
	 * register a service object as a remote service.
	 * 
	 * @param clazzes
	 *            the names of the service interfaces under which the service
	 *            will be registered.
	 * @param service
	 *            the service object.
	 * @param properties
	 *            the service properties.
	 * @see org.eclipse.ecf.remoteservice.IRemoteServiceContainerAdapter#registerRemoteService(java.lang.String[],
	 *      java.lang.Object, java.util.Dictionary)
	 */
	public IRemoteServiceRegistration registerRemoteService(final String[] clazzes, final Object service, final Dictionary properties) {
		if (containerID == null) {
			throw new IllegalStateException("Container is not connected"); //$NON-NLS-1$
		}

		final Dictionary props = properties == null ? new Hashtable() : clone(properties);

		// add the hint property for R-OSGi that this service is intended to be
		// accessed remotely.
		props.put(RemoteOSGiService.R_OSGi_REGISTRATION, Boolean.TRUE);
		// remove the RFC 119 hint, if present, to avoid loops
		props.remove("osgi.remote.interfaces"); //$NON-NLS-1$
		// ECF remote service properties
		// container ID (ID)
		props.put(org.eclipse.ecf.remoteservice.Constants.SERVICE_CONTAINER_ID, containerID);
		// Object classes (String [])
		props.put(org.eclipse.ecf.remoteservice.Constants.OBJECTCLASS, clazzes);
		// service ranking (Integer).  Allow this to be set by user
		Integer serviceRanking = (Integer) properties.get(org.eclipse.ecf.remoteservice.Constants.SERVICE_RANKING);
		serviceRanking = (serviceRanking == null) ? new Integer(0) : serviceRanking;
		props.put(org.eclipse.ecf.remoteservice.Constants.SERVICE_RANKING, serviceRanking);

		// register the service with the local framework
		final ServiceRegistration reg = context.registerService(clazzes, service, props);
		// Set ECF remote service id property based upon local service property
		reg.setProperties(prepareProperties(reg.getReference()));

		synchronized (remoteServicesRegs) {
			remoteServicesRegs.put(reg.getReference(), reg);
		}
		// Construct a IRemoteServiceID, and provide to new registration impl instance
		return new RemoteServiceRegistrationImpl(createRemoteServiceID(containerID, (Long) reg.getReference().getProperty(Constants.SERVICE_ID)), reg);
	}

	Dictionary prepareProperties(ServiceReference reference) {
		String[] propKeys = reference.getPropertyKeys();
		Dictionary newDictionary = new Properties();
		for (int i = 0; i < propKeys.length; i++) {
			Object v = reference.getProperty(propKeys[i]);
			newDictionary.put(propKeys[i], v);
			// Make the remote service SERVICE_ID have the same value as OSGi SERVICE_ID
			if (Constants.SERVICE_ID.equals(propKeys[i])) {
				newDictionary.put(org.eclipse.ecf.remoteservice.Constants.SERVICE_ID, v);
			}
		}
		return newDictionary;
	}

	/**
	 * remove a registered remote service listener.
	 * 
	 * @param listener
	 *            the remote service listener.
	 * @see org.eclipse.ecf.remoteservice.IRemoteServiceContainerAdapter#removeRemoteServiceListener(org.eclipse.ecf.remoteservice.IRemoteServiceListener)
	 */
	public void removeRemoteServiceListener(final IRemoteServiceListener listener) {
		remoteServiceListeners.remove(listener);
	}

	/**
	 * 
	 * @see org.eclipse.ecf.remoteservice.IRemoteServiceContainerAdapter#ungetRemoteService(org.eclipse.ecf.remoteservice.IRemoteServiceReference)
	 */
	public boolean ungetRemoteService(IRemoteServiceReference reference) {
		if (!(reference instanceof RemoteServiceReferenceImpl))
			return false;
		RemoteServiceReferenceImpl impl = (RemoteServiceReferenceImpl) reference;
		RemoteServiceReference rsr = impl.getR_OSGiServiceReference();
		if (!rsr.isActive())
			return false;
		remoteService.ungetRemoteService(rsr);
		return true;
	}

	/**
	 * returns an adapter for a given class. In this particular case, only the
	 * IRemoteServiceContainerAdapter interface and the IContainer interface are
	 * supported.
	 * 
	 * @param adapter
	 *            the class to adapt to.
	 * @return the adapter or null if the adaptation is not supported.
	 * @see org.eclipse.core.runtime.IAdaptable#getAdapter(java.lang.Class)
	 */
	public Object getAdapter(final Class adapter) {
		if (adapter.equals(IRemoteServiceContainerAdapter.class)) {
			return this;
		} else if (adapter.equals(IContainer.class)) {
			return this;
		}
		return null;
	}

	// container part

	/**
	 * add a container listener.
	 * 
	 * @param listener
	 *            the container listener.
	 * 
	 * @see org.eclipse.ecf.core.IContainer#addListener(org.eclipse.ecf.core.IContainerListener)
	 */
	public void addListener(final IContainerListener listener) {
		containerListeners.add(listener);
	}

	/**
	 * connect the container to a remote container instance.
	 * 
	 * @param targetID
	 *            the target ID to connect to.
	 * @param connectContext
	 *            the connection context.
	 * @throws ContainerConnectException
	 *             if the connecting fails.
	 * @see org.eclipse.ecf.core.IContainer#connect(org.eclipse.ecf.core.identity.ID,
	 *      org.eclipse.ecf.core.security.IConnectContext)
	 */
	public synchronized void connect(final ID targetID, final IConnectContext cc) throws ContainerConnectException {
		if (targetID == null)
			throw new ContainerConnectException("targetID may not be null"); //$NON-NLS-1$

		if (!((targetID instanceof R_OSGiID) || targetID instanceof StringID)) {
			throw new ContainerConnectException("targetID is of incorrect type for this container: " + targetID.toString()); //$NON-NLS-1$
		}
		if (connectedID != null) {
			throw new ContainerConnectException("Container is already connected to " + connectedID); //$NON-NLS-1$
		}

		this.connectContext = cc;

		final R_OSGiID target;
		try {
			if (targetID instanceof StringID) {
				target = new R_OSGiID(((StringID) targetID).getName());
			} else if (targetID instanceof R_OSGiID) {
				target = (R_OSGiID) targetID;
			} else {
				throw new ContainerConnectException("Incompatible target id " + targetID); //$NON-NLS-1$
			}

			fireListeners(new ContainerConnectingEvent(containerID, connectedID));

			final RemoteServiceReference[] refs = doConnect(target);
			if (refs != null) {
				for (int i = 0; i < refs.length; i++) {
					checkImport(refs[i]);
				}
			}
			connectedID = target;

			startRegTracker();

		} catch (IOException ioe) {
			throw new ContainerConnectException(ioe);
		} catch (IDCreateException e) {
			throw new ContainerConnectException(e);
		}
		fireListeners(new ContainerConnectedEvent(containerID, connectedID));
	}

	private RemoteServiceReference[] doConnect(R_OSGiID targetID) throws IOException {
		return remoteService.connect(targetID.getURI());
	}

	private void doDisconnect(R_OSGiID targetID) {
		remoteService.disconnect(targetID.getURI());
	}

	/**
	 * disconnect from the remote container.
	 * 
	 * @see org.eclipse.ecf.core.IContainer#disconnect()
	 */
	public synchronized void disconnect() {
		if (connectedID != null) {
			fireListeners(new ContainerDisconnectingEvent(containerID, connectedID));
			doDisconnect(connectedID);
			connectedID = null;
			remoteService = null;
			fireListeners(new ContainerDisconnectedEvent(containerID, connectedID));
		}

	}

	/**
	 * dispose the container.
	 * 
	 * @see org.eclipse.ecf.core.IContainer#dispose()
	 */
	public void dispose() {
		// unregister remote services
		if (remoteServicesTracker != null) {
			final ServiceReference[] refs = remoteServicesTracker.getServiceReferences();
			if (refs != null) {
				for (int i = 0; i < refs.length; i++) {
					final ServiceRegistration reg = (ServiceRegistration) remoteServicesRegs.get(refs[i]);
					if (reg != null) {
						reg.unregister();
					}
				}
			}
			remoteServicesTracker.close();
			remoteServicesTracker = null;
		}

		// unregister remote listeners
		final ServiceRegistration[] lstn = (ServiceRegistration[]) remoteServiceListeners.values().toArray(new ServiceRegistration[remoteServiceListeners.size()]);
		for (int i = 0; i < lstn.length; i++) {
			try {
				lstn[i].unregister();
			} catch (Throwable t) {
				// ignore and continue
			}
		}

		if (connectedID != null) {
			disconnect();
		}

		fireListeners(new ContainerDisposeEvent(containerID));
		containerListeners.clear();
	}

	/**
	 * get the connect namespace.
	 * 
	 * @return the connect namespace.
	 * @see org.eclipse.ecf.core.IContainer#getConnectNamespace()
	 */
	public Namespace getConnectNamespace() {
		return R_OSGiNamespace.getDefault();
	}

	/**
	 * get the ID to which the container is connected to. Can be
	 * <code>null</code> if the container is not yet connected.
	 * 
	 * @return the ID or null.
	 * @see org.eclipse.ecf.core.IContainer#getConnectedID()
	 */
	public synchronized ID getConnectedID() {
		return connectedID;
	}

	/**
	 * remove a registered container listener.
	 * 
	 * @param listener
	 *            the container listener.
	 * @see org.eclipse.ecf.core.IContainer#removeListener(org.eclipse.ecf.core.IContainerListener)
	 */
	public void removeListener(final IContainerListener listener) {
		containerListeners.remove(listener);
	}

	/**
	 * get the ID of this container instance.
	 * 
	 * @return the ID of this container.
	 * @see org.eclipse.ecf.core.identity.IIdentifiable#getID()
	 */
	public ID getID() {
		return containerID;
	}

	/**
	 * fire the listeners.
	 * 
	 * @param event
	 *            the event.
	 */
	private void fireListeners(final IContainerEvent event) {
		final IContainerListener[] listeners = (IContainerListener[]) containerListeners.toArray(new IContainerListener[containerListeners.size()]);
		new Thread() {
			public void run() {
				for (int i = 0; i < listeners.length; i++) {
					listeners[i].handleEvent(event);
				}
			}
		}.start();
	}

	/**
	 * get the events from R-OSGi received through a RemoteServiceListener
	 * instance.
	 * 
	 * @see ch.ethz.iks.r_osgi.RemoteServiceListener#remoteServiceEvent(ch.ethz.iks.r_osgi.RemoteServiceEvent)
	 */
	public void remoteServiceEvent(final RemoteServiceEvent event) {
		if (event.getType() == RemoteServiceEvent.REGISTERED) {
			checkImport(event.getRemoteReference());
		}
	}

	/**
	 * check if the remote service should be automatically imported by this
	 * container.
	 * 
	 * @param ref
	 *            the remote service reference to check.
	 */
	private void checkImport(final RemoteServiceReference ref) {
		final Object target = ref.getProperty(org.eclipse.ecf.remoteservice.Constants.SERVICE_REGISTRATION_TARGETS);
		if (target instanceof ID && ((ID) target).equals(containerID)) {
			remoteService.getRemoteService(ref);
		} else if (target instanceof ID[]) {
			final ID[] targets = (ID[]) target;
			for (int i = 0; i < targets.length; i++) {
				if (targets[i].equals(containerID)) {
					remoteService.getRemoteService(ref);
				}
			}
		}
	}

	/**
	 * Clone a dictionary instance to avoid modification by the caller of the
	 * registration method.
	 * 
	 * @param props
	 *            the dictionary instance.
	 * @return a clone.
	 */
	private Hashtable clone(final Dictionary props) {
		final Hashtable clone = new Hashtable();
		for (Enumeration e = props.keys(); e.hasMoreElements();) {
			final Object key = e.nextElement();
			clone.put(key, props.get(key));
		}
		return clone;
	}

	public IFuture asyncGetRemoteServiceReferences(final ID[] idFilter, final String clazz, final String filter) {
		IExecutor executor = new ThreadsExecutor();
		return executor.execute(new IProgressRunnable() {
			public Object run(IProgressMonitor monitor) throws Exception {
				return getRemoteServiceReferences(idFilter, clazz, filter);
			}
		}, null);
	}

	public IFuture asyncGetRemoteServiceReferences(final ID target, final String clazz, final String filter) {
		IExecutor executor = new ThreadsExecutor();
		return executor.execute(new IProgressRunnable() {
			public Object run(IProgressMonitor monitor) throws Exception {
				return getRemoteServiceReferences(target, clazz, filter);
			}
		}, null);
	}

	public Namespace getRemoteServiceNamespace() {
		return IDFactory.getDefault().getNamespaceByName(R_OSGiRemoteServiceNamespace.NAME);
	}

	public IRemoteFilter createRemoteFilter(String filter) throws InvalidSyntaxException {
		return new RemoteFilterImpl(context, filter);
	}

	public IRemoteServiceID getRemoteServiceID(ID containerId, long containerRelativeId) {
		return (IRemoteServiceID) IDFactory.getDefault().createID(getRemoteServiceNamespace(), new Object[] {containerID, new Long(containerRelativeId)});
	}

	public IRemoteServiceReference getRemoteServiceReference(IRemoteServiceID serviceId) {
		if (serviceId == null)
			return null;
		ID cID = serviceId.getContainerID();
		// If the container ID isn't relevant to us we ignore
		if (cID instanceof R_OSGiID) {
			// If it's not the same as who we're connected to, we ignore
			if (cID.equals(getConnectedID())) {
				final String filter = "(" + Constants.SERVICE_ID + "=" + serviceId + ")"; //$NON-NLS-1$ //$NON-NLS-2$ //$NON-NLS-3$
				try {
					// Get remote service references...I imagine this can/would block
					RemoteServiceReference[] refs = remoteService.getRemoteServiceReferences(((R_OSGiID) cID).getURI(), null, context.createFilter(filter));
					// There should be either zero or 1 remote service reference
					if (refs == null || refs.length == 0)
						return null;
					return new RemoteServiceReferenceImpl(createRemoteServiceID(refs[0]), refs[0]);
				} catch (InvalidSyntaxException e) {
					// shouldn't happen as filter better be well formed
					return null;
				}
			}
		}
		return null;
	}

	public void setConnectContextForAuthentication(IConnectContext connectContext) {
		this.connectContext = connectContext;
	}

}