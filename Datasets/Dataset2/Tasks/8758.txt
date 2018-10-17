int uid = folder.getConfiguration().getInteger("uid");

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
package org.columba.mail.gui.table.action;

import org.columba.core.action.AbstractColumbaAction;
import org.columba.core.gui.frame.FrameMediator;
import org.columba.core.gui.selection.SelectionChangedEvent;
import org.columba.core.gui.selection.SelectionListener;
import org.columba.core.gui.util.ImageLoader;
import org.columba.core.main.MainInterface;

import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.folder.MessageFolder;
import org.columba.mail.folder.RootFolder;
import org.columba.mail.folder.command.ExpungeFolderCommand;
import org.columba.mail.folder.command.MarkMessageCommand;
import org.columba.mail.folder.command.MoveMessageCommand;
import org.columba.mail.gui.frame.MailFrameMediator;
import org.columba.mail.gui.table.selection.TableSelectionChangedEvent;
import org.columba.mail.util.MailResourceLoader;

import java.awt.event.ActionEvent;
import java.awt.event.KeyEvent;

import javax.swing.KeyStroke;


/**
 * @author frd
 *
 * To change this generated comment go to
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
public class DeleteMessageAction extends AbstractColumbaAction
    implements SelectionListener {
    public DeleteMessageAction(FrameMediator frameMediator) {
        super(frameMediator,
            MailResourceLoader.getString("menu", "mainframe",
                "menu_message_delete"));

        // toolbar text
        putValue(TOOLBAR_NAME,
            MailResourceLoader.getString("menu", "mainframe",
                "menu_message_delete_toolbar"));

        // tooltip text
        putValue(SHORT_DESCRIPTION,
            MailResourceLoader.getString("menu", "mainframe",
                "menu_message_delete_tooltip").replaceAll("&", ""));

        // icon for menu
        putValue(SMALL_ICON,
            ImageLoader.getSmallImageIcon("stock_delete-16.png"));

        // icon for toolbar
        putValue(LARGE_ICON, ImageLoader.getImageIcon("stock_delete.png"));

        // shortcut key
        putValue(ACCELERATOR_KEY,
            KeyStroke.getKeyStroke(KeyEvent.VK_D, ActionEvent.ALT_MASK));

        // disable toolbar text
        setShowToolBarText(false);

        setEnabled(false);

        ((MailFrameMediator) frameMediator).registerTableSelectionListener(this);
    }

    /* (non-Javadoc)
     * @see java.awt.event.ActionListener#actionPerformed(java.awt.event.ActionEvent)
     */
    public void actionPerformed(ActionEvent evt) {
        FolderCommandReference[] r = ((MailFrameMediator) getFrameMediator()).getTableSelection();
        r[0].setMarkVariant(MarkMessageCommand.MARK_AS_EXPUNGED);

        MessageFolder folder = (MessageFolder) r[0].getFolder();
        int uid = folder.getFolderItem().getInteger("uid");
        MessageFolder trash = (MessageFolder) ((RootFolder) folder.getRootFolder()).getTrashFolder();

        //Folder trash = (MessageFolder) MainInterface.treeModel.getTrashFolder();
        // trash folder has uid==105
        if (uid == trash.getUid()) {
            // trash folder is selected
            //  -> delete message
            MainInterface.processor.addOp(new MarkMessageCommand(r));

            MainInterface.processor.addOp(new ExpungeFolderCommand(r));
        } else {
            // -> move messages to trash
            MessageFolder destFolder = trash;

            FolderCommandReference[] result = new FolderCommandReference[2];
            FolderCommandReference[] r1 = ((MailFrameMediator) getFrameMediator()).getTableSelection();
            FolderCommandReference r2 = new FolderCommandReference(destFolder);

            result[0] = r1[0];
            result[1] = r2;

            MoveMessageCommand c = new MoveMessageCommand(result);

            MainInterface.processor.addOp(c);
        }
    }

    /* (non-Javadoc)
         * @see org.columba.core.gui.util.SelectionListener#selectionChanged(org.columba.core.gui.util.SelectionChangedEvent)
         */
    public void selectionChanged(SelectionChangedEvent e) {
        setEnabled(((TableSelectionChangedEvent) e).getUids().length > 0);
    }
}