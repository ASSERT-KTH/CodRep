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

import org.eclipse.core.runtime.IAdaptable;

class TreeObject implements IAdaptable {
    protected String name;
    private TreeParent parent;
    public TreeObject(String name) {
        this.name = name;
    }
    public Object getAdapter(Class key) {
        return null;
    }
    public String getName() {
        return name;
    }
    public TreeParent getParent() {
        return parent;
    }
    public void setParent(TreeParent parent) {
        this.parent = parent;
    }
    public String toString() {
        return getName();
    }
}
 No newline at end of file