getObservable().clearMessage(500);	// 500 ms delay

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

import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.util.Enumeration;

import org.columba.core.logging.ColumbaLogger;
import org.columba.mail.folder.Folder;
import org.columba.mail.message.ColumbaHeader;
import org.columba.mail.message.HeaderList;
import org.columba.mail.util.MailResourceLoader;
import org.columba.ristretto.message.HeaderInterface;

/**
 * IMAP-specific implementation of a header cache.
 * 
 *
 * @author fdietz
 */
public class RemoteHeaderCache extends AbstractFolderHeaderCache {

	/**
	 * Constructor for RemoteHeaderCache.
	 * @param folder
	 */
	public RemoteHeaderCache(Folder folder) {
		super(folder);
	}

	public void load() throws Exception {
		ColumbaLogger.log.info("loading header-cache=" + headerFile);
		headerList = new HeaderList();

		ObjectInputStream p = openInputStream();
		int capacity = 0 ;
		
		if (p.available() > 0)
			capacity = p.readInt();
		
		ColumbaLogger.log.info("capacity=" + capacity);

		if (getObservable() != null) {
			getObservable().setMessage(
				MailResourceLoader.getString(
					"statusbar",
					"message",
					"load_headers"));
			getObservable().setMax(capacity);
			getObservable().resetCurrent();
		}

		for (int i = 1; i <= capacity; i++) {
			if (getObservable() != null)
				getObservable().setCurrent(i);

			ColumbaHeader h = new ColumbaHeader();

			loadHeader(p, h);

			headerList.add(h, (Integer) h.get("columba.uid"));
		}

		// close stream
		closeInputStream();

		// we are done
		if (getObservable() != null) {
			getObservable().clearMessage();
			getObservable().resetCurrent();
		}
		
	}

	public void save() throws Exception {
		// we didn't load any header to save
		if (!isHeaderCacheLoaded())
			return;

		ColumbaLogger.log.info("saving header-cache=" + headerFile);

		ObjectOutputStream p = openOutputStream();

		int count = headerList.count();
		if (count == 0)
			return;

		p.writeInt(count);

		ColumbaHeader h;

		for (Enumeration e = headerList.keys(); e.hasMoreElements();) {
			Object uid = (Integer) e.nextElement();

			h = (ColumbaHeader) headerList.getHeader(uid);

			saveHeader(p, h);
		}

		closeOutputStream();
	}

	/* (non-Javadoc)
	 * @see org.columba.mail.folder.headercache.AbstractHeaderCache#loadHeader(java.io.ObjectInputStream, org.columba.mail.message.HeaderInterface)
	 */
	protected void loadHeader(ObjectInputStream p, HeaderInterface h)
		throws Exception {

		Object uid = p.readObject();
		h.set("columba.uid", uid);
		super.loadHeader(p, h);
	}

	/* (non-Javadoc)
	 * @see org.columba.mail.folder.headercache.AbstractHeaderCache#saveHeader(java.io.ObjectOutputStream, org.columba.mail.message.HeaderInterface)
	 */
	protected void saveHeader(ObjectOutputStream p, HeaderInterface h)
		throws Exception {

		p.writeObject(h.get("columba.uid"));

		super.saveHeader(p, h);
	}
}