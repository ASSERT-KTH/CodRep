public ID getRemoteContainerID();

package org.eclipse.ecf.remoteservice;

import org.eclipse.ecf.core.identity.ID;

public interface IRemoteServiceReference {
	public ID getRemoteID();
	public Object getProperty(String key);
	public String [] getPropertyKeys();
}