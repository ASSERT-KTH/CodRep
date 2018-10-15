buf.append(aServiceURL.getURLPath());

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
package org.eclipse.ecf.internal.provider.jslp;

import ch.ethz.iks.slp.ServiceURL;
import java.net.URI;
import org.eclipse.core.runtime.Assert;
import org.eclipse.ecf.core.identity.*;
import org.eclipse.ecf.core.util.Trace;
import org.eclipse.ecf.discovery.identity.IServiceID;
import org.eclipse.ecf.provider.jslp.identity.JSLPNamespace;

/**
 * Adapts jSLP's ServiceURL to an ECF's IServiceID and vice versa
 */
public class ServiceURLAdapter {

	private URI uri;
	private IServiceID serviceID;

	public ServiceURLAdapter(ServiceURL aServiceURL) {
		this(aServiceURL, new String[0]);
	}

	public ServiceURLAdapter(ServiceURL aServiceURL, String[] scopes) {
		Assert.isNotNull(aServiceURL);
		Assert.isNotNull(scopes);
		setIServiceID(aServiceURL, scopes);
		setURI(aServiceURL);
	}

	private void setURI(ServiceURL aServiceURL) {
		StringBuffer buf = new StringBuffer();
		String protocol = aServiceURL.getProtocol();
		if (protocol == null) {
			protocol = "unknown"; //$NON-NLS-1$
		}
		buf.append(protocol);
		buf.append("://"); //$NON-NLS-1$
		buf.append(aServiceURL.getHost());
		buf.append(":"); //$NON-NLS-1$
		buf.append(aServiceURL.getPort());
		buf.append("/"); //$NON-NLS-1$
		uri = URI.create(buf.toString());
	}

	private void setIServiceID(ServiceURL aServiceURL, String[] scopes) {
		Namespace namespace = IDFactory.getDefault().getNamespaceByName(JSLPNamespace.NAME);
		try {
			serviceID = (IServiceID) namespace.createInstance(new Object[] {aServiceURL, scopes});
		} catch (IDCreateException e) {
			// may never happen
			Trace.catching(Activator.PLUGIN_ID, JSLPDebugOptions.EXCEPTIONS_CATCHING, this.getClass(), "setIServiceID", e); //$NON-NLS-1$
		}
	}

	/**
	 * @return URI
	 */
	public URI getURI() {
		return uri;
	}

	/**
	 * @return IServiceID
	 */
	public IServiceID getIServiceID() {
		return serviceID;
	}
}