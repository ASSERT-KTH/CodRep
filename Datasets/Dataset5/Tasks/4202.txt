public CompositeServiceID(final CompositeNamespace compositeNamespace, final IServiceTypeID serviceTypeID, final String string) {

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

import org.eclipse.ecf.discovery.identity.IServiceTypeID;
import org.eclipse.ecf.discovery.identity.ServiceID;

public class CompositeServiceID extends ServiceID {

	private static final long serialVersionUID = -5296876662431183581L;

	/**
	 * @param compositeNamespace
	 * @param serviceTypeID
	 * @param string
	 */
	public CompositeServiceID(CompositeNamespace compositeNamespace, IServiceTypeID serviceTypeID, String string) {
		super(compositeNamespace, serviceTypeID, string);
	}
}