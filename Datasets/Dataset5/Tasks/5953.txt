private static final String XMPP_ROOM_PROTOCOL = "xmpp.muc";

package org.eclipse.ecf.provider.xmpp.identity;

import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDInstantiationException;
import org.eclipse.ecf.core.identity.Namespace;

public class XMPPRoomNamespace extends Namespace {

	private static final long serialVersionUID = 4348545761410397583L;
	private static final String XMPP_ROOM_PROTOCOL = "xmpp.room";
	
	public ID makeInstance(Class[] argTypes, Object[] args)
			throws IDInstantiationException {
		try {
			if (args.length == 5) {
				return new XMPPRoomID(this, (String) args[0], (String) args[1],
						(String) args[2], (String) args[3], (String) args[4]);
			}
			throw new IllegalArgumentException(
					"XMPPRoomID constructor arguments invalid");
		} catch (Exception e) {
			throw new IDInstantiationException("XMPP ID creation exception", e);
		}
	}

	public String getScheme() {
		return XMPP_ROOM_PROTOCOL;
	}
}