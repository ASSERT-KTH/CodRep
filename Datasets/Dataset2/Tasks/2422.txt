setTooltipText(

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

import org.columba.core.action.FrameAction;
import org.columba.core.gui.config.GeneralOptionsDialog;
import org.columba.core.gui.frame.AbstractFrameController;
import org.columba.core.gui.util.ImageLoader;
import org.columba.mail.util.MailResourceLoader;

public class GlobalOptionsAction extends FrameAction {

	public GlobalOptionsAction(AbstractFrameController controller) {
		super(
			controller,
			MailResourceLoader.getString(
				"menu",
				"mainframe",
				"menu_edit_generaloptions"));

		setLongDescription(
			MailResourceLoader.getString(
				"menu",
				"mainframe",
				"menu_edit_generaloptions_tooltip"));

		setSmallIcon(ImageLoader.getSmallImageIcon("stock_preferences-16.png"));

		setLargeIcon(ImageLoader.getImageIcon("stock_preferences.png"));

	}

	/* (non-Javadoc)
	 * @see java.awt.event.ActionListener#actionPerformed(java.awt.event.ActionEvent)
	 */
	public void actionPerformed(ActionEvent evt) {
		GeneralOptionsDialog dialog =
			new GeneralOptionsDialog(frameController.getView());

		/*
		ThemeSwitcher.updateFrame(frameController.getView());
		*/
	}

}