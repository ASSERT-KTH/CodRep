RequestDispatcher rd = context.getFacade().getRequestDispatcher(requestURI);

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
import org.apache.tomcat.core.Constants;
import org.apache.tomcat.util.*;
import java.io.*;
import java.net.*;
import java.util.*;
import javax.servlet.http.*;
import javax.servlet.*;


/**
 * Interceptor that loads the "load-on-startup" servlets
 *
 * @author costin@dnt.ro
 */
public class LoadOnStartupInterceptor extends BaseInterceptor {
    private static StringManager sm =StringManager.getManager("org.apache.tomcat.context");
    
    public LoadOnStartupInterceptor() {
    }

    public void contextInit(Context ctx) {
	Hashtable loadableServlets = new Hashtable();
	init(ctx,loadableServlets);
	
	Vector orderedKeys = new Vector();
	Enumeration e=  loadableServlets.keys();
		
	// order keys
	while (e.hasMoreElements()) {
	    Integer key = (Integer)e.nextElement();
	    int slot = -1;
	    for (int i = 0; i < orderedKeys.size(); i++) {
	        if (key.intValue() <
		    ((Integer)(orderedKeys.elementAt(i))).intValue()) {
		    slot = i;
		    break;
		}
	    }
	    if (slot > -1) {
	        orderedKeys.insertElementAt(key, slot);
	    } else {
	        orderedKeys.addElement(key);
	    }
	}

	// loaded ordered servlets

	// Priorities IMO, should start with 0.
	// Only System Servlets should be at 0 and rest of the
	// servlets should be +ve integers.
	// WARNING: Please do not change this without talking to:
	// harishp@eng.sun.com (J2EE impact)

	for (int i = 0; i < orderedKeys.size(); i ++) {
	    Integer key = (Integer)orderedKeys.elementAt(i);
	    Enumeration sOnLevel =  ((Vector)loadableServlets.get( key )).elements();
	    while (sOnLevel.hasMoreElements()) {
		String servletName = (String)sOnLevel.nextElement();
		ServletWrapper  result = ctx.getServletByName(servletName);

		if( ctx.getDebug() > 0 ) ctx.log("Loading " + key + " "  + servletName );
		if(result==null)
		    System.out.println("Warning: we try to load an undefined servlet " + servletName);
		else {
		    try {
			if( result.getPath() != null )
			    loadJsp( ctx, result );
			else
			    result.loadServlet();
		    } catch (Exception ee) {
			String msg = sm.getString("context.loadServlet.e",
						  servletName);
			System.out.println(msg);
		    } 
		}
	    }
	}
    }

    void loadJsp( Context context, ServletWrapper result ) throws Exception {
	// A Jsp initialized in web.xml -

	// Log ( since I never saw this code called, let me know if it does
	// for you )
	System.out.println("Initializing JSP with JspWrapper");
	
	// Ugly code to trick JSPServlet into loading this.

	// XXX XXX XXX
	// core shouldn't depend on a particular connector!
	// need to find out what this code does!
	
	// XXX XXX find a better way !!!
	//	RequestAdapterImpl reqA=new RequestAdapterImpl();
	//	ResponseAdapterImpl resA=new ResponseAdapterImpl();
	String path=result.getPath();
	RequestImpl request = new RequestImpl();
	ResponseImpl response = new ResponseImpl();
	request.setContextManager( context.getContextManager());
	request.recycle();
	response.recycle();
	
	//	request.setRequestAdapter( reqA );
	// response.setResponseAdapter( resA );
	
	request.setResponse(response);
	response.setRequest(request);
	
	String requestURI = path + "?jsp_precompile=true";
	
	request.setRequestURI(context.getPath() + path);
	request.setQueryString( "jsp_precompile=true" );
	
	request.setContext(context);
	request.getSession(true);
	
	RequestDispatcher rd = context.getRequestDispatcher(requestURI);
	
	try {
	    rd.forward(request.getFacade(), response.getFacade());
	} catch (ServletException se) {
	} catch (IOException ioe) {
	}
    }
    // -------------------- 
    // Old logic from Context - probably something cleaner can replace it.

    void init(Context ctx, Hashtable loadableServlets ) {
	Enumeration enum=ctx.getServletNames();
	while(enum.hasMoreElements()) {
	    String name=(String)enum.nextElement();
	    ServletWrapper sw=ctx.getServletByName( name );
	    int i=sw.getLoadOnStartUp();
	    Integer level=new Integer(i);
	    if( i!= 0) {
		Vector v;
		if( loadableServlets.get(level) != null ) 
		    v=(Vector)loadableServlets.get(level);
		else
		    v=new Vector();
		
		v.addElement(name);
		loadableServlets.put(level, v);
	    }
	}
    }
    

}