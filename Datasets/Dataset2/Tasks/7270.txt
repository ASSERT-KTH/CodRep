ColumbaLogger.log.fine("not yet implemented");

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
package org.columba.mail.pop3;

import org.columba.core.action.AbstractColumbaAction;
import org.columba.core.logging.ColumbaLogger;
import org.columba.core.main.MainInterface;

import org.columba.mail.command.POP3CommandReference;
import org.columba.mail.config.AccountItem;
import org.columba.mail.config.PopItem;
import org.columba.mail.pop3.command.CheckForNewMessagesCommand;
import org.columba.mail.pop3.command.FetchNewMessagesCommand;

import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

import javax.swing.Timer;


/**
 * @author freddy
 *
 * To change this generated comment edit the template variable "typecomment":
 * Window>Preferences>Java>Templates.
 * To enable and disable the creation of type comments go to
 * Window>Preferences>Java>Code Generation.
 */
public class POP3ServerController implements ActionListener {
    private final static int ONE_SECOND = 1000;
    protected POP3Server server;
    private boolean hide;
    public AbstractColumbaAction checkAction;
    private AbstractColumbaAction manageAction;
    private Timer timer;
    private int uid;

    /**
     * Constructor for POP3ServerController.
     */
    public POP3ServerController(AccountItem accountItem) {
        server = new POP3Server(accountItem);

        hide = true;

        uid = accountItem.getUid();
        checkAction = new AbstractColumbaAction(null,
                accountItem.getName() + " (" +
                accountItem.getIdentityItem().get("address") + ")") {
                    public void actionPerformed(ActionEvent e) {
                        fetch();
                    }
                };

        manageAction = new AbstractColumbaAction(null,
                accountItem.getName() + " (" +
                accountItem.getIdentityItem().get("address") + ")") {
                    public void actionPerformed(ActionEvent e) {
                        ColumbaLogger.log.info("not yet implemented");
                    }
                };
        manageAction.setEnabled(false);

        restartTimer();
    }

    public POP3Server getServer() {
        return server;
    }

    public AccountItem getAccountItem() {
        return getServer().getAccountItem();
    }

    public void restartTimer() {
        PopItem item = getAccountItem().getPopItem();

        if (item.getBoolean("enable_mailcheck")) {
            int interval = item.getInteger("mailcheck_interval");

            timer = new Timer(ONE_SECOND * interval * 60, this);
            timer.restart();
        } else {
            if (timer != null) {
                timer.stop();
                timer = null;
            }
        }
    }

    public void updateAction() {
        checkAction.putValue(AbstractColumbaAction.NAME,
            getAccountItem().getName() + " (" +
            getAccountItem().getIdentityItem().get("address") + ")");
        manageAction.putValue(AbstractColumbaAction.NAME,
            getAccountItem().getName() + " (" +
            getAccountItem().getIdentityItem().get("address") + ")");
        uid = getAccountItem().getUid();
    }

    public AbstractColumbaAction getCheckAction() {
        return checkAction;
    }

    public AbstractColumbaAction getManageAction() {
        return manageAction;
    }

    public void enableActions(boolean b) {
        getCheckAction().setEnabled(b);
        getManageAction().setEnabled(b);
    }

    public void setHide(boolean b) {
        hide = b;
    }

    public boolean getHide() {
        return hide;
    }

    public void fetch() {
        enableActions(false);

        POP3CommandReference[] r = new POP3CommandReference[1];
        r[0] = new POP3CommandReference(this);

        FetchNewMessagesCommand c = new FetchNewMessagesCommand(r);

        MainInterface.processor.addOp(c);
    }

    public void check() {
        enableActions(false);

        POP3CommandReference[] r = new POP3CommandReference[1];
        r[0] = new POP3CommandReference(this);

        CheckForNewMessagesCommand c = new CheckForNewMessagesCommand(r);

        MainInterface.processor.addOp(c);
    }

    public void actionPerformed(ActionEvent e) {
        Object src = e.getSource();

        if (src.equals(timer)) {
            if ((checkAction.isEnabled() == true) &&
                    (manageAction.isEnabled() == true)) {
                check();
            } else {
                timer.restart();
            }

            return;
        }

        String action = e.getActionCommand();
    }

    public int getUid() {
        return uid;
    }
}