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
import java.util.logging.Logger;

import org.columba.core.gui.action.AbstractSelectableAction;
import org.columba.mail.config.AccountItem;
import org.columba.mail.config.SecurityItem;
import org.columba.mail.gui.composer.ComposerController;
import org.columba.mail.gui.composer.ComposerModel;
import org.columba.mail.gui.util.MailImageLoader;
import org.columba.mail.util.MailResourceLoader;


/**
 * @author frd
 *
 * To change this generated comment go to
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
public class EncryptMessageAction extends AbstractSelectableAction {

    /** JDK 1.4+ logging framework logger, used for logging. */
    private static final Logger LOG = Logger.getLogger("org.columba.mail.gui.composer.action");

    public EncryptMessageAction(ComposerController composerController) {
        super(composerController,
            MailResourceLoader.getString("menu", "composer",
                "menu_message_encrypt"));

        // tooltip text
        putValue(SHORT_DESCRIPTION,
            MailResourceLoader.getString("menu", "composer",
                "menu_message_encrypt").replaceAll("&", ""));

        // small icon for menu
        putValue(SMALL_ICON, MailImageLoader.getSmallIcon("lock.png"));
        
        ComposerModel model = composerController.getModel();
        AccountItem account = model.getAccountItem();
        SecurityItem pgp = account.getPGPItem();
   
        setState(pgp.getBooleanWithDefault("always_encrypt", false));
        
        //setEnabled(false);
    }

    /* (non-Javadoc)
     * @see java.awt.event.ActionListener#actionPerformed(java.awt.event.ActionEvent)
     */
    public void actionPerformed(ActionEvent evt) {
        LOG.info("start encryption...");

        ComposerModel model = (ComposerModel) ((ComposerController) getFrameMediator()).getModel();
        model.setEncryptMessage(getState());
    }
}