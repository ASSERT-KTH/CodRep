super("org.columba.core.menu",null);

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

package org.columba.core.gui.menu;

import java.util.Vector;

import org.columba.core.plugin.AbstractPluginHandler;
import org.columba.core.xml.XmlElement;

public class MenuPluginHandler extends AbstractPluginHandler {

	Vector menuPlugins;

	public MenuPluginHandler() {
		super("menu",null);
		
		menuPlugins=new Vector();
	}

	/* (non-Javadoc)
	 * @see org.columba.core.plugin.AbstractPluginHandler#getDefaultNames()
	 */
	public String[] getPluginIdList() {
		return null;
	}

	public void insertPlugins(Menu menu) {
		for( int i=0; i<menuPlugins.size(); i++) {
			menu.extendMenu((XmlElement)menuPlugins.get(i));
		}
	}

	/* (non-Javadoc)
	 * @see org.columba.core.plugin.AbstractPluginHandler#addExtension(java.lang.String, org.columba.core.xml.XmlElement)
	 */
	public void addExtension(String id, XmlElement extension) {
		menuPlugins.add(extension.getElement("menu"));
	}

}