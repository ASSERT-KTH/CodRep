monitor.beginTask("", 100);

/*******************************************************************************
 * Copyright (c) 2005 IBM Corporation and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors:
 *     IBM Corporation - initial API and implementation
 *******************************************************************************/
package org.eclipse.core.internal.filesystem.ftp;

import java.net.URL;
import org.eclipse.core.filesystem.EFS;
import org.eclipse.core.filesystem.IFileInfo;
import org.eclipse.core.filesystem.provider.FileInfo;
import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.core.runtime.SubProgressMonitor;
import org.eclipse.ftp.*;

/**
 * 
 */
public class FTPUtil {
	private static final ThreadLocal openClients = new ThreadLocal();

	public static IClient createClient(URL url) throws FtpException {
		IClient client = Ftp.createClient(url);
		client.setDataTransferMode(IClient.PASSIVE_DATA_TRANSFER, true);
		client.setAuthentication(KeyRing.USER, KeyRing.PASS);
		client.setTimeout(5);
		return client;
	}

	public static IClient getClient() {
		return (IClient) openClients.get();
	}

	/**
	 * Use this method to ensure that the same connection is used for multiple commands
	 * issued from the same thread.
	 * @throws FtpException
	 */
	public static void run(URL url, IFtpRunnable runnable, IProgressMonitor monitor) throws FtpException {
		monitor = Policy.monitorFor(monitor);
		IClient openClient = (IClient) openClients.get();
		monitor.beginTask(null, 100);
		//if the wrong client is connected, disconnect before trying again
		if (openClient != null && !openClient.getUrl().equals(url)) {
			openClient.close(new SubProgressMonitor(monitor, 0));
			openClient = null;
		}
		if (openClient == null) {
			openClient = createClient(url);
			openClient.open(new SubProgressMonitor(monitor, 5));
			openClient.changeDirectory(url.getPath(), new SubProgressMonitor(monitor, 5));
			openClients.set(openClient);
		}
		runnable.run(new SubProgressMonitor(monitor, 90));
		//just leave the client open to reuse the connection
	}

	/**
	 * Converts a directory entry to a file info
	 * @param entry
	 * @return The file information for a directory entry
	 */
	public static IFileInfo entryToFileInfo(IDirectoryEntry entry) {
		FileInfo info = new FileInfo();
		info.setExists(true);
		info.setName(entry.getName());
		info.setLastModified(entry.getModTime().getTime());
		info.setLength(entry.getSize());
		info.setDirectory(entry.hasDirectorySemantics());
		return info;
	}
}