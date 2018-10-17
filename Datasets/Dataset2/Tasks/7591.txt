public static final String TOMCAT_VERSION = "3.3.1 Dev";

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

import org.apache.tomcat.util.log.Log;

import java.util.Hashtable;
import java.util.Vector;
import java.util.Enumeration;


/**
  ContextManager controls requests processing and server configuration.
  It maintains a list of Contexts ( web applications )  and a list of
  global modules that deal with server configuration and request processing,
  and global properties ( directories, general settings, etc ).

  The request processing is similar with Apache and other servers, with the
  addition of a "contextMap" chain that will select a tomcat-specific.
 
  <h2>Configuration and startup</h2>

  Starting tomcat involves a number of actions and states. In order to
  start tomcat:
  
  <ol>
  <li> Create ContextManager. The server state is STATE_NEW

  <li> Set properties for ContextManager ( home, debug, etc).

  <li> Add the initial set of modules ( addInterceptor() ). ContextManager
       will call setContextManager() and then the addInterceptor() hook.

  <li> Add the initial set of web applications ( Contexts ). Configuration
       modules can also add web applications - but no "addContext" hook
       will be called ( since the server is not initialized ).

  <li> Call init().
       <ol>
         <li>Init will notify all modules using the engineInit() hook. At
	 this point the ContextManager will be in STATE_CONFIG.
	 <li>It'll then call addContext() hooks for each context that were
	 added by config modules. Contexts will be in STATE_ADDED.
	 <li>It'll then call context.init() hooks for each context that were
	 added by config modules. Contexts will be in STATE_READY.
	 <li>After all contexts are added and initialized, server will be
	 in STATE_INIT.
       </ol>
  XXX Do we need finer control ? ( like initModules(), initContexts() ? )
       
  <li> At this point the server is fully configured, but not started.
       The user can add/remove modules and applications - the rules are
       defined in "run-time configuration".

  <li> Call start(). The engineStart() hook will be called,
  the connector modules should accept and serve requests. 

  <li> Call stop() to stop the server ( engineStop() hook will be called,
  no requests more will be accepted )

  <li> Call shutdown() to clean up all resources in use by web applications
  and modules. The server will revert to STATE_CONFIG.
       <ol>
         <li>contextShutdown() will be called for each application. Modules
	 must clean any resources allocated for that context. 

	 <li>removeContext() will be called for each application.

	 <li>engineShutdown() will be called for each module
       </ol>

  </ol>


  <h2>Runtime configuration</h2>

  XXX The only "supported" feature is adding/removing web applications.
  Since each module can have a set of local modules, you can change the
  configuration or modules for each context. Changing "global" modules may
  work, but it's not finalized or tested.
  
  While tomcat is running, you can temporarily disable web applications,
  remove and add new applications.
  
  @author James Duncan Davidson [duncan@eng.sun.com]
  @author James Todd [gonzo@eng.sun.com]
  @author Harish Prabandham
  @author Costin Manolache
  @author Hans Bergsten [hans@gefionsoftware.com]
 */
public class ContextManager {
    /** Official name and version
     */
    public static final String TOMCAT_VERSION = "3.3 Final";
    public static final String TOMCAT_NAME = "Tomcat Web Server";
    
    /** System property used to set the base directory ( tomcat home ).
     *  use -DTOMCAT_HOME= in java command line or as a System.setProperty.
     */
    public static final String TOMCAT_HOME="tomcat.home";

    /** System property used to set the install directory ( tomcat install ).
     *  use -DTOMCAT_INSTALL= in java command line or as a System.setProperty.
     */
    public static final String TOMCAT_INSTALL="tomcat.install";

    // State

    /**
     *  Server is beeing configured - modules are added.
     */
    public static final int STATE_NEW=0;

    /**
     *  Server and global modules are initialized and stable.
     */
    public static final int STATE_CONFIG=1;

    /**
     *  Web applications are  configured and initialized.
     */
    public static final int STATE_INIT=2;
 
    /**
     *  Server is started and may process requests.
     */
    public static final int STATE_START=3;

    // -------------------- local variables --------------------

    private int state=STATE_NEW;
    
    // All contexts managed by the server ( can belong to different
    // virtual hosts )
    private Vector contextsV=new Vector();
    private Hashtable contexts=new Hashtable();

