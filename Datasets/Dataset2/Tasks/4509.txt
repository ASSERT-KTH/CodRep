Enumeration levels = ctx.getInitLevels();

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
import org.apache.tomcat.deployment.*;
import java.io.*;
import java.net.*;
import java.util.*;
import javax.servlet.http.*;


/**
 * Will configure the context using the default web.xml
 *
 * @author costin@dnt.ro
 */
public class WebXmlInterceptor {
    private static StringManager sm =StringManager.getManager("org.apache.tomcat.core");
    
    public WebXmlInterceptor() {
    }
	
    public int handleContextInit(Context ctx) {
	// process base configuration
	try {
	    Class webApplicationDescriptor = Class.forName(
	        "org.apache.tomcat.deployment.WebApplicationDescriptor");
	    InputStream is =
	        webApplicationDescriptor.getResourceAsStream(
	            org.apache.tomcat.deployment.Constants.ConfigFile);
	    String msg = sm.getString("context.getConfig.msg", "default");

    	    System.out.println(msg);

	    processWebApp(ctx, is, true);
	} catch (Exception e) {
	    String msg = sm.getString("context.getConfig.e", "default");
	    System.out.println(msg);
	}

	// process webApp configuration

	String s = ctx.getDocumentBase().toString();
	if (ctx.getDocumentBase().getProtocol().equalsIgnoreCase("war")) {
	    if (s.endsWith("/")) {
	        s = s.substring(0, s.length() - 1);
	    }

	    s += "!/";
	}

	URL webURL = null;
	try {
	    webURL = new URL(s + Constants.Context.ConfigFile);

	    InputStream is = webURL.openConnection().getInputStream();
	    String msg = sm.getString("context.getConfig.msg",
				      webURL.toString());

	    System.out.println(msg);
	    
	    processWebApp(ctx, is, false);
	} catch (Exception e) {
	    String msg = sm.getString("context.getConfig.e",
	        (webURL != null) ? webURL.toString() : "not available");

            // go silent on this one
	    // System.out.println(msg);
	}
	return 0;
    }


    private void processWebApp(Context ctx, InputStream is, boolean internal) {
        if (is != null) {
	    try {
	        WebApplicationDescriptor webDescriptor =
		    (new WebApplicationReader()).getDescriptor(is,
		        new WebDescriptorFactoryImpl(),
			ctx.isWARValidated());

		ctx.setDescription( webDescriptor.getDescription());
		ctx.setDistributable( webDescriptor.isDistributable());

		Enumeration contextParameters=webDescriptor.getContextParameters();
		while (contextParameters.hasMoreElements()) {
		    ContextParameter contextParameter =
			(ContextParameter)contextParameters.nextElement();
		    ctx.setInitParameter(contextParameter.getName(),
					 contextParameter.getValue());
		}
		ctx.setSessionTimeOut( webDescriptor.getSessionTimeout());

		processServlets(ctx, webDescriptor.getWebComponentDescriptors());
		processMimeMaps(ctx, webDescriptor.getMimeMappings());
		processWelcomeFiles(ctx, webDescriptor.getWelcomeFiles(),
				    internal);
		processErrorPages(ctx, webDescriptor.getErrorPageDescriptors());
	    } catch (Throwable e) {
                String msg = "config parse: " + e.getMessage();

                System.out.println(msg);
	    }
	}
    }

