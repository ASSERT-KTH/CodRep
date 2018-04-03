rk = new RemoteKey(spaceID, InetAddress.getLocalHost().getAddress());

/*
 * @(#) JClientInterceptorHelper.java	1.0 02/07/15
 *
 * Copyright (C) 2002 - INRIA (www.inria.fr)
 *
 * CAROL: Common Architecture for RMI ObjectWeb Layer
 *
 * This library is developed inside the ObjectWeb Consortium,
 * http://www.objectweb.org
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2.1 of the License, or any later version.
 * 
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 * 
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307
 * USA
 * 
 *
 */
package org.objectweb.carol.rmi.jrmp.interceptor;

//java import 
import java.io.IOException;
import java.io.ObjectInput;
import java.io.ObjectOutput;
import java.rmi.server.UID;
import java.net.InetAddress;

import org.objectweb.carol.util.configuration.TraceCarol;

/**
 * Class <code>JInterceptorHelper</code> is the CAROL JRMP Interceptor Helper 
 * this class is used by the other pakage class to manage interceptions 
 * 
 * @author  Guillaume Riviere (Guillaume.Riviere@inrialpes.fr)
 * @version 1.0, 15/07/2002
 */
public abstract class JInterceptorHelper {
    
    // int value for context propagation optimization
    protected static final int NO_CTX     = 0;
    protected static final int REMOTE_CTX = 1;
    protected static final int LOCAL_CTX  = 2;
    

    /**
     * The spaceID
     */
    protected static RemoteKey rk = null;   
    
    /**
     * The spaceID
     */
    protected static UID spaceID = null;

    /**
     * hold a unique identifier of this class and jvm
     */
    public static RemoteKey getRemoteKey() {
        return rk;
    }

    static {
	try {
	    spaceID = new UID();
	    rk = new RemoteKey(spaceID, InetAddress.getLocalHost());
	} catch (Exception e) {
	    e.printStackTrace();
	}
    }

}