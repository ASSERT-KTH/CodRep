public class SharedObjectDeactivatedEvent implements ISharedObjectDeactivatedEvent {

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

public class SharedObjectDeactivatedEvent implements ContainerEvent {

    private final ID deactivatedID;
    private final ID localContainerID;

    public SharedObjectDeactivatedEvent(ID container, ID deact) {
        super();
        this.localContainerID = container;
        this.deactivatedID = deact;
    }
    public ID getDeactivatedID() {
        return deactivatedID;
    }
    public ID getLocalContainerID() {
        return localContainerID;
    }
    public String toString() {
        StringBuffer sb = new StringBuffer("SharedObjectDeactivatedEvent {");
        sb.append("deactivatedID: ").append(deactivatedID).append(", ");
        sb.append("localContainerID: ").append(localContainerID).append("}");
        return sb.toString();
    }
}
 No newline at end of file