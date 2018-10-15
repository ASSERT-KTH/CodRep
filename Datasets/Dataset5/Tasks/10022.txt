public ID createInstance(Object[] parameters) {

/*******************************************************************************
 * Copyright (c) 2008 Versant Corp.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     Markus Kuppe (mkuppe <at> versant <dot> com) - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.internal.provider.discovery;

import org.eclipse.ecf.core.identity.*;
import org.eclipse.ecf.discovery.identity.IServiceTypeID;
import org.eclipse.ecf.discovery.identity.ServiceTypeID;

public class CompositeNamespace extends Namespace {

	private static final long serialVersionUID = -4774766051014928510L;
	public static final String NAME = "ecf.namespace.composite"; //$NON-NLS-1$

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.core.identity.Namespace#createInstance(java.lang.Object[])
	 */
	public ID createInstance(Object[] parameters) throws IDCreateException {
		if (parameters == null || parameters.length < 1 || parameters.length > 2) {
			throw new IDCreateException(Messages.CompositeNamespace_WrongParameterCount);
		} else if (parameters[0] instanceof String) {
			return new CompositeServiceID(this, new ServiceTypeID(this, (String) parameters[0]), (String) parameters[1]);
		} else if (parameters[0] instanceof IServiceTypeID) {
			return new CompositeServiceID(this, (IServiceTypeID) parameters[0], (String) parameters[1]);
		} else {
			throw new IDCreateException(Messages.CompositeNamespace_WrongParameters);
		}
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.core.identity.Namespace#getScheme()
	 */
	public String getScheme() {
		return "composite"; //$NON-NLS-1$
	}

}