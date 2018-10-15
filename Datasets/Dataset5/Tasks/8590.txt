public Class[][] getSupportedParameterTypes() {

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

import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDCreateException;
import org.eclipse.ecf.core.identity.Namespace;
import org.eclipse.osgi.util.NLS;

public final class TorrentNamespace extends Namespace {

	private static final long serialVersionUID = 253376096062553775L;

	private static final String SCHEME = "torrent"; //$NON-NLS-1$

	public ID createInstance(Object[] args) throws IDCreateException {
		if (args == null || args.length == 0) {
			throw new IDCreateException(
					BitTorrentMessages.TorrentNamespace_InvalidParameter);
		} else {
			File file = null;
			if (args[0] instanceof String) {
				file = new File((String) args[0]);
			} else if (args[0] instanceof File) {
				file = (File) args[0];
			} else {
				throw new IDCreateException(
						BitTorrentMessages.TorrentNamespace_InvalidParameter);
			}

			if (file.isDirectory()) {
				throw new IDCreateException(NLS.bind(
						BitTorrentMessages.TorrentNamespace_FileIsDirectory,
						file.getAbsolutePath()));
			} else if (file.canRead()) {
				return new TorrentID(this, file);
			} else {
				throw new IDCreateException(NLS.bind(
						BitTorrentMessages.TorrentNamespace_CannotReadFile,
						file.getAbsolutePath()));
			}
		}
	}

	public String getScheme() {
		return SCHEME;
	}

	public Class[][] getSupportedParamterTypes() {
		return new Class[][] { { String.class }, { File.class } };
	}

}