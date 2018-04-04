contentLength = (clB==null || clB.isNull() ) ? -1 : clB.getInt();

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

import org.apache.tomcat.util.*;
import org.apache.tomcat.util.http.*;
import org.apache.tomcat.helper.*;
import org.apache.tomcat.session.ServerSession;
import java.io.IOException;
import java.io.*;
import java.net.*;
import java.security.*;
import java.util.*;

/**
 *
 * @author James Duncan Davidson [duncan@eng.sun.com]
 * @author James Todd [gonzo@eng.sun.com]
 * @author Jason Hunter [jch@eng.sun.com]
 * @author Harish Prabandham
 * @author Alex Cruikshank [alex@epitonic.com]
 * @author Hans Bergsten [hans@gefionsoftware.com]
 */
public class Request {
    public static final int ACC_PRE_CMAP=0;
    public static final int ACC_PRE_RMAP=1;
    public static final int ACC_POST_MAP=2;
    public static final int ACC_PRE_SERVICE=3;
    public static final int ACC_POST_SERVICE=4;
    public static final int ACC_IN_OUT=5;
    public static final int ACC_OUT_COUNT=6;

    public static final int ACCOUNTS=7;

    public static final String SESSIONID_FROM_COOKIE="cookie";
    public static final String SESSIONID_FROM_URL="url";
    public static final int MAX_INCLUDE=10;

    /** Magic attribute that allows access to the real request from
     *  facade - for trusted applications
     */
    public static final String ATTRIB_REAL_REQUEST="org.apache.tomcat.request";

    public static final int STATE_UNUSED=0;

    public static final int STATE_INVALID=-1;

    public static final int STATE_NEW=1;

    public static final int STATE_CONTEXT_MAPPED=2;

    public static final int STATE_MAPPED=3;
    
    // -------------------- properties --------------------

    protected int serverPort;
    protected String remoteAddr;
    protected String remoteHost;
    protected String localHost;

    protected int state;

    // Request components represented as MB.
    // MB are also used for headers - it allows lazy
    // byte->char conversion so we can add the encoding
    // that is known only after header parsing. Work in progress.
    protected MessageBytes schemeMB=new MessageBytes();

    protected MessageBytes methodMB=new MessageBytes();
    protected MessageBytes uriMB=new MessageBytes();
    protected MessageBytes queryMB=new MessageBytes();
    protected MessageBytes protoMB=new MessageBytes();
    // uri components
    protected MessageBytes contextMB=new MessageBytes();
    protected MessageBytes servletPathMB=new MessageBytes();
    protected MessageBytes pathInfoMB=new MessageBytes();

    // GS, used by the load balancing layer in the Web Servers
    // jvmRoute == the name of the JVM inside the plugin.
    protected String jvmRoute;

    protected Hashtable attributes = new Hashtable();
    protected MimeHeaders headers;

    // Processed information ( redundant ! )
    protected Hashtable parameters = new Hashtable();
    protected boolean didReadFormData;
    protected boolean didParameters;

    protected int contentLength = -1;
    protected String contentType = null;
    protected String charEncoding = null;
    protected MessageBytes serverNameMB=new MessageBytes();

    // auth infor
    protected String authType;
    boolean notAuthenticated=true;
    protected String remoteUser;
    protected Principal principal;
    // active roles for the current user
    protected String userRoles[];
    protected String reqRoles[];

    // Association with other tomcat comp.
    protected Response response;
    protected ContextManager contextM;
    protected Context context;
    protected Object requestFacade;

    // Session
    protected String reqSessionId;
    protected String sessionIdSource;
    protected String sessionId;
    // cache- avoid calling SessionManager for each getSession()
    protected ServerSession serverSession;

    // Handler
    protected Handler handler = null;
    Container container;

    Cookies scookies;
    //    ServerCookie scookies[]=new ServerCookie[4];
    // -1 = cookies not processed yet
    //    int cookieCount=-1;

    // sub-request support 
    Request top;
    Request parent;
    Request child;

    // Error handling support
    Exception errorException;

