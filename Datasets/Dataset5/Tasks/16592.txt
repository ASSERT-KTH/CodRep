public ID createInstance(Class[] argTypes, Object[] args)

package org.eclipse.ecf.provider.xmpp.identity;

import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDInstantiationException;
import org.eclipse.ecf.core.identity.Namespace;

public class XMPPSNamespace extends Namespace {

	private static final long serialVersionUID = 390139788867091795L;
	private static final String XMPP_PROTOCOL = "xmpps";
	
	public ID makeInstance(Class[] argTypes, Object[] args)
			throws IDInstantiationException {
		try {
			return new XMPPID(this, (String) args[0]);
		} catch (Exception e) {
			throw new IDInstantiationException("XMPP ID creation exception", e);
		}
	}

	public String getScheme() {
		return XMPP_PROTOCOL;
	}
}