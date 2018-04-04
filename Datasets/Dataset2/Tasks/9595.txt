fireMessageAdded(newUid, getFlags(newUid));

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

import org.columba.api.command.IWorkerStatusController;
import org.columba.core.filter.Filter;
import org.columba.core.io.DiskIO;
import org.columba.mail.config.FolderItem;
import org.columba.mail.folder.AbstractMessageFolder;
import org.columba.mail.folder.IMailbox;
import org.columba.mail.folder.headercache.HeaderList;
import org.columba.mail.folder.imap.IMAPFolder;
import org.columba.mail.folder.search.DefaultSearchEngine;
import org.columba.mail.message.ColumbaHeader;
import org.columba.mail.message.ColumbaMessage;
import org.columba.mail.message.IColumbaHeader;
import org.columba.mail.message.IColumbaMessage;
import org.columba.mail.message.IHeaderList;
import org.columba.ristretto.io.SourceInputStream;
import org.columba.ristretto.io.TempSourceFactory;
import org.columba.ristretto.message.Attributes;
import org.columba.ristretto.message.Flags;
import org.columba.ristretto.message.Header;
import org.columba.ristretto.message.LocalMimePart;
import org.columba.ristretto.message.Message;
import org.columba.ristretto.message.MimeTree;
import org.columba.ristretto.parser.MessageParser;

/**
 * @author freddy
 */
public class TempFolder extends AbstractMessageFolder {

    /** JDK 1.4+ logging framework logger, used for logging. */
    private static final Logger LOG = Logger.getLogger("org.columba.mail.folder.temp");

    protected IHeaderList headerList;
    protected Hashtable messageList;
    protected int nextUid = 0;
    protected IColumbaMessage aktMessage;

