commonCL=jdk11Compat.newClassLoaderInstance(new URL [] {}, null);

package org.apache.tomcat.startup;

import java.net.*;
import java.io.*;

import org.apache.tomcat.core.*;
import org.apache.tomcat.util.log.*;
import org.apache.tomcat.util.compat.*;
import org.apache.tomcat.util.IntrospectionUtils;
import java.security.*;
import java.util.*;
import java.lang.reflect.*;

/* EmbededTomcat is the bean you use to embed tomcat in your application.
   Main is a wrapper that will guess TOMCAT_HOME and dispatch to 
   tasks performing different actions, including EmbededTomcat.

*/

/* Required setup:
   -  EmbededTomcat is assumed to be loaded in the same class loader with
   lib/common, and without lib/container. It'll deal with setting a separate
   class loader for container and applications.

   - tomcat.install or tomcat.home property must be set ( from TOMCAT_HOME env.)

*/

/**
 *
 *  Use this class to embed tomcat in your application. If all you want is to
 *  start/stop tomcat, with minimal customization, you can use Main.main()
 *
 *  This class is designed as a java bean, where you set different properties,
 *  then call methods to perform actions. The main method is "execute", that
 *  will start tomcat. Few other methods allow to perform different other tasks.
 *
 *  EmbededTomcat is usable as an "ant" task as well, using the TaskAdapter.
 *  ( see sample - TODO XXX ).
 * 
 *  Adding tomcat to your application:
 * 
 *  - Create a java class that will act as adapter and start tomcat ( and
 *    hold your customization code ). The class and all the files in
 *    TOMCAT_HOME/lib/common must be available in the class loader.
 *    lib/container and lib/apps should  _not_ be visible, EmbededTomcat
 *    will handle that. All the application files you want visible from 
 *    tomcat must be included as well.
 *    ADVANCED1. Completely separated classloader
 *
 *  - In your adapter, create an instance of EmbededTomcat.
 * 
 *  - set properties you want to customize. 
 *  
 *  - add all interceptors including your application-specific. That includes
 *   the connector modules ( shortcuts are provided for common sets of
 *   modules and for common connector configuration ).
 *
 *  - add the root context ( required ) and any other contexts you want.
 *    More context can be added at runtime. You can also use existing
 *    configuration modules that automatically add/deploy Contexts. 
 *    
 *  -  call start(). Tomcat will initialize and start. The method returns
 *     when everything is ready.
 * 
 *  -  You can add/remove contexts at runtime.
 *
 *  -  call stop(). Tomcat will clean up all resources and shutdown ( clean 
 *     shutdown ). All common modules have been tested and shouldn't leave
 *     any garbage, however it is possible that user code will leave threads
 *     or other garbage ( i.e. not clean on destroy ). If tomcat is run in
 *     a sandbox, this shouldn't be a problem ( as untrusted servlets can't
 *     create threads ). It is your responsiblity to make sure all apps you trust
 *     or custom modules support clean shutdown.
 *
 *  - ADVANCED2. You can throw away the classloader, and use another one
 *    if you start again. That would take care of all garbage and classes
 *    except threads and associated objects ( there is no way to handle
 *    dangling threads except killing them, assuming you can distinguish
 *    them from your own threads ).
 *
 *  All file paths _should_ be absolute. If not, you should set "home" and
 *  make sure you include the "PathSetter" module before anything else.
 *
 * <b>Example1</b>
 * <pre>
    // Assume EmbededTomcat and all common jars are in CLASSPATH
    EmbededTomcat tomcat=new EmbededTomcat();
    tomcat.setInstallDir( installDir );

    // tomcat.setDebug( debug );
    // tomcat.setAutoDeploy( false ); // no webapps/ is used
    // tomcat.setEstart(true ); // server.xml will not be used 

    tomcat.initClassLoaders();

    if( explicitModules ) {
      // For each module you want to add ( you must include a minimal set )
      int mid=tomcat.addModule( "org.apache.tomcat.modules.xxxx" );
      tomcat.setModuleProperty( mid, "property", "value" );
    } else {
      // Nothing - server.xml will be used if setEstart(false) ( default )
      //           the default set will be used if setEstart(true)
    }

    // If you don't add one explicitely, the defaults are used ( HTTP/8080,
    //  Ajp12/8007 for shutdown )
    // tomcat.addEndpoint( port, null, null );
    // You can add other connectors using addModule()

    // tomcat.addApplicationAdapter( myModule );

    // If you also want "webapps/" ( if you don addContext this is automatic )
    // tomcat.addAutoDeploy(); 
    // tomcat.addContext( path, docBase, null);
    
    tomcat.execute();
    
   </pre>
 * 
 * @author Costin Manolache
 */
