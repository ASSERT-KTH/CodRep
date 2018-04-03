statusSB.append("Status: " ).append( status ).append(" ").append(message).append("\r\n");

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
	    // XXX - Add workarounds for the fact that the underlying
	    // serverSocket.accept() call can now time out.  This whole
	    // architecture needs some serious review.
	    if (connection == null)
		return;
	    Socket socket=connection.getSocket();
	    if (socket == null)
		return;
	    socket.setSoLinger( true, 100);
	    //	    socket.setSoTimeout( 1000); // or what ?

	    //	    RequestImpl request = new RequestImpl();
	    AJP12RequestAdapter reqA = new AJP12RequestAdapter(contextM, socket);
	    reqA.setContextManager( contextM );
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

	    // XXX is this needed ??
	    int contentLength = reqA.getFacade().getIntHeader("content-length");
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
    boolean doLog;

    public int doRead() throws IOException {
	return ajpin.read();
    }

    public  int doRead( byte b[], int off, int len ) throws IOException {
	return ajpin.read(b,off,len);
    }

    void log( String s ) {
	contextM.log( s );
    }
    
    public AJP12RequestAdapter(ContextManager cm, Socket s) throws IOException {
	this.socket = s;
	this.contextM=cm;
	sin = s.getInputStream();
	in = new BufferedServletInputStream( this );
	ajpin = new Ajpv12InputStream(sin);
	doLog=contextM.getDebug() > 10;
    }

    protected void readNextRequest() throws IOException {
	String dummy,token1,token2;
	int marker;
	int signal;
//      Hashtable env_vars=new Hashtable();


	try {
	    boolean more=true;
            while (more) {
		marker = ajpin.read();
		switch (marker) {
		case 0:       //NOP marker useful for testing if stream is OK
		    break;
		    
		case 1: //beginning of request
		    method = ajpin.readString(null);              //Method
		    
		    contextPath = ajpin.readString(null);               //Zone
		    // GS, the following commented line causes the Apache + Jserv + Tomcat
		    // combination to hang with a 404!!!
		    // if("ROOT".equals( contextPath ) ) contextPath="";
		    if("ROOT".equalsIgnoreCase( contextPath ) ) contextPath=null;
		    if( doLog ) log("AJP: CP=" + contextPath);
		    
		    if( contextPath!= null )
			context=contextM.getContext( contextPath );
		    if( doLog ) log("AJP: context=" + context );
		    
		    servletName = ajpin.readString(null);         //Servlet
		    if( doLog ) log("AJP: servlet=" + servletName );
		    
		    serverName = ajpin.readString(null);            //Server hostname
		    if( doLog ) log("AJP: serverName=" + serverName );
		    
		    dummy = ajpin.readString(null);               //Apache document root
		    
		    pathInfo = ajpin.readString(null);               //Apache parsed path-info
		    if( doLog ) log("AJP: PI=" + pathInfo );
		    
		    // XXX Bug in mod_jserv !!!!!
		    pathTranslated = ajpin.readString(null);               //Apache parsed path-translated
		    if( doLog ) log("AJP: PT=" + pathTranslated );
		    
		    queryString = ajpin.readString(null);         //query string
		    if( doLog ) log("AJP: QS=" + queryString );
		    
		    remoteAddr = ajpin.readString("");            //remote address
		    if( doLog ) log("AJP: RA=" + remoteAddr );
		    
		    remoteHost = ajpin.readString("");            //remote host
		    if( doLog ) log("AJP: RH=" + remoteHost );
		    
		    remoteUser = ajpin.readString(null);                 //remote user
		    if( doLog ) log("AJP: RU=" + remoteUser);
		    
		    authType = ajpin.readString(null);                 //auth type
		    if( doLog ) log("AJP: AT=" + authType);
		    
		    dummy = ajpin.readString(null);                 //remote port
		    
		    method = ajpin.readString(null);                //request method
		    if( doLog ) log("AJP: Meth=" + method );
		    
		    requestURI = ajpin.readString("");             //request uri
		    if( doLog ) log("AJP: URI: " + requestURI + " CP:" + contextPath + " LP: " + lookupPath);

		    // XXX don't set lookup path - problems with URL rewriting.
		    // need to be fixed.
		    //		if(contextPath!=null && contextPath.length() >0 )
		    //		    lookupPath=requestURI.substring( contextPath.length() + 1 );
		    if( doLog ) log("AJP: URI: " + requestURI + " CP:" + contextPath + " LP: " + lookupPath);
		    
		    dummy = ajpin.readString(null);                   //script filename
		    //		System.out.println("AJP: Script filen=" + dummy);
		    
		    dummy = ajpin.readString(null);                   //script name
		    //		System.out.println("AJP: Script name=" + dummy);
		    
		    serverName = ajpin.readString("");                //server name
		    if( doLog ) log("AJP: serverName=" + serverName );
		    try {
			serverPort = Integer.parseInt(ajpin.readString("80")); //server port
		    } catch (Exception any) {
			serverPort = 80;
		    }
		    
		    dummy = ajpin.readString("");                     //server protocol
		    //		System.out.println("AJP: Server proto=" + dummy);
		    dummy = ajpin.readString("");                     //server signature
		    //		System.out.println("AJP: Server sign=" + dummy);
		    dummy = ajpin.readString("");                     //server software
		    //		System.out.println("AJP: Server softw=" + dummy);
		    jvmRoute = ajpin.readString("");                     //JSERV ROUTE
		    if(jvmRoute.length() == 0) {
			jvmRoute = null;
		    }
		    if( doLog ) log("AJP: Server jvmRoute=" + jvmRoute);
		    
		    
                    /**
                     * The two following lines are commented out because we don't
                     * want to depend on unreleased versions of the jserv module.
                     *                                            - costin
                     * The two following lines are uncommented because JServ 1.1 final
                     * is far behind.
                     * NB: you need a recent mod_jserv to use the latest protocol version.
                     * Theses env vars are simply ignored. (just here for compatibility)
                     *                                            - jluc
                     */
                     dummy = ajpin.readString(""); 
                     dummy = ajpin.readString("");
		    // XXX all dummy fields will be used after core is changed to make use
		    // of them!
		    
		    break;
		    
                    
                    /**
                     * Marker = 5 will be used by mod_jserv to send environment vars
                     * as key+value (dynamically configurable).
                     * can be considered as "reserved", and safely ignored by other connectors.
                     * env_vars is (above in this  code) commented out for performance issues.
                     * so theses env vars are simply ignored. (just here for compatibility)
                     * but it is where mod_jserv would place SSL_* env vars (by exemple)
                     * See the new parameter for mod_jserv (version > 1.1):
                     * ApJServEnvVar localname remotename
                     *                                            - jluc
                     */
                case 5: // Environment vars
                    token1 = ajpin.readString(null);
                    token2 = ajpin.readString("");
//                  env_vars.put(token1, token2);
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
				// same behavior as in past, because it seems that
				// stopping everything doesn't work - need to figure
				// out what happens with the threads ( XXX )
				System.exit(0);

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
		    more=false;
		    break;
		    
		case -1:
		    throw new java.io.IOException("Stream closed prematurely");
		    
		    
		default:
		    throw new java.io.IOException("Stream broken");
		    
		    
		} // switch
            } // while
	} catch (IOException ioe) {
	    throw ioe;
        } catch (Exception e) {
	    System.err.println("Uncaught exception" + e);
	    e.printStackTrace();
        }
	
	// REQUEST_URI includes query string
	int indexQ=requestURI.indexOf("?");
	int rLen=requestURI.length();
	if ( (indexQ >-1) && ( indexQ  < rLen) ) {
	    if(doLog) log("Orig QS " + queryString );
	    queryString = requestURI.substring(indexQ + 1, requestURI.length());
	    if(doLog) log("New QS " + queryString );
	    requestURI = requestURI.substring(0, indexQ);
	} 
	
	if( doLog ) log("Request: " + requestURI );
	if( doLog ) log ("Query: " + queryString );
	// System.out.println("ENV: " + env_vars );
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
    protected void sendStatus( int status, String message)  throws IOException {
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

