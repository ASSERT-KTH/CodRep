package org.eclipse.ecf.internal.ui.deprecated.views;

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
package org.eclipse.ecf.ui.views;

import java.util.ArrayList;
import java.util.Iterator;

import org.eclipse.ecf.core.identity.ID;

public class RosterParent extends RosterObject {
	protected ArrayList children;

	public RosterParent(String name) {
		super(name);
		children = new ArrayList();
	}

	public RosterParent(String name, ID id) {
		super(name, id);
		children = new ArrayList();
	}

	public void addChild(RosterObject child) {
		children.add(child);
		child.setParent(this);
	}

	public void removeChild(RosterObject child) {
		children.remove(child);
		child.setParent(null);
	}

	public void removeChildren() {
		for (Iterator i = children.iterator(); i.hasNext();) {
			RosterObject obj = (RosterObject) i.next();
			obj.setParent(null);
		}
		children.clear();
	}

	public RosterObject[] getChildren() {
		return (RosterObject[]) children.toArray(new RosterObject[children
				.size()]);
	}

	public boolean hasChildren() {
		return children.size() > 0;
	}
}
 No newline at end of file