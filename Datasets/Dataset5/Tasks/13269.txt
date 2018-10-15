package org.eclipse.ecf.internal.provider.filetransfer;

/*******************************************************************************
 * Copyright (c) 2004 Composent, Inc. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.provider.filetransfer;

import java.io.BufferedOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.net.URL;

import org.apache.commons.httpclient.HttpClient;
import org.apache.commons.httpclient.methods.GetMethod;
import org.eclipse.ecf.filetransfer.IIncomingFileTransfer;
import org.eclipse.ecf.filetransfer.IncomingFileTransferException;
import org.eclipse.ecf.filetransfer.events.IIncomingFileTransferReceiveStartEvent;
import org.eclipse.ecf.filetransfer.identity.IFileID;

public class HttpClientRetrieveFileTransfer extends AbstractRetrieveFileTransfer {

	protected static final int DEFAULT_CONNECTION_TIMEOUT = 30000;
	
	GetMethod getMethod = null;
	HttpClient client = null;
	
	protected void hardClose() {
		super.hardClose();
		if (getMethod != null) {
			getMethod.releaseConnection();
			getMethod = null;
		}
	}
	
	protected void openStreams() throws IncomingFileTransferException {
		URL theURL = null;

		try {
			theURL = getRemoteFileURL();
			
		    client = new HttpClient();
		    client.getHttpConnectionManager().
		        getParams().setConnectionTimeout(DEFAULT_CONNECTION_TIMEOUT);

			getMethod = new GetMethod(theURL.toExternalForm());
			getMethod.setFollowRedirects(true);
			
			client.executeMethod(getMethod);
			
			long contentLength = getMethod.getResponseContentLength();
			setInputStream(getMethod.getResponseBodyAsStream());
			setFileLength(contentLength);

			listener
					.handleTransferEvent(new IIncomingFileTransferReceiveStartEvent() {
						private static final long serialVersionUID = -59096575294481755L;

						public IFileID getFileID() {
							return remoteFileID;
						}

						public IIncomingFileTransfer receive(
								File localFileToSave) throws IOException {
							setOutputStream(new BufferedOutputStream(
									new FileOutputStream(localFileToSave)));
							job = new FileTransferJob(getRemoteFileURL().toString());
							job.schedule();
							return HttpClientRetrieveFileTransfer.this;
						}

						public String toString() {
							StringBuffer sb = new StringBuffer(
									"IIncomingFileTransferReceiveStartEvent[");
							sb.append("isdone=").append(done).append(";");
							sb.append("bytesReceived=").append(bytesReceived)
									.append("]");
							return sb.toString();
						}

						public void cancel() {
							hardClose();
						}

						public IIncomingFileTransfer receive(OutputStream streamToStore) throws IOException {
							setOutputStream(new BufferedOutputStream(streamToStore));
							setCloseOutputStream(false);
							job = new FileTransferJob(getRemoteFileURL().toString());
							job.schedule();
							return HttpClientRetrieveFileTransfer.this;
						}

					});
		} catch (Exception e) {
			throw new IncomingFileTransferException("Exception connecting to "
					+ theURL.toString(), e);
		}

	}


}