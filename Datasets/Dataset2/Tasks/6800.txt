if( e.getResponse() != null && e.getResponse().isERR() ) {

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
package org.columba.mail.pop3;

import java.io.File;
import java.io.IOException;
import java.util.Date;
import java.util.Enumeration;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;
import java.util.logging.Logger;

import org.columba.core.command.CommandCancelledException;
import org.columba.core.command.StatusObservable;
import org.columba.core.util.ListTools;
import org.columba.core.util.Lock;
import org.columba.mail.config.AccountItem;
import org.columba.mail.config.PopItem;
import org.columba.mail.config.SpecialFoldersItem;
import org.columba.mail.folder.MessageFolder;
import org.columba.mail.folder.headercache.CachedHeaderfields;
import org.columba.mail.main.MailInterface;
import org.columba.mail.message.ColumbaHeader;
import org.columba.mail.message.ColumbaMessage;
import org.columba.mail.message.HeaderList;
import org.columba.ristretto.pop3.POP3Exception;


public class POP3Server {
	/** JDK 1.4+ logging framework logger, used for logging. */
	private static final Logger LOG = Logger
			.getLogger("org.columba.mail.folder.headercache");

	private static final long DAY_IN_MS = 24 * 60 * 60 * 1000;
	
	
    private AccountItem accountItem;
    private File file;
    private boolean alreadyLoaded;
    private POP3Store store;
    protected POP3HeaderCache headerCache;
    private Lock lock;
    
    /**
     * Dirty flag. If set to true, we have to save the headercache changes.
     * If set to false, nothing changed. Therefore no need to save the headercache.
     */
    private boolean cacheChanged;

    public POP3Server(AccountItem accountItem) {
        this.accountItem = accountItem;

        int uid = accountItem.getUid();

        file = new File(MailInterface.config.getPOP3Directory(),
                (new Integer(uid)).toString());

        PopItem item = accountItem.getPopItem();

        store = new POP3Store(item);

        headerCache = new POP3HeaderCache(this);

        lock = new Lock();
        
        setCacheChanged(false);
    }

    public void save() throws Exception {
    	// only save headercache if something changed
    	if ( isCacheChanged() )
    		headerCache.save();
    }

    public File getConfigFile() {
        return file;
    }

    public AccountItem getAccountItem() {
        return accountItem;
    }

    public MessageFolder getFolder() {
        SpecialFoldersItem foldersItem = accountItem.getSpecialFoldersItem();
        String inboxStr = foldersItem.get("inbox");

        int inboxInt = Integer.parseInt(inboxStr);

        MessageFolder f = (MessageFolder) MailInterface.treeModel.getFolder(inboxInt);

        return f;
    }

    public void logout() throws Exception {
        getStore().logout();
    }

    public void forceLogout() throws Exception {
        getStore().logout();
    }

    public List synchronize() throws Exception {
        // Get the uids from the headercache
        LinkedList headerUids = new LinkedList();
        Enumeration keys = headerCache.getHeaderList().keys();

        while (keys.hasMoreElements()) {
            headerUids.add(keys.nextElement());
        }

        // Get the list of the uids on the server
        List newUids = store.getUIDList();

        // substract the uids that we already downloaded ->
        // newUids contains all uids to fetch from the server
        ListTools.substract(newUids, headerUids);

        // substract the uids on the server from the downloaded uids ->
        // headerUids are the uids that have been removed from the server
        ListTools.substract(headerUids, store.getUIDList());

        Iterator it = headerUids.iterator();

        // update the cache 
        while (it.hasNext()) {
            headerCache.getHeaderList().remove(it.next());
            cacheChanged = true;
        }

        // return the uids that are new
        return newUids;
    }

    public void deleteMessage(Object uid) throws IOException, POP3Exception, CommandCancelledException {
        try {
			store.deleteMessage(uid);
		
	        headerCache.remove(uid);
	        
	        // set dirty flag
	        setCacheChanged(true);
        } catch (POP3Exception e) {
        	if( e.getResponse().isERR() ) {
        		// Message already deleted from server
        		headerCache.remove(uid);
        		setCacheChanged(true);
        	} else throw e;
		}
        
    }
    
    public void deleteMessagesOlderThan(Date date) throws IOException, POP3Exception, CommandCancelledException {
    	LOG.info("Removing message older than " + date);
    	HeaderList headerList = headerCache.getHeaderList();
    	Enumeration uids = headerList.keys();
    	while( uids.hasMoreElements() ) {
    		Object uid = uids.nextElement();
    		ColumbaHeader header = headerList.get(uid);
    		if( ((Date)header.get("columba.date")).before(date) ) {
    			deleteMessage(uid);
    			LOG.info("removed "+ uid + " from " + accountItem.getName());
    		}    		
    	}    	
    }
    
    public void cleanUpServer() throws IOException, POP3Exception, CommandCancelledException {
		PopItem item = getAccountItem().getPopItem();
		
		if( item.getBoolean("leave_messages_on_server", false) && item.getBoolean("remove_old_from_server", false)) {
			int days  = item.getInteger("older_than");
			long date = new Date().getTime();
			date -= days * DAY_IN_MS;
			
			deleteMessagesOlderThan(new Date(date));
		}
    }

    public int getMessageCount() throws Exception {
        return getStore().getMessageCount();
    }

    public ColumbaMessage getMessage(Object uid) throws Exception {
        ColumbaMessage message = getStore().fetchMessage(uid);

        if (message == null) {
            return null;
        }

        ColumbaHeader header = (ColumbaHeader) message.getHeader();

        // set the attachment flag
        String contentType = (String) header.get("Content-Type");

        header.set("columba.attachment", header.hasAttachments());
        header.getAttributes().put("columba.fetchstate", Boolean.TRUE);
        header.getAttributes().put("columba.accountuid",
            new Integer(accountItem.getInteger("uid")));

        // remove useless headers to save memory
        header = CachedHeaderfields.stripHeaders(header);
        
        headerCache.getHeaderList().add(header, uid);
        
        // set headercache dirty flag
        setCacheChanged(true);

        return message;
    }

    public int getMessageSize(Object uid) throws Exception {
        return store.getSize(uid);
    }

    public String getFolderName() {
        return accountItem.getName();
    }

    /**
 * Returns the store.
 *
 * @return POP3Store
 */
    public POP3Store getStore() {
        return store;
    }

    public StatusObservable getObservable() {
        return store.getObservable();
    }

    public boolean tryToGetLock(Object locker) {
        return lock.tryToGetLock(locker);
    }

    public void releaseLock(Object locker) {
        lock.release(locker);
    }
    
	/**
	 * @return Returns the hasChanged.
	 */
	public boolean isCacheChanged() {
		return cacheChanged;
	}
	/**
	 * @param hasChanged The hasChanged to set.
	 */
	private void setCacheChanged(boolean hasChanged) {
		this.cacheChanged = hasChanged;
	}
	
	/**
	 * Call this method if the underlying configuration changed.
	 */
	public void updateConfig() {
		 PopItem item = accountItem.getPopItem();

	     store = new POP3Store(item);
	}
}