    private int debug=0;

    /** Private workspace for this server
     */
    private String workDir="work";

    /** The base directory where this instance runs.
     *  It can be different from the install directory to
     *  allow one install per system and multiple users
     */
    private String home;

    /** The directory where tomcat is installed
     */
    private String installDir;
    
    // Server properties ( interceptors, etc ) - it's one level above "/"
    private Container defaultContainer;

    // the embedding application loader. @see getParentLoader
    private ClassLoader parentLoader;

    // the common class loader, shared by container and apps
    private ClassLoader commonLoader;

    // the container class loader, used to load all container modules
    private ClassLoader containerLoader;

    // the webapp loader, with classes shared by all webapps.
    private ClassLoader appsLoader;

    private Hashtable properties=new Hashtable();
    
    /**
     * Construct a new ContextManager instance with default values.
     */
    public ContextManager() {
        defaultContainer=createContainer();
        defaultContainer.setContext( null );
	defaultContainer.setContextManager( this );
        defaultContainer.setPath( null ); // default container
    }

    // -------------------- setable properties --------------------

    /**
     *  The home of the tomcat instance - you can have multiple
     *  users running tomcat, with a shared install directory.
     *  
     *  Home is used as a base for logs, webapps, local config.
     *  Install dir ( if different ) is used to find lib ( jar
     *   files ).
     *
     *  The "tomcat.home" system property is used if no explicit
     *  value is set. XXX
     */
    public void setHome(String home) {
	this.home=home;
	if( home != null ) 
	    System.getProperties().put(TOMCAT_HOME, home );
    }

    public String getHome() {
	return home;
    }

    /**
     *  Get installation directory. This is used to locate
     *  jar files ( lib ). If tomcat instance is shared,
     *  home is used for webapps, logs, config.
     *  If either home or install is not set, the other
     *  is used as default.
     * 
     */
    public String getInstallDir() {
	return installDir;
    }

    public void setInstallDir( String tH ) {
	installDir=tH;
    }

    /**
     * WorkDir property - where all working files will be created
     */
    public void setWorkDir( String wd ) {
	if(debug>0) log("set work dir " + wd);
	this.workDir=wd;
    }

    public String getWorkDir() {
	return workDir;
    }


    /** Debug level
     */
    public void setDebug( int level ) {
	if( level != debug )
	    log( "Setting debug level to " + level);
	debug=level;
    }

    public final int getDebug() {
	return debug;
    }

    //  XmlMapper will call setProperty(name,value) if no explicit setter
    // is found - it's better to use this mechanism for special
    // properties ( that are not generic enough and used by few specific
    // module )

    /** Generic properties support. You can get properties like
     *  "showDebugInfo", "randomClass", etc.
     */
    public String getProperty( String name ) {
	return (String)properties.get( name );
    }

    public void setProperty( String name, String value ) {
	if( name!=null && value!=null )
	    properties.put( name, value );
    }

    public Hashtable getProperties() {
	return properties;
    }
    
    // -------------------- Other properties --------------------

    /** Return the current state of the tomcat server.
     */
    public final int getState() {
	return state;
    }

    /** Change the state, after notifying all modules about the change
     *  Any error will be propagated - the server will not change the
     *  state and should fail if any module can't handle that.
     */
    public void setState( int state )
	throws TomcatException
    {
	BaseInterceptor existingI[]=defaultContainer.getInterceptors();
	for( int i=0; i<existingI.length; i++ ) {
	    existingI[i].engineState( this, state );
	}
	this.state=state;
    }

    protected void setState1( int state ) {
	this.state=state;
    }
    
    /**
     *  Parent loader is the "base" class loader of the
     *	application that starts tomcat, and includes no
     *	tomcat classes.
     * 
     *  Each web applications will use a loader that will have it as
     *  a parent loader, so all classes visible to parentLoader
     *  will be available to servlets.
     *
     *  Tomcat will add the right servlet.jar and Facade.
     *
     *  Trusted applications will also see the internal tomcat
     *  classes.
     *
     *  Interceptors may also add custom classes to a webapp,
     *  based on tomcat configuration.
     *
     *  Tomcat.core and all internal classes will be loaded by
     *  another class loader, having the same parentLoader.
     *
     *  <pre>
     *  parentLoader  -> tomcat.core.loader [ -> trusted.webapp.loader ]
     *                -> webapp.loaders
     *  </pre>
     */
    public void setParentLoader( ClassLoader cl ) {
	parentLoader=cl;
    }

