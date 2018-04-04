new Rfc822Parser().parse(source, header);

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
package org.columba.mail.folder.headercache;

import java.util.Enumeration;

import org.columba.core.command.WorkerStatusController;
import org.columba.mail.coder.EncodedWordDecoder;
import org.columba.mail.config.FolderItem;
import org.columba.mail.folder.Folder;
import org.columba.mail.folder.LocalFolder;
import org.columba.mail.folder.command.MarkMessageCommand;
import org.columba.mail.message.AbstractMessage;
import org.columba.mail.message.ColumbaHeader;
import org.columba.mail.message.HeaderInterface;
import org.columba.mail.message.HeaderList;
import org.columba.mail.parser.Rfc822Parser;

/**
 * @author fdietz
 *
 * <class>CachedFolder</class> adds a header-cache
 * facility to <class>LocalFolder</class> to be 
 * able to quickly show a message summary, etc.
 */
public abstract class CachedFolder extends LocalFolder {

	// header-cache implementation
	protected AbstractHeaderCache headerCache;

	/**
	 * @param item	<class>FolderItem</class> contains xml configuration of this folder
	 */
	public CachedFolder(FolderItem item) {
		super(item);
	}

	/**
	 * @see org.columba.mail.folder.Folder#addMessage(org.columba.mail.message.AbstractMessage, org.columba.core.command.WorkerStatusController)
	 */
	public Object addMessage(
		AbstractMessage message,
		WorkerStatusController worker)
		throws Exception {

		// get headerlist before adding a message
		getHeaderList(worker);

		// call addMessage of superclass LocalFolder
		// to do the dirty work
		Object newUid = super.addMessage(message, worker);

		// this message was already parsed and so we
		// re-use the header to save us some cpu time
		ColumbaHeader h =
			(ColumbaHeader) ((ColumbaHeader) message.getHeader()).clone();

		// decode all headerfields:

		// init encoded word decoder
		EncodedWordDecoder decoder = new EncodedWordDecoder();

		// get list of used-defined headerfields
		String[] list = CachedHeaderfieldOwner.getCachedHeaderfieldArray();

		//TableItem v = MailConfig.getMainFrameOptionsConfig().getTableItem();
		String column;
		for (int j = 0; j < list.length; j++) {

			column = (String) list[j];

			Object item = h.get(column);

			// only decode strings
			if (item instanceof String) {
				String str = (String) item;
				h.set(column, decoder.decode(str));
			}
		}

		// remove all unnecessary headerfields which doesn't
		// need to be cached
		// -> saves much memory
		ColumbaHeader strippedHeader = CachedHeaderfieldOwner.stripHeaders(h);

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
	 * @see org.columba.mail.folder.Folder#exists(java.lang.Object, org.columba.core.command.WorkerStatusController)
	 */
	public boolean exists(Object uid, WorkerStatusController worker)
		throws Exception {

		// check if message with UID exists
		return getCachedHeaderList(worker).containsKey(uid);
	}

	/**
	 * @see org.columba.mail.folder.Folder#expungeFolder(org.columba.core.command.WorkerStatusController)
	 */
	public void expungeFolder(WorkerStatusController worker) throws Exception {

		// get list of all uids 
		Object[] uids = getUids(worker);

		for (int i = 0; i < uids.length; i++) {
			Object uid = uids[i];

			// if message with uid doesn't exist -> skip
			if (exists(uid, worker) == false)
				continue;

			// retrieve header of messages
			ColumbaHeader h = getMessageHeader(uid, worker);
			Boolean expunged = (Boolean) h.get("columba.flags.expunged");

			if (expunged.equals(Boolean.TRUE)) {
				// move message to trash if marked as expunged

				// remove message
				removeMessage(uid, worker);

			}
		}

		// folder was modified
		changed = true;
	}

	/**
	 * 
	 * Return headerlist from cache
	 * 
	 * 
	 * @param worker		<class>WorkerStatusController</class>
	 * @return				<class>HeaderList</class>
	 * @throws Exception	<class>Exception</class>
	 */
	protected HeaderList getCachedHeaderList(WorkerStatusController worker)
		throws Exception {
		HeaderList result;
		result = getHeaderCacheInstance().getHeaderList(worker);

		return result;
	}

	/**
	 * @see org.columba.mail.folder.Folder#getHeaderList(org.columba.core.command.WorkerStatusController)
	 */
	public HeaderList getHeaderList(WorkerStatusController worker)
		throws Exception {
		return getCachedHeaderList(worker);
	}

	/**
	 * @see org.columba.mail.folder.LocalFolder#getMessage(java.lang.Object, org.columba.core.command.WorkerStatusController)
	 */
	public AbstractMessage getMessage(
		Object uid,
		WorkerStatusController worker)
		throws Exception {

		// check if message was already parsed before
		if (aktMessage != null) {
			if (aktMessage.getUID().equals(uid)) {
				// this message is already cached
				// -> no need to parse it again
				return (AbstractMessage) aktMessage.clone();
			}
		}

		// get source of message as string
		String source = getMessageSource(uid, worker);

		// get header from cache
		ColumbaHeader header =
			(ColumbaHeader) getCachedHeaderList(worker).get(uid);

		// generate message object from source
		AbstractMessage message =
			new Rfc822Parser().parse(source, true, header, 0);

		// set message uid
		message.setUID(uid);

		// set message source
		message.setSource(source);
		if (source == null) {
			source = new String();
		}

		// this is the new cached message
		// which should be re-used if possible
		aktMessage = message;

		return (AbstractMessage) message.clone();
	}

	/**
	 * @see org.columba.mail.folder.Folder#getMessageHeader(java.lang.Object, org.columba.core.command.WorkerStatusController)
	 */
	public ColumbaHeader getMessageHeader(
		Object uid,
		WorkerStatusController worker)
		throws Exception {

		if ((aktMessage != null) && (aktMessage.getUID().equals(uid))) {
			// message is already cached

			// try to compare the headerfield count of
			// the actually parsed message with the cached
			// headerfield count
			AbstractMessage message = getMessage(uid, worker);

			// number of headerfields
			int size = message.getHeader().count();

			// get header from cache
			HeaderInterface h =
				(ColumbaHeader) getCachedHeaderList(worker).get(uid);

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
			return (ColumbaHeader) getCachedHeaderList(worker).get(uid);
	}

	/**
	 * @see org.columba.mail.folder.Folder#getUids(org.columba.core.command.WorkerStatusController)
	 */
	public Object[] getUids(WorkerStatusController worker) throws Exception {

		int count = getCachedHeaderList(worker).count();
		Object[] uids = new Object[count];
		int i = 0;
		for (Enumeration e = getCachedHeaderList(worker).keys();
			e.hasMoreElements();
			) {
			uids[i++] = e.nextElement();
		}

		return uids;
	}

	/**
	 * @see org.columba.mail.folder.Folder#innerCopy(org.columba.mail.folder.Folder, java.lang.Object[], org.columba.core.command.WorkerStatusController)
	 */
	public void innerCopy(
		Folder destFolder,
		Object[] uids,
		WorkerStatusController worker)
		throws Exception {
		for (int i = 0; i < uids.length; i++) {

			Object uid = uids[i];

			if (exists(uid, worker)) {
				AbstractMessage message = getMessage(uid, worker);

				destFolder.addMessage(message, worker);
			}

			worker.setProgressBarValue(i);
		}
	}

	/**
	 * @param uid
	 * @param variant
	 * @param worker
	 * @throws Exception
	 */
	protected void markMessage(
		Object uid,
		int variant,
		WorkerStatusController worker)
		throws Exception {
		ColumbaHeader h = (ColumbaHeader) getCachedHeaderList(worker).get(uid);

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

		changed = true;
	}

	/* (non-Javadoc)
	 * @see org.columba.mail.folder.Folder#markMessage(java.lang.Object[], int, org.columba.core.command.WorkerStatusController)
	 */
	public void markMessage(
		Object[] uids,
		int variant,
		WorkerStatusController worker)
		throws Exception {

		for (int i = 0; i < uids.length; i++) {
			if (exists(uids[i], worker)) {
				markMessage(uids[i], variant, worker);
			}
		}
	}

	/* (non-Javadoc)
	 * @see org.columba.mail.folder.Folder#removeMessage(java.lang.Object, org.columba.core.command.WorkerStatusController)
	 */
	public void removeMessage(Object uid, WorkerStatusController worker)
		throws Exception {
		ColumbaHeader header = (ColumbaHeader) getMessageHeader(uid, worker);

		if (header.get("columba.flags.seen").equals(Boolean.FALSE))
			getMessageFolderInfo().decUnseen();
		if (header.get("columba.flags.recent").equals(Boolean.TRUE))
			getMessageFolderInfo().decRecent();

		getHeaderCacheInstance().remove(uid);
		super.removeMessage(uid, worker);
	}

	/* (non-Javadoc)
	 * @see org.columba.mail.folder.Folder#save(org.columba.core.command.WorkerStatusController)
	 */
	public void save(WorkerStatusController worker) throws Exception {
		// only save header-cache if folder data changed
		if (getChanged() == true) {

			getHeaderCacheInstance().save(worker);
			setChanged(false);
		}

		// call Folder.save() to be sure that messagefolderinfo is saved
		super.save(worker);
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

}