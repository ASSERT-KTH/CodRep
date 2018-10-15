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
import org.eclipse.ecf.ui.SharedImages;
import org.eclipse.swt.graphics.Image;

public class RosterBuddy extends RosterParent {
	IPresence presence = null;

	ID svcID = null;

	public RosterBuddy(ID svcID, String name, ID id, IPresence p) {
		super(name, id);
		this.svcID = svcID;
		this.presence = p;
	}

	public IPresence getPresence() {
		return presence;
	}

	public void setPresence(IPresence p) {
		this.presence = p;
	}

	public ID getServiceID() {
		return svcID;
	}

	public Image getImage() {
		IPresence p = getPresence();
		if (p != null) {
			IPresence.Type pType = p.getType();
			IPresence.Mode pMode = p.getMode();
			// If type is unavailable then we're unavailable
			if (pType.equals(IPresence.Type.AVAILABLE)) {
				// if type and mode are both 'available' then we're actually
				// available
				if (pMode.equals(IPresence.Mode.AVAILABLE))
					return SharedImages
							.getImage(SharedImages.IMG_USER_AVAILABLE);
				// If mode is away then we're away
				else if (pMode.equals(IPresence.Mode.AWAY)
						|| pMode.equals(IPresence.Mode.EXTENDED_AWAY))
					return SharedImages.getImage(SharedImages.IMG_USER_AWAY);
			}
		}
		return SharedImages.getImage(SharedImages.IMG_USER_UNAVAILABLE);
	}
}
 No newline at end of file