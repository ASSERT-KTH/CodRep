item.getBoolean("enable_ssl", false));

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

package org.columba.mail.imap;

import java.net.SocketException;
import java.text.MessageFormat;
import java.util.LinkedList;
import java.util.List;
import java.util.Vector;

import javax.swing.JOptionPane;

import org.columba.core.command.StatusObservable;
import org.columba.core.logging.ColumbaLogger;
import org.columba.mail.config.ImapItem;
import org.columba.mail.filter.FilterRule;
import org.columba.mail.folder.command.MarkMessageCommand;
import org.columba.mail.folder.headercache.CachedHeaderfieldOwner;
import org.columba.mail.folder.imap.IMAPRootFolder;
import org.columba.mail.gui.util.PasswordDialog;
import org.columba.mail.message.ColumbaHeader;
import org.columba.mail.message.HeaderList;
import org.columba.mail.util.MailResourceLoader;
import org.columba.ristretto.imap.IMAPHeader;
import org.columba.ristretto.imap.IMAPResponse;
import org.columba.ristretto.imap.ListInfo;
import org.columba.ristretto.imap.MessageSet;
import org.columba.ristretto.imap.parser.FlagsParser;
import org.columba.ristretto.imap.parser.IMAPHeaderParser;
import org.columba.ristretto.imap.parser.ListInfoParser;
import org.columba.ristretto.imap.parser.MessageFolderInfoParser;
import org.columba.ristretto.imap.parser.MessageSourceParser;
import org.columba.ristretto.imap.parser.MimePartParser;
import org.columba.ristretto.imap.parser.MimeTreeParser;
import org.columba.ristretto.imap.parser.SearchResultParser;
import org.columba.ristretto.imap.parser.UIDParser;
import org.columba.ristretto.imap.parser.UIDSetParser;
import org.columba.ristretto.imap.protocol.Arguments;
import org.columba.ristretto.imap.protocol.BadCommandException;
import org.columba.ristretto.imap.protocol.CommandFailedException;
import org.columba.ristretto.imap.protocol.DisconnectedException;
import org.columba.ristretto.imap.protocol.IMAPException;
import org.columba.ristretto.imap.protocol.IMAPProtocol;
import org.columba.ristretto.message.Flags;
import org.columba.ristretto.message.Header;
import org.columba.ristretto.message.LocalMimePart;
import org.columba.ristretto.message.MessageFolderInfo;
import org.columba.ristretto.message.MimePart;
import org.columba.ristretto.message.MimeTree;
import org.columba.ristretto.message.io.CharSequenceSource;
import org.columba.ristretto.message.io.ConcatenatedSource;
import org.columba.ristretto.message.io.Source;
import org.columba.ristretto.parser.HeaderParser;
import org.columba.ristretto.parser.ParserException;
import org.columba.ristretto.progress.ProgressObserver;

/**
 * IMAPStore encapsulates IMAPProtocol and the parsers for IMAPFolder.
 * <p>
 * This way {@link IMAPFolder}doesn't need to do any parsing work, etc.
 * <p>
 * Every {@link IMAPFolder}of a single account has also an
 * {@link IMAPRootFolder}, which keeps a reference to {@link IMAPStore}.
 * Which itself uses {@link IMAPProtocol}.
 * <p>
 * IMAPStore handles the current state of connection:
 * <ul>
 * <li>STATE_NONAUTHENTICATE - not authenticated</li>
 * <li>STATE_AUTHENTICATE - authenticated</li>
 * <li>STATE_SELECTED - mailbox is selected</li>
 * </ul>
 * <p>
 * It keeps a reference to the currently selected mailbox.
 * <p>
 * IMAPFolder shouldn't use IMAPProtocol directly, instead it should use
 * IMAPStore.
 * 
 * @author fdietz
 */
public class IMAPStore {

	/**
	 * not connected to IMAP server
	 */
	public static final int STATE_NONAUTHENTICATE = 0;

	/**
	 * connected an authenticated to IMAP server
	 */
	public static final int STATE_AUTHENTICATE = 1;

	/**
	 * mailbox selected
	 */
	public static final int STATE_SELECTED = 2;

	/**
	 * list of IMAP server capabilites
	 */
	private List capabilities;

	/**
	 * current state
	 */
	private int state = STATE_NONAUTHENTICATE;

	/**
	 * currently selected mailbox
	 */
	private String selectedFolderPath;

	/**
	 * mailbox name delimiter
	 * <p>
	 * example: "/" (uw-imap), or "." (cyrus)
	 */
	private String delimiter;

	/**
	 * reference to IMAP protocol
	 */
	private IMAPProtocol imap;

	/**
	 * configuration options of this IMAP account
	 */
	private ImapItem item;

