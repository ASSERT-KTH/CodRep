if (proxyService != null && proxyService.isProxiesEnabled()) {

/*******************************************************************************
 * Copyright (c) 2004, 2007 Composent, Inc. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.provider.filetransfer.outgoing;

import java.io.*;
import java.net.MalformedURLException;
import java.net.URL;
import java.util.Map;
import org.eclipse.core.net.proxy.IProxyData;
import org.eclipse.core.net.proxy.IProxyService;
import org.eclipse.core.runtime.*;
import org.eclipse.core.runtime.jobs.Job;
import org.eclipse.ecf.core.identity.*;
import org.eclipse.ecf.core.security.IConnectContext;
import org.eclipse.ecf.core.util.Proxy;
import org.eclipse.ecf.core.util.ProxyAddress;
import org.eclipse.ecf.filetransfer.*;
import org.eclipse.ecf.filetransfer.events.*;
import org.eclipse.ecf.filetransfer.identity.IFileID;
import org.eclipse.ecf.filetransfer.service.ISendFileTransfer;
import org.eclipse.ecf.internal.provider.filetransfer.Activator;
import org.eclipse.ecf.internal.provider.filetransfer.Messages;
import org.eclipse.ecf.provider.filetransfer.identity.FileTransferNamespace;
import org.eclipse.osgi.util.NLS;

public abstract class AbstractOutgoingFileTransfer implements IOutgoingFileTransfer, ISendFileTransfer {

	public static final int DEFAULT_BUF_LENGTH = 4096;

	private static final int FILETRANSFER_ERRORCODE = 1001;

	protected Job job;

	protected URL remoteFileURL;

	protected IFileID remoteFileID;

	protected IFileTransferListener listener;

	protected int buff_length = DEFAULT_BUF_LENGTH;

	protected boolean done = false;

	protected long bytesSent = 0;

	protected InputStream localFileContents;

	protected OutputStream remoteFileContents;

	protected Exception exception;

	protected IFileTransferInfo fileTransferInfo;

	protected Map options = null;

	protected IConnectContext connectContext;

	protected Proxy proxy;

	protected URL getRemoteFileURL() {
		return remoteFileURL;
	}

	protected void setInputStream(InputStream ins) {
		localFileContents = ins;
	}

	protected void setOutputStream(OutputStream outs) {
		remoteFileContents = outs;
	}

	protected IFileTransferInfo getFileTransferInfo() {
		return fileTransferInfo;
	}

	protected Map getOptions() {
		return options;
	}

	public AbstractOutgoingFileTransfer() {
		//
	}

	public class FileTransferJob extends Job {

		public FileTransferJob(String name) {
			super(name);
		}

		protected IStatus run(IProgressMonitor monitor) {
			final byte[] buf = new byte[buff_length];
			final long totalWork = ((fileTransferInfo.getFileSize() == -1) ? 100 : fileTransferInfo.getFileSize());
			double factor = (totalWork > Integer.MAX_VALUE) ? (((double) Integer.MAX_VALUE) / ((double) totalWork)) : 1.0;
			int work = (totalWork > Integer.MAX_VALUE) ? Integer.MAX_VALUE : (int) totalWork;
			monitor.beginTask(getRemoteFileURL().toString() + Messages.AbstractOutgoingFileTransfer_Progress_Data, work);
			try {
				while (!isDone()) {
					if (monitor.isCanceled())
						throw new UserCancelledException(Messages.AbstractOutgoingFileTransfer_Exception_User_Cancelled);
					final int bytes = localFileContents.read(buf);
					if (bytes != -1) {
						bytesSent += bytes;
						remoteFileContents.write(buf, 0, bytes);
						fireTransferSendDataEvent();
						monitor.worked((int) Math.round(factor * bytes));
					} else {
						done = true;
					}
				}
			} catch (final Exception e) {
				exception = e;
				done = true;
			} finally {
				hardClose();
				monitor.done();
				fireTransferSendDoneEvent();
			}
			return getFinalStatus(exception);
		}

	}

	protected IStatus getFinalStatus(Throwable exception1) {
		if (exception1 == null)
			return new Status(IStatus.OK, Activator.getDefault().getBundle().getSymbolicName(), 0, Messages.AbstractOutgoingFileTransfer_Status_Transfer_Completed_OK, null);
		else if (exception1 instanceof UserCancelledException)
			return new Status(IStatus.CANCEL, Activator.PLUGIN_ID, FILETRANSFER_ERRORCODE, Messages.AbstractOutgoingFileTransfer_Exception_User_Cancelled, exception1);
		else
			return new Status(IStatus.ERROR, Activator.PLUGIN_ID, FILETRANSFER_ERRORCODE, Messages.AbstractOutgoingFileTransfer_Status_Transfer_Exception, exception1);
	}

	protected void hardClose() {
		try {
			if (remoteFileContents != null)
				remoteFileContents.close();
		} catch (final IOException e) {
			Activator.getDefault().log(new Status(IStatus.ERROR, Activator.PLUGIN_ID, IStatus.ERROR, "hardClose", e)); //$NON-NLS-1$
		}
		try {
			if (localFileContents != null)
				localFileContents.close();
		} catch (final IOException e) {
			Activator.getDefault().log(new Status(IStatus.ERROR, Activator.PLUGIN_ID, IStatus.ERROR, "hardClose", e)); //$NON-NLS-1$
		}
		job = null;
		remoteFileContents = null;
		localFileContents = null;
	}

	public ID getID() {
		return remoteFileID;
	}

	protected void fireTransferSendDoneEvent() {
		listener.handleTransferEvent(new IOutgoingFileTransferSendDoneEvent() {

			private static final long serialVersionUID = -2686266564645210722L;

			public IOutgoingFileTransfer getSource() {
				return AbstractOutgoingFileTransfer.this;
			}

			public Exception getException() {
				return AbstractOutgoingFileTransfer.this.getException();
			}

			public String toString() {
				final StringBuffer sb = new StringBuffer("IOutgoingFileTransferSendDoneEvent["); //$NON-NLS-1$
				sb.append("bytesSent=").append(bytesSent) //$NON-NLS-1$
						.append(";fileLength=").append(fileTransferInfo.getFileSize()).append(";exception=").append(getException()) //$NON-NLS-1$ //$NON-NLS-2$
						.append("]"); //$NON-NLS-1$
				return sb.toString();
			}
		});
	}

	protected void fireTransferSendDataEvent() {
		listener.handleTransferEvent(new IOutgoingFileTransferSendDataEvent() {

			private static final long serialVersionUID = -2916500675859842392L;

			public IOutgoingFileTransfer getSource() {
				return AbstractOutgoingFileTransfer.this;
			}

			public String toString() {
				final StringBuffer sb = new StringBuffer("IOutgoingFileTransferSendDataEvent["); //$NON-NLS-1$
				sb.append("bytesSent=").append(bytesSent) //$NON-NLS-1$
						.append(";fileLength=").append(fileTransferInfo.getFileSize()) //$NON-NLS-1$ 
						.append("]"); //$NON-NLS-1$
				return sb.toString();
			}
		});
	}

	public long getBytesSent() {
		return bytesSent;
	}

	public void cancel() {
		if (job != null)
			job.cancel();
	}

	public Exception getException() {
		return exception;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.filetransfer.IFileTransfer#getPercentComplete()
	 */
	public double getPercentComplete() {
		long fileLength = fileTransferInfo.getFileSize();
		if (fileLength == -1 || fileLength == 0)
			return fileLength;
		return ((double) bytesSent / (double) fileLength);
	}

	public boolean isDone() {
		return done;
	}

	public Object getAdapter(Class adapter) {
		if (adapter == null)
			return null;
		if (adapter.isInstance(this)) {
			return this;
		}
		final IAdapterManager adapterManager = Activator.getDefault().getAdapterManager();
		return (adapterManager == null) ? null : adapterManager.loadAdapter(this, adapter.getName());
	}

	/**
	 * Open incoming and outgoing streams associated with this file transfer.
	 * Subclasses must implement this method to open input and output streams.
	 * The <code>remoteFileContents</code> and <code>localFileContent</code>
	 * must be non-<code>null</code> after successful completion of the
	 * implementation of this method.
	 * 
	 * @throws SendFileTransferException
	 */
	protected abstract void openStreams() throws SendFileTransferException;

	public Namespace getOutgoingNamespace() {
		return IDFactory.getDefault().getNamespaceByName(FileTransferNamespace.PROTOCOL);
	}

	public IFileTransferListener getListener() {
		return listener;
	}

	protected void setupAndScheduleJob() {
		job = new FileTransferJob(getRemoteFileURL().toString());
		job.schedule();
	}

	protected void fireSendStartEvent() {
		listener.handleTransferEvent(new IOutgoingFileTransferResponseEvent() {

			private static final long serialVersionUID = 2171381825030082432L;

			public String toString() {
				final StringBuffer sb = new StringBuffer("IOutgoingFileTransferResponseEvent["); //$NON-NLS-1$
				sb.append("isdone=").append(done).append(";"); //$NON-NLS-1$ //$NON-NLS-2$
				sb.append("bytesSent=").append(bytesSent) //$NON-NLS-1$
						.append("]"); //$NON-NLS-1$
				return sb.toString();
			}

			public boolean requestAccepted() {
				return true;
			}

			public IOutgoingFileTransfer getSource() {
				return AbstractOutgoingFileTransfer.this;
			}

		});
	}

	protected abstract void setupProxy(Proxy proxy);

	protected void setupProxies() {
		// If it's been set directly (via ECF API) then this overrides platform settings
		if (proxy == null) {
			try {
				IProxyService proxyService = Activator.getDefault().getProxyService();
				// Only do this if platform service exists
				if (proxyService != null) {
					// Setup via proxyService entry
					URL target = getRemoteFileURL();
					String type = IProxyData.SOCKS_PROXY_TYPE;
					if (target.getProtocol().equalsIgnoreCase(IProxyData.HTTP_PROXY_TYPE)) {
						type = IProxyData.HTTP_PROXY_TYPE;
					} else if (target.getProtocol().equalsIgnoreCase(IProxyData.HTTPS_PROXY_TYPE)) {
						type = IProxyData.HTTPS_PROXY_TYPE;
					}
					final IProxyData proxyData = proxyService.getProxyDataForHost(target.getHost(), type);
					if (proxyData != null) {
						proxy = new Proxy(((type.equalsIgnoreCase(IProxyData.SOCKS_PROXY_TYPE)) ? Proxy.Type.SOCKS : Proxy.Type.HTTP), new ProxyAddress(proxyData.getHost(), proxyData.getPort()), proxyData.getUserId(), proxyData.getPassword());
					}
				}
			} catch (Exception e) {
				// If we don't even have the classes for this (i.e. the org.eclipse.core.net plugin not available)
				// then we simply log and ignore
				Activator.logNoProxyWarning(e);
			} catch (NoClassDefFoundError e) {
				Activator.logNoProxyWarning(e);
			}
		}
		if (proxy != null)
			setupProxy(proxy);

	}

	public void sendOutgoingRequest(IFileID targetReceiver, IFileTransferInfo localFileToSend, IFileTransferListener transferListener, Map ops) throws SendFileTransferException {
		Assert.isNotNull(targetReceiver, Messages.AbstractOutgoingFileTransfer_RemoteFileID_Not_Null);
		Assert.isNotNull(transferListener, Messages.AbstractOutgoingFileTransfer_TransferListener_Not_Null);
		Assert.isNotNull(localFileToSend, Messages.AbstractOutgoingFileTransfer_EXCEPTION_FILE_TRANSFER_INFO_NOT_NULL);
		this.done = false;
		this.bytesSent = 0;
		this.exception = null;
		this.fileTransferInfo = localFileToSend;
		this.remoteFileID = targetReceiver;
		this.options = ops;

		try {
			this.remoteFileURL = targetReceiver.getURL();
		} catch (final MalformedURLException e) {
			throw new SendFileTransferException(NLS.bind(Messages.AbstractOutgoingFileTransfer_MalformedURLException, targetReceiver), e);
		}
		this.listener = transferListener;
		setupProxies();
		openStreams();
		setupAndScheduleJob();
	}

	public void sendOutgoingRequest(IFileID targetReceiver, final File localFileToSend, IFileTransferListener transferListener, Map ops) throws SendFileTransferException {
		sendOutgoingRequest(targetReceiver, new FileTransferInfo(localFileToSend, null, null), transferListener, ops);
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.filetransfer.ISendFileTransferContainerAdapter#addListener(org.eclipse.ecf.filetransfer.IIncomingFileTransferRequestListener)
	 */
	public void addListener(IIncomingFileTransferRequestListener l) {
		// Not needed
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.filetransfer.ISendFileTransferContainerAdapter#removeListener(org.eclipse.ecf.filetransfer.IIncomingFileTransferRequestListener)
	 */
	public boolean removeListener(IIncomingFileTransferRequestListener l) {
		return false;
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.filetransfer.ISendFileTransferContainerAdapter#setConnectContextForAuthentication(org.eclipse.ecf.core.security.IConnectContext)
	 */
	public void setConnectContextForAuthentication(IConnectContext connectContext) {
		this.connectContext = connectContext;
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.filetransfer.ISendFileTransferContainerAdapter#setProxy(org.eclipse.ecf.core.util.Proxy)
	 */
	public void setProxy(Proxy proxy) {
		this.proxy = proxy;
	}

}