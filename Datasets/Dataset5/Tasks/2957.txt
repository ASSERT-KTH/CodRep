public interface IConfigViewer {

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

package org.eclipse.ecf.ui.views;

import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.user.IUser;

public interface ILocalUserSettable {
    
    public void setLocalUser(IUser user, ITextInputHandler inputHandler);
    public void setGroup(ID groupManager);
    public void memberDeparted(ID member);
}