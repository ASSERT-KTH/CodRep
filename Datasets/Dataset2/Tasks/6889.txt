location = makeAbsolute(req, location);

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


package org.apache.tomcat.context;

import org.apache.tomcat.core.*;
import org.apache.tomcat.request.*;
import org.apache.tomcat.util.*;
import java.io.*;
import java.net.*;
import java.util.*;
import java.security.*;

import org.apache.tomcat.util.log.*;

// don't extend - replace !

/**
 * Handle errors - this is the default handler, you can replace it
 * with customized versions
 *
 * @author Costin Manolache
 */
public final class ErrorHandler extends BaseInterceptor {
    private Context rootContext=null;
    
    public ErrorHandler() {
    }

    public void engineInit( ContextManager cm )
    	throws TomcatException
    {
    }
    
    public void addContext( ContextManager cm, Context ctx)
	throws TomcatException
    {
    }

    /** Add default error handlers
     */
    public void contextInit( Context ctx)
	throws TomcatException
    {
	if( ctx.getHost() == null && ctx.getPath().equals(""))
	    rootContext = ctx;
	ctx.addServlet( new ExceptionHandler());
	ctx.addServlet( new StatusHandler());

	// Default status handlers
	ctx.addServlet( new RedirectHandler());
	ctx.addErrorPage( "302", "tomcat.redirectHandler");
	ctx.addServlet( new NotFoundHandler());
	ctx.addErrorPage( "404", "tomcat.notFoundHandler");
    }

    public int handleError( Request req, Response res, Throwable t ) {
	ContextManager cm=req.getContextManager();
	Context ctx = req.getContext();
	if(ctx==null) {
	    // that happens only if the request can't pass contextMap
	    // hook. The reason for that is a malformed request, or any
	    // other error.
	    ctx=rootContext;
	}

	if( t==null ) {
	    handleStatusImpl( cm, ctx, req, res, res.getStatus() );
	} else {
	    handleErrorImpl( cm, ctx, req, res, t );
	}
	return 200;
    }

    // -------------------- Implementation of handleError
    // Originally in ContextManager.
    
    private final void handleStatusImpl( ContextManager cm, Context ctx,
					 Request req, Response res,
					 int code )
    {
	String errorPath=null;
	Handler errorServlet=null;

	// don't log normal cases ( redirect and need_auth ), they are not
	// error
	// XXX this log was intended to debug the status code generation.
	// it can be removed for all cases.
	if( code != 302 && code != 401 && code!=400  ) // tuneme
	    ctx.log( "Status code:" + code + " request:"  + req + " msg:" +
		     req.getAttribute("javax.servlet.error.message"));
	
	errorPath = ctx.getErrorPage( code );
	if( errorPath != null ) {
	    errorServlet=getHandlerForPath( cm, ctx, errorPath );

	    // Make sure Jsps will work
	    req.setAttribute( "javax.servlet.include.request_uri",
				  ctx.getPath()  + "/" + errorPath );
	    req.setAttribute( "javax.servlet.include.servlet_path", errorPath );
	}

	boolean isDefaultHandler = false;
	if( errorServlet==null ) {
	    errorServlet=ctx.getServletByName( "tomcat.statusHandler");
	    isDefaultHandler = true;
	}

	if (errorServlet == null) {
	    ctx.log( "Handler errorServlet is null! errorPath:" + errorPath);
	    return;
	}

	if (!isDefaultHandler)
	    res.resetBuffer();

	req.setAttribute("javax.servlet.error.status_code",new Integer( code));
	req.setAttribute("tomcat.servlet.error.request", req);

	if( debug>0 )
	    ctx.log( "Handler " + errorServlet + " " + errorPath);

	errorServlet.service( req, res );
    }

    // XXX XXX Security - we should log the message, but nothing
    // should show up  to the user - it gives up information
    // about the internal system !
    // Developers can/should use the logs !!!

