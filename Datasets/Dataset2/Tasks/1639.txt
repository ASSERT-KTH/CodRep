h.set(columnNames[j], Boolean.valueOf(p.readBoolean()));

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

import java.io.BufferedInputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.util.Date;

import org.columba.core.logging.ColumbaLogger;
import org.columba.core.util.BooleanCompressor;
import org.columba.mail.message.ColumbaHeader;
import org.columba.mail.message.HeaderList;
import org.columba.ristretto.message.HeaderInterface;

/**
 * Provides basic support for saving and loading email headers as
 * fast as possible.
 * <p>
 * It therefor tries to compress the data to make it as small as possible,
 * which improves performance dramatically
 * 
 * @author fdietz
 */
public abstract class AbstractHeaderCache {

	protected HeaderList headerList;

	protected File headerFile;

	private boolean headerCacheLoaded;

	protected String[] columnNames;

	private static final int NULL = 0;
	private static final int STRING = 1;
	private static final int DATE = 2;
	private static final int BOOLEAN = 3;
	private static final int INTEGER = 4;

	FileOutputStream ostream;
	ObjectOutputStream oos;

	FileInputStream istream;
	ObjectInputStream ois;

	/**
	 * @param folder
	 */
	public AbstractHeaderCache(File headerFile) {
		this.headerFile = headerFile;

		headerList = new HeaderList();

		headerCacheLoaded = false;

		columnNames = null;
	}

	protected void loadColumnNames() {
		if (columnNames == null) {
			columnNames = CachedHeaderfieldOwner.getCachedHeaderfieldArray();
		}
	}

	/**
	 * @return
	 */
	public HeaderInterface createHeaderInstance() {
		return new ColumbaHeader();
	}

	/**
	 * @return
	 */
	public boolean isHeaderCacheLoaded() {
		return headerCacheLoaded;
	}

	/**
	 * @param uid
	 * @return
	 * @throws Exception
	 */
	public boolean exists(Object uid) throws Exception {
		return headerList.contains(uid);
	}

	/**
	 * @return
	 */
	public int count() {
		return headerList.size();
	}

	/**
	 * @param uid
	 * @throws Exception
	 */
	public void remove(Object uid) throws Exception {
		ColumbaLogger.log.debug("trying to remove message UID=" + uid);

		if (headerList.containsKey(uid)) {
			ColumbaLogger.log.debug("remove UID=" + uid);

			headerList.remove(uid);
		}
	}

	/**
	 * @param header
	 * @throws Exception
	 */
	public void add(HeaderInterface header) throws Exception {
		headerList.add(header, header.get("columba.uid"));
	}

	/** Get or (re)create the header cache file.
	 *
	 * @return the HeaderList
	 * @throws Exception
	 */
	public HeaderList getHeaderList()
		throws Exception {
		boolean needToRelease = false;
		// if there exists a ".header" cache-file
		//  try to load the cache	
		if (!headerCacheLoaded) {

			if (headerFile.exists()) {
				try {
					load();
				} catch (Exception e) {
					e.printStackTrace();

					headerCacheLoaded = true;
					headerList = new HeaderList();

					return headerList;
				}
			}

			headerCacheLoaded = true;
		}

		return headerList;
	}

	/**

	 * @throws Exception
	 */
	public abstract void load() throws Exception;

	/**

	 * @throws Exception
	 */
	public abstract void save() throws Exception;
	/**
	 * @param p
	 * @param h
	 * @throws Exception
	 */
	protected void loadAdditionalHeader(ObjectInputStream p, HeaderInterface h)
		throws Exception {
	}

	/**
	 * @param p
	 * @param h
	 * @throws Exception
	 */
	protected void saveAditionalHeader(ObjectInputStream p, HeaderInterface h)
		throws Exception {
	}

