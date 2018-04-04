fixJDKContextClassLoader(req.getContext());

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

package org.apache.tomcat.modules.generators;

import org.apache.tomcat.core.*;
import org.apache.tomcat.util.*;
import org.apache.tomcat.util.compat.*;
import java.io.*;
import java.net.*;
import java.util.*;

/**
 *  JDK1.2 specific options. Fix the class loader, etc.
 */
public final class Jdk12Interceptor extends  BaseInterceptor {
    private ContextManager cm;
    private int debug=0;

    public Jdk12Interceptor() {
    }

    public void preServletInit( Context ctx, Handler sw )
	throws TomcatException
    {
	fixJDKContextClassLoader(ctx);
    }

    public int preInitCheck( Request req, Handler sw )
	throws TomcatException
    {
	fixJDKContextClassLoader(ctx);
	return 0;
    }

    /** Servlet Destroy  notification
     */
    public void preServletDestroy( Context ctx, Handler sw )
	throws TomcatException
    {
	fixJDKContextClassLoader(ctx);
    }

    public void postServletDestroy( Context ctx, Handler sw )
	throws TomcatException
    {
	jdk11Compat.setContextClassLoader(this.getClass().getClassLoader());
    }
    
    public void postServletInit( Context ctx, Handler sw )
	throws TomcatException
    {
	jdk11Compat.setContextClassLoader(this.getClass().getClassLoader());
    }
    
    public int postInitCheck( Request req, Handler sw )
	throws TomcatException
    {
	jdk11Compat.setContextClassLoader(this.getClass().getClassLoader());
	return 0;
    }
    /** Called before service method is invoked. 
     */
    public int preService(Request request, Response response) {
	if( request.getContext() == null ) return 0;
	// fix for 1112
	Request child=request.getChild();
	if( child!=null ) {
	    request=child;
	}
	fixJDKContextClassLoader(request.getContext());
	return 0;
    }

    public int postService(Request request, Response response) {
	Request child=request.getChild();
	if( child==null ) return 0;

	// after include, reset the class loader
	// fix for 1112
	request=child.getParent();
	if( request != null )
	    fixJDKContextClassLoader(request.getContext());
	else
	    jdk11Compat.setContextClassLoader(this.getClass().getClassLoader());
	return 0;
    }

    static Jdk11Compat jdk11Compat=Jdk11Compat.getJdkCompat();
    
    
    // Before we do init() or service(), we need to do some tricks
    // with the class loader - see bug #116.
    // some JDK1.2 code will not work without this fix
    // we save the originalCL because we might be in include
    // and we need to revert to it when we finish
    // that will set a new (JDK)context class loader, and return the old one
    // if we are in JDK1.2
    // XXX move it to interceptor !!!
    final private void fixJDKContextClassLoader( Context ctx ) {
	final ClassLoader cl=ctx.getClassLoader();
	if( cl==null ) {
	    log("ERROR: Jdk12Interceptor: classloader==null");
	    return;
	}
	if( cl == jdk11Compat.getContextClassLoader() )
	    return; // nothing to do - or in include if same context
	
	jdk11Compat.setContextClassLoader(cl);
    }
    
}