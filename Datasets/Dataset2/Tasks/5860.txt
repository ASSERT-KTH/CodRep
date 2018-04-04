return new JUnicastRefSf(ref, cis, JInterceptorStore.getJRMPInitializers(), -2);

/*
 * @(#) JUnicastServerRefSf.java	1.0 02/07/15
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
package org.objectweb.carol.rmi.jrmp.server;

//sun import 
import java.io.ObjectOutput;
import java.rmi.server.RMIClientSocketFactory;
import java.rmi.server.RMIServerSocketFactory;
import java.rmi.server.RemoteRef;

import org.objectweb.carol.rmi.jrmp.interceptor.JClientRequestInterceptor;
import org.objectweb.carol.rmi.jrmp.interceptor.JInterceptorStore;
import org.objectweb.carol.rmi.jrmp.interceptor.JServerRequestInterceptor;

import sun.rmi.transport.LiveRef;

/**
 * Class <code>JUnicastServerRefSf</code> implements the remote reference layer server-side
 * behavior for remote objects exported with the JUnicastRefSf reference
 * type.
 * 
 * @author  Guillaume Riviere (Guillaume.Riviere@inrialpes.fr)
 * @version 1.0, 15/07/2002    
 */
public class JUnicastServerRefSf extends JUnicastServerRef {

   /**
     * constructor 
     */    
    public JUnicastServerRefSf() {
    }
    /**
     * Constructor  with interceptor
     * Create a new Unicast Server RemoteRef.
     * @param liveRef the live reference
     * @param sis the server interceptor array
     * @param cis the client interceptor array   
     */
    public JUnicastServerRefSf(LiveRef ref, JServerRequestInterceptor [] sis, JClientRequestInterceptor [] cis) {
        super(ref, sis, cis);
    }
   /**
     * Constructor  with interceptor and custum sckets factories 
     * @param port the port reference
     * @param csf the client socket factory 
     * @param sf the server socket factory      
     * @param sis the server interceptor array
     * @param cis the client interceptor array
     */
    public JUnicastServerRefSf(int port,
                                 RMIClientSocketFactory csf,
                                 RMIServerSocketFactory ssf, 
			       JServerRequestInterceptor [] sis, 
			       JClientRequestInterceptor [] cis) {
        super(new LiveRef(port, csf, ssf), sis, cis);
    }

    /**
     * get the ref class name
     * @return String the class name
     */    
    public String getRefClass(ObjectOutput out) {
        super.getRefClass(out);
        return "org.objectweb.carol.rmi.jrmp.server.JUnicastServerRefSf";
    }

    /**
     * use a different kind of RemoteRef instance
     * @return remoet Ref the remote reference
     */
    protected RemoteRef getClientRef() {
        return new JUnicastRefSf(ref, cis, JInterceptorStore.getJRMPInitializers());
    }
}