protected void sendStatus( int status, String message)  throws IOException {

/*
 *
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


/*
  Based on Ajp11ConnectionHandler and Ajp12 implementation of JServ
*/

package org.apache.tomcat.service.connector;

import java.io.*;
import java.net.*;
import java.util.*;
import org.apache.tomcat.core.*;
import org.apache.tomcat.util.*;
import org.apache.tomcat.server.*;
import org.apache.tomcat.service.http.*;
import org.apache.tomcat.service.http.HttpResponseAdapter;
import org.apache.tomcat.service.http.HttpRequestAdapter;
import org.apache.tomcat.service.*;
import javax.servlet.*;
import javax.servlet.http.*;

/* Deprecated - must be rewriten to the connector model.  
 */
public class Ajp12ConnectionHandler implements  TcpConnectionHandler {
    StringManager sm = StringManager.getManager("org.apache.tomcat.service");
    
    ContextManager contextM;
    
    public Ajp12ConnectionHandler() {
    }

    public Object[] init() {
	return null;
    }

    public void setAttribute(String name, Object value ) {
	if("context.manager".equals(name) ) {
	    contextM=(ContextManager)value;
	}
    }
    
    public void setContextManager( ContextManager contextM ) {
	this.contextM=contextM;
    }

    public void processConnection(TcpConnection connection, Object[] theData) {
	
        try {
	    Socket socket=connection.getSocket();
	    socket.setSoLinger( true, 100);
	    //	    socket.setSoTimeout( 1000); // or what ? 

	    //	    RequestImpl request = new RequestImpl();
	    AJP12RequestAdapter reqA = new AJP12RequestAdapter(contextM, socket);
	    //	    ResponseImpl response=new ResponseImpl();
	    AJP12ResponseAdapter resA=new AJP12ResponseAdapter();

	    InputStream in=socket.getInputStream();
	    OutputStream out=socket.getOutputStream();
	    
	    //	    request.setRequestAdapter(reqA);
	    //	    response.setResponseAdapter( resA );
	    resA.setOutputStream(socket.getOutputStream());

	    reqA.setResponse(resA);
	    resA.setRequest(reqA);

	    reqA.readNextRequest();
	    if( reqA.shutdown )
		return;
	    if (resA.getStatus() >= 400) {
		resA.finish();
		
		socket.close();
		return;
	    } 

	    // resolve the server that we are for

	    int contentLength = reqA.getIntHeader("content-length");
	    if (contentLength != -1) {
		BufferedServletInputStream sis =
		    (BufferedServletInputStream)reqA.getInputStream();
		sis.setLimit(contentLength);
	    }

	    contextM.service( reqA, resA );

	    resA.finish();
	    socket.close();
	} catch (Exception e) {
            // XXX
	    // this isn't what we want, we want to log the problem somehow
	    System.out.println("HANDLER THREAD PROBLEM: " + e);
	    e.printStackTrace();
	}
    }
}

class AJP12RequestAdapter extends RequestImpl {
    StringManager sm = StringManager.getManager("org.apache.tomcat.service");
    Socket socket;
    InputStream sin;
    Ajpv12InputStream ajpin;
    ContextManager contextM;
    boolean shutdown=false;
    
    public int doRead() throws IOException {
	return ajpin.read();
    }

    public  int doRead( byte b[], int off, int len ) throws IOException {
	return ajpin.read(b,off,len);
    }

    public AJP12RequestAdapter(ContextManager cm, Socket s) throws IOException {
	this.socket = s;
	this.contextM=cm;
	sin = s.getInputStream();
	in = new BufferedServletInputStream( this );
	ajpin = new Ajpv12InputStream(sin);
    }
    
    protected void readNextRequest() throws IOException {
	String dummy,token1,token2;
	int marker;
	int signal;

	try {
            while (true) {
	    marker = ajpin.read();
	    switch (marker) {
	    case 0:       //NOP marker useful for testing if stream is OK
		break;

	    case 1: //beginning of request
		method = ajpin.readString(null);              //Method
		dummy = ajpin.readString(null);               //Zone
		dummy = ajpin.readString(null);         //Servlet
		serverName = ajpin.readString(null);            //Server hostname
		dummy = ajpin.readString(null);               //Apache document root
		dummy = ajpin.readString(null);               //Apache parsed path-info
		dummy = ajpin.readString(null);               //Apache parsed path-translated
		queryString = ajpin.readString(null);         //query string
		remoteAddr = ajpin.readString("");            //remote address
		remoteHost = ajpin.readString("");            //remote host
		dummy = ajpin.readString(null);                 //remote user
		dummy = ajpin.readString(null);                 //auth type
		dummy = ajpin.readString(null);                 //remote port
		dummy = ajpin.readString(null);                //request method
		requestURI = ajpin.readString("");             //request uri
		dummy = ajpin.readString(null);                   //script filename
		dummy = ajpin.readString(null);                   //script name
		serverName = ajpin.readString("");                //server name
		try {
		    serverPort = Integer.parseInt(ajpin.readString("80")); //server port
		} catch (Exception any) {
		    serverPort = 80;
		}
		dummy = ajpin.readString("");                     //server protocol 
		dummy = ajpin.readString("");                     //server signature
		dummy = ajpin.readString("");                     //server software
		dummy = ajpin.readString("");                     //JSERV ROUTE
                /**
                 * The two following lines are commented out because we don't 
                 * want to depend on unreleased versions of the jserv module. 
                 *                                            - costin
                 */
                //		dummy = ajpin.readString("");                     //SSL_CLIENT_DN
                //		dummy = ajpin.readString("");                     //SSL_CLIENT_IDN
		// XXX all dummy fields will be used after core is changed to make use
		// of them!
		
		break;

	    case 3: // Header
		token1 = ajpin.readString(null);
		token2 = ajpin.readString("");
		headers.putHeader(token1.toLowerCase(), token2);
		break;

	    case 254: // Signal
		signal = ajpin.read();

		if (signal == 0) { // PING implemented as signal
		    try {
			// close the socket connection after we send reply
			socket.getOutputStream().write(0); // PING reply
			sin.close();
		    } catch (IOException ignored) {
			System.err.println(ignored);
		    }
		} else {
		    try {
			// close the socket connection before handling any signal
			sin.close();
			if ( signal== 15 ) {
			    // Shutdown - probably apache was stoped with apachectl stop
			    contextM.stop();
			    shutdown=true;
			    return;
			}
		    } catch (Exception ignored) {
			System.err.println(ignored);
		    }
		    System.err.println("Signal ignored: " + signal);
		}
		return;

	    case 4:
	    case 255:
		return;

	    case -1:
		throw new java.io.IOException("Stream closed prematurely");
            

	    default:
		throw new java.io.IOException("Stream broken");
            

	    } // while
            } // switch
	} catch (IOException ioe) {
	    throw ioe;
        } catch (Exception e) {
	    System.err.println("Uncaught exception" + e);
        }
	
	// REQUEST_URI includes query string 
	int idQ= requestURI.indexOf("?");
	if ( idQ > -1) {
	    requestURI = requestURI.substring(0, idQ);
        }


	// 	System.out.println("Request: " + requestURI );
	// 	System.out.println("Query: " + queryString );
	// 	System.out.println("ENV: " + env_vars );
	// 	System.out.println("HEADERS: " + headers_in );
	// 	System.out.println("PARAMETERS: " + parameters );


	//processCookies();
	
	contentLength = headers.getIntHeader("content-length");
	contentType = headers.getHeader("content-type");
	    
	// XXX
	// detect for real whether or not we have more requests
	// coming
	
	// XXX
	// Support persistent connection in AJP21
	//moreRequests = false;	
    }    

}


// Ajp use Status: instead of Status 
class AJP12ResponseAdapter extends HttpResponseAdapter {
    /** Override setStatus
     */
    public void setStatus( int status, String message) throws IOException {
	statusSB.setLength(0);
	statusSB.append("Status: " ).append( status ).append("\r\n");
	sout.write(statusSB.toString().getBytes());
    }
}

class Ajpv12InputStream extends BufferedInputStream {

    // UTF8 is a strict superset of ASCII.
    final static String CHARSET = "UTF8";
    
    public Ajpv12InputStream(InputStream in) {
        super(in);
    }

    public Ajpv12InputStream(InputStream in, int bufsize) {
        super(in,bufsize);
    }


    public int readWord() throws java.io.IOException {
        int b1 = read();
        if( b1 == -1)
            return -1;

        int b2 = read();
        if ( b2==-1) 
            return -1;

        return ((int)((b1 << 8) | b2)) & 0xffff;
    }

    public String readString(String def) throws java.io.IOException {
        int len = readWord();

        if( len == 0xffff) 
            return def;

        if( len == -1) 
            throw new java.io.IOException("Stream broken");

        byte[] b = new byte[len];
        int p = 0;
        int r;
        while(p<len) {
            r = read(b,p, len - p);
            if( r< 0) {
                throw new java.io.IOException("Stream broken, couldn't demarshal string :"+len+":"+p);
            }
            p = p+r;
        }
        return new String(b, CHARSET);
    }
}

