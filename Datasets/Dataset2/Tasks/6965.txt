import org.columba.core.gui.frame.FrameController;

/*
 * Created on 26.03.2003
 *
 * To change this generated comment go to 
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
package org.columba.addressbook.gui.action;

import java.awt.event.ActionEvent;
import java.awt.event.KeyEvent;

import javax.swing.KeyStroke;

import org.columba.addressbook.util.AddressbookResourceLoader;
import org.columba.core.action.FrameAction;
import org.columba.core.gui.FrameController;
import org.columba.core.gui.util.ImageLoader;

/**
 * @author frd
 *
 * To change this generated comment go to 
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
public class DeleteAction extends FrameAction {

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
	public DeleteAction(FrameController frameController) {
		super(
			frameController,
			AddressbookResourceLoader.getString(
				"menu",
				"mainframe",
				"menu_edit_delete"),
			AddressbookResourceLoader.getString(
				"menu",
				"mainframe",
				"menu_edit_delete"),
			"DELETE",
			ImageLoader.getSmallImageIcon("stock_paste-16.png"),
			ImageLoader.getImageIcon("stock_paste.png"),
			'D',
			KeyStroke.getKeyStroke(KeyEvent.VK_D, ActionEvent.CTRL_MASK));
		
	}

	/* (non-Javadoc)
	 * @see java.awt.event.ActionListener#actionPerformed(java.awt.event.ActionEvent)
	 */
	public void actionPerformed(ActionEvent evt) {
		// TODO Auto-generated method stub
		super.actionPerformed(evt);
	}

}