	/**
	 * reference to root folder
	 */
	private IMAPRootFolder parent;

	private MimeTree aktMimePartTree;
	private Object aktMessageUid;

	private MessageFolderInfo messageFolderInfo;

	public IMAPStore(ImapItem item, IMAPRootFolder root) {

		this.item = item;
		this.parent = root;

		// create IMAP protocol
		imap =
			new IMAPProtocol(
				item.get("host"),
				item.getInteger("port"),
				item.getBoolean("enable_ssl", true));

		// register interest on status updates
		imap.registerInterest((ProgressObserver) root.getObservable());

		// initialy set state to be not authenticated
		state = 0;
	}

	/**
	 * @return
	 */
	public StatusObservable getObservable() {
		return parent.getObservable();
	}

	/**
	 * @param message
	 */
	protected void printStatusMessage(String message) {
		getObservable().setMessage(item.get("host") + ": " + message);
	}

	/**
	 * Get mailbox path delimiter
	 * <p>
	 * example: "/" (uw-imap), or "." (cyrus)
	 * 
	 * @return delimiter
	 */
	public String getDelimiter() {
		if (delimiter == null) {
			// try to determine delimiter
			try {
				delimiter = fetchDelimiter();
			} catch (Exception e) {
				e.printStackTrace();
			}
		}
		return delimiter;
	}

	/**
	 * @return currenlty selected mailbox
	 */
	public String getSelectedFolderPath() {
		return selectedFolderPath;
	}

	/**
	 * @param s
	 *            currenlty selected mailbox
	 */
	public void setSelectedFolderPath(String s) {
		selectedFolderPath = s;
	}

	/**
	 * Logout cleanly.
	 * 
	 * @throws Exception
	 */
	public void logout() throws Exception {
		if (state != STATE_NONAUTHENTICATE)
			getProtocol().logout();
	}

	/**
	 * @return current state
	 */
	public int getState() {
		return state;
	}

	/**
	 * Login to IMAP server.
	 * <p>
	 * Ask user for password.
	 * 
	 * @throws Exception
	 */
	public void login() throws Exception {

		PasswordDialog dialog = null;

		boolean answer = false;
		boolean cancel = false;
		boolean first = true;

		boolean openport = false;
		int portNumber = -1;

		try {
			portNumber = item.getInteger("port");
		} catch (NumberFormatException e) {
			// fall back to default IMAP port
			portNumber = 143;
		}

		try {
			printStatusMessage(
				MailResourceLoader.getString(
					"statusbar",
					"message",
					"authenticating"));

			openport = getProtocol().openPort();

		} catch (Exception e) {
			if (e instanceof SocketException)
				throw new IMAPException(e.getMessage());

			e.printStackTrace();
		}

		if (openport) {
			try {
				// Try first communication with NOOP
				getProtocol().noop();
			} catch (Exception e1) {
				getProtocol().setUseSSL(false);
				getProtocol().openPort();

				//update configuration
				item.set("enable_ssl", "true");
			}

			while (!cancel) {
				if (first) {

					if (item.get("password").length() != 0) {
						getProtocol().login(
							item.get("user"),
							item.get("password"));

						state = STATE_AUTHENTICATE;
						answer = true;
						break;
					}

					first = false;
				}

				dialog = new PasswordDialog();
				dialog.showDialog(
					item.get("host") + "@" + item.get("user"),
					item.get("password"),
					item.getBoolean("save_password"));

				char[] name;

				if (dialog.success()) {
					// ok pressed
					name = dialog.getPassword();
					String password = new String(name);
					//String user = dialog.getUser();
					boolean save = dialog.getSave();

					getProtocol().login(item.get("user"), password);

					answer = true;

					state = STATE_AUTHENTICATE;

					if (answer) {
						cancel = true;

						//item.setUser(user);

						state = STATE_AUTHENTICATE;

						item.set("save_password", save);

						if (save)
							item.set("password", password);

					} else
						cancel = false;
				} else {
					cancel = true;
					answer = false;
					// cancel pressed
				}
			}

		} else {
			answer = false;
		}

		//System.out.println("login successful");
	}

	/**
	 * Check if mailbox is already selected.
	 * <p>
	 * If its not selected -> select it.
	 * 
	 * @param path
	 *            mailbox path
	 * @throws Exception
	 */
	public void ensureSelectedState(String path) throws Exception {

		// ensure that we are logged in already
		ensureLoginState();

		if (getState() == STATE_SELECTED) {
			// we are already in selected state
			if (path.equals(getSelectedFolderPath())) {
				// correct folder selected
				// -> do nothing
			} else {
				// force selection of correct folder
				select(path);

			}

		} else {
			// force selection of correct folder

			// currenlty selected folder == null
			setSelectedFolderPath(null);

			select(path);
		}

	}

