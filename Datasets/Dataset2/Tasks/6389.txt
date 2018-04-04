//        System.out.println(s+":"+o);

package org.apache.tomcat.startup;

import java.beans.*;
import java.io.*;
import java.io.IOException;
import java.lang.reflect.*;
import java.util.Hashtable;
import java.util.*;
import java.net.*;
import org.apache.tomcat.util.*;
import org.apache.tomcat.modules.config.*;
import org.apache.tomcat.util.xml.*;
import org.apache.tomcat.core.*;
import org.apache.tomcat.util.log.*;
import org.xml.sax.*;
import org.apache.tomcat.util.collections.*;

/**
 * Starter for Tomcat using XML.
 * Based on Ant.
 *
 * @author costin@dnt.ro
 */
public class Tomcat extends Log {

    private static StringManager sm =
	StringManager.getManager("org.apache.tomcat.resources");

    private String action="start";

    // null means user didn't set one
    String configFile=null;
    // relative to TOMCAT_HOME
    static final String DEFAULT_CONFIG="conf/server.xml";
    SimpleHashtable attributes=new SimpleHashtable();;

    public Tomcat() {
	super("tc_log");
    }

    public void execute() throws Exception {
	if( "stop".equals( action )){
	    stop();
	} else if( "help".equals( action )) {
	    printUsage();
	} else if( "start".equals( action )) {
	    start();
	}
    }

    public void stop() throws Exception {
	System.out.println(sm.getString("tomcat.stop"));
	try {
	    StopTomcat task=
		new  StopTomcat();

//	    task.setConfig( configFile );
	    task.execute();     
	}
	catch (TomcatException te) {
	    if (te.getRootCause() instanceof java.net.ConnectException)
		System.out.println(sm.getString("tomcat.connectexception"));
	    else
		throw te;
	}
	return;
    }

    public void start() throws Exception {
	EmbededTomcat tcat=new EmbededTomcat();

	PathSetter pS=new PathSetter();
	tcat.addInterceptor( pS );
	
	ServerXmlReader sxmlConf=new ServerXmlReader();
	sxmlConf.setConfig( configFile );
	tcat.addInterceptor( sxmlConf );
        ClassLoader cl=(ClassLoader)attributes.get("parentClassLoader");
        //System.out.println("parentClassLoader:"+cl);
        //System.out.println("thisClassLoader:"+this.getClass().getClassLoader());
        if (cl==null) cl=this.getClass().getClassLoader();
        //System.out.println("parentClassLoader:"+cl);
        tcat.getContextManager().setParentLoader(cl);
	tcat.initContextManager();

	tcat.start();
    }

    public void setAction(String s ) {
	action=s;
    }

    public static void main(String args[] ) {
	try {
	    Tomcat tomcat=new Tomcat();
            if( ! tomcat.processArgs( args )) {
                tomcat.setAction("help");
            }
            tomcat.execute();
	} catch(Exception ex ) {
	    System.out.println(sm.getString("tomcat.fatal"));
	    System.err.println(Logger.throwableToString(ex));
	    System.exit(1);
	}
    }

    // -------------------- Command-line args processing --------------------


    public static void printUsage() {
	//System.out.println(sm.getString("tomcat.usage"));
	System.out.println("Usage: java org.apache.tomcat.startup.Tomcat {options}");
	System.out.println("  Options are:");
	System.out.println("    -config file (or -f file)  Use this fileinstead of server.xml");
	System.out.println("    -help (or help)            Show this usage report");
	System.out.println("    -home dir (or -h dir)      Use this directory as tomcat.home");
	System.out.println("    -stop                      Shut down currently running Tomcat");
    }

    /** Process arguments - set object properties from the list of args.
     */
    public  boolean processArgs(String[] args) {
	for (int i = 0; i < args.length; i++) {
	    String arg = args[i];

	    if (arg.equals("-help") || arg.equals("help")) {
		action="help";
		return false;
	    } else if (arg.equals("-stop")) {
		action="stop";
	    } else if (arg.equals("-g") || arg.equals("-generateConfigs")) {
		// config generation is now a module. //doGenerate=true;
	    } else if (arg.equals("-f") || arg.equals("-config")) {
		i++;
		if( i < args.length )
		    configFile = args[i];
		else
		    return false;
	    } else if (arg.equals("-h") || arg.equals("-home")) {
		i++;
		if (i < args.length)
		    System.getProperties().put("tomcat.home", args[i]);
		else
		    return false;
	    }
	}
	return true;
    }

    public void setAttribute(String s,Object o) {
        attributes.put(s,o);
        System.out.println(s+":"+o);
    }
    public void executeWithAttributes() throws Exception {
       String[] args=(String[])attributes.get("args");
        if ( args != null ){
            if( ! processArgs( args )) {
                setAction("help");
            }
        } else setAction("help");
        execute();
    }
}