public class EmbededTomcat { 
    // the "real" server
    protected ContextManager contextM = new ContextManager();

    // your application
    protected Object application;

    // null == not set up
    protected Vector connectors=new Vector();

    String home=null;
    String installDir=null;
    
    Hashtable attributes=new Hashtable();
    
    // configurable properties
    protected int dL=0;

    boolean defaultConnectors=true;
    boolean autoDeploy=true;
    
    boolean serverXml=true;
    boolean help;

    // prevent tomcat from starting.
    boolean nostart=false;
    
    public EmbededTomcat() {
    }

    // -------------------- 

    /** Access to the ContextManager.
     */
    public ContextManager getContextManager() {
	return contextM;
    }
    
    // -------------------- Properties - set before start

    /**
     *  Debug for EmbededTomcat, enable debugging on tomcat
     *  and the LogEvents module.
     *  "-debug debug" on the command line
     */
    public void setDebug( int debug ) {
	this.dL=debug;
	contextM.setDebug( debug );
	debug( "Debugging enabled ");
    }


    boolean noClassLoaders=false;
    
    public void setNoClassloaders( boolean b ) {
        noClassLoaders=b;
    }
    
    /** Set the home dir for tomcat, where webapps/ will be located.
     *  "-home dir" on the command line.
     */
    public void setHome( String s ) {
	home=s;
    }

    /** Set install dir for tomcat, where libs will be located.
     *  "-install dir" on the command line.
     */
    public void setInstall(String install) {
	this.installDir=install;
 	contextM.setInstallDir( install );
	if( dL > 0 ) debug( "setInstall " + install);
    }

    /** Set location of the server.xml file, to be used by ServerXml reader.
     * 	Not used if EStart() is used.
     *  "-config foo" on the command line.
     */
    public void setConfig( String s ) {
	attributes.put("config", s);
    }

    /** Tomcat will run in a sandboxed environment, under SecurityManager.
     *  "-sandbox" on the command line
     */
    public void setSandbox(boolean b) {
	attributes.put("sandbox", "true");
    }

    /** Generate Jk configuration, without running tomcat. 
     *  Equivalent with "-jkconf" on the command line.
     */
    public void setJkconf(boolean b ) {
	attributes.put("jkconf", "true");
	nostart=true;
    }
    
    /** Dummy, "-start" on the command line.
     */
    public void setStart(boolean b) {
	// nothing, default mode
    }

    /** Use 'embeded' configuration to start tomcat. 
     *
     *  If Estart is false ( the default ), we'll load server.xml and all
     * the modules inside.
     *
     * If it is set to true, we'll load the a hard-coded set of modules.
     *
     * If you add explicitely your own set of module it will be used
     * instead of the defaults. Modules need to be added before 
     * adding the first connector or initContextManager is called.
     *
     * Equivalent with "-estart" on the command line.
     */
    public void setEstart(boolean b) {
	debug( "Using default embedded config ");
	serverXml=false;
    }

    /** Dummy, "-run" on the command line.
     */
    public void setRun(boolean b) {
	setStart(true);
    }

    /** Don't run, just display the help message.
	"-help" on the command line.
     */
    public void setHelp(boolean b) {
	help=b;
    }
    
    // -------------------- Generic properties --------------------

    public void setProperty( String name, String v ) {
	if( name.equals("home")  )
	    setHome((String) v );
	if( name.equals("install")  )
	    setInstall( (String) v);
	if( name.equals("sandbox"))
	    setSandbox(true);
	attributes.put( name, v );
    }

