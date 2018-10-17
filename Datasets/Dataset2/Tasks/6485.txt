import org.columba.core.gui.frame.FrameController;

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
import org.columba.core.gui.FrameController;
import org.columba.core.gui.util.ImageLoader;
import org.columba.core.main.MainInterface;
import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.folder.command.ApplyFilterCommand;
import org.columba.mail.util.MailResourceLoader;

/**
 * @author frd
 *
 * To change this generated comment go to 
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
public class ApplyFilterAction extends FrameAction {

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
	public ApplyFilterAction(FrameController frameController) {
		super(
			frameController,
			MailResourceLoader.getString(
				"menu",
				"mainframe",
				"menu_folder_applyfilter"),
			MailResourceLoader.getString(
				"menu",
				"mainframe",
				"menu_folder_applyfilter"),
			MailResourceLoader.getString(
				"menu",
				"mainframe",
				"menu_folder_applyfilter"),
			"APPLYFILTER",
			ImageLoader.getSmallImageIcon("apply-filters-16.png"),
			null,
			'F',
			KeyStroke.getKeyStroke(KeyEvent.VK_A, ActionEvent.ALT_MASK));

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

		//Folder folder = (Folder) r[0].getFolder();
		MainInterface.processor.addOp(new ApplyFilterCommand(r));
	}

}