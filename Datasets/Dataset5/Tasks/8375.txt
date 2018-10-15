package org.eclipse.ecf.core.sharedobject;

/*******************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.core;

import java.util.Map;

import org.eclipse.core.runtime.IAdapterFactory;
import org.eclipse.core.runtime.Status;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.core.identity.IDCreateException;
import org.eclipse.ecf.internal.core.ECFPlugin;

public abstract class AbstractSharedObjectContainerAdapterFactory implements
		IAdapterFactory {

	protected static final int ADD_ADAPTER_ERROR_CODE = 300001;

	protected static final String ADD_ADAPTER_ERROR_MESSAGE = "Exception adding shared object adapter";

	private static final int CREATE_ADAPTER_ID_ERROR_CODE = 300002;

	private static final String CREATE_ADAPTER_ID_ERROR_MESSAGE = null;

	protected ID sharedObjectID = null;
	
	public Object getAdapter(Object adaptableObject, Class adapterType) {
		if (ISharedObjectContainer.class.isInstance(adaptableObject))
			return getSharedObjectAdapter(
					(ISharedObjectContainer) adaptableObject, adapterType);
		else
			return null;
	}

	protected synchronized ISharedObject getSharedObjectAdapter(
			ISharedObjectContainer container, Class adapterType) {
		ISharedObjectManager manager = container.getSharedObjectManager();
		// Check to see if the container already has the given shared object
		// If so then return it
		if (sharedObjectID != null) {
			ISharedObject so = manager.getSharedObject(sharedObjectID);
			if (so != null) return so;
		}
		ISharedObject adapter = createAdapter(container, adapterType);
		if (adapter == null)
			return null;
		sharedObjectID = createAdapterID(adapter,
				adapterType);
		if (sharedObjectID == null)
			return null;
		Map sharedObjectProperties = createAdapterProperties(
				adapter, adapterType);
		try {
			manager.addSharedObject(sharedObjectID, adapter,
					sharedObjectProperties);
		} catch (SharedObjectAddException e) {
			ECFPlugin.getDefault().getLog().log(
					new Status(IStatus.ERROR, ECFPlugin.getDefault()
							.getBundle().getSymbolicName(),
							ADD_ADAPTER_ERROR_CODE, ADD_ADAPTER_ERROR_MESSAGE,
							e));
			return null;
		}
		return adapter;
	}

	protected Map createAdapterProperties(
			ISharedObject sharedObjectAdapter, Class adapterType) {
		return null;
	}

	protected ID createAdapterID(ISharedObject adapter,
			Class adapterType) {
		String singletonName = adapter.getClass().getName();
		try {
			return IDFactory.getDefault().createStringID(singletonName);
		} catch (IDCreateException e) {
			ECFPlugin.getDefault().getLog().log(
					new Status(IStatus.ERROR, ECFPlugin.getDefault()
							.getBundle().getSymbolicName(),
							CREATE_ADAPTER_ID_ERROR_CODE, CREATE_ADAPTER_ID_ERROR_MESSAGE,
							e));
			return null;
		}
	}

	protected abstract ISharedObject createAdapter(ISharedObjectContainer container, Class adapterType);

	public abstract Class[] getAdapterList();

}