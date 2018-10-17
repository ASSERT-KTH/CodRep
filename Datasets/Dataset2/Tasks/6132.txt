import org.columba.core.gui.frame.FrameController;

/*
 * Created on 11.03.2003
 *
 * To change this generated comment go to 
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
package org.columba.mail.gui.tree.action;

import java.awt.event.ActionEvent;

import org.columba.core.action.FrameAction;
import org.columba.core.gui.FrameController;
import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.config.FolderItem;
import org.columba.mail.folder.Folder;
import org.columba.mail.gui.frame.MailFrameController;
import org.columba.mail.util.MailResourceLoader;

/**
 * @author frd
 *
 * To change this generated comment go to 
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
public class FilterPreferencesAction extends FrameAction {

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
	public FilterPreferencesAction(FrameController frameController) {
		super(
			frameController,
			MailResourceLoader.getString(
				"menu",
				"mainframe",
				"menu_folder_filterconfig"),
			MailResourceLoader.getString(
				"menu",
				"mainframe",
				"menu_folder_filterconfig"),
			MailResourceLoader.getString(
				"menu",
				"mainframe",
				"menu_folder_filterconfig"),
			"FILTER_PREFERENCES",
			null,
			null,
			'U',
			null);

	}

	/* (non-Javadoc)
	 * @see java.awt.event.ActionListener#actionPerformed(java.awt.event.ActionEvent)
	 */
	public void actionPerformed(ActionEvent evt) {
		FolderCommandReference[] r =
			(FolderCommandReference[]) frameController
				.getSelectionManager()
				.getSelection(
				"mail.tree");
		Folder folder = (Folder) r[0].getFolder();

		if (folder == null)
			return;

		FolderItem item = folder.getFolderItem();
		if (item == null)
			return;

		folder.showFilterDialog(((MailFrameController)getFrameController()));
	}

}