	/**
	 * Selected mailbox.
	 * 
	 * @param path
	 *            mailbox to selected
	 * @return @throws
	 *         Exception
	 */
	public boolean select(String path) throws Exception {

		// make sure we are already logged in
		ensureLoginState();

		ColumbaLogger.log.info("selecting path=" + path);

		try {

			printStatusMessage(
				MessageFormat.format(
					MailResourceLoader.getString(
						"statusbar",
						"message",
						"select_path"),
					new Object[] { path }));

			if (getSelectedFolderPath() != null) {
				// if another folder is selected, close this one first
				// -> this is necessary, because the close command
				// -> also deletes all messages that are marked as expunged

				getProtocol().close();
			}
			IMAPResponse[] responses = getProtocol().select(path);

			messageFolderInfo = MessageFolderInfoParser.parse(responses);

			ColumbaLogger.log.info("exists:" + messageFolderInfo.getExists());

			state = STATE_SELECTED;
			selectedFolderPath = path;
		} catch (BadCommandException ex) {
			state = STATE_AUTHENTICATE;
			selectedFolderPath = null;
			JOptionPane.showMessageDialog(
				null,
				"Error while selecting mailbox: " + path);
		} catch (CommandFailedException ex) {
			JOptionPane.showMessageDialog(
				null,
				"Error while selecting mailbox: " + path + ex.getMessage());

			state = STATE_AUTHENTICATE;
			selectedFolderPath = null;
		} catch (DisconnectedException ex) {
			state = STATE_NONAUTHENTICATE;
			selectedFolderPath = null;
			select(path);

		}
		return true;
	}

	/**
	 * @return
	 */
	/**
	 * Returns the IMAPProtocol
	 * 
	 * @return IMAPProtocol
	 */
	protected IMAPProtocol getProtocol() {
		return imap;
	}

	/**
	 * Fetch delimiter.
	 *  
	 */
	protected String fetchDelimiter() throws Exception {
		// make sure we are already logged in
		ensureLoginState();

		try {
			printStatusMessage(
				MailResourceLoader.getString(
					"statusbar",
					"message",
					"fetch_folder_list"));
			IMAPResponse[] responses = getProtocol().list("", "");

			ListInfo listInfo = ListInfoParser.parse(responses[0]);

			return listInfo.getDelimiter();
		} catch (BadCommandException ex) {
		} catch (CommandFailedException ex) {
		} catch (DisconnectedException ex) {
			state = STATE_NONAUTHENTICATE;
			return fetchDelimiter();
		}

		return null;
	}

	/**
	 * List mailbox.
	 * 
	 * @param reference
	 * @param pattern
	 * @return @throws
	 *         Exception
	 */
	public ListInfo[] lsub(String reference, String pattern) throws Exception {

		ensureLoginState();

		try {
			printStatusMessage(
				MailResourceLoader.getString(
					"statusbar",
					"message",
					"fetch_folder_list"));
			IMAPResponse[] responses = getProtocol().lsub(reference, pattern);

			List v = new Vector();
			ListInfo[] list = null;
			for (int i = 0; i < responses.length - 1; i++) {
				if (responses[i] == null) {
					continue;
				}

				if (responses[i].getResponseSubType().equals("LSUB")) {
					ListInfo listInfo = ListInfoParser.parse(responses[i]);
					v.add(listInfo);
				}
			}

			if (v.size() > 0) {
				list = new ListInfo[v.size()];
				((Vector) v).copyInto(list);

				return list;
			}

		} catch (BadCommandException ex) {
		} catch (CommandFailedException ex) {
		} catch (DisconnectedException ex) {
			state = STATE_NONAUTHENTICATE;
			lsub(reference, pattern);
		}

		return null;
	}

	/**
	 * Append message to mailbox.
	 * 
	 * @param mailboxName
	 *            name of mailbox
	 * @param messageSource
	 *            message source
	 * @throws Exception
	 */
	public void append(String mailboxName, String messageSource)
		throws Exception {

		// make sure we are already logged in
		ensureLoginState();

		try {
			getProtocol().append(mailboxName, messageSource);
		} catch (BadCommandException ex) {
		} catch (CommandFailedException ex) {
		} catch (DisconnectedException ex) {
			state = STATE_NONAUTHENTICATE;
			append(mailboxName, messageSource);
		}
	}

