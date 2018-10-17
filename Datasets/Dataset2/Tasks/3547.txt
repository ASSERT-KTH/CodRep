private DependManager dependM=new DependManager();

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

import org.apache.tomcat.util.depend.*;
import org.apache.tomcat.util.MimeMap;
import org.apache.tomcat.util.log.*;

import java.io.File;
import java.net.FileNameMap;
import java.net.URL;

import java.util.Hashtable;
import java.util.Vector;
import java.util.Enumeration;


/**
 * Context represent a Web Application as specified by Servlet Specs.
 * The implementation is a repository for all the properties
 * defined in web.xml and tomcat specific properties.
 * 
 * This object has many properties, but doesn't do anything special
 * except simple cashing.
 *
 * You need to set at least "path" and "base" before adding a
 * context to a server. You can also set any other properties.
 *
 * At addContext() stage log and paths will be "fixed" based on
 * context manager settings.
 *
 * At initContext() stage, web.xml will be read and all other
 * properties will be set. WebXmlReader must be the first
 * module in initContext() chain. 
 *
 * @author James Duncan Davidson [duncan@eng.sun.com]
 * @author James Todd [gonzo@eng.sun.com]
 * @author Jason Hunter [jch@eng.sun.com]
 * @author Harish Prabandham
 * @author costin@dnt.ro
 * @author Gal Shachor shachor@il.ibm.com
 */
public final class Context implements LogAware {
    // -------------------- Constants --------------------
    
    // Proprietary attribute names for contexts - defined
    // here so we can document them ( will show in javadoc )

    /** Private tomcat attribute names
     */
    public static final String ATTRIB_PREFIX="org.apache.tomcat";

    /** Protection domain to be used to create new classes in this context.
	This is used only by JspServlet, and should be avoided -
	the preferred mechanism is to use the default policy file
	and URLClassLoader.
    */
    public static final String ATTRIB_PROTECTION_DOMAIN=
	"org.apache.tomcat.protection_domain";

    /** Workdir - a place where the servlets are allowed to write
     */
    public static final String ATTRIB_WORKDIR="org.apache.tomcat.workdir";
    public static final String ATTRIB_WORKDIR1 = "javax.servlet.context.tempdir";
    public static final String ATTRIB_WORKDIR2 = "sun.servlet.workdir";
    

    /** This attribute will return the real context (
     *  org.apache.tomcat.core.Context).
     *  Only "trusted" applications will get the value. Null if the application
     * 	is not trusted.
     */
    public static final String ATTRIB_REAL_CONTEXT="org.apache.tomcat.context";

    /** Context is new, possibly not even added to server.
	ContextManager is not set, and most of the paths are not fixed
    */
    public static final int STATE_NEW=0;

    /** Context was added to the server, but contextInit() is not
	called. Paths are not set yet, the only valid information is
	the contextURI.
     */
    public static final int STATE_ADDED=1;
    
    /**
       Relative paths are fixed, based
       on server base, and CM is set.
       If a request arives for this context, an error message should be
       displayed ( "application is temporary disabled" )
     */
    public static final int STATE_DISABLED=2;

    /** Context is initialized and ready to serve. We have all mappings
	and configs from web.xml.
    */
    public static final int STATE_READY=3;
    
    // -------------------- internal properties
    // context "id"
    private String path = "";

    // directory where the context files are located.
    private String docBase;

    // Absolute path to docBase if file-system based
    private String absPath;
    private Hashtable properties=new Hashtable();
    
    private int state=STATE_NEW;
    
    // internal state / related objects
    private ContextManager contextM;
    private Object contextFacade;
    // print debugging information
    private int debug=0;

    // enable reloading
    private boolean reloadable=true; 

    // XXX Use a better repository
    private Hashtable attributes = new Hashtable();

    // directory with write-permissions for servlets
    private File workDir;

    // Servlets loaded by this context( String->ServletWrapper )
    private Hashtable servlets = new Hashtable();

    // Initial properties for the context
    private Hashtable initializationParameters = new Hashtable();

