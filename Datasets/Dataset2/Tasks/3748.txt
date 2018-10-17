final ComposerController composerController = (ComposerController ) getFrameMediator();

/*
 * Created on 25.03.2003
 *
 * To change this generated comment go to 
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
package org.columba.mail.gui.composer.action;

import java.awt.event.ActionEvent;

import org.columba.core.action.FrameAction;
import org.columba.core.gui.frame.AbstractFrameController;
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

	public ExternalEditorAction(AbstractFrameController frameController) {
		super(
				frameController,
				MailResourceLoader.getString(
					"menu", "composer", "menu_edit_extern_edit"));
		
		// tooltip text
		setTooltipText(
				MailResourceLoader.getString(
					"menu", "composer", "menu_edit_extern_edit"));
		
		// action command
		setActionCommand("EXTERNEDIT");
		
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
				//composerController.getEditorController().getView().setEnabled(false);
				composerController.getEditorController().setViewEnabled(false);
				ExternalEditor Ed = new ExternalEditor();
				//Ed.startExternalEditor(
				//	composerController.getEditorController().getView());
				Ed.startExternalEditor(
					composerController.getEditorController());
				return Ed;
			}

			//Runs on the event-dispatching thread.
			public void finished() {
				composerController.getView().setEnabled(true);
				//composerController.getEditorController().getView().setEnabled(true);
				composerController.getEditorController().setViewEnabled(true);
				//composerInterface.composerFrame.setCursor(Cursor.DEFAULT_CURSOR);
			}
		};
		worker.start(); //required for SwingWorker 3

	}

}