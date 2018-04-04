public class SMTPCommandReference extends MailFolderCommandReference {

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
package org.columba.mail.command;

import org.columba.mail.folder.AbstractFolder;
import org.columba.mail.message.ColumbaMessage;


/**
 * @author freddy
 *
 * To change this generated comment edit the template variable "typecomment":
 * Window>Preferences>Java>Templates.
 * To enable and disable the creation of type comments go to
 * Window>Preferences>Java>Code Generation.
 */
public class SMTPCommandReference extends FolderCommandReference {
    /**
 * Constructor for SMTPCommandReference.
 * @param folder
 */
    public SMTPCommandReference(AbstractFolder folder) {
        super(folder);
    }

    /**
 * Constructor for SMTPCommandReference.
 * @param folder
 * @param message
 */
    public SMTPCommandReference(AbstractFolder folder, ColumbaMessage message) {
        super(folder, message);
    }

    /**
 * Constructor for SMTPCommandReference.
 * @param folder
 * @param uids
 */
    public SMTPCommandReference(AbstractFolder folder, Object[] uids) {
        super(folder, uids);
    }

    /**
 * Constructor for SMTPCommandReference.
 * @param folder
 * @param uids
 * @param address
 */
    public SMTPCommandReference(AbstractFolder folder, Object[] uids,
        Integer[] address) {
        super(folder, uids, address);
    }
}