    // WelcomeFiles
    private Vector welcomeFilesV=new Vector();
    // cached for faster access
    private String welcomeFiles[] = null;

    // Defined error pages. 
    private Hashtable errorPages = new Hashtable();

    // mime mappings
    private MimeMap mimeTypes = new MimeMap();

    // Default session time out
    private int sessionTimeOut = -1;

    private boolean isDistributable = false;

    // Maps specified in web.xml ( String url -> Handler  )
    private Hashtable mappings = new Hashtable();

    // Security constraints ( String url -> Container )
    private Hashtable constraints=new Hashtable();

    // All url patterns ( url_pattern -> properties )
    private Hashtable containers=new Hashtable();

    // Container used if no match is found
    // Also contains the special properties for
    // this context. 
    private Container defaultContainer = null;

    // Authentication properties
    private String authMethod;
    private String realmName;
    private String formLoginPage;
    private String formErrorPage;

    // Servlet-Engine header ( default set by Servlet facade)
    private String engineHeader = null;

    // Virtual host name ( null if default )
    private String vhost=null;
    // vhost aliases 
    private Vector vhostAliases=new Vector();

    // are servlets allowed to access internal objects? 
    private boolean trusted=false;

    // log channels for context and servlets 
    private Log loghelper = new Log("tc_log", this);
    private Log loghelperServlet;

    // servlet API implemented by this Context
    private String apiLevel="2.2";

    // class loader for this context
    private ClassLoader classLoader;
    // Vector<URL>, using URLClassLoader conventions
    private Vector classPath=new Vector();

    // true if a change was detected and this context
    // needs reload
    private boolean reload;
    // Tool used to control reloading
    private DependManager dependM;

    // -------------------- from web.xml --------------------
    // Those properties are not directly used in context
    // operation, we just store them.
    private String description = null;
    private String icon=null;
    // taglibs
    private Hashtable tagLibs=new Hashtable();
    // Env entries
    private Hashtable envEntryTypes=new Hashtable();
    private Hashtable envEntryValues=new Hashtable();

    // -------------------- Constructor --------------------
    
    public Context() {
	defaultContainer=new Container();
	defaultContainer.setContext( this );
	defaultContainer.setPath( null ); // default container
    }


    // -------------------- Active methods --------------------

    // The main role of Context is to store the many properties
    // that a web application have.

    // There are only few methods here that actually do something
    // ( and we try to keep the object "passive" - it is already
    // full of properties, no need to make it to complicated.

    
    /**
     * Maps a named servlet to a particular path or extension.
     *
     * If the named servlet is unregistered, it will be added
     * and subsequently mapped. The servlet can be set by intereceptors
     * during addContainer() hook.
     *
     * If the mapping already exists it will be replaced by the new
     * mapping.
     */
    public final  void addServletMapping(String path, String servletName)
	throws TomcatException
    {
	if( mappings.get( path )!= null) {
	    log( "Removing duplicate " + path + " -> " + mappings.get(path) );
	    mappings.remove( path );
	    Container ct=(Container)containers.get( path );
	    removeContainer( ct );
	}

	// sw may be null - in wich case interceptors may
	// set it 
        Handler sw = getServletByName(servletName);
	
	Container map=new Container();
	map.setContext( this );
	map.setHandlerName( servletName );
	map.setHandler( sw );
	map.setPath( path );

	// Notify interceptors that a new container is added
	BaseInterceptor cI[]=defaultContainer.getInterceptors();
	for( int i=0; i< cI.length; i++ ) {
	    cI[i].addContainer( map );
	}

	sw = getServletByName(servletName);
	
	
	if (sw == null) {
	    // web.xml validation - a mapping with no servlet rollback
	    removeContainer( map );
 	    throw new TomcatException( "Mapping with invalid servlet  " +
				       path + " " + servletName );
	}

	containers.put( path, map );
	mappings.put( path, sw );
	if( debug > 4 )
	    log( "Map " + path + " -> " + mappings.get(path));
    }

