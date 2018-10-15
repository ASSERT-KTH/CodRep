protected static final long DEFAULT_TIMEOUT = new Long(System.getProperty("ecf.remotecall.timeout", "30000")).longValue(); //$NON-NLS-1$ //$NON-NLS-2$

/*******************************************************************************
  * Copyright (c) 2004 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.provider.remoteservice.generic;

import java.lang.reflect.*;
import java.util.Arrays;
import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.ecf.core.jobs.JobsExecutor;
import org.eclipse.ecf.core.util.ECFException;
import org.eclipse.ecf.internal.provider.remoteservice.Messages;
import org.eclipse.ecf.remoteservice.*;
import org.eclipse.equinox.concurrent.future.IFuture;
import org.eclipse.equinox.concurrent.future.IProgressRunnable;
import org.eclipse.osgi.util.NLS;

public class RemoteServiceImpl implements IRemoteService, InvocationHandler {

	protected static final long DEFAULT_TIMEOUT = 30000;

	protected RemoteServiceRegistrationImpl registration = null;

	protected RegistrySharedObject sharedObject = null;

	public RemoteServiceImpl(RegistrySharedObject sharedObject, RemoteServiceRegistrationImpl registration) {
		this.sharedObject = sharedObject;
		this.registration = registration;
	}

	/**
	 * @since 3.0
	 * @see org.eclipse.ecf.remoteservice.IRemoteService#callAsync(org.eclipse.ecf.remoteservice.IRemoteCall, org.eclipse.ecf.remoteservice.IRemoteCallListener)
	 */
	public void callAsync(IRemoteCall call, IRemoteCallListener listener) {
		sharedObject.sendCallRequestWithListener(registration, call, listener);
	}

	/**
	 * @since 3.0
	 * @see org.eclipse.ecf.remoteservice.IRemoteService#callAsync(org.eclipse.ecf.remoteservice.IRemoteCall)
	 */
	public IFuture callAsync(final IRemoteCall call) {
		JobsExecutor executor = new JobsExecutor(NLS.bind("callAsynch({0}", call.getMethod())); //$NON-NLS-1$
		return executor.execute(new IProgressRunnable() {
			public Object run(IProgressMonitor monitor) throws Exception {
				return callSync(call);
			}
		}, null);
	}

	/**
	 * @since 3.0
	 * @see org.eclipse.ecf.remoteservice.IRemoteService#callSync(org.eclipse.ecf.remoteservice.IRemoteCall)
	 */
	public Object callSync(IRemoteCall call) throws ECFException {
		return sharedObject.callSynch(registration, call);
	}

	/**
	 * @since 3.0
	 * @see org.eclipse.ecf.remoteservice.IRemoteService#fireAsync(org.eclipse.ecf.remoteservice.IRemoteCall)
	 */
	public void fireAsync(IRemoteCall call) throws ECFException {
		sharedObject.sendFireRequest(registration, call);
	}

	public Object getProxy() throws ECFException {
		Object proxy;
		try {
			// Get clazz from reference
			final String[] clazzes = registration.getClasses();
			final Class[] cs = new Class[clazzes.length];
			for (int i = 0; i < clazzes.length; i++)
				cs[i] = Class.forName(clazzes[i]);
			proxy = Proxy.newProxyInstance(this.getClass().getClassLoader(), cs, this);
		} catch (final Exception e) {
			throw new ECFException(Messages.RemoteServiceImpl_EXCEPTION_CREATING_PROXY, e);
		}
		return proxy;
	}

	public Object invoke(Object proxy, final Method method, final Object[] args) throws Throwable {
		// methods declared by Object
		if (method.getName().equals("toString")) { //$NON-NLS-1$
			final String[] clazzes = registration.getClasses();
			String proxyClass = (clazzes.length == 1) ? clazzes[0] : Arrays.asList(clazzes).toString();
			return proxyClass + ".proxy@" + registration.getID(); //$NON-NLS-1$
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
		}
		return this.callSync(new IRemoteCall() {

			public String getMethod() {
				return method.getName();
			}

			public Object[] getParameters() {
				return args;
			}

			public long getTimeout() {
				return DEFAULT_TIMEOUT;
			}
		});
	}

}