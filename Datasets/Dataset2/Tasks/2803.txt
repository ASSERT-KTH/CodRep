BaseInterceptor reqI[]= req.getContext().getContainer().

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

import org.apache.tomcat.core.*;
import org.apache.tomcat.context.*;
import org.apache.tomcat.request.*;
import org.apache.tomcat.util.*;
import org.apache.tomcat.util.log.*;
import java.io.*;
import java.net.*;
import java.util.*;

/**
  ContextManager is the entry point and "controler" of the servlet execution.
  It maintains a list of WebApplications and a list of global event
  interceptors that are set up to handle the actual execution.
 
  The ContextManager will direct the request processing flow
  from its arrival from the server/protocl adapter ( in service() ).
  It will do that by calling a number of hooks implemented by Interceptors.
 
  Hooks are provided for request parsing and mapping, auth, autorization,
  pre/post service, actual invocation and logging.
 
  ContextManager will also store properties that are global to the servlet
  container - like root directory, install dir, work dir.
 
  The extension mechanism for tomcat is the Interceptor.
  This class is final - if you need to change certain functionality
  you should add a new hook.
 
  ContextManager is not a singleton - it represent a servlet container
  instance ( with all associated ports and configurations ).
  One application may try to embed multiple ( distinct ) servlet containers -
  this feature hasn't been tested or used
 
 
   Expected startup order:

  1. Create ContextManager

  2. Set settable properties for ContextManager ( home, debug, etc)

  3. Add global Interceptors

  4. You may create, set and add Contexts. NO HOOKS ARE CALLED.
  
  5. Call init(). At this stage engineInit() callback will be
     called for all global interceptors.
     - DefaultCMSetter ( or a replacement ) must be the first in
     the chain and will adjust the paths and set defaults for
     all unset properties.
     - AutoSetup and other interceptors can automatically add/set
     more properties and make other calls.

     During engineInit() a number of Contexts are created and
     added to the server. No addContext() callback is called until
     the last engineInit() returns. ( XXX do we need this restriction ?)

  XXX I'n not sure about contextInit and about anything below.

  x. Server will move to INITIALIZED state. No callback other than engineInit
     can be called before the server enters this state.

  x. addContext() callbacks will be called for each context.
     After init you may add more contexts, and addContext() callback
     will be called (since the server is initialized )

  x. Call start().

  x. All contexts will be initialized ( contextInit()
     callback ).

  x. Server will move to STARTED state. No servlet should be 
     served before this state.

     
     During normal operation, it is possible to add  Contexts.

  1. Create the Context, set properties ( that can be done from servlets
     or by interceptors like ~user)

  2. call CM.addContext(). This will triger the addContext() callback.
     ( if CM is initialized )

  3. call CM.initContext( ctx ). This will triger contextInit() callback.
     After that the context is initialized and can serve requests.
     No request belonging to this context can't be served before this
     method returns.

     XXX Context state
     
     It is also possible to remove Contexts.

  1. Find the Context ( enumerate all existing contexts and find the one
    you need - host and path are most likely keys ).

  2. Call removeContext(). This will call removeContext() callbacks.

  
     To stop the server, you need to:

  1. Call shutdown().

  2. The server will ...

 
  @author James Duncan Davidson [duncan@eng.sun.com]
  @author James Todd [gonzo@eng.sun.com]
  @author Harish Prabandham
  @author costin@eng.sun.com
  @author Hans Bergsten [hans@gefionsoftware.com]
 */
public final class ContextManager implements LogAware{
    /** Official name and version
     */
    public static final String TOMCAT_VERSION = "3.3 dev";
    public static final String TOMCAT_NAME = "Tomcat Web Server";
    
    /** System property used to set the base directory ( tomcat home )
     */
    public static final String TOMCAT_HOME=
	"tomcat.home";

    // State

    /** Server is not initialized
     */
    public static final int STATE_PRE_INIT=0;
    /** Server was initialized, engineInit() was called.
	addContext() can be called.
     */
    public static final int STATE_INIT=1;

    /** Engine is running. All configured contexts are
	initialized ( contextInit()), and requests can be served.
     */
    public static final int STATE_START=2;

    /** Engine has stoped
     */
    public static final int STATE_STOP=3;
    
    // -------------------- local variables --------------------

    private int state=STATE_PRE_INIT;
    
