super(null, serviceID, DEFAULT_PRIORITY, DEFAULT_WEIGHT, new ServiceProperties());

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
package org.eclipse.ecf.provider.jslp.container;

import ch.ethz.iks.slp.ServiceLocationException;
import ch.ethz.iks.slp.ServiceURL;
import java.net.URI;
import org.eclipse.ecf.core.identity.IDCreateException;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.discovery.*;
import org.eclipse.ecf.discovery.identity.*;
import org.eclipse.ecf.internal.provider.jslp.ServicePropertiesAdapter;
import org.eclipse.ecf.internal.provider.jslp.ServiceURLAdapter;
import org.eclipse.ecf.provider.jslp.identity.JSLPNamespace;

public class JSLPServiceInfo extends ServiceInfo implements IServiceInfo {

	private static final long serialVersionUID = 6828789192986625259L;

	public JSLPServiceInfo(URI anURI, IServiceID serviceID, int priority, int weight, IServiceProperties props) {
		super(anURI, serviceID, priority, weight, props);
	}

	/**
	 * @param serviceID
	 * @deprecated
	 */
	public JSLPServiceInfo(IServiceID serviceID) {
		super(null, serviceID, ServicePropertiesAdapter.PRIORITY_UNSET, ServicePropertiesAdapter.WEIGHT_UNSET, new ServiceProperties());
	}

	public JSLPServiceInfo(IServiceInfo aSI) throws IDCreateException, SecurityException {
		this(aSI.getLocation(), ServiceIDFactory.getDefault().createServiceID(IDFactory.getDefault().getNamespaceByName(JSLPNamespace.NAME), aSI.getServiceID().getServiceTypeID(), aSI.getServiceID().getServiceName()), aSI.getPriority(), aSI.getWeight(), aSI.getServiceProperties());
	}

	public JSLPServiceInfo(ServiceURLAdapter anAdapter, int priority, int weight, ServicePropertiesAdapter aServicePropertiesAdapter) {
		this(anAdapter.getURI(), anAdapter.getIServiceID(), priority, weight, aServicePropertiesAdapter.toServiceProperties());
	}

	public ServiceURL getServiceURL() throws ServiceLocationException {
		IServiceTypeID stid = getServiceID().getServiceTypeID();
		URI location = getLocation();
		String scheme = location.getScheme();
		String authority = location.getAuthority();
		String path = location.getPath() == null ? "" : location.getPath(); //$NON-NLS-1$
		return new ServiceURL(stid.getInternal() + "://" + scheme + "://" + authority + path, ServiceURL.LIFETIME_PERMANENT); //$NON-NLS-1$ //$NON-NLS-2$
	}
}