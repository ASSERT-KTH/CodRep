public ID createInstance(Class[] argTypes, Object[] args)

package org.eclipse.ecf.provider.jmdns.identity;

import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDInstantiationException;
import org.eclipse.ecf.core.identity.Namespace;

public class JMDNSNamespace extends Namespace {
	private static final long serialVersionUID = 1L;
	private static final String JMDNS_SCHEME = "jmdns";
	
	public ID makeInstance(Class[] argTypes, Object[] args)
			throws IDInstantiationException {
		String type = (String) args[0];
		String name = null;
		if (args.length > 1) {
			name = (String) args[1];
		}
		return new JMDNSServiceID(this, type, name);
	}

	public String getScheme() {
		return JMDNS_SCHEME;
	}
}