public class SharedObjectActivatedEvent implements ISharedObjectActivatedEvent {

/*******************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/

package org.eclipse.ecf.core.events;

import java.util.Arrays;

import org.eclipse.ecf.core.identity.ID;

public class SharedObjectActivatedEvent implements ContainerEvent {

    private final ID activatedID;
    private final ID[] groupMemberIDs;
    private final ID localContainerID;

    public SharedObjectActivatedEvent(ID container, ID act, ID[] others) {
        super();
        this.localContainerID = container;
        this.activatedID = act;
        this.groupMemberIDs = others;
    }

    public ID getActivatedID() {
        return activatedID;
    }

    public ID getLocalContainerID() {
        return localContainerID;
    }
    public ID[] getGroupMemberIDs() {
        return groupMemberIDs;
    }

    public String toString() {
        StringBuffer sb = new StringBuffer("SharedObjectActivatedEvent {");
        sb.append("activatedID: ").append(activatedID).append(", ");
        sb.append("groupMemberIDs: ").append(Arrays.asList(groupMemberIDs)).append(", ");
        sb.append("localContainerID: ").append(localContainerID).append("}");
        return sb.toString();
    }
}
 No newline at end of file