    public ClassLoader getParentLoader() {
	return parentLoader;
    }

    public void setCommonLoader( ClassLoader cl ) {
	commonLoader=cl;
    }

    public ClassLoader getCommonLoader() {
	return commonLoader;
    }

    public void setContainerLoader( ClassLoader cl ) {
	containerLoader=cl;
    }

    public ClassLoader getContainerLoader() {
	return containerLoader;
    }

    public void setAppsLoader( ClassLoader cl ) {
	appsLoader=cl;
    }

    public ClassLoader getAppsLoader() {
	return appsLoader;
    }

    /** Default container. The interceptors for this container will
	be called for all requests, and it will be associated with
	invalid requests ( where context can't be found ).
     */
    public Container getContainer() {
        return defaultContainer;
    }

    public void setContainer(Container newDefaultContainer) {
        defaultContainer = newDefaultContainer;
    }

    /** Add a global interceptor. The addInterceptor() hook will be called.
     *  If the module is added after STATE_CONFIG, the engineInit() hook will
     *  be called ( otherwise we wait for init() ).
     *  If the module is added after STATE_INIT, the addContext and
     *  initContext hooks will be called.
     *  If the module is added after STATE_START, the engineStart hooks will
     *  be called.
     */
    public void addInterceptor( BaseInterceptor ri )
	throws TomcatException
    {
	ri.setContextManager( this );

	// first, add the module ( addInterceptor may change the ordering )
        defaultContainer.addInterceptor(ri);

	// second, let the module know it's added. It may look at
	// other module and even choose to remove himself and throw exception.
	ri.addInterceptor( this, null, ri ); // should know about itself

	// let other modules know about the new friend.
	BaseInterceptor existingI[]=defaultContainer.getInterceptors();
	for( int i=0; i<existingI.length; i++ ) {
	    if( existingI[i] != ri )
		existingI[i].addInterceptor( this, null, ri );
	}
	
	// startup module, server is not initialized
	if( state==STATE_NEW ) return;

	// we are at last initialized, call engineInit hook ( a module
	// at runtime will get the same calls as a setup module )
	ri.engineInit( this );

	if( state== STATE_CONFIG ) return;
	
	// addContext hook for all existing contexts
	Enumeration enum = getContexts();
	while (enum.hasMoreElements()) {
	    Context ctx = (Context)enum.nextElement();
	    try {
		ri.addContext( this, ctx ); 
	    } catch( TomcatException ex ) {
		log( "Error adding context " +ctx + " to " + ri ); // ignore
	    }
	}
	
	// contextInit hook if we're started
	enum = getContexts();
	while (enum.hasMoreElements()) {
	    Context ctx = (Context)enum.nextElement();
	    try {
		ri.contextInit( ctx );
	    } catch( TomcatException ex ) {
		log( "Error adding context " +ctx + " to " + ri );
		    // ignore it
	    }
	}

	if( state==STATE_INIT ) return;

	// we are running - let the module know about that.
	ri.engineStart(this);
    }

    /** Remove a module. Hooks will be called to allow the module to
     *  free the resources. 
     */
    public void removeInterceptor( BaseInterceptor ri )
	throws TomcatException
    {
	
	BaseInterceptor existingI[]=defaultContainer.getInterceptors();
	for( int i=0; i<existingI.length; i++ ) {
	    existingI[i].removeInterceptor( this, null, ri );
	}
	ri.removeInterceptor( this, null, ri );
	
	defaultContainer.removeInterceptor( ri );

	if( state==STATE_NEW ) return;

	if( state==STATE_START )
	    ri.engineStop(this);

	if( state >= STATE_INIT ) {
	    Enumeration enum = getContexts();
	    while (enum.hasMoreElements()) {
		Context ctx = (Context)enum.nextElement();
		try {
		    ri.contextShutdown( ctx );
		} catch( TomcatException ex ) {
		    log( "Error shuting down context " +ctx + " to " + ri );
		}
	    }
	    
	    enum = getContexts();
	    while (enum.hasMoreElements()) {
		Context ctx = (Context)enum.nextElement();
		try {
		    ri.removeContext( this, ctx ); 
		} catch( TomcatException ex ) {
		    log( "Error removing context " +ctx + " to " + ri );
		    // ignore it
		}
	    }
	}

    }

