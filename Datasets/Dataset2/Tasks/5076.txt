new Rfc822Parser().parse(source, true, header, 0);

package org.columba.mail.folder.mh;

import java.util.Enumeration;
import java.util.Hashtable;

import org.columba.core.command.WorkerStatusController;
import org.columba.core.config.AdapterNode;
import org.columba.core.logging.ColumbaLogger;
import org.columba.mail.config.FolderItem;
import org.columba.mail.folder.Folder;
import org.columba.mail.folder.LocalHeaderCache;
import org.columba.mail.folder.command.MarkMessageCommand;
import org.columba.mail.message.AbstractMessage;
import org.columba.mail.message.ColumbaHeader;
import org.columba.mail.message.HeaderInterface;
import org.columba.mail.message.HeaderList;
import org.columba.mail.message.Message;
import org.columba.mail.parser.Rfc822Parser;

/**
 * @author freddy
 *
 * To change this generated comment edit the template variable "typecomment":
 * Window>Preferences>Java>Templates.
 * To enable and disable the creation of type comments go to
 * Window>Preferences>Java>Code Generation.
 */
public class CachedMHFolder extends MHFolder {

	protected LocalHeaderCache cache;

	public CachedMHFolder(AdapterNode node, FolderItem item) {
		super(node, item);

		cache = new LocalHeaderCache(this);
	}

	public HeaderList getHeaderList(WorkerStatusController worker)
		throws Exception {
		return cache.getHeaderList(worker);
	}

	public void save() throws Exception {
		cache.save(null);
	}

	public boolean exists(Object uid, WorkerStatusController worker)
		throws Exception {
		return cache.getHeaderList(worker).containsKey(uid);
	}

	public ColumbaHeader getMessageHeader(
		Object uid,
		WorkerStatusController worker)
		throws Exception {

		return (ColumbaHeader) cache.getHeaderList(worker).get(uid);
	}
	
	public AbstractMessage getMessage(
		Object uid,
		WorkerStatusController worker)
		throws Exception {
		if (aktMessage != null) {
			if (aktMessage.getUID().equals(uid)) {
				// this message is already cached
				//ColumbaLogger.log.info("using already cached message..");

				return aktMessage;
			}
		}

		String source = getMessageSource(uid, worker);
		ColumbaHeader header = getMessageHeader(uid, worker);
		
		AbstractMessage message =
			new Rfc822Parser().parse(source, false, header, 0);
		message.setUID(uid);
		message.setSource( source );

		aktMessage = message;

		return message;
	}

	public Object addMessage(String source, WorkerStatusController worker)
		throws Exception {

		getHeaderList(worker);

		Object newUid = super.addMessage(source, worker);

		Rfc822Parser parser = new Rfc822Parser();

		ColumbaHeader header = parser.parseHeader(source);

		AbstractMessage m = new Message(header);
		ColumbaHeader h = (ColumbaHeader) m.getHeader();

		parser.addColumbaHeaderFields(h);

		if (h.get("columba.flags.recent").equals(Boolean.TRUE))
			getMessageFolderInfo().incRecent();
		if (h.get("columba.flags.seen").equals(Boolean.FALSE))
			getMessageFolderInfo().incUnseen();
		Integer sizeInt = new Integer(source.length());
		int size = Math.round(sizeInt.intValue() / 1024);
		h.set("columba.size", new Integer(size));

		h.set("columba.uid", newUid);

		cache.add(h);

		return newUid;
	}

	public Object addMessage(
		AbstractMessage message,
		WorkerStatusController worker)
		throws Exception {

		getHeaderList(worker);

		Object newUid = super.addMessage(message, worker);

		ColumbaHeader h =
			(ColumbaHeader) ((ColumbaHeader) message.getHeader()).clone();

		h.set("columba.uid", newUid);

		if (h.get("columba.flags.recent").equals(Boolean.TRUE))
			getMessageFolderInfo().incRecent();
		if (h.get("columba.flags.seen").equals(Boolean.FALSE))
			getMessageFolderInfo().incUnseen();

		cache.add(h);

		return newUid;
	}

	public void expungeFolder(Object[] uids, WorkerStatusController worker)
		throws Exception {

		for (int i = 0; i < uids.length; i++) {
			Object uid = uids[i];

			if (exists(uid, worker) == false)
				continue;

			ColumbaHeader h = getMessageHeader(uid, worker);
			Boolean expunged = (Boolean) h.get("columba.flags.expunged");

			//ColumbaLogger.log.debug("expunged=" + expunged);

			if (expunged.equals(Boolean.TRUE)) {
				// move message to trash

				//ColumbaLogger.log.info("moving message with UID " + uid + " to trash");

				// remove message
				removeMessage(uid, worker);

			}
		}
	}

	public void removeMessage(Object uid, WorkerStatusController worker)
		throws Exception {
		ColumbaHeader header = (ColumbaHeader) getMessageHeader(uid, worker);

		if (header.get("columba.flags.seen").equals(Boolean.FALSE))
			getMessageFolderInfo().decUnseen();
		if (header.get("columba.flags.recent").equals(Boolean.TRUE))
			getMessageFolderInfo().decRecent();

		cache.remove(uid);
		super.removeMessage(uid, worker);

	}

	protected void markMessage(
		Object uid,
		int variant,
		WorkerStatusController worker)
		throws Exception {
		ColumbaHeader h = (ColumbaHeader) cache.getHeaderList(worker).get(uid);

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
			case MarkMessageCommand.MARK_AS_FLAGGED :
				{
					h.set("columba.flags.flagged", Boolean.TRUE);
					break;
				}
			case MarkMessageCommand.MARK_AS_EXPUNGED :
				{

					h.set("columba.flags.expunged", Boolean.TRUE);
					break;
				}
			case MarkMessageCommand.MARK_AS_ANSWERED :
				{
					h.set("columba.flags.answered", Boolean.TRUE);
					break;
				}
		}
	}

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

	public Hashtable getAttributes() {
		Hashtable attributes = new Hashtable();
		attributes.put("accessrights", "user");
		attributes.put("messagefolder", "true");
		attributes.put("type", "columba");
		attributes.put("subfolder", "true");
		attributes.put("accessrights", "true");
		attributes.put("add", "true");
		attributes.put("remove", "true");
		return attributes;
	}

	public Folder instanceNewChildNode(AdapterNode node, FolderItem item) {
		return new CachedMHFolder(node, item);
	}

	public Object[] getUids(WorkerStatusController worker) throws Exception {
		cache.getHeaderList(worker);
		int count = cache.count();
		Object[] uids = new Object[count];
		int i = 0;
		for (Enumeration e = cache.getHeaderList(worker).keys();
			e.hasMoreElements();
			) {
			uids[i++] = e.nextElement();
		}

		return uids;
	}

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

}