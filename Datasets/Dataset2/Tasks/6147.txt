return (ColumbaHeader) headerList.getHeader(uid);

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
//
//$Log: IMAPFolder.java,v $
//
package org.columba.mail.folder.imap;

import java.io.InputStream;
import java.util.ArrayList;
import java.util.Enumeration;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;

import org.columba.core.command.StatusObservable;
import org.columba.core.command.WorkerStatusController;
import org.columba.core.io.StreamUtils;
import org.columba.core.logging.ColumbaLogger;
import org.columba.core.util.ListTools;
import org.columba.core.xml.XmlElement;
import org.columba.mail.config.FolderItem;
import org.columba.mail.config.ImapItem;
import org.columba.mail.filter.Filter;
import org.columba.mail.folder.Folder;
import org.columba.mail.folder.FolderTreeNode;
import org.columba.mail.folder.RemoteFolder;
import org.columba.mail.folder.command.MarkMessageCommand;
import org.columba.mail.folder.headercache.RemoteHeaderCache;
import org.columba.mail.imap.IMAPStore;
import org.columba.mail.message.ColumbaHeader;
import org.columba.mail.message.ColumbaMessage;
import org.columba.mail.message.HeaderList;
import org.columba.mail.util.MailResourceLoader;
import org.columba.ristretto.imap.IMAPFlags;
import org.columba.ristretto.message.Flags;
import org.columba.ristretto.message.Header;
import org.columba.ristretto.message.MessageFolderInfo;
import org.columba.ristretto.message.MimePart;
import org.columba.ristretto.message.MimeTree;
import org.columba.ristretto.message.StreamableMimePart;
import org.columba.ristretto.message.io.CharSequenceSource;
import org.columba.ristretto.message.io.SourceInputStream;

public class IMAPFolder extends RemoteFolder {

	/**
	 *
	 */
	private ImapItem item;
	/**
	 *
	 */
	//private boolean select=false;
	//private boolean fetch=false;

	//private StringBuffer cache;

	private Object aktMessageUid;
	/**
	 *
	 */
	private ColumbaMessage aktMessage;

	/**
	 *
	 */
	private boolean mailcheck = false;

	/**
	 *
	 */
	private IMAPStore store;

	/**
	 *
	 */
	protected HeaderList headerList;
	/**
	 *
	 */
	//Vector uids;

	protected RemoteHeaderCache cache;

	protected boolean existsOnServer;

	/**
	 *
	 */
	//protected RemoteSearchEngine searchEngine;

	/**
	 * @see org.columba.mail.folder.FolderTreeNode#FolderTreeNode(org.columba.mail.config.FolderItem)
	 */
	public IMAPFolder(FolderItem folderItem) {
		super(folderItem);

		cache = new RemoteHeaderCache(this);

		existsOnServer = true;

		//setChanged(true);
	}

	/**
	 * Method getSearchEngineInstance.
	 * @return AbstractSearchEngine
	 */
	/*
	public AbstractSearchEngine getSearchEngineInstance() {
		if (searchEngine == null)
			searchEngine = new RemoteSearchEngine(this);
	
		return searchEngine;
	}
	*/
	/**
	 * @see org.columba.mail.folder.Folder#searchMessages(org.columba.mail.filter.Filter, java.lang.Object, org.columba.core.command.WorkerStatusController)
	 */
	public Object[] searchMessages(Filter filter, Object[] uids)
		throws Exception {

		return getStore()
			.search(uids, filter.getFilterRule(), getImapPath())
			.toArray();
	}

	/**
	 * @see org.columba.mail.folder.Folder#searchMessages(org.columba.mail.filter.Filter, org.columba.core.command.WorkerStatusController)
	 */
	public Object[] searchMessages(Filter filter) throws Exception {

		List list = getStore().search(filter.getFilterRule(), getImapPath());

		if (list != null)
			return list.toArray();

		return null;
	}

	/**
	 * @see org.columba.mail.folder.FolderTreeNode#removeFolder()
	 */
	public void removeFolder() throws Exception {

		if (existsOnServer) {
			String path = getImapPath();

			boolean result = getStore().deleteFolder(path);
			if (!result)
				return;
		}
		super.removeFolder();
	}

