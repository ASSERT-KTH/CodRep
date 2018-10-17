null, null,	"menu_edit_paste_tooltip"));

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

package org.columba.core.gui.action;

import java.awt.event.ActionEvent;
import java.awt.event.KeyEvent;

import javax.swing.KeyStroke;

import org.columba.core.action.FrameAction;
import org.columba.core.gui.frame.AbstractFrameController;
import org.columba.core.gui.util.ImageLoader;
import org.columba.core.main.MainInterface;
import org.columba.core.util.GlobalResourceLoader;

public class PasteAction extends FrameAction {

	public PasteAction(AbstractFrameController controller) {
		super(
				controller,
				GlobalResourceLoader.getString(
					null, null,	"menu_edit_paste"));

		// tooltip text
		setTooltipText(
				GlobalResourceLoader.getString(
					null, null,	"menu_edit_paste"));
		
		// action command
		setActionCommand("PASTE");

		// small icon for menu
		setSmallIcon(ImageLoader.getImageIcon("stock_paste-16.png"));
		
		// large icon for toolbar
		setLargeIcon(ImageLoader.getImageIcon("stock_paste.png"));
		
		// shortcut key
		setAcceleratorKey(
				KeyStroke.getKeyStroke(
					KeyEvent.VK_V, ActionEvent.CTRL_MASK));
		
		// disable toolbar text
		enableToolBarText(false);
		
		// shortcut key
		setAcceleratorKey(
				KeyStroke.getKeyStroke(
					KeyEvent.VK_V, ActionEvent.CTRL_MASK));
		
		setEnabled(false);
		MainInterface.focusManager.setPasteAction(this);
	}

	/* (non-Javadoc)
	 * @see java.awt.event.ActionListener#actionPerformed(java.awt.event.ActionEvent)
	 */
	public void actionPerformed(ActionEvent evt) {
		MainInterface.focusManager.paste();
	}
	
	/* (non-Javadoc)
		 * @see org.columba.core.action.FrameAction#isSingleton()
		 */
		public boolean isSingleton() {
			return true;
		}
}