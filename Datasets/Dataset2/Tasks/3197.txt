ServletWrapper  result = container.getServletByName(servletName);

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

import org.apache.tomcat.server.*;
import org.apache.tomcat.util.*;
import org.apache.tomcat.deployment.*;
import java.io.*;
import java.net.*;
import java.util.*;
import javax.servlet.http.*;

/**
 * 
 * @author James Duncan Davidson [duncan@eng.sun.com]
 * @author James Todd [gonzo@eng.sun.com]
 * @author Jason Hunter [jch@eng.sun.com]
 * @author Harish Prabandham
 */

//
// WARNING: Some of the APIs in this class are used by J2EE. 
// Please talk to harishp@eng.sun.com before making any changes.
//

public class Context {
    
    private StringManager sm =
        StringManager.getManager(Constants.Package);
    private boolean initialized = false;
    private Server server;
    private String description = null;
    private boolean isDistributable = false;
    private String engineHeader = null;
    private Container container = new Container(this);
    private ClassLoader classLoader = null;
    private String classPath = ""; // classpath used by the classloader.
    //private Hashtable sessions = new Hashtable();
    private ServerSessionManager sessionManager =
	ServerSessionManager.getManager();
    private ServletContextFacade contextFacade;
    private Hashtable initializationParameters = new Hashtable();
    private Hashtable attributes = new Hashtable();
    private MimeMap mimeTypes = new MimeMap();
    private int sessionTimeOut = -1;
    private Vector welcomeFiles = new Vector();
    private Hashtable errorPages = new Hashtable();
    private Hashtable loadableServlets = new Hashtable();
    private URL docBase;
    private String path = "";
    //private String sessionCookieName;
    private boolean isInvokerEnabled = false;
    private File workDir =
        new File(System.getProperty("user.dir", ".") +
            System.getProperty("file.separator") + Constants.WorkDir);
    private boolean isWorkDirPersistent = false;
    private File warDir = null;
    private boolean isWARExpanded = false;
    private boolean isWARValidated = false;
    private Vector initInterceptors = new Vector();
    private Vector serviceInterceptors = new Vector();
    private Vector destroyInterceptors = new Vector();
    private RequestSecurityProvider rsProvider =
        DefaultRequestSecurityProvider.getInstance();

    public Context() {
    }
	
    public Context(Server server, String path) {
        this.server = server;
	this.path = path;

        contextFacade = new ServletContextFacade(server, this);

	//String s = Double.toString(Math.abs(Math.random()));
	//s = s.substring(2, s.length());
	//sessionCookieName="SESSION" + s + "ID";

	Properties props = getProperties(Constants.Property.Name);

	/*
	 * Whoever modifies this needs to check this modification is
	 * ok with the code in com.jsp.runtime.ServletEngine or talk
	 * to akv before you check it in. 
	 */

	engineHeader = props.getProperty(
	    Constants.Property.EngineHeader,
	    Constants.Context.EngineHeader + "; Java " +
	    System.getProperty("java.version") + "; " +
	    System.getProperty("os.name") + " " +
	    System.getProperty("os.version") + " " +
	    System.getProperty("os.arch") + "; java.vendor=" +
	    System.getProperty("java.vendor") + ")");
    }

    public String getEngineHeader() {
        return engineHeader;
    }
    
    public String getPath() {
	return path;
    }

    public void setPath(String path) {
	this.path = path;
    }

    public boolean isInvokerEnabled() {
        return isInvokerEnabled;
    }

    public void setInvokerEnabled(boolean isInvokerEnabled) {
        this.isInvokerEnabled = isInvokerEnabled;
    }

    public void setRequestSecurityProvider(
	RequestSecurityProvider rsProvider) {
	this.rsProvider = rsProvider;
    }

    public RequestSecurityProvider getRequestSecurityProvider() {
	return this.rsProvider;
    }

    public File getWorkDir() {
        return this.workDir;
    }

    public void setWorkDir(String workDir, boolean isWorkDirPersistent) {
        File f = null;

        try {
	    f = new File(workDir);
	} catch (Exception e) {
	}

	setWorkDir(f, isWorkDirPersistent);
    }

