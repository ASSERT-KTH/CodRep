throw new ECFException("Failed to load proxy interface class", e); //$NON-NLS-1$

/*******************************************************************************
* Copyright (c) 2010 Composent, Inc. and others. All rights reserved. This
* program and the accompanying materials are made available under the terms of
* the Eclipse Public License v1.0 which accompanies this distribution, and is
* available at http://www.eclipse.org/legal/epl-v10.html
*
* Contributors:
*   Composent, Inc. - initial API and implementation
******************************************************************************/
package org.eclipse.ecf.remoteservice;

import java.lang.reflect.*;
import java.util.*;
import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.ecf.core.jobs.JobsExecutor;
import org.eclipse.ecf.core.util.ECFException;
import org.eclipse.equinox.concurrent.future.IFuture;
import org.eclipse.equinox.concurrent.future.IProgressRunnable;
import org.eclipse.osgi.util.NLS;
import org.osgi.framework.ServiceException;

/**
 * Abstract remote service implementation.  Clients may subclass to avoid re-implementing 
 * methods from IRemoteService.
 * 
 * @since 4.1
 */
public abstract class AbstractRemoteService implements IRemoteService, InvocationHandler {

	protected static final Object[] EMPTY_ARGS = new Object[0];

	protected abstract String[] getInterfaceClassNames();

	protected abstract IRemoteServiceID getRemoteServiceID();

	protected abstract IRemoteServiceReference getRemoteServiceReference();

	protected Class loadInterfaceClass(String className) throws ClassNotFoundException {
		return Class.forName(className);
	}

	protected IRemoteService getRemoteService() {
		return this;
	}

	protected long getDefaultTimeout() {
		return IRemoteCall.DEFAULT_TIMEOUT;
	}

	public IFuture callAsync(final IRemoteCall call) {
		JobsExecutor executor = new JobsExecutor(NLS.bind("callAsynch({0}", call.getMethod())); //$NON-NLS-1$
		return executor.execute(new IProgressRunnable() {
			public Object run(IProgressMonitor monitor) throws Exception {
				return callSync(call);
			}
		}, null);
	}

	@SuppressWarnings("unchecked")
	public Object getProxy() throws ECFException {
		try {
			// Get clazz from reference
			final String[] clazzes = getInterfaceClassNames();
			List classes = new ArrayList();
			for (int i = 0; i < clazzes.length; i++) {
				Class c = loadInterfaceClass(clazzes[i]);
				classes.add(c);
				// check to see if async remote service proxy interface is defined
				Class asyncRemoteServiceProxyClass = findAsyncRemoteServiceProxyClass(c);
				if (asyncRemoteServiceProxyClass != null && asyncRemoteServiceProxyClass.isInterface())
					classes.add(asyncRemoteServiceProxyClass);
			}
			// add IRemoteServiceProxy interface to set of interfaces supported by this proxy
			classes.add(IRemoteServiceProxy.class);
			return createProxy((Class[]) classes.toArray(new Class[] {}));
		} catch (final Exception e) {
			throw new ECFException("Failed to create proxy", e); //$NON-NLS-1$
		} catch (final NoClassDefFoundError e) {
			throw new ECFException("Failed to load proxy interface", e); //$NON-NLS-1$
		}
	}

	protected Object createProxy(Class[] classes) {
		return Proxy.newProxyInstance(this.getClass().getClassLoader(), classes, this);
	}

	/**
	 * @since 3.3
	 */
	protected Class findAsyncRemoteServiceProxyClass(Class c) {
		try {
			return Class.forName(convertInterfaceNameToAsyncInterfaceName(c.getName()));
		} catch (Exception t) {
			return null;
		} catch (NoClassDefFoundError e) {
			return null;
		}
	}

	protected String convertInterfaceNameToAsyncInterfaceName(String interfaceName) {
		return interfaceName + IAsyncRemoteServiceProxy.ASYNC_INTERFACE_SUFFIX;
	}

	protected Object[] getCallParametersForProxyInvoke(String callMethod, Method proxyMethod, Object[] args) {
		return args == null ? EMPTY_ARGS : args;
	}

	protected long getCallTimeoutForProxyInvoke(String callMethod, Method proxyMethod, Object[] args) {
		return IRemoteCall.DEFAULT_TIMEOUT;
	}

	protected String getCallMethodNameForProxyInvoke(Method method, Object[] args) {
		return method.getName();
	}

	protected Object invokeObject(Object proxy, final Method method, final Object[] args) throws Throwable {
		if (method.getName().equals("toString")) { //$NON-NLS-1$
			final String[] clazzes = getInterfaceClassNames();
			String proxyClass = (clazzes.length == 1) ? clazzes[0] : Arrays.asList(clazzes).toString();
			return proxyClass + ".proxy@" + getRemoteServiceID(); //$NON-NLS-1$
		} else if (method.getName().equals("hashCode")) { //$NON-NLS-1$
			return new Integer(hashCode());
		} else if (method.getName().equals("equals")) { //$NON-NLS-1$
			if (args == null || args.length == 0)
				return Boolean.FALSE;
			try {
				return new Boolean(Proxy.getInvocationHandler(args[0]).equals(this));
			} catch (IllegalArgumentException e) {
				return Boolean.FALSE;
			}
			// This handles the use of IRemoteServiceProxy.getRemoteService method
		} else if (method.getName().equals("getRemoteService")) { //$NON-NLS-1$
			return getRemoteService();
		} else if (method.getName().equals("getRemoteServiceReference")) { //$NON-NLS-1$
			return getRemoteServiceReference();
		}
		return null;
	}

