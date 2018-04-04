import org.apache.tomcat.util.depend.*;

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
import org.apache.tomcat.depend.*;
import java.io.*;
import java.net.*;
import java.util.*;
import java.security.*;

import org.apache.tomcat.logging.*;
import org.apache.tomcat.loader.*;

/**
 * Set class loader based on WEB-INF/classes, lib.
 * Uses the protection domain - if any, so PolicyInterceptor
 * must be called before it.
 *
 * @author costin@dnt.ro
 */
public class LoaderInterceptor1 extends BaseInterceptor {
    String classLoaderName;
    
    public LoaderInterceptor1() {
    }

    public void setClassLoaderName( String name ) {
	classLoaderName=name;
    }

    /** The class paths are added when the context is added
     */
    public void addContext( ContextManager cm, Context context)
	throws TomcatException
    {
	if( debug>0) log( "Add context " + context.getPath());
        String base = context.getDocBase();

	// Add "WEB-INF/classes"
	File dir = new File(base + "/WEB-INF/classes");

        // GS, Fix for the jar@lib directory problem.
        // Thanks for Kevin Jones for providing the fix.
        dir = cm.getAbsolute(dir);
	if( dir.exists() ) {
	    try {
		URL url=new URL( "file", null, dir.getAbsolutePath() + "/" );
		context.addClassPath( url );
	    } catch( MalformedURLException ex ) {
	    }
        }

        File f = cm.getAbsolute(new File(base + "/WEB-INF/lib"));
	Vector jars = new Vector();
	getJars(jars, f);

	for(int i=0; i < jars.size(); ++i) {
	    String jarfile = (String) jars.elementAt(i);
	    File jarF=new File(f, jarfile );
	    File jf=cm.getAbsolute( jarF );
	    String absPath=jf.getAbsolutePath();
	    try {
		URL url=new URL( "file", null, absPath );
		context.addClassPath( url );
	    } catch( MalformedURLException ex ) {
	    }
	}
    }

    /** The class loader is set when the context us initialized
     *  or at reload
     */
    public void contextInit( Context context)
	throws TomcatException
    {
	if( debug>0 ) log( "Init context " + context.getPath());
        ContextManager cm = context.getContextManager();
	URL urls[]=context.getClassPath();

	DependManager dm=context.getDependManager();
	if( dm==null ) {
	    dm=new DependManager();
	    context.setDependManager( dm );
	}
	URLClassLoader urlLoader=URLClassLoader.newInstance( urls );
	DependClassLoader dcl=new DependClassLoader( dm, urlLoader);

	context.setClassLoader( dcl );
    }

    public void reload( Request req, Context context) throws TomcatException {
	log( "Reload event " );
	
	ContextManager cm = context.getContextManager();
	URL urls[]=context.getClassPath();

	DependManager dm=new DependManager();
	context.setDependManager( dm );

	URLClassLoader urlLoader=URLClassLoader.newInstance( urls );
	DependClassLoader dcl=new DependClassLoader( dm, urlLoader);
	
	context.setClassLoader( dcl );
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

}