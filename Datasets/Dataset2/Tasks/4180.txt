new SearchFrame((AbstractMailFrameController) getFrameMediator(),

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
package org.columba.mail.gui.action;

import java.awt.event.ActionEvent;
import java.awt.event.KeyEvent;

import javax.swing.KeyStroke;

import org.columba.api.gui.frame.IFrameMediator;
import org.columba.core.gui.action.AbstractColumbaAction;
import org.columba.core.resourceloader.ImageLoader;
import org.columba.mail.folder.IMailbox;
import org.columba.mail.gui.config.search.SearchFrame;
import org.columba.mail.gui.frame.AbstractMailFrameController;
import org.columba.mail.gui.tree.FolderTreeModel;
import org.columba.mail.util.MailResourceLoader;


public class SearchMessageAction extends AbstractColumbaAction {
    public SearchMessageAction(IFrameMediator controller) {
        super(controller,
            MailResourceLoader.getString("menu", "mainframe",
                "menu_edit_searchmessages"));

        // tooltip text
        putValue(SHORT_DESCRIPTION,
            MailResourceLoader.getString("menu", "mainframe",
                "menu_edit_searchmessages").replaceAll("&", ""));

        // small icon for menu
        putValue(SMALL_ICON, ImageLoader.getSmallImageIcon("virtualfolder.png"));

        // large icon for toolbar
        putValue(LARGE_ICON, ImageLoader.getImageIcon("virtualfolder.png"));

        // shortcut key
        putValue(ACCELERATOR_KEY,
            KeyStroke.getKeyStroke(KeyEvent.VK_S, ActionEvent.CTRL_MASK));
    }

    /* (non-Javadoc)
     * @see java.awt.event.ActionListener#actionPerformed(java.awt.event.ActionEvent)
     */
    public void actionPerformed(ActionEvent evt) {
    	IMailbox searchFolder = (IMailbox) FolderTreeModel.getInstance().getFolder(106);

        SearchFrame frame = new SearchFrame((AbstractMailFrameController) getFrameMediator(),
                searchFolder);
    }
}