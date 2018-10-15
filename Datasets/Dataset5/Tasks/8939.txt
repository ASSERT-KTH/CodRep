public ID createInstance(Object[] args)

/****************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Composent, Inc. - initial API and implementation
 *****************************************************************************/
package org.eclipse.ecf.provider.xmpp.identity;

import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDCreateException;
import org.eclipse.ecf.core.identity.Namespace;

public class XMPPRoomNamespace extends Namespace {

	private static final long serialVersionUID = 4348545761410397583L;
	private static final String XMPP_ROOM_PROTOCOL = "xmpp.muc";
	
	public ID createInstance(Class[] argTypes, Object[] args)
			throws IDCreateException {
		try {
			if (args.length == 5) {
				return new XMPPRoomID(this, (String) args[0], (String) args[1],
						(String) args[2], (String) args[3], (String) args[4]);
			}
			throw new IllegalArgumentException(
					"XMPPRoomID constructor arguments invalid");
		} catch (Exception e) {
			throw new IDCreateException("XMPP ID creation exception", e);
		}
	}

	public String getScheme() {
		return XMPP_ROOM_PROTOCOL;
	}
}