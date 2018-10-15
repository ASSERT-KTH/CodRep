JSLPServiceTypeID stid = new JSLPServiceTypeID(this, anURL, (String[]) parameters[1]);

/*******************************************************************************
 * Copyright (c) 2007 Versant Corp.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     Markus Kuppe
 ******************************************************************************/
package org.eclipse.ecf.provider.jslp.identity;

import ch.ethz.iks.slp.ServiceURL;
import org.eclipse.ecf.core.identity.*;
import org.eclipse.ecf.core.util.StringUtils;
import org.eclipse.ecf.discovery.identity.*;
import org.eclipse.ecf.internal.provider.jslp.Messages;

public class JSLPNamespace extends Namespace {
	private static final String JSLP_SCHEME = "jslp"; //$NON-NLS-1$

	private static final long serialVersionUID = -3041453162456476102L;

	public static final String NAME = "ecf.namespace.slp"; //$NON-NLS-1$

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.core.identity.Namespace#createInstance(java.lang.Object[])
	 */
	public ID createInstance(Object[] parameters) throws IDCreateException {
		if (parameters == null || parameters.length < 1 || parameters.length > 2) {
			throw new IDCreateException(Messages.JSLPNamespace_2);
		} else if (parameters[0] == null || parameters[0].equals("")) { //$NON-NLS-1$
			throw new IDCreateException(Messages.JSLPNamespace_3);
		} else if (parameters[0] instanceof ServiceURL) { // handles internal creation
			ServiceURL anURL = (ServiceURL) parameters[0];
			JSLPServiceTypeID stid = new JSLPServiceTypeID(this, anURL);
			return new JSLPServiceID(this, stid, anURL.getHost());
		} else if (parameters[0] instanceof JSLPServiceID) { // handles conversion call where conversion isn't necessary
			return (ID) parameters[0];
		} else if (parameters[0] instanceof IServiceID) {
			IServiceID anId = (IServiceID) parameters[0];
			return createInstance(new Object[] {anId.getServiceTypeID(), parameters[1]});
		} else if (parameters[0] instanceof IServiceTypeID) {
			IServiceTypeID stid = (IServiceTypeID) parameters[0];
			return createInstance(new Object[] {stid.getName(), parameters[1]});
		} else if (parameters[0] instanceof String) { // creates from either external or internal string
			String type = (String) parameters[0];
			IServiceTypeID stid = null;
			if (StringUtils.contains(type, "._")) { //$NON-NLS-1$ // converts external to internal
				ServiceTypeID aStid = new ServiceTypeID(this, type);
				stid = new JSLPServiceTypeID(this, aStid);
			} else {
				stid = new JSLPServiceTypeID(this, type);
			}
			String name = null;
			if (parameters.length > 1) {
				try {
					name = (String) parameters[1];
				} catch (final ClassCastException e) {
					throw new IDCreateException(Messages.JSLPNamespace_4);
				}
			}
			return new JSLPServiceID(this, stid, name);
		} else {
			throw new IDCreateException(Messages.JSLPNamespace_3);
		}
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.core.identity.Namespace#getScheme()
	 */
	public String getScheme() {
		return JSLP_SCHEME;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.identity.Namespace#getSupportedParameterTypesForCreateInstance()
	 */
	public Class[][] getSupportedParameterTypes() {
		return new Class[][] { {String.class}, {String.class, String.class}, {ServiceURL.class}, {IServiceTypeID.class}, {IServiceID.class}};
	}
}