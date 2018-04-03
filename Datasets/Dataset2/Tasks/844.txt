Context ctx=cm.createContext();

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

import org.apache.tomcat.core.*;
import org.apache.tomcat.util.*;
import java.io.*;
import java.net.*;
import java.util.*;

import org.apache.tomcat.util.xml.*;

/**
 * Automatically add all the web applications from a directory.
 * You can use multiple AutoWebApp modules with different locations.
 * 
 * This module will not "deploy" wars or do any other configuration. It'll
 * just use all the sub-directories as web application bases, and use
 * a simple escaping scheme. 
 * 
 * Based on the original AutoSetup.
 * 
 * @author cmanolache@yahoo.com
 */
public class AutoWebApp extends BaseInterceptor {
    int debug=0;
    Hashtable hosts=new Hashtable();
    String appsD="webapps";
    String defaultHost=null; 
    boolean flat=true;
    boolean ignoreDot=true;
    String profile=null;
    boolean trusted=false;
    String prefix="";
    
    // encoding scheme - XXX review, customize, implement
    char hostSeparator='@'; // if support for vhost configuration is enabled
    // instead of one-dir-per-host, this char will separate the host part.
    char dotReplacement='_'; // use this in the host part to replace dots.
    char slashReplacement='_'; // use this in the path part to replace /
    
    public AutoWebApp() {
    }

    //-------------------- Config --------------------
    
    /** Use this directory for auto configuration. Default is
     *  TOMCAT_HOME/webapps.
     *  @param d A directory containing your applications.
     *    If it's not an absoulte path, TOMCAT_HOME will be used as base.
     */
    public void setDir( String d ) {
	appsD=d;
    }

    /** Add a prefix to all deployed context paths
     */
    public void setPrefix(String s ) {
	prefix=s;
    }
    
    /** All applications in the directory will be added to a
	single virtual host. If not set, an encoding scheme
	will be used to extract the virtual host name from
	the application name. For backward compatibilty you
	can set it to "DEFAULT". This is also usefull when you
	want each virtual host to have it's own directory.
    */
    public void setHost( String h ) {
	defaultHost=h;
    }

    /** Ignore directories starting with a "."
     */
    public void setIngoreDot( boolean b ) {
	ignoreDot=b;
    }
    

    /** Not implemented - default is true. If flat==false, virtual
	hosts will be configured using the hierarchy in webapps.
	( webapps/DEFAULT/, webapps/VHOST1, etc ).
    */
    public void setFlat( boolean b ) {
	flat=b;
    }

    /** Set the "profile" attribute on each context. This
	can be used by a profile module to configure the
	context with special settings.
    */
    public void setProfile( String s ) {
	profile=s;
    }

    /** Set the trusted attribute to all apps. This is
	used for "internal" apps, to reduce the number 
	of manual configurations. It works by creating
	a special directory and using <AutoWebApp> to
	add all the apps inside with a trusted attribute.
    */
    public void setTrusted( boolean b ) {
	trusted=b;
    }
    
    //-------------------- Implementation --------------------
    
