.instanciateExtension(null);

package org.columba.core.gui.externaltools;

import java.io.File;

import org.columba.api.exception.PluginHandlerNotFoundException;
import org.columba.api.plugin.IExtension;
import org.columba.core.config.Config;
import org.columba.core.plugin.PluginManager;
import org.columba.core.pluginhandler.ExternalToolsExtensionHandler;
import org.columba.core.xml.XmlElement;

/**
 * Provides an easy way to integrate external apps in Columba.
 * <p>
 * This includes a first-time assistant for the user. And a configuration file
 * "external_tools.xml" to store the options of the external tools.
 * <p>
 * When using external commandline (already used examples are aspell and GnuPG)
 * tools, you should just use this handler to get the location of the
 * executable.
 * <p>
 * If the executable wasn't configured, yet a wizard will assist the user in
 * configuring the external tool. If everything is correctly configured, it will
 * just return the path of the commandline tool as <code>File</code>.
 * <p>
 * <verbatim> File file = getLocationOfExternalTool("gpg"); </verbatim>
 * 
 * <p>
 * 
 * @see org.columba.api.plugin.external_tools.xml
 * 
 * @author fdietz
 */
public class ExternalToolsManager {

	private static ExternalToolsManager instance = new ExternalToolsManager();

	private ExternalToolsExtensionHandler handler;

	private ExternalToolsManager() {
	}

	public static ExternalToolsManager getInstance() {
		return instance;
	}

	private ExternalToolsExtensionHandler getHandler() {
		if (handler == null) {
			try {
				handler = (ExternalToolsExtensionHandler) PluginManager
						.getInstance().getHandler(
								ExternalToolsExtensionHandler.NAME);
			} catch (PluginHandlerNotFoundException e) {
				e.printStackTrace();
			}
		}

		return handler;
	}

	/**
	 * Gets the location of an external commandline tool.
	 * <p>
	 * TODO: test this method
	 * 
	 * @param toolID
	 *            id of tool
	 * @return location of tool
	 */
	public File getLocationOfExternalTool(String toolID) {
		AbstractExternalToolsPlugin plugin = null;

		try {
			IExtension extension = getHandler().getExtension(toolID);

			plugin = (AbstractExternalToolsPlugin) extension
					.instanciateExtension(new Object[] { null });
		} catch (Exception e1) {
			e1.printStackTrace();

			return null;
		}

		// check configuration
		XmlElement root = getConfiguration(toolID);

		if (root == null) {
			// create xml node
			XmlElement parent = Config.getInstance().get("external_tools")
					.getElement("tools");
			XmlElement child = new XmlElement("tool");
			child.addAttribute("first_time", "true");
			child.addAttribute("name", toolID);
			parent.addElement(child);

			root = child;
		}

		boolean firsttime = false;

		if (root.getAttribute("first_time").equals("true")) {
			firsttime = true;
		}

		if (firsttime) {
			// start the configuration wizard
			ExternalToolsWizardLauncher launcher = new ExternalToolsWizardLauncher();
			launcher.launchWizard(toolID, true);

			if (launcher.isFinished()) {
				// ok, now the tool is initialized correctly
				XmlElement r = getConfiguration(toolID);
				File file = new File(r.getAttribute("location"));

				return file;
			}
		} else {
			String location = root.getAttribute("location");

			File file = new File(location);

			return file;
		}

		return null;
	}

	/**
	 * Gets xml configuration of tool with id.
	 * 
	 * @param id
	 *            id of tool
	 * @return xml treenode
	 */
	public XmlElement getConfiguration(String id) {
		XmlElement root = Config.getInstance().get("external_tools")
				.getElement("tools");
		boolean firsttime = false;

		for (int i = 0; i < root.count(); i++) {
			XmlElement child = root.getElement(i);

			if (child.getAttribute("name").equals(id)) {
				return child;
			}
		}

		return null;
	}
}