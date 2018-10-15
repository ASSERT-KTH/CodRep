if (!getContext().isGroupManager()) {

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

package org.eclipse.ecf.example.collab.share.url;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

import org.eclipse.ecf.core.ISharedObjectConfig;
import org.eclipse.ecf.core.SharedObjectDescription;
import org.eclipse.ecf.core.SharedObjectInitException;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.example.collab.Trace;
import org.eclipse.ecf.example.collab.share.GenericSharedObject;


public class ExecURL extends GenericSharedObject {
	
	public static Trace debug = Trace.create("urlsharedobject");
	
	ID receiver;
	String url;
	
	// Host
	public ExecURL(ID rcvr, String url) {
		this.receiver = rcvr;
		this.url = url;
	}
	public ExecURL() {
        
    }
    public void init(ISharedObjectConfig config) throws SharedObjectInitException {
        super.init(config);
        Map props = config.getProperties();
        debug("props is "+props);
        Object [] args = (Object []) props.get("args");
        debug("args is "+args);
        if (args != null && args.length > 1) {
            receiver = (ID) args[0];
            url = (String) args[1];
            debug("url is now "+url);
        }
    }
	public ExecURL(String url) {
		this.url = url;
	}
	protected void debug(String msg) {
		if (Trace.ON && debug != null) {
			debug.msg(msg);
		}
	}
	protected void debug(Throwable t, String msg) {
		if (Trace.ON && debug != null) {
			debug.dumpStack(t,msg);
		}
	}
	protected String getURL() {
		return url;
	}
	protected SharedObjectDescription getReplicaDescription(ID remoteMember)
	{
		String types[] = { ID.class.getName(), String.class.getName()}; 
		Object args[] = { receiver, url };
        HashMap map = new HashMap();
        map.put("args",args);
        map.put("types",types);
        return new SharedObjectDescription(getHomeContainerID(),
                                        getClass().getName(),
                                        map,
                                        replicateID++);
	}
	
	protected void replicate(ID remoteMember)
	{
        debug("replicateSelf("+remoteMember+")");
        // If we don't have a specific receiver, simply allow superclass to handle replication.
        if (receiver == null) { super.replicate(remoteMember); return; }
        // If we do have a specific receiver, only send create message to the specific receiver
        // if we're replicating on activation
        else if (remoteMember == null) {
            try {
                SharedObjectDescription createInfo = getReplicaDescription(receiver);
                if (createInfo != null) {
                     getContext().sendCreate(receiver, createInfo);
                }
            } catch (IOException e) {
                traceDump("Exception in replicateSelf",e);
                return;
            }
        }
	}
	
	public void activated(ID [] others) {
		debug("activated()");
		try {
			if (!getContext().isGroupServer()) {
				GetExec.showURL(url,true);
			} else {
				debug("Not executing commands because is server");
			}
		} catch (Exception e) {
			debug(e, "Exception on startup()");
			/*
			 * For now, just ignore failure.
			 */
		}
		super.activated(others);
		destroySelfLocal();
	}


}