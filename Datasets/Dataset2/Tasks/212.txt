import org.columba.core.gui.frame.FrameController;

/*
 * Created on 11.03.2003
 *
 * To change this generated comment go to 
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
package org.columba.mail.gui.tree.action;

import java.awt.event.ActionEvent;
import java.awt.event.KeyEvent;

import javax.swing.KeyStroke;

import org.columba.core.action.FrameAction;
import org.columba.core.gui.FrameController;
import org.columba.core.gui.util.ImageLoader;
import org.columba.core.main.MainInterface;
import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.gui.tree.command.CreateSubFolderCommand;
import org.columba.mail.gui.tree.util.EditFolderDialog;
import org.columba.mail.util.MailResourceLoader;

/**
 * @author frd
 *
 * To change this generated comment go to 
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
public class CreateSubFolderAction extends FrameAction {

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
	public CreateSubFolderAction(FrameController frameController) {
		super(
			frameController,
			MailResourceLoader.getString(
				"menu",
				"mainframe",
				"menu_folder_newfolder"),
			MailResourceLoader.getString(
				"menu",
				"mainframe",
				"menu_folder_newfolder"),
			MailResourceLoader.getString(
				"menu",
				"mainframe",
				"menu_folder_newfolder"),
			"CREATE_SUBFOLDER",
			ImageLoader.getSmallImageIcon("folder.png"),
			ImageLoader.getImageIcon("folder.png"),
			'N',
			KeyStroke.getKeyStroke(KeyEvent.VK_N, ActionEvent.ALT_MASK));

	}

	/* (non-Javadoc)
	 * @see java.awt.event.ActionListener#actionPerformed(java.awt.event.ActionEvent)
	 */
	public void actionPerformed(ActionEvent evt) {
		EditFolderDialog dialog = new EditFolderDialog("New Folder");
		dialog.showDialog();

		String name;

		if (dialog.success() == true) {
			// ok pressed
			name = dialog.getName();
		} else {
			// cancel pressed
			return;
		}

		FolderCommandReference[] r =
			(FolderCommandReference[]) frameController
				.getSelectionManager()
				.getSelection(
				"mail.tree");
		r[0].setFolderName(name);

		MainInterface.processor.addOp(new CreateSubFolderCommand(r));
	}

}