	/**
	 * @see org.columba.mail.folder.Folder#renameFolder(java.lang.String)
	 */
	public boolean renameFolder(String name) throws Exception {
		String oldPath = getImapPath();
		ColumbaLogger.log.debug("old path=" + oldPath);

		String newPath = null;
		if (getParent() instanceof IMAPFolder)
			newPath = ((IMAPFolder) getParent()).getImapPath();

		newPath += getStore().getDelimiter() + name;
		ColumbaLogger.log.debug("new path=" + newPath);

		boolean result = getStore().renameFolder(oldPath, newPath);
		if (!result)
			return false;

		return super.renameFolder(name);

	}

	/**
	 * @see org.columba.mail.folder.Folder#getRootFolder()
	 */
	public FolderTreeNode getRootFolder() {
		FolderTreeNode folderTreeNode = (FolderTreeNode) getParent();
		while (folderTreeNode != null) {
			if (folderTreeNode instanceof IMAPRootFolder) {

				return (IMAPRootFolder) folderTreeNode;
			}

			folderTreeNode = (FolderTreeNode) folderTreeNode.getParent();
		}

		return null;
	}

	/**
	 * Method getStore.
	 * @return IMAPStore
	 */
	public IMAPStore getStore() {
		if (store == null)
			store = ((IMAPRootFolder) getRootFolder()).getStore();

		return store;
	}

	/**
	 * @see org.columba.mail.folder.Folder#getHeaderList(org.columba.core.command.WorkerStatusController)
	 */
	public HeaderList getHeaderList() throws Exception {

		headerList = cache.getHeaderList();
		// if this is the first time we download
		// a headerlist -> we need to save headercache
		if (headerList.count() == 0)
			changed = true;

		getObservable().setMessage(
			MailResourceLoader.getString(
				"statusbar",
				"message",
				"fetch_uid_list"));

		List newList = getStore().fetchUIDList(getImapPath());

		if (newList == null)
			return new HeaderList();

		List result = synchronize(headerList, newList);

		getObservable().setMessage(
			MailResourceLoader.getString(
				"statusbar",
				"message",
				"fetch_flags_list"));

		Flags[] flags = getStore().fetchFlagsList(getImapPath());

		getObservable().setMessage(
			MailResourceLoader.getString(
				"statusbar",
				"message",
				"fetch_header_list"));

		// if available -> fetch new headers
		if (result.size() > 0) {
			getStore().fetchHeaderList(headerList, result, getImapPath());			
		}

		messageFolderInfo = getStore().getSelectedFolderMessageFolderInfo();

		updateFlags(flags);

		return headerList;
	}

	/**
	 * Method updateFlags.
	 * @param flagsList
	 */
	protected void updateFlags(Flags[] flagsList) {
		
		

		// ALP 04/29/03
		// Reset the number of seen/resent/existing messages. Otherwise you
		// just keep adding to the number.
		MessageFolderInfo info = getMessageFolderInfo();
		info.setExists(0);
		info.setRecent(0);
		info.setUnseen(0);
		// END ADDS ALP 04/29/03

		for (int i = 0; i < flagsList.length; i++) {
			
			
			IMAPFlags flags = (IMAPFlags) flagsList[i];
			
			Integer uid = (Integer) flags.getUid();
				
			ColumbaHeader header = (ColumbaHeader) headerList.get(uid.toString());
			
			// if the parser didn't return a complete flags object
			// the UID in the flags object is totally wrong
			// -> just skip this flags update
			if ( header == null ) continue;
			
			Flags localFlags = header.getFlags();

			localFlags.setFlags(flags.getFlags());

			if (!flags.get(Flags.SEEN)) {
				info.incUnseen();
			}

			if (flags.get(Flags.RECENT)) {
				info.incRecent();
			}

			info.incExists();
		}
	}

	/**
	 * Method save.
	 */
	public void save() throws Exception {
		// only save header-cache if folder data changed
		if (hasChanged()) {
			cache.save();
			setChanged(false);
		}		
	}

	/**
	 * Method synchronize.
	 * @param headerList
	 * @param newList
	 * @return Vector
	 * @throws Exception
	 */
	public List synchronize(HeaderList headerList, List newList)
		throws Exception {

		LinkedList headerUids = new LinkedList();
		Enumeration keys = headerList.keys();
		while (keys.hasMoreElements()) {
			headerUids.add(keys.nextElement());
		}
		LinkedList newUids = new LinkedList(newList);

		ListTools.substract(newUids, headerUids);

		ListTools.substract(headerUids, new ArrayList(newList));
		Iterator it = headerUids.iterator();
		while (it.hasNext()) {
			headerList.remove(it.next());
		}
		return newUids;
		/*
		List result = new Vector();
		
		// delete old headers
		
		for (Enumeration e = headerList.keys(); e.hasMoreElements();) {
			String str = (String) e.nextElement();
		
			if (existsRemotely(str, 0, newList)) {
				// mail exists on server
				//  -> keep it
			} else {
				// mail doesn't exist on server
				//  -> remove it from local cache
				headerList.remove(str);
			}
		}
		for (Iterator it = newList.iterator(); it.hasNext();) {
			String str = (String) it.next();
			// for (int i = 0; i < newList.size(); i++) {
			// String str = (String) newList.get(i);
		
			if (existsLocally(str, headerList) == false) {
				// new message on server
				result.add(str);
			}
		}
		
		return result;
		*/
	}