    public void setAttribute( String name, Object v ) {
	if( name.equals("parentClassLoader")  )
	    setParentClassLoader((ClassLoader)v);
	if( name.equals("commonClassLoader")  )
	    setCommonClassLoader((ClassLoader)v);
	if( name.equals("args")  )
	    setArgs((String [])v);
	if( name.equals("commonClassPath")  )
	    setCommonClassPath((URL [])v);
	if( v==null)
	    attributes.remove( name );
	else
	    attributes.put( name, v );
    }
    
    // Ant compatibility ( TODO )
    public void addProperty(Property prop) {
    }
    
    // -------------------- Application Modules --------------------

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

    // -------------------- Module configuration --------------------

    Vector modules=new Vector();

    /** Add a module explicitely. You can use server.xml, a pre-defined
     *	set of modules, or your own set.
     *
     * Must be called before adding the first endpoint or context and
     * before initContextManger.
     *
     * If you add a module you must also call addDefaultModules (before
     * or after your modules ) - or you can add all the required modules
     * manually.
     */
    public int addModule( BaseInterceptor ri )
	throws TomcatException
    {
	if( ri==null ) return -1;
	if( dL > 20 ) debug( "addModule " + ri.getClass().getName());
	if(ri.getClass().getName().indexOf("Xml") <0 )
	    ri.setDebug( dL );
	modules.addElement( ri );
	return modules.size()-1;
    }
    
    /** Add a custom module. It'll return the module id, that can be
     *  used to set properties
     *  @see addModule( BaseInterceptor ri )
     */
    public int addModule( String className )
	throws TomcatException
    {
	BaseInterceptor bi=createModule( className );
	if( bi==null )
	    throw new TomcatException("module not found " + className);
	return addModule( bi );
    }

    /** Find a module from the set added with  addModule() or addDefaultModules()
     */
    public int findModule( String className, int startPos )
    {
	for( int i=startPos; i<modules.size(); i++ ) {
	    Object o=modules.elementAt(i);
	    if( className.equals( o.getClass().getName() )) 
		return i;
	}
	return -1;
    }

    /** Configure a module property. Since modules can be added from
     *  child classloaders this is the best way to configure them.
     *  If the module is in the same class loader you can also set
     *  the property explicitely, but for more flexibility it's better
     *  to use this method.
     */
    public void setModuleProperty( int id, String name, String value )
	throws TomcatException
    {
	Object o=modules.elementAt( id );
	if( dL>0 ) debug( "setModuleProperty " + o.getClass().getName() +
			  " " + name + " " + value );
	IntrospectionUtils.setProperty( o, name, value );
    }

    // -------------------- Module helpers --------------------

    /** Init tomcat using server.xml-style configuration. Called
     *  automatically if no module was explicitely added and Estart is
     *  true ( default ). The automatic call happens before addContext,
     *  addEndpoint or execute()
     */
    public void addServerXmlModules() throws TomcatException {
	String conf=(String)attributes.get( "config" );

	addModule( "org.apache.tomcat.modules.config.PathSetter");
	int mid=addModule( "org.apache.tomcat.modules.config.ServerXmlReader");

	if( null!=conf ) {
	    if( dL>0) debug( "Using config file " + conf);
	    setModuleProperty( mid, "config",conf );
	}
    }

    /** Add all the default modules, needed for a fully functional container.
     *  You must setEtomcat( true ) if you don't want  server.xml to be used.
     */ 
    public void addDefaultModules()
	throws TomcatException
    {
	//this is a bug in 3.3.0, we shoud disable it automcatically 
	if( serverXml ) {
	    addServerXmlModules();
	    return;
	}
	if( dL > 0) {
	    int mid=addModule( LOG_EVENTS_MODULE );
	    setModuleProperty(mid, "enabled", "true");
	}
	    
	for( int i=0; i<moduleSet1.length; i++ ) {
	    addModule( moduleSet1[i] );
	}
    }

    /** Add modules needed for auto-deploy function. 
     *  By default you need to explicitely add ( using addContext() ) any
     * 	webapp. Use this with addDefaultModules().
     *
     *  Will be called automcatically if no context was added, you must
     *  call it if you want both autodeploy and manually-added contexts.
     */
    public void addAutoDeploy()
	throws TomcatException
    {
	if( serverXml ) return;
	for( int i=0; i<moduleSetAD.length; i++ ) {
	    addModule( moduleSetAD[i] );
	}
    }

    
    // -------------------- Context add/remove --------------------

