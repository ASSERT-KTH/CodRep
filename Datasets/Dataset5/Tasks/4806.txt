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

/**
 * @author slewis
 *
 */
public class ChatMembershipEvent implements Event {
    
	private static final long serialVersionUID = 8293255412415864623L;
	String id;
	boolean add;
	
    public ChatMembershipEvent(String id, boolean add) {
    	this.id = id;
    	this.add = add;
    }
    
    public String getFrom() {
        return id;
    }
    public boolean isAdd() {
    	return add;
    }
    public String toString() {
        StringBuffer buf = new StringBuffer("ChatMembershipEvent[");
        buf.append(id).append(";").append(add).append("]");
        return buf.toString();
    }
}