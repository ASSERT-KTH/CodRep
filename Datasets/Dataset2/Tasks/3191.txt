folder.setNextMessageUid(nextUid);

package org.columba.mail.folder;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.util.Enumeration;

import org.columba.core.command.WorkerStatusController;
import org.columba.core.logging.ColumbaLogger;
import org.columba.mail.message.ColumbaHeader;
import org.columba.mail.message.HeaderInterface;
import org.columba.mail.message.HeaderList;

/**
 * @author freddy
 *
 * To change this generated comment edit the template variable "typecomment":
 * Window>Preferences>Java>Templates.
 * To enable and disable the creation of type comments go to
 * Window>Preferences>Java>Code Generation.
 */
public abstract class AbstractHeaderCache {

	protected HeaderList headerList;

	protected File headerFile;

	protected boolean headerCacheAlreadyLoaded;

	protected LocalFolder folder;

	public AbstractHeaderCache(LocalFolder folder) {
		this.folder = folder;

		headerFile = new File(folder.getDirectoryFile(), ".header");

		headerList = new HeaderList();

		headerCacheAlreadyLoaded = false;
	}
	
	public HeaderInterface createHeaderInstance()
	{
		return new ColumbaHeader();
	}

	public boolean isHeaderCacheAlreadyLoaded() {
		return headerCacheAlreadyLoaded;
	}

	public boolean exists(Object uid) throws Exception {
		return headerList.contains(uid);
	}

	public int count() {
		return headerList.size();
	}

	public void remove(Object uid) throws Exception {
		ColumbaLogger.log.debug("trying to remove message UID=" + uid);

		if (headerList.containsKey(uid)) {
			ColumbaLogger.log.debug("remove UID=" + uid);

			headerList.remove(uid);
		}
	}

	public void add(HeaderInterface header) throws Exception {
		headerList.add(header, header.get("columba.uid"));
	}

	public HeaderList getHeaderList(WorkerStatusController worker)
		throws Exception {
		// if there exists a ".header" cache-file
		//  try to load the cache	
		if (headerCacheAlreadyLoaded == false) {
			try {
				if (headerFile.exists()) {
					load(worker);
					headerCacheAlreadyLoaded = true;
				} else {
					headerList =
						folder.getDataStorageInstance().recreateHeaderList(
							worker);
					headerCacheAlreadyLoaded = true;
				}
			} catch (Exception ex) {
				ex.printStackTrace();

				headerList =
					folder.getDataStorageInstance().recreateHeaderList(worker);

				headerCacheAlreadyLoaded = true;

			}

		}

		//System.out.println("headerList=" + headerList);

		return headerList;
	}

	public void load(WorkerStatusController worker) throws Exception {

		ColumbaLogger.log.info("loading header-cache=" + headerFile);

		FileInputStream istream = new FileInputStream(headerFile.getPath());
		ObjectInputStream p = new ObjectInputStream(istream);

		int capacity = p.readInt();
		ColumbaLogger.log.info("capacity=" + capacity);

		if (capacity != folder.getDataStorageInstance().getMessageCount()) {
			// messagebox headercache-file is corrupted

			headerList =
				folder.getDataStorageInstance().recreateHeaderList(worker);
			return;
		}

		headerList = new HeaderList(capacity);
		Integer uid;

		//System.out.println("Number of Messages : " + capacity);

		worker.setDisplayText("Loading headers from cache...");
		
		if (worker != null)
			worker.setProgressBarMaximum(capacity);

		int nextUid = -1;

		for (int i = 1; i <= capacity; i++) {
			if (worker != null)
				worker.setProgressBarValue(i);

			//ColumbaHeader h = message.getHeader();
			HeaderInterface h = createHeaderInstance();

			/*
			// read current number of message
			p.readInt();
			*/

			loadHeader(p, h);

			//System.out.println("message=" + h.get("subject"));

			headerList.add(h, (Integer) h.get("columba.uid"));

			if ( h.get("columba.flags.recent").equals(Boolean.TRUE) ) folder.getMessageFolderInfo().incRecent();
			if ( h.get("columba.flags.seen").equals(Boolean.FALSE)  ) folder.getMessageFolderInfo().incUnseen();
			folder.getMessageFolderInfo().incExists();
		
			int aktUid = ((Integer) h.get("columba.uid")).intValue();
			if (nextUid < aktUid)
				nextUid = aktUid;

		}

		nextUid++;
		ColumbaLogger.log.debug("next UID for new messages =" + nextUid);
		folder.setNextUid(nextUid);

		// close stream
		p.close();
	}

	public void save(WorkerStatusController worker) throws Exception {

		// we didn't load any header to save
		if (isHeaderCacheAlreadyLoaded() == false)
			return;

		ColumbaLogger.log.info("saveing header-cache=" + headerFile);
		// this has to called only if the uid becomes higher than Integer allows
		//cleanUpIndex();

		//System.out.println("saving headerfile: "+ headerFile.toString() );

		FileOutputStream istream = new FileOutputStream(headerFile.getPath());
		ObjectOutputStream p = new ObjectOutputStream(istream);

		//int count = getMessageFileCount();
		int count = headerList.count();
		ColumbaLogger.log.info("capacity=" + count);
		p.writeInt(count);

		ColumbaHeader h;
		//Message message;

		int i = 0;
		for (Enumeration e = headerList.keys(); e.hasMoreElements();) {
			Object uid = e.nextElement();

			h = (ColumbaHeader) headerList.getHeader(uid);

			if (h != null)
				saveHeader(p, h);
		}
		/*
		for (int i = 0; i < count; i++) {
			p.writeInt(i + 1);
		
			h = headerList.getHeader(new Integer(i));
		
			saveHeader(p, h);
		
		}
		*/
		//p.flush();
		p.close();
	}

	protected abstract void loadHeader(ObjectInputStream p, HeaderInterface h)
		throws Exception;

	protected abstract void saveHeader(ObjectOutputStream p, HeaderInterface h)
		throws Exception;

}