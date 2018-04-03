ComposerModel model = (ComposerModel) ((ComposerController)getFrameMediator()).getModel();

/*
 * Created on 25.03.2003
 *
 * To change this generated comment go to 
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
package org.columba.mail.gui.composer.action;

import java.awt.event.ActionEvent;

import org.columba.core.action.CheckBoxAction;
import org.columba.core.gui.util.ImageLoader;
import org.columba.core.logging.ColumbaLogger;
import org.columba.mail.gui.composer.ComposerController;
import org.columba.mail.gui.composer.ComposerModel;
import org.columba.mail.util.MailResourceLoader;

/**
 * @author frd
 *
 * To change this generated comment go to 
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
public class EncryptMessageAction extends CheckBoxAction {

	public EncryptMessageAction(ComposerController composerController) {
		
		super(
				composerController,
				MailResourceLoader.getString(
					"menu", "composer", "menu_message_encrypt"));
		
		// tooltip text
		setTooltipText(
				MailResourceLoader.getString(
					"menu", "composer", "menu_message_encrypt"));
		
		// action command
		setActionCommand("ENCRYPT");
		
		// small icon for menu
		setSmallIcon(ImageLoader.getSmallImageIcon("encrypt_small.png"));
		
		//setEnabled(false);
	}

	/* (non-Javadoc)
	 * @see java.awt.event.ActionListener#actionPerformed(java.awt.event.ActionEvent)
	 */
	public void actionPerformed(ActionEvent evt) {
		ColumbaLogger.log.debug("start encryption...");
	
		ComposerModel model = (ComposerModel) ((ComposerController)getFrameController()).getModel();
		model.setEncryptMessage( getCheckBoxMenuItem().isSelected() );
	}

}