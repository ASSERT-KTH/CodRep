import org.columba.core.main.MainInterface;

package org.columba.mail.filter.plugins;

import javax.swing.JOptionPane;

import org.columba.core.command.Command;
import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.filter.FilterAction;
import org.columba.mail.folder.Folder;
import org.columba.mail.folder.command.CopyMessageCommand;
import org.columba.main.MainInterface;

/**
 * @author freddy
 *
 * To change this generated comment edit the template variable "typecomment":
 * Window>Preferences>Java>Templates.
 * To enable and disable the creation of type comments go to
 * Window>Preferences>Java>Code Generation.
 */
public class CopyMessageAction extends AbstractFilterAction {

	

	public Command getCommand(FilterAction filterAction, Folder srcFolder, Object[] uids) throws Exception {

		int uid = filterAction.getUid();

		Folder destFolder = (Folder) MainInterface.treeModel.getFolder(uid);

		if (destFolder == null) {
			JOptionPane.showMessageDialog(
				null,
				"Unable to find destination folder, please correct the destination folder path for this filter");
			throw new Exception("File not found");
		}

		FolderCommandReference[] r = new FolderCommandReference[2];
		r[0] = new FolderCommandReference(srcFolder, uids);
		r[1] = new FolderCommandReference(destFolder);

		CopyMessageCommand c = new CopyMessageCommand( r);

		return c;
	}

}