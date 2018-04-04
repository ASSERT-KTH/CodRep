SimpleHashtable attributes=new SimpleHashtable();

package org.apache.tomcat.startup;

import java.beans.*;
import java.io.*;
import java.io.IOException;
import java.lang.reflect.*;
import java.util.Hashtable;
import java.util.*;
import java.net.*;
import org.apache.tomcat.util.res.StringManager;
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
public class Tomcat {

    private static StringManager sm =
	StringManager.getManager("org.apache.tomcat.resources");

    private String action="start";

    String home=null;
    String args[];
    ClassLoader parentClassLoader;
    boolean sandbox=false;
    
    // null means user didn't set one
    String configFile=null;
    // relative to TOMCAT_HOME
    static final String DEFAULT_CONFIG="conf/server.xml";
    SimpleHashtable attributes=new SimpleHashtable();;
    static Log log=Log.getLog( "tc_log", "Tomcat" );
    
    public Tomcat() {
    }
    //-------------------- Properties --------------------
    
    public void setHome(String home) {
	this.home=home;
    }
    
    public void setArgs(String args[]) {
	this.args=args;
    }
    

    public void setAction(String s ) {
	action=s;
    }

    public void setSandbox( boolean b ) {
	sandbox=b;
    }
    
    public void setParentClassLoader( ClassLoader cl ) {
	parentClassLoader=cl;
    }
    // -------------------- main/execute --------------------
    
    public static void main(String args[] ) {
	try {
	    Tomcat tomcat=new Tomcat();
	    tomcat.setArgs( args );
            tomcat.execute();
	} catch(Exception ex ) {
	    log.log(sm.getString("tomcat.fatal"), ex);
	    System.exit(1);
	}
    }

    public void execute() throws Exception {
	//	String[] args=(String[])attributes.get("args");
        if ( args == null || ! processArgs( args )) {
	    setAction("help");
	}
	if( "stop".equals( action )){
	    stop();
	} else if( "enableAdmin".equals( action )){
	    enableAdmin();
	} else if( "help".equals( action )) {
	    printUsage();
	} else if( "start".equals( action )) {
	    start();
	}
    }

    // -------------------- Actions --------------------

    public void enableAdmin() throws IOException
    {
	System.out.println("Overriding apps-admin settings ");
	FileWriter fw=new FileWriter( home + File.separator +
				      "conf" + File.separator +
				      "apps-admin.xml" );
	PrintWriter pw=new PrintWriter( fw );
	pw.println( "<webapps>" );
	pw.println( "  <Context path=\"/admin\"");
	pw.println( "           docBase=\"webapps/admin\"");
	pw.println( "           trusted=\"true\">");
	pw.println( "    <SimpleRealm");
        pw.println( "      filename=\"conf/users/admin-users.xml\" />");
	pw.println( "  </Context>");
	pw.println( "</webapps>" );
	pw.close();
    }
	
    public void stop() throws Exception {
	System.out.println(sm.getString("tomcat.stop"));
	try {
	    StopTomcat task=
		new  StopTomcat();

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
        ClassLoader cl=parentClassLoader;

        if (cl==null) cl=this.getClass().getClassLoader();

        tcat.getContextManager().setParentLoader(cl);
	if( sandbox )
	    tcat.getContextManager().setProperty( "sandbox", "true");
	tcat.initContextManager();

	tcat.start();
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
	    } else if (arg.equals("-sandbox")) {
		sandbox=true;
	    } else if (arg.equals("-security")) {
		sandbox=true;
	    } else if (arg.equals("-enableAdmin")) {
		action="enableAdmin";
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

    // Hack for Main.java, will be replaced with calling the setters directly
    public void setAttribute(String s,Object o) {
	if( "home".equals( s ) )
	    setHome( (String)o);
	else if("args".equals( s ) ) 
	    setArgs((String[])o);
	else if( "parentClassLoader".equals( s ) ) {
	    setParentClassLoader((ClassLoader)o);
	} else {
	    System.out.println("Tomcat: setAttribute " + s + "=" + o);
	    attributes.put(s,o);
	}
    }
}