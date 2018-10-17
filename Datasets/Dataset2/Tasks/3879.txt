loader.addRepository( new File( base + "/WEB-INF/lib/" +jarfile ));

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
import org.apache.tomcat.request.*;
import org.apache.tomcat.util.*;
import java.io.*;
import java.net.*;
import java.util.*;
import javax.servlet.http.*;

import org.apache.tomcat.logging.*;

/**
 * Check ContextManager and set defaults for non-set properties
 *
 * @author costin@dnt.ro
 */
public class DefaultCMSetter extends BaseInterceptor {

    public DefaultCMSetter() {
    }

    public void engineInit(ContextManager cm) throws TomcatException {
	// check if we are in the right directory
	File f=new File( cm.getHome() + "/conf/web.xml");
	if( ! f.exists() ) {
	    throw new TomcatException( "Wrong home " + cm.getHome());
	}
    }
    
    /** Called when a new context is added to the server.
     *
     *  - Check it and set defaults for WorkDir, EngineHeader and SessionManager.
     *  If you don't like the defaults, set them in Context before adding it to the
     *  engine.
     *
     *  - Set up defaults for context interceptors and session if nothing is set
     */
    public void addContext(ContextManager cm, Context ctx)
	throws TomcatException
    {
    }

    public void contextInit( Context ctx)
	throws TomcatException
    {
	setEngineHeader( ctx );

	if( ctx.getWorkDir() == null)
	    setWorkDir(ctx);

	if (! ctx.getWorkDir().exists()) {
	    //log  System.out.println("Creating work dir " + ctx.getWorkDir() );
	    ctx.getWorkDir().mkdirs();
	}
	ctx.setAttribute(Constants.ATTRIB_WORKDIR1, ctx.getWorkDir());
	ctx.setAttribute(Constants.ATTRIB_WORKDIR , ctx.getWorkDir());

	// Set default session manager if none set
	if( ctx.getSessionManager() == null ) 
	    ctx.setSessionManager(new org.apache.tomcat.session.StandardSessionManager());
	//  Alternative: org.apache.tomcat.session.ServerSessionManager.getManager();

	ServletWrapper authWrapper=new ServletWrapper();
	authWrapper.setContext( ctx );
	authWrapper.setServletClass( "org.apache.tomcat.servlets.AuthServlet" );
	authWrapper.setServletName( "tomcat.authServlet");
	ctx.addServlet( authWrapper );

	ServletWrapper errorWrapper=new ServletWrapper();
	errorWrapper.setContext( ctx );
	errorWrapper.setServletClass( "org.apache.tomcat.servlets.DefaultErrorPage" );
	errorWrapper.setServletName( "tomcat.errorPage");
	ctx.addServlet( errorWrapper );

	// XXX Loader properties - need to be set on loader!!
	//ctx.setServletLoader( new org.apache.tomcat.loader.ServletClassLoaderImpl());
	ctx.setServletLoader( new org.apache.tomcat.loader.AdaptiveServletLoader());
	initURLs( ctx );
	// Validation for error  servlet
	try {
	    ServletWrapper errorWrapper1=ctx.getServletByName( "tomcat.errorPage");
	    errorWrapper1.loadServlet();
	} catch( Exception ex ) {
	    System.out.println("Error loading default servlet ");
            ex.printStackTrace();
	    // XXX remove this context from CM
	    throw new TomcatException( "Error loading default error servlet ", ex );
	}
    }
    
    private void initURLs(Context context) {
	ServletLoader loader=context.getServletLoader();
	if( loader==null) return;

	// Add "WEB-INF/classes"

	String base = context.getDocBase();
	File dir = new File(base + "/WEB-INF/classes");
        if (!dir.isAbsolute()) {
            // evaluate repository path relative to the context's home directory
            ContextManager cm = context.getContextManager();
	    dir = new File(cm.getHome(), base + "/WEB-INF/classes");
        }
	if( dir.exists() ) {
	    loader.addRepository( dir );
	}

	File f =  new File(base + "/WEB-INF/lib");
	Vector jars = new Vector();
	getJars(jars, f);
            
	for(int i=0; i < jars.size(); ++i) {
	    String jarfile = (String) jars.elementAt(i);
	    loader.addRepository( new File( base + "/WEB-INF/" +jarfile ));
	}
    }


    private void getJars(Vector v, File f) {
        FilenameFilter jarfilter = new FilenameFilter() {
		public boolean accept(File dir, String fname) {
		    if(fname.endsWith(".jar"))
			return true;
		    
		    return false;
		}
	    };
        FilenameFilter dirfilter = new FilenameFilter() {
		public boolean accept(File dir, String fname) {
		    File f1 = new File(dir, fname);
		    if(f1.isDirectory())
			return true;
		    
		    return false;
		}
	    };
        
        if(f.exists() && f.isDirectory() && f.isAbsolute()) {
            String[] jarlist = f.list(jarfilter);

            for(int i=0; (jarlist != null) && (i < jarlist.length); ++i) {
                v.addElement(jarlist[i]);
            }

            String[] dirlist = f.list(dirfilter);

            for(int i=0; (dirlist != null) && (i < dirlist.length); ++i) {
                File dir = new File(f, dirlist[i]);
                getJars(v, dir);
            }
        }
    }

    // -------------------- implementation
    /** Encoded ContextManager.getWorkDir() + host + port + path
     */
    private void setWorkDir(Context ctx ) {
	ContextManager cm=ctx.getContextManager();
	
	StringBuffer sb=new StringBuffer();
	sb.append(cm.getWorkDir());
	sb.append(File.separator);
	sb.append(cm.getHostName() );
	sb.append("_").append(cm.getPort());
	sb.append(URLEncoder.encode( ctx.getPath() ));
	
	ctx.setWorkDir( new File(sb.toString()));
    }
    
    private void setEngineHeader(Context ctx) {
        String engineHeader=ctx.getEngineHeader();

	if( engineHeader==null) {
	    /*
	     * Whoever modifies this needs to check this modification is
	     * ok with the code in com.jsp.runtime.ServletEngine or talk
	     * to akv before you check it in. 
	     */
	    // Default value for engine header
	    // no longer use core.properties - the configuration comes from
	    // server.xml or web.xml - no more properties.
	    StringBuffer sb=new StringBuffer();
	    sb.append(Constants.TOMCAT_NAME).append("/").append(Constants.TOMCAT_VERSION);
	    sb.append(" (").append(Constants.JSP_NAME).append(" ").append(Constants.JSP_VERSION);
	    sb.append("; ").append(Constants.SERVLET_NAME).append(" ");
	    sb.append(Constants.SERVLET_MAJOR).append(".").append(Constants.SERVLET_MINOR);
	    sb.append( "; Java " );
	    sb.append(System.getProperty("java.version")).append("; ");
	    sb.append(System.getProperty("os.name") + " ");
	    sb.append(System.getProperty("os.version") + " ");
	    sb.append(System.getProperty("os.arch") + "; java.vendor=");
	    sb.append(System.getProperty("java.vendor")).append(")");
	    engineHeader=sb.toString();
	}
	ctx.setEngineHeader( engineHeader );
    }

}