xh.addRule( "Host", xh.setVar( "current_host", "name"));

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
package org.apache.tomcat.modules.config;

import java.beans.*;
import java.io.*;
import java.lang.reflect.*;
import java.util.Hashtable;
import java.util.*;
import java.net.*;
import org.apache.tomcat.util.res.StringManager;
import org.apache.tomcat.util.xml.*;
import org.apache.tomcat.core.*;
import org.apache.tomcat.modules.server.*;
import org.apache.tomcat.util.log.Log;
import org.xml.sax.*;

/**
 * This is a configuration module that will read context configuration files,
 * including server.xml, and configure the server by adding the contexts.
 *
 * @author Costin Manolache
 */
public class ContextXmlReader extends BaseInterceptor {
    private static StringManager sm =
	StringManager.getManager("org.apache.tomcat.resources");
    
    public ContextXmlReader() {
    }

    // -------------------- Properties --------------------
    String configFile=null;   
    static final String DEFAULT_CONFIG="conf/server.xml";

    public void setConfig( String s ) {
	configFile=s;
    }

    public void setHome( String h ) {
	System.getProperties().put("tomcat.home", h);
    }

    // -------------------- Hooks -------------------- 

    public void engineInit(ContextManager cm)
	throws TomcatException
    {
        if( configFile==null )
	    configFile=(String)cm.getNote("configFile");

	XmlMapper xh=new XmlMapper();
	xh.setDebug( debug );

	// use the same tags for context-local modules
	addTagRules(cm, xh);
	setContextRules( xh );
	setBackward( xh );

	// load the config file(s)
	File f  = null;
	if (configFile == null)
	    configFile=DEFAULT_CONFIG;

        f=new File(configFile);
	if( !f.isAbsolute())
	    f=new File( cm.getHome(), "/" + configFile);

	if( f.exists() )
	    ServerXmlReader.loadConfigFile(xh,f,cm);

	// load server-*.xml
	Vector v = ServerXmlReader.getUserConfigFiles(f);
	for (Enumeration e = v.elements();
	     e.hasMoreElements() ; ) {
	    f = (File)e.nextElement();
	    if( f.exists() ) {
		String s=f.getAbsolutePath();
		if( s.startsWith( cm.getHome()))
		    s="$TOMCAT_HOME" + s.substring( cm.getHome().length());
		log( "Context config=" + s);
	    }
	    ServerXmlReader.loadConfigFile(xh,f,cm);
	}
    }

    // -------------------- Xml reading details --------------------

    // rules for reading teh context config
    public static void setContextRules( XmlMapper xh ) {
	// Default host
	xh.addRule( "Context",
		    xh.objectCreate("org.apache.tomcat.core.Context"));
	xh.addRule( "Context",
		    xh.setProperties() );
	xh.addRule( "Context",
		    xh.setParent("setContextManager") );
	
	// Virtual host support - if Context is inside a <Host>
	xh.addRule( "Host", xh.setVariable( "current_host", "name"));
	xh.addRule( "Host", xh.setProperties());

	xh.addRule( "Context", new XmlAction() {
		public void end( SaxContext ctx) throws Exception {
		    Context tcCtx=(Context)ctx.currentObject();
		    String host=(String)ctx.getVariable("current_host");
		    
		    if( host!=null && ! "DEFAULT".equals( host )) 
			    tcCtx.setHost( host );
		}
	    });

	xh.addRule( "Context",
		    xh.addChild("addContext",
				"org.apache.tomcat.core.Context") );
    }
    
    // -------------------- Backward compatibility -------------------- 

    // Read old configuration formats
    private static void setBackward( XmlMapper xh ) {
	// Configure context interceptors
	xh.addRule( "Context/Interceptor",
		    xh.objectCreate(null, "className"));
	xh.addRule( "Context/Interceptor",
		    xh.setProperties() );
	xh.addRule( "Context/Interceptor",
		    xh.setParent("setContext") );
	xh.addRule( "Context/Interceptor",
		    xh.addChild( "addInterceptor",
				 "org.apache.tomcat.core.BaseInterceptor"));
	// Old style 
	xh.addRule( "Context/RequestInterceptor",
		    xh.objectCreate(null, "className"));
	xh.addRule( "Context/RequestInterceptor",
		    xh.setProperties() );
	xh.addRule( "Context/RequestInterceptor",
		    xh.setParent("setContext") );
	xh.addRule( "Context/RequestInterceptor",
		    xh.addChild( "addInterceptor",
				 "org.apache.tomcat.core.BaseInterceptor"));
	xh.addRule("Context/Logger",
		   xh.objectCreate("org.apache.tomcat.util.log.QueueLogger"));
	xh.addRule("Context/Logger", xh.setProperties());
	xh.addRule("Context/Logger", 
		   xh.addChild("setLogger",
			       "org.apache.tomcat.util.log.Logger") );
	
	xh.addRule("Context/ServletLogger",
		   xh.objectCreate("org.apache.tomcat.util.log.QueueLogger"));
	xh.addRule("Context/ServletLogger", xh.setProperties());
	xh.addRule("Context/ServletLogger", 
		   xh.addChild("setServletLogger",
			       "org.apache.tomcat.util.log.Logger") );
    }

    // --------------------

    public void addTagRules( ContextManager cm, XmlMapper xh )
	throws TomcatException
    {
	Hashtable modules=(Hashtable)cm.getNote("modules");
	if( modules==null) return;
	Enumeration keys=modules.keys();
	while( keys.hasMoreElements() ) {
	    String name=(String)keys.nextElement();
	    String classN=(String)modules.get( name );

	    String tag="Context" + "/" + name;
	    xh.addRule(  tag ,
			 xh.objectCreate( classN, null ));
	    xh.addRule( tag ,
			xh.setProperties());
	    xh.addRule( tag,
			xh.addChild( "addInterceptor",
				     "org.apache.tomcat.core.BaseInterceptor"));
	}
    }
}
