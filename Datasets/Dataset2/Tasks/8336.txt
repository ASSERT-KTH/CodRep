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
import org.apache.tomcat.util.*;
import org.apache.tomcat.logging.*;
import java.io.*;
import java.net.*;
import java.util.*;

/**
 * Interceptor that loads the "load-on-startup" servlets
 *
 * @author costin@dnt.ro
 */
public class LoadOnStartupInterceptor extends BaseInterceptor {
    private static StringManager sm =
	StringManager.getManager("org.apache.tomcat.resources");
    
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
		Handler result = ctx.getServletByName(servletName);

		if( ctx.getDebug() > 0 ) ctx.log("Loading " + key + " "  + servletName );
		if(result==null)
		    log("Warning: we try to load an undefined servlet " + servletName, Logger.WARNING);
		else {
		    try {
			if( result.getPath() != null )
			    loadJsp( ctx, result );
			else {
			    result.init();
			}
		    } catch (Exception ee) {
			String msg = sm.getString("context.loadServlet.e",
						  servletName);
			log(msg, ee);
		    } 
		}
	    }
	}
    }

    void loadJsp( Context context, Handler result ) throws Exception {
	// A Jsp initialized in web.xml -

	// Log ( since I never saw this code called, let me know if it does
	// for you )
	log("Initializing JSP with JspWrapper");
	
	// Ugly code to trick JSPServlet into loading this.
	ContextManager cm=context.getContextManager();
	String path=result.getPath();
	Request request = new Request();
	Response response = new Response();
	request.recycle();
	response.recycle();
	cm.initRequest(request,response);
	
	String requestURI = path + "?jsp_precompile=true";
	
	request.setRequestURI(context.getPath() + path);
	request.setQueryString( "jsp_precompile=true" );
	
	request.setContext(context);

	cm.service( request, response );
    }
    // -------------------- 
    // Old logic from Context - probably something cleaner can replace it.

    void init(Context ctx, Hashtable loadableServlets ) {
	Enumeration enum=ctx.getServletNames();
	while(enum.hasMoreElements()) {
	    String name=(String)enum.nextElement();
	    Handler sw= ctx.getServletByName( name );
	    if( sw.getLoadingOnStartUp() ) {
		Integer level=new Integer(sw.getLoadOnStartUp());
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