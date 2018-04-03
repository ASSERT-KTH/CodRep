null,

// This program is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation; either version 2 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Library General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program; if not, write to the Free Software
// Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

package org.columba.mail.gui.composer.action;

import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.KeyEvent;

import javax.swing.KeyStroke;

import org.columba.addressbook.gui.SelectAddressDialog;
import org.columba.core.action.BasicAction;
import org.columba.core.config.ViewItem;
import org.columba.core.gui.util.ImageLoader;
import org.columba.core.main.MainInterface;
import org.columba.core.util.SwingWorker;
import org.columba.mail.command.ComposerCommandReference;
import org.columba.mail.config.AccountItem;
import org.columba.mail.config.MailConfig;
import org.columba.mail.config.SpecialFoldersItem;
import org.columba.mail.folder.Folder;
import org.columba.mail.folder.outbox.OutboxFolder;
import org.columba.mail.gui.composer.ComposerController;
import org.columba.mail.gui.composer.ComposerInterface;
import org.columba.mail.gui.composer.command.SaveMessageCommand;
import org.columba.mail.gui.composer.util.ExternalEditor;
import org.columba.mail.smtp.SendMessageCommand;
import org.columba.mail.util.MailResourceLoader;

public class ComposerActionListener implements ActionListener {
	private ComposerInterface composerInterface;

	public BasicAction undoAction;
	public BasicAction redoAction;
	public BasicAction attachFileAction;
	public BasicAction spellCheckAction;
	public BasicAction attachMessageAction;
	public BasicAction cutAction;
	public BasicAction copyAction;
	public BasicAction pasteAction;
	public BasicAction deleteAction;
	public BasicAction sendAction;
	public BasicAction sendLaterAction;
	public BasicAction newAction;
	public BasicAction saveAction;
	public BasicAction saveAsAction;
	public BasicAction saveDraftAction;
	public BasicAction saveTemplateAction;
	public BasicAction exitAction;
	public BasicAction addressbookAction;
	public BasicAction selectAllAction;
	public BasicAction signAction;
	public BasicAction encryptAction;
	// 09/16/02 ALP
	// Added as part of external editor support
	public BasicAction externEditAction;

	public ComposerActionListener(ComposerInterface iface) {
		composerInterface = iface;
		composerInterface.composerActionListener = this;

		initActions();
	}

