return !controller.getAccountItem().getPopItem()

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

import org.columba.core.main.MainInterface;

import org.columba.mail.command.POP3CommandReference;
import org.columba.mail.config.AccountItem;
import org.columba.mail.main.MailInterface;
import org.columba.mail.pop3.POP3Server;
import org.columba.mail.pop3.command.FetchNewMessagesCommand;


/**
 * POP3 mail-checking item.
 *
 * @author fdietz
 */
public class POP3MailCheckingAction extends AbstractMailCheckingAction {
    private int accountUid;

    /**
 * Constructor
 * 
 * @param item                account item
 */
    public POP3MailCheckingAction(AccountItem accountItem) {
        super(accountItem);

        // account ID
        accountUid = accountItem.getUid();
    }

    /**
 * @see org.columba.mail.mailchecking.AbstractMailCheckingAction#check()
 */
    public void check() {
        POP3Server controller = MailInterface.popServerCollection.uidGet(accountUid);
        
        setEnabled( false );
        
        POP3CommandReference[] r = new POP3CommandReference[1];
        r[0] = new POP3CommandReference(controller);

        FetchNewMessagesCommand c = new FetchNewMessagesCommand(this, r);

        MainInterface.processor.addOp(c);
    }
	/**
	 * @see org.columba.mail.mailchecking.AbstractMailCheckingAction#isCheckAll()
	 */
	public boolean isCheckAll() {
        POP3Server controller = MailInterface.popServerCollection.uidGet(accountUid);

        return controller.getAccountItem().getPopItem()
        .getBoolean("exclude_from_checkall",
                false);
	}
}