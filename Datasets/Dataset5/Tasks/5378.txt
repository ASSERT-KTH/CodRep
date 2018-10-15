return (sharedObjectReceiverIDs==null)?new ID[0]:sharedObjectReceiverIDs;

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

/**
 * @author slewis
 *
 */
public class SharedObjectManagerConnectEvent implements
        ISharedObjectManagerEvent {
    ID localContainerID = null;
    ID [] sharedObjectReceiverIDs = null;
    
    ID sharedObjectSenderID = null;
    
    public SharedObjectManagerConnectEvent(ID localContainerID, ID sharedObjectSenderID, ID [] sharedObjectReceiverIDs) {
        this.localContainerID = localContainerID;
        this.sharedObjectSenderID = sharedObjectSenderID;
        this.sharedObjectReceiverIDs = sharedObjectReceiverIDs;
    }
    /* (non-Javadoc)
     * @see org.eclipse.ecf.core.events.IContainerEvent#getLocalContainerID()
     */
    public ID getLocalContainerID() {
        return localContainerID;
    }
    public ID[] getSharedObjectReceiverIDs() {
        return sharedObjectReceiverIDs;
    }
    public ID getSharedObjectSenderID() {
        return sharedObjectSenderID;
    }
    public String toString() {
        StringBuffer buf = new StringBuffer("SharedObjectManagerConnectEvent[");
        buf.append(getLocalContainerID()).append(";");
        buf.append(getSharedObjectSenderID()).append(";");
        buf.append(Arrays.asList(getSharedObjectReceiverIDs())).append("]");
        return buf.toString();
    }
}