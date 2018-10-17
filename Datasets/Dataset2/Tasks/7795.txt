"org.apache.tomcat.core.ContextInterceptor") );

package org.apache.tomcat.startup;

import java.beans.*;
import java.io.*;
import java.io.IOException;
import java.lang.reflect.*;
import java.util.Hashtable;
import java.util.*;
import java.net.*;
import org.apache.tomcat.util.*;
import org.apache.tomcat.util.xml.*;
import org.apache.tomcat.core.*;
import org.apache.tomcat.logging.*;
import org.xml.sax.*;
import org.apache.tomcat.core.Constants;

/**
 * Starter for Tomcat using XML.
 * Based on Ant.
 *
 * @author costin@dnt.ro
 */
public class Tomcat extends Logger.Helper {

    private static StringManager sm =
	StringManager.getManager("org.apache.tomcat.resources");

    Tomcat() {
	super("tc_log");
    }

    // Set the mappings
    void setHelper( XmlMapper xh ) {
	xh.addRule( "ContextManager", xh.setProperties() );

	xh.addRule( "ContextManager/ContextInterceptor",
		    xh.objectCreate(null, "className"));
	xh.addRule( "ContextManager/ContextInterceptor",
		    xh.setProperties() );
	xh.addRule( "ContextManager/ContextInterceptor",
		    xh.setParent("setContextManager") );
	xh.addRule( "ContextManager/ContextInterceptor",
		    xh.addChild( "addContextInterceptor",
				 "org.apache.tomcat.core.ContextInterceptor"));

	xh.addRule( "ContextManager/RequestInterceptor",
		    xh.objectCreate(null, "className"));
	xh.addRule( "ContextManager/RequestInterceptor",
		    xh.setProperties() );
	xh.addRule( "ContextManager/RequestInterceptor",
		    xh.setParent("setContextManager") );
	xh.addRule( "ContextManager/RequestInterceptor",
		    xh.addChild( "addRequestInterceptor",
				 "org.apache.tomcat.core.RequestInterceptor"));

	// Default host
 	xh.addRule( "ContextManager/Context",
		    xh.objectCreate("org.apache.tomcat.core.Context"));
	xh.addRule( "ContextManager/Context",
		    xh.setParent( "setContextManager") );
	xh.addRule( "ContextManager/Context",
		    xh.setProperties() );
	xh.addRule( "ContextManager/Context",
		    xh.addChild( "addContext", null ) );

	// Virtual host support.
	// Push a host object on the stack
 	xh.addRule( "ContextManager/Host", new XmlAction() {
		public void start( SaxContext ctx) throws Exception {
		    Stack st=ctx.getObjectStack();
		    // get attributes 
		    int top=ctx.getTagCount()-1;
		    AttributeList attributes = ctx.getAttributeList( top );

		    // get CM
		    ContextManager cm=(ContextManager)st.peek();

		    // construct virtual host config helper
		    HostConfig hc=new HostConfig(cm);

		    // set the host name
		    hc.setName( attributes.getValue("name")); 
		    st.push( hc );
		}
		public void cleanup( SaxContext ctx) {
		    Stack st=ctx.getObjectStack();
		    Object o=st.pop();
		}
	    });
	xh.addRule( "ContextManager/Host", xh.setProperties());
	
 	xh.addRule( "ContextManager/Host/Context",
		    xh.objectCreate("org.apache.tomcat.core.Context"));
	xh.addRule( "ContextManager/Host/Context",
		    xh.setProperties() );
	xh.addRule( "ContextManager/Host/Context", new XmlAction() {
		public void end( SaxContext ctx) throws Exception {
		    Stack st=ctx.getObjectStack();
		    
		    Context tcCtx=(Context)st.pop(); // get the Context
		    HostConfig hc=(HostConfig)st.peek();
		    st.push( tcCtx );
		    // put back the context, to be cleaned up corectly
		    
		    hc.addContext( tcCtx );
		}
	    });
    }

