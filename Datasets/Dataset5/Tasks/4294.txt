private static Trace debug = Trace.create("containerfactory");

/*******************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/

package org.eclipse.ecf.core;

import java.util.ArrayList;
import java.util.Hashtable;
import java.util.List;

import org.eclipse.ecf.core.provider.IContainerInstantiator;
import org.eclipse.ecf.core.util.AbstractFactory;
import org.eclipse.ecf.internal.core.Trace;

/**
 * Factory for creating {@link IContainer} instances. This
 * class provides ECF clients an entry point to constructing {@link IContainer}
 * instances.  
 * <br>
 * <br>
 * Here is an example use of the ContainerFactory to construct an instance
 * of the 'standalone' container (has no connection to other containers):
 * <br><br>
 * <code>
 * 	    IContainer container = <br>
 * 			ContainerFactory.getDefault().makeContainer('standalone');
 *      <br><br>
 *      ...further use of container variable here...
 * </code>
 * 
 */
public class ContainerFactory implements IContainerFactory {

    private static Trace debug = Trace.create("simplecontainerfactory");
    
    private static Hashtable containerdescriptions = new Hashtable();
    protected static IContainerFactory instance = null;
    
    static {
    	instance = new ContainerFactory();
    }
    protected ContainerFactory() {
    }
    public static IContainerFactory getDefault() {
    	return instance;
    }
    private static void trace(String msg) {
        if (Trace.ON && debug != null) {
            debug.msg(msg);
        }
    }

    private static void dumpStack(String msg, Throwable e) {
        if (Trace.ON && debug != null) {
            debug.dumpStack(e, msg);
        }
    }
    /* (non-Javadoc)
	 * @see org.eclipse.ecf.core.IContainerFactory#addDescription(org.eclipse.ecf.core.ContainerDescription)
	 */
    public ContainerDescription addDescription(
            ContainerDescription scd) {
        trace("addDescription("+scd+")");
        return addDescription0(scd);
    }
    /* (non-Javadoc)
	 * @see org.eclipse.ecf.core.IContainerFactory#getDescriptions()
	 */
    public List getDescriptions() {
        return getDescriptions0();
    }
    protected List getDescriptions0() {
        return new ArrayList(containerdescriptions.values());
    }
    protected ContainerDescription addDescription0(
            ContainerDescription n) {
        if (n == null)
            return null;
        return (ContainerDescription) containerdescriptions.put(n
                .getName(), n);
    }
    /* (non-Javadoc)
	 * @see org.eclipse.ecf.core.IContainerFactory#containsDescription(org.eclipse.ecf.core.ContainerDescription)
	 */
    public boolean containsDescription(
            ContainerDescription scd) {
        return containsDescription0(scd);
    }
    protected boolean containsDescription0(
            ContainerDescription scd) {
        if (scd == null)
            return false;
        return containerdescriptions.containsKey(scd.getName());
    }
    protected ContainerDescription getDescription0(
            ContainerDescription scd) {
        if (scd == null)
            return null;
        return (ContainerDescription) containerdescriptions.get(scd
                .getName());
    }
    protected ContainerDescription getDescription0(
            String name) {
        if (name == null)
            return null;
        return (ContainerDescription) containerdescriptions.get(name);
    }
    /* (non-Javadoc)
	 * @see org.eclipse.ecf.core.ISharedObjectContainerFactory#getDescriptionByName(java.lang.String)
	 */
    public ContainerDescription getDescriptionByName(
            String name) throws ContainerInstantiationException {
        trace("getDescriptionByName("+name+")");
        ContainerDescription res = getDescription0(name);
        if (res == null) {
            throw new ContainerInstantiationException(
                    "ContainerDescription named '" + name
                            + "' not found");
        }
        return res;
    }
    /* (non-Javadoc)
	 * @see org.eclipse.ecf.core.IContainerFactory#makeContainer(org.eclipse.ecf.core.ContainerDescription, java.lang.String[], java.lang.Object[])
	 */
    public IContainer makeContainer(
            ContainerDescription desc, String[] argTypes,
            Object[] args) throws ContainerInstantiationException {
        trace("makeContainer("+desc+","+Trace.convertStringAToString(argTypes)+","+Trace.convertObjectAToString(args)+")");
        if (desc == null)
            throw new ContainerInstantiationException(
                    "ContainerDescription cannot be null");
        ContainerDescription cd = getDescription0(desc);
        if (cd == null)
            throw new ContainerInstantiationException(
                    "ContainerDescription named '" + desc.getName()
                            + "' not found");
        Class clazzes[] = null;
        IContainerInstantiator instantiator = null;
        try {
            instantiator = (IContainerInstantiator) cd
            .getInstantiator();
            clazzes = AbstractFactory.getClassesForTypes(argTypes, args, cd.getClassLoader());
        } catch (Exception e) {
            ContainerInstantiationException newexcept = new ContainerInstantiationException(
                    "makeContainer exception with description: "+desc+": "+e.getClass().getName()+": "+e.getMessage());
            newexcept.setStackTrace(e.getStackTrace());
            dumpStack("Exception in makeContainer",newexcept);
            throw newexcept;
        }
        if (instantiator == null)
            throw new ContainerInstantiationException(
                    "Instantiator for ContainerDescription "
                            + cd.getName() + " is null");
        // Ask instantiator to actually create instance
        return (IContainer) instantiator
                .makeInstance(desc,clazzes, args);
    }
    /* (non-Javadoc)
	 * @see org.eclipse.ecf.core.IContainerFactory#makeContainer(java.lang.String)
	 */
    public IContainer makeContainer(
            String descriptionName)
            throws ContainerInstantiationException {
        return makeContainer(
                getDescriptionByName(descriptionName), null, null);
    }
    /* (non-Javadoc)
	 * @see org.eclipse.ecf.core.IContainerFactory#makeContainer(java.lang.String, java.lang.Object[])
	 */
    public IContainer makeContainer(
            String descriptionName, Object[] args)
            throws ContainerInstantiationException {
        return makeContainer(
                getDescriptionByName(descriptionName), null, args);
    }
    /* (non-Javadoc)
	 * @see org.eclipse.ecf.core.IContainerFactory#makeContainer(java.lang.String, java.lang.String[], java.lang.Object[])
	 */
    public IContainer makeContainer(
            String descriptionName, String[] argsTypes, Object[] args)
            throws ContainerInstantiationException {
        return makeContainer(
                getDescriptionByName(descriptionName), argsTypes, args);
    }
    /* (non-Javadoc)
	 * @see org.eclipse.ecf.core.IContainerFactory#removeDescription(org.eclipse.ecf.core.ContainerDescription)
	 */
    public ContainerDescription removeDescription(
            ContainerDescription scd) {
        trace("removeDescription("+scd+")");
        return removeDescription0(scd);
    }
    protected ContainerDescription removeDescription0(
            ContainerDescription n) {
        if (n == null)
            return null;
        return (ContainerDescription) containerdescriptions.remove(n
                .getName());
    }

}
 No newline at end of file