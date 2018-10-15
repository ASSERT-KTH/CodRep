public IFuture callAsynch(IRemoteCall call) {

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
import java.lang.reflect.Proxy;
import org.eclipse.ecf.core.util.*;
import org.eclipse.ecf.internal.provider.remoteservice.Messages;
import org.eclipse.ecf.remoteservice.*;
import org.eclipse.ecf.remoteservice.events.IRemoteCallCompleteEvent;
import org.eclipse.ecf.remoteservice.events.IRemoteCallEvent;

public class RemoteServiceImpl implements IRemoteService, InvocationHandler {

	protected static final long DEFAULT_TIMEOUT = 30000;

	protected RemoteServiceRegistrationImpl registration = null;

	protected RegistrySharedObject sharedObject = null;

	public RemoteServiceImpl(RegistrySharedObject sharedObject, RemoteServiceRegistrationImpl registration) {
		this.sharedObject = sharedObject;
		this.registration = registration;
	}

	public void callAsynch(IRemoteCall call, IRemoteCallListener listener) {
		sharedObject.sendCallRequestWithListener(registration, call, listener);
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.remoteservice.IRemoteService#callAsynch(org.eclipse.ecf.remoteservice.IRemoteCall)
	 */
	public IFutureStatus callAsynch(IRemoteCall call) {
		final FutureStatus result = new FutureStatus();
		final IRemoteCallListener listener = new IRemoteCallListener() {
			public void handleEvent(IRemoteCallEvent event) {
				if (event instanceof IRemoteCallCompleteEvent) {
					IRemoteCallCompleteEvent cce = (IRemoteCallCompleteEvent) event;
					if (cce.hadException())
						result.setException(cce.getException());
					else
						result.set(cce.getResponse());
				}
			}
		};
		callAsynch(call, listener);
		return result;
	}

	public Object callSynch(IRemoteCall call) throws ECFException {
		return sharedObject.callSynch(registration, call);
	}

	public void fireAsynch(IRemoteCall call) throws ECFException {
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
		return this.callSynch(new IRemoteCall() {

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