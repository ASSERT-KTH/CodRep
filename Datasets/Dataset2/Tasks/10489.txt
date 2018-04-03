public IMailboxInfo getMessageFolderInfo();

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
//The Initial Developers of the Original Code are Frederik Dietz and Timo
// Stich.
//Portions created by Frederik Dietz and Timo Stich are Copyright (C) 2003.
//
//All Rights Reserved.

package org.columba.mail.folder;

import java.io.File;
import java.io.IOException;
import java.io.InputStream;

import org.columba.api.command.IStatusObservable;
import org.columba.core.filter.Filter;
import org.columba.core.filter.FilterList;
import org.columba.mail.message.IHeaderList;
import org.columba.ristretto.message.Attributes;
import org.columba.ristretto.message.Flags;
import org.columba.ristretto.message.Header;
import org.columba.ristretto.message.MailboxInfo;
import org.columba.ristretto.message.MimeTree;

/**
 * Every mailbox which actually containss message should implement this
 * interface.
 * <p>
 * Note, that this also means to subclass {@link Folder}.
 * 
 * @author fdietz
 */
public interface IMailbox extends IMailFolder {

	/**
	 * Get the {@link MailboxInfo} of this mailbox
	 * 
	 * @return
	 * @throws IOException
	 */
	public MailboxInfo getMessageFolderInfo();

	/**
	 * Removes all messages which are marked as expunged
	 * 
	 * @throws Exception
	 */
	public void expungeFolder() throws Exception;

	/**
	 * Checks if message with uid exists in this folder.
	 * 
	 * @param uid
	 *            UID of message
	 * @return boolean true, if message exists. False, otherwise.
	 * @throws Exception
	 */
	public boolean exists(Object uid) throws Exception;

	/**
	 * Return list of headers.
	 * 
	 * @return HeaderList list of headers
	 * @throws Exception
	 */
	public IHeaderList getHeaderList() throws Exception;

	/**
	 * Mark messages as read/flagged/expunged/etc.
	 * 
	 * See <code>MarkMessageCommand</code> for more information especially concerning
	 * the variant value.
	 * 
	 * @param uid
	 *            array of UIDs
	 * @param variant
	 *            variant can be a value between 0 and 6
	 * @throws Exception
	 */
	public abstract void markMessage(Object[] uids, int variant)
			throws Exception;

	/**
	 * Return mimepart structure. See <class>MimePartTree </class> for more
	 * details.
	 * 
	 * @param uid
	 *            UID of message
	 * @return MimePartTree return mimepart structure
	 * @throws Exception
	 */
	public MimeTree getMimePartTree(Object uid) throws Exception;

	/**
	 * Copy messages identified by UID to this folder.
	 * <p>
	 * This method is necessary for optimization reasons.
	 * <p>
	 * Think about using local and remote folders. If we would have only methods
	 * to add/remove messages this wouldn't be very efficient when moving
	 * messages between for example IMAP folders on the same server. We would
	 * have to download a complete message to remove it and then upload it again
	 * to add it to the destination folder.
	 * <p>
	 * Using the innercopy method the IMAP server can use its COPY command to
	 * move the message on the server-side.
	 * 
	 * @param destFolder
	 *            the destination folder of the copy operation
	 * @param uids
	 *            an array of UID's identifying the messages
	 * @throws Exception
	 */
	public void innerCopy(IMailbox destFolder, Object[] uids) throws Exception;

	/**
	 * Adds a message to this Mailbox
	 * 
	 * @param in
	 *            The message InputStream
	 * @return The new uid of the added message or null if not defined
	 * @throws Exception
	 */
	public Object addMessage(InputStream in) throws Exception;

	/**
	 * Adds a message to this Mailbox
	 * 
	 * @param in
	 *            The message InputStream
	 * @param attributes
	 *            The attributes of the message
	 * @param flags
	 *            the flags of the message
	 * @return The new uid of the added message or null if not defined
	 * @throws Exception
	 */
	public Object addMessage(InputStream in, Attributes attributes, Flags flags)
			throws Exception;