	/**
	 * Create new mailbox.
	 * 
	 * @param mailboxName
	 *            name of new mailbox
	 * @return @throws
	 *         Exception
	 */
	public boolean createFolder(String mailboxName) throws Exception {

		//		make sure we are already logged in
		ensureLoginState();

		try {
			getProtocol().create(mailboxName);
			// if we don't subscribe to this folder
			// it won't be visible in Columba
			getProtocol().subscribe(mailboxName);
		} catch (BadCommandException ex) {
		} catch (CommandFailedException ex) {
			JOptionPane.showMessageDialog(
				null,
				"Error while creating mailbox: "
					+ mailboxName
					+ ex.getMessage());
			return false;
		} catch (DisconnectedException ex) {
			state = STATE_NONAUTHENTICATE;
			createFolder(mailboxName);
		}
		return true;
	}

	/**
	 * Delete mailbox.
	 * 
	 * @param mailboxName
	 *            name of mailbox
	 * @return @throws
	 *         Exception
	 */
	public boolean deleteFolder(String mailboxName) throws Exception {

		// make sure we are already logged in
		ensureLoginState();

		try {
			// we need to ensure that this folder is closed
			getProtocol().close();

			// delete folder
			getProtocol().delete(mailboxName);

			// unsubscribe
			getProtocol().unsubscribe(mailboxName);
		} catch (BadCommandException ex) {
		} catch (CommandFailedException ex) {
			return false;
		} catch (DisconnectedException ex) {
			state = STATE_NONAUTHENTICATE;
			deleteFolder(mailboxName);
		}

		return true;
	}

	/**
	 * Rename mailbox.
	 * 
	 * @param oldMailboxName
	 *            old mailbox name
	 * @param newMailboxName
	 *            new mailbox name
	 * @return @throws
	 *         Exception
	 */
	public boolean renameFolder(String oldMailboxName, String newMailboxName)
		throws Exception {

		// make sure we are already logged in
		ensureLoginState();

		try {
			// we need to ensure that this folder is closed
			getProtocol().close();

			getProtocol().rename(oldMailboxName, newMailboxName);
		} catch (BadCommandException ex) {
		} catch (CommandFailedException ex) {
			return false;
		} catch (DisconnectedException ex) {
			state = STATE_NONAUTHENTICATE;
			renameFolder(oldMailboxName, newMailboxName);
		}
		return true;
	}

	/**
	 * Subscribe to mailbox.
	 * 
	 * @param mailboxName
	 *            name of mailbox
	 * @return @throws
	 *         Exception
	 */
	public boolean subscribeFolder(String mailboxName) throws Exception {

		// make sure we are already logged in
		ensureLoginState();

		try {
			getProtocol().subscribe(mailboxName);
		} catch (BadCommandException ex) {
		} catch (CommandFailedException ex) {
			return false;
		} catch (DisconnectedException ex) {
			state = STATE_NONAUTHENTICATE;
			subscribeFolder(mailboxName);
		}
		return true;
	}

	/**
	 * Unsubscribe to mailbox.
	 * 
	 * @param mailboxName
	 *            name of mailbox
	 * @return @throws
	 *         Exception
	 */
	public boolean unsubscribeFolder(String mailboxName) throws Exception {

		// make sure we are already logged in
		ensureLoginState();

		try {
			getProtocol().unsubscribe(mailboxName);
		} catch (BadCommandException ex) {
		} catch (CommandFailedException ex) {
			return false;
		} catch (DisconnectedException ex) {
			state = STATE_NONAUTHENTICATE;
			unsubscribeFolder(mailboxName);
		}
		return true;
	}

	/** ************************** selected state *************************** */

	/**
	 * Fetch UID list and parse it.
	 * 
	 * @param path
	 *            mailbox name
	 * @return list of UIDs
	 * @throws Exception
	 */
	public List fetchUIDList(String path) throws Exception {

		ensureSelectedState(path);

		try {
			int count = messageFolderInfo.getExists();
			if (count == 0)
				return null;

			printStatusMessage(
				MailResourceLoader.getString(
					"statusbar",
					"message",
					"fetch_uid_list"));

			LinkedList uids = new LinkedList();
			IMAPResponse[] responses = imap.fetchUIDList("1:*", count);

			for (int i = 0; i < responses.length; i++) {
				if (responses[i].getResponseSubType().equals("FETCH")) {
					uids.add(UIDParser.parse(responses[i]));
					responses[i] = null;
				}
			}
			return uids;
		} catch (BadCommandException ex) {
		} catch (CommandFailedException ex) {
		} catch (DisconnectedException ex) {
			state = STATE_NONAUTHENTICATE;
			fetchUIDList(path);
		}
		return null;
	}

