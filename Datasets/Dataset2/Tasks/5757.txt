import org.columba.api.plugin.IExtensionInterface;

// The contents of this file are subject to the Mozilla Public License Version
// 1.1
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
package org.columba.mail.spam;

import org.columba.core.plugin.IExtensionInterface;
import org.columba.mail.folder.IMailbox;

public interface ISpamPlugin extends IExtensionInterface{

	/**
	 * Score message. Check if message is spam or non spam.
	 * 
	 * @param mailbox
	 * @param uid
	 * @return
	 * @throws Exception TODO
	 */
	boolean scoreMessage(IMailbox mailbox, Object uid) throws Exception;
	
	/**
	 * Add this message to the token database as spam.
	 * 
	 * @param mailbox
	 * @param uid
	 * @throws Exception TODO
	 */
	void trainMessageAsSpam(IMailbox mailbox, Object uid) throws Exception;
	
	/**
	 * Add this message to the token database as ham.
	 * 
	 * @param mailbox
	 * @param uid
	 * @throws Exception TODO
	 */
	void trainMessageAsHam(IMailbox mailbox, Object uid) throws Exception;
	
	void save();
	
	void load();
}