ClientPlugin.log(MessageLoader.getFormattedString("EclipseFileTransferAndLaunch.EXCEPTION_LAUNCHING", localFile), e1); //$NON-NLS-1$

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

package org.eclipse.ecf.example.collab.share.io;

import java.io.File;
import org.eclipse.ecf.example.collab.share.EclipseCollabSharedObject;
import org.eclipse.ecf.internal.example.collab.ClientPlugin;
import org.eclipse.ecf.internal.example.collab.ui.MessageLoader;
import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.osgi.util.NLS;
import org.eclipse.swt.program.Program;
import org.eclipse.swt.widgets.Display;

public class EclipseFileTransferAndLaunch extends EclipseFileTransfer {

	private static final long serialVersionUID = -7524767418102487435L;

	public EclipseFileTransferAndLaunch() {
	}

	public void sendDone(FileTransferSharedObject obj, Exception e) {
		if (senderUI != null)
			senderUI.sendDone(transferParams.getRemoteFile(), e);
		// Now launch file locally, if it's sucessful
		if (e == null) {
			String senderPath = ((EclipseCollabSharedObject) getContext()
					.getSharedObjectManager().getSharedObject(sharedObjectID))
					.getLocalFullDownloadPath();
			launchFile(new File(new File(senderPath), transferParams
					.getRemoteFile().getName()).getAbsolutePath());
		}
	}

	private void launchFile(String fileName) {
		try {
			Program.launch(fileName);
		} catch (final IllegalArgumentException e1) {
			ClientPlugin.log(MessageLoader.getString("EclipseFileTransferAndLaunch.EXCEPTION_LAUNCHING") + localFile, e1); //$NON-NLS-1$
			Display.getDefault().asyncExec(new Runnable() {
				public void run() {
					MessageDialog
							.openInformation(
									null,
									MessageLoader
											.getString(MessageLoader.getString("EclipseFileTransferAndLaunch.PROGRAM_LAUNCH_MSGBOX_TITLE")), //$NON-NLS-1$
									MessageLoader
											.getString(NLS
													.bind(
															MessageLoader.getString("EclipseFileTransferAndLaunch.PROGRAM_LAUNCH_MSGBOX_TEXT"), //$NON-NLS-1$
															localFile
																	.getAbsolutePath(),
															e1.getMessage())));
				}
			});
		}
	}

	public void receiveDone(FileTransferSharedObject obj, Exception e) {
		// Need GUI progress indicator here
		if (receiverUI != null)
			receiverUI.receiveDone(getHomeContainerID(), localFile, e);
		// Now...we launch the file
		if (e == null && localFile != null)
			launchFile(localFile.getAbsolutePath());
	}

}
 No newline at end of file