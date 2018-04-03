public void removeMessage(Object uid, WorkerStatusController worker) throws Exception {

package org.columba.mail.folder.temp;

import java.util.Enumeration;
import java.util.Hashtable;

import org.columba.core.command.WorkerStatusController;
import org.columba.core.config.AdapterNode;
import org.columba.core.logging.ColumbaLogger;
import org.columba.mail.config.FolderItem;
import org.columba.mail.filter.Filter;
import org.columba.mail.folder.DataStorageInterface;
import org.columba.mail.folder.Folder;
import org.columba.mail.folder.LocalSearchEngine;
import org.columba.mail.folder.SearchEngineInterface;
import org.columba.mail.message.AbstractMessage;
import org.columba.mail.message.ColumbaHeader;
import org.columba.mail.message.HeaderList;
import org.columba.mail.message.Message;
import org.columba.mail.message.MimePart;
import org.columba.mail.message.MimePartTree;
import org.columba.mail.parser.Rfc822Parser;

/**
 * @author freddy
 *
 * To change this generated comment edit the template variable "typecomment":
 * Window>Preferences>Java>Templates.
 * To enable and disable the creation of type comments go to
 * Window>Preferences>Java>Code Generation.
 */
public class TempFolder extends Folder {

	protected HeaderList headerList;
	protected Hashtable messageList;

	protected int nextUid;
	protected AbstractMessage aktMessage;
	protected DataStorageInterface dataStorage;
	protected LocalSearchEngine searchEngine;

	/**
	 * Constructor for TempFolder.
	 * @param name
	 */
	public TempFolder(String name) {
		super(name);

		headerList = new HeaderList();
		messageList = new Hashtable();

		nextUid = 0;
	}

	public void clear() {
		headerList.clear();
		messageList.clear();
	}

	protected Object generateNextUid() {
		return new Integer(nextUid++);
	}

	public void setNextUid(int next) {
		nextUid = next;
	}

	/**
	 * @see org.columba.modules.mail.folder.Folder#expungeFolder(WorkerStatusController)
	 */
	public void expungeFolder(WorkerStatusController worker) throws Exception {
	}

	/**
	 * @see org.columba.modules.mail.folder.Folder#addMessage(AbstractMessage, WorkerStatusController)
	 */
	public Object addMessage(
		AbstractMessage message,
		WorkerStatusController worker)
		throws Exception {
		Object newUid = generateNextUid();

		ColumbaLogger.log.debug("new UID=" + newUid);

		ColumbaHeader h =
			(ColumbaHeader) ((ColumbaHeader) message.getHeader()).clone();

		h.set("columba.uid", newUid);

		headerList.add(h, newUid);

		messageList.put(newUid, message);

		return newUid;
	}

	/**
	 * @see org.columba.modules.mail.folder.Folder#addMessage(String, WorkerStatusController)
	 */
	public Object addMessage(String source, WorkerStatusController worker)
		throws Exception {
		Object newUid = generateNextUid();

		Rfc822Parser parser = new Rfc822Parser();

		ColumbaHeader header = parser.parseHeader(source);

		AbstractMessage m = new Message(header);
		ColumbaHeader h = (ColumbaHeader) m.getHeader();

		parser.addColumbaHeaderFields(h);

		Integer sizeInt = new Integer(source.length());
		int size = Math.round(sizeInt.intValue() / 1024);
		h.set("columba.size", new Integer(size));

		h.set("columba.uid", newUid);

		headerList.add(h, newUid);

		messageList.put(newUid, m);

		return newUid;
	}

	/**
	 * @see org.columba.modules.mail.folder.Folder#exists(Object)
	 */
	public boolean exists(Object uid) throws Exception {
		return messageList.containsKey(uid);
	}

	/**
	 * @see org.columba.modules.mail.folder.Folder#getHeaderList(WorkerStatusController)
	 */
	public HeaderList getHeaderList(WorkerStatusController worker)
		throws Exception {
		return headerList;
	}

	/**
	 * @see org.columba.modules.mail.folder.Folder#markMessage(Object[], int, WorkerStatusController)
	 */
	public void markMessage(
		Object[] uids,
		int variant,
		WorkerStatusController worker)
		throws Exception {
	}

	/**
	 * @see org.columba.modules.mail.folder.Folder#removeMessage(Object)
	 */
	public void removeMessage(Object uid) throws Exception {
		headerList.remove(uid);
		messageList.remove(uid);
	}

	/**
	 * @see org.columba.modules.mail.folder.Folder#getMimePart(Object, Integer[], WorkerStatusController)
	 */
	public MimePart getMimePart(
		Object uid,
		Integer[] address,
		WorkerStatusController worker)
		throws Exception {
		AbstractMessage message = (AbstractMessage) messageList.get(uid);

		MimePart mimePart = message.getMimePartTree().getFromAddress(address);

		return mimePart;
	}

	/**
	 * @see org.columba.modules.mail.folder.Folder#getMessageSource(Object, WorkerStatusController)
	 */
	public String getMessageSource(Object uid, WorkerStatusController worker)
		throws Exception {

		AbstractMessage message = getMessage(uid, worker);
		if (message == null) {
			System.out.println("no message for uid=" + uid);
			System.out.println("list-count=" + headerList.count());
			System.out.println("message-count=" + messageList.size());
			for (Enumeration e = messageList.keys(); e.hasMoreElements();) {
				System.out.println(e.nextElement());

			}

		}

		return message.getSource();
	}

	/**
	 * @see org.columba.modules.mail.folder.Folder#getMimePartTree(Object, WorkerStatusController)
	 */
	public MimePartTree getMimePartTree(
		Object uid,
		WorkerStatusController worker)
		throws Exception {
		AbstractMessage message = (AbstractMessage) messageList.get(uid);

		MimePartTree mptree = message.getMimePartTree();

		return mptree;
	}

	/**
	 * @see org.columba.modules.mail.folder.Folder#getMessageHeader(Object, WorkerStatusController)
	 */
	public ColumbaHeader getMessageHeader(
		Object uid,
		WorkerStatusController worker)
		throws Exception {

		ColumbaHeader header = (ColumbaHeader) headerList.get(uid);

		return header;
	}

	/**
	 * @see org.columba.modules.mail.folder.Folder#getMessage(Object, WorkerStatusController)
	 */
	public AbstractMessage getMessage(
		Object uid,
		WorkerStatusController worker)
		throws Exception {
		AbstractMessage message = (AbstractMessage) messageList.get(uid);

		return message;
	}

	public SearchEngineInterface getSearchEngineInstance() {
		if (searchEngine == null)
			searchEngine = new LocalSearchEngine(this);

		return searchEngine;
	}

	/**
	 * @see org.columba.modules.mail.folder.Folder#searchMessages(Filter, Object[], WorkerStatusController)
	 */
	public Object[] searchMessages(
		Filter filter,
		Object[] uids,
		WorkerStatusController worker)
		throws Exception {
		return getSearchEngineInstance().searchMessages(filter, uids, worker);
	}

	/**
	 * @see org.columba.modules.mail.folder.Folder#searchMessages(Filter, WorkerStatusController)
	 */
	public Object[] searchMessages(
		Filter filter,
		WorkerStatusController worker)
		throws Exception {
		return getSearchEngineInstance().searchMessages(filter, worker);
	}

	/**
	 * @see org.columba.modules.mail.folder.FolderTreeNode#instanceNewChildNode(AdapterNode, FolderItem)
	 */
	public Folder instanceNewChildNode(AdapterNode node, FolderItem item) {
		return null;
	}

	/**
	 * @see org.columba.modules.mail.folder.FolderTreeNode#getAttributes()
	 */
	public Hashtable getAttributes() {
		return null;
	}

	public String getName() {
		return toString();
	}

	public String toString() {
		return (String) getUserObject();
	}
}