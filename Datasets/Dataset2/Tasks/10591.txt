//setEnabled(false);

/*
 * Created on 25.03.2003
 *
 * To change this generated comment go to 
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
package org.columba.mail.gui.composer.action;

import java.awt.event.ActionEvent;

import org.columba.core.action.CheckBoxAction;
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
public class SignMessageAction extends CheckBoxAction {

	public SignMessageAction(ComposerController composerController) {
		super(
				composerController,
				MailResourceLoader.getString(
					"menu", "composer", "menu_message_sign"));
		
		// tooltip text
		setTooltipText(
				MailResourceLoader.getString(
					"menu", "composer", "menu_message_sign"));
					
		// action command
		setActionCommand("SIGN");
		
		// TODO: Use & to define mnemonic instead
		setMnemonic(
				MailResourceLoader.getMnemonic(
					"menu", "composer", "menu_message_sign"));

		setEnabled(false);
	}

	/* (non-Javadoc)
	 * @see java.awt.event.ActionListener#actionPerformed(java.awt.event.ActionEvent)
	 */
	public void actionPerformed(ActionEvent evt) {
		ColumbaLogger.log.debug("start signing...");
		
		ComposerModel model = (ComposerModel) ((ComposerController)getFrameController()).getModel();
		model.setSignMessage( getCheckBoxMenuItem().isSelected() );
	}

}