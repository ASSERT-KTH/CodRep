import org.columba.ristretto.imap.ListInfo;

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
//
//$Log: IMAPRootFolder.java,v $
//
package org.columba.mail.folder.imap;

import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.util.List;

import javax.swing.ImageIcon;
import javax.swing.Timer;

import org.columba.core.command.StatusObservable;
import org.columba.core.command.StatusObservableImpl;
import org.columba.core.gui.util.ImageLoader;
import org.columba.core.logging.ColumbaLogger;
import org.columba.core.main.MainInterface;
import org.columba.core.shutdown.ShutdownManager;
import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.config.AccountItem;
import org.columba.mail.config.FolderItem;
import org.columba.mail.config.MailConfig;
import org.columba.mail.filter.Filter;
import org.columba.mail.folder.FolderTreeNode;
import org.columba.mail.folder.command.CheckForNewMessagesCommand;
import org.columba.mail.imap.IMAPStore;
import org.columba.ristretto.imap.parser.ListInfo;
import org.columba.ristretto.imap.protocol.IMAPProtocol;

public class IMAPRootFolder extends FolderTreeNode implements ActionListener {
	
	protected final static ImageIcon imapRootIcon =
		//ImageLoader.getSmallImageIcon("imap-16.png");
	ImageLoader.getSmallImageIcon("stock_internet-16.png");

	private IMAPProtocol imap;
	//private boolean select=false;
	private boolean fetch = false;

	private StringBuffer cache;
	private int state;
	private List lsubList;

	private final static int ONE_SECOND = 1000;
	private Timer timer;

	//    private ImapOperator operator;

	private AccountItem accountItem;

	private IMAPStore store;
	
	/**
	 * Status information updates are handled in using StatusObservable.
	 * <p>
	 * Every command has to register its interest to this events before
	 * accessing the folder. 
	 */
	protected StatusObservable observable;
	

	public IMAPRootFolder(FolderItem folderItem) {
		//super(node, folderItem);
		super(folderItem);
		observable = new StatusObservableImpl();

		accountItem =
			MailConfig.getAccountList().uidGet(
				folderItem.getInteger("account_uid"));

		updateConfiguration();

	}

	public IMAPRootFolder(AccountItem accountItem) {
		//super(node, folderItem);
		//super(getDefaultItem("IMAPRootFolder", getDefaultProperties()));
		super(accountItem.get("name"), "IMAPRootFolder");
		observable = new StatusObservableImpl();

		this.accountItem = accountItem;

		getFolderItem().set("account_uid", accountItem.getInteger("uid"));

		updateConfiguration();
	}

	public ImageIcon getCollapsedIcon() {
		return imapRootIcon;
	}

	public ImageIcon getExpandedIcon() {
		return imapRootIcon;
	}

	public String getDefaultChild() {
		return "IMAPFolder";
	}

	/**
		 * @see org.columba.mail.folder.FolderTreeNode#addFolder(java.lang.String)
		 */
	/*
	public FolderTreeNode addFolder(String name) throws Exception {
	
		String path = name;
	
		boolean result = getStore().createFolder(path);
	
		if (result)
			return super.addFolder(name);
	
		return null;
	}
	*/

	// we can't use 
	//   "folder.addFolder(subchild)"
	// here
	//
	// -> this would tell the IMAP server to create a new
	// -> folder, too
	//
	// -> but we only want to create it in Columba without 
	// -> touching the server
	/*
	protected FolderTreeNode addIMAPChildFolder(
		FolderTreeNode folder,
		ListInfo info,
		String subchild)
		throws Exception {
		ColumbaLogger.log.debug("creating folder=" + subchild);
	
		ColumbaLogger.log.debug("info.getName()=" + info.getName());
		ColumbaLogger.log.debug("info.getLastName()=" + info.getLastName());
	
		if (subchild.equals(info.getLastName())) {
	
			// this is just a parent-folder we need to
			// create in order to create a child-folder
			ColumbaLogger.log.debug("creating immediate folder=" + subchild);
	
			return folder.addFolder(subchild, "IMAPFolder");
	
		} else {
	
			// this folder is associated with ListInfo
			// pass parameters to folderinfo 			
			ColumbaLogger.log.debug("create final folder" + subchild);
	
			IMAPFolder imapFolder =
				(IMAPFolder) folder.addFolder(subchild, "IMAPFolder");
			FolderItem folderItem = imapFolder.getFolderItem();
	
			folderItem.set("selectable", false);
	
			return imapFolder;
		}
	
	}
	*/

