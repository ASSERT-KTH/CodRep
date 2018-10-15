//public IChatRoomContainer createChatRoomContainer() throws ContainerInstantiationException;

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
package org.eclipse.ecf.presence.chat;

import org.eclipse.ecf.core.ContainerInstantiationException;
import org.eclipse.ecf.core.identity.ID;

public interface IChatRoomManager {
	
	/**
	 * Get parent IChatRoomManager.  If this manager is the root, then this method
	 * returns null.
	 * @return IChatRoomManager instance if this manager has a parent.  Returns null if this manager is the
	 * root of the hierarchy 
	 */
	public IChatRoomManager getParent();
	/**
	 * Get any children managers of this IChatRoomManager.  If this chat room manager
	 * has children chat room managers, then the returned array will have more than zero elements.
	 * If this IChatRoomManager has no children, then a zero-length array will be returned.
	 * 
	 * @return IChatRoomManager[] of children for this chat room manager.  If no children,
	 * a zero-length array will be returned.  Null will not be returned.
	 */
	public IChatRoomManager[] getChildren();
	
	/**
	 * Get IDs for chat rooms available via this chat room manager
	 * @return null if no access provided to chat room identities
	 */
	public ID[] getChatRooms();
	/**
	 * Get detailed room info for given room id
	 * @param roomID the id of the room to get detailed info for
	 * @return IRoomInfo an instance that provides the given info
	 */
	public IRoomInfo getChatRoomInfo(ID roomID);
	/**
	 * Get detailed room info for all chat rooms associated with this manager
	 * @return IRoomInfo an array of instances that provide info for all chat rooms
	 */
	public IRoomInfo[] getChatRoomsInfo();
   	/**
	 * Create a new IChatRoomContainer instance
	 * @return non-null IChatRoomContainer implementer
	 * @throws ContainerInstantiationException if chat room container cannot be made
	 */
	public IChatRoomContainer createChatRoomContainer() throws ContainerInstantiationException;
	
}