import org.columba.mail.smtp.command.SendMessageCommand;

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
import org.columba.core.gui.frame.AbstractFrameController;
import org.columba.core.gui.util.ImageLoader;
import org.columba.core.main.MainInterface;
import org.columba.mail.command.ComposerCommandReference;
import org.columba.mail.folder.outbox.OutboxFolder;
import org.columba.mail.gui.composer.ComposerController;
import org.columba.mail.smtp.SendMessageCommand;
import org.columba.mail.util.MailResourceLoader;

/**
 * @author frd
 *
 * To change this generated comment go to 
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
public class SendAction extends FrameAction {

	/**
	 * @param composerController
	 * @param name
	 * @param longDescription
	 * @param tooltip
	 * @param actionCommand
	 * @param small_icon
	 * @param big_icon
	 * @param mnemonic
	 * @param keyStroke
	 */
	public SendAction(AbstractFrameController frameController) {
		super(
			frameController,
			MailResourceLoader.getString("menu", "composer", "menu_file_send"),
			MailResourceLoader.getString("menu", "composer", "menu_file_send"),
			MailResourceLoader.getString(
				"menu",
				"composer",
				"menu_file_send_tooltip"),
			"SEND",
			ImageLoader.getSmallImageIcon("send-16.png"),
			ImageLoader.getImageIcon("send-24.png"),
			MailResourceLoader.getMnemonic(
				"menu",
				"composer",
				"menu_file_send"),
			KeyStroke.getKeyStroke(KeyEvent.VK_ENTER, ActionEvent.CTRL_MASK));

	}

	/* (non-Javadoc)
	 * @see java.awt.event.ActionListener#actionPerformed(java.awt.event.ActionEvent)
	 */
	public void actionPerformed(ActionEvent evt) {
		final ComposerController composerController = (ComposerController ) getFrameController();
		
		if (composerController.checkState() == false)
			return;

		/*
		ComposerOperation op =
			new ComposerOperation(
				Operation.COMPOSER_SEND,
				0,
				composerInterface.composerController);
		
		MainInterface.crossbar.operate(op);
		*/

		OutboxFolder outboxFolder =
			(OutboxFolder) MainInterface.treeModel.getFolder(103);

		ComposerCommandReference[] r = new ComposerCommandReference[1];
		r[0] =
			new ComposerCommandReference(
				composerController,
				outboxFolder);

		SendMessageCommand c = new SendMessageCommand(r);

		MainInterface.processor.addOp(c);

	}

}