	/**
	 * @return	observable containing status information
	 */
	public StatusObservable getObservable() {
		return observable;
	}

	protected void syncFolder(
		FolderTreeNode parent,
		String name,
		ListInfo info)
		throws Exception {

		ColumbaLogger.log.debug("creating folder=" + name);

		if (name.indexOf(store.getDelimiter()) != -1 && name.indexOf(store.getDelimiter()) != name.length()-1) {

			// delimiter found
			//  -> recursively create all necessary folders to create
			//  -> the final folder 
			String subchild =
				name.substring(0, name.indexOf(store.getDelimiter()));
			FolderTreeNode subFolder =
				(FolderTreeNode) parent.getChild(subchild);

			// if folder doesn't exist already
			if (subFolder == null) {
				subFolder = new IMAPFolder(subchild, "IMAPFolder");
				parent.add( subFolder );
				parent.getNode().addElement(subFolder.getNode());

				((IMAPFolder) subFolder).existsOnServer = true;
				subFolder.getFolderItem().set("selectable", "false");

				// this is the final folder
				//subFolder = addIMAPChildFolder(parent, info, subchild);
			} else {
				if( !((IMAPFolder) subFolder).existsOnServer) {
				((IMAPFolder) subFolder).existsOnServer = true;
				subFolder.getFolderItem().set("selectable", "false");
				}
			}
			
			
			// recursively go on
			syncFolder(
				subFolder,
				name.substring(name.indexOf(store.getDelimiter()) + 1),
				info);

		} else {

			// no delimiter found
			//  -> this is already the final folder

			// if folder doesn't exist already
			FolderTreeNode subFolder = (FolderTreeNode) parent.getChild(name);
			if (subFolder == null) {

				subFolder = new IMAPFolder(name, "IMAPFolder");
				parent.add( subFolder );
				parent.getNode().addElement(subFolder.getNode());

				((IMAPFolder) subFolder).existsOnServer = true;
			} else {
				((IMAPFolder) subFolder).existsOnServer = true;
			}
			
			if( info.getParameter(ListInfo.NOSELECT) ) {
				subFolder.getFolderItem().set("selectable", "false");
			} else {
				subFolder.getFolderItem().set("selectable", "true");				
			}
		}
	}

	protected void markAllSubfoldersAsExistOnServer(
		FolderTreeNode parent,
		boolean value) {
		FolderTreeNode child;
		for (int i = 0; i < parent.getChildCount(); i++) {
			child = (FolderTreeNode) parent.getChildAt(i);
			if (child instanceof IMAPFolder) {
				((IMAPFolder) child).existsOnServer = value;
				markAllSubfoldersAsExistOnServer(child, value);
			}
		}
	}

	protected void removeNotMarkedSubfolders(FolderTreeNode parent)
		throws Exception {
		FolderTreeNode child;

		// first remove all subfolders recursively
		for (int i = 0; i < parent.getChildCount(); i++) {
			child = (FolderTreeNode) parent.getChildAt(i);
			if (child instanceof IMAPFolder) {
				removeNotMarkedSubfolders(child);
			}
		}

		// maybe remove this folder
		if (parent instanceof IMAPFolder) {
			if (!((IMAPFolder) parent).existsOnServer) {
				parent.removeFolder();
			}
		}
	}

