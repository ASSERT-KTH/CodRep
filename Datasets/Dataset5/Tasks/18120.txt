IRemoteCallParameter val = (serializer == null) ? null : serializer.serializeParameter(uri, call, callable, defaultCallableParameters[i], p);

/*******************************************************************************
* Copyright (c) 2009 Composent, Inc. and others. All rights reserved. This
* program and the accompanying materials are made available under the terms of
* the Eclipse Public License v1.0 which accompanies this distribution, and is
* available at http://www.eclipse.org/legal/epl-v10.html
*
* Contributors:
*   Composent, Inc. - initial API and implementation
******************************************************************************/
package org.eclipse.ecf.remoteservice.client;

import java.io.NotSerializableException;
import java.lang.reflect.Method;
import java.util.*;
import org.eclipse.core.runtime.Assert;
import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.ecf.core.AbstractContainer;
import org.eclipse.ecf.core.ContainerConnectException;
import org.eclipse.ecf.core.events.*;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.Namespace;
import org.eclipse.ecf.core.jobs.JobsExecutor;
import org.eclipse.ecf.core.security.IConnectContext;
import org.eclipse.ecf.remoteservice.*;
import org.eclipse.ecf.remoteservice.events.*;
import org.eclipse.ecf.remoteservice.util.RemoteFilterImpl;
import org.eclipse.equinox.concurrent.future.*;
import org.osgi.framework.InvalidSyntaxException;

/**
 * @since 3.3
 */
public abstract class AbstractRemoteServiceClientContainer extends AbstractContainer implements IRemoteServiceClientContainerAdapter {

	protected ID containerID;
	// The ID we've been assigned to connect to
	protected ID connectedID;
	protected Object connectLock = new Object();

	protected IConnectContext connectContext;

	protected Object remoteResponseDeserializerLock = new Object();
	protected IRemoteResponseDeserializer remoteResponseDeserializer = null;

	protected Object parameterSerializerLock = new Object();
	protected IRemoteCallParameterSerializer parameterSerializer = null;

	protected RemoteServiceClientRegistry registry;
	protected List remoteServiceListeners = new ArrayList();

	private List referencesInUse = new ArrayList();

	public AbstractRemoteServiceClientContainer(ID containerID) {
		this.containerID = containerID;
		Assert.isNotNull(this.containerID);
		this.registry = new RemoteServiceClientRegistry(this);
	}

	public void setConnectContextForAuthentication(IConnectContext connectContext) {
		this.connectContext = connectContext;
	}

	public IConnectContext getConnectContextForAuthentication() {
		return connectContext;
	}

	public void setResponseDeserializer(IRemoteResponseDeserializer resource) {
		synchronized (remoteResponseDeserializerLock) {
			this.remoteResponseDeserializer = resource;
		}
	}

	public IRemoteResponseDeserializer getResponseDeserializer() {
		synchronized (remoteResponseDeserializerLock) {
			return this.remoteResponseDeserializer;
		}
	}

	public void setParameterSerializer(IRemoteCallParameterSerializer serializer) {
		synchronized (parameterSerializerLock) {
			this.parameterSerializer = serializer;
		}
	}

	protected IRemoteCallParameterSerializer getParameterSerializer() {
		synchronized (parameterSerializerLock) {
			return this.parameterSerializer;
		}
	}

	protected IRemoteResponseDeserializer getResponseDeserializer(IRemoteCall call, IRemoteCallable callable, Map responseHeaders) {
		synchronized (remoteResponseDeserializerLock) {
			return remoteResponseDeserializer;
		}
	}

	protected IRemoteCallParameterSerializer getParameterSerializer(IRemoteCallParameter parameter, Object value) {
		synchronized (parameterSerializerLock) {
			return parameterSerializer;
		}
	}

	public void addRemoteServiceListener(IRemoteServiceListener listener) {
		remoteServiceListeners.add(listener);
	}

	public IFuture asyncGetRemoteServiceReferences(final ID[] idFilter, final String clazz, final String filter) {
		IExecutor executor = new JobsExecutor("asyncGetRemoteServiceReferences"); //$NON-NLS-1$
		return executor.execute(new IProgressRunnable() {
			public Object run(IProgressMonitor monitor) throws Exception {
				return getRemoteServiceReferences(idFilter, clazz, filter);
			}
		}, null);
	}

