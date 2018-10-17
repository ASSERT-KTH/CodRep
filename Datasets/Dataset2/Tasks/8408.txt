//cmLog=logger;

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
import org.apache.tomcat.net.*;
import org.apache.tomcat.context.*;
import org.apache.tomcat.request.*;
import org.apache.tomcat.util.*;
import org.apache.tomcat.logging.*;
import javax.servlet.*;
import javax.servlet.http.*;
import java.io.*;
import java.net.*;
import java.util.*;


/**
 * A collection class representing the Contexts associated with a particular
 * Server.  The managed Contexts can be accessed by path.
 *
 * It also store global default properties - the server name and port ( returned by
 * getServerName(), etc) and workdir.
 *
 * @author James Duncan Davidson [duncan@eng.sun.com]
 * @author James Todd [gonzo@eng.sun.com]
 * @author Harish Prabandham
 */
public class ContextManager {
    /**
     * The string constants for this ContextManager.
     */
    private StringManager sm = StringManager.getManager("org.apache.tomcat.core");

    private Vector requestInterceptors = new Vector();
    private Vector contextInterceptors = new Vector();
    
    // cache - faster access
    ContextInterceptor cInterceptors[];
    RequestInterceptor rInterceptors[];
    
    /**
     * The set of Contexts associated with this ContextManager,
     * keyed by context paths.
     */
    private Hashtable contexts = new Hashtable();

    public static final String DEFAULT_HOSTNAME="localhost";
    public static final int DEFAULT_PORT=8080;
    public static final String DEFAULT_WORK_DIR="work";
    
    /**
     * The virtual host name for the Server this ContextManager
     * is associated with.
     */
    String hostname;

    /**
     * The port number being listed to by the Server this ContextManager
     * is associated with.
     */
    int port;

    int debug=0;
    String workDir;

    // Instalation directory  
    String home;
    
    Vector connectors=new Vector();

    
    /**
     * Construct a new ContextManager instance with default values.
     */
    public ContextManager() {
    }

    // -------------------- Context repository --------------------

    /** Set default settings ( interceptors, connectors, loader, manager )
     *  It is called from init if no connector is set up  - note that we
     *  try to avoid any "magic" - you either set up everything ( using
     *  server.xml or alternatives) or you don't set up and then defaults
     *  will be used.
     * 
     *  Set interceptors or call setDefaults before adding contexts.
     */
    public void setDefaults() {
	if(connectors.size()==0) {
	    if(debug>5) log("Setting default adapter");
	    org.apache.tomcat.service.SimpleTcpConnector sc=new org.apache.tomcat.service.SimpleTcpConnector();
	    sc.setTcpConnectionHandler( new org.apache.tomcat.service.http.HttpConnectionHandler());
	    addServerConnector(  sc );
	}
	
	if( contextInterceptors.size()==0) {
	    if(debug>5) log("Setting default context interceptors");
	    addContextInterceptor(new LogEvents());
	    addContextInterceptor(new AutoSetup());
	    addContextInterceptor(new DefaultCMSetter());
	    addContextInterceptor(new WorkDirInterceptor());
	    addContextInterceptor( new WebXmlReader());
	    addContextInterceptor(new LoadOnStartupInterceptor());
	}
	
	if( requestInterceptors.size()==0) {
	    if(debug>5) log("Setting default request interceptors");
	    SimpleMapper smap=new SimpleMapper();
	    smap.setContextManager( this );
	    addRequestInterceptor(smap);
	    addRequestInterceptor(new SessionInterceptor());
	}
    }
     
    
    /**
     * Get the names of all the contexts in this server.
     */
    public Enumeration getContextNames() {
        return contexts.keys();
    }

