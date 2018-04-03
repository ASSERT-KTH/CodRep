SelectFolderDialog dialog = new SelectFolderDialog(getFrameMediator());

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
import org.columba.mail.folder.command.MoveMessageCommand;
import org.columba.mail.gui.frame.MailFrameMediator;
import org.columba.mail.gui.table.selection.TableSelectionChangedEvent;
import org.columba.mail.gui.tree.util.SelectFolderDialog;
import org.columba.mail.main.MailInterface;
import org.columba.mail.util.MailResourceLoader;

import java.awt.event.ActionEvent;


/**
 * @author frd
 *
 * To change this generated comment go to
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
public class MoveMessageAction extends AbstractColumbaAction
    implements SelectionListener {
    public MoveMessageAction(FrameMediator frameMediator) {
        super(frameMediator,
            MailResourceLoader.getString("menu", "mainframe",
                "menu_message_move"));

        // toolbar text
        putValue(TOOLBAR_NAME,
            MailResourceLoader.getString("menu", "mainframe",
                "menu_message_move_toolbar"));

        // tooltip text
        putValue(SHORT_DESCRIPTION,
            MailResourceLoader.getString("menu", "mainframe",
                "menu_message_move_tooltip").replaceAll("&", ""));

        // icons
        putValue(SMALL_ICON,
            ImageLoader.getSmallImageIcon("movemessage_small.png"));
        putValue(LARGE_ICON, ImageLoader.getImageIcon("move-message.png"));

        // disable toolbar text
        setShowToolBarText(false);

        setEnabled(false);

        ((MailFrameMediator) frameMediator).registerTableSelectionListener(this);
    }

    /* (non-Javadoc)
     * @see java.awt.event.ActionListener#actionPerformed(java.awt.event.ActionEvent)
     */
    public void actionPerformed(ActionEvent evt) {
        SelectFolderDialog dialog = MailInterface.treeModel.getSelectFolderDialog();

        if (dialog.success()) {
            MessageFolder destFolder = dialog.getSelectedFolder();

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