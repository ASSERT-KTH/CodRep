public IContainer createInstance(

package org.eclipse.ecf.provider.jmdns.container;

import java.io.IOException;

import org.eclipse.ecf.core.ContainerDescription;
import org.eclipse.ecf.core.ContainerInstantiationException;
import org.eclipse.ecf.core.IContainer;
import org.eclipse.ecf.core.identity.IDInstantiationException;
import org.eclipse.ecf.core.provider.IContainerInstantiator;

public class ContainerInstantiator implements
		IContainerInstantiator {

	public ContainerInstantiator() {
		super();
	}

	public IContainer makeInstance(
			ContainerDescription description, Class[] argTypes,
			Object[] args) throws ContainerInstantiationException {
			try {
				JMDNSDiscoveryContainer container = new JMDNSDiscoveryContainer();
				return container;
			} catch (IDInstantiationException e) {
				ContainerInstantiationException excep = new ContainerInstantiationException("Exception making JMDNS container");
				excep.setStackTrace(e.getStackTrace());
				throw excep;
			} catch (IOException e) {
				ContainerInstantiationException excep = new ContainerInstantiationException("Exception getting InetAddress for JMDNS container");
				excep.setStackTrace(e.getStackTrace());
				throw excep;
			}
	}

}