AddressbookFrameController addressbookFrameController = (AddressbookFrameController) frameMediator;

/*
 * Created on 26.03.2003
 *
 * To change this generated comment go to 
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
package org.columba.addressbook.gui.action;

import java.awt.event.ActionEvent;

import org.columba.addressbook.folder.ContactCard;
import org.columba.addressbook.folder.Folder;
import org.columba.addressbook.gui.dialog.contact.ContactDialog;
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
public class AddContactCardAction extends FrameAction {

	public AddContactCardAction(AbstractFrameController frameController) {
		super(
				frameController,
				AddressbookResourceLoader.getString(
					"menu", "mainframe", "menu_file_addcontact"));
		
		// tooltip text
		setTooltipText(
				AddressbookResourceLoader.getString(
					"menu", "mainframe", "menu_file_addcontact_tooltip"));
					
		setToolBarText(
						AddressbookResourceLoader.getString(
							"menu", "mainframe", "menu_file_addcontact_toolbar"));
		enableToolBarText(true);
		
		// action command
		setActionCommand("ADDCONTACT");
		
		// icons
		setSmallIcon(ImageLoader.getSmallImageIcon("contact_small.png"));
		setLargeIcon(ImageLoader.getImageIcon("contact.png"));

	}

	/* (non-Javadoc)
	 * @see java.awt.event.ActionListener#actionPerformed(java.awt.event.ActionEvent)
	 */
	public void actionPerformed(ActionEvent evt) {
		AddressbookFrameController addressbookFrameController = (AddressbookFrameController) frameController;
		
		ContactDialog dialog =
				new ContactDialog(addressbookFrameController.getView());

			dialog.setVisible(true);
			if (dialog.getResult()) {
				System.out.println("saving contact");

				// Ok

				ContactCard card = new ContactCard();

				dialog.updateComponents(card, false);

				Folder folder = addressbookFrameController.getTree().getView().getSelectedFolder();

				folder.add(card);

				addressbookFrameController.getTable().getView().setFolder(folder);
			}
	}

}