    private Object notes[]=new Object[ContextManager.MAX_NOTES];
    // Accounting
    private Counters cntr=new Counters(ACCOUNTS);

    // -------------------- Constructor --------------------

    public Request() {
 	headers = new MimeHeaders();
	scookies = new Cookies( headers );
	initRequest(); 	
    }

    public final int getState() {
	return state;
    }

    final void setState( int state ) {
	this.state=state;
    }
    
    /** Called by mapper interceptors after the context
	is found or directly by server adapters when
	this is known in advance
    */
    public void setContext(Context context) {
	this.context = context;
    }

    public Context getContext() {
	return context;
    }

    public void setContextManager( ContextManager cm ) {
	contextM=cm;
    }

    public ContextManager getContextManager() {
	return contextM;
    }

    public Object getFacade() {
	return requestFacade;
    }

    public void setFacade(Object facade ) {
	requestFacade=facade;
    }

    public void setResponse(Response response) {
	this.response = response;
    }

    public Response getResponse() {
	return response;
    }

    public MimeHeaders getMimeHeaders() {
	return headers;
    }

    public final Counters getCounters() {
	return cntr;
    }

    // -------------------- Request data --------------------

    public MessageBytes scheme() {
	return schemeMB;
    }
    
    public MessageBytes method() {
	return methodMB;
    }
    
    public MessageBytes requestURI() {
	return uriMB;
    }

    public MessageBytes queryString() {
	return queryMB;
    }
    
    public String getProtocol() {
        return protoMB.toString();
    }

    public void setProtocol( String protocol ) {
	protoMB.setString(protocol);
    }

    /** Return the buffer holding the server name, if
     *  any. Use isNull() to check if there is no value
     *  set.
     *  This is the "virtual host", derived from the
     *  Host: header.
     */
    public MessageBytes serverName() {
	return serverNameMB;
    }

//     /** Return the server name. If none was set,
//      *  extract it from the host header.
//      *
//      */
//     public String getServerName() {
//         return serverName;
//     }

//     /** Virtual host */
//     public void setServerName(String serverName) {
// 	this.serverName = serverName;
//     }

    
    public int getServerPort() {
        return serverPort;
    }

    public String getRemoteAddr() {
        return remoteAddr;
    }

    public String getRemoteHost() {
	return remoteHost;
    }

    public void setPathInfo(String pathInfo) {
        pathInfoMB.setString( pathInfo );
    }

//     // What's between context path and servlet name ( /servlet )
//     // A smart server may use arbitrary prefixes and rewriting
//     public String getServletPrefix() {
// 	return null;
//     }

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


    // -------------------- Parameters --------------------
    
    // XXX optimize for common case ( single params )
    public String getParameter(String name ) {
	String[] values = getParameterValues(name);
        if (values != null) {
            return values[0];
        } else {
	    return null;
        }
    }

    public String[] getParameterValues(String name) {
	handleParameters();
        return (String[])parameters.get(name);
    }

    public Enumeration getParameterNames() {
	handleParameters();
        return parameters.keys();
    }

    // --------------------

    public void setAuthType(String authType) {
        this.authType = authType;
    }
    
    public String getAuthType() {
    	return authType;
    }

    public String getCharacterEncoding() {
        if(charEncoding!=null) return charEncoding;
        charEncoding = RequestUtil.getCharsetFromContentType( getContentType());
	return charEncoding;
    }

    public void setCharEncoding( String enc ) {
	this.charEncoding=enc;
    }

    public void setContentLength( int  len ) {
	this.contentLength=len;
    }

    public int getContentLength() {
        if( contentLength > -1 ) return contentLength;

	MessageBytes clB=headers.getValue("content-length");
        contentLength = (clB==null) ? -1 : clB.getInt();

	return contentLength;
    }

    // XXX XXX POSSIBLE BUG - should trim the charset encoding ( or not ? )
    public String getContentType() {
	if(contentType != null) return contentType;
	contentType = getHeader("content-type");
	if(contentType != null) return contentType;
	// can be null!! -
	return contentType;
    }

    public void setContentType( String type ) {
	this.contentType=type;
    }