    void setConnectorHelper( XmlMapper xh ) {
	xh.addRule( "ContextManager/Connector",
		    xh.objectCreate(null, "className"));
	xh.addRule( "ContextManager/Connector",
		    xh.setParent( "setServer", "java.lang.Object") );
	xh.addRule( "ContextManager/Connector",
		    xh.addChild( "addServerConnector",
				 "org.apache.tomcat.core.ServerConnector") );

	xh.addRule( "ContextManager/Connector/Parameter",
		    xh.methodSetter("setProperty",2) );
	xh.addRule( "ContextManager/Connector/Parameter",
		    xh.methodParam(0, "name") );
	xh.addRule( "ContextManager/Connector/Parameter",
		    xh.methodParam(1, "value") );

	// Connector as ContextInterceptor - experimental
	xh.addRule( "ContextManager/Connector1",
		    xh.objectCreate(null, "className"));
	xh.addRule( "ContextManager/Connector1",
		    xh.setParent( "setContextManager",
				  "org.apache.tomcat.core.ContextManager") );
	xh.addRule( "ContextManager/Connector1",
		    xh.addChild( "addContextInterceptor",
				 "org.apache.tomcat.core.ContextInterceptor"));

	xh.addRule( "ContextManager/Connector1/Parameter",
		    xh.methodSetter("setProperty",2) );
	xh.addRule( "ContextManager/Connector1/Parameter",
		    xh.methodParam(0, "name") );
	xh.addRule( "ContextManager/Connector1/Parameter",
		    xh.methodParam(1, "value") );
    }


    /** Setup loggers when reading the configuration file - this will be
     *  called only when starting tomcat as deamon, all other modes will
     * output to stderr
     * *** [I don't think that's true any more -Alex]
     */
    void setLogHelper( XmlMapper xh ) {
	xh.addRule("Server/Logger",
		   xh.objectCreate("org.apache.tomcat.logging.TomcatLogger"));
	xh.addRule("Server/Logger", xh.setProperties());
	xh.addRule("Server/Logger", 
		   xh.addChild("addLogger",
			       "org.apache.tomcat.logging.Logger") );
    }

    /**
     * Return the configuration file we are processing.  If the
     * <code>-config filename</code> command line argument is not
     * used, the default configuration filename will be loaded from
     * the TOMCAT_HOME directory.
     *
     * If a relative config file is used, it will be relative to the current
     * working directory.
     *
     * @param cm The ContextManager we are configuring
     **/
    File getConfigFile(ContextManager cm) {
	// If configFile is already set, use it
	if (configFile != null)
	    return (new File(configFile));

	// Use the "tomcat.home" property to resolve the default filename
	String tchome = System.getProperty("tomcat.home");
	if (tchome == null) {
	    System.out.println(sm.getString("tomcat.nohome"));
	    tchome = ".";
	    // Assume current working directory
	}
	// Home will be identical to tomcat home if default config is used.
	cm.setInstallDir(tchome);
	return (new File(tchome, DEFAULT_CONFIG));

    }

    public void execute(String args[] ) throws Exception {
	if( ! processArgs( args ) ) {
	    // System.out.println(sm.getString("tomcat.wrongargs"));	    
	    printUsage();
	    return;
	}

	if( doStop ) {
	    System.out.println(sm.getString("tomcat.stop"));
	    try {
		stopTomcat(); // stop serving
	    }
	    catch (TomcatException te) {
		if (te.getRootCause() instanceof java.net.ConnectException)
		    System.out.println(sm.getString("tomcat.connectexception"));
		else
		    throw te;
	    }
	    return;
	}

	XmlMapper xh=new XmlMapper();
	xh.setDebug( 0 );
	ContextManager cm=new ContextManager();
	setHelper( xh );
	setConnectorHelper( xh );
	setLogHelper( xh );

	File f = getConfigFile(cm);
	log(sm.getString("tomcat.loading") + " " + f);
	try {
	    xh.readXml(f,cm);
	} catch( Exception ex ) {
	    log( sm.getString("tomcat.fatalconfigerror"), ex );
	    throw ex;
	}
	log(sm.getString("tomcat.loaded") + " " + f);

	// by now, we should know where the log file is
	String path = cm.getLogger().getPath();
	if (path == null)
	    path = "console";
	else
	    path = new File(path).getAbsolutePath();
	System.out.println(sm.getString("tomcat.start", new Object[] { path }));
	
	cm.init(); // set up contexts
	log(Constants.TOMCAT_NAME + " " + Constants.TOMCAT_VERSION);	

	// XXX Make this optional, and make sure it doesn't require
	// a full start. It is called after init to make sure
	// auto-configured contexts are initialized.
	generateServerConfig( cm );
	try {
	    cm.start(); // start serving
	}
	catch (java.net.BindException be) {
	    log("Starting Tomcat: " + be.getMessage(), Logger.ERROR);
	    System.out.println(sm.getString("tomcat.bindexception"));
	    try {
		cm.stop();
	    }
	    catch (Exception e) {
		log("Stopping ContextManager", e);
	    }
	}
    }

