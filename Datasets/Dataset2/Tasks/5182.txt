ColumbaLogger.log.fine("playing sound file=" + file);

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
package org.columba.mail.pop3.command;

import org.columba.core.command.Command;
import org.columba.core.command.CommandCancelledException;
import org.columba.core.command.DefaultCommandReference;
import org.columba.core.command.StatusObservableImpl;
import org.columba.core.command.Worker;

import org.columba.mail.command.POP3CommandReference;
import org.columba.mail.pop3.POP3Server;
import org.columba.mail.util.MailResourceLoader;

import java.awt.Toolkit;

import java.io.IOException;

import java.util.List;

import javax.swing.JOptionPane;


public class CheckForNewMessagesCommand extends Command {
    POP3Server server;

    public CheckForNewMessagesCommand(DefaultCommandReference[] references) {
        super(references);
    }

    /**
     * @see org.columba.core.command.Command#execute(Worker)
     */
    public void execute(Worker worker) throws Exception {
        FetchNewMessagesCommand command = new FetchNewMessagesCommand(getReferences());

        POP3CommandReference[] r = (POP3CommandReference[]) getReferences(FIRST_EXECUTION);

        server = r[0].getServer();

        //		register interest on status bar information
        ((StatusObservableImpl) server.getObservable()).setWorker(worker);

        command.log(MailResourceLoader.getString("statusbar", "message",
                "authenticating"));

        try {
            int totalMessageCount = server.getMessageCount();

            List newMessagesUIDList = command.synchronize();

            int newMessagesCount = newMessagesUIDList.size();

            if ((newMessagesCount > 0) &&
                    (server.getAccountItem().getPopItem().getBoolean("enable_sound"))) {
                playSound();
            }

            if (server.getAccountItem().getPopItem().getBoolean("automatically_download_new_messages")) {
                command.downloadNewMessages(newMessagesUIDList, worker);
            }

            command.logout();
        } catch (CommandCancelledException e) {
            server.forceLogout();
        } catch (IOException e) {
            String name = e.getClass().getName();
            JOptionPane.showMessageDialog(null, e.getLocalizedMessage(),
                name.substring(name.lastIndexOf(".")), JOptionPane.ERROR_MESSAGE);
        } finally {
            // always enable the menuitem again 
            r[0].getPOP3ServerController().enableActions(true);
        }
    }

    protected void playSound() {
        // re-enable this feature later, make it a general option
        // not a per-account based one
        // -> playing wav-files should be only optional
        // just play a system beep 
        // -> this works better for most people
        // -> java doesn't support sound servers like 
        // -> alsa or esound anyway
        Toolkit kit = Toolkit.getDefaultToolkit();
        kit.beep(); //system beep

        /*
        AccountItem item = server.getAccountItem();
        PopItem popItem = item.getPopItem();
        String file = popItem.get("sound_file");

        ColumbaLogger.log.info("playing sound file=" + file);

        if (file.equalsIgnoreCase("default")) {
                PlaySound.play("newmail.wav");
        } else {
                try {
                        PlaySound.play(new URL("file:+" + file));
                } catch (Exception ex) {
                        ex.printStackTrace();
                }
        }
        */
    }
}