	protected Object invokeSync(IRemoteCall call) throws ECFException {
		return callSync(call);
	}

	public Object invoke(Object proxy, final Method method, final Object[] args) throws Throwable {
		// methods declared by Object
		try {
			// If the method is from Class Object, or from IRemoteServiceProxy
			// then return result
			Object resultObject = invokeObject(proxy, method, args);
			if (resultObject != null)
				return resultObject;
			// If the method's class is a subclass of IAsyncRemoteServiceProxy, then we assume
			// that the methods are intended to be invoked asynchronously
			if (Arrays.asList(method.getDeclaringClass().getInterfaces()).contains(IAsyncRemoteServiceProxy.class))
				return invokeAsync(method, args);
			// else call synchronously/block and return result
			final String callMethod = getCallMethodNameForProxyInvoke(method, args);
			final Object[] callParameters = getCallParametersForProxyInvoke(callMethod, method, args);
			final long callTimeout = getCallTimeoutForProxyInvoke(callMethod, method, args);
			final IRemoteCall remoteCall = new IRemoteCall() {
				public String getMethod() {
					return callMethod;
				}

				public Object[] getParameters() {
					return callParameters;
				}

				public long getTimeout() {
					return callTimeout;
				}
			};
			return invokeSync(remoteCall);
		} catch (Throwable t) {
			if (t instanceof ServiceException)
				throw t;
			// rethrow as service exception
			throw new ServiceException("Service exception on remote service proxy rsid=" + getRemoteServiceID(), ServiceException.REMOTE, t); //$NON-NLS-1$
		}
	}

	/**
	 * @since 3.3
	 */
	protected class AsyncArgs {
		private IRemoteCallListener listener;
		private Object[] args;

		public AsyncArgs(IRemoteCallListener listener, Object[] originalArgs) {
			this.listener = listener;
			if (this.listener != null) {
				int asynchArgsLength = originalArgs.length - 1;
				this.args = new Object[asynchArgsLength];
				System.arraycopy(originalArgs, 0, args, 0, asynchArgsLength);
			} else
				this.args = originalArgs;
		}

		public IRemoteCallListener getListener() {
			return listener;
		}

		public Object[] getArgs() {
			return args;
		}
	}

	/**
	 * @since 3.3
	 */
	protected Object invokeAsync(final Method method, final Object[] args) throws Throwable {
		final String invokeMethodName = getAsyncInvokeMethodName(method);
		final AsyncArgs asyncArgs = getAsyncArgs(method, args);
		IRemoteCallListener listener = asyncArgs.getListener();
		IRemoteCall call = new IRemoteCall() {
			public String getMethod() {
				return invokeMethodName;
			}

			public Object[] getParameters() {
				return asyncArgs.getArgs();
			}

			public long getTimeout() {
				return DEFAULT_TIMEOUT;
			}
		};
		if (listener == null)
			return callAsync(call);
		callAsync(call, listener);
		return null;
	}

	/**
	 * @since 3.3
	 */
	protected AsyncArgs getAsyncArgs(Method method, Object[] args) {
		IRemoteCallListener listener = null;
		Class returnType = method.getReturnType();
		// If the return type is declared to be *anything* except an IFuture, then 
		// we are expecting the last argument to be an IRemoteCallListener
		if (!returnType.equals(IFuture.class)) {
			// If the provided args do *not* include an IRemoteCallListener then we have a problem
			if (args == null || args.length == 0)
				throw new IllegalArgumentException("Async calls must include a IRemoteCallListener instance as the last argument"); //$NON-NLS-1$
			// Get the last arg
			Object lastArg = args[args.length - 1];
			// If it's an IRemoteCallListener implementer directly, then just cast and return
			if (lastArg instanceof IRemoteCallListener) {
				listener = (IRemoteCallListener) lastArg;
			}
			// If it's an implementation of IAsyncCallback, then create a new listener based upon 
			// callback and return
			if (lastArg instanceof IAsyncCallback) {
				listener = new CallbackRemoteCallListener((IAsyncCallback) lastArg);
			}
			// If the last are is not an instance of IRemoteCallListener then there is a problem
			if (listener == null)
				throw new IllegalArgumentException("Last argument must be an instance of IRemoteCallListener"); //$NON-NLS-1$
		}
		return new AsyncArgs(listener, args);
	}

	/**
	 * @since 3.3
	 */
	protected String getAsyncInvokeMethodName(Method method) {
		String methodName = method.getName();
		return methodName.endsWith(IAsyncRemoteServiceProxy.ASYNC_METHOD_SUFFIX) ? methodName.substring(0, methodName.length() - IAsyncRemoteServiceProxy.ASYNC_METHOD_SUFFIX.length()) : methodName;
	}

}