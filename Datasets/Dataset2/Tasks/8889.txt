System.out.println("Failed to generate automatic apache configuration " + ex.toString());

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
import java.io.*;
import java.net.*;
import java.util.*;
import javax.servlet.http.*;


/**
 * Used by ContextManager to generate automatic apache configurations
 *
 * @author costin@dnt.ro
 */
public class ApacheConfig  { // implements XXX
    // XXX maybe conf/
    public static final String APACHE_CONFIG="/conf/tomcat-apache.conf";
    
    public ApacheConfig() {
    }

    String findApache() {
	return null;
    }
    
    public void execute(ContextManager cm) throws TomcatException {
	try {
	    String tomcatHome= cm.getHome();
	    String apacheHome=findApache();
	    
	    //System.out.println("Tomcat home= " + tomcatHome);
	    
	    FileWriter configW=new FileWriter( tomcatHome + APACHE_CONFIG);
	    PrintWriter pw=new PrintWriter( configW );

	    if( System.getProperty( "os.name" ).toLowerCase().indexOf("windows") >= 0 ) {
		pw.println("LoadModule jserv_module modules/ApacheModuleJServ.dll");
	    } else {
		// XXX XXX change it to mod_jserv_${os.name}.so, put all so in tomcat
		// home
		pw.println("LoadModule jserv_module libexec/mod_jserv.so");
	    }

	    pw.println("ApJServManual on");
	    pw.println("ApJServDefaultProtocol ajpv12");
	    pw.println("ApJServSecretKey DISABLED");
	    pw.println("ApJServMountCopy on");
	    pw.println("ApJServLogLevel notice");
	    pw.println();
	    
	    // XXX read it from ContextManager
	    pw.println("ApJServDefaultPort 8007");

	    pw.println();
	    pw.println("AddType test/jsp .jsp");
	    pw.println("AddHandler jserv-servlet .jsp");

	    
	    // Set up contexts 
	    
	    Enumeration enum = cm.getContextNames();
	    while (enum.hasMoreElements()) {
		String path=(String)enum.nextElement();
		Context context = cm.getContext(path);
		if( path.length() > 1) {
		    // It's not the root context
		    // assert path.startsWith( "/" )

		    // Static files will be served by Apache
		    pw.println("Alias " + path + " " + 
                               FileUtil.patch(tomcatHome + "/webapps" + path));

		    // Dynamic /servet pages go to tomcat
		    pw.println("ApJServMount " + path +"/servlet" + " " + path);

		    // Deny WEB-INF
		    pw.println("<Location " + path + "/WEB-INF/ >");
		    pw.println("    AllowOverride None");
		    pw.println("    deny from all");
		    pw.println("</Location>");
		    pw.println();

		    // SetHandler broken in jserv ( no zone is sent )
		    // 		    pw.println("<Location " + path + "/servlet/ >");
		    // 		    pw.println("    AllowOverride None");
		    // 		    pw.println("    SetHandler jserv-servlet");
		    // 		    pw.println("</Location>");
		    // 		    pw.println();

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
				    
		    // SetHandler broken in jserv ( no zone is sent )
		    // 		    pw.println("<Location " + path + " >");
		    // 		    pw.println("    AllowOverride None");
		    // 		    pw.println("    AddHandler jserv-servlet .jsp");
		    // 		    pw.println("    Options Indexes");
		    // 		    pw.println("</Location>");

		    // XXX ErrorDocument

		    // XXX mime types - AddEncoding, AddLanguage, TypesConfig

		    
		} else {
		    // the root context
		    // XXX use a non-conflicting name
		    pw.println("ApJServMount /servlet /ROOT");
		}

	    }

	    pw.close();
	} catch( Exception ex ) {
	    //	    ex.printStackTrace();
	    //throw new TomcatException( "Error generating Apache config", ex );
	    System.out.println("Failed to generate automactic apache confiugration " + ex.toString());
	}
	    
    }

}