    /** This method will generate Server config files that
	reflect the existing cm settings. It is called
	at startup, and may be called when a new context is
	added ( at runtime for example ).
    */
    public static void generateServerConfig( ContextManager cm )
	throws TomcatException
    {
	// Generate Apache configs
	//
	org.apache.tomcat.task.ApacheConfig apacheConfig=
	    new  org.apache.tomcat.task.ApacheConfig();
	apacheConfig.execute( cm );     

	// Generate IIS configs
	//
	org.apache.tomcat.task.IISConfig iisConfig=
	    new  org.apache.tomcat.task.IISConfig();
	iisConfig.execute( cm );     

	// Generate Netscape configs
	//
	org.apache.tomcat.task.NSConfig nsConfig=
	    new  org.apache.tomcat.task.NSConfig();
	nsConfig.execute( cm );     
    }
    
    public static void main(String args[] ) {
	try {
	    Tomcat tomcat=new Tomcat();
	    tomcat.execute( args );
	} catch(Exception ex ) {
	    System.out.println(sm.getString("tomcat.fatal"));
	    System.err.println(Logger.throwableToString(ex));
	    System.exit(1);
	}

    }

    /** Stop tomcat using the configured cm
     *  The manager is set up using the same configuration file, so
     *  it will have the same port as the original instance ( no need
     *  for a "log" file).
     *  It uses the Ajp12 connector, which has a built-in "stop" method,
     *  that will change when we add real callbacks ( it's equivalent
     *  with the previous RMI method from almost all points of view )
     */
    void stopTomcat() throws TomcatException {
	XmlMapper xh=new XmlMapper();
	xh.setDebug( 0 );
	ContextManager cm=new ContextManager();
	setConnectorHelper( xh );
	File f = getConfigFile(cm);
	try {
	    xh.readXml(f,cm);
	} catch( Exception ex ) {
	    throw new TomcatException("Fatal exception reading " + f, ex);
	}
	
	org.apache.tomcat.task.StopTomcat stopTc=
	    new  org.apache.tomcat.task.StopTomcat();
	stopTc.execute( cm );     
    }
    
    // -------------------- Command-line args processing --------------------
    // null means user didn't set one
    String configFile=null;
    // relative to TOMCAT_HOME 
    static final String DEFAULT_CONFIG="conf/server.xml";

    boolean doStop=false;
    
    public static void printUsage() {
	System.out.println(sm.getString("tomcat.usage"));
    }

    /** Process arguments - set object properties from the list of args.
     */
    public  boolean processArgs(String[] args) {
	for (int i = 0; i < args.length; i++) {
	    String arg = args[i];
            
	    if (arg.equals("-help") || arg.equals("help")) {
		printUsage();
		return false;
		
	    } else if (arg.equals("-stop")) {
		doStop=true;
	    } else if (arg.equals("-f") || arg.equals("-config")) {
		i++;
		if( i < args.length )
		    configFile = args[i];
	    } else if (arg.equals("-h") || arg.equals("-home")) {
		i++;
		if (i < args.length)
		    System.getProperties().put("tomcat.home", args[i]);
	    }
	}
	return true;
    }        

}