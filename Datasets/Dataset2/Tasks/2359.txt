new SubscribeDialog( getFrameMediator().getView().getFrame(), rootFolder);

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

import org.columba.core.action.AbstractColumbaAction;
import org.columba.core.gui.frame.FrameMediator;
import org.columba.core.gui.selection.SelectionChangedEvent;
import org.columba.core.gui.selection.SelectionListener;
import org.columba.core.gui.util.ImageLoader;

import org.columba.mail.folder.AbstractFolder;
import org.columba.mail.folder.imap.IMAPFolder;
import org.columba.mail.folder.imap.IMAPRootFolder;
import org.columba.mail.gui.config.subscribe.SubscribeDialog;
import org.columba.mail.gui.frame.MailFrameMediator;
import org.columba.mail.gui.tree.selection.TreeSelectionChangedEvent;
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
public class SubscribeFolderAction extends AbstractColumbaAction
    implements SelectionListener {
    private IMAPRootFolder rootFolder;

    public SubscribeFolderAction(FrameMediator frameMediator) {
        super(frameMediator,
            MailResourceLoader.getString("menu", "mainframe",
                "menu_folder_subscribe"));

        // tooltip text
        putValue(SHORT_DESCRIPTION,
            MailResourceLoader.getString("menu", "mainframe",
                "menu_folder_subscribe").replaceAll("&", ""));

        // icons
        putValue(SMALL_ICON, ImageLoader.getSmallImageIcon("remotehost.png"));
        putValue(LARGE_ICON, ImageLoader.getImageIcon("remotehost.png"));

        // shortcut key
        putValue(ACCELERATOR_KEY,
            KeyStroke.getKeyStroke(KeyEvent.VK_S, ActionEvent.ALT_MASK));

        setEnabled(false);

        ((MailFrameMediator) frameMediator).registerTreeSelectionListener(this);
    }

    /* (non-Javadoc)
 * @see java.awt.event.ActionListener#actionPerformed(java.awt.event.ActionEvent)
 */
    public void actionPerformed(ActionEvent evt) {
        new SubscribeDialog(rootFolder);
    }

    /* (non-Javadoc)
 * @see org.columba.core.gui.util.SelectionListener#selectionChanged(org.columba.core.gui.util.SelectionChangedEvent)
 */
    public void selectionChanged(SelectionChangedEvent e) {
        if (((TreeSelectionChangedEvent) e).getSelected().length > 0) {
            AbstractFolder selected = ((TreeSelectionChangedEvent) e).getSelected()[0];

            if (selected instanceof IMAPFolder) {
                rootFolder = (IMAPRootFolder) ((IMAPFolder) selected).getRootFolder();
                setEnabled(true);
            } else if (selected instanceof IMAPRootFolder) {
                rootFolder = (IMAPRootFolder) selected;
                setEnabled(true);
            } else {
                setEnabled(false);
            }
        } else {
            setEnabled(false);
        }
    }
}