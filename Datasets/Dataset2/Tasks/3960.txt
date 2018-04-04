.getExtensionHandler(IExtensionHandlerKeys.ORG_COLUMBA_CORE_COMPONENT);

package org.columba.core.component;

import java.util.Enumeration;

import org.apache.commons.cli.CommandLine;
import org.columba.api.exception.PluginHandlerNotFoundException;
import org.columba.api.exception.ServiceNotFoundException;
import org.columba.api.plugin.IExtension;
import org.columba.api.plugin.IExtensionHandler;
import org.columba.api.plugin.IExtensionHandlerKeys;
import org.columba.api.plugin.IPluginManager;
import org.columba.core.services.ServiceRegistry;

public class ComponentManager implements IComponentPlugin {

	private static ComponentManager instance = new ComponentManager();

	private IExtensionHandler extensionHandler;

	private ComponentManager() {
		initDefaultPlugins();
	};

	public static ComponentManager getInstance() {
		return instance;
	}

	private IExtensionHandler getExtensionHandler() {
		if (extensionHandler == null) {
			try {
				// retrieve plugin manager instance
				IPluginManager pm = null;
				try {
					pm = (IPluginManager) ServiceRegistry
							.getInstance().getService(IPluginManager.class);
				} catch (ServiceNotFoundException e) {
					e.printStackTrace();
				}

				extensionHandler =  pm
						.getHandler(IExtensionHandlerKeys.ORG_COLUMBA_CORE_COMPONENT);
			} catch (PluginHandlerNotFoundException e) {
				e.printStackTrace();
			}
		}
		return extensionHandler;
	}

	public IComponentPlugin getPlugin(String id) {
		IComponentPlugin component = null;

		IExtension extension = getExtensionHandler().getExtension(id);

		try {
			component = (IComponentPlugin) extension.instanciateExtension(null);
		} catch (Exception e) {
			e.printStackTrace();
		}

		return component;
	}

	/**
	 * @see org.columba.core.component.IComponentPlugin#init()
	 */
	public void init() {
		Enumeration extensionEnumeration = getExtensionHandler()
				.getExtensionEnumeration();

		while (extensionEnumeration.hasMoreElements()) {
			IExtension ext = (IExtension) extensionEnumeration.nextElement();
			IComponentPlugin p;
			try {
				p = (IComponentPlugin) ext.instanciateExtension(null);
				p.init();
			} catch (Exception e) {
				e.printStackTrace();
			}
		}
	}

	/**
	 * @see org.columba.core.component.IComponentPlugin#postStartup()
	 */
	public void postStartup() {
		Enumeration extensionEnumeration = getExtensionHandler()
				.getExtensionEnumeration();

		while (extensionEnumeration.hasMoreElements()) {
			IExtension ext = (IExtension) extensionEnumeration.nextElement();
			IComponentPlugin p;
			try {
				p = (IComponentPlugin) ext.instanciateExtension(null);
				p.postStartup();
			} catch (Exception e) {
				e.printStackTrace();
			}
		}
	}

	/**
	 * @see org.columba.core.component.IComponentPlugin#registerCommandLineArguments()
	 */
	public void registerCommandLineArguments() {
		// init mail/addressbook internal components
		// FIXME
		// initDefaultPlugins();

		Enumeration extensionEnumeration = getExtensionHandler()
				.getExtensionEnumeration();

		while (extensionEnumeration.hasMoreElements()) {
			IExtension ext = (IExtension) extensionEnumeration.nextElement();
			IComponentPlugin p;
			try {
				p = (IComponentPlugin) ext.instanciateExtension(null);
				p.registerCommandLineArguments();
			} catch (Exception e) {
				e.printStackTrace();
			}

		}
	}

	/**
	 * @see org.columba.core.component.IComponentPlugin#handleCommandLineParameters(org.apache.commons.cli.CommandLine)
	 */
	public void handleCommandLineParameters(CommandLine commandLine) {
		Enumeration extensionEnumeration = getExtensionHandler()
				.getExtensionEnumeration();

		while (extensionEnumeration.hasMoreElements()) {
			IExtension ext = (IExtension) extensionEnumeration.nextElement();
			IComponentPlugin p;
			try {
				p = (IComponentPlugin) ext.instanciateExtension(null);
				p.handleCommandLineParameters(commandLine);
			} catch (Exception e) {
				e.printStackTrace();
			}
		}
	}

	private void initDefaultPlugins() {
		//getPlugin("MailComponent");
		//getPlugin("AddressbookComponent");
	}

}