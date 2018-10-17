"org.apache.tomcat.modules.config.ServerXmlReader",

package org.apache.tomcat.startup;

import java.net.*;
import java.io.*;

import org.apache.tomcat.core.*;
import org.apache.tomcat.util.log.*;
import org.apache.tomcat.modules.server.*;
import java.security.*;
import java.util.*;

/**
 *
 *  Wrapper around ContextManager. Use this class to embed tomcat in your
 *  application if you want to use "API"-based configuration ( instead
 *  or in addition to server.xml ).
 *
 *  The order is important:
 * 
 *  1. set properties like workDir and debug
 *  2. add all interceptors including your application-specific
 *  3. add the endpoints 
 *  4. add at least the root context ( you can add more if you want )
 *  5. call start(). The web service will be operational.
 *  6. You can add/remove contexts
 *  7. stop().
 *  
 *  You can add more contexts after start, but interceptors and  
 *  endpoints must be set before the first context and root must be
 *  set before start().
 *
 *  All file paths _must_ be absolute. ( right now if the path is relative it
 *  will be made absolute using tomcat.home as base. This behavior is very
 *  "expensive" as code complexity and will be deprecated ).
 * 
 * @author costin@eng.sun.com
 */
public class EmbededTomcat { 
    // the "real" server
    protected ContextManager contextM = new ContextManager();

    // your application
    protected Object application;

    // null == not set up
    protected Vector requestInt=null;
    protected Vector connectors=new Vector();

    // configurable properties
    protected int debug=0;
    
    public EmbededTomcat() {
    }

    // -------------------- Properties - set before start

    public ContextManager getContextManager() {
	return contextM;
    }
    
    /** Set debugging - must be called before anything else
     */
    public void setDebug( int debug ) {
	this.debug=debug;
	contextM.setDebug( debug );
    }


    // -------------------- Application Modules --------------------

    /** This is an adapter object that provides callbacks into the
     *  application.
     */
    public void addApplicationAdapter( BaseInterceptor adapter )
	throws TomcatException
    {
	if(requestInt==null)  initDefaultInterceptors();
	addInterceptor(adapter);
    }

    /** Keep a reference to the application in which we are embeded
     */
    public void setApplication( Object app ) {
	application=app;
    }

    /** Keep a reference to the application in which we are embeded
     */
    public Object getApplication() {
	return application;
    }

    // -------------------- Helpers for http connectors --------------------
    
    /** Add a HTTP listener.
     */
    public void addEndpoint( int port, InetAddress addr , String hostname)
	throws TomcatException
    {
	if(debug>0) log( "addConnector " + port + " " + addr +
			 " " + hostname );

	Http10Interceptor sc=new Http10Interceptor();
	sc.setPort( port ) ;
	if( addr != null ) sc.setAddress( addr );
	if( hostname != null ) sc.setHostName( hostname );
	
	contextM.addInterceptor(  sc );
    }

    /** Add AJP12 listener.
     */
    public void addAjpEndpoint( int port, InetAddress addr , String hostname)
	throws TomcatException
    {
	if(debug>0) log( "addAjp12Connector " + port + " " + addr +
			 " " + hostname );

	Ajp12Interceptor sc=new Ajp12Interceptor();
	sc.setPort( port ) ;
	if( addr != null ) sc.setAddress( addr );
	if( hostname != null ) sc.setHostName( hostname );
	
	contextM.addInterceptor(  sc );
    }

    /** Add a secure HTTP listener.
     */
    public void addSecureEndpoint( int port, InetAddress addr, String hostname,
				    String keyFile, String keyPass )
	throws TomcatException
    {
	if(debug>0) log( "addSecureConnector " + port + " " + addr + " " +
			 hostname );
	
	Http10Interceptor sc=new Http10Interceptor();
	sc.setPort( port ) ;
	if( addr != null ) sc.setAddress(  addr );
	if( hostname != null ) sc.setHostName( hostname );
	
	sc.setSocketFactory("org.apache.tomcat.util.net.SSLSocketFactory");
	sc.setSecure(true);

	contextM.addInterceptor(  sc );
    }

    // -------------------- Context add/remove --------------------

    boolean initialized=false;
    
