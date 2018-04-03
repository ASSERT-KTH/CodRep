}else serverNameMB.setString( hostHeader);

/*
 * ====================================================================
 *
 * The Apache Software License, Version 1.1
 *
 * Copyright (c) 1999 The Apache Software Foundation.  All rights 
 * reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer. 
 *
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in
 *    the documentation and/or other materials provided with the
 *    distribution.
 *
 * 3. The end-user documentation included with the redistribution, if
 *    any, must include the following acknowlegement:  
 *       "This product includes software developed by the 
 *        Apache Software Foundation (http://www.apache.org/)."
 *    Alternately, this acknowlegement may appear in the software itself,
 *    if and wherever such third-party acknowlegements normally appear.
 *
 * 4. The names "The Jakarta Project", "Tomcat", and "Apache Software
 *    Foundation" must not be used to endorse or promote products derived
 *    from this software without prior written permission. For written 
 *    permission, please contact apache@apache.org.
 *
 * 5. Products derived from this software may not be called "Apache"
 *    nor may "Apache" appear in their names without prior written
 *    permission of the Apache Group.
 *
 * THIS SOFTWARE IS PROVIDED ``AS IS'' AND ANY EXPRESSED OR IMPLIED
 * WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
 * OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED.  IN NO EVENT SHALL THE APACHE SOFTWARE FOUNDATION OR
 * ITS CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 * LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
 * USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 * ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
 * OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
 * OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
 * SUCH DAMAGE.
 * ====================================================================
 *
 * This software consists of voluntary contributions made by many
 * individuals on behalf of the Apache Software Foundation.  For more
 * information on the Apache Software Foundation, please see
 * <http://www.apache.org/>.
 *
 * [Additional notices, if required by prior licensing conditions]
 *
 */ 


package org.apache.tomcat.modules.server;

import java.io.*;
import java.net.*;
import java.util.*;
import org.apache.tomcat.core.*;
import org.apache.tomcat.helper.*;
import org.apache.tomcat.util.*;
import org.apache.tomcat.util.net.*;
import org.apache.tomcat.util.net.ServerSocketFactory;
import org.apache.tomcat.util.log.*;

/** Standalone http.
 *
 *  Connector properties:
 *  - secure - will load a SSL socket factory and act as https server
 *
 *  Properties passed to the net layer:
 *  - timeout
 *  - backlog
 *  - address
 *  - port
 * Thread pool properties:
 *  - minSpareThreads
 *  - maxSpareThreads
 *  - maxThreads
 *  - poolOn
 * Properties for HTTPS:
 *  - keystore - certificates - default to ~/.keystore
 *  - keypass - password
 *  - clientauth - true if the server should authenticate the client using certs
 */
public class Http10Interceptor extends PoolTcpConnector
    implements  TcpConnectionHandler
{
    public Http10Interceptor() {
	super();
    }

    // -------------------- PoolTcpConnector --------------------

    protected void localInit() throws Exception {
	ep.setConnectionHandler( this );
    }

    // -------------------- Attributes --------------------
    // -------------------- Handler implementation --------------------
    public void setServer( Object o ) {
	this.cm=(ContextManager)o;
    }
    
    public Object[] init() {
	Object thData[]=new Object[3];
	HttpRequest reqA=new HttpRequest();
	HttpResponse resA=new HttpResponse();
	cm.initRequest( reqA, resA );
	thData[0]=reqA;
	thData[1]=resA;
	thData[2]=null;
	return  thData;
    }

    public void processConnection(TcpConnection connection, Object thData[]) {
	Socket socket=null;
	HttpRequest reqA=null;
	HttpResponse resA=null;

	try {
	    reqA=(HttpRequest)thData[0];
	    resA=(HttpResponse)thData[1];

	    socket=connection.getSocket();

	    reqA.setSocket( socket );
	    resA.setSocket( socket );

	    reqA.readNextRequest(resA);
	    if( secure ) {
		reqA.scheme().setString( "https" );
	    }
	    
	    cm.service( reqA, resA );

	    TcpConnection.shutdownInput( socket );
	}
	catch(java.net.SocketException e) {
	    // SocketExceptions are normal
	    log( "SocketException reading request, ignored", null,
		 Logger.INFORMATION);
	    log( "SocketException reading request:", e, Logger.DEBUG);
	}
	catch (java.io.IOException e) {
	    // IOExceptions are normal 
	    log( "IOException reading request, ignored", null,
		 Logger.INFORMATION);
	    log( "IOException reading request:", e, Logger.DEBUG);
	}
	// Future developers: if you discover any other
	// rare-but-nonfatal exceptions, catch them here, and log as
	// above.
	catch (Throwable e) {
	    // any other exception or error is odd. Here we log it
	    // with "ERROR" level, so it will show up even on
	    // less-than-verbose logs.
	    e.printStackTrace();
	    log( "Error reading request, ignored", e, Logger.ERROR);
	} 
	finally {
	    // recycle kernel sockets ASAP
	    try { if (socket != null) socket.close (); }
	    catch (IOException e) { /* ignore */ }
        }
    }
}

