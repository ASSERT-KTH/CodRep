throw new ECFException(NLS.bind(Messages.RegistrySharedObject_19, Long.toString(call.getTimeout())), new TimeoutException(call.getTimeout()));

/*******************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.provider.remoteservice.generic;

import java.io.IOException;
import java.io.Serializable;
import java.security.*;
import java.util.*;
import org.eclipse.core.runtime.*;
import org.eclipse.core.runtime.jobs.Job;
import org.eclipse.ecf.core.ContainerConnectException;
import org.eclipse.ecf.core.events.IContainerConnectedEvent;
import org.eclipse.ecf.core.events.IContainerDisconnectedEvent;
import org.eclipse.ecf.core.identity.*;
import org.eclipse.ecf.core.jobs.JobsExecutor;
import org.eclipse.ecf.core.security.IConnectContext;
import org.eclipse.ecf.core.sharedobject.*;
import org.eclipse.ecf.core.sharedobject.events.ISharedObjectActivatedEvent;
import org.eclipse.ecf.core.util.*;
import org.eclipse.ecf.internal.provider.remoteservice.*;
import org.eclipse.ecf.remoteservice.*;
import org.eclipse.ecf.remoteservice.events.*;
import org.eclipse.equinox.concurrent.future.*;
import org.eclipse.osgi.util.NLS;
import org.osgi.framework.*;

public class RegistrySharedObject extends BaseSharedObject implements IRemoteServiceContainerAdapter {

	protected RemoteServiceRegistryImpl localRegistry;

	protected final Map remoteRegistrys = Collections.synchronizedMap(new HashMap());

	protected final List serviceListeners = new ArrayList();

	protected final Map localServiceRegistrations = new HashMap();

	protected Map addRegistrationRequests = new Hashtable();

	/**
	 * @since 3.0
	 */
	protected int addRegistrationRequestTimeout = ADD_REGISTRATION_REQUEST_TIMEOUT;

	protected List requests = Collections.synchronizedList(new ArrayList());

	/**
	 * @since 3.0
	 */
	protected IConnectContext connectContext;

	public RegistrySharedObject() {
		//
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
		final IRemoteFilter remoteFilter = (filter == null) ? null : new RemoteFilterImpl(filter);
		final List references = new ArrayList();
		// Add any from local registry
		synchronized (localRegistry) {
			addReferencesFromRegistry(clazz, remoteFilter, localRegistry, references);
		}
		// Lookup from remote registrys...add to given references List
		addReferencesFromRemoteRegistrys(null, clazz, remoteFilter, references);
		final IRemoteServiceReference[] result = (IRemoteServiceReference[]) references.toArray(new IRemoteServiceReference[references.size()]);
		Trace.exiting(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_EXITING, this.getClass(), "getAllRemoteServiceReferences", result); //$NON-NLS-1$
		return (result.length == 0) ? null : result;
	}

	/**
	 * @since 3.0
	 */
	public IRemoteServiceReference[] getRemoteServiceReferences(ID targetID, String clazz, String filter) throws InvalidSyntaxException, ContainerConnectException {
		// If no target specified, just search for all available references
		if (targetID == null)
			return getRemoteServiceReferences((ID[]) null, clazz, filter);
		// If we're not already connected, then connect to targetID
		// If we *are* already connected, then we do *not* connect to target, but rather just search for targetID/endpoint
		if (!isConnected()) {
			getContext().connect(targetID, connectContext);
		}
		// Now we're connected (or already were connected), so we look for remote service references for target
		return getRemoteServiceReferences(new ID[] {targetID}, clazz, filter);
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.remoteservice.IRemoteServiceContainerAdapter#getRemoteServiceReferences(org.eclipse.ecf.core.identity.ID[], java.lang.String, java.lang.String)
	 */
	public IRemoteServiceReference[] getRemoteServiceReferences(ID[] idFilter, String clazz, String filter) throws InvalidSyntaxException {
		Trace.entering(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_ENTERING, this.getClass(), "getRemoteServiceReferences", new Object[] {idFilter, clazz, filter}); //$NON-NLS-1$
		if (clazz == null)
			return null;
		final IRemoteFilter remoteFilter = (filter == null) ? null : new RemoteFilterImpl(filter);
		final List references = new ArrayList();
		// Lookup from remote registrys...add to given references List
		addReferencesFromRemoteRegistrys(idFilter, clazz, remoteFilter, references);
		// If none found the first time we send a registration request and wait
		if (references.size() == 0) {
			AddRegistrationRequest first = null;
			List ourAddRegistrationRequests = new ArrayList();
			// It's not already here...so send out AddRegistrationRequests
			if (idFilter == null) {
				first = new AddRegistrationRequest(null, clazz, filter, first);
				ourAddRegistrationRequests.add(first);
			} else {
				for (int i = 0; i < idFilter.length; i++) {
					ID target = idFilter[i];
					if (target != null) {
						AddRegistrationRequest request = new AddRegistrationRequest(target, clazz, filter, first);
						if (i == 0)
							first = request;
						// Add to list of all know
						ourAddRegistrationRequests.add(request);
						addRegistrationRequests.put(request.getId(), request);
						sendAddRegistrationRequest(target, request, getAddRegistrationRequestCredentials(request));
					}
				}
			}
			// Wait here for timeout or response
			first.waitForResponse(ADD_REGISTRATION_REQUEST_TIMEOUT);
			// Now look again
			addReferencesFromRemoteRegistrys(idFilter, clazz, remoteFilter, references);
			// In either case, remove all the addRegistrationRequests
			for (Iterator i = ourAddRegistrationRequests.iterator(); i.hasNext();) {
				AddRegistrationRequest request = (AddRegistrationRequest) i.next();
				addRegistrationRequests.remove(request.getId());
			}

		}
		ID localContainerID = getLocalContainerID();
		// Only look in local remote service registry if idFilter is null OR the idFilter 
		// contains the local container ID
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
		return null;
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.remoteservice.IRemoteServiceContainerAdapter#registerRemoteService(java.lang.String[], java.lang.Object, java.util.Dictionary)
	 */
	public IRemoteServiceRegistration registerRemoteService(String[] clazzes, Object service, Dictionary properties) {
		Trace.entering(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_ENTERING, this.getClass(), "registerRemoteService", new Object[] {clazzes, service, properties}); //$NON-NLS-1$
		if (service == null) {
			throw new NullPointerException(Messages.RegistrySharedObject_EXCEPTION_SERVICE_CANNOT_BE_NULL);
		}
		final int size = clazzes.length;

		if (size == 0) {
			throw new IllegalArgumentException(Messages.RegistrySharedObject_EXCEPTION_SERVICE_CLASSES_LIST_EMPTY);
		}

		final String[] copy = new String[clazzes.length];
		for (int i = 0; i < clazzes.length; i++) {
			copy[i] = new String(clazzes[i].getBytes());
		}
		clazzes = copy;

		final String invalidService = checkServiceClass(clazzes, service);
		if (invalidService != null) {
			throw new IllegalArgumentException(Messages.RegistrySharedObject_7 + invalidService);
		}

		final RemoteServiceRegistrationImpl reg = new RemoteServiceRegistrationImpl();
		reg.publish(this, localRegistry, service, clazzes, properties);

		final ID[] targets = getTargetsFromProperties(properties);
		if (targets == null)
			sendAddRegistration(null, reg);
		else
			for (int i = 0; i < targets.length; i++)
				sendAddRegistration(targets[i], reg);

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
		super.addEventProcessor(new IEventProcessor() {
			public boolean processEvent(Event arg0) {
				if (arg0 instanceof IContainerConnectedEvent) {
					handleContainerConnectedEvent((IContainerConnectedEvent) arg0);
				} else if (arg0 instanceof IContainerDisconnectedEvent) {
					handleContainerDisconnectedEvent((IContainerDisconnectedEvent) arg0);
				} else if (arg0 instanceof ISharedObjectActivatedEvent) {
					if (getSOContext().getConnectedID() != null) {
						// We're already connected, so send request for update
						sendRegistryUpdateRequest();
					}
				}
				return false;
			}
		});
		localRegistry = new RemoteServiceRegistryImpl(getLocalContainerID());
		Trace.exiting(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_EXITING, this.getClass(), "initialize"); //$NON-NLS-1$
	}

	protected void handleContainerDisconnectedEvent(IContainerDisconnectedEvent event) {
		Trace.entering(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_ENTERING, this.getClass(), "handleContainerDisconnectedEvent", event); //$NON-NLS-1$
		final ID targetID = event.getTargetID();
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
		// Do notification outside synchronized block
		if (registrations != null) {
			for (int i = 0; i < registrations.length; i++) {
				fireRemoteServiceListeners(createUnregisteredEvent(registrations[i]));
			}
		}
		Trace.exiting(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_EXITING, this.getClass(), "handleContainerDisconnectedEvent"); //$NON-NLS-1$
	}

	protected void sendRegistryUpdate(ID targetContainerID) {
		synchronized (localRegistry) {
			final RemoteServiceRegistrationImpl registrations[] = localRegistry.getRegistrations();
			if (registrations != null) {
				for (int i = 0; i < registrations.length; i++) {
					final RemoteServiceRegistrationImpl registration = registrations[i];
					sendAddRegistration(targetContainerID, registration);
				}
			}
		}
	}

	protected void handleContainerConnectedEvent(IContainerConnectedEvent event) {
		Trace.entering(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_ENTERING, this.getClass(), "handleContainerConnectedEvent", event); //$NON-NLS-1$
		// If we're a group manager or the newly connected container is the
		// group manager
		ID targetID = event.getTargetID();
		// If we're the group manager, or we've just joined the group,
		// then we sendAddRegistration to all
		if (getContext().isGroupManager() || event.getTargetID().equals(getConnectedID())) {
			targetID = null;
		}
		sendRegistryUpdate(targetID);
		Trace.exiting(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_EXITING, this.getClass(), "handleContainerConnectedEvent"); //$NON-NLS-1$
	}

	private Request createRequest(RemoteServiceRegistrationImpl remoteRegistration, IRemoteCall call, IRemoteCallListener listener) {
		final RemoteServiceReferenceImpl refImpl = (RemoteServiceReferenceImpl) remoteRegistration.getReference();
		return new Request(this.getLocalContainerID(), remoteRegistration.getServiceId(), RemoteCallImpl.createRemoteCall(refImpl.getRemoteClass(), call.getMethod(), call.getParameters(), call.getTimeout()), listener);
	}

	protected void fireRemoteServiceListeners(IRemoteServiceEvent event) {
		List entries = null;
		synchronized (serviceListeners) {
			entries = new ArrayList(serviceListeners);
		}
		for (final Iterator i = entries.iterator(); i.hasNext();) {
			final IRemoteServiceListener l = (IRemoteServiceListener) i.next();
			l.handleServiceEvent(event);
		}
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
			// Then get the specified timeout and calculate when we should
			// timeout in real time
			final long timeout = call.getTimeout() + System.currentTimeMillis();
			// Now loop until timeout time has elapsed
			while ((timeout - System.currentTimeMillis()) > 0 && !doneWaiting) {
				synchronized (request) {
					if (request.isDone()) {
						Trace.trace(Activator.PLUGIN_ID, Messages.RegistrySharedObject_15 + request);
						doneWaiting = true;
						response = request.getResponse();
						if (response == null)
							throw new ECFException(Messages.RegistrySharedObject_EXCEPTION_INVALID_RESPONSE);
					} else {
						Trace.trace(Activator.PLUGIN_ID, "Waiting " + RESPONSE_WAIT_INTERVAL + " for response to request: " + request); //$NON-NLS-1$ //$NON-NLS-2$
						request.wait(RESPONSE_WAIT_INTERVAL);
					}
				}
			}
			if (!doneWaiting)
				throw new ECFException(Messages.RegistrySharedObject_19 + call.getTimeout() + Messages.RegistrySharedObject_20);
		} catch (final IOException e) {
			log(CALL_REQUEST_ERROR_CODE, CALL_REQUEST_ERROR_MESSAGE, e);
			throw new ECFException(Messages.RegistrySharedObject_EXCEPTION_SENDING_REQUEST, e);
		} catch (final InterruptedException e) {
			log(CALL_REQUEST_TIMEOUT_ERROR_CODE, CALL_REQUEST_TIMEOUT_ERROR_MESSAGE, e);
			throw new ECFException(Messages.RegistrySharedObject_EXCEPTION_WAIT_INTERRUPTED, e);
		}
		// Success...now get values and return
		Object result = null;
		if (response.hadException())
			throw new ECFException(Messages.RegistrySharedObject_EXCEPTION_IN_REMOTE_CALL, response.getException());
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

	private static final String FIRE_REQUEST_ERROR_MESSAGE = Messages.RegistrySharedObject_EXCEPTION_SENDING_FIRE_REQUEST;

	private static final int FIRE_REQUEST_ERROR_CODE = 202;

	private static final String CALL_REQUEST = "handleCallRequest"; //$NON-NLS-1$

	private static final String CALL_REQUEST_ERROR_MESSAGE = Messages.RegistrySharedObject_EXCEPTION_SENDING_CALL_REQUEST;

	private static final int CALL_REQUEST_ERROR_CODE = 203;

	private static final String CALL_REQUEST_TIMEOUT_ERROR_MESSAGE = Messages.RegistrySharedObject_EXCEPTION_TIMEOUT_FOR_CALL_REQUEST;

	private static final int CALL_REQUEST_TIMEOUT_ERROR_CODE = 204;

	private static final String UNREGISTER = "handleUnregister"; //$NON-NLS-1$

	private static final String UNREGISTER_ERROR_MESSAGE = Messages.RegistrySharedObject_EXCEPTION_SENDING_SERVICE_UNREGISTER;

	private static final int UNREGISTER_ERROR_CODE = 206;

	private static final String MSG_INVOKE_ERROR_MESSAGE = Messages.RegistrySharedObject_EXCEPTION_SHARED_OBJECT_INVOKE;

	private static final int MSG_INVOKE_ERROR_CODE = 207;

	private static final String SERVICE_INVOKE_ERROR_MESSAGE = Messages.RegistrySharedObject_EXCEPTION_INVOKING_SERVICE;

	private static final int SERVICE_INVOKE_ERROR_CODE = 208;

	private static final String HANDLE_REQUEST_ERROR_MESSAGE = Messages.RegistrySharedObject_EXCEPTION_LOCALLY_INVOKING_REMOTE_CALL;

	private static final int HANDLE_REQUEST_ERROR_CODE = 209;

	private static final String CALL_RESPONSE = "handleCallResponse"; //$NON-NLS-1$

	private static final String CALL_RESPONSE_ERROR_MESSAGE = Messages.RegistrySharedObject_EXCEPTION_SENDING_RESPONSE;

	private static final int CALL_RESPONSE_ERROR_CODE = 210;

	private static final String REQUEST_NOT_FOUND_ERROR_MESSAGE = Messages.RegistrySharedObject_EXCEPTION_REQUEST_NOT_FOUND;

	private static final int REQUEST_NOT_FOUND_ERROR_CODE = 211;

	private static final long RESPONSE_WAIT_INTERVAL = 5000;

	private static final String ADD_REGISTRATION = "handleAddRegistration"; //$NON-NLS-1$

	private static final String ADD_REGISTRATION_ERROR_MESSAGE = Messages.RegistrySharedObject_EXCEPTION_SENDING_ADD_SERVICE;

	private static final int ADD_REGISTRATION_ERROR_CODE = 212;

	private static final String ADD_REGISTRATION_REFUSED = "handleAddRegistrationRefused"; //$NON-NLS-1$

	private static final String ADD_REGISTRATION_REFUSED_ERROR_MESSAGE = "Error sending addRegistration refused"; //$NON-NLS-1$

	private static final int ADD_REGISTRATION_REFUSED_ERROR_CODE = 214;

	private static final String REQUEST_SERVICE = "handleRequestService"; //$NON-NLS-1$

	private static final int REQUEST_SERVICE_ERROR_CODE = 213;

	private static final String REQUEST_SERVICE_ERROR_MESSAGE = "Error sending requestServiceReference"; //$NON-NLS-1$

	private static final String REGISTRY_UPDATE_REQUEST = "handleRegistryUpdateRequest"; //$NON-NLS-1$

	private static final int ADD_REGISTRATION_REQUEST_TIMEOUT = new Integer(System.getProperty("ecf.addregistrationrequest.timeout", "5000")).intValue(); //$NON-NLS-1$ //$NON-NLS-2$

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
		if (remoteContainerID == null || getLocalContainerID().equals(remoteContainerID)) {
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
		if (request == null || request.getService() == null)
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
		synchronized (localRegistry) {
			RemoteServiceReferenceImpl[] srs = (RemoteServiceReferenceImpl[]) localRegistry.lookupServiceReferences(request.getService(), rf);
			if (srs != null && srs.length > 0) {
				for (int i = 0; i < srs.length; i++) {
					RemoteServiceRegistrationImpl impl = getRemoteServiceRegistrationImpl(srs[i]);
					if (impl != null) {
						sendAddRegistration(remoteContainerID, requestId, impl);
					}
				}
			} else
				sendAddRegistrationRequestRefused(remoteContainerID, requestId, null);
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

	protected void handleAddRegistration(ID remoteContainerID, Integer requestId, final RemoteServiceRegistrationImpl registration) {
		Trace.entering(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_ENTERING, this.getClass(), ADD_REGISTRATION, new Object[] {remoteContainerID, registration});
		if (remoteContainerID == null || getLocalContainerID().equals(remoteContainerID)) {
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
	 */
	private void notifyAddRegistrationResponse(ID remoteContainerID, Integer requestId, AccessControlException exception) {
		if (remoteContainerID == null)
			return;
		List pendingRequests = new ArrayList();
		// If the requestId is null, this isn't in response to any particular request,
		// So we get all AddRegistrationRequests
		synchronized (addRegistrationRequests) {
			if (requestId == null) {
				for (Iterator i = addRegistrationRequests.keySet().iterator(); i.hasNext();) {
					Integer key = (Integer) i.next();
					pendingRequests.add(addRegistrationRequests.get(key));
				}
			} else
				pendingRequests.add(addRegistrationRequests.get(requestId));
		}
		// Then notify each one of the response from given remoteContainerID
		for (Iterator i = pendingRequests.iterator(); i.hasNext();) {
			AddRegistrationRequest request = (AddRegistrationRequest) i.next();
			if (request != null)
				request.notifyResponse(remoteContainerID, exception);
		}
	}

	private void localRegisterService(RemoteServiceRegistrationImpl registration) {
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

	private void addLocalServiceRegistration(ID remoteContainerID, ServiceRegistration registration) {
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

	protected void handleCallRequest(Request request) {
		Trace.entering(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_ENTERING, this.getClass(), "handleCallRequest", request); //$NON-NLS-1$
		final ID responseTarget = request.getRequestContainerID();
		final RemoteServiceRegistrationImpl localRegistration = getLocalRegistrationForRequest(request);
		// Else we've got a local service and we invoke it
		final RemoteCallImpl call = request.getCall();
		Response response = null;
		Object result = null;
		try {
			result = localRegistration.callService(call);
			response = new Response(request.getRequestId(), result);
		} catch (final Exception e) {
			response = new Response(request.getRequestId(), e);
			log(SERVICE_INVOKE_ERROR_CODE, SERVICE_INVOKE_ERROR_MESSAGE, e);
		}
		// Now send response back to responseTarget (original requestor)
		sendCallResponse(responseTarget, response);
		Trace.exiting(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_EXITING, this.getClass(), "handleCallRequest"); //$NON-NLS-1$
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
			throw new ECFException(Messages.RegistrySharedObject_EXCEPTION_SENDING_REMOTE_REQUEST, e);
		}
		Trace.exiting(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_EXITING, this.getClass(), "sendFireRequest", request); //$NON-NLS-1$
		return request;
	}

	protected void handleFireRequest(Request request) {
		Trace.entering(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_ENTERING, this.getClass(), FIRE_REQUEST, new Object[] {request});
		final RemoteServiceRegistrationImpl localRegistration = getLocalRegistrationForRequest(request);
		// Else we've got a local service and we invoke it
		final RemoteCallImpl call = request.getCall();
		try {
			localRegistration.callService(call);
		} catch (final Exception e) {
			log(HANDLE_REQUEST_ERROR_CODE, HANDLE_REQUEST_ERROR_MESSAGE, e);
		}
		Trace.exiting(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_EXITING, this.getClass(), FIRE_REQUEST);
	}

	protected void sendUnregister(RemoteServiceRegistrationImpl serviceRegistration) {
		Trace.entering(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_ENTERING, this.getClass(), "sendUnregister", new Object[] {serviceRegistration}); //$NON-NLS-1$
		synchronized (localRegistry) {
			localRegistry.unpublishService(serviceRegistration);
			final ID containerID = serviceRegistration.getContainerID();
			final Long serviceId = new Long(serviceRegistration.getServiceId());
			try {
				this.sendSharedObjectMsgTo(null, SharedObjectMsg.createMsg(UNREGISTER, new Object[] {containerID, serviceId}));
			} catch (final IOException e) {
				log(UNREGISTER_ERROR_CODE, UNREGISTER_ERROR_MESSAGE, e);
			}
		}
		fireRemoteServiceListeners(createUnregisteredEvent(serviceRegistration));
		Trace.exiting(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_EXITING, this.getClass(), "sendUnregister"); //$NON-NLS-1$
	}

	private void unregisterServiceRegistrationsForContainer(ID containerID) {
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

	private void unregisterAllServiceRegistrations() {
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

	private RemoteServiceRegistrationImpl getLocalRegistrationForRequest(Request request) {
		synchronized (localRegistry) {
			return localRegistry.findRegistrationForServiceId(request.getServiceId());
		}
	}

	private boolean addRequest(Request request) {
		return requests.add(request);
	}

	private Request getRequest(long requestId) {
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

	private boolean removeRequest(Request request) {
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
			logException(MSG_INVOKE_ERROR_CODE, NLS.bind(MSG_INVOKE_ERROR_MESSAGE, msg), e);
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