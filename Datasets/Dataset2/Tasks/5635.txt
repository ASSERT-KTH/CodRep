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

import org.columba.core.gui.action.AbstractColumbaAction;
import org.columba.core.resourceloader.ImageLoader;
import org.columba.mail.gui.composer.ComposerController;
import org.columba.mail.gui.util.MailImageLoader;
import org.columba.mail.util.MailResourceLoader;


/**
 * Add attachment to message.
 *
 * @author fdietz
 */
public class AttachFileAction extends AbstractColumbaAction {
    public AttachFileAction(ComposerController composerController) {
        super(composerController,
            MailResourceLoader.getString("menu", "composer",
                "menu_message_attachFile"));

        // tooltip text
        putValue(SHORT_DESCRIPTION,
            MailResourceLoader.getString("menu", "composer",
                "menu_message_attachFile_tooltip").replaceAll("&", ""));

        // toolbar text
        putValue(TOOLBAR_NAME,
            MailResourceLoader.getString("menu", "composer",
                "menu_message_attachFile_toolbar"));

        // large icon for toolbar
        putValue(LARGE_ICON, MailImageLoader.getIcon("mail-attachment.png"));

        // small icon for menu
        putValue(SMALL_ICON, MailImageLoader.getIcon("mail-attachment.png"));

        //shortcut key
        putValue(ACCELERATOR_KEY,
            KeyStroke.getKeyStroke(KeyEvent.VK_A,
                ActionEvent.CTRL_MASK | ActionEvent.ALT_MASK));
    }

    /* (non-Javadoc)
     * @see java.awt.event.ActionListener#actionPerformed(java.awt.event.ActionEvent)
     */
    public void actionPerformed(ActionEvent evt) {
        ComposerController composerController = ((ComposerController) getFrameMediator());

        composerController.getAttachmentController().addFileAttachment();
    }
}