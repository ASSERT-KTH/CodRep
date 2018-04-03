addTagRules( cm, xh );

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
import org.apache.tomcat.util.io.FileUtil;
import org.apache.tomcat.util.xml.*;
import org.apache.tomcat.core.*;
import org.apache.tomcat.modules.server.*;
import org.apache.tomcat.util.log.*;
import org.apache.tomcat.util.hooks.*;
import org.apache.tomcat.util.IntrospectionUtils;
import org.xml.sax.*;

/**
 * This is a configuration module that will read a server.xml file
 * and dynamically configure the server by adding modules and interceptors.
 *
 * Tomcat can be configured ( and auto-configured ) in many ways, and
 * a configuration module will have access to all server events, and will
 * be able to update it's state, etc.
 *
 * @author Costin Manolache
 */
public class ServerXmlReader extends BaseInterceptor {
    private static StringManager sm =
	StringManager.getManager("org.apache.tomcat.resources");

    
    public ServerXmlReader() {
    }

    // -------------------- Properties --------------------
    String configFile=null;
    String moduleFile=null;
    static final String DEFAULT_CONFIG="conf/server.xml";
    static final String DEFAULT_MODULES="conf/modules.xml";
    boolean useCachedModules=true;// can roll back
    
    public void setConfig( String s ) {
	configFile=s;
    }

    public void setHome( String h ) {
	System.getProperties().put("tomcat.home", h);
    }

    public void setModuleConfig( String f ) {
	moduleFile=f;
    }
    
    // -------------------- Hooks --------------------

    /** When this module is added, it'll automatically load
     *  a configuration file and add all global modules.
     */
    public void addInterceptor(ContextManager cm, Context ctx,
			       BaseInterceptor module)
	throws TomcatException
    {
	//	checkHooks(cm, ctx, module);
	if( this != module ) return;
	setupHookFinder();
	XmlMapper xh=new XmlMapper();
	xh.setDebug( debug );
	xh.addRule( "ContextManager", xh.setProperties() );
	setPropertiesRules( cm, xh );
	setTagRules( xh );
	addDefaultTags(cm, xh);
	//addTagRules( cm, xh );
	setBackward( xh );

	// load the config file(s)
	File f  = null;
	if (configFile == null) {
	    f=new File( cm.getHome(), DEFAULT_CONFIG);
	} else {
	    // All other paths are relative to TOMCAT_HOME, except this one.
	    // The user will either type an absolute path or a path relative
	    // to his working dir ( relative to TOMCAT_HOME is counterintuitive)
	    f=new File(configFile);
	}

	if( f.exists() ){
	    f=new File( f.getAbsolutePath());
            cm.setNote( "configFile", f.getAbsolutePath());
	    loadConfigFile(xh,f,cm);
	    String s=f.getAbsolutePath();
	    if( s.startsWith( cm.getHome()))
		s="$TOMCAT_HOME" + s.substring( cm.getHome().length());
	    log( "Config=" + s);
            // load server-*.xml
            Vector v = getUserConfigFiles(f);
            for (Enumeration e = v.elements();
                 e.hasMoreElements() ; ) {
                f = (File)e.nextElement();
                loadConfigFile(xh,f,cm);
		cm.log(sm.getString("tomcat.loading") + " " + f);
            }
	    
        }
    }

    // -------------------- Xml reading details --------------------

    public static void loadConfigFile(XmlMapper xh, File f, Object cm)
	throws TomcatException
    {
	try {
	    xh.readXml(f,cm);
	} catch( Exception ex ) {
	    ex.printStackTrace();
	    //	    cm.log( sm.getString("tomcat.fatalconfigerror"), ex );
	    throw new TomcatException(ex);
	}
    }

    static class CMPropertySource
	implements IntrospectionUtils.PropertySource
    {
	ContextManager cm;
	
	CMPropertySource( ContextManager cm ) {
	    this.cm=cm;
	}
	
	public String getProperty( String key ) {
	    if( "tomcat.home".equals( key ) ) {
		return cm.getHome();
	    }
	    // XXX add other "predefined" properties
	    return cm.getProperty( key );
	}
    }

    public static void setPropertiesRules( ContextManager cm, XmlMapper xh )
	throws TomcatException
    {
	CMPropertySource propS=new CMPropertySource( cm );
	xh.setPropertySource( propS );
	
	xh.addRule( "ContextManager/property", new XmlAction() {
		public void start(SaxContext ctx ) throws Exception {
		    AttributeList attributes = ctx.getCurrentAttributes();
		    String name=attributes.getValue("name");
		    String value=attributes.getValue("value");
		    if( name==null || value==null ) return;
		    XmlMapper xm=ctx.getMapper();
		    
		    ContextManager cm1=(ContextManager)ctx.currentObject();
		    // replace ${foo} in value
		    value=xm.replaceProperties( value );
		    if( cm1.getDebug() > 0 )
			cm1.log("Setting " + name + "=" + value);
		    cm1.setProperty( name, value );
		}
	    });
    }

    public static void addTagRules( ContextManager cm, XmlMapper xh )
	throws TomcatException
    {
	Hashtable modules=(Hashtable)cm.getNote("modules");
	if( modules==null) return;
	Enumeration keys=modules.keys();
	while( keys.hasMoreElements() ) {
	    String tag=(String)keys.nextElement();
	    String classN=(String)modules.get( tag );

	    addTagRule( xh, tag, classN );
	}
    }

    public static void addTagRule( XmlMapper xh, String tag, String classN ) {
	xh.addRule( tag ,
		    xh.objectCreate( classN, null ));
	xh.addRule( tag ,
		    xh.setProperties());
	xh.addRule( tag,
		    xh.addChild( "addInterceptor",
				 "org.apache.tomcat.core.BaseInterceptor"));
    }

