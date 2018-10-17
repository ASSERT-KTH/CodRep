if (dialog.success()) {

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
import org.columba.core.gui.frame.AbstractFrameController;
import org.columba.core.gui.selection.SelectionChangedEvent;
import org.columba.core.gui.selection.SelectionListener;
import org.columba.core.main.MainInterface;
import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.folder.command.RenameFolderCommand;
import org.columba.mail.gui.frame.MailFrameController;
import org.columba.mail.gui.tree.selection.TreeSelectionChangedEvent;
import org.columba.mail.gui.tree.util.EditFolderDialog;
import org.columba.mail.util.MailResourceLoader;

/**
 * @author frd
 *
 * To change this generated comment go to 
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
public class RenameFolderAction
	extends FrameAction
	implements SelectionListener {

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
	public RenameFolderAction(AbstractFrameController frameController) {
		super(
			frameController,
			MailResourceLoader.getString(
				"menu",
				"mainframe",
				"menu_folder_renamefolder"),
			MailResourceLoader.getString(
				"menu",
				"mainframe",
				"menu_folder_renamefolder"),
			MailResourceLoader.getString(
				"menu",
				"mainframe",
				"menu_folder_renamefolder"),
			"RENAME_FOLDER",
			null,
			null,
			'R',
			KeyStroke.getKeyStroke(KeyEvent.VK_F2, 0));
		setEnabled(false);
		((MailFrameController) frameController).registerTreeSelectionListener(
			this);
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

		MainInterface.processor.addOp(new RenameFolderCommand(r));
	}
	/* (non-Javadoc)
					 * @see org.columba.core.gui.util.SelectionListener#selectionChanged(org.columba.core.gui.util.SelectionChangedEvent)
					 */
	public void selectionChanged(SelectionChangedEvent e) {

		if (((TreeSelectionChangedEvent) e).getSelected().length > 0)
			setEnabled(true);
		else
			setEnabled(false);

	}
}