    public void setWorkDir(File workDir, boolean isWorkDirPersistent) {
        this.isWorkDirPersistent = isWorkDirPersistent;

	if (workDir == null) {
	    workDir = this.workDir;
	}

	if (! isWorkDirPersistent) {
	    clearDir(workDir);
        }

	this.workDir = workDir;

	setAttribute(Constants.Attribute.WorkDirectory, this.workDir);
    }

    public boolean isWorkDirPersistent() {
        return this.isWorkDirPersistent;
    }

    File getWARDir() {
        return this.warDir;
    }

    public boolean isWARExpanded() {
        return this.isWARExpanded;
    }

    public void setIsWARExpanded(boolean isWARExpanded) {
        this.isWARExpanded = isWARExpanded;
    }

    public boolean isWARValidated() {
        return this.isWARValidated;
    }

    public void setIsWARValidated(boolean isWARValidated) {
        this.isWARValidated = isWARValidated;
    }

    public ClassLoader getClassLoader() {
      return this.classLoader;
    }

    public void setClassLoader(ClassLoader classLoader) {
      this.classLoader = classLoader;
    }

    public String getClassPath() {
        String cp = this.classPath.trim();
        String servletLoaderClassPath =
            this.container.getLoader().getClassPath();

        if (servletLoaderClassPath != null &&
            servletLoaderClassPath.trim().length() > 0) {
            cp += ((cp.length() > 0) ? File.pathSeparator : "") +
                servletLoaderClassPath;
        }

        return cp;
    }
    
    public void setClassPath(String classPath) {
        if (this.classPath.trim().length() > 0) {
	    this.classPath += File.pathSeparator;
	}

        this.classPath += classPath;
    }
    
    /**
     * Adds an interceptor for init() method.
     * If Interceptors a, b and c are added to a context, the
     * implementation would guarantee the following call order:
     * (no matter what happens, for eg.Exceptions ??)
     *
     * <P>
     * <BR> a.preInvoke(...)
     * <BR> b.preInvoke(...)
     * <BR> c.preInvoke(...)
     * <BR> init()
     * <BR> c.postInvoke(...)
     * <BR> b.postInvoke(...)
     * <BR> a.postInvoke(...)
     */

    public void addInitInterceptor(LifecycleInterceptor interceptor) {
	initInterceptors.addElement(interceptor);
    }

    /**
     * Adds an interceptor for destroy() method.
     * If Interceptors a, b and c are added to a context, the
     * implementation would guarantee the following call order:
     * (no matter what happens, for eg.Exceptions ??)
     *
     * <P>
     * <BR> a.preInvoke(...)
     * <BR> b.preInvoke(...)
     * <BR> c.preInvoke(...)
     * <BR> destroy()
     * <BR> c.postInvoke(...)
     * <BR> b.postInvoke(...)
     * <BR> a.postInvoke(...)
     */

    public void addDestroyInterceptor(LifecycleInterceptor interceptor) {
	destroyInterceptors.addElement(interceptor);
    }

    /**
     * Adds an interceptor for service() method.
     * If Interceptors a, b and c are added to a context, the
     * implementation would guarantee the following call order:
     * (no matter what happens, for eg.Exceptions ??)
     *
     * <P>
     * <BR> a.preInvoke(...)
     * <BR> b.preInvoke(...)
     * <BR> c.preInvoke(...)
     * <BR> service()
     * <BR> c.postInvoke(...)
     * <BR> b.postInvoke(...)
     * <BR> a.postInvoke(...)
     */

    public void addServiceInterceptor(ServiceInterceptor interceptor) {
	serviceInterceptors.addElement(interceptor);
    }

    Vector getInitInterceptors() {
	return initInterceptors;
    }

    Vector getDestroyInterceptors() {
	return destroyInterceptors;
    }

    Vector getServiceInterceptors() {
	return serviceInterceptors;
    }
    
    /**
     * Initializes this context to take on requests. This action
     * will cause the context to load it's configuration information
     * from the webapp directory in the docbase.
     *
     * <p>This method may only be called once and must be called
     * before any requests are handled by this context.
     */
    
