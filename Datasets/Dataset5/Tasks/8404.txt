package org.eclipse.ecf.core.sharedobject.events;

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

package org.eclipse.ecf.core.events;

import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.util.AsynchResult;
import org.eclipse.ecf.core.util.Event;

public class SharedObjectCallEvent implements ISharedObjectCallEvent {
	private static final long serialVersionUID = 3904674977264250933L;
	ID sender;
    Event event;
    AsynchResult result;

    public SharedObjectCallEvent(ID sender, Event evt, AsynchResult res) {
        super();
        this.sender = sender;
        this.event = evt;
        this.result = res;
    }

    /*
     * (non-Javadoc)
     * 
     * @see org.eclipse.ecf.core.events.ISharedObjectCallEvent#getAsynchResult()
     */
    public AsynchResult getAsynchResult() {
        return result;
    }

    /*
     * (non-Javadoc)
     * 
     * @see org.eclipse.ecf.core.events.ISharedObjectEvent#getSenderSharedObjectID()
     */
    public ID getSenderSharedObjectID() {
        return sender;
    }

    /*
     * (non-Javadoc)
     * 
     * @see org.eclipse.ecf.core.events.ISharedObjectEvent#getEvent()
     */
    public Event getEvent() {
        return event;
    }
}
 No newline at end of file