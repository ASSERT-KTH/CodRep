package org.eclipse.ecf.internal.provider.xmpp.events;

/*******************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.provider.xmpp.events;

import org.eclipse.ecf.core.util.Event;
import org.jivesoftware.smack.packet.Presence;

/**
 * @author slewis
 *
 */
public class PresenceEvent implements Event {
    
	private static final long serialVersionUID = -8207158000504357229L;
	protected Presence presence = null;
    
    public PresenceEvent(Presence presence) {
        this.presence = presence;
    }
    
    public Presence getPresence() {
        return presence;
    }
    public String toString() {
        StringBuffer buf = new StringBuffer("PresenceEvent[");
        buf.append(presence).append(";").append((presence==null)?"":presence.toXML()).append("]");
        return buf.toString();
    }
}