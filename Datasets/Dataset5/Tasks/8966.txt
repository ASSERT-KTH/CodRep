if (!getContext().isGroupManager() || includeServer.equals(Boolean.TRUE)) {

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


public class ExecProg extends GenericSharedObject
{
    public static Trace myDebug = Trace.create("progsharedobject");
    public static final Boolean DEFAULT_INCLUDE_SERVER = Boolean.FALSE;
    // Host values
    protected String [] cmds;
    protected String [] env;
    // Values specifically for replicas
    protected String [] replicaCmds;
    protected String [] replicaEnv;

    protected ID receiver;
    protected Process proc = null;
    public Boolean includeHost;
    protected Boolean includeServer;

    public ExecProg() {
        
    }
    public ExecProg(ID rcvr, String cmds[], String env[],
           Boolean includeHost, Boolean includeServer) throws Exception
    {
        receiver = rcvr;
        this.cmds = cmds;
        this.env = ((env == null)?new String[0]:env);
        this.includeHost = includeHost;
        if (includeServer == null) this.includeServer = DEFAULT_INCLUDE_SERVER;
        else this.includeServer = includeServer;
    }
	protected void debug(String msg) {
		if (Trace.ON && myDebug != null) {
			myDebug.msg(msg);
		}
	}
	protected void debug(Throwable t, String msg) {
		if (Trace.ON && myDebug != null) {
			myDebug.dumpStack(t,msg);
		}
	}
    public ExecProg(ID rcvr, String hostCmds[], String hostEnv[],
           String replicaCmds[], String replicaEnv[], Boolean includeHost, Boolean includeServer)
        throws Exception
    {
        this(rcvr, hostCmds, hostEnv, includeHost, includeServer);
        this.replicaCmds = replicaCmds;
        this.replicaEnv = replicaEnv;
    }

    public ExecProg(ID rcvr, String cmds[], String env[]) throws Exception
    {
        this(rcvr, cmds, env, Boolean.FALSE, null);
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

    public void init(ISharedObjectConfig config) throws SharedObjectInitException {
        super.init(config);
        Map props = config.getProperties();
        debug("props is "+props);
        Object [] args = (Object []) props.get("args");
        debug("args is "+args);
        if (args != null && args.length > 4) {
            receiver = (ID) args[0];
            cmds = (String []) args[1];
            env = (String []) args[2];
            includeHost = (Boolean) args[3];
            includeServer = (Boolean) args[4];
        }
        
    }
    protected SharedObjectDescription getReplicaDescription(ID remoteMember)
    {
        String types[] = { ID.class.getName(), String.class.getName(),String.class.getName(), "[Ljava.lang.String;", Boolean.class.getName(), Boolean.class.getName() };
        Object args[] = { receiver, (replicaCmds==null)?cmds:replicaCmds, (replicaEnv==null)?env:replicaEnv, includeHost, includeServer };
        HashMap map = new HashMap();
        map.put("args",args);
        map.put("types",types);
        return new SharedObjectDescription(getHomeContainerID(),
                                        getClass().getName(),
                                        map,
                                        replicateID++);
    }

    public void activated(ID [] others)
    {
        debug("activated()");
        try {
            if (!getContext().isGroupServer() || includeServer.equals(Boolean.TRUE)) {
                startup();
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
        postActivated();
    }

    /**
     *  Method called within the 'activated' message handler.  This method is called after the
     *  activated method completes its operations.
     */
    protected void postActivated()
    {
        debug("postActivated()");
    }

    protected void startup() throws Exception
    {
        debug("startup()");
        if (cmds != null) {
            // This is all trace output
            if (Trace.ON && myDebug != null) {
                myDebug.msg("Executing command line:");
                if (cmds != null) {
                    for(int i=0; i < cmds.length; i++) {
                        myDebug.msg("  "+cmds[i]+" ");
                    }
                }
                myDebug.msg("With enviromnent:");
                if (env != null) {
                    for(int i=0; i < env.length; i++) {
                        myDebug.msg("  "+env[i]+" ");
                    }
                }
            }
            // Here's the real action
            if (env==null || env.length==0) {
                if (cmds.length ==1) {
                    proc = Runtime.getRuntime().exec(cmds[0]);
                } else proc = Runtime.getRuntime().exec(cmds);
            } else {
                proc = Runtime.getRuntime().exec(cmds, (env.length==0)?null:env);
            }
        }
    }

}