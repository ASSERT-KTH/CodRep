protected ColumbaMessage getMessage(Object uid) throws Exception {

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
package org.columba.mail.folder.headercache;

import java.io.InputStream;
import java.util.Enumeration;
import java.util.List;
import java.util.Vector;

import org.columba.core.logging.ColumbaLogger;
import org.columba.core.util.Mutex;
import org.columba.mail.config.FolderItem;
import org.columba.mail.folder.LocalFolder;
import org.columba.mail.folder.command.MarkMessageCommand;
import org.columba.mail.message.ColumbaHeader;
import org.columba.mail.message.ColumbaMessage;
import org.columba.mail.message.HeaderList;
import org.columba.ristretto.message.Flags;
import org.columba.ristretto.message.Header;
import org.columba.ristretto.message.Message;
import org.columba.ristretto.message.io.CharSequenceSource;
import org.columba.ristretto.message.io.Source;
import org.columba.ristretto.parser.HeaderParser;
import org.columba.ristretto.parser.MessageParser;

/**
 * 
 * CachedFolder adds a header-cache facility to {@link LocalFolder}to be able
 * to quickly show a message summary, etc.
 * 
 * @author fdietz
 */
public abstract class CachedFolder extends LocalFolder {

	// header-cache implementation
	protected AbstractHeaderCache headerCache;
	protected Mutex mutex;

	/**
	 * @param item
	 *            <class>FolderItem</class> contains xml configuration of
	 *            this folder
	 */
	public CachedFolder(FolderItem item) {
		super(item);

		mutex = new Mutex(getName());
	}

	/**
	 * @see org.columba.mail.folder.Folder#addMessage(org.columba.mail.message.AbstractMessage,
	 *      org.columba.core.command.WorkerStatusController)
	 */
	public Object addMessage(ColumbaMessage message) throws Exception {

		if (message == null)
			return null;

		// get headerlist before adding a message
		getHeaderList();

		// call addMessage of superclass LocalFolder
		// to do the dirty work
		Object newUid = super.addMessage(message);
		if (newUid == null)
			return null;

		// this message was already parsed and so we
		// re-use the header to save us some cpu time
		ColumbaHeader h =
			(ColumbaHeader) ((ColumbaHeader) message.getHeader()).clone();

		// decode all headerfields:

		// remove all unnecessary headerfields which doesn't
		// need to be cached
		// -> saves much memory
		ColumbaHeader strippedHeader = CachedHeaderfields.stripHeaders(h);

		// free memory
		h = null;

		// set UID for new message
		strippedHeader.set("columba.uid", newUid);

		// increment recent count of messages if appropriate
		if (strippedHeader.get("columba.flags.recent").equals(Boolean.TRUE))
			getMessageFolderInfo().incRecent();

		// increment unseen count of messages if appropriate
		if (strippedHeader.get("columba.flags.seen").equals(Boolean.FALSE))
			getMessageFolderInfo().incUnseen();

		// add header to header-cache list
		getHeaderCacheInstance().add(strippedHeader);

		return newUid;
	}

	/**
	 * @see org.columba.mail.folder.Folder#exists(java.lang.Object,
	 *      org.columba.core.command.WorkerStatusController)
	 */
	public boolean exists(Object uid) throws Exception {

		// check if message with UID exists
		return getCachedHeaderList().containsKey(uid);
	}

	/**
	 * @see org.columba.mail.folder.Folder#expungeFolder(org.columba.core.command.WorkerStatusController)
	 */
	public void expungeFolder() throws Exception {

		// get list of all uids
		Object[] uids = getUids();

		for (int i = 0; i < uids.length; i++) {
			Object uid = uids[i];

			if (uid == null)
				continue;

			// if message with uid doesn't exist -> skip
			if (exists(uid) == false) {
				ColumbaLogger.log.debug("uid " + uid + " doesn't exist");

				continue;
			}

			Boolean expunged =
				(Boolean) getAttribute(uid, "columba.flags.expunged");

			if (expunged.equals(Boolean.TRUE)) {
				// move message to trash if marked as expunged

				ColumbaLogger.log.debug("removing uid=" + uid);

				// remove message
				removeMessage(uid);

			}
		}

		// folder was modified
		changed = true;
	}

	/**
	 * 
	 * Return headerlist from cache
	 * 
	 * This method is just another layer for getHeaderList() which adds a mutex
	 * to it.
	 * 
	 * We lock folders to be sure that only one <code>Command</code> at a
	 * time can modify the folder.
	 * 
	 * But we also allow to add messages at any time, because that doesn't
	 * interfere or causes problems ;-)
	 * 
	 * Adding the headercache here, makes it necessary to load the headercache,
	 * for the first time before we do any operation.
	 * 
	 * This is a speciality of the headercache implementation which has nothing
	 * to do with our Folder locking system and is put here for this reason.
	 * 
	 * @return <class>HeaderList</class>
	 * @throws Exception
	 *             <class>Exception</class>
	 */
	protected HeaderList getCachedHeaderList() throws Exception {
		HeaderList result;

		try {
			mutex.getMutex();
			result = getHeaderCacheInstance().getHeaderList();
		} finally {
			mutex.releaseMutex();
		}

		return result;
	}

	/**
	 * @see org.columba.mail.folder.Folder#getHeaderList(org.columba.core.command.WorkerStatusController)
	 */
	public HeaderList getHeaderList() throws Exception {
		return getCachedHeaderList();
	}

	/**
	 * @see org.columba.mail.folder.LocalFolder#getMessage(java.lang.Object,
	 *      org.columba.core.command.WorkerStatusController)
	 */
	public ColumbaMessage getMessage(Object uid) throws Exception {

		// check if message was already parsed before
		if (aktMessage != null) {
			if (aktMessage.getUID().equals(uid)) {
				// this message is already cached
				// -> no need to parse it again

				//return (AbstractMessage) aktMessage.clone();
				return (ColumbaMessage) aktMessage;
			}
		}

		// get source of message as string
		String source = getMessageSource(uid);

		// get header from cache
		ColumbaHeader header = (ColumbaHeader) getCachedHeaderList().get(uid);

		// generate message object from source
		Message m = MessageParser.parse(new CharSequenceSource(source));
		ColumbaMessage message = new ColumbaMessage(header, m);

		// set message uid
		message.setUID(uid);

		// set message source
		message.setStringSource(source);
		if (source == null) {
			source = new String();
		}

		// this is the new cached message
		// which should be re-used if possible
		aktMessage = message;

		// there's no need to clone() here

		//return (AbstractMessage) message.clone();
		return (ColumbaMessage) message;
	}

	/**
	 * @see org.columba.mail.folder.Folder#getMessageHeader(java.lang.Object,
	 *      org.columba.core.command.WorkerStatusController)
	 */
	public ColumbaHeader getMessageHeader(Object uid) throws Exception {

		if ((aktMessage != null) && (aktMessage.getUID().equals(uid))) {
			// message is already cached

			// try to compare the headerfield count of
			// the actually parsed message with the cached
			// headerfield count
			ColumbaMessage message = getMessage(uid);

			// number of headerfields
			int size = message.getHeader().count();

			// get header from cache
			ColumbaHeader h = (ColumbaHeader) getCachedHeaderList().get(uid);

			// message doesn't exist (this shouldn't happen here)
			if (h == null)
				return null;

			// number of headerfields
			int cachedSize = h.count();

			// if header contains from fields than the cached header
			if (size > cachedSize)
				return (ColumbaHeader) message.getHeader();

			return (ColumbaHeader) h;
		} else
			// message isn't cached
			// -> just return header from cache
			return (ColumbaHeader) getCachedHeaderList().get(uid);
	}

	/**
	 * @see org.columba.mail.folder.Folder#getUids(org.columba.core.command.WorkerStatusController)
	 */
	public Object[] getUids() throws Exception {

		int count = getCachedHeaderList().count();
		//Object[] uids = new Object[count];
		List list = new Vector(count);
		int i = 0;
		for (Enumeration e = getCachedHeaderList().keys();
			e.hasMoreElements();
			) {
			//uids[i++] = e.nextElement();
			list.add(e.nextElement());
		}

		Object[] uids = new Object[list.size()];
		((Vector) list).copyInto(uids);

		return uids;
	}

	/**
	 * @param uid
	 * @param variant
	 * @param worker
	 * @throws Exception
	 */
	protected void markMessage(Object uid, int variant) throws Exception {
		ColumbaHeader h = (ColumbaHeader) getCachedHeaderList().get(uid);

		switch (variant) {
			case MarkMessageCommand.MARK_AS_READ :
				{
					if (getAttribute(uid, "columba.flags.recent")
						.equals(Boolean.TRUE))
						getMessageFolderInfo().decRecent();

					if (getAttribute(uid, "columba.flags.seen")
						.equals(Boolean.FALSE))
						getMessageFolderInfo().decUnseen();

					setAttribute(uid, "columba.flags.seen", Boolean.TRUE);
					setAttribute(uid, "columba.flags.recent", Boolean.FALSE);
					break;
				}
			case MarkMessageCommand.MARK_AS_UNREAD :
				{
					setAttribute(uid, "columba.flags.seen", Boolean.FALSE);
					getMessageFolderInfo().incUnseen();
					break;
				}
			case MarkMessageCommand.MARK_AS_FLAGGED :
				{
					setAttribute(uid, "columba.flags.flagged", Boolean.TRUE);
					break;
				}
			case MarkMessageCommand.MARK_AS_UNFLAGGED :
				{
					setAttribute(uid, "columba.flags.flagged", Boolean.FALSE);
					break;
				}
			case MarkMessageCommand.MARK_AS_EXPUNGED :
				{
					if (getAttribute(uid, "columba.flags.seen")
						.equals(Boolean.FALSE))
						getMessageFolderInfo().decUnseen();

					setAttribute(uid, "columba.flags.seen", Boolean.TRUE);
					setAttribute(uid, "columba.flags.recent", Boolean.FALSE);

					h.set("columba.flags.expunged", Boolean.TRUE);
					break;
				}
			case MarkMessageCommand.MARK_AS_UNEXPUNGED :
				{

					setAttribute(uid, "columba.flags.expunged", Boolean.FALSE);
					break;
				}
			case MarkMessageCommand.MARK_AS_ANSWERED :
				{
					setAttribute(uid, "columba.flags.answered", Boolean.TRUE);
					break;
				}
			case MarkMessageCommand.MARK_AS_SPAM :
				{
					setAttribute(uid, "columba.spam", Boolean.TRUE);
					break;
				}
			case MarkMessageCommand.MARK_AS_NOTSPAM :
				{
					setAttribute(uid, "columba.spam", Boolean.FALSE);
					break;
				}
		}

		// message data has changed
		changed = true;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.columba.mail.folder.Folder#markMessage(java.lang.Object[], int,
	 *      org.columba.core.command.WorkerStatusController)
	 */
	public void markMessage(Object[] uids, int variant) throws Exception {

		for (int i = 0; i < uids.length; i++) {
			if (exists(uids[i])) {
				markMessage(uids[i], variant);
			}
		}
	}

	public void removeMessage(Object uid) throws Exception {

		// update message folder info
		if (getAttribute(uid, "columba.flags.seen").equals(Boolean.FALSE))
			getMessageFolderInfo().decUnseen();
		if (getAttribute(uid, "columba.flags.recent").equals(Boolean.TRUE))
			getMessageFolderInfo().decRecent();

		// remove message from headercache
		getHeaderCacheInstance().remove(uid);

		// call LocalFolder->removeMessage
		super.removeMessage(uid);
	}

	public void save() throws Exception {
		// only save header-cache if folder data changed
		if (hasChanged() == true) {

			getHeaderCacheInstance().save();
			setChanged(false);
		}

		// call Folder.save() to be sure that messagefolderinfo is saved
		super.save();
	}

	/**
	 * @return
	 */
	public AbstractHeaderCache getHeaderCacheInstance() {
		if (headerCache == null) {
			headerCache = new LocalHeaderCache(this);
		}
		return headerCache;
	}

	/**
	 * @param type
	 */
	public CachedFolder(String name, String type) {
		super(name, type);

		mutex = new Mutex(getName());

	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.columba.mail.folder.MailboxInterface#addMessage(java.io.InputStream)
	 */
	public Object addMessage(InputStream in) throws Exception {
		// get headerlist before adding a message
		getHeaderList();

		int size = in.available();

		// call addMessage of superclass LocalFolder
		// to do the dirty work
		Object newUid = super.addMessage(in);
		if (newUid == null)
			return null;

		Source source = getDataStorageInstance().getFileSource(newUid);

		Header header = HeaderParser.parse(source);
		ColumbaHeader h = new ColumbaHeader(header);
		h.getAttributes().put("columba.size", new Integer(size / 1024));

		// decode all headerfields:

		// remove all unnecessary headerfields which doesn't
		// need to be cached
		// -> saves much memory
		ColumbaHeader strippedHeader = CachedHeaderfields.stripHeaders(h);

		// free memory
		h = null;

		// set UID for new message
		strippedHeader.getAttributes().put("columba.uid", newUid);

		// increment recent count of messages if appropriate
		if (strippedHeader.getAttributes().get("columba.flags.recent").equals(Boolean.TRUE))
			getMessageFolderInfo().incRecent();

		// increment unseen count of messages if appropriate
		if (strippedHeader.getAttributes().get("columba.flags.seen").equals(Boolean.FALSE))
			getMessageFolderInfo().incUnseen();

		// add header to header-cache list
		getHeaderCacheInstance().add(strippedHeader);

		return newUid;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.columba.mail.folder.MailboxInterface#setFlags(java.lang.Object,
	 *      org.columba.ristretto.message.Flags)
	 */
	public void setFlags(Object uid, Flags flags) throws Exception {
		ColumbaHeader h = (ColumbaHeader) getCachedHeaderList().get(uid);

		Flags oldFlags = h.getFlags();
		h.setFlags(flags);

		// update MessageFolderInfo
		if (oldFlags.get(Flags.RECENT) && !flags.get(Flags.RECENT)) {
			getMessageFolderInfo().decRecent();
		}
		if (!oldFlags.get(Flags.RECENT) && flags.get(Flags.RECENT)) {
			getMessageFolderInfo().incRecent();
		}

		if (oldFlags.get(Flags.SEEN) && !flags.get(Flags.SEEN)) {
			getMessageFolderInfo().incUnseen();
		}
		if (!oldFlags.get(Flags.SEEN) && flags.get(Flags.SEEN)) {
			getMessageFolderInfo().decUnseen();
		}

	}

	public Object getAttribute(Object uid, String key) throws Exception {
		// get header with UID
		ColumbaHeader header = (ColumbaHeader) getHeaderList().get(uid);

		return header.getAttributes().get(key);
	}

	public void setAttribute(Object uid, String key, Object value)
		throws Exception {
		// get header with UID
		ColumbaHeader header = (ColumbaHeader) getHeaderList().get(uid);

		header.getAttributes().put(key, value);

		// set folder changed flag
		// -> if not, the header cache wouldn't notice that something
		// -> has changed. And wouldn't save the changes.
		setChanged(true);
	}

	/**
	 * This method first tries to find the requested header in the header
	 * cache. If the headerfield is not cached, the message source is parsed
	 * (@see LocalFolder).
	 *  
	 */
	public Header getHeaderFields(Object uid, String[] keys) throws Exception {
		// get header with UID
		ColumbaHeader header = (ColumbaHeader) getHeaderList().get(uid);

		Header result = new Header();

		// if only one headerfield wasn't found in cache
		// -> call LocalFolder.getHeaderFields() to parse the
		// -> complete message source
		boolean parsingNeeded = false;
		for (int i = 0; i < keys.length; i++) {
			if (header.get(keys[i]) != null) {
				// headerfield found
				result.set(keys[i], header.get(keys[i]));
			} else
				parsingNeeded = true;
		}

		if (parsingNeeded)
			return super.getHeaderFields(uid, keys);
		else
			return result;
	}

}