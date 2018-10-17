Object instance = handler.getInterpreter(type);//, "org.columba.core.scripting.PythonInterpreterPlugin", null);

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

import java.io.File;
import java.net.URL;

import org.columba.core.loader.ExternalClassLoader;
import org.columba.core.logging.ColumbaLogger;
import org.columba.core.main.MainInterface;
import org.columba.core.scripting.AbstractInterpreter;

/**
 * @author freddy
 *
 * To change this generated comment edit the template variable "typecomment":
 * Window>Preferences>Java>Templates.
 * To enable and disable the creation of type comments go to
 * Window>Preferences>Java>Code Generation.
 */
public class PluginLoader {

	/**
	 * Constructor for PluginLoader.
	 */
	public PluginLoader() {
		super();
	}

	public static Object loadExternalPlugin(
		String className,
		String type,
		File file,
		Object[] args)
		throws Exception {

		ColumbaLogger.log.debug("loading..");

		if (type.equals("java") || type.equals("jar") ) {
			String path = file.getPath();

			URL[] url = new URL[1];
			URL newURL = new File(path).toURL();
			url[0] = newURL;
			/*
			if ( libs[0] != null )
			url[1] = libs[0].toURL();
			*/
			ColumbaLogger.log.debug("url=" + newURL);

			return new ExternalClassLoader(url).instanciate(className, args);

		}

		InterpreterHandler handler =
			(InterpreterHandler) MainInterface.pluginManager.getHandler(
				"interpreter");

		Object instance = handler.getPlugin(type, "org.columba.core.scripting.PythonInterpreterPlugin", null);

		/*
		if (type.equals("python")) {
			
			
			String pythonFile = file.toString()+"/"+className.toString();
			
			
			String pythonClass = className.toString().substring(0,className.toString().length()-3);
			//Class pluginClass = Class.forName(pythonClass);
			return Python.instanciate(pythonFile, pythonClass, args,  "test");
			
		} 
		*/

		if (instance != null) {
			AbstractInterpreter ip = (AbstractInterpreter) instance;

			String pythonFile = file.toString() + "/" + className.toString();

			String pythonClass =
				className.toString().substring(
					0,
					className.toString().length() - 3);

			Object i = ip.instanciate(pythonFile, pythonClass, args, "test");

			return i;
		}
		
		return null;
	}

}