    /** Init() is called after the context manager is set up
     *  and configured. 
     */
    public void init()  throws TomcatException {
	String cp=System.getProperty( "java.class.path");
	log( "<l:tomcat home=\"" + home + "\" classPath=\"" + cp + "\" />");
	//	long time=System.currentTimeMillis();
	ContextInterceptor cI[]=getContextInterceptors();
	for( int i=0; i< cI.length; i++ ) {
	    cI[i].engineInit( this );
	}
	
    	// init contexts
	Enumeration enum = getContextNames();
	Context context=null;
	while (enum.hasMoreElements()) {
	    context = getContext((String)enum.nextElement());
	    try {
		initContext( context );
	    } catch (TomcatException ex ) {
		if( context!=null ) {
		    log( "ERROR initializing " + context.toString() );
		    removeContext( context.getPath() );	    
		    Throwable ex1=ex.getRootCause();
		    if( ex1!=null ) ex.printStackTrace();
		}
	    }
	}
	//	log("Time to initialize: "+ (System.currentTimeMillis()-time), Logger.INFORMATION);
    }

    
    /**
     * Initializes this context to take on requests. This action
     * will cause the context to load it's configuration information
     * from the webapp directory in the docbase.
     *
     * <p>This method may only be called once and must be called
     * before any requests are handled by this context and after setContextManager()
     * is called.
     */
    public void initContext( Context ctx ) throws TomcatException {
	ContextInterceptor cI[]=getContextInterceptors();
	for( int i=0; i< cI.length; i++ ) {
	    cI[i].contextInit( ctx );
	}
    }
    
    public void shutdownContext( Context ctx ) throws TomcatException {
	// shut down and servlet
	Enumeration enum = ctx.getServletNames();

	while (enum.hasMoreElements()) {
	    String key = (String)enum.nextElement();
	    ServletWrapper wrapper = ctx.getServletByName( key );
	    ctx.removeServletByName( key );
	    wrapper.destroy();
	}
	
	ContextInterceptor cI[]=getContextInterceptors();
	for( int i=0; i< cI.length; i++ ) {
	    cI[i].contextShutdown( ctx );
	}
    }
    
    /** Will start the connectors and begin serving requests
     */
    public void start() throws Exception {//TomcatException {
	Enumeration connE=getConnectors();
	while( connE.hasMoreElements() ) {
	    ((ServerConnector)connE.nextElement()).start();
	}
    }

    public void stop() throws Exception {//TomcatException {
	if(debug>0) log("Stopping context manager ");
	Enumeration connE=getConnectors();
	while( connE.hasMoreElements() ) {
	    ((ServerConnector)connE.nextElement()).stop();
	}

	ContextInterceptor cI[]=getContextInterceptors();
	Enumeration enum = getContextNames();
	while (enum.hasMoreElements()) {
	    removeContext((String)enum.nextElement());
	}
    }

    /**
     * Gets a context by it's name, or <code>null</code> if there is
     * no such context.
     *
     * @param name Name of the requested context
     */
    public Context getContext(String name) {
	return (Context)contexts.get(name);
    }
    
    /**
     * Adds a new Context to the set managed by this ContextManager.
     *
     * @param ctx context to be added.
     */
    public void addContext( Context ctx ) throws TomcatException {
	// Make sure context knows about its manager.
	ctx.setContextManager( this );

	// it will replace existing context - it's better than  IllegalStateException.
	String path=ctx.getPath();
	if( getContext( path ) != null ) {
	    if(debug>0) log("Warning: replacing context for " + path);
	    removeContext(path);
	}

	ContextInterceptor cI[]=getContextInterceptors();
	for( int i=0; i< cI.length; i++ ) {
	    cI[i].addContext( this, ctx );
	}
	
	ctx.log("<l:addContext path=\"" +  ctx.getPath() + "\"  docBase=\"" + ctx.getDocBase() + "\" />");

	contexts.put( path, ctx );
    }
    
    /**
     * Shut down and removes a context from service.
     *
     * @param name Name of the Context to be removed
     */
    public void removeContext(String name) throws TomcatException {
	Context context = (Context)contexts.get(name);
	log( "<l:removeContext path=\"" + context.getPath() + "\" />");

	ContextInterceptor cI[]=getContextInterceptors();
	for( int i=0; i< cI.length; i++ ) {
	    cI[i].removeContext( this, context );
	}

	if(context != null) {
	    shutdownContext( context );
	    contexts.remove(name);
	}
    }

    public void addContainer( Container container )
    	throws TomcatException
    {
	ContextInterceptor cI[]=getContextInterceptors();
	for( int i=0; i< cI.length; i++ ) {
	    cI[i].addContainer( container);
	}
    }

    public void removeContainer( Container container )
	throws TomcatException
    {
	ContextInterceptor cI[]=getContextInterceptors();
	for( int i=0; i< cI.length; i++ ) {
	    cI[i].removeContainer( container);
	}
    }

