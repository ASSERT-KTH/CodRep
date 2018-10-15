newContainer.dispose();

/*******************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/

package org.eclipse.ecf.core;

import org.eclipse.ecf.internal.core.Trace;

/**
 * Factory for creating {@link ISharedObjectContainer} instances. This
 * class provides ECF clients an entry point to constructing {@link ISharedObjectContainer}
 * instances.  
 * <br>
 * <br>
 * Here is an example use of the SharedObjectContainerFactory to construct an instance
 * of the 'standalone' container (has no connection to other containers):
 * <br><br>
 * <code>
 * 	    ISharedObjectContainer container = <br>
 * 			SharedObjectContainerFactory.getDefault().makeSharedObjectContainer('standalone');
 *      <br><br>
 *      ...further use of container variable here...
 * </code>
 * 
 */
public class SharedObjectContainerFactory implements ISharedObjectContainerFactory {

    private static Trace debug = Trace.create("sharedobjectcontainerfactory");
    
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
        if (Trace.ON && debug != null) {
            debug.msg(msg);
        }
    }

    /* (non-Javadoc)
	 * @see org.eclipse.ecf.core.ISharedObjectContainerFactory#makeSharedObjectContainer(org.eclipse.ecf.core.SharedObjectContainerDescription, java.lang.String[], java.lang.Object[])
	 */
    public ISharedObjectContainer makeSharedObjectContainer(
            ContainerDescription desc, String[] argTypes,
            Object[] args) throws ContainerInstantiationException {
        trace("makeSharedObjectContainer("+desc+","+Trace.convertStringAToString(argTypes)+","+Trace.convertObjectAToString(args)+")");
        if (desc == null)
            throw new ContainerInstantiationException(
                    "ContainerDescription cannot be null");
        IContainer newContainer = ContainerFactory.getDefault().makeContainer(desc,argTypes,args);
        ISharedObjectContainer soContainer = (ISharedObjectContainer) newContainer.getAdapter(ISharedObjectContainer.class);
        if (soContainer == null) {
        	newContainer.dispose(-1L);
        	throw new ContainerInstantiationException("new container is not a shared object container");
        }
        return soContainer;
    }
    /* (non-Javadoc)
	 * @see org.eclipse.ecf.core.ISharedObjectContainerFactory#makeSharedObjectContainer(java.lang.String)
	 */
    public ISharedObjectContainer makeSharedObjectContainer(
            String descriptionName)
            throws ContainerInstantiationException {
    	
        return makeSharedObjectContainer(
                ContainerFactory.getDefault().getDescriptionByName(descriptionName), null, null);
    }
    /* (non-Javadoc)
	 * @see org.eclipse.ecf.core.ISharedObjectContainerFactory#makeSharedObjectContainer(java.lang.String, java.lang.Object[])
	 */
    public ISharedObjectContainer makeSharedObjectContainer(
            String descriptionName, Object[] args)
            throws ContainerInstantiationException {
        return makeSharedObjectContainer(
        		ContainerFactory.getDefault().getDescriptionByName(descriptionName), null, args);
    }
    /* (non-Javadoc)
	 * @see org.eclipse.ecf.core.ISharedObjectContainerFactory#makeSharedObjectContainer(java.lang.String, java.lang.String[], java.lang.Object[])
	 */
    public ISharedObjectContainer makeSharedObjectContainer(
            String descriptionName, String[] argsTypes, Object[] args)
            throws ContainerInstantiationException {
        return makeSharedObjectContainer(
        		ContainerFactory.getDefault().getDescriptionByName(descriptionName), argsTypes, args);
    }
}
 No newline at end of file