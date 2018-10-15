public static final String START_EPOINT = ECFNAMESPACE + ".startup";

/*******************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.internal.core;

import java.util.Iterator;
import java.util.Map;
import java.util.MissingResourceException;
import java.util.Properties;
import java.util.ResourceBundle;
import java.util.WeakHashMap;
import org.eclipse.core.runtime.CoreException;
import org.eclipse.core.runtime.IConfigurationElement;
import org.eclipse.core.runtime.IExtension;
import org.eclipse.core.runtime.IExtensionDelta;
import org.eclipse.core.runtime.IExtensionPoint;
import org.eclipse.core.runtime.IExtensionRegistry;
import org.eclipse.core.runtime.ILog;
import org.eclipse.core.runtime.IRegistryChangeEvent;
import org.eclipse.core.runtime.IRegistryChangeListener;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Platform;
import org.eclipse.core.runtime.Plugin;
import org.eclipse.core.runtime.Status;
import org.eclipse.ecf.core.ContainerFactory;
import org.eclipse.ecf.core.ContainerTypeDescription;
import org.eclipse.ecf.core.IContainerFactory;
import org.eclipse.ecf.core.ISharedObjectFactory;
import org.eclipse.ecf.core.SharedObjectFactory;
import org.eclipse.ecf.core.SharedObjectTypeDescription;
import org.eclipse.ecf.core.comm.ConnectionFactory;
import org.eclipse.ecf.core.comm.ConnectionTypeDescription;
import org.eclipse.ecf.core.comm.provider.ISynchAsynchConnectionInstantiator;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.core.identity.IIDFactory;
import org.eclipse.ecf.core.identity.Namespace;
import org.eclipse.ecf.core.provider.IContainerInstantiator;
import org.eclipse.ecf.core.provider.ISharedObjectInstantiator;
import org.eclipse.ecf.core.start.ECFStartJob;
import org.eclipse.ecf.core.start.IECFStart;
import org.osgi.framework.BundleContext;

public class ECFPlugin extends Plugin {
	protected static Trace trace = null;
	public static final String ECFNAMESPACE = "org.eclipse.ecf";
	public static final String NAMESPACE_EPOINT = ECFNAMESPACE + ".namespace";
	public static final String CONTAINER_FACTORY_EPOINT = ECFNAMESPACE
			+ ".containerFactory";
	public static final String SHAREDOBJECT_FACTORY_EPOINT = ECFNAMESPACE
			+ ".sharedObjectFactory";
	public static final String COMM_FACTORY_EPOINT = ECFNAMESPACE
			+ ".connectionFactory";
	public static final String START_EPOINT = ECFNAMESPACE + ".start";
	
	public static final String PLUGIN_RESOURCE_BUNDLE = ECFNAMESPACE
			+ ".ECFPluginResources";
	public static final String CLASS_ATTRIBUTE = "class";
	public static final String NAME_ATTRIBUTE = "name";
	public static final String DESCRIPTION_ATTRIBUTE = "description";
	public static final String ARG_ELEMENT_NAME = "defaultargument";
	public static final String ARG_TYPE_ATTRIBUTE = "type";
	public static final String VALUE_ATTRIBUTE = "value";
	public static final String PROPERTY_ELEMENT_NAME = "property";
	public static final int FACTORY_DOES_NOT_IMPLEMENT_ERRORCODE = 10;
	public static final int FACTORY_NAME_COLLISION_ERRORCODE = 20;
	public static final int INSTANTIATOR_DOES_NOT_IMPLEMENT_ERRORCODE = 30;
	public static final int INSTANTIATOR_NAME_COLLISION_ERRORCODE = 50;
	public static final int INSTANTIATOR_NAMESPACE_LOAD_ERRORCODE = 60;
	public static final int START_ERRORCODE = 70;
	// The shared instance.
	private static ECFPlugin plugin;
	// Resource bundle.
	private ResourceBundle resourceBundle;
	BundleContext bundlecontext = null;
	private Map disposables = new WeakHashMap();
	private IRegistryChangeListener registryManager = null;
	private static void debug(String msg) {
		if (Trace.ON && trace != null) {
			trace.msg(msg);
		}
	}
	private static void dumpStack(String msg, Throwable e) {
		if (Trace.ON && trace != null) {
			trace.dumpStack(e, msg);
		}
	}
	public ECFPlugin() {
		super();
		plugin = this;
		try {
			resourceBundle = ResourceBundle.getBundle(PLUGIN_RESOURCE_BUNDLE);
		} catch (MissingResourceException x) {
			resourceBundle = null;
		}
	}
	public void addDisposable(IDisposable disposable) {
		disposables.put(disposable, null);
	}
	public void removeDisposable(IDisposable disposable) {
		disposables.remove(disposable);
	}
	protected void fireDisposables() {
		for (Iterator i = disposables.keySet().iterator(); i.hasNext();) {
			IDisposable d = (IDisposable) i.next();
			if (d != null)
				d.dispose();
		}
	}
	public static void log(IStatus status) {
		if (status == null)
			return;
		ILog log = plugin.getLog();
		if (log != null) {
			log.log(status);
		} else {
			System.err.println("No log output.  Status Message: "
					+ status.getMessage());
		}
	}
	class DefaultArgs {
		String[] types;
		String[] defaults;
		String[] names;
		public DefaultArgs(String[] types, String[] defaults, String[] names) {
			this.types = types;
			this.defaults = defaults;
			this.names = names;
		}
		public String[] getDefaults() {
			return defaults;
		}
		public String[] getNames() {
			return names;
		}
		public String[] getTypes() {
			return types;
		}
	}
	protected DefaultArgs getDefaultArgs(IConfigurationElement[] argElements) {
		String[] argTypes = new String[0];
		String[] argDefaults = new String[0];
		String[] argNames = new String[0];
		if (argElements != null) {
			if (argElements.length > 0) {
				argTypes = new String[argElements.length];
				argDefaults = new String[argElements.length];
				argNames = new String[argElements.length];
				for (int i = 0; i < argElements.length; i++) {
					argTypes[i] = argElements[i]
							.getAttribute(ARG_TYPE_ATTRIBUTE);
					argDefaults[i] = argElements[i]
							.getAttribute(VALUE_ATTRIBUTE);
					argNames[i] = argElements[i].getAttribute(NAME_ATTRIBUTE);
				}
			}
		}
		return new DefaultArgs(argTypes, argDefaults, argNames);
	}
	protected Map getProperties(IConfigurationElement[] propertyElements) {
		Properties props = new Properties();
		if (propertyElements != null) {
			if (propertyElements.length > 0) {
				for (int i = 0; i < propertyElements.length; i++) {
					String name = propertyElements[i]
							.getAttribute(NAME_ATTRIBUTE);
					String value = propertyElements[i]
							.getAttribute(VALUE_ATTRIBUTE);
					if (name != null && !name.equals("") && value != null
							&& !value.equals("")) {
						props.setProperty(name, value);
					}
				}
			}
		}
		return props;
	}
	/**
	 * Remove extensions for container factory extension point
	 * 
	 * @param members
	 *            the members to remove
	 */
	protected void removeContainerFactoryExtensions(
			IConfigurationElement[] members) {
		String bundleName = getDefault().getBundle().getSymbolicName();
		// For each configuration element
		for (int m = 0; m < members.length; m++) {
			IConfigurationElement member = members[m];
			// Get the label of the extender plugin and the ID of the extension.
			IExtension extension = member.getDeclaringExtension();
			String name = null;
			try {
				// Get name and get version, if available
				name = member.getAttribute(NAME_ATTRIBUTE);
				if (name == null) {
					name = member.getAttribute(CLASS_ATTRIBUTE);
				}
				IContainerFactory factory = ContainerFactory.getDefault();
				ContainerTypeDescription cd = factory
						.getDescriptionByName(name);
				if (cd == null || !factory.containsDescription(cd)) {
					continue;
				}
				// remove
				factory.removeDescription(cd);
				debug("removeContainerExtension:removed description from factory:"
						+ cd);
			} catch (Exception e) {
				log(getStatusForContException(extension, bundleName, name));
				dumpStack("Exception in removeContainerExtension", e);
			}
		}
	}
	/**
	 * Add container factory extension point extensions
	 * 
	 * @param members
	 *            to add
	 */
	protected void addContainerFactoryExtensions(IConfigurationElement[] members) {
		String bundleName = getDefault().getBundle().getSymbolicName();
		// For each configuration element
		for (int m = 0; m < members.length; m++) {
			IConfigurationElement member = members[m];
			// Get the label of the extender plugin and the ID of the extension.
			IExtension extension = member.getDeclaringExtension();
			Object exten = null;
			String name = null;
			try {
				// The only required attribute is "class"
				exten = member.createExecutableExtension(CLASS_ATTRIBUTE);
				String clazz = exten.getClass().getName();
				// Get name and get version, if available
				name = member.getAttribute(NAME_ATTRIBUTE);
				if (name == null) {
					name = clazz;
				}
				// Get description, if present
				String description = member.getAttribute(DESCRIPTION_ATTRIBUTE);
				if (description == null) {
					description = "";
				}
				// Get any arguments
				DefaultArgs defaults = getDefaultArgs(member
						.getChildren(ARG_ELEMENT_NAME));
				// Get any property elements
				Map properties = getProperties(member
						.getChildren(PROPERTY_ELEMENT_NAME));
				// Now make description instance
				ContainerTypeDescription scd = new ContainerTypeDescription(
						name, (IContainerInstantiator) exten, description,
						defaults.getTypes(), defaults.getDefaults(), defaults
								.getNames(), properties);
				debug("addContainerExtensions:created description:" + scd);
				IContainerFactory factory = ContainerFactory.getDefault();
				if (factory.containsDescription(scd)) {
					throw new CoreException(getStatusForContException(
							extension, bundleName, name));
				}
				// Now add the description and we're ready to go.
				factory.addDescription(scd);
				debug("addContainerExtensions:added description to factory:"
						+ scd);
			} catch (CoreException e) {
				log(e.getStatus());
				dumpStack("CoreException in addContainerExtensions", e);
			} catch (Exception e) {
				log(getStatusForContException(extension, bundleName, name));
				dumpStack("Exception in addContainerExtensions", e);
			}
		}
	}
	/**
	 * Setup container factory extension point
	 * 
	 * @param context
	 *            the BundleContext for this bundle
	 */
	protected void setupContainerFactoryExtensionPoint(BundleContext bc) {
		IExtensionRegistry reg = Platform.getExtensionRegistry();
		IExtensionPoint extensionPoint = reg
				.getExtensionPoint(CONTAINER_FACTORY_EPOINT);
		if (extensionPoint == null) {
			return;
		}
		addContainerFactoryExtensions(extensionPoint.getConfigurationElements());
	}
	/**
	 * Remove extensions for shared object extension point
	 * 
	 * @param members
	 *            the members to remove
	 */
	protected void removeSharedObjectExtensions(IConfigurationElement[] members) {
		String bundleName = getDefault().getBundle().getSymbolicName();
		for (int m = 0; m < members.length; m++) {
			IConfigurationElement member = members[m];
			String name = null;
			IExtension extension = member.getDeclaringExtension();
			try {
				name = member.getAttribute(NAME_ATTRIBUTE);
				if (name == null) {
					name = member.getAttribute(CLASS_ATTRIBUTE);
				}
				if (name == null)
					continue;
				ISharedObjectFactory factory = SharedObjectFactory.getDefault();
				SharedObjectTypeDescription sd = factory
						.getDescriptionByName(name);
				if (sd == null || !factory.containsDescription(sd)) {
					continue;
				}
				// remove
				factory.removeDescription(sd);
				debug("removeSharedObjectExtensions:removed description from factory:"
						+ sd);
			} catch (Exception e) {
				log(getStatusForContException(extension, bundleName, name));
				dumpStack("Exception in removeSharedObjectExtensions", e);
			}
		}
	}
	/**
	 * Add shared object extension point extensions
	 * 
	 * @param members
	 *            to add
	 */
	protected void addSharedObjectExtensions(IConfigurationElement[] members) {
		String bundleName = getDefault().getBundle().getSymbolicName();
		// For each configuration element
		for (int m = 0; m < members.length; m++) {
			IConfigurationElement member = members[m];
			// Get the label of the extender plugin and the ID of the extension.
			IExtension extension = member.getDeclaringExtension();
			ISharedObjectInstantiator exten = null;
			String name = null;
			try {
				// The only required attribute is "class"
				exten = (ISharedObjectInstantiator) member
						.createExecutableExtension(CLASS_ATTRIBUTE);
				name = member.getAttribute(NAME_ATTRIBUTE);
				if (name == null) {
					name = member.getAttribute(CLASS_ATTRIBUTE);
				}
				// Get description, if present
				String description = member.getAttribute(DESCRIPTION_ATTRIBUTE);
				if (description == null) {
					description = "";
				}
				// Get any property elements
				Map properties = getProperties(member
						.getChildren(PROPERTY_ELEMENT_NAME));
				// Now make description instance
				SharedObjectTypeDescription scd = new SharedObjectTypeDescription(
						name, exten, description, properties);
				debug("setupSharedObjectExtensionPoint:created description:"
						+ scd);
				ISharedObjectFactory factory = SharedObjectFactory.getDefault();
				if (factory.containsDescription(scd)) {
					throw new CoreException(getStatusForContException(
							extension, bundleName, name));
				}
				// Now add the description and we're ready to go.
				factory.addDescription(scd);
				debug("setupSharedObjectExtensionPoint:added description to factory:"
						+ scd);
			} catch (CoreException e) {
				log(e.getStatus());
				dumpStack("CoreException in setupSharedObjectExtensionPoint", e);
			} catch (Exception e) {
				log(getStatusForContException(extension, bundleName, name));
				dumpStack("Exception in setupSharedObjectExtensionPoint", e);
			}
		}
	}
	/**
	 * Setup shared object extension point
	 * 
	 * @param context
	 *            the BundleContext for this bundle
	 */
	protected void setupSharedObjectExtensionPoint(BundleContext bc) {
		IExtensionRegistry reg = Platform.getExtensionRegistry();
		IExtensionPoint extensionPoint = reg
				.getExtensionPoint(SHAREDOBJECT_FACTORY_EPOINT);
		if (extensionPoint == null) {
			return;
		}
		addSharedObjectExtensions(extensionPoint.getConfigurationElements());
	}
	/**
	 * Remove extensions for identity namespace extension point
	 * 
	 * @param members
	 *            the members to remove
	 */
	protected void removeNamespaceExtensions(IConfigurationElement[] members) {
		String bundleName = getDefault().getBundle().getSymbolicName();
		for (int m = 0; m < members.length; m++) {
			IConfigurationElement member = members[m];
			String name = null;
			IExtension extension = member.getDeclaringExtension();
			try {
				name = member.getAttribute(NAME_ATTRIBUTE);
				if (name == null) {
					name = member.getAttribute(CLASS_ATTRIBUTE);
				}
				if (name == null)
					continue;
				IIDFactory factory = IDFactory.getDefault();
				Namespace n = factory.getNamespaceByName(name);
				if (n == null || !factory.containsNamespace(n)) {
					continue;
				}
				// remove
				factory.removeNamespace(n);
				debug("removeIdentityExtensions:removed namespace from factory:"
						+ n);
			} catch (Exception e) {
				log(getStatusForContException(extension, bundleName, name));
				dumpStack("Exception in removeIdentityExtensions", e);
			}
		}
	}
	/**
	 * Add identity namespace extension point extensions
	 * 
	 * @param members
	 *            to add
	 */
	protected void addNamespaceExtensions(IConfigurationElement[] members) {
		String bundleName = getDefault().getBundle().getSymbolicName();
		// For each service:
		for (int m = 0; m < members.length; m++) {
			IConfigurationElement member = members[m];
			// Get the label of the extender plugin and the ID of the
			// extension.
			IExtension extension = member.getDeclaringExtension();
			String nsName = null;
			try {
				Namespace ns = (Namespace) member
						.createExecutableExtension(CLASS_ATTRIBUTE);
				String clazz = ns.getClass().getName();
				nsName = member.getAttribute(NAME_ATTRIBUTE);
				if (nsName == null) {
					nsName = clazz;
				}
				String nsDescription = member
						.getAttribute(DESCRIPTION_ATTRIBUTE);
				ns.initialize(nsName, nsDescription);
				debug("addNamespaceExtensions:created namespace:" + ns);
				if (IDFactory.getDefault().containsNamespace(ns)) {
					throw new CoreException(getStatusForIDException(extension,
							bundleName, nsName));
				}
				// Now add to known namespaces
				IDFactory.getDefault().addNamespace(ns);
				debug("addNamespaceExtensions:added namespace to factory:" + ns);
			} catch (CoreException e) {
				log(e.getStatus());
				dumpStack("Exception in setupIdentityExtensionPoint", e);
			} catch (Exception e) {
				log(getStatusForIDException(extension, bundleName, nsName));
				dumpStack("Exception in setupIdentityExtensionPoint", e);
			}
		}
	}
	/**
	 * Setup identity namespace extension point
	 * 
	 * @param context
	 *            the BundleContext for this bundle
	 */
	protected void setupNamespaceExtensionPoint(BundleContext context) {
		// Process extension points
		IExtensionRegistry reg = Platform.getExtensionRegistry();
		IExtensionPoint extensionPoint = reg
				.getExtensionPoint(NAMESPACE_EPOINT);
		if (extensionPoint == null) {
			return;
		}
		addNamespaceExtensions(extensionPoint.getConfigurationElements());
	}
	/**
	 * Remove extensions for comm extension point
	 * 
	 * @param members
	 *            the members to remove
	 */
	protected void removeCommExtensions(IConfigurationElement[] members) {
		String bundleName = getDefault().getBundle().getSymbolicName();
		for (int m = 0; m < members.length; m++) {
			IConfigurationElement member = members[m];
			String name = null;
			IExtension extension = member.getDeclaringExtension();
			try {
				name = member.getAttribute(NAME_ATTRIBUTE);
				if (name == null) {
					name = member.getAttribute(CLASS_ATTRIBUTE);
				}
				if (name == null)
					continue;
				ConnectionTypeDescription cd = ConnectionFactory
						.getDescriptionByName(name);
				if (cd == null || !ConnectionFactory.containsDescription(cd)) {
					continue;
				}
				// remove
				ConnectionFactory.removeDescription(cd);
				debug("removeCommExtensions:removed connection description:"
						+ cd);
			} catch (Exception e) {
				log(getStatusForContException(extension, bundleName, name));
				dumpStack("Exception in removeCommExtensions", e);
			}
		}
	}
	/**
	 * Add comm extension point extensions
	 * 
	 * @param members
	 *            to add
	 */
	protected void addCommExtensions(IConfigurationElement[] members) {
		String bundleName = getDefault().getBundle().getSymbolicName();
		// For each configuration element
		for (int m = 0; m < members.length; m++) {
			IConfigurationElement member = members[m];
			// Get the label of the extender plugin and the ID of the extension.
			IExtension extension = member.getDeclaringExtension();
			Object exten = null;
			String name = null;
			try {
				// The only required attribute is "instantiatorClass"
				exten = member.createExecutableExtension(CLASS_ATTRIBUTE);
				// Verify that object implements
				// ISynchAsynchConnectionInstantiator
				String clazz = exten.getClass().getName();
				// Get name and get version, if available
				name = member.getAttribute(NAME_ATTRIBUTE);
				if (name == null) {
					name = clazz;
				}
				String description = member.getAttribute(DESCRIPTION_ATTRIBUTE);
				if (description == null) {
					description = "";
				}
				// Get any arguments
				// Get any arguments
				DefaultArgs defaults = getDefaultArgs(member
						.getChildren(ARG_ELEMENT_NAME));
				ConnectionTypeDescription cd = new ConnectionTypeDescription(
						name, (ISynchAsynchConnectionInstantiator) exten,
						description, defaults.getTypes(), defaults
								.getDefaults(), defaults.getNames());
				debug("setupCommExtensionPoint:created description:" + cd);
				if (ConnectionFactory.containsDescription(cd)) {
					// It's already there...log and throw as we can't use the
					// same named factory
					IStatus s = new Status(
							Status.ERROR,
							bundleName,
							FACTORY_NAME_COLLISION_ERRORCODE,
							getResourceString("ExtPointError.CommNameCollisionPrefix")
									+ name
									+ getResourceString("ExtPointError.CommNameCollisionSuffix")
									+ extension
											.getExtensionPointUniqueIdentifier(),
							null);
					log(s);
					throw new CoreException(getStatusForCommException(
							extension, bundleName, name));
				}
				// Now add the description and we're ready to go.
				ConnectionFactory.addDescription(cd);
				debug("setupCommExtensionPoint:added description to factory:"
						+ cd);
			} catch (CoreException e) {
				log(e.getStatus());
				dumpStack("CoreException in setupCommExtensionPoint", e);
			} catch (Exception e) {
				log(getStatusForCommException(extension, bundleName, name));
				dumpStack("Exception in setupCommExtensionPoint", e);
			}
		}
	}
	protected void setupCommExtensionPoint(BundleContext bc) {
		IExtensionRegistry reg = Platform.getExtensionRegistry();
		IExtensionPoint extensionPoint = reg
				.getExtensionPoint(COMM_FACTORY_EPOINT);
		if (extensionPoint == null) {
			return;
		}
		addCommExtensions(extensionPoint.getConfigurationElements());
	}
	protected void setupStartExtensionPoint(BundleContext bc) {
		IExtensionRegistry reg = Platform.getExtensionRegistry();
		IExtensionPoint extensionPoint = reg
				.getExtensionPoint(START_EPOINT);
		if (extensionPoint == null) {
			return;
		}
		startStartExtensions(extensionPoint.getConfigurationElements());
	}
	protected void startStartExtensions(IConfigurationElement[] configurationElements) {
		String bundleName = getDefault().getBundle().getSymbolicName();
		// For each configuration element
		for (int m = 0; m < configurationElements.length; m++) {
			IConfigurationElement member = configurationElements[m];
			// Get the label of the extender plugin and the ID of the extension.
			IExtension extension = member.getDeclaringExtension();
			IECFStart exten = null;
			String name = null;
			try {
				// The only required attribute is "class"
				exten = (IECFStart) member.createExecutableExtension(CLASS_ATTRIBUTE);
				// Get name and get version, if available
				name = member.getAttribute(NAME_ATTRIBUTE);
				if (name == null) name = exten.getClass().getName();
				startExtension(name,exten);
			} catch (CoreException e) {
				log(e.getStatus());
				dumpStack("CoreException in startStartExtensions", e);
			} catch (Exception e) {
				log(getStatusForStartException(extension, bundleName, e));
				dumpStack("Exception in startStartExtensions", e);
			}
		}
	}
	private void startExtension(String name, IECFStart exten) {
		// Create job to do start, and schedule
		ECFStartJob job = new ECFStartJob(name,exten);
		job.schedule();
	}
	protected IStatus getStatusForCommException(IExtension ext,
			String bundleName, String name) {
		IStatus s = new Status(
				Status.ERROR,
				bundleName,
				FACTORY_NAME_COLLISION_ERRORCODE,
				getResourceString("ExtPointError.CommNameCollisionPrefix")
						+ name
						+ getResourceString("ExtPointError.CommNameCollisionSuffix")
						+ ext.getExtensionPointUniqueIdentifier(), null);
		return s;
	}
	protected IStatus getStatusForStartException(IExtension ext,
			String bundleName, Exception e) {
		IStatus s = new Status(
				Status.ERROR,
				bundleName,
				START_ERRORCODE,"Unknown start exception", e);
		return s;
	}
	protected IStatus getStatusForContException(IExtension ext,
			String bundleName, String name) {
		IStatus s = new Status(
				Status.ERROR,
				bundleName,
				FACTORY_NAME_COLLISION_ERRORCODE,
				getResourceString("ExtPointError.ContainerNameCollisionPrefix")
						+ name
						+ getResourceString("ExtPointError.ContainerNameCollisionSuffix")
						+ ext.getExtensionPointUniqueIdentifier(), null);
		return s;
	}
	protected IStatus getStatusForIDException(IExtension ext,
			String bundleName, String name) {
		IStatus s = new Status(
				Status.ERROR,
				bundleName,
				FACTORY_NAME_COLLISION_ERRORCODE,
				getResourceString("ExtPointError.IDNameCollisionPrefix")
						+ name
						+ getResourceString("ExtPointError.IDNameCollisionSuffix")
						+ ext.getExtensionPointUniqueIdentifier(), null);
		return s;
	}
	/**
	 * This method is called upon plug-in activation
	 */
	public void start(BundleContext context) throws Exception {
		super.start(context);
		trace = Trace.create("factoryinit");
		this.bundlecontext = context;
		this.registryManager = new ECFRegistryManager();
		Platform.getExtensionRegistry().addRegistryChangeListener(
				registryManager);
		setupContainerFactoryExtensionPoint(context);
		setupNamespaceExtensionPoint(context);
		setupCommExtensionPoint(context);
		setupSharedObjectExtensionPoint(context);
		setupStartExtensionPoint(context);
	}
	protected class ECFRegistryManager implements IRegistryChangeListener {
		public void registryChanged(IRegistryChangeEvent event) {
			IExtensionDelta delta[] = event.getExtensionDeltas(ECFNAMESPACE,
					"containerFactory");
			for (int i = 0; i < delta.length; i++) {
				switch (delta[i].getKind()) {
				case IExtensionDelta.ADDED:
					addContainerFactoryExtensions(delta[i].getExtension()
							.getConfigurationElements());
					break;
				case IExtensionDelta.REMOVED:
					removeContainerFactoryExtensions(delta[i].getExtension()
							.getConfigurationElements());
					break;
				}
			}
			delta = event.getExtensionDeltas(ECFNAMESPACE,
					"sharedObjectFactory");
			for (int i = 0; i < delta.length; i++) {
				switch (delta[i].getKind()) {
				case IExtensionDelta.ADDED:
					addSharedObjectExtensions(delta[i].getExtension()
							.getConfigurationElements());
					break;
				case IExtensionDelta.REMOVED:
					removeSharedObjectExtensions(delta[i].getExtension()
							.getConfigurationElements());
					break;
				}
			}
			delta = event.getExtensionDeltas(ECFNAMESPACE, "namespace");
			for (int i = 0; i < delta.length; i++) {
				switch (delta[i].getKind()) {
				case IExtensionDelta.ADDED:
					addNamespaceExtensions(delta[i].getExtension()
							.getConfigurationElements());
					break;
				case IExtensionDelta.REMOVED:
					removeNamespaceExtensions(delta[i].getExtension()
							.getConfigurationElements());
					break;
				}
			}
			delta = event.getExtensionDeltas(ECFNAMESPACE, "connectionFactory");
			for (int i = 0; i < delta.length; i++) {
				switch (delta[i].getKind()) {
				case IExtensionDelta.ADDED:
					addCommExtensions(delta[i].getExtension()
							.getConfigurationElements());
					break;
				case IExtensionDelta.REMOVED:
					removeCommExtensions(delta[i].getExtension()
							.getConfigurationElements());
					break;
				}
			}
		}
	}
	/**
	 * This method is called when the plug-in is stopped
	 */
	public void stop(BundleContext context) throws Exception {
		super.stop(context);
		fireDisposables();
		this.disposables = null;
		this.bundlecontext = null;
		Platform.getExtensionRegistry().removeRegistryChangeListener(
				registryManager);
		this.registryManager = null;
	}
	/**
	 * Returns the shared instance.
	 */
	public static ECFPlugin getDefault() {
		return plugin;
	}
	/**
	 * Returns the string from the plugin's resource bundle, or 'key' if not
	 * found.
	 */
	public static String getResourceString(String key) {
		ResourceBundle bundle = ECFPlugin.getDefault().getResourceBundle();
		try {
			return (bundle != null) ? bundle.getString(key) : "!" + key + "!";
		} catch (MissingResourceException e) {
			return "!" + key + "!";
		}
	}
	/**
	 * Returns the plugin's resource bundle,
	 */
	public ResourceBundle getResourceBundle() {
		return resourceBundle;
	}
}
 No newline at end of file