	/**
	 * Expunge folder.
	 * <p>
	 * Delete every message mark as expunged.
	 * 
	 * @param path
	 *            name of mailbox
	 * @return @throws
	 *         Exception
	 */
	public boolean expunge(String path) throws Exception {

		ensureLoginState();
		ensureSelectedState(path);

		//Object[] expungedUids = null;
		try {
			IMAPResponse[] responses = imap.expunge();

			//expungedUids = FlagsParser.parseFlags(responses);

		} catch (BadCommandException ex) {
		} catch (CommandFailedException ex) {
		} catch (DisconnectedException ex) {
			state = STATE_NONAUTHENTICATE;
			expunge(path);
		}
		return true;
	}

	/**
	 * Copy a set of messages to another mailbox on the same IMAP server.
	 * <p>
	 * <p>
	 * We copy messages in pieces of 100 headers. This means we tokenize the
	 * <code>list</code> in sublists of the size of 100. Then we execute the
	 * command and process those 100 results.
	 * 
	 * @param destFolder
	 *            destination mailbox
	 * @param uids
	 *            UIDs of messages
	 * @param path
	 *            source mailbox
	 * @throws Exception
	 */
	public void copy(String destFolder, Object[] uids, String path)
		throws Exception {

		ensureLoginState();
		ensureSelectedState(path);

		try {

			// we use a token size of 100
			MessageSetTokenizer tok = new MessageSetTokenizer(uids, 100);

			while (tok.hasNext()) {
				List list = (List) tok.next();
				//MessageSet set = new MessageSet(list.toArray());

				IMAPResponse[] responses =
					imap.copy(UIDSetParser.parse(list.toArray()), destFolder);
			}

		} catch (BadCommandException ex) {
		} catch (CommandFailedException ex) {
		} catch (DisconnectedException ex) {
			state = STATE_NONAUTHENTICATE;
		}
	}

	/**
	 * Fetch list of flags and parse it.
	 * 
	 * @param path
	 *            mailbox name
	 * @return list of flags
	 * @throws Exception
	 */
	public Flags[] fetchFlagsList(String path) throws Exception {

		Flags[] result = null;

		ensureLoginState();
		ensureSelectedState(path);

		try {
			printStatusMessage(
				MailResourceLoader.getString(
					"statusbar",
					"message",
					"fetch_flags_list"));
			IMAPResponse[] responses =
				imap.fetchFlagsList("1:*", messageFolderInfo.getExists());

			result = FlagsParser.parseFlags(responses);
		} catch (BadCommandException ex) {
			ex.printStackTrace();
		} catch (CommandFailedException ex) {
			ex.printStackTrace();
		} catch (DisconnectedException ex) {
			state = STATE_NONAUTHENTICATE;
			fetchFlagsList(path);
		}
		return result;
	}

	/**
	 * @param headerString
	 * @return
	 */
	private ColumbaHeader parseMessage(String headerString) {

		try {
			ColumbaHeader h =
				new ColumbaHeader(
					HeaderParser.parse(new CharSequenceSource(headerString)));

			return h;
		} catch (ParserException e) {
			return null;
		}
	}

	/**
	 * Fetch list of headers and parse them.
	 * <p>
	 * We fetch headers in pieces of 100 headers. This means we tokenize the
	 * <code>list</code> in sublists of the size of 100. Then we execute the
	 * command and process those 100 results.
	 * 
	 * @param headerList
	 *            headerlist to add new headers
	 * @param list
	 *            list of UIDs to download
	 * @param path
	 *            mailbox name
	 * @throws Exception
	 */
	public void fetchHeaderList(HeaderList headerList, List list, String path)
		throws Exception {

		// make sure we are logged in
		ensureLoginState();

		// make sure this mailbox is selected
		ensureSelectedState(path);

		//	get list of user-defined headerfields
		String[] headercacheList =
			CachedHeaderfieldOwner.getCachedHeaderfieldArray();

		// create string representation
		StringBuffer headerFields = new StringBuffer();
		String name;
		for (int j = 0; j < headercacheList.length; j++) {
			name = (String) headercacheList[j];
			headerFields.append(name + " ");
		}

		// calculate number of requests
		int requestCount = list.size() / 100;

		// initialize progressbar
		getObservable().setMax(requestCount);
		getObservable().setCurrent(0);

		// we use a token size of 100
		MessageSetTokenizer tok = new MessageSetTokenizer(list, 100);

		int counter = 0;
		while (tok.hasNext()) {
			List l = (List) tok.next();
			//MessageSet set = new MessageSet(l.toArray());

			// fetch headers from server
			IMAPResponse[] r =
				getProtocol().fetchHeaderList(
					UIDSetParser.parse(l.toArray()),
					headerFields.toString().trim());

			// parse headers
			for (int i = 0; i < r.length; i++) {
				if (r[i].getResponseSubType().equals("FETCH")) {
					// parse the reponse
					IMAPHeader imapHeader = IMAPHeaderParser.parse(r[i]);
					// consume this line
					r[i] = null;

					// add it to the headerlist
					ColumbaHeader header =
						new ColumbaHeader(imapHeader.getHeader());
					Object uid = imapHeader.getUid();

					header.set("columba.uid", uid);
					header.set("columba.size", imapHeader.getSize());
					
					// set the attachment flag
					
					String contentType = (String) header.get("Content-Type");

					if (contentType != null) {
						if (contentType.indexOf("multipart") != -1)
							header.set("columba.attachment", Boolean.TRUE);
						else
							header.set("columba.attachment", Boolean.FALSE);
					}
					headerList.add(header, uid);
				}

			}

			if (getObservable() != null)
				getObservable().setCurrent(counter++);

			printStatusMessage(
				MailResourceLoader.getString(
					"statusbar",
					"message",
					"fetch_headers"));
		}

	}

