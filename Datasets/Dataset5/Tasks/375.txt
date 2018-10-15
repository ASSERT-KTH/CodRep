import org.eclipse.ecf.provider.xmpp.identity.XMPPID;

/****************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Composent, Inc. - initial API and implementation
 *****************************************************************************/
package org.eclipse.ecf.internal.provider.xmpp.filetransfer;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;

import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDCreateException;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.filetransfer.IFileTransferInfo;
import org.eclipse.ecf.filetransfer.IFileTransferListener;
import org.eclipse.ecf.filetransfer.IOutgoingFileTransfer;
import org.eclipse.ecf.filetransfer.events.IFileTransferEvent;
import org.eclipse.ecf.filetransfer.events.IOutgoingFileTransferResponseEvent;
import org.eclipse.ecf.filetransfer.events.IOutgoingFileTransferSendDataEvent;
import org.eclipse.ecf.filetransfer.events.IOutgoingFileTransferSendDoneEvent;
import org.eclipse.ecf.internal.provider.xmpp.identity.XMPPID;
import org.jivesoftware.smack.XMPPException;
import org.jivesoftware.smackx.filetransfer.FileTransfer;
import org.jivesoftware.smackx.filetransfer.FileTransferManager;
import org.jivesoftware.smackx.filetransfer.OutgoingFileTransfer;
import org.jivesoftware.smackx.filetransfer.FileTransfer.Status;
import org.jivesoftware.smackx.filetransfer.OutgoingFileTransfer.NegotiationProgress;

public class XMPPOutgoingFileTransfer implements IOutgoingFileTransfer {

	private static final int BUFFER_SIZE = 4096;

	ID sessionID;
	XMPPID remoteTarget;
	IFileTransferInfo transferInfo;
	IFileTransferListener listener;
	FileTransferManager manager;

	File localFile;

	long fileSize;

	OutgoingFileTransfer outgoingFileTransfer;

	long amountWritten = 0;

	Status status;

	Exception exception;

	public XMPPOutgoingFileTransfer(FileTransferManager manager,
			XMPPID remoteTarget, IFileTransferInfo fileTransferInfo,
			IFileTransferListener listener) {
		this.manager = manager;
		this.remoteTarget = remoteTarget;
		this.transferInfo = fileTransferInfo;
		this.listener = listener;
		this.sessionID = createSessionID();
		String fullyQualifiedName = remoteTarget.getFQName();
		outgoingFileTransfer = manager.createOutgoingFileTransfer(fullyQualifiedName);
	}

	private ID createSessionID() {
		try {
			return IDFactory.getDefault().createGUID();
		} catch (IDCreateException e) {
			throw new NullPointerException(
					"cannot create id for XMPPOutgoingFileTransfer");
		}
	}

	public synchronized ID getRemoteTargetID() {
		return remoteTarget;
	}

	public ID getID() {
		return sessionID;
	}

	private void fireTransferListenerEvent(IFileTransferEvent event) {
		listener.handleTransferEvent(event);
	}

	private void setStatus(Status s) {
		this.status = s;
	}

	private void setException(Exception e) {
		this.exception = e;
	}

	private Status getStatus() {
		return this.status;
	}

	NegotiationProgress progress = new NegotiationProgress();

