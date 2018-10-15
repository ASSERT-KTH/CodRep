package org.eclipse.ecf.tests.provider.xmpp;

/****************************************************************************
 * Copyright (c) 2008 Composent, Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Composent, Inc. - initial API and implementation
 *****************************************************************************/

package org.ecllpse.ecf.tests.provider.xmpp;

import org.eclipse.ecf.tests.presence.AbstractChatRoomTest;

/**
 *
 */
public class ChatRoomTest extends AbstractChatRoomTest {

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.tests.presence.AbstractPresenceTestCase#getClientContainerName()
	 */
	protected String getClientContainerName() {
		return XMPPS.CONTAINER_NAME;
	}

}