	/**
	 * Ensure that we are in login state.
	 * 
	 * @throws Exception
	 */
	public void ensureLoginState() throws Exception {
		if ((getState() == STATE_AUTHENTICATE)
			|| (getState() == STATE_SELECTED)) {
			// ok, we are logged in
		} else {
			// we are in Imap4.STATE_NONAUTHENTICATE
			// -> force new login
			login();

			// synchronize folder list with server
			parent.syncSubscribedFolders();
		}
	}

	/**
	 * Get {@link MimeTree}.
	 * 
	 * @param uid
	 *            message UID
	 * @param path
	 *            mailbox name
	 * @return mimetree
	 * @throws Exception
	 */
	public MimeTree getMimePartTree(Object uid, String path) throws Exception {

		ensureLoginState();
		ensureSelectedState(path);
		try {

			IMAPResponse[] responses = getProtocol().fetchMimePartTree(uid);

			MimeTree mptree = MimeTreeParser.parse(responses);

			aktMessageUid = uid;
			aktMimePartTree = mptree;

			return mptree;
		} catch (BadCommandException ex) {
		} catch (CommandFailedException ex) {
		} catch (DisconnectedException ex) {
			state = STATE_NONAUTHENTICATE;
			getMimePartTree(uid, path);
		}
		return null;
	}

	/**
	 * Get {@link MimePart}.
	 * 
	 * @param uid
	 *            message UID
	 * @param address
	 *            address of MimePart in MimeTree
	 * @param path
	 *            mailbox name
	 * @return mimepart
	 * @throws Exception
	 */
	public MimePart getMimePart(Object uid, Integer[] address, String path)
		throws Exception {

		ensureLoginState();
		ensureSelectedState(path);

		if (!aktMessageUid.equals(uid)) {
			getMimePartTree(uid, path);
		}

		LocalMimePart part =
			new LocalMimePart(
				aktMimePartTree.getFromAddress(address).getHeader());

		try {
			IMAPResponse[] responses =
				getProtocol().fetchMimePart(uid, address);

			part.setBody(MimePartParser.parse(responses[0]));

			return part;
		} catch (BadCommandException ex) {
		} catch (CommandFailedException ex) {
		} catch (DisconnectedException ex) {
			state = STATE_NONAUTHENTICATE;
			getMimePart(uid, address, path);
		}
		return null;
	}

	/**
	 * Get {@link MimePart}.
	 * 
	 * @param uid
	 *            message UID
	 * @param address
	 *            address of MimePart in MimeTree
	 * @param path
	 *            mailbox name
	 * @return mimepart
	 * @throws Exception
	 */
	public Header getHeaders(Object uid, String[] keys, String path)
		throws Exception {

		ensureLoginState();
		ensureSelectedState(path);

		// create string representation
		StringBuffer headerFields = new StringBuffer();
		String name;
		for (int j = 0; j < keys.length - 1; j++) {
			name = (String) keys[j];
			headerFields.append(name);
			headerFields.append(" ");
		}
		headerFields.append(keys[keys.length - 1]);

		try {
			IMAPResponse[] responses =
				getProtocol().fetchHeaderList(
					uid.toString(),
					headerFields.toString());

			IMAPHeader header = IMAPHeaderParser.parse(responses[0]);

			return header.getHeader();
		} catch (BadCommandException ex) {
		} catch (CommandFailedException ex) {
		} catch (DisconnectedException ex) {
			state = STATE_NONAUTHENTICATE;
			return getHeaders(uid, keys, path);
		}
		return null;
	}