    // -------------------- Server functions --------------------

    /**
     *  Init() is called after the context manager is set up (properties)
     *  and configured ( modules ).
     *
     *  All engineInit() hooks will be called and the server will 
     *  move to state= INIT
     * 
     */
    public void init()  throws TomcatException {
	if( state >= STATE_CONFIG  ) // already initialized
	    return;
	
	if(debug>0 ) log( "Tomcat init");
	
	BaseInterceptor existingI[]=defaultContainer.getInterceptors();
	for( int i=0; i<existingI.length; i++ ) {
	    existingI[i].engineInit( this );
	}

	// The server is configured, all modules are ready
	setState(STATE_CONFIG);
	log("Tomcat configured and in stable state ");
	
	existingI=defaultContainer.getInterceptors();
	// deal with contexts that were added before init()
	// ( by user or modules during engineInit )

	// first trusted apps - they may do special actions
	Enumeration enum = getContexts();
	while (enum.hasMoreElements()) {
	    Context ctx = (Context)enum.nextElement();
	    if( ctx.isTrusted() )
		fireAddContext(ctx, existingI );
	}
	
	// Initialize the contexts
	enum = getContexts();
	while (enum.hasMoreElements()) {
	    Context ctx = (Context)enum.nextElement();
	    if( ctx.isTrusted() ) {
		try {
		    ctx.init();
		} catch( TomcatException ex ) {
		    // just log the error - the context will not serve requests
		    log( "Error initializing " + ctx , ex );
		    continue; 
		}
	    }
	}

	// again - it may change
	existingI=defaultContainer.getInterceptors();

	// Same thing for untrusted apps 
	enum = getContexts();
	while (enum.hasMoreElements()) {
	    Context ctx = (Context)enum.nextElement();
	    if( ! ctx.isTrusted() )
		fireAddContext(ctx, existingI );
	}

	// Initialize the contexts
	enum = getContexts();
	while (enum.hasMoreElements()) {
	    Context ctx = (Context)enum.nextElement();
	    if( ! ctx.isTrusted() ) {
		try {
		    ctx.init();
		} catch( TomcatException ex ) {
		    // just log the error - the context will not serve requests
		    log( "Error initializing " + ctx , ex );
		    continue; 
		}
	    }
	}

	setState( STATE_INIT );
    }

    private void fireAddContext(Context ctx, BaseInterceptor existingI[] ) {
	ctx.setContextManager( this );
	try {
	    for( int i=0; i<existingI.length; i++ ) {
		existingI[i].addContext( this, ctx );
	    }
	} catch( TomcatException ex ) {
	    log( "Error adding context " + ctx , ex );
	    return; 
	}
	try {
	    // set state may throw exception
	    ctx.setState( Context.STATE_ADDED );
	    log("Adding  " +  ctx.toString());
	} catch( TomcatException ex ) {
	    log( "Error adding context " + ctx , ex );
	    return; 
	}
    }
    
    /** Will start the connectors and begin serving requests.
     *  It must be called after init.
     */
    public void start() throws TomcatException {
	if( state==STATE_NEW ) {
	    init();
	}
        if( state==STATE_START ) return;
	BaseInterceptor cI[]=defaultContainer.getInterceptors();
	for( int i=0; i< cI.length; i++ ) {
	    cI[i].engineStart( this );
	}

	// requests can be processed now
	setState(STATE_START);
    }

    /** Will stop all connectors
     */
    public void stop() throws TomcatException {
	setState(STATE_INIT); // initialized, but not accepting connections
	
	BaseInterceptor cI[]=defaultContainer.getInterceptors();
	for( int i=0; i< cI.length; i++ ) {
	    cI[i].engineStop( this );
	}
    }

