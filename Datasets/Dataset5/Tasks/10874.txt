package org.eclipse.ecf.presence;

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

package org.eclipse.ecf.presence.im;

/**
 * IM message listener.  This listener receives IIMMessageEvents.
 */
public interface IIMMessageListener {

	/**
	 * Handle message event (reception of chat, typing, or object message).
	 * 
	 * @param messageEvent
	 *            the event instance to handle. Will not be null.
	 */
	public void handleMessageEvent(IIMMessageEvent messageEvent);

}