package org.eclipse.ecf.internal.example.collab.ui;

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

package org.eclipse.ecf.example.collab.ui;

import org.eclipse.ecf.example.collab.share.User;

class TreeUser extends TreeParent {
    User ud;
    TreeUser(LineChatClientView view, User ud) {
        super(view, ud.getNickname());
        this.ud = ud;
    }
    User getUser() {
        return ud;
    }
}
 No newline at end of file