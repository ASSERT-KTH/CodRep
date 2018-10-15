synchronized void close() {

/*******************************************************************************
 * Copyright (c) 2010-2011 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *   Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.osgi.services.remoteserviceadmin;

import org.osgi.framework.ServiceReference;

public class ImportReference implements
		org.osgi.service.remoteserviceadmin.ImportReference {

	private ServiceReference importedServiceReference;
	private EndpointDescription endpointDescription;

	protected ImportReference(ServiceReference serviceReference,
			EndpointDescription endpointDescription) {
		this.importedServiceReference = serviceReference;
		this.endpointDescription = endpointDescription;
	}

	public synchronized ServiceReference getImportedService() {
		return importedServiceReference;
	}

	public synchronized org.osgi.service.remoteserviceadmin.EndpointDescription getImportedEndpoint() {
		return endpointDescription;
	}

	public synchronized void close() {
		this.importedServiceReference = null;
		this.endpointDescription = null;
	}

	public synchronized String toString() {
		return "ImportReference[importedServiceReference="
				+ importedServiceReference + ", endpointDescription="
				+ endpointDescription + "]";
	}

}