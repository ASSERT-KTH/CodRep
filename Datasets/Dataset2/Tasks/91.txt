if( removed==null) removed=new Vector();

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

import org.apache.tomcat.util.*;
import org.apache.tomcat.core.*;
import java.io.*;
import java.net.*;
import java.security.*;
import java.util.*;
import javax.servlet.*;
import javax.servlet.http.*;

/**
 *   Control class for facades - this is the only "gate" between servlets
 *   and tomcat.
 *
 *   This is an important security component, shouldn't be used for
 *   anything else. Please keep all the code short and clean - and review
 *   everything very often.
 *  
 */
public final class Servlet22Interceptor
    extends BaseInterceptor
{
    public static final String SERVLET_STAMP = " ( JSP 1.1; Servlet 2.2 )";
	
    public Servlet22Interceptor() {
    }

    public Servlet22Interceptor(Context ctx) {
    }

    // -------------------- implementation
    private void setEngineHeader(Context ctx) {
        String engineHeader=ctx.getEngineHeader();

	// EngineHeader can be set as a Context Property!
	if( engineHeader==null) {
	    StringBuffer sb=new StringBuffer();
	    sb.append(ContextManager.TOMCAT_NAME);
	    sb.append("/");
	    sb.append(ContextManager.TOMCAT_VERSION );
	    sb.append(SERVLET_STAMP);
	    engineHeader=sb.toString();
	}
	ctx.setEngineHeader( engineHeader );
    }

    /** Call servlet.destroy() for all servlets, as required
	by the spec
    */
    public void contextShutdown( Context ctx )
	throws TomcatException
    {
	// shut down and servlets
	Enumeration enum = ctx.getServletNames();
	while (enum.hasMoreElements()) {
	    String key = (String)enum.nextElement();
	    Handler wrapper = ctx.getServletByName( key );
	    
	    if( ! (wrapper instanceof ServletHandler) ) 
		continue;

	    try {
		((ServletHandler)wrapper).destroy();
	    } catch(Exception ex ) {
		ctx.log( "Error in destroy ", ex);
	    }
	    // remove the context after it is destroyed.
	    // remove will "un-declare" the servlet
	    // After this the servlet will be in STATE_NEW, and can
	    // be reused.
	    ctx.removeServletByName( key );
	}
    }
    
    public void addContext( ContextManager cm, Context ctx )
	throws TomcatException
    {
	ctx.setFacade(new ServletContextFacade(cm , ctx));
	setEngineHeader( ctx );
    }

    public void addContainer( Container ct )
    	throws TomcatException
    {
	String hN=ct.getHandlerName();
	if( hN == null ) return;
			     
	if( ct.getHandler() == null ) {
	    // we have a container with a valid handler name but without
	    // a Handler. Create a ServletWrapper
	    ServletHandler handler=new ServletHandler();
	    handler.setServletClassName( hN );
	    handler.setName( hN );
	    handler.setContext( ct.getContext() );
	    // *.jsp -> jsp is a legacy default mapping  
	    if(debug>0 &&  ! "jsp".equals(hN) ) {
		log( "Create handler " + hN);
	    }
	    handler.setModule( this );
	    ct.setHandler(handler);
	    ct.getContext().addServlet( handler );
	}
	    
    }


    /** Call the Servlet22 callbacks when session expires.
     */
    public int sessionState( Request req, ServerSession sess, int newState)
    {
	if( newState==ServerSession.STATE_SUSPEND ||
	    newState==ServerSession.STATE_EXPIRED )   {
	    
	    // generate "unbould" events when the session is suspended or
	    // expired
	    HttpSession httpSess=(HttpSession)sess.getFacade();

	    Vector removed=null; // lazy 
	    Enumeration e = sess.getAttributeNames();
	    // announce all values with listener that we'll remove them
	    while( e.hasMoreElements() )   {
		String key = (String) e.nextElement();
		Object value = sess.getAttribute(key);

		if( value instanceof  HttpSessionBindingListener) {
		    ((HttpSessionBindingListener) value).valueUnbound
			(new HttpSessionBindingEvent(httpSess , key));
		    if( removed=null) removed=new Vector();
		    removed.addElement( key );
		}
	    }
	    if( removed!=null ) {
		// remove
		e=removed.elements();
		while( e.hasMoreElements() ) {
		    String key = (String) e.nextElement();
		    sess.removeAttribute( key );
		}
	    }
	} 
	return 0;
    }

    
    public int postRequest(Request rreq, Response rres ) {
	//if( rreq.getContext() != ctx ) return; // throw

	//	log( "Recycling " + rreq );
	HttpServletRequest req=(HttpServletRequest)rreq.getFacade();
	if( ! (req instanceof HttpServletRequestFacade))
	    return 0;
	
	((HttpServletRequestFacade)req).recycle();

	// recycle response
	//	Response rres=rreq.getResponse();
	if( rres== null )
	    return 0;
	
	HttpServletResponse res=(HttpServletResponse)rres.getFacade();
	if( res!=null) ((HttpServletResponseFacade)res).recycle();

	// recycle output stream
	// XXX XXX implement it

	return 0;
    }
}
    