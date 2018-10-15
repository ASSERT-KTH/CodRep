Trace.trace(Activator.PLUGIN_ID, msg);

/*******************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.core.sharedobject;

import org.eclipse.ecf.core.ContainerCreateException;
import org.eclipse.ecf.core.ContainerFactory;
import org.eclipse.ecf.core.ContainerTypeDescription;
import org.eclipse.ecf.core.IContainer;
import org.eclipse.ecf.core.util.Trace;
import org.eclipse.ecf.internal.core.sharedobject.Activator;
import org.eclipse.ecf.internal.core.sharedobject.Messages;

/**
 * Factory for creating {@link ISharedObjectContainer} instances. This class
 * provides ECF clients an entry point to constructing
 * {@link ISharedObjectContainer} instances. <br>
 * <br>
 * Here is an example use of the SharedObjectContainerFactory to construct an
 * instance of the 'standalone' container (has no connection to other
 * containers): <br>
 * <br>
 * <code>
 * 	    ISharedObjectContainer container = <br>
 * 			SharedObjectContainerFactory.getDefault().createSharedObjectContainer('standalone');
 *      <br><br>
 *      ...further use of container variable here...
 * </code>
 * 
 */
public class SharedObjectContainerFactory implements
		ISharedObjectContainerFactory {
	protected static ISharedObjectContainerFactory instance = null;
	static {
		instance = new SharedObjectContainerFactory();
	}

	protected SharedObjectContainerFactory() {
	}

	public static ISharedObjectContainerFactory getDefault() {
		return instance;
	}

	private static void trace(String msg) {
		Trace.trace(Activator.getDefault(), msg);
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.ISharedObjectContainerFactory#createSharedObjectContainer(org.eclipse.ecf.core.SharedObjectContainerDescription,
	 *      java.lang.Object[])
	 */
	public ISharedObjectContainer createSharedObjectContainer(
			ContainerTypeDescription desc, Object[] args)
			throws ContainerCreateException {
		trace("createSharedObjectContainer(" + desc + "," //$NON-NLS-1$ //$NON-NLS-2$
				+ Trace.getArgumentsString(args) + ")"); //$NON-NLS-1$
		if (desc == null)
			throw new ContainerCreateException(
					Messages.SharedObjectContainerFactory_Exception_Description_Not_Null);
		IContainer newContainer = ContainerFactory.getDefault()
				.createContainer(desc, args);
		ISharedObjectContainer soContainer = (ISharedObjectContainer) newContainer
				.getAdapter(ISharedObjectContainer.class);
		if (soContainer == null) {
			newContainer.dispose();
			throw new ContainerCreateException(
					Messages.SharedObjectContainerFactory_Exception_Container_Wrong_Type);
		}
		return soContainer;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.ISharedObjectContainerFactory#createSharedObjectContainer(java.lang.String)
	 */
	public ISharedObjectContainer createSharedObjectContainer(
			String descriptionName) throws ContainerCreateException {
		return createSharedObjectContainer(ContainerFactory.getDefault()
				.getDescriptionByName(descriptionName), null);
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.ISharedObjectContainerFactory#createSharedObjectContainer(java.lang.String,
	 *      java.lang.Object[])
	 */
	public ISharedObjectContainer createSharedObjectContainer(
			String descriptionName, Object[] args)
			throws ContainerCreateException {
		return createSharedObjectContainer(ContainerFactory.getDefault()
				.getDescriptionByName(descriptionName), args);
	}

}
 No newline at end of file