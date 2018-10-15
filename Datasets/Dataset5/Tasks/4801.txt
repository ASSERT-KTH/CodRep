package org.eclipse.ecf.internal.provider.xmpp.deprecated;

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
package org.eclipse.ecf.provider.xmpp.container;

import org.eclipse.ecf.core.sharedobject.ISharedObjectContainerConfig;

public interface IGroupChatContainerConfig extends ISharedObjectContainerConfig {
    
    public String getRoomName();
    public String getOwnerName();
    public String getNickname();
    public String getPassword();
    
}