this.serviceEndpointDescription = new RemoteServiceEndpointDescriptionImpl(

/*******************************************************************************
 * Copyright (c) 2009 EclipseSource and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *   EclipseSource - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.internal.osgi.services.discovery;

import java.util.Collection;
import java.util.Collections;
import org.eclipse.ecf.discovery.IServiceInfo;
import org.osgi.service.discovery.DiscoveredServiceNotification;
import org.osgi.service.discovery.ServiceEndpointDescription;

public class DiscoveredServiceNotificationImpl implements
		DiscoveredServiceNotification {

	private final int type;
	private ServiceEndpointDescription serviceEndpointDescription;

	public DiscoveredServiceNotificationImpl(int type, IServiceInfo serviceInfo) {
		this.type = type;
		this.serviceEndpointDescription = new ECFServiceEndpointDescriptionImpl(
				serviceInfo);
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @seeorg.osgi.service.discovery.DiscoveredServiceNotification#
	 * getServiceEndpointDescription()
	 */
	public ServiceEndpointDescription getServiceEndpointDescription() {
		return serviceEndpointDescription;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.osgi.service.discovery.DiscoveredServiceNotification#getType()
	 */
	public int getType() {
		return type;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see java.lang.Object#toString()
	 */
	public String toString() {
		StringBuffer sb = new StringBuffer("DiscoveredServiceNotificationImpl["); //$NON-NLS-1$
		sb.append("type=").append(getType()).append(";sed=").append( //$NON-NLS-1$ //$NON-NLS-2$
				getServiceEndpointDescription()).append("]"); //$NON-NLS-1$
		return sb.toString();
	}

	public Collection getFilters() {
		// XXX TODO
		return Collections.EMPTY_LIST;
	}

	public Collection getInterfaces() {
		// XXX TODO
		return Collections.EMPTY_LIST;
	}
}