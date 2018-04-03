import org.columba.core.gui.frame.FrameController;

//The contents of this file are subject to the Mozilla Public License Version 1.1
//(the "License"); you may not use this file except in compliance with the 
//License. You may obtain a copy of the License at http://www.mozilla.org/MPL/
//
//Software distributed under the License is distributed on an "AS IS" basis,
//WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License 
//for the specific language governing rights and
//limitations under the License.
//
//The Original Code is "The Columba Project"
//
//The Initial Developers of the Original Code are Frederik Dietz and Timo Stich.
//Portions created by Frederik Dietz and Timo Stich are Copyright (C) 2003. 
//
//All Rights Reserved.
package org.columba.core.gui.menu;

import java.awt.event.MouseAdapter;

import javax.swing.JMenu;
import javax.swing.JMenuBar;

import org.columba.core.action.BasicAction;
import org.columba.core.gui.FrameController;
import org.columba.core.gui.util.CMenu;
import org.columba.core.gui.util.CMenuItem;
import org.columba.core.gui.util.NotifyDialog;
import org.columba.core.main.MainInterface;
import org.columba.core.plugin.PluginHandlerNotFoundException;
import org.columba.core.xml.XmlElement;

public class Menu extends JMenuBar {

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

	//XmlElement menuRoot;

	private FrameController frameController;

	protected MenuBarGenerator menuGenerator;

	public Menu(String xmlRoot, FrameController frameController) {
		super();

		this.frameController = frameController;

		menuGenerator =
			createMenuBarGeneratorInstance(xmlRoot, frameController);

		menuGenerator.createMenuBar(this);

		try {

			(
				(MenuPluginHandler) MainInterface.pluginManager.getHandler(
					"org.columba.core.menu")).insertPlugins(
				this);
		} catch (PluginHandlerNotFoundException ex) {
			NotifyDialog d = new NotifyDialog();
			d.showDialog(ex);
		}
	}

	public MenuBarGenerator createMenuBarGeneratorInstance(
		String xmlRoot,
		FrameController frameController) {
		if (menuGenerator == null) {
			menuGenerator = new MenuBarGenerator(frameController, xmlRoot);
		}

		return menuGenerator;
	}

	public void extendMenuFromFile(String path) {
		menuGenerator.extendMenuFromFile(path);
		menuGenerator.createMenuBar(this);
	}

	public void extendMenu(XmlElement menuExtension) {
		menuGenerator.extendMenu(menuExtension);
	}

	/*
	protected void initFromXML() {
		removeAll();
		ListIterator it = menuRoot.getElements().listIterator();
		while (it.hasNext()) {
			add(createMenu((XmlElement) it.next()));
		}
	}
	
	protected JMenu createMenu(XmlElement menuElement) {
		List childs = menuElement.getElements();
		ListIterator it = childs.listIterator();
	
		JMenu menu =
			new JMenu(
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					menuElement.getAttribute("name")));
	
		while (it.hasNext()) {
			XmlElement next = (XmlElement) it.next();
			String name = next.getName();
			if (name.equals("menuitem")) {
	
				if (next.getAttribute("action") != null) {
					try {
	
						menu.add(
							(
								(
									ActionPluginHandler) MainInterface
										.pluginManager
										.getHandler(
									"action")).getAction(
								next.getAttribute("action"),
								frameController));
					} catch (Exception e) {
						ColumbaLogger.log.error(e);
					}
				} else if (next.getAttribute("checkboxaction") != null) {
					try {
						CheckBoxAction action =
							(CheckBoxAction)
								(
									(
										ActionPluginHandler) MainInterface
											.pluginManager
											.getHandler(
										"action")).getAction(
								next.getAttribute("checkboxaction"),
								frameController);
						JCheckBoxMenuItem menuitem =
							new JCheckBoxMenuItem(action);
						menu.add(menuitem);
						action.setCheckBoxMenuItem(menuitem);
					} catch (Exception e) {
						ColumbaLogger.log.error(e);
					}
				} else if (next.getAttribute("imenu") != null) {
					try {
						menu.add(
							(
								(
									ActionPluginHandler) MainInterface
										.pluginManager
										.getHandler(
									"action")).getIMenu(
								next.getAttribute("imenu"),
								frameController));
					} catch (Exception e) {
						ColumbaLogger.log.error(e);
					}
				}
	
			} else if (name.equals("separator")) {
				menu.addSeparator();
			} else if (name.equals("menu")) {
				menu.add(createMenu(next));
			}
		}
	
		return menu;
	}
	
	public void extendMenuFromFile(String path) {
		XmlIO menuXml = new XmlIO();
		menuXml.setURL(DiskIO.getResourceURL(path));
		menuXml.load();
	
		ListIterator iterator =
			menuXml
				.getRoot()
				.getElement("menubar")
				.getElements()
				.listIterator();
		while (iterator.hasNext()) {
			extendMenu((XmlElement) iterator.next());
		}
	
		initFromXML();
	}
	
	public void extendMenu(XmlElement menuExtension) {
		XmlElement menu, extension;
		String menuName = menuExtension.getAttribute("name");
		String extensionName = menuExtension.getAttribute("extensionpoint");
		if (extensionName == null) {
			// new menu
			menuRoot.insertElement(
				(XmlElement) menuExtension.clone(),
				menuRoot.count() - 1);
			return;
		}
	
		ListIterator iterator = menuRoot.getElements().listIterator();
	
		int insertIndex = 0;
	
		while (iterator.hasNext()) {
			menu = ((XmlElement) iterator.next());
			if (menu.getAttribute("name").equals(menuName)) {
	
				iterator = menu.getElements().listIterator();
				while (iterator.hasNext()) {
					extension = ((XmlElement) iterator.next());
					if (extension.getName().equals("extensionpoint")) {
						if (extension
							.getAttribute("name")
							.equals(extensionName)) {
							int size = menuExtension.count();
							for (int i = 0; i < size; i++) {
								menu.insertElement(
									menuExtension.getElement(0),
									insertIndex + i);
							}
							return;
						}
					}
					insertIndex++;
				}
			}
		}
	
	}
	*/

