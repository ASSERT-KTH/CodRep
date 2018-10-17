((AbstractMailFrameController) getFrameMediator())

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

package org.columba.mail.gui.table.action;

import java.awt.event.ActionEvent;
import java.awt.event.KeyEvent;
import java.util.Observable;
import java.util.Observer;

import javax.swing.KeyStroke;

import org.columba.core.action.FrameAction;
import org.columba.core.gui.frame.AbstractFrameController;
import org.columba.core.gui.selection.SelectionChangedEvent;
import org.columba.core.gui.selection.SelectionListener;
import org.columba.core.gui.util.ImageLoader;
import org.columba.core.main.MainInterface;
import org.columba.core.xml.XmlElement;
import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.config.MailConfig;
import org.columba.mail.gui.composer.command.ForwardCommand;
import org.columba.mail.gui.composer.command.ForwardInlineCommand;
import org.columba.mail.gui.frame.AbstractMailFrameController;
import org.columba.mail.gui.table.selection.TableSelectionChangedEvent;
import org.columba.mail.util.MailResourceLoader;

/**
 * Forward Message As Attachment or Inline.
 * <p>
 * Based on user configuration.
 *
 * @author fdietz
 */
public class ForwardAction
	extends FrameAction
	implements SelectionListener, Observer {

	private XmlElement forward;
	private String forwardStyle;

	public ForwardAction(AbstractFrameController frameController) {
		super(
			frameController,
			MailResourceLoader.getString(
				"menu",
				"mainframe",
				"menu_message_forward"));

		// tooltip text
		setTooltipText(
			MailResourceLoader.getString(
				"menu",
				"mainframe",
				"menu_message_forward_tooltip"));

		// action command
		setActionCommand("FORWARD");

		// icon for menu
		setSmallIcon(ImageLoader.getSmallImageIcon("forward_small.png"));

		// icon for toolbar
		setLargeIcon(ImageLoader.getImageIcon("forward.png"));

		// shortcut key
		setAcceleratorKey(
			KeyStroke.getKeyStroke(KeyEvent.VK_L, ActionEvent.CTRL_MASK));

		// toolbar text is usually a bit shorter
		setToolBarText(
			MailResourceLoader.getString(
				"menu",
				"mainframe",
				"menu_message_forward_toolbar"));
		enableToolBarText(true);

		setEnabled(false);
		(
			(
				AbstractMailFrameController) frameController)
					.registerTableSelectionListener(
			this);

		XmlElement composerOptions =
			MailConfig.getComposerOptionsConfig().getRoot().getElement(
				"/options");

		forward = composerOptions.getElement("forward");
		if (forward == null) {
			forward = composerOptions.addSubElement("forward");
		}

		// listen for configuration changes
		forward.addObserver(this);

		forwardStyle = forward.getAttribute("style", "attachment");

	}

	/* (non-Javadoc)
	 * @see java.awt.event.ActionListener#actionPerformed(java.awt.event.ActionEvent)
	 */
	public void actionPerformed(ActionEvent evt) {
		FolderCommandReference[] r =
			((AbstractMailFrameController) getFrameController())
				.getTableSelection();

		if (forwardStyle.equals("attachment"))
			MainInterface.processor.addOp(new ForwardCommand(r));
		else
			MainInterface.processor.addOp(new ForwardInlineCommand(r));

	}
	/* (non-Javadoc)
			 * @see org.columba.core.gui.util.SelectionListener#selectionChanged(org.columba.core.gui.util.SelectionChangedEvent)
			 */
	public void selectionChanged(SelectionChangedEvent e) {
		setEnabled(((TableSelectionChangedEvent) e).getUids().length > 0);
	}

	/**
	 * Gets fired if configuration changes
	 * 
	 * @see org.columba.mail.gui.config.general.MailOptionsDialog
	 * 
	 * @see java.util.Observer#update(java.util.Observable, java.lang.Object)
	 */
	public void update(Observable arg0, Object arg1) {
		forwardStyle = forward.getAttribute("style", "attachment");

	}

}