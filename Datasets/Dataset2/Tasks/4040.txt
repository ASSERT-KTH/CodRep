wrapper.service(realRequest, realResponse);

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
import org.apache.tomcat.facade.*;
import org.apache.tomcat.core.Constants;
import java.io.IOException;
import java.io.PrintWriter;
import javax.servlet.ServletException;
import javax.servlet.ServletOutputStream;
import javax.servlet.UnavailableException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

/**
 *
 *
 * @author James Duncan Davidson [duncan@eng.sun.com]
 * @author Jason Hunter [jch@eng.sun.com]
 * @author James Todd [gonzo@eng.sun.com]
 */
public class InvokerServlet extends TomcatInternalServlet {
    private Context context;
    
    public void init() throws ServletException {
        context = facadeM.getRealContext( getServletContext());
    }
    
    public void service(HttpServletRequest request,HttpServletResponse response)
	throws ServletException, IOException
    {
        String requestURI = request.getRequestURI();
	String includedRequestURI = (String)request.getAttribute("javax.servlet.include.request_uri");
	boolean inInclude = (includedRequestURI != null);

	// it's possible to have include.pathInfo==null and getPathInfo()!= null
	String pathInfo;
	if( inInclude)
	    pathInfo = (String)request.getAttribute("javax.servlet.include.path_info");
	else
	    pathInfo = request.getPathInfo();

	String servletPath;
	if( inInclude )
	    servletPath=(String)request.getAttribute("javax.servlet.include.servlet_path");
	else
	    servletPath=request.getServletPath();
	
        if (pathInfo == null || !pathInfo.startsWith("/") ||  pathInfo.length() < 3) {
	    // theres not enough information here to invoke a servlet
	    response.sendError(404, "Not enough information " + request.getRequestURI() + " " + pathInfo);
            return;
	}
	
        // XXX
        // yet another example of substring overkill -- we can do
        // this better....
	int piLen=pathInfo.length();
	String servletName = pathInfo.substring(1, piLen );

	if (servletName.indexOf("/") > -1) {
	    servletName = servletName.substring(0, servletName.indexOf("/"));
	}
	
	String newServletPath = servletPath + "/" + servletName;
	
	String newPathInfo;
	int sNLen=servletName.length();
	if( piLen > sNLen +1 )
	    newPathInfo= pathInfo.substring(sNLen + 1 );
	else
	    newPathInfo=null;

	/*
	  String newPathInfo = "";
	  // XXX XXX I think it's wrong inInclude..
	  if (inInclude) {
	  newPathInfo = includedRequestURI.substring(
	  newServletPath.length(),
	  includedRequestURI.length());
	  } else {
	  newPathInfo = requestURI.substring(
	  context.getPath().length() +
	  newServletPath.length(),
	  requestURI.length());
	  }
	*/
	    
	// RequestURI doesn't include QUERY - no need for that
	/* int i = newPathInfo.indexOf("?");
	   if (i > -1) {
	   newPathInfo = newPathInfo.substring(0, i);
	   }
	*/

        // try the easy one -- lookup by name
	if( context == null ) {
	    System.out.println("Servlet called before init. Need to keep it disabled, sync at startup");
	    return;
	}
        ServletWrapper wrapper = context.getServletByName(servletName);

        if (wrapper == null) {
	    // XXX Check if the wrapper is valid -
	    
	    
	    // even if the server doesn't supports dynamic mappings,
	    // we'll avoid the interceptor for include() and
	    // it's a much cleaner way to construct the servlet and
	    // make sure all interceptors are up to date.
	    try {
		context.addServletMapping( newServletPath + "/*" , servletName );
		wrapper = context.getServletByName( servletName);
		wrapper.setOrigin( ServletWrapper.ORIGIN_INVOKER );
	    } catch( TomcatException ex ) {
		ex.printStackTrace();
		response.sendError(505, "Error getting the servlet " + ex);
		return;
	    }

	    /* Original code - rollback if anything is broken ( it shouldn't )
	       // Moved loadServlet here //loadServlet(servletName);
	       wrapper = new ServletWrapper();
	       wrapper.setContext(context);
	       wrapper.setServletClass(servletName);
	       wrapper.setServletName(servletName); // XXX it can create a conflict !
	       
	       try {
	       context.addServlet( wrapper );
	       } catch(TomcatException ex ) {
	       ex.printStackTrace();
	       }
	    */
        }

	if( context.getDebug() > 3 ) context.log( "Invoker-based execution " + newServletPath + " " + newPathInfo );
	Request realRequest = facadeM.getRealRequest( request );
	Response realResponse = realRequest.getResponse();

	if (! inInclude) {
	    realRequest.setServletPath(newServletPath);
	    realRequest.setPathInfo(newPathInfo);
	} else {
	    realRequest.setAttribute("javax.servlet.include.servlet_path",
				     newServletPath);
	    if (newPathInfo != null) {
		realRequest.setAttribute("javax.servlet.include.path_info",
					 newPathInfo);
	    } else {
		realRequest.removeAttribute("javax.servlet.include.path_info");
	    }
	}

        wrapper.handleRequest(realRequest, realResponse);

	// restore servletPath and pathInfo.
	// Usefull because we may include with the same request multiple times.
	// 
	if (!inInclude) {
	    realRequest.setServletPath( servletPath);
	    realRequest.setPathInfo( pathInfo);
	} else {
	    realRequest.setAttribute("javax.servlet.include.servlet_path",
				     servletPath);
	    
	    if (pathInfo != null) {
		realRequest.setAttribute("javax.servlet.include.path_info",
					 pathInfo);
	    } else {
		realRequest.removeAttribute("javax.servlet.include.path_info");
	    }
	}
    }

    
}