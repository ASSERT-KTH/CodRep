ColumbaLogger.log.info(

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
package org.columba.mail.gui.table.action;

import org.columba.core.action.AbstractColumbaAction;
import org.columba.core.gui.frame.FrameMediator;
import org.columba.core.logging.ColumbaLogger;
import org.columba.core.main.MainInterface;

import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.gui.message.command.ViewMessageCommand;

import java.awt.event.ActionEvent;


public class ViewMessageAction extends AbstractColumbaAction {
    protected Object oldUid;

    /**
     * @param controller
     */
    public ViewMessageAction(FrameMediator controller) {
        super(controller, "ViewMessageAction");
    }

    /* (non-Javadoc)
     * @see java.awt.event.ActionListener#actionPerformed(java.awt.event.ActionEvent)
     */
    public void actionPerformed(ActionEvent evt) {
        FolderCommandReference[] references = (FolderCommandReference[]) getFrameMediator()
                                                                             .getSelectionManager()
                                                                             .getSelection("mail.table");
        Object[] uids = references[0].getUids();

        if (uids.length == 1) {
            if (oldUid == uids[0]) {
                ColumbaLogger.log.debug(
                    "this message was already selected, don't fire any event");

                return;
            }

            oldUid = uids[0];

            MainInterface.processor.addOp(new ViewMessageCommand(
                    getFrameMediator(), references));
        }
    }
}