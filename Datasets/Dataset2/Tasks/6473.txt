import org.columba.core.gui.frame.FrameController;

/*
 * Created on 25.03.2003
 *
 * To change this generated comment go to 
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
package org.columba.mail.gui.composer.action;

import java.awt.event.ActionEvent;

import org.columba.core.action.FrameAction;
import org.columba.core.gui.FrameController;
import org.columba.core.util.SwingWorker;
import org.columba.mail.gui.composer.ComposerController;
import org.columba.mail.gui.composer.util.ExternalEditor;
import org.columba.mail.util.MailResourceLoader;

/**
 * @author frd
 *
 * To change this generated comment go to 
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
public class ExternalEditorAction extends FrameAction {

	/**
	 * @param composerController
	 * @param name
	 * @param longDescription
	 * @param tooltip
	 * @param actionCommand
	 * @param small_icon
	 * @param big_icon
	 * @param mnemonic
	 * @param keyStroke
	 */
	public ExternalEditorAction(FrameController frameController) {
		super(
			frameController,
			MailResourceLoader.getString(
				"menu",
				"composer",
				"menu_edit_extern_edit"),
			MailResourceLoader.getString(
				"menu",
				"composer",
				"menu_edit_extern_edit"),
			MailResourceLoader.getString(
				"menu",
				"composer",
				"menu_edit_extern_edit"),
			"EXTERNEDIT",
			null,
			null,
			MailResourceLoader.getMnemonic(
				"menu",
				"composer",
				"menu_edit_extern_edit"),
			null);

	}

	/* (non-Javadoc)
	 * @see java.awt.event.ActionListener#actionPerformed(java.awt.event.ActionEvent)
	 */
	public void actionPerformed(ActionEvent evt) {
		final ComposerController composerController = (ComposerController ) getFrameController();
		
		final SwingWorker worker = new SwingWorker() {
			public Object construct() {
				//composerInterface.composerFrame.setCursor(Cursor.WAIT_CURSOR);
				composerController.getView().setEnabled(false);
				composerController.getEditorController().getView().setEnabled(false);
				ExternalEditor Ed = new ExternalEditor();
				Ed.startExternalEditor(
				composerController.getEditorController().getView());
				return Ed;
			}

			//Runs on the event-dispatching thread.
			public void finished() {
				composerController.getView().setEnabled(true);
				composerController.getEditorController().getView().setEnabled(true);
				//composerInterface.composerFrame.setCursor(Cursor.DEFAULT_CURSOR);
			}
		};
		worker.start(); //required for SwingWorker 3

	}

}