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

import java.util.Iterator;

import org.eclipse.ecf.example.collab.share.User;
import org.eclipse.jface.viewers.ISelection;
import org.eclipse.jface.viewers.IStructuredSelection;
import org.eclipse.jface.viewers.TreeViewer;
import org.eclipse.swt.widgets.Composite;

class ChatTreeViewer extends TreeViewer {
	ChatTreeViewer(Composite parent, int options) {
		super(parent, options);
	}

	private User findUserNode(TreeObject to) {
		if (to == null)
			return null;
		if (to instanceof TreeUser) {
			TreeUser tu = (TreeUser) to;
			return tu.getUser();
		}
		if (to instanceof TreeParent) {
			return findUserNode(((TreeParent) to).getParent());
		}
		return null;
	}

	public User getSelectionUser() {
		User result = null;
		ISelection s = getSelection();
		if (s != null && s instanceof IStructuredSelection) {
			IStructuredSelection ss = (IStructuredSelection) s;
			for (Iterator i = ss.iterator(); i.hasNext();) {
				Object o = i.next();
				result = findUserNode((TreeObject) o);
				if (result != null)
					return result;
			}
		}
		return null;
	}
}
 No newline at end of file