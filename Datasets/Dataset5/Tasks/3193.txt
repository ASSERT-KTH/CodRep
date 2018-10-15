DEFAULT_INCLUDE_SERVER = Boolean.getBoolean(str);

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
import java.io.Serializable;
import java.util.Date;

public class FileTransferParams implements Serializable {
	private static final long serialVersionUID = -2871056005778727843L;
	protected static int DEFAULT_CHUNK_SIZE = 1024;
	protected static int DEFAULT_WAIT_TIME = 1000;
	protected static int DEFAULT_FILE_LENGTH = -1;
	protected static boolean DEFAULT_INCLUDE_SERVER = false;
	// Suggested remote file name
	protected File remoteFile;
	protected int chunkSize;
	protected int waitTime;
	protected Date startDate;
	protected boolean includeServer;
	protected long length;
	protected float rate;
	protected FileTransferListener progressListener;

	static {
		try {
			String str = System.getProperty(FileTransferParams.class.getName()
					+ ".FILECHUNKSIZE", "" + DEFAULT_CHUNK_SIZE);
			DEFAULT_CHUNK_SIZE = Integer.parseInt(str);
			str = System.getProperty(FileTransferParams.class.getName()
					+ ".FILEWAITTIME", DEFAULT_WAIT_TIME + "");
			DEFAULT_WAIT_TIME = Integer.parseInt(str);
			str = System.getProperty(FileTransferParams.class.getName()
					+ ".FILELENGTH", DEFAULT_FILE_LENGTH + "");
			DEFAULT_FILE_LENGTH = Integer.parseInt(str);
			str = System.getProperty(FileTransferParams.class.getName()
					+ ".FILEINCLUDESERVER", "false");
			DEFAULT_INCLUDE_SERVER = Boolean.valueOf(str).booleanValue();
		} catch (Exception e) {
		}
	}

	public FileTransferParams(File aFile, int chunkSize, int waitTime,
			Date startDate, boolean includeServer, long length,
			FileTransferListener listener) {
		remoteFile = aFile;
		if (chunkSize == -1)
			this.chunkSize = DEFAULT_CHUNK_SIZE;
		else
			this.chunkSize = chunkSize;
		this.waitTime = waitTime;
		if (waitTime == -1)
			this.waitTime = DEFAULT_WAIT_TIME;
		else
			this.waitTime = waitTime;
		this.startDate = startDate;
		this.includeServer = includeServer;
		this.length = length;
		this.rate = (chunkSize * 8) / ((float) waitTime / (float) 1000);
		this.progressListener = listener;
	}

	public FileTransferParams() {
		this(null, DEFAULT_CHUNK_SIZE, DEFAULT_WAIT_TIME, null,
				DEFAULT_INCLUDE_SERVER, DEFAULT_FILE_LENGTH, null);
	}

	public File getRemoteFile() {
		return remoteFile;
	}

	public void setRemoteFile(File aFile) {
		remoteFile = aFile;
	}

	public int getChunkSize() {
		return chunkSize;
	}

	public void setChunkSize(int size) {
		chunkSize = size;
	}

	public int getWaitTime() {
		return waitTime;
	}

	public void setWaitTime(int wait) {
		waitTime = wait;
	}

	public Date getStartDate() {
		return startDate;
	}

	public void setStartDate(Date aDate) {
		startDate = aDate;
	}

	public boolean getIncludeServer() {
		return includeServer;
	}

	public void setIncludeServer(boolean include) {
		includeServer = include;
	}

	public long getLength() {
		return length;
	}

	public void setLength(long len) {
		length = len;
	}

	public float getRate() {
		return rate;
	}

	protected FileTransferListener getProgressListener() {
		return progressListener;
	}

	protected void setProgressListener(FileTransferListener list) {
		progressListener = list;
	}

	public String toString() {
		StringBuffer sb = new StringBuffer("FileTransferParams[");
		sb.append(remoteFile).append(";").append(chunkSize).append(";");
		sb.append(waitTime).append(";");
		sb.append(startDate).append(";").append(includeServer).append(";");
		sb.append(length).append(";").append(rate).append(";");
		sb.append(progressListener).append("]");
		return sb.toString();
	}
}