if( name.equals( "org.apache.tomcat.protection_domain") ) {

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
import org.apache.tomcat.facade.*;
import org.apache.tomcat.util.*;
import java.security.*;
import java.lang.reflect.*;
import org.apache.tomcat.logging.*;
import java.io.*;
import java.net.*;
import java.util.*;
import javax.servlet.http.*;
import javax.servlet.*;


/* Right now we have all the properties defined in web.xml.
   The interceptors will  go into Container ( every request will
   be associated with the final container, which will point back to the
   context). That will allow us to use a simpler and more "targeted"
   object model.

   The only "hard" part is moving getResource() and getRealPath() in
   a different class, using a filesystem independent abstraction. 
   
*/
   

/**
 * Context represent a Web Application as specified by Servlet Specs.
 * The implementation is a repository for all the properties
 * defined in web.xml and tomcat specific properties.
 *
 * @author James Duncan Davidson [duncan@eng.sun.com]
 * @author James Todd [gonzo@eng.sun.com]
 * @author Jason Hunter [jch@eng.sun.com]
 * @author Harish Prabandham
 * @author costin@dnt.ro
 * @author Gal Shachor shachor@il.ibm.com
 */
public class Context {
    private static StringManager sm =StringManager.getManager("org.apache.tomcat.core");

    // -------------------- internal properties
    // context "id"
    private String path = "";
    private String docBase;

    // Absolute path to docBase if file-system based
    private String absPath; 
    // internal state / related objects
    private ContextManager contextM;
    private ServletContext contextFacade;

    private ServletLoader servletL;
    boolean reloadable=true; // XXX change default to false after testing

    private Hashtable attributes = new Hashtable();

    private File workDir;

    // Security Permissions for webapps and jsp for this context
    Object perms = null;
    Object protectionDomain;
 
    //    private RequestSecurityProvider rsProvider;

    private Vector contextInterceptors = new Vector();
    private Vector requestInterceptors = new Vector();

    // Servlets loaded by this context( String->ServletWrapper )
    private Hashtable servlets = new Hashtable();

    // -------------------- from web.xml
    private Hashtable initializationParameters = new Hashtable();
    // all welcome files that are added are treated as "system default"
    private boolean expectUserWelcomeFiles=false;
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

    Container defaultContainer = null; // generalization, will replace most of the
    // functionality. By using a default container we avoid a lot of checkings
    // and speed up searching, and we can get rid of special properties.
    private ServletWrapper defaultServlet = null;

    // Authentication properties
    String authMethod;
    String realmName;
    String formLoginPage;
    String formErrorPage;

    int debug=0;
    // are servlets allowed to access internal objects? 
    boolean trusted=false;
    String vhost=null;
    Vector vhostAliases=new Vector();
    FacadeManager facadeM;
    
    public Context() {
	defaultContainer=new Container();
	defaultContainer.setContext( this );
	defaultContainer.setPath( null ); // default container
    }

    /** Every context is associated with a facade
     */
    public ServletContext getFacade() {
        if(contextFacade==null )
	    contextFacade = getFacadeManager().createServletContextFacade( this );
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

    public FacadeManager getFacadeManager() {
	if( facadeM==null ) {
	    /* XXX make it configurable
	     */
	    facadeM=new SimpleFacadeManager( this );
	}
	return facadeM;
    }

    /** Base URL for this context
     */
    public String getPath() {
	return path;
    }

    /** Base URL for this context
     */
    public void setPath(String path) {
	// config believes that the root path is called "/",
	//
	if( "/".equals(path) )
	    path="";
	this.path = path;
    }

    /** DocBase points to the web application files.
     *
     *  There is no restriction on the syntax and content of DocBase,
     *  it's up to the various modules to interpret this and use it.
     *  For example, to serve from a war file you can use war: protocol,
     *  and set up War interceptors.
     *
     *  "Basic" tomcat treats it as a file ( either absolute or relative to
     *  the CM home ).
     *
     *  If docBase is relative assume it is relative  to the context manager home.
     */
    public void setDocBase( String docB ) {
	this.docBase=docB;
    }


    public String getDocBase() {
	return docBase;
    }

    /** Return the absolute path for the docBase, if we are file-system
     *  based, null otherwise.
    */
    public String getAbsolutePath() {
	if( absPath!=null) return absPath;

	if (FileUtil.isAbsolute( docBase ) )
	    absPath=docBase;
	else
	    absPath = contextM.getHome() + File.separator + docBase;
	try {
	    absPath = new File(absPath).getCanonicalPath();
	} catch (IOException npe) {
	}
	return absPath;
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

    /** If any new welcome file is added, remove the old list of
     *  welcome files and start a new one. This is used as a hack to
     *  allow a default web.xml file to specifiy welcome files.
     *  We should use a better mechanism! 
     */
    public void expectUserWelcomeFiles() {
	expectUserWelcomeFiles = true;
    }
    

    public void addWelcomeFile( String s) {
	// user specified at least one user welcome file, remove the system
	// files
	if(  expectUserWelcomeFiles  ) {
	    removeWelcomeFiles();
	    expectUserWelcomeFiles=false;
	} 
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
        if (name.startsWith("org.apache.tomcat")) {
	    // XXX XXX XXX XXX Security - servlets may get too much access !!!
	    // right now we don't check because we need JspServlet to
	    // be able to access classloader and classpath
	    
	    if (name.equals("org.apache.tomcat.jsp_classpath")) {
		String cp= getServletLoader().getClassPath();
		return cp;
	    }
	    if( name.equals( Constants.ATTRIB_JSP_ProtectionDomain) ) {
		return getProtectionDomain();
	    }
	    if(name.equals("org.apache.tomcat.classloader")) {
		return this.getServletLoader().getClassLoader();
	    }
	    if( name.equals(FacadeManager.FACADE_ATTRIBUTE)) {
		if( ! allowAttribute(name) ) return null;
		return this.getFacadeManager();
	    }
	    return null; // org.apache.tomcat namespace is reserved in tomcat
	} else {
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

    /** Will add a new security constraint:
	For all paths:
	if( match(path) && match(method) && match( transport ) )
	then require("roles")

	This is equivalent with adding a Container with the path,
	method and transport. If the container will be matched,
	the request will have to pass the security constraints.
	
    */
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
	    ct.setMethods( methods );

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

    // return the container associated with this context -
    // which is also the default container
    public Container getContainer() {
	return defaultContainer;
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

    public void setDebug( String level ) {
	try {
	    setDebug( Integer.parseInt(level) );
	} catch (Exception e) {
	    log("Set debug to '" + level + "':", e);
	}
    }

    public int getDebug( ) {
	return debug;
    }

    /** Internal log method
     */
    public final void log(String msg) {
	log(msg, null);
    }

    public void log(String msg, Throwable t) {
	// XXX \n
	// Custom output -
	if( contextM == null ) {
	    System.out.println( msg );
	    if( t!=null ) 
		t.printStackTrace(System.out);
	    return;
	}
	if( msg.startsWith( "<l:" ))
	    contextM.doLog( msg, t );
	else
	    contextM.doLog(this.toString() + " " + msg, t);
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
	    csLog.log("Context log path=\"" + path  + "\" :" + msg + "\n");
	    //	    csLog.log("<l:context path=\"" + path  + "\" >" + msg + "</l:context>\n");
	} else {
	    System.out.println("Context log path=\"" + path  + "\"" + msg);
	    //	    System.out.println("<l:context path=\"" + path  + "\" >" + msg + "</l:context>");
	}
    }

    public String toString() {
	return "Ctx( " + (vhost==null ? "" : vhost + ":" )  +  path +  " )";
    }

    // -------------------- Facade methods --------------------

    public Context getContext(String path) {
	if (! path.startsWith("/")) {
	    return null; // according to spec, null is returned
	    // if we can't  return a servlet, so it's more probable
	    // servlets will check for null than IllegalArgument
	}
	// absolute path
	Request lr=contextM.createRequest( path );
	if( vhost != null ) lr.setServerName( vhost );
	getContextManager().processRequest(lr);
        return lr.getContext();
    }

    /** Implements getResource()
     *  See getRealPath(), it have to be local to the current Context -
     *  and can't go to a sub-context. That means we don't need any overhead.
     */
    public URL getResource(String rpath) throws MalformedURLException {
        if (rpath == null) return null;

        URL url = null;
	String absPath=getAbsolutePath();

	if ("".equals(rpath))
	    return new URL( "file", null, 0, absPath );


	if ( ! rpath.startsWith("/")) {
	    rpath="/" + rpath;
	}

	String realPath=absPath + rpath;
	try {
	    if( ! new File(realPath).getCanonicalPath().startsWith(absPath) ) {
		// no access to files in a different context.
		// XXX needs a better design - it should be in an interceptor,
		// in order to support non-file based repositories.
		return null;
	    }
	    
            url=new URL("file", null, 0,realPath );
	    if( debug>9) log( "getResourceURL=" + url + " request=" + rpath );
	    return url;
	} catch( IOException ex ) {
	    ex.printStackTrace();
	    return null;
	}
    }


    /**   According to Servlet 2.2 the real path is interpreted as
     *    relative to the current web app and _cannot_ go outside the 
     *    box. If your intention is different or want the "other" behavior 
     *    you'll have to first call getContext(path) and call getRealPath()
     *    on the result context ( if any - the server may disable that from
     *    security reasons !).
     *    XXX find out how can we find the context path in order to remove it
     *    from the path - that's the only way a user can do that unless he have
     *    prior knowledge of the mappings !
     */
    public String getRealPath( String path) {
	// No need for a sub-request, that's a great simplification
	// in servlet space.

	// Important: that's different from what some people might
	// expect and how other server APIs work, but that's how it's
	// specified in 2.2. From a security point of view that's very
	// good, it keeps inter-webapp communication under control.

	// XXX Everything can/should be abstracted out as soon as we
	// are ready to support non-file-based servers.

	// Hack for Jsp ( and other servlets ) that use rel. paths 
	if( ! path.startsWith("/") ) path="/"+ path;
	String normP=FileUtil.normPath(path);

	String absPath=getAbsolutePath();
	String realPath= absPath + normP;

	// Probably not needed - it will be used on the local FS
	realPath = FileUtil.patch(realPath);

	// extra-extra safety check, ( but slow )
	try {
	    if( ! new File(realPath).getCanonicalPath().startsWith(absPath) ) {
		// no access to files in a different context.
		// XXX needs a better design - it should be in an interceptor,
		// in order to support non-file based repositories.
		return null;
	    }
	} catch( IOException ex ) {
	    ex.printStackTrace();
	    return null;
	}

	if( debug>5) {
	    log("Get real path " + path + " " + realPath + " " + normP );
	    //   /*DEBUG*/ try {throw new Exception(); } catch(Exception ex) {ex.printStackTrace();}
	}
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

//     /**  @deprecated
//      */
//     public void setRequestSecurityProvider(RequestSecurityProvider rsProvider) {
// 	this.rsProvider = rsProvider;
//     }

//     /**  @deprecated
//      */
//     public RequestSecurityProvider getRequestSecurityProvider() {
// 	return this.rsProvider;
//     }

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
	if( contextInterceptors.size() == 0 ) {
	    // this context was not set up with individual interceptors.
	    // XXX no test done for context-specific interceptors, this will be the normal
	    // case, we need to find out what is the best behavior and config
	    return contextM.getContextInterceptors();
	}
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
	if( requestInterceptors.size() == 0 ) {
	    // this context was not set up with individual interceptors.
	    // XXX no test done for context-specific interceptors, this will be the normal
	    // case, we need to find out what is the best behavior and config
	    return contextM.getRequestInterceptors();
	}
	if( rInterceptors == null || rInterceptors.length != requestInterceptors.size()) {
	    rInterceptors=new RequestInterceptor[requestInterceptors.size()];
	    for( int i=0; i<rInterceptors.length; i++ ) {
		rInterceptors[i]=(RequestInterceptor)requestInterceptors.elementAt(i);
	    }
	}
	return rInterceptors;
    }

//      /**
//       * Adds a Permission to a Permissions object which will be used as
//       * the Permissions for this Context.  These are the Permissions
//       * set using the <Permission> element within the <Context> server.xml element.
//       */
//      public void setPermission(String className, String attr, String value) {
//          try {
//              if( perms == null )
//                  perms = new Permissions();
//              Class c=Class.forName(className);
//              Constructor con=c.getConstructor(new Class[]{String.class,String.class});
//              Object [] args=new Object[2];
//              args[0] = attr;
//              args[1] = value;
//              Permission p = (Permission)con.newInstance(args);
//              ((Permissions)perms).add(p);
//          } catch( ClassNotFoundException ex ) {
//              System.out.println("SecurityManager Class not found: " + className);
//              System.exit(1);
//          } catch( Exception ex ) {
//              System.out.println("SecurityManager Class could not be loaded: " + className);
//              ex.printStackTrace();
//              System.exit(1);
//          }
//          System.out.println("SecurityManager, " + className + ", \"" + attr + "\", \"" + value + "\" added");
//      }  
 
     /**
      * Get the SecurityManager Permissions for this Context.
      */
    public Object getPermissions() {
	return perms;
    }

    public void setPermissions( Object o ) {
	perms=o;
    }
    
    public Object getProtectionDomain() {
	return protectionDomain;
    }

    public void setProtectionDomain(Object o) {
	protectionDomain=o;
    }


    /** @deprecated - use getDocBase and URLUtil if you need it as URL
     *  NOT USED INSIDE TOMCAT - ONLY IN OLD J2EE CONNECTORS !
     */
    public URL getDocumentBase() {
	if( documentBase == null ) {
	    if( docBase == null)
		return null;
	    try {
		String absPath=docBase;

		// detect absolute path ( use the same logic in all tomcat )
		if (FileUtil.isAbsolute( docBase ) )
		    absPath=docBase;
	        else
		    absPath = contextM.getHome() + File.separator + docBase;

		try {
		    absPath = new File(absPath).getCanonicalPath();
		} catch (IOException npe) {
		}

		documentBase = new URL("file", "", absPath);

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

    /** Make this context visible as part of a virtual host
     */
    public void setHost( String h ) {
	vhost=h;
    }

    /** Return the virtual host name, or null if we are in the
	default context
    */
    public String getHost() {
	return vhost;
    }
    
    /** Virtual host support - this context will be part of 
     *  a virtual host with the specified name. You should
     *  set all the aliases. XXX Not implemented
     */
    public void addHostAlias( String alias ) {
	vhostAliases.addElement( alias );
    }

    public Enumeration getHostAliases() {
	return vhostAliases.elements();
    }
    // -------------------- Security - trusted code -------------------- 
    
    public void setTrusted( boolean t ) {
	trusted=t;
    }

    public boolean isTrusted() {
	return trusted;
    }

    public boolean allowAttribute( String name ) {
	// check if we can access this attribute.
	if( isTrusted() ) return true;
	if( true ) {
	    // XXX  XXX XXX
	    log( "Illegal access to internal attribute ");
	    return true;
	}
	 	
	// XXX We may check Permissions, etc 
	return false;
    }
}