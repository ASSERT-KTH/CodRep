import org.eclipse.ecf.presence.chatroom.IChatRoomManager;

/****************************************************************************
 * Copyright (c) 2005 Composent, Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Chris Aniszczyk <zx@us.ibm.com> - initial API and implementation
 *****************************************************************************/
package org.eclipse.ecf.presence;

import java.util.List;
import java.util.Vector;

import org.eclipse.core.runtime.Platform;
import org.eclipse.ecf.presence.chat.IChatRoomManager;

/**
 * An abstract {@link IPresenceContainerAdapter} implementation. This class is
 * intended to be subclassed.
 */
public abstract class AbstractPresenceContainer implements
		IPresenceContainerAdapter {

	private Vector messageListeners = new Vector();

	/**
	 * @see org.eclipse.ecf.presence.IPresenceContainerAdapter#addMessageListener(org.eclipse.ecf.presence.IMessageListener)
	 */
	public void addMessageListener(IMessageListener listener) {
		messageListeners.add(listener);
	}

	/**
	 * Remove a message listener
	 * 
	 * @param listener
	 */
	public void removeMessageListener(IMessageListener listener) {
		messageListeners.remove(listener);
	}

	/**
	 * @see org.eclipse.core.runtime.IAdaptable#getAdapter(java.lang.Class)
	 */
	public Object getAdapter(Class adapter) {
		return Platform.getAdapterManager().getAdapter(this, adapter);
	}

	/**
	 * @return The list of message listeners
	 */
	public List getMessageListeners() {
		return messageListeners;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.presence.IPresenceContainerAdapter#getAccountManager()
	 */
	public IAccountManager getAccountManager() {
		return null;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.presence.IPresenceContainerAdapter#getChatRoomManager()
	 */
	public IChatRoomManager getChatRoomManager() {
		return null;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.presence.IPresenceContainerAdapter#getPresenceSender()
	 */
	public IPresenceSender getPresenceSender() {
		return null;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.presence.IPresenceContainerAdapter#getMessageSender()
	 */
	public IMessageSender getMessageSender() {
		return null;
	}

}