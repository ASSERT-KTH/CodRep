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
import org.jivesoftware.smack.packet.Message;

/**
 * @author slewis
 *
 */
public class MessageEvent implements Event {
    
	private static final long serialVersionUID = 6940577888021931351L;
	protected Message message = null;
    
    public MessageEvent(Message message) {
        this.message = message;
    }
    
    public Message getMessage() {
        return message;
    }
    
    public String toString() {
        StringBuffer buf = new StringBuffer("MessageEvent[");
        buf.append(message).append(";").append((message==null)?"":message.toXML()).append("]");
        return buf.toString();
    }
}