package org.eclipse.ecf.internal.provider.bittorrent.ui;

/****************************************************************************
 * Copyright (c) 2007 Remy Suen and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Remy Suen <remy.suen@gmail.com> - initial API and implementation
 *****************************************************************************/
package org.eclipse.ecf.internal.provider.msn.ui;

import java.io.File;
import java.io.IOException;

import org.eclipse.ecf.core.IContainer;
import org.eclipse.ecf.core.identity.IDCreateException;
import org.eclipse.ecf.filetransfer.IFileTransfer;
import org.eclipse.ecf.filetransfer.IFileTransferListener;
import org.eclipse.ecf.filetransfer.IRetrieveFileTransferContainerAdapter;
import org.eclipse.ecf.filetransfer.IncomingFileTransferException;
import org.eclipse.ecf.filetransfer.events.IFileTransferEvent;
import org.eclipse.ecf.filetransfer.events.IIncomingFileTransferEvent;
import org.eclipse.ecf.filetransfer.events.IIncomingFileTransferReceiveStartEvent;
import org.eclipse.ecf.filetransfer.identity.IFileID;
import org.eclipse.ecf.filetransfer.ui.FileTransfersView;
import org.eclipse.ecf.ui.IConnectWizard;
import org.eclipse.ecf.ui.dialogs.ContainerConnectErrorDialog;
import org.eclipse.jface.wizard.Wizard;
import org.eclipse.ui.IWorkbench;
import org.eclipse.ui.IWorkbenchPage;

public class BitTorrentConnectWizard extends Wizard implements IConnectWizard {

	private IWorkbench workbench;

	private BitTorrentConnectWizardPage page;

	private IContainer container;

	private IFileID targetID;

	private IWorkbenchPage workbenchPage;

	public void addPages() {
		page = new BitTorrentConnectWizardPage();
		addPage(page);
	}

	public void init(IWorkbench workbench, IContainer container) {
		this.workbench = workbench;
		this.container = container;
	}

	public boolean performFinish() {
		workbenchPage = workbench.getActiveWorkbenchWindow().getActivePage();
		IRetrieveFileTransferContainerAdapter irftca = (IRetrieveFileTransferContainerAdapter) container
				.getAdapter(IRetrieveFileTransferContainerAdapter.class);
		try {
			targetID = (IFileID) irftca.getRetrieveNamespace().createInstance(
					new Object[] { page.getTorrentName() });
		} catch (IDCreateException e) {
			new ContainerConnectErrorDialog(workbench
					.getActiveWorkbenchWindow().getShell(), 1,
					"The target ID to connect to could not be created", page
							.getTorrentName(), e).open();
			return true;
		}

		try {
			irftca.sendRetrieveRequest(targetID, new IFileTransferListener() {
				public void handleTransferEvent(final IFileTransferEvent e) {
					if (e instanceof IIncomingFileTransferReceiveStartEvent) {
						try {
							final IFileTransfer ift = ((IIncomingFileTransferReceiveStartEvent) e)
									.receive(new File(page.getTargetName()));
							workbenchPage.getWorkbenchWindow().getShell()
									.getDisplay().asyncExec(new Runnable() {
										public void run() {
											FileTransfersView.addTransfer(ift);
										}
									});
						} catch (IOException ioe) {
							new ContainerConnectErrorDialog(workbench
									.getActiveWorkbenchWindow().getShell(), 1,
									"Could not write to "
											+ page.getTargetName(), page
											.getTargetName(), null).open();
						}
					} else if (e instanceof IIncomingFileTransferEvent) {
						final FileTransfersView ftv = (FileTransfersView) workbenchPage
								.findView(FileTransfersView.ID);
						if (ftv != null) {
							workbenchPage.getWorkbenchWindow().getShell()
									.getDisplay().asyncExec(new Runnable() {
										public void run() {
											ftv
													.update(((IIncomingFileTransferEvent) e)
															.getSource());
										}
									});
						}
					}
				}
			}, null);
		} catch (IncomingFileTransferException e) {
			new ContainerConnectErrorDialog(workbench
					.getActiveWorkbenchWindow().getShell(), 1,
					"Could not send retrieval request.", targetID.getName(), e)
					.open();
		}

		return true;
	}
}