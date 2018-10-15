.getClass().getClassLoader());

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
import org.eclipse.ecf.core.provider.ISharedObjectInstantiator;
import org.eclipse.ecf.core.util.AbstractFactory;
import org.eclipse.ecf.internal.core.Trace;

/**
 * Factory for creating {@link ISharedObject} instances. This class provides ECF
 * clients an entry point to constructing {@link ISharedObject} instances. <br>
 */
public class SharedObjectFactory implements ISharedObjectFactory {
	private static Trace debug = Trace.create("containerfactory");
	private static Hashtable sharedobjectdescriptions = new Hashtable();
	protected static ISharedObjectFactory instance = null;
	static {
		instance = new SharedObjectFactory();
	}

	protected SharedObjectFactory() {
	}

	public static ISharedObjectFactory getDefault() {
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

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.ISharedObjectFactory#addDescription(org.eclipse.ecf.core.SharedObjectDescription)
	 */
	public SharedObjectDescription addDescription(SharedObjectDescription description) {
		trace("addDescription(" + description + ")");
		return addDescription0(description);
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.ISharedObjectFactory#getDescriptions()
	 */
	public List getDescriptions() {
		return getDescriptions0();
	}

	protected List getDescriptions0() {
		return new ArrayList(sharedobjectdescriptions.values());
	}

	protected SharedObjectDescription addDescription0(SharedObjectDescription n) {
		if (n == null)
			return null;
		return (SharedObjectDescription) sharedobjectdescriptions.put(n.getName(), n);
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.ISharedObjectFactory#containsDescription(org.eclipse.ecf.core.SharedObjectDescription)
	 */
	public boolean containsDescription(SharedObjectDescription scd) {
		return containsDescription0(scd);
	}

	protected boolean containsDescription0(SharedObjectDescription scd) {
		if (scd == null)
			return false;
		return sharedobjectdescriptions.containsKey(scd.getName());
	}

	protected SharedObjectDescription getDescription0(SharedObjectDescription scd) {
		if (scd == null)
			return null;
		return (SharedObjectDescription) sharedobjectdescriptions.get(scd.getName());
	}

	protected SharedObjectDescription getDescription0(String name) {
		if (name == null)
			return null;
		return (SharedObjectDescription) sharedobjectdescriptions.get(name);
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.ISharedObjectContainerFactory#getDescriptionByName(java.lang.String)
	 */
	public SharedObjectDescription getDescriptionByName(String name)
			throws SharedObjectInstantiationException {
		trace("getDescriptionByName(" + name + ")");
		SharedObjectDescription res = getDescription0(name);
		if (res == null) {
			throw new SharedObjectInstantiationException(
					"SharedObjectInstantiationException named '" + name + "' not found");
		}
		return res;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.ISharedObjectContainerFactory#createSharedObject(org.eclipse.ecf.core.SharedObjectDescription,
	 *      java.lang.String[], java.lang.Object[])
	 */
	public ISharedObject createSharedObject(SharedObjectDescription desc,
			String[] argTypes, Object[] args)
			throws SharedObjectInstantiationException {
		trace("createSharedObject(" + desc + ","
				+ Trace.convertStringAToString(argTypes) + ","
				+ Trace.convertObjectAToString(args) + ")");
		if (desc == null)
			throw new SharedObjectInstantiationException(
					"SharedObjectDescription cannot be null");
		SharedObjectDescription cd = getDescription0(desc);
		if (cd == null)
			throw new SharedObjectInstantiationException(
					"SharedObjectDescription named '" + desc.getName()
							+ "' not found");
		Class clazzes[] = null;
		ISharedObjectInstantiator instantiator = null;
		try {
			instantiator = (ISharedObjectInstantiator) cd.getInstantiator();
			clazzes = AbstractFactory.getClassesForTypes(argTypes, args, cd
					.getClassLoader());
		} catch (Exception e) {
			SharedObjectInstantiationException newexcept = new SharedObjectInstantiationException(
					"createSharedObject exception with description: " + desc + ": "
							+ e.getClass().getName() + ": " + e.getMessage());
			newexcept.setStackTrace(e.getStackTrace());
			dumpStack("Exception in createSharedObject", newexcept);
			throw newexcept;
		}
		if (instantiator == null)
			throw new SharedObjectInstantiationException(
					"Instantiator for SharedObjectDescription " + cd.getName()
							+ " is null");
		// Ask instantiator to actually create instance
		return (ISharedObject) instantiator.createInstance(desc, clazzes, args);
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.ISharedObjectContainerFactory#createSharedObject(java.lang.String)
	 */
	public ISharedObject createSharedObject(String descriptionName)
			throws SharedObjectInstantiationException {
		return createSharedObject(getDescriptionByName(descriptionName), null, null);
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.ISharedObjectContainerFactory#createSharedObject(java.lang.String,
	 *      java.lang.Object[])
	 */
	public ISharedObject createSharedObject(String descriptionName, Object[] args)
			throws SharedObjectInstantiationException {
		return createSharedObject(getDescriptionByName(descriptionName), null, args);
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.ISharedObjectContainerFactory#createSharedObject(java.lang.String,
	 *      java.lang.String[], java.lang.Object[])
	 */
	public ISharedObject createSharedObject(String descriptionName, String[] argsTypes,
			Object[] args) throws SharedObjectInstantiationException {
		return createSharedObject(getDescriptionByName(descriptionName), argsTypes,
				args);
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.ISharedObjectContainerFactory#removeDescription(org.eclipse.ecf.core.SharedObjectDescription)
	 */
	public SharedObjectDescription removeDescription(SharedObjectDescription scd) {
		trace("removeDescription(" + scd + ")");
		return removeDescription0(scd);
	}

	protected SharedObjectDescription removeDescription0(SharedObjectDescription n) {
		if (n == null)
			return null;
		return (SharedObjectDescription) sharedobjectdescriptions.remove(n.getName());
	}
}
 No newline at end of file