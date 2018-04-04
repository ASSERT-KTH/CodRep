import org.columba.core.main.MainInterface;

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

package org.columba.mail.gui.frame.action;

import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.net.MalformedURLException;
import java.net.URL;

import org.columba.core.config.ViewItem;
import org.columba.core.gui.util.AboutDialog;
import org.columba.core.gui.util.ImageLoader;
import org.columba.core.gui.util.ThemeSwitcher;
import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.command.POP3CommandReference;
import org.columba.mail.config.MailConfig;
import org.columba.mail.folder.Folder;
import org.columba.mail.folder.outbox.OutboxFolder;
import org.columba.mail.gui.action.BasicAction;
import org.columba.mail.gui.composer.ComposerController;
import org.columba.mail.gui.config.general.GeneralOptionsDialog;
import org.columba.mail.gui.config.mailboximport.ImportWizard;
import org.columba.mail.gui.frame.MailFrameController;
import org.columba.mail.gui.util.URLController;
import org.columba.mail.pop3.FetchNewMessagesCommand;
import org.columba.mail.pop3.POP3ServerController;
import org.columba.mail.smtp.SendAllMessagesCommand;
import org.columba.mail.util.MailResourceLoader;
import org.columba.main.MainInterface;

public class FrameActionListener implements ActionListener {

	MailFrameController frameController;

	public BasicAction exitAction;
	public BasicAction generalOptionsAction;

	public BasicAction findAction;
	public BasicAction findAgainAction;

	public FrameActionListener(MailFrameController c) {
		this.frameController = c;

		initActions();
	}

	public void initActions() {

		exitAction =
			new BasicAction(
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_file_exit"),
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_file_exit"),
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_file_exit"),
				"EXIT",
				ImageLoader.getSmallImageIcon("stock_exit-16.png"),
				ImageLoader.getImageIcon("stock_exit.png"),
				'X',
				null);
		exitAction.addActionListener(this);
		generalOptionsAction =
			new BasicAction(
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_edit_generaloptions"),
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_edit_generaloptions_tooltip"),
				"GENERAL_OPTIONS",
				ImageLoader.getSmallImageIcon("stock_preferences-16.png"),
				ImageLoader.getImageIcon("stock_preferences.png"),
				'0',
				null);
		generalOptionsAction.addActionListener(this);

		findAction =
			new BasicAction(
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_edit_find"),
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_edit_find_tooltip"),
				"FIND",
				ImageLoader.getSmallImageIcon("stock_search-16.png"),
				ImageLoader.getImageIcon("stock_search.png"),
				'0',
				null);
		findAction.setEnabled(false);

		findAgainAction =
			new BasicAction(
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_edit_findagain"),
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_edit_findagain_tooltip"),
				"FIND_AGAIN",
				null,
				null,
				'0',
				null);

		findAgainAction.setEnabled(false);
	}

