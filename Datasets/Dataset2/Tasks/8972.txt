BaseInterceptor ci[]=cm.getContainer().getInterceptors();

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
package org.apache.tomcat.task;

import org.apache.tomcat.core.*;
import org.apache.tomcat.util.*;
import org.apache.tomcat.util.log.*;
import java.io.*;
import java.net.*;
import java.util.*;

// Used to find Ajp12 connector port
import org.apache.tomcat.service.PoolTcpConnector;
import org.apache.tomcat.service.connector.Ajp12ConnectionHandler;
import org.apache.tomcat.modules.server.Ajp12Interceptor;

/**
 * Used by ContextManager to generate automatic apache configurations
 *
 * @author costin@dnt.ro
 */
public class ApacheConfig  { // implements XXX
    // XXX maybe conf/
    public static final String APACHE_CONFIG  = "/conf/jserv/tomcat-apache.conf";
    public static final String MOD_JK_CONFIG  = "/conf/jk/mod_jk.conf";
    public static final String WORKERS_CONFIG = "/conf/jk/workers.properties";
    public static final String JK_LOG_LOCATION = "/logs/mod_jk.log";

    public ApacheConfig() {
    }

    String findApache() {
	return null;
    }

    Log loghelper = new Log("tc_log", this);
    
    public void execute(ContextManager cm) throws TomcatException {
	try {
	    String tomcatHome = cm.getHome();
	    String apacheHome = findApache();

	    //log("Tomcat home= " + tomcatHome);

	    FileWriter configW=new FileWriter(tomcatHome + APACHE_CONFIG);
	    PrintWriter pw=new PrintWriter(configW);
        PrintWriter mod_jk = new PrintWriter(new FileWriter(tomcatHome + MOD_JK_CONFIG + "-auto"));

        mod_jk.println("###################################################################");
        mod_jk.println("# Auto generated configuration. Dated: " +  new Date());
        mod_jk.println("###################################################################");
        mod_jk.println();
        
        mod_jk.println("#");
        mod_jk.println("# The following line instructs Apache to load the jk module");
        mod_jk.println("#");
	    if( System.getProperty( "os.name" ).toLowerCase().indexOf("windows") >= 0 ) {
		pw.println("LoadModule jserv_module modules/ApacheModuleJServ.dll");
                mod_jk.println("LoadModule jk_module modules/mod_jk.dll");
                mod_jk.println();                
                mod_jk.println("JkWorkersFile \"" + new File(tomcatHome, WORKERS_CONFIG).toString().replace('\\', '/') + "\"");
                mod_jk.println("JkLogFile \"" + new File(tomcatHome, JK_LOG_LOCATION).toString().replace('\\', '/') + "\"");
	    } else {
		// XXX XXX change it to mod_jserv_${os.name}.so, put all so in tomcat
		// home
		pw.println("LoadModule jserv_module libexec/mod_jserv.so");
                mod_jk.println("LoadModule jk_module libexec/mod_jk.so");
                mod_jk.println();                                
                mod_jk.println("JkWorkersFile " + new File(tomcatHome, WORKERS_CONFIG));
                mod_jk.println("JkLogFile " + new File(tomcatHome, JK_LOG_LOCATION));
	    }


	    pw.println("ApJServManual on");
	    pw.println("ApJServDefaultProtocol ajpv12");
	    pw.println("ApJServSecretKey DISABLED");
	    pw.println("ApJServMountCopy on");
	    pw.println("ApJServLogLevel notice");
	    pw.println();

	    // Find Ajp12 connector
	    int portInt=8007;
	    BaseInterceptor ci[]=cm.getInterceptors();
	    for( int i=0; i<ci.length; i++ ) {
		Object con=ci[i];
		if( con instanceof  Ajp12ConnectionHandler ) {
		    PoolTcpConnector tcpCon=(PoolTcpConnector) con;
		    portInt=tcpCon.getPort();
		}
		if( con instanceof  Ajp12Interceptor ) {
		    Ajp12Interceptor tcpCon=(Ajp12Interceptor) con;
		    portInt=tcpCon.getPort();
		}
	    }
	    pw.println("ApJServDefaultPort " + portInt);
	    pw.println();

	    pw.println("AddType text/jsp .jsp");
	    pw.println("AddHandler jserv-servlet .jsp");
	    pw.println();

        mod_jk.println();
        mod_jk.println("#");        
        mod_jk.println("# Log level to be used by mod_jk");
        mod_jk.println("#");        
        mod_jk.println("JkLogLevel error");
	    mod_jk.println();

        mod_jk.println("###################################################################");
        mod_jk.println("#                     SSL configuration                           #");
        mod_jk.println("# ");                
        mod_jk.println("# By default mod_jk is configured to collect SSL information from");
        mod_jk.println("# the apache environment and send it to the Tomcat workers. The");
        mod_jk.println("# problem is that there are many SSL solutions for Apache and as");
        mod_jk.println("# a result the environment variable names may change.");
        mod_jk.println("#");        
        mod_jk.println("# The following (commented out) JK related SSL configureation");        
        mod_jk.println("# can be used to customize mod_jk's SSL behaviour.");        
        mod_jk.println("# ");        
        mod_jk.println("# Should mod_jk send SSL information to Tomact (default is On)");        
        mod_jk.println("# JkExtractSSL Off");        
        mod_jk.println("# ");        
        mod_jk.println("# What is the indicator for SSL (default is HTTPS)");        
        mod_jk.println("# JkHTTPSIndicator HTTPS");        
        mod_jk.println("# ");        
        mod_jk.println("# What is the indicator for SSL session (default is SSL_SESSION_ID)");        
        mod_jk.println("# JkSESSIONIndicator SSL_SESSION_ID");        
        mod_jk.println("# ");        
        mod_jk.println("# What is the indicator for client SSL cipher suit (default is SSL_CIPHER)");        
        mod_jk.println("# JkCIPHERIndicator SSL_CIPHER");
        mod_jk.println("# ");        
        mod_jk.println("# What is the indicator for the client SSL certificated (default is SSL_CLIENT_CERT)");        
        mod_jk.println("# JkCERTSIndicator SSL_CLIENT_CERT");
        mod_jk.println("# ");        
        mod_jk.println("#                                                                 #");        
        mod_jk.println("###################################################################");
        mod_jk.println();


        mod_jk.println("#");        
        mod_jk.println("# Root context mounts for Tomcat");
        mod_jk.println("#");        
        mod_jk.println("JkMount /*.jsp ajp12");
        mod_jk.println("JkMount /servlet/* ajp12");
        mod_jk.println();

	    // Set up contexts
	    // XXX deal with Virtual host configuration !!!!
	Enumeration  enum = cm.getContexts();
	    while (enum.hasMoreElements()) {
		Context context = (Context)enum.nextElement();
		String path  = context.getPath();
		String vhost = context.getHost();

		if( vhost != null ) {
		    // Generate Apache VirtualHost section for this host
		    // You'll have to do it manually right now
		    // XXX
		    continue;
		}
		if( path.length() > 1) {

		    // It's not the root context
		    // assert path.startsWith( "/" )

		    // Calculate the absolute path of the document base
		    String docBase = context.getDocBase();
		    if (!FileUtil.isAbsolute(docBase))
			docBase = tomcatHome + "/" + docBase;
		    docBase = FileUtil.patch(docBase);
			if (File.separatorChar == '\\')
				docBase = docBase.replace('\\','/');	// use separator preferred by Apache

		    // Static files will be served by Apache
		    pw.println("Alias " + path + " \"" + docBase + "\"");
		    pw.println("<Directory \"" + docBase + "\">");
		    pw.println("    Options Indexes FollowSymLinks");
		    pw.println("</Directory>");

		    // Dynamic /servet pages go to Tomcat
		    pw.println("ApJServMount " + path +"/servlet" + " " + path);

		    // Deny serving any files from WEB-INF
		    pw.println("<Location \"" + path + "/WEB-INF/\">");
		    pw.println("    AllowOverride None");
		    pw.println("    deny from all");
		    pw.println("</Location>");
			// For Windows, use Directory too. Location doesn't work unless case matches
			if (File.separatorChar == '\\') {
				pw.println("<Directory \"" + docBase + "/WEB-INF/\">");
				pw.println("    AllowOverride None");
				pw.println("    deny from all");
				pw.println("</Directory>");
			}

		    // Deny serving any files from META-INF
			pw.println("<Location \"" + path + "/META-INF/\">");
			pw.println("    AllowOverride None");
			pw.println("    deny from all");
			pw.println("</Location>");
			// For Windows, use Directory too. Location doesn't work unless case matches
			if (File.separatorChar  == '\\') {
				pw.println("<Directory \"" + docBase + "/META-INF/\">");
				pw.println("    AllowOverride None");
				pw.println("    deny from all");
				pw.println("</Directory>");
			}
		    pw.println();


		    // Static files will be served by Apache
            mod_jk.println("#########################################################");		    
            mod_jk.println("# Auto configuration for the " + path + " context starts.");
            mod_jk.println("#########################################################");		    
            mod_jk.println();
            
            mod_jk.println("#");		    
            mod_jk.println("# The following line makes apache aware of the location of the " + path + " context");
            mod_jk.println("#");                        
		    mod_jk.println("Alias " + path + " \"" + docBase + "\"");
		    mod_jk.println("<Directory \"" + docBase + "\">");
		    mod_jk.println("    Options Indexes FollowSymLinks");
		    mod_jk.println("</Directory>");
            mod_jk.println();            

		    // Dynamic /servet pages go to Tomcat
            mod_jk.println("#");		    
            mod_jk.println("# The following line mounts all JSP files and the /servlet/ uri to tomcat");
            mod_jk.println("#");                        
		    mod_jk.println("JkMount " + path +"/servlet/* ajp12");
		    mod_jk.println("JkMount " + path +"/*.jsp ajp12");


		    // Deny serving any files from WEB-INF
            mod_jk.println();            
            mod_jk.println("#");		    
            mod_jk.println("# The following line prohibits users from directly accessing WEB-INF");
            mod_jk.println("#");                        
		    mod_jk.println("<Location \"" + path + "/WEB-INF/\">");
		    mod_jk.println("    AllowOverride None");
		    mod_jk.println("    deny from all");
		    mod_jk.println("</Location>");
			if (File.separatorChar == '\\') {
				mod_jk.println("#");		    
				mod_jk.println("# Use Directory too. On Windows, Location doesn't work unless case matches");
				mod_jk.println("#");                        
				mod_jk.println("<Directory \"" + docBase + "/WEB-INF/\">");
				mod_jk.println("    AllowOverride None");
				mod_jk.println("    deny from all");
				mod_jk.println("</Directory>");
			}

			// Deny serving any files from META-INF
        	mod_jk.println();            
        	mod_jk.println("#");		    
        	mod_jk.println("# The following line prohibits users from directly accessing META-INF");
        	mod_jk.println("#");                        
			mod_jk.println("<Location \"" + path + "/META-INF/\">");
			mod_jk.println("    AllowOverride None");
			mod_jk.println("    deny from all");
			mod_jk.println("</Location>");
			if (File.separatorChar == '\\') {
				mod_jk.println("#");		    
				mod_jk.println("# Use Directory too. On Windows, Location doesn't work unless case matches");
				mod_jk.println("#");                        
				mod_jk.println("<Directory \"" + docBase + "/META-INF/\">");
				mod_jk.println("    AllowOverride None");
				mod_jk.println("    deny from all");
				mod_jk.println("</Directory>");
			}
		    mod_jk.println();

            mod_jk.println("#######################################################");		    
            mod_jk.println("# Auto configuration for the " + path + " context ends.");
            mod_jk.println("#######################################################");		    
            mod_jk.println();

		    // XXX check security
		    if( false ) {
			pw.println("<Location " + path + "/servlet/ >");
			pw.println("    AllowOverride None");
			pw.println("   AuthName \"restricted \"");
			pw.println("    AuthType Basic");
			pw.println("    AuthUserFile conf/users");
			pw.println("    require valid-user");
			pw.println("</Location>");
		    }

	        // XXX ErrorDocument

		    // XXX mime types - AddEncoding, AddLanguage, TypesConfig
		} else {
		    // the root context
		    // XXX use a non-conflicting name
		    pw.println("ApJServMount /servlet /ROOT");
		}

	    }

	    pw.close();
	    mod_jk.close();        
	} catch( Exception ex ) {
	    loghelper.log("Error generating automatic apache configuration", ex);
	}
    }
}