    // XXX XXX Servlet API conflicts with the CGI specs -
    // PathInfo should be "" if no path info is requested ( as it is in CGI ).
    // We are following the spec, but IMHO it's a bug ( in the spec )
    public String getPathInfo() {
        return pathInfoMB.toString();
    }

    public void setRemoteUser(String s) {
	remoteUser=s;
	// this is set by an auth module
	// 	context.log("Set user " + s );
	notAuthenticated=false;
    }

    public String getRemoteUser() {
	if( notAuthenticated ) {
	    notAuthenticated=false;

	    // Call all authentication callbacks. If any of them is able to
	    // 	identify the user it will set the principal in req.
	    int status=0;
	    BaseInterceptor reqI[]= getContext().getContainer().getInterceptors(Container.H_authenticate);
            //.getInterceptors(this,);
	    for( int i=0; i< reqI.length; i++ ) {
		status=reqI[i].authenticate( this, response );
		if ( status != 0 ) {
		    break;
		}
	    }
	    // 	    context.log("Auth " + remoteUser );
	}
	return remoteUser;
    }

    public boolean isSecure() {
	// The adapter is responsible for providing this information
        return schemeMB.equalsIgnoreCase("HTTPS");
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

    public void setRequiredRoles( String roles[] ) {
	reqRoles=roles;
    }

    public String[] getRequiredRoles( ) {
	return reqRoles;
    }

    public void setUserRoles( String roles[] ) {
	userRoles=roles;
    }

    public String[] getUserRoles( ) {
	return userRoles;
    }

    String checkRoles[]=new String[1];
    public boolean isUserInRole(String role) {
	checkRoles[0]=role;

	int status=0;
	BaseInterceptor reqI[]= getContainer().
	    getInterceptors(Container.H_authorize);

	// Call all authorization callbacks. 
	for( int i=0; i< reqI.length; i++ ) {
	    status = reqI[i].authorize( this, response, checkRoles );
	    if ( status != 0 ) {
		break;
	    }
	}
	return status==0;
    }

    public String getServletPath() {
        return servletPathMB.toString();
    }

    public void setServletPath(String servletPath) {
	servletPathMB.setString( servletPath );
    }



    // -------------------- Session --------------------
    // GS - return the jvm load balance route
    public String getJvmRoute() {
	    return jvmRoute;
    }

    public void setJvmRoute(String jvmRoute) {
	if( jvmRoute==null || "".equals(jvmRoute))
	    this.jvmRoute=null;
	this.jvmRoute=jvmRoute;
    }

    /** Session ID requested by client as a cookie or any other
     *   method. It may be a valid ( and existing ) session or not.
     */
    public String getRequestedSessionId() {
        return reqSessionId;
    }

    public void setRequestedSessionId(String reqSessionId) {
	this.reqSessionId = reqSessionId;
    }

    /** Method used to determine requestedSessionId
     */
    public String getSessionIdSource() {
	return sessionIdSource;
    }

    public void setSessionIdSource(String s) {
	sessionIdSource=s;
    }

    /** "Real" session Id, coresponding to an existing ServerSession
     */
    public void setSessionId( String id ) {
	if( ! response.isIncluded() ) sessionId=id;
    }

    public String getSessionId() {
	return sessionId;
    }

    /** Set the session associated with this request. This can be
	the current session or a new session, set by a session
	interceptor.

	Important: you also need to set the session id ( this is needed to
	cleanly separate the layers, and will be improved soon - the
	whole session management will follow after core is done )
    */
    public void setSession(ServerSession serverSession) {
	this.serverSession = serverSession;
    }

    
    public ServerSession getSession(boolean create) {


	if( serverSession!=null ) {
             /// XXX a forwarded request whose session was invalidated
            if (!serverSession.getTimeStamp().isValid() && create){
                 serverSession.getSessionManager().removeSession( serverSession );
                 serverSession=null;
            } else
                // if not null, it is validated by the session module
        	return serverSession;
	}

	if( ! create ) return null;
        
	BaseInterceptor reqI[]= getContainer().
	    getInterceptors(Container.H_newSessionRequest);

	for( int i=0; i< reqI.length; i++ ) {
	    reqI[i].newSessionRequest( this, response );
	}

	return serverSession;
    }

    // -------------------- Cookies --------------------

    public Cookies getCookies() {
	return scookies;
    }
    
//     public int getCookieCount() {
// 	if( cookieCount == -1 ) {
// 	    cookieCount=0;
// 	    // compute cookies
// 	    CookieTools.processCookies( this );
// 	}
// 	return cookieCount;
//     }

//     public ServerCookie getCookie( int idx ) {
// 	if( cookieCount == -1 ) {
// 	    getCookieCount(); // will also update the cookies
// 	}
// 	return scookies[idx];
//     }

//     public void addCookie( ServerCookie c ) {
// 	// not really needed - happen in 1 thread
// 	synchronized ( this ) {
// 	    if( cookieCount >= scookies.length  ) {
// 		ServerCookie scookiesTmp[]=new ServerCookie[2*cookieCount];
// 		System.arraycopy( scookies, 0, scookiesTmp, 0, cookieCount);
// 		scookies=scookiesTmp;
// 	    }
// 	    scookies[cookieCount++]=c;
// 	}
//     }

    // -------------------- LookupResult

    /** As result of mapping the request a "handler" will be associated
	and called to generate the result.

	The handler is null if no mapping was found ( so far ).

	The handler can be set if the request is found to match any
	of the rules defined in web.xml ( and as a result, a container will
	be set ), or if a special interceptor will define a tomcat-specific
	handler ( like static, jsp, or invoker ).
    */
    public Handler getHandler() {
	return handler;
    }

    public void setHandler(Handler handler) {
	this.handler=handler;
    }

    /** Return the container ( URL pattern ) where this request has been
	mapped.

	If the request is invalid ( context can't be determined )
	the ContextManager.container will be returned.

	If the request is not mapped ( requestMap not called yet )
	or the request corresponds to the "default" map ( * ) or a
	special implicit map ( *.jsp, invoker ),
	then the context's default container is returned
    */
    public Container getContainer() {
	if( container==null && context==null) {
	    container=contextM.getContainer();
	    // only for invalid requests !
	}
	if( container==null ) {
	    container=context.getContainer();
	}
	return container;
    }

    public void setContainer(Container container) {
	this.container=container;
    }

    public void setParameters( Hashtable h ) {
	if(h!=null)
	    this.parameters=h;
    }

    public Hashtable getParameters() {
	return parameters;
    }

    // -------------------- Attributes
    
    public Object getAttribute(String name) {
        Object value=attributes.get(name);
	if( value != null )
	    return value;

	// allow access to FacadeManager for servlets
	if(name.equals(ATTRIB_REAL_REQUEST)) {
	    if( ! context.allowAttribute(name) ) return null;
	    return this;
	}

	return null;
    }

    public void setAttribute(String name, Object value) {
	//	contextM.log( "setAttribure " + name +  " " + value );
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

    // -------------------- Sub requests --------------------

    /** If this is a sub-request, return the parent
     */
    public Request getParent() {
	return parent;
    }

    public void setParent( Request req ) {
	parent =req;
    }

    /** During include, a sub-request will be created.
     *  This represents the current included request
     */
    public Request getChild() {
	return child;
    }

    public void setChild( Request req ) {
	child=req;
    }

    /** This is the top request ( for a sub-request )
     */
    public Request getTop() {
	if( top == null  ) {
	    if( parent==null )
		top=this;
	    else {
		int i=MAX_INCLUDE;
		Request p=parent;
		while( i-- > 0 && p.getParent()!= null )
		    p=p.getParent();
		if( i == 0 )
		    throw new IllegalStateException("Too deep includes");
		top=p;
	    }
	}
	return top;
    }

    // -------------------- Facade for MimeHeaders
    public Enumeration getHeaders(String name) {
	return getMimeHeaders().values(name);
    }

    public String getHeader(String name) {
        return headers.getHeader(name);
    }

    public Enumeration getHeaderNames() {
        return headers.names();
    }

    // -------------------- Utils - facade for RequestUtil
    private void handleParameters() {
   	if(!didParameters) {
	    String qString=queryString().toString();
	    if(qString!=null) {
		didParameters=true;
		RequestUtil.processFormData( qString, parameters );
	    }
	}
	if (!didReadFormData) {
	    didReadFormData = true;
	    Hashtable postParameters=RequestUtil.readFormData( this );
	    if(postParameters!=null)
		parameters = RequestUtil.mergeParameters(parameters,
							 postParameters);
	}
    }


    // -------------------- Computed fields --------------------
    

    // -------------------- For adapters --------------------
    
    /** Fill in the buffer. This method is probably easier to implement than
	previous.
	This method should only be called from SerlvetInputStream implementations.
	No need to implement it if your adapter implements ServletInputStream.
     */
    // you need to override this method if you want non-empty InputStream
    public  int doRead( byte b[], int off, int len ) throws IOException {
	return -1; // not implemented - implement getInputStream
    }


    // This method must be removed and replaced with a real buffer !!!
    byte b[]=new byte[1]; // read operations happen in the same thread.
    // if needed, upper layer can synchronize ( well, 2 threads reading
    // the input stream is not good anyway )
    
    public int doRead() throws IOException {
        byte []b = new byte[1];
        int rc = doRead(b, 0, 1);

        if(rc <= 0) {
            return -1;
        }

	return b[0];
	// ??
	//return ((int)b[0]) & 0x000000FF;
    }

    // ----------------- Error State -----------------

    /** Set most recent exception that occurred while handling
	this request.
     */
    public void setErrorException( Exception ex ) {
	errorException = ex;
    }

    /** Get most recent exception that occurred while handling
	this request.
     */
    public Exception getErrorException() {
	return errorException;
    }

    public boolean isExceptionPresent() {
	return ( errorException != null );
    }

    // -------------------- debug --------------------
    
    public String toString() {
	StringBuffer sb=new StringBuffer();
	sb.append( "R( ");
	if( context!=null) {
	    sb.append( context.getPath() );
	    if( getServletPath() != null )
		sb.append( " + " + getServletPath() + " + " + getPathInfo());
	} else {
	    sb.append(requestURI().toString());
	}
	sb.append(")");
	return sb.toString();
    }

    // -------------------- Per-Request "notes" --------------------

    public final void setNote( int pos, Object value ) {
	notes[pos]=value;
    }

    public final Object getNote( int pos ) {
	return notes[pos];
    }

    // -------------------- Recycling -------------------- 
    public void recycle() {
	initRequest();
    }

    public void initRequest() {
        context = null;
        attributes.clear();
        parameters.clear();
	contentLength = -1;
        contentType = null;
        charEncoding = null;
        authType = null;
        remoteUser = null;
        reqSessionId = null;
        serverSession = null;
        didParameters = false;
        didReadFormData = false;
        container=null;
        handler=null;
	errorException=null;
        jvmRoute = null;
        headers.clear(); // XXX use recycle pattern
        serverNameMB.recycle();
	//serverName=null;
        serverPort=-1;
        sessionIdSource = null;
	sessionId=null;
	
// 	for( int i=0; i< cookieCount; i++ ) {
// 	    if( scookies[i]!=null )
// 		scookies[i].recycle();
// 	}
// 	cookieCount=-1;
	scookies.recycle();
	
	// counters and notes
        cntr.recycle();
        for( int i=0; i<ContextManager.MAX_NOTES; i++ ) notes[i]=null;

	// sub-req
	parent=null;
	child=null;
	top=null;

	// auth
        notAuthenticated=true;
	userRoles=null;
	reqRoles=null;

	uriMB.recycle();
	contextMB.recycle();
	pathInfoMB.recycle();
	servletPathMB.recycle();
	queryMB.recycle();
	methodMB.recycle();
	protoMB.recycle();

	// XXX Do we need such defaults ?
        schemeMB.setString("http");
	methodMB.setString("GET");
        uriMB.setString("/");
        queryMB.setString("");
        protoMB.setString("HTTP/1.0");
        remoteAddr="127.0.0.1";
        remoteHost="localhost";
//        localHost="localhost";

    }
}