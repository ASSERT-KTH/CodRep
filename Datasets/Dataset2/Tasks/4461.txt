public final void setState( int state ) {

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

import org.apache.tomcat.util.http.MimeHeaders;
import org.apache.tomcat.util.http.Parameters;
import org.apache.tomcat.util.http.ContentType;
import org.apache.tomcat.util.http.Cookies;

import org.apache.tomcat.util.buf.*;


//import org.apache.tomcat.util.http.*;

import java.security.Principal;
import java.io.IOException;
import java.util.Enumeration;
import java.util.Hashtable;

/**
 * This is a low-level, efficient representation of a server request. Most fields
 * are GC-free, expensive operations are delayed until the  user code needs the
 * information.
 *
 * Most processing is delegated to modules, using a hook mechanism.
 * 
 * This class is not intended for user code - it is used internally by tomcat
 * for processing the request in the most efficient way. Users ( servlets ) can
 * access the information using a facade, which provides the high-level view
 * of the request.
 *
 * For lazy evaluation, the request uses the getInfo() hook. The following ids
 * are defined:
 * <ul>
 *  <li>req.encoding - returns the request encoding
 *  <li>req.attribute - returns a module-specific attribute ( like SSL keys, etc ).
 * </ul>
 *
 * Tomcat defines a number of attributes:
 * <ul>
 *   <li>"org.apache.tomcat.request" - allows access to the low-level
 *       request object in trusted applications 
 * </ul>
 *
 * @author James Duncan Davidson [duncan@eng.sun.com]
 * @author James Todd [gonzo@eng.sun.com]
 * @author Jason Hunter [jch@eng.sun.com]
 * @author Harish Prabandham
 * @author Alex Cruikshank [alex@epitonic.com]
 * @author Hans Bergsten [hans@gefionsoftware.com]
 * @author Costin Manolache
 */
public class Request {
    // As specified in the servlet specs
    public static final String DEFAULT_CHARACTER_ENCODING="ISO-8859-1";
    
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
    //    protected String remoteAddr;
    //    protected String remoteHost;
    protected String localHost;

    protected int state;

    // Request components represented as MB.
    // MB are also used for headers - it allows lazy
    // byte->char conversion so we can add the encoding
    // that is known only after header parsing. Work in progress.
    protected MessageBytes schemeMB=new MessageBytes();

    // uri without any parsing performed
    protected MessageBytes unparsedURIMB=new MessageBytes();

    protected MessageBytes methodMB=new MessageBytes();
    protected MessageBytes uriMB=new MessageBytes();
    protected MessageBytes queryMB=new MessageBytes();
    protected MessageBytes protoMB=new MessageBytes();
    // uri components
    protected MessageBytes contextMB=new MessageBytes();
    protected MessageBytes servletPathMB=new MessageBytes();
    protected MessageBytes pathInfoMB=new MessageBytes();

    // remote address/host
    protected MessageBytes remoteAddrMB=new MessageBytes();
    protected MessageBytes remoteHostMB=new MessageBytes();
    
    // GS, used by the load balancing layer in the Web Servers
    // jvmRoute == the name of the JVM inside the plugin.
    protected String jvmRoute;

    protected Hashtable attributes = new Hashtable();
    protected MimeHeaders headers;

    // Processed information ( redundant ! )
    protected Parameters params=new Parameters();
    protected boolean didReadFormData=false;

    protected int contentLength = -1;
    // how much body we still have to read.
    protected int available = -1; 

    protected MessageBytes contentTypeMB=null;
    //    protected String contentType = null;
    protected String charEncoding = null;
    protected MessageBytes serverNameMB=new MessageBytes();

    // auth infor
    protected String authType;
    protected boolean notAuthenticated=true;
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
    protected Container container;

    protected Cookies scookies;

    // sub-request support 
    protected Request top;
    protected Request parent;
    protected Request child;

    protected UDecoder urlDecoder;
    
    // Error handling support
    protected Exception errorException;

    private Object notes[]=new Object[ContextManager.MAX_NOTES];

    // -------------------- Constructor --------------------

    public Request() {
 	headers = new MimeHeaders();
	scookies = new Cookies( headers );
	urlDecoder=new UDecoder();
	params.setQuery( queryMB );
	params.setURLDecoder( urlDecoder );
	params.setHeaders( headers );
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

    public UDecoder getURLDecoder() {
	return urlDecoder;
    }

    // cached note ids 
    private int encodingInfo;
    private int attributeInfo;
    
    public void setContextManager( ContextManager cm ) {
	contextM=cm;
	try {
	    encodingInfo=cm.getNoteId(ContextManager.REQUEST_NOTE,
				      "req.encoding" );
	    attributeInfo=cm.getNoteId(ContextManager.REQUEST_NOTE,
				       "req.attribute");
	} catch( TomcatException ex ) {
	    ex.printStackTrace();
	}
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

    // -------------------- 
    
    public MimeHeaders getMimeHeaders() {
	return headers;
    }

    // -------------------- Request data --------------------

    public MessageBytes scheme() {
	return schemeMB;
    }
    
    public MessageBytes method() {
	return methodMB;
    }

    /** @deprecated After Tomcat 3.2, use {@link #method()} instead */
    public String getMethod() {
	return methodMB.toString();
    }

    /** @deprecated After Tomcat 3.2, use {@link #method()} instead */
    public void setMethod(String method) {
	methodMB.setString(method);
    }

    public MessageBytes requestURI() {
	return uriMB;
    }

    /** @deprecated After Tomcat 3.2, use {@link #requestURI()} instead */
    public String getRequestURI() {
	return uriMB.toString();
    }

    /** @deprecated After Tomcat 3.2, use {@link #requestURI()} instead */
    public void setRequestURI(String r) {
	uriMB.setString(r);
    }

    public MessageBytes unparsedURI() {
	return unparsedURIMB;
    }

    public MessageBytes query() {
	return queryMB;
    }

    public MessageBytes queryString() {
	return query();
    }

    public MessageBytes servletPath() {
	return servletPathMB;
    }

    public MessageBytes pathInfo() {
	return pathInfoMB;
    }

    public MessageBytes protocol() {
	return protoMB;
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
    
    public int getServerPort() {
        return serverPort;
    }

    public void setServerPort(int serverPort ) {
	this.serverPort=serverPort;
    }
    
    public MessageBytes remoteAddr() {
	return remoteAddrMB;
    }

    public MessageBytes remoteHost() {
	return remoteHostMB;
    }

    public String getLocalHost() {
	return localHost;
    }

    public void setLocalHost(String host) {
	this.localHost = host;
    }


    // -------------------- Parameters --------------------

    /** Read the body, if POST, and add the post parameters.
     *  Before this method is called, only query-line parameters
     *  are available.
     */
    public void handlePostParameters() {
	if( didReadFormData )
	    return;
	didReadFormData=true;

	if( ! method().equalsIgnoreCase("POST") )
	    return;
	String contentType= getContentType();
	if (contentType == null ||
            ! contentType.startsWith("application/x-www-form-urlencoded")) {
	    return;
	}

	int len=getContentLength();
	int available=getAvailable();
	
	// read only available ( someone else may have read the content )
	if( available > 0 ) {
	    try {
		byte[] formData=null;
		if( available < CACHED_POST_LEN ) {
		    if( postData == null ) postData=new byte[CACHED_POST_LEN];
		    formData=postData;
		} else {
		    formData = new byte[available];
		}
		readBody( formData, available );
		
		handleQueryParameters();

		params.processParameters( formData, 0, available );
	    } catch(IOException ex ) {
		ex.printStackTrace();
		// XXX should we throw exception or log ?
		return;
	    }
	}
    }

    public void handleQueryParameters() {
	// set the encoding for query parameters.
	getCharacterEncoding();
	if( charEncoding  != null ) 
	    params.setEncoding( getCharacterEncoding() );
	else
	    params.setEncoding( DEFAULT_CHARACTER_ENCODING );
	params.handleQueryParameters();
    }
    
    // Avoid re-allocating the buffer for each post
    private static int CACHED_POST_LEN=8192;
    private byte postData[]=null;

    public Parameters parameters() {
	return params;
    }
    
    // -------------------- encoding/type --------------------

    public String getCharacterEncoding() {
	return getCharEncoding();
    }

    public String getCharEncoding() {
        if(charEncoding!=null) return charEncoding;

	Object result=null;
	Context ctx=getContext();
	if( ctx!=null ) {
	    
	    BaseInterceptor reqI[]= ctx.getContainer().
		getInterceptors(Container.H_getInfo);
	    for( int i=0; i< reqI.length; i++ ) {
		result=reqI[i].getInfo( ctx, this, encodingInfo, null );
		if ( result != null ) {
		    break;
		}
	    }
	    if( result != null ) {
		charEncoding=(String)result;
		return charEncoding;
	    }
	}
	
	if( charEncoding == null )
	    charEncoding=DEFAULT_CHARACTER_ENCODING;
 	return charEncoding;
    }

    public void setCharEncoding( String enc ) {
	this.charEncoding=enc;
	//	if( enc==null ) enc=DEFAULT_CHARACTER_ENCODING;
	//	b2c=getDecoder( enc );
    }
    
    public void setContentLength( int  len ) {
	this.contentLength=len;
	available=len;
    }

    public int getContentLength() {
        if( contentLength > -1 ) return contentLength;

	MessageBytes clB=getMimeHeaders().getValue("content-length");
        contentLength = (clB==null || clB.isNull() ) ? -1 : clB.getInt();
	available=contentLength;

	return contentLength;
    }

    /** @deprecated
     */
    public String getContentType() {
	contentType();
	if( contentTypeMB==null ||
	    contentTypeMB.isNull() ) return null;
	return contentTypeMB.toString();
    }

    /** @deprecated
     */
    public void setContentType( String type ) {
	contentTypeMB.setString( type );
    }

    public MessageBytes contentType() {
	if( contentTypeMB == null )
	    contentTypeMB=getMimeHeaders().getValue( "content-type" );
	return contentTypeMB;
    }

    /** @deprecated
     */
    public void setContentType( MessageBytes mb  ) {
	contentTypeMB=mb;
    }
    // -------------------- Security info -------------------- 
    
    public void setAuthType(String authType) {
        this.authType = authType;
    }
    
    public String getAuthType() {
    	return authType;
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
	    BaseInterceptor reqI[]= getContext().getContainer().
		getInterceptors(Container.H_authenticate);
	    for( int i=0; i< reqI.length; i++ ) {
		status=reqI[i].authenticate( this, response );
		if ( status != BaseInterceptor.DECLINED ) {
		    break;
		}
	    }
	    //context.log("Auth " + remoteUser );
	}
	return remoteUser;
    }

    public boolean isSecure() {
	// The adapter is responsible for providing this information
        return scheme().equalsIgnoreCase("HTTPS");
    }

    public void setUserPrincipal( Principal p ) {
	principal=p;
    }

    /** Return the principal - the adapter will set it
     */
    public Principal getUserPrincipal() {
	if( getRemoteUser() == null ) return null;
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

    private String checkRoles[]=new String[1];
    public boolean isUserInRole(String role) {
	checkRoles[0]=role;

	int status=0;
	BaseInterceptor reqI[]= getContainer().
	    getInterceptors(Container.H_authorize);

	// Call all authorization callbacks. 
	for( int i=0; i< reqI.length; i++ ) {
	    status = reqI[i].authorize( this, response, checkRoles );
	    if ( status != BaseInterceptor.DECLINED ) {
		break;
	    }
	}
	return status==0;
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
	if (serverSession!=null && !serverSession.isValid())
	    serverSession=null;

	if( ! create || serverSession!=null )
	    return serverSession;

	// create && serverSession==null

	BaseInterceptor reqI[]= getContainer().
	    getInterceptors(Container.H_findSession);

	for( int i=0; i< reqI.length; i++ ) {
	    serverSession=reqI[i].findSession( this, null, create );
	    if( serverSession!=null ) break;
	}
	if( serverSession!= null ) {
	    setSessionId( serverSession.getId().toString());
	}
	return serverSession;
    }

    // -------------------- Cookies --------------------

    public Cookies getCookies() {
	return scookies;
    }
    
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

    // -------------------- Attributes
    
    public Object getAttribute(String name) {
        Object value=attributes.get(name);
	if( value != null )
	    return value;

	Object result=null;
	Context ctx=getContext();
	if( ctx== null )
	    return null;
	
	BaseInterceptor reqI[]= ctx.getContainer().
	    getInterceptors(Container.H_getInfo);
	for( int i=0; i< reqI.length; i++ ) {
	    result=reqI[i].getInfo( ctx, this, attributeInfo, name );
	    if ( result != null ) {
		break;
	    }
	}
	if( result != null ) {
	    return result;
	}
    
	// allow access to FacadeManager for servlets
	// XXX move to module. Don't add any new special case, the hooks should
	// be used
	if(name.equals(ATTRIB_REAL_REQUEST)) {
	    if( ! context.allowAttribute(name) ) return null;
	    return this;
	}

	return null;
    }

    public void setAttribute(String name, Object value) {
	int status=BaseInterceptor.DECLINED;
	Context ctx=getContext();
	if( ctx!=null ) {
	    BaseInterceptor reqI[]= ctx.getContainer().
		getInterceptors(Container.H_setInfo);
	    for( int i=0; i< reqI.length; i++ ) {
		status=reqI[i].setInfo( ctx, this, attributeInfo,
					name, value );
		if ( status != BaseInterceptor.DECLINED ) {
		    break;
		}
	    }
	    if ( status != BaseInterceptor.DECLINED ) {
		return; // don't set it, the module will manage it
	    }
	}

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
     *  ( the request embeding this request )
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
    /** @deprecated
     */
    public Enumeration getHeaders(String name) {
	return getMimeHeaders().values(name);
    }

    /** @deprecated
     */
    public String getHeader(String name) {
        return getMimeHeaders().getHeader(name);
    }

    /** @deprecated
     */
    public Enumeration getHeaderNames() {
        return getMimeHeaders().names();
    }

    // -------------------- Computed fields --------------------
    

    // -------------------- For adapters --------------------
    // This should move to an IntputBuffer - the reading of the
    // request body is really bad in tomcat, it needs some work
    // and optimizations.

    // We need to make sure nobody reads more than is available
    // That may happen if both POST and input stream are used
    // ( illegal, but can happen - and then we're hunged )
    // ( also, getParameter doesn't throw any exception - if the
    // user reads the body and then calls getParameter() the best
    // action is to get him the query params - which are available.
    

    public void setAvailable( int  len ) {
	this.available=len;
    }

    /** How many bytes from the body are still available
     */
    public int getAvailable() {
	
	return available;
    }

    
    /** Fill in the buffer. This method is probably easier to implement than
	previous.
	This method should only be called from SerlvetInputStream
	implementations.
	No need to implement it if your adapter implements ServletInputStream.
     */
    // you need to override this method if you want non-empty InputStream
    public  int doRead( byte b[], int off, int len ) throws IOException {
	//	System.out.println( "doRead " );
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
    
    /** Read request data, filling a byte[]
     */
    public int readBody(byte body[], int len)
	throws IOException
    {
	int offset = 0;
	//	System.out.println( "ReadBody ");
	do {
	    int inputLen = doRead(body, offset, len - offset);
	    if (inputLen <= 0) {
		return offset;
	    }
	    offset += inputLen;
	} while ((len - offset) > 0);
	return len;
    }



    
    // -------------------- debug --------------------
    
    public String toString() {
	StringBuffer sb=new StringBuffer();
	sb.append( "R( ");
	if( context!=null) {
	    sb.append( context.getPath() );
	    if( ! servletPath().isNull() )
		sb.append( " + " + servletPath().toString() + " + " +
			   pathInfo().toString());
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

    public Object getNote( String name ) throws TomcatException {
	int id=contextM.getNoteId( ContextManager.REQUEST_NOTE,
				   name );
	return getNote( id );
    }

    public void setNote( String name, Object value ) throws TomcatException {
	int id=contextM.getNoteId( ContextManager.REQUEST_NOTE,
				   name );
	setNote( id, value );
    }


    // -------------------- Recycling -------------------- 
    public void recycle() {
	initRequest();
    }

    public void initRequest() {
        context = null;
        attributes.clear();
	//        parametersH.clear();
	params.recycle();
	contentLength = -1;
        contentTypeMB=null;
        charEncoding = null;
        authType = null;
        remoteUser = null;
	principal = null;
        reqSessionId = null;
        serverSession = null;
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
	//	b2c=null;
	
	scookies.recycle();
	
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
	unparsedURIMB.recycle();
	contextMB.recycle();
	pathInfoMB.recycle();
	servletPathMB.recycle();
	queryMB.recycle();
	methodMB.recycle();
	protoMB.recycle();
	remoteAddrMB.recycle();
	remoteHostMB.recycle();

	// XXX Do we need such defaults ?
        schemeMB.setString("http");
	methodMB.setString("GET");
        uriMB.setString("/");
        queryMB.setString("");
        protoMB.setString("HTTP/1.0");
        remoteAddrMB.setString("127.0.0.1");
        remoteHostMB.setString("localhost");
    }
}