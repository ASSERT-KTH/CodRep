handler = PluginManager.getInstance().getExtensionHandler(

// The contents of this file are subject to the Mozilla Public License Version
// 1.1
//(the "License"); you may not use this file except in compliance with the
//License. You may obtain a copy of the License at http://www.mozilla.org/MPL/
//
//Software distributed under the License is distributed on an "AS IS" basis,
//WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
//for the specific language governing rights and
//limitations under the License.
//
//The Original Code is "The Columba Project"
//
//The Initial Developers of the Original Code are Frederik Dietz and Timo
// Stich.
//Portions created by Frederik Dietz and Timo Stich are Copyright (C) 2003.
//
//All Rights Reserved.
package org.columba.core.scripting.service;

import java.util.Enumeration;
import java.util.logging.Level;
import java.util.logging.Logger;

import org.columba.api.exception.PluginException;
import org.columba.api.exception.PluginHandlerNotFoundException;
import org.columba.api.plugin.IExtensionHandler;
import org.columba.api.plugin.IExtensionHandlerKeys;
import org.columba.api.plugin.IExtensionInterface;
import org.columba.core.logging.Logging;
import org.columba.core.plugin.Extension;
import org.columba.core.plugin.PluginManager;

public class ServiceManager {

	private static final Logger LOG = Logger
			.getLogger("org.columba.core.scripting.service.ServiceManager");

	private static ServiceManager instance = new ServiceManager();

	private IExtensionHandler handler;

	private ServiceManager() {
		try {
			handler = PluginManager.getInstance().getHandler(
					IExtensionHandlerKeys.ORG_COLUMBA_CORE_SERVICE);
		} catch (PluginHandlerNotFoundException e) {
			e.printStackTrace();
		}
	}

	public static ServiceManager getInstance() {
		return instance;
	}

	/**
	 * Retrieve service instance. <code>ExtensionHandler</code> automatically
	 * handles singleton extensions. We don't need to cache instances.
	 * 
	 * @param extension
	 *            extension metadata
	 * @return instance of extension interface
	 */
	private IColumbaService getServiceInstance(Extension extension) {

		IExtensionInterface service = null;
		try {
			service = (IExtensionInterface) extension
					.instanciateExtension(new Object[] {});
		} catch (PluginException e1) {
			LOG.severe("Failed to load service: " + e1.getMessage());

			if (Logging.DEBUG)
				e1.printStackTrace();

			return null;
		}

		if (!(service instanceof IColumbaService)) {
			LOG.log(Level.WARNING,
					"Service plugin doesn't explicitly declare an "
							+ "IColumbaService interface. Service ignored...");
			return null;
		}

		return (IColumbaService) service;

	}

	/**
	 * Instanciate all services.
	 * 
	 */
	public void initServices() {
		Enumeration e = handler.getExtensionEnumeration();
		while (e.hasMoreElements()) {
			Extension extension = (Extension) e.nextElement();

			// retrieving the instance for the first time
			// creates an instance in ExtensionHandler subclass
			// 
			// instance reference is kept in hashmap automatically
			IColumbaService service = getServiceInstance(extension);
			service.initService();

		}

	}

	public void disposeServices() {
		Enumeration e = handler.getExtensionEnumeration();
		while (e.hasMoreElements()) {
			Extension extension = (Extension) e.nextElement();
			IColumbaService service = getServiceInstance(extension);
			service.disposeService();
		}
	}

	public void startServices() {
		Enumeration e = handler.getExtensionEnumeration();
		while (e.hasMoreElements()) {
			Extension extension = (Extension) e.nextElement();
			IColumbaService service = getServiceInstance(extension);
			service.startService();
		}

	}

	public void stopServices() {
		Enumeration e = handler.getExtensionEnumeration();
		while (e.hasMoreElements()) {
			Extension extension = (Extension) e.nextElement();
			IColumbaService service = getServiceInstance(extension);
			service.stopService();
		}
	}
}