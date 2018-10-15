public class HostContainerSelector implements IHostContainerSelector {

package org.eclipse.ecf.osgi.services.remoteserviceadmin;

import org.eclipse.ecf.remoteservice.IRemoteServiceContainer;
import org.osgi.framework.ServiceReference;

public class DefaultHostContainerSelector implements IHostContainerSelector {

	public IRemoteServiceContainer[] selectHostContainers(
			ServiceReference serviceReference,
			String[] serviceExportedInterfaces,
			String[] serviceExportedConfigs, String[] serviceIntents) {
		// TODO Auto-generated method stub
		return null;
	}

}