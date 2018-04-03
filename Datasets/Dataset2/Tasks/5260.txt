public int engineInit(ContextManager cm) {

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

import org.apache.tomcat.task.Expand;

/**
 *  Prepare a context manager - expand wars in webapps and
 *  automaticly install contexts
 *
 *  This happens _before_ Context.init()  
 * 
 * @author costin@dnt.ro
 */
public class AutoSetup { //  implements TomcatHandler

    public AutoSetup() {
    }
	
    public int handleContextManagerInit(ContextManager cm) {
	String home=cm.getHome();
	File webappD=new File(home + "/webapps");
	if (! webappD.exists() || ! webappD.isDirectory())
	    return 0; // nothing to set up

	String[] list = webappD.list();
	for (int i = 0; i < list.length; i++) {
	    String name = list[i];
	    if( name.endsWith(".war") ) {
		String fname=name.substring(0, name.length()-4);
		File appDir=new File( home + "/webapps/" + fname);
		if( ! appDir.exists() ) {
		    // no check if war file is "newer" than directory 
		    // To update you need to "remove" the context first!!!
		    appDir.mkdirs();
		    // Expand war file
		    Expand expand=new Expand();
		    expand.setSrc( home + "/webapps/" + name );
		    expand.setDest( home + "/webapps/" + fname);
		    try {
			expand.execute();
		    } catch( IOException ex) {
			ex.printStackTrace();
			// do what ?
		    }
		}
		// we will add the directory to the path
		name=fname;
	    }
	    
	    // XXX XXX Add a .xml case
	    // If a "path.xml" file is found in webapps/, it will be loaded
	    // as a <context> fragment ( what will allow setting options
	    // for contexts or automatic config for contexts with different base)
	    
	    // Decode path

	    // Path will be based on the War name
	    // Current code supports only one level, we
	    // need to decide an encoding scheme for multi-level
	    String path="/" + name; // decode(name)
	    //	    System.out.println("XXX : " + path );
	    if( path.equals("/ROOT") )
		path="";
	    
	    if( cm.getContext(path) == null ) {
		// if no explicit set up
		System.out.println("Automatic addContext( " + path + ", webapps/" + name + ")");
		Context ctx=new Context();
		ctx.setContextManager( cm );
		ctx.setPath(path);
		ctx.setDocBase(  "webapps/" + name);
		cm.addContext(ctx);
	    } else {
		//System.out.println("Already set up: " + path + " " + cm.getContext(path));
	    }

		
	}

	return 0;
    }
}