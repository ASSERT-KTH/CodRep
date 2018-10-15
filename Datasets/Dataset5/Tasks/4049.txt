File getFile() {

/*******************************************************************************
 * Copyright (c) 2006, 2007 Remy Suen, Composent Inc., and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Remy Suen <remy.suen@gmail.com> - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.internal.provider.bittorrent;

import java.io.File;
import java.net.MalformedURLException;
import java.net.URL;

import org.eclipse.ecf.core.identity.Namespace;
import org.eclipse.ecf.filetransfer.identity.IFileID;

public final class TorrentID implements IFileID {

	private static final long serialVersionUID = 4350711107160524282L;

	private final Namespace namespace;

	private final File file;

	private final String name;

	TorrentID(Namespace namespace, File file) {
		this.namespace = namespace;
		this.file = file;
		name = file.getName();
	}
	
	public boolean equals(Object obj) {
		if (obj == null) {
			return false;
		} else if (obj == this) {
			return true;
		} else if (obj instanceof TorrentID) {
			return file.equals(((TorrentID) obj).file);
		} else {
			return false;
		}
	}
	
	public int hashCode() {
		return file.hashCode();
	}

	public String getFilename() {
		return name;
	}

	public String getName() {
		return name;
	}

	public Namespace getNamespace() {
		return namespace;
	}

	public String toExternalForm() {
		return file.getAbsolutePath();
	}

	public int compareTo(Object o) {
		return file.compareTo(o);
	}

	public Object getAdapter(Class adapter) {
		return null;
	}

	public File getFile() {
		return file;
	}

	public URL getURL() throws MalformedURLException {
		return file.toURL();
	}

}