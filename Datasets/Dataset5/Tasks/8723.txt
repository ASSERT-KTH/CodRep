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

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

import org.eclipse.ecf.example.collab.share.TreeItem;

class TreeParent extends TreeObject {
    private List children;
    private TreeItem treeItem;
    public TreeParent(LineChatClientView view, String name) {
        super(name);
        children = Collections.synchronizedList(new ArrayList());
    }
    public TreeParent(LineChatClientView view, TreeItem item) {
        this(view, item.toString());
        treeItem = item;
    }
    public void addChild(TreeObject child) {
        children.add(child);
        child.setParent(this);
    }
    public List children() {
        return children;
    }
    public TreeObject[] getChildren() {
        return (TreeObject[]) children.toArray(new TreeObject[children
                .size()]);
    }
    public TreeItem getTreeItem() {
        return treeItem;
    }
    public boolean hasChildren() {
        return children.size() > 0;
    }
    public void removeAllChildren() {
        synchronized (children) {
            for (int i = 0; i < children.size(); i++) {
                TreeObject child = (TreeObject) children.remove(i);
                child.setParent(null);
            }
        }
    }
    public void removeChild(TreeObject child) {
        children.remove(child);
        child.setParent(null);
    }
}
 No newline at end of file