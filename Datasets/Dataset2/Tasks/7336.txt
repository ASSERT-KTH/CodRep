FolderCommandReference r = ((MailFrameMediator) getFrameMediator()).getTableSelection();

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

import java.awt.event.ActionEvent;

import javax.swing.KeyStroke;

import org.columba.core.action.AbstractColumbaAction;
import org.columba.core.gui.frame.FrameMediator;
import org.columba.core.gui.selection.SelectionChangedEvent;
import org.columba.core.gui.selection.SelectionListener;
import org.columba.core.gui.util.ImageLoader;
import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.gui.frame.MailFrameMediator;
import org.columba.mail.gui.table.selection.TableSelectionChangedEvent;
import org.columba.mail.util.MailResourceLoader;


/**
 * @author frd
 *
 * To change this generated comment go to
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
public class PreviousMessageAction extends AbstractColumbaAction
    implements SelectionListener {
    public PreviousMessageAction(FrameMediator frameMediator) {
        super(frameMediator,
            MailResourceLoader.getString("menu", "mainframe",
                "menu_view_prevmessage"));

        // tooltip text
        putValue(SHORT_DESCRIPTION,
            MailResourceLoader.getString("menu", "mainframe",
                "menu_view_prevmessage_tooltip").replaceAll("&", ""));

        // icons
        putValue(LARGE_ICON,
            ImageLoader.getSmallImageIcon("previous-message.png"));

        // shortcut key
        putValue(ACCELERATOR_KEY, KeyStroke.getKeyStroke("B"));

        // disable toolbar text
        setShowToolBarText(false);

        setEnabled(false);

        // uncomment to enable action

        /*
        ((MailFrameMediator) frameMediator).registerTableSelectionListener(this);
        */
    }

    /* (non-Javadoc)
     * @see java.awt.event.ActionListener#actionPerformed(java.awt.event.ActionEvent)
     */
    public void actionPerformed(ActionEvent evt) {
        FolderCommandReference[] r = ((MailFrameMediator) getFrameMediator()).getTableSelection();

        //		TODO: fix previous-message action

        /*
        if ( r.length>0 )
        {
                FolderCommandReference ref = r[0];
                TableController table = ((TableViewOwner) getFrameController()).getTableController();
                MessageNode node = table.getView().getSelectedNode();
                MessageNode previousNode = (MessageNode) node.getPreviousNode();
                Object nextUid = previousNode.getUid();

                Object[] uids = new Object[1];
                uids[0] = nextUid;
                ref.setUids(uids);

                ((MailFrameMediator) getFrameController()).setTableSelection(r);
                table.setSelected(uids);

                MainInterface.processor.addOp(new ViewMessageCommand(getFrameController(), r));
        }
        */
    }

    /* (non-Javadoc)
     * @see org.columba.core.gui.util.SelectionListener#selectionChanged(org.columba.core.gui.util.SelectionChangedEvent)
     */
    public void selectionChanged(SelectionChangedEvent e) {
        setEnabled(((TableSelectionChangedEvent) e).getUids().length > 0);
    }
}