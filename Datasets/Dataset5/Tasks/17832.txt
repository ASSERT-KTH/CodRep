public class SharedObjectContainerDepartedEvent implements ISharedObjectContainerDepartedEvent {

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

public class SharedObjectContainerDepartedEvent implements ContainerEvent {

    private final ID departedContainerID;
    private final ID localContainerID;

    public SharedObjectContainerDepartedEvent(ID container, ID o) {
        super();
        this.localContainerID = container;
        this.departedContainerID = o;
    }

    public ID getDepartedContainerID() {
        return departedContainerID;
    }
    public ID getLocalContainerID() {
        return localContainerID;
    }
    
    /* (non-Javadoc)
	 * @see java.lang.Object#toString()
	 */
	public String toString() {
		StringBuffer buf = new StringBuffer("SharedObjectContainerDepartedEvent {");
		buf.append("departedContainerID: ").append(departedContainerID).append(", ");
		buf.append("localContainerID: ").append(localContainerID).append("}");
		return buf.toString();
	}
}
 No newline at end of file