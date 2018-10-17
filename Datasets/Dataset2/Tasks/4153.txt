public void addRequestInterceptor( BaseInterceptor ri ) {

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
import org.apache.tomcat.util.depend.*;
import org.apache.tomcat.util.*;
import java.security.*;
import java.lang.reflect.*;
import org.apache.tomcat.logging.*;
import java.io.*;
import java.net.*;
import java.util.*;


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
public class Context implements LogAware {
    // Proprietary attribute names for contexts - defined
    // here so we can document them.

    /** Private tomcat attribute names
     */
    public static final String ATTRIB_PREFIX="org.apache.tomcat";

    /** Workdir - a place where the servlets are allowed to write
     */
    public static final String ATTRIB_WORKDIR="org.apache.tomcat.workdir";

    /** This attribute will return the real context ( org.apache.tomcat.core.Context).
     *  Only "trusted" applications will get the value. Null if the application
     * 	is not trusted.
     */
    public static final String ATTRIB_REAL_CONTEXT="org.apache.tomcat.context";

    // -------------------- internal properties
    // context "id"
    private String path = "";
    private String docBase;

    // Absolute path to docBase if file-system based
    private String absPath; 
    // internal state / related objects
    private ContextManager contextM;
    private Object contextFacade;

    boolean reloadable=true; // XXX change default to false after testing

    private Hashtable attributes = new Hashtable();

    private File workDir;

    // Security Permissions for webapps and jsp for this context
    Object perms = null;
    Object protectionDomain;
 
    //    private RequestSecurityProvider rsProvider;

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

    // Maps specified in web.xml ( String url -> Handler  )
    private Hashtable mappings = new Hashtable();
    Hashtable constraints=new Hashtable();

    Hashtable containers=new Hashtable();

    Container defaultContainer = null; // generalization, will replace most of the
    // functionality. By using a default container we avoid a lot of checkings
    // and speed up searching, and we can get rid of special properties.
    private Handler defaultServlet = null;

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

    String facadeClassName;
    FacadeManager facadeM;
    
    public Context() {
	defaultContainer=new Container();
	defaultContainer.setContext( this );
	defaultContainer.setPath( null ); // default container
    }

    /** Every context is associated with a facade. We don't know the exact
	type of the facade, as a Context can be associated with a 2.2 ...
	ServletContext.

	I'm not sure if this method is good - it adds deps to upper layers.
     */
    public Object getFacade() {
        if(contextFacade==null )
	    contextFacade = getFacadeManager().createServletContextFacade( this );
	return contextFacade;
    }

    public void setFacade(Object obj) {
        if(contextFacade!=null )
	    log( "Changing facade " + contextFacade + " " +obj);
	contextFacade=obj;
    }


    // -------------------- Settable context properties --------------------
    // -------------------- Required properties
    public ContextManager getContextManager() {
	return contextM;
    }

    public void setContextManager(ContextManager cm) {
	contextM=cm;
    }

    public void setFacadeClassName(String s ) {
	facadeClassName=s;
    }

    public String getFacadeClassName() {
	return facadeClassName;
    }

    private static final String DEFAULT_FACADE="org.apache.tomcat.facade.Servlet22Manager";

    /** The servlet API variant that will be used for requests in this
     *  context
     */ 
    public void setServletAPI( String s ) {
	if( s!=null &&
	    ( s.endsWith("23") || s.endsWith("2.3")) ) {
	    facadeClassName="org.apache.tomcat.facade23.Servlet23Manager";
	} else {
	    facadeClassName=DEFAULT_FACADE;
	}
    }

    public FacadeManager getFacadeManager() {
	if( facadeM==null ) {
	    if( facadeClassName==null) 
		facadeClassName=DEFAULT_FACADE;
	    try {
		Class facadeMC=Class.forName( facadeClassName );
		if( facadeMC==null )
		    facadeMC=Class.forName( DEFAULT_FACADE );
		Constructor cons=facadeMC.getConstructor( new Class[] { this.getClass() });
		facadeM=(FacadeManager)cons.newInstance( new Object[] {this });
	    } catch( Exception ex ) {
		ex.printStackTrace();
	    }
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
	if (s == null ) return;
	s=s.trim();
	if(s.length() == 0)
	    return;
	if(  expectUserWelcomeFiles  ) {
	    removeWelcomeFiles();
	    expectUserWelcomeFiles=false;
	} 
	welcomeFiles.addElement( s );
    }

    /** Add a taglib declaration for this context
     */
    public void addTaglib( String uri, String location ) {
	//	log("Add taglib " + uri + "  " + location );
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
	log("Add env-entry " + name + "  " + type + " " + value + " " +description );
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

        
    /** Workdir attribute - XXX is it specified anyway ? 
     */
    public static final String ATTRIB_WORKDIR1 = "javax.servlet.context.tempdir";
    // XXX deprecated, is anyone in the world using it ?
    public static final String ATTRIB_WORKDIR2 = "sun.servlet.workdir";
    
    public Object getAttribute(String name) {
	// deprecated 
	if( name.equals( ATTRIB_WORKDIR1 ) ) 
	    return getWorkDir();
	if( name.equals( ATTRIB_WORKDIR2 ) ) 
	    return getWorkDir();

	
	if (name.startsWith( ATTRIB_PREFIX )) {
	    // XXX XXX XXX XXX Security - servlets may get too much access !!!
	    // right now we don't check because we need JspServlet to
	    // be able to access classloader and classpath
	    if( name.equals( ATTRIB_WORKDIR ) ) 
		return getWorkDir();
	    
	    if (name.equals("org.apache.tomcat.jsp_classpath")) {
		String separator = System.getProperty("path.separator", ":");
		StringBuffer cpath=new StringBuffer();
		URL classPaths[]=getClassPath();
		for(int i=0; i< classPaths.length ; i++ ) {
		    URL cp = classPaths[i];
		    if (cpath.length()>0) cpath.append( separator );
		    cpath.append(cp.getFile());
		}
		if( debug>9 ) log("Getting classpath " + cpath);
		return cpath.toString();
	    }
	    if( name.equals( "org.apache.tomcat.protection_domain") ) {
		return getProtectionDomain();
	    }
	    if(name.equals("org.apache.tomcat.classloader")) {
		return this.getClassLoader();
	    }
	    if(name.equals(ATTRIB_REAL_CONTEXT)) {
		if( ! allowAttribute(name) ) return null;
		return this;
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

    public void setDistributable(String s) {
	// XXX
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

    public void setFormLoginPage( String page ) {
	formLoginPage=page;
    }
    
    public void setFormErrorPage( String page ) {
	formErrorPage=page;
    }

    public void setLoginConfig( String authMethod, String realmName,
				String formLoginPage, String formErrorPage)
    {
	// 	log("Login config: " + authMethod + " " + realmName + " " +
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
        Handler sw = (Handler)servlets.get(servletName);
	if (sw == null) {
	    // Strict web.xml
	    throw new TomcatException( "Mapping with invalid servlet name " +
				       path + " " + servletName );
	    // Workaround for frequent "bug" in web.xmls
	    // Declare a default mapping
	    // log("Mapping with unregistered servlet " + servletName );
	    // 	    sw = addServlet( servletName, servletName );
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

//     public Handler getDefaultServlet() {
// 	if( defaultServlet==null)
// 	    defaultServlet=getServletByName(Constants.DEFAULT_SERVLET_NAME );
// 	return defaultServlet;
//     }

    // -------------------- Servlets management --------------------

    // XXX do we need that ??
    /** Remove the servlet with a specific name
     */
    public void removeServletByName(String servletName)
	throws TomcatException
    {
	servlets.remove( servletName );
    }

    public Handler getServletByName(String servletName) {
	return (Handler)servlets.get(servletName);
    }

    public Handler createHandler() {
	return getFacadeManager().createHandler();
    }
    
    /**
     * Add a servlet with the given name to the container. The
     * servlet will be loaded by the container's class loader
     * and instantiated using the given class name.
     *
     * Called to add a new servlet from web.xml
     */
    public void addServlet(Handler wrapper)
    	throws TomcatException
    {
	wrapper.setContext( this );
	String name=wrapper.getName();
	//	log("Adding servlet " + name  + " " + wrapper);

        // check for duplicates
        if (servlets.get(name) != null) {
	    log("Removing duplicate servlet " + name  + " " + wrapper);
            removeServletByName(name);
	    //	    getServletByName(name).destroy();
        }
	servlets.put(name, wrapper);
    }

//     public Handler addServlet(String name, String classN)
// 	throws TomcatException
//     {
// 	Handler sw = new Handler();
// 	sw.setContext(this);
	
// 	sw.setServletName(name);
// 	if ( classN.startsWith("/")) {
// 	    sw.setPath(classN);
// 	} else {
// 	    sw.setServletClass(classN);
// 	}
// 	addServlet( sw );
// 	return sw;
//     }

    public Enumeration getServletNames() {
	return servlets.keys();
    }

    // -------------------- Loading and sessions --------------------
    ClassLoader classLoader;
    boolean reload;
    // Vector<URL>, using URLClassLoader conventions
    Vector classPath=new Vector();
    DependManager dependM;
    
    /** The current class loader. This value may change if reload
     *  is used, you shouldn't cache the result
     */
    public final ClassLoader getClassLoader() {
	// 	if( servletL!=null) // backward compat
	// 	    return servletL.getClassLoader();
	return classLoader;
    }

    public final void setClassLoader(ClassLoader cl ) {
	classLoader=cl;
    }

    // temp. properties until reloading is separated.
    public boolean shouldReload() {
	// 	if( servletL!=null) // backward compat
	// 	    return servletL.shouldReload();
	if( dependM != null )
	    return dependM.shouldReload();
	return reload;
    }

    public void setReload( boolean b ) {
	reload=b;
    }

    public void reload() {
	// 	if( servletL!=null) // backward compat
	// 	    servletL.reload();
	Enumeration sE=servlets.elements();
	while( sE.hasMoreElements() ) {
	    try {
		Handler sw=(Handler)sE.nextElement();
		// 		if( sw.getServletClassName() != null ) {
		// 		    // this is dynamicaly added, probably a JSP.
		// 		    // in any case, we can't save it
		sw.reload();
		//		}
	    } catch( Exception ex ) {
		log( "Reload exception: " + ex);
	    }
	}
	// XXX todo
    }

    public void addClassPath( URL url ) {
	classPath.addElement( url);
    }

    public URL[] getClassPath() {
	if( classPath==null ) return new URL[0];
	URL serverCP[]=contextM.getServerClassPath();
	URL urls[]=new URL[classPath.size() + serverCP.length];
	int pos=0;
	for( int i=0; i<serverCP.length; i++ ) {
	    urls[pos++]=serverCP[i];
	}
	for( int i=0; i<classPath.size(); i++ ) {
	    urls[pos++]=(URL)classPath.elementAt( i );
	}
	return urls;
    }

    public void setDependManager(DependManager dm ) {
	dependM=dm;
    }

    public DependManager getDependManager( ) {
	return dependM;
    }
    
    /* -------------------- Utils  -------------------- */
    public void setDebug( int level ) {
	if (level!=debug)
	    log( "Setting debug to " + level );
	debug=level;
    }

    public void setDebug( String level ) {
	try {
	    setDebug( Integer.parseInt(level) );
	} catch (Exception e) {
	    log("Trying to set debug to '" + level + "':", e, Logger.ERROR);
	}
    }

    public int getDebug( ) {
	return debug;
    }

    // ------------------- Logging ---------------

    Logger.Helper loghelper = new Logger.Helper("tc_log", this);
    Logger.Helper loghelperServlet;

    /** Internal log method
     */
    public final void log(String msg) {
	loghelper.log(msg);
    }

    /** Internal log method
     */
    public void log(String msg, Throwable t) {
	loghelper.log(msg, t);
    }

    /** Internal log method
     */
    public void log(String msg, Throwable t, int level) {
	loghelper.log(msg, t, level);
    }

    /** User-level log method ( called from a servlet)
     */
    public void logServlet( String msg , Throwable t ) {
	if (loghelperServlet == null) {
	    loghelperServlet = new Logger.Helper
		("servlet_log",
		 (vhost==null ? "" : vhost + ":" )  +  path);
	}
	if (t == null)
	    loghelperServlet.log(msg);	// uses level INFORMATION
	else
	    loghelperServlet.log(msg, t); // uses level ERROR
	// note: log(msg,t) is deprecated in ServletContext; that
	// means most servlet messages will arrive with level
	// INFORMATION.  So the "servlet_log" Logger should be
	// specified with verbosityLevel="INFORMATION" in server.xml
	// in order to see servlet log() messages.
    }

    public void setLogger(Logger logger) {
	loghelper.setLogger(logger);
    }

    public Logger.Helper getLoggerHelper() {
	return loghelper;
    }
    
    public String toString() {
	return "Ctx(" + (vhost==null ? "" : vhost + ":" )  +  path +  ")";
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

	if ( ! rpath.startsWith("/")) 
	    rpath="/" + rpath;

	String realPath=FileUtil.safePath( absPath, rpath);
	if( realPath==null ) {
	    log( "Unsafe path " + absPath + " " + rpath );
	    return null;
	}
	
	try {
            url=new URL("file", null, 0,realPath );
	    if( debug>9) log( "getResourceURL=" + url + " request=" + rpath );
	    return url;
	} catch( IOException ex ) {
	    log("getting resource " + rpath, ex);
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
	String base=getAbsolutePath();
	if( path==null ) path="";

	String realPath=FileUtil.safePath( base, path );
	// No need for a sub-request, that's a great simplification
	// in servlet space.

	// Important: that's different from what some people might
	// expect and how other server APIs work, but that's how it's
	// specified in 2.2. From a security point of view that's very
	// good, it keeps inter-webapp communication under control.
	
	if( debug>5) {
	    log("Get real path " + path + " " + realPath + " " + base );
	}
	return realPath;
    }

    // -------------------- Deprecated
    // tomcat specific properties
    private String engineHeader = null;

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
    public File getWorkDir() {
	return workDir;
    }

    /**  @deprecated
     */
    public void setWorkDir(File workDir) {
	this.workDir = workDir;
    }

    
    public Object getProtectionDomain() {
	return protectionDomain;
    }

    public void setProtectionDomain(Object o) {
	protectionDomain=o;
    }

    /**
      * Get the SecurityManager Permissions for this Context.
      */
    public Object getPermissions() {
	return perms;
    }

    public void setPermissions( Object o ) {
	perms=o;
    }

    // -------------------- Virtual host support --------------------
    
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

    private boolean allowAttribute( String name ) {
	// check if we can access this attribute.
	if( isTrusted() ) return true;
	log( "Illegal access to internal attribute ", null, Logger.ERROR);
	return false;
    }

    public void addRequestInterceptor( RequestInterceptor ri ) {
        defaultContainer.addRequestInterceptor(ri);
    }
}