    // -------------------- Connectors and Interceptors --------------------

    /**
     * Add the specified server connector to the those attached to this server.
     *
     * @param con The new server connector
     */
    public synchronized void addServerConnector( ServerConnector con ) {
	if(debug>0) log("<l:addConnector javaClass=\"" + con.getClass().getName() + "\" />");
	con.setContextManager( this );
	connectors.addElement( con );
    }

    public Enumeration getConnectors() {
	return connectors.elements();
    }
    
    public void addRequestInterceptor( RequestInterceptor ri ) {
	if(debug>0) log("<l:requestInterceptor javaClass=\"" + ri.getClass().getName() + "\" />");
	requestInterceptors.addElement( ri );
	if( ri instanceof ContextInterceptor )
	    contextInterceptors.addElement( ri );
	// XXX XXX use getMethods() to find what notifications are needed by interceptor
	// ( instead of calling all interceptors )
	// No API change - can be done later.
    }

    /** Return the context interceptors as an array.
	For performance reasons we use an array instead of
	returning the vector - the interceptors will not change at
	runtime and array access is faster and easier than vector
	access
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

    public void addContextInterceptor( ContextInterceptor ci) {
	contextInterceptors.addElement( ci );
    }


    /** Return the context interceptors as an array.
	For performance reasons we use an array instead of
	returning the vector - the interceptors will not change at
	runtime and array access is faster and easier than vector
	access
    */
    public ContextInterceptor[] getContextInterceptors() {
	if( contextInterceptors.size() == 0 ) {
	    setDefaults();
	}
	if( cInterceptors == null || cInterceptors.length != contextInterceptors.size()) {
	    cInterceptors=new ContextInterceptor[contextInterceptors.size()];
	    for( int i=0; i<cInterceptors.length; i++ ) {
		cInterceptors[i]=(ContextInterceptor)contextInterceptors.elementAt(i);
	    }
	}
	return cInterceptors;
    }

    public void addLogger(Logger logger) {
	// Will use this later once I feel more sure what I want to do here.
	// -akv
	firstLog=false;
	cmLog=logger;
    }


    // -------------------- Defaults for all contexts --------------------
    /** The root directory of tomcat
     */
    public String getHome() {
	if( home == null ) setHome(".");
	return home;
    }
    
    /** 
     * Set installation directory.  If path specified is relative, evaluate
     * it relative to the tomcat.home property if available, otherwise, 
     * evaluate it relative to the current working directory.
     */
    public void setHome(String home) {
        File homeFile = new File(home);
        if (!homeFile.isAbsolute()) {
            String tomcat_home = System.getProperty("tomcat.home");
            if (tomcat_home != null) homeFile = new File(tomcat_home, home); 
        }
        
        try {
            this.home = homeFile.getCanonicalPath();
        } catch (IOException ioe) {
            this.home = home; // oh well, we tried...
        }
    }
    
    /**
     * Sets the port number on which this server listens.
     *
     * @param port The new port number
     * @deprecated 
     */
    public void setPort(int port) {
	this.port=port;
    }

    /**
     * Gets the port number on which this server listens.
     * @deprecated 
     */
    public int getPort() {
	if(port==0) port=DEFAULT_PORT;
	return port;
    }

    /**
     * Sets the virtual host name of this server.
     *
     * @param host The new virtual host name
     * @deprecated 
     */
    public void setHostName( String host) {
	this.hostname=host;
    }

    /**
     * Gets the virtual host name of this server.
     * @deprecated 
     */
    public String getHostName() {
	if(hostname==null)
	    hostname=DEFAULT_HOSTNAME;
	return hostname;
    }

    /**
     * WorkDir property - where all temporary files will be created
     */ 
    public void setWorkDir( String wd ) {
	if(debug>0) log("set work dir " + wd);
	this.workDir=wd;
    }

    public String getWorkDir() {
	if( workDir==null)
	    workDir=DEFAULT_WORK_DIR;
	return workDir;
    }
    
    // -------------------- Request processing / subRequest --------------------
    
