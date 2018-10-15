String res = ((n.startsWith("/"))?n:"/"+n); //$NON-NLS-1$ //$NON-NLS-2$

/*******************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.provider.app;

public class NamedGroup {
	Connector parent;
	String name;
	
	public NamedGroup(String name) {
		this.name = name;
	}
	protected void setParent(Connector c) {
		this.parent = c;
	}
	public String getName() {
		return cleanGroupName(name);
	}
	public String getIDForGroup() {
		return parent.getID()+getName();
	}
	protected String cleanGroupName(String n) {
		String res = ((n.startsWith("/"))?n:"/"+n);
		return res;
	}
}
 No newline at end of file