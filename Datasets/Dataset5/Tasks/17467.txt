package org.eclipse.ecf.internal.ui.deprecated.views;

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
import org.eclipse.ecf.presence.IPresence;

public interface ILocalInputHandler {
	public void inputText(ID userID, String text);

	public void startTyping(ID userID);

	public void updatePresence(ID userID, IPresence presence);

	public void sendRosterAdd(String user, String name, String[] groups);

	public void sendRosterRemove(ID userID);

	public void disconnect();
}