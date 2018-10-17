public final class ServletContextFacade implements ServletContext {

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


package org.apache.tomcat.facade;

import org.apache.tomcat.core.*;
import org.apache.tomcat.util.res.StringManager;
import org.apache.tomcat.util.io.FileUtil;
import org.apache.tomcat.util.compat.*;
import java.io.*;
import java.net.*;
import java.util.*;
import javax.servlet.*;


/**
 * Implementation of the javax.servlet.ServletContext interface that
 * servlets see. Having this as a Facade class to the Context class
 * means that we can split up some of the work.
 *
 * @author James Duncan Davidson [duncan@eng.sun.com]
 * @author Jason Hunter [jch@eng.sun.com]
 * @author James Todd [gonzo@eng.sun.com]
 * @author Harish Prabandham
 */
final class ServletContextFacade implements ServletContext {
    // Use the strings from core
    private StringManager sm = StringManager.getManager("org.apache.tomcat.resources");
    private ContextManager contextM;
    private Context context;
    Jdk11Compat jdk11Compat=Jdk11Compat.getJdkCompat();
    Object accessControlContext=null;
    
    ServletContextFacade(ContextManager server, Context context) {
        this.contextM = server;
        this.context = context;
	try {
	    accessControlContext=jdk11Compat.getAccessControlContext();
	} catch( Exception ex) {
	    ex.printStackTrace();
	}
    }

    Context getRealContext() {
	return context;
    }

    // -------------------- Public facade methods --------------------
    public ServletContext getContext(String path) {
        Context target=contextM.getContext(context, path);
	return (ServletContext)target.getFacade();
    }

    
    public Object getAttribute(String name) {
        return context.getAttribute(name);
    }

    public Enumeration getAttributeNames() {
        return context.getAttributeNames();
    }

    public void setAttribute(String name, Object object) {
        context.setAttribute(name, object);
    }

    public void removeAttribute(String name) {
        context.removeAttribute(name);
    } 
    
    public int getMajorVersion() {
	// hardcoded - this facade is only for 2.2
        return 2;
    }

    public int getMinorVersion() {
        return 2;
    }

    public String getMimeType(String filename) {
        return context.getMimeMap().getContentTypeFor(filename);
    }

    // Specific to servlet version and interpretation.
    public String getRealPath(String path) {
 	return FileUtil.safePath( context.getAbsolutePath(),
				  path);
    }

    public InputStream getResourceAsStream(String path) {
        InputStream is = null;
        try {
            URL url = getResource(path);
	    if( url==null ) return null;
            URLConnection con = url.openConnection();
            con.connect();
            is = con.getInputStream();
        } catch (MalformedURLException e) {
        } catch (IOException e) {
        }
	return is;
    }

    public URL getResource(String rpath) throws MalformedURLException {
	if (rpath == null) return null;

	String absPath=context.getAbsolutePath();
	String realPath=FileUtil.safePath( absPath, rpath);
	if( realPath==null ) {
	    log( "Unsafe path " + absPath + " " + rpath );
	    return null;
	}
	File f=new File( realPath );
	if( ! f.exists() ) {
	    return null;
	}
	try {
            return new URL("file", null, 0,realPath );
	} catch( IOException ex ) {
	    log("getting resource " + rpath, ex);
	    return null;
	}
    }

    public RequestDispatcher getRequestDispatcher(String path) {
	if ( path == null  || ! path.startsWith("/")) {
	    return null; // spec say "return null if we can't return a dispather
	}
	RequestDispatcherImpl rD=new RequestDispatcherImpl( context, accessControlContext);
	rD.setPath( path );
	
	return rD;
    }

    public RequestDispatcher getNamedDispatcher(String name) {
        if (name == null)
	    return null;

	// We need to do the checks
	Handler wrapper = context.getServletByName( name );
	if (wrapper == null)
	    return null;
	RequestDispatcherImpl rD=new RequestDispatcherImpl( context, accessControlContext );
	rD.setName( name );

	return rD;
    }

    public String getServerInfo() {
        return context.getEngineHeader();
    }

    public void log(String msg) {
	context.logServlet( msg, null );
    }

    public String getInitParameter(String name) {
        return context.getInitParameter(name);
    }

    public Enumeration getInitParameterNames() {
	return context.getInitParameterNames();
    }

    public void log(String msg, Throwable t) {
	context.logServlet(msg, t);
    }

    /**
     *
     * @deprecated This method is deprecated in the
     *             javax.servlet.ServletContext interface
     */
    public void log(Exception e, String msg) {
        log(msg, e);
    }

    /**
     *
     * @deprecated This method is deprecated in the
     *             javax.servlet.ServletContext interface
     */
    public Servlet getServlet(String name) throws ServletException {
        return null;
    }

    /**
     * This method has been deprecated in the public api and always
     * return an empty enumeration.
     *
     * @deprecated
     */
    public Enumeration getServlets() {
	// silly hack to get an empty enumeration
	Vector v = new Vector();
	return v.elements();
    }
    
    /**
     * This method has been deprecated in the public api and always
     * return an empty enumeration.
     *
     * @deprecated
     */
    public Enumeration getServletNames() {
	// silly hack to get an empty enumeration
	Vector v = new Vector();
	return v.elements();
    }

}