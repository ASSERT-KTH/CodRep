(ComposerController) getFrameMediator();

/*
 * Created on 25.03.2003
 *
 * To change this generated comment go to 
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
package org.columba.mail.gui.composer.action;

import java.awt.event.ActionEvent;
import java.awt.event.KeyEvent;

import javax.swing.KeyStroke;

import org.columba.core.action.FrameAction;
import org.columba.core.gui.frame.AbstractFrameController;
import org.columba.core.gui.util.ImageLoader;
import org.columba.mail.gui.composer.ComposerController;
import org.columba.mail.util.MailResourceLoader;

/**
 * Start interactive spell-checking of composed message.
 *
 * @author fdietz
 */
public class SpellcheckAction extends FrameAction {

	public SpellcheckAction(AbstractFrameController frameController) {
		super(
				frameController,
				MailResourceLoader.getString(
					"menu", "composer",	"menu_message_spellCheck"));
		
		// tooltip text
		setTooltipText(
				MailResourceLoader.getString(
					"menu", "composer",	"menu_message_spellCheck_tooltip"));
		
		// action command
		setActionCommand("SPELLCHECK");
		
		// large icon for toolbar
		setLargeIcon(ImageLoader.getImageIcon("stock_spellcheck_24.png"));
		
		// small icon for menu
		setSmallIcon(ImageLoader.getSmallImageIcon("stock_spellcheck_16.png"));
		
		// disable text in toolbar
		enableToolBarText(false);
		
//		shortcut key
		setAcceleratorKey(KeyStroke.getKeyStroke(KeyEvent.VK_L, ActionEvent.CTRL_MASK | ActionEvent.SHIFT_MASK));
		
	}

	/* (non-Javadoc)
	 * @see java.awt.event.ActionListener#actionPerformed(java.awt.event.ActionEvent)
	 */
	public void actionPerformed(ActionEvent evt) {
		ComposerController composerController =
			(ComposerController) getFrameController();

		//String checked =
		//	composerController.getComposerSpellCheck().checkText(
		//		composerController.getEditorController().getView().getText());
		String checked =
			composerController.getComposerSpellCheck().checkText(
				composerController.getEditorController().getViewText());


		//composerController.getEditorController().getView().setText(checked);
		composerController.getEditorController().setViewText(checked);
	}

}