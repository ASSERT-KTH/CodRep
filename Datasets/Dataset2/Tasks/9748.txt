import org.columba.mail.folder.MessageFolder;

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

import java.util.Arrays;
import java.util.Calendar;
import java.util.Date;
import java.util.Enumeration;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;
import java.util.logging.Logger;

import javax.swing.JOptionPane;

import org.columba.core.main.MainInterface;
import org.columba.core.util.ListTools;
import org.columba.mail.folder.DataStorageInterface;
import org.columba.mail.folder.Folder;
import org.columba.mail.folder.LocalFolder;
import org.columba.mail.message.ColumbaHeader;
import org.columba.mail.message.HeaderList;
import org.columba.mail.util.MailResourceLoader;
import org.columba.ristretto.message.Flags;
import org.columba.ristretto.message.Header;
import org.columba.ristretto.message.MessageFolderInfo;
import org.columba.ristretto.message.io.Source;
import org.columba.ristretto.parser.HeaderParser;


/**
 * Implementation of a local headercache facility, which is also able to resync
 * itself with the {@DataStorageInterface}.
 *
 * @author fdietz
 */
public class LocalHeaderCache extends AbstractFolderHeaderCache {

    /** JDK 1.4+ logging framework logger, used for logging. */
    private static final Logger LOG = Logger.getLogger("org.columba.mail.folder.headercache");

    private static final int WEEK = 1000 * 60 * 60 * 24 * 7;
    private boolean configurationChanged;

    public LocalHeaderCache(LocalFolder folder) {
        super(folder);

        configurationChanged = false;
    }

    public HeaderList getHeaderList() throws Exception {
        boolean needToRelease = false;

        // if there exists a ".header" cache-file
        //  try to load the cache
        if (!isHeaderCacheLoaded()) {
            if (headerFile.exists()) {
                try {
                    load();

                    if (needToSync(headerList.count())) {
                        sync();
                    }
                } catch (Exception e) {
                    sync();
                }
            } else {
                sync();
            }

            setHeaderCacheLoaded(true);
        }

        return headerList;
    }

    /*
     * (non-Javadoc)
     *
     * @see org.columba.mail.folder.headercache.AbstractHeaderCache#needToSync(int)
     */
    public boolean needToSync(int capacity) {
        int mcount = ((LocalFolder) folder).getDataStorageInstance()
                      .getMessageCount();

        if (capacity != mcount) {
            return true;
        }

        return false;
    }

    /**
     * @param worker
     * @throws Exception
     */
    public void load() throws Exception {
        LOG.fine("loading header-cache=" + headerFile);

        try {
            reader = new ObjectReader(headerFile);
        } catch (Exception e) {
            if (MainInterface.DEBUG) {
                e.printStackTrace();
            }
        }

        int capacity = ((Integer) reader.readObject()).intValue();
        LOG.fine("capacity=" + capacity);

        boolean needToRelease = false;

        int additionalHeaderfieldsCount = ((Integer) reader.readObject()).intValue();

        if (additionalHeaderfieldsCount != 0) {
            // user-defined headerfields found
            // -> read all keys from file
            for (int i = 0; i < additionalHeaderfieldsCount; i++) {
                additionalHeaderfields.add((String) reader.readObject());
            }
        }

        String[] userDefinedHeaders = CachedHeaderfields.getUserDefinedHeaderfields();

        if ((userDefinedHeaders != null)
                && (userDefinedHeaders.length >= additionalHeaderfieldsCount)) {
            configurationChanged = true;
        }

        headerList = new HeaderList(capacity);

        //System.out.println("Number of Messages : " + capacity);
        if (getObservable() != null) {
            getObservable().setMessage(folder.getName() + ": "
                    + MailResourceLoader.getString("statusbar", "message",
                             "load_headers"));
            getObservable().setMax(capacity);
            getObservable().resetCurrent(); // setCurrent(0)
        }

        int nextUid = -1;

        // exists/unread/recent should be set to 0
        folder.setMessageFolderInfo(new MessageFolderInfo());

        for (int i = 0; i < capacity; i++) {
            if ((getObservable() != null) && ((i % 100) == 0)) {
                getObservable().setCurrent(i);
            }

            ColumbaHeader h = createHeaderInstance();

            loadHeader(h);

            headerList.add(h, (Integer) h.get("columba.uid"));

            if (h.getFlags().getRecent()) {
                folder.getMessageFolderInfo().incRecent();
            }

            if (!h.getFlags().getSeen()) {
                folder.getMessageFolderInfo().incUnseen();
            }

            folder.getMessageFolderInfo().incExists();

            int aktUid = ((Integer) h.get("columba.uid")).intValue();

            if (nextUid < aktUid) {
                nextUid = aktUid;
            }
        }

        /*
        // Check if the count of the
        if (needToSync(capacity)) {
            ColumbaLogger.log.fine(
            "need to recreateHeaderList() because capacity is not matching");

            throw new FolderInconsistentException();
        }
        */
        nextUid++;
        LOG.info("next UID for new messages =" + nextUid);
        ((LocalFolder) folder).setNextMessageUid(nextUid);

        reader.close();

        if (configurationChanged) {
            // headerfield cache configuration changed
            // -> try to properly fill the cache again
            reorganizeCache();
        }

        // we are done
        if (getObservable() != null) {
            getObservable().clearMessageWithDelay();
            getObservable().resetCurrent();
        }
    }

