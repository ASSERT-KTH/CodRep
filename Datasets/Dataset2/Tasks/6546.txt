return context.getEngineHeader();

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


package org.apache.tomcat.core;

import org.apache.tomcat.util.*;
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

public class ServletContextFacade
implements ServletContext {

    private StringManager sm =
        StringManager.getManager(Constants.Package);
    private ContextManager contextM;
    private Context context;

    ServletContextFacade(ContextManager server, Context context) {
        this.contextM = server;
        this.context = context;
    }

    /**
     * The one package level hole through the facade for use by
     * the default servlet and invoker servlet
     */

    public Context getRealContext() {
	return context;
    }
    
    public Object getAttribute(String name) {
	Object o = context.getAttribute(name);
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
    
    public ServletContext getContext(String path) {

        // XXX
        // we need to check to see if the servlet should have
        // this sort of visibility into the inner workings of
        // the server. For now, we aren't running secure, so
        // it's no big deal, but later on, we'll want to throttle
        // access to contexts through this method

	if (! path.startsWith("/")) {
            String msg = sm.getString("sfcacade.context.iae", path);

	    throw new IllegalArgumentException(msg);
	}

        return contextM.getContextByPath(path).getFacade();
    }

    public int getMajorVersion() {
        return Constants.SERVLET_MAJOR;
    }

    public int getMinorVersion() {
        return Constants.SERVLET_MINOR;
    }

    public String getMimeType(String filename) {
        return context.getMimeMap().getContentTypeFor(filename);
    }

    public String getRealPath(String path) {
        String realPath = null;

        path = normPath(path);

        try {
            URL url = getResource(path);

            if (url != null) {
                if (url.getProtocol().equalsIgnoreCase("war")) {
		    if (context.isWARExpanded()) {
		        String spec = url.getFile();

			if (spec.startsWith("/")) {
			    spec = spec.substring(1);
			}

			int separator = spec.indexOf('!');
			URL warURL = null;

			if (separator > -1) {
			    warURL = new URL(spec.substring(0, separator++));
			}

			if (warURL.getProtocol().equalsIgnoreCase("file")) {
			    String s = context.getWorkDir() +"/" +
			        Constants.Context.WARExpandDir + path;
			    File f = new File(s);
			    String absPath = f.getAbsolutePath();
 
			    // take care of File.getAbsolutePath()
			    // troubles on jdk1.1.x/win

			    realPath = FileUtil.patch(absPath);
			} else if (url.getProtocol().equalsIgnoreCase("http")) {
			    // XXX
			    // need to support http docBase'd context
			}
		    } else {
                        realPath = url.toString();
		    }
		} else if (url.getProtocol().equalsIgnoreCase("http")) {
                    // XXX
                    // need to support http docBase'd context
                } else if (url.getProtocol().equalsIgnoreCase("file")) {
		    // take care of File.getAbsolutePath() troubles on
		    // jdk1.1.x/win

	            realPath = FileUtil.patch(url.getFile());
                }

	    }
        } catch (Exception e) {
        }

	return realPath;
    }

    public InputStream getResourceAsStream(String path) {
        InputStream is = null;

        try {
            URL url = getResource(path);
            URLConnection con = url.openConnection();

            con.connect();

            is = con.getInputStream();
        } catch (MalformedURLException e) {
        } catch (IOException e) {
        }

	return is;
    }

    public URL getResource(String path)
    throws MalformedURLException {
        URL url = null;

        if (path == null) {
            String msg = sm.getString("scfacade.getresource.npe");

            throw new NullPointerException(msg);
        } else if (! path.equals("") &&
	    ! path.startsWith("/")) {
	    String msg = sm.getString("scfacade.getresource.iae", path);

	    throw new IllegalArgumentException(msg);
	}

	// XXX
	// this could use a once over - after war perhaps


	
        URL docBase = context.getDocumentBase();

	Request lr = new Request();
	lr.setLookupPath( path );
	lr.setContext( getRealContext() );
	getRealContext().getContextManager().internalRequestParsing(lr);

	String mappedPath = path;

	if (lr != null &&
	    lr.getMappedPath() != null &&
	    lr.getMappedPath().trim().length() > 0) {
	    mappedPath = lr.getMappedPath();
	}

	if (path.equals("")) {
	    url = docBase;
	} else if (docBase.getProtocol().equalsIgnoreCase("war")) {
	    if (context.isWARExpanded()) {
		File f = new File(context.getWARDir().toString());
		String absPath = f.getAbsolutePath();

		// take care of File.getAbsolutePath() troubles
		// on jdk1.1.x/win

		absPath = FileUtil.patch(absPath);

                if (! absPath.startsWith("/")) {
                    absPath = "/" + absPath;
                }

		url = new URL("file://localhost" + absPath + "/" +
		    mappedPath);
	    } else {
                String documentBase = context.getDocumentBase().toString();

                if (documentBase.endsWith("/")) {
                    documentBase = documentBase.substring(0,
                        documentBase.length() - 1);
                }

                url = new URL(documentBase + "!" + mappedPath);
	    }
	} else {
            url = new URL(docBase.getProtocol(), docBase.getHost(),
                docBase.getPort(), docBase.getFile() + mappedPath);
        }

        return url;
    }

    public RequestDispatcher getRequestDispatcher(String path) {
	if (path == null ||
	    ! path.startsWith("/")) {
            String msg = sm.getString("scfacade.dispatcher.iae", path);

	    throw new IllegalArgumentException(msg);
	}

        RequestDispatcherImpl requestDispatcher =
	    new RequestDispatcherImpl(context);

	requestDispatcher.setPath(path);

        return (requestDispatcher.isValid()) ? requestDispatcher : null;
    }

    public RequestDispatcher getNamedDispatcher(String name) {
        if (name == null) {
	    String msg = sm.getString("scfacade.dispatcher.iae2", name);

	    throw new IllegalArgumentException(msg);
	}

        RequestDispatcherImpl requestDispatcher =
	    new RequestDispatcherImpl(context);

	requestDispatcher.setName(name);

	return (requestDispatcher.isValid()) ? requestDispatcher : null;
    }

    public String getServerInfo() {
        return contextM.getServerInfo();
    }

    public void log(String msg) {
        // Can't get this anymore - Harish. A stop-gap arrangement.
	// context.getLogModule().log(msg);
	
	System.err.println(msg);
    }

    public String getInitParameter(String name) {
        return context.getInitParameter(name);
    }

    public Enumeration getInitParameterNames() {
	return context.getInitParameterNames();
    }

    public void log(String msg, Throwable t) {
        // Can't get this anymore - Harish. A stop-gap arrangement.
        // context.getLogModule().log(msg, t);

	System.err.println(msg);
	t.printStackTrace(System.err);
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

    private String normPath(String path) {
        int i = -1;
 
        while ((i = path.indexOf('\\')) > -1) {
            String a = path.substring(0, i);
            String b = "";
 
            if (i < path.length() - 1) {
                b = path.substring(i + 1);
            } 
 
            path = a + "/" + b;
        }
 
        return path;
    }
}