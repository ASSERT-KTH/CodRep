import org.columba.core.gui.action.CRadioButtonMenuItem;

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
package org.columba.mail.gui.tree.action;

import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

import javax.swing.ButtonGroup;
import javax.swing.JPopupMenu;
import javax.swing.JRadioButtonMenuItem;

import org.columba.api.gui.frame.IFrameMediator;
import org.columba.core.config.DefaultItem;
import org.columba.core.config.IDefaultItem;
import org.columba.core.gui.base.CRadioButtonMenuItem;
import org.columba.core.xml.XmlElement;
import org.columba.mail.config.MailConfig;
import org.columba.mail.gui.frame.TreeViewOwner;
import org.columba.mail.gui.tree.TreeController;
import org.columba.mail.gui.tree.comparator.FolderComparator;
import org.columba.mail.gui.tree.comparator.UnreadFolderComparator;
import org.columba.mail.util.MailResourceLoader;

/**
 * Menu items for sorting the folder tree.
 * @author redsolo
 */
public class SortFoldersMenu extends JPopupMenu implements ActionListener {

    private static final String UNSORTED_ACTION = "UNSORTED";
    private static final String ALPHABETIC_ACTION = "ALPHABETIC";
    private static final String UNREAD_ACTION = "UNREAD";
    private static final String DESC_ACTION = "DESC";
    private static final String ASC_ACTION = "ASC";

    private ButtonGroup sortGroup;
    private ButtonGroup orderGroup;

    private JRadioButtonMenuItem unsortedMenuItem;
    private JRadioButtonMenuItem unreadMenuItem;
    private JRadioButtonMenuItem alphaMenuItem;

    private JRadioButtonMenuItem ascendingMenuItem;
    private JRadioButtonMenuItem descendingMenuItem;

    private String activeComparator;

    private IFrameMediator frameMediator;
    
    /**
     * Creates the sort folders submenu.
     * @param controller the controller.
     */
    public SortFoldersMenu(IFrameMediator controller) {
    	this.frameMediator = controller;
        //super(controller, MailResourceLoader.getString("menu", "mainframe", "menu_view_sort_tree"),"menu_view_sort_tree");

        createSubMenu();
        loadConfig();
    }

    /**
     * Creates the sub menu.
     */
    private void createSubMenu() {
        removeAll();

        sortGroup = new ButtonGroup();

        unsortedMenuItem = addRadioButtonItem(sortGroup, "menu_view_sort_tree_unsorted", UNSORTED_ACTION);
        alphaMenuItem = addRadioButtonItem(sortGroup, "menu_view_sort_tree_alpha", ALPHABETIC_ACTION);
        unreadMenuItem = addRadioButtonItem(sortGroup, "menu_view_sort_tree_unread", UNREAD_ACTION);

        addSeparator();

        orderGroup = new ButtonGroup();
        ascendingMenuItem = addRadioButtonItem(orderGroup, "menu_view_sort_asc", ASC_ACTION);
        descendingMenuItem = addRadioButtonItem(orderGroup, "menu_view_sort_desc", DESC_ACTION);
    }

    /**
     * Loads the configuration.
     */
    private void loadConfig() {
        XmlElement element = MailConfig.getInstance().get("options").getElement("/options/gui/tree/sorting");

        FolderComparator comparator = null;
        if (element != null) {
            IDefaultItem item = new DefaultItem(element);
            boolean ascending = item.getBooleanWithDefault("ascending", true);
            activeComparator = 
                item.getRoot().getAttribute("comparator", "").toUpperCase();

            if (activeComparator.equals(ALPHABETIC_ACTION)) {
                comparator = new FolderComparator(ascending);
                alphaMenuItem.setSelected(true);
            } else if (activeComparator.equals(UNREAD_ACTION)) {
                comparator = new UnreadFolderComparator(ascending);
                unreadMenuItem.setSelected(true);
            } else {
                unsortedMenuItem.setSelected(true);
                ascendingMenuItem.setEnabled(false);
                descendingMenuItem.setEnabled(false);
            }

            if (ascending) {
                ascendingMenuItem.setSelected(true);
            } else {
                descendingMenuItem.setSelected(true);
            }
        } else {
            comparator = new FolderComparator(true);
            alphaMenuItem.setSelected(true);
            ascendingMenuItem.setSelected(true);
        }

        if (comparator != null) {
            TreeViewOwner mediator = (TreeViewOwner) frameMediator;
            ((TreeController)mediator.getTreeController()).getView().setFolderComparator(comparator);
            ((TreeController)mediator.getTreeController()).getView().setSortingEnabled(true);
        }
    }

    /**
     * Saves the config.
     */
    private void saveConfig() {
        XmlElement treeElement = MailConfig.getInstance().get("options").getElement("/options/gui/tree");
        if (treeElement == null) {
            treeElement = MailConfig.getInstance().get("options").getElement("/options/gui").addSubElement("tree");
        }

        XmlElement element = treeElement.getElement("sorting");
        if (element == null) {
            element = treeElement.addSubElement("sorting");
        }

        IDefaultItem item = new DefaultItem(element);
        item.setBoolean("ascending", ascendingMenuItem.isSelected());
        item.setString("comparator", activeComparator.toLowerCase());
        item.setBoolean("sorted", !activeComparator.equals(UNSORTED_ACTION));
        element.notifyObservers();
    }

    /**
     * Adds a new JRadioButtonMenuItem to the menu and group.
     * @param group the button group.
     * @param i18nName the i18n name in the mainframe properties file.
     * @param actionCommand the action command string for the action.
     * @return the newly created menu item.
     */
    private JRadioButtonMenuItem addRadioButtonItem(ButtonGroup group, String i18nName, String actionCommand) {
        String i18n = MailResourceLoader.getString("menu", "mainframe", i18nName);
        CRadioButtonMenuItem headerMenuItem = new CRadioButtonMenuItem(i18n);
        headerMenuItem.setActionCommand(actionCommand);
        headerMenuItem.addActionListener(this);
        group.add(headerMenuItem);
        add(headerMenuItem);
        return headerMenuItem;
    }

    /**
     * Menu actions.
     * @param e the action event.
     */
    public void actionPerformed(ActionEvent e) {
        String action = e.getActionCommand();

        TreeViewOwner mediator = (TreeViewOwner) frameMediator;

        if (action.equals(UNSORTED_ACTION)) {

            activeComparator = UNSORTED_ACTION;
            ascendingMenuItem.setEnabled(false);
            descendingMenuItem.setEnabled(false);
            ((TreeController)mediator.getTreeController()).getView().setSortingEnabled(false);
        } else {

            ascendingMenuItem.setEnabled(true);
            descendingMenuItem.setEnabled(true);
            ((TreeController)mediator.getTreeController()).getView().setSortingEnabled(true);
            if (action.equals(ASC_ACTION)) {
            	((TreeController)mediator.getTreeController()).getView().sortAscending(true);
            } else if (action.equals(DESC_ACTION)) {
            	((TreeController)mediator.getTreeController()).getView().sortAscending(false);
            } else {
                activeComparator = action;
                if (action.equals(UNREAD_ACTION)) {
                	((TreeController)mediator.getTreeController()).getView().setFolderComparator(new UnreadFolderComparator(ascendingMenuItem.isSelected()));
                } else if (action.equals(ALPHABETIC_ACTION)) {
                	((TreeController)mediator.getTreeController()).getView().setFolderComparator(new FolderComparator(ascendingMenuItem.isSelected()));
                }
            }
        }
        saveConfig();
    }
}