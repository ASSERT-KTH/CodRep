log.debug("Skipping file : " + targetFile.getAbsolutePath() + " cause it exists already");

/*******************************************************************************
 * Copyright (c) 2005, 2006 committers of openArchitectureWare and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     committers of openArchitectureWare - initial API and implementation
 *******************************************************************************/
package org.eclipse.xpand2.output;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.UnsupportedEncodingException;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;

public class FileHandleImpl implements FileHandle {
	private final Log log = LogFactory.getLog(getClass());

	private StringBuffer buffer = new StringBuffer();

	private File targetFile = null;

	private Outlet outlet = null;

	public FileHandleImpl(final Outlet outlet, final File f) {
		this.outlet = outlet;
		targetFile = f.getAbsoluteFile();
	}

	public Outlet getOutlet() {
		return outlet;
	}

	public CharSequence getBuffer() {
		return buffer;
	}

	public void setBuffer(final CharSequence buffer) {
		this.buffer = new StringBuffer(buffer);
	}

	public File getTargetFile() {
		return targetFile;
	}

	public boolean isAppend() {
		return outlet.isAppend();
	}

	public boolean isOverwrite() {
		return outlet.isOverwrite();
	}

	public String getFileEncoding() {
		return outlet.getFileEncoding();
	}

	public void writeAndClose() {
		try {
			if (!isOverwrite() && targetFile.exists()) {
				log.debug("Skipping file : " + targetFile.getAbsolutePath() + " cause it exists allready");
				return;
			}
			log.debug("Opening file : " + targetFile.getAbsolutePath());
			// create all parent directories
			final File parentDir = targetFile.getParentFile();
			if (!parentDir.exists()) {
				parentDir.mkdirs();
				if (!parentDir.isDirectory())
					throw new RuntimeException("Failed to create parent directories of file " + targetFile.getAbsolutePath());
			}
			outlet.beforeWriteAndClose(this);
			if (outlet.shouldWrite(this)) {
				FileOutputStream out = null;
				try {
					out = new FileOutputStream(targetFile, isAppend());
					out.write(getBytes());
				} finally {
					if (out != null) {
						try {
							out.close();
							outlet.afterClose(this);
						} catch (final IOException e) {
							throw new RuntimeException(e);
						}
					}
				}
			}
		} catch (final IOException e) {
			throw new RuntimeException(e);
		}
	}

	public byte[] getBytes() {
		if (getFileEncoding() != null) {
			try {
				return buffer.toString().getBytes(getFileEncoding());
			} catch (UnsupportedEncodingException e) {
				log.error(e.getMessage(), e);
			}
		}
		return buffer.toString().getBytes();
	}
}