	public IFuture asyncGetRemoteServiceReferences(final ID target, final String clazz, final String filter) {
		IExecutor executor = new JobsExecutor("asyncGetRemoteServiceReferences"); //$NON-NLS-1$
		return executor.execute(new IProgressRunnable() {
			public Object run(IProgressMonitor monitor) throws Exception {
				return getRemoteServiceReferences(target, clazz, filter);
			}
		}, null);
	}

	public IRemoteFilter createRemoteFilter(String filter) throws InvalidSyntaxException {
		return new RemoteFilterImpl(filter);
	}

	public IRemoteServiceReference[] getAllRemoteServiceReferences(String clazz, String filter) throws InvalidSyntaxException {
		return registry.getAllRemoteServiceReferences(clazz, (filter == null) ? null : createRemoteFilter(filter));
	}

	public IRemoteService getRemoteService(IRemoteServiceReference reference) {
		if (reference == null || !(reference instanceof RemoteServiceClientReference))
			return null;
		RemoteServiceClientRegistration registration = registry.findServiceRegistration((RemoteServiceClientReference) reference);
		if (registration == null)
			return null;
		IRemoteService result = (registration == null) ? null : createRemoteService(registration);
		if (result != null)
			referencesInUse.add(reference);
		return result;
	}

	public IRemoteServiceID getRemoteServiceID(ID containerID1, long containerRelativeID) {
		return registry.getRemoteServiceID(containerID1, containerRelativeID);
	}

	public Namespace getRemoteServiceNamespace() {
		return getConnectNamespace();
	}

	public IRemoteServiceReference getRemoteServiceReference(IRemoteServiceID serviceID) {
		return registry.findServiceReference(serviceID);
	}

	public IRemoteServiceReference[] getRemoteServiceReferences(ID[] idFilter, String clazz, String filter) throws InvalidSyntaxException {
		return registry.getRemoteServiceReferences(idFilter, clazz, (filter == null) ? null : createRemoteFilter(filter));
	}

	public IRemoteServiceReference[] getRemoteServiceReferences(ID target, String clazz, String filter) throws InvalidSyntaxException, ContainerConnectException {
		return registry.getRemoteServiceReferences(target, clazz, (filter == null) ? null : createRemoteFilter(filter));
	}

	public IRemoteServiceRegistration registerRemoteService(final String[] clazzes, Object service, Dictionary properties) {
		if (service instanceof List) {
			return registerRemoteCallables(clazzes, (List) service, properties);
		} else if (service instanceof IRemoteCallable[][]) {
			return registerCallables(clazzes, (IRemoteCallable[][]) service, properties);
		}
		throw new RuntimeException("registerRemoteService cannot be used with rest client container"); //$NON-NLS-1$
	}

	public void removeRemoteServiceListener(IRemoteServiceListener listener) {
		remoteServiceListeners.remove(listener);
	}

	public boolean ungetRemoteService(final IRemoteServiceReference reference) {
		boolean result = referencesInUse.contains(reference);
		referencesInUse.remove(reference);
		fireRemoteServiceEvent(new IRemoteServiceUnregisteredEvent() {

			public IRemoteServiceReference getReference() {
				return reference;
			}

			public ID getLocalContainerID() {
				return getID();
			}

			public ID getContainerID() {
				return getID();
			}

			public String[] getClazzes() {
				return registry.getClazzes(reference);
			}
		});
		return result;
	}

	// Implementation of IRestClientContainerAdapter
	public IRemoteServiceRegistration registerCallables(IRemoteCallable[] restCallables, Dictionary properties) {
		Assert.isNotNull(restCallables);
		final RemoteServiceClientRegistration registration = createRestServiceRegistration(restCallables, properties);
		// notify
		fireRemoteServiceEvent(new IRemoteServiceRegisteredEvent() {

			public IRemoteServiceReference getReference() {
				return registration.getReference();
			}

			public ID getLocalContainerID() {
				return registration.getContainerID();
			}

			public ID getContainerID() {
				return getID();
			}

			public String[] getClazzes() {
				return registration.getClazzes();
			}
		});
		this.registry.registerRegistration(registration);
		return registration;
	}

	public IRemoteServiceRegistration registerCallables(String[] clazzes, IRemoteCallable[][] restCallables, Dictionary properties) {
		final RemoteServiceClientRegistration registration = createRestServiceRegistration(clazzes, restCallables, properties);
		// notify
		fireRemoteServiceEvent(new IRemoteServiceRegisteredEvent() {

			public IRemoteServiceReference getReference() {
				return registration.getReference();
			}

			public ID getLocalContainerID() {
				return registration.getContainerID();
			}

			public ID getContainerID() {
				return getID();
			}

			public String[] getClazzes() {
				return registration.getClazzes();
			}
		});
		this.registry.registerRegistration(registration);
		return registration;
	}

