public final class HttpServletRequestFacade implements HttpServletRequest {

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


package org.apache.tomcat.facade;

import org.apache.tomcat.util.res.StringManager;
import org.apache.tomcat.util.io.FileUtil;
import org.apache.tomcat.util.buf.DateTool;
import org.apache.tomcat.util.buf.UEncoder;
import org.apache.tomcat.util.http.*;
import org.apache.tomcat.core.*;
import org.apache.tomcat.facade.*;
import java.io.*;
import java.net.*;
import java.security.*;
import java.util.*;
import java.text.*;
import javax.servlet.*;
import javax.servlet.http.*;

/**
 * The facade to the request that a servlet will see.
 *
 * @author James Duncan Davidson [duncan@eng.sun.com]
 * @author Jason Hunter [jch@eng.sun.com]
 * @author James Todd [gonzo@eng.sun.com]
 * @author Harish Prabandham
 * @author Costin Manolache
 * @author Ignacio J. Ortega
 *
 */
final class HttpServletRequestFacade implements HttpServletRequest {
    private static StringManager sm =
	StringManager.getManager("org.apache.tomcat.resources");

    private Request request;

    HttpSessionFacade sessionFacade;
    ServletInputStreamFacade isFacade=new ServletInputStreamFacade();
    boolean isFacadeInitialized=false;
    BufferedReader reader=null;
    DateFormat []dateFormats;
    UEncoder uencoder;

    private boolean usingStream = false;
    private boolean usingReader = false;

    private boolean parametersProcessed=false;
    
    /** Not public 
     */
    HttpServletRequestFacade(Request request) {
        this.request = request;
	isFacade.setRequest( request );
	try {
	    // we may create facades more often than requests
	    if( dateFormats==null ) {
		dateFormats=new DateFormat[] {
		    new SimpleDateFormat(DateTool.RFC1123_PATTERN, Locale.US),
		    new SimpleDateFormat(DateTool.rfc1036Pattern, Locale.US),
		    new SimpleDateFormat(DateTool.asctimePattern, Locale.US)
		};
	    }
	    if( uencoder==null ) {
		uencoder=new UEncoder();
		uencoder.addSafeCharacter(';');
		uencoder.addSafeCharacter('/');
		request.setNote( "req.uencoder", uencoder );
	    } 
	} catch( TomcatException ex ) {
	    ex.printStackTrace();
	}

    }

    /** Not public - is called only from FacadeManager on behalf of Request
     */
    void recycle() {
	usingReader=false;
	usingStream=false;
	parametersProcessed=false;
	sessionFacade=null;
	if( isFacade != null ) isFacade.recycle();
	isFacadeInitialized=false;
        reader=null;
    }

    /** Not public - is called only from FacadeManager
     */
    Request getRealRequest() {
	return request;
    }

    /** Not public - is called only from FacadeManager
     */
    void setRequest( Request req ) {
	request=req;
    }
    
    // -------------------- Public facade methods --------------------
    public Object getAttribute(String name) {
	return request.getAttribute(name);
    }

    public Enumeration getAttributeNames() {
	return request.getAttributeNames();
    }

    public void setAttribute(String name, Object value) {
        request.setAttribute(name, value);
    }

    public void removeAttribute(String name) {
	request.removeAttribute(name);
    }
    
    public String getCharacterEncoding() {
	String enc=request.getCharacterEncoding();

	// Source is set if we are sure about the encoding,
	// we've got it from header or session or some
	// well-defined mechanism. No source means the default
	// is used.
	try {
	    Object o=request.getNote( "req.encodingSource" );
	    if( o==null ) return null;
	} catch( TomcatException ex ) {
	    ex.printStackTrace();
	}
	return enc;
    }

    public int getContentLength() {
        return request.getContentLength();
    }

    public String getContentType() {
	return request.getContentType();
    }

    public Cookie[] getCookies() {
	Cookies cookies=request.getCookies();
	int count=cookies.getCookieCount();
	Cookie[] cookieArray = new Cookie[ count ];

	// Convert from ServerCookie to Cookie.
	// The price is payed _only_ by servlets that call getCookie().
	// ( if you don't call it no allocation happens for cookies )
	// ( well, it happens, the code to reuse have to be written )
	for (int i = 0; i < count; i ++) {
	    ServerCookie sC=cookies.getCookie(i);
	    cookieArray[i] = new CookieFacade(sC);
	}

	return cookieArray;
    }