	/**
	 * Gets all specified headerfields. An example headerfield might be
	 * "Subject" or "From" (take care of lower/uppercaseletters).
	 * <p>
	 * Note, that you should use getAttributes() for fetching the internal
	 * headerfields (for example: columba.subject, columba.flags.seen, etc.).
	 * <p>
	 * This method first tries to find the requested header in the header cache
	 * (@see CachedFolder). If the headerfield is not cached, the message source
	 * is parsed.
	 * 
	 * @param uid
	 *            The uid of the desired message
	 * @param keys
	 *            The keys like defined in e.g. RFC2822
	 * @return A {@link Header}containing the headerfields if they were present
	 * @throws Exception
	 */
	public Header getHeaderFields(Object uid, String[] keys) throws Exception;

	/**
	 * Gets the InputStream from the body of the mimepart. This excludes the
	 * header. If the stream was encoded with QuotedPrintable or Base64 decoding
	 * is already done.
	 * 
	 * @param uid
	 *            The UID of the message
	 * @param address
	 *            The address of the mimepart
	 * @return
	 * @throws Exception
	 */
	public InputStream getMimePartBodyStream(Object uid, Integer[] address)
			throws Exception;

	/**
	 * Gets the InputStream from the complete mimepart. This includes the
	 * header.
	 * 
	 * @param uid
	 *            The UID of the message
	 * @param address
	 *            address The address of the mimepart
	 * @return
	 * @throws Exception
	 */
	public InputStream getMimePartSourceStream(Object uid, Integer[] address)
			throws Exception;

	/**
	 * Gets the InputStream of the complete messagesource.
	 * 
	 * @param uid
	 *            The UID of the message
	 * @return
	 * @throws Exception
	 */
	public InputStream getMessageSourceStream(Object uid) throws Exception;

	/**
	 * Gets the Flags of the message.
	 * 
	 * @param uid
	 *            The UID of the message
	 * @return
	 * @throws Exception
	 */
	public Flags getFlags(Object uid) throws Exception;

	/**
	 * Gets a attribute from the message
	 * 
	 * @param uid
	 *            The UID of the message
	 * @param key
	 *            The name of the attribute (e.g. "columba.subject",
	 *            "columba.size")
	 * @return
	 * @throws Exception
	 */
	public Object getAttribute(Object uid, String key) throws Exception;

	/**
	 * Gets the attributes from the message
	 * 
	 * @param uid
	 *            The UID of the message
	 * @return
	 * @throws Exception
	 */
	public Attributes getAttributes(Object uid) throws Exception;

	/**
	 * Set attribute for message with UID.
	 * 
	 * @param uid
	 *            UID of message
	 * @param key
	 *            name of attribute (e.g."columba.subject");
	 * @param value
	 *            value of attribute
	 * @throws Exception
	 */
	public void setAttribute(Object uid, String key, Object value)
			throws Exception;

	/**
	 * Return array of uids this folder contains.
	 * 
	 * @return Object[] array of all UIDs this folder contains
	 */
	public Object[] getUids() throws Exception;

	/**
	 * Get all email headers.
	 * 
	 * @param uid
	 *            message uid
	 * @return complete email headers
	 * @throws Exception
	 */
	public Header getAllHeaderFields(Object uid) throws Exception;

	public Object[] searchMessages(Filter filter) throws Exception;

	public Object[] searchMessages(Filter filter, Object[] uids)
			throws Exception;

	/**
	 * Is this mailbox read-only?
	 * 
	 * @return 
	 * 
	 */
	public boolean isReadOnly();

	IStatusObservable getObservable();

	Object getLastSelection();

	void setLastSelection(Object lastSel);

	FilterList getFilterList();

	public File getDirectoryFile();

	public boolean isInboxFolder();

	public boolean isTrashFolder();
}