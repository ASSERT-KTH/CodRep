StringBuffer sb = new StringBuffer("XmlRpcId["); //$NON-NLS-1$

/*******************************************************************************
 * Copyright (c) 2009-2010 Naumen. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors: Pavel Samolisov - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.remoteservice.rpc.identity;

import java.net.URI;
import org.eclipse.ecf.core.identity.Namespace;
import org.eclipse.ecf.core.identity.URIID;

public class RPCID extends URIID {

	private static final long serialVersionUID = -713344242499901489L;

	public RPCID(Namespace namespace, URI uri) {
		super(namespace, uri);
	}

	public String toString() {
		StringBuffer sb = new StringBuffer("XMLRPCID["); //$NON-NLS-1$
		sb.append(getName()).append("]"); //$NON-NLS-1$
		return sb.toString();
	}
}