getFrameMediator()

/*
 * Created on 30.03.2003
 *
 * To change this generated comment go to 
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
package org.columba.mail.gui.attachment.action;

import java.awt.event.ActionEvent;

import org.columba.core.action.FrameAction;
import org.columba.core.gui.frame.AbstractFrameController;
import org.columba.core.gui.selection.SelectionChangedEvent;
import org.columba.core.gui.selection.SelectionListener;
import org.columba.core.gui.util.ImageLoader;
import org.columba.core.main.MainInterface;
import org.columba.mail.gui.attachment.AttachmentSelectionChangedEvent;
import org.columba.mail.gui.attachment.command.SaveAttachmentCommand;
import org.columba.mail.util.MailResourceLoader;

/**
 * @author frd
 *
 * To change this generated comment go to 
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
public class SaveAsAction extends FrameAction implements SelectionListener {

	public SaveAsAction(AbstractFrameController frameController) {
		super(
				frameController,
				MailResourceLoader.getString(
					"menu", "mainframe", "attachmentsaveas"));
		
		// tooltip text
		setTooltipText(
				MailResourceLoader.getString(
					"menu", "mainframe", "attachmentsaveas_tooltip"));
		
		// action command
		setActionCommand("SAVE_AS");
		
		// icons
		setSmallIcon(ImageLoader.getSmallImageIcon("stock_save_as-16.png"));
		setLargeIcon(ImageLoader.getImageIcon("stock_save_as.png"));

		frameController.getSelectionManager().registerSelectionListener("mail.attachment", this);
	}

	/* (non-Javadoc)
	 * @see java.awt.event.ActionListener#actionPerformed(java.awt.event.ActionEvent)
	 */
	public void actionPerformed(ActionEvent evt) {
		
		MainInterface.processor.addOp(
			new SaveAttachmentCommand(
				getFrameController()
					.getSelectionManager()
					.getHandler("mail.attachment")
					.getSelection()));
	}

	/* (non-Javadoc)
	 * @see org.columba.mail.gui.attachment.AttachmentSelectionListener#attachmentSelectionChanged(java.lang.Integer[])
	 */
	public void selectionChanged( SelectionChangedEvent e) {
		if( ((AttachmentSelectionChangedEvent)e).getAddress() != null ) {
			setEnabled( true );
		} else {
			setEnabled( false );
		}
	}

}