import org.eclipse.ecf.core.sharedobject.events.ISharedObjectMessageEvent;

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

package org.eclipse.ecf.core.sharedobject;

import org.eclipse.ecf.core.events.ISharedObjectMessageEvent;
import org.eclipse.ecf.core.util.Event;
import org.eclipse.ecf.core.util.IEventProcessor;

/**
 * Event processor to process SharedObjectMsgEvents
 *
 */
public class SharedObjectMsgEventProcessor implements IEventProcessor {
	
	AbstractSharedObject sharedObject = null;
	
	public SharedObjectMsgEventProcessor(AbstractSharedObject sharedObject) {
		super();
		this.sharedObject = sharedObject;
	}
	public boolean processEvent(Event event) {
		if (!(event instanceof ISharedObjectMessageEvent)) return false;
		return processSharedObjectMsgEvent((ISharedObjectMessageEvent) event);
	}
	protected boolean processSharedObjectMsgEvent(ISharedObjectMessageEvent event) {
		return sharedObject.handleSharedObjectMsgEvent(event);
	}
}