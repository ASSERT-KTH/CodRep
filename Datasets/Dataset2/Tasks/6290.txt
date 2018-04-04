log("Creating work dir " + ctx.getWorkDir());

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
import java.io.*;
import java.net.*;
import java.util.*;

/**
 * Handles work dir setup/removal
 *
 * @author costin@dnt.ro
 */
public class WorkDirInterceptor extends BaseInterceptor {
    boolean cleanWorkDir=false;
    
    public WorkDirInterceptor() {
    }

    /** IMHO this shouldn't be used - if true, we'll loose
	all jsp compiled files. The workdir is the only directory
	where the servlet is allowed to write anyway ( if policy
	is used ).

	In case this proves to be usefull, the property should
	belong to context.
    */
    public void setCleanWorkDir( boolean b ) {
	cleanWorkDir=b;
    }
	
    public void contextInit(Context ctx) {
	if( ctx.getWorkDir() == null)
	    setWorkDir(ctx);

	if (! ctx.getWorkDir().exists()) {
	    //log  System.out.println("Creating work dir " + ctx.getWorkDir() );
	    ctx.getWorkDir().mkdirs();
	}
	ctx.setAttribute(Constants.ATTRIB_WORKDIR1, ctx.getWorkDir());
	ctx.setAttribute(Constants.ATTRIB_WORKDIR , ctx.getWorkDir());

	if ( cleanWorkDir ) {
	    clearDir(ctx.getWorkDir() );
	}
    }

    public void contextShutdown( Context ctx ) {
	if ( cleanWorkDir ) {
	    clearDir(ctx.getWorkDir());
	}
    }

    // -------------------- Implementation --------------------

    /** Encoded ContextManager.getWorkDir() + host + port + path
     */
    private void setWorkDir(Context ctx ) {
	ContextManager cm=ctx.getContextManager();

	StringBuffer sb=new StringBuffer();
	sb.append(cm.getWorkDir());
	sb.append(File.separator);
	String host=ctx.getHost();
	if( host==null ) 
	    sb.append(cm.getHostName() );
	else
	    sb.append( host );
	sb.append("_").append(cm.getPort());
	sb.append(URLEncoder.encode( ctx.getPath() ));
	
	ctx.setWorkDir( new File(sb.toString()));
    }
    

    private void clearDir(File dir) {
        String[] files = dir.list();

        if (files != null) {
	    for (int i = 0; i < files.length; i++) {
	        File f = new File(dir, files[i]);

	        if (f.isDirectory()) {
		    clearDir(f);
	        }

	        try {
	            f.delete();
	        } catch (Exception e) {
	        }
	    }

	    try {
	        dir.delete();
	    } catch (Exception e) {
	    }
        }
    }


	
}