    /** General error handling mechanism. It will try to find an error handler
     * or use the default handler.
     */
    void handleErrorImpl( ContextManager cm, Context ctx,
			  Request req, Response res , Throwable t  )
    {
	/** The exception must be available to the user.
	    Note that it is _WRONG_ to send the trace back to
	    the client. AFAIK the trace is the _best_ debugger.
	*/
	if( t instanceof IllegalStateException ) {
	    ctx.log("IllegalStateException in " + req, t);
	    // Nothing special in jasper exception treatement, no deps
	    //} else if( t instanceof org.apache.jasper.JasperException ) {
	    // 	    ctx.log("JasperException in " + req, t);
	} else if( t instanceof IOException ) {
            if( "Broken pipe".equals(t.getMessage()))
	    {
		ctx.log("Broken pipe in " + req, t, Logger.DEBUG);  // tuneme
		return;
	    }
            if( "Connection reset by peer".equals(t.getMessage()))
	    {
		ctx.log("Connection reset by peer in " + req, t, Logger.DEBUG);  // tuneme
		return;
	    }

	    ctx.log("IOException in " + req, t );
	} else {
	    ctx.log("Exception in " + req , t );
	}

	if(null!=req.getAttribute("tomcat.servlet.error.defaultHandler")){
	    // we are in handleRequest for the "default" error handler
	    log("ERROR: can't find default error handler, or error in default error page", t);
	}

	String errorPath=null;
	Handler errorServlet=null;

	// Scan the exception's inheritance tree looking for a rule
	// that this type of exception should be forwarded
	Class clazz = t.getClass();
	while (errorPath == null && clazz != null) {
	    String name = clazz.getName();
	    errorPath = ctx.getErrorPage(name);
	    clazz = clazz.getSuperclass();
	}

	if( errorPath != null ) {
	    errorServlet=getHandlerForPath( cm, ctx, errorPath );

	    // Make sure Jsps will work
	    req.setAttribute( "javax.servlet.include.request_uri",
				  ctx.getPath()  + "/" + errorPath );
	    req.setAttribute( "javax.servlet.include.servlet_path", errorPath );
	}

	boolean isDefaultHandler = false;
	if ( errorLoop( ctx, req ) ){
                return;
        }
        if ( errorServlet==null) {
	    errorServlet = ctx.getServletByName("tomcat.exceptionHandler");
	    isDefaultHandler = true;
	}

	if (errorServlet == null) {
	    ctx.log( "Handler errorServlet is null! errorPath:" + errorPath);
	    return;
	}

	if (!isDefaultHandler)
	    res.resetBuffer();

	req.setAttribute("javax.servlet.error.exception_type", t.getClass());
	req.setAttribute("javax.servlet.error.message", t.getMessage());
	req.setAttribute("tomcat.servlet.error.throwable", t);
	req.setAttribute("tomcat.servlet.error.request", req);

	if( debug>0 )
	    ctx.log( "Handler " + errorServlet + " " + errorPath);

	errorServlet.service( req, res );
    }

    public final Handler getHandlerForPath( ContextManager cm,
					    Context ctx, String path ) {
	if( ! path.startsWith( "/" ) ) {
	    return ctx.getServletByName( path );
	}
	Request req1=new Request();
	Response res1=new Response();
	cm.initRequest( req1, res1 );

	req1.requestURI().setString( ctx.getPath() + path );
	cm.processRequest( req1 );
	return req1.getHandler();
    }

    /** Handle the case of error handler generating an error or special status
     */
    private boolean errorLoop( Context ctx, Request req ) {
	if( req.getAttribute("javax.servlet.error.status_code") != null
	    || req.getAttribute("javax.servlet.error.exception_type")!=null) {

	    if( ctx.getDebug() > 0 )
		ctx.log( "Error: exception inside exception servlet " +
			 req.getAttribute("javax.servlet.error.status_code") +
			 " " + req.
			 getAttribute("javax.servlet.error.exception_type"));

	    return true;
	}
	return false;
    }



    
}

class NotFoundHandler extends Handler {
    static StringManager sm=StringManager.
	getManager("org.apache.tomcat.resources");
    int sbNote=0;
    
