ColumbaHeader header = (ColumbaHeader) message.getHeader();

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
package org.columba.mail.pop3;

import java.io.File;
import java.util.ArrayList;
import java.util.Enumeration;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;

import org.columba.core.command.StatusObservable;
import org.columba.core.config.Config;
import org.columba.core.main.MainInterface;
import org.columba.core.util.ListTools;
import org.columba.mail.config.AccountItem;
import org.columba.mail.config.PopItem;
import org.columba.mail.config.SpecialFoldersItem;
import org.columba.mail.folder.Folder;
import org.columba.mail.main.MailInterface;
import org.columba.mail.message.ColumbaMessage;
import org.columba.mail.message.ColumbaHeader;
import org.columba.mail.message.HeaderList;
import org.columba.ristretto.pop3.protocol.POP3Protocol;

public class POP3Server {

	private AccountItem accountItem;

	private File file;

	public POP3Protocol pop3Connection;

	private boolean alreadyLoaded;

	private POP3Store store;

	protected POP3HeaderCache headerCache;

	public POP3Server(AccountItem accountItem) {
		this.accountItem = accountItem;

		int uid = accountItem.getUid();

		file = new File(Config.pop3Directory, (new Integer(uid)).toString());

		PopItem item = accountItem.getPopItem();

		store = new POP3Store(item);

		headerCache = new POP3HeaderCache(this);

	}

	public void save() throws Exception {
		headerCache.save();
	}

	public File getConfigFile() {
		return file;
	}

	public AccountItem getAccountItem() {
		return accountItem;
	}

	public Folder getFolder() {
		SpecialFoldersItem foldersItem = accountItem.getSpecialFoldersItem();
		String inboxStr = foldersItem.get("inbox");

		int inboxInt = Integer.parseInt(inboxStr);

		Folder f = (Folder) MailInterface.treeModel.getFolder(inboxInt);

		return f;
	}

	public void logout() throws Exception {
		getStore().logout();
	}

	public void forceLogout() throws Exception {
		getStore().close();
	}

	public List getUIDList(int totalMessageCount) throws Exception {
		return getStore().fetchUIDList(totalMessageCount);
	}

	public List getMessageSizeList() throws Exception {
		return getStore().fetchMessageSizeList();
	}

	protected boolean existsLocally(Object uid, HeaderList list)
		throws Exception {

		for (Enumeration e = headerCache.getHeaderList().keys();
			e.hasMoreElements();
			) {
			Object localUID = e.nextElement();

			//System.out.println("local message uid: " + localUID);
			if (uid.equals(localUID)) {
				//System.out.println("remote uid exists locally");
				return true;
			}
		}

		return false;
	}

	protected boolean existsRemotely(Object uid, List uidList)
		throws Exception {
		for (Iterator it = uidList.iterator(); it.hasNext();) {
			Object serverUID = it.next();
			// for (int i = 0; i < uidList.size(); i++) {
			// Object serverUID = uidList.get(i);

			//System.out.println("server message uid: " + serverUID);
			if (uid.equals(serverUID)) {
				//System.out.println("local uid exists remotely");
				return true;
			}
		}

		return false;
	}

	public List synchronize(List newList) throws Exception {

		LinkedList headerUids = new LinkedList();
		Enumeration keys = headerCache.getHeaderList().keys();
		while (keys.hasMoreElements()) {
			headerUids.add(keys.nextElement());
		}
		LinkedList newUids = new LinkedList(newList);

		ListTools.substract(newUids, headerUids);

		ListTools.substract(headerUids, new ArrayList(newList));
		Iterator it = headerUids.iterator();
		while (it.hasNext()) {
			headerCache.getHeaderList().remove(it.next());
		}

		return newUids;

	}

	public void deleteMessages(int[] indexes) throws Exception {
		for (int i = 0; i < indexes.length; i++) {
			store.deleteMessage(indexes[i]);
		}
	}

	public void deleteMessage(int index) throws Exception {
		store.deleteMessage(index);
	}

	public int getMessageCount() throws Exception {
		return getStore().fetchMessageCount();
	}

	public ColumbaMessage getMessage(int index, Object uid) throws Exception {

		ColumbaMessage message = getStore().fetchMessage(index);

		if (message == null)
			return null;

		ColumbaHeader header = (ColumbaHeader) message.getHeaderInterface();
		header.set("columba.pop3uid", uid);
		header.set("columba.flags.recent", Boolean.TRUE);

		// set the attachment flag
		String contentType = (String) header.get("Content-Type");

		if (contentType != null) {
			if (contentType.indexOf("multipart") != -1)
				header.set("columba.attachment", Boolean.TRUE);
			else
				header.set("columba.attachment", Boolean.FALSE);
		}

		headerCache.getHeaderList().add(header, uid);

		return message;
	}

	public String getFolderName() {
		return accountItem.getName();
	}

	/**
	 * Returns the store.
	 * 
	 * @return POP3Store
	 */
	public POP3Store getStore() {
		return store;
	}

	public StatusObservable getObservable() {
		return store.getObservable();
	}

}