	public IRemoteServiceRegistration registerRemoteCallables(Class[] clazzes, List callables, Dictionary properties) {
		Assert.isNotNull(clazzes);
		IRemoteCallable[][] restCallables = createCallablesFromClasses(clazzes, callables);
		Assert.isNotNull(restCallables);
		Assert.isTrue(restCallables.length > 0);
		final String[] classNames = new String[clazzes.length];
		for (int i = 0; i < clazzes.length; i++) {
			classNames[i] = clazzes[i].getName();
		}
		return registerCallables(classNames, restCallables, properties);
	}

	public IRemoteServiceRegistration registerRemoteCallables(String[] clazzes, List callables, Dictionary properties) {
		Assert.isNotNull(clazzes);
		Assert.isNotNull(callables);
		return registerRemoteCallables(getClazzesFromStrings(clazzes), callables, properties);
	}

	public IRemoteCallable[][] createCallablesFromClasses(Class[] cls, List callables) {
		Assert.isNotNull(cls);
		Assert.isTrue(cls.length > 0);
		// First create result list to hold IRestCallable[]...for each Class
		List results = new ArrayList();
		for (int i = 0; i < cls.length; i++) {
			Method[] methods = getMethodsForClass(cls[i]);
			IRemoteCallable[] methodCallables = getCallablesForMethods(methods, callables);
			if (methodCallables != null && methodCallables.length > 0)
				results.add(methodCallables);
		}
		return (IRemoteCallable[][]) results.toArray(new IRemoteCallable[][] {});
	}

	protected IRemoteCallable[] getCallablesForMethods(Method[] methods, List callables) {
		Assert.isNotNull(methods);
		Assert.isTrue(methods.length > 0);
		List results = new ArrayList();
		for (int i = 0; i < methods.length; i++) {
			IRemoteCallable callable = findCallableForName(methods[i].getName(), callables);
			if (callable != null)
				results.add(callable);
		}
		return (IRemoteCallable[]) results.toArray(new IRemoteCallable[] {});
	}

	protected IRemoteCallable findCallableForName(String fqMethodName, List callables) {
		if (callables == null || callables.isEmpty())
			return null;
		for (Iterator i = callables.iterator(); i.hasNext();) {
			IRemoteCallable callable = (IRemoteCallable) i.next();
			if (callable != null && fqMethodName.equals(callable.getMethod()))
				return callable;
		}
		return null;
	}

	private Method[] getMethodsForClass(Class class1) {
		Method[] results = null;
		try {
			results = class1.getDeclaredMethods();
		} catch (Exception e) {
			logException("Could not get declared methods for class=" + class1.getName(), e); //$NON-NLS-1$
			return null;
		}
		return results;
	}

	public Class[] getClazzesFromStrings(String[] clazzes) throws IllegalArgumentException {
		List results = new ArrayList();
		for (int i = 0; i < clazzes.length; i++) {
			Class clazz = getClazzFromString(clazzes[i]);
			if (clazz != null)
				results.add(clazz);
		}
		return (Class[]) results.toArray(new Class[] {});
	}

	public Class getClazzFromString(String className) throws IllegalArgumentException {
		Class result = null;
		try {
			result = Class.forName(className, true, this.getClass().getClassLoader());
		} catch (Exception e) {
			String errorMsg = "ClassNotFoundException for class with name=" + className; //$NON-NLS-1$
			logException(errorMsg, e);
			throw new IllegalArgumentException(errorMsg);
		} catch (NoClassDefFoundError e) {
			String errorMsg = "NoClassDefFoundError for class with name=" + className; //$NON-NLS-1$
			logException(errorMsg, e);
			throw new IllegalArgumentException(errorMsg);
		}
		return result;
	}