	/**
	 * Get {@link MimePart}.
	 * 
	 * @param uid
	 *            message UID
	 * @param address
	 *            address of MimePart in MimeTree
	 * @param path
	 *            mailbox name
	 * @return mimepart
	 * @throws Exception
	 */
	public MimePart getMimePartSource(
		Object uid,
		Integer[] address,
		String path)
		throws Exception {

		ensureLoginState();
		ensureSelectedState(path);

		if (!aktMessageUid.equals(uid)) {
			getMimePartTree(uid, path);
		}

		LocalMimePart part =
			new LocalMimePart(
				aktMimePartTree.getFromAddress(address).getHeader());

		try {
			IMAPResponse[] responses =
				getProtocol().fetchMimePartHeader(uid, address);

			Source headerSource = MimePartParser.parse(responses[0]);

			responses = getProtocol().fetchMimePart(uid, address);

			Source bodySource = MimePartParser.parse(responses[0]);

			ConcatenatedSource mimepartSource = new ConcatenatedSource();
			mimepartSource.addSource(headerSource);
			mimepartSource.addSource(bodySource);

			part.setBody(mimepartSource);

			return part;
		} catch (BadCommandException ex) {
		} catch (CommandFailedException ex) {
		} catch (DisconnectedException ex) {
			state = STATE_NONAUTHENTICATE;
			getMimePart(uid, address, path);
		}
		return null;
	}

	/**
	 * Get complete message source.
	 * 
	 * @param uid
	 *            message UID
	 * @param path
	 *            mailbox name
	 * @return message source
	 * @throws Exception
	 */
	public String getMessageSource(Object uid, String path) throws Exception {

		ensureLoginState();
		ensureSelectedState(path);

		try {
			IMAPResponse[] responses = getProtocol().fetchMessageSource(uid);

			String source = MessageSourceParser.parse(responses);

			return source;
		} catch (BadCommandException ex) {
		} catch (CommandFailedException ex) {
		} catch (DisconnectedException ex) {
			state = STATE_NONAUTHENTICATE;
			getMessageSource(uid, path);
		}
		return null;
	}

	/**
	 * Mark message as specified by variant.
	 * <p>
	 * See {@link MarkMessageCommand}for a list of variants.
	 * <p>
	 * We mark messages in pieces of 100 headers. This means we tokenize the
	 * <code>list</code> in sublists of the size of 100. Then we execute the
	 * command and process those 100 results.
	 * 
	 * @param uids
	 *            message UID
	 * @param variant
	 *            variant (read/flagged/expunged/etc.)
	 * @param path
	 *            mailbox name
	 * @throws Exception
	 */
	public void markMessage(Object[] uids, int variant, String path)
		throws Exception {

		ensureLoginState();
		ensureSelectedState(path);

		try {

			// we use a token size of 100
			MessageSetTokenizer tok = new MessageSetTokenizer(uids, 100);

			while (tok.hasNext()) {
				List list = (List) tok.next();
				//MessageSet set = new MessageSet(list.toArray());

				String flagsString = parseVariant(variant);
				ColumbaLogger.log.debug("flags=" + flagsString);

				// unset flags command
				if (variant >= 4) {
					IMAPResponse[] responses =
						getProtocol().removeFlags(
							UIDSetParser.parse(list.toArray()),
							flagsString,
							true);
				} else {
					IMAPResponse[] responses =
						getProtocol().storeFlags(
							UIDSetParser.parse(list.toArray()),
							flagsString,
							true);
				}

			}

		} catch (BadCommandException ex) {
		} catch (CommandFailedException ex) {
		} catch (DisconnectedException ex) {
			state = STATE_NONAUTHENTICATE;
			markMessage(uids, variant, path);
		}
	}

	/**
	 * Search messages.
	 * 
	 * @param uids
	 *            message UIDs
	 * @param filterRule
	 *            filter rules
	 * @param path
	 *            mailbox name
	 * @return list of UIDs which match filter rules
	 * @throws Exception
	 */
	public LinkedList search(Object[] uids, FilterRule filterRule, String path)
		throws Exception {
		LinkedList result = new LinkedList();

		ensureLoginState();
		ensureSelectedState(path);

		try {
			printStatusMessage(
				MessageFormat.format(
					MailResourceLoader.getString(
						"statusbar",
						"message",
						"search_in"),
					new Object[] { path }));

			MessageSet set = new MessageSet(uids);

			SearchRequestBuilder b = new SearchRequestBuilder();
			b.setCharset("UTF-8");
			List list = b.generateSearchArguments(filterRule);
			Arguments searchArguments =
				b.generateSearchArguments(filterRule, list);

			IMAPResponse[] responses = null;

			// try to use UTF-8 first
			// -> fall back to system default charset
			try {
				responses =
					imap.searchWithCharsetSupport("UTF-8", searchArguments);
			} catch (BadCommandException ex) {
				// this probably means that UTF-8 isn't support by server
				// -> lets try the system default charset instead

				try {
					String charset =
						(String) System.getProperty("file.encoding");
					b.setCharset(charset);
					list = b.generateSearchArguments(filterRule);
					searchArguments =
						b.generateSearchArguments(filterRule, list);
					responses =
						imap.searchWithCharsetSupport(charset, searchArguments);
				} catch (BadCommandException ex2) {
					// this is the last possible fall back

					String charset = "US-ASCII";
					b.setCharset(charset);
					list = b.generateSearchArguments(filterRule);
					searchArguments =
						b.generateSearchArguments(filterRule, list);
					responses = imap.search(searchArguments);
				}
			}

			result = SearchResultParser.parse(responses);

			//result = convertIndexToUid(result, worker);

			return result;
		} catch (BadCommandException ex) {
		} catch (CommandFailedException ex) {
		} catch (DisconnectedException ex) {
			state = STATE_NONAUTHENTICATE;
			//search(uids, searchString, path, worker);
		}
		return null;
	}