	/**
	 * Method existsRemotely.
	 * @param uid
	 * @param startIndex
	 * @param uidList
	 * @return boolean
	 * @throws Exception
	 */
	protected boolean existsRemotely(String uid, int startIndex, List uidList)
		throws Exception {
		for (Iterator it = uidList.iterator(); it.hasNext();) {
			String serverUID = (String) it.next();
			// for (int i = startIndex; i < uidList.size(); i++) {
			// String serverUID = (String) uidList.get(i);

			//System.out.println("server message uid: "+ serverUID );
			if (uid.equals(serverUID)) {
				//System.out.println("local uid exists remotely");
				return true;
			}
		}

		return false;
	}

	/**
	 * Method existsLocally.
	 * @param uid
	 * @param list
	 * @return boolean
	 * @throws Exception
	 */
	protected boolean existsLocally(String uid, HeaderList list)
		throws Exception {

		for (Enumeration e = headerList.keys(); e.hasMoreElements();) {
			String localUID = (String) e.nextElement();

			//System.out.println("server message uid: "+ serverUID );
			if (uid.equals(localUID)) {
				//System.out.println("local uid exists remotely");
				return true;
			}
		}

		return false;
	}

	/**
	 * @see org.columba.mail.folder.Folder#getMimePartTree(java.lang.Object, org.columba.core.command.WorkerStatusController)
	 */
	public MimeTree getMimePartTree(Object uid) throws Exception {

		//System.out.println("------------------->IMAPFolder->getMimePartTree");

		return getStore().getMimePartTree(uid, getImapPath());
	}

	/**
	 * @see org.columba.mail.folder.Folder#getMimePart(java.lang.Object, java.lang.Integer, org.columba.core.command.WorkerStatusController)
	 */
	public MimePart getMimePart(Object uid, Integer[] address)
		throws Exception {

		//System.out.println("------------------->IMAPFolder->getMimePart");

		return getStore().getMimePart(uid, address, getImapPath());
	}

	/**
	 * @see org.columba.mail.folder.Folder#innerCopy(org.columba.mail.folder.Folder, java.lang.Object, org.columba.core.command.WorkerStatusController)
	 */
	public void innerCopy(Folder destFolder, Object[] uids) throws Exception {

		getStore().copy(
			((IMAPFolder) destFolder).getImapPath(),
			uids,
			getImapPath());

		//			mailbox was modified
		changed = true;
	}

	/**
	 * @see org.columba.mail.folder.Folder#addMessage(org.columba.mail.message.AbstractMessage, org.columba.core.command.WorkerStatusController)
	 */
	public Object addMessage(ColumbaMessage message) throws Exception {
		return null;
	}

	/**
	 * @see org.columba.mail.folder.Folder#addMessage(java.lang.String, org.columba.core.command.WorkerStatusController)
	 */
	public Object addMessage(String source) throws Exception {

		getStore().append(getImapPath(), source);

		// mailbox was modified
		changed = true;

		return null;
	}

	/**
	 * @see org.columba.mail.folder.Folder#exists(java.lang.Object, org.columba.core.command.WorkerStatusController)
	 */
	public boolean exists(Object uid) throws Exception {
		return cache.getHeaderList().containsKey(uid);
	}