class HttpRequest extends Request {
    Http10 http=new Http10();
    private boolean moreRequests = false;
    Socket socket;
    
    public HttpRequest() {
        super();
    }

    public void recycle() {
	super.recycle();
	if( http!=null) http.recycle();
    }

    public void setSocket(Socket socket) throws IOException {
	http.setSocket( socket );
	this.socket=socket;
    }

    public Socket getSocket() {
        return socket;
    }

    public int doRead() throws IOException {
	return http.doRead();
    }

    public int doRead(byte[] b, int off, int len) throws IOException {
	return http.doRead( b, off, len );
    }
    

    public void readNextRequest(Response response) throws IOException {
	int status=http.processRequestLine( methodMB, uriMB,queryMB, protoMB );
	// XXX remove this after we swich to MB
	// 	method=methodMB.toString();
	// 	requestURI=uriMB.toString();
	// 	queryString=queryMB.toString();
	// 	protocol=protoMB.toString();
	
	if( status > 200 ) {
	    response.setStatus( status );
	    return;
	}

	// for 0.9, we don't have headers!
	if (! protoMB.equals("")) {
	    // all HTTP versions with protocol also have headers
	    // ( 0.9 has no HTTP/0.9 !)
	    status=http.readHeaders( headers  );
	    if( status >200 ) {
		response.setStatus( status );
		return;
	    }
	}

	// XXX detect for real whether or not we have more requests
	// coming
	moreRequests = false;
    }

    // -------------------- override special methods


    public String getRemoteAddr() {
        return socket.getInetAddress().getHostAddress();
    }

    public String getRemoteHost() {
	return socket.getInetAddress().getHostName();
    }

    public String getLocalHost() {
	InetAddress localAddress = socket.getLocalAddress();
	localHost = localAddress.getHostName();
	return localHost;
    }

    public MessageBytes serverName(){
        if(! serverNameMB.isNull()) return serverNameMB;
        parseHostHeader();
        return serverNameMB;
    }

    public int getServerPort(){
        if(serverPort!=-1) return serverPort;
        parseHostHeader();
        return serverPort;
    }

    protected void parseHostHeader() {
	MessageBytes hH=getMimeHeaders().getValue("host");
        serverPort = socket.getLocalPort();
	if (hH != null) {
	    // XXX use MessageBytes
	    String hostHeader = hH.toString();
	    int i = hostHeader.indexOf(':');
	    if (i > -1) {
		serverNameMB.setString( hostHeader.substring(0,i));
                hostHeader = hostHeader.substring(i+1);
                try{
                    serverPort=Integer.parseInt(hostHeader);
                }catch(NumberFormatException  nfe){
                }
	    }
            return;
	}
	if( localHost != null ) {
	    serverNameMB.setString( localHost );
	}
	// default to localhost - and warn
	//	log("No server name, defaulting to localhost");
        serverNameMB.setString( getLocalHost() );
    }
}


class HttpResponse extends  Response {
    Http10 http;
    
    public HttpResponse() {
        super();
    }

    public void setSocket( Socket s ) {
	http=((HttpRequest)request).http;
    }

    public void recycle() {
	super.recycle();
    }

    public void endHeaders()  throws IOException {
	super.endHeaders();
	http.sendStatus( status, RequestUtil.getMessage( status ));
	http.sendHeaders( getMimeHeaders() );
    }

    public void doWrite( byte buffer[], int pos, int count)
	throws IOException
    {
	http.doWrite( buffer, pos, count);
    }
}