	public void syncSubscribedFolders() {
		// first clear all flags
		markAllSubfoldersAsExistOnServer(this, false);
		
		IMAPFolder inbox = (IMAPFolder) this.getChild("INBOX");
		inbox.existsOnServer = true;

		try {
			// create and tag all subfolders on server
			ListInfo[] listInfo = getStore().lsub("", "*");

			if (listInfo != null) {
				for (int i = 0; i < listInfo.length; i++) {
					ListInfo info = listInfo[i];
					ColumbaLogger.log.debug(
						"delimiter=" + getStore().getDelimiter());

					String folderPath = info.getName();

					syncFolder(this, folderPath, info);

				}
			}

			// remove all subfolders that are not marked as existonserver
			removeNotMarkedSubfolders(this);



		} catch (Exception ex) {
			ex.printStackTrace();
		}

		// This fixes the strange behaviour of the courier imapserver
		// which sets the \Noselect flag on INBOX
		inbox.getFolderItem().set("selectable", "true");
	}

	public IMAPStore getStore() {
		return store;
	}

	public void updateConfiguration() {
		store = new IMAPStore(accountItem.getImapItem(), this);

		if (accountItem.getImapItem().getBoolean("enable_mailcheck")) {
			int interval =
				accountItem.getImapItem().getInteger("mailcheck_interval");

			timer = new Timer(ONE_SECOND * interval * 60, this);
			timer.restart();

		} else {

			if (timer != null) {
				timer.stop();
				timer = null;
			}
		}
	}

	public void actionPerformed(ActionEvent e) {
		Object src = e.getSource();

		if (src.equals(timer)) {

			System.out.println("timer action");

			FolderCommandReference[] r = new FolderCommandReference[1];
			r[0] = new FolderCommandReference(this);

			MainInterface.processor.addOp(new CheckForNewMessagesCommand(r));

		}
	}

	/*
	public String getDelimiter() {
		return delimiter;
	}
	
	public boolean isLogin(SwingWorker worker) throws Exception {
		if (getState() == Imap4.STATE_AUTHENTICATE)
			return true;
		else {
			// we are in Imap4.STATE_NONAUTHENTICATE
	
			login(worker);
			return false;
		}
	
	}
	
	public void clearLSubList() {
		lsubList = null;
	}
	
	public int getAccountUid() {
		return accountUid;
	}
	
	public ImapItem getImapItem() {
		return item;
	}
	
	public Imap4 getImapServerConnection() {
		return imap;
	}
	
	private boolean isSubscribed(IMAPFolder folder, Vector lsubList) {
		String folderPath = folder.getImapPath();
	
		for (int i = 0; i < lsubList.size(); i++) {
	
			String path = (String) lsubList.get(i);
	
			if (folderPath.equalsIgnoreCase(path))
				return true;
		}
	
		return false;
	}
	
	private void removeUnsubscribedFolders(Folder child) {
		if (!(child instanceof IMAPRootFolder)) {
			if (child.getChildCount() == 0) {
				Folder parent = (Folder) child.getParent();
				child.removeFromParent();
				System.out.println("folder removed:" + parent);
	
				removeUnsubscribedFolders(parent);
			}
		}
	}
	
	public void removeUnsubscribedFolders(Folder parent, Vector lsubList) {
		for (int i = 0; i < parent.getChildCount(); i++) {
			if (!(parent.getChildAt(i) instanceof IMAPFolder))
				continue;
	
			IMAPFolder child = (IMAPFolder) parent.getChildAt(i);
	
			if (child.getChildCount() == 0) {
				// if folder is not subscribed: remove folder
				if (!isSubscribed(child, lsubList)) {
					//removeUnsubscribedFolders(child);
					child.removeFromParent();
					i--;
				}
			} else
				removeUnsubscribedFolders(child, lsubList);
		}
	}
	
	private void addFolder(Folder folder, String name, Vector lsubList) {
	
		if (name.indexOf(delimiter) != -1) {
	
			String subchild = name.substring(0, name.indexOf(delimiter));
			IMAPFolder subFolder = (IMAPFolder) folder.getChild(subchild);
	
			if (subFolder == null) {
	
				// folder does not exist, create new folder
				subFolder =
					(IMAPFolder) MainInterface
						.treeModel
						.addImapFolder(
						folder,
						subchild,
						item,
						this,
						accountUid);
	
				//subFolder.getFolderItem().setMessageFolder("false");
			}
	
			addFolder(
				subFolder,
				name.substring(name.indexOf(delimiter) + 1, name.length()),
				lsubList);
		} else {
			if (folder.getChild(name) == null)
				MainInterface.treeModel.addImapFolder(
					folder,
					name,
					item,
					this,
					accountUid);
		}
	
	}
	*/