	// create the menu
	private void init() {
		/*
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
		
		
		//fileMenu.add(new OpenNewWindow(frameController));
		
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
		ViewItem viewItem =
			MailConfig.getMainFrameOptionsConfig().getViewItem();
		if (viewItem.getBoolean("toolbars", "main"))
			cbMenuItem.setSelected(true);
		subMenu.add(cbMenuItem);
		
		cbMenuItem =
			new JCheckBoxMenuItem(
				frameController.globalActionCollection.viewFilterToolbarAction);
		cbMenuItem.addActionListener(frameController.getActionListener());
		cbMenuItem.setActionCommand("VIEW_FILTERTOOLBAR");
		if (viewItem.getBoolean("toolbars", "filter"))
			cbMenuItem.setSelected(true);
		subMenu.add(cbMenuItem);
		
		cbMenuItem =
			new JCheckBoxMenuItem(
				frameController.globalActionCollection.viewFolderInfoAction);
		cbMenuItem.addActionListener(frameController.getActionListener());
		cbMenuItem.setActionCommand("VIEW_FOLDERINFO");
		if (viewItem.getBoolean("toolbars", "folderinfo"))
			cbMenuItem.setSelected(true);
		subMenu.add(cbMenuItem);
		
		menuItem =
			new CMenuItem(frameController.getStatusBar().getCancelAction());
		
		viewMenu.add(menuItem);
		
		menuItem = new CMenuItem("Refresh");
		menuItem.setAccelerator(KeyStroke.getKeyStroke(KeyEvent.VK_F5, 0));
		menuItem.setIcon(ImageLoader.getSmallImageIcon("stock_refresh-16.png"));
		
		viewMenu.add(menuItem);
		
		viewMenu.addSeparator();
		
		viewMenu.add(subMenu);
		
		viewMenu.addSeparator();
		
		
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
			new CCheckBoxMenuItem(
				frameController
					.tableController
					.getActionListener()
					.viewThreadedAction);
		cbMenuItem.setSelected(true);
		
		
		
		viewMenu.add(cbMenuItem);
		
		viewMenu.addSeparator();
		
		subMenu =
			new CMenu(
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_view_next"));
		subMenu.setIcon(ImageLoader.getSmallImageIcon("stock_right-16.png"));
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
		subMenu.setIcon(ImageLoader.getSmallImageIcon("stock_left-16.png"));
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
		
		subMenu =
			new CMenu(
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_message_filteronmessage"));
		menuItem =
			new CMenuItem(
				frameController
					.tableController
					.getActionListener()
					.filterSubjectAction);
		menuItem.addMouseListener(handler);
		subMenu.add(menuItem);
		menuItem =
			new CMenuItem(
				frameController
					.tableController
					.getActionListener()
					.filterFromAction);
		menuItem.addMouseListener(handler);
		subMenu.add(menuItem);
		menuItem =
			new CMenuItem(
				frameController
					.tableController
					.getActionListener()
					.filterToAction);
		menuItem.addMouseListener(handler);
		subMenu.add(menuItem);
		
		utilitiesMenu.add(subMenu);
		
		subMenu =
			new CMenu(
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_message_vfolderonmessage"));
		menuItem =
			new CMenuItem(
				frameController
					.tableController
					.getActionListener()
					.vFolderSubjectAction);
		menuItem.addMouseListener(handler);
		subMenu.add(menuItem);
		menuItem =
			new CMenuItem(
				frameController
					.tableController
					.getActionListener()
					.vFolderFromAction);
		menuItem.addMouseListener(handler);
		subMenu.add(menuItem);
		menuItem =
			new CMenuItem(
				frameController
					.tableController
					.getActionListener()
					.vFolderToAction);
		menuItem.addMouseListener(handler);
		subMenu.add(menuItem);
		
		utilitiesMenu.add(subMenu);
		
		utilitiesMenu.addSeparator();
		
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
		menuItem.setEnabled(true);
		menuItem.setIcon(ImageLoader.getImageIcon("stock_help_16.png"));
		menuItem.addActionListener(frameController.getActionListener());
		helpMenu.add(menuItem);
		menuItem =
			new CMenuItem(
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_help_homepage"),
				KeyEvent.VK_P);
		menuItem.setIcon(ImageLoader.getImageIcon("stock_home_16.png"));
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
		*/
	}

	public void addMenuEntry(String id, BasicAction action) {

		CMenuItem menuItem = new CMenuItem(action);
		menuItem.addMouseListener(handler);

		JMenu menu = getMenu(id);
		menu.add(menuItem);

	}

	public JMenu getMenu(String id) {

		for (int i = 0; i < getMenuCount(); i++) {
			JMenu menu = (JMenu) getComponent(i);

			if (menu.getActionCommand().equalsIgnoreCase(id)) {
				// found the right menu

				return menu;
			}
		}

		return null;
	}

	public void addMenuSeparator(String id) {

		for (int i = 0; i < getMenuCount(); i++) {
			JMenu menu = (JMenu) getComponent(i);

			if (menu.getActionCommand().equalsIgnoreCase(id)) {
				// found the right menu

				menu.addSeparator();
			}
		}

	}

}