public class ContainerHolder implements IContainerHolder {

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
package org.eclipse.ecf.ui;

import org.eclipse.ecf.core.ContainerTypeDescription;
import org.eclipse.ecf.core.IContainer;

public class ContainerHolder {

	protected IContainer container;
	protected ContainerTypeDescription containerTypeDescription;
	
	public ContainerHolder(ContainerTypeDescription containerTypeDescription, IContainer container) {
		this.containerTypeDescription = containerTypeDescription;
		this.container = container;
	}
	
	public IContainer getContainer() {
		return this.container;
	}
	
	public ContainerTypeDescription getContainerTypeDescription() {
		return this.containerTypeDescription;
	}
	
	public String toString() {
		StringBuffer buf = new StringBuffer("ContainerHolder[");
		buf.append(containerTypeDescription).append(";");
		buf.append(container).append("]");
		return buf.toString();
	}
}