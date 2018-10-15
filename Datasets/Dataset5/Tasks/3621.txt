IExecutor executor = new ThreadsExecutor();

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
import ch.ethz.iks.r_osgi.channels.ChannelEndpointManager;
import java.io.IOException;
import java.util.*;
import org.eclipse.core.runtime.Assert;
import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.ecf.core.*;
import org.eclipse.ecf.core.events.*;
import org.eclipse.ecf.core.identity.*;
import org.eclipse.ecf.core.security.IConnectContext;
import org.eclipse.ecf.core.util.*;
import org.eclipse.ecf.provider.r_osgi.identity.R_OSGiID;
import org.eclipse.ecf.provider.r_osgi.identity.R_OSGiNamespace;
import org.eclipse.ecf.remoteservice.*;
import org.eclipse.ecf.remoteservice.events.IRemoteServiceRegisteredEvent;
import org.eclipse.ecf.remoteservice.events.IRemoteServiceUnregisteredEvent;
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

	// the EndpointManager for the endpoint.
	private ChannelEndpointManager endpointMgr;

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

	/**
	 * @throws IDCreateException
	 */
	public R_OSGiRemoteServiceContainer() throws IDCreateException {
		context = Activator.getDefault().getContext();
		remoteService = Activator.getDefault().getRemoteOSGiService();
		if (remoteService == null) {
			throw new IDCreateException("R-OSGi not running. Cannot create local container ID"); //$NON-NLS-1$
		}
	}

	public R_OSGiRemoteServiceContainer(final ID containerID) throws IDCreateException {
		this();
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
			final String filter = "(" + org.eclipse.ecf.remoteservice.Constants.REMOTE_SERVICE_CONTAINER_ID + "=" + containerID + ")"; //$NON-NLS-1$ //$NON-NLS-2$ //$NON-NLS-3$
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
							public String[] getClazzes() {
								return (String[]) event.getRemoteReference().getProperty(Constants.OBJECTCLASS);
							}

							public ID getContainerID() {
								return containerID;
							}

							public IRemoteServiceReference getReference() {
								return new RemoteServiceReferenceImpl(containerID, event.getRemoteReference());
							}

							public String toString() {
								return "RemoteServiceRegisteredEvent(" + containerID + "," + getReference(); //$NON-NLS-1$ //$NON-NLS-2$
							}
						});
						return;
					case RemoteServiceEvent.UNREGISTERING :
						listener.handleServiceEvent(new IRemoteServiceUnregisteredEvent() {
							public String[] getClazzes() {
								return (String[]) event.getRemoteReference().getProperty(Constants.OBJECTCLASS);
							}

							public ID getContainerID() {
								return containerID;
							}

							public IRemoteServiceReference getReference() {
								return new RemoteServiceReferenceImpl(containerID, event.getRemoteReference());
							}

							public String toString() {
								return "RemoteServiceUnregisteredEvent(" + containerID + "," + getReference(); //$NON-NLS-1$ //$NON-NLS-2$
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
		Assert.isNotNull(clazz);

		final RemoteServiceReference[] refs = remoteService.getRemoteServiceReferences(connectedID.getURI(), clazz, filter == null ? null : createRemoteFilter(filter));
		if (refs == null) {
			return null;
		}
		final IRemoteServiceReference[] result = new IRemoteServiceReference[refs.length];
		for (int i = 0; i < refs.length; i++) {
			result[i] = new RemoteServiceReferenceImpl(containerID, refs[i]);
		}
		return result;
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
		props.put(org.eclipse.ecf.remoteservice.Constants.REMOTE_SERVICE_CONTAINER_ID, containerID);

		// register the service with the local framework
		final ServiceRegistration reg = context.registerService(clazzes, service, props);

		remoteServicesRegs.put(reg.getReference(), reg);

		return new RemoteServiceRegistrationImpl(containerID, reg);
	}

	/**
	 * remove a registered remote service listener.
	 * 
	 * @param listener
	 *            the remote service listener.
	 * @see org.eclipse.ecf.remoteservice.IRemoteServiceContainerAdapter#removeRemoteServiceListener(org.eclipse.ecf.remoteservice.IRemoteServiceListener)
	 */
	public void removeRemoteServiceListener(final IRemoteServiceListener listener) {

		final ServiceRegistration reg = (ServiceRegistration) remoteServiceListeners.remove(listener);
		if (reg == null) {
			return;
		}

		reg.unregister();
	}

	/**
	 * 
	 * @see org.eclipse.ecf.remoteservice.IRemoteServiceContainerAdapter#ungetRemoteService(org.eclipse.ecf.remoteservice.IRemoteServiceReference)
	 */
	public boolean ungetRemoteService(IRemoteServiceReference reference) {
		remoteService.ungetRemoteService(((RemoteServiceReferenceImpl) reference).getR_OSGiServiceReference());
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
	public void connect(final ID targetID, final IConnectContext connectContext) throws ContainerConnectException {
		Assert.isNotNull(targetID);
		//Assert.isNotNull(connectContext);

		if (containerID != null) {
			throw new ContainerConnectException("Container is already connected to " + containerID); //$NON-NLS-1$
		}

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

			final RemoteServiceReference[] refs = remoteService.connect(target.getURI());
			if (refs != null) {
				for (int i = 0; i < refs.length; i++) {
					checkImport(refs[i]);
				}
			}
			connectedID = target;

			endpointMgr = remoteService.getEndpointManager(target.getURI());

			containerID = (R_OSGiID) IDFactory.getDefault().createID(R_OSGiNamespace.NAME, endpointMgr.getLocalAddress().toString());

			startRegTracker();

		} catch (IOException ioe) {
			throw new ContainerConnectException(ioe);
		} catch (IDCreateException e) {
			throw new ContainerConnectException(e);
		}
		fireListeners(new ContainerConnectedEvent(containerID, connectedID));
	}

	/**
	 * disconnect from the remote container.
	 * 
	 * @see org.eclipse.ecf.core.IContainer#disconnect()
	 */
	public void disconnect() {
		if (connectedID != null) {
			fireListeners(new ContainerDisconnectingEvent(containerID, connectedID));
			remoteService.disconnect(connectedID.getURI());
			connectedID = null;
			fireListeners(new ContainerDisconnectedEvent(containerID, connectedID));
		}

	}

	/**
	 * dispose the container.
	 * 
	 * @see org.eclipse.ecf.core.IContainer#dispose()
	 */
	public void dispose() {
		remoteService = null;

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
	public ID getConnectedID() {
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
		IExecutor executor = new ThreadExecutor();
		return executor.execute(new IProgressRunnable() {
			public Object run(IProgressMonitor monitor) throws Throwable {
				return getRemoteServiceReferences(idFilter, clazz, filter);
			}
		}, null);
	}

	public Namespace getRemoteServiceNamespace() {
		return getConnectNamespace();
	}

	public IRemoteFilter createRemoteFilter(String filter) throws InvalidSyntaxException {
		return new RemoteFilterImpl(context, filter);
	}
}