    private void processServlets(Context ctx, Enumeration servlets) {
        // XXX
        // oh my ... this has suddenly turned rather ugly
        // perhaps the reader should do this normalization work

        while (servlets.hasMoreElements()) {
	    WebComponentDescriptor webComponentDescriptor =
	        (WebComponentDescriptor)servlets.nextElement();
	    String name = webComponentDescriptor.getCanonicalName();
	    String description = webComponentDescriptor.getDescription();
	    String resourceName = null;
	    boolean removeResource = false;

	    if (webComponentDescriptor instanceof ServletDescriptor) {
		resourceName =
		    ((ServletDescriptor)webComponentDescriptor).getClassName();

		if ( ctx.containsServletByName(name)) {
		    String msg = sm.getString("context.dd.dropServlet",
					      name + "(" + resourceName + ")" );
		    
		    System.out.println(msg);
		    
		    removeResource = true;
		    ctx.removeServletByName(name);
		}

		ctx.addServlet(name, resourceName, description);
	    } else if (webComponentDescriptor instanceof JspDescriptor) {
		resourceName =
		    ((JspDescriptor)webComponentDescriptor).getJspFileName();

		if (! resourceName.startsWith("/")) {
		    resourceName = "/" + resourceName;
		}

		if (ctx.containsJSP(resourceName)) {
		    String msg = sm.getString("context.dd.dropServlet",
					      resourceName);

		    System.out.println(msg);
		    
		    removeResource = true;
		    ctx.removeJSP(resourceName);
		}

		ctx.addJSP(name, resourceName, description);
	    }


	    // XXX ugly, but outside of context - the whole thing will be
	    // rewriten, so don't worry
	    
	    // if the resource was already defined, override with the new definition
	    // XXX I have very little ideea about what it does !
	    if (removeResource) {

	        Enumeration levels = ctx.getInitLevles();

		while (levels.hasMoreElements()) {
		    Integer level = (Integer)levels.nextElement();
		    Enumeration servletsOnLevel=ctx.getLoadableServlets( level );
		    
		    Vector buf = new Vector();
		    while (servletsOnLevel.hasMoreElements()) {
		        String servletName = (String)servletsOnLevel.nextElement();

			if (ctx.containsServletByName(servletName)) {
			    buf.addElement(servletName);
			}
		    }
		    ctx.setLoadableServlets(level, buf);
		}
	    }
	    
	    int loadOnStartUp = webComponentDescriptor.getLoadOnStartUp();

            if (loadOnStartUp > Integer.MIN_VALUE) {
	        Integer key = new Integer(loadOnStartUp);
		ctx.addLoadableServlet( key, name );
		
	    }

	    Enumeration enum =
	        webComponentDescriptor.getInitializationParameters();
	    Hashtable initializationParameters = new Hashtable();

	    while (enum.hasMoreElements()) {
	        InitializationParameter initializationParameter =
		    (InitializationParameter)enum.nextElement();

		initializationParameters.put(
		    initializationParameter.getName(),
		    initializationParameter.getValue());
	    }

	    ctx.setServletInitParams( webComponentDescriptor.getCanonicalName(),
				 initializationParameters);

	    enum = webComponentDescriptor.getUrlPatterns();

	    while (enum.hasMoreElements()) {
	        String mapping = (String)enum.nextElement();

		if (! mapping.startsWith("*.") &&
		    ! mapping.startsWith("/")) {
		    mapping = "/" + mapping;
		}

		if (! ctx.containsServlet(mapping) &&
		    ! ctx.containsJSP(mapping)) {
		    if (ctx.containsMapping(mapping)) {
		        String msg = sm.getString("context.dd.dropMapping",
			    mapping);

			System.out.println(msg);

			ctx.removeMapping(mapping);
		    }

                    ctx.addMapping(name, mapping);
		} else {
		    String msg = sm.getString("context.dd.ignoreMapping",
		        mapping);

		    System.out.println(msg);
		}
	    }
	}
    }

    private void processMimeMaps(Context ctx, Enumeration mimeMaps) {
        while (mimeMaps.hasMoreElements()) {
	    MimeMapping mimeMapping = (MimeMapping)mimeMaps.nextElement();

	    ctx.addContentType(	mimeMapping.getExtension(),
				mimeMapping.getMimeType());
	}
    }

    private void processWelcomeFiles(Context ctx, Enumeration welcomeFiles,
        boolean internal) {
        if (! internal && welcomeFiles.hasMoreElements()) {
            ctx.removeWelcomeFiles();
        }

	while (welcomeFiles.hasMoreElements()) {
	    ctx.addWelcomeFile((String)welcomeFiles.nextElement());
	}
    }

    private void processErrorPages(Context ctx, Enumeration errorPages) {
        while (errorPages.hasMoreElements()) {
	    ErrorPageDescriptor errorPageDescriptor =
	        (ErrorPageDescriptor)errorPages.nextElement();
	    String key = null;

	    if (errorPageDescriptor.getErrorCode() > -1) {
	        key = String.valueOf(errorPageDescriptor.getErrorCode());
	    } else {
	        key = errorPageDescriptor.getExceptionType();
	    }

	    ctx.addErrorPage(key, errorPageDescriptor.getLocation());
	}
    }

    
}