import org.eclipse.ecf.discovery.identity.ServiceID;

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

import org.eclipse.ecf.core.identity.Namespace;
import org.eclipse.ecf.discovery.ServiceID;

public class JMDNSServiceID extends ServiceID {

	private static final String DELIMITER = ".";
	private static final long serialVersionUID = 1L;

	public JMDNSServiceID(Namespace namespace, String type, String name) {
		super(namespace, type, name);
	}

	protected String getFullyQualifiedName() {
		if (name == null)
			return type;
		else
			return name+DELIMITER+type;
	}

}