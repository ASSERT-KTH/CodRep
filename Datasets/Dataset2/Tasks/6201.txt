return getScheme().equalsIgnoreCase("HTTPS");

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


package org.apache.tomcat.core;

import org.apache.tomcat.facade.*;
import org.apache.tomcat.util.*;
import java.io.IOException;
import java.io.*;
import java.net.*;
import java.security.*;
import java.util.*;
import javax.servlet.*;
import javax.servlet.http.*;


/**
 *
 * @author James Duncan Davidson [duncan@eng.sun.com]
 * @author James Todd [gonzo@eng.sun.com]
 * @author Jason Hunter [jch@eng.sun.com]
 * @author Harish Prabandham
 * @author Alex Cruikshank [alex@epitonic.com]
 */
public class RequestImpl  implements Request {

    // GS, used by the load balancing layer in the Web Servers
    // jvmRoute == the name of the JVM inside the plugin.
    protected String jvmRoute;

    // XXX used by forward to override, need a better
    // mechanism
    protected String requestURI;
    protected String queryString;

   //  RequestAdapterImpl Hints
    protected String serverName=null;
    protected Vector cookies = new Vector();

    protected String contextPath;
    protected String lookupPath; // everything after contextPath before ?
    protected String servletPath;
    protected String pathInfo;
    protected String pathTranslated;
    // Need to distinguish between null pathTranslated and
    // lazy-computed pathTranlsated
    protected boolean pathTranslatedIsSet=false;
    
    protected Hashtable parameters = new Hashtable();
    protected int contentLength = -1;
    protected String contentType = null;
    protected String charEncoding = null;
    protected String authType;
    protected String remoteUser;

    protected Principal principal;
    // active roles for the current user
    protected String userRoles[];
    
    // Request
    protected Response response;
    protected HttpServletRequest requestFacade;
    protected Context context;
    protected ContextManager contextM;
    protected Hashtable attributes = new Hashtable();

    protected boolean didReadFormData;
    protected boolean didParameters;
    protected boolean didCookies;
    // end "Request" variables

    // Session
    // set by interceptors - the session id
    protected String reqSessionId;
    protected String sessionIdSource;
    // cache- avoid calling SessionManager for each getSession()
    protected HttpSession serverSession;


    // LookupResult - used by sub-requests and
    // set by interceptors
    protected String servletName;
    protected ServletWrapper handler = null;
    Container container;

    protected String mappedPath = null;

    protected String scheme;
    protected String method;
    protected String protocol;
    protected MimeHeaders headers;
    protected ServletInputStream in;

    protected int serverPort;
    protected String remoteAddr;
    protected String remoteHost;
    protected String localHost;
    protected ByteBuffer bBuffer;

    protected static StringManager sm =
        StringManager.getManager("org.apache.tomcat.core");

    public RequestImpl() {
	//	System.out.println("XXX new ri " );
 	headers = new MimeHeaders();
 	recycle(); // XXX need better placement-super()
    }

    public void setContext(Context context) {
	this.context = context;
    }

    public void setContextManager( ContextManager cm ) {
	contextM=cm;
    }

    public ContextManager getContextManager() {
	return contextM;
    }

    public String getScheme() {
        return scheme;
    }

    public String getMethod() {
        return method;
    }

    public String getRequestURI() {
        if( requestURI!=null) return requestURI;
	return requestURI;
    }

    // XXX used by forward
    public String getQueryString() {
	if( queryString != null ) return queryString;
        return queryString;
    }

    public String getProtocol() {
        return protocol;
    }

    /** Return the server name. If none was set,
     *  extract it from the host header.
     *  
     */
    public String getServerName() {
	if(serverName!=null) return serverName;

	String hostHeader = this.getHeader("host");
	if (hostHeader != null) {
	    int i = hostHeader.indexOf(':');
	    if (i > -1) {
		hostHeader = hostHeader.substring(0,i);
	    }
	    serverName=hostHeader;
	    return serverName;
	}

	if( localHost != null ) {
	    serverName = localHost;
	    return serverName;
	}
	// default to localhost - and warn
	//	System.out.println("No server name, defaulting to localhost");
	serverName="localhost";
	return serverName;
    }

    /** Virtual host */
    public void setServerName(String serverName) {
	this.serverName = serverName;
    }

    public String getLookupPath() {
	return lookupPath;
    }

    public void setLookupPath( String l ) {
	lookupPath=l;
    }

    public String[] getParameterValues(String name) {
	handleParameters();
        return (String[])parameters.get(name);
    }

    public Enumeration getParameterNames() {
	handleParameters();
        return parameters.keys();
    }

    public String getAuthType() {
    	return authType;
    }