	public synchronized void startSend(File localFile, String description)
			throws XMPPException {
		this.localFile = localFile;
		this.fileSize = localFile.length();
		setStatus(Status.INITIAL);
		// outgoingFileTransfer.sendFile(localFile, description);
		outgoingFileTransfer.sendFile(localFile.getAbsolutePath(),
				this.fileSize, description, progress);

		Thread transferThread = new Thread(new Runnable() {
			public void run() {
				setStatus(outgoingFileTransfer.getStatus());
				boolean negotiation = true;
				while (negotiation) {
					// check the state of the progress
					try {
						Thread.sleep(300);
					} catch (InterruptedException e) {
						return;
					}
					Status s = progress.getStatus();
					setStatus(s);
					final boolean negotiated = getStatus().equals(
							Status.NEGOTIATED);
					if (s.equals(Status.NEGOTIATED) || s.equals(Status.CANCLED)
							|| s.equals(Status.COMPLETE)
							|| s.equals(Status.ERROR)
							|| s.equals(Status.REFUSED)) {
						fireTransferListenerEvent(new IOutgoingFileTransferResponseEvent() {
							private static final long serialVersionUID = -5940612388464073240L;

							public boolean requestAccepted() {
								return negotiated;
							}

							public IOutgoingFileTransfer getSource() {
								return XMPPOutgoingFileTransfer.this;
							}

							public String toString() {
								StringBuffer buf = new StringBuffer(
										"OutgoingFileTransferResponseEvent[");
								buf.append("requestAccepted=").append(
										requestAccepted()).append("]");
								return buf.toString();
							}
						});
						// And negotiation is over
						negotiation = false;
					}
				}

				OutputStream outs = progress.getOutputStream();

				if (outs == null)
					return;

				InputStream inputStream = null;

				try {
					inputStream = new FileInputStream(
							XMPPOutgoingFileTransfer.this.localFile);
					writeToStream(inputStream, outs);
				} catch (FileNotFoundException e) {
					setStatus(FileTransfer.Status.ERROR);
					setException(e);
				} catch (XMPPException e) {
					setStatus(FileTransfer.Status.ERROR);
					setException(e);
				} finally {
					setStatus(Status.COMPLETE);
					try {
						if (inputStream != null) {
							inputStream.close();
						}
					} catch (IOException e) {
						/* Do Nothing */
					}
					try {
						outs.flush();
						outs.close();
					} catch (IOException e) {
						/* Do Nothing */
					}
					// Then notify that the sending is done
					fireTransferListenerEvent(new IOutgoingFileTransferSendDoneEvent() {
						private static final long serialVersionUID = -6315336868737148845L;

						public IOutgoingFileTransfer getSource() {
							return XMPPOutgoingFileTransfer.this;
						}

						public String toString() {
							StringBuffer buf = new StringBuffer(
									"IOutgoingFileTransferSendDoneEvent[");
							buf.append("isDone="+getSource().isDone());
							buf.append(";bytesSent=").append(
									getSource().getBytesSent()).append(
									"]");
							return buf.toString();
						}

					});
				}
			}
		}, "ECF XMPP file send");

		transferThread.start();
	}

	public synchronized void cancel() {
		setStatus(Status.CANCLED);
	}

	public synchronized File getLocalFile() {
		return localFile;
	}

	public Object getAdapter(Class adapter) {
		return null;
	}

	public long getBytesSent() {
		return amountWritten;
	}

	public Exception getException() {
		return exception;
	}

	public double getPercentComplete() {
		return (fileSize <= 0) ? 1.0 : (((double) amountWritten) / ((double) fileSize));
	}

	public boolean isDone() {
		return status == Status.CANCLED || status == Status.ERROR
				|| status == Status.COMPLETE;
	}

	public ID getSessionID() {
		return sessionID;
	}

	protected void writeToStream(final InputStream in, final OutputStream out)
			throws XMPPException {
		final byte[] b = new byte[BUFFER_SIZE];
		int count = 0;
		amountWritten = 0;

		do {
			try {
				out.write(b, 0, count);
			} catch (IOException e) {
				throw new XMPPException("error writing to output stream", e);
			}

			amountWritten += count;

			if (count > 0) {
				fireTransferListenerEvent(new IOutgoingFileTransferSendDataEvent() {
					private static final long serialVersionUID = 2327297070577249812L;
	
					public IOutgoingFileTransfer getSource() {
						return XMPPOutgoingFileTransfer.this;
					}
	
					public String toString() {
						StringBuffer buf = new StringBuffer(
								"IOutgoingFileTransferSendDataEvent[");
						buf.append("bytesSent=").append(getSource().getBytesSent());
						buf.append(";percentComplete=").append(
								getSource().getPercentComplete()).append("]");
						return buf.toString();
					}
	
				});
			}
			// read more bytes from the input stream
			try {
				count = in.read(b);
			} catch (IOException e) {
				throw new XMPPException("error reading from input stream", e);
			}
		} while (count != -1 && !getStatus().equals(Status.CANCLED));

		// the connection was likely terminated abrubtly if these are not equal
		if (!getStatus().equals(Status.CANCLED) && amountWritten != fileSize) {
			setStatus(Status.ERROR);
		}
	}

}