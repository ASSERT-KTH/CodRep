package org.eclipse.ecf.provider.xmpp.identity;

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
package org.eclipse.ecf.internal.provider.xmpp.identity;

import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDCreateException;
import org.eclipse.ecf.core.identity.Namespace;

public class XMPPNamespace extends Namespace {

	private static final long serialVersionUID = 3257569499003041590L;

	private static final String XMPP_PROTOCOL = "xmpp";
	
	public ID createInstance(Object[] args)
			throws IDCreateException {
		try {
			return new XMPPID(this, (String) args[0]);
		} catch (Exception e) {
			throw new IDCreateException("XMPP ID creation exception", e);
		}
	}

	public String getScheme() {
		return XMPP_PROTOCOL;
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.core.identity.Namespace#getSupportedParameterTypesForCreateInstance()
	 */
	public Class[][] getSupportedParameterTypes() {
		return new Class[][] { { String.class } };
	}
}