    public static void setTagRules( XmlMapper xh ) {
	xh.addRule( "module",  new XmlAction() {
		public void start(SaxContext ctx ) throws Exception {
		    Object elem=ctx.currentObject();
		    AttributeList attributes = ctx.getCurrentAttributes();
		    String name=attributes.getValue("name");
		    String classN=attributes.getValue("javaClass");
		    if( name==null || classN==null ) return;
		    ContextManager cm=(ContextManager)ctx.currentObject();
		    Hashtable modules=(Hashtable)cm.getNote("modules");
		    modules.put( name, classN );
		    addTagRule( ctx.getMapper(), name, classN );
		    if( ctx.getDebug() > 0 ) ctx.log("Adding " + name + " " + classN );
		}
	    });
    }

    // read modules.xml, if any, and load taskdefs
    public void addDefaultTags( ContextManager cm, XmlMapper xh)
	throws TomcatException
    {
	if( cm.getNote( "modules" ) != null )
	    return;
	if( moduleFile==null ) moduleFile=DEFAULT_MODULES;
        File f=new File(moduleFile);
        if ( !f.isAbsolute())
	    f=new File( cm.getHome(), moduleFile );

	if( f.exists() ) {
	    // try cached value
	    File cachedM=new File( cm.getWorkDir() );
	    if( !cachedM.isAbsolute())
		cachedM=new File( cm.getHome(), cm.getWorkDir());
	    cachedM=new File( cachedM, "modules.properties");
	    Properties modules=new Properties();
	    cm.setNote( "modules", modules );
	    if( useCachedModules &&
		cachedM.exists() &&
		cachedM.lastModified() > f.lastModified() ) {
		// XXX check the other modules-foo.xml
		loadCachedModules(cachedM, modules );
		return;
	    } else {
		loadConfigFile( xh, f, cm );
		// load module-*.xml
		Vector v = getUserConfigFiles(f);
		for (Enumeration e = v.elements();
		     e.hasMoreElements() ; ) {
		    f = (File)e.nextElement();
		    loadConfigFile(xh,f,cm);
		}
		saveCachedModules(cachedM, modules);
	    }
	}
    }

    void loadCachedModules( File f, Properties mods ) {
	try {
	    FileInputStream pos=new FileInputStream( f );
	    mods.load( pos );
	} catch(IOException ex ) {
	    log("Error loading modules ", ex );
	}
    }

    void saveCachedModules( File f, Properties mods ) {
	try {
	    FileOutputStream pos=new FileOutputStream( f );
	    mods.save( pos, "Auto-generated cache file");
	} catch(IOException ex ) {
	    //log("Error saving modules ", ex );
	}
    }

    void setupHookFinder() {
	Hooks.setHookFinder( new IntrospectionHookFinder() );
    }

    static class IntrospectionHookFinder implements Hooks.HookFinder {
	public boolean hasHook( Object o, String hook ) {
	    return IntrospectionUtils.hasHook( o, hook );
	}
    }
    // -------------------- File utils --------------------

    // get additional files
    public static Vector getUserConfigFiles(File master) {
	File dir = new File(master.getParent());
	String[] names = dir.list();
	//	System.out.println("getUserConfigFiles " + dir );

	String masterName=master.getAbsolutePath();

	String base=FileUtil.getBase(masterName) + "-";
	String ext=FileUtil.getExtension( masterName );
	
	Vector v = new Vector();
	if( names==null ) return v;
	for (int i=0; i<names.length; ++i) {
	    if( names[i].startsWith( base )
		&& ( ext==null || names[i].endsWith( ext )) ) {

		File found = new File(dir, names[i]);
		v.addElement(found);
	    }
	}
	return v;
    }

    // -------------------- Backward compatibility --------------------

    // Read old configuration formats
    private void setBackward( XmlMapper xh ) {
	xh.addRule( "ContextManager/ContextInterceptor",
		    xh.objectCreate(null, "className"));
	xh.addRule( "ContextManager/ContextInterceptor",
		    xh.setProperties() );
	xh.addRule( "ContextManager/ContextInterceptor",
		    xh.addChild( "addInterceptor",
				 "org.apache.tomcat.core.BaseInterceptor"));

	xh.addRule( "ContextManager/RequestInterceptor",
		    xh.objectCreate(null, "className"));
	xh.addRule( "ContextManager/RequestInterceptor",
		    xh.setProperties() );
	xh.addRule( "ContextManager/RequestInterceptor",
		    xh.addChild( "addInterceptor",
				 "org.apache.tomcat.core.BaseInterceptor"));

	// old <connector>
	xh.addRule( "ContextManager/Connector",
		    xh.objectCreate(null, "className"));
	xh.addRule( "ContextManager/Connector",
		    xh.setParent( "setContextManager",
				  "org.apache.tomcat.core.ContextManager") );
	xh.addRule( "ContextManager/Connector",
		    xh.addChild( "addInterceptor",
				 "org.apache.tomcat.core.BaseInterceptor"));

	xh.addRule( "ContextManager/Connector/Parameter",
		    xh.methodSetter("setProperty",2) );
	xh.addRule( "ContextManager/Connector/Parameter",
		    xh.methodParam(0, "name") );
	xh.addRule( "ContextManager/Connector/Parameter",
		    xh.methodParam(1, "value") );

	// old <Logger>
	xh.addRule("Server/Logger",
		   xh.objectCreate("org.apache.tomcat.util.log.QueueLogger"));
	xh.addRule("Server/Logger", xh.setProperties());
	xh.addRule("Server/Logger", 
		   xh.addChild("addLogger",
			       "org.apache.tomcat.util.log.Logger") );

    }


}
