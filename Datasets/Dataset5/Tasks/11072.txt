throw new IDCreateException(Messages.getString("GenericContainerInstantiator.ID_Cannot_Be_Null")); //$NON-NLS-1$

/*******************************************************************************
 * Copyright (c) 2004, 2007 Composent, Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.provider.generic;

import java.util.Arrays;
import java.util.HashSet;
import java.util.Iterator;
import java.util.Set;

import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Platform;
import org.eclipse.core.runtime.Status;
import org.eclipse.ecf.core.ContainerCreateException;
import org.eclipse.ecf.core.ContainerTypeDescription;
import org.eclipse.ecf.core.IContainer;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDCreateException;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.core.provider.IContainerInstantiator;
import org.eclipse.ecf.core.util.Trace;
import org.eclipse.ecf.internal.provider.ECFProviderDebugOptions;
import org.eclipse.ecf.internal.provider.ProviderPlugin;

public class GenericContainerInstantiator implements IContainerInstantiator {

	public static final String TCPCLIENT_NAME = "ecf.generic.client"; //$NON-NLS-1$

	public static final String TCPSERVER_NAME = "ecf.generic.server"; //$NON-NLS-1$

	private static final int CREATE_INSTANCE_ERROR_CODE = 4441;

	public GenericContainerInstantiator() {
		super();
	}

	protected ID getIDFromArg(Object arg) throws IDCreateException {
		if (arg == null)
			throw new IDCreateException("id cannot be null");
		if (arg instanceof ID)
			return (ID) arg;
		if (arg instanceof String) {
			String val = (String) arg;
			if (val.equals("")) { //$NON-NLS-1$
				return IDFactory.getDefault().createGUID();
			} else
				return IDFactory.getDefault().createStringID(val);
		} else if (arg instanceof Integer) {
			return IDFactory.getDefault()
					.createGUID(((Integer) arg).intValue());
		} else
			return IDFactory.getDefault().createGUID();
	}

	protected Integer getIntegerFromArg(Object arg) {
		if (arg == null)
			return new Integer(-1);
		if (arg instanceof Integer)
			return (Integer) arg;
		else if (arg instanceof String) {
			return new Integer((String) arg);
		} else
			return new Integer(-1);
	}

	protected class GenericContainerArgs {
		ID id;

		Integer keepAlive;

		public GenericContainerArgs(ID id, Integer keepAlive) {
			this.id = id;
			this.keepAlive = keepAlive;
		}

		public ID getID() {
			return id;
		}

		public Integer getKeepAlive() {
			return keepAlive;
		}
	}

	protected GenericContainerArgs getClientArgs(String[] argDefaults,
			Object[] args) throws IDCreateException {
		ID newID = null;
		Integer ka = null;
		if (argDefaults != null && argDefaults.length > 0) {
			if (argDefaults.length == 2) {
				newID = getIDFromArg(argDefaults[0]);
				ka = getIntegerFromArg(argDefaults[1]);
			} else
				ka = getIntegerFromArg(argDefaults[0]);
		}
		if (args != null && args.length > 0) {
			if (args.length == 2) {
				newID = getIDFromArg(args[0]);
				ka = getIntegerFromArg(args[1]);
			} else
				ka = getIntegerFromArg(args[0]);
		}
		if (newID == null)
			newID = IDFactory.getDefault().createGUID();
		if (ka == null)
			ka = new Integer(0);
		return new GenericContainerArgs(newID, ka);
	}

	protected boolean isClient(ContainerTypeDescription description) {
		if (description.getName().equals(TCPSERVER_NAME))
			return false;
		return true;
	}

	protected GenericContainerArgs getServerArgs(String[] argDefaults,
			Object[] args) throws IDCreateException {
		ID newID = null;
		Integer ka = null;
		if (argDefaults != null && argDefaults.length > 0) {
			if (argDefaults.length == 2) {
				newID = getIDFromArg(argDefaults[0]);
				ka = getIntegerFromArg(argDefaults[1]);
			} else
				newID = getIDFromArg(argDefaults[0]);
		}
		if (args != null && args.length > 0) {
			if (args.length == 2) {
				newID = getIDFromArg(args[0]);
				ka = getIntegerFromArg(args[1]);
			} else
				newID = getIDFromArg(args[0]);
		}
		if (newID == null)
			newID = IDFactory.getDefault().createGUID();
		if (ka == null)
			ka = new Integer(0);
		return new GenericContainerArgs(newID, ka);
	}

	public IContainer createInstance(ContainerTypeDescription description,
			Object[] args) throws ContainerCreateException {
		boolean isClient = isClient(description);
		try {
			GenericContainerArgs gcargs = null;
			String[] argDefaults = description.getParameterDefaults();
			if (isClient)
				gcargs = getClientArgs(argDefaults, args);
			else
				gcargs = getServerArgs(argDefaults, args);
			// new ID must not be null
			if (isClient) {
				return new TCPClientSOContainer(new SOContainerConfig(gcargs
						.getID()), gcargs.getKeepAlive().intValue());
			} else {
				return new TCPServerSOContainer(new SOContainerConfig(gcargs
						.getID()), gcargs.getKeepAlive().intValue());
			}
		} catch (Exception e) {
			Trace.catching(ProviderPlugin.getDefault(),
					ECFProviderDebugOptions.EXCEPTIONS_CATCHING, this
							.getClass(), "createInstance", e); //$NON-NLS-1$
			ProviderPlugin.getDefault().getLog().log(
					new Status(IStatus.ERROR, ProviderPlugin.PLUGIN_ID,
							CREATE_INSTANCE_ERROR_CODE, "createInstance", e)); //$NON-NLS-1$
			Trace.throwing(ProviderPlugin.getDefault(),
					ECFProviderDebugOptions.EXCEPTIONS_THROWING, this
							.getClass(), "createInstance", e); //$NON-NLS-1$
			throw new ContainerCreateException("createInstance", e); //$NON-NLS-1$
		}
	}

	protected Set getAdaptersForClass(Class clazz) {
		Set result = new HashSet();
		result.addAll(Arrays.asList(Platform.getAdapterManager()
				.computeAdapterTypes(clazz)));
		return result;
	}

	protected Set getInterfacesForClass(Set s, Class clazz) {
		if (clazz.equals(Object.class))
			return s;
		else
			s.addAll(getInterfacesForClass(s, clazz.getSuperclass()));
		s.addAll(Arrays.asList(clazz.getInterfaces()));
		return s;
	}

	protected Set getInterfacesForClass(Class clazz) {
		Set clazzes = getInterfacesForClass(new HashSet(), clazz);
		int index = 0;
		Set result = new HashSet();
		for (Iterator i = clazzes.iterator(); i.hasNext(); index++)
			result.add(((Class) i.next()).getName());
		return result;
	}

	protected String[] getInterfacesAndAdaptersForClass(Class clazz) {
		Set result = getAdaptersForClass(clazz);
		result.addAll(getInterfacesForClass(clazz));
		return (String[]) result.toArray(new String[] {});
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.provider.IContainerInstantiator#getSupportedAdapterTypes(org.eclipse.ecf.core.ContainerTypeDescription)
	 */
	public String[] getSupportedAdapterTypes(
			ContainerTypeDescription description) {
		if (!isClient(description))
			return getInterfacesAndAdaptersForClass(TCPServerSOContainer.class);
		else
			return getInterfacesAndAdaptersForClass(TCPClientSOContainer.class);
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.provider.IContainerInstantiator#getSupportedParameterTypes(org.eclipse.ecf.core.ContainerTypeDescription)
	 */
	public Class[][] getSupportedParameterTypes(
			ContainerTypeDescription description) {
		if (!isClient(description))
			return new Class[][] { { ID.class }, { ID.class, Integer.class } };
		else
			return new Class[][] { {}, { ID.class },
					{ ID.class, Integer.class } };
	}
}
 No newline at end of file