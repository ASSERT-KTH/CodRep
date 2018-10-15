package org.eclipse.ecf.filetransfer.ui.actions;

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

package org.eclipse.ecf.filetransfer.ui.action;

import java.io.File;
import java.util.Map;

import org.eclipse.core.runtime.Assert;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Status;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.util.IExceptionHandler;
import org.eclipse.ecf.filetransfer.FileTransferInfo;
import org.eclipse.ecf.filetransfer.IFileTransferInfo;
import org.eclipse.ecf.filetransfer.IFileTransferListener;
import org.eclipse.ecf.filetransfer.IOutgoingFileTransferContainerAdapter;
import org.eclipse.ecf.filetransfer.events.IFileTransferEvent;
import org.eclipse.ecf.filetransfer.events.IOutgoingFileTransferSendDoneEvent;
import org.eclipse.ecf.internal.filetransfer.ui.Activator;
import org.eclipse.ecf.internal.filetransfer.ui.Messages;
import org.eclipse.jface.action.Action;
import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.osgi.util.NLS;
import org.eclipse.swt.widgets.Display;

/**
 * Action super class for initiating outging file transfers. Subclasses should
 * be created to implement {@link #getOutgoingFileTransferAdapter()} and to
 * override any desired methods.
 */
public abstract class AbstractFileSendAction extends Action {

	protected ID targetReceiver;

	protected IFileTransferInfo fileTransferInfo;

	protected IFileTransferListener fileTransferListener;

	protected Map options;

	protected IExceptionHandler exceptionHandler = null;

	public void setTargetReceiver(ID targetReceiver) {
		this.targetReceiver = targetReceiver;
	}

	public ID getTargetReceiver() {
		return this.targetReceiver;
	}

	public void setFileTransferInfo(IFileTransferInfo info) {
		this.fileTransferInfo = info;
	}

	public IFileTransferInfo getFileTransferInfo() {
		return this.fileTransferInfo;
	}

	public void setFileToSend(File fileToSend) {
		// /this.fileToSend = fileToSend;
		this.fileTransferInfo = createFileTransferInfoFromFile(fileToSend);
	}

	/**
	 * @param fileToSend
	 * @return
	 */
	private IFileTransferInfo createFileTransferInfoFromFile(
			final File fileToSend) {
		return new FileTransferInfo(fileToSend);
	}

	public File getFileToSend() {
		if (this.fileTransferInfo == null)
			return null;
		else
			return this.fileTransferInfo.getFile();
	}

	public void setFileTransferListener(IFileTransferListener listener) {
		this.fileTransferListener = listener;
	}

	public IFileTransferListener getFileTransferListener() {
		return this.fileTransferListener;
	}

	public void setFileTransferOptions(Map options) {
		this.options = options;
	}

	public Map getFileTransferOptions() {
		return this.options;
	}

	public void setExceptionHandler(IExceptionHandler exceptionHandler) {
		this.exceptionHandler = exceptionHandler;
	}

	public IExceptionHandler getExceptionhandler() {
		return this.exceptionHandler;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.jface.action.Action#run()
	 */
	public void run() {
		try {
			sendFileToTarget();
		} catch (Exception e) {
			if (exceptionHandler != null)
				exceptionHandler.handleException(e);
			else
				Activator.getDefault().getLog().log(
						new Status(IStatus.ERROR, Activator.PLUGIN_ID,
								IStatus.ERROR, NLS.bind(
										Messages.getString("AbstractFileSendAction.EXCEPTION_SENDING_TO_TARGET"), //$NON-NLS-1$
										getTargetReceiver()), e));
		}

	}

	/**
	 * Get the container adapter for actually initiating the file transer
	 * request.
	 * 
	 * @return IOutgoingFileTransferContainerAdapter to use for the action
	 *         {@link #run()}. Must not return <code>null</code>.
	 */
	protected abstract IOutgoingFileTransferContainerAdapter getOutgoingFileTransferAdapter();

	protected void sendFileToTarget() throws Exception {
		ID target = getTargetReceiver();
		Assert.isNotNull(target, Messages.getString("AbstractFileSendAction.RECEIVER_NOT_NULL")); //$NON-NLS-1$
		IOutgoingFileTransferContainerAdapter adapter = getOutgoingFileTransferAdapter();
		Assert.isNotNull(adapter, Messages.getString("AbstractFileSendAction.ADAPTER_NOT_NULL")); //$NON-NLS-1$
		IFileTransferListener listener = getFileTransferListener();
		if (listener == null)
			listener = createDefaultFileTransferListener();
		Assert.isNotNull(listener, Messages.getString("AbstractFileSendAction.LISTENER_NOT_NULL")); //$NON-NLS-1$
		IFileTransferInfo info = getFileTransferInfo();
		Assert.isNotNull(info, Messages.getString("AbstractFileSendAction.FILE_NOT_NULL")); //$NON-NLS-1$
		// Now call
		adapter.sendOutgoingRequest(target, info, listener, this.options);
	}

	/**
	 * @return IFileTransferListener to use as the default listener. Must not be
	 *         <code>null</code>.
	 */
	protected IFileTransferListener createDefaultFileTransferListener() {
		return new IFileTransferListener() {
			public void handleTransferEvent(final IFileTransferEvent event) {
				// Only handle send done event. If custom UI handling for other
				// events is desired...e.g. progress reporting or other handling
				// then a custom IFileTransferListener should be provided.
				if (event instanceof IOutgoingFileTransferSendDoneEvent) {
					final IOutgoingFileTransferSendDoneEvent oftsde = (IOutgoingFileTransferSendDoneEvent) event;
					final Exception errorException = oftsde.getSource()
							.getException();
					Display.getDefault().asyncExec(new Runnable() {
						public void run() {
							if (errorException == null) {
								MessageDialog
										.openInformation(
												null,
												Messages.getString("AbstractFileSendAction.TITLE_FILE_TRANSFER_SUCESSFUL"), //$NON-NLS-1$
												NLS
														.bind(
																Messages.getString("AbstractFileSendAction.MESSAGE_FILE_TRANSFER_SUCCESSFUL"), //$NON-NLS-1$
																getFileTransferInfo()
																		.getFile()
																		.getName()));
							} else {
								MessageDialog
										.openError(
												null,
												Messages.getString("AbstractFileSendAction.TITLE_FILE_TRANSFER_FAILED"), //$NON-NLS-1$
												NLS
														.bind(
																Messages.getString("AbstractFileSendAction.MESSAGE_FILE_TRANSFER_FAILED"), //$NON-NLS-1$
																errorException
																		.getLocalizedMessage()));
							}
						}
					});

				}
			}
		};
	}
}