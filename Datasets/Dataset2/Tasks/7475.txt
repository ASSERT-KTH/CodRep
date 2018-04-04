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

package org.columba.mail.gui.frame;

import java.awt.event.ActionEvent;
import java.awt.event.KeyEvent;
import java.awt.event.MouseAdapter;

import javax.swing.ButtonGroup;
import javax.swing.JCheckBoxMenuItem;
import javax.swing.JMenu;
import javax.swing.JMenuBar;
import javax.swing.JMenuItem;
import javax.swing.JRadioButtonMenuItem;
import javax.swing.KeyStroke;

import org.columba.core.config.ViewItem;
import org.columba.core.gui.util.CMenu;
import org.columba.core.gui.util.CMenuItem;
import org.columba.core.gui.util.ImageLoader;
import org.columba.mail.config.MailConfig;
import org.columba.mail.gui.action.BasicAction;
import org.columba.mail.pop3.POP3ServerController;
import org.columba.mail.util.MailResourceLoader;
import org.columba.main.MainInterface;

public class MailMenu extends JMenuBar {

	private MouseAdapter handler;

	private CMenu fetchMessageSubmenu;
	private CMenu manageSubmenu;
	private CMenu sortSubMenu;

	private JMenu fileMenu;
	private JMenu editMenu;
	private JMenu viewMenu;
	private JMenu folderMenu;
	private JMenu messageMenu;
	private JMenu utilitiesMenu;
	private JMenu helpMenu;

	private MailFrameController frameController;
	public MailMenu(MailFrameController frameController) {
		super();

		this.frameController = frameController;
		init();
	}

	public void updatePopServerMenu() {
		CMenuItem menuItem;

		fetchMessageSubmenu.removeAll();
		for (int i = 0; i < MainInterface.popServerCollection.count(); i++) {
			POP3ServerController c = MainInterface.popServerCollection.get(i);
			c.updateAction();
			fetchMessageSubmenu.add(new CMenuItem(c.getCheckAction()));
		}

		manageSubmenu.removeAll();
		for (int i = 0; i < MainInterface.popServerCollection.count(); i++) {
			POP3ServerController c = MainInterface.popServerCollection.get(i);
			c.updateAction();
			menuItem = new CMenuItem(c.getManageAction());
			manageSubmenu.add(menuItem);
		}

	}

