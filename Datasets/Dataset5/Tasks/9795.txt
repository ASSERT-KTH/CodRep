help.append("Eclipse Communication Framework (ECF) Commands");

/*******************************************************************************
* Copyright (c) 2009 Composent, Inc. and others. All rights reserved. This
* program and the accompanying materials are made available under the terms of
* the Eclipse Public License v1.0 which accompanies this distribution, and is
* available at http://www.eclipse.org/legal/epl-v10.html
*
* Contributors:
*   Composent, Inc. - initial API and implementation
******************************************************************************/
package org.eclipse.ecf.internal.console;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Iterator;
import java.util.List;

import org.eclipse.ecf.core.ContainerTypeDescription;
import org.eclipse.ecf.core.IContainer;
import org.eclipse.ecf.core.IContainerFactory;
import org.eclipse.ecf.core.IContainerManager;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.core.identity.Namespace;
import org.eclipse.osgi.framework.console.CommandInterpreter;
import org.osgi.framework.BundleContext;
import org.osgi.util.tracker.ServiceTracker;

public class ECFCommandProvider implements
		org.eclipse.osgi.framework.console.CommandProvider {

	public static final String NEW_LINE = System.getProperty("line.separator", "\n"); //$NON-NLS-1$ //$NON-NLS-2$

	private BundleContext context;
	private ServiceTracker containerManagerTracker;
	
	public ECFCommandProvider(BundleContext context) {
		this.context = context;
	}
	
	private IContainerManager getContainerManager() {
		if (containerManagerTracker == null) {
			containerManagerTracker = new ServiceTracker(this.context,IContainerManager.class.getName(),null);
			containerManagerTracker.open();
		}
		return (IContainerManager) containerManagerTracker.getService();
	}
	
	private IContainerFactory getContainerFactory() {
		return getContainerManager().getContainerFactory();
	}
	
	public void dispose() {
		if (containerManagerTracker != null) {
			containerManagerTracker.close();
			containerManagerTracker = null;
		}
		this.context = null;
	}

	private IContainer createContainer(CommandInterpreter interpreter, String containerTypeDescriptionName, String[] args) {
		IContainerFactory containerFactory = getContainerFactory();
		try {
			if (containerTypeDescriptionName == null) return containerFactory.createContainer();
			else if (args == null) return containerFactory.createContainer(containerTypeDescriptionName);
			else return containerFactory.createContainer(containerTypeDescriptionName,args);
		} catch (Exception e) {
			printException(interpreter,"Could not create container with type="+containerTypeDescriptionName,e);
			return null;
		}
	}
	
	private void printException(CommandInterpreter interpreter, String message, Throwable t) {
		interpreter.println("--Exception--");
		if (message != null) interpreter.println(message);
		if (t != null) interpreter.printStackTrace(t);
		interpreter.println("--End Exception--");
	}

	private String[] getArgs(CommandInterpreter interpreter) {
		List result = new ArrayList();
		String arg = null;
		while ((arg = interpreter.nextArgument()) != null) result.add(arg);
		return (String[]) result.toArray(new String[] {});
	}
	
	private String[] getRemainingArgs(String[] args, int startPosition) {
		int targetLength = args.length-startPosition;
		String[] result = new String[targetLength];
		System.arraycopy(args, startPosition, result, 0, targetLength);
		return result;
	}
	
	public void _createcontainer(CommandInterpreter interpreter) {
		String[] args = getArgs(interpreter);
		String factoryName = (args.length==0)?null:args[0];
		String[] targetArgs = (args.length==0)?null:getRemainingArgs(args,1);
		IContainer c = createContainer(interpreter, factoryName, targetArgs);
		if (c != null) {
			interpreter.print("container created. ");
			printID(interpreter, c.getID());
		}
	}
	
	private void printContainer(CommandInterpreter interpreter, IContainer container, boolean verbose) {
		interpreter.println("--Container--");
		printID(interpreter, container.getID());
		if (verbose) {
			interpreter.print("\tclass=");
			interpreter.println(container.getClass().getName());
			ID connectedID = container.getConnectedID();
			if (connectedID != null) {
				interpreter.print("\tConnected to: ");
				printID(interpreter, connectedID);
			} else interpreter.println("\tNot connected.");
			Namespace ns = container.getConnectNamespace();
			if (ns != null) {
				interpreter.print("\tConnect namespace: ");
				interpreter.println(ns.getName());
			} else interpreter.println("\tNo connect namespace.");
			ContainerTypeDescription desc = getContainerManager().getContainerTypeDescription(container.getID());
			if (desc != null) printDescription(interpreter, desc);
		}
		interpreter.println("--End Container--");
	}
	
	private void printDescription(CommandInterpreter interpreter, ContainerTypeDescription desc) {
		interpreter.print("\tFactory name=");
		interpreter.println(desc.getName());
		interpreter.print("\tFactory description=");
		interpreter.println(desc.getDescription());
		String[] arr = desc.getSupportedIntents();
		if (arr != null) {
			interpreter.print("\tSupported intents=");
			interpreter.println(Arrays.asList(arr));
		}
		arr = desc.getSupportedConfigs();
		if (arr != null) {
			interpreter.print("\tSupported configs=");
			interpreter.println(Arrays.asList(arr));
		}
		arr = desc.getSupportedAdapterTypes();
		if (arr != null) {
			interpreter.print("\tSupported adapters=");
			interpreter.println(Arrays.asList(arr));
		}
		interpreter.println("\tHidden="+desc.isHidden());
		interpreter.println("\tServer="+desc.isServer());
	}
	
	public void _listcontainers(CommandInterpreter interpreter) {
		String[] args = getArgs(interpreter);
		boolean verbose = (args.length < 1)?false:new Boolean(args[0]).booleanValue();
		IContainer[] containers = getContainerManager().getAllContainers();
		if (containers == null || containers.length == 0) interpreter.println("No containers found.");
		for(int i=0; i < containers.length; i++) {
			printContainer(interpreter, containers[i], verbose);
		}
	}

	public void _listfactories(CommandInterpreter interpreter) {
		List descs = getContainerManager().getContainerFactory().getDescriptions();
		if (descs == null || descs.size() == 0) interpreter.println("No factories.");
		for(Iterator i=descs.iterator(); i.hasNext(); ) {
			ContainerTypeDescription desc = (ContainerTypeDescription) i.next();
			printDescription(interpreter, desc);
		}
	}

	private void printID(CommandInterpreter interpreter, ID id) {
		interpreter.print("\tID:");
		if (id == null) {
			interpreter.println("null");
			return;
		}
		interpreter.print("ns="+id.getNamespace().getName());
		interpreter.print(";name=");
		interpreter.print(id.getName());
		interpreter.println();
	}

	public void _destroycontainer(CommandInterpreter interpreter) {
		String[] args = getArgs(interpreter);
		if (args == null || args.length != 2) {
			interpreter.println("Incorrect number of arguments for container destroy");
			return;
		}
		ID id = createID(interpreter, args[0],args[1]);
		if (id == null) return;
		IContainer container = getContainerManager().removeContainer(id);
		if (container == null) {
			interpreter.println("Container not found to remove");
			return;
		}
		// Dispose the container instance
		container.dispose();
		interpreter.println("Container destroyed.");
	}
	
	private ID createID(CommandInterpreter interpreter, String namespace, String val) {
		try {
		return IDFactory.getDefault().createID(namespace, val);
		} catch (Exception e) {
			interpreter.printStackTrace(e);
			return null;
		}
	}

	public String getHelp() {
		StringBuffer help = new StringBuffer();
		help.append(NEW_LINE);
		help.append("---");
		help.append("ECF Commands");
		help.append("---");
		help.append(NEW_LINE);
		help.append("\tlistfactories -- List all container factories.");
		help.append(NEW_LINE);
		help.append("\tlistcontainers [verbose] -- List all existing containers.");
		help.append(NEW_LINE);
		help.append("\tcreatecontainer [<containerFactoryName> [<arg0> <arg1>...]] -- Create new container.");
		help.append(NEW_LINE);
		help.append("\tdestroycontainer <namespace> <id> -- Remove and dispose container specified by namespace/id combination.");
		help.append(NEW_LINE);
		return help.toString();
	}

}