import org.columba.api.plugin.IExtensionInterface;

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
package org.columba.core.gui.themes.plugin;

import org.columba.core.plugin.IExtensionInterface;

/**
 * @author frd
 * 
 * To change the template for this generated type comment go to
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
public abstract class AbstractThemePlugin implements IExtensionInterface {
	public AbstractThemePlugin() {
		super();
	}

	/**
	 * 
	 * load your theme here:
	 * 
	 * UIManager.setLookAndFeel(
	 * "com.sun.java.swing.plaf.windows.WindowsLookAndFeel" );
	 * 
	 */
	public abstract void setLookAndFeel() throws Exception;
}