    /** Remove all contexts.
     *  - call removeContext ( that will call Interceptor.removeContext hooks )
     *  - call Interceptor.engineShutdown() hooks.
     */
    public void shutdown() throws TomcatException {
        if( state==STATE_START ) stop();

	Enumeration enum = getContexts();
	while (enum.hasMoreElements()) {
	    Context ctx = (Context)enum.nextElement();
	    try {
		ctx.shutdown();
	    } catch( TomcatException ex ) {
		log( "Error shuting down context " +ctx );
	    }
	}
	// No need to remove - since init() doesn't add the contexts.
	// Modules could remove contexts ( and add them in init() ), but who
	// adds should also remove
	// 	while (!contextsV.isEmpty()) {
	// 	    try {
	// 		Context ctx=(Context)contextsV.firstElement();
	// 		removeContext(ctx);
	// 	    } catch(Exception ex ) {
	// 		log( "shutdown.removeContext" , ex );
	// 	    }
	// 	}

	// Notify all modules that the server will shutdown,
	// let them clean up all resources

	BaseInterceptor cI[]=defaultContainer.getInterceptors();
	for( int i=0; i< cI.length; i++ ) {
	    try {
		cI[i].engineShutdown( this );
	    } catch( Exception ex ) {
		log( "shutdown.engineShutdown" , ex );
	    }
	}

	setState( STATE_NEW );
	// remove the modules ( XXX do we need that ? )
	// 	for( int i=0; i< cI.length; i++ ) {
	// 	    try {
	// 		removeInterceptor( cI[i] );
	// 	    } catch( Exception ex ) {
	// 		log( "shutdown.removeInterceptor" , ex );
	// 	    }
	// 	}
    }

    // -------------------- Contexts --------------------

    /** Return the list of contexts managed by this server.
     *  Tomcat can handle multiple virtual hosts. 
     *
     *  All contexts are stored in ContextManager when added.
     *  Modules can use the information in context ( when addContext
     *  hook is called ) and prepare mapping tables.
     */
    public Enumeration getContexts() {
	return contextsV.elements();
    }

    public Enumeration getContextNames() {
	return contexts.keys();
    }

    public Context getContext(String name ) {
	return (Context)contexts.get( name );
    }
    
    /**
     * Adds a new Context to the set managed by this ContextManager.
     * It'll also init the server if it hasn't been already.
     *
     * All addContext hooks will be called. The context will be
     * in STATE_ADDED - it'll not serve requests.
     *
     * @param ctx context to be added.
     */
    public void addContext( Context ctx ) throws TomcatException {
	// Make sure context knows about its manager.
	// this will also initialized all context-specific modules.
	ctx.setContextManager( this );
	ctx.setState( Context.STATE_NEW );

	contextsV.addElement( ctx );
	contexts.put( ctx.getName(), ctx );

	if( getState() == STATE_NEW )
	    return;

	// we are at least configured, can call the hook
	try {
	    BaseInterceptor cI[]=ctx.getContainer().getInterceptors();
	    for( int i=0; i< cI.length; i++ ) {
		// If an exception is thrown, context will remain in
		// NEW state.
		cI[i].addContext( this, ctx ); 
	    }
	    ctx.setState( Context.STATE_ADDED );
	    log("Adding context " +  ctx.toString());
	} catch (TomcatException ex ) {
	    log( "Context not added " + ctx , ex );
	    throw ex;
	}
    }


    /** Shut down and removes a context from service.
     */
    public void removeContext( Context context ) throws TomcatException {
	if( context==null ) return;

	log( "Removing context " + context.toString());

	contextsV.removeElement(context);
	contexts.remove( context.getName());

	if( getState() == STATE_NEW )
	    return; // we are not even initialized
	// modules can add/remove contexts at init time, but no
	// action will take place until the server is stable.
	
	// if it's already disabled - or was never activated,
	// no need to shutdown and remove
	if( context.getState() == Context.STATE_NEW )
	    return;
	
	// disable the context - it it is running 
	if( context.getState() == Context.STATE_READY )
	    context.shutdown();

	// remove it from operation - notify interceptors that
	// this context is no longer active
	BaseInterceptor cI[]=context.getContainer().getInterceptors();
	for( int i=0; i< cI.length; i++ ) {
	    cI[i].removeContext( this, context );
	}

	// mark the context as "not active" 
	context.setState( Context.STATE_NEW );
    }


    // -------------------- Request processing / subRequest ------------------
    // -------------------- Main request processing methods ------------------