    /** Will add a new security constraint:
	For all paths:
	if( match(path) && match(method) && match( transport ) )
	then require("roles")

	This is equivalent with adding a Container with the path,
	method and transport. If the container will be matched,
	the request will have to pass the security constraints.
	
    */
    public final  void addSecurityConstraint( String path[], String methods[],
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

	    // Notify interceptors that a new container is added
	    BaseInterceptor cI[]=ct.getInterceptors();
	    for( int j=0; j< cI.length; j++ ) {
		cI[j].addContainer( ct );
	    }
	}
    }

    /** getAttribute( "org.apache.tomcat.*" ) may return something
	special
    */
    private Object getSpecialAttribute( String name ) {
	// deprecated - invalid and wrong prefix
	if( name.equals( ATTRIB_WORKDIR1 ) ) 
	    return getWorkDir();
	if( name.equals( ATTRIB_WORKDIR2 ) ) 
	    return getWorkDir();

	// this saves 5 compare for non-special attributes
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
	    if(name.equals("org.apache.tomcat.classloader")) {
		return this.getClassLoader();
	    }
	    if(name.equals(ATTRIB_REAL_CONTEXT)) {
		if( ! allowAttribute(name) ) {
			return null;
		}
		return this;
	    }
	}
	return null; 
    }
    
    /** Check if "special" attributes can be used by
     *   user application. Only trusted apps can get 
     *   access to the implementation object.
     */
    public final  boolean allowAttribute( String name ) {
	// check if we can access this attribute.
	if( isTrusted() ) return true;
	log( "Attempt to access internal attribute in untrusted app",
	     null, Logger.ERROR);
	return false;
    }

    // -------------------- Passive properties --------------------
    // Everything bellow is just get/set
    // for web application properties 
    // --------------------
    
    // -------------------- Facade --------------------
    
    /** Every context is associated with a facade. We don't know the exact
	type of the facade, as a Context can be associated with a 2.2 ...
	ServletContext.
     */
    public final  Object getFacade() {
	return contextFacade;
    }

    public final  void setFacade(Object obj) {
        if(contextFacade!=null )
	    log( "Changing facade " + contextFacade + " " +obj);
	contextFacade=obj;
    }


    // -------------------- Settable context properties --------------------

    /** Returned the main server ( servlet container )
     */
    public final  ContextManager getContextManager() {
	return contextM;
    }

    /** This method is called when the Context is added
	to a server. Some of the Context properties
	depend on the ContextManager, and will be adjusted
	by interceptors ( DefaultCMSetter )
    */
    public final  void setContextManager(ContextManager cm) {
	if( contextM != null ) return;
	contextM=cm;
    }

    /** Default container for this context.
     */
    public final  Container getContainer() {
	return defaultContainer;
    }

    public final int getState() {
	return state;
    }

    /** Move the context in a different state.
	Can be called only from tomcat.core.ContextManager.
	( package access )
    */
    void setState( int state ) {
	this.state=state;
    }

    /**
     * Initializes this context to be able to accept requests. This action
     * will cause the context to load it's configuration information
     * from the webapp directory in the docbase.
     *
     * <p>This method must be called
     * before any requests are handled by this context. It will be called
     * after the context was added, typically when the engine starts
     * or after the admin adds a new context.
     *
     * After this call, the context will be in READY state and will
     * be able to server requests.
     * 
     * @exception if any interceptor throws an exception the error
     *   will prevent the context from becoming READY
     */
    public final void init() throws TomcatException {
	if( state==STATE_READY ) {
	    log( "Already initialized " );
	    return;
	}
	// make sure we see all interceptors added so far
	getContainer().resetInterceptorCache(Container.H_engineInit);

	// initialize all local-interceptors
	BaseInterceptor cI[]=getContainer().getInterceptors();
	for( int i=0; i<cI.length ; i++ ) {
	    if( this !=cI[i].getContext()) continue;
	    cI[i].setContextManager( contextM );
	    try {
		for( int j=0; j<cI.length ; j++ ) {
		    cI[j].addInterceptor( contextM, this, cI[i] );
		}

		cI[i].engineInit( contextM );
	    } catch( TomcatException ex ) {
		log( "Error initializing " + cI[i] + " for " + this );
	    }
	}

	
	// no action if ContextManager is not initialized
	if( contextM==null ||
	    contextM.getState() == ContextManager.STATE_CONFIG ) {
	    log( "ContextManager is not yet initialized ");
	    return;
	}

	if( state==STATE_NEW ) {
	    // this context was not added yet
	    // throw new TomcatException("Context not added yet " + this );
	    contextM.addContext( this );
	}
	
	cI=getContainer().getInterceptors();
	for( int i=0; i< cI.length; i++ ) {
	    cI[i].contextInit( this );
	}
	
	// Only if all init methods succeed an no ex is thrown
	setState( Context.STATE_READY );
    }


    /** Stop the context. After the call the context will be disabled,
	( DISABLED state ) and it'll not be able to serve requests.
	The context will still be available and can be enabled later
	by calling initContext(). Requests mapped to this context
	should report a "temporary unavailable" message.
	
	
	All servlets will be destroyed, and resources held by the
	context will be freed.

	The contextShutdown callbacks can wait until the running serlvets
	are completed - there is no way to force the shutdown.
     */
    public void shutdown() throws TomcatException {
	setState( Context.STATE_DISABLED ); // called before
	// the hook, no more request should be allowed in unstable state

	BaseInterceptor cI[]= getContainer().getInterceptors();
	for( int i=0; i< cI.length; i++ ) {
	    cI[i].contextShutdown( this );
	}
    }


    
    // -------------------- Basic properties --------------------

    /** Base URL for this context
     */
    public final  String getPath() {
	return path;
    }

    /** Base URL for this context
     */
    public final  void setPath(String path) {
	// config believes that the root path is called "/",
	//
	if( "/".equals(path) )
	    path="";
	this.path = path;
	loghelper.setLogPrefix("Ctx("+ path +") ");
    }

    /**
     *  Make this context visible as part of a virtual host.
     *  The host is the "default" name, it may also have aliases.
     */
    public final  void setHost( String h ) {
	vhost=h;
    }

    /**
     * Return the virtual host name, or null if we are in the
     * default context
     */
    public final  String getHost() {
	return vhost;
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
     */
    public final  void setDocBase( String docB ) {
	this.docBase=docB;
    }

    public final  String getDocBase() {
	return docBase;
    }

    /** Return the absolute path for the docBase, if we are file-system
     *  based, null otherwise.
    */
    public final  String getAbsolutePath() {
	return absPath;
    }

    /** Set the absolute path to this context.
     * 	If not set explicitely, it'll be docBase ( if absolute )
     *  or relative to "home" ( cm.getHome() ).
     *  DefaultCMSetter will "fix" the path.
     */
    public final  void setAbsolutePath(String s) {
	absPath=s;
    }

    public String getProperty( String n ) {
	return (String)properties.get( n );
    }

    public void setProperty( String n, String v ) {
	properties.put( n, v );
    }
    
    // -------------------- Tomcat specific properties --------------------
    
    public final  void setReloadable( boolean b ) {
	reloadable=b;
    }

    /** Should we reload servlets ?
     */
    public final  boolean getReloadable() {
	return reloadable;
    }

    // -------------------- API level --------------------
    
    /** The servlet API variant that will be used for requests in this
     *  context
     */ 
    public final  void setServletAPI( String s ) {
	if( s==null ) return;
	if( s.endsWith("23") || s.endsWith("2.3")) {
	    apiLevel="2.3";
	} else if( ( s.endsWith("22") || s.endsWith("2.2")) ) {
	    apiLevel="2.2";
	} else {
	    log( "Unknown API " + s );
	}
    }

    public final  String getServletAPI() {
	return apiLevel;
    }
    
    // -------------------- Welcome files --------------------

    /** Return welcome files defined in web.xml or the
     *  defaults, if user doesn't define any
     */
    public final  String[] getWelcomeFiles() {
	if( welcomeFiles==null ) {
	    welcomeFiles=new String[ welcomeFilesV.size() ];
	    for( int i=0; i< welcomeFiles.length; i++ ) {
		welcomeFiles[i]=(String)welcomeFilesV.elementAt( i );
	    }
	}
	return welcomeFiles;
    }

    /** Add an welcome file. 
     */
    public final  void addWelcomeFile( String s) {
	if (s == null ) return;
	s=s.trim();
	if(s.length() == 0)
	    return;
	welcomeFiles=null; // invalidate the cache
	welcomeFilesV.addElement( s );
    }

    // -------------------- Init parameters --------------------
    
    public final  String getInitParameter(String name) {
        return (String)initializationParameters.get(name);
    }

    public final  void addInitParameter( String name, String value ) {
	initializationParameters.put(name, value );
    }

    public final  Enumeration getInitParameterNames() {
        return initializationParameters.keys();
    }


    // --------------------  Attributes --------------------

    /** Return an attribute value.
     *  "Special" attributes ( defined org.apache.tomcat )
     *  are computed
     * 
     *  XXX Use callbacks !!
     */
    public final  Object getAttribute(String name) {
	Object o=getSpecialAttribute( name );
	if ( o!=null ) return o;
	return attributes.get(name);    
    }

    public final  Enumeration getAttributeNames() {
        return attributes.keys();
    }

    public final  void setAttribute(String name, Object object) {
        attributes.put(name, object);
    }

    public final  void removeAttribute(String name) {
        attributes.remove(name);
    }


    // -------------------- Web.xml properties --------------------

    /** Add a taglib declaration for this context
     */
    public final  void addTaglib( String uri, String location ) {
	tagLibs.put( uri, location );
    }

    public final  String getTaglibLocation( String uri ) {
	return (String)tagLibs.get(uri );
    }

    public final  Enumeration getTaglibs() {
	return tagLibs.keys();
    }

    /** Add Env-entry to this context
     */
    public final  void addEnvEntry( String name,String type, String value, String description ) {
	log("Add env-entry " + name + "  " + type + " " + value + " " +description );
	if( name==null || type==null) throw new IllegalArgumentException();
	envEntryTypes.put( name, type );
	if( value!=null)
	    envEntryValues.put( name, value );
    }

    public final  String getEnvEntryType(String name) {
	return (String)envEntryTypes.get(name);
    }

    public final  String getEnvEntryValue(String name) {
	return (String)envEntryValues.get(name);
    }

    public final  Enumeration getEnvEntries() {
	return envEntryTypes.keys();
    }

    
    public final  String getDescription() {
        return this.description;
    }

    public final  void setDescription(String description) {
        this.description = description;
    }

    public final  void setIcon( String icon ) {
	this.icon=icon;
    }

    public final  boolean isDistributable() {
        return this.isDistributable;
    }

    public final  void setDistributable(boolean isDistributable) {
        this.isDistributable = isDistributable;
    }

    public final  int getSessionTimeOut() {
        return this.sessionTimeOut;
    }

    public final  void setSessionTimeOut(int sessionTimeOut) {
        this.sessionTimeOut = sessionTimeOut;
    }

    // -------------------- Mime types --------------------

    public final  FileNameMap getMimeMap() {
        return mimeTypes;
    }

    public final  void addContentType( String ext, String type) {
	mimeTypes.addContentType( ext, type );
    }
    
    // -------------------- Error pages --------------------

    public final  String getErrorPage(int errorCode) {
        return getErrorPage(String.valueOf(errorCode));
    }

    public final  void addErrorPage( String errorType, String value ) {
	this.errorPages.put( errorType, value );
    }

    public final  String getErrorPage(String errorCode) {
        return (String)errorPages.get(errorCode);
    }


    // -------------------- Auth --------------------
    
    /** Authentication method, if any specified
     */
    public final  String getAuthMethod() {
	return authMethod;
    }

    /** Realm to be used
     */
    public final  String getRealmName() {
	return realmName;
    }

    public final  String getFormLoginPage() {
	return formLoginPage;
    }

    public final  String getFormErrorPage() {
	return formErrorPage;
    }

    public final  void setFormLoginPage( String page ) {
	formLoginPage=page;
    }
    
    public final  void setFormErrorPage( String page ) {
	formErrorPage=page;
    }

    public final  void setLoginConfig( String authMethod, String realmName,
				String formLoginPage, String formErrorPage)
    {
	this.authMethod=authMethod;
	this.realmName=realmName;
	this.formLoginPage=formLoginPage;
	this.formErrorPage=formErrorPage;
    }

    // -------------------- Mappings --------------------

    public final  Enumeration getContainers() {
	return containers.elements();
    }

    /** Return an enumeration of Strings, representing
     *  all URLs ( relative to this context ) having
     *	associated properties ( handlers, security, etc)
     */
    public final  Enumeration getContainerLocations() {
	return containers.keys();
    }

    /** Return the container ( properties ) associated
     *  with a path ( relative to this context )
     */
    public final  Container getContainer( String path ) {
	return (Container)containers.get(path);
    }

    /** Remove a container
     */
    public final  void removeContainer( Container ct )
	throws TomcatException
    {
	containers.remove(ct.getPath());

	// notify modules that a container was removed
	BaseInterceptor cI[]=ct.getInterceptors();
	for( int i=0; i< cI.length; i++ ) {
	    cI[i].removeContainer( ct );
	}
    }

    // -------------------- Servlets management --------------------
    /**
     * Add a servlet. Servlets are mapped by name.
     * This method is used to maintain the list of declared
     * servlets, that can be used for mappings.
     */
    public final  void addServlet(Handler wrapper)
    	throws TomcatException
    {
	//	wrapper.setContext( this );
	wrapper.setState( Handler.STATE_ADDED );
	String name=wrapper.getName();

        // check for duplicates
        if (getServletByName(name) != null) {
	    log("Removing duplicate servlet " + name  + " " + wrapper);
            removeServletByName(name);
        }
	if( debug>5 ) log( "Adding servlet=" + name + "-> "
			   + wrapper);
	servlets.put(name, wrapper);
    }

    /** Remove the servlet with a specific name
     */
    public final  void removeServletByName(String servletName)
	throws TomcatException
    {
	Handler h=getServletByName( servletName );
	if( h!=null )
	    h.setState( Handler.STATE_NEW );
	servlets.remove( servletName );
    }

    /**
     *  
     */
    public final  Handler getServletByName(String servletName) {
	return (Handler)servlets.get(servletName);
    }


    
    /** Return all servlets registered with this Context
     *  The elements will be of type Handler ( or sub-types ) 
     */
    public final  Enumeration getServletNames() {
	return servlets.keys();
    }

    // -------------------- Loading and sessions --------------------

    /** The current class loader. This value may change if reload
     *  is used, you shouldn't cache the result
     */
    public final ClassLoader getClassLoader() {
	return classLoader;
    }

    public final void setClassLoader(ClassLoader cl ) {
	classLoader=cl;
    }

    // temp. properties until reloading is separated.
    public final  boolean shouldReload() {
	if( !reload && dependM != null )
	    return dependM.shouldReload();
	return reload;
    }

    public final  void setReload( boolean b ) {
	reload=b;
    }

    // -------------------- ClassPath --------------------
    
    public final  void addClassPath( URL url ) {
	classPath.addElement( url);
    }

    /** Returns the full classpath - concatenation
	of ContextManager classpath and locally specified
	class path
    */
    public final  URL[] getClassPath() {
	if( classPath==null ) return new URL[0];
	URL serverCP[]=new URL[0]; //contextM.getServerClassPath();
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

    // -------------------- Depend manager ( used for reloading ) -----------
    
    public final  void setDependManager(DependManager dm ) {
	dependM=dm;
    }

    public final  DependManager getDependManager( ) {
	return dependM;
    }
    
    /* -------------------- Utils  -------------------- */
    public final  void setDebug( int level ) {
	if (level!=debug)
	    log( "Setting debug to " + level );
	debug=level;
    }

    public final  int getDebug( ) {
	return debug;
    }

    public final  String toString() {
	return "Ctx( " +  (vhost==null ? "" :
					    vhost + ":" )  +  path +  ")";
    }

    // ------------------- Logging ---------------

    public final  String getId() {
	return ((vhost==null) ? "" : vhost + ":" )  +  path;
    }
    
    /** Internal log method
     */
    public final void log(String msg) {
	loghelper.log(msg);
    }

    /** Internal log method
     */
    public final  void log(String msg, Throwable t) {
	loghelper.log(msg, t);
    }

    /** Internal log method
     */
    public final  void log(String msg, Throwable t, int level) {
	loghelper.log(msg, t, level);
    }

    /** User-level log method ( called from a servlet).
     *  Context supports 2 log streams - one is used by the
     *  tomcat core ( internals ) and one is used by 
     *  servlets
     */
    public final  void logServlet( String msg , Throwable t ) {
	if (loghelperServlet == null) {
	    String pr= getId();
	    loghelperServlet = new Log("servlet_log", pr );
	}
	if (t == null)
	    loghelperServlet.log(msg);	// uses level INFORMATION
	else
	    loghelperServlet.log(msg, t); // uses level ERROR
    }

    public final  void setLogger(Logger logger) {
	if (loghelper == null) {
	    String pr=getId();
	    loghelper = new Log("tc_log", pr );
	}
	loghelper.setLogger(logger);
    }

    public final  void setServletLogger(Logger logger) {
	if (loghelperServlet == null) {
	    String pr=getId();
	    loghelperServlet = new Log("servlet_log",pr);
	}
	loghelperServlet.setLogger(logger);
    }

    public final  Log getLog() {
	return loghelper;
    }

    public final  Log getServletLog() {
	return loghelperServlet;
    }

    // -------------------- Path methods  --------------------

    /**  What is reported in the "Servlet-Engine" header
     *   for this context. It is set automatically by
     *   a facade interceptor.
     *   XXX Do we want to allow user to customize it ?
     */
    public final  void setEngineHeader(String s) {
        engineHeader=s;
    }

    /**  
     */
    public final  String getEngineHeader() {
	return engineHeader;
    }

    // -------------------- Work dir --------------------
    
    /**
     *  Work dir is a place where servlets are allowed
     *  to write
     */
    public final  void setWorkDir(String workDir) {
	this.workDir = new File(workDir);
    }

    /**  
     */
    public final  File getWorkDir() {
	return workDir;
    }

    /**  
     */
    public final  void setWorkDir(File workDir) {
	this.workDir = workDir;
    }

    // -------------------- Virtual host support --------------------
    
    /** Virtual host support - this context will be part of 
     *  a virtual host with the specified name. You should
     *  set all the aliases. XXX Not implemented
     */
    public final  void addHostAlias( String alias ) {
	vhostAliases.addElement( alias );
    }

    public final  Enumeration getHostAliases() {
	return vhostAliases.elements();
    }
    // -------------------- Security - trusted code -------------------- 

    /** Mark the webapplication as trusted, i.e. it can
     *  access internal objects and manipulate tomcat core
     */
    public final  void setTrusted( boolean t ) {
	trusted=t;
    }

    public final  boolean isTrusted() {
	return trusted;
    }

    // -------------------- Per-context interceptors ----------

    /** Add a per-context interceptor. The hooks defined will
     *  be used only for requests that are matched in this context.
     *  contextMap hook is not called ( since the context is not
     *	known at that time
     */
    public final  void addInterceptor( BaseInterceptor ri )
	throws TomcatException
    {
	// the interceptor can be added before or after the
	// context is added.
	if( contextM!=null ) {
	    // make sure the interceptor is properly initialized
	    ri.setContextManager( contextM );

	    BaseInterceptor existingI[]=defaultContainer.getInterceptors();
	    for( int i=0; i<existingI.length; i++ ) {
		existingI[i].addInterceptor( contextM, this, ri );
	    }

	    // if we are already added, make sure engine init is called
	    ri.engineInit( contextM );
	}

	defaultContainer.addInterceptor(ri);

    }

}