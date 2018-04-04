jri.add_request_service_context(new DummyClientServiceContext(CLIENT_CTX_ID, java.net.InetAddress.getLocalHost().getHostName()));

/*
 * @(#) DummyClientInterceptor.java	1.0 02/07/15
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

// Carol JRMP API Import
import org.objectweb.carol.rmi.jrmp.interceptor.JClientRequestInterceptor;
import org.objectweb.carol.rmi.jrmp.interceptor.JClientRequestInfo;

/**
 * Class <code>DummyClientServiceContext</code> is a JRMP Dummy client interceptor
 * for carol testing
 * 
 * @author  Guillaume Riviere (Guillaume.Riviere@inrialpes.fr)
 * @version 1.0, 15/07/2002
 */
public class DummyClientInterceptor implements JClientRequestInterceptor {

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
    public DummyClientInterceptor(String name) {
	interceptorName = name;
    }

    /**
     * get the name of this interceptor
     * @return name
     */
    public String name() {
	return interceptorName;
    } 

    /**
     * send client context with the request. The sendingRequest method of the JPortableInterceptors
     * is called prior to marshalling arguments and contexts
     * @param JClientRequestInfo jri the jrmp client info 
     * @exception IOException if an exception occur with the ObjectOutput
     */
    public void send_request(JClientRequestInfo jri) throws IOException {
	//	System.out.println("JRMP ClientInterceptor Add/Send Dummy Client Service Context");
	jri.add_request_service_context(new DummyClientServiceContext(CLIENT_CTX_ID, java.net.InetAddress.getLocalHost().getHostName()), true);
    }

    /**
     * Receive reply interception
     * @param JClientRequestInfo jri the jrmp client info 
     * @exception IOException if an exception occur with the ObjectOutput
     */
    public void receive_reply(JClientRequestInfo jri)throws IOException{
	//System.out.print("JRMP ClientInterceptor Get/Receive Dummy Server Service Context: ");
	//System.out.println((DummyServerServiceContext)jri.get_reply_service_context(SERVER_CTX_ID));
	
    }

    // empty method
    public void send_poll(JClientRequestInfo jri) throws IOException {
    }

    public void receive_exception(JClientRequestInfo jri) throws IOException {
    }

    public void receive_other(JClientRequestInfo jri) throws IOException {
    }
}