throw new IDCreateException(Messages.DnsSdNamespace_Wrong_Parameters);

/*******************************************************************************
 * Copyright (c) 2009 Markus Alexander Kuppe.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     Markus Alexander Kuppe (ecf-dev_eclipse.org <at> lemmster <dot> de) - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.provider.dnssd;

import java.net.URI;

import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDCreateException;
import org.eclipse.ecf.core.identity.Namespace;
import org.eclipse.ecf.discovery.identity.IServiceTypeID;

public class DnsSdNamespace extends Namespace {

	private static final long serialVersionUID = 7902507535188221743L;

	public static final String SCHEME = "dnssd"; //$NON-NLS-1$
	public static final String NAME = "ecf.namespace.dnssd"; //$NON-NLS-1$

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.core.identity.Namespace#createInstance(java.lang.Object[])
	 */
	public ID createInstance(Object[] parameters) throws IDCreateException {
		if(parameters != null && parameters.length == 1 && parameters[0] instanceof String) {
			String str = (String) parameters[0];
			return new DnsSdServiceTypeID(this, str);
		} else if (parameters != null && parameters.length == 1 && parameters[0] instanceof IServiceTypeID) {
			IServiceTypeID serviceTypeID = (IServiceTypeID) parameters[0];
			return new DnsSdServiceTypeID(this, serviceTypeID);
		} else if (parameters != null && parameters.length == 2 && parameters[0] instanceof IServiceTypeID && parameters[1] instanceof URI) {
			IServiceTypeID serviceTypeID = (IServiceTypeID) parameters[0];
			URI uri = (URI) parameters[1];
			return new DnsSdServiceID(this, new DnsSdServiceTypeID(this, serviceTypeID), uri);
		} else {
			throw new IDCreateException("Wrong parameters");
		}
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.core.identity.Namespace#getScheme()
	 */
	public String getScheme() {
		return SCHEME;
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.core.identity.Namespace#getSupportedParameterTypes()
	 */
	public Class[][] getSupportedParameterTypes() {
		return new Class[][] {{String.class}, {IServiceTypeID.class}, {IServiceTypeID.class, URI.class}};
	}
}