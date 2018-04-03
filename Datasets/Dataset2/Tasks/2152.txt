import org.columba.core.pluginhandler.ViewPluginHandler;

// The contents of this file are subject to the Mozilla Public License Version
// 1.1
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
//The Initial Developers of the Original Code are Frederik Dietz and Timo
// Stich.
//Portions created by Frederik Dietz and Timo Stich are Copyright (C) 2003.
//
//All Rights Reserved.
package org.columba.mail.gui.messageframe;

import org.columba.core.config.ViewItem;
import org.columba.core.gui.util.NotifyDialog;
import org.columba.core.gui.view.AbstractView;
import org.columba.core.main.MainInterface;
import org.columba.core.plugin.PluginHandlerNotFoundException;
import org.columba.core.plugin.ViewPluginHandler;
import org.columba.core.xml.XmlElement;

import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.folder.MessageFolder;
import org.columba.mail.gui.attachment.AttachmentSelectionHandler;
import org.columba.mail.gui.frame.AbstractMailFrameController;
import org.columba.mail.gui.message.command.ViewMessageCommand;
import org.columba.mail.gui.view.AbstractMessageFrameView;
import org.columba.mail.main.MailInterface;


/**
 *
 *  Mail frame controller which contains a message viewer only.
 *
 *  @author fdietz
 *
 */
public class MessageFrameController extends AbstractMailFrameController {
    FolderCommandReference[] treeReference;
    FolderCommandReference[] tableReference;
    FixedTableSelectionHandler tableSelectionHandler;
    protected AbstractMessageFrameView view;

    /**
     * @param viewItem
     */
    public MessageFrameController() {
        super("MessageFrame",
            new ViewItem(MailInterface.config.get("options").getElement("/options/gui/messageframe/view")));

        getView().loadPositions();

        if(getView().getFrame() != null) {
            getView().getFrame().setVisible(true);
        }
    }

    protected void init() {
        super.init();

        tableSelectionHandler = new FixedTableSelectionHandler(tableReference);
        getSelectionManager().addSelectionHandler(tableSelectionHandler);

        getSelectionManager().addSelectionHandler(new AttachmentSelectionHandler(
                attachmentController.getView()));
    }

    public void selectInbox() {
        MessageFolder inboxFolder = (MessageFolder) MailInterface.treeModel.getFolder(101);

        try {
            Object[] uids = inboxFolder.getUids();

            if (uids.length > 0) {
                Object uid = uids[0];

                Object[] newUids = new Object[1];
                newUids[0] = uid;

                FolderCommandReference[] r = new FolderCommandReference[1];
                r[0] = new FolderCommandReference(inboxFolder, newUids);

                // set tree and table references
                treeReference = new FolderCommandReference[1];
                treeReference[0] = new FolderCommandReference(inboxFolder);

                tableReference = new FolderCommandReference[1];
                tableReference[0] = new FolderCommandReference(inboxFolder,
                        newUids);

                // FIXME
                /*
                getSelectionManager().getHandler("mail.table").setSelection(r);
                */
                MainInterface.processor.addOp(new ViewMessageCommand(this, r));
            }
        } catch (Exception ex) {
            ex.printStackTrace();
        }
    }

    /* (non-Javadoc)
     * @see org.columba.core.gui.frame.FrameMediator#createView()
     */
    public AbstractView createView() {
        //MessageFrameView view = new MessageFrameView(this);
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
            view = (AbstractMessageFrameView) handler.getPlugin(
                getViewItem().getRoot().getAttribute("frame", id), args);
        } catch (Exception ex) {
            ex.printStackTrace();
        }

        /*
        view.setFolderInfoPanel(folderInfoPanel);
        */
        view.init(messageController.getView(), statusBar);

        view.getFrame().pack();

        view.getFrame().setVisible(true);

        return view;
    }

    /* *20030831, karlpeder* Using method on super class instead
    public void close() {
            view.saveWindowPosition();
            view.setVisible(false);
    }
    */
    /* *20030831, karlpeder* Not used, close method is used instead
    public void saveAndClose() {

            super.saveAndClose();
    }
    */
    /* (non-Javadoc)
     * @see org.columba.core.gui.frame.FrameMediator#initInternActions()
     */
    protected void initInternActions() {
    }

    /* (non-Javadoc)
     * @see org.columba.mail.gui.frame.MailFrameInterface#getTableSelection()
     */
    public FolderCommandReference[] getTableSelection() {
        return tableReference;
    }

    /* (non-Javadoc)
     * @see org.columba.mail.gui.frame.MailFrameInterface#getTreeSelection()
     */
    public FolderCommandReference[] getTreeSelection() {
        return treeReference;
    }

    /**
     * @param references
     */
    public void setTreeSelection(FolderCommandReference[] references) {
        treeReference = references;
    }

    /**
     * @param references
     */
    public void setTableSelection(FolderCommandReference[] references) {
        tableReference = references;

        tableSelectionHandler.setSelection(tableReference);
    }

    /* (non-Javadoc)
     * @see org.columba.mail.gui.frame.AbstractMailFrameController#hasTable()
     */
    public boolean hasTable() {
        return false;
    }
}