	// create the menu
	private void init() {
		handler = frameController.getMouseTooltipHandler();

		JMenu menu, subMenu;
		JMenuItem menuItem;
		JRadioButtonMenuItem rbMenuItem;
		ButtonGroup group;

		fileMenu =
			new JMenu(
				MailResourceLoader.getString("menu", "mainframe", "menu_file"));
		fileMenu.setActionCommand("FILE");
		fileMenu.setMnemonic(KeyEvent.VK_F);
		add(fileMenu);

		menuItem = new CMenuItem("Open New Window..");
		menuItem.setActionCommand("OPEN_NEW_WINDOW");
		menuItem.addActionListener(frameController.getActionListener());

		fileMenu.add(menuItem);

		fileMenu.addSeparator();

		fetchMessageSubmenu =
			new CMenu(
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_file_checkmessage"));

		for (int i = 0; i < MainInterface.popServerCollection.count(); i++) {
			fetchMessageSubmenu.add(
				new CMenuItem(
					MainInterface.popServerCollection.get(i).getCheckAction()));
		}

		fileMenu.add(fetchMessageSubmenu);

		fileMenu.addSeparator();

		/*
		  JMenuItem item = new JMenuItem("Receive and Send Messages");
		  item.setActionCommand("RECEIVE_SEND");
		  item.addActionListener( new FrameActionListener( mainInterface ) );
		*/

		menuItem =
			new CMenuItem(
				frameController.globalActionCollection.receiveSendAction);
		menuItem.addMouseListener(handler);
		fileMenu.add(menuItem);

		//menu.addSeparator();

		JMenuItem item =
			new CMenuItem(
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_file_receive"));
		item.setAccelerator(
			KeyStroke.getKeyStroke(KeyEvent.VK_T, ActionEvent.CTRL_MASK));
		item.setActionCommand("RECEIVE");
		item.addActionListener(frameController.getActionListener());
		fileMenu.add(item);

		item =
			new CMenuItem(
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_file_sendunsentmessages"));
		item.setActionCommand("SEND");
		item.addActionListener(frameController.getActionListener());
		fileMenu.add(item);

		fileMenu.addSeparator();

		manageSubmenu =
			new CMenu(
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_file_manage"));

		for (int i = 0; i < MainInterface.popServerCollection.count(); i++) {
			menuItem =
				new CMenuItem(
					MainInterface.popServerCollection.get(i).getManageAction());
			menuItem.setEnabled(true);
			manageSubmenu.add(menuItem);
		}

		fileMenu.add(manageSubmenu);

		fileMenu.addSeparator();

		menuItem =
			new CMenuItem(
				frameController
					.tableController
					.getActionListener()
					.printAction);
		menuItem.addMouseListener(handler);
		fileMenu.add(menuItem);

		fileMenu.addSeparator();

		menuItem =
			new CMenuItem(frameController.getActionListener().exitAction);
		menuItem.addMouseListener(handler);
		fileMenu.add(menuItem);

		editMenu =
			new JMenu(
				MailResourceLoader.getString("menu", "mainframe", "menu_edit"));
		editMenu.setMnemonic(KeyEvent.VK_E);
		editMenu.setActionCommand("EDIT");
		add(editMenu);

		menuItem =
			new CMenuItem(MainInterface.processor.getUndoManager().undoAction);
		menuItem.addMouseListener(handler);
		editMenu.add(menuItem);

		menuItem =
			new CMenuItem(MainInterface.processor.getUndoManager().redoAction);
		menuItem.addMouseListener(handler);
		editMenu.add(menuItem);

		editMenu.addSeparator();

		menuItem =
			new CMenuItem(frameController.globalActionCollection.cutAction);
		menuItem.addMouseListener(handler);
		editMenu.add(menuItem);

		menuItem =
			new CMenuItem(frameController.globalActionCollection.copyAction);
		menuItem.addMouseListener(handler);
		editMenu.add(menuItem);

		menuItem =
			new CMenuItem(frameController.globalActionCollection.pasteAction);
		menuItem.addMouseListener(handler);
		editMenu.add(menuItem);

		menuItem =
			new CMenuItem(frameController.globalActionCollection.deleteAction);
		menuItem.addMouseListener(handler);
		editMenu.add(menuItem);

		menuItem =
			new CMenuItem(
				frameController.globalActionCollection.selectAllAction);
		menuItem.addMouseListener(handler);
		editMenu.add(menuItem);

		editMenu.addSeparator();

		menuItem =
			new CMenuItem(frameController.getActionListener().findAction);
		editMenu.add(menuItem);

		menuItem =
			new CMenuItem(frameController.getActionListener().findAgainAction);
		editMenu.add(menuItem);

		editMenu.addSeparator();

		menuItem =
			new CMenuItem(
				frameController.globalActionCollection.searchMessageAction);
		menuItem.addMouseListener(handler);
		editMenu.add(menuItem);

		editMenu.addSeparator();

		menuItem =
			new JMenuItem(
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_edit_accountconfig"),
				ImageLoader.getSmallImageIcon("configure_16_mail.png"));
		menuItem.setMnemonic(KeyEvent.VK_U);
		menuItem.setActionCommand("ACCOUNT_PREFERENCES");
		menuItem.addActionListener(frameController.getActionListener());
		editMenu.add(menuItem);

		editMenu.addSeparator();

		/*
		menuItem =
			new JMenuItem(GlobalResourceLoader.getString("menu","mainframe", "menu_edit_preferences"));
		//ImageLoader.getImageIcon("", "Preferences16" ) );
		menuItem.setMnemonic(KeyEvent.VK_P);
		menuItem.setActionCommand("MAIN_PREFERENCES");
		menuItem.addActionListener(new FrameActionListener(mainInterface));
		menu.add(menuItem);
		*/

		menuItem =
			new CMenuItem(
				frameController.getActionListener().generalOptionsAction);
		editMenu.add(menuItem);

		viewMenu =
			new JMenu(
				MailResourceLoader.getString("menu", "mainframe", "menu_view"));
		viewMenu.setMnemonic(KeyEvent.VK_V);
		viewMenu.setActionCommand("VIEW");
		add(viewMenu);

		subMenu =
			new CMenu(
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_view_show_hide"));

		JCheckBoxMenuItem cbMenuItem =
			new JCheckBoxMenuItem(
				frameController.globalActionCollection.viewToolbarAction);
		cbMenuItem.addActionListener(frameController.getActionListener());
		cbMenuItem.setActionCommand("VIEW_TOOLBAR");
		ViewItem viewItem = MailConfig
					.getMainFrameOptionsConfig()
					.getViewItem();
		if ( viewItem.getBoolean("toolbars","main") )
			cbMenuItem.setSelected(true);
		subMenu.add(cbMenuItem);

		cbMenuItem =
			new JCheckBoxMenuItem(
				frameController.globalActionCollection.viewFilterToolbarAction);
		cbMenuItem.addActionListener(frameController.getActionListener());
		cbMenuItem.setActionCommand("VIEW_FILTERTOOLBAR");
		if (viewItem.getBoolean("toolbars","filter"))
			cbMenuItem.setSelected(true);
		subMenu.add(cbMenuItem);

		cbMenuItem =
			new JCheckBoxMenuItem(
				frameController.globalActionCollection.viewFolderInfoAction);
		cbMenuItem.addActionListener(frameController.getActionListener());
		cbMenuItem.setActionCommand("VIEW_FOLDERINFO");
		if (viewItem.getBoolean("toolbars","folderinfo"))
			cbMenuItem.setSelected(true);
		subMenu.add(cbMenuItem);

		viewMenu.add(subMenu);

		viewMenu.addSeparator();

		/*
		    cbMenuItem = new JCheckBoxMenuItem( frameController.globalActionCollection.useAdvancedViewerAction );
		    //cbMenuItem.addActionListener( new FrameActionListener( mainInterface ) );
		    cbMenuItem.setActionCommand("USE_ADVANCEDVIEWER");
		    if ( MainInterface.mainFrameWindowItem.getAdvancedViewer()  ) cbMenuItem.setSelected( true );
		    menu.add( cbMenuItem );
		
		    menu.addSeparator();
		*/

		sortSubMenu =
			new CMenu(
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_view_sort"));
		updateSortMenu();
		viewMenu.add(sortSubMenu);

		subMenu = new CMenu("Messages Filter");

		group = new ButtonGroup();
		menuItem = new JRadioButtonMenuItem("Show All Messages");
		menuItem.setSelected(true);
		menuItem.setActionCommand("ALL");
		menuItem.addActionListener(
			frameController.tableController.getFilterActionListener());
		group.add(menuItem);
		subMenu.add(menuItem);
		menuItem = new JRadioButtonMenuItem("Show Unread Messages");
		group.add(menuItem);
		menuItem.setActionCommand("UNREAD");
		menuItem.addActionListener(
			frameController.tableController.getFilterActionListener());
		subMenu.add(menuItem);

		viewMenu.add(subMenu);

		viewMenu.addSeparator();

		cbMenuItem =
			new JCheckBoxMenuItem(
				frameController
					.tableController
					.getActionListener()
					.viewThreadedAction);
		cbMenuItem.setSelected(true);
		cbMenuItem.setSelected(false);

		viewMenu.add(cbMenuItem);

		viewMenu.addSeparator();

		subMenu =
			new CMenu(
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_view_next"));
		//subMenu.setIcon(ImageLoader.getSmallImageIcon("next-message.png"));
		subMenu.setMnemonic(KeyEvent.VK_N);

		menuItem =
			new CMenuItem(
				frameController.tableController.getActionListener().nextAction);
		menuItem.addMouseListener(handler);
		subMenu.add(menuItem);
		menuItem =
			new CMenuItem(
				frameController
					.tableController
					.getActionListener()
					.nextUnreadAction);
		menuItem.addMouseListener(handler);
		subMenu.add(menuItem);

		menuItem =
			new CMenuItem(
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_view_nextflaggedmessage"),
				KeyEvent.VK_M);
		menuItem.setEnabled(false);
		menuItem.setMnemonic(KeyEvent.VK_F);
		subMenu.add(menuItem);
		subMenu.addSeparator();
		menuItem =
			new CMenuItem(
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_view_nextunreadthread"),
				KeyEvent.VK_M);
		menuItem.setEnabled(false);
		menuItem.setAccelerator(KeyStroke.getKeyStroke("T"));
		menuItem.setMnemonic(KeyEvent.VK_T);
		subMenu.add(menuItem);

		viewMenu.add(subMenu);

		subMenu =
			new CMenu(
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_view_prev"));
		//subMenu.setIcon(ImageLoader.getSmallImageIcon("prev-message.png"));
		subMenu.setMnemonic(KeyEvent.VK_P);

		menuItem =
			new CMenuItem(
				frameController.tableController.getActionListener().prevAction);
		menuItem.addMouseListener(handler);
		subMenu.add(menuItem);
		menuItem =
			new CMenuItem(
				frameController
					.tableController
					.getActionListener()
					.prevUnreadAction);
		menuItem.addMouseListener(handler);
		subMenu.add(menuItem);

		menuItem =
			new CMenuItem(
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_view_prevflaggedmessage"),
				KeyEvent.VK_M);
		menuItem.setMnemonic(KeyEvent.VK_F);
		menuItem.setEnabled(false);
		subMenu.add(menuItem);
		subMenu.addSeparator();
		menuItem =
			new CMenuItem(
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_view_prevunreadthread"),
				KeyEvent.VK_M);
		menuItem.setMnemonic(KeyEvent.VK_T);
		menuItem.setEnabled(false);
		subMenu.add(menuItem);

		viewMenu.add(subMenu);
		viewMenu.addSeparator();

		viewMenu.add(MainInterface.charsetManager.createMenu(handler));

		viewMenu.addSeparator();

		menuItem =
			new CMenuItem(
				frameController
					.tableController
					.getActionListener()
					.viewSourceAction);
		menuItem.addMouseListener(handler);
		viewMenu.add(menuItem);

		folderMenu =
			new JMenu(
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_folder"));
		folderMenu.setMnemonic(KeyEvent.VK_F);
		folderMenu.setActionCommand("FOLDER");
		add(folderMenu);

		menuItem =
			new CMenuItem(
				frameController.treeController.getActionListener().addAction);
		menuItem.addMouseListener(handler);

		folderMenu.add(menuItem);
		menuItem =
			new CMenuItem(
				frameController
					.treeController
					.getActionListener()
					.addVirtualAction);
		menuItem.addMouseListener(handler);

		folderMenu.add(menuItem);
		menuItem =
			new CMenuItem(
				frameController
					.treeController
					.getActionListener()
					.renameAction);
		menuItem.addMouseListener(handler);

		folderMenu.add(menuItem);
		menuItem =
			new CMenuItem(
				frameController
					.treeController
					.getActionListener()
					.removeAction);
		menuItem.addMouseListener(handler);

		folderMenu.add(menuItem);

		folderMenu.addSeparator();

		menuItem =
			new CMenuItem(
				frameController
					.treeController
					.getActionListener()
					.expungeAction);
		menuItem.addMouseListener(handler);
		folderMenu.add(menuItem);
		menuItem =
			new CMenuItem(
				frameController.treeController.getActionListener().emptyAction);
		menuItem.addMouseListener(handler);
		folderMenu.add(menuItem);

		folderMenu.addSeparator();

		menuItem =
			new CMenuItem(
				frameController
					.treeController
					.getActionListener()
					.applyFilterAction);
		menuItem.addMouseListener(handler);
		folderMenu.add(menuItem);
		menuItem =
			new CMenuItem(
				frameController
					.treeController
					.getActionListener()
					.filterPreferencesAction);
		menuItem.addMouseListener(handler);
		folderMenu.add(menuItem);
		folderMenu.addSeparator();
		menuItem =
			new CMenuItem(
				frameController
					.treeController
					.getActionListener()
					.subscribeAction);
		menuItem.addMouseListener(handler);
		folderMenu.add(menuItem);

		messageMenu =
			new JMenu(
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_message"));
		messageMenu.setMnemonic(KeyEvent.VK_M);
		messageMenu.setActionCommand("MESSAGE");
		add(messageMenu);

		menuItem =
			new CMenuItem(
				frameController.globalActionCollection.newMessageAction);
		menuItem.addMouseListener(handler);
		messageMenu.add(menuItem);

		menuItem =
			new CMenuItem(
				frameController
					.tableController
					.getActionListener()
					.openMessageWithComposerAction);
		menuItem.addMouseListener(handler);
		messageMenu.add(menuItem);

		menuItem =
			new CMenuItem(
				frameController.tableController.getActionListener().saveAction);
		menuItem.addMouseListener(handler);
		messageMenu.add(menuItem);

		messageMenu.addSeparator();

		menuItem =
			new CMenuItem(
				frameController
					.tableController
					.getActionListener()
					.replyAction);
		menuItem.addMouseListener(handler);
		messageMenu.add(menuItem);

		menuItem =
			new CMenuItem(
				frameController
					.tableController
					.getActionListener()
					.replyToAllAction);
		menuItem.addMouseListener(handler);
		messageMenu.add(menuItem);

		menuItem =
			new CMenuItem(
				frameController
					.tableController
					.getActionListener()
					.replyToAction);
		menuItem.addMouseListener(handler);
		messageMenu.add(menuItem);

		menuItem =
			new CMenuItem(
				frameController
					.tableController
					.getActionListener()
					.replyAsAttachmentAction);
		menuItem.addMouseListener(handler);
		messageMenu.add(menuItem);

		menuItem =
			new CMenuItem(
				frameController
					.tableController
					.getActionListener()
					.forwardAction);
		menuItem.addMouseListener(handler);
		messageMenu.add(menuItem);

		menuItem =
			new CMenuItem(
				frameController
					.tableController
					.getActionListener()
					.forwardInlineAction);
		menuItem.addMouseListener(handler);
		messageMenu.add(menuItem);

		// for the bounce Action make a new Menu-entry
		// bounce meanse reply with an error-message
		menuItem =
			new CMenuItem(
				frameController
					.tableController
					.getActionListener()
					.bounceAction);
		menuItem.addMouseListener(handler);
		messageMenu.add(menuItem);

		messageMenu.addSeparator();

		menuItem =
			new CMenuItem(
				frameController
					.tableController
					.getActionListener()
					.moveMessageAction);
		menuItem.addMouseListener(handler);
		messageMenu.add(menuItem);

		menuItem =
			new CMenuItem(
				frameController
					.tableController
					.getActionListener()
					.copyMessageAction);
		menuItem.addMouseListener(handler);
		messageMenu.add(menuItem);

		menuItem =
			new CMenuItem(
				frameController
					.tableController
					.getActionListener()
					.deleteMessageAction);
		menuItem.addMouseListener(handler);
		messageMenu.add(menuItem);

		messageMenu.addSeparator();

		menuItem =
			new CMenuItem(
				frameController
					.tableController
					.getActionListener()
					.addSenderAction);
		menuItem.addMouseListener(handler);
		messageMenu.add(menuItem);

		menuItem =
			new CMenuItem(
				frameController
					.tableController
					.getActionListener()
					.addAllSendersAction);
		menuItem.addMouseListener(handler);
		messageMenu.add(menuItem);

		messageMenu.addSeparator();

		subMenu =
			new CMenu(
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_message_mark"));
		subMenu.setMnemonic(KeyEvent.VK_K);

		menuItem =
			new CMenuItem(
				frameController
					.tableController
					.getActionListener()
					.markAsReadAction);
		menuItem.addMouseListener(handler);
		subMenu.add(menuItem);
		menuItem =
			new CMenuItem(
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_message_markthreadasread"),
				KeyEvent.VK_T);
		menuItem.setEnabled(false);
		subMenu.add(menuItem);
		menuItem =
			new CMenuItem(
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_message_markallasread"),
				KeyEvent.VK_A);
		menuItem.setAccelerator(KeyStroke.getKeyStroke("A"));
		menuItem.setEnabled(false);
		subMenu.add(menuItem);
		subMenu.addSeparator();
		menuItem =
			new CMenuItem(
				frameController
					.tableController
					.getActionListener()
					.markAsFlaggedAction);
		menuItem.addMouseListener(handler);
		subMenu.add(menuItem);
		menuItem =
			new CMenuItem(
				frameController
					.tableController
					.getActionListener()
					.markAsExpungedAction);
		menuItem.addMouseListener(handler);
		subMenu.add(menuItem);

		messageMenu.add(subMenu);

		//menu.addSeparator();

		messageMenu.add(subMenu);

		utilitiesMenu =
			new JMenu(
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_utilities"));
		utilitiesMenu.setMnemonic('U');
		utilitiesMenu.setActionCommand("UTILITIES");
		add(utilitiesMenu);

		/*
		subMenu =
			new JMenu(GlobalResourceLoader.getString("menu","mainframe", "menu_message_filteronmessage"));
		menuItem =
			new CMenuItem(
				MainInterface.headerTableViewer.getActionListener().filterSubjectAction);
		menuItem.addMouseListener(handler);
		subMenu.add(menuItem);
		menuItem =
			new CMenuItem(
				MainInterface.headerTableViewer.getActionListener().filterFromAction);
		menuItem.addMouseListener(handler);
		subMenu.add(menuItem);
		menuItem =
			new CMenuItem(
				MainInterface.headerTableViewer.getActionListener().filterToAction);
		menuItem.addMouseListener(handler);
		subMenu.add(menuItem);
		
		menu.add(subMenu);
		
		subMenu =
			new JMenu(GlobalResourceLoader.getString("menu","mainframe", "menu_message_vfolderonmessage"));
		menuItem =
			new CMenuItem(
				MainInterface.headerTableViewer.getActionListener().vFolderSubjectAction);
		menuItem.addMouseListener(handler);
		subMenu.add(menuItem);
		menuItem =
			new CMenuItem(
				MainInterface.headerTableViewer.getActionListener().vFolderFromAction);
		menuItem.addMouseListener(handler);
		subMenu.add(menuItem);
		menuItem =
			new CMenuItem(
				MainInterface.headerTableViewer.getActionListener().vFolderToAction);
		menuItem.addMouseListener(handler);
		subMenu.add(menuItem);
		
		menu.add(subMenu);
		
		menu.addSeparator();
		*/

		menuItem =
			new CMenuItem(
				frameController.globalActionCollection.addressbookAction);
		menuItem.addMouseListener(handler);
		utilitiesMenu.add(menuItem);

		utilitiesMenu.addSeparator();

		menuItem =
			new CMenuItem(
				frameController
					.messageController
					.getActionListener()
					.dictAction);
		menuItem.addMouseListener(handler);
		utilitiesMenu.add(menuItem);

		utilitiesMenu.addSeparator();

		menuItem = new CMenuItem("Forget PGP Passphrase");
		menuItem.setEnabled(false);
		utilitiesMenu.add(menuItem);

		utilitiesMenu.addSeparator();

		menuItem = new CMenuItem("Import Mailbox...");
		menuItem.setIcon(ImageLoader.getImageIcon("stock_convert-16.png"));
		menuItem.setActionCommand("IMPORT");
		menuItem.addActionListener(frameController.getActionListener());
		menuItem.setEnabled(true);
		utilitiesMenu.add(menuItem);

		/*
		menu = new JMenu(GlobalResourceLoader.getString("menu","mainframe", "menu_preferences"));
		menu.setMnemonic('P');
		add(menu);
		*/

		//menu.addSeparator();

		//menu.addSeparator();

		//menu.addSeparator();

		helpMenu =
			new JMenu(
				MailResourceLoader.getString("menu", "mainframe", "menu_help"));
		helpMenu.setMnemonic('H');
		helpMenu.setActionCommand("HELP");
		add(helpMenu);

		menuItem =
			new CMenuItem(
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_help_help"));
		menuItem.setEnabled(false);
		menuItem.addActionListener(frameController.getActionListener());
		helpMenu.add(menuItem);
		menuItem =
			new CMenuItem(
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_help_homepage"),
				KeyEvent.VK_P);
		menuItem.setActionCommand("HOMEPAGE");
		menuItem.addActionListener(frameController.getActionListener());
		menuItem.setEnabled(true);
		helpMenu.add(menuItem);
		menuItem =
			new CMenuItem(
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_help_faq"),
				KeyEvent.VK_P);
		menuItem.setEnabled(true);
		menuItem.addActionListener(frameController.getActionListener());
		menuItem.setActionCommand("FAQ");
		helpMenu.add(menuItem);
		menuItem =
			new CMenuItem(
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_help_bug"),
				KeyEvent.VK_P);
		menuItem.setEnabled(true);
		menuItem.addActionListener(frameController.getActionListener());
		menuItem.setActionCommand("BUGREPORT");
		helpMenu.add(menuItem);
		menuItem =
			new CMenuItem(
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_help_license"),
				KeyEvent.VK_P);
		menuItem.setEnabled(true);
		menuItem.addActionListener(frameController.getActionListener());
		menuItem.setActionCommand("LICENSE");
		helpMenu.add(menuItem);

		menuItem =
			new CMenuItem(
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_help_sourceforge"),
				KeyEvent.VK_P);
		menuItem.setEnabled(true);
		menuItem.addActionListener(frameController.getActionListener());
		menuItem.setActionCommand("SOURCEFORGE");
		helpMenu.add(menuItem);

		helpMenu.addSeparator();

		menuItem =
			new CMenuItem(
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_help_about"),
				ImageLoader.getSmallImageIcon("stock_about-16.png"));
		menuItem.setActionCommand("ABOUT");
		menuItem.setEnabled(true);
		menuItem.addActionListener(frameController.getActionListener());
		helpMenu.add(menuItem);

	}

	public void addMenuEntry(String id, BasicAction action) {
		/*
		CMenuItem menuItem = new CMenuItem( action );
		menuItem.addMouseListener(handler);
		
		for ( int i=0; i<getMenuCount(); i++ )
		{
			JMenu menu = (JMenu) getComponent(i);
		
			if ( menu.getActionCommand().equalsIgnoreCase(id) )
			{
				// found the right menu
				
				menu.add(menuItem);
			}	
		}
		*/
	}

	public void addMenuSeparator(String id) {
		/*	
		
		for ( int i=0; i<getMenuCount(); i++ )
		{
			JMenu menu = (JMenu) getComponent(i);
		
			if ( menu.getActionCommand().equalsIgnoreCase(id) )
			{
				// found the right menu
				
				menu.addSeparator();
			}	
		}
		*/
	}

	public void updateSortMenu() {
		//FIXME
		/*
		HeaderTableItem v =
			MailConfig.getMainFrameOptionsConfig().getHeaderTableItem();
		
		sortSubMenu.removeAll();
		
		ButtonGroup group = new ButtonGroup();
		JRadioButtonMenuItem menuItem;
		String c;
		
		for (int i = 0; i < v.count(); i++) {
			c = (String) v.getName(i);
		
			boolean enabled = v.getEnabled(i);
		
			if (enabled == true) {
				String str = null;
				try {
					str =
						MailResourceLoader.getString("header", c.toLowerCase());
				} catch (Exception ex) {
					//ex.printStackTrace();
					System.out.println("exeption: " + ex.getMessage());
					str = c;
				}
		
				menuItem = new JRadioButtonMenuItem(str);
				menuItem.setActionCommand(c);
				menuItem.addActionListener(
					MainInterface
						.headerTableViewer
						.getHeaderItemActionListener());
				if (c
					.equals(
						MainInterface
							.headerTableViewer
							.getTableModelSorter()
							.getSortingColumn()))
					menuItem.setSelected(true);
		
				//menuItem.addActionListener( new FrameActionListener( mainInterface ));
		
				sortSubMenu.add(menuItem);
				group.add(menuItem);
			}
		
		}
		
		menuItem = new JRadioButtonMenuItem("In Order Received");
		menuItem.addActionListener(
			MainInterface.headerTableViewer.getHeaderItemActionListener());
		sortSubMenu.add(menuItem);
		group.add(menuItem);
		
		sortSubMenu.addSeparator();
		
		group = new ButtonGroup();
		
		menuItem = new JRadioButtonMenuItem("Ascending");
		menuItem.addActionListener(
			MainInterface.headerTableViewer.getHeaderItemActionListener());
		if (MainInterface
			.headerTableViewer
			.getTableModelSorter()
			.getSortingOrder()
			== true)
			menuItem.setSelected(true);
		
		sortSubMenu.add(menuItem);
		group.add(menuItem);
		menuItem = new JRadioButtonMenuItem("Descending");
		menuItem.addActionListener(
			MainInterface.headerTableViewer.getHeaderItemActionListener());
		if (MainInterface
			.headerTableViewer
			.getTableModelSorter()
			.getSortingOrder()
			== false)
			menuItem.setSelected(true);
		sortSubMenu.add(menuItem);
		group.add(menuItem);
		*/
	}

}