    public synchronized void init() {
	// check to see if we've already been init'd

	if (this.initialized) {
	    String msg = sm.getString("context.init.alreadyinit");

	    throw new IllegalStateException(msg);
	}

	this.initialized = true;
	
	if (this.docBase == null) {
	    //String msg = sm.getString("context.init.nodocbase");
	    //throw new IllegalStateException(msg);

	    // XXX
	    // for now we are going to pretend it doens't matter
	}

	// set up work dir attribute

	if (this.workDir != null) {
	    setAttribute(Constants.Context.Attribute.WorkDir.Name,
	        this.workDir);

	    if (! this.workDir.exists()) {
	        this.workDir.mkdirs();
	    }
	}

	// expand WAR

	URL servletBase = this.docBase;

	if (docBase.getProtocol().equalsIgnoreCase(
	    Constants.Request.WAR)) {
	    if (isWARExpanded()) {
	        this.warDir = new File(getWorkDir(),
		    Constants.Context.WARExpandDir);

		if (! this.warDir.exists()) {
		    this.warDir.mkdirs();

		    try {
		        WARUtil.expand(this.warDir, getDocumentBase());
		    } catch (MalformedURLException mue) {
		    } catch (IOException ioe) {
		    }

		    try {
                        servletBase = URLUtil.resolve(this.warDir.toString());
		    } catch (Exception e) {
		    }
		}
	    }
	}

        this.container.setServletBase(servletBase);

        for (int i = 0; i < Constants.Context.CLASS_PATHS.length; i++) {
            this.container.addClassPath(Constants.Context.CLASS_PATHS[i]);
	}

        for (int i = 0; i < Constants.Context.LIB_PATHS.length; i++) {
            this.container.addLibPath(Constants.Context.LIB_PATHS[i]);
	}

	// process base configuration

	try {
	    Class webApplicationDescriptor = Class.forName(
	        "org.apache.tomcat.deployment.WebApplicationDescriptor");
	    InputStream is =
	        webApplicationDescriptor.getResourceAsStream(
	            org.apache.tomcat.deployment.Constants.ConfigFile);
	    String msg = sm.getString("context.getConfig.msg", "default");

    	    System.out.println(msg);

	    processWebApp(is, true);
	} catch (Exception e) {
	    String msg = sm.getString("context.getConfig.e", "default");

	    System.out.println(msg);
	}

	// process webApp configuration

	String s = docBase.toString();

	if (docBase.getProtocol().equalsIgnoreCase(
	    Constants.Request.WAR)) {
	    if (s.endsWith("/")) {
	        s = s.substring(0, s.length() - 1);
	    }

	    s += "!/";
	}

	URL webURL = null;

	try {
	    webURL = new URL(s + Constants.Context.ConfigFile);

	    InputStream is = webURL.openConnection().getInputStream();
	    String msg = sm.getString("context.getConfig.msg",
	        webURL.toString());

	    System.out.println(msg);

	    processWebApp(is);
	} catch (Exception e) {
	    String msg = sm.getString("context.getConfig.e",
	        (webURL != null) ? webURL.toString() : "not available");

            // go silent on this one
	    // System.out.println(msg);
	}

	if (! this.isInvokerEnabled) {
	    // Put in a special "no invoker" that handles
	    // /servlet requests and explains why no servlet
	    // is being invoked

	    this.container.addServlet(Constants.Servlet.NoInvoker.Name,
	        Constants.Servlet.NoInvoker.Class);
	    this.container.addMapping(Constants.Servlet.NoInvoker.Name,
	        Constants.Servlet.NoInvoker.Map);
	}

	// load-on-startup

        if (! loadableServlets.isEmpty()) {
	    loadServlets();
        }
    }

    public void shutdown() {
	// shut down container

	container.shutdown();

	// shut down any sessions

	sessionManager.removeApplicationSessions(this);

	if (! isWorkDirPersistent) {
            clearDir(workDir);
	}

	System.out.println("Context: " + this + " down");
    }
    
