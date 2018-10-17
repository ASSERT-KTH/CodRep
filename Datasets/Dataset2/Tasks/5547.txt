private static int dL=0;

package org.apache.tomcat.startup;

import java.beans.*;
import java.io.*;
import java.io.IOException;
import java.lang.reflect.*;
import java.util.Hashtable;
import java.util.*;
import java.net.*;
import org.apache.tomcat.util.res.StringManager;
import org.apache.tomcat.util.xml.*;
import org.apache.tomcat.util.compat.*;
import org.apache.tomcat.util.log.*;
import org.xml.sax.*;
import org.apache.tomcat.util.collections.*;
import org.apache.tomcat.util.IntrospectionUtils;

/**
 * 
 * @author Costin Manolache
 */
public class Jspc {

    Hashtable attributes=new Hashtable();
    String args[];
    String installDir;
    ClassLoader parentL;

    public Jspc() {
    }
    
    //-------------------- Properties --------------------

    public void setArgs( String args[]) {
	this.args=args;
    }

    public void setInstall( String s ) {
	installDir=s;
    }
    
    // -------------------- execute --------------------
    static Jdk11Compat jdk11Compat=Jdk11Compat.getJdkCompat();
    
    public void execute() throws Exception
    {
	if( args!=null )
	    processArgs( args );
	Vector v=new Vector();
	String commonDir=installDir + File.separator + "lib" +
	    File.separator + "common";
	IntrospectionUtils.addToClassPath( v, commonDir);
	IntrospectionUtils.addToolsJar(v);
	String containerDir=installDir + File.separator + "lib" +
	    File.separator + "container";
	IntrospectionUtils.addToClassPath( v, containerDir);
	String appsDir=installDir + File.separator + "lib" +
	    File.separator + "apps";
	IntrospectionUtils.addToClassPath( v, appsDir);
	URL commonCP[]=
	    IntrospectionUtils.getClassPath( v );
	ClassLoader commonCL=
	    jdk11Compat.newClassLoaderInstance(commonCP, parentL);

	Class jspcClass=commonCL.loadClass( "org.apache.jasper.JspC");
	IntrospectionUtils.callMain( jspcClass, args );
    }
	
    // -------------------- Command-line args processing --------------------

    /** Process arguments - set object properties from the list of args.
     */
    public  boolean processArgs(String[] args) {
	try {
	    if( args.length > 0  && "jspc".equalsIgnoreCase( args[0])) {
		String args1[]=new String[args.length-1];
		System.arraycopy( args,1, args1, 0, args.length-1);
		args=args1;
	    }
	    setArgs(args);	    
	    // return IntrospectionUtils.processArgs( this, args,getOptions1(),
	    // 		   null, getOptionAliases());
	} catch( Exception ex ) {
	    ex.printStackTrace();
	}
	return false;
    }

    /** Callback from argument processing
     */
    public void setProperty(String s,Object v) {
	if ( dL > 0 ) debug( "Generic property " + s );
	attributes.put(s,v);
    }

    /** Called by Main to set non-string properties
     */
    public void setAttribute(String s,Object o) {
	if( "install".equals( s ) ) {
	    setInstall( (String)o);
	}
	
        if ( "args".equals(s) ) {
	    args=(String[])o;
	}
        if ( "parentClassLoader".equals(s) ) {
	    parentL=(ClassLoader)o;
	}


	attributes.put(s,o);
    }

    // -------------------- Main --------------------

    public static void main(String args[] ) {
	try {
	    Jspc task=new Jspc();
	    task.setArgs( args );
            task.execute();
	} catch(Exception ex ) {
	    ex.printStackTrace();
	    System.exit(1);
	}
    }

    private static int dL=10;
    private void debug( String s ) {
	System.out.println("Jspc: " + s );
    }
}