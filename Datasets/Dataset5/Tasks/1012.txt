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

import java.util.Map;

import org.eclipse.core.runtime.IAdapterFactory;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.osgi.services.discovery.RemoteServiceEndpointDescription;
import org.eclipse.ecf.osgi.services.discovery.RemoteServicePublication;
import org.osgi.service.discovery.ServiceEndpointDescription;

public class ServiceEndpointDescriptionFactory implements IAdapterFactory {

	/*
	 * (non-Javadoc)
	 * 
	 * @see
	 * org.eclipse.core.runtime.IAdapterFactory#getAdapter(java.lang.Object,
	 * java.lang.Class)
	 */
	public Object getAdapter(Object adaptableObject, Class adapterType) {
		if (adapterType.equals(RemoteServiceEndpointDescription.class)
				&& adaptableObject instanceof ServiceEndpointDescription) {
			ServiceEndpointDescription sed = (ServiceEndpointDescription) adaptableObject;
			Map properties = sed.getProperties();
			Object obj1 = properties
					.get(RemoteServicePublication.ENDPOINT_CONTAINERID);
			Object obj2 = properties
					.get(RemoteServicePublication.ENDPOINT_CONTAINERID_NAMESPACE);
			if (obj1 instanceof byte[]) {
				obj1 = new String(((byte[]) obj1));
			}
			if (obj1 instanceof String && obj2 instanceof String) {
				// create the endpoint id
				final String endpointStr = (String) obj1;
				final String namespaceStr = (String) obj2;
				return new RemoteServiceEndpointDescriptionImpl(sed, IDFactory
						.getDefault().createID(namespaceStr, endpointStr));
			}
		}
		return null;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.core.runtime.IAdapterFactory#getAdapterList()
	 */
	public Class[] getAdapterList() {
		return new Class[] { ServiceEndpointDescription.class };
	}
}