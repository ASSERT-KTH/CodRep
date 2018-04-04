"menu_file_checkmessage"),"menu_file_checkmessage");

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

package org.columba.mail.mailchecking;

import java.util.Observable;
import java.util.Observer;

import org.columba.core.action.AbstractColumbaAction;
import org.columba.core.action.IMenu;
import org.columba.core.gui.frame.FrameMediator;
import org.columba.mail.util.MailResourceLoader;

/**
 * Provides a menu item for each mail account enabling users to fetch new
 * messages.
 */
public class FetchMessageSubMenu extends IMenu implements Observer {
    //private POP3ServerCollection popServer;

    public FetchMessageSubMenu(FrameMediator controller) {
        super(controller,
            MailResourceLoader.getString("menu", "mainframe",
                "menu_file_checkmessage"));

        createMenu();

        // register interest on account changes
        MailCheckingManager.getInstance().addObserver(this);
    }

    protected void createMenu() {
        // remove all items
        removeAll();

        MailCheckingManager mailCheckingManager = MailCheckingManager.getInstance();
        AbstractColumbaAction[] actions = mailCheckingManager.getActions();

        for (int i = 0; i < actions.length; i++) {
            add(actions[i]);
        }
    }

    /**
 * Listening for account changes here.
 * 
 * @see java.util.Observer#update(java.util.Observable, java.lang.Object)
 */
    public void update(Observable observable, Object arg1) {
        // recreate menu
        createMenu();
    }
}