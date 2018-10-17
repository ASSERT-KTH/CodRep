import org.apache.tomcat.util.buf.Base64;

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
package org.apache.tomcat.util.test;

import java.net.*;
import java.io.*;
import java.util.*;
import java.net.*;

import org.apache.tomcat.util.Base64;

/**
 *  Part of GTest - defines a Http request. This tool gives a lot 
 *  of control over the request, and is usable with ant ( testing
 *  is also a part of the build process :-) or other xml-tools
 *  using similar patterns.
 *
 *  
 */
public class HttpRequest {
    // Defaults
    static String defaultHost="localhost";
    static int defaultPort=8080;
    static int defaultDebug=0;
    static String defaultProtocol="HTTP/1.0";
    
    String id;

    String host=null;
    int port=-1;

    String method="GET";
    String protocol=null;
    String path;
    
    String requestLine;

    Vector headerVector=new Vector();
    Vector paramsV=new Vector();
    String user;
    String password;
    Body body;

    // Request body as it'll be sent
    String fullRequest;
    
    int debug=defaultDebug;
    HttpClient client=null;
    HttpResponse response=null;
    

    public HttpRequest() {
    }

    /** Associated response, set after executing the request
     */
    public void setHttpResponse(HttpResponse r) {
	response=r;
    }

    public HttpResponse getHttpResponse() {
	return response;
    }


    public void setHttpClient( HttpClient c ) {
	client=c;
    }

    public HttpClient getHttpClient() {
	return client;
    }

    /** Set an unique id to this request. This allows it to be
     *  referenced later, for complex tests/matchers that look
     * 	at multiple requests.
     */
    public void setId(String id) {
	this.id=id;
    }

    /** Server that will receive the request
     */
    public void setHost(String h) {
	this.host=h;
    }

    public String getHost() {
	if( host==null ) host=defaultHost;
	return host;
    }
    
    /** 
     */
    public void setMethod(String h) {
	this.method=h;
    }

    /** The port used to send the request
     */
    public void setPort(String portS) {
	this.port=Integer.valueOf( portS).intValue();
    }

    /** Set the port as int - different name to avoid confusing introspection
     */
    public void setPortInt(int i) {
	this.port=i;
    }

    public int getPort() {
	if( port==-1) port=defaultPort;
	return port;
    }

    public void setUser( String u ) {
	this.user=u;
    }

    public void setPassword( String p ) {
	password=p;
    }
    
    /** Do a POST with the specified content.
     */
    public void setContent(String s) {
	body=new Body( s );
    }

    /** Add content to the request, for POST ( alternate method )
     */
    public void addBody( Body b ) {
	body=b;
    }

    public void setProtocol( String s ) {
	protocol=s;
    }
    
    public void setPath( String s ) {
	path=s;
    }

    public void addHeader( String n, String v ) {
	headerVector.addElement( new Header( n, v) );
    }

    /** Add a header to the request
     */
    public void addHeader( Header rh ) {
	headerVector.addElement( rh );
    }

    /** Add headers - string representation, will be parsed
     *  The value is a "|" separated list of headers to expect.
     *  It's preferable to use the other 2 methods.
     */
    public void setHeaders( String s ) {
       Header.parseHeadersAsString( s, headerVector );
    }


    /** Add a parameter to the request
     */
    public void addParam( Parameter rp ) {
	paramsV.addElement( rp );
    }

    /** Display debug info
     */
    public void setDebug( int d ) {
	debug=d;
    }

    /** Verbose request line - including method and protocol
     */
    public void setRequestLine( String s ) {
	this.requestLine=s;
    }
    
    public String getRequestLine( ) {
	if( requestLine==null ) {
	    prepareRequest(); 
	    int idx=fullRequest.indexOf("\r");
	    if( idx<0 )
		requestLine=fullRequest;
	    else
		requestLine=fullRequest.substring(0, idx );
	}
	return requestLine;
    }
    
    /** Allow sending a verbose request
     */
    public void setFullRequest( String s ) {
	fullRequest=s;
    }

    public String getFullRequest() {
	return fullRequest;
    }

    /** Add content to the request, for POST ( alternate method )
     */
    public void addVerbose( Body b ) {
	fullRequest=b.getBody();
    }

    /** Alternate method for sending a verbose request
     */
    public void addText(String s ) {
	fullRequest=s;
    }

    // -------------------- Execute the request --------------------

    public void execute() {
	prepareRequest();
    }

