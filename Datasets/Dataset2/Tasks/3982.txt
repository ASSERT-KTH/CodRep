public AbstractMessageFolder createFolder(int folderId) {

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

package org.columba.mail.folder;

import org.columba.core.io.DiskIO;
import org.columba.core.xml.XmlIO;
import org.columba.mail.config.AccountItem;
import org.columba.mail.folder.imap.IMAPFolder;
import org.columba.mail.folder.imap.IMAPRootFolder;

public class IMAPTstFactory implements MailboxTstFactory {
	
	IMAPRootFolder cyrusRoot;
	IMAPFolder inbox;
	String namebase;
	
	public IMAPTstFactory() {
		XmlIO accountXml = new XmlIO(DiskIO.getResourceURL("org/columba/mail/folder/cyrusaccount.xml"));
		accountXml.load();
		
		AccountItem accountItem = new AccountItem(accountXml.getRoot().getElement("account"));
		
		
		cyrusRoot = new IMAPRootFolder( accountItem, FolderTstHelper.homeDirectory + "/folders/");

		try {
			inbox = new IMAPFolder("INBOX","IMAPFolder", FolderTstHelper.homeDirectory + "/folders/");
			cyrusRoot.add(inbox);
		} catch (Exception e) {
			e.printStackTrace();
		}
		
		// An individual 3 digit number
		namebase = Integer.toString((int)(System.currentTimeMillis() % 1000));
	}
	
	/**
	 * @see org.columba.mail.folder.MailboxTstFactory#createFolder(int)
	 */
	public MessageFolder createFolder(int folderId) {
		try {
			IMAPFolder folder = new IMAPFolder(namebase + Integer.toString(folderId),"IMAPFolder", FolderTstHelper.homeDirectory + "/folders/");
			inbox.addSubfolder( folder );
		/*
		((AbstractFolder)MailInterface.treeModel.getRoot()).add(cyrusRoot);
		((AbstractFolder) MailInterface.treeModel.getRoot())
        .getConfiguration().getRoot().addElement(
        		cyrusRoot.getConfiguration().getRoot());
		MailInterface.treeModel.nodeStructureChanged(cyrusRoot.getParent());
		*/
			return folder;
		} catch (Exception e) {
			e.printStackTrace();
		}
		return null;
	}
}