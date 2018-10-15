public ID createInstance(Object[] parameters) {

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

import org.eclipse.ecf.core.identity.*;
import org.eclipse.ecf.internal.provider.jmdns.Messages;
import org.eclipse.osgi.util.NLS;

public class JMDNSNamespace extends Namespace {

	private static final long serialVersionUID = -7220857203720337921L;

	public static final String JMDNS_SCHEME = "jmdns"; //$NON-NLS-1$

	public static final String NAME = "ecf.namespace.jmdns"; //$NON-NLS-1$

	/**
	 * 
	 */
	public JMDNSNamespace() {
		super();
	}

	private String getInitFromExternalForm(Object[] args) {
		if (args == null || args.length < 1 || args[0] == null)
			return null;
		if (args[0] instanceof String) {
			String arg = (String) args[0];
			if (arg.startsWith(getScheme() + Namespace.SCHEME_SEPARATOR)) {
				int index = arg.indexOf(Namespace.SCHEME_SEPARATOR);
				if (index >= arg.length())
					return null;
				return arg.substring(index + 1);
			}
		}
		return null;
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.core.identity.Namespace#createInstance(java.lang.Object[])
	*/
	public ID createInstance(Object[] parameters) throws IDCreateException {
		String type = null;
		try {
			String init = getInitFromExternalForm(parameters);
			if (init != null)
				type = init;
			else {
				if (parameters == null || parameters.length < 1 || parameters.length > 2) {
					throw new IDCreateException(Messages.JMDNSNamespace_EXCEPTION_ID_WRONG_PARAM_COUNT);
				}
				if (parameters[0] instanceof JMDNSServiceTypeID) {
					type = ((JMDNSServiceTypeID) parameters[0]).getInternal();
				} else if (parameters[0] instanceof String) {
					type = (String) parameters[0];
				} else
					throw new IDCreateException(Messages.JMDNSNamespace_EXCEPTION_TYPE_PARAM_NOT_STRING);
			}
		} catch (Exception e) {
			throw new IDCreateException(NLS.bind("{0} createInstance()", getName()), e); //$NON-NLS-1$
		}
		final JMDNSServiceTypeID stid = new JMDNSServiceTypeID(this, type);

		String name = null;
		if (parameters.length > 1) {
			try {
				name = (String) parameters[1];
			} catch (final ClassCastException e) {
				throw new IDCreateException(Messages.JMDNSNamespace_EXCEPTION_ID_PARAM_2_WRONG_TYPE);
			}
		}
		return new JMDNSServiceID(this, stid, name);
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.core.identity.Namespace#getScheme()
	 */
	public String getScheme() {
		return JMDNS_SCHEME;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.identity.Namespace#getSupportedParameterTypesForCreateInstance()
	 */
	public Class[][] getSupportedParameterTypes() {
		return new Class[][] { {String.class}, {String.class, String.class}};
	}
}