    /**
     * Constructor for TempFolder.
     *
     * @param path                example: /home/donald/mail/
     */
    public TempFolder(String path) {
        super("temp-folder-name", "temp", path);

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
     * @see org.columba.modules.mail.folder.Folder#getHeaderList(IWorkerStatusController)
     */
    public IHeaderList getHeaderList() throws Exception {
        return headerList;
    }


    /**
     * @see org.columba.modules.mail.folder.Folder#remove(Object)
     */
    public void removeMessage(Object uid) throws Exception {
        
        Flags flags = getFlags(uid);
        
        fireMessageRemoved(uid, flags);
               
        headerList.remove(uid);
        messageList.remove(uid);
       
        
    }

   

    /**
     * @see org.columba.modules.mail.folder.Folder#getMimeTree(Object,
     *      IMAPFolder)
     */
    public MimeTree getMimePartTree(Object uid) throws Exception {
        return ((IColumbaMessage) messageList.get(uid)).getMimePartTree();
    }

    /**
     * @see org.columba.modules.mail.folder.Folder#getMessageHeader(Object,
     *      IWorkerStatusController)
     * @TODO dont use deprecated method
     */
    public IColumbaHeader getMessageHeader(Object uid) throws Exception {
        ColumbaHeader header = (ColumbaHeader) headerList.get(uid);

        return header;
    }

    /**
     * @see org.columba.modules.mail.folder.Folder#getMessage(Object,
     *      IWorkerStatusController)
     */
    public IColumbaMessage getMessage(Object uid) throws Exception {
        IColumbaMessage message = (IColumbaMessage) messageList.get(uid);

        return message;
    }

    /**
     * @see org.columba.modules.mail.folder.Folder#searchMessages(Filter,
     *      Object[], IWorkerStatusController)
     */
    public Object[] searchMessages(Filter filter, Object[] uids)
        throws Exception {
        return getSearchEngine().searchMessages(filter, uids);
    }

    /**
     * @see org.columba.modules.mail.folder.Folder#searchMessages(Filter,
     *      IWorkerStatusController)
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

    // FIXME (@author fdietz): Do we need this implementation in a TempFolder?
    // If not, just put an empty method here, just like in VirtualFolder.
    public void innerCopy(IMailbox destFolder, Object[] uids)
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

        h.getAttributes().put("columba.uid", newUid);

        headerList.add(h, newUid);

        messageList.put(newUid, new ColumbaMessage(h, message));

        fireMessageAdded(newUid);
        return newUid;
    }

    /*
     * (non-Javadoc)
     *
     * @see org.columba.mail.folder.IMailbox#getAttribute(java.lang.Object,
     *      java.lang.String)
     */
    public Object getAttribute(Object uid, String key)
        throws Exception {
        return ((ColumbaHeader) headerList.get(uid)).getAttributes().get(key);
    }

    /*
     * (non-Javadoc)
     *
     * @see org.columba.mail.folder.IMailbox#getFlags(java.lang.Object)
     */
    public Flags getFlags(Object uid) throws Exception {
        return ((ColumbaHeader) headerList.get(uid)).getFlags();
    }

    public Attributes getAttributes(Object uid) throws Exception {
        if (getHeaderList().exists(uid)) {
            return getHeaderList().get(uid).getAttributes();
        } else {
            return null;
        }
    }

    /*
     * (non-Javadoc)
     *
     * @see org.columba.mail.folder.IMailbox#getHeaderFields(java.lang.Object,
     *      java.lang.String[])
     */
    public Header getHeaderFields(Object uid, String[] keys)
        throws Exception {
        IColumbaHeader header = ((IColumbaMessage) messageList.get(uid)).getHeader();

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
     * @see org.columba.mail.folder.IMailbox#getMessageSourceStream(java.lang.Object)
     */
    public InputStream getMessageSourceStream(Object uid)
        throws Exception {
        return new SourceInputStream(((IColumbaMessage) messageList.get(uid)).getSource());
    }

    /*
     * (non-Javadoc)
     *
     * @see org.columba.mail.folder.IMailbox#getMimePartBodyStream(java.lang.Object,
     *      java.lang.Integer[])
     */
    public InputStream getMimePartBodyStream(Object uid, Integer[] address)
        throws Exception {
        IColumbaMessage message = (IColumbaMessage) messageList.get(uid);

        LocalMimePart mimepart = (LocalMimePart) message.getMimePartTree()
                                                        .getFromAddress(address);

        return mimepart.getInputStream();
    }

    /*
     * (non-Javadoc)
     *
     * @see org.columba.mail.folder.IMailbox#getMimePartSourceStream(java.lang.Object,
     *      java.lang.Integer[])
     */
    public InputStream getMimePartSourceStream(Object uid, Integer[] address)
        throws Exception {
        IColumbaMessage message = (IColumbaMessage) messageList.get(uid);

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
     * @see org.columba.mail.folder.IMailbox#addMessage(java.io.InputStream, org.columba.ristretto.message.Attributes)
     */
    public Object addMessage(InputStream in) throws Exception {
        return addMessage(in, null, null);
    }
    
    /**
     * @see org.columba.modules.mail.folder.Folder#addMessage(AbstractMessage,
     *      IWorkerStatusController)
     */
    public Object addMessage(IColumbaMessage message) throws Exception {
        Object newUid = generateNextUid();

        ColumbaHeader h = (ColumbaHeader) ((ColumbaHeader) message.getHeader());

        h.getAttributes().put("columba.uid", newUid);

        headerList.add(h, newUid);

        messageList.put(newUid, message);

        return newUid;
    }
    
	/**
	 * @see org.columba.mail.folder.AbstractFolder#removeFolder()
	 */
	public void removeFolder() throws Exception {
		//super.removeFolder();
		// do nothing
	}

	/**
	 * @see org.columba.mail.folder.IMailbox#getAllHeaderFields(java.lang.Object)
	 */
	public Header getAllHeaderFields(Object uid) throws Exception {
		IColumbaHeader header = ((IColumbaMessage) messageList.get(uid)).getHeader();
		
		return header.getHeader();
	}
}