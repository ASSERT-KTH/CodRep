jri.add_reply_service_context(new DummyServerServiceContext(SERVER_CTX_ID, java.net.InetAddress.getLocalHost().getHostName()));

/*
 * @(#) DummyServerInterceptor.java	1.0 02/07/15
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
package org.objectweb.carol.jtests.conform.interceptor.jrmp;

// java import
import java.io.IOException;

//carol JRMP Interceptor API Import
import org.objectweb.carol.rmi.jrmp.interceptor.JServerRequestInterceptor;
import org.objectweb.carol.rmi.jrmp.interceptor.JServerRequestInfo;

/**
 * Class <code>DummyClientServiceContext</code> is a  JRMP Interface for Interceptor implementation
 * for carol testing
 * 
 * @author  Guillaume Riviere (Guillaume.Riviere@inrialpes.fr)
 * @version 1.0, 15/07/2002
 */
public class DummyServerInterceptor implements  JServerRequestInterceptor {

    /**
     * Server dummy context id
     */
    private static int SERVER_CTX_ID = 50;

    /**
     * Client dummy context id
     */
    private static int CLIENT_CTX_ID = 51;

    /**
     * interceptor name
     */
   private String interceptorName = null;

    /**
     * constructor 
     * @param String name
     */
    public DummyServerInterceptor(String name) {
	interceptorName = name;
    }

    /**
     * Receive request 
     * @param JServerRequestInfo the jrmp server request information
     * @exception IOException if an exception occur with the ObjectOutput
     */
    public void receive_request(JServerRequestInfo jri) throws IOException {	
	//System.out.print("JRMP ServerInterceptor Get/Receive Dummy Client Service Context:");
	//System.out.println((DummyClientServiceContext)jri.get_request_service_context(CLIENT_CTX_ID));
    }

    /**
     * send reply with context
     * @param JServerRequestInfo the jrmp server request information
     * @exception IOException if an exception occur with the ObjectOutput
     */
    public void send_reply(JServerRequestInfo jri)throws IOException {	
	//System.out.println("JRMP ServerInterceptor Add/Send Dummy Server Service Context");
	jri.add_reply_service_context(new DummyServerServiceContext(SERVER_CTX_ID, java.net.InetAddress.getLocalHost().getHostName()), true);
    }

    
     /**
     * get the name of this interceptor
     * @return name
     */
    public String name() {
	return interceptorName;
    } 


    public void send_exception(JServerRequestInfo jri) throws IOException {
    }

    public void send_other(JServerRequestInfo jri) throws IOException {
    }
}