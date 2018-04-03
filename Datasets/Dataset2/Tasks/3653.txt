csLog.log("<l:context path=\"" + path  + "\" >" + msg + "</l:context>\n");

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

import org.apache.tomcat.context.*;
import org.apache.tomcat.util.*;
import org.apache.tomcat.logging.*;
import java.io.*;
import java.net.*;
import java.util.*;
import javax.servlet.http.*;
import javax.servlet.*;

/**
 * Context represent a Web Application as specified by Servlet Specs.
 * The implementation is a repository for all the properties
 * defined in web.xml and tomcat specific properties, with all the
 * functionality delegated to interceptors.
 * 
 * @author James Duncan Davidson [duncan@eng.sun.com]
 * @author James Todd [gonzo@eng.sun.com]
 * @author Jason Hunter [jch@eng.sun.com]
 * @author Harish Prabandham
 * @author costin@dnt.ro
 */
public class Context {
    private static StringManager sm =StringManager.getManager("org.apache.tomcat.core");

    // -------------------- internal properties
    // context "id"
    private String path = "";
    private String docBase;

    // internal state / related objects
    private ContextManager contextM;
    private ServletContextFacade contextFacade;

    private SessionManager sessionManager;
    private ServletLoader servletL;
    boolean reloadable=true; // XXX change default to false after testing

    private Hashtable attributes = new Hashtable();

    private File workDir;
    
    private RequestSecurityProvider rsProvider;

    private Vector contextInterceptors = new Vector();
    private Vector requestInterceptors = new Vector();
    
    // Servlets loaded by this context( String->ServletWrapper )
    private Hashtable servlets = new Hashtable();

    // -------------------- from web.xml
    private Hashtable initializationParameters = new Hashtable();
    private Vector welcomeFiles = new Vector();
    private Hashtable errorPages = new Hashtable();
    private String description = null;
    private boolean isDistributable = false;
    private MimeMap mimeTypes = new MimeMap();
    private int sessionTimeOut = -1;

    // taglibs
    Hashtable tagLibs=new Hashtable();
    // Env entries
    Hashtable envEntryTypes=new Hashtable();
    Hashtable envEntryValues=new Hashtable();

    // Maps specified in web.xml ( String url -> ServletWrapper  )
    private Hashtable mappings = new Hashtable();
    Hashtable constraints=new Hashtable();
    
    Hashtable containers=new Hashtable();
    
    private ServletWrapper defaultServlet = null;
    
    // Authentication properties
    String authMethod;
    String realmName;
    String formLoginPage;
    String formErrorPage;

    int debug=0;
    
    public Context() {
	//	System.out.println("New Context ");
	// XXX  customize it per context
    }
	
    ServletContextFacade getFacade() {
        if(contextFacade==null )
	    contextFacade = new ServletContextFacade(contextM, this);
	return contextFacade;
    }


    // -------------------- Settable context properties --------------------
    // -------------------- Required properties
    public ContextManager getContextManager() {
	return contextM;
    }

    public void setContextManager(ContextManager cm) {
	contextM=cm;
    }
    
    public String getPath() {
	return path;
    }

    public void setPath(String path) {
	// config believes that the root path is called "/",
	// 
	if( "/".equals(path) )
	    path="";
	this.path = path;
    }

    /* NOTE: if docBase is a URL to a remote location, we should download
       the context and unpack it. It is _very_ inefficient to serve
       files from a remote location ( at least 2x slower )
    */
    
    /** DocBase points to the web application files.
     *
     *  There is no restriction on the syntax and content of DocBase,
     *  it's up to the various modules to interpret this and use it.
     *  For example, to server from a war file you can use war: protocol,
     *  and set up War interceptors.
     * 
     *  "Basic" tomcat treats it is a file ( either absolute or relative to
     *  the CM home ). XXX Make it absolute ??
     *
     */
    public void setDocBase( String docB ) {
	this.docBase=docB;
    }

    public String getDocBase() {
	return docBase;
    }

    // -------------------- Tomcat specific properties
    // workaround for XmlMapper unable to set anything but strings
    public void setReloadable( String s ) {
	reloadable=new Boolean( s ).booleanValue();
    }
    
    public void setReloadable( boolean b ) {
	reloadable=b;
    }

