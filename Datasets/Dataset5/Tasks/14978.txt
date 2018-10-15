return new ReplicaSharedObjectDescription(getClass(), getID(),getConfig().getHomeContainerID(),map,

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
import java.io.InputStream;
import java.util.HashMap;
import java.util.Map;
import org.eclipse.ecf.core.ISharedObjectConfig;
import org.eclipse.ecf.core.ISharedObjectContainerTransaction;
import org.eclipse.ecf.core.ReplicaSharedObjectDescription;
import org.eclipse.ecf.core.SharedObjectAddAbortException;
import org.eclipse.ecf.core.SharedObjectInitException;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.example.collab.ClientPlugin;
import org.eclipse.ecf.example.collab.share.EclipseCollabSharedObject;
import org.eclipse.ecf.example.collab.ui.FileReceiverUI;
import org.eclipse.ecf.example.collab.ui.FileSenderUI;
import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.swt.widgets.Display;

public class EclipseFileTransfer extends FileTransferSharedObject implements
		FileTransferListener {

	private static final long serialVersionUID = -4496151870561737078L;

	FileSenderUI senderUI;

	ID eclipseStageID;

	public EclipseFileTransfer(FileSenderUI view, ID target, InputStream ins,
			FileTransferParams params, ID receiverID) {
		super(target, ins, params);
		senderUI = view;
		progressListener = this;
		this.eclipseStageID = receiverID;
	}

	protected ReplicaSharedObjectDescription getReplicaDescription(ID remoteMember) {
		HashMap map = new HashMap();
		map.put("args", new Object[] { transferParams, eclipseStageID });
		map.put("types", new String[] { FileTransferParams.class.getName(),
				ID.class.getName() });
		return new ReplicaSharedObjectDescription(getID(), getClass().getName(), map,
				replicateID++);
	}

	public void init(ISharedObjectConfig config)
			throws SharedObjectInitException {
		super.init(config);
		Map props = config.getProperties();
		trace("args is " + props);
		Object[] args = (Object[]) props.get("args");
		if (args != null && args.length == 2) {
			transferParams = (FileTransferParams) args[0];
			eclipseStageID = (ID) args[1];
			progressListener = this;
		}
		if (args != null && args.length == 5) {
			senderUI = (FileSenderUI) args[0];
			targetReceiver = (ID) args[1];
			setInputStream((InputStream) args[2]);
			transferParams = (FileTransferParams) args[3];
			eclipseStageID = (ID) args[4];
			progressListener = this;
		}
	}

	/**
	 * Client constructor
	 * 
	 * @param params
	 *            the file send parameters associated with this file delivery
	 */
	public EclipseFileTransfer(FileTransferParams params, ID receiverID) {
		super(params);
		this.progressListener = this;
		this.eclipseStageID = receiverID;
	}

	public EclipseFileTransfer() {
		super();
	}

	public void sendStart(FileTransferSharedObject obj, long length, float rate) {
		if (senderUI != null) {
			senderUI.sendStart(transferParams.getRemoteFile(), length, rate);
		} else {
			System.out.println("Sending file: "
					+ transferParams.getRemoteFile() + ", length: " + length);
		}
	}

	public void sendData(FileTransferSharedObject obj, int dataLength) {
		if (senderUI != null) {
			senderUI.sendData(transferParams.getRemoteFile(), dataLength);
		} else {
			System.out.println("Sending data: " + dataLength + " bytes");
		}
	}

	public void sendDone(FileTransferSharedObject obj, Exception e) {
		if (senderUI != null) {
			senderUI.sendDone(transferParams.getRemoteFile(), e);
		} else {
			System.out.println("Sending done for: "
					+ transferParams.getRemoteFile());
		}
	}

	protected File createPath(EclipseCollabSharedObject stage, boolean server,
			File file, long length, float rate) {

		String downloadpath = null;
		// First, find EclipseCollabSharedObject if available
		try {
			if (stage != null) {
				downloadpath = stage.getLocalFullDownloadPath();
			}
		} catch (Exception e) {
		}
		File downloadDir = new File(downloadpath);
		// create directories if we need them
		downloadDir.mkdirs();
		// Then create new file
		File retFile = new File(downloadDir, file.getName());
		return retFile;
	}

	protected File localFile = null;

	protected FileReceiverUI receiverUI = null;

	protected EclipseCollabSharedObject receiverStage = null;

	public void receiveStart(FileTransferSharedObject obj, File aFile,
			long length, float rate) {
		
		final FileReceiver r = new FileReceiver(aFile, length, rate);
        Display.getDefault().syncExec(new Runnable() {
            public void run() {
                if (r != null) r.run();
            }
        });
	}

	public void receiveData(FileTransferSharedObject obj, int dataLength) {
		if (receiverUI != null) {
			receiverUI.receiveData(getHomeContainerID(), localFile, dataLength);
		} else {
			System.out.println("Receiving data: " + dataLength + " bytes");
		}
	}

	public void receiveDone(FileTransferSharedObject obj, Exception e) {
		// Need GUI progress indicator here
		if (receiverUI != null) {
			receiverUI.receiveDone(getHomeContainerID(), localFile, e);
		} else {
			System.out.println("Receiving done for: " + localFile);
		}
	}

	protected boolean votingCompleted() throws SharedObjectAddAbortException {
		if (failedParticipants != null && failedParticipants.size() > 0) {
			// In this case, we're going to go ahead and continue anyway
			return true;
			// Abort!
			// If no problems, and the number of participants to here from is 0,
			// then we're done
		} else if (state == ISharedObjectContainerTransaction.VOTING
				&& participantIDs.size() == 0) {
			// Success!
			return true;
		}
		// Else continue waiting
		return false;
	}
	
	private class FileReceiver implements Runnable {
		private File aFile = null;
		private long length;
		private float rate;
		
		public FileReceiver(File aFile, long length, float rate) {
			this.aFile = aFile;
			this.length = length;
			this.rate = rate;
		}
		/* (non-Javadoc)
		 * @see java.lang.Runnable#run()
		 */
		public void run() {
			boolean isServer = false;
			
			if (ClientPlugin.getDefault().getPluginPreferences().getBoolean(ClientPlugin.PREF_CONFIRM_FILE_RECEIVE)) {
				MessageDialog dialog = new MessageDialog(ClientPlugin.getDefault().getActiveShell(), "File Receive Confirmation", null, "Accept file?", MessageDialog.QUESTION, null , 0);
				dialog.setBlockOnOpen(true);
				int response = dialog.open();
				
				if (response == MessageDialog.CANCEL) {
					return;
				}
			}
			// First, find out if our local environment has access to an
			// EclipseCollabSharedObject instance
			try {
				receiverStage = (EclipseCollabSharedObject) getContext()
						.getSharedObjectManager().getSharedObject(eclipseStageID);
			} catch (Exception e) {
				// Should never happen
				e.printStackTrace(System.err);
			}

			try {
				isServer = getContext().isGroupManager();
			} catch (Exception e) {
				e.printStackTrace(System.err);
			}

			if (receiverStage != null) {
				receiverUI = receiverStage.getFileReceiverUI(EclipseFileTransfer.this, transferParams);
			}
			localFile = createPath(receiverStage, isServer, aFile, length, rate);
			// Our superclass depends upon the transferParams.getRemoteFile() call
			// to give a valid file.
			// We modify this to the new local file we've decided upon
			transferParams.setRemoteFile(localFile);

			if (receiverUI != null) {
				receiverUI.receiveStart(getHomeContainerID(), localFile, length,
						rate);
			} else {
				System.out.println("Receiving to local file: " + localFile);
			}
		}
		
	}

}
 No newline at end of file