	/*
	private void addSubscribedFolders(Vector lsubList) throws Exception {
		boolean inbox = false;
		boolean answer;
	
		for (int i = 0; i < lsubList.size(); i++) {
			String name = (String) lsubList.get(i);
	
			if (name.toLowerCase().equalsIgnoreCase("inbox"))
				inbox = true;
	
			addFolder(this, name, lsubList);
	
		}
	
		if (inbox == false) {
			answer = imap.flist("", "");
			//System.out.println("trying to parse flist");
			String str = imap.getResult();
			//System.out.println("str: "+ str );
			str = str.toLowerCase();
			//System.out.println("str: "+ str );
	
			if (str.indexOf("inbox") != -1) {
				Folder childFolder = (Folder) getChild("Inbox");
				if (childFolder == null) {
					MainInterface.treeModel.addImapFolder(
						this,
						"Inbox",
						item,
						this,
						accountUid);
				}
			} else {
				System.out.println("string inbox not found");
			}
		}
	}
	
	protected void lsubsub(Vector lsubList, Vector v) throws Exception {
	
		//lsubList.addAll(v);
	
		for (int i = 0; i < v.size(); i++) {
			String path = (String) v.get(i);
			lsubList.add(path);
	
			System.out.println("path:" + path);
	
			boolean answer = imap.flsub(path + "/*");
	
			if (imap.getResult().length() > 0) {
				Vector temp = Imap4Parser.parseLsub(imap.getResult());
	
				if (temp.size() > 0)
					lsubsub(lsubList, temp);
			}
	
		}
	
	}
	*/

	/**
	 *
	 * this method is called to get the initial folder-list
	 *  ( this happens when doppel-clicking the imap root-folder
	 * */

	/*
	public void lsub(SwingWorker worker) throws Exception {
	
		boolean answer;
		lsubList = new Vector();
		Vector v = new Vector();
	
		getImapServerConnection().setState(Imap4.STATE_NONAUTHENTICATE);
	
		isLogin(worker);
	
		if (worker != null)
			worker.setText("Retrieve folder listing...");
	
		if (worker != null)
			worker.startTimer();
	
		answer = imap.flist("", "");
	
		String result = imap.getResult();
	
		delimiter = Imap4Parser.parseDelimiter(result);
		System.out.println("delimiter=" + delimiter);
	
		answer = imap.flsub("*");
		//System.out.println("trying to parse lsub");
		String result2 = imap.getResult();
		System.out.println("--------->result:\n" + result2);
	
		lsubList = Imap4Parser.parseLsub(result2);
	
		//lsubsub(lsubList, v);
	
		v = new Vector();
		v.add("INBOX");
	
		lsubsub(lsubList, v);
	
		// add subscribed folders
	
		addSubscribedFolders(lsubList);
	
		// remove unsubscribed folders
	
		removeUnsubscribedFolders(this, lsubList);
	
		if (worker != null)
			worker.stopTimer();
	
	}
	*/

