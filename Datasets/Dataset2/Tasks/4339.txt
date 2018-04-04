(AddressbookFrameController) frameMediator;

/*
 * Created on 26.03.2003
 *
 * To change this generated comment go to 
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
package org.columba.addressbook.gui.action;

import java.awt.event.ActionEvent;

import org.columba.addressbook.folder.Folder;
import org.columba.addressbook.folder.GroupListCard;
import org.columba.addressbook.gui.EditGroupDialog;
import org.columba.addressbook.gui.frame.AddressbookFrameController;
import org.columba.addressbook.util.AddressbookResourceLoader;
import org.columba.core.action.FrameAction;
import org.columba.core.gui.frame.AbstractFrameController;
import org.columba.core.gui.util.ImageLoader;

/**
 * @author frd
 *
 * To change this generated comment go to 
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
public class AddGroupCardAction extends FrameAction {

	public AddGroupCardAction(AbstractFrameController frameController) {
		super(
				frameController,
				AddressbookResourceLoader.getString(
					"menu", "mainframe", "menu_file_addgroup"));
					
		// tooltip text
		setTooltipText(
				AddressbookResourceLoader.getString(
					"menu", "mainframe", "menu_file_addgroup_tooltip"));
					
		setToolBarText(
						AddressbookResourceLoader.getString(
							"menu", "mainframe", "menu_file_addgroup_toolbar"));
		enableToolBarText(true);
		
		// action command
		setActionCommand("ADDGROUP");
		
		// icons
		setSmallIcon(ImageLoader.getSmallImageIcon("group_small.png"));
		setLargeIcon(ImageLoader.getImageIcon("group.png"));

	}

	/* (non-Javadoc)
	 * @see java.awt.event.ActionListener#actionPerformed(java.awt.event.ActionEvent)
	 */
	public void actionPerformed(ActionEvent evt) {
		
		AddressbookFrameController addressbookFrameController =
				(AddressbookFrameController) frameController;
		
		Folder folder =
				(Folder) addressbookFrameController.getTree().
					getView().getSelectedFolder();
		if (folder == null) return;

		EditGroupDialog dialog =
				new EditGroupDialog(
					addressbookFrameController.getView(),
					addressbookFrameController,
					null);

		dialog.setHeaderList(folder.getHeaderItemList());

		dialog.setVisible(true);

		if (dialog.getResult()) {
			// Ok
			GroupListCard card = new GroupListCard();

			dialog.updateComponents(card, null, false);

			folder.add(card);
			addressbookFrameController.getTable().getView().setFolder(folder);
		}
	}

}