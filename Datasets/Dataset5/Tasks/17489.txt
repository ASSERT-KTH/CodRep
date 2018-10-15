return new Class[][] { { String.class } };

/****************************************************************************
 * Copyright (c) 2006, 2007 Remy Suen, Composent Inc., and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Remy Suen <remy.suen@gmail.com> - initial API and implementation
 *****************************************************************************/
package org.eclipse.ecf.internal.provider.msn;

import org.eclipse.core.runtime.Assert;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDCreateException;
import org.eclipse.ecf.core.identity.Namespace;

public class MSNNamespace extends Namespace {

	private static final long serialVersionUID = 7302784914405195380L;
	private static final String SCHEME_IDENTIFIER = "msn"; //$NON-NLS-1$

	public ID createInstance(Object[] parameters) throws IDCreateException {
		Assert.isNotNull(parameters, Messages.MSNNamespace_ParameterIsNull);
		if (parameters.length == 1 && parameters[0] instanceof String) {
			return new MSNID(this, (String) parameters[0]);
		} else {
			throw new IDCreateException(
					Messages.MSNNamespace_ParameterIsInvalid);
		}
	}

	public String getScheme() {
		return SCHEME_IDENTIFIER;
	}

	public Class[][] getSupportedParameterTypes() {
		return new Class[][] { { String.class }, { String.class, String.class } };
	}

}