    NotFoundHandler() {
	initialized=true;
	internal=true;
	name="tomcat.notFoundHandler";
    }

    public void doService(Request req, Response res)
	throws Exception
    {
	res.setContentType("text/html");	// ISO-8859-1 default

	String requestURI = (String)req.
	    getAttribute("javax.servlet.include.request_uri");

	if (requestURI == null) {
	    requestURI = req.requestURI().toString();
	}

	if( sbNote==0 ) {
	    sbNote=req.getContextManager().getNoteId(ContextManager.REQUEST_NOTE,
						     "NotFoundHandler.buff");
	}

	// we can recycle it because
	// we don't call toString();
	StringBuffer buf=(StringBuffer)req.getNote( sbNote );
	if( buf==null ) {
	    buf = new StringBuffer();
	    req.setNote( sbNote, buf );
	}
	
	buf.append("<head><title>")
	    .append(sm.getString("defaulterrorpage.notfound404"))
	    .append("</title></head>\r\n");
	buf.append("<body><h1>")
	    .append(sm.getString("defaulterrorpage.notfound404"))
	    .append("</h1>\r\n");
	buf.append(sm.getString("defaulterrorpage.originalrequest"))
	    .append( requestURI );
	buf.append("</body>\r\n");

	res.setContentLength(buf.length());

	res.getBuffer().write( buf );
	buf.setLength(0);
    }
}

class ExceptionHandler extends Handler {
    static StringManager sm=StringManager.
	getManager("org.apache.tomcat.resources");
    int sbNote=0;

    ExceptionHandler() {
	initialized=true;
	internal=true;
	name="tomcat.exceptionHandler";
    }

    public void doService(Request req, Response res)
	throws Exception
    {
	String msg=(String)req.getAttribute("javax.servlet.error.message");
	
	Throwable e= (Throwable)req.
	    getAttribute("tomcat.servlet.error.throwable");
	if( e==null ) {
	    log("Exception handler called without an exception", new Throwable("trace"));
	    return;
	}

	res.setContentType("text/html");
	res.setStatus( 500 );
	
	if( sbNote==0 ) {
	    sbNote=req.getContextManager().getNoteId(ContextManager.REQUEST_NOTE,
						     "ExceptionHandler.buff");
	}

	// we can recycle it because
	// we don't call toString();
	StringBuffer buf=(StringBuffer)req.getNote( sbNote );
	if( buf==null ) {
	    buf = new StringBuffer();
	    req.setNote( sbNote, buf );
	}
	buf.append("<h1>");
	if( res.isIncluded() ) {
	    buf.append(sm.getString("defaulterrorpage.includedservlet") ).
		append(" ");
	}  else {
	    buf.append("Error: ");
	}
	
	buf.append( 500 );
	buf.append("</h1>\r\n");

	// More info - where it happended"
	buf.append("<h2>")
	    .append(sm.getString("defaulterrorpage.location"))
	    .append(req.requestURI().toString())
	    .append("</h2>");

	buf.append("<b>")
	    .append(sm.getString("defaulterrorpage.internalservleterror"))
	    .append("</b><br>");

        buf.append("<pre>");
	// prints nested exceptions too, including SQLExceptions, recursively
	String trace = Logger.throwableToString
	    (e,	"<b>" + sm.getString("defaulterrorpage.rootcause") + "</b>");
	buf.append(trace);

	buf.append("</pre>\r\n");
	
	buf.append("\r\n");
	
	res.getBuffer().write( buf );
	buf.setLength(0);
    }
}

class StatusHandler extends Handler {
    static StringManager sm=StringManager.
	getManager("org.apache.tomcat.resources");
    int sbNote=0;

    StatusHandler() {
	initialized=true;
	internal=true;
	name="tomcat.statusHandler";
    }
    