    /** Should we reload servlets ?
     */
    public boolean getReloadable() {
	return reloadable;
    }
    
    // -------------------- Web.xml properties --------------------
    public Enumeration getWelcomeFiles() {
	return welcomeFiles.elements();
    }

    /** @deprecated It is used as a hack to allow web.xml override default
	 welcome files.
	 Tomcat will first load the "default" web.xml and then this file.
    */
    public void removeWelcomeFiles() {
	if( ! this.welcomeFiles.isEmpty() )
	    this.welcomeFiles.removeAllElements();
    }

    public void addWelcomeFile( String s) {
	welcomeFiles.addElement( s );
    }

    /** Add a taglib declaration for this context
     */
    public void addTaglib( String uri, String location ) {
	//	System.out.println("Add taglib " + uri + "  " + location );
	tagLibs.put( uri, location );
    }

    public String getTaglibLocation( String uri ) {
	return (String)tagLibs.get(uri );
    }

    public Enumeration getTaglibs() {
	return tagLibs.keys();
    }

    /** Add Env-entry to this context
     */
    public void addEnvEntry( String name,String type, String value, String description ) {
	System.out.println("Add env-entry " + name + "  " + type + " " + value + " " +description );
	if( name==null || type==null) throw new IllegalArgumentException();
	envEntryTypes.put( name, type );
	if( value!=null)
	    envEntryValues.put( name, value );
    }

    public String getEnvEntryType(String name) {
	return (String)envEntryTypes.get(name);
    }

    public String getEnvEntryValue(String name) {
	return (String)envEntryValues.get(name);
    }

    public Enumeration getEnvEntries() {
	return envEntryTypes.keys();
    }
    
    
    public String getInitParameter(String name) {
        return (String)initializationParameters.get(name);
    }

    /** @deprecated use addInitParameter
     */
    public void setInitParameter( String name, String value ) {
	initializationParameters.put(name, value );
    }

    public void addInitParameter( String name, String value ) {
	initializationParameters.put(name, value );
    }
    
    public Enumeration getInitParameterNames() {
        return initializationParameters.keys();
    }

