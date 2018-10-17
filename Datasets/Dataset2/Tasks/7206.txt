if( "EXPERIMENTAL_FORM".equals( ctx.getAuthMethod() )) {

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


package org.apache.tomcat.servlets;

import org.apache.tomcat.util.*;
import org.apache.tomcat.core.*;
import java.io.*;
import javax.servlet.*;
import javax.servlet.http.*;


/**
 * Will authenticate the request for non-form auth
 * ( sort of "default form auth" );
 *
 */
public class AuthServlet extends HttpServlet {
    
    public void service(HttpServletRequest request,
			HttpServletResponse response)
	throws ServletException, IOException
    {
	Request req=((HttpServletRequestFacade)request).getRealRequest();
	Context ctx=req.getContext();
	String realm=ctx.getRealmName();
	if( "FORM".equals( ctx.getAuthMethod() )) {
	    // the code is not uglier that the spec, we are just implementing it.
	    // if you don't understand what's here - you're not alone !
	    // ( it helps to  read the spec > 10 times !)

	    String page=ctx.getFormLoginPage();
	    if(page!=null) {
		HttpSession session=request.getSession( true );
		// Because of _stupid_ "j_security_check" we have
		// to start the session ( since login page migh not do it ),
		// then save the current page ( since we'll have to return here
		// and the obvious  solution is too ... simple, and we need to
		// do something realy complex ).

		// We can't forward to the page - because we set some headers in getSession
		// 		RequestDispatcher rd= ctx.getRequestDispatcher( page );
		// 		rd.include( request, response );

		session.setAttribute( "tomcat.auth.originalLocation", req.getRequestURI());
		if( ctx.getDebug() > 0 ) ctx.log("Setting orig location " + req.getRequestURI());
		if( ! page.startsWith("/")) page="/" + page;
		response.sendRedirect( ctx.getPath() + page );
		return; 
	    }
	}

	// Default is BASIC
	if(realm==null) realm="default";
	response.setHeader( "WWW-Authenticate",
			    "Basic realm=\"" + realm + "\"");
	response.sendError(HttpServletResponse.SC_UNAUTHORIZED);
    }

}