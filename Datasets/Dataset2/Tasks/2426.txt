public void shutdown() {

package org.columba.addressbook.shutdown;

import org.columba.addressbook.folder.Folder;
import org.columba.addressbook.folder.LocalHeaderCacheFolder;
import org.columba.addressbook.gui.tree.AddressbookTreeNode;
import org.columba.core.main.MainInterface;
import org.columba.core.shutdown.ShutdownPluginInterface;

/**
 * @author freddy
 *
 * To change this generated comment edit the template variable "typecomment":
 * Window>Preferences>Java>Templates.
 * To enable and disable the creation of type comments go to
 * Window>Preferences>Java>Code Generation.
 */
public class SaveAllAddressbooksPlugin implements ShutdownPluginInterface {

	/**
	 * Constructor for SaveAllFoldersPlugin.
	 */
	public SaveAllAddressbooksPlugin() {
		super();
	}

	/**
	 * @see org.columba.core.shutdown.ShutdownPluginInterface#run()
	 */
	public void run() {
		saveFolders(
			(AddressbookTreeNode) MainInterface
				.addressbookInterface
				.treeModel
				.getRoot());
	}

	public void saveFolders(AddressbookTreeNode folder) {
		for (int i = 0; i < folder.getChildCount(); i++) {
			AddressbookTreeNode child = (AddressbookTreeNode) folder.getChildAt(i);

			if (child instanceof LocalHeaderCacheFolder) {
				try {

					((LocalHeaderCacheFolder) child).save(null);
				} catch (Exception ex) {
					ex.printStackTrace();
				}
			}
		}
	}

}