    /** Prepare the req/resp pair for use in tomcat.
     *  Call it after you create the request/response objects.
     *  ( for example in a connector, or when an internal sub-request is
     *  created )
     */
    public void initRequest( Request req, Response resp ) {
	// We may add other special calls here.
	resp.setRequest( req );
	req.setResponse( resp );
	req.setContextManager( this );
	resp.init();
    }

    /** This is the entry point in tomcat - the connectors ( or any other
     *  component able to generate Request/Response implementations ) will
     *  call this method to get it processed.
     */
    public void service( Request req, Response res ) {
	if( state!=STATE_START ) {
	    // A request was received before all components are
	    // in started state. Than can happen if the adapter was
	    // started too soon or of the server is temporarily
	    // disabled.
	    req.setAttribute("javax.servlet.error.message",
			     "Server is starting");
	    handleStatus( req, res, 503 ); // service unavailable
	} else {
	    internalService( req, res );
	}
	
	// clean up
	try {
	    res.finish();
	} catch( Throwable ex ) {
	    handleError( req, res, ex );
	}
	finally {
	    BaseInterceptor reqI[];
	    if( req.getContext()==null )
		reqI=getContainer().getInterceptors( Container.H_handleError );
	    else
		reqI= req.getContext().getContainer().
		    getInterceptors(Container.H_postRequest);

	    for( int i=0; i< reqI.length; i++ ) {
		reqI[i].postRequest( req, res );
	    }
	    req.recycle();
	    res.recycle();
	}
	return;
    }

    // Request processing steps and behavior
    private void internalService( Request req, Response res ) {
	try {
	    /* assert req/res are set up
	       corectly - have cm, and one-one relation
	    */
	    // wrong request - parsing error
	    int status=res.getStatus();

	    if( status >= 400 ) {
		if( debug > 0)
		    log( "Error reading request " + req + " " + status);
		handleStatus( req, res, status ); 
		return;
	    }

	    status= processRequest( req );

	    if( status != 0 ) {
		if( debug > 0)
		    log("Error mapping the request " + req + " " + status);
		handleStatus( req, res, status );
		return;
	    }

	    if( req.getHandler() == null ) {
		status=404;
		if( debug > 0)
		    log("No handler for request " + req + " " + status);
		handleStatus( req, res, status );
		return;
	    }

	    Container sct=req.getSecurityContext();
	    if(sct != null ) {
		status=0;
		BaseInterceptor reqI[];
		// assert( req.getContext()!=null ) - checked in processRequest
		reqI = req.getContext().getContainer().
		    getInterceptors(Container.H_authorize);

		// Call all authorization callbacks. 
		for( int i=0; i< reqI.length; i++ ) {
		    status = reqI[i].authorize( req, res, sct.getRoles() );
		    if ( status != BaseInterceptor.DECLINED ) {
			break;
		    }
		}
	    }
	    if( status != BaseInterceptor.OK ) {
		if( debug > 0)
		    log("Unauthorized " + req + " " + status);
		if( status==BaseInterceptor.DECLINED )
		    status=401; // unauthorized
		handleStatus( req, res, status );
		return;
	    }

	    req.getHandler().service(req, res);

	} catch (Throwable t) {
	    handleError( req, res, t );
	}
    }

    /** Will find the Handler for a servlet, assuming we already have
     *  the Context. This is also used by Dispatcher and getResource -
     *  where the Context is already known.
     *
     *  This method will only map the request, it'll not do authorization
     *  or authentication.
     */
    public int processRequest( Request req ) {
	if(debug>9) log("Before processRequest(): "+req.toString());

	int status=0;
        BaseInterceptor ri[];
	ri=defaultContainer.getInterceptors(Container.H_postReadRequest);
	
	for( int i=0; i< ri.length; i++ ) {
	    status=ri[i].postReadRequest( req );
	    if( status!=0 ) return status;
	}

	ri=defaultContainer.getInterceptors(Container.H_contextMap);
	
	for( int i=0; i< ri.length; i++ ) {
	    status=ri[i].contextMap( req );
	    if( status!=0 ) return status;
	}
	req.setState(Request.STATE_CONTEXT_MAPPED );

	if( req.getContext() == null) {
	    req.setAttribute("javax.servlet.error.message",
			     "No context found");
	}
	if( req.getContext().getState() != Context.STATE_READY ) {
	    // the context is not fully initialized.
	    req.setAttribute("javax.servlet.error.message",
			     "Context " + req.getContext() + " not ready");
	    // return error code - the caller will handle it
	    return 503;
	}
	
	ri=req.getContext().getContainer().
	    getInterceptors(Container.H_requestMap);
	for( int i=0; i< ri.length; i++ ) {
	    if( debug > 1 )
		log( "RequestMap " + ri[i] );
	    status=ri[i].requestMap( req );
	    if( status!=0 ) return status;
	}
	req.setState(Request.STATE_MAPPED );

	if(debug>9) log("After processRequest(): "+req.toString());

	return 0;
    }


