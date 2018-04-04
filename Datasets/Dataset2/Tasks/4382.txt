import org.columba.core.gui.frame.FrameController;

/*
 * Created on 26.03.2003
 *
 * To change this generated comment go to 
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
package org.columba.addressbook.gui.action;

import java.awt.event.ActionEvent;

import org.columba.addressbook.util.AddressbookResourceLoader;
import org.columba.core.action.FrameAction;
import org.columba.core.gui.FrameController;

/**
 * @author frd
 *
 * To change this generated comment go to 
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
public class AddressbookImportAction extends FrameAction {

	/**
	 * @param frameController
	 * @param name
	 * @param longDescription
	 * @param actionCommand
	 * @param small_icon
	 * @param big_icon
	 * @param mnemonic
	 * @param keyStroke
	 */
	public AddressbookImportAction(FrameController frameController) {
		super(
			frameController,
			AddressbookResourceLoader.getString(
				"menu",
				"mainframe",
				"menu_utilities_addressbook"),
			AddressbookResourceLoader.getString(
				"menu",
				"mainframe",
				"menu_utilities_addressbook"),
			"ADDRESSBOOK_IMPORT",
			null,
			null,
			'0',
			null);

	}

	/* (non-Javadoc)
	 * @see java.awt.event.ActionListener#actionPerformed(java.awt.event.ActionEvent)
	 */
	public void actionPerformed(ActionEvent evt) {
		// TODO Auto-generated method stub
		super.actionPerformed(evt);
	}

}