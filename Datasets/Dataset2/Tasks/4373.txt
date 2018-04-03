new Rfc822Parser().parse(source, null);

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

import org.columba.core.command.WorkerStatusController;
import org.columba.core.io.DiskIO;
import org.columba.core.logging.ColumbaLogger;
import org.columba.core.xml.XmlElement;
import org.columba.mail.config.FolderItem;
import org.columba.mail.filter.Filter;
import org.columba.mail.filter.FilterList;
import org.columba.mail.folder.search.AbstractSearchEngine;
import org.columba.mail.folder.search.LocalSearchEngine;
import org.columba.mail.folder.search.LuceneSearchEngine;
import org.columba.mail.message.AbstractMessage;
import org.columba.mail.message.ColumbaHeader;
import org.columba.mail.message.Message;
import org.columba.mail.message.MimePart;
import org.columba.mail.message.MimePartTree;
import org.columba.mail.parser.Rfc822Parser;

/**
 * @author fdietz
 *
 * <class>LocalFolder</class> is a near-working folder,
 * which only needs a specific datastorage and
 * search-engine "plugged in" to make it work.
 * 
 * This class is abstract becaused we use 
 * <class>CachedLocalFolder</class> instead which
 * contains a header-cache facility which 
 * Columba needs to be able to quickly show
 * a message summary, etc.
 *  
 */
public abstract class LocalFolder extends Folder {

	// the next messag which gets added to this folder
	// receives this unique ID
	protected int nextMessageUid;

	// we keep one message in cache in order to not 
	// needing to parse it twice times
	protected AbstractMessage aktMessage;

	// implement your own mailbox format here
	protected DataStorageInterface dataStorage;

	// implement your own search-engine here
	protected AbstractSearchEngine searchEngine;

	/**
	 * @param item	<class>FolderItem</class> contains xml configuration of this folder
	 */
	public LocalFolder(FolderItem item) {
		super(item);

		// create filterlist datastructure
		XmlElement filterListElement = node.getElement("filterlist");
		if (filterListElement == null) {
			// no filterlist treenode found 
			// -> create a new one
			filterListElement = new XmlElement("filterlist");
			getFolderItem().getRoot().addElement(filterListElement);
		}

		filterList = new FilterList(filterListElement);

	} // constructor

	/**
	 * @param name	<class>String</class> with name of folder
	 */
	// use this constructor only with tempfolders
	public LocalFolder(String name) {
		super(name);
	} // constructor

	/**
	 * Remove folder from tree
	 * 
	 * @see org.columba.mail.folder.FolderTreeNode#removeFolder()
	 */
	public void removeFolder() throws Exception {
		// delete folder from your harddrive
		boolean b = DiskIO.deleteDirectory(directoryFile);

		// if this worked, remove it from tree.xml configuration, too
		if (b == true)
			super.removeFolder();
	}

	/**
	 * 
	 * Generate new unique message ID
	 * 
	 * @return	<class>Integer</class> containing UID
	 */
	protected Object generateNextMessageUid() {
		return new Integer(nextMessageUid++);
	}

	/**
	 * 
	 * Set next unique message ID
	 * 
	 * @param next		number of next message
	 */
	public void setNextMessageUid(int next) {
		nextMessageUid = next;
	}

	/**
	 * 
	 * Implement a <class>DataStorageInterface</class> for the
	 * mailbox format of your pleasure
	 * 
	 * @return	instance of <class>DataStorageInterface</class> 
	 */
	public abstract DataStorageInterface getDataStorageInstance();

	/**
	
	 * 
	 * @see org.columba.mail.folder.Folder#exists(java.lang.Object, org.columba.core.command.WorkerStatusController)
	 */
	public boolean exists(Object uid, WorkerStatusController worker)
		throws Exception {
		return getDataStorageInstance().exists(uid);
	}

	/**
	
	 * 
	 * @see org.columba.mail.folder.Folder#addMessage(org.columba.mail.message.AbstractMessage, org.columba.core.command.WorkerStatusController)
	 */
	public Object addMessage(
		AbstractMessage message,
		WorkerStatusController worker)
		throws Exception {

		// load headerlist before adding a message
		getHeaderList(worker);

		// generate UID for new message
		Object newUid = generateNextMessageUid();

		// apply UID for message
		message.setUID(newUid);

		ColumbaLogger.log.debug("new UID=" + newUid);

		// get message source
		String source = message.getSource();
		if( source == null) {
			System.out.println( "source is null " + newUid );
		}

		// save message to disk
		getDataStorageInstance().saveMessage(source, newUid);

		// increase total count of messages
		getMessageFolderInfo().incExists();

		// notify search-engine 
		getSearchEngineInstance().messageAdded(message);

		// this folder has changed
		changed = true;

		//		free memory 
		// -> we don't need the message object anymore
		message.freeMemory();

		return newUid;
	}

