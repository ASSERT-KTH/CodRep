super("org.columba.mail.import", "org/columba/mail/plugin/import.xml");

/*
 * Created on 23.03.2003
 *
 * To change this generated comment go to 
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
package org.columba.mail.plugin;

import java.util.ListIterator;

import org.columba.core.plugin.AbstractPluginHandler;
import org.columba.core.xml.XmlElement;

/**
 * @author frd
 *
 * To change this generated comment go to 
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
public class ImportPluginHandler extends AbstractPluginHandler {

	

	/**
	 * @param id
	 * @param config
	 */
	public ImportPluginHandler() {
		super("org.columba.mail.import", "org/columba/mail/folder/import.xml");

		parentNode = getConfig().getRoot().getElement("importlist");
	}

	
	/* (non-Javadoc)
	 * @see org.columba.core.plugin.AbstractPluginHandler#addExtension(java.lang.String, org.columba.core.xml.XmlElement)
	 */
	public void addExtension(String id, XmlElement extension) {
		ListIterator iterator = extension.getElements().listIterator();
		XmlElement action;
		while (iterator.hasNext()) {
			action = (XmlElement) iterator.next();
			String newName = id + '$' + action.getAttribute("name");
			String userVisibleName = action.getAttribute("name");

			// associate id with newName for later reference
			//transformationTable.put(id, newName);

			action.addAttribute("name", newName);
			action.addAttribute("uservisiblename", userVisibleName);

			parentNode.addElement(action);
		}
	}

}