	public void actionPerformed(ActionEvent e) {
		String action = e.getActionCommand();

		if (action.equals("ACCOUNT_PREFERENCES")) {
			org.columba.mail.gui.config.account.ConfigFrame frame =
				new org.columba.mail.gui.config.account.ConfigFrame();

		} else if (
			action.equals(
				frameController
					.globalActionCollection
					.searchMessageAction
					.getActionCommand())) {
			Folder searchFolder =
				(Folder) MainInterface.treeModel.getFolder(106);
			
			org.columba.mail.gui.config.search.SearchFrame frame =
				new org.columba.mail.gui.config.search.SearchFrame(
					frameController,
					searchFolder);

			
		} else if (action.equals("RECEIVESEND")) {
			System.out.println("receive and send messages");

			POP3ServerController[] list =
				MainInterface.popServerCollection.getList();

			for (int i = 0; i < list.length; i++) {
				POP3ServerController controller =
					(POP3ServerController) list[i];

				POP3CommandReference[] r = new POP3CommandReference[1];
				r[0] = new POP3CommandReference(controller.getServer());

				FetchNewMessagesCommand c =
					new FetchNewMessagesCommand( r);

				MainInterface.processor.addOp(c);
			}

		} else if (action.equals("RECEIVE")) {
			System.out.println("receive messages");

			POP3ServerController[] list =
				MainInterface.popServerCollection.getList();

			for (int i = 0; i < list.length; i++) {
				POP3ServerController controller =
					(POP3ServerController) list[i];

				POP3CommandReference[] r = new POP3CommandReference[1];
				r[0] = new POP3CommandReference(controller.getServer());

				FetchNewMessagesCommand c =
					new FetchNewMessagesCommand(r);

				MainInterface.processor.addOp(c);
			}

			/*
			MainInterface.popServerCollection.fetchAllServers();
			*/

		} else if (action.equals("SEND")) {
			System.out.println("send messages");

			FolderCommandReference[] r = new FolderCommandReference[1];
			OutboxFolder folder =
				(OutboxFolder) MainInterface.treeModel.getFolder(103);

			r[0] = new FolderCommandReference(folder);

			SendAllMessagesCommand c =
				new SendAllMessagesCommand(frameController, r);

			MainInterface.processor.addOp(c);

		} else if (action.equals("VIEW_TOOLBAR")) {
			System.out.println("show toolbar");
			ViewItem item =
				MailConfig.getMainFrameOptionsConfig().getViewItem();
			boolean folderInfo = item.getBoolean("toolbars", "show_folderinfo");
			boolean toolbar = item.getBoolean("toolbars", "show_main");
			if (toolbar == true) {

				frameController.getView().hideToolbar(folderInfo);
				item.set("toolbars", "show_main", false);
			} else {

				frameController.getView().showToolbar(folderInfo);
				item.set("toolbars", "show_main", true);
			}

		} else if (action.equals("VIEW_FILTERTOOLBAR")) {

			System.out.println("show filtertoolbar");
			ViewItem item =
				MailConfig.getMainFrameOptionsConfig().getViewItem();
			boolean folderInfo = item.getBoolean("toolbars", "show_folderinfo");
			boolean toolbar = item.getBoolean("toolbars", "show_main");
			boolean filter = item.getBoolean("toolbars", "show_filter");
			if (filter == true) {

				frameController.getView().hideFilterToolbar();
				item.set("toolbars", "show_filter", false);
			} else {

				frameController.getView().showFilterToolbar();
				item.set("toolbars", "show_filter", true);
			}

		} else if (action.equals("VIEW_FOLDERINFO")) {
			System.out.println("show folderinfo");
			ViewItem item =
				MailConfig.getMainFrameOptionsConfig().getViewItem();
			boolean folderInfo = item.getBoolean("toolbars", "show_folderinfo");
			boolean toolbar = item.getBoolean("toolbars", "show_main");
			boolean filter = item.getBoolean("toolbars", "show_filter");

			if (folderInfo == true) {

				frameController.getView().hideFolderInfo(toolbar);
				item.set("toolbars", "show_folderinfo", false);
			} else {

				frameController.getView().showFolderInfo(toolbar);
				item.set("toolbars", "show_folderinfo", true);
			}

		} else if (action.equals("USE_ADVANCEDVIEWER")) {

			/*
			System.out.println("advance dviewer");
			
			boolean b =
				MailConfig
					.getMainFrameOptionsConfig()
					.getWindowItem()
					.getAdvancedViewer();
			
			if (b == true) {
			
				MainInterface.messageViewer.createTextPane(false, false);
				MailConfig
					.getMainFrameOptionsConfig()
					.getWindowItem()
					.setAdvancedViewer(
					false);
			} else {
			
				MainInterface.messageViewer.createTextPane(true, false);
				MailConfig
					.getMainFrameOptionsConfig()
					.getWindowItem()
					.setAdvancedViewer(
					true);
			}
			*/
		} else if (action.equals("ABOUT")) {
			AboutDialog dialog = new AboutDialog();

		} else if (action.equals("ADDRESSBOOK")) {
			//AddressbookFrame frame = new AddressbookFrame( );
			MainInterface.addressbookInterface.frame.setVisible(true);

		} else if (action.equals("MAIN_PREFERENCES")) {

		} else if (action.equals("IMPORT")) {
			ImportWizard wizard = new ImportWizard();

		} else if (action.equals("GENERAL_OPTIONS")) {
			GeneralOptionsDialog dialog =
				new GeneralOptionsDialog(frameController.getView());
			dialog.updateComponents(true);
			dialog.setVisible(true);

			if (dialog.getResult() == true) {
				dialog.updateComponents(false);

				ThemeSwitcher.setTheme();
				ThemeSwitcher.updateFrame(frameController.getView());
			}
		} else if (action.equals("HOMEPAGE")) {
			URLController c = new URLController();
			try {
				c.open(new URL("http://columba.sourceforge.net"));
			} catch (MalformedURLException mue) {
			}
		} else if (action.equals("FAQ")) {
			URLController c = new URLController();
			try {
				c.open(
					new URL("http://columba.sourceforge.net/index.php?page=faq"));
			} catch (MalformedURLException mue) {
			}
		} else if (action.equals("LICENSE")) {
			URLController c = new URLController();
			try {
				c.open(
					new URL("http://columba.sourceforge.net/index.php?page=license"));
			} catch (MalformedURLException mue) {
			}
		} else if (action.equals("BUGREPORT")) {
			URLController c = new URLController();
			try {
				c.open(
					new URL("http://www.sourceforge.net/projects/columba/bugs"));
			} catch (MalformedURLException mue) {
			}
		} else if (action.equals("SOURCEFORGE")) {
			URLController c = new URLController();
			try {
				c.open(new URL("http://www.sourceforge.net/projects/columba"));
			} catch (MalformedURLException mue) {
			}
		} else if (action.equals("EXIT")) {
			/*
			ExitWorker worker = new ExitWorker();
			worker.register(MainInterface.taskManager);
			worker.start();
			*/
			MainInterface.frameModel.close();

		} else if (action.equals("NEW_MESSAGE")) {

			ComposerController controller = new ComposerController();
			controller.showComposerWindow();

		} else if (action.equals("OPEN_NEW_WINDOW")) {
			MainInterface.frameModel.openView();
		}

	}

}