	/** 
	 * @see org.columba.mail.folder.Folder#addMessage(java.lang.String, org.columba.core.command.WorkerStatusController)
	 */
	public Object addMessage(String source, WorkerStatusController worker)
		throws Exception {

		// init parser
		Rfc822Parser parser = new Rfc822Parser();

		// parse header of message
		ColumbaHeader header = parser.parseHeader(source);

		// calculate size of message based on source string length
		int size = Math.round(source.length() / 1024);
		header.set("columba.size", new Integer(size));

		// add Columba's internal headerfields
		parser.addColumbaHeaderFields(header);

		// generate message object 
		AbstractMessage m = new Message(header);
		m.setSource(source);

		// this folder was modified
		changed = true;

		return addMessage(m, worker);
	}

	/**
	 * @see org.columba.mail.folder.Folder#removeMessage(java.lang.Object, org.columba.core.command.WorkerStatusController)
	 */
	public void removeMessage(Object uid, WorkerStatusController worker)
		throws Exception {

		// remove message from disk
		getDataStorageInstance().removeMessage(uid);

		// notify search-engine
		getSearchEngineInstance().messageRemoved(uid);

		// decrement total count of message
		getMessageFolderInfo().decExists();

		// this folder was modified
		changed = true;
	}

	/**
	 * 
	 * Return message with certain UID 
	 * 
	 * 
	 * @param uid			unique message ID
	 * @param worker		<class>WorkerStatusController</class>
	 * @return				a message object referring to this UID
	 * @throws Exception	<class>Exception</class>
	 */
	public AbstractMessage getMessage(
		Object uid,
		WorkerStatusController worker)
		throws Exception {
		if (aktMessage != null) {
			if (aktMessage.getUID().equals(uid)) {
				// this message is already cached
				//ColumbaLogger.log.info("using already cached message..");

				return (AbstractMessage) aktMessage.clone();
			}
		}

		String source = getMessageSource(uid, worker);
		//ColumbaHeader h = getMessageHeader(uid, worker);

		AbstractMessage message =
			new Rfc822Parser().parse(source, true, null, 0);
		message.setUID(uid);
		message.setSource(source);
		//message.setHeader(h);

		aktMessage = message;

		return (AbstractMessage) message.clone();
	}

	/**
	 * @see org.columba.mail.folder.Folder#getMimePart(java.lang.Object, java.lang.Integer[], org.columba.core.command.WorkerStatusController)
	 */
	public MimePart getMimePart(
		Object uid,
		Integer[] address,
		WorkerStatusController worker)
		throws Exception {

		// get message with UID
		AbstractMessage message = getMessage(uid, worker);

		// get mimepart of message
		MimePart mimePart = message.getMimePartTree().getFromAddress(address);

		return mimePart;
	}

	/**
	 * @see org.columba.mail.folder.Folder#getMessageHeader(java.lang.Object, org.columba.core.command.WorkerStatusController)
	 */
	public ColumbaHeader getMessageHeader(
		Object uid,
		WorkerStatusController worker)
		throws Exception {

		// get message with UID
		AbstractMessage message = getMessage(uid, worker);

		// get header of message
		ColumbaHeader header = (ColumbaHeader) message.getHeader();

		return header;
	}

	/**
	 * @see org.columba.mail.folder.Folder#getMessageSource(java.lang.Object, org.columba.core.command.WorkerStatusController)
	 */
	public String getMessageSource(Object uid, WorkerStatusController worker)
		throws Exception {

		// get source of message
		String source = getDataStorageInstance().loadMessage(uid);

		return source;
	}

	/* (non-Javadoc)
	 * @see org.columba.mail.folder.Folder#getMimePartTree(java.lang.Object, org.columba.core.command.WorkerStatusController)
	 */
	public MimePartTree getMimePartTree(
		Object uid,
		WorkerStatusController worker)
		throws Exception {

		// get message with UID
		AbstractMessage message = getMessage(uid, worker);

		// get tree-like structure of mimeparts
		MimePartTree mptree = message.getMimePartTree();

		return mptree;
	}

	/********************** searching/filtering ***********************/

	/**
	* @return		instance of search-engine implementation
	*/
	public AbstractSearchEngine getSearchEngineInstance() {
		// only use lucene backend if specified in tree.xml
		if (searchEngine == null) {
			boolean enableLucene =
				getFolderItem().getBoolean("property", "enable_lucene", false);

			if (enableLucene == true)
				searchEngine = new LuceneSearchEngine(this);
			else
				searchEngine = new LocalSearchEngine(this);
		}

		return searchEngine;
	}

	/**
	 * @see org.columba.mail.folder.Folder#searchMessages(org.columba.mail.filter.Filter, java.lang.Object[], org.columba.core.command.WorkerStatusController)
	 */
	public Object[] searchMessages(
		Filter filter,
		Object[] uids,
		WorkerStatusController worker)
		throws Exception {
		return getSearchEngineInstance().searchMessages(filter, uids, worker);
	}

	/**
	 * @see org.columba.mail.folder.Folder#searchMessages(org.columba.mail.filter.Filter, org.columba.core.command.WorkerStatusController)
	 */
	public Object[] searchMessages(
		Filter filter,
		WorkerStatusController worker)
		throws Exception {
		return getSearchEngineInstance().searchMessages(filter, worker);
	}

	/**
	 * @see org.columba.mail.folder.Folder#size()
	 */
	public int size() {

		// return number of messages
		return getDataStorageInstance().getMessageCount();
	}

}