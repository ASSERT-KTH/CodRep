import org.columba.core.gui.frame.FrameController;

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
package org.columba.core.action;

import javax.swing.ImageIcon;
import javax.swing.JCheckBoxMenuItem;
import javax.swing.KeyStroke;

import org.columba.core.gui.FrameController;

/**
 * @author frd
 *
 * To change this generated comment edit the template variable "typecomment":
 * Window>Preferences>Java>Templates.
 * To enable and disable the creation of type comments go to
 * Window>Preferences>Java>Code Generation.
 */
public class CheckBoxAction extends FrameAction {

	private JCheckBoxMenuItem checkBoxMenuItem;
	

	/**
	 * @param frameController
	 * @param name
	 * @param longDescription
	 * @param actionCommand
	 * @param small_icon
	 * @param big_icon
	 * @param mnemonic
	 * @param keyStroke
	 */
	public CheckBoxAction(
		FrameController frameController,
		String name,
		String longDescription,
		String actionCommand,
		ImageIcon small_icon,
		ImageIcon big_icon,
		int mnemonic,
		KeyStroke keyStroke) {
		super(
			frameController,
			name,
			longDescription,
			actionCommand,
			small_icon,
			big_icon,
			mnemonic,
			keyStroke);
	}

	/**
	 * @param frameController
	 * @param name
	 * @param longDescription
	 * @param tooltip
	 * @param actionCommand
	 * @param small_icon
	 * @param big_icon
	 * @param mnemonic
	 * @param keyStroke
	 */
	public CheckBoxAction(
		FrameController frameController,
		String name,
		String longDescription,
		String tooltip,
		String actionCommand,
		ImageIcon small_icon,
		ImageIcon big_icon,
		int mnemonic,
		KeyStroke keyStroke) {
		super(
			frameController,
			name,
			longDescription,
			tooltip,
			actionCommand,
			small_icon,
			big_icon,
			mnemonic,
			keyStroke);
	}

	/**
		 * Returns the checkBoxMenuItem.
		 * @return JCheckBoxMenuItem
		 */
		public JCheckBoxMenuItem getCheckBoxMenuItem() {
			return checkBoxMenuItem;
		}

		/**
		 * Sets the checkBoxMenuItem.
		 * @param checkBoxMenuItem The checkBoxMenuItem to set
		 */
		public void setCheckBoxMenuItem(JCheckBoxMenuItem checkBoxMenuItem) {
			this.checkBoxMenuItem = checkBoxMenuItem;
			checkBoxMenuItem.setState(getInitState());
		}
		
		public boolean getState() {
			return checkBoxMenuItem.getState();
		}
		
		public void setState(boolean value) {
			checkBoxMenuItem.setState(value);
		}

		protected boolean getInitState() {
			return false;
		}

}