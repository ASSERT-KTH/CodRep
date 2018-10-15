protected EndpointDescription createExportEndpointDescription(

/*******************************************************************************
 * Copyright (c) 2010 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *   Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.osgi.services.remoteserviceadmin;

import java.util.Map;

import org.eclipse.core.runtime.IStatus;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.internal.osgi.services.remoteserviceadmin.DebugOptions;
import org.eclipse.ecf.internal.osgi.services.remoteserviceadmin.LogUtility;
import org.eclipse.ecf.remoteservice.IRemoteServiceContainer;
import org.eclipse.ecf.remoteservice.IRemoteServiceID;
import org.eclipse.ecf.remoteservice.IRemoteServiceRegistration;
import org.osgi.framework.BundleContext;
import org.osgi.framework.ServiceReference;

public abstract class AbstractRemoteServiceAdmin {

	private BundleContext context;

	public AbstractRemoteServiceAdmin(BundleContext context) {
		this.context = context;
	}

	protected BundleContext getContext() {
		return context;
	}

	protected void logError(String methodName, String message, IStatus status) {
		LogUtility.logError(methodName, DebugOptions.REMOTE_SERVICE_ADMIN,
				this.getClass(), status);
	}

	protected void trace(String methodName, String message) {
		LogUtility.trace(methodName, DebugOptions.REMOTE_SERVICE_ADMIN,
				this.getClass(), message);
	}

	protected void logWarning(String methodName, String message) {
		LogUtility.logWarning(methodName, DebugOptions.REMOTE_SERVICE_ADMIN,
				this.getClass(), message);
	}

	protected void logError(String methodName, String message) {
		LogUtility.logError(methodName, DebugOptions.REMOTE_SERVICE_ADMIN,
				this.getClass(), message);
	}

	protected Object getService(ServiceReference serviceReference) {
		return context.getService(serviceReference);
	}

	private Object getPropertyValue(String propertyName,
			ServiceReference serviceReference, Map<String, Object> properties) {
		Object result = properties.get(propertyName);
		if (result == null) {
			result = serviceReference.getProperty(propertyName);
		}
		return result;
	}

	protected EndpointDescription createEndpointDescription(
			ServiceReference serviceReference, Map<String, Object> properties,
			IRemoteServiceRegistration registration,
			IRemoteServiceContainer container) {
		// endpoint ID is container ID
		ID endpointID = registration.getContainerID();
		// If connectTarget is set
		Object connectTarget = getPropertyValue(
				RemoteConstants.ENDPOINT_CONNECTTARGET_ID, serviceReference,
				properties);
		ID connectTargetID = null;
		if (connectTarget != null) {
			// Then we get the host container connected ID
			ID connectedID = container.getContainer().getConnectedID();
			if (connectedID != null && !connectedID.equals(endpointID))
				connectTargetID = connectedID;
		}
		ID[] idFilter = (ID[]) getPropertyValue(
				RemoteConstants.ENDPOINT_IDFILTER_IDS, serviceReference,
				properties);
		String rsFilter = (String) getPropertyValue(
				RemoteConstants.ENDPOINT_REMOTESERVICE_FILTER,
				serviceReference, properties);
		IRemoteServiceID rsID = registration.getID();
		return new EndpointDescription(serviceReference, properties,
				rsID.getContainerID(), rsID.getContainerRelativeID(),
				connectTargetID, idFilter, rsFilter);
	}

	public void close() {
		this.context = null;
	}
}