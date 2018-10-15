Object[] args)

/*******************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.provider.remoteservice.generic;

import java.util.HashMap;
import java.util.Map;

import org.eclipse.ecf.core.ContainerCreateException;
import org.eclipse.ecf.core.ContainerTypeDescription;
import org.eclipse.ecf.core.IContainer;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.core.provider.IContainerInstantiator;
import org.eclipse.ecf.core.sharedobject.ISharedObjectContainerConfig;

public class RemoteServiceContainerFactory implements
		IContainerInstantiator {

	public IContainer createInstance(ContainerTypeDescription description,
			Class[] argTypes, Object[] args)
			throws ContainerCreateException {
		try {
			final ID newID = IDFactory.getDefault().createGUID();
			return new RemoteServiceContainer(new ISharedObjectContainerConfig() {
				public Object getAdapter(Class clazz) {
					return null;
				}
				public Map getProperties() {
					return new HashMap();
				}
				public ID getID() {
					return newID;
				}});
		} catch (Exception e) {
			throw new ContainerCreateException("Exception creating GenericRemoteServiceContainer",e);
		}				
		
	}

}