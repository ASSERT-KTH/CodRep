import org.columba.mail.gui.table.selection.TableSelectionChangedEvent;

/*
 * Created on 11.03.2003
 *
 * To change this generated comment go to 
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
package org.columba.mail.gui.table.action;

import java.awt.event.ActionEvent;

import org.columba.core.action.FrameAction;
import org.columba.core.gui.frame.FrameController;
import org.columba.core.gui.selection.SelectionChangedEvent;
import org.columba.core.gui.selection.SelectionListener;
import org.columba.core.gui.util.ImageLoader;
import org.columba.core.main.MainInterface;
import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.folder.command.ExpungeFolderCommand;
import org.columba.mail.folder.command.MarkMessageCommand;
import org.columba.mail.gui.frame.MailFrameController;
import org.columba.mail.gui.table.TableSelectionChangedEvent;
import org.columba.mail.util.MailResourceLoader;

/**
 * @author frd
 *
 * To change this generated comment go to 
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
public class DeleteMessageAction
	extends FrameAction
	implements SelectionListener {

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
	 * @param showToolbarText
	 */
	public DeleteMessageAction(FrameController frameController) {
		super(
			frameController,
			MailResourceLoader.getString(
				"menu",
				"mainframe",
				"menu_message_delete"),
			MailResourceLoader.getString(
				"menu",
				"mainframe",
				"menu_message_delete_toolbar"),
			MailResourceLoader.getString(
				"menu",
				"mainframe",
				"menu_message_delete_tooltip"),
			"DELETE_MESSAGE",
			ImageLoader.getSmallImageIcon("stock_delete-16.png"),
			ImageLoader.getImageIcon("stock_delete.png"),
			'0',
			null,
			false);
		setEnabled(false);
		((MailFrameController) frameController).registerTableSelectionListener(
			this);
	}

	/* (non-Javadoc)
	 * @see java.awt.event.ActionListener#actionPerformed(java.awt.event.ActionEvent)
	 */
	public void actionPerformed(ActionEvent evt) {
		FolderCommandReference[] r =
			((MailFrameController) getFrameController()).getTableSelection();
		r[0].setMarkVariant(MarkMessageCommand.MARK_AS_EXPUNGED);

		MarkMessageCommand c = new MarkMessageCommand(r);

		MainInterface.processor.addOp(c);

		MainInterface.processor.addOp(new ExpungeFolderCommand(r));
	}
	/* (non-Javadoc)
			 * @see org.columba.core.gui.util.SelectionListener#selectionChanged(org.columba.core.gui.util.SelectionChangedEvent)
			 */
	public void selectionChanged(SelectionChangedEvent e) {

		if (((TableSelectionChangedEvent) e).getUids().length > 0)
			setEnabled(true);
		else
			setEnabled(false);

	}
}