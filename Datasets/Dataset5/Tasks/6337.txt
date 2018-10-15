throw new ContainerCreateException("Could not create RPCClientContainer", e); //$NON-NLS-1$

/******************************************************************************* 
 * Copyright (c) 2010-2011 Naumen. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *   Pavel Samolisov - initial API and implementation
 *******************************************************************************/
package org.eclipse.ecf.internal.remoteservice.rpc;

import java.util.*;
import org.eclipse.ecf.core.*;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.core.provider.BaseContainerInstantiator;
import org.eclipse.ecf.core.provider.IRemoteServiceContainerInstantiator;
import org.eclipse.ecf.remoteservice.rpc.client.RpcClientContainer;
import org.eclipse.ecf.remoteservice.rpc.identity.RpcId;
import org.eclipse.ecf.remoteservice.rpc.identity.RpcNamespace;

public class RpcClientContainerInstantiator extends BaseContainerInstantiator implements
		IRemoteServiceContainerInstantiator {

	private static final String RPC_CONTAINER_TYPE = "ecf.xmlrpc.client"; //$NON-NLS-1$

	public IContainer createInstance(ContainerTypeDescription description, Object[] parameters)
			throws ContainerCreateException {
		try {
			RpcId ID = null;
			if (parameters != null && parameters[0] instanceof RpcId)
				ID = (RpcId) parameters[0];
			else
				ID = (RpcId) IDFactory.getDefault().createID(RpcNamespace.NAME, parameters);
			return new RpcClientContainer(ID);
		} catch (Exception e) {
			throw new ContainerCreateException(Messages.RPC_COULD_NOT_CREATE_CONTAINER, e);
		}
	}

	public String[] getSupportedAdapterTypes(ContainerTypeDescription description) {
		return getInterfacesAndAdaptersForClass(RpcClientContainer.class);
	}

	public Class[][] getSupportedParameterTypes(ContainerTypeDescription description) {
		RpcNamespace namespace = (RpcNamespace) IDFactory.getDefault().getNamespaceByName(RpcNamespace.NAME);
		return namespace.getSupportedParameterTypes();
	}

	public String[] getImportedConfigs(ContainerTypeDescription description, String[] exporterSupportedConfigs) {
		if (RPC_CONTAINER_TYPE.equals(description.getName())) {
			List supportedConfigs = Arrays.asList(exporterSupportedConfigs);
			if (supportedConfigs.contains(RPC_CONTAINER_TYPE))
				return new String[] {RPC_CONTAINER_TYPE};
		}
		return null;
	}

	public Dictionary getPropertiesForImportedConfigs(ContainerTypeDescription description, String[] importedConfigs,
			Dictionary exportedProperties) {
		return null;
	}

	public String[] getSupportedConfigs(ContainerTypeDescription description) {
		return new String[] {RPC_CONTAINER_TYPE};
	}
}