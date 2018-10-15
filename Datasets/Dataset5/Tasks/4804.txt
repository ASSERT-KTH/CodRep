package org.eclipse.ecf.internal.provider.xmpp.deprecated;

/*******************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.provider.xmpp.container;

import org.eclipse.ecf.core.ContainerCreateException;
import org.eclipse.ecf.core.ContainerTypeDescription;
import org.eclipse.ecf.core.IContainer;
import org.eclipse.ecf.core.sharedobject.ISharedObjectContainer;
import org.eclipse.ecf.filetransfer.IOutgoingFileTransferContainerAdapter;
import org.eclipse.ecf.presence.IPresenceContainerAdapter;
import org.eclipse.ecf.presence.chatroom.IChatRoomManager;
import org.eclipse.ecf.provider.generic.GenericContainerInstantiator;

public class XMPPContainerInstantiator extends GenericContainerInstantiator {
	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.provider.IContainerInstantiator#createInstance(ContainerDescription,
	 *      java.lang.Object[])
	 */
	public IContainer createInstance(ContainerTypeDescription description,
			Object[] args) throws ContainerCreateException {
		try {
			Integer ka = new Integer(XMPPClientSOContainer.DEFAULT_KEEPALIVE);
			String name = null;
			if (args != null) {
				if (args.length > 0) {
					name = (String) args[0];
					if (args.length > 1) {
						ka = getIntegerFromArg(args[1]);
					}
				}
			}
			if (name == null) {
				if (ka == null) {
					return new XMPPClientSOContainer();
				} else {
					return new XMPPClientSOContainer(ka.intValue());
				}
			} else {
				if (ka == null) {
					ka = new Integer(XMPPClientSOContainer.DEFAULT_KEEPALIVE);
				}
				return new XMPPClientSOContainer(name, ka.intValue());
			}
		} catch (Exception e) {
			throw new ContainerCreateException(
					"Exception creating generic container", e);
		}
	}

	public String[] getSupportedAdapterTypes(
			ContainerTypeDescription description) {
		return new String[] { IChatRoomManager.class.getName(),
				IPresenceContainerAdapter.class.getName(),
				IOutgoingFileTransferContainerAdapter.class.getName(),
				ISharedObjectContainer.class.getName() };
	}

}
 No newline at end of file