    // -------------------- Sub-Request mechanism --------------------

    /** Create a new sub-request in a given context, set the context "hint"
     *  This is a particular case of sub-request that can't get out of
     *  a context ( and we know the context before - so no need to compute it
     *  again)
     *
     *  Note that session and all stuff will still be computed.
     */
    public Request createRequest( Context ctx, String urlPath ) {
	// assert urlPath!=null

	// deal with paths with parameters in it
	String contextPath=ctx.getPath();
	String origPath=urlPath;

	// append context path
	if( !"".equals(contextPath) && !"/".equals(contextPath)) {
	    if( urlPath.startsWith("/" ) )
		urlPath=contextPath + urlPath;
	    else
		urlPath=contextPath + "/" + urlPath;
	} else {
	    // root context
	    if( !urlPath.startsWith("/" ) )
		urlPath= "/" + urlPath;
	}

	if( debug >4 ) log("createRequest " + origPath + " " + urlPath  );
	Request req= createSubRequest( ctx.getHost(), urlPath );
	req.setContext( ctx );
	return req;
    }

    /** Create a new sub-request, deal with query string
     */
    private Request createSubRequest( String host, String urlPath ) {
	String queryString=null;
	int i = urlPath.indexOf("?");
	int len=urlPath.length();
	if (i>-1) {
	    if(i<len)
		queryString =urlPath.substring(i + 1, urlPath.length());
	    urlPath = urlPath.substring(0, i);
	}

	Request lr = createRequest();
	Response res = createResponse(lr);
	lr.setContextManager( this );
	lr.setResponse( res );
	res.setRequest( lr );
	lr.requestURI().setString( urlPath );
	lr.queryString().setString(queryString );

	if( host != null) lr.serverName().setString( host );

	return lr;
    }

    /**
     *   Find a context by doing a sub-request and mapping the request
     *   against the active rules ( that means you could use a /~costin
     *   if a UserHomeInterceptor is present )
     *
     *   The new context will be in the same virtual host as base.
     *
     */
    public  Context getContext(Context base, String path) {
	// XXX Servlet checks should be done in facade
	if (! path.startsWith("/")) {
	    return null; // according to spec, null is returned
	    // if we can't  return a servlet, so it's more probable
	    // servlets will check for null than IllegalArgument
	}
	// absolute path
	Request lr=this.createSubRequest( base.getHost(), path );
	this.processRequest(lr);
        return lr.getContext();
    }


    // -------------------- Error handling --------------------

    /** Called for error-codes. Will call the error hook with a status code.
     */
    public void handleStatus( Request req, Response res, int code ) {
	if( code!=0 )
	    res.setStatus( code );
	
	BaseInterceptor ri[];
	int status;
	if( req.getContext()==null )
	    ri=getContainer().getInterceptors( Container.H_handleError );
	else
	    ri=req.getContext().getContainer().
		getInterceptors( Container.H_handleError );
	
	for( int i=0; i< ri.length; i++ ) {
	    status=ri[i].handleError( req, res, null );
	    if( status!=0 ) return;
	}
    }

    /**
     *  Call error hook with an exception code.
     */
    public void handleError( Request req, Response res , Throwable t  ) {
	BaseInterceptor ri[];
	int status;
	if( req.getContext() == null )
	    ri=getContainer().getInterceptors( Container.H_handleError );
	else
	    ri=req.getContext().getContainer().
		getInterceptors( Container.H_handleError );
	if( ri==null ) {
	    log( "handleError with no error handlers " + req + " " + req.getContext());
	    return;
	}
	for( int i=0; i< ri.length; i++ ) {
	    status=ri[i].handleError( req, res, t );
	    if( status!=0 ) return;
	}
    }

