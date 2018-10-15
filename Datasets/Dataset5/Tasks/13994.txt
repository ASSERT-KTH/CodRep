public boolean isImporterForRemoteConfigType(String configType) {

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
import java.util.List;
import org.eclipse.core.runtime.*;
import org.eclipse.ecf.core.provider.IContainerInstantiator;
import org.eclipse.ecf.core.provider.IRemoteServiceContainerInstantiator;
import org.eclipse.ecf.core.util.Trace;
import org.eclipse.ecf.internal.core.ECFDebugOptions;
import org.eclipse.ecf.internal.core.ECFPlugin;

/**
 * Description of an {@link IContainer} type.  Instances of this class are used to represent {@link IContainerInstantiator}s
 * in the {@link ContainerFactory}
 * 
 * @see ContainerFactory IContainerInstantiator
 */
public class ContainerTypeDescription {

	private static final String[] EMPTY_ARRAY = new String[0];

	protected String name = null;

	protected String instantiatorClass = null;

	protected IContainerInstantiator instantiator = null;

	protected String description = null;

	protected int hashCode = 0;

	protected boolean server;

	protected boolean hidden;

	public ContainerTypeDescription(String name, String instantiatorClass, String description) {
		this(name, instantiatorClass, description, false, false);
	}

	public ContainerTypeDescription(String name, String instantiatorClass, String description, boolean server, boolean hidden) {
		Assert.isNotNull(name, "ContainerTypeDescription<init> name cannot be null"); //$NON-NLS-1$
		this.name = name;
		this.hashCode = name.hashCode();
		Assert.isNotNull(instantiatorClass, "ContainerTypeDescription<init> instantiatorClass cannot be null"); //$NON-NLS-1$
		this.instantiatorClass = instantiatorClass;
		this.description = description;
		this.server = server;
		this.hidden = hidden;
	}

	public ContainerTypeDescription(String name, IContainerInstantiator instantiator, String description) {
		this(name, instantiator, description, false, false);
	}

	public ContainerTypeDescription(String name, IContainerInstantiator inst, String desc, boolean server, boolean hidden) {
		Assert.isNotNull(name, "ContainerTypeDescription<init> name cannot be null"); //$NON-NLS-1$
		this.name = name;
		this.hashCode = name.hashCode();
		Assert.isNotNull(inst, "ContainerTypeDescription<init> instantiator instance cannot be null"); //$NON-NLS-1$
		this.instantiator = inst;
		this.description = desc;
		this.server = server;
		this.hidden = hidden;
	}

	/**
	 * Get ContainerTypeDescription name
	 * 
	 * @return String name for the ContainerTypeDescription. Will not be null.
	 */
	public String getName() {
		return name;
	}

	public boolean equals(Object other) {
		if (!(other instanceof ContainerTypeDescription))
			return false;
		ContainerTypeDescription scd = (ContainerTypeDescription) other;
		return scd.name.equals(name);
	}

	public int hashCode() {
		return hashCode;
	}

	public String toString() {
		StringBuffer b = new StringBuffer("ContainerTypeDescription["); //$NON-NLS-1$
		b.append("name=").append(name).append(";"); //$NON-NLS-1$ //$NON-NLS-2$
		if (instantiator == null)
			b.append("instantiatorClass=").append(instantiatorClass) //$NON-NLS-1$
					.append(";"); //$NON-NLS-1$
		else
			b.append("instantiator=").append(instantiator).append(";"); //$NON-NLS-1$ //$NON-NLS-2$
		b.append("desc=").append(description).append(";"); //$NON-NLS-1$ //$NON-NLS-2$
		return b.toString();
	}

	protected IContainerInstantiator getInstantiator() throws ClassNotFoundException, InstantiationException, IllegalAccessException {
		synchronized (this) {
			if (instantiator == null)
				initializeInstantiator();
			return instantiator;
		}
	}

	private void initializeInstantiator() throws ClassNotFoundException, InstantiationException, IllegalAccessException {
		// Load instantiator class
		Class clazz = Class.forName(instantiatorClass);
		// Make new instance
		instantiator = (IContainerInstantiator) clazz.newInstance();
	}

	/**
	 * Get the String description associated with this ContainerTypeDescription
	 * instance
	 * 
	 * @return String description. May be null.
	 */
	public String getDescription() {
		return description;
	}

	public boolean isServer() {
		return server;
	}

	public boolean isHidden() {
		return hidden;
	}

	/**
	 * Get array of supported adapters for this container type description. The
	 * returned array entries will be the fully qualified names of the adapter
	 * classes.
	 * 
	 * Note that the returned types do not guarantee that a subsequent call to
	 * {@link IContainer#getAdapter(Class)} with the same type name as a
	 * returned value will return a non-<code>null</code result. In other words, even if the
	 * class name is in the returned array, subsequent calls to
	 * {@link IContainer#getAdapter(Class)} may still return <code>null</code>.
	 * 
	 * @return String[] of supported adapters. The entries in the returned array
	 *         will be the fully qualified class names of adapters supported by
	 *         the given description. An empty string array (String[0]) will be
	 *         returned if no adapters are supported.
	 */
	public String[] getSupportedAdapterTypes() {
		String method = "getSupportedAdapterTypes"; //$NON-NLS-1$
		Trace.entering(ECFPlugin.PLUGIN_ID, ECFDebugOptions.METHODS_ENTERING, this.getClass(), method);
		String[] result = new String[0];
		try {
			String[] r = getInstantiator().getSupportedAdapterTypes(this);
			if (r != null)
				result = r;
		} catch (Exception e) {
			traceAndLogException(IStatus.ERROR, method, e);
		}
		List resultList = new ArrayList();
		for (int i = 0; i < result.length; i++) {
			resultList.add(result[i]);
		}
		if (!resultList.contains(IContainer.class.getName()))
			resultList.add(IContainer.class.getName());
		Trace.exiting(ECFPlugin.PLUGIN_ID, ECFDebugOptions.METHODS_EXITING, this.getClass(), method, result);
		return (String[]) resultList.toArray(new String[] {});
	}

	protected void traceAndLogException(int code, String method, Throwable e) {
		Trace.catching(ECFPlugin.PLUGIN_ID, ECFDebugOptions.EXCEPTIONS_CATCHING, this.getClass(), method, e);
		ECFPlugin.getDefault().log(new Status(IStatus.ERROR, ECFPlugin.PLUGIN_ID, code, method, e));
	}

	/**
	 * Get array of parameter types for this ContainerTypeDescription. Each of
	 * the rows of the returned array specifies a Class[] of parameter types.
	 * These parameter types correspond to the types of Objects that can be
	 * passed into the second parameter of
	 * {@link IContainerInstantiator#createInstance(ContainerTypeDescription, Object[])}.
	 * For example, if this method returns a Class [] = {{ String.class,
	 * String.class }, { String.class }} this indicates that a call to
	 * createInstance(description,new String[] { "hello", "there" }) and a call
	 * to createInstance(description,new String[] { "hello" }) will be
	 * understood by the underlying provider implementation.
	 * 
	 * @return Class[][] array of Class arrays. Each row corresponds to a
	 *         Class[] that describes the types of Objects for second parameter
	 *         to
	 *         {@link IContainerInstantiator#createInstance(ContainerTypeDescription, Object[])}.
	 *         If no parameter types are understood as arguments, a Class[0][0]
	 *         array will be returned
	 */
	public Class[][] getSupportedParameterTypes() {
		String method = "getParameterTypes"; //$NON-NLS-1$
		Trace.entering(ECFPlugin.PLUGIN_ID, ECFDebugOptions.METHODS_ENTERING, this.getClass(), method);
		Class[][] result = new Class[0][0];
		try {
			Class[][] r = getInstantiator().getSupportedParameterTypes(this);
			if (r != null)
				result = r;
		} catch (Exception e) {
			traceAndLogException(IStatus.ERROR, method, e);
		}
		Trace.exiting(ECFPlugin.PLUGIN_ID, ECFDebugOptions.METHODS_EXITING, this.getClass(), method, result);
		return result;
	}

	/**
	 * @return String[] of container's intents.
	 * 
	 * @since 3.0
	 */
	public String[] getSupportedIntents() {
		String method = "getSupportedIntents"; //$NON-NLS-1$
		Trace.entering(ECFPlugin.PLUGIN_ID, ECFDebugOptions.METHODS_ENTERING, this.getClass(), method);
		String[] result = EMPTY_ARRAY;
		try {
			IContainerInstantiator ci = getInstantiator();
			return (ci instanceof IRemoteServiceContainerInstantiator) ? ((IRemoteServiceContainerInstantiator) ci).getSupportedIntents(this) : result;
		} catch (Exception e) {
			traceAndLogException(IStatus.ERROR, method, e);
		}
		Trace.exiting(ECFPlugin.PLUGIN_ID, ECFDebugOptions.METHODS_EXITING, this.getClass(), method, result);
		return result;
	}

	/**
	 * @since 4.0
	 */
	public String[] getSupportedConfigTypes() {
		String method = "getSupportedConfigTypes"; //$NON-NLS-1$
		Trace.entering(ECFPlugin.PLUGIN_ID, ECFDebugOptions.METHODS_ENTERING, this.getClass(), method);
		String[] result = EMPTY_ARRAY;
		try {
			IContainerInstantiator ci = getInstantiator();
			return (ci instanceof IRemoteServiceContainerInstantiator) ? ((IRemoteServiceContainerInstantiator) ci).getSupportedConfigTypes(this) : new String[] {getName()};
		} catch (Exception e) {
			traceAndLogException(IStatus.ERROR, method, e);
		}
		Trace.exiting(ECFPlugin.PLUGIN_ID, ECFDebugOptions.METHODS_EXITING, this.getClass(), method, result);
		return result;
	}

	/**
	 * @since 4.0
	 */
	public boolean isImporter(String configType) {
		if (configType == null)
			return false;
		String method = "isImporter"; //$NON-NLS-1$
		Trace.entering(ECFPlugin.PLUGIN_ID, ECFDebugOptions.METHODS_ENTERING, this.getClass(), method);
		try {
			IContainerInstantiator ci = getInstantiator();
			return (ci instanceof IRemoteServiceContainerInstantiator) ? ((IRemoteServiceContainerInstantiator) ci).isImporterForRemoteConfigType(this, configType) : false;
		} catch (Exception e) {
			traceAndLogException(IStatus.ERROR, method, e);
			return false;
		}
	}
}
 No newline at end of file