	/**
	 * Method markMessage.
	 * @param uid
	 * @param variant
	 * @param worker
	 * @throws Exception
	 */
	protected void markMessage(Object uid, int variant) throws Exception {
		ColumbaHeader h = (ColumbaHeader) cache.getHeaderList().get(uid);

		if (h != null) {
			switch (variant) {
				case MarkMessageCommand.MARK_AS_READ :
					{
						if (h.get("columba.flags.recent").equals(Boolean.TRUE))
							getMessageFolderInfo().decRecent();
						if (h.get("columba.flags.seen").equals(Boolean.FALSE))
							getMessageFolderInfo().decUnseen();

						h.set("columba.flags.seen", Boolean.TRUE);
						h.set("columba.flags.recent", Boolean.FALSE);
						break;
					}
				case MarkMessageCommand.MARK_AS_UNREAD :
					{
						h.set("columba.flags.seen", Boolean.FALSE);
						getMessageFolderInfo().incUnseen();
						break;
					}
				case MarkMessageCommand.MARK_AS_FLAGGED :
					{
						h.set("columba.flags.flagged", Boolean.TRUE);
						break;
					}
				case MarkMessageCommand.MARK_AS_UNFLAGGED :
					{
						h.set("columba.flags.flagged", Boolean.FALSE);
						break;
					}
				case MarkMessageCommand.MARK_AS_EXPUNGED :
					{
						h.set("columba.flags.expunged", Boolean.TRUE);
						break;
					}
				case MarkMessageCommand.MARK_AS_UNEXPUNGED :
					{

						h.set("columba.flags.expunged", Boolean.FALSE);
						break;
					}
				case MarkMessageCommand.MARK_AS_ANSWERED :
					{
						h.set("columba.flags.answered", Boolean.TRUE);
						break;
					}
			}
		}
	}

	/**
	 * @see org.columba.mail.folder.Folder#markMessage(java.lang.Object, int, org.columba.core.command.WorkerStatusController)
	 */
	public void markMessage(Object[] uids, int variant) throws Exception {

		getStore().markMessage(uids, variant, getImapPath());

		for (int i = 0; i < uids.length; i++) {
			markMessage(uids[i], variant);
		}

		// mailbox was modified
		changed = true;
	}

	/**
	 * @see org.columba.mail.folder.Folder#removeMessage(java.lang.Object, org.columba.core.command.WorkerStatusController)
	 */
	public void removeMessage(Object uid) throws Exception {
	}

	/**
	 * @see org.columba.mail.folder.Folder#getUids(org.columba.core.command.WorkerStatusController)
	 */
	public Object[] getUids() throws Exception {
		headerList = cache.getHeaderList();
		Object[] uids = new Object[headerList.size()];
		int i = 0;
		for (Enumeration e = headerList.keys(); e.hasMoreElements();) {
			Object uid = e.nextElement();
			uids[i++] = uid;
		}

		return uids;
	}

	/**
	 * @see org.columba.mail.folder.Folder#expungeFolder(java.lang.Object, org.columba.core.command.WorkerStatusController)
	 */
	public void expungeFolder() throws Exception {

		boolean result = getStore().expunge(getImapPath());
		if (!result)
			return;

		Object[] uids = getUids();

		if (uids != null) {
			for (int i = 0; i < uids.length; i++) {
				Object uid = uids[i];

				ColumbaHeader h = (ColumbaHeader) headerList.getHeader(uid);

				Boolean expunged = (Boolean) h.get("columba.flags.expunged");

				ColumbaLogger.log.debug("expunged=" + expunged);

				if (expunged.equals(Boolean.TRUE)) {
					// move message to trash

					ColumbaLogger.log.debug(
						"moving message with UID " + uid + " to trash");

					// remove message
					headerList.remove(uid);
				}
			}
		}

		//		mailbox was modified
		changed = true;
	}

	/**
	 * @see org.columba.mail.folder.Folder#getMessageSource(java.lang.Object, org.columba.core.command.WorkerStatusController)
	 */
	public String getMessageSource(Object uid) throws Exception {
		return getStore().getMessageSource(uid, getImapPath());
	}

	/**
	 * @see org.columba.mail.folder.Folder#getMessageHeader(java.lang.Object, org.columba.core.command.WorkerStatusController)
	 */
	public ColumbaHeader getMessageHeader(Object uid) throws Exception {
		if (headerList == null)
			getHeaderList();
		return (ColumbaHeader) headerList.getHeader((String) uid);
	}

	/**
	 * Method getMessage.
	 * @param uid
	 * @param worker
	 * @return AbstractMessage
	 * @throws Exception
	 */
	public ColumbaMessage getMessage(Object uid) throws Exception {
		return new ColumbaMessage(
			(ColumbaHeader) headerList.getHeader((String) uid));
	}

	/**
	 * Method getImapPath.
	 * @return String
	 */
	public String getImapPath() {
		StringBuffer path = new StringBuffer();
		path.append(getName());
		FolderTreeNode child = this;

		while (true) {
			child = (FolderTreeNode) child.getParent();
			if (child instanceof IMAPRootFolder)
				break;

			String n = ((IMAPFolder) child).getName();

			path.insert(0, n + getStore().getDelimiter());
		}

		return path.toString();
	}

