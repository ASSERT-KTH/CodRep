sharedObject.sendCallRequestWithListener(registration, call, listener);

package org.eclipse.ecf.provider.remoteservice.generic;

import java.io.IOException;
import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Method;
import java.lang.reflect.Proxy;

import org.eclipse.ecf.core.util.ECFException;
import org.eclipse.ecf.remoteservice.IRemoteCall;
import org.eclipse.ecf.remoteservice.IRemoteCallListener;
import org.eclipse.ecf.remoteservice.IRemoteService;

public class RemoteServiceImpl implements IRemoteService, InvocationHandler {

	protected static final long DEFAULT_TIMEOUT = 30000;

	protected RemoteServiceRegistrationImpl registration = null;

	protected RegistrySharedObject sharedObject = null;

	public RemoteServiceImpl(RegistrySharedObject sharedObject,
			RemoteServiceRegistrationImpl registration) {
		this.sharedObject = sharedObject;
		this.registration = registration;
	}

	public void callAsynch(IRemoteCall call, IRemoteCallListener listener) {
		// TODO Auto-generated method stub
	}

	public Object callSynch(IRemoteCall call) throws ECFException {
		return sharedObject.fireCallAndWait(registration, call);
	}

	public void fireAsynch(IRemoteCall call) throws ECFException {
		try {
			sharedObject.sendFireRequest(registration, call);
		} catch (IOException e) {
			throw new ECFException("IOException sending remote request", e);
		}
	}

	public Object getProxy() throws ECFException {
		Object proxy;
		try {
			// Get clazz from reference
			RemoteServiceReferenceImpl reference = (RemoteServiceReferenceImpl) registration
					.getReference();
			String clazz = reference.getRemoteClass();
			Class loadedClass = Class.forName(clazz);
			proxy = Proxy.newProxyInstance(this.getClass().getClassLoader(),
					new Class[] { loadedClass }, this);
		} catch (Exception e) {
			throw new ECFException(
					"Exception creating proxy for remote service", e);
		}
		return proxy;
	}

	public Object invoke(Object proxy, final Method method, final Object[] args)
			throws Throwable {
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