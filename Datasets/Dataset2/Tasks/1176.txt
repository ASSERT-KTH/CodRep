//public static PGPController pgpController;

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

package org.columba.mail.main;

import org.columba.mail.config.MailConfig;
import org.columba.mail.gui.tree.TreeModel;
import org.columba.mail.mailchecking.MailCheckingManager;
import org.columba.mail.pgp.PGPController;
import org.columba.mail.pop3.POP3ServerCollection;

/**
 * Main Interface keeping static instances of all objects
 * which need to be accessed by other subsystems.
 *
 * @author fdietz
 */
public class MailInterface {
    // POP3 servers 
    public static POP3ServerCollection popServerCollection;

    // mailfolder treemodel
    public static TreeModel treeModel;

    // PGP encryption package
    public static PGPController pgpController;
    
    // mailchecking manager
    public static MailCheckingManager mailCheckingManager;
    
    // mail configuration
    public static MailConfig config;
}