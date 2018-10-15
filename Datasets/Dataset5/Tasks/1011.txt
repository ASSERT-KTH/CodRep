import org.eclipse.ecf.osgi.services.discovery.ServiceEndpointDescription;

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
package org.eclipse.ecf.provider.localdiscovery;

import java.net.URI;
import java.util.Collection;
import java.util.Map;

import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.discovery.identity.IServiceID;
import org.eclipse.ecf.osgi.services.discovery.RemoteServiceEndpointDescription;
import org.osgi.service.discovery.ServiceEndpointDescription;

public class RemoteServiceEndpointDescriptionImpl extends
		RemoteServiceEndpointDescription {

	private final ID endpointId;
	private final ServiceEndpointDescription serviceEndpoint;

	public RemoteServiceEndpointDescriptionImpl(ServiceEndpointDescription sed,
			ID anEndpointId) {
		super(sed.getProperties());
		serviceEndpoint = sed;
		endpointId = anEndpointId;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see
	 * org.eclipse.ecf.osgi.services.discovery.RemoteServiceEndpointDescription
	 * #getProperties()
	 */
	public Map getProperties() {
		return serviceEndpoint.getProperties();
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see
	 * org.eclipse.ecf.osgi.services.discovery.RemoteServiceEndpointDescription
	 * #getProperty(java.lang.String)
	 */
	public Object getProperty(String key) {
		return serviceEndpoint.getProperty(key);
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see
	 * org.eclipse.ecf.osgi.services.discovery.RemoteServiceEndpointDescription
	 * #getPropertyKeys()
	 */
	public Collection getPropertyKeys() {
		return serviceEndpoint.getPropertyKeys();
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see
	 * org.eclipse.ecf.osgi.services.discovery.RemoteServiceEndpointDescription
	 * #getEndpointID()
	 */
	public String getEndpointID() {
		return serviceEndpoint.getEndpointID();
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see
	 * org.eclipse.ecf.osgi.services.discovery.RemoteServiceEndpointDescription
	 * #getEndpointInterfaceName(java.lang.String)
	 */
	public String getEndpointInterfaceName(String interfaceName) {
		return serviceEndpoint.getEndpointInterfaceName(interfaceName);
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see
	 * org.eclipse.ecf.osgi.services.discovery.RemoteServiceEndpointDescription
	 * #getLocation()
	 */
	public URI getLocation() {
		return serviceEndpoint.getLocation();
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see
	 * org.eclipse.ecf.osgi.services.discovery.RemoteServiceEndpointDescription
	 * #getProvidedInterfaces()
	 */
	public Collection getProvidedInterfaces() {
		return serviceEndpoint.getProvidedInterfaces();
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see
	 * org.eclipse.ecf.osgi.services.discovery.RemoteServiceEndpointDescription
	 * #getVersion(java.lang.String)
	 */
	public String getVersion(String interfaceName) {
		return serviceEndpoint.getVersion(interfaceName);
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see
	 * org.eclipse.ecf.osgi.services.discovery.RemoteServiceEndpointDescription
	 * #getECFEndpointID()
	 */
	public ID getEndpointAsID() {
		return endpointId;
	}

	public ID getConnectTargetID() {
		return null;
	}

	public IServiceID getServiceID() {
		return null;
	}
}