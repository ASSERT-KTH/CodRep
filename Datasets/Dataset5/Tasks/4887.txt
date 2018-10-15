final Object localServiceRegistrationValue = registration.getProperty(Constants.PROXY_SERVICE_REGISTRATION);

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
import java.security.AccessController;
import java.security.PrivilegedAction;
import java.util.*;
import org.eclipse.ecf.core.events.IContainerConnectedEvent;
import org.eclipse.ecf.core.events.IContainerDisconnectedEvent;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.sharedobject.*;
import org.eclipse.ecf.core.sharedobject.events.ISharedObjectActivatedEvent;
import org.eclipse.ecf.core.util.*;
import org.eclipse.ecf.internal.provider.remoteservice.*;
import org.eclipse.ecf.remoteservice.*;
import org.eclipse.ecf.remoteservice.events.*;
import org.osgi.framework.BundleContext;
import org.osgi.framework.ServiceRegistration;

public class RegistrySharedObject extends BaseSharedObject implements IRemoteServiceContainerAdapter {

	protected RemoteServiceRegistryImpl localRegistry;

	protected final Map remoteRegistrys = Collections.synchronizedMap(new HashMap());

	protected final List serviceListeners = new ArrayList();

	protected final Map localServiceRegistrations = new HashMap();

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
	}

	/* Begin implementation of IRemoteServiceContainerAdapter public interface */
	public void addRemoteServiceListener(IRemoteServiceListener listener) {
		synchronized (serviceListeners) {
			serviceListeners.add(listener);
		}
	}

	public void removeRemoteServiceListener(IRemoteServiceListener listener) {
		synchronized (serviceListeners) {
			serviceListeners.remove(listener);
		}
	}

	public IRemoteService getRemoteService(IRemoteServiceReference reference) {
		Trace.entering(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_ENTERING, this.getClass(), "getRemoteService", reference); //$NON-NLS-1$
		final RemoteServiceRegistrationImpl registration = getRemoteServiceRegistrationImpl(reference);
		if (registration == null)
			return null;
		final RemoteServiceImpl remoteService = new RemoteServiceImpl(this, registration);
		Trace.exiting(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_EXITING, this.getClass(), "getRemoteService", remoteService); //$NON-NLS-1$
		return remoteService;
	}

	public IRemoteServiceReference[] getRemoteServiceReferences(ID[] idFilter, String clazz, String filter) {
		Trace.entering(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_ENTERING, this.getClass(), "getRemoteServiceReferences", new Object[] {idFilter, clazz, filter}); //$NON-NLS-1$
		final IRemoteFilter remoteFilter = createRemoteFilterFromString(filter);
		final List references = new ArrayList();
		synchronized (remoteRegistrys) {
			if (idFilter == null) {
				final ArrayList registrys = new ArrayList(remoteRegistrys.values());
				for (final Iterator i = registrys.iterator(); i.hasNext();) {
					final RemoteServiceRegistryImpl registry = (RemoteServiceRegistryImpl) i.next();
					// Add IRemoteServiceReferences from each remote registry
					addReferencesFromRegistry(clazz, remoteFilter, registry, references);
				}
			} else {
				for (int i = 0; i < idFilter.length; i++) {
					final RemoteServiceRegistryImpl registry = (RemoteServiceRegistryImpl) remoteRegistrys.get(idFilter[i]);
					if (registry != null) {
						addReferencesFromRegistry(clazz, remoteFilter, registry, references);
					}
				}
			}
		}
		synchronized (localRegistry) {
			addReferencesFromRegistry(clazz, remoteFilter, localRegistry, references);
		}
		final IRemoteServiceReference[] result = (IRemoteServiceReference[]) references.toArray(new IRemoteServiceReference[references.size()]);
		Trace.exiting(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_EXITING, this.getClass(), "getRemoteServiceReferences", result); //$NON-NLS-1$
		return result;
	}

	protected ID[] getTargetsFromProperties(Dictionary properties) {
		return null;
	}

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

	public boolean ungetRemoteService(IRemoteServiceReference ref) {
		return true;
	}

	protected ISharedObjectContext getSOContext() {
		return super.getContext();
	}

	/* End implementation of IRemoteServiceContainerAdapter public interface */

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
		synchronized (remoteRegistrys) {
			final RemoteServiceRegistryImpl registry = getRemoteRegistry(targetID);
			if (registry != null) {
				removeRemoteRegistry(targetID);
				final RemoteServiceRegistrationImpl registrations[] = registry.getRegistrations();
				if (registrations != null) {
					for (int i = 0; i < registrations.length; i++) {
						registry.unpublishService(registrations[i]);
						unregisterServiceRegistrationsForContainer(registrations[i].getContainerID());
						fireRemoteServiceListeners(createUnregisteredEvent(registrations[i]));
					}
				}
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
		Trace.exiting(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_EXITING, this.getClass(), "handleContainerDisconnectedEvent"); //$NON-NLS-1$
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

	private IRemoteFilter createRemoteFilterFromString(String filter) {
		// XXX make remote filter
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
			final long requestId = sendCallRequest(registration, call);
			// Then get the specified timeout and calculate when we should
			// timeout in real time
			final long timeout = call.getTimeout() + System.currentTimeMillis();
			// Now loop until timeout time has elapsed
			while ((timeout - System.currentTimeMillis()) > 0 && !doneWaiting) {
				final Request request = findRequestForId(requestId);
				if (request == null) {
					throw new NullPointerException(Messages.RegistrySharedObject_14 + requestId);
				}
				synchronized (request) {
					if (request.isDone()) {
						removeRequest(request);
						Trace.trace(Activator.PLUGIN_ID, Messages.RegistrySharedObject_15 + request);
						doneWaiting = true;
						response = request.getResponse();
						if (response == null) {
							throw new NullPointerException(Messages.RegistrySharedObject_EXCEPTION_INVALID_RESPONSE);
						}
					} else {
						Trace.trace(Activator.PLUGIN_ID, "Waiting " + RESPONSE_WAIT_INTERVAL + " for response to request: " + request); //$NON-NLS-1$ //$NON-NLS-2$
						request.wait(RESPONSE_WAIT_INTERVAL);
					}
				}
			}
			if (!doneWaiting) {
				throw new ECFException(Messages.RegistrySharedObject_19 + call.getTimeout() + Messages.RegistrySharedObject_20);
			}
		} catch (final IOException e) {
			log(CALL_REQUEST_ERROR_CODE, CALL_REQUEST_ERROR_MESSAGE, e);
			throw new ECFException(Messages.RegistrySharedObject_EXCEPTION_SENDING_REQUEST, e);
		} catch (final InterruptedException e) {
			log(CALL_REQUEST_TIMEOUT_ERROR_CODE, CALL_REQUEST_TIMEOUT_ERROR_MESSAGE, e);
			throw new ECFException(Messages.RegistrySharedObject_EXCEPTION_WAIT_INTERRUPTED, e);
		}
		// Success...now get values and return
		Object result = null;
		if (response.hadException()) {
			throw new ECFException(Messages.RegistrySharedObject_EXCEPTION_IN_REMOTE_CALL, response.getException());
		}
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

	private static final String REGISTRY_UPDATE_REQUEST = "handleRegistryUpdateRequest"; //$NON-NLS-1$

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

	protected void sendAddRegistration(ID receiver, RemoteServiceRegistrationImpl reg) {
		Trace.entering(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_ENTERING, this.getClass(), "sendAddRegistration", new Object[] {receiver, reg}); //$NON-NLS-1$
		try {
			sendSharedObjectMsgTo(receiver, SharedObjectMsg.createMsg(null, ADD_REGISTRATION, getLocalContainerID(), reg));
		} catch (final IOException e) {
			log(ADD_REGISTRATION_ERROR_CODE, ADD_REGISTRATION_ERROR_MESSAGE, e);
		}
		Trace.exiting(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_EXITING, this.getClass(), "sendAddRegistration"); //$NON-NLS-1$
	}

	protected void handleAddRegistration(ID remoteContainerID, final RemoteServiceRegistrationImpl registration) {
		Trace.entering(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_ENTERING, this.getClass(), ADD_REGISTRATION, new Object[] {remoteContainerID, registration});
		if (remoteContainerID == null || getLocalContainerID().equals(remoteContainerID)) {
			return;
		}
		synchronized (remoteRegistrys) {
			// Find registry for remoteContainer
			RemoteServiceRegistryImpl registry = getRemoteRegistry(remoteContainerID);
			// If there's not one already then lazily make one and add it
			if (registry == null) {
				registry = new RemoteServiceRegistryImpl(remoteContainerID);
				addRemoteRegistry(registry);
			}
			// publish service in this registry. At this point it's ready to go
			registry.publishService(registration);
			localRegisterService(registration);
			// notify IRemoteServiceListeners synchronously
			fireRemoteServiceListeners(createRegisteredEvent(registration));
		}
		Trace.exiting(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_EXITING, this.getClass(), ADD_REGISTRATION);
	}

	private void localRegisterService(RemoteServiceRegistrationImpl registration) {
		final Object localServiceRegistrationValue = registration.getProperty(Constants.LOCAL_SERVICE_REGISTRATION);
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
			properties.put(Constants.SERVICE_REGISTRATION_CONTAINER_ID, remoteContainerID.getName());
			properties.put(Constants.REMOTE_SERVICE, remoteServiceImpl);
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

	protected long sendCallRequest(RemoteServiceRegistrationImpl remoteRegistration, final IRemoteCall call) throws IOException {
		Trace.entering(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_ENTERING, this.getClass(), "sendCallRequest", new Object[] {remoteRegistration, call}); //$NON-NLS-1$
		final Request request = createRequest(remoteRegistration, call, null);
		addRequest(request);
		try {
			sendSharedObjectMsgTo(remoteRegistration.getContainerID(), SharedObjectMsg.createMsg(CALL_REQUEST, request));
		} catch (final IOException e) {
			removeRequest(request);
			throw e;
		}
		final long requestId = request.getRequestId();
		Trace.exiting(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_EXITING, this.getClass(), "sendCallRequest", new Long(requestId)); //$NON-NLS-1$
		return requestId;
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
		}
		Trace.exiting(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_EXITING, this.getClass(), "sendCallResponse"); //$NON-NLS-1$
	}

	protected void handleCallResponse(Response response) {
		Trace.entering(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_ENTERING, this.getClass(), CALL_RESPONSE, new Object[] {response});
		final Request request = findRequestForId(response.getRequestId());
		if (request == null) {
			log(REQUEST_NOT_FOUND_ERROR_CODE, REQUEST_NOT_FOUND_ERROR_MESSAGE, new NullPointerException());
			return;
		}
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
		synchronized (remoteRegistrys) {
			// get registry for given containerID
			final RemoteServiceRegistryImpl serviceRegistry = (RemoteServiceRegistryImpl) remoteRegistrys.get(containerID);
			if (serviceRegistry != null) {
				final RemoteServiceRegistrationImpl registration = serviceRegistry.findRegistrationForServiceId(serviceId.longValue());
				if (registration != null) {
					serviceRegistry.unpublishService(registration);
					unregisterServiceRegistrationsForContainer(registration.getContainerID());
					fireRemoteServiceListeners(createUnregisteredEvent(registration));
				}
			}
		}
		Trace.exiting(Activator.PLUGIN_ID, IRemoteServiceProviderDebugOptions.METHODS_EXITING, this.getClass(), "handleUnregister"); //$NON-NLS-1$
	}

	protected IRemoteServiceUnregisteredEvent createUnregisteredEvent(final RemoteServiceRegistrationImpl registration) {
		return new IRemoteServiceUnregisteredEvent() {

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
				final StringBuffer buf = new StringBuffer("RemoteServiceUnregisteredEvent["); //$NON-NLS-1$
				buf.append("containerID=").append(registration.getContainerID()); //$NON-NLS-1$
				buf.append(";clazzes=").append(Arrays.asList(registration.getClasses())); //$NON-NLS-1$
				buf.append(";reference=").append(registration.getReference()).append("]"); //$NON-NLS-1$ //$NON-NLS-2$
				return buf.toString();
			}
		};
	}

	protected IRemoteServiceRegisteredEvent createRegisteredEvent(final RemoteServiceRegistrationImpl registration) {
		return new IRemoteServiceRegisteredEvent() {

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
				buf.append("containerID=").append(registration.getContainerID()); //$NON-NLS-1$
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

	protected List requests = Collections.synchronizedList(new ArrayList());

	protected boolean addRequest(Request request) {
		return requests.add(request);
	}

	protected Request findRequestForId(long requestId) {
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

	protected boolean removeRequest(Request request) {
		return requests.remove(request);
	}

	protected boolean handleSharedObjectMsg(SharedObjectMsg msg) {
		try {
			msg.invoke(this);
		} catch (final Exception e) {
			log(MSG_INVOKE_ERROR_CODE, MSG_INVOKE_ERROR_MESSAGE, e);
		}
		return false;
	}

}