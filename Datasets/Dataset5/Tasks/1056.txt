package org.eclipse.ecf.internal.provisional.docshare;

/****************************************************************************
 * Copyright (c) 2007 Composent, Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Composent, Inc. - initial API and implementation
 *****************************************************************************/

package org.eclipse.ecf.docshare;

import org.eclipse.core.filesystem.IFileStore;
import org.eclipse.ui.ide.FileStoreEditorInput;

public class DocShareEditorInput extends FileStoreEditorInput {

	private final String user;
	private final String fileName;

	public DocShareEditorInput(IFileStore fileStore, String user, String file) {
		super(fileStore);
		this.user = user;
		this.fileName = file;
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ui.IEditorInput#getName()
	 */
	public String getName() {
		return user + ": " + fileName; //$NON-NLS-1$
	}

}
 No newline at end of file