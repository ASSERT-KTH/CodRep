import org.columba.core.gui.frame.FrameController;

/*
 * Created on 25.03.2003
 *
 * To change this generated comment go to 
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
package org.columba.mail.gui.composer.action;

import java.awt.event.ActionEvent;

import org.columba.core.action.FrameAction;
import org.columba.core.gui.FrameController;
import org.columba.core.gui.util.ImageLoader;
import org.columba.core.main.MainInterface;
import org.columba.mail.command.ComposerCommandReference;
import org.columba.mail.config.AccountItem;
import org.columba.mail.config.SpecialFoldersItem;
import org.columba.mail.folder.outbox.OutboxFolder;
import org.columba.mail.gui.composer.ComposerController;
import org.columba.mail.gui.composer.ComposerModel;
import org.columba.mail.gui.composer.command.SaveMessageCommand;
import org.columba.mail.util.MailResourceLoader;

/**
 * @author frd
 *
 * To change this generated comment go to 
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
public class SendLaterAction extends FrameAction {

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
	public SendLaterAction(FrameController FrameController) {
		super(
			FrameController,
			MailResourceLoader.getString(
				"menu",
				"composer",
				"menu_file_sendlater"),
			MailResourceLoader.getString(
				"menu",
				"composer",
				"menu_file_sendlater"),
			MailResourceLoader.getString(
				"menu",
				"composer",
				"menu_file_sendlater"),
			"SENDLATER",
			ImageLoader.getSmallImageIcon("send-later-16.png"),
			null,
			MailResourceLoader.getMnemonic(
				"menu",
				"composer",
				"menu_file_sendlater"),
			null);

	}

	/* (non-Javadoc)
	 * @see java.awt.event.ActionListener#actionPerformed(java.awt.event.ActionEvent)
	 */
	public void actionPerformed(ActionEvent evt) {
		final ComposerController composerController =
			(ComposerController) getFrameController();

		if (composerController.checkState() == false)
			return;

		AccountItem item =
			((ComposerModel) composerController.getModel()).getAccountItem();
		SpecialFoldersItem folderItem = item.getSpecialFoldersItem();
		String str = folderItem.get("drafts");
		int destUid = Integer.parseInt(str);
		OutboxFolder destFolder =
			(OutboxFolder) MainInterface.treeModel.getFolder(103);

		ComposerCommandReference[] r = new ComposerCommandReference[1];
		r[0] = new ComposerCommandReference(composerController, destFolder);

		SaveMessageCommand c = new SaveMessageCommand(r);

		MainInterface.processor.addOp(c);
	}

}