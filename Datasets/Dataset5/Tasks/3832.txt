//props.put(IDiscoveryService.CONTAINER_NAME, "ecf.discovery.jmdns"); //$NON-NLS-1$

package org.eclipse.ecf.internal.provider.jmdns;

import java.net.InetAddress;
import java.util.Properties;
import org.eclipse.core.runtime.*;
import org.eclipse.ecf.core.IContainer;
import org.eclipse.ecf.core.start.IECFStart;
import org.eclipse.ecf.discovery.service.IDiscoveryService;
import org.eclipse.ecf.provider.jmdns.container.JMDNSDiscoveryContainer;

public class DiscoveryStart implements IECFStart {

	public DiscoveryStart() {
		// nothing to do
	}

	public IStatus run(IProgressMonitor monitor) {
		IDiscoveryService discovery = JMDNSPlugin.getDefault().getDiscoveryService();
		if (discovery == null) {
			try {
				IContainer discoveryContainer = new JMDNSDiscoveryContainer(InetAddress.getLocalHost());
				discoveryContainer.connect(null, null);
				Properties props = new Properties();
				props.put(IDiscoveryService.CONTAINER_ID, discoveryContainer.getID());
				props.put(IDiscoveryService.CONTAINER_NAME, "ecf.discovery.jmdns"); //$NON-NLS-1$
				JMDNSPlugin.getDefault().getContext().registerService(IDiscoveryService.class.getName(), discoveryContainer, props);
			} catch (Exception e) {
				e.printStackTrace();
				return new Status(IStatus.WARNING, JMDNSPlugin.PLUGIN_ID, IStatus.WARNING, Messages.ECFStart_WARNING_COULD_NOT_REGISTER_DISCOVERY, e);
			}
		}
		return Status.OK_STATUS;
	}

}