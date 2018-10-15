this(aSI.getLocation(), ServiceIDFactory.getDefault().createServiceID(IDFactory.getDefault().getNamespaceByName(JSLPNamespace.NAME), aSI.getServiceID().getServiceTypeID(), aSI.getServiceID().getServiceName()), aSI.getPriority(), aSI.getWeight(), aSI.getServiceProperties());

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
import org.eclipse.ecf.internal.provider.jslp.ServiceURLAdapter;
import org.eclipse.ecf.provider.jslp.identity.JSLPNamespace;

public class JSLPServiceInfo extends ServiceInfo implements IServiceInfo {

	private static final long serialVersionUID = 6828789192986625259L;

	public JSLPServiceInfo(URI anURI, IServiceID serviceID, int priority, int weight, IServiceProperties props) {
		super(anURI, serviceID, priority, weight, props);
	}

	public JSLPServiceInfo(IServiceID serviceID) {
		super(null, serviceID, -1, -1, new ServiceProperties());
	}

	public JSLPServiceInfo(IServiceInfo aSI) throws IDCreateException, SecurityException {
		this(aSI.getLocation(), ServiceIDFactory.getDefault().createServiceID(IDFactory.getDefault().getNamespaceByName(JSLPNamespace.NAME), aSI.getServiceID().getServiceTypeID()), aSI.getPriority(), aSI.getWeight(), aSI.getServiceProperties());
	}

	public JSLPServiceInfo(ServiceURLAdapter anAdapter, int priority, int weight, ServiceProperties serviceProperties) {
		this(anAdapter.getURI(), anAdapter.getIServiceID(), priority, weight, serviceProperties);
	}

	public ServiceURL getServiceURL() throws ServiceLocationException {
		IServiceTypeID stid = getServiceID().getServiceTypeID();
		return new ServiceURL(stid.getInternal() + "://" + getLocation().getScheme() + "://" + getLocation().getHost() + ":" + getLocation().getPort(), ServiceURL.LIFETIME_PERMANENT); //$NON-NLS-1$ //$NON-NLS-2$ //$NON-NLS-3$
	}
}