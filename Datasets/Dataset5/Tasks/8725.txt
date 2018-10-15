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

import org.eclipse.core.resources.ResourcesPlugin;
import org.eclipse.jface.viewers.IStructuredContentProvider;
import org.eclipse.jface.viewers.ITreeContentProvider;
import org.eclipse.jface.viewers.Viewer;

class ViewContentProvider implements IStructuredContentProvider,
		ITreeContentProvider {
	private TreeParent invisibleRoot;
	private TreeParent presenceRoot;
	protected LineChatClientView view;

    public ViewContentProvider(LineChatClientView view) {
        super();
        this.view = view;
    }
	public void dispose() {
	}

	public Object[] getChildren(Object parent) {
		if (parent instanceof TreeParent) {
			return ((TreeParent) parent).getChildren();
		}
		return new Object[0];
	}

	public Object[] getElements(Object parent) {
		
		if (parent.equals(ResourcesPlugin.getWorkspace())) {
			if (presenceRoot == null)
				initialize();
			return getChildren(presenceRoot);
		}
		return getChildren(parent);

	}

	public Object getParent(Object child) {
		if (child instanceof TreeObject) {
			return ((TreeObject) child).getParent();
		}
		return null;
	}

	public TreeParent getPresenceRoot() {
		return presenceRoot;
	}

	public TreeParent getRoot() {
		return invisibleRoot;
	}

	public boolean hasChildren(Object parent) {
		if (parent instanceof TreeParent)
			return ((TreeParent) parent).hasChildren();
		return false;
	}

	private void initialize() {
		presenceRoot = new TreeParent(view,LineChatClientView.TREE_HEADER);
		invisibleRoot = new TreeParent(view, "");
		invisibleRoot.addChild(presenceRoot);
	}

	public void inputChanged(Viewer v, Object oldInput, Object newInput) {
	}
}
 No newline at end of file