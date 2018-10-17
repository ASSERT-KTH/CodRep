interpreterTable.put(interpreter.getAttribute("name"), PluginLoader.loadExternalPlugin(interpreter.getAttribute("main_class"), pluginManager.getPluginType(id),pluginManager.getJarFile(id),null));

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
package org.columba.core.plugin;

import java.util.Hashtable;

import org.columba.core.scripting.AbstractInterpreter;
import org.columba.core.xml.XmlElement;

/**
 * @author freddy
 *
 * To change this generated comment edit the template variable "typecomment":
 * Window>Preferences>Java>Templates.
 * To enable and disable the creation of type comments go to
 * Window>Preferences>Java>Code Generation.
 */
public class InterpreterHandler extends AbstractPluginHandler {

	private Hashtable interpreterTable;

	/**
	 * Constructor for InterpreterHandler.
	 * @param id
	 * @param config
	 */

	public InterpreterHandler() {
		super("org.columba.core.interpreter", null);
		interpreterTable = new Hashtable();
	}

	/**
	 * @see org.columba.core.plugin.AbstractPluginHandler#getDefaultNames()
	 */
	public String[] getPluginIdList() {
		return null;
	}

	/*
	public Object getPlugin(String name, String className, Object[] args)
			throws Exception {
	
		ColumbaLogger.log.debug("trying to load interpreter plugin");
		
			try {
				return loadPlugin(className, args);
			} catch (ClassNotFoundException ex) {
				
				XmlElement parent = (XmlElement) externalPlugins.get(name);
				XmlElement child = parent.getElement("runtime");
				//String type = child.getAttribute("type");
				
				File file = (File) pluginFolders.get(name);
	
				return PluginLoader.loadExternalPlugin(className, "java", file, args);
			}
	
		}
	*/

	public AbstractInterpreter getInterpreter(String type) {
		return (AbstractInterpreter) interpreterTable.get(type);		
	}

	/* (non-Javadoc)
	 * @see org.columba.core.plugin.AbstractPluginHandler#addExtension(java.lang.String, org.columba.core.xml.XmlElement)
	 */
	public void addExtension(String id, XmlElement extension) {
		XmlElement interpreter = extension.getElement("interpreter");
		
		try {
			interpreterTable.put(interpreter.getAttribute("name"), PluginLoader.loadExternalPlugin(interpreter.getAttribute("main_class"), pluginManager.getPluginType(id),pluginManager.getPluginDir(id),null));
		} catch (Exception e) {
			e.printStackTrace();
		}
	}

}