	private void initActions() {

		undoAction =
			new BasicAction(
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_edit_undo"),
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_edit_undo"),
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_edit_undo"),
				"UNDO",
				ImageLoader.getSmallImageIcon("stock_undo-16.png"),
				ImageLoader.getImageIcon("stock_undo.png"),
				MailResourceLoader.getMnemonic(
					"menu",
					"composer",
					"menu_edit_undo"),
				KeyStroke.getKeyStroke(KeyEvent.VK_Z, ActionEvent.CTRL_MASK),
				false);
		undoAction.addActionListener(this);
		undoAction.setEnabled(true);

		redoAction =
			new BasicAction(
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_edit_redo"),
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_edit_redo"),
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_edit_redo"),
				"REDO",
				ImageLoader.getSmallImageIcon("stock_redo-16.png"),
				ImageLoader.getImageIcon("stock_redo.png"),
				MailResourceLoader.getMnemonic(
					"menu",
					"composer",
					"menu_edit_redo"),
				KeyStroke.getKeyStroke(KeyEvent.VK_Y, ActionEvent.CTRL_MASK),
				false);
		redoAction.addActionListener(this);
		redoAction.setEnabled(true);

		cutAction =
			new BasicAction(
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_edit_cut"),
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_edit_cut"),
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_edit_cut"),
				"CUT",
				ImageLoader.getSmallImageIcon("stock_cut-16.png"),
				ImageLoader.getImageIcon("stock_cut.png"),
				MailResourceLoader.getMnemonic(
					"menu",
					"composer",
					"menu_edit_cut"),
				KeyStroke.getKeyStroke(KeyEvent.VK_X, ActionEvent.CTRL_MASK),
				false);
		cutAction.addActionListener(this);
		cutAction.setEnabled(true);

		copyAction =
			new BasicAction(
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_edit_copy"),
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_edit_copy"),
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_edit_copy"),
				"COPY",
				ImageLoader.getSmallImageIcon("stock_copy-16.png"),
				ImageLoader.getImageIcon("stock_copy.png"),
				MailResourceLoader.getMnemonic(
					"menu",
					"composer",
					"menu_edit_copy"),
				KeyStroke.getKeyStroke(KeyEvent.VK_C, ActionEvent.CTRL_MASK),
				false);
		copyAction.addActionListener(this);
		copyAction.setEnabled(true);

		pasteAction =
			new BasicAction(
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_edit_paste"),
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_edit_paste"),
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_edit_paste"),
				"PASTE",
				ImageLoader.getSmallImageIcon("stock_paste-16.png"),
				ImageLoader.getImageIcon("stock_paste.png"),
				MailResourceLoader.getMnemonic(
					"menu",
					"composer",
					"menu_edit_paste"),
				KeyStroke.getKeyStroke(KeyEvent.VK_V, ActionEvent.CTRL_MASK),
				false);

		pasteAction.addActionListener(this);
		pasteAction.setEnabled(false);

		attachFileAction =
			new BasicAction(
				MailResourceLoader.getString(
					"menu",
					"composer",
					"menu_message_attachFile"),
				MailResourceLoader.getString(
					"menu",
					"composer",
					"menu_message_attachFile"),
				MailResourceLoader.getString(
					"menu",
					"composer",
					"menu_message_attachFile_tooltip"),
				"ATTACH",
				ImageLoader.getSmallImageIcon("stock_attach-16.png"),
				ImageLoader.getImageIcon("stock_attach.png"),
				MailResourceLoader.getMnemonic(
					"menu",
					"composer",
					"menu_message_attachFile"),
				null);
		attachFileAction.addActionListener(this);
		attachFileAction.setEnabled(true);

		spellCheckAction =
			new BasicAction(
				MailResourceLoader.getString(
					"menu",
					"composer",
					"menu_message_spellCheck"),
				MailResourceLoader.getString(
					"menu",
					"composer",
					"menu_message_spellCheck"),
				MailResourceLoader.getString(
					"menu",
					"composer",
					"menu_message_spellCheck"),
				"SPELLCHECK",
				ImageLoader.getSmallImageIcon("stock_spellcheck_16.png"),
				ImageLoader.getImageIcon("stock_spellcheck_24.png"),
				MailResourceLoader.getMnemonic(
					"menu",
					"composer",
					"menu_message_spellCheck"),
				null,
				false);
		spellCheckAction.addActionListener(this);
		spellCheckAction.setEnabled(true);

		attachMessageAction =
			new BasicAction(
				MailResourceLoader.getString(
					"menu",
					"composer",
					"menu_message_attachMessage"),
				MailResourceLoader.getString(
					"menu",
					"composer",
					"menu_message_attachMessage"),
				MailResourceLoader.getString(
					"menu",
					"composer",
					"menu_message_attachMessage"),
				"QUOTE",
				ImageLoader.getSmallImageIcon("stock_attach-16.png"),
				ImageLoader.getImageIcon("stock_attach.png"),
				MailResourceLoader.getMnemonic(
					"menu",
					"composer",
					"menu_message_attachMessage"),
				null);
		attachMessageAction.addActionListener(this);
		attachMessageAction.setEnabled(true);

		sendAction =
			new BasicAction(
				MailResourceLoader.getString(
					"menu",
					"composer",
					"menu_file_send"),
				MailResourceLoader.getString(
					"menu",
					"composer",
					"menu_file_send"),
				MailResourceLoader.getString(
					"menu",
					"composer",
					"menu_file_send_tooltip"),
				"SEND",
				ImageLoader.getSmallImageIcon("send-16.png"),
				ImageLoader.getImageIcon("send-24.png"),
				MailResourceLoader.getMnemonic(
					"menu",
					"composer",
					"menu_file_send"),
				KeyStroke.getKeyStroke(
					KeyEvent.VK_ENTER,
					ActionEvent.CTRL_MASK));
		sendAction.addActionListener(this);
		sendAction.setEnabled(true);

		sendLaterAction =
			new BasicAction(
				MailResourceLoader.getString(
					"menu",
					"composer",
					"menu_file_sendlater"),
				MailResourceLoader.getString(
					"menu",
					"composer",
					"menu_file_sendlater"),
				MailResourceLoader.getString(
					"menu",
					"composer",
					"menu_file_sendlater"),
				"SENDLATER",
				ImageLoader.getSmallImageIcon("send-later-16.png"),
				null,
				MailResourceLoader.getMnemonic(
					"menu",
					"composer",
					"menu_file_sendlater"),
				null);
		sendLaterAction.addActionListener(this);
		sendLaterAction.setEnabled(true);

		saveAction =
			new BasicAction(
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_file_save"),
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_file_save"),
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_file_save"),
				"SAVE",
				ImageLoader.getSmallImageIcon("stock_save-16.png"),
				ImageLoader.getImageIcon("stock_save.png"),
				MailResourceLoader.getMnemonic(
					"menu",
					"mainframe",
					"menu_file_save"),
				KeyStroke.getKeyStroke(KeyEvent.VK_W, ActionEvent.CTRL_MASK));
		saveAction.addActionListener(this);
		saveAction.setEnabled(false);

		saveAsAction =
			new BasicAction(
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_file_saveas"),
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_file_saveas"),
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_file_saveas"),
				"SAVEAS",
				ImageLoader.getSmallImageIcon("stock_save_as-16.png"),
				ImageLoader.getImageIcon("stock_save_as.png"),
				MailResourceLoader.getMnemonic(
					"menu",
					"mainframe",
					"menu_file_saveas"),
				KeyStroke.getKeyStroke(KeyEvent.VK_S, ActionEvent.CTRL_MASK));
		saveAsAction.addActionListener(this);
		saveAsAction.setEnabled(false);

		saveDraftAction =
			new BasicAction(
				MailResourceLoader.getString(
					"menu",
					"composer",
					"menu_file_savedraft"),
				MailResourceLoader.getString(
					"menu",
					"composer",
					"menu_file_savedraft"),
				MailResourceLoader.getString(
					"menu",
					"composer",
					"menu_file_savedraft"),
				"SAVEDRAFT",
				null,
				null,
				MailResourceLoader.getMnemonic(
					"menu",
					"composer",
					"menu_file_savedraft"),
				null);
		saveDraftAction.addActionListener(this);
		saveDraftAction.setEnabled(true);

		saveAsAction.setEnabled(false);

		saveTemplateAction =
			new BasicAction(
				MailResourceLoader.getString(
					"menu",
					"composer",
					"menu_file_savetemplate"),
				MailResourceLoader.getString(
					"menu",
					"composer",
					"menu_file_savetemplate"),
				MailResourceLoader.getString(
					"menu",
					"composer",
					"menu_file_savetemplate"),
				"SAVETEMPLATE",
				null,
				null,
				MailResourceLoader.getMnemonic(
					"menu",
					"composer",
					"menu_file_savetemplate"),
				null);
		saveTemplateAction.addActionListener(this);
		saveTemplateAction.setEnabled(true);

		newAction =
			new BasicAction(
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_file_new"),
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_file_new"),
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_file_new"),
				"NEW",
				ImageLoader.getSmallImageIcon("stock_edit-16.png"),
				ImageLoader.getImageIcon("stock_edit.png"),
				MailResourceLoader.getMnemonic(
					"menu",
					"mainframe",
					"menu_file_new"),
				KeyStroke.getKeyStroke(KeyEvent.VK_M, ActionEvent.CTRL_MASK));
		newAction.addActionListener(this);
		newAction.setEnabled(true);

		exitAction =
			new BasicAction(
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_file_close"),
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_file_close"),
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_file_close"),
				"EXIT",
				ImageLoader.getSmallImageIcon("stock_exit-16.png"),
				ImageLoader.getImageIcon("stock_exit.png"),
				MailResourceLoader.getMnemonic(
					"menu",
					"mainframe",
					"menu_file_close"),
				KeyStroke.getKeyStroke(KeyEvent.VK_W, ActionEvent.CTRL_MASK));
		exitAction.addActionListener(this);
		exitAction.setEnabled(true);

		addressbookAction =
			new BasicAction(
				MailResourceLoader.getString(
					"menu",
					"composer",
					"menu_message_addressbook"),
				MailResourceLoader.getString(
					"menu",
					"composer",
					"menu_message_addressbook"),
				MailResourceLoader.getString(
					"menu",
					"composer",
					"menu_message_addressbook"),
				"ADDRESSBOOK",
				ImageLoader.getSmallImageIcon("contact_small.png"),
				ImageLoader.getImageIcon("contact.png"),
				MailResourceLoader.getMnemonic(
					"menu",
					"composer",
					"menu_message_addressbook"),
				null,
				false);
		addressbookAction.addActionListener(this);
		addressbookAction.setEnabled(true);

		deleteAction =
			new BasicAction(
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_edit_delete"),
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_edit_delete"),
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_edit_delete"),
				"DELETE",
				ImageLoader.getSmallImageIcon("stock_delete-16.png"),
				ImageLoader.getImageIcon("stock_delete.png"),
				MailResourceLoader.getMnemonic(
					"menu",
					"composer",
					"menu_edit_delete"),
				KeyStroke.getKeyStroke(KeyEvent.VK_DELETE, 0));
		deleteAction.addActionListener(this);
		deleteAction.setEnabled(true);

		selectAllAction =
			new BasicAction(
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_edit_selectall"),
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_edit_selectall"),
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_edit_selectall"),
				"SELECTALL",
				null,
				null,
				MailResourceLoader.getMnemonic(
					"menu",
					"composer",
					"menu_edit_selectall"),
				KeyStroke.getKeyStroke(KeyEvent.VK_A, ActionEvent.CTRL_MASK));
		selectAllAction.addActionListener(this);
		selectAllAction.setEnabled(false);

		signAction =
			new BasicAction(
				MailResourceLoader.getString(
					"menu",
					"composer",
					"menu_message_sign"),
				MailResourceLoader.getString(
					"menu",
					"composer",
					"menu_message_sign"),
				MailResourceLoader.getString(
					"menu",
					"composer",
					"menu_message_sign"),
				"SIGN",
				null,
				null,
				MailResourceLoader.getMnemonic(
					"menu",
					"composer",
					"menu_message_sign"),
				null);
		signAction.addActionListener(this);
		signAction.setEnabled(true);

		encryptAction =
			new BasicAction(
				MailResourceLoader.getString(
					"menu",
					"composer",
					"menu_message_encrypt"),
				MailResourceLoader.getString(
					"menu",
					"composer",
					"menu_message_encrypt"),
				MailResourceLoader.getString(
					"menu",
					"composer",
					"menu_message_encrypt"),
				"ENCRYPT",
				ImageLoader.getSmallImageIcon("encrypt_small.png"),
				null,
				MailResourceLoader.getMnemonic(
					"menu",
					"composer",
					"menu_message_encrypt"),
				null);
		encryptAction.addActionListener(this);
		encryptAction.setEnabled(true);

		// 09/16/02 ALP
		// Added as part of external editor support
		externEditAction =
			new BasicAction(
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
				ImageLoader.getSmallImageIcon("extern_edit_small.png"),
				null,
				MailResourceLoader.getMnemonic(
					"menu",
					"composer",
					"menu_edit_extern_edit"),
				null);
		externEditAction.addActionListener(this);
		externEditAction.setEnabled(true);
	}