    /**
     * @param worker
     * @throws Exception
     */
    public void save() throws Exception {
        // we didn't load any header to save
        if (!isHeaderCacheLoaded()) {
            return;
        }

        LOG.fine("saving header-cache=" + headerFile);

        // this has to called only if the uid becomes higher than Integer
        // allows
        //cleanUpIndex();
        try {
            writer = new ObjectWriter(headerFile);
        } catch (Exception e) {
            if (MainInterface.DEBUG) {
                e.printStackTrace();
            }
        }

        // write total number of headers to file
        int count = headerList.count();
        LOG.fine("capacity=" + count);
        writer.writeObject(new Integer(count));

        // write keys of user specified headerfields in file
        // -> this allows a much more failsafe handling, when
        // -> users add/remove headerfields from the cache
        String[] userDefinedHeaderFields = CachedHeaderfields.getUserDefinedHeaderfields();

        if (userDefinedHeaderFields != null) {
            // write number of additional headerfields to file
            writer.writeObject(new Integer(userDefinedHeaderFields.length));

            // write keys to file
            for (int i = 0; i < userDefinedHeaderFields.length; i++) {
                writer.writeObject(userDefinedHeaderFields[i]);
            }
        } else {
            // no additionally headerfields
            writer.writeObject(new Integer(0));
        }

        ColumbaHeader h;

        //Message message;
        for (Enumeration e = headerList.keys(); e.hasMoreElements();) {
            Object uid = e.nextElement();

            h = (ColumbaHeader) headerList.get(uid);

            saveHeader(h);
        }

        writer.close();
    }

    /**
     * @param worker
     * @throws Exception
     */
    public void sync() throws Exception {
        if (getObservable() != null) {
            getObservable().setMessage(folder.getName()
                    + ": Syncing headercache...");
        }

        DataStorageInterface ds = ((LocalFolder) folder).getDataStorageInstance();

        Object[] uids = ds.getMessageUids();

        HeaderList oldHeaderList = headerList;

        headerList = new HeaderList(uids.length);

        Date today = Calendar.getInstance().getTime();

        // parse all message files to recreate the header cache
        ColumbaHeader header = null;
        MessageFolderInfo messageFolderInfo = folder.getMessageFolderInfo();
        messageFolderInfo.setExists(0);
        messageFolderInfo.setRecent(0);
        messageFolderInfo.setUnseen(0);

        folder.setChanged(true);

        if (getObservable() != null) {
            getObservable().setMax(uids.length);
        }

        for (int i = 0; i < uids.length; i++) {
            if ((oldHeaderList != null) && oldHeaderList.containsKey(uids[i])) {
                header = oldHeaderList.get(uids[i]);
                headerList.add(header, uids[i]);
            } else {
                try {
                    Source source = ds.getMessageSource(uids[i]);

                    if (source.length() == 0) {
                        ds.removeMessage(uids[i]);

                        continue;
                    }

                    header = new ColumbaHeader(HeaderParser.parse(source));

                    header = CachedHeaderfields.stripHeaders(header);

                    if (isOlderThanOneWeek(today,
                                ((Date) header.getAttributes().get("columba.date")))) {
                        header.getFlags().set(Flags.SEEN);
                    }

                    int size = source.length() >> 10; // Size in KB
                    header.set("columba.size", new Integer(size));

                    // set the attachment flag
                    String contentType = (String) header.get("Content-Type");

                    header.set("columba.attachment", header.hasAttachments());

                    header.set("columba.uid", uids[i]);

                    headerList.add(header, uids[i]);

                    source = null;
                } catch (Exception ex) {
                    ex.printStackTrace();
                    LOG.severe("Error syncing HeaderCache :" + ex.getLocalizedMessage());
                }
            }
            
            

            if (header.get("columba.flags.recent").equals(Boolean.TRUE)) {
                messageFolderInfo.incRecent();
            }

            if (header.get("columba.flags.seen").equals(Boolean.FALSE)) {
                messageFolderInfo.incUnseen();
            }
            

            header = null;

            
            messageFolderInfo.incExists();
            
            
            ((LocalFolder) folder).setNextMessageUid(((Integer) uids[uids.length
                                                                     - 1]).intValue() + 1);

            if ((getObservable() != null) && ((i % 100) == 0)) {
                getObservable().setCurrent(i);
            }
        }

        // we are done
        if (getObservable() != null) {
            getObservable().resetCurrent();
        }
    }

    protected void loadHeader(ColumbaHeader h) throws Exception {
        h.set("columba.uid", reader.readObject());

        super.loadHeader(h);
    }

    protected void saveHeader(ColumbaHeader h) throws Exception {
        writer.writeObject(h.get("columba.uid"));

        super.saveHeader(h);
    }

    public boolean isOlderThanOneWeek(Date arg0, Date arg1) {
        return (arg0.getTime() - WEEK) > arg1.getTime();
    }

    /**
     * Method tries to fill the headercache with proper values.
     * <p>
     * This is needed after the user changed the headerfield caching setup.
     *
     */
    protected void reorganizeCache() throws Exception {
        List list = new LinkedList(Arrays.asList(
                    CachedHeaderfields.getUserDefinedHeaderfields()));
        ListTools.substract(list, additionalHeaderfields);

        if (list.size() == 0) {
            return;
        }

        JOptionPane.showMessageDialog(null,
            "<html></body><p>Columba recognized that you just changed the headerfield caching setup."
                + " This makes it necessary to reorganize the cache and will take a bit longer than generally.</p></body></html>");

        DataStorageInterface ds = ((LocalFolder) folder).getDataStorageInstance();

        Object[] uids = ds.getMessageUids();
        Header helper;
        ColumbaHeader header;

        for (int i = 0; i < uids.length; i++) {
            header = (ColumbaHeader) headerList.get(uids[i]);

            Source source = ds.getMessageSource(uids[i]);

            if (source.length() == 0) {
                continue;
            }

            helper = HeaderParser.parse(source);
            source.close();

            Iterator it = list.iterator();

            while (it.hasNext()) {
                String h = (String) it.next();
                header.set(h, helper.get(h));
            }
        }
    }
}