    boolean prepared=false;
    static String CRLF="\r\n";
    /** 
     */
    public void prepareRequest() 
    {
	if( prepared ) return;
	if( host==null ) host=defaultHost;
	if( port==-1) port=defaultPort;
	if( protocol==null ) protocol=defaultProtocol;
	
	prepared=true;
	
	if( id==null ) {
	    id="Req" + getId();
	}
	registerHttpRequest( id, this );

	// explicitely set - the rest doesn't matter
	if( fullRequest != null ) return;

	// use the existing info to compose what will be sent to the
	// server
	StringBuffer sb=new StringBuffer();
	if( requestLine != null ) 
	    sb.append(requestLine); // explicitely set 
	else {
	    sb.append( method ).append(" ").append(path);
	    // all GET parameters
	    boolean first=true;
	    for( int i=0; i< paramsV.size(); i++ ) {
		Parameter p=(Parameter)paramsV.elementAt(i);
		if( "GET".equals( p.getType( method ) )) {
		    if( first && (path.indexOf("?") <0) ) {
			sb.append("?");
			first=false;
		    } else {
			sb.append( "&" );
		    }
		    // not null? Encode ?
		    sb.append(p.getName());
		    sb.append("=");
		    String v=p.getValue();
		    if( v!=null) sb.append(v);
		}
	    }
	    sb.append(" ").append(protocol);
	    requestLine=sb.toString();
	}

	sb.append(CRLF);

	// We may test HTTP0.9 behavior. If it's post 1.0, it needs
	// a LF
	if( requestLine.indexOf( "HTTP/1." ) <0 ) {
	    fullRequest=sb.toString();
	    return; // nothing to add
	}

	String contentL=null;
	String hostHeader=null;
	String contentType=null;
	String authorization=null;

	Enumeration headersE=headerVector.elements();
	while( headersE.hasMoreElements() ) {
	    Header h=(Header)headersE.nextElement();
	    sb.append(h.getName()).append(": ");
	    sb.append(h.getValue()).append( CRLF );
	    if( "Content-Type".equals( h.getName() )) 
		contentType=h.getValue();
	    if( "Content-Length".equals( h.getName() )) 
		contentL=h.getValue();
	    if( "Host".equals( h.getName() )) 
		hostHeader=h.getValue();
	    if( "Authorization".equals( h.getName() )) 
		authorization=h.getValue();
	}
	if( hostHeader == null && host!=null && ! "".equals(host)  ) {
	    sb.append("Host: ").append( host ).append( CRLF );
	}

	// If we are in a POST and Parameters are specified -
	// add the header and prepare the body
	if( body==null && "POST".equals( method ) ) {
	    // we may have POST parameters.
	    StringBuffer bodySB=new StringBuffer();
	    
	    boolean first=true;
	    for( int i=0; i< paramsV.size(); i++ ) {
		Parameter p=(Parameter)paramsV.elementAt(i);
		if( "POST".equals( p.getType( "POST") )) {
		    if( ! first ) {
			bodySB.append( "&" );
		    }
		    first=false;
		    // not null? Encode ?
		    bodySB.append(p.getName());
		    bodySB.append("=");
		    String v=p.getValue();
		    if( v!=null) bodySB.append(v);
		}
	    }
	    if( ! first ) {
		// we had a post param and we constructed the body
		if( contentType==null ) {
		    sb.append( "Content-Type: ");
		    sb.append( "application/x-www-form-urlencoded");
		    sb.append(CRLF);
		}
		body= new Body( bodySB.toString());
	    }
	}

	// Deal with authorization
	if( authorization == null &&
	    user!=null && password !=null ) {
	    sb.append( "Authorization: Basic " );
	    String token=user + ":" + password;
	    sb.append( Base64.encode( token.getBytes() ));
	    sb.append( CRLF );
	}
	
	// If we have a body
	if( body != null) {
	    // If set explicitely ( maybe we're testing bad POSTs )
	    if( contentL==null ) {
		sb.append("Content-Length: ").append( body.getBody().length());
		sb.append(CRLF).append( CRLF);
	    }
	    
	    sb.append(body.getBody());
	    // no /n at the end -see HTTP specs!
	    // If we want to test bad POST - set Content-Length
	    // explicitely.
	} else {
	    sb.append( CRLF );
	}

	// set the fullRequest
	fullRequest=sb.toString();
    }

    /** Return a URI (guessed) from the requestLine/fullRequest
     */
    public String getURI() {
	String toExtract=getRequestLine();
	if( fullRequest==null ) toExtract=requestLine;
	if( toExtract==null ) return null;

	//	if( ! toExtract.startsWith("GET")) return null;
	try {
	    StringTokenizer st=new StringTokenizer( toExtract," " );
	    st.nextToken(); // GET
	    return st.nextToken();
	} catch( Exception ex ) {
	    return "";
	}
    }

    // -------------------- Repository for requet definitions ----------
    static int idCounter=0;
    static Hashtable allRequests=new Hashtable();

    public static synchronized int getId() {
	return idCounter++;
    }
    
    /** Return one of the "named" clients that have been executed so far.
     */
    public static Hashtable getAllRequests() {
	return allRequests;
    }

    public static void registerHttpRequest( String id, HttpRequest req ) {
	allRequests.put( id, req );
    }

    public static HttpRequest getHttpRequest( String id ) {
	return (HttpRequest)allRequests.get(id);
    }

    public static Enumeration getHttpRequests() {
	return allRequests.keys();
    }

}