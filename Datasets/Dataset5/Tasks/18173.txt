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

import org.eclipse.ecf.core.identity.ID;

public class RosterObject {
	
	private String name;

	private RosterParent parent;

	private ID id;

	public RosterObject(String name, ID id) {
		this.name = name;
		this.id = id;
	}

	public RosterObject(String name) {
		this(name, null);
	}

	public String getName() {
		return name;
	}

	public void setName(String name) {
		this.name = name;
	}

	public ID getID() {
		return id;
	}
	
	public void setID(ID newID) {
		this.id = newID;
	}

	public void setParent(RosterParent parent) {
		this.parent = parent;
	}

	public RosterParent getParent() {
		return parent;
	}

	public String toString() {
		return getName();
	}

}
 No newline at end of file