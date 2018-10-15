public IContainer createInstance(

package org.eclipse.ecf.provider.xmpp.container;

import org.eclipse.ecf.core.ContainerDescription;
import org.eclipse.ecf.core.ContainerInstantiationException;
import org.eclipse.ecf.core.IContainer;

public class SecureContainerInstantiator extends ContainerInstantiator {
	public SecureContainerInstantiator() {
		super();
	}
    public IContainer makeInstance(
            ContainerDescription description, Class[] argTypes,
            Object[] args)
            throws ContainerInstantiationException {
        try {
            Integer ka = new Integer(XMPPSClientSOContainer.DEFAULT_KEEPALIVE);
            String name = null;
            if (args != null) {
                if (args.length > 0) {
                    name = (String) args[0];
                    if (args.length > 1) {
                        ka = getIntegerFromArg(argTypes[1], args[1]);
                    }
                }
            }
            if (name == null) {
                if (ka == null) {
                    return new XMPPSClientSOContainer();
                } else {
                    return new XMPPSClientSOContainer(ka.intValue());
                }
            } else {
                if (ka == null) {
                    ka = new Integer(XMPPSClientSOContainer.DEFAULT_KEEPALIVE);
                }
                return new XMPPSClientSOContainer(name,ka.intValue());                
            }
        } catch (Exception e) {
            throw new ContainerInstantiationException(
                    "Exception creating generic container", e);
        }
    }

}