    // -------------------- Support for notes --------------------

    /** Note id counters. Synchronized access is not necesarily needed
     *  ( the initialization is in one thread ), but anyway we do it
     */
    public static final int NOTE_COUNT=8;
    private  int noteId[]=new int[NOTE_COUNT];

    /** Maximum number of notes supported
     */
    public static final int MAX_NOTES=32;
    public static final int RESERVED=5;

    public static final int SERVER_NOTE=0;
    public static final int CONTAINER_NOTE=1;
    public static final int REQUEST_NOTE=2;
    public static final int HANDLER_NOTE=3;
    public static final int SESSION_NOTE=4;
    public static final int MODULE_NOTE=5;
    
    public static final int REQ_RE_NOTE=0;

    private String noteName[][]=new String[NOTE_COUNT][MAX_NOTES];
    
    /** used to allow interceptors to set specific per/request, per/container
     * and per/CM informations.
     *
     * This will allow us to remove all "specialized" methods in
     * Request and Container/Context, without losing the functionality.
     * Remember - Interceptors are not supposed to have internal state
     * and minimal configuration, all setup is part of the "core", under
     *  central control.
     *  We use indexed notes instead of attributes for performance -
     * this is internal to tomcat and most of the time in critical path
     */

    /** Create a new note id. Interceptors will get an Id at init time for
     *  all notes that it needs.
     *
     *  Throws exception if too many notes are set ( shouldn't happen in
     *  normal use ).
     *  @param noteType The note will be associated with the server,
     *   container or request.
     *  @param name the name of the note.
     */
    public synchronized int getNoteId( int noteType, String name )
	throws TomcatException
    {
	// find if we already have a note with this name
	// ( this is in init(), not critical )
	for( int i=0; i< noteId[noteType] ; i++ ) {
	    if( name.equals( noteName[noteType][i] ) )
		return i;
	}

	if( noteId[noteType] >= MAX_NOTES )
	    throw new TomcatException( "Too many notes ");

	// make sure the note id is > RESERVED
	if( noteId[noteType] < RESERVED ) noteId[noteType]=RESERVED;

	noteName[noteType][ noteId[noteType] ]=name;
	return noteId[noteType]++;
    }

    public String getNoteName( int noteType, int noteId ) {
	return noteName[noteType][noteId];
    }

    // -------------------- Per-server notes --------------------
    private Object notes[]=new Object[MAX_NOTES];
    
    public final void setNote( int pos, Object value ) {
	notes[pos]=value;
    }

    public final Object getNote( int pos ) {
	return notes[pos];
    }

    public Object getNote( String name ) throws TomcatException {
	int id=getNoteId( SERVER_NOTE, name );
	return getNote( id );
    }

    public void setNote( String name, Object value ) throws TomcatException {
	int id=getNoteId( SERVER_NOTE, name );
	setNote( id, value );
    }
    
    // -------------------- Logging and debug --------------------

    // default, is going to console until replaced (unless aleady configured)
    private Log loghelper = Log.getLog("org/apache/tomcat/core",
				       "ContextManager");
    /**
     * So other classes can piggyback on the context manager's log
     * stream.
     **/
    public Log getLog() {
	return loghelper;
    }

    public void setLog(Log log) {
	loghelper=log;
    }
 
    public void log(String msg) {
	loghelper.log(msg);
    }

    public void log(String msg, Throwable t) {
        loghelper.log(msg, t);
    }

    public void log(String msg, int level) {
        loghelper.log(msg, level);
    }

    public void log(String msg, Throwable t, int level) {
        loghelper.log(msg, t, level);
    }

    // -------------------- Factories --------------------

    public Context createContext() {
	return new Context();
    }

    public Request createRequest() {
	Request req=new Request();
	//Response res=new Response();
	//initRequest( req, res );
	return req;
	
    }

    public Response createResponse(Request req) {
	//return req.getResponse();
	return new Response();
    }

    public Container createContainer() {
	return new Container();
    }

    public OutputBuffer createOutputBuffer() {
	return new OutputBuffer();
    }

    public OutputBuffer createOutputBuffer(int size) {
	return new OutputBuffer(size);
    }

    public ServerSession createServerSession() {
	ServerSession ss=new ServerSession();
	ss.setContextManager( this );
	return ss;
    }
}