    public String getCharacterEncoding() {
        if(charEncoding!=null) return charEncoding;
        charEncoding = RequestUtil.getCharsetFromContentType( getContentType());
	return charEncoding;
    }

    public int getContentLength() {
        if( contentLength > -1 ) return contentLength;

	String value=getHeader( "content-length" );
	if( value==null) return -1;

	contentLength = Integer.parseInt(value);
	return contentLength;
    }

    public String getContentType() {
	if(contentType != null) return contentType;
	contentType = getHeader("content-type");
	if(contentType != null) return contentType;
	// can be null!! -
	return contentType;
    }

    /** All adapters that know the PT needs to call this method,
	in order to set pathTranslatedIsSet, otherwise tomcat
	will try to compute it again
    */
    public void setPathTranslated(String s ) {
	pathTranslated=s;
	pathTranslatedIsSet=true;
    }

    public String getPathTranslated() {
	if( pathTranslatedIsSet ) return pathTranslated;

	// not set yet - we'll compute it
	pathTranslatedIsSet=true;
	String path=getPathInfo();
	// In CGI spec, PATH_TRANSLATED shouldn't be set if no path info is present
	pathTranslated=null;
	if(path==null || "".equals( path ) ) return null;
	pathTranslated=context.getRealPath( path );
	return pathTranslated;
    }


    // XXX XXX Servlet API conflicts with the CGI specs -
    // PathInfo should be "" if no path info is requested ( as it is in CGI ).
    // We are following the spec, but IMHO it's a bug ( in the spec )
    public String getPathInfo() {
        return pathInfo;
    }
    
    public void setRemoteUser(String s) {
	remoteUser=s;
    }

    public String getRemoteUser() {
	return remoteUser;
    }

    public boolean isSecure() {
	// The adapter is responsible for providing this information 
        return getProtocol().equalsIgnoreCase("HTTPS");
    }
    
    public void setUserPrincipal( Principal p ) {
	principal=p;
    }
    
    /** Return the principal - the adapter will set it
     */
    public Principal getUserPrincipal() {
	if( getRemoteUser() == null ) return null;
	if( principal == null ) {
	    principal=new SimplePrincipal( getRemoteUser() );
	}
	return principal; 
    }

    public void setUserRoles( String roles[] ) {
	userRoles=roles;
    }

    public String[] getUserRoles( ) {
	return userRoles;
    }

    public boolean isUserInRole(String role) {
	if (userRoles != null) {
	    if( SecurityTools.haveRole( role, userRoles ))
		return true;
	}
	return false;
    }

    public String getServletPath() {
        return servletPath;
    }

    // End hints

    // -------------------- Request methods ( high level )
    public HttpServletRequest getFacade() {
	// some requests are internal, and will never need a
	// facade - no need to create a new object unless needed.
        if( requestFacade==null ) {
	    if( context==null ) {
		// wrong request
		// XXX the will go away after we remove the one-one relation between
		// request and facades ( security, etc)
		requestFacade = contextM.getContext("" ).getFacadeManager().createHttpServletRequestFacade(this );
		return requestFacade;
	    }
	    requestFacade = context.getFacadeManager().createHttpServletRequestFacade(this);
	}
	return requestFacade;
    }

    public Context getContext() {
	return context;
    }

    public void setResponse(Response response) {
	this.response = response;
    }

    public Response getResponse() {
	return response;
    }

    // -------------------- Session --------------------
    // GS - return the jvm load balance route
    public String getJvmRoute() {
	    return jvmRoute;
    }

    public void setJvmRoute(String jvmRoute) {
	    this.jvmRoute=jvmRoute;
    }

    public String getRequestedSessionId() {
        return reqSessionId;
    }

    public void setRequestedSessionId(String reqSessionId) {
	this.reqSessionId = reqSessionId;
    }

    public String getSessionIdSource() {
	return sessionIdSource;
    }

    public void setSessionIdSource(String s) {
	sessionIdSource=s;
    }

    public void setSession(HttpSession serverSession) {
	//	context.log("RequestImpl: set session ! ");
	this.serverSession = serverSession;
    }

    public HttpSession getSession(boolean create) {
	if( serverSession!=null ) {
	    // if not null, it is validated by the session module
	    return serverSession;
	}
	
	if( ! create ) return null;
	
	//	context.log("RequestImpl:  created new session!");
	contextM.doNewSessionRequest( this, response );
	if ( serverSession == null ) {
	    context.log("RequestImpl: no session created!");
	    return null;
	}
	
	reqSessionId = serverSession.getId();
	response.setSessionId( reqSessionId );

	return serverSession;
    }

    // --------------------
    public int getCookieCount() {
	if( ! didCookies ) {
	    didCookies=true;
	    RequestUtil.processCookies( this, cookies );
	}
	return cookies.size();
    }

