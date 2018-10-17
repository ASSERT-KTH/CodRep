if( useAL && !context.isTrusted() )

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
import org.apache.tomcat.util.compat.*;
import org.apache.tomcat.util.depend.*;
import java.io.*;
import java.net.*;
import java.util.*;
import java.security.*;

/**
 * Set class loader based on WEB-INF/classes, lib.
 * Compatible with JDK1.1, but takes advantage of URLClassLoader if
 * java2 is detected.
 * 
 *
 * @author costin@dnt.ro
 */
public class LoaderInterceptor11 extends BaseInterceptor {
    boolean useAL=false;
    boolean useNoParent=false;
    
    public LoaderInterceptor11() {
    }

    /** Use ContextManager.getParentLoader() - typlically the class loader
     *  that is set by the application embedding tomcat.
     */
    public void setUseApplicationLoader( boolean b ) {
	useAL=b;
    }

    /** Use no parent loader. The contexts will be completely isolated.
     */
    public void setUseNoParent( boolean b ) {
	useNoParent=b;
    }
    
    public void addContext( ContextManager cm, Context context)
	throws TomcatException
    {
        String base = context.getAbsolutePath();

	// Add "WEB-INF/classes"
	File dir = new File(base + "/WEB-INF/classes");

        // GS, Fix for the jar@lib directory problem.
        // Thanks for Kevin Jones for providing the fix.
	if( dir.exists() ) {
	    try {
		// Note: URLClassLoader in JDK1.2.2 doesn't work with file URLs
		// that contain '\' characters.  Insure only '/' is used.
		URL url=new URL( "file", null,
			dir.getAbsolutePath().replace('\\','/') + "/" );
		context.addClassPath( url );
	    } catch( MalformedURLException ex ) {
	    }
        }

        File f = new File(base + "/WEB-INF/lib");
	Vector jars = new Vector();
	getJars(jars, f);

	for(int i=0; i < jars.size(); ++i) {
	    String jarfile = (String) jars.elementAt(i);
	    File jf=new File(f, jarfile );
	    // Note: URLClassLoader in JDK1.2.2 doesn't work with file URLs
	    // that contain '\' characters.  Insure only '/' is used.
	    String absPath=jf.getAbsolutePath().replace('\\','/');
	    try {
		URL url=new URL( "file", null, absPath );
		context.addClassPath( url );
	    } catch( MalformedURLException ex ) {
	    }
	}

	// Add servlet.jar and jasper.jar
    }
    
    public void contextInit( Context context)
	throws TomcatException
    {
	if( debug>0 ) log( "Init context " + context.getPath());
        ContextManager cm = context.getContextManager();
	URL classP[]=context.getClassPath();
	if( debug>5 ) {
	    log("  Context classpath URLs:");
	    for (int i = 0; i < classP.length; i++)
		log("    " + classP[i].toString() );
	}

	DependManager dm=context.getDependManager();
	if( dm==null ) {
	    dm=new DependManager();
	    context.setDependManager( dm );
	}

	ClassLoader parent=null;
	if( useAL )
	    parent=cm.getParentLoader();
	else if( useNoParent )
	    parent=null;
	else
	    parent=this.getClass().getClassLoader();

	// Construct a class loader. Use URLClassLoader if Java2,
	// replacement ( SimpleClassLoader ) if not
	//	SimpleClassLoader loader=new SimpleClassLoader(classP, parent);
	ClassLoader loader=jdk11Compat.newClassLoaderInstance( classP, parent);
	DependClassLoader dcl=new DependClassLoader( dm, loader);
	if( debug > 0 )
	    log("Loader " + loader.getClass().getName() + " " + parent);
	context.setClassLoader( dcl );
	// support for jasper and other applications
	context.setAttribute( "org.apache.tomcat.classloader",
			      context.getClassLoader());
    }

    public void reload( Request req, Context context) throws TomcatException {
	log( "Reload event " + context.getPath() );
	
	ContextManager cm = context.getContextManager();
	URL urls[]=context.getClassPath();
	if( debug>5 ) {
	    log("  Context classpath URLs:");
	    for (int i = 0; i < urls.length; i++)
		log("    " + urls[i].toString() );
	}

	DependManager dm=new DependManager();
	context.setDependManager( dm );
	ClassLoader oldLoader=context.getClassLoader();
	int oldLoaderNote=cm.getNoteId( ContextManager.CONTAINER_NOTE,
					"oldLoader");
	context.getContainer().setNote( oldLoaderNote, oldLoader);
	
	ClassLoader parent=null;
	if( useAL )
	    parent=cm.getParentLoader();
	else if( useNoParent )
	    parent=null;
	else
	    parent=this.getClass().getClassLoader();

	// Construct a class loader. Use URLClassLoader if Java2,
	// replacement ( SimpleClassLoader ) if not
	//	SimpleClassLoader loader=new SimpleClassLoader(urls, parent);
	ClassLoader loader=jdk11Compat.newClassLoaderInstance( urls, parent);
	DependClassLoader dcl=new DependClassLoader( dm, loader);
	context.setClassLoader( dcl );
	context.setAttribute( "org.apache.tomcat.classloader",
			      ctx.getClassLoader());
    }

    // --------------------

    static final Jdk11Compat jdk11Compat=Jdk11Compat.getJdkCompat();
    
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