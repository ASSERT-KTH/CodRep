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
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.util.HashMap;
import java.util.Map;

import org.eclipse.ecf.core.IContainer;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.filetransfer.IFileTransferInfo;
import org.eclipse.ecf.filetransfer.IFileTransferListener;
import org.eclipse.ecf.filetransfer.IIncomingFileTransfer;
import org.eclipse.ecf.filetransfer.IIncomingFileTransferRequestListener;
import org.eclipse.ecf.filetransfer.IncomingFileTransferException;
import org.eclipse.ecf.filetransfer.events.IFileTransferEvent;
import org.eclipse.ecf.filetransfer.events.IFileTransferRequestEvent;
import org.eclipse.ecf.filetransfer.events.IIncomingFileTransferReceiveDoneEvent;
import org.eclipse.ecf.internal.provider.xmpp.identity.XMPPID;
import org.jivesoftware.smackx.filetransfer.FileTransferListener;
import org.jivesoftware.smackx.filetransfer.FileTransferRequest;
import org.jivesoftware.smackx.filetransfer.IncomingFileTransfer;

public class XMPPFileTransferRequestListener implements FileTransferListener {

	protected IFileTransferListener transferListener;

	protected IIncomingFileTransferRequestListener requestListener;

	protected IncomingFileTransfer incoming = null;

	protected IContainer container = null;

	public XMPPFileTransferRequestListener(IContainer container,
			IIncomingFileTransferRequestListener listener) {
		this.container = container;
		this.requestListener = listener;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.jivesoftware.smackx.filetransfer.FileTransferListener#fileTransferRequest(org.jivesoftware.smackx.filetransfer.FileTransferRequest)
	 */
	public void fileTransferRequest(final FileTransferRequest request) {
		requestListener
				.handleFileTransferRequest(new IFileTransferRequestEvent() {

					private static final long serialVersionUID = -6173401619917403353L;

					boolean requestAccepted = false;

					IFileTransferInfo fileTransferInfo = new IFileTransferInfo() {

						Map props = new HashMap();

						File f = new File(request.getFileName());

						public String getDescription() {
							return request.getDescription();
						}

						public File getFile() {
							return f;
						}

						public Map getProperties() {
							return props;
						}

						public Object getAdapter(Class adapter) {
							return null;
						}

						public long getFileSize() {
							return request.getFileSize();
						}

						public String getMimeType() {
							return request.getMimeType();
						}

						public String toString() {
							StringBuffer buf = new StringBuffer(
									"FileTransferInfo[");
							buf.append("file=").append(f);
							buf.append(";size=").append(getFileSize());
							buf.append(";description=" + getDescription());
							buf.append(";mimeType=").append(getMimeType())
									.append("]");
							return buf.toString();
						}

					};

					public IIncomingFileTransfer accept(File localFileToSave)
							throws IncomingFileTransferException {

						try {
							final OutputStream outs = new FileOutputStream(
									localFileToSave);
							return accept(outs, new IFileTransferListener() {
								public void handleTransferEvent(
										IFileTransferEvent event) {
									if (event instanceof IIncomingFileTransferReceiveDoneEvent) {
										try {
											outs.close();
										} catch (IOException e) {
										}
									}
								}
							});
						} catch (FileNotFoundException e) {
							throw new IncomingFileTransferException(
									"Exception opening file for writing", e);
						}
					}

					public IFileTransferInfo getFileTransferInfo() {
						return fileTransferInfo;
					}

					public ID getRequesterID() {
						return createIDFromName(request.getRequestor());
					}

					public void reject() {
						request.reject();
					}

					public boolean requestAccepted() {
						return requestAccepted;
					}

					public String toString() {
						StringBuffer buf = new StringBuffer(
								"FileTransferRequestEvent[");
						buf.append("requester=").append(getRequesterID());
						buf.append(";requestAccepted=").append(
								requestAccepted());
						buf.append(";transferInfo=").append(
								getFileTransferInfo()).append("]");
						return buf.toString();
					}

					public IIncomingFileTransfer accept(
							OutputStream outputStream,
							IFileTransferListener listener)
							throws IncomingFileTransferException {
						if (requestAccepted)
							throw new IncomingFileTransferException(
									"Incoming request previously accepted");
						if (outputStream == null)
							throw new IncomingFileTransferException(
									"outputStream cannot be null");
						incoming = request.accept();
						try {
							return new XMPPIncomingFileTransfer(IDFactory
									.getDefault().createStringID(
											request.getStreamID()), incoming
									.recieveFile(), outputStream, request
									.getFileSize(), listener);
						} catch (Exception e) {
							throw new IncomingFileTransferException(
									"Exception receiving file", e);
						}
					}
				});
	}

	private XMPPID createIDFromName(String uname) {
		try {
			return new XMPPID(container.getConnectNamespace(), uname);
		} catch (Exception e) {
			return null;
		}
	}

	/**
	 * @param listener2
	 * @return
	 */
	public boolean hasListener(IIncomingFileTransferRequestListener listener2) {
		return (listener2 == requestListener);
	}

}