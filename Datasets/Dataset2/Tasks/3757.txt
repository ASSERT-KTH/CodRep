import org.columba.mail.resourceloader.MailImageLoader;

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
import java.awt.event.KeyEvent;

import javax.swing.KeyStroke;

import org.columba.api.gui.frame.IFrameMediator;
import org.columba.api.selection.ISelectionListener;
import org.columba.api.selection.SelectionChangedEvent;
import org.columba.core.command.CommandProcessor;
import org.columba.core.gui.action.AbstractColumbaAction;
import org.columba.mail.command.IMailFolderCommandReference;
import org.columba.mail.gui.composer.command.ReplyToAllCommand;
import org.columba.mail.gui.frame.MailFrameMediator;
import org.columba.mail.gui.table.selection.TableSelectionChangedEvent;
import org.columba.mail.gui.util.MailImageLoader;
import org.columba.mail.util.MailResourceLoader;


/**
 * @author frd
 *
 * To change this generated comment go to
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
public class ReplyToAllAction extends AbstractColumbaAction
    implements ISelectionListener {
    public ReplyToAllAction(IFrameMediator frameMediator) {
        super(frameMediator,
            MailResourceLoader.getString("menu", "mainframe",
                "menu_message_replytoall"));

        // tooltip text
        putValue(SHORT_DESCRIPTION,
            MailResourceLoader.getString("menu", "mainframe",
                "menu_message_replytoall_tooltip").replaceAll("&", ""));

        // icons
        putValue(SMALL_ICON,
        		MailImageLoader.getSmallIcon("mail-reply-all.png"));
        putValue(LARGE_ICON, MailImageLoader.getIcon("mail-reply-all.png"));

        // set toolbar text
        putValue(TOOLBAR_NAME,
            MailResourceLoader.getString("menu", "mainframe",
                "menu_message_replytoall"));

        putValue(ACCELERATOR_KEY, KeyStroke.getKeyStroke(KeyEvent.VK_R,
				ActionEvent.CTRL_MASK | ActionEvent.SHIFT_MASK));
        
        setEnabled(false);

        ((MailFrameMediator) frameMediator).registerTableSelectionListener(this);
    }

    /* (non-Javadoc)
     * @see java.awt.event.ActionListener#actionPerformed(java.awt.event.ActionEvent)
     */
    public void actionPerformed(ActionEvent evt) {
        IMailFolderCommandReference r = ((MailFrameMediator) getFrameMediator()).getTableSelection();
        CommandProcessor.getInstance().addOp(new ReplyToAllCommand(r));
    }

    /* (non-Javadoc)
     * @see org.columba.core.gui.util.ISelectionListener#selectionChanged(org.columba.core.gui.util.SelectionChangedEvent)
     */
    public void selectionChanged(SelectionChangedEvent e) {
        setEnabled(((TableSelectionChangedEvent) e).getUids().length > 0);
    }
}