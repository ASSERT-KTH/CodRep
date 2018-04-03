import org.columba.core.pluginhandler.ViewPluginHandler;

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
package org.columba.mail.gui.frame;

import org.columba.core.config.ViewItem;
//import org.columba.core.gui.frame.AbstractFrameView;
import org.columba.core.gui.view.AbstractView;
import org.columba.core.gui.util.DialogStore;

import org.columba.core.gui.util.NotifyDialog;
import org.columba.core.main.MainInterface;
import org.columba.core.plugin.PluginHandlerNotFoundException;
import org.columba.core.plugin.ViewPluginHandler;
import org.columba.core.xml.XmlElement;

import org.columba.mail.gui.attachment.AttachmentSelectionHandler;
import org.columba.mail.gui.composer.HeaderController;
import org.columba.mail.gui.infopanel.FolderInfoPanel;
import org.columba.mail.gui.table.FilterToolbar;
import org.columba.mail.gui.table.TableController;
import org.columba.mail.gui.table.action.DownAction;
import org.columba.mail.gui.table.action.UpAction;
import org.columba.mail.gui.table.selection.TableSelectionHandler;
import org.columba.mail.gui.tree.TreeController;
import org.columba.mail.gui.tree.action.ApplyFilterAction;
import org.columba.mail.gui.tree.action.RenameFolderAction;
import org.columba.mail.gui.tree.selection.TreeSelectionHandler;
import org.columba.mail.gui.view.AbstractMailView;
import org.columba.mail.main.MailInterface;

import java.awt.event.KeyEvent;

import javax.swing.JFrame;
import javax.swing.KeyStroke;


/**
 *
 *  Mail frame controller which contains a tree, table and a message
 *  viewer.
 *
 *  @author fdietz
 *
 */
public class ThreePaneMailFrameController extends AbstractMailFrameController
    implements TableViewOwner, TreeViewOwner {
    public TreeController treeController;
    public TableController tableController;
    public HeaderController headerController;
    public FilterToolbar filterToolbar;
    public FolderInfoPanel folderInfoPanel;
    protected AbstractMailView view;

    /**
 * @param viewItem
 */
    public ThreePaneMailFrameController(ViewItem viewItem) {
        super("ThreePaneMail", viewItem);

        TableUpdater.add(this);
    }

    protected void initActions() {
        // Register UP key so its easy to move through messages in the list
        tableController.getView().getInputMap().put(KeyStroke.getKeyStroke(
                KeyEvent.VK_UP, 0), "UP");

        UpAction upAction = new UpAction(this);
        tableController.getView().getActionMap().put("UP", upAction);

        // Register DOWN key so its easy to move through messages in the list
        tableController.getView().getInputMap().put(KeyStroke.getKeyStroke(
                KeyEvent.VK_DOWN, 0), "DOWN");

        DownAction downAction = new DownAction(this);
        tableController.getView().getActionMap().put("DOWN", downAction);

        RenameFolderAction renameFolderAction = new RenameFolderAction(this);

        // Register F2 hotkey for renaming folder when the message panel has focus
        tableController.getView().getActionMap().put("F2", renameFolderAction);
        tableController.getView().getInputMap().put(KeyStroke.getKeyStroke(
                KeyEvent.VK_F2, 0), "F2");

        // Register F2 hotkey for renaming folder when the folder tree itself has focus
        treeController.getView().getActionMap().put("F2", renameFolderAction);
        treeController.getView().getInputMap().put(KeyStroke.getKeyStroke(
                KeyEvent.VK_F2, 0), "F2");

        ApplyFilterAction applyFilterAction = new ApplyFilterAction(this);

        // Register ALT-A hotkey for apply filter on folder when the folder tree itself has focus
        treeController.getView().getActionMap().put("ALT_A", applyFilterAction);
        treeController.getView().getInputMap().put(KeyStroke.getKeyStroke(
                KeyEvent.VK_A, KeyEvent.ALT_DOWN_MASK), "ALT_A");
        tableController.getView().getActionMap().put("ALT_A", applyFilterAction);
        tableController.getView().getInputMap().put(KeyStroke.getKeyStroke(
                KeyEvent.VK_A, KeyEvent.ALT_DOWN_MASK), "ALT_A");

        //register the markasread timer as selection listener
        ((MailFrameMediator)tableController.getFrameController()).registerTableSelectionListener(tableController.getMarkAsReadTimer());
    }

    public AbstractView createView() {
        //MailFrameView view = new MailFrameView(this);
        // Load "plugin" view instead
        ViewPluginHandler handler = null;

        try {
            handler = (ViewPluginHandler) MainInterface.pluginManager.getHandler(
                    "org.columba.core.view");
        } catch (PluginHandlerNotFoundException ex) {
            NotifyDialog d = new NotifyDialog();
            d.showDialog(ex);
        }

        // get view using the plugin handler found above
        Object[] args = {this};

        try {
            view = (AbstractMailView) handler.getPlugin(
                getViewItem().getRoot().getAttribute("frame", id), args);
        } catch (Exception ex) {
            ex.printStackTrace();
        }

        view.setFolderInfoPanel(folderInfoPanel);

        view.init(treeController.getView(), tableController.getView(),
            filterToolbar, messageController.getView(), statusBar);

        return view;
    }

    protected void init() {
        super.init();

        treeController = new TreeController(this, MailInterface.treeModel);

        tableController = new TableController(this);

        folderInfoPanel = new FolderInfoPanel();

        //treeController.getTreeSelectionManager().addFolderSelectionListener(folderInfoPanel);
        filterToolbar = new FilterToolbar(tableController);

        new DialogStore((MailFrameView) view);

        // create selection handlers
        TableSelectionHandler tableHandler = new TableSelectionHandler(tableController.getView());
        getSelectionManager().addSelectionHandler(tableHandler);

        TreeSelectionHandler treeHandler = new TreeSelectionHandler(treeController.getView());
        getSelectionManager().addSelectionHandler(treeHandler);

        getSelectionManager().addSelectionHandler(new AttachmentSelectionHandler(
                attachmentController.getView()));

        /*
treeController.getTreeSelectionManager().registerSelectionListener(""
        tableController.getTableSelectionManager());
*/
        tableController.createPopupMenu();
        treeController.createPopupMenu();
        messageController.createPopupMenu();
        attachmentController.createPopupMenu();
    }

    /* (non-Javadoc)
 * @see org.columba.mail.gui.frame.AbstractMailFrameController#hasTable()
 */
    public boolean hasTable() {
        return true;
    }

    /* (non-Javadoc)
 * @see org.columba.mail.gui.frame.ViewHeaderListInterface#getTableController()
 */
    public TableController getTableController() {
        return tableController;
    }

    /* (non-Javadoc)
 * @see org.columba.mail.gui.frame.TreeOwner#getTreeController()
 */
    public TreeController getTreeController() {
        return treeController;
    }

}