import org.apache.tomcat.util.io.FileUtil;

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
 * Will manage a repository of .war files, expanding them automatically
 * and eventually re-deploying them.
 *
 * Based on the original AutoSetup.
 * 
 * @author cmanolache@yahoo.com
 */
public class AutoDeploy extends BaseInterceptor {
    // Afer DefaultCMSettup, before any other interceptor that needs contexts
    Hashtable hosts=new Hashtable();

    String src="webapps";
    String dest="webapps";

    public AutoDeploy() {
    }

    //-------------------- Config --------------------
    
    /**
     *  Directory where war files are deployed
     *  Defaults to TOMCAT_HOME/webapps.
     */
    public void setSource( String d ) {
	src=d;
    }

    /**
     *  Directory where war files are deployed
     *  Defaults to TOMCAT_HOME/webapps.
     */
    public void setTarget( String d ) {
	dest=d;
    }

    /**
     * "Flat" directory support - no virtual host support.
     *  XXX Not implemented - only true.
     */
    public void setFlat( boolean b ) {
    }

    /**
     *  Re-deploy the context if the war file is modified.
     *  XXX Not implemented.
     */
    public void setRedeploy( boolean b ) {

    }
    
    //-------------------- Implementation --------------------
    
    /**
     *  Find all wars, expand them, register dependency.
     */
    public void engineInit(ContextManager cm) throws TomcatException {

	// For all contexts in <server.xml > or loaded by differen means,
	// check if the docBase ends with .war - and expand it if so,
	// after that replace the docBase with the dir. See bug 427.
	/* XXX not ready yet.
	Enumeration loadedCtx=cm.getContexts();
	while( loadedCtx.hasMoreElements() ) {
	    Context ctx=(Context)loadedCtx.nextElement();
	    String docBase=ctx.getDocBase();
	    if( docBase.endsWith( ".war" ) ) {
		expandWar( ctx, docBase);
	    }
	}
	*/
	
	// expand all the wars from srcDir ( webapps/*.war ).
	String home=cm.getHome();

	File webappS;
	File webappD;
	
	if( src.startsWith( "/" ) ) 
	    webappS=new File(src);
	else
	    webappS=new File(home + "/" + src);

	if( dest.startsWith( "/" ) ) 
	    webappD=new File(dest);
	else
	    webappD=new File(home + "/" + dest);
	
	if (! webappD.exists() || ! webappD.isDirectory() ||
	    ! webappS.exists() || ! webappS.isDirectory()) {
	    log("Source or destination missing ");
	    return ; // nothing to set up
	}
	
	String[] list = webappS.list();

	for (int i = 0; i < list.length; i++) {
	    String name = list[i];
	    File f=new File( webappS, name );
	    if( name.endsWith(".war") ) {
		expandWar( webappS, webappD, name );
	    }
	}
    }

    /** Auto-expand wars
     */
    private void expandWar( File srcD, File destD, String name ) {
	String fname=name.substring(0, name.length()-4);

	File appDir=new File( destD, fname);
	if( ! appDir.exists() ) {
	    // no check if war file is "newer" than directory 
	    // To update you need to "remove" the context first!!!
	    appDir.mkdirs();
	    // Expand war file
	    try {
		FileUtil.expand(srcD.getAbsolutePath() + "/" + name,
				destD.getAbsolutePath() + "/" + fname );
	    } catch( IOException ex) {
		log("expanding webapp " + name, ex);
		// do what ?
	    }
	}
    }
}
