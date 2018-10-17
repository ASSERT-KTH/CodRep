import org.columba.core.gui.frame.FrameController;

/*
 * Created on 11.03.2003
 *
 * To change this generated comment go to 
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
package org.columba.mail.gui.table.action;

import java.awt.event.ActionEvent;

import org.columba.core.action.FrameAction;
import org.columba.core.gui.FrameController;
import org.columba.core.gui.util.ImageLoader;
import org.columba.core.main.MainInterface;
import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.folder.Folder;
import org.columba.mail.folder.command.MoveMessageCommand;
import org.columba.mail.gui.tree.util.SelectFolderDialog;
import org.columba.mail.util.MailResourceLoader;

/**
 * @author frd
 *
 * To change this generated comment go to 
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
public class MoveMessageAction extends FrameAction {

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
	public MoveMessageAction(FrameController frameController) {
		super(
			frameController,
			MailResourceLoader.getString(
				"menu",
				"mainframe",
				"menu_message_move"),
			MailResourceLoader.getString(
				"menu",
				"mainframe",
				"menu_message_move_toolbar"),
			MailResourceLoader.getString(
				"menu",
				"mainframe",
				"menu_message_move_tooltip"),
			"MOVE_MESSAGE",
			ImageLoader.getSmallImageIcon("movemessage_small.png"),
			ImageLoader.getImageIcon("move-message.png"),
			'M',
			null,
			false);

	}

	/* (non-Javadoc)
	 * @see java.awt.event.ActionListener#actionPerformed(java.awt.event.ActionEvent)
	 */
	public void actionPerformed(ActionEvent evt) {
		SelectFolderDialog dialog =
			MainInterface.treeModel.getSelectFolderDialog();

		if (dialog.success()) {

			Folder destFolder = dialog.getSelectedFolder();

			FolderCommandReference[] result = new FolderCommandReference[2];
			FolderCommandReference[] r1 =
				(FolderCommandReference[]) getFrameController()
					.getSelectionManager()
					.getSelection("mail.table");
			FolderCommandReference r2 = new FolderCommandReference(destFolder);

			result[0] = r1[0];
			result[1] = r2;
			MoveMessageCommand c = new MoveMessageCommand(result);

			MainInterface.processor.addOp(c);

		}

	}

}