    /** Common for all connectors, needs to be shared in order to avoid
	code duplication
    */
    public void service( Request rrequest, Response rresponse ) {
	//	log( "New  request " + rrequest );
	try {
	    //	    System.out.print("A");
	    rrequest.setContextManager( this );
	    rrequest.setResponse(rresponse);
	    rresponse.setRequest(rrequest);

	    // wront request - parsing error
	    int status=rresponse.getStatus();

	    if( status < 400 )
		status= processRequest( rrequest );
	    
	    if(status==0)
		status=authenticate( rrequest, rresponse );
	    if(status == 0)
		status=authorize( rrequest, rresponse );
	    if( status == 0 ) {
		rrequest.getWrapper().handleRequest(rrequest,
						    rresponse);
	    } else {
		// something went wrong
		handleError( rrequest, rresponse, null, status );
	    }
	} catch (Throwable t) {
	    handleError( rrequest, rresponse, t, 0 );
	}
	//	System.out.print("B");
	try {
	    rresponse.finish();
	    rrequest.recycle();
	    rresponse.recycle();
	} catch( Throwable ex ) {
	    if(debug>0) log( "Error closing request " + ex);
	}
	//	log( "Done with request " + rrequest );
	//	System.out.print("C");
	return;
    }

    /** Will find the ServletWrapper for a servlet, assuming we already have
     *  the Context. This is used by Dispatcher and getResource - where the Context
     *  is already known.
     */
    int processRequest( Request req ) {
	req.setContextManager( this );
	//	if(debug>0) log("ProcessRequest: "+req.toString());

	for( int i=0; i< requestInterceptors.size(); i++ ) {
	    ((RequestInterceptor)requestInterceptors.elementAt(i)).contextMap( req );
	}

	for( int i=0; i< requestInterceptors.size(); i++ ) {
	    ((RequestInterceptor)requestInterceptors.elementAt(i)).requestMap( req );
	}

	// if(debug>0) log("After processing: "+req.toString());

	return 0;
    }

    int authenticate( Request req, Response res ) {
	for( int i=0; i< requestInterceptors.size(); i++ ) {
	    ((RequestInterceptor)requestInterceptors.elementAt(i)).authenticate( req, res );
	}
	return 0;
    }

    int authorize( Request req, Response res ) {
	for( int i=0; i< requestInterceptors.size(); i++ ) {
	    int err = ((RequestInterceptor)requestInterceptors.elementAt(i)).authorize( req, res );
	    if ( err != 0 ) return err;
	}
	return 0;
    }


    int doBeforeBody( Request req, Response res ) {
	for( int i=0; i< requestInterceptors.size(); i++ ) {
	    ((RequestInterceptor)requestInterceptors.elementAt(i)).beforeBody( req, res );
	}
	return 0;
    }

