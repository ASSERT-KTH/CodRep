public DefaultSearchEngine getSearchEngine() {

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

package org.columba.mail.folder.imap;

import java.io.InputStream;
import java.util.*;
import java.util.logging.Logger;

import org.columba.core.command.StatusObservable;
import org.columba.core.io.StreamUtils;
import org.columba.core.util.ListTools;
import org.columba.core.xml.XmlElement;
import org.columba.mail.config.FolderItem;
import org.columba.mail.config.ImapItem;
import org.columba.mail.folder.*;
import org.columba.mail.folder.headercache.CachedHeaderfields;
import org.columba.mail.folder.headercache.RemoteHeaderListStorage;
import org.columba.mail.folder.search.DefaultSearchEngine;
import org.columba.mail.folder.search.IMAPQueryEngine;
import org.columba.mail.imap.IMAPStore;
import org.columba.mail.message.ColumbaHeader;
import org.columba.mail.message.ColumbaMessage;
import org.columba.mail.message.HeaderList;
import org.columba.mail.util.MailResourceLoader;
import org.columba.ristretto.imap.IMAPFlags;
import org.columba.ristretto.message.*;
import org.columba.ristretto.message.io.Source;
import org.columba.ristretto.message.io.SourceInputStream;

public class IMAPFolder extends RemoteFolder {

    /** JDK 1.4+ logging framework logger, used for logging. */
    private static final Logger LOG = Logger.getLogger("org.columba.mail.folder.imap");

    /**
     *
     */
    private ImapItem item;

    //private boolean select=false;
    //private boolean fetch=false;
    //private StringBuffer cache;
    private Object aktMessageUid;

    /**
     *
     */
    private ColumbaMessage aktMessage;

    /**
     *
     */
    private boolean mailcheck = false;

    /**
     *
     */
    private IMAPStore store;

    /**
     *
     */
    protected HeaderList headerList;

    /**
     *
     */
    protected boolean existsOnServer = true;

    /**
     *
     */
    private HeaderListStorage attributeStorage;

    /**
     * @see org.columba.mail.folder.FolderTreeNode#FolderTreeNode(org.columba.mail.config.FolderItem)
     */
    public IMAPFolder(FolderItem folderItem, String path) {
        super(folderItem, path);

        DefaultSearchEngine engine = new DefaultSearchEngine(this);
        engine.setNonDefaultEngine(new IMAPQueryEngine(this));
        setSearchEngine(engine);

        //setChanged(true);
    }

    /**
     * @param type
     */
    public IMAPFolder(String name, String type, String path) throws Exception {
        super(name, type, path);

        FolderItem item = getConfiguration();
        item.set("property", "accessrights", "user");
        item.set("property", "subfolder", "true");
    }

    /**
     * @see org.columba.mail.folder.FolderTreeNode#removeFolder()
     */
    public void removeFolder() throws Exception {
        if (existsOnServer) {
            String path = getImapPath();

            boolean result = getStore().deleteFolder(path);

            if (!result) { return; }
        }

        super.removeFolder();
    }

    public void setName(String name) {
        if(getName() == null) {  // if creating new folder
            super.setName(name);
            return;
        }
        
        try {
            String oldPath = getImapPath();
            LOG.info("old path=" + oldPath);

            String newPath = null;

            if (getParent() instanceof IMAPFolder) {
                newPath = ((IMAPFolder) getParent()).getImapPath();
            }

            newPath += (getStore().getDelimiter() + name);
            LOG.info("new path=" + newPath);

            if (getStore().renameFolder(oldPath, newPath)) {
                super.setName(name);
            }
        } catch (Exception e) {
            LOG.severe(e.getMessage());
        }
    }

    /**
     * Method getStore.
     *
     * @return IMAPStore
     */
    public IMAPStore getStore() {
        if (store == null) {
            store = ((IMAPRootFolder) getRootFolder()).getStore();
        }

        return store;
    }

    /**
     * @see org.columba.mail.folder.Folder#getHeaderList(org.columba.core.command.WorkerStatusController)
     */
    public HeaderList getHeaderList() throws Exception {
        //if (headerList == null) {
        headerList = super.getHeaderList();

        // if this is the first time we download
        // a headerlist -> we need to save headercache
        if (headerList.count() == 0) {
            changed = true;
        }

        getObservable().setMessage(
                MailResourceLoader.getString("statusbar", "message",
                        "fetch_uid_list"));

        List newList = getStore().fetchUIDList(getImapPath());

        if (newList == null) {
            return new HeaderList();
        }

        List result = synchronize(headerList, newList);

        getObservable().setMessage(
                MailResourceLoader.getString("statusbar", "message",
                        "fetch_flags_list"));

        Flags[] flags = getStore().fetchFlagsList(getImapPath());

        getObservable().setMessage(
                MailResourceLoader.getString("statusbar", "message",
                        "fetch_header_list"));

        // if available -> fetch new headers
        if (result.size() > 0) {
            getStore().fetchHeaderList(headerList, result, getImapPath());
        }

        messageFolderInfo = getStore().getSelectedFolderMessageFolderInfo();

        updateFlags(flags);

        // clear statusbar message
        getObservable().clearMessage();

        //}
        return headerList;
    }

    /**
     * Method updateFlags.
     *
     * @param flagsList
     */
    protected void updateFlags(Flags[] flagsList) {
        // ALP 04/29/03
        // Reset the number of seen/resent/existing messages. Otherwise you
        // just keep adding to the number.
        MessageFolderInfo info = getMessageFolderInfo();
        info.setExists(0);
        info.setRecent(0);
        info.setUnseen(0);

        // END ADDS ALP 04/29/03
        for (int i = 0; i < flagsList.length; i++) {
            IMAPFlags flags = (IMAPFlags) flagsList[i];

            Integer uid = (Integer) flags.getUid();

            ColumbaHeader header = (ColumbaHeader) headerList.get(uid);

            // if the parser didn't return a complete flags object
            // the UID in the flags object is totally wrong
            // -> just skip this flags update
            if (header == null) {
                continue;
            }

            Flags localFlags = header.getFlags();

            localFlags.setFlags(flags.getFlags());

            if (!flags.get(Flags.SEEN)) {
                info.incUnseen();
            }

            if (flags.get(Flags.RECENT)) {
                info.incRecent();
            }

            info.incExists();

            //Junk flag
            header.getAttributes().put("columba.spam",
                    Boolean.valueOf(flags.get(IMAPFlags.JUNK)));
        }
    }

    /**
     * Method save.
     */
    public void save() throws Exception {
        //  make sure that messagefolderinfo(total/unread/recent count)
        // is saved in tree.xml file
        saveMessageFolderInfo();

        // only save header-cache if folder data changed
        if (hasChanged()) {
            getHeaderListStorage().save();
            setChanged(false);
        }
    }

    /**
     * Method synchronize.
     *
     * @param headerList
     * @param newList
     * @return Vector
     * @throws Exception
     */
    public List synchronize(HeaderList headerList, List newList)
            throws Exception {
        LinkedList headerUids = new LinkedList();
        Enumeration keys = headerList.keys();

        while (keys.hasMoreElements()) {
            headerUids.add(keys.nextElement());
        }

        LinkedList newUids = new LinkedList(newList);

        ListTools.substract(newUids, headerUids);

        ListTools.substract(headerUids, new ArrayList(newList));

        Iterator it = headerUids.iterator();

        while (it.hasNext()) {
            headerList.remove(it.next());
        }

        return newUids;

        /*
         * List result = new Vector(); // delete old headers
         *
         * for (Enumeration e = headerList.keys(); e.hasMoreElements();) {
         * String str = (String) e.nextElement();
         *
         * if (existsRemotely(str, 0, newList)) { // mail exists on server // ->
         * keep it } else { // mail doesn't exist on server // -> remove it
         * from local cache headerList.remove(str); } } for (Iterator it =
         * newList.iterator(); it.hasNext();) { String str = (String)
         * it.next(); // for (int i = 0; i < newList.size(); i++) { // String
         * str = (String) newList.get(i);
         *
         * if (existsLocally(str, headerList) == false) { // new message on
         * server result.add(str); } }
         *
         * return result;
         */
    }

    /**
     * Method existsRemotely.
     *
     * @param uid
     * @param startIndex
     * @param uidList
     * @return boolean
     * @throws Exception
     */
    protected boolean existsRemotely(String uid, int startIndex, List uidList)
            throws Exception {
        for (Iterator it = uidList.iterator(); it.hasNext();) {
            String serverUID = (String) it.next();

            // for (int i = startIndex; i < uidList.size(); i++) {
            // String serverUID = (String) uidList.get(i);
            //System.out.println("server message uid: "+ serverUID );
            if (uid.equals(serverUID)) {
                //System.out.println("local uid exists remotely");
                return true;
            }
        }

        return false;
    }

    /**
     * Method existsLocally.
     *
     * @param uid
     * @param list
     * @return boolean
     * @throws Exception
     */
    protected boolean existsLocally(String uid, HeaderList list)
            throws Exception {
        for (Enumeration e = headerList.keys(); e.hasMoreElements();) {
            String localUID = (String) e.nextElement();

            if (uid.equals(localUID)) {
                return true;
            }
        }

        return false;
    }

    /**
     * @see org.columba.mail.folder.Folder#getMimePartTree(java.lang.Object,
     *      org.columba.core.command.WorkerStatusController)
     */
    public MimeTree getMimePartTree(Object uid) throws Exception {
        return getStore().getMimePartTree(uid, getImapPath());
    }

    /**
     * @see org.columba.mail.folder.Folder#getMimePart(java.lang.Object,
     *      java.lang.Integer, org.columba.core.command.WorkerStatusController)
     */
    public MimePart getMimePart(Object uid, Integer[] address) throws Exception {
        return getStore().getMimePart(uid, address, getImapPath());
    }

    /**
     * Copies a set of messages from this folder to a destination folder.
     * <p>
     * The IMAP copy command also keeps the flags intact. So, there's no need
     * to change these manually.
     *
     * @see org.columba.mail.folder.Folder#innerCopy(org.columba.mail.folder.MailboxInterface,
     *      java.lang.Object, org.columba.core.command.WorkerStatusController)
     */
    public void innerCopy(MailboxInterface destFolder, Object[] uids)
            throws Exception {
        getStore().copy(((IMAPFolder) destFolder).getImapPath(), uids,
                getImapPath());

        //FIXME: Use method addMessage(Object) from destination folder
        //to notify it of message additions -> remove code below
        
        // update messagefolderinfo of destination-folder
        // -> this is necessary to reflect the changes visually
        for (int i = 0; i < uids.length; i++) {
            Flags flag = (Flags) getFlags(uids[i]);

            // skip non existing messages
            // -> this can happen when we have multiple filteraction
            // -> on the same set of messages
            if (flag == null) {
                continue;
            }

            // increment recent count of messages if appropriate
            if (flag.getRecent()) {
                destFolder.getMessageFolderInfo().incRecent();
            }

            // increment unseen count of messages if appropriate
            if (!flag.getSeen()) {
                destFolder.getMessageFolderInfo().incUnseen();
            }
        }

        // mailbox was modified
        changed = true;
    }

    /**
     * @see org.columba.mail.folder.Folder#markMessage(java.lang.Object, int,
     *      org.columba.core.command.WorkerStatusController)
     */
    public void markMessage(Object[] uids, int variant) throws Exception {
        getStore().markMessage(uids, variant, getImapPath());

        super.markMessage(uids, variant);
    }

    /**
     * @see org.columba.mail.folder.Folder#removeMessage(java.lang.Object,
     *      org.columba.core.command.WorkerStatusController)
     */
    protected void removeMessage(Object uid) throws Exception {
        super.removeMessage(uid);
        
//      remove message
        //headerList.remove(uid);
        getHeaderListStorage().removeMessage(uid);
    }


    /**
     * @see org.columba.mail.folder.Folder#expungeFolder(java.lang.Object,
     *      org.columba.core.command.WorkerStatusController)
     */
    public void expungeFolder() throws Exception {
        boolean result = getStore().expunge(getImapPath());

        if (!result) { return; }

        super.expungeFolder();
    }

    /**
     * @see org.columba.mail.folder.Folder#getMessageHeader(java.lang.Object,
     *      org.columba.core.command.WorkerStatusController)
     */
    public ColumbaHeader getMessageHeader(Object uid) throws Exception {
        if (headerList == null) {
            getHeaderList();
        }

        return (ColumbaHeader) headerList.get(uid);
    }

    /**
     * Method getMessage.
     *
     * @param uid
     * @param worker
     * @return AbstractMessage
     * @throws Exception
     */
    public ColumbaMessage getMessage(Object uid) throws Exception {
        return new ColumbaMessage((ColumbaHeader) headerList.get((String) uid));
    }

    /**
     * Method getImapPath.
     *
     * @return String
     */
    public String getImapPath() throws Exception {
        StringBuffer path = new StringBuffer();
        path.append(getName());

        AbstractFolder child = this;

        while (true) {
            child = (AbstractFolder) child.getParent();

            if (child instanceof IMAPRootFolder) {
                break;
            }

            String n = ((IMAPFolder) child).getName();

            path.insert(0, n + getStore().getDelimiter());
        }

        return path.toString();
    }

    /**
     * @see org.columba.mail.folder.FolderTreeNode#getDefaultProperties()
     */
    public static XmlElement getDefaultProperties() {
        XmlElement props = new XmlElement("property");

        props.addAttribute("accessrights", "user");
        props.addAttribute("subfolder", "true");

        return props;
    }

    /**
     * @see org.columba.mail.folder.FolderTreeNode#tryToGetLock(java.lang.Object)
     */
    public boolean tryToGetLock(Object locker) {
        // IMAP Folders have no own lock ,but share the lock from the Root
        // to ensure that only one operation can be processed simultanous
        AbstractFolder root = getRootFolder();

        if (root != null) {
            return root.tryToGetLock(locker);
        } else {
            return false;
        }
    }

    /**
     * @see org.columba.mail.folder.FolderTreeNode#releaseLock()
     */
    public void releaseLock(Object locker) {
        AbstractFolder root = getRootFolder();

        if (root != null) {
            root.releaseLock(locker);
        }
    }

    /*
     * (non-Javadoc)
     *
     * @see org.columba.mail.folder.FolderTreeNode#addSubfolder(org.columba.mail.folder.FolderTreeNode)
     */
    public void addSubfolder(AbstractFolder child) throws Exception {
        if (child instanceof IMAPFolder) {
            String path = getImapPath() + getStore().getDelimiter()
                    + child.getName();

            getStore().createFolder(path);
        }

        super.addSubfolder(child);
    }

    /*
     * (non-Javadoc)
     *
     * @see org.columba.mail.folder.Folder#getObservable()
     */
    public StatusObservable getObservable() {
        return ((IMAPRootFolder) getRootFolder()).getObservable();
    }

    /*
     * (non-Javadoc)
     *
     * @see org.columba.mail.folder.MailboxInterface#addMessage(java.io.InputStream)
     */
    public Object addMessage(InputStream in, Attributes attributes, Flags flags)
            throws Exception {
        StringBuffer stringSource = StreamUtils.readInString(in);

        getStore().append(getImapPath(), stringSource.toString());

        fireMessageAdded(null);
        return null;
    }

    /*
     * (non-Javadoc)
     *
     * @see org.columba.mail.folder.MailboxInterface#getHeaderFields(java.lang.Object,
     *      java.lang.String[])
     */
    public Header getHeaderFields(Object uid, String[] keys) throws Exception {
        // get header with UID
        ColumbaHeader header = (ColumbaHeader) getHeaderList().get(uid);

        Header result = new Header();

        // if only one headerfield wasn't found in cache
        // -> call IMAPStore.getHeader() to fetch the
        // -> missing headerfields
        boolean parsingNeeded = false;

        // cached headerfield list
        List list = Arrays.asList(CachedHeaderfields.getCachedHeaderfields());

        for (int i = 0; i < keys.length; i++) {
            if (header.get(keys[i]) != null) {
                // headerfield found
                result.set(keys[i], header.get(keys[i]));
            } else {
                // check if this headerfield is in the cache
                // -> if its not a cached headerfield, we need to fetch it
                if (!list.contains(keys[i])) {
                    parsingNeeded = true;
                }
            }
        }

        if (parsingNeeded) {
            return getStore().getHeaders(uid, keys, getImapPath());
        } else {
            return result;
        }
    }

    /*
     * (non-Javadoc)
     *
     * @see org.columba.mail.folder.MailboxInterface#getMessageSourceStream(java.lang.Object)
     */
    public InputStream getMessageSourceStream(Object uid) throws Exception {
        Source source = getStore().getMessageSource(uid, getImapPath());

        return new SourceInputStream(source);
    }

    /*
     * (non-Javadoc)
     *
     * @see org.columba.mail.folder.MailboxInterface#getMimePartSourceStream(java.lang.Object,
     *      java.lang.Integer[])
     */
    public InputStream getMimePartSourceStream(Object uid, Integer[] address)
            throws Exception {
        return ((StreamableMimePart) getStore().getMimePartSource(uid, address,
                getImapPath())).getInputStream();
    }


    /*
     * (non-Javadoc)
     *
     * @see org.columba.mail.folder.MailboxInterface#getMimePartBodyStream(java.lang.Object,
     *      java.lang.Integer[])
     */
    public InputStream getMimePartBodyStream(Object uid, Integer[] address)
            throws Exception {
        StreamableMimePart mimePart = (StreamableMimePart) getStore()
                .getMimePart(uid, address, getImapPath());

        return decodeStream(mimePart.getHeader(), mimePart.getInputStream());
    }

    /*
     * (non-Javadoc)
     *
     * @see org.columba.mail.folder.Folder#isInboxFolder()
     */
    public boolean isInboxFolder() {
        RootFolder root = (RootFolder) getRootFolder();

        if (root != null) {
            return root.getInboxFolder() == this;
        } else {
            return false;
        }
    }

    /*
     * (non-Javadoc)
     *
     * @see org.columba.mail.folder.Folder#isTrashFolder()
     */
    public boolean isTrashFolder() {
        RootFolder root = (RootFolder) getRootFolder();

        if (root != null) {
            return root.getTrashFolder() == this;
        } else {
            return false;
        }
    }

    /*
     * (non-Javadoc)
     *
     * @see org.columba.mail.folder.MailboxInterface#addMessage(java.io.InputStream,
     *      org.columba.ristretto.message.Attributes)
     */
    public Object addMessage(InputStream in) throws Exception {
        return addMessage(in, null, null);
    }

    /**
     * @see org.columba.mail.folder.Folder#getHeaderListStorage()
     */
    public HeaderListStorage getHeaderListStorage() {
        if (attributeStorage == null)
                attributeStorage = new RemoteHeaderListStorage(this);

        return attributeStorage;
    }
    /**
     * @see org.columba.mail.folder.Folder#getSearchEngineInstance()
     */
    public DefaultSearchEngine getSearchEngineInstance() {
        if (searchEngine == null) {
            searchEngine = new DefaultSearchEngine(this);
            searchEngine.setNonDefaultEngine(new IMAPQueryEngine(this));
        }

        return searchEngine;
    }
}