    /** Add and init a context. Must be called after all modules are added.
     */
    public Context addContext(  String ctxPath, URL docRoot, String hosts[] )
	throws TomcatException
    {
	if(debug>0) log( "add context \"" + hosts[0] + ":" + ctxPath + "\" " +
			 docRoot );
	if( ! initialized ) {
	    initContextManager();
	}
	
	// tomcat supports only file-based contexts
	if( ! "file".equals( docRoot.getProtocol()) ) {
	    log( "addContext() invalid docRoot: " + docRoot );
	    throw new RuntimeException("Invalid docRoot " + docRoot );
	}

	try {
	    Context ctx=new Context();
	    ctx.setDebug( debug );
	    ctx.setContextManager( contextM );
	    ctx.setPath( ctxPath );
	    ctx.setDocBase( docRoot.getFile());
	    if( hosts!=null && hosts.length>0 ) {
		ctx.setHost( hosts[0] );
		for( int i=1; i>hosts.length; i++) {
		    ctx.addHostAlias( hosts[i]);
		}
	    }

	    contextM.addContext( ctx );
	    return ctx;
	} catch( Exception ex ) {
	    log("exception adding context " + ctxPath + "/" + docRoot, ex);
	}
	return null;
    }

    /** Find the context mounted at /cpath for a virtual host.
     */
    public Context getContext( String host, String cpath )
    {
	// We don't support virtual hosts in embeded tomcat
	// ( it's not difficult, but can be done later )
	Enumeration ctxE=contextM.getContexts();
	while( ctxE.hasMoreElements() ) {
	    Context ctx=(Context)ctxE.nextElement();
	    // XXX check host too !
	    if( ctx.getPath().equals( cpath )) {
		// find if the host matches
		if( ctx.getHost()==null ) 
		    return ctx;
		if( host==null )
		    return ctx;
		if( ctx.getHost().equals( host ))
		    return ctx;
		Enumeration aliases=ctx.getHostAliases();
		while( aliases.hasMoreElements()){
		    if( host.equals( (String)aliases.nextElement()))
			return ctx;
		}
	    }
	}
	return null;
    }

    public void start() throws TomcatException {
	contextM.start();
    }

    /** Stop contextM - will not exit the VM.
     */
    public void stop() throws TomcatException {
	contextM.stop();
    }

    // -------------------- Private methods
    public void addInterceptor( BaseInterceptor ri ) {
	if( requestInt == null ) requestInt=new Vector();
	requestInt.addElement( ri );
	ri.setDebug( debug );
    }

    protected void initContextManager()
	throws TomcatException 
    {
	if(requestInt==null)  initDefaultInterceptors();
	
	for( int i=0; i< requestInt.size() ; i++ ) {
	    contextM.addInterceptor( (BaseInterceptor)
				     requestInt.elementAt( i ) );
	}

	try {
	    contextM.init();
	} catch( Exception ex ) {
	    log("exception initializing ContextManager", ex);
	}
	if(debug>0) log( "ContextManager initialized" );
	initialized=true;
    }

    // no AutoSetup !

    protected String moduleSet1[] = {
	"org.apache.tomcat.modules.config.PathSetter", 
	"org.apache.tomcat.facade.WebXmlReader",
	"org.apache.tomcat.modules.config.PolicyInterceptor",
	"org.apache.tomcat.modules.config.LoaderInterceptor12",
	"org.apache.tomcat.modules.generators.ErrorHandler",
	"org.apache.tomcat.modules.config.WorkDirSetup",
	"org.apache.tomcat.modules.session.SessionId",
	"org.apache.tomcat.modules.mappers.SimpleMapper1",
	"org.apache.tomcat.modules.generators.InvokerInterceptor",
	"org.apache.tomcat.facade.JspInterceptor",
	"org.apache.tomcat.modules.generators.StaticInterceptor",
	"org.apache.tomcat.modules.session.SimpleSessionStore",
	"org.apache.tomcat.facade.LoadOnStartupInterceptor",
	"org.apache.tomcat.facade.Servlet22Interceptor",
	"org.apache.tomcat.modules.aaa.AccessInterceptor",
	"org.apache.tomcat.modules.aaa.CredentialsInterceptor",
	"org.apache.tomcat.modules.mappers.Jdk12Interceptor"
    };
    
    protected String moduleSet2[] = {
	"org.apache.tomcat.modules.config.PathSetter",
	"org.apache.tomcat.modules.config.ServerXmlInterceptor",
    };
    
    protected void initDefaultInterceptors() {
	addModules( moduleSet1 );
    }

    protected void addModules(String set[] ) {
	for( int i=0; i<set.length; i++ ) {
	    addInterceptor( createModule( set[i] ));
	}
    }

    // -------------------- Utils --------------------
    public void log( String s ) {
	contextM.log( s );
    }
    public void log( String s, Throwable t ) {
	contextM.log( s, t );
    }

    private BaseInterceptor createModule( String classN ) {
	try {
	    Class c=Class.forName( classN );
	    return (BaseInterceptor)c.newInstance();
	} catch( Exception ex ) {
	    ex.printStackTrace();
	    return null;
	}
    }

    
}
