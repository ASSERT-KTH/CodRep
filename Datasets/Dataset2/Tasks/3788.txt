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
package org.columba.mail.gui.composer.action;

import java.awt.event.ActionEvent;
import java.awt.event.KeyEvent;

import javax.swing.KeyStroke;

import org.columba.api.gui.frame.IFrameMediator;
import org.columba.core.command.CommandProcessor;
import org.columba.core.gui.action.AbstractColumbaAction;
import org.columba.core.resourceloader.ImageLoader;
import org.columba.mail.command.ComposerCommandReference;
import org.columba.mail.folder.outbox.OutboxFolder;
import org.columba.mail.gui.composer.ComposerController;
import org.columba.mail.gui.tree.FolderTreeModel;
import org.columba.mail.gui.util.MailImageLoader;
import org.columba.mail.smtp.command.SendMessageCommand;
import org.columba.mail.util.MailResourceLoader;


/**
 * @author frd
 *
 * To change this generated comment go to
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
public class SendAction extends AbstractColumbaAction {
    public SendAction(IFrameMediator frameMediator) {
        super(frameMediator,
            MailResourceLoader.getString("menu", "composer", "menu_file_send"));

        // tooltip text
        putValue(SHORT_DESCRIPTION,
            MailResourceLoader.getString("menu", "composer",
                "menu_file_send_tooltip").replaceAll("&", ""));

        // toolbar text
        putValue(TOOLBAR_NAME,
            MailResourceLoader.getString("menu", "composer",
                "menu_file_send_toolbar"));

        // large icon for toolbar
        putValue(LARGE_ICON, MailImageLoader.getIcon("send.png"));
      

        // small icon for menu
        putValue(SMALL_ICON, MailImageLoader.getSmallIcon("send.png"));
       

        // shortcut key
        putValue(ACCELERATOR_KEY,
            KeyStroke.getKeyStroke(KeyEvent.VK_ENTER, ActionEvent.CTRL_MASK));
    }

    /* (non-Javadoc)
     * @see java.awt.event.ActionListener#actionPerformed(java.awt.event.ActionEvent)
     */
    public void actionPerformed(ActionEvent evt) {
        final ComposerController composerController = (ComposerController) getFrameMediator();

        if (composerController.checkState()) {
            return;
        }

        OutboxFolder outboxFolder = (OutboxFolder) FolderTreeModel.getInstance().getFolder(103);

        ComposerCommandReference r = new ComposerCommandReference(composerController, outboxFolder);

        SendMessageCommand c = new SendMessageCommand(r);

        CommandProcessor.getInstance().addOp(c);
    }
}