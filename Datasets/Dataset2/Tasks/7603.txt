super("filter", "org/columba/mail/filter/filter.xml", "filterlist");

package org.columba.mail.plugin;

import java.io.File;

import org.columba.core.xml.XmlElement;



/**
 * @author freddy
 *
 * To change this generated comment edit the template variable "typecomment":
 * Window>Preferences>Java>Templates.
 * To enable and disable the creation of type comments go to
 * Window>Preferences>Java>Code Generation.
 */
public class LocalFilterPluginHandler extends AbstractFilterPluginHandler {

	

	/**
	 * Constructor for LocalFilterPluginHandler.
	 * @param id
	 * @param config
	 */
	public LocalFilterPluginHandler() {
		super("filter_local", "org/columba/mail/filter/filter_local.xml", "filterlist");

		
	}

	public void addPlugin(String name, File pluginFolder, XmlElement element) {
			super.addPlugin(name, pluginFolder, element);

			XmlElement child = element.getElement("arguments/filter");

			parentNode.addElement(child);

		}

}