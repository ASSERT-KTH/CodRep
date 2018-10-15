targetID = IDFactory.getDefault().makeStringID(COMPOSENT_TARGET);

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

package org.eclipse.ecf.example.collab.actions;

import org.eclipse.ecf.core.identity.IDFactory;


public class ClientConnectComposentAction extends ClientConnectAction {
    
    public static final String COMPOSENT_TARGET = "ecftcp://composent.com:3282/server";
    
	public ClientConnectComposentAction() {
        super();
        try {
            targetID = IDFactory.makeStringID(COMPOSENT_TARGET);
        } catch (Exception e) {
            throw new RuntimeException("Exception in ClientConnectAction()",e);
        }
	}
}
 No newline at end of file