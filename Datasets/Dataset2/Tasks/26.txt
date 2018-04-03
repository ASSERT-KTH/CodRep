//initPopupMenu();

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
package org.columba.mail.gui.attachment.menu;

import java.awt.event.MouseAdapter;

import javax.swing.JPopupMenu;
import javax.swing.JSeparator;

import org.columba.mail.gui.attachment.AttachmentController;
import org.columba.mail.gui.attachment.action.AttachmentActionListener;

/**
 * menu for the tableviewer
 */

public class AttachmentMenu {
	private JPopupMenu popup;
	private AttachmentController attachmentViewer;

	public AttachmentMenu(AttachmentController attachmentViewer) {
		this.attachmentViewer = attachmentViewer;

		initPopupMenu();
	}

	public JPopupMenu getPopupMenu() {
		return popup;
	}

	protected AttachmentActionListener getActionListener() {
		return attachmentViewer.getActionListener();
	}

	protected void initPopupMenu() {
		popup = new JPopupMenu();

		MouseAdapter statusHandler = attachmentViewer.getMailFrameController().getMouseTooltipHandler();
		org.columba.core.gui.util.CMenuItem menuItem;

		menuItem =
			new org.columba.core.gui.util.CMenuItem(
				getActionListener().openAction);
		menuItem.addMouseListener(statusHandler);

		popup.add(menuItem);

		menuItem =
			new org.columba.core.gui.util.CMenuItem(
				getActionListener().openWithAction);
		menuItem.addMouseListener(statusHandler);

		popup.add(menuItem);

		menuItem =
			new org.columba.core.gui.util.CMenuItem(
				getActionListener().saveAsAction);
		menuItem.addMouseListener(statusHandler);

		popup.add(menuItem);

		popup.add(new JSeparator());

		menuItem =
			new org.columba.core.gui.util.CMenuItem(
				getActionListener().viewHeaderAction);
		menuItem.addMouseListener(statusHandler);

		popup.add(menuItem);
	}

}