    void handleError( Request req, Response res , Throwable t, int code ) {
	Context ctx = req.getContext();
	if(ctx==null) {
	    ctx=getContext("");
	}
	if(ctx.getDebug() > 4 ) ctx.log("In error handler " + code + " " + t +  " / " + req );
	//	/*DEBUG*/ try {throw new Exception(); } catch(Exception ex) {ex.printStackTrace();}
	String path=null;
	ServletWrapper errorServlet=null;

	// normal redirects or non-errors
	if( code!=0 && code < 400 ) {
	    errorServlet=ctx.getServletByName("tomcat.errorPage");
	} else if( req.getAttribute("javax.servlet.error.status_code") != null ||
	    req.getAttribute("javax.servlet.error.exception_type")!=null) {
	    //  /*DEBUG*/ try {throw new Exception(); } catch(Exception ex) {ex.printStackTrace();}
	    if( ctx.getDebug() > 0 ) ctx.log( "Error: exception inside exception servlet " +
					      req.getAttribute("javax.servlet.error.status_code") + " " +
					      req.getAttribute("javax.servlet.error.exception_type"));
	    errorServlet=ctx.getServletByName("tomcat.errorPage");
	}

	if( t==null) {
	    if( code==0 )
		code=res.getStatus();
	    // we can't support error pages for non-errors, it's to
	    // complex and insane
	    if( code >= 400 )
		path = ctx.getErrorPage( code );
	    
	    if( code==HttpServletResponse.SC_UNAUTHORIZED ) {
		// set extra info for login page
		if( errorServlet==null)
		    errorServlet=ctx.getServletByName("tomcat.authServlet");
		if( ctx.getDebug() > 0 ) ctx.log( "Setting auth servlet " + errorServlet );
	    }
            req.setAttribute("javax.servlet.error.status_code",new Integer( code));
	} else {
	    // Scan the exception's inheritance tree looking for a rule
	    // that this type of exception should be forwarded
	    Class clazz = t.getClass();
	    while (path == null && clazz != null) {
		String name = clazz.getName();
		path = ctx.getErrorPage(name);
		clazz = clazz.getSuperclass();
	    }
	    req.setAttribute("javax.servlet.error.exception_type", t.getClass());
            req.setAttribute("javax.servlet.error.message", t.getMessage());
	    req.setAttribute("tomcat.servlet.error.throwable", t);
	}

	// Save the original request, we want to report it
	// and we need to use it in the "authentication" case to implement
	// the strange requirements for login pages
	req.setAttribute("tomcat.servlet.error.request", req);


	// No error page or "Exception in exception handler", call internal servlet
	if( path==null && errorServlet==null) {
	    // this is the default handler -  avoid loops
	    req.setAttribute( "tomcat.servlet.error.defaultHandler", "true");
	    errorServlet=ctx.getServletByName("tomcat.errorPage");
	}

	// Try a normal "error page"
	if( errorServlet==null && path != null ) {
	    try {
		RequestDispatcher rd = ctx.getRequestDispatcher(path);
		
		// try a forward
		res.reset();
		if (res.isStarted()) 
		    rd.include(req.getFacade(), res.getFacade());
		else
		    rd.forward(req.getFacade(), res.getFacade());
		return ;
	    } catch( Throwable t1 ) {
		ctx.log(" Error in custom error handler " + t1 );
		// nothing - we'll call DefaultErrorPage
	    }
	}
	
	// If No handler or an error happened in handler 
	// Default handler
	// loop control
	if( req.getAttribute("tomcat.servlet.error.handler") != null &&
	    code >= 400 ) {
	    // error page for 404 doesn't exist... ( or watchdog tests :-)
	    ctx.log( "Error/loop in default error handler " + req + " " + code + " " + t + " " +  path );
	} else {
	    if( ctx.getDebug() > 0 ) ctx.log( "Error: Calling servlet " + errorServlet );
	    req.setAttribute("tomcat.servlet.error.handler", errorServlet);
	    errorServlet.handleRequest(req.getFacade(),res.getFacade());
	    // will call this if any error happens
	}
	return;
    }
    
    // -------------------- Sub-Request mechanism --------------------

    /** Create a new sub-request in a given context, set the context "hint"
     *  This is a particular case of sub-request that can't get out of
     *  a context ( and we know the context before - so no need to compute it again)
     *
     *  Note that session and all stuff will still be computed.
     */
    Request createRequest( Context ctx, String urlPath ) {
	// assert urlPath!=null

	// deal with paths with parameters in it
	String queryString=null;
	int i = urlPath.indexOf("?");
	int len=urlPath.length();
	if (i>-1) {
	    if(i<len)
		queryString =urlPath.substring(i + 1, urlPath.length());
	    urlPath = urlPath.substring(0, i);
	}

	/** Creates an "internal" request
	 */
	RequestImpl lr = new RequestImpl();
	//	RequestAdapterImpl reqA=new RequestAdapterImpl();
	//lr.setRequestAdapter( reqA);
	lr.setLookupPath( urlPath );
	lr.setQueryString( queryString );
	//	lr.processQueryString();

	lr.setContext( ctx );
	
	// XXX set query string too 
	return lr;
    }

    public void setDebug( int level ) {
	
	if( level != 0 ) System.out.println( "Setting level to " + level);
	debug=level;
    }

    public final void log(String msg) {
	if( msg.startsWith( "<l:" ))
	    doLog( msg );
	else
	    doLog("<l:tc>" + msg + "</l:tc>");
    }

    boolean firstLog = true;
    Logger cmLog = null;
    
    public final void doLog(String msg) {
	if (firstLog == true) {
	    cmLog = Logger.getLogger("tc_log");
	    if( cmLog!= null ) {
		cmLog.setCustomOutput("true");
		cmLog.setVerbosityLevel(Logger.INFORMATION);
	    }
	    firstLog = false;
	}

	if (cmLog != null) {
	    cmLog.log(msg + "\n");
	    // XXX \n should be added to logger, portable
	} else {
	    System.out.println(msg);
	}
    }
    
}