    public Cookie getCookie( int idx ) {
	if( ! didCookies ) {
	    didCookies=true;
	    RequestUtil.processCookies( this, cookies );
	}
	return (Cookie)cookies.elementAt(idx);
    }
    
    public Cookie[] getCookies() {
	int count=getCookieCount();
	Cookie[] cookieArray = new Cookie[ count ];

	for (int i = 0; i < count; i ++) {
	    cookieArray[i] = getCookie( i );
	}

	return cookieArray;
    }
    // -------------------- LookupResult
    public ServletWrapper getWrapper() {
	return handler;
    }

    public void setWrapper(ServletWrapper handler) {
	this.handler=handler;
    }

    public Container getContainer() {
	return container;
    }

    public void setContainer(Container container) {
	this.container=container;
    }

    /** The file - result of mapping the request ( using aliases and other
     *  mapping rules. Usefull only for static resources.
     */
    public String getMappedPath() {
	return mappedPath;
    }

    public void setMappedPath( String m ) {
	mappedPath=m;
    }

    public void setRequestURI( String r ) {
 	this.requestURI=r;
    }

    public void setParameters( Hashtable h ) {
	if(h!=null)
	    this.parameters=h;
	// XXX Should we override query parameters ??
    }

    public Hashtable getParameters() {
	return parameters;
    }

    public void setContentLength( int  len ) {
	this.contentLength=len;
    }

    public void setContentType( String type ) {
	this.contentType=type;
    }

    public void setCharEncoding( String enc ) {
	this.charEncoding=enc;
    }

    public void setAuthType(String authType) {
        this.authType = authType;
    }


    public void setPathInfo(String pathInfo) {
        this.pathInfo = pathInfo;
    }

    /** Set query string - will be called by forward
     */
    public void setQueryString(String queryString) {
	// the query will be processed when getParameter() will be called.
	// Or - if you alredy have it parsed, call setParameters()
	this.queryString = queryString;
    }

    public void setServletPath(String servletPath) {
	this.servletPath = servletPath;
    }


    // XXX
    // the server name should be pulled from a server object of some
    // sort, not just set and got.

    // -------------------- Attributes
    public Object getAttribute(String name) {
        Object value=attributes.get(name);
	if( value != null )
	    return value;

	// allow access to FacadeManager for servlets 
	// ( this way you don't need to deal with init ).
	if( name.equals(FacadeManager.FACADE_ATTRIBUTE)) {
	    return context.getAttribute( name ); 
	}
	return null;
    }

    public void setAttribute(String name, Object value) {
	if(name!=null && value!=null)
	    attributes.put(name, value);
    }

    public void removeAttribute(String name) {
	attributes.remove(name);
    }

    public Enumeration getAttributeNames() {
        return attributes.keys();
    }
    // End Attributes

    // -------------------- Facade for MimeHeaders
    public Enumeration getHeaders(String name) {
	//	Vector v = reqA.getMimeHeaders().getHeadersVector(name);
	Vector v = getMimeHeaders().getHeadersVector(name);
	return v.elements();
    }

    // -------------------- Utils - facade for RequestUtil
    public BufferedReader getReader()
	throws IOException
    {
	return RequestUtil.getReader( this );
    }

    private void handleParameters() {
   	if(!didParameters) {
	    String qString=getQueryString();
	    if(qString!=null) {
		didParameters=true;
		RequestUtil.processFormData( qString, parameters );
	    }
	}
	if (!didReadFormData) {
	    didReadFormData = true;
	    Hashtable postParameters=RequestUtil.readFormData( this );
	    if(postParameters!=null)
		parameters = RequestUtil.mergeParameters(parameters, postParameters);
	}
    }

    // -------------------- End utils
    public void recycle() {
        if( requestFacade != null && context!=null ) {
            context.getFacadeManager().recycle(this);
        }

        context = null;
        attributes.clear();
        parameters.clear();
        cookies.removeAllElements();
	//        requestURI = null;
	//        queryString = null;
        contentLength = -1;
        contentType = null;
        charEncoding = null;
        authType = null;
        remoteUser = null;
        reqSessionId = null;
        serverSession = null;
        didParameters = false;
        didReadFormData = false;
        didCookies = false;
        container=null;
        handler=null;
        jvmRoute = null;
        scheme = "http";// no need to use Constants
        method = "GET";
        requestURI="/";
        queryString=null;
        protocol="HTTP/1.0";
        headers.clear(); // XXX use recycle pattern
        serverName=null;
        serverPort=8080;
        pathTranslated=null;
        pathInfo=null;
        pathTranslatedIsSet=false;

        // XXX a request need to override those if it cares
        // about security
        remoteAddr="127.0.0.1";
        remoteHost="localhost";
        localHost="localhost";
	if( bBuffer != null ) bBuffer.recycle();
        for( int i=0; i<ACCOUNTS; i++ ) accTable[i]=0;
        for( int i=0; i<ContextManager.MAX_NOTES; i++ ) notes[i]=null;
    }