    protected boolean initialized=false;
    
    /** Add and init a context. Must be called after all modules and endpoints
     *  are added.
     *
     *  This will initialize the context manager.
     */
    public Context addContext(  String ctxPath, URL docRoot, String hosts[] )
	throws TomcatException
    {
	if( "ROOT".equals( ctxPath ) ) {
	    ctxPath="";
	}
	if(dL>0)
	    debug( "add context \"" + hosts[0] + ":" + ctxPath + "\" "+
		   docRoot );
	// User added a context explicitely, disable the default.
	autoDeploy=false;
	
	if( ! initialized )  initContextManager();

	// tomcat supports only file-based contexts
	if( ! "file".equals( docRoot.getProtocol()) ) {
	    debug( "addContext() invalid docRoot: " + docRoot );
	    throw new RuntimeException("Invalid docRoot " + docRoot );
	}

	try {
	    Context ctx=contextM.createContext();
	    ctx.setDebug( dL );
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
	    ctx.init();
	    return ctx;
	} catch( Exception ex ) {
	    debug("exception adding context " + ctxPath + "/" + docRoot, ex);
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

    // -------------------- Startup/shutdown methods --------------------

    /** Initialize the context manager. Called automatically before the
     *  first addContext or on execute(). You can call it explicitely
     *  if you want to 'tweak' the cm before execute.
     */
    public void initContextManager()
	throws TomcatException 
    {
	if( initialized ) return;
	if( installDir==null ) {
	    installDir=IntrospectionUtils.guessInstall("tomcat.install",
						       "tomcat.home","tomcat.jar");
	    if( dL > 0 ) debug( "Guessed installDir " + installDir );
	}
	if( home==null ) {
	    home = System.getProperty("tomcat.home");
            if( home == null )
                home = installDir;
	    if( dL > 0 ) debug( "Using homeDir " + installDir );
        }

	contextM.setInstallDir( installDir );
        contextM.setHome( home );

	try {
	    setTomcatProperties();

	    initClassLoaders();

	    jdk11Compat.setContextClassLoader( containerCL );

	    // 
	    if(modules.size()==0) 
		addDefaultModules();

	    if( !serverXml ) {
		if( attributes.get("sandbox") != null )
		    addModule( POLICY_MODULE );
	    
		if( autoDeploy )
		    addAutoDeploy();
	    
		if( defaultConnectors )
		    addDefaultConnectors();
	    }
	    beforeAddInterceptors();
	    
	    for( int i=0; i< modules.size() ; i++ ) {
		contextM.addInterceptor( (BaseInterceptor)
					 modules.elementAt( i ) );
	    }
	    contextM.init();
	} catch( Throwable ex ) {
	    if( ex instanceof InvocationTargetException ) {
		ex=((InvocationTargetException)ex).getTargetException();
	    }
	    debug("exception initializing ContextManager", ex);
	    throw new TomcatException( "EmbededTomcat.initContextManager", ex );
	}
	if(dL>0) debug( "ContextManager initialized" );
	initialized=true;
    }

    /** Start the context manager. Will do nothing if -jkConfig or -help
     *  ( or the equivalent setters ) are used.
     */
    public void start() throws TomcatException {
	if( nostart ) {
	    debug("Tomcat will not start  - configuration only mode ");
	    contextM.shutdown();
	    return;
	}
	long time3=System.currentTimeMillis();
	contextM.start();
	long time4=System.currentTimeMillis();
	debug("Startup time " + ( time4-time3 ));
    }

    /** Shutdown contextM - <em>may</em> exit the VM.
     *  This method is <b>intrinsically dangerous</b>, so use at your own
     *  risk.  It is very possible that the entire VM will shut down after 
     *  calling this method. You should only call this method if you need
     *  to implement <em>advanced</em> functionality.
     */
    public void shutdown() throws TomcatException {
	contextM.shutdown();
    }

    /** Stop contextM - will not exit the VM.
     */
    public void stop() throws TomcatException {
	contextM.stop();
    }

    // -------------------- Helpers and shortcuts --------------------
    
    /** Add a HTTP listener. Must be called after all 'core' modules
     *  are called. If no endpoint is added explicitely the defaults will
     *  be added.
     */
    public int addEndpoint( int port, InetAddress addr , String hostname)
	throws TomcatException
    {
	if(modules.size()==0)  addDefaultModules();
	defaultConnectors=false;
	if(dL>0) debug( "addConnector " + port + " " + addr +
			 " " + hostname );

	int mid=addModule("org.apache.tomcat.modules.server.Http10Interceptor");

	setModuleProperty( mid, "port", Integer.toString(port) );
	if( addr != null )
	    setModuleProperty( mid, "address", addr.getHostAddress());
	if( hostname != null )
	    setModuleProperty( mid, "hostName",  hostname );
	return mid;
    }

    /** Add AJP12 listener.
     */
    public int addAjpEndpoint( int port, InetAddress addr , String hostname)
	throws TomcatException
    {
	if(modules.size()==0)  addDefaultModules();
	defaultConnectors=false;
	if(dL>0) debug( "addAjp12Connector " + port + " " + addr +
			 " " + hostname );

	int mid=addModule("org.apache.tomcat.modules.server.Ajp12Interceptor");

	setModuleProperty( mid, "port", Integer.toString( port )) ;
	if( addr != null )
	    setModuleProperty( mid, "address", addr.getHostAddress());
	if( hostname != null )
	    setModuleProperty( mid, "hostName",  hostname );
	return mid;
    }

    /** Add a secure HTTP listener.
     */
    public int addSecureEndpoint( int port, InetAddress addr, String hostname,
				    String keyFile, String keyPass )
	throws TomcatException
    {
	if(modules.size()==0)  addDefaultModules();
	int mid=addEndpoint( port, addr, hostname );
	
	setModuleProperty( mid, "socketFactory",
			   "org.apache.tomcat.util.net.SSLSocketFactory");
	setModuleProperty( mid, "secure", "true");

	return mid;
    }

    /** Add the default HTTP/8080, Ajp12-stop/8007, if no explicit addEndpoint
     *  was called
     */
    public void addDefaultConnectors()
	throws TomcatException
    {
	addEndpoint( 8080, null, null );
	addAjpEndpoint( 8007, null, null );
    }
    
    // -------------------- execute() --------------------

    /** Main and Ant action. It's expected to be overriden with completely
	different functionality - do not use super.execute(), but call
	directly the methods you need.
     */
    public void execute() throws Exception {
	final EmbededTomcat et=this;
	jdk11Compat.doPrivileged( new Action() {
		public Object run() throws Exception {
		    et.execute1();
		    return null;
		}
	    }, jdk11Compat.getAccessControlContext());
    }
    
    public void execute1() throws Exception {
	if( args!=null )
	    processArgs( args );
        if( help ) {
            printUsage();
            return;
        }
	// Init 
	if( ! initialized ) {
	    long time1=System.currentTimeMillis();
	    initContextManager();
	    long time2=System.currentTimeMillis();
	    debug("Init time "  + (time2-time1));
	}

	// Start
	start();
    }


    // -------------------- Main --------------------
    protected String args[]=null;

    public void setArgs( String args[] ) {
	this.args=args;
    }

    public boolean processArgs(String args[]) {
	try {
	    if( dL> 0 ) {
		debug( "Processing args " );
		for( int i=0; i<args.length; i++ ) debug(args[i]);
	    }
	    return IntrospectionUtils.processArgs( this, args );
	} catch( Exception ex ) {
	    ex.printStackTrace();
	    return false;
	}
    }
    
    public static void main(String args[] ) {
	EmbededTomcat tomcat=new EmbededTomcat();
	try {
	    tomcat.setArgs( args );
            tomcat.execute();
	} catch(Exception ex ) {
	    tomcat.debug("main", ex);
	    System.exit(1);
	}
    }

    // -------------------- Utils --------------------

    /** Cleanup from a previous run
     */
    public void cleanupPrevious() {
	// remove ajp12.id
    }

    private void setTomcatProperties() throws TomcatException {
	Enumeration attN=attributes.keys();
	while( attN.hasMoreElements() ) {
	    String k=(String)attN.nextElement();
	    Object o=attributes.get( k );
	    if( o instanceof String ) {
		IntrospectionUtils.setProperty( contextM, k, (String)o);
		if( dL> 0 ) debug("Set tomcat property " + k + " " + o );
	    } else
		contextM.setNote( k, o );
	}
    }

    // -------------------- Class loader configuration --------------------
    // Set those if you embed tomcat in your app. If not, defaults
    // will be used as described in the comments.
    ClassLoader parentCL;
    ClassLoader appsCL;
    ClassLoader commonCL;
    ClassLoader containerCL;
    ClassLoader modulesCL;
    URL[] commonCP;
    URL[] modulesCP;
    URL[] appsCP;
    URL[] containerCP;
	

    /** Parent class loader is the parent of "common" loader. It
	can be used as a parent for the webapps, if you want them to
	have the minimal visibility of tomcat. If you do so,
	make sure you include at least servlet.jar.
    */
    public void setParentClassLoader( ClassLoader cl ) {
	this.parentCL=cl;
    }

    /** Class loader containing lib/common ( or equivalent ). This will be the
     *  parent of both the server container and also parent of webapp loaders.
     *  Typically used to load EmbededTomcat ( defaults to
     *  this.getClassLoader()).
     *
     *   For backward compat, the caller can include  all elements of the 
     *   org.apache.tomcat.common.classpath property.
     */
    public void setCommonClassLoader( ClassLoader cl ) {
	this.commonCL=cl;
    }

    /** Classpath used for common class loader ( probably not needed of
	URLClassLoader is used ). Used for javac.
    */
    public void setCommonClassPath( URL cp[] ) {
	commonCP=cp;
    }

    /** Parent class loader for all web applications.
     *  Defaults to common + lib/apps + all elements of
     *  org.apache.tomcat.apps.classpath
     */
    public void setAppsClassLoader( ClassLoader cl ) {
	this.appsCL=cl;
    }

    /** Class loader used to load tomcat internal classes, not
     *	visible to webapps.
     *  Defaults to common + ${TOMCAT_HOME}/lib/container/ + 
     *  ${TOMCAT_HOME}/classes + ${JAVA_HOME}/lib/tools.jar
     */
    public void setContainerClassLoader( ClassLoader cl ) {
	this.containerCL=cl;
    }

    public ClassLoader getContainerClassLoader() {
	return containerCL;
    }
    // -------------------- Class loader methods --------------------

    static final Jdk11Compat jdk11Compat=Jdk11Compat.getJdkCompat();
    /** System property used to set the application class loader, which
	will be the parent of all webapps.
    */
    public static final String PROPERTY_APPS_LOADER =
	"org.apache.tomcat.apps.classpath";
    public static final String PROPERTY_CONTAINER_LOADER =
	"org.apache.tomcat.container.classpath";
	

    /** Initialize class loaders with the defaults, if not set
     */
    public void initClassLoaders()
	throws IOException, MalformedURLException
    {
	if( dL > 0 ) debug( "Init class loaders " + noClassLoaders );
        if( noClassLoaders ) {
            commonCL=this.getClass().getClassLoader();
            if( commonCL == null ) {
                commonCL=new java.net.URLClassLoader( new URL[] {}, null );
            }
            parentCL=commonCL;
            containerCL=commonCL;
            modulesCL=commonCL;
            if( dL> 0 ) debug( "All class loaders " + commonCL );
            contextM.setParentLoader(parentCL);
            contextM.setCommonLoader(modulesCL);
            contextM.setContainerLoader(containerCL);
            contextM.setAppsLoader(appsCL);
            return;
        }
	if( parentCL==null ) {
	    if( dL > 0 ) debug( "Default parent loader: null");
	}

	String prefix=installDir + File.separator + "lib" + File.separator;
	// At least this is assumed to be set.
	if( commonCL==null ) {
	    debug( "Default commonCL ");
	    commonCL=this.getClass().getClassLoader();
	}
	
	// Intermediary class loader - add modules/xxx/WEB-INF/common/*
	modulesCP=getModulesCommonCP();
	if( modulesCP == null ) {
	    modulesCL=commonCL;
	} else {
	    if( dL > 0 )
		IntrospectionUtils.displayClassPath( "Modules-common", modulesCP );
	    modulesCL=jdk11Compat.newClassLoaderInstance( modulesCP, commonCL );
	}

	if( containerCL == null ) {
	    if( dL > 0 )
		debug( "Dir : " + prefix+"container" + " " +
		       PROPERTY_CONTAINER_LOADER);
	    containerCP=
		IntrospectionUtils.getClassPath( prefix+"container",
						 null,
						 PROPERTY_CONTAINER_LOADER,
						 true );
	    containerCP=addModulesContainerCP( containerCP );
	    containerCL=
		jdk11Compat.newClassLoaderInstance(containerCP , modulesCL);
	    if( dL > 0 ) IntrospectionUtils.displayClassPath( "ContainerCP",
							      containerCP );
	}
	if( appsCL==null ) {
	    appsCP=
		IntrospectionUtils.getClassPath( prefix + "apps",
						 null,
						 PROPERTY_APPS_LOADER, false );
	    appsCL=jdk11Compat.newClassLoaderInstance(appsCP , modulesCL);
	}
	// Tomcat initialization 
	// Set the env. variable with the classpath
	String cp=System.getProperty("tc_path_add");
	cp=IntrospectionUtils.classPathAdd(commonCP,cp);
	if( modulesCP!= null )
	    cp=IntrospectionUtils.classPathAdd(modulesCP,cp);
	cp=IntrospectionUtils.classPathAdd(appsCP,cp);
	if( cp != null ) 
	    System.getProperties().put("tc_path_add",cp);
	
	contextM.setParentLoader(parentCL);
	contextM.setCommonLoader(modulesCL);
	contextM.setContainerLoader(containerCL);
	contextM.setAppsLoader(appsCL);
    }

    /** Allow modules to add libs in the common CP. This reduce the
     *	setup overhead when installing modules.
     */
    protected URL[] getModulesCommonCP() {
	return findModulesCP( "/WEB-INF/lib/common");
    }

    protected URL[] findModulesCP(String dir) {
	String prefix= installDir + File.separator + "modules" + File.separator;
	File f=new File( prefix );
	if( ! f.exists() ) return null;
	Vector jarsV = new Vector();
	String[] list = f.list();
	for (int i = 0; i < list.length; i++) {
	    File commonF=new File( f, list[i] + dir );
	    if( commonF.exists() ) {
		// Add all the jars
		IntrospectionUtils.addToClassPath(jarsV, commonF.getAbsolutePath());
		File classes=new File( commonF, "classes" );
		if( classes.exists() ) {
		    URL url=IntrospectionUtils.getURL( commonF.getAbsolutePath(),"classes" );
		    if( url!=null )
			jarsV.addElement( url );
		}
	    }
	}
	if(jarsV.size() == 0 ) return null;
	return IntrospectionUtils.getClassPath( jarsV );
    }

    protected URL[] addModulesContainerCP(URL orig[] ) {
	URL mCP[]=findModulesCP( "/WEB-INF/lib/container" );
	if( mCP == null || mCP.length==0 ) return orig;
	URL result[]=new URL[ orig.length + mCP.length ];
	System.arraycopy( mCP, 0, result, 0, mCP.length );
	System.arraycopy( orig, 0, result, 0, orig.length );
	return result;
    }
    
    // -------------------- Utils --------------------


    public void debug( String s ) {
	debug( s, null );
    }

    public void debug( String s, Throwable t ) {
	System.out.println("EmbededTomcat: " + s );
	if( t!=null) t.printStackTrace();
    }

    public BaseInterceptor createModule( String classN ) {
	try {
	    Class c=containerCL.loadClass( classN );
	    return (BaseInterceptor)c.newInstance();
	} catch( Exception ex ) {
	    debug( "error creating module " + classN, ex);
	    return null;
	}
    }

    // -------------------- COMPAT --------------------

    // Alternative property names, for backward compat.
    public void setSecurity(boolean b) {
	setSandbox(true);
    }
    public void setH(String s ) {
	setHome(s);
    }
    public void setI(String s ) {
	setInstall(s);
    }
    public void setF(String s ) {
	setConfig(s);
    }
    public void addInterceptor( BaseInterceptor ri )
	throws TomcatException
    {
	addModule( ri );
    }

    // Other methods, no longer used 
    public boolean isInitialized() {
	return initialized;
    }

    /** This is an adapter object that provides callbacks into the
     *  application.
     */
    public void addApplicationAdapter( BaseInterceptor adapter )
	throws TomcatException
    {
	if(modules.size()==0)
	    addDefaultModules();
	addModule(adapter);
    }

    // -------------------- PROPERTIES --------------------

    // Server.xml equivalent
    protected String moduleSet1[] = {
	"org.apache.tomcat.modules.config.HookSetter",
	"org.apache.tomcat.modules.config.PathSetter",
	"org.apache.tomcat.modules.config.LoaderInterceptor11",
	"org.apache.tomcat.modules.config.TrustedLoader",
	"org.apache.tomcat.modules.config.LogSetter", 

	"org.apache.tomcat.modules.mappers.SimpleMapper1",
	"org.apache.tomcat.modules.session.SessionExpirer",
	"org.apache.tomcat.modules.session.SessionIdGenerator",
	"org.apache.tomcat.modules.session.SessionId",

	"org.apache.tomcat.facade.WebXmlReader",
	"org.apache.tomcat.modules.generators.ErrorHandler",
	"org.apache.tomcat.modules.config.WorkDirSetup",
	"org.apache.tomcat.modules.generators.Jdk12Interceptor",
	"org.apache.tomcat.modules.generators.InvokerInterceptor",
        //XXX GCC-HACK	"org.apache.tomcat.facade.JspInterceptor",
	"org.apache.tomcat.modules.generators.StaticInterceptor",

	"org.apache.tomcat.modules.mappers.ReloadInterceptor",

	"org.apache.tomcat.modules.session.SimpleSessionStore",
	
	"org.apache.tomcat.modules.aaa.AccessInterceptor",
	"org.apache.tomcat.modules.aaa.CredentialsInterceptor",
	"org.apache.tomcat.modules.aaa.SimpleRealm",
	
	"org.apache.tomcat.facade.LoadOnStartupInterceptor",
	"org.apache.tomcat.facade.Servlet22Interceptor",

	"org.apache.tomcat.modules.mappers.DecodeInterceptor"
    };

    static String POLICY_MODULE=
	"org.apache.tomcat.modules.config.PolicyInterceptor";
    static String LOG_EVENTS_MODULE =
	"org.apache.tomcat.modules.loggers.LogEvents";
    // Autodeploy/autowebapp
    protected String moduleSetAD[] = { 
	"org.apache.tomcat.modules.config.ContextXmlReader",
	"org.apache.tomcat.modules.config.AutoDeploy",
	"org.apache.tomcat.modules.config.AutoWebApp"
   };
    
    // -------------------- Help --------------------

    public static void printUsage() {
	PrintStream out=System.out;
	out.println("Usage: java org.apache.tomcat.startup.EmbeddedTomcat {options}");
	out.println("  Options are:");
	out.println("    -config file (or -f file)  Use this file instead of server.xml");
        out.println("    -debug level               Sets specified debug level on EmbeddedTomcat,");
        out.println("                                   ContextManager, \"Xml\" modules, and contexts");
        out.println("    -estart                    Starts Tomcat without reading server.xml");
        out.println("    -help                      Show this usage report");
	out.println("    -home dir                  Use this directory as tomcat.home");
	out.println("    -install dir (or -i dir)   Use this directory as tomcat.install");
        out.println("    -jkconf                    Write mod_jk configuration files, without");
        out.println("                                   starting Tomcat");
        out.println("    -sandbox                   Enable security manager (includes java.policy)");
        out.println("Note: the '-' on the options is optional.");
        out.println();
    }

    // -------------------- Override --------------------

    /** Hook - will be called after all modules are configured,
     *  before they are added to the ContextManager.
     */ 
    protected void beforeAddInterceptors() throws TomcatException {
	//int mid=findModule( "org.apache.tomcat.modules.config.LoaderInterceptor11" ,0);
	//setModuleProperty( mid, "debug", "10" );
    }
}