	protected void loadHeader(ObjectInputStream p, HeaderInterface h)
		throws Exception {

		int compressedFlags = p.readInt();
		h.set(
			"columba.flags.seen",
			BooleanCompressor.decompress(compressedFlags, 0));
		h.set(
			"columba.flags.answered",
			BooleanCompressor.decompress(compressedFlags, 1));
		h.set(
			"columba.flags.flagged",
			BooleanCompressor.decompress(compressedFlags, 2));
		h.set(
			"columba.flags.expunged",
			BooleanCompressor.decompress(compressedFlags, 3));
		h.set(
			"columba.flags.draft",
			BooleanCompressor.decompress(compressedFlags, 4));
		h.set(
			"columba.flags.recent",
			BooleanCompressor.decompress(compressedFlags, 5));
		h.set(
			"columba.attachment",
			BooleanCompressor.decompress(compressedFlags, 6));

		h.set("columba.date", new Date(p.readLong()));

		h.set("columba.size", new Integer(p.readInt()));

		h.set("columba.from", p.readObject());

		h.set("columba.priority", new Integer(p.readInt()));

		h.set("columba.host", p.readUTF());

		h.set("columba.subject", p.readUTF());

		loadColumnNames();

		int classCode;
		for (int j = 0; j < columnNames.length; j++) {
			classCode = p.readInt();

			switch (classCode) {
				case NULL :
					{
						break;
					}
				case STRING :
					{
						h.set(columnNames[j], p.readUTF());
						break;
					}

				case INTEGER :
					{
						h.set(columnNames[j], new Integer(p.readInt()));
						break;
					}

				case BOOLEAN :
					{
						h.set(columnNames[j], new Boolean(p.readBoolean()));
						break;
					}

				case DATE :
					{
						h.set(columnNames[j], new Date(p.readLong()));
						break;
					}
			}
		}

	}

	protected void saveHeader(ObjectOutputStream p, HeaderInterface h)
		throws Exception {

		p.writeInt(
			BooleanCompressor.compress(
				new Boolean[] {
					(Boolean) h.get("columba.flags.seen"),
					(Boolean) h.get("columba.flags.answered"),
					(Boolean) h.get("columba.flags.flagged"),
					(Boolean) h.get("columba.flags.expunged"),
					(Boolean) h.get("columba.flags.draft"),
					(Boolean) h.get("columba.flags.recent"),
					(Boolean) h.get("columba.attachment")}));

		p.writeLong(((Date) h.get("columba.date")).getTime());

		p.writeInt(((Integer) h.get("columba.size")).intValue());
		
		p.writeObject( h.get("columba.from") );

		p.writeInt(((Integer) h.get("columba.priority")).intValue());

		p.writeUTF((String) h.get("columba.host"));
		
		p.writeUTF((String) h.get("columba.subject"));

		loadColumnNames();

		Object o;
		for (int j = 0; j < columnNames.length; j++) {
			o = h.get(columnNames[j]);
			if (o == null) {
				p.writeInt(NULL);
			} else if (o instanceof String) {
				p.writeInt(STRING);
				p.writeUTF((String) o);
			} else if (o instanceof Integer) {
				p.writeInt(INTEGER);
				p.writeInt(((Integer) o).intValue());
			} else if (o instanceof Boolean) {
				p.writeInt(BOOLEAN);
				p.writeBoolean(((Boolean) o).booleanValue());
			} else if (o instanceof Date) {
				p.writeInt(DATE);
				p.writeLong(((Date) o).getTime());
			}

		}
	}

	public ObjectInputStream openInputStream() throws Exception {
		istream = new FileInputStream(headerFile.getPath());
		ois = new ObjectInputStream(new BufferedInputStream(istream));
		return ois;
	}

	public ObjectOutputStream openOutputStream() throws Exception {
		ostream = new FileOutputStream(headerFile.getPath());
		oos = new ObjectOutputStream(ostream);

		return oos;
	}

	public void closeInputStream() throws Exception {

		ois.close();
		istream.close();
	}

	public void closeOutputStream() throws Exception {

		oos.close();
		ostream.close();
	}

	/**
	 * @param b
	 */
	public void setHeaderCacheLoaded(boolean b) {
		headerCacheLoaded = b;
	}

}