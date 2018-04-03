ComposerController composerController = ((ComposerController)getFrameMediator());

/*
 * Created on 25.03.2003
 *
 * To change this generated comment go to 
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
package org.columba.mail.gui.composer.action;

import java.awt.event.ActionEvent;
import java.awt.event.KeyEvent;

import javax.swing.KeyStroke;

import org.columba.core.action.FrameAction;
import org.columba.core.gui.util.ImageLoader;
import org.columba.mail.gui.composer.ComposerController;
import org.columba.mail.util.MailResourceLoader;

/**
 * Add attachment to message.
 *
 * @author fdietz
 */
public class AttachFileAction extends FrameAction {

	public AttachFileAction(ComposerController composerController) {
		super(
				composerController,
				MailResourceLoader.getString(
					"menu", "composer", "menu_message_attachFile"));
		
		// tooltip text
		setTooltipText(
				MailResourceLoader.getString(
					"menu", "composer", "menu_message_attachFile_tooltip"));
		
		// toolbar text
		setToolBarText(
				MailResourceLoader.getString(
					"menu", "composer", "menu_message_attachFile_toolbar"));
		enableToolBarText(true);
		
		// action command
		setActionCommand("ATTACH");
		
		// large icon for toolbar
		setLargeIcon(ImageLoader.getImageIcon("stock_attach.png"));
		
		// small icon for menu
		setSmallIcon(ImageLoader.getImageIcon("stock_attach-16.png"));
		
//		shortcut key
		setAcceleratorKey(KeyStroke.getKeyStroke(KeyEvent.VK_A, ActionEvent.CTRL_MASK | ActionEvent.ALT_MASK));

	}

	
	/* (non-Javadoc)
	 * @see java.awt.event.ActionListener#actionPerformed(java.awt.event.ActionEvent)
	 */
	public void actionPerformed(ActionEvent evt) {
		ComposerController composerController = ((ComposerController)getFrameController());

		composerController.getAttachmentController().addFileAttachment();
		
	}

}