    // All contexts managed by the server ( can belong to different
    // virtual hosts )
    private Vector contextsV=new Vector();

    private int debug=0;

    // Global properties for this tomcat instance:

    /** Private workspace for this server
     */
    private String workDir;

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

    // Store Loggers before initializing them
    private Hashtable loggers;

    /**
     * Construct a new ContextManager instance with default values.
     */
    public ContextManager() {
        defaultContainer=new Container();
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
     *  value is set.
     */
    public final void setHome(String home) {
	this.home=home;
    }

    public final String getHome() {
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
    public final String getInstallDir() {
	return installDir;
    }

    public final void setInstallDir( String tH ) {
	installDir=tH;
    }

    /**
     * WorkDir property - where all working files will be created
     */
    public final void setWorkDir( String wd ) {
	if(debug>0) log("set work dir " + wd);
	this.workDir=wd;
    }

    public final String getWorkDir() {
	return workDir;
    }


    /** Debug level
     */
    public final void setDebug( int level ) {
	if( level != debug )
	    log( "Setting debug level to " + level);
	debug=level;
    }

    public final int getDebug() {
	return debug;
    }

    // -------------------- Other properties --------------------

    public final int getState() {
	return state;
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
    public final void setParentLoader( ClassLoader cl ) {
	parentLoader=cl;
    }

    public final ClassLoader getParentLoader() {
	return parentLoader;
    }

    /** Default container. The interceptors for this container will
	be called for all requests, and it will be associated with
	invalid requests ( where context can't be found ).
     */
    public final Container getContainer() {
        return defaultContainer;
    }

    public final void setContainer(Container newDefaultContainer) {
        defaultContainer = newDefaultContainer;
    }

    public final void addInterceptor( BaseInterceptor ri ) {
	// The interceptors are handled per/container ( thanks to Nacho
	// for this contribution ).
        defaultContainer.addInterceptor(ri);
    }


    // -------------------- Server functions --------------------

    /**
     *  Init() is called after the context manager is set up
     *  and configured ( all setFoo methods are called, all initial
     *  interceptors are added and their setters are called ).
     *
     *  CM will:
     *   - call Interceptor.engineInit() hook
     *   - move to state= INIT
     *   - call Interceptor.addContext() hook for all contexts
     *     added before init() and those added  by interceptors in
     *     engineInit hook ).
     *
     *  It is possible to add and init contexts later. 
     *
     *  Note that addContext() is called each time a context is added,
     *  and that can be _before_ tomcat is initialized.
     *
     * @see addContext()
     */
    public final void init()  throws TomcatException {
	if(debug>0 ) log( "Tomcat init");

	BaseInterceptor cI[]=defaultContainer.getInterceptors();
	for( int i=0; i< cI.length; i++ ) {
	    cI[i].setContextManager( this );
	    cI[i].engineInit( this );
	}

	state=STATE_INIT;

	// delayed execution of addContext
	Enumeration existingCtxE=contextsV.elements();
	while( existingCtxE.hasMoreElements() ) {
	    Context ctx=(Context)existingCtxE.nextElement();
	    cI=ctx.getContainer().getInterceptors();
	    for( int i=0; i< cI.length; i++ ) {
		cI[i].addContext( this, ctx );
	    }
	    ctx.setState( Context.STATE_ADDED );
	}
    }

    /** Remove all contexts.
     *  - call removeContext ( that will call Interceptor.removeContext hooks )
     *  - call Interceptor.engineShutdown() hooks.
     */
    public final void shutdown() throws TomcatException {
	Enumeration enum = getContexts();
	while (enum.hasMoreElements()) {
	    removeContext((Context)enum.nextElement());
	}

	BaseInterceptor cI[]=defaultContainer.getInterceptors();
	for( int i=0; i< cI.length; i++ ) {
	    cI[i].engineShutdown( this );
	}
    }

    /** Will start the connectors and begin serving requests.
     *  It must be called after init.
     */
    public final void start() throws TomcatException {
	
	Enumeration enum = getContexts();
	while (enum.hasMoreElements()) {
	    Context ctx = (Context)enum.nextElement();
	    BaseInterceptor cI[]=ctx.getContainer().getInterceptors();
	    for( int i=0; i< cI.length; i++ ) {
		cI[i].contextInit( ctx );
	    }
	    ctx.setState( Context.STATE_READY );
	}
	
	state=STATE_START;
    }

    /** Will stop all connectors
     */
    public final void stop() throws Exception {
	shutdown();
    }

    // -------------------- Contexts --------------------

    /** Return the list of contexts managed by this server
     */
    public final Enumeration getContexts() {
	return contextsV.elements();
    }

    /**
     * Adds a new Context to the set managed by this ContextManager.
     *
     * If the server is initialized ( ContextManager.init() was called )
     * the addContext() hook will be called, otherwise the call will
     * be delayed until the server enters INIT state.
     *
     * The context will be in DISABLED state until start() is called.
     *
     * @param ctx context to be added.
     */
    public final void addContext( Context ctx ) throws TomcatException {
	log("Adding context " +  ctx.toString());
	
	// Make sure context knows about its manager.
	ctx.setContextManager( this );
	ctx.setState( Context.STATE_NEW );
	
	contextsV.addElement( ctx );

	if( state == STATE_PRE_INIT )
	    return; 
	
	BaseInterceptor cI[]=ctx.getContainer().getInterceptors();
	for( int i=0; i< cI.length; i++ ) {
	    cI[i].addContext( this, ctx );
	}
	ctx.setState( Context.STATE_ADDED );
    }

    /** Shut down and removes a context from service.
     */
    public final void removeContext( Context context ) throws TomcatException {
	if( context==null ) return;

	log( "Removing context " + context.toString());
	
	// disable the context.
	if( context.getState() == Context.STATE_READY )
	    shutdownContext( context );

	if( context.getState() == Context.STATE_DISABLED )
	    return;
	
	context.setState( Context.STATE_NEW );

	// remove it from operation
	BaseInterceptor cI[]=context.getContainer().getInterceptors();
	for( int i=0; i< cI.length; i++ ) {
	    cI[i].removeContext( this, context );
	}

	contextsV.removeElement(context);
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
     */
    public final void initContext( Context ctx ) throws TomcatException {
	if( state!= STATE_PRE_INIT ) {
	    BaseInterceptor cI[]=ctx.getContainer().getInterceptors();
	    for( int i=0; i< cI.length; i++ ) {
		cI[i].contextInit( ctx );
	    }
	}
	ctx.setState( Context.STATE_READY );
    }

    /** Stop the context. After the call the context will be disabled,
	( DISABLED state ) and it'll not be able to serve requests.
	The context will still be available and can be enabled later
	by calling initContext(). Requests mapped to this context
	should report a "temporary unavailable" message.
	

	All servlets will be destroyed, and resources held by the
	context will be freed.
     */
    public final void shutdownContext( Context ctx ) throws TomcatException {
	ctx.setState( Context.STATE_DISABLED ); // called before
	// the hook, no request should be allowed in unstable state

	BaseInterceptor cI[]=ctx.getContainer().getInterceptors();
	for( int i=0; i< cI.length; i++ ) {
	    cI[i].contextShutdown( ctx );
	}
    }

    // -------------------- Request processing / subRequest ------------------
    // -------------------- Main request processing methods ------------------

    /** Prepare the req/resp pair for use in tomcat.
     *  Call it after you create the request/response objects.
     *  ( for example in a connector, or when an internal sub-request is
     *  created )
     */
    public final void initRequest( Request req, Response resp ) {
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
    public final void service( Request req, Response res ) {
	internalService( req, res );
	// clean up
	try {
	    res.finish();
	} catch( Throwable ex ) {
	    handleError( req, res, ex );
	}
	finally {
	    BaseInterceptor reqI[]= req.getContainer().
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
    private final void internalService( Request req, Response res ) {
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

	    String roles[]=req.getRequiredRoles();
	    if(roles != null ) {
		status=0;
		BaseInterceptor reqI[]= req.getContainer().
		    getInterceptors(Container.H_authorize);

		// Call all authorization callbacks. 
		for( int i=0; i< reqI.length; i++ ) {
		    status = reqI[i].authorize( req, res, roles );
		    if ( status != 0 ) {
			break;
		    }
		}
	    }
	    if( status > 200 ) {
		if( debug > 0)
		    log("Authorize error " + req + " " + status);
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
    public final int processRequest( Request req ) {
	if(debug>9) log("Before processRequest(): "+req.toString());

	int status=0;
        BaseInterceptor ri[];
	ri=defaultContainer.getInterceptors(Container.H_contextMap);
	
	for( int i=0; i< ri.length; i++ ) {
	    status=ri[i].contextMap( req );
	    if( status!=0 ) return status;
	}
	req.setState(Request.STATE_CONTEXT_MAPPED );
	
	ri=defaultContainer.getInterceptors(Container.H_requestMap);
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
    public final Request createRequest( Context ctx, String urlPath ) {
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
    private final Request createSubRequest( String host, String urlPath ) {
	String queryString=null;
	int i = urlPath.indexOf("?");
	int len=urlPath.length();
	if (i>-1) {
	    if(i<len)
		queryString =urlPath.substring(i + 1, urlPath.length());
	    urlPath = urlPath.substring(0, i);
	}

	Request lr = new Request();
	lr.setContextManager( this );
	lr.requestURI().setString( urlPath );
	lr.queryString().setString(queryString );

	if( host != null) lr.setServerName( host );

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
    public final  Context getContext(Context base, String path) {
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
    
    /** Called for error-codes. Will call the error hook.
     */
    public final void handleStatus( Request req, Response res, int code ) {
	if( code!=0 )
	    res.setStatus( code );
	
	BaseInterceptor ri[];
	int status;
	ri=req.getContainer().getInterceptors( Container.H_handleError );
	
	for( int i=0; i< ri.length; i++ ) {
	    status=ri[i].handleError( req, res, null );
	    if( status!=0 ) return;
	}
    }

    /**
     *  Call error hook
     */
    void handleError( Request req, Response res , Throwable t  ) {
	BaseInterceptor ri[];
	int status;
	ri=req.getContainer().getInterceptors( Container.H_handleError );
	
	for( int i=0; i< ri.length; i++ ) {
	    status=ri[i].handleError( req, res, t );
	    if( status!=0 ) return;
	}
    }

    // -------------------- Support for notes --------------------

    /** Note id counters. Synchronized access is not necesarily needed
     *  ( the initialization is in one thread ), but anyway we do it
     */
    public static final int NOTE_COUNT=5;
    private  int noteId[]=new int[NOTE_COUNT];

    /** Maximum number of notes supported
     */
    public static final int MAX_NOTES=32;
    public static final int RESERVED=3;

    public static final int SERVER_NOTE=0;
    public static final int CONTAINER_NOTE=1;
    public static final int REQUEST_NOTE=2;
    public static final int HANDLER_NOTE=3;
    
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
    public final synchronized int getNoteId( int noteType, String name )
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

    public final String getNoteName( int noteType, int noteId ) {
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

    // -------------------- Logging and debug --------------------
    private Log loghelper = new Log("tc_log", "ContextManager");

    /**
     * Get the Logger object that the context manager is writing to (necessary?)
     **/
    public final Logger getLogger() {
	return loghelper.getLogger();
    }

    /**
     * So other classes can piggyback on the context manager's log
     * stream, using Logger.Helper.setProxy()
     **/
    public final Log getLog() {
	return loghelper;
    }
 
    /**
     * Force this object to use the given Logger.
     **/
    public final void setLogger( Logger logger ) {
	log("!!!! setLogger: " + logger, Logger.DEBUG);
	loghelper.setLogger(logger);
    }

    public final void addLogger(Logger l) {
	if (debug>20)
	    log("addLogger: " + l, new Throwable("trace"), Logger.DEBUG);
        if( loggers==null ) loggers=new Hashtable();
        loggers.put(l.toString(),l);
    }

    public final Hashtable getLoggers(){
        return loggers;
    }

    public final void log(String msg) {
	loghelper.log(msg);
    }

    public final void log(String msg, Throwable t) {
        loghelper.log(msg, t);
    }

    public final void log(String msg, int level) {
        loghelper.log(msg, level);
    }

    public final void log(String msg, Throwable t, int level) {
        loghelper.log(msg, t, level);
    }

    // -------------------- DEPRECATED --------------------
    /** System property used to set the random number generator
     */
    public static final String RANDOM_CLASS_PROPERTY=
	"tomcat.sessionid.randomclass";

    // XXX RandomClass will be set on the interceptor that sets it
    //     public final String getRandomClass() {
    // XXX XXX @deprecated - use  interceptor properties
    public final void setRandomClass(String randomClass) {
        System.setProperty(RANDOM_CLASS_PROPERTY, randomClass);
    }

    
}