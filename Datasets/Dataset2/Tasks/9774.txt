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
import org.columba.core.gui.action.AbstractColumbaAction;
import org.columba.mail.gui.composer.ComposerController;
import org.columba.mail.gui.util.MailImageLoader;
import org.columba.mail.util.MailResourceLoader;


/**
 * Start interactive spell-checking of composed message.
 *
 * @author fdietz
 */
public class SpellcheckAction extends AbstractColumbaAction {
    public SpellcheckAction(IFrameMediator frameMediator) {
        super(frameMediator,
            MailResourceLoader.getString("menu", "composer",
                "menu_message_spellCheck"));

        // tooltip text
        putValue(SHORT_DESCRIPTION,
            MailResourceLoader.getString("menu", "composer",
                "menu_message_spellCheck_tooltip").replaceAll("&", ""));

        // large icon for toolbar
        putValue(LARGE_ICON, MailImageLoader.getIcon("spellcheck.png"));

        // small icon for menu
        putValue(SMALL_ICON, MailImageLoader.getSmallIcon("spellcheck.png"));

        // disable text in toolbar
        setShowToolBarText(false);

        //shortcut key
        putValue(ACCELERATOR_KEY,
            KeyStroke.getKeyStroke(KeyEvent.VK_L,
                ActionEvent.CTRL_MASK | ActionEvent.SHIFT_MASK));
    }

    /* (non-Javadoc)
     * @see java.awt.event.ActionListener#actionPerformed(java.awt.event.ActionEvent)
     */
    public void actionPerformed(ActionEvent evt) {
        ComposerController composerController = (ComposerController) getFrameMediator();

        //String checked =
        //	composerController.getComposerSpellCheck().checkText(
        //		composerController.getEditorController().getView().getText());
        String checked = composerController.getComposerSpellCheck().checkText(composerController.getEditorController()
                                                                                                .getViewText());

        //composerController.getEditorController().getView().setText(checked);
        composerController.getEditorController().setViewText(checked);
    }
}