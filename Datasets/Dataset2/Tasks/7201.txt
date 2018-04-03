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
import org.columba.mail.gui.frame.MailFrameController;
import org.columba.mail.gui.tree.util.EditFolderDialog;
import org.columba.mail.util.MailResourceLoader;

/**
 * @author frd
 *
 * To change this generated comment go to 
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
public class CreateVirtualFolderAction extends FrameAction {

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
	public CreateVirtualFolderAction(FrameController frameController) {
		super(
			frameController,
			MailResourceLoader.getString(
				"menu",
				"mainframe",
				"menu_folder_newvirtualfolder"),
			MailResourceLoader.getString(
				"menu",
				"mainframe",
				"menu_folder_newvirtualfolder"),
			MailResourceLoader.getString(
				"menu",
				"mainframe",
				"menu_folder_newvirtualfolder"),
			"CREATE_VIRTUAL_SUBFOLDER",
			ImageLoader.getSmallImageIcon("virtualfolder.png"),
			ImageLoader.getImageIcon("virtualfolder.png"),
			'0',
			KeyStroke.getKeyStroke(KeyEvent.VK_V, ActionEvent.ALT_MASK));

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

			try {
				FolderCommandReference[] r =
					(FolderCommandReference[]) frameController
						.getSelectionManager()
						.getSelection(
						"mail.tree");
				r[0].getFolder().addFolder(name, "VirtualFolder");

				MainInterface.treeModel.nodeStructureChanged(
					((MailFrameController) getFrameController())
						.treeController
						.getTreeSelectionManager()
						.getFolder());

			} catch (Exception ex) {
				ex.printStackTrace();
			}
		} else {
			// cancel pressed
			return;
		}
	}

}