    /** 
     */
    public void engineInit(ContextManager cm) throws TomcatException {
	// Make sure we know about all contexts added before.
	Enumeration loadedCtx=cm.getContexts();
	// loaded but not initialized - since we are still configuring
	// the server
	while( loadedCtx.hasMoreElements() ) {
	    Context ctx=(Context)loadedCtx.nextElement();
	    String host=ctx.getHost();
	    if(host==null) host="DEFAULT";
	    
	    Hashtable loaded=(Hashtable)hosts.get( host );
	    if( loaded==null ) {
		loaded=new Hashtable();
		hosts.put(host, loaded );
	    }
	    loaded.put( ctx.getPath(), ctx );
	}
	
	String home=cm.getHome();
	File webappD;
	
	if( appsD.startsWith( "/" ) ) 
	    webappD=new File(appsD);
	else
	    webappD=new File(home + "/" + appsD);
	
	if (! webappD.exists() || ! webappD.isDirectory()) {
	    log("No autoconf directory " + webappD );
	    return ; // nothing to set up
	}
	
	String[] list = webappD.list();

	if( flat ) {
	    for (int i = 0; i < list.length; i++) {
		String name = list[i];
		if( ignoreDot && name.startsWith( "." ))
		    continue;
		File f=new File( webappD, name );
		if( f.isDirectory() ) {
		    String appHost=defaultHost;
		    // Decode the host ( only if a host is not specified )
		    if( defaultHost==null ) {
			int idx=name.indexOf( hostSeparator ); // may change
			if( idx > 0 ) {
			    appHost=name.substring( 0, idx );
			    name=name.substring( idx );
			}
		    }
		    if( appHost == null )
			appHost="DEFAULT";

		    addWebApp( cm, f, appHost, name );
		}
	    }
	} else {
	    for (int i = 0; i < list.length; i++) {
		String name = list[i];
		File f=new File( webappD, name );
		if( f.isDirectory() ) {
		    if( ignoreDot && name.startsWith("." )) {
			continue;
		    } else
			addVHost( cm, webappD, name );
		}
	    }
	}
    }

    /** Add one application
     */
    private void addWebApp( ContextManager cm, File dir, String host,
			    String name)
	throws TomcatException
    {
	host= unEscapeHost( host );
	if(host==null) host="DEFAULT";

	String path="/" + unEscapePath( name );
	if( path.equals("/ROOT") )
	    path="";

	Hashtable loaded=(Hashtable)hosts.get(host);
	if( loaded != null && loaded.get( path ) != null ) {
	    log( "Loaded from config: " + host + ":" +
		 ( "".equals(path) ? "/" : path ) );
	    return; // already loaded
	}
	log("Auto-Adding " + host + ":" +
	    ( "".equals(path) ? "/" : path ) );

	if (dir.isDirectory()) {
	    Context ctx=new Context();
	    ctx.setContextManager( cm );
	    ctx.setPath(prefix + path);
	    if( ! "DEFAULT".equals( host ) )
		ctx.setHost( host );
	    try {
		ctx.setDocBase( dir.getCanonicalPath() );
	    } catch(IOException ex ) {
		ctx.setDocBase( dir.getAbsolutePath());
	    }

	    if( trusted ) 
		ctx.setTrusted( true );
	    if( profile!=null )
		ctx.setProperty( "profile", profile );
	    
	    if( debug > 0 )
		log("automatic add " + host + ":" + ctx.toString() + " " +
		    path);
	    cm.addContext(ctx);
	} else {
	    log( "Not a dir " + dir.getAbsolutePath());
	}
    }

   /** Add all the contexts for a virtual host
     */
   private void addVHost( ContextManager cm, File dir, String host )
       throws TomcatException
    {
        File webappD=new File( dir, host );
	
        String[] list = webappD.list();
	if( list.length==0 ) {
	    log("No contexts in " + webappD );
	}
	
	for (int i = 0; i < list.length; i++) {
	    String name = list[i];
	    File f=new File(webappD, name );
	    if( f.isDirectory() ) {
		addWebApp( cm, webappD,host,  name );
	    }
	}
    }

    // -------------------- Escaping --------------------
        
    private String unEscapeHost( String hostName ) {
	return unEscapeString( hostName, dotReplacement , '.' );
    }

    private String unEscapePath( String pathDir ) {
	return unEscapeString( pathDir, slashReplacement, '/' );
    }

    /** Replace 'esc' with 'repl', and 'esc''esc' with 'esc'
     */
    private String unEscapeString( String s, char esc, char repl ) {
	StringBuffer sb=new StringBuffer();
	int len=s.length();
	for( int i=0; i< len; i++ ) {
	    char c=s.charAt( i );
	    if( c== esc ) {
		if( len > i + 1 && s.charAt( i+1 ) == esc ) {
		    // _ _
		    i++;
		    sb.append( esc );
		} else {
		    sb.append( repl );
		}
	    } else {
		sb.append( c );
	    }
	}
	return sb.toString();
    }

}