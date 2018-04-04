public void removeMessage(Object uid) throws Exception {

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

package org.columba.mail.folder.temp;

import java.io.File;
import java.io.InputStream;
import java.util.Hashtable;
import java.util.logging.Logger;

import org.columba.core.command.WorkerStatusController;
import org.columba.core.io.DiskIO;
import org.columba.mail.config.FolderItem;
import org.columba.mail.filter.Filter;
import org.columba.mail.folder.HeaderListStorage;
import org.columba.mail.folder.MailboxInterface;
import org.columba.mail.folder.MessageFolder;
import org.columba.mail.folder.search.DefaultSearchEngine;
import org.columba.mail.message.ColumbaHeader;
import org.columba.mail.message.ColumbaMessage;
import org.columba.mail.message.HeaderList;
import org.columba.ristretto.io.SourceInputStream;
import org.columba.ristretto.io.TempSourceFactory;
import org.columba.ristretto.message.Attributes;
import org.columba.ristretto.message.Flags;
import org.columba.ristretto.message.Header;
import org.columba.ristretto.message.LocalMimePart;
import org.columba.ristretto.message.Message;
import org.columba.ristretto.message.MimePart;
import org.columba.ristretto.message.MimeTree;
import org.columba.ristretto.parser.MessageParser;

/**
 * @author freddy
 */
public class TempFolder extends MessageFolder {

    /** JDK 1.4+ logging framework logger, used for logging. */
    private static final Logger LOG = Logger.getLogger("org.columba.mail.folder.temp");

    protected HeaderList headerList;
    protected Hashtable messageList;
    protected int nextUid = 0;
    protected ColumbaMessage aktMessage;

    /**
     * Constructor for TempFolder.
     *
     * @param path                example: /home/donald/mail/
     */
    public TempFolder(String path) {
        super();

        String dir = path + "temp";

        if (DiskIO.ensureDirectory(dir)) {
            directoryFile = new File(dir);
        }

        headerList = new HeaderList();
        messageList = new Hashtable();
        
        setSearchEngine(new DefaultSearchEngine(this));
    }

    public void clear() {
        headerList.clear();
        messageList.clear();
    }

    public Object[] getUids() throws Exception {
        return messageList.keySet().toArray();
    }

    protected Object generateNextUid() {
        return new Integer(nextUid++);
    }

    public void setNextUid(int next) {
        nextUid = next;
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
    public HeaderList getHeaderList() throws Exception {
        return headerList;
    }


    /**
     * @see org.columba.modules.mail.folder.Folder#removeMessage(Object)
     */
    protected void removeMessage(Object uid) throws Exception {
        
        Flags flags = getFlags(uid);
        
        fireMessageRemoved(uid, flags);
               
        headerList.remove(uid);
        messageList.remove(uid);
       
        
    }

    /**
     * @see org.columba.modules.mail.folder.Folder#getMimePart(Object,
     *      Integer[], WorkerStatusController)
     * @TODO dont use deprecated method
     */
    public MimePart getMimePart(Object uid, Integer[] address)
        throws Exception {
        ColumbaMessage message = (ColumbaMessage) messageList.get(uid);

        MimePart mimePart = message.getMimePartTree().getFromAddress(address);

        return mimePart;
    }

    /**
     * @see org.columba.modules.mail.folder.Folder#getMimeTree(Object,
     *      WorkerStatusController)
     */
    public MimeTree getMimePartTree(Object uid) throws Exception {
        return ((ColumbaMessage) messageList.get(uid)).getMimePartTree();
    }

    /**
     * @see org.columba.modules.mail.folder.Folder#getMessageHeader(Object,
     *      WorkerStatusController)
     * @TODO dont use deprecated method
     */
    public ColumbaHeader getMessageHeader(Object uid) throws Exception {
        ColumbaHeader header = (ColumbaHeader) headerList.get(uid);

        return header;
    }

    /**
     * @see org.columba.modules.mail.folder.Folder#getMessage(Object,
     *      WorkerStatusController)
     */
    public ColumbaMessage getMessage(Object uid) throws Exception {
        ColumbaMessage message = (ColumbaMessage) messageList.get(uid);

        return message;
    }

    /**
     * @see org.columba.modules.mail.folder.Folder#searchMessages(Filter,
     *      Object[], WorkerStatusController)
     */
    public Object[] searchMessages(Filter filter, Object[] uids)
        throws Exception {
        return getSearchEngine().searchMessages(filter, uids);
    }

    /**
     * @see org.columba.modules.mail.folder.Folder#searchMessages(Filter,
     *      WorkerStatusController)
     */
    public Object[] searchMessages(Filter filter) throws Exception {
        return getSearchEngine().searchMessages(filter);
    }

    /**
     * @see org.columba.modules.mail.folder.FolderTreeNode#instanceNewChildNode(AdapterNode,
     *      FolderItem)
     */
    public String getDefaultChild() {
        return null;
    }

    public String getName() {
        return toString();
    }

    public String toString() {
        return (String) getUserObject();
    }

    // TODO: Do we need this implementation in a TempFolder?
    // If not, just put an empty method here, just like in VirtualFolder.
    public void innerCopy(MailboxInterface destFolder, Object[] uids)
        throws Exception {
        for (int i = 0; i < uids.length; i++) {

            InputStream messageSourceStream = getMessageSourceStream(uids[i]);
            destFolder.addMessage(messageSourceStream);
            messageSourceStream.close();
        }
    }

    public Object addMessage(InputStream in, Attributes attributes, Flags flags)
        throws Exception {

        Message message = MessageParser.parse(
                TempSourceFactory.createTempSource(in, -1));

        Object newUid = generateNextUid();

        LOG.info("new UID=" + newUid);

        ColumbaHeader h = new ColumbaHeader(message.getHeader());

        if (attributes != null) {
            h.setAttributes((Attributes) attributes.clone());
        }
        
        if ( flags != null ) {
            h.setFlags((Flags) flags.clone());
        }

        h.set("columba.uid", newUid);

        headerList.add(h, newUid);

        messageList.put(newUid, new ColumbaMessage(h, message));

        fireMessageAdded(newUid);
        return newUid;
    }

    /*
     * (non-Javadoc)
     *
     * @see org.columba.mail.folder.MailboxInterface#getAttribute(java.lang.Object,
     *      java.lang.String)
     */
    public Object getAttribute(Object uid, String key)
        throws Exception {
        return ((ColumbaHeader) headerList.get(uid)).getAttributes().get(key);
    }

    /*
     * (non-Javadoc)
     *
     * @see org.columba.mail.folder.MailboxInterface#getFlags(java.lang.Object)
     */
    public Flags getFlags(Object uid) throws Exception {
        return ((ColumbaHeader) headerList.get(uid)).getFlags();
    }

    public Attributes getAttributes(Object uid) throws Exception {
        if (getHeaderList().containsKey(uid)) {
            return getHeaderList().get(uid).getAttributes();
        } else {
            return null;
        }
    }

    /*
     * (non-Javadoc)
     *
     * @see org.columba.mail.folder.MailboxInterface#getHeaderFields(java.lang.Object,
     *      java.lang.String[])
     */
    public Header getHeaderFields(Object uid, String[] keys)
        throws Exception {
        ColumbaHeader header = ((ColumbaMessage) messageList.get(uid)).getHeader();

        Header subHeader = new Header();
        String value;

        for (int i = 0; i < keys.length; i++) {
            value = (String) header.get(keys[i]);

            if (value != null) {
                subHeader.set(keys[i], value);
            }
        }

        return subHeader;
    }

    /*
     * (non-Javadoc)
     *
     * @see org.columba.mail.folder.MailboxInterface#getMessageSourceStream(java.lang.Object)
     */
    public InputStream getMessageSourceStream(Object uid)
        throws Exception {
        return new SourceInputStream(((ColumbaMessage) messageList.get(uid)).getSource());
    }

    /*
     * (non-Javadoc)
     *
     * @see org.columba.mail.folder.MailboxInterface#getMimePartBodyStream(java.lang.Object,
     *      java.lang.Integer[])
     */
    public InputStream getMimePartBodyStream(Object uid, Integer[] address)
        throws Exception {
        ColumbaMessage message = (ColumbaMessage) messageList.get(uid);

        LocalMimePart mimepart = (LocalMimePart) message.getMimePartTree()
                                                        .getFromAddress(address);

        return mimepart.getInputStream();
    }

    /*
     * (non-Javadoc)
     *
     * @see org.columba.mail.folder.MailboxInterface#getMimePartSourceStream(java.lang.Object,
     *      java.lang.Integer[])
     */
    public InputStream getMimePartSourceStream(Object uid, Integer[] address)
        throws Exception {
        ColumbaMessage message = (ColumbaMessage) messageList.get(uid);

        LocalMimePart mimepart = (LocalMimePart) message.getMimePartTree()
                                                        .getFromAddress(address);

        return new SourceInputStream(mimepart.getSource());
    }

    public void setAttribute(Object uid, String key, Object value)
        throws Exception {
        // get header with UID
        ColumbaHeader header = (ColumbaHeader) getHeaderList().get(uid);

        header.getAttributes().put(key, value);
    }

    /* (non-Javadoc)
     * @see org.columba.mail.folder.MailboxInterface#addMessage(java.io.InputStream, org.columba.ristretto.message.Attributes)
     */
    public Object addMessage(InputStream in) throws Exception {
        return addMessage(in, null, null);
    }
    
    /**
     * @see org.columba.modules.mail.folder.Folder#addMessage(AbstractMessage,
     *      WorkerStatusController)
     */
    public Object addMessage(ColumbaMessage message) throws Exception {
        Object newUid = generateNextUid();

        ColumbaHeader h = (ColumbaHeader) ((ColumbaHeader) message.getHeader());

        h.set("columba.uid", newUid);

        headerList.add(h, newUid);

        messageList.put(newUid, message);

        return newUid;
    }
    
    /**
     * @see org.columba.mail.folder.Folder#getHeaderListStorage()
     */
    public HeaderListStorage getHeaderListStorage() {
        
        return null;
    }
	/**
	 * @see org.columba.mail.folder.AbstractFolder#removeFolder()
	 */
	public void removeFolder() throws Exception {
		//super.removeFolder();
		// do nothing
	}
}