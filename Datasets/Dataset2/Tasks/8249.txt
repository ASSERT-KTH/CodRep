import org.columba.core.main.MainInterface;

// This program is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation; either version 2 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Library General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program; if not, write to the Free Software
// Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

package org.columba.mail.pop3;

import java.io.File;
import java.util.Enumeration;
import java.util.Vector;

import org.columba.core.command.WorkerStatusController;
import org.columba.core.config.Config;
import org.columba.core.logging.ColumbaLogger;
import org.columba.mail.config.AccountItem;
import org.columba.mail.config.PopItem;
import org.columba.mail.config.SpecialFoldersItem;
import org.columba.mail.folder.Folder;
import org.columba.mail.message.ColumbaHeader;
import org.columba.mail.message.HeaderList;
import org.columba.mail.message.Message;
import org.columba.mail.pop3.protocol.POP3Protocol;
import org.columba.main.MainInterface;

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

		file =
			new File(
				Config.pop3Directory,
				(new Integer(uid)).toString());

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
		System.out.println("inbox-string=" + inboxStr);

		int inboxInt = Integer.parseInt(inboxStr);

		Folder f = (Folder) MainInterface.treeModel.getFolder(inboxInt);
		System.out.println("f=" + f);

		return f;
	}

	public void logout() throws Exception {
		getStore().logout();
	}

	public void forceLogout() throws Exception {
		getStore().close();
	}

	public Vector getUIDList(int totalMessageCount, WorkerStatusController worker) throws Exception {
		return getStore().fetchUIDList(totalMessageCount, worker);
	}

	public Vector getMessageSizeList() throws Exception {
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

	protected boolean existsRemotely(Object uid, Vector uidList)
		throws Exception {
		for (int i = 0; i < uidList.size(); i++) {
			Object serverUID = uidList.get(i);

			//System.out.println("server message uid: " + serverUID);
			if (uid.equals(serverUID)) {
				//System.out.println("local uid exists remotely");
				return true;
			}
		}

		return false;
	}

	protected Vector synchronize(Vector newList) throws Exception {
		Vector result = new Vector();
		HeaderList headerList = headerCache.getHeaderList();

		for (Enumeration e = headerList.keys(); e.hasMoreElements();) {
			String str = (String) e.nextElement();

			if (existsRemotely(str, newList) == true) {
				// mail exists on server
				//  -> keep it
			} else {
				// mail doesn't exist on server
				//  -> remove it from local cache
				ColumbaLogger.log.debug("remove uid=" + str);
				headerList.remove(str);
			}
		}

		for (int i = 0; i < newList.size(); i++) {
			Object str = newList.get(i);

			if (existsLocally(str, headerList) == false) {
				// new message on server

				result.add(str);
				ColumbaLogger.log.debug("adding uid=" + str);
				//System.out.println("download:" + str);

			}
		}

		return result;
	}

	public void deleteMessages(int[] indexes) throws Exception {
		for (int i = 0; i < indexes.length; i++) {
			store.deleteMessage(indexes[i]);
		}
	}
	
	public int getMessageCount() throws Exception
	{
		return getStore().fetchMessageCount();
	}

	public Message getMessage(int index, Object uid, WorkerStatusController worker) throws Exception {
		Message message = getStore().fetchMessage(index, worker);

		ColumbaHeader header = (ColumbaHeader) message.getHeader();
		header.set("columba.pop3uid", uid);
		header.set("columba.flags.recent", Boolean.TRUE);

		headerCache.getHeaderList().add(header, uid);

		return message;
	}

	public String getFolderName() {
		return accountItem.getName();
	}

	/**
	 * Returns the store.
	 * @return POP3Store
	 */
	public POP3Store getStore() {
		return store;
	}

}