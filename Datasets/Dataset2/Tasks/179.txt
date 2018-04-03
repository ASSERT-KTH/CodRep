import org.apache.tomcat.util.log.*;

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

import org.apache.tomcat.logging.*;

/**
 * Check ContextManager and set defaults for non-set properties
 *
 * @author costin@dnt.ro
 */
public class DefaultCMSetter extends BaseInterceptor {

    public DefaultCMSetter() {
    }

    public void contextInit( Context ctx)
	throws TomcatException
    {
	ctx.addServlet( new ExceptionHandler());
	ctx.addServlet( new StatusHandler());

	// Default status handlers
	ctx.addServlet( new RedirectHandler());
	ctx.addErrorPage( "302", "tomcat.redirectHandler");
	ctx.addServlet( new NotFoundHandler());
	ctx.addErrorPage( "404", "tomcat.notFoundHandler");
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
	    requestURI = req.getRequestURI();
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
	    .append(req.getRequestURI())
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
	    .append(req.getRequestURI())
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
	
	location = makeAbsolute(req, location);

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
	String scheme = req.getScheme ();
	int port = req.getServerPort ();
	String urlPath = req.getRequestURI();
	
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