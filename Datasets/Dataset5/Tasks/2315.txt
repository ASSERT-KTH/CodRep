protected JMDNSServiceTypeID(final Namespace namespace, final String type) {

/*******************************************************************************
 * Copyright (c) 2007 Versant Corp.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     Markus Kuppe (mkuppe <at> versant <dot> com) - initial API and implementation
 ******************************************************************************/

package org.eclipse.ecf.provider.jmdns.identity;

import org.eclipse.ecf.core.identity.Namespace;
import org.eclipse.ecf.discovery.identity.ServiceTypeID;

/**
 * 
 */
public class JMDNSServiceTypeID extends ServiceTypeID {

	private static final long serialVersionUID = 7549266915001431139L;

	protected JMDNSServiceTypeID(Namespace namespace, String type) {
		super(namespace, type);
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.discovery.identity.ServiceTypeID#getInternal()
	 */
	public String getInternal() {
		final StringBuffer buf = new StringBuffer();
		//services
		buf.append("_"); //$NON-NLS-1$
		for (int i = 0; i < services.length; i++) {
			buf.append(services[i]);
			buf.append(DELIM);
		}

		buf.append(protocols[0]);
		buf.append("."); //$NON-NLS-1$

		buf.append(scopes[0]);
		buf.append("."); //$NON-NLS-1$

		return buf.toString();
	}
}