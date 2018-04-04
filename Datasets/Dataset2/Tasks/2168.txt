(FolderCommandReference[]) frameMediator

/*
 * Created on 11.03.2003
 *
 * To change this generated comment go to 
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
package org.columba.mail.gui.tree.action;

import java.awt.event.ActionEvent;

import javax.swing.JOptionPane;

import org.columba.core.action.FrameAction;
import org.columba.core.gui.frame.AbstractFrameController;
import org.columba.core.gui.selection.SelectionChangedEvent;
import org.columba.core.gui.selection.SelectionListener;
import org.columba.core.gui.util.ImageLoader;
import org.columba.core.main.MainInterface;
import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.config.FolderItem;
import org.columba.mail.folder.Folder;
import org.columba.mail.folder.FolderTreeNode;
import org.columba.mail.folder.command.RemoveFolderCommand;
import org.columba.mail.gui.frame.AbstractMailFrameController;
import org.columba.mail.gui.tree.selection.TreeSelectionChangedEvent;
import org.columba.mail.util.MailResourceLoader;

/**
 * @author frd
 *
 * To change this generated comment go to 
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
public class RemoveFolderAction
	extends FrameAction
	implements SelectionListener {

	public RemoveFolderAction(AbstractFrameController frameController) {
		super(
				frameController,
				MailResourceLoader.getString(
					"menu", "mainframe", "menu_folder_removefolder"));

		// tooltip text
		setTooltipText(
				MailResourceLoader.getString(
					"menu", "mainframe", "menu_folder_removefolder"));

		// action command
		setActionCommand("REMOVE_FOLDER");
		
		// icons
		setSmallIcon(ImageLoader.getSmallImageIcon("stock_delete-16.png"));
		setLargeIcon(ImageLoader.getImageIcon("stock_delete.png"));
					
		setEnabled(false);
		(
			(
				AbstractMailFrameController) frameController)
					.registerTreeSelectionListener(
			this);
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
		FolderTreeNode folder = r[0].getFolder();

		if (!folder.isLeaf()) {

			// warn user
			JOptionPane.showMessageDialog(
				null,
				"Your can only remove leaf folders!");
			return;
		} else {
		    // warn user in any other cases
            int n = JOptionPane.showConfirmDialog(
                    null,
                    MailResourceLoader.getString("tree", "tree",  "folder_warning"),
                    MailResourceLoader.getString("tree", "tree",  "folder_warning_title"),
                    JOptionPane.YES_NO_OPTION);
            if (n == JOptionPane.NO_OPTION) {
                return;
            }
        }

		MainInterface.processor.addOp(new RemoveFolderCommand(r));
	}
	/* (non-Javadoc)
					 * @see org.columba.core.gui.util.SelectionListener#selectionChanged(org.columba.core.gui.util.SelectionChangedEvent)
					 */
	public void selectionChanged(SelectionChangedEvent e) {

		if (((TreeSelectionChangedEvent) e).getSelected().length > 0) {
			FolderTreeNode folder = ((TreeSelectionChangedEvent) e).getSelected()[0];

			if (folder != null && folder instanceof Folder ) {

				FolderItem item = folder.getFolderItem();
				if (item.get("property", "accessrights").equals("user"))
					setEnabled(true);
				else
					setEnabled(false);
			}
		} else
			setEnabled(false);

	}
}