	protected boolean checkInformation() {

		/*
		if (composerInterface.composerHeader.getToSize() == 0) {
		
			System.out.println("no recipient");
			NotifyDialog dialog = new NotifyDialog();
			dialog.showDialog("No recipients specified!");
		
			return false;
		
		
		}
		*/

		/*
		String subject = composerInterface.editorController.getSubject();
		if (subject.length() == 0) {
		subject = new String("no subject");
		SubjectDialog dialog = new SubjectDialog(composerInterface.composerFrame);
		dialog.showDialog(subject);
		if (dialog.success() == true)
			subject = dialog.getSubject();
		
		composerInterface.composerEditor.setSubject(subject);
		}
		*/

		return true;
	}

	public void actionPerformed(ActionEvent e) {
		String command;

		command = e.getActionCommand();

		if (command.equals("NEW")) {
			ComposerController controller = new ComposerController();
			controller.showComposerWindow();

		}

		if (command.equals("SEND")) {

			/*
			if (checkInformation() == false)
				return;
			*/

			if (composerInterface.composerController.checkState() == false)
				return;

			/*
			ComposerOperation op =
				new ComposerOperation(
					Operation.COMPOSER_SEND,
					0,
					composerInterface.composerController);
			
			MainInterface.crossbar.operate(op);
			*/

			OutboxFolder outboxFolder =
				(OutboxFolder) MainInterface.treeModel.getFolder(103);

			ComposerCommandReference[] r = new ComposerCommandReference[1];
			r[0] =
				new ComposerCommandReference(
					composerInterface.composerController,
					outboxFolder);

			SendMessageCommand c = new SendMessageCommand(r);

			MainInterface.processor.addOp(c);

			return;

		}
		if (command.equals("SENDLATER")) {
			if (composerInterface.composerController.checkState() == false)
				return;

			AccountItem item =
				composerInterface
					.composerController
					.getModel()
					.getAccountItem();
			SpecialFoldersItem folderItem = item.getSpecialFoldersItem();
			String str = folderItem.get("drafts");
			int destUid = Integer.parseInt(str);
			OutboxFolder destFolder =
				(OutboxFolder) MainInterface.treeModel.getFolder(103);

			ComposerCommandReference[] r = new ComposerCommandReference[1];
			r[0] =
				new ComposerCommandReference(
					composerInterface.composerController,
					destFolder);

			SaveMessageCommand c = new SaveMessageCommand(r);

			MainInterface.processor.addOp(c);
			/*
			if (checkInformation() == false)
				return;
			*/

			/*
			if (composerInterface.composerController.checkState() == false)
				return;
			
			ComposerOperation op =
				new ComposerOperation(
					Operation.COMPOSER_SENDLATER,
					0,
					composerInterface.composerController);
			
			MainInterface.crossbar.operate(op);
			*/
		}
		if (command.equals("SAVEDRAFT")) {
			if (composerInterface.composerController.checkState() == false)
				return;

			AccountItem item =
				composerInterface
					.composerController
					.getModel()
					.getAccountItem();
			SpecialFoldersItem folderItem = item.getSpecialFoldersItem();
			String str = folderItem.get("drafts");
			int destUid = Integer.parseInt(str);
			Folder destFolder =
				(Folder) MainInterface.treeModel.getFolder(destUid);

			ComposerCommandReference[] r = new ComposerCommandReference[1];
			r[0] =
				new ComposerCommandReference(
					composerInterface.composerController,
					destFolder);

			SaveMessageCommand c = new SaveMessageCommand(r);

			MainInterface.processor.addOp(c);

			/*
			ComposerOperation op =
				new ComposerOperation(
					Operation.COMPOSER_SAVEDRAFT,
					0,
					composerInterface.composerController);
			
			MainInterface.crossbar.operate(op);
			*/

		}
		if (command.equals("SAVETEMPLATE")) {
			if (composerInterface.composerController.checkState() == false)
				return;

			AccountItem item =
				composerInterface
					.composerController
					.getModel()
					.getAccountItem();
			SpecialFoldersItem folderItem = item.getSpecialFoldersItem();
			String str = folderItem.get("templates");
			int destUid = Integer.parseInt(str);
			Folder destFolder =
				(Folder) MainInterface.treeModel.getFolder(destUid);

			ComposerCommandReference[] r = new ComposerCommandReference[1];
			r[0] =
				new ComposerCommandReference(
					composerInterface.composerController,
					destFolder);

			SaveMessageCommand c = new SaveMessageCommand(r);

			MainInterface.processor.addOp(c);
			/*
			ComposerOperation op =
				new ComposerOperation(
					Operation.COMPOSER_SAVETEMPLATE,
					0,
					composerInterface.composerController);
			
				MainInterface.crossbar.operate(op);
			*/
		}
		if (command.equals("ATTACH")) {
			composerInterface.attachmentController.addFileAttachment();
			return;
		}
		if (command.equals("SPELLCHECK")) {

			String checked =
				composerInterface.composerSpellCheck.checkText(
					composerInterface.editorController.getView().getText());

			composerInterface.editorController.getView().setText(checked);

			return;
		}

		if (command.equals("QUOTE")) {
			return;
		}
		if (command.equals("REMOVE")) {
			composerInterface.attachmentController.removeSelected();
			return;
		}
		if (command.equals("EXIT")) {

			composerInterface.composerController.saveWindowPosition();
			composerInterface.composerController.hideComposerWindow();
			return;
		}
		if (command.equals("UNDO")) {
			composerInterface.editorController.undo();
			return;
		}
		if (command.equals("REDO")) {
			composerInterface.editorController.redo();
			return;
		}
		if (command.equals("CUT")) {
			pasteAction.setEnabled(true);

			composerInterface.editorController.getView().cut();

			return;
		}
		if (command.equals("COPY")) {
			pasteAction.setEnabled(true);

			composerInterface.editorController.getView().copy();

			return;
		}
		if (command.equals("PASTE")) {

			composerInterface.editorController.getView().paste();

			return;
		}
		if (command.equals("ADDRESSBOOK")) {

			System.out.println("addressbook");

			composerInterface.headerController.cleanupHeaderItemList();

			SelectAddressDialog dialog =
				new SelectAddressDialog(
					MainInterface.addressbookInterface,
					composerInterface.composerFrame,
					composerInterface.headerController.getHeaderItemLists());

			org.columba.addressbook.folder.Folder folder =
				(org.columba.addressbook.folder.Folder) MainInterface
					.addressbookInterface
					.treeModel
					.getFolder(101);
			dialog.setHeaderList(folder.getHeaderItemList());

			dialog.setVisible(true);

			composerInterface.headerController.setHeaderItemLists(
				dialog.getHeaderItemLists());

		}
		if (command.equals("SIGN")) {
			//composerInterface.composerController.getModel().setSignMessage( true );
		}
		if (command.equals("ENCRYPT")) {
			//composerInterface.composerController.getModel().setEncryptMessage( true );
		}
		if (command.equals("VIEW_ADDRESSBOOK")) {

			ViewItem item = MailConfig.getComposerOptionsConfig().getViewItem();

			if (item.getBoolean("addressbook", "enabled") == true) {
				composerInterface.composerController.hideAddressbookWindow();
				item.set("addressbook", "enabled", false);
			} else {
				composerInterface.composerController.showAddressbookWindow();
				item.set("addressbook", "enabled", true);
			}

		}

		// 09/16/02 ALP
		// Added as part of external editor support
		if (command.equals("EXTERNEDIT")) {
			System.out.println("********************************************");
			System.out.println("*** External Editor support is pre-alpha ***");
			System.out.println("*** USE AT YOUR OWN RISK                 ***");
			System.out.println("********************************************");

			final SwingWorker worker = new SwingWorker() {
				public Object construct() {
						//composerInterface.composerFrame.setCursor(Cursor.WAIT_CURSOR);
					composerInterface.composerFrame.setEnabled(false);
					composerInterface.editorController.getView().setEnabled(
						false);
					ExternalEditor Ed = new ExternalEditor();
					Ed.startExternalEditor(
						composerInterface.editorController.getView());
					return Ed;
				}

				//Runs on the event-dispatching thread.
				public void finished() {
					composerInterface.composerFrame.setEnabled(true);
					composerInterface.editorController.getView().setEnabled(
						true);
					//composerInterface.composerFrame.setCursor(Cursor.DEFAULT_CURSOR);
				}
			};
			worker.start(); //required for SwingWorker 3
		}

	}

}