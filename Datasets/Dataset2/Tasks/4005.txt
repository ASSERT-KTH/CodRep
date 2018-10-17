super("org.columba.addressbook.folder", "org/columba/addressbook/plugin/folder.xml");

//The contents of this file are subject to the Mozilla Public License Version 1.1
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
//The Initial Developers of the Original Code are Frederik Dietz and Timo Stich.
//Portions created by Frederik Dietz and Timo Stich are Copyright (C) 2003. 
//
//All Rights Reserved.
package org.columba.addressbook.plugin;

import org.columba.core.plugin.AbstractPluginHandler;
import org.columba.core.xml.XmlElement;

/**
 * @author frd
 *
 * To change this generated comment edit the template variable "typecomment":
 * Window>Preferences>Java>Templates.
 * To enable and disable the creation of type comments go to
 * Window>Preferences>Java>Code Generation.
 */
public class FolderPluginHandler extends AbstractPluginHandler {

	
	
	/**
	 * Constructor for FolderPluginHandler.
	 * @param id
	 * @param config
	 */
	public FolderPluginHandler() {
		super("org.columba.addressbook.folder", "org/columba/addressbook/folder/folder.xml");

		parentNode = getConfig().getRoot().getElement("folderlist");
	}

	/* (non-Javadoc)
	 * @see org.columba.core.plugin.AbstractPluginHandler#addExtension(java.lang.String, org.columba.core.xml.XmlElement)
	 */
	public void addExtension(String id, XmlElement extension) {
		// TODO adding folders with the plugin-mechanism shouldn't work unless we don't implement this - this is mostly copy/paste from other plugin-handler classes

	}

}