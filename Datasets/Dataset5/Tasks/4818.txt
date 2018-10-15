package org.eclipse.ecf.internal.provider.xmpp.smack;

/*******************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.provider.xmpp.smack;

import org.eclipse.ecf.provider.comm.AsynchEvent;
import org.eclipse.ecf.provider.comm.IAsynchConnection;
import org.jivesoftware.smack.packet.Packet;

public class ECFConnectionPacketEvent extends AsynchEvent {

	private static final long serialVersionUID = 7000820721266245824L;

	public ECFConnectionPacketEvent(IAsynchConnection source, Packet p) {
		super(source,p);
	}
	
	public String toString() {
	    StringBuffer sb = new StringBuffer("ECFConnectionPacketEvent[");
	    sb.append(getData()).append(";");
	    sb.append(getConnection()).append("]");
	    return sb.toString();
	}
}