    /** Tomcat Request doesn't deal with header to date conversion.
     *  We delegate this to RequestUtil. ( adapter function )
     */
    public long getDateHeader(String name) {
	String value=request.getHeader( name );
	if( value==null) return -1;

	long date=DateTool.parseDate(value,dateFormats);
	if( date==-1) {
	    String msg = sm.getString("httpDate.pe", value);
	    throw new IllegalArgumentException(msg);
	}
	return date;
    }

    public String getHeader(String name) {
        return request.getHeader(name);
    }

    public Enumeration getHeaders(String name) {
        return request.getHeaders(name);
    }

    public Enumeration getHeaderNames() {
        return request.getHeaderNames();
    }

    /** Adapter: Tomcat Request allows both stream and writer access.
     */
    public ServletInputStream getInputStream() throws IOException {
	if (usingReader) {
	    String msg = sm.getString("reqfac.getinstream.ise");
	    throw new IllegalStateException(msg);
	}
	usingStream = true;

	if( ! isFacadeInitialized ) {
	    isFacade.prepare();
	    isFacadeInitialized=true;
	}
	return isFacade;
    }

    /** Adapter: Tomcat Request doesn't deal with header to int conversion.
     */
    public int getIntHeader(String name)
	throws  NumberFormatException
    {
	String value=request.getHeader( name );
	if( value==null) return -1;
	int valueInt=Integer.parseInt(value);
	return valueInt;
    }
    
    public String getMethod() {
        return request.method().toString();
    }

    /** Adapter: Request doesn't deal with this servlet convention
     */
    public String getParameter(String name) {
	if( ! parametersProcessed ) {
	    request.handleQueryParameters();
	    if( request.method().equals("POST")) {
		request.handlePostParameters();
	    }
	    parametersProcessed=true;
	}
        return request.parameters().getParameter( name );
    }

    public String[] getParameterValues(String name) {
	if( ! parametersProcessed ) {
	    request.handleQueryParameters();
	    if( request.method().equals("POST")) {
		request.handlePostParameters();
	    }
	    parametersProcessed=true;
	}
        return request.parameters().getParameterValues(name);
    }

    public Enumeration getParameterNames() {
	if( ! parametersProcessed ) {
	    request.handleQueryParameters();
	    if( request.method().equals("POST")) {
		request.handlePostParameters();
	    }
	    parametersProcessed=true;
	}
        return request.parameters().getParameterNames();
    }
    
    public String getPathInfo() {
	// DECODED
        return request.pathInfo().toString();
    }

    public String getPathTranslated() {
	// DECODED
	// Servlet 2.2 spec differs from what Apache and
	// all other web servers consider to be PATH_TRANSLATED.
	// It's important not to use CGI PATH_TRANSLATED - this
	// code is specific to servlet 2.2 ( or more )
	String path=getPathInfo();
	if(path==null || "".equals( path ) ) return null;
	String pathTranslated=
	    FileUtil.safePath( request.getContext().getAbsolutePath(),
			       path);
	return pathTranslated;
    }
    
    public String getProtocol() {
        return request.protocol().toString();
    }

    public String getQueryString() {
	// ENCODED. We don't decode the original query string,
	// we we can return the same thing
	String qS=request.queryString().toString();
	if( "".equals(qS) )
	    return null;
	return qS;
    }

    public String getRemoteUser() {
	return request.getRemoteUser();
    }

    public String getScheme() {
        return request.scheme().toString();
    }

    public String getServerName() {
	return request.serverName().toString();
    }

    public int getServerPort() {
        return request.getServerPort();
    }

    /** Adapter: Tomcat Request allows both stream and writer access.
     */
    public BufferedReader getReader() throws IOException {
	if (usingStream) {
	    String msg = sm.getString("reqfac.getreader.ise");
	    throw new IllegalStateException(msg);
	}
	usingReader = true;

	if( reader != null ) return reader; // method already called 

	if( ! isFacadeInitialized ) {
	    isFacade.prepare();
	    isFacadeInitialized=true;
	}

	// XXX  provide recycleable objects
	String encoding = request.getCharacterEncoding();
	
	InputStreamReader r =
            new InputStreamReader(isFacade, encoding);
	reader= new BufferedReader(r);
	return reader;
    }
    
    public String getRemoteAddr() {
        return request.remoteAddr().toString();
    }

    public String getRemoteHost() {
	String remoteHost = request.remoteHost().toString();

        // AJP12 defaults to empty string, AJP13 defaults to null
        if(remoteHost != null && remoteHost.length() != 0)
            return remoteHost;

        try{
            remoteHost = InetAddress.getByName(request.remoteAddr().toString()).getHostName();
        }catch(Exception e){
            // If anything went wrong then fall back to using the remote hosts IP address
            remoteHost = request.remoteAddr().toString();
        }

        return remoteHost;
    }

