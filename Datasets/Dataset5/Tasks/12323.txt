private static final long serialVersionUID = 6880286157835412766L;

/*******************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.core.events;

import org.eclipse.ecf.core.identity.ID;

public class SharedObjectActivatedEvent implements ISharedObjectActivatedEvent {
	private static final long serialVersionUID = 3258416110105079864L;
	private final ID activatedID;
	private final ID localContainerID;

	public SharedObjectActivatedEvent(ID container, ID act) {
		super();
		this.localContainerID = container;
		this.activatedID = act;
	}

	public ID getActivatedID() {
		return activatedID;
	}

	public ID getLocalContainerID() {
		return localContainerID;
	}

	public String toString() {
		StringBuffer sb = new StringBuffer("SharedObjectActivatedEvent[");
		sb.append(getLocalContainerID()).append(";");
		sb.append(getActivatedID()).append("]");
		return sb.toString();
	}
}
 No newline at end of file