	// IContainer implementation methods
	public void connect(ID targetID, IConnectContext connectContext1) throws ContainerConnectException {
		if (targetID == null)
			throw new ContainerConnectException("targetID cannot be null"); //$NON-NLS-1$
		Namespace targetNamespace = targetID.getNamespace();
		Namespace connectNamespace = getConnectNamespace();
		if (connectNamespace == null)
			throw new ContainerConnectException("targetID namespace cannot be null"); //$NON-NLS-1$
		if (!(targetNamespace.getName().equals(connectNamespace.getName())))
			throw new ContainerConnectException("targetID of incorrect type"); //$NON-NLS-1$
		fireContainerEvent(new ContainerConnectingEvent(containerID, targetID));
		synchronized (connectLock) {
			if (connectedID == null) {
				connectedID = targetID;
				this.connectContext = connectContext1;
			} else if (!connectedID.equals(targetID))
				throw new ContainerConnectException("Already connected to " + connectedID.getName()); //$NON-NLS-1$
		}
		fireContainerEvent(new ContainerConnectedEvent(containerID, targetID));
	}

	public void disconnect() {
		ID oldId = connectedID;
		fireContainerEvent(new ContainerDisconnectingEvent(containerID, oldId));
		synchronized (connectLock) {
			connectedID = null;
			connectContext = null;
		}
		fireContainerEvent(new ContainerDisconnectedEvent(containerID, oldId));
	}

	public ID getConnectedID() {
		synchronized (connectLock) {
			return connectedID;
		}
	}

	public ID getID() {
		return containerID;
	}

	public void dispose() {
		disconnect();
		remoteServiceListeners.clear();
		super.dispose();
	}

	void fireRemoteServiceEvent(IRemoteServiceEvent event) {
		List toNotify = null;
		// Copy array
		synchronized (remoteServiceListeners) {
			toNotify = new ArrayList(remoteServiceListeners);
		}
		for (Iterator i = toNotify.iterator(); i.hasNext();) {
			((IRemoteServiceListener) i.next()).handleServiceEvent(event);
		}
	}

	protected RemoteServiceClientRegistration createRestServiceRegistration(String[] clazzes, IRemoteCallable[][] callables, Dictionary properties) {
		return new RemoteServiceClientRegistration(getRemoteServiceNamespace(), clazzes, callables, properties, registry);
	}

	protected RemoteServiceClientRegistration createRestServiceRegistration(IRemoteCallable[] callables, Dictionary properties) {
		return new RemoteServiceClientRegistration(getRemoteServiceNamespace(), callables, properties, registry);
	}

	protected void logException(String string, Throwable e) {
		// XXX log properly
		if (string != null)
			System.out.println(string);
		if (e != null)
			e.printStackTrace();
	}

	protected ID getRemoteCallTargetID() {
		// First synchronize on connect lock
		synchronized (connectLock) {
			ID cID = getConnectedID();
			return (cID == null) ? getID() : cID;
		}
	}

	protected IRemoteCallParameter[] prepareParametersForRequest(String uri, IRemoteCall call, IRemoteCallable callable) throws NotSerializableException {
		List results = new ArrayList();
		Object[] callParameters = call.getParameters();
		IRemoteCallParameter[] defaultCallableParameters = callable.getDefaultParameters();
		if (callParameters == null)
			return defaultCallableParameters;
		for (int i = 0; i < callParameters.length; i++) {
			Object p = callParameters[i];
			// If the parameter is already a rest parameter just add
			if (p instanceof IRemoteCallParameter) {
				results.add(p);
				continue;
			}
			String name = null;
			if (defaultCallableParameters != null && i < defaultCallableParameters.length) {
				// If the call parameter (p) is null, then add the associated
				// callableParameter
				if (p == null)
					results.add(defaultCallableParameters[i]);
				// If not null, then we need to serialize
				name = defaultCallableParameters[i].getName();
				// Get parameter serializer...and
				IRemoteCallParameterSerializer serializer = getParameterSerializer();
				String val = (serializer == null) ? null : serializer.serializeParameter(uri, call, callable, p, defaultCallableParameters[i]);
				if (val != null)
					results.add(new RemoteCallParameter(name, val));
			}
		}
		return (IRemoteCallParameter[]) results.toArray(new IRemoteCallParameter[] {});
	}

	protected Object processResponse(String uri, IRemoteCall call, IRemoteCallable callable, Map responseHeaders, String responseBody) throws NotSerializableException {
		IRemoteResponseDeserializer deserializer = getResponseDeserializer();
		return (deserializer == null) ? null : deserializer.deserializeResponse(uri, call, callable, responseHeaders, responseBody);
	}

	protected abstract IRemoteService createRemoteService(RemoteServiceClientRegistration registration);

	protected abstract String prepareURIForRequest(IRemoteCall call, IRemoteCallable callable);

}