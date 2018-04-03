public void shutdown() {

package org.columba.mail.shutdown;

import java.util.Enumeration;

import org.columba.core.main.MainInterface;
import org.columba.core.shutdown.*;
import org.columba.mail.folder.FolderTreeNode;
import org.columba.mail.folder.imap.IMAPFolder;
import org.columba.mail.folder.mh.CachedMHFolder;
import org.columba.mail.folder.outbox.OutboxFolder;

/**
 * @author freddy
 *
 * To change this generated comment edit the template variable "typecomment":
 * Window>Preferences>Java>Templates.
 * To enable and disable the creation of type comments go to
 * Window>Preferences>Java>Code Generation.
 */
public class SaveAllFoldersPlugin implements ShutdownPluginInterface {

	public void run() {
		saveAllFolders();
	}

	public void saveAllFolders() {
		FolderTreeNode rootFolder =
			(FolderTreeNode) MainInterface.treeModel.getRoot();

		saveFolder(rootFolder);
	}

	public void saveFolder(FolderTreeNode parentFolder) {

		int count = parentFolder.getChildCount();
		FolderTreeNode child;
		FolderTreeNode folder;

		for (Enumeration e = parentFolder.children(); e.hasMoreElements();) {

			child = (FolderTreeNode) e.nextElement();

			if (child instanceof CachedMHFolder) {
				CachedMHFolder mhFolder = (CachedMHFolder) child;
				try {
					mhFolder.save();
				} catch (Exception ex) {
					ex.printStackTrace();
				}
			} else if (child instanceof OutboxFolder) {
				OutboxFolder outboxFolder = (OutboxFolder) child;
				try {
					outboxFolder.save();
				} catch (Exception ex) {
					ex.printStackTrace();
				}
			} else if (child instanceof IMAPFolder) {
				IMAPFolder imapFolder = (IMAPFolder) child;

				try {
					imapFolder.save();
				} catch (Exception ex) {
					ex.printStackTrace();
				}
			}

			saveFolder(child);
		}
	}

}