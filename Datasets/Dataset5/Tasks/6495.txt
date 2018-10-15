import org.eclipse.ecf.core.sharedobject.util.IQueueEnqueue;

/*******************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.provider.xmpp.container;

import java.io.IOException;
import java.util.Map;

import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.util.IQueueEnqueue;
import org.eclipse.ecf.provider.generic.SOContainer;
import org.eclipse.ecf.provider.generic.SOContext;
import org.jivesoftware.smack.Roster;
import org.jivesoftware.smack.packet.Presence;

public class XMPPContainerContext extends SOContext {

    public XMPPContainerContext(ID objID, ID homeID, SOContainer cont, Map props, IQueueEnqueue queue) {
        super(objID, homeID, cont, props, queue);
    }
    
    public Object getAdapter(Class clazz) {
        if (clazz.equals(IIMMessageSender.class)) {
            return new IIMMessageSender() {
                public void sendMessage(ID target, String message) throws IOException {
                    ((XMPPClientSOContainer) container).sendMessage(target,message);
                }
                public Roster getRoster() throws IOException {
                    return ((XMPPClientSOContainer) container).getRoster();
                }
				public void sendPresenceUpdate(ID target, Presence presence) throws IOException {
					if (presence == null) throw new NullPointerException("presence cannot be null");
	                ((XMPPClientSOContainer) container).sendPresenceUpdate(target,presence);
				}
				public void sendRosterAdd(String user, String name, String[] groups) throws IOException {
	                ((XMPPClientSOContainer) container).sendRosterAdd(user,name,groups);
				}
				public void sendRosterRemove(String user) throws IOException {
	                ((XMPPClientSOContainer) container).sendRosterRemove(user);
				}
            };
        } else return super.getAdapter(clazz);
    }
}