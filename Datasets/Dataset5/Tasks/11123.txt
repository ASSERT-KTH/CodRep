public void removeRosterSubscribeListener(IRosterSubscribeListener listener) {

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

	private Vector presenceListeners = new Vector();

	private Vector subscribeListeners = new Vector();

	/**
	 * @see org.eclipse.ecf.presence.IPresenceContainerAdapter#addRosterSubscribeListener(org.eclipse.ecf.presence.IRosterSubscribeListener)
	 */
	public void addRosterSubscribeListener(IRosterSubscribeListener listener) {
		subscribeListeners.add(listener);
	}

	/**
	 * @see org.eclipse.ecf.presence.IPresenceContainerAdapter#addPresenceListener(org.eclipse.ecf.presence.IPresenceListener)
	 */
	public void addPresenceListener(IPresenceListener listener) {
		presenceListeners.add(listener);
	}

	/**
	 * @see org.eclipse.ecf.presence.IPresenceContainerAdapter#addMessageListener(org.eclipse.ecf.presence.IMessageListener)
	 */
	public void addMessageListener(IMessageListener listener) {
		messageListeners.add(listener);
	}

	/**
	 * Remove a subscription listener
	 * 
	 * @param listener
	 */
	public void removeSubscribeListener(IRosterSubscribeListener listener) {
		subscribeListeners.remove(listener);
	}

	/**
	 * Remove a presence listener
	 * 
	 * @param listener
	 */
	public void removePresenceListener(IPresenceListener listener) {
		presenceListeners.remove(listener);
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

	/**
	 * @return The list of presence listeners
	 */
	public List getPresenceListeners() {
		return presenceListeners;
	}

	/**
	 * @return The list of {@link IRosterSubscribeListener}
	 */
	public List getSubscribeListeners() {
		return subscribeListeners;
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