	/**
	 *
	 *  this method is called by the subscribe/unsubscribe dialog
	 *
	 *
	 **/
	/*
	public Vector getLSubList() throws Exception {
		if (lsubList != null)
			return lsubList;
	
		boolean answer;
		lsubList = new Vector();
	
		try {
	
			answer = imap.flsub("*");
			//System.out.println("trying to parse lsub");
	
			lsubList = Imap4Parser.parseLsub(imap.getResult());
	
		} catch (Exception ex) {
			//System.out.println("imapfolder->lsub: "+ ex.getMessage() );
			throw new Exception(
				"IMAPRootFolder->getLSubList: " + ex.getMessage());
		}
	
		return lsubList;
	}
	
	public boolean subscribe(String path) throws Exception {
		boolean answer = false;
	
		try {
			answer = imap.subscribe(path);
		} catch (Exception ex) {
			//System.out.println("imapfolder->lsub: "+ ex.getMessage() );
			throw new Exception(
				"IMAPRootFolder->subscribe: " + ex.getMessage());
		}
	
		return answer;
	}
	
	public boolean unsubscribe(String path) throws Exception {
		boolean answer = false;
		try {
			answer = imap.unsubscribe(path);
		} catch (Exception ex) {
			//System.out.println("imapfolder->lsub: "+ ex.getMessage() );
			throw new Exception(
				"IMAPRootFolder->unsubscribe: " + ex.getMessage());
		}
	
		return answer;
	}
	*/
	/**
	 *
	 *  this method is called by the subscribe/unsubscribe dialog
	 *
	 *
	 **/
	/*
	public Vector getList(SubscribeTreeNode treeNode) throws Exception {
		StringBuffer buf = new StringBuffer(treeNode.getName());
		SubscribeTreeNode node = (SubscribeTreeNode) treeNode.getParent();
		while (node != null) {
			if (node.getName().equals("root"))
				break;
	
			buf.insert(0, node.getName() + "/");
			node = (SubscribeTreeNode) node.getParent();
		}
	
		String name = buf.toString();
	
		Vector v = new Vector();
	
		boolean answer;
	
		try {
	
			answer = imap.flist(name.trim() + "/%", "");
			//System.out.println("trying to parse list");
			v = Imap4Parser.parseList(imap.getResult());
	
		} catch (Exception ex) {
			//System.out.println("imapfolder->lsub: "+ ex.getMessage() );
			throw new Exception("IMAPRootFolder->getList: " + ex.getMessage());
		}
	
		return v;
	}
	*/
	/**
	 *
	 *  this method is called by the subscribe/unsubscribe dialog
	 *
	 *
	 **/

	/*
	public Vector getList() throws Exception {
		Vector v = new Vector();
	
		boolean answer;
	
		isLogin(null);
	
		answer = imap.flist("*", "");
		// System.out.println("trying to parse list");
		v = Imap4Parser.parseList(imap.getResult());
	
		return v;
	}
	*/

	/*
	public boolean addFolder(String path) throws Exception {
		isLogin(null);
	
		boolean b = imap.create(path);
	
		if (b == false) {
			throw new ImapException(imap.getResult());
		}
	
		return b;
	}
	*/

	/**
	 * @see org.columba.mail.folder.Folder#searchMessages(org.columba.mail.filter.Filter, java.lang.Object, org.columba.core.command.WorkerStatusController)
	 */
	public Object[] searchMessages(Filter filter, Object[] uids)
		throws Exception {
		return null;
	}

	/**
	 * @see org.columba.mail.folder.Folder#searchMessages(org.columba.mail.filter.Filter, org.columba.core.command.WorkerStatusController)
	 */
	public Object[] searchMessages(Filter filter) throws Exception {
		return null;
	}

	/**
	 * @return
	 */
	public AccountItem getAccountItem() {
		return accountItem;
	}

	/**
	 * @param type
	 */
	public IMAPRootFolder(String name, String type) {
		super(name, type);

		FolderItem item = getFolderItem();
		item.set("property", "accessrights", "system");
		item.set("property", "subfolder", "true");

	}

	/* (non-Javadoc)
	 * @see org.columba.mail.folder.FolderTreeNode#addSubfolder(org.columba.mail.folder.FolderTreeNode)
	 */
	public void addSubfolder(FolderTreeNode child) throws Exception {
		String path = child.getName();
		boolean result = getStore().createFolder(path);
		
		if (result) super.addSubfolder(child);
	}

	/* (non-Javadoc)
	 * @see org.columba.mail.folder.Folder#save()
	 */
	public void save() throws Exception {
		
		ColumbaLogger.log.debug("Logout from IMAPServer "+ getName());
		if( ShutdownManager.getMode() == ShutdownManager.SHUTDOWN ) {
			getStore().logout();
		}
		
	}

}