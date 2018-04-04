//	    sw.setServletClass( servletName );

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
package org.apache.tomcat.request;

import org.apache.tomcat.util.*;
import org.apache.tomcat.core.*;
import java.io.IOException;
import java.io.PrintWriter;

/**
 *
 *
 * @author James Duncan Davidson [duncan@eng.sun.com]
 * @author Jason Hunter [jch@eng.sun.com]
 * @author James Todd [gonzo@eng.sun.com]
 * @author Costin Manolache
 */
public class InvokerInterceptor extends BaseInterceptor {

    String prefix="/servlet/";
    int prefixLen=prefix.length();

    public int requestMap(Request req) {
	// If we have an explicit mapper - return
	Container ct=req.getContainer();

	// 	log( "Ct: " + ct.getHandler() + " " +
	// 	     ct.getPath() + " " + ct.getMapType());
	
	if(  req.getHandler()!=null &&
	     ct!=null &&
	     ct.getMapType() != Container.DEFAULT_MAP )
	    return 0;
	
	// default servlet / container
	
	// if doesn't starts with /servlet - return
	String pathInfo = req.getPathInfo();
	String servletPath=req.getServletPath();
	
	// Now we need to fix path info and servlet path
	if( servletPath == null ||
	    ! servletPath.startsWith( prefix ))
	    return 0;

	Context ctx=req.getContext();
	// Set the wrapper, and add a new mapping - next time
	// we'll not have to do that ( the simple mapper is
	// supposed to be faster )
	
	String servletName = null;
	String newPathInfo = null;
	
	if( debug>0 )
	    log( "Original ServletPath=" +servletPath +
		 " PathInfo=" + pathInfo);

	int secondSlash=servletPath.indexOf("/", prefixLen );
	if ( secondSlash > -1) {
	    servletName = servletPath.substring(prefixLen, secondSlash );
	    newPathInfo = servletPath.substring( secondSlash );
	} else {
	    servletName = servletPath.substring( prefixLen );
	}
	
	String newServletPath = prefix + servletName;

	if( debug > 0)
	    log( "After pathfix SN=" + servletName +
		 " SP=" + newServletPath +
		 " PI=" + newPathInfo);
	
 	req.setServletPath(newServletPath);
	req.setPathInfo(newPathInfo);
	
	Handler wrapper = ctx.getServletByName(servletName);
	if (wrapper != null) {
	    req.setHandler( wrapper );
	    return 0;
	}
	    
	// Dynamic add for the wrapper
	
	// even if the server doesn't supports dynamic mappings,
	// we'll avoid the interceptor for include() and
	// it's a much cleaner way to construct the servlet and
	// make sure all interceptors are up to date.
	try {
	    ctx.addServletMapping( newServletPath + "/*" ,
				   servletName );
	    // The facade should create the servlet name
	    
	    Handler sw=ctx.getServletByName( servletName );
	    // 	    sw.setContext(ctx);
	    // 	    sw.setServletName(servletName);
	    //	    ctx.addServlet( sw );
	    sw.setServletClass( servletName );
	    sw.setOrigin( Handler.ORIGIN_INVOKER );
	    wrapper=sw;

	    if( debug > 0)
		log( "Added mapping " + wrapper +
		     " path=" + newServletPath + "/*" );
	} catch( TomcatException ex ) {
	    loghelper.log("dynamically adding wrapper for " + servletName, ex);
	    return 404;
	}

	req.setHandler( wrapper );
	return 0;
    }
    

}