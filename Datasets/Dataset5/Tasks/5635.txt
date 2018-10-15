return (registration != null);

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

	public ID getContainerID() {
		return registration.getContainerID();
	}

	public boolean isActive() {
		return (registration == null);
	}
	
	protected synchronized void setInactive() {
		registration = null;
		clazz = null;
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