	/**
	 * @param filterRule
	 * @param path
	 * @return @throws
	 *         Exception
	 */
	public LinkedList search(FilterRule filterRule, String path)
		throws Exception {
		LinkedList result = new LinkedList();

		ensureLoginState();
		ensureSelectedState(path);

		try {
			//MessageSet set = new MessageSet(uids);
			printStatusMessage(
				MessageFormat.format(
					MailResourceLoader.getString(
						"statusbar",
						"message",
						"search_in"),
					new Object[] { path }));
			SearchRequestBuilder b = new SearchRequestBuilder();
			b.setCharset("UTF-8");
			List list = b.generateSearchArguments(filterRule);
			Arguments searchArguments =
				b.generateSearchArguments(filterRule, list);

			IMAPResponse[] responses = null;

			// try to use UTF-8 first
			// -> fall back to system default charset
			try {
				responses =
					imap.searchWithCharsetSupport("UTF-8", searchArguments);
			} catch (BadCommandException ex) {
				// this probably means that UTF-8 isn't support by server
				// -> lets try the system default charset instead

				try {
					String charset =
						(String) System.getProperty("file.encoding");
					b.setCharset(charset);
					list = b.generateSearchArguments(filterRule);
					searchArguments =
						b.generateSearchArguments(filterRule, list);
					responses =
						imap.searchWithCharsetSupport(charset, searchArguments);
				} catch (BadCommandException ex2) {
					// this is the last possible fall back

					String charset = "US-ASCII";
					b.setCharset(charset);
					list = b.generateSearchArguments(filterRule);
					searchArguments =
						b.generateSearchArguments(filterRule, list);
					responses = imap.search(searchArguments);
				}
			}

			result = SearchResultParser.parse(responses);

			return result;
		} catch (BadCommandException ex) {
		} catch (CommandFailedException ex) {
		} catch (DisconnectedException ex) {
			state = STATE_NONAUTHENTICATE;
			//search(searchString, path, worker);
		}
		return null;
	}

	/**
	 * Check if string contains US-ASCII characters.
	 * 
	 * @param s
	 * @return true, if string contains US-ASCII characters
	 */
	protected static boolean isAscii(String s) {
		int l = s.length();

		for (int i = 0; i < l; i++) {
			if ((int) s.charAt(i) > 0177) // non-ascii
				return false;
		}
		return true;
	}

	/**
	 * Create string representation of {@ link MarkMessageCommand}constants.
	 * 
	 * @param variant
	 * @return
	 */
	private String parseVariant(int variant) {
		StringBuffer buf = new StringBuffer();
		List arg = new Vector();
		switch (variant) {
			case MarkMessageCommand.MARK_AS_READ :
			case MarkMessageCommand.MARK_AS_UNREAD :
				{
					arg.add("\\Seen");
					break;
				}
			case MarkMessageCommand.MARK_AS_FLAGGED :
			case MarkMessageCommand.MARK_AS_UNFLAGGED :
				{
					arg.add("\\Flagged");
					break;
				}
			case MarkMessageCommand.MARK_AS_EXPUNGED :
			case MarkMessageCommand.MARK_AS_UNEXPUNGED :
				{
					arg.add("\\Deleted");
					break;
				}
			case MarkMessageCommand.MARK_AS_ANSWERED :
				{
					arg.add("\\Answered");
					break;
				}
		}

		//if (arg.size() > 1)
		buf.append("(");
		for (int i = 0; i < arg.size(); i++) {
			buf.append((String) arg.get(i));
			if (i != arg.size() - 1)
				buf.append(" ");
		}
		//if (arg.size() > 1)
		buf.append(")");

		return buf.toString();
	}

	/**
	 * @return
	 */
	public MessageFolderInfo getSelectedFolderMessageFolderInfo() {
		return messageFolderInfo;
	}

}