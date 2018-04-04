package org.apache.tomcat.modules.config;

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

package org.apache.tomcat.modules.aaa;

import org.apache.tomcat.core.*;
import java.io.*;
import java.net.*;
import java.util.*;
import java.security.*;

import org.apache.tomcat.util.*;
import org.apache.tomcat.util.log.*;

// don't extend - replace !

/**
 * Check ContextManager and set defaults for non-set properties
 *
 * @author costin@dnt.ro
 */
public final class DefaultCMSetter extends BaseInterceptor {
    /** Default work dir, relative to home
     */
    public static final String DEFAULT_WORK_DIR="work";

    public DefaultCMSetter() {
    }

    /** Adjust context manager paths.
     *  FIRST
     */
    public void engineInit( ContextManager cm )
    	throws TomcatException
    {
	// Adjust paths in CM
	String home=cm.getHome();
	if( home==null ) {
	    // try system property
	    home=System.getProperty(ContextManager.TOMCAT_HOME);
	}
	
	// Make it absolute
	if( home!= null ) {
	    home=FileUtil.getCanonicalPath( home );
	    cm.setHome( home );
	    log( "engineInit: home= " + home );
	}
	
	
	String installDir=cm.getInstallDir();
	if( installDir!= null ) {
	    installDir=FileUtil.getCanonicalPath( installDir );
	    cm.setInstallDir( installDir );
	    log( "engineInit: install= " + installDir );
	}

	// if only one is set home==installDir

	if( home!=null && installDir == null )
	    cm.setInstallDir( home );

	if( home==null && installDir != null )
	    cm.setHome( installDir );

	// if neither home or install is set,
	// and no system property, try "."
	if( home==null && installDir==null ) {
	    home=FileUtil.getCanonicalPath( "." );
	    installDir=home;

	    cm.setHome( home );
	    cm.setInstallDir( home );
	}

	// Adjust work dir
	String workDir=cm.getWorkDir();
	if( workDir==null ) {
	    workDir= DEFAULT_WORK_DIR;
	}

	if( ! FileUtil.isAbsolute( workDir )) {
	    workDir=FileUtil.
		getCanonicalPath(home + File.separator+
				 workDir);
	}
	cm.setWorkDir( workDir );
        initLoggers(cm.getLoggers());
    }

    /** Generate a random number
     */
    public void engineStart( ContextManager cm )
	throws TomcatException
    {
	try {
	    PrintWriter stopF=new PrintWriter
		(new FileWriter(cm.getHome() + "/conf/random.txt"));
	    stopF.println( Math.random() );
	    stopF.close();
	} catch( IOException ex ) {
	    log( "Can't create stop file " + ex );
	}
    }
    

    private void initLoggers(Hashtable Loggers){
        if( Loggers!=null ){
            Enumeration el=Loggers.elements();
            while( el.hasMoreElements()){
                Logger l=(Logger)el.nextElement();
                String path=l.getPath();
                if( path!=null ) {
                    File f=new File( path );
                    if( ! f.isAbsolute() ) {
                        File wd= new File(cm.getHome(), f.getPath());
                        l.setPath( wd.getAbsolutePath() );
                    }
                    // create the files, ready to log.
                }
                l.open();
            }
        }
    }

    /** Adjust paths
     */
    public void addContext( ContextManager cm, Context ctx)
	throws TomcatException
    {
	// adjust context paths and loggers

	String docBase=ctx.getDocBase();
	String absPath=ctx.getAbsolutePath();
	if( absPath==null ) {
	    if (FileUtil.isAbsolute( docBase ) )
		absPath=docBase;
	    else
		absPath = cm.getHome() + File.separator + docBase;
	    try {
		absPath = new File(absPath).getCanonicalPath();
	    } catch (IOException npe) {
	    }
	    ctx.setAbsolutePath( absPath );
	}
	if( debug > 0 ) {
	    String h=ctx.getHost();
	    log( "addContext: " + ((h==null) ? "":h) + ":" +
		 ctx.getPath() + " " + docBase + " " + absPath + " " +
		 cm.getHome());
	}
	
	// this would belong to a logger interceptor ?
	Log loghelper=ctx.getLog();
	Log loghelperServlet=ctx.getServletLog();
	
	if( loghelper!=null && loghelper.getLogger() != null )
	    cm.addLogger( loghelper.getLogger() );
	if( loghelperServlet != null &&
	    loghelperServlet.getLogger() != null)
	    cm.addLogger( loghelperServlet.getLogger() );
    }
}