    public Enumeration getWelcomeFiles() {
	return welcomeFiles.elements();
    }
    
    public String getInitParameter(String name) {
        return (String)initializationParameters.get(name);
    }

    public Enumeration getInitParameterNames() {
        return initializationParameters.keys();
    }

    public Object getAttribute(String name) {
        if (name.equals("org.apache.tomcat.jsp_classpath"))
	  return getClassPath();
	else if(name.equals("org.apache.tomcat.classloader")) {
	  return this.container.getLoader();
        }else {
            Object o = attributes.get(name);
            return attributes.get(name);
        }
    }

    public Enumeration getAttributeNames() {
        return attributes.keys();
    }

    public void setAttribute(String name, Object object) {
        attributes.put(name, object);
    }

    public void removeAttribute(String name) {
        attributes.remove(name);
    }
    
    public URL getDocumentBase() {
        return docBase;
    }

    public void setDocumentBase(URL docBase) {
	String file = docBase.getFile();

	if (! file.endsWith("/")) {
	    try {
		docBase = new URL(docBase.getProtocol(),
                    docBase.getHost(), docBase.getPort(), file + "/");
	    } catch (MalformedURLException mue) {
		System.out.println("SHOULD NEVER HAPPEN: " + mue);
	    }
	}

	this.docBase = docBase;
    }

