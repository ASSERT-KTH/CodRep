super("org.columba.addressbook.folder", "org/columba/addressbook/folder/folder.xml");

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

	protected XmlElement parentNode;
	
	/**
	 * Constructor for FolderPluginHandler.
	 * @param id
	 * @param config
	 */
	public FolderPluginHandler() {
		super("addressbook_folder", "org/columba/addressbook/folder/folder.xml");

		parentNode = getConfig().getRoot().getElement("folderlist");
	}

	/**
	 * @see org.columba.core.plugin.AbstractPluginHandler#getNames()
	 */
	public String[] getPluginIdList() {
		int count = parentNode.count();

		String[] list = new String[count];

		for (int i = 0; i < count; i++) {
			XmlElement action = parentNode.getElement(i);
			String s = action.getAttribute("name");

			list[i] = s;

		}

		return list;
	}

	/**
		 * @see org.columba.core.plugin.AbstractPluginHandler#getPluginClassName(java.lang.String, java.lang.String)
		 */
	protected String getPluginClassName(String name, String id) {

		int count = parentNode.count();

		for (int i = 0; i < count; i++) {

			XmlElement action = parentNode.getElement(i);
			String s = action.getAttribute("name");

			if (name.equalsIgnoreCase(s))
				return action.getAttribute(id);

		}

		return null;
	}

	public Object getPlugin(String name, Object[] args) throws Exception {
		String className = getPluginClassName(name, "class");
		return getPlugin(name, className, args);
	}

	public Class getPluginClass(String name) {
		String className = getPluginClassName(name, "class");
		
		try {

			Class clazz = Class.forName(className);
			return clazz;
		} catch (Exception ex) {
			ex.printStackTrace();
		}
		return null;
	}
	/* (non-Javadoc)
	 * @see org.columba.core.plugin.AbstractPluginHandler#addExtension(java.lang.String, org.columba.core.xml.XmlElement)
	 */
	public void addExtension(String id, XmlElement extension) {
		// TODO Auto-generated method stub

	}

}