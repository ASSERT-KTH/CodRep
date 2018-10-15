.getProperty(RemoteConstants.SERVICE_EXPORTED_CONTAINER_FACTORY_ARGS);

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

import java.util.ArrayList;
import java.util.List;

import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Status;
import org.eclipse.ecf.core.ContainerConnectException;
import org.eclipse.ecf.core.ContainerCreateException;
import org.eclipse.ecf.core.ContainerTypeDescription;
import org.eclipse.ecf.core.IContainer;
import org.eclipse.ecf.core.IContainerFactory;
import org.eclipse.ecf.core.IContainerManager;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.core.identity.IIDFactory;
import org.eclipse.ecf.core.identity.Namespace;
import org.eclipse.ecf.core.security.IConnectContext;
import org.eclipse.ecf.internal.osgi.services.remoteserviceadmin.Activator;
import org.eclipse.ecf.internal.osgi.services.remoteserviceadmin.DebugOptions;
import org.eclipse.ecf.internal.osgi.services.remoteserviceadmin.LogUtility;
import org.eclipse.ecf.remoteservice.IRemoteServiceContainer;
import org.eclipse.ecf.remoteservice.IRemoteServiceContainerAdapter;
import org.eclipse.ecf.remoteservice.RemoteServiceContainer;
import org.osgi.framework.ServiceReference;

public abstract class AbstractContainerSelector {

	public static final IRemoteServiceContainer[] EMPTY_REMOTE_SERVICE_CONTAINER_ARRAY = new IRemoteServiceContainer[] {};

	protected IIDFactory getIDFactory() {
		return IDFactory.getDefault();
	}

	protected IContainerManager getContainerManager() {
		return Activator.getDefault().getContainerManager();
	}

	protected IContainerFactory getContainerFactory() {
		return getContainerManager().getContainerFactory();
	}

	protected ContainerTypeDescription[] getContainerTypeDescriptions() {
		return (ContainerTypeDescription[]) getContainerFactory()
				.getDescriptions().toArray(new ContainerTypeDescription[] {});
	}

	protected IContainer[] getContainers() {
		return getContainerManager().getAllContainers();
	}

	protected IRemoteServiceContainerAdapter hasRemoteServiceContainerAdapter(
			IContainer container) {
		return (IRemoteServiceContainerAdapter) container
				.getAdapter(IRemoteServiceContainerAdapter.class);
	}

	protected ContainerTypeDescription getContainerTypeDescription(
			IContainer container) {
		return getContainerManager().getContainerTypeDescription(
				container.getID());
	}

	protected IRemoteServiceContainer[] getRemoteServiceContainers(
			IContainer[] containers) {
		List results = new ArrayList();
		for (int i = 0; i < containers.length; i++) {
			IRemoteServiceContainerAdapter adapter = hasRemoteServiceContainerAdapter(containers[i]);
			if (adapter != null)
				results.add(new RemoteServiceContainer(containers[i], adapter));
		}
		return (IRemoteServiceContainer[]) results
				.toArray(new IRemoteServiceContainer[] {});
	}

	protected boolean includeContainerWithConnectNamespace(
			IContainer container, String connectNamespaceName) {
		if (connectNamespaceName != null) {
			Namespace namespace = container.getConnectNamespace();
			if (namespace != null
					&& namespace.getName().equals(connectNamespaceName))
				return true;
		}
		return false;
	}

	protected void connectContainer(IContainer container, ID connectTargetID,
			IConnectContext connectContext) throws ContainerConnectException {
		trace("connectContainer", "Connecting container=" + container.getID() //$NON-NLS-1$ //$NON-NLS-2$
				+ " to connectTargetID=" + connectTargetID); //$NON-NLS-1$
		container.connect(connectTargetID, connectContext);
	}

	protected String[] getSupportedConfigTypes(
			ContainerTypeDescription containerTypeDescription) {
		String[] supportedConfigs = containerTypeDescription
				.getSupportedConfigs();
		return (supportedConfigs == null) ? new String[0] : supportedConfigs;
	}

	protected String[] getSupportedIntents(
			ContainerTypeDescription containerTypeDescription) {
		String[] supportedIntents = containerTypeDescription
				.getSupportedIntents();
		return (supportedIntents == null) ? new String[0] : supportedIntents;
	}

	protected IContainer createContainer(ServiceReference serviceReference,
			ContainerTypeDescription containerTypeDescription)
			throws ContainerCreateException {

		IContainerFactory containerFactory = getContainerFactory();

		Object containerFactoryArguments = serviceReference
				.getProperty(RemoteConstants.EXPORTED_CONTAINER_FACTORY_ARGS);
		if (containerFactoryArguments instanceof String) {
			return containerFactory.createContainer(containerTypeDescription,
					(String) containerFactoryArguments);
		} else if (containerFactoryArguments instanceof ID) {
			return containerFactory.createContainer(containerTypeDescription,
					(ID) containerFactoryArguments);
		} else if (containerFactoryArguments instanceof Object[]) {
			return containerFactory.createContainer(containerTypeDescription,
					(Object[]) containerFactoryArguments);
		}
		return containerFactory.createContainer(containerTypeDescription);
	}

	protected ID createTargetID(IContainer container, Object target) {
		ID targetID = null;
		if (target instanceof String)
			targetID = getIDFactory().createID(container.getConnectNamespace(),
					(String) target);
		return targetID;
	}

	protected void disconnectContainer(IContainer container) {
		container.disconnect();
	}

	protected IConnectContext createConnectContext(
			ServiceReference serviceReference, IContainer container,
			Object context) {
		if (context instanceof IConnectContext)
			return (IConnectContext) context;
		return null;
	}

	protected void logException(String string, Exception e) {
		Activator.getDefault().log(
				new Status(IStatus.ERROR, Activator.PLUGIN_ID, string, e));
	}

	protected void trace(String methodName, String message) {
		LogUtility.trace(methodName, DebugOptions.CONTAINERSELECTOR,
				this.getClass(), message);
	}

	protected void traceException(String methodName, String message, Throwable t) {
		LogUtility.traceException(methodName, DebugOptions.EXCEPTIONS_CATCHING,
				this.getClass(), message, t);
	}

	protected void logError(String methodName, String message, Throwable t) {
		LogUtility.logError(methodName, DebugOptions.CONTAINERSELECTOR,
				this.getClass(), message, t);
	}

	protected void logError(String methodName, String message) {
		LogUtility.logError(methodName, DebugOptions.CONTAINERSELECTOR,
				this.getClass(), message);
	}

	protected void logWarning(String methodName, String message) {
		LogUtility.logWarning(methodName, DebugOptions.CONTAINERSELECTOR,
				this.getClass(), message);
	}

	protected boolean matchConnectNamespace(IContainer container,
			ID endpointID, ID connectTargetID) {
		if (connectTargetID != null) {
			return connectTargetID.getNamespace().getName()
					.equals(container.getConnectNamespace().getName());
		}
		if (endpointID == null)
			return false;
		return endpointID.getNamespace().getName()
				.equals(container.getConnectNamespace().getName());
	}

	protected boolean matchContainerID(IContainer container, ID endpointID) {
		if (endpointID == null)
			return false;
		return endpointID.equals(container.getID());
	}

}