    // We don't want interceptors called for redirect
    // handler
    public void doService(Request req, Response res)
	throws Exception
    {
	String msg=(String)req.getAttribute("javax.servlet.error.message");
	
	res.setContentType("text/html");
	// res is reset !!!
	// status is already set
	int sc=res.getStatus();
	
	if( sbNote==0 ) {
	    sbNote=req.getContextManager().getNoteId(ContextManager.REQUEST_NOTE,
						     "StatusHandler.buff");
	}

	// we can recycle it because
	// we don't call toString();
	StringBuffer buf=(StringBuffer)req.getNote( sbNote );
	if( buf==null ) {
	    buf = new StringBuffer();
	    req.setNote( sbNote, buf );
	}
	buf.append("<h1>");
	if( res.isIncluded() ) {
	    buf.append(sm.getString("defaulterrorpage.includedservlet") );
	}  else {
	    buf.append("Error: ");
	}
	
	buf.append( sc );
	buf.append("</h1>\r\n");

	// More info - where it happended"
	buf.append("<h2>")
	    .append(sm.getString("defaulterrorpage.location"))
	    .append(req.requestURI().toString())
	    .append("</h2>");

	buf.append("<b>")
	    .append(msg)
	    .append("</b><br>");

	res.setContentLength(buf.length());
	res.getBuffer().write( buf );
	buf.setLength(0);
    }
}
	
class RedirectHandler extends Handler {
    static StringManager sm=StringManager.
	getManager("org.apache.tomcat.resources");
    int sbNote=0;

    RedirectHandler() {
	initialized=true;
	internal=true;
	name="tomcat.redirectHandler";
    }

    // We don't want interceptors called for redirect
    // handler
    public void doService(Request req, Response res)
	throws Exception
    {
	String location	= (String)
	    req.getAttribute("javax.servlet.error.message");
	Context ctx=req.getContext();
	
	//location = makeAbsolute(req, location);

	if( debug>0) ctx.log("Redirect " + location + " " + req );

	res.setContentType("text/html");	// ISO-8859-1 default
	res.setHeader("Location", location);

	if( sbNote==0 ) {
	    sbNote=req.getContextManager().getNoteId(ContextManager.REQUEST_NOTE,
						     "RedirectHandler.buff");
	}

	// we can recycle it because
	// we don't call toString();
	StringBuffer buf=(StringBuffer)req.getNote( sbNote );
	if( buf==null ) {
	    buf = new StringBuffer();
	    req.setNote( sbNote, buf );
	}
	buf.append("<head><title>").
	    append(sm.getString("defaulterrorpage.documentmoved")).
	    append("</title></head>\r\n<body><h1>").
	    append(sm.getString("defaulterrorpage.documentmoved")).
	    append("</h1>\r\n").
	    append(sm.getString("defaulterrorpage.thisdocumenthasmoved")).
	    append(" <a href=\"").
	    append(location).
	    append("\">here</a>.<p>\r\n</body>\r\n");

	res.setContentLength(buf.length());
	res.getBuffer().write( buf );
	buf.setLength(0);

    }

    // XXX Move it to URLUtil !!!
    private String makeAbsolute(Request req, String location) {
        URL url = null;
        try {
	    // Try making a URL out of the location
	    // Throws an exception if the location is relative
            url = new URL(location);
	} catch (MalformedURLException e) {
	    String requrl = getRequestURL(req);
	    try {
	        url = new URL(new URL(requrl), location);
	    }
	    catch (MalformedURLException ignored) {
	        // Give up
	        return location;
	    }
	}
        return url.toString();
    }

    static String getRequestURL( Request req )  {
 	StringBuffer url = new StringBuffer ();
	String scheme = req.scheme().toString();
	int port = req.getServerPort ();
	String urlPath = req.requestURI().toString();
	
	url.append (scheme);		// http, https
	url.append ("://");
	url.append (req.getServerName ());
	if ((scheme.equals ("http") && port != 80)
		|| (scheme.equals ("https") && port != 443)) {
	    url.append (':');
	    url.append (req.getServerPort ());
	}
	url.append(urlPath);
	return url.toString();
    }
}