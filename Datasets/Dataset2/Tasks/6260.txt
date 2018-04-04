super("selection", "SelectionOptions", mediator);

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
package org.columba.mail.folderoptions;

import org.columba.core.config.DefaultItem;
import org.columba.core.main.MainInterface;
import org.columba.core.xml.XmlElement;

import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.folder.Folder;
import org.columba.mail.gui.frame.MailFrameMediator;
import org.columba.mail.gui.frame.TableViewOwner;
import org.columba.mail.gui.message.command.ViewMessageCommand;
import org.columba.mail.gui.table.TableController;
import org.columba.mail.gui.table.TableView;


/**
 * Handles selecting message after folder selection changes.
 * <p>
 * This implementation remembers the the selected message, and
 * tries to reselect it again.
 * As default fall back it selects the first or last message,
 * depending on the sorting order.
 *
 * @author fdietz, waffel
 */
public class SelectionOptionsPlugin extends AbstractFolderOptionsPlugin {
    
    /**
     * Constructor
     * @param mediator  mail frame mediator
     */
    public SelectionOptionsPlugin(MailFrameMediator mediator) {
        super("selection", mediator);
    }

    /**
     * @see org.columba.mail.folderoptions.AbstractFolderOptionsPlugin#saveOptionsToXml(org.columba.mail.folder.Folder)
     */
    public void saveOptionsToXml(Folder folder) {
        XmlElement parent = getConfigNode(folder);
        DefaultItem item = new DefaultItem(parent);

        TableController tableController = ((TableViewOwner) getMediator()).getTableController();
    }

    /**
     * @see org.columba.mail.folderoptions.AbstractFolderOptionsPlugin#loadOptionsFromXml(org.columba.mail.folder.Folder)
     */
    public void loadOptionsFromXml(Folder folder) {
        XmlElement parent = getConfigNode(folder);
        DefaultItem item = new DefaultItem(parent);

        TableController tableController = ((TableViewOwner) getMediator()).getTableController();

        TableView view = tableController.getView();

        // should we re-use the last remembered selection?
        boolean remember = item.getBoolean("remember_last_selection", true);

        // sorting order
        boolean ascending = tableController.getTableModelSorter()
                                           .getSortingOrder();

        // row count
        int row = view.getTree().getRowCount();

        // row count == 0 --> empty table
        if (row == 0) {
            return;
        }

        // clear current selection
        view.clearSelection();

        // if the last selection for the current folder is null, then we show the
        // first/last message in the table and scroll to it.
        if ((!remember) || (folder.getLastSelection() == null)) {
            // changing the selection to the first/last row based on ascending state
            Object uid = null;

            if (ascending) {
                uid = view.selectLastRow();
            } else {
                uid = view.selectFirstRow();
            }

            // no messages in this folder
            if (uid == null) {
                return;
            }

            FolderCommandReference[] refNew = new FolderCommandReference[1];
            refNew[0] = new FolderCommandReference(folder, new Object[] {uid});

            // view the message under the new node
            MainInterface.processor.addOp(new ViewMessageCommand(
                    getMediator(), refNew));
        } else {
            // if a lastSelection for this folder is set
            // getting the last selected uid
            Object[] lastSelUids = {folder.getLastSelection()};

            // no messages in this folder
            if (lastSelUids[0] == null) {
                return;
            }

            // this message doesn't exit in this folder anymore
            if (tableController.getHeaderTableModel().getMessageNode(lastSelUids[0]) == null) {
                Object uid = null;

                if (ascending) {
                    uid = view.selectLastRow();
                } else {
                    uid = view.selectFirstRow();
                }

                // no messages in this folder
                if (uid == null) {
                    return;
                }

                // link to the new uid
                lastSelUids[0] = uid;
            }

            // selecting the message
            tableController.setSelected(lastSelUids);

            int selRow = view.getSelectedRow();

            // scroll to the position of the selection
            view.scrollRectToVisible(view.getCellRect(selRow, 0, false));
            view.requestFocus();

            // create command reference
            FolderCommandReference[] refNew = new FolderCommandReference[1];
            refNew[0] = new FolderCommandReference(folder, lastSelUids);

            // view the message under the new node
            MainInterface.processor.addOp(new ViewMessageCommand(
                    getMediator(), refNew));
        }
    }

    /**
       * @see org.columba.mail.folderoptions.AbstractFolderOptionsPlugin#createDefaultElement()
       */
    public XmlElement createDefaultElement(boolean global) {
        XmlElement parent = super.createDefaultElement(global);
        parent.addAttribute("remember_last_selection", "true");

        return parent;
    }
}