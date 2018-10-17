public HttpServletRequest getFacade() ;

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
import java.io.*;
import java.net.*;
import java.security.*;
import java.util.*;
import javax.servlet.*;
import javax.servlet.http.*;


/**
 *
 */
public interface Request  {

    // -------------------- Basic Request properties --------------------
    public String getScheme() ;

    public String getMethod() ;

    public String getRequestURI() ;

    public void setRequestURI( String r ) ;

    public String getQueryString() ;

    public String getProtocol() ;

    // -------------------- Connection information
    public String getServerName() ;

    public void setServerName(String serverName) ;

    public int getServerPort() ;

    public String getRemoteAddr() ;

    /** Expensive - should be implemented as a callback where
     *  possible!
    */
    public String getRemoteHost() ;

    // -------------------- Headers --------------------
    public String getHeader(String name) ;

    public Enumeration getHeaderNames() ;

    public Enumeration getHeaders(String name) ;

    //-------------------- "Computed" properties --------------------
    // ( directly derived from headers or request paths )

    /** Return the cookies
     */
    public Cookie[] getCookies() ;

    public int getContentLength() ;

    public void setContentLength( int  len ) ;

    public String getContentType() ;

    public void setContentType( String type ) ;

    public void setCharEncoding( String enc ) ;

    public String getCharacterEncoding() ;

    // -------------------- Mapping --------------------
    // Will be set by mappers or
    // by adapter

    /** Context - will be set by contextMap stage of request interceptors
     */
    public void setContext(Context context) ;

    public Context getContext() ;

    /** Real Path - should be implemented as a callback ( override it in adapters).
     *  Map interceptor should set it to something reasonable ( context home + path )
     *  MappedPath is similar - it contain mappings inside a context, for normal
     *      contexts pathTranslated==context.docBase + mappedPath
     */
    String getPathTranslated() ;

    /**
     */
    void setPathTranslated(String path) ;

    /** Path Info - set be mappers or from adapter
     */
    public String getPathInfo() ;

    public void setPathInfo(String pathInfo) ;

    /** Servlet Path
     */
    public void setServletPath(String servletPath) ;

    public String getServletPath() ;


    public Container getContainer() ;

    public void setContainer(Container handler) ;

    // -------------------- Security --------------------
    // Will be set by security interceptors

    public String getAuthType() ;

    public void setAuthType(String authType) ;

    String getRemoteUser() ;

    void setRemoteUser(String s) ;

    boolean isSecure() ;

    public void setUserRoles( String roles[] );

    public String[] getUserRoles( );
    
    /**
     */
     Principal getUserPrincipal() ;

    void setUserPrincipal(Principal p) ;

    /**
     */
    boolean isUserInRole(String role) ;

    // -------------------- Session --------------------
    // Multiple JVM support
    // GS, used by the load balancing layer
    public String getJvmRoute();
    public void setJvmRoute(String route);

    // Will be set by session interceptors
    public String getRequestedSessionId() ;

    public void setRequestedSessionId(String reqSessionId) ;

    public static final String SESSIONID_FROM_COOKIE="cookie";
    public static final String SESSIONID_FROM_URL="url";

    /** Get the source of the session Id.
     */
    public String getSessionIdSource() ;
    
    public void setSessionIdSource(String s) ;

    public void setSession(HttpSession serverSession) ;

    public HttpSession getSession(boolean create) ;

    // -------------------- Parameters --------------------
    /** Set query string - will be called by forward
     */
    public void setQueryString(String queryString) ;

    public String[] getParameterValues(String name) ;

    public Enumeration getParameterNames() ;

    // -------------------- Attributes --------------------
    public Object getAttribute(String name) ;

    public void setAttribute(String name, Object value) ;

    public void removeAttribute(String name) ;

    public Enumeration getAttributeNames() ;

    // -------------------- Input --------------------

    // XXX review - do we need both reader and IS ?
    public BufferedReader getReader() 	throws IOException;

    public ServletInputStream getInputStream() 	throws IOException;

    // -------------------- Internal methods --------------------
    /** Support for "pools"
     */
    public void recycle() ;

    /** One-to-One with Response
     */
    public Response getResponse() ;

    public void setResponse(Response response) ;

    /** One-to-One with Facade
     */
    public HttpServletRequestFacade getFacade() ;

    /** Pointer to the server engine - for errors, etc
     */
    public void setContextManager( ContextManager cm );

    public ContextManager getContextManager();

    // -------------------- Internal/deprecated--------------------
    // Derived from parsing query string and body (for POST)

    // Used in ReqDispatcher
    /** @deprecated internal use only */
    public void setParameters( Hashtable h ) ;
    /** @deprecated internal use only */
    public Hashtable getParameters() ;


    /** Wrapper - the servlet that will execute the request
     *  Similar with "handler" in Apache.
     *  @deprecated - use Container instead
     */
    public ServletWrapper getWrapper() ;

    /**
     *  @deprecated - use Container instead
     */
    public void setWrapper(ServletWrapper handler) ;

    // -------------------- Notes --------------------
    /** Add a per/request internal attribute.
     *  We keep internal attributes in a separate space to prevent
     *  servlets from accessing them. We also use indexed access for
     *  speed ( as oposed to hashtable lookups ). Get an Id from ContextManager.
     */
    public void setNote( int pos, Object value );

    public Object getNote( int pos );
}