    public MimeHeaders getMimeHeaders() {
	return headers;
    }

    public String getHeader(String name) {
        return headers.getHeader(name);
    }

    public Enumeration getHeaderNames() {
        return headers.names();
    }

    public ByteBuffer getInputBuffer() {
	return bBuffer;
    }

    public void setInputBuffer(ByteBuffer buf) {
	bBuffer=buf;
    }

    
    public ServletInputStream getInputStream() throws IOException {
    	return in;
    }

    public int getServerPort() {
        return serverPort;
    }

    public String getRemoteAddr() {
        return remoteAddr;
    }

    public String getRemoteHost() {
	return remoteHost;
    }

    /** Fill in the buffer. This method is probably easier to implement than
	previous.
	This method should only be called from SerlvetInputStream implementations.
	No need to implement it if your adapter implements ServletInputStream.
     */
    // you need to override this method if you want non-empty InputStream
    public  int doRead( byte b[], int off, int len ) throws IOException {
	return -1; // not implemented - implement getInputStream
    }


    // XXX I hate this - but the only way to remove this method from the
    // inteface is to implement it on top of doRead(b[]).
    // Don't use this method if you can ( it is bad for performance !!)
    // you need to override this method if you want non-empty InputStream
    public int doRead() throws IOException {
	return -1;
    }

    // -------------------- "cooked" info --------------------
    // Hints = return null if you don't know,
    // and Tom will find the value. You can also use the static
    // methods in RequestImpl

    // What's between context path and servlet name ( /servlet )
    // A smart server may use arbitrary prefixes and rewriting
    public String getServletPrefix() {
	return null;
    }

    public void setScheme( String scheme ) {
	this.scheme=scheme;
    }

    public void setMethod( String method ) {
	this.method=method;
    }

    public void setProtocol( String protocol ) {
	this.protocol=protocol;
    }

    public void setMimeHeaders( MimeHeaders headers ) {
	this.headers=headers;
    }

    public void setBody( StringBuffer body ) {
	// ???
    }

    public void setServerPort(int serverPort ) {
	this.serverPort=serverPort;
    }

    public void setRemoteAddr( String remoteAddr ) {
	this.remoteAddr=remoteAddr;
    }

    public void setRemoteHost(String remoteHost) {
	this.remoteHost=remoteHost;
    }

    public String getLocalHost() {
	return localHost;
    }
    
    public void setLocalHost(String host) {
	this.localHost = host;
    }
    

    public String toString() {
	StringBuffer sb=new StringBuffer();
	sb.append( "R( ");
	if( context!=null) {
	    sb.append( context.getPath() );
	    if( getServletPath() != null )
		sb.append( " + " + getServletPath() + " + " + getPathInfo());
	    else
		sb.append( " + " + getLookupPath());
	} else {
	    sb.append(getRequestURI());
	}
	sb.append(")");
	return sb.toString();
    }

    public String toStringDebug() {
	StringBuffer sb=new StringBuffer();
	sb.append( "Request( " + context ).append("\n");
	sb.append( "    URI:" + getRequestURI()  ).append("\n");
	sb.append( "    SP:" + getServletPath() );
	sb.append( ",PI:" + getPathInfo() );
	sb.append( ",LP:" + getLookupPath() );
	sb.append( ",MP:" + getMappedPath() );
	sb.append( "," + getWrapper() +") ");
	return sb.toString();
    }

    // -------------------- Accounting --------------------
    // XXX Will be implemented as a note !
    public static final int ACC_PRE_CMAP=0;
    public static final int ACC_PRE_RMAP=1;
    public static final int ACC_POST_MAP=2;
    public static final int ACC_PRE_SERVICE=3;
    public static final int ACC_POST_SERVICE=4;
    public static final int ACC_IN_OUT=5;
    public static final int ACC_OUT_COUNT=6;
    
    public static final int ACCOUNTS=7;
    long accTable[]=new long[ACCOUNTS];

    public void setAccount( int pos, long value ) {
	accTable[pos]=value;
    }

    public long getAccount( int pos ) {
	return accTable[pos];
    }

    // -------------------- Per-Container "notes"
    Object notes[]=new Object[ContextManager.MAX_NOTES];

    public void setNote( int pos, Object value ) {
	notes[pos]=value;
    }

    public Object getNote( int pos ) {
	return notes[pos];
    }

}