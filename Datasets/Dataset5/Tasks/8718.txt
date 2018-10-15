package org.eclipse.ecf.internal.example.collab.ui;

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
package org.eclipse.ecf.example.collab.ui;

import org.eclipse.core.resources.IFile;
import org.eclipse.core.runtime.CoreException;
import org.eclipse.ui.IEditorInput;
import org.eclipse.ui.IEditorPart;
import org.eclipse.ui.editors.text.TextEditor;
import org.eclipse.ui.part.FileEditorInput;

/**
 * A skeleton shared editor based on TextEditor.  
 *
 */
public class SharedEditor extends TextEditor implements IEditorPart {

	protected void doSetInput(IEditorInput input) throws CoreException {		
		super.doSetInput(input);
		
		if (input instanceof FileEditorInput) {
			IFile file = ((FileEditorInput)input).getFile();
			System.out.println("Create EclipseCollabSharedObject for " + file.getFullPath());
		}
		
		
	}
}