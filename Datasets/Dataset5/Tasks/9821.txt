public Class[][] getSupportedParameterTypes() {

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

package org.eclipse.ecf.provider.irc.identity;

import java.net.URI;
import java.net.URISyntaxException;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDCreateException;

public class IRCNamespace extends org.eclipse.ecf.core.identity.Namespace {

	private static final long serialVersionUID = 1005111581522377553L;

	public static final String IRC_PROTOCOL = "irc";

	public ID createInstance(Object[] args) throws IDCreateException {
		URI newURI = null;
		String s = null;
		try {
			s = (String) args[0];
		} catch (ClassCastException e) {
			throw new IDCreateException("Cannot cast argument " + args[0]
					+ " to String");
		}
		try {
			newURI = new URI(s);
		} catch (URISyntaxException e) {
			throw new IDCreateException("Exception creating URI out of " + s);
		}
		String uriScheme = newURI.getScheme();
		if (uriScheme == null || !uriScheme.equalsIgnoreCase(getScheme())) {
			throw new IDCreateException(newURI
					+ " has invalid protocol.  URI must have protocol "
					+ IRC_PROTOCOL);
		}
		return new IRCID(this, newURI);
	}

	public String getScheme() {
		return IRC_PROTOCOL;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.identity.Namespace#getSupportedParameterTypesForCreateInstance()
	 */
	public Class[][] getSupportedParameterTypesForCreateInstance() {
		return new Class[][] { { String.class } };
	}
}