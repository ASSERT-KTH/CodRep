Assert.isNotNull(fName);

/****************************************************************************
 * Copyright (c) 2007 Composent, Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Composent, Inc. - initial API and implementation
 *****************************************************************************/

package org.eclipse.ecf.docshare;

import java.io.File;
import java.io.IOException;
import java.io.InvalidObjectException;
import java.io.OutputStream;
import java.util.Hashtable;

import org.eclipse.core.filesystem.EFS;
import org.eclipse.core.filesystem.IFileStore;
import org.eclipse.core.runtime.Assert;
import org.eclipse.core.runtime.CoreException;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Status;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.util.ECFException;
import org.eclipse.ecf.datashare.AbstractShare;
import org.eclipse.ecf.datashare.IChannelContainerAdapter;
import org.eclipse.ecf.datashare.events.IChannelDisconnectEvent;
import org.eclipse.ecf.docshare.messages.Message;
import org.eclipse.ecf.docshare.messages.StartMessage;
import org.eclipse.ecf.docshare.messages.StopMessage;
import org.eclipse.ecf.docshare.messages.UpdateMessage;
import org.eclipse.ecf.internal.docshare.Activator;
import org.eclipse.ecf.internal.docshare.Messages;
import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.jface.text.DocumentEvent;
import org.eclipse.jface.text.IDocument;
import org.eclipse.jface.text.IDocumentListener;
import org.eclipse.osgi.util.NLS;
import org.eclipse.swt.custom.StyledText;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Display;
import org.eclipse.ui.IEditorDescriptor;
import org.eclipse.ui.IEditorInput;
import org.eclipse.ui.IEditorRegistry;
import org.eclipse.ui.IWorkbench;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.editors.text.EditorsUI;
import org.eclipse.ui.texteditor.IDocumentProvider;
import org.eclipse.ui.texteditor.ITextEditor;

/**
 * Represents a document sharing session between two participants.
 */
public class DocShare extends AbstractShare {

	private static final Hashtable docsharechannels = new Hashtable();

	public static DocShare getDocShare(ID containerID) {
		return (DocShare) docsharechannels.get(containerID);
	}

	public static DocShare addDocShare(ID containerID, IChannelContainerAdapter channelAdapter) throws ECFException {
		return (DocShare) docsharechannels.put(containerID, new DocShare(channelAdapter));
	}

	public static DocShare removeDocShare(ID containerID) {
		return (DocShare) docsharechannels.remove(containerID);
	}

	/**
	 * The ID of the initiator
	 */
	ID initiatorID;
	/**
	 * The ID of the receiver.  
	 */
	ID receiverID;
	/**
	 * Our ID
	 */
	ID ourID;
	/**
	 * Text editor
	 */
	ITextEditor editor;
	/**
	 * Content that we have received via start message, before user has responded
	 * to question about whether or not to display in editor.  Should be null
	 * at all other times.
	 */
	String startContent = null;
	/**
	 * Object to use as lock for changing connected state of this docshare instance
	 */
	Object stateLock = new Object();

	/**
	 * The document listener is the listener for changes to the *local* copy of the 
	 * IDocument.  This listener is responsible for sending document update messages when 
	 * notified.
	 */
	IDocumentListener documentListener = new IDocumentListener() {
		public void documentAboutToBeChanged(DocumentEvent event) {
			// nothing to do
		}

		public void documentChanged(DocumentEvent event) {
			// If the channel is gone, then no reason to handle this.
			if (getChannel() == null || !Activator.getDefault().isListenerActive()) {
				return;
			}
			// If the listener is not active, ignore input
			if (!Activator.getDefault().isListenerActive()) {
				//The local editor is being updated by an remote peer, so we do not
				//wish to echo this change.
				return;
			}
			// Otherwise end update message
			sendUpdateMessage(event);
		}
	};

	public DocShare(IChannelContainerAdapter adapter) throws ECFException {
		super(adapter);
	}

	public ID getInitiatorID() {
		return initiatorID;
	}

	public ID getReceiverID() {
		return receiverID;
	}

	public ID getOurID() {
		return ourID;
	}

	public ITextEditor getTextEditor() {
		return this.editor;
	}

	public boolean isSharing() {
		synchronized (stateLock) {
			return (this.editor != null);
		}
	}

	public ID getOtherID() {
		synchronized (stateLock) {
			if (isInitiator())
				return receiverID;
			return initiatorID;
		}
	}

	public boolean isInitiator() {
		synchronized (stateLock) {
			if (ourID == null || initiatorID == null || receiverID == null)
				return false;
			return ourID.equals(initiatorID);
		}
	}