    public String getDescription() {
        return this.description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public boolean isDistributable() {
        return this.isDistributable;
    }

    public void setDistributable(boolean isDistributable) {
        this.isDistributable = isDistributable;
    }


    public int getSessionTimeOut() {
        return this.sessionTimeOut;
    }

    public void setSessionTimeOut(int sessionTimeOut) {
        this.sessionTimeOut = sessionTimeOut;
    }
    
    public MimeMap getMimeMap() {
        return mimeTypes;
    }

    public String getErrorPage(int errorCode) {
        return getErrorPage(String.valueOf(errorCode));
    }

    public String getErrorPage(String errorCode) {
        return (String)errorPages.get(errorCode);
    }

    public Container getContainer() {
	return container;
    }

    ServletContextFacade getFacade() {
        return contextFacade;
    }

    public void handleRequest(Request request, Response response)
    throws IOException {
	// XXX
	// make sure we are init'd or throw an illegal state exception

	request.setContext(this);
	request.setResponse(response);
	
	// look for session id -- cookies only right now

	ServerSession session =
	    sessionManager.getServerSession(request, response, false);

	if (session != null) {
	    session.accessed();

	    ApplicationSession appSession =
	        session.getApplicationSession(this, false);

	    if (appSession != null) {
	        appSession.accessed();
	    }
	}

	request.setServerSession(session);  // may be null

	LookupResult result =
	    container.lookupServlet(request.getLookupPath());
	
	request.setServletPath(result.getServletPath());
	request.setPathInfo(result.getPathInfo());

        if (result.getResolvedServlet() != null) {
            request.setAttribute(Constants.Attribute.RESOLVED_SERVLET,
                result.getResolvedServlet());
        } else if (result.getMappedPath() != null) {
            request.setAttribute(Constants.Attribute.RESOLVED_SERVLET,
                result.getMappedPath());
        } else {
            request.removeAttribute(Constants.Attribute.RESOLVED_SERVLET);
        }

	result.getWrapper().handleRequest(request.getFacade(),
            response.getFacade());

	//ServletWrapper wrap = container.resolveServlet(request);
	
	// XXX
	// we want to be sure to handle any IOExceptions here
	// and log 'em -- also an UnavailableExceptions would be
	// trapped here.
	
	//wrap.handleRequest(request.getFacade(), response.getFacade());
    }

    private Properties getProperties(String propertyFileName) {
        Properties props = new Properties();

        try {
	    props.load(this.getClass().getResourceAsStream(propertyFileName));
	} catch (IOException ioe) {
	}

	return props;
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

    private void processWebApp(InputStream is) {
        processWebApp(is, false);
    }

    private void processWebApp(InputStream is, boolean internal) {
        if (is != null) {
	    try {
	        WebApplicationDescriptor webDescriptor =
		    (new WebApplicationReader()).getDescriptor(is,
		        new WebDescriptorFactoryImpl(),
			isWARValidated());

		processDescription(webDescriptor.getDescription());
		processDistributable(webDescriptor.isDistributable());
		processInitializationParameters(
		    webDescriptor.getContextParameters());
		processSessionTimeOut(webDescriptor.getSessionTimeout());
		processServlets(webDescriptor.getWebComponentDescriptors());
		processMimeMaps(webDescriptor.getMimeMappings());
		processWelcomeFiles(webDescriptor.getWelcomeFiles(),
                    internal);
		processErrorPages(webDescriptor.getErrorPageDescriptors());
	    } catch (Throwable e) {
                String msg = "config parse: " + e.getMessage();

                System.out.println(msg);
	    }
	}
    }

    private void processDescription(String description) {
        this.description = description;
    }

    private void processDistributable(boolean isDistributable) {
        this.isDistributable = isDistributable;
    }

    private void processInitializationParameters(
	Enumeration contextParameters) {
        while (contextParameters.hasMoreElements()) {
	    ContextParameter contextParameter =
	        (ContextParameter)contextParameters.nextElement();
	    initializationParameters.put(contextParameter.getName(),
	        contextParameter.getValue());
	}
    }

    private void processSessionTimeOut(int sessionTimeOut) {
        this.sessionTimeOut = sessionTimeOut;
    }

    private void processServlets(Enumeration servlets) {
        // XXX
        // oh my ... this has suddenly turned rather ugly
        // perhaps the reader should do this normalization work

        while (servlets.hasMoreElements()) {
	    WebComponentDescriptor webComponentDescriptor =
	        (WebComponentDescriptor)servlets.nextElement();
	    String name = webComponentDescriptor.getCanonicalName();
	    String description = webComponentDescriptor.getDescription();
	    String resourceName = null;
	    boolean removeResource = false;

	    if (webComponentDescriptor instanceof ServletDescriptor) {
		resourceName =
		    ((ServletDescriptor)webComponentDescriptor).getClassName();

		if (container.containsServletByName(name)) {
		    String msg = sm.getString("context.dd.dropServlet",
		        name + "(" + resourceName + ")" );

		    System.out.println(msg);
		    
		    removeResource = true;
		    container.removeServletByName(name);
		}

		container.addServlet(name, resourceName, description);
	    } else if (webComponentDescriptor instanceof JspDescriptor) {
		resourceName =
		    ((JspDescriptor)webComponentDescriptor).getJspFileName();

		if (! resourceName.startsWith("/")) {
		    resourceName = "/" + resourceName;
		}

		if (container.containsJSP(resourceName)) {
		    String msg = sm.getString("context.dd.dropServlet",
		        resourceName);

		    System.out.println(msg);

		    removeResource = true;
		    container.removeJSP(resourceName);
		}

		container.addJSP(name, resourceName, description);
	    }

	    if (removeResource) {
	        Enumeration enum = loadableServlets.keys();

		while (enum.hasMoreElements()) {
		    Integer key = (Integer)enum.nextElement();
		    Vector v = (Vector)loadableServlets.get(key);

		    Enumeration e = v.elements();
		    Vector buf = new Vector();

		    while (e.hasMoreElements()) {
		        String servletName = (String)e.nextElement();

			if (container.containsServletByName(servletName)) {
			    buf.addElement(servletName);
			}
		    }

		    loadableServlets.put(key, buf);
		}
	    }

	    int loadOnStartUp = webComponentDescriptor.getLoadOnStartUp();

            if (loadOnStartUp > Integer.MIN_VALUE) {
	        Integer key = new Integer(loadOnStartUp);
		Vector v = (Vector)((loadableServlets.containsKey(key)) ?
		    loadableServlets.get(key) : new Vector());

		v.addElement(name);
		loadableServlets.put(key, v);
	    }

	    Enumeration enum =
	        webComponentDescriptor.getInitializationParameters();
	    Hashtable initializationParameters = new Hashtable();

	    while (enum.hasMoreElements()) {
	        InitializationParameter initializationParameter =
		    (InitializationParameter)enum.nextElement();

		initializationParameters.put(
		    initializationParameter.getName(),
		    initializationParameter.getValue());
	    }

	    container.setServletInitParams(
	        webComponentDescriptor.getCanonicalName(),
		initializationParameters);

	    enum = webComponentDescriptor.getUrlPatterns();

	    while (enum.hasMoreElements()) {
	        String mapping = (String)enum.nextElement();

		if (! mapping.startsWith("*.") &&
		    ! mapping.startsWith("/")) {
		    mapping = "/" + mapping;
		}

		if (! container.containsServlet(mapping) &&
		    ! container.containsJSP(mapping)) {
		    if (container.containsMapping(mapping)) {
		        String msg = sm.getString("context.dd.dropMapping",
			    mapping);

			System.out.println(msg);

			container.removeMapping(mapping);
		    }

                    container.addMapping(name, mapping);
		} else {
		    String msg = sm.getString("context.dd.ignoreMapping",
		        mapping);

		    System.out.println(msg);
		}
	    }
	}
    }

    private void processMimeMaps(Enumeration mimeMaps) {
        while (mimeMaps.hasMoreElements()) {
	    MimeMapping mimeMapping = (MimeMapping)mimeMaps.nextElement();

	    this.mimeTypes.addContentType(
	        mimeMapping.getExtension(), mimeMapping.getMimeType());
	}
    }

    private void processWelcomeFiles(Enumeration welcomeFiles) {
        processWelcomeFiles(welcomeFiles, false);
    }

    private void processWelcomeFiles(Enumeration welcomeFiles,
        boolean internal) {
        if (! internal &&
            ! this.welcomeFiles.isEmpty() &&
            welcomeFiles.hasMoreElements()) {
            this.welcomeFiles.removeAllElements();
        }

	while (welcomeFiles.hasMoreElements()) {
	    this.welcomeFiles.addElement(welcomeFiles.nextElement());
	}
    }

    private void processErrorPages(Enumeration errorPages) {
        while (errorPages.hasMoreElements()) {
	    ErrorPageDescriptor errorPageDescriptor =
	        (ErrorPageDescriptor)errorPages.nextElement();
	    String key = null;

	    if (errorPageDescriptor.getErrorCode() > -1) {
	        key = String.valueOf(errorPageDescriptor.getErrorCode());
	    } else {
	        key = errorPageDescriptor.getExceptionType();
	    }

	    this.errorPages.put(key, errorPageDescriptor.getLocation());
	}
    }

    private void loadServlets() {
	Vector orderedKeys = new Vector();
	Enumeration e = loadableServlets.keys();
	
	// order keys

	while (e.hasMoreElements()) {
	    Integer key = (Integer)e.nextElement();
	    int slot = -1;

	    for (int i = 0; i < orderedKeys.size(); i++) {
	        if (key.intValue() <
		    ((Integer)(orderedKeys.elementAt(i))).intValue()) {
		    slot = i;

		    break;
		}
	    }

	    if (slot > -1) {
	        orderedKeys.insertElementAt(key, slot);
	    } else {
	        orderedKeys.addElement(key);
	    }
	}

	// loaded ordered servlets

	// Priorities IMO, should start with 0.
	// Only System Servlets should be at 0 and rest of the
	// servlets should be +ve integers.
	// WARNING: Please do not change this without talking to:
	// harishp@eng.sun.com (J2EE impact)

	for (int i = 0; i < orderedKeys.size(); i ++) {
	    Integer key = (Integer)orderedKeys.elementAt(i);
	    e = ((Vector)(loadableServlets.get(key))).elements();

	    while (e.hasMoreElements()) {
		String servletName = (String)e.nextElement();
		ServletsWrapper  result = container.getServletByName(servletName);
		
		if(result==null)
		    System.out.println("Warning: we try to load an undefined servlet " + servletName);
		
		try {
		    if(result!=null)
			result.loadServlet();
		} catch (Exception ee) {
		    String msg = sm.getString("context.loadServlet.e",
		        servletName);

		    System.out.println(msg);
		} 
	    }
	}
    }
}