    public Object getAttribute(String name) {
        if (name.equals("org.apache.tomcat.jsp_classpath")) {
	    //return getServletLoader().getClassPath();
	    String cp= getServletLoader().getClassPath();
	    //	    System.out.println("CP: " + cp);
	    return cp;
	}
	else if(name.equals("org.apache.tomcat.classloader")) {
	  return this.getServletLoader();
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
    
    public String getDescription() {
        return this.description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public void setIcon( String icon ) {

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
    
    public FileNameMap getMimeMap() {
        return mimeTypes;
    }

    public void addContentType( String ext, String type) {
	mimeTypes.addContentType( ext, type );
    }

    public String getErrorPage(int errorCode) {
        return getErrorPage(String.valueOf(errorCode));
    }

    public void addErrorPage( String errorType, String value ) {
	this.errorPages.put( errorType, value );
    }

    public String getErrorPage(String errorCode) {
        return (String)errorPages.get(errorCode);
    }


    /** Authentication method, if any specified
     */
    public String getAuthMethod() {
	return authMethod;
    }

    /** Realm to be used
     */
    public String getRealmName() {
	return realmName;
    }

    public String getFormLoginPage() {
	return formLoginPage;
    }

    public String getFormErrorPage() {
	return formErrorPage;
    }

    public void setLoginConfig( String authMethod, String realmName,
				String formLoginPage, String formErrorPage)
    {
	// 	System.out.println("Login config: " + authMethod + " " + realmName + " " +
	// 			   formLoginPage + " " + formErrorPage);
	this.authMethod=authMethod;
	this.realmName=realmName;
	this.formLoginPage=formLoginPage;
	this.formErrorPage=formErrorPage;
    }   
    
    // -------------------- Mappings --------------------
    
    /**
     * Maps a named servlet to a particular path or extension.
     * If the named servlet is unregistered, it will be added
     * and subsequently mapped.
     *
     * Note that the order of resolution to handle a request is:
     *
     *    exact mapped servlet (eg /catalog)
     *    prefix mapped servlets (eg /foo/bar/*)
     *    extension mapped servlets (eg *jsp)
     *    default servlet
     *
     */
    public void addServletMapping(String path, String servletName)
	throws TomcatException
    {
	if( mappings.get( path )!= null) {
	    log( "Removing duplicate " + path + " -> " + mappings.get(path) );
	    mappings.remove( path );
	    Container ct=(Container)containers.get( path );
	    removeContainer( ct );
	}
        ServletWrapper sw = (ServletWrapper)servlets.get(servletName);
	if (sw == null) {
	    //	    System.out.println("Servlet not registered " + servletName );
	    // Workaround for frequent "bug" in web.xmls
	    // Declare a mapping for a JSP or servlet that is not
	    // declared as servlet. 
	    
	    sw = new ServletWrapper(this);

	    sw.setServletName(servletName);
	    if ( servletName.startsWith("/")) {
	        sw.setPath(servletName);
	    } else {
		sw.setServletClass(servletName);
	    }
	    addServlet( sw );

	    // or throw an exception !
	}
	if( "/".equals(path) )
	    defaultServlet = sw;

	mappings.put( path, sw );
	
	Container map=new Container();
	map.setContext( this );
	map.setHandler( sw );
	map.setPath( path );
	contextM.addContainer( map );
	containers.put( path, map );
    }

    public void addSecurityConstraint( String path[], String methods[],
				       String roles[], String transport)
	throws TomcatException
    {
	for( int i=0; i< path.length; i++ ) {
	    Container ct=new Container();
	    ct.setContext( this );
	    ct.setTransport( transport );
	    ct.setRoles( roles );
	    ct.setPath( path[i] );
	    
	    // XXX check if exists, merge if true.
	    constraints.put( path[i], ct );
	    //contextM.addSecurityConstraint( this, path[i], ct);
	    contextM.addContainer(  ct );
	}
    }

    public Enumeration getContainers() {
	return containers.elements();
    }
    
    public Enumeration getContainerLocations() {
	return containers.keys();
    }

    public Container getContainer( String path ) {
	return (Container)containers.get(path);
    }
    
    public void removeContainer( Container ct ) {
	containers.remove(ct.getPath());
    }
    
    public ServletWrapper getDefaultServlet() {
	if( defaultServlet==null)
	    defaultServlet=getServletByName(Constants.DEFAULT_SERVLET_NAME );
	return defaultServlet;
    }

    // -------------------- Servlets management --------------------

    // XXX do we need that ?? 
    /** Remove the servlet with a specific name
     */
    public void removeServletByName(String servletName)
	throws TomcatException
    {
	servlets.remove( servletName );
    }

    public ServletWrapper getServletByName(String servletName) {
	return (ServletWrapper)servlets.get(servletName);
    }

    /**
     * Add a servlet with the given name to the container. The
     * servlet will be loaded by the container's class loader
     * and instantiated using the given class name.
     *
     * Called to add a new servlet from web.xml
     */
    public void addServlet(ServletWrapper wrapper)
    	throws TomcatException
    {
	String name=wrapper.getServletName();
	//	System.out.println("Adding servlet " + name  + " " + wrapper);

        // check for duplicates
        if (servlets.get(name) != null) {
	    log("Removing duplicate servlet " + name  + " " + wrapper);
            removeServletByName(name);
	    //	    getServletByName(name).destroy();
        }
	servlets.put(name, wrapper);
    }

    public Enumeration getServletNames() {
	return servlets.keys();
    }

    // -------------------- Loading and sessions --------------------
    public SessionManager getSessionManager() {
	return sessionManager;
    }

    public void setSessionManager( SessionManager manager ) {
	sessionManager= manager;
    }


    public void setServletLoader(ServletLoader loader ) {
	this.servletL=loader;
    }
    
    public ServletLoader getServletLoader() {
	return servletL;
    }

    /* -------------------- Utils  -------------------- */
    public void setDebug( int level ) {
	if(level>0) log( "Set debug to " + level );
	debug=level;
    }

    public int getDebug( ) {
	return debug;
    }

    /** Internal log method
     */
    public final void log(String msg) {
	// XXX \n
	// Custom output -
	if( msg.startsWith( "<l:" ))
	    contextM.doLog( msg );
	else
	    contextM.doLog("<l:ctx path=\"" + path  + "\" >" + msg + "</l:ctx>");
    }

    boolean firstLog = true;
    Logger csLog = null;

    /** User-level log method ( called from a servlet)
     */
    public void logServlet( String msg , Throwable t ) {
	if (firstLog == true) {
	    csLog = Logger.getLogger("servlet_log");
	    if( csLog!= null ) {
		csLog.setCustomOutput("true");
		csLog.setVerbosityLevel(Logger.INFORMATION);
		firstLog = false;
	    }
	}
	if (csLog != null) {
	    csLog.log("<l:context path=\"" + path  + "\" >" + msg + "</l:context>");
	} else {
	    System.out.println("<l:context path=\"" + path  + "\" >" + msg + "</l:context>");
	}
    }
    
    public String toString() {
	return "Ctx(" + path + "," + getDocBase() + ")";
	// + " , " + getDocumentBase() + " ) ";
    }

    // -------------------- Facade methods --------------------

    public RequestDispatcher getRequestDispatcher(String path) {
	if ( path == null  || ! path.startsWith("/")) {
	    return null; // spec say "return null if we can't return a dispather
	}
	RequestDispatcherImpl rD=new RequestDispatcherImpl( this );
	rD.setPath( path );

	return rD;
    }

    public RequestDispatcher getNamedDispatcher(String name) {
        if (name == null)
	    return null;

	// We need to do the checks 
	ServletWrapper wrapper = getServletByName( name );
	if (wrapper == null)
	    return null;
	RequestDispatcherImpl rD=new RequestDispatcherImpl( this );
	rD.setName( name );

	return rD;
    }

    /** Implements getResource() - use a sub-request to let interceptors do the job.
     */
    public URL getResource(String rpath) throws MalformedURLException {
        URL url = null;

	if ("".equals(rpath)) 
	    return getDocumentBase();
	
        if (rpath == null)
	    return null;

	if ( ! rpath.startsWith("/")) {
	    rpath="/" + rpath;
	}

	// Create a Sub-Request, do the request processing stage
	// that will take care of aliasing and set the paths
	Request lr=contextM.createRequest( this, rpath );
	getContextManager().processRequest(lr);

	String mappedPath = lr.getMappedPath();

	// XXX workaround for mapper bugs
	if( mappedPath == null ) {
	    mappedPath=lr.getPathInfo();
	}
	if(mappedPath == null )
	    mappedPath=lr.getLookupPath();
	
        URL docBase = getDocumentBase();

	url=new URL(docBase.getProtocol(), docBase.getHost(),
		       docBase.getPort(), docBase.getFile() + mappedPath);
	if( debug>9) log( "getResourceURL=" + url + " request=" + lr );
	return url;
    }

    
    Context getContext(String path) {
	if (! path.startsWith("/")) {
	    return null; // according to spec, null is returned
	    // if we can't  return a servlet, so it's more probable
	    // servlets will check for null than IllegalArgument
	}
	Request lr=contextM.createRequest( this, path );
	getContextManager().processRequest(lr);
        return lr.getContext();
    }

    public void log(String msg, Throwable t) {
	System.err.println(msg);
	t.printStackTrace(System.err);
    }

    /**
     * 
     */
    String getRealPath( String path) {
	//	Real Path is the same as PathTranslated for a new request
	
	Context base=this; // contextM.getContext("");
	Request req=contextM.createRequest( base , FileUtil.normPath(path) );
	contextM.processRequest(req);
	
	String mappedPath = req.getMappedPath();

	// XXX workaround - need to fix mapper to return mapped path
	if( mappedPath == null ) 
	    mappedPath=req.getPathInfo();
	if(mappedPath == null )
	    mappedPath=req.getLookupPath();
	
	String realPath= this.getDocBase() + mappedPath;

	// Probably not needed - it will be used on the local FS
	realPath = FileUtil.patch(realPath);

	return realPath;
    }

    // -------------------- Deprecated
    // tomcat specific properties
    private boolean isWorkDirPersistent = false;
    private String engineHeader = null;
    private URL documentBase;
    private URL servletBase = null;
    private boolean isInvokerEnabled = false;
    // for serving WARs directly 
    private File warDir = null;
    private boolean isWARExpanded = false;
    private boolean isWARValidated = false;



    /**  @deprecated
     */
    public boolean isInvokerEnabled() {
        return isInvokerEnabled;
    }
    
    /**  @deprecated
     */
    public void setInvokerEnabled(boolean isInvokerEnabled) {
        this.isInvokerEnabled = isInvokerEnabled;
    }

    /**  @deprecated
     */
    public boolean isWorkDirPersistent() {
        return this.isWorkDirPersistent;
    }

    /**  @deprecated
     */
    public void setWorkDirPersistent( boolean b ) {
	isWorkDirPersistent=b;
    }
    
    /**  @deprecated
     */
    public File getWorkDir() {
	return workDir;
    }

    /**  @deprecated
     */
    public void setWorkDir(File workDir) {
	this.workDir = workDir;
    }

    /** Set work dir using a String property
     *  @deprecated
     */
    public void setWorkDirPath(String workDir) {
	this.workDir=new File(workDir);
    }

    /**  @deprecated
     */
    public String getEngineHeader() {
	return engineHeader;
    }

    /**  @deprecated
     */
    public void setEngineHeader(String s) {
        engineHeader=s;
    }

    /**  @deprecated
     */
    public void setRequestSecurityProvider(RequestSecurityProvider rsProvider) {
	this.rsProvider = rsProvider;
    }

    /**  @deprecated
     */
    public RequestSecurityProvider getRequestSecurityProvider() {
	return this.rsProvider;
    }

    /**  @deprecated
     */
    public File getWARDir() {
        return this.warDir;
    }

    /**  @deprecated
     */
    public void setWARDir( File f ) {
	warDir=f;
    }

    /**  @deprecated
     */
    public boolean isWARExpanded() {
        return this.isWARExpanded;
    }

    /**  @deprecated
     */
    public void setIsWARExpanded(boolean isWARExpanded) {
        this.isWARExpanded = isWARExpanded;
    }

    /**  @deprecated
     */
    public boolean isWARValidated() {
        return this.isWARValidated;
    }

    /**  @deprecated
     */
    public void setIsWARValidated(boolean isWARValidated) {
        this.isWARValidated = isWARValidated;
    }
    
    /**  @deprecated
     */
    public void addContextInterceptor( ContextInterceptor ci) {
	contextInterceptors.addElement( ci );
    }

    ContextInterceptor cInterceptors[];

    /** Return the context interceptors as an array.
	For performance reasons we use an array instead of
	returning the vector - the interceptors will not change at
	runtime and array access is faster and easier than vector
	access
	@deprecated
    */
    public ContextInterceptor[] getContextInterceptors() {
	if( cInterceptors == null || cInterceptors.length != contextInterceptors.size()) {
	    cInterceptors=new ContextInterceptor[contextInterceptors.size()];
	    for( int i=0; i<cInterceptors.length; i++ ) {
		cInterceptors[i]=(ContextInterceptor)contextInterceptors.elementAt(i);
	    }
	}
	return cInterceptors;
    }

    /**  @deprecated
     */
    public void addRequestInterceptor( RequestInterceptor ci) {
	requestInterceptors.addElement( ci );
    }

    RequestInterceptor rInterceptors[];
    
    /** Return the context interceptors as an array.
	For performance reasons we use an array instead of
	returning the vector - the interceptors will not change at
	runtime and array access is faster and easier than vector
	access
	@deprecated 
    */
    public RequestInterceptor[] getRequestInterceptors() {
	if( rInterceptors == null || rInterceptors.length != requestInterceptors.size()) {
	    rInterceptors=new RequestInterceptor[requestInterceptors.size()];
	    for( int i=0; i<rInterceptors.length; i++ ) {
		rInterceptors[i]=(RequestInterceptor)requestInterceptors.elementAt(i);
	    }
	}
	return rInterceptors;
    }

    /** @deprecated - use getDocBase and URLUtil if you need it as URL
     */
    public URL getDocumentBase() {
	if( documentBase == null ) {
	    if( docBase != null)
		try {
		    documentBase=URLUtil.resolve( docBase );
		} catch( MalformedURLException ex ) {
		    ex.printStackTrace();
		}
	}
        return documentBase;
    }

    /** @deprecated - use setDocBase
     */
    public void setDocumentBase(URL s) {
	// Used only by startup, will be removed
        this.documentBase=s;
    }



}