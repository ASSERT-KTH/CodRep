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
package org.columba.core.gui.plugin;

import javax.swing.JPanel;

import org.columba.core.plugin.IExtensionInterface;

/**
 * 
 * 
 * <class>AbstractConfigPlugin</class> is the abstract class for the
 * org.columba.core.config plugin extension point
 * 
 * @author fdietz
 * 
 */
public abstract class AbstractConfigPlugin implements IExtensionInterface {
	/**
	 * default constructor
	 */
	public AbstractConfigPlugin() {
	}

	/** ******************* abstract methods ******************************** */
	/**
	 * 
	 * This method is called when the dialog is viewed the first time.
	 * updateComponents(true) - initialse the gui elements with the
	 * configuration data
	 * 
	 * Its also called when pressing the OK button updateComponents(false) -
	 * update the configuration data in using the gui elements data
	 * 
	 * 
	 * 
	 * @param b
	 *            if true, model -> view, otherwise view -> model
	 * 
	 */
	public abstract void updateComponents(boolean b);

	/**
	 * 
	 * Create your configuration <class>JPanel</class> here
	 * 
	 * This panel will be automatically plugged in the configuration dialog.
	 * 
	 * 
	 * @return <class>JPanel</class>
	 */
	public abstract JPanel createPanel();

	/** ****************** internal stuff ********************************* */
}