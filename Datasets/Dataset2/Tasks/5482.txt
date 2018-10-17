//putValue(SMALL_ICON, ImageLoader.getSmallImageIcon("16_sign.png"));

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
//The Initial Developers of the Original Code are Frederik Dietz and Timo
// Stich.
//Portions created by Frederik Dietz and Timo Stich are Copyright (C) 2003.
//
//All Rights Reserved.
package org.columba.mail.gui.composer.action;

import java.awt.event.ActionEvent;
import java.awt.event.ItemEvent;
import java.awt.event.ItemListener;
import java.util.logging.Logger;

import org.columba.core.gui.action.AbstractSelectableAction;
import org.columba.core.resourceloader.ImageLoader;
import org.columba.mail.config.AccountItem;
import org.columba.mail.config.SecurityItem;
import org.columba.mail.gui.composer.AccountView;
import org.columba.mail.gui.composer.ComposerController;
import org.columba.mail.util.MailResourceLoader;

/**
 * @author frd
 * 
 * To change this generated comment go to Window>Preferences>Java>Code
 * Generation>Code and Comments
 */
public class SignMessageAction extends AbstractSelectableAction implements
        ItemListener {

    /** JDK 1.4+ logging framework logger, used for logging. */
    private static final Logger LOG = Logger
            .getLogger("org.columba.mail.gui.composer.action"); //$NON-NLS-1$

    private ComposerController composerController;

    public SignMessageAction(ComposerController composerController) {
        super(composerController, MailResourceLoader.getString("menu",
                "composer", "menu_message_sign"));
        this.composerController = composerController;

        // tooltip text
        putValue(SHORT_DESCRIPTION, MailResourceLoader.getString("menu",
                "composer", "menu_message_sign").replaceAll("&", ""));

        // small icon for menu
        putValue(SMALL_ICON, ImageLoader.getSmallImageIcon("16_sign.png"));

        composerController.getAccountController().getView().addItemListener(
                this);

        SecurityItem item = this.composerController.getModel().getAccountItem()
                .getPGPItem();
        setState(item.getBooleanWithDefault("always_sign", false));
        LOG.info("always_sign=" + item.get("always_sign")); //$NON-NLS-1$ //$NON-NLS-2$

        composerController.getModel().setSignMessage(getState());

        //setEnabled(false);
    }

    /*
     * (non-Javadoc)
     * 
     * @see java.awt.event.ActionListener#actionPerformed(java.awt.event.ActionEvent)
     */
    public void actionPerformed(ActionEvent evt) {
        LOG.info("start signing...");

        //ComposerModel model = (ComposerModel)
        // ((ComposerController)getFrameController()).getModel();
        composerController.getModel().setSignMessage(getState());
    }

    public void itemStateChanged(ItemEvent e) {
        if (e.getStateChange() == ItemEvent.SELECTED) {
            AccountItem item = (AccountItem) ((AccountView)e.getSource()).getSelectedItem();
            SecurityItem pgp = item.getPGPItem();
            setState(pgp.getBooleanWithDefault("always_sign", false));
        }
    }

}