	/**
	 * @see org.columba.mail.folder.FolderTreeNode#getDefaultProperties()
	 */
	public static XmlElement getDefaultProperties() {
		XmlElement props = new XmlElement("property");

		props.addAttribute("accessrights", "user");
		props.addAttribute("subfolder", "true");

		return props;
	}

	/**
	 * @see org.columba.mail.folder.FolderTreeNode#tryToGetLock(java.lang.Object)
	 */
	public boolean tryToGetLock(Object locker) {
		// IMAP Folders have no own lock ,but share the lock from the Root
		// to ensure that only one operation can be processed simultanous

		return getRootFolder().tryToGetLock(locker);
	}

	/**
	 * @see org.columba.mail.folder.FolderTreeNode#releaseLock()
	 */
	public void releaseLock() {
		if (getRootFolder() != null)
			getRootFolder().releaseLock();
	}
	/**
	 * @param type
	 */
	public IMAPFolder(String name, String type) throws Exception {
		super(name, type);

		existsOnServer = true;

		cache = new RemoteHeaderCache(this);

		FolderItem item = getFolderItem();
		item.set("property", "accessrights", "user");
		item.set("property", "subfolder", "true");		
	}

	/* (non-Javadoc)
	 * @see org.columba.mail.folder.FolderTreeNode#addSubfolder(org.columba.mail.folder.FolderTreeNode)
	 */
	public void addSubfolder(FolderTreeNode child) throws Exception {
		super.addSubfolder(child);

		String path = getImapPath() + getStore().getDelimiter() + child.getName();

		boolean result = getStore().createFolder(path);
		
	}

	/* (non-Javadoc)
	 * @see org.columba.mail.folder.Folder#getObservable()
	 */
	public StatusObservable getObservable() {
		return ((IMAPRootFolder)getRootFolder()).getObservable();
	}

	/* (non-Javadoc)
	 * @see org.columba.mail.folder.MailboxInterface#addMessage(java.io.InputStream)
	 */
	public Object addMessage(InputStream in) throws Exception {
		StringBuffer stringSource = StreamUtils.readInString(in);

		getStore().append(getImapPath(), stringSource.toString());

		return null;
	}

	/* (non-Javadoc)
	 * @see org.columba.mail.folder.MailboxInterface#getAttribute(java.lang.Object, java.lang.String)
	 */
	public Object getAttribute(Object uid, String key) throws Exception {
		ColumbaHeader header = (ColumbaHeader) cache.getHeaderList().get(uid);

		return header.getAttributes();
	}

	/* (non-Javadoc)
	 * @see org.columba.mail.folder.MailboxInterface#getFlags(java.lang.Object)
	 */
	public Flags getFlags(Object uid) throws Exception {
		ColumbaHeader header = (ColumbaHeader) cache.getHeaderList().get(uid);

		return header.getFlags();
	}

	/* (non-Javadoc)
	 * @see org.columba.mail.folder.MailboxInterface#getHeaderFields(java.lang.Object, java.lang.String[])
	 */
	public Header getHeaderFields(Object uid, String[] keys) throws Exception {
		return null;
	}

	/* (non-Javadoc)
	 * @see org.columba.mail.folder.MailboxInterface#getMessageSourceStream(java.lang.Object)
	 */
	public InputStream getMessageSourceStream(Object uid) throws Exception {
		String stringSource = getStore().getMessageSource(uid, getImapPath());

		return new SourceInputStream((new CharSequenceSource(stringSource)));
	}

	/* (non-Javadoc)
	 * @see org.columba.mail.folder.MailboxInterface#getMimePartSourceStream(java.lang.Object, java.lang.Integer[])
	 */
	public InputStream getMimePartSourceStream(Object uid, Integer[] address)
		throws Exception {
		//TODO Implement this with the IMAP protocol
		return null;
	}

	/* (non-Javadoc)
	 * @see org.columba.mail.folder.MailboxInterface#getMimePartBodyStream(java.lang.Object, java.lang.Integer[])
	 */
	public InputStream getMimePartBodyStream(Object uid, Integer[] address)
		throws Exception {
		return (
			(StreamableMimePart) getStore().getMimePart(
				uid,
				address,
				getImapPath()))
			.getInputStream();
		//;
	}

	

}