	public void startShare(final ID our, final String fromName, final ID toID, final String fileName, final ITextEditor editorPart) {
		Assert.isNotNull(our);
		final String fName = (fromName == null) ? our.getName() : fromName;
		Assert.isNotNull(toID);
		Assert.isNotNull(fileName);
		Assert.isNotNull(editorPart);
		Display.getDefault().syncExec(new Runnable() {
			public void run() {
				try {
					// Get content from local document
					final String content = editorPart.getDocumentProvider().getDocument(editorPart.getEditorInput()).get();
					// send start message
					send(toID, new StartMessage(our, fName, toID, content, fileName));
					// Set local sharing start (to setup doc listener)
					localStartShare(our, our, toID, editorPart);
				} catch (final Exception e) {
					logError(Messages.DocShare_ERROR_STARTING_EDITOR_TITLE, e);
					showErrorToUser(Messages.DocShare_ERROR_STARTING_EDITOR_TITLE, NLS.bind(Messages.DocShare_ERROR_STARTING_EDITOR_MESSAGE, e.getLocalizedMessage()));
				}
			}
		});
	}

	public void stopShare() {
		if (isSharing()) {
			// send stop message to other
			sendStopMessage();
		}
		localStopShare();
	}

	void send(ID toID, Message message) throws Exception {
		super.sendMessage(toID, message.serialize());
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.datashare.AbstractShare#handleMessage(org.eclipse.ecf.core.identity.ID, byte[])
	 */
	protected void handleMessage(ID fromContainerID, byte[] data) {
		try {
			final Message message = Message.deserialize(data);
			Assert.isNotNull(message);
			if (message instanceof StartMessage) {
				handleStartMessage((StartMessage) message);
			} else if (message instanceof UpdateMessage) {
				handleUpdateMessage((UpdateMessage) message);
			} else if (message instanceof StopMessage) {
				handleStopMessage((StopMessage) message);
			} else {
				throw new InvalidObjectException(NLS.bind(Messages.DocShare_EXCEPTION_INVALID_MESSAGE, message.getClass().getName()));
			}
		} catch (final Exception e) {
			logError(Messages.DocShare_EXCEPTION_HANDLE_MESSAGE, e);
		}
	}

	/**
	 * @param message
	 */
	protected void handleStartMessage(final StartMessage message) {
		final ID senderID = message.getSenderID();
		Assert.isNotNull(senderID);
		final String senderUsername = message.getSenderUsername();
		Assert.isNotNull(senderUsername);
		final ID our = message.getReceiverID();
		Assert.isNotNull(our);
		final String filename = message.getFilename();
		Assert.isNotNull(filename);
		final String documentContent = message.getDocumentContent();
		Assert.isNotNull(documentContent);
		// First synchronize on any state changes by getting stateLock
		synchronized (stateLock) {
			// If we are already sharing, or have non-null start content
			if (isSharing() || startContent != null) {
				sendStopMessage(senderID);
				// And we're done
				return;
			}
			// Otherwise set start content to the message-provided documentContent
			startContent = documentContent;
		}
		// Then open UI and show text editor if appropriate
		Display.getDefault().asyncExec(new Runnable() {
			public void run() {
				try {
					// First, ask user if they want to receive the doc
					if (openReceiverDialog(senderID, senderUsername, filename)) {
						// If so, then we create a new DocShareEditorInput
						final DocShareEditorInput dsei = new DocShareEditorInput(getTempFileStore(senderUsername, filename, startContent), senderUsername, filename);
						// Then open up text editor
						final ITextEditor ep = (ITextEditor) PlatformUI.getWorkbench().getActiveWorkbenchWindow().getActivePage().openEditor(dsei, getEditorIdForFileName(filename));
						// Then change our local state
						localStartShare(our, senderID, our, ep);
					} else {
						// Send stop message to initiator
						sendStopMessage();
						// Then we stop the local share
						localStopShare();
					}
				} catch (final Exception e) {
					logError(Messages.DocShare_EXCEPTION_RECEIVING_MESSAGE_TITLE, e);
					showErrorToUser(Messages.DocShare_EXCEPTION_RECEIVING_MESSAGE_TITLE, NLS.bind(Messages.DocShare_EXCEPTION_RECEIVING_MESSAGE_MESSAGE, e.getLocalizedMessage()));
				}
			}
		});
	}

	void modifyStartContent(int offset, int length, String text) {
		final StringBuffer result = new StringBuffer(startContent.substring(0, offset));
		result.append(text);
		result.append(startContent.substring(offset + length));
		startContent = result.toString();
	}

	/**
	 * @param message
	 */
	protected void handleUpdateMessage(final UpdateMessage message) {
		final int offset = message.getOffset();
		Assert.isTrue(offset > -1);
		final int length = message.getLength();
		Assert.isTrue(length > -1);
		final String text = message.getText();
		Assert.isTrue(text != null);
		synchronized (stateLock) {
			// If we're waiting on user to start then change the startContent directly
			if (startContent != null) {
				modifyStartContent(offset, length, text);
				// And we're done
				return;
			}
		}
		// Else replace in document directly
		Display.getDefault().asyncExec(new Runnable() {
			public void run() {
				try {
					final IDocument document = getDocumentFromEditor();
					if (document != null) {
						// We setup editor to not take input while we are changing document
						setEditorToRefuseInput();
						document.replace(offset, length, text);
					}
				} catch (final Exception e) {
					logError(Messages.DocShare_EXCEPTION_RECEIVING_MESSAGE_TITLE, e);
					showErrorToUser(Messages.DocShare_EXCEPTION_RECEIVING_MESSAGE_TITLE, NLS.bind(Messages.DocShare_EXCEPTION_RECEIVING_MESSAGE_MESSAGE, e.getLocalizedMessage()));
				} finally {
					// Have editor accept input
					setEditorToAcceptInput();
				}
			}
		});
	}

	/**
	 * @param message
	 */
	protected void handleStopMessage(StopMessage message) {
		if (isSharing()) {
			localStopShare();
		}
	}

	void setEditorToRefuseInput() {
		setEditorEditable(false);
		Activator.getDefault().setListenerActive(false);
	}

	void setEditorToAcceptInput() {
		setEditorEditable(true);
		Activator.getDefault().setListenerActive(true);
	}

	IEditorInput getEditorInput() {
		synchronized (stateLock) {
			if (editor == null)
				return null;
			return editor.getEditorInput();
		}
	}

	boolean openReceiverDialog(ID fromID, String fromUsername, String fileName) {
		return MessageDialog.openQuestion(null, Messages.DocShare_EDITOR_SHARE_POPUP_TITLE, NLS.bind(Messages.DocShare_EDITOR_SHARE_POPUP_MESSAGE, fromUsername, fileName));
	}

	protected void handleDisconnectEvent(IChannelDisconnectEvent cde) {
		super.handleDisconnectEvent(cde);
		localStopShare();
	}

	IFileStore getTempFileStore(String fromUsername, String fileName, String content) throws IOException, CoreException {
		final IFileStore fileStore = EFS.getLocalFileSystem().fromLocalFile(File.createTempFile(fromUsername, fileName));
		final OutputStream outs = fileStore.openOutputStream(EFS.OVERWRITE, null);
		outs.write(content.getBytes());
		outs.close();
		return fileStore;
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.datashare.AbstractShare#dispose()
	 */
	public synchronized void dispose() {
		localStopShare();
		super.dispose();
	}

	void logError(IStatus status) {
		Activator.getDefault().getLog().log(status);
	}

	void showErrorToUser(String title, String message) {
		MessageDialog.openError(null, title, message);
	}

	void logError(String exceptionString, Throwable e) {
		Activator.getDefault().getLog().log(new Status(IStatus.ERROR, Activator.PLUGIN_ID, IStatus.ERROR, exceptionString, e));
	}

	StyledText getTextControl() {
		synchronized (stateLock) {
			if (editor == null)
				return null;
			return (StyledText) editor.getAdapter(Control.class);
		}
	}

	void setEditorEditable(final boolean editable) {
		final StyledText textControl = getTextControl();
		if (textControl != null && !textControl.isDisposed()) {
			Display.getDefault().syncExec(new Runnable() {
				public void run() {
					textControl.setEditable(editable);
				}
			});
		}
	}

	String getEditorIdForFileName(String fileName) {
		final IWorkbench wb = PlatformUI.getWorkbench();
		final IEditorRegistry er = wb.getEditorRegistry();
		final IEditorDescriptor desc = er.getDefaultEditor(fileName);
		if (desc != null)
			return desc.getId();
		return EditorsUI.DEFAULT_TEXT_EDITOR_ID;
	}

	IDocument getDocumentFromEditor() {
		synchronized (stateLock) {
			if (editor == null)
				return null;
			final IDocumentProvider documentProvider = editor.getDocumentProvider();
			if (documentProvider == null)
				return null;
			return documentProvider.getDocument(editor.getEditorInput());
		}
	}

	void localStartShare(ID our, ID initiator, ID receiver, ITextEditor edt) {
		synchronized (stateLock) {
			localStopShare();
			this.ourID = our;
			this.initiatorID = initiator;
			this.receiverID = receiver;
			this.editor = edt;
			final IDocument doc = getDocumentFromEditor();
			if (doc != null)
				doc.addDocumentListener(documentListener);
		}
	}

	void localStopShare() {
		synchronized (stateLock) {
			this.ourID = null;
			this.initiatorID = null;
			this.receiverID = null;
			this.startContent = null;
			final IDocument doc = getDocumentFromEditor();
			if (doc != null)
				doc.removeDocumentListener(documentListener);
			this.editor = null;
		}
	}

	void sendUpdateMessage(DocumentEvent event) {
		if (isSharing()) {
			try {
				send(getOtherID(), new UpdateMessage(event.getOffset(), event.getLength(), event.getText()));
			} catch (final Exception e) {
				logError(Messages.DocShare_EXCEPTION_SEND_MESSAGE, e);
			}
		}
	}

	void sendStopMessage() {
		sendStopMessage(getOtherID());
	}

	void sendStopMessage(ID other) {
		if (isSharing()) {
			try {
				send(other, new StopMessage());
			} catch (final Exception e) {
				logError(Messages.DocShare_EXCEPTION_SEND_MESSAGE, e);
			}
		}
	}

}