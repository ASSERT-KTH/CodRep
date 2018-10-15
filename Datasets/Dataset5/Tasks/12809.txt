public ID getContainerID() {

package org.eclipse.ecf.provider.remoteservice.generic;

import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.remoteservice.IRemoteServiceReference;

public class RemoteServiceReferenceImpl implements IRemoteServiceReference {

	protected RemoteServiceRegistrationImpl registration;
	protected String clazz = null;
	
	public RemoteServiceReferenceImpl(RemoteServiceRegistrationImpl registration) {
		this.registration = registration;
	}
	
	public Object getProperty(String key) {
		return registration.getProperty(key);
	}

	public String[] getPropertyKeys() {
		return registration.getPropertyKeys();
	}

	public ID getRemoteContainerID() {
		return registration.getContainerID();
	}

	protected RemoteServiceRegistrationImpl getRegistration() {
		return registration;
	}
	protected void setRemoteClass(String clazz) {
		this.clazz = clazz;
	}

	protected String getRemoteClass() {
		return clazz;
	}
}