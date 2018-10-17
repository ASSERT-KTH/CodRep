return !imapRootFolder.getAccountItem().getImapItem().getBoolean("exclude_from_checkall",

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

import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.config.AccountItem;
import org.columba.mail.folder.command.CheckForNewMessagesCommand;
import org.columba.mail.folder.imap.IMAPRootFolder;
import org.columba.mail.main.MailInterface;


/**
 * IMAP mail checking item.
 *
 * @author fdietz
 */
public class IMAPMailCheckingAction extends AbstractMailCheckingAction {
    private int accountUid;

    /**
 * Constructor
 * 
 * @param item                account item
 */
    public IMAPMailCheckingAction(AccountItem accountItem) {
        super(accountItem);

        // account ID
        accountUid = accountItem.getUid();
    }

    /**
 * @see org.columba.mail.mailchecking.AbstractMailCheckingAction#check()
 */
    public void check() {
    	setEnabled(false);
        IMAPRootFolder imapRootFolder = (IMAPRootFolder) MailInterface.treeModel.getImapFolder(accountUid);
        FolderCommandReference[] r = new FolderCommandReference[1];
        r[0] = new FolderCommandReference(imapRootFolder);

        MainInterface.processor.addOp(new CheckForNewMessagesCommand(this, r));
    }

    /**
	 * @see org.columba.mail.mailchecking.AbstractMailCheckingAction#isCheckAll()
	 */
	public boolean isCheckAll() {
        IMAPRootFolder imapRootFolder = (IMAPRootFolder) MailInterface.treeModel.getImapFolder(accountUid);
        return imapRootFolder.getAccountItem().getImapItem().getBoolean("exclude_from_checkall",
                false);
	}
}