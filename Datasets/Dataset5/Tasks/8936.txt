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
package org.eclipse.ecf.provider.jmdns.identity;

import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDCreateException;
import org.eclipse.ecf.core.identity.Namespace;

public class JMDNSNamespace extends Namespace {
	private static final long serialVersionUID = 1L;
	private static final String JMDNS_SCHEME = "jmdns";
	
	public ID createInstance(Class[] argTypes, Object[] args)
			throws IDCreateException {
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