    public String getRequestURI() {
	// ENCODED
	if( request.unparsedURI().isNull() ) {
	    // unparsed URI is used as a cache.
	    // request.unparsedURI().duplicate( request.requestURI() );
	    String decoded=request.requestURI().toString();
	    // XXX - I'm not sure what encoding should we use - maybe output ?,
	    // since this will probably be used for the output
	    uencoder.setEncoding(request.getCharacterEncoding());
	    String encoded= uencoder.encodeURL( decoded );
	    
	    request.unparsedURI().setString( encoded );
	}
        return request.unparsedURI().toString();
    }

    
    /** Facade: we delegate to the right object ( the context )
     */
    public RequestDispatcher getRequestDispatcher(String path) {
        if (path == null)
	    return null;

	if (! path.startsWith("/")) {
	    // The original implementation returned that RD relative
	    // to lookupPath, which is RequestPath + PathInfo
	    String pI= request.pathInfo().toString();
	    if( pI == null ) 
		path= FileUtil.catPath( request.servletPath().toString(),
					path );
	    else
		path= FileUtil.catPath( request.servletPath().toString() + pI,
					path);
	    if( path==null) return null;
	}

	Context ctx=request.getContext();
	return ((ServletContext)ctx.getFacade()).getRequestDispatcher(path);
    }

    /** Adapter: first elelment
     */
    public Locale getLocale() {
	return (Locale)getLocales().nextElement();
    }

    /** Delegate to RequestUtil
     */
    public Enumeration getLocales() {
	MimeHeaders headers=request.getMimeHeaders();
        return AcceptLanguage.getLocales(headers.getHeader("Accept-Language"));
    }

    /** Delegate to Context
     */
    public String getContextPath() {
	// Should be ENCODED ( in 2.3 ). tomcat4.0 doesn't seem to do that
	// ( it's in fact returning 404 on any encoded context paths ), and
	// is very likely to result in user errors - if anyone expects it to
	// be decoded, as it allways was in 3.x or if anyone will use it as
	// a key.
        return request.getContext().getPath();
    }

    public String getServletPath() {
	// DECODED
        return request.servletPath().toString();
    }

    /**
     * @deprecated
     */
    public String getRealPath(String name) {
	Context ctx=request.getContext();
        return FileUtil.safePath( ctx.getAbsolutePath(),
				  name);
    }
    
    // -------------------- Security --------------------
    public String getAuthType() {
	return request.getAuthType();
    }
    
    public boolean isSecure() {
	return request.isSecure();
    }

    public boolean isUserInRole(String role) {
        // get the servletWrapper...
        ServletHandler handler=(ServletHandler)request.getHandler();
        String realRole=role;
        if ( handler!= null ) {
            // lookup the alias
            String mappedRole = handler.getServletInfo().getSecurityRole(role);
            if ( mappedRole != null ) {
                // use translated role
                realRole = mappedRole;
            }
        }
        return request.isUserInRole(realRole);
    }

    public Principal getUserPrincipal() {
	return request.getUserPrincipal();
    }
    
    // -------------------- Session --------------------

    public HttpSession getSession() {
	return getSession(true);
    }

    /** Create the Facade for session.
     */
    public HttpSession getSession(boolean create) {
	ServerSession realSession = (ServerSession)request.getSession(create);

	// No real session, return null
	if( realSession == null ) {
	    sessionFacade=null;
	    return null;
	}

	
	sessionFacade=(HttpSessionFacade)realSession.getFacade();
	if( sessionFacade==null ) {
	    sessionFacade=new HttpSessionFacade();
	    sessionFacade.setRealSession( realSession );
	    realSession.setFacade( sessionFacade );
	}
        return sessionFacade;
    }

    public String getRequestedSessionId() {
        return request.getRequestedSessionId();
    }
    
    public boolean isRequestedSessionIdValid() {
        boolean isvalid = false;
        ServerSession session = (ServerSession)request.getSession(false);
        if(session != null && session.getId().equals(getRequestedSessionId()))
            isvalid = true;

        return isvalid;
    }

    /** Adapter - Request uses getSessionIdSource
     */
    public boolean isRequestedSessionIdFromCookie() {
	return Request.SESSIONID_FROM_COOKIE.equals( request.getSessionIdSource() );
    }

    /**
     * @deprecated
     */
    public boolean isRequestedSessionIdFromUrl() {
	return isRequestedSessionIdFromURL();
    }

    public boolean isRequestedSessionIdFromURL() {
	return Request.SESSIONID_FROM_URL.equals( request.getSessionIdSource() );
    }

}