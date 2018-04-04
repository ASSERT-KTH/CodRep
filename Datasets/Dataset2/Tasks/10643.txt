Log loghelper = Log.getLog("tc_log", "IISConfig");

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
package org.apache.tomcat.modules.config;

import org.apache.tomcat.core.*;
import org.apache.tomcat.util.*;
import org.apache.tomcat.util.log.*;
import java.io.*;
import java.net.*;
import java.util.*;


/**
 * Used by ContextManager to generate automatic IIS configurations
 *
 * @author Gal Shachor shachor@il.ibm.com
 */
public class IISConfig extends BaseInterceptor  { 

    public static final String WORKERS_CONFIG = "/conf/jk/workers.properties";
    public static final String URL_WORKERS_MAP_CONFIG = "/conf/jk/uriworkermap.properties";
    public static final String JK_LOG_LOCATION = "/logs/iis_redirect.log";
    public static final String IIS_REG_FILE = "/conf/jk/iis_redirect.reg";    

    Log loghelper = new Log("tc_log", "IISConfig");

    public IISConfig() 
    {
    }

    public void engineInit(ContextManager cm) throws TomcatException
    {
	execute( cm );
    }
        
    public void execute(ContextManager cm) throws TomcatException 
    {
	    try {
	        String tomcatHome = cm.getHome();

            PrintWriter regfile = new PrintWriter(new FileWriter(tomcatHome + IIS_REG_FILE + "-auto"));
            PrintWriter uri_worker = new PrintWriter(new FileWriter(tomcatHome + URL_WORKERS_MAP_CONFIG + "-auto"));        

            regfile.println("REGEDIT4");
            regfile.println();
            regfile.println("[HKEY_LOCAL_MACHINE\\SOFTWARE\\Apache Software Foundation\\Jakarta Isapi Redirector\\1.0]");
            regfile.println("\"extension_uri\"=\"/jakarta/isapi_redirect.dll\"");
            regfile.println("\"log_file\"=\"" + dubleSlash(new File(tomcatHome, JK_LOG_LOCATION).toString()) +"\"");
            regfile.println("\"log_level\"=\"debug\"");
            regfile.println("\"worker_file\"=\"" + dubleSlash(new File(tomcatHome, WORKERS_CONFIG).toString()) +"\"");
            regfile.println("\"worker_mount_file\"=\"" + dubleSlash(new File(tomcatHome, URL_WORKERS_MAP_CONFIG).toString()) +"\"");

            
            uri_worker.println("###################################################################");		    
            uri_worker.println("# Auto generated configuration. Dated: " +  new Date());
            uri_worker.println("###################################################################");		    
            uri_worker.println();

            uri_worker.println("#");        
            uri_worker.println("# Default worker to be used through our mappings");
            uri_worker.println("#");        
            uri_worker.println("default.worker=ajp12");        
            uri_worker.println();
            
            uri_worker.println("#");                    
            uri_worker.println("# Root context mounts for Tomcat");
            uri_worker.println("#");        
		    uri_worker.println("/servlet/*=$(default.worker)");
		    uri_worker.println("/*.jsp=$(default.worker)");
            uri_worker.println();            


	        // Set up contexts
	        // XXX deal with Virtual host configuration !!!!
	        Enumeration enum = cm.getContexts();
	        while (enum.hasMoreElements()) {
		        Context context = (Context)enum.nextElement();
		        String path  = context.getPath();
		        String vhost = context.getHost();

		        if(vhost != null) {
		            // Vhosts are not supported yet for IIS
		            continue;
		        }
		        if(path.length() > 1) {
                    // Static files will be served by Apache
                    uri_worker.println("#########################################################");		    
                    uri_worker.println("# Auto configuration for the " + path + " context starts.");
                    uri_worker.println("#########################################################");		    
                    uri_worker.println();
            

                    uri_worker.println("#");		    
                    uri_worker.println("# The following line mounts all JSP file and the /servlet/ uri to tomcat");
                    uri_worker.println("#");                        
		            uri_worker.println(path +"/servlet/*=$(default.worker)");
		            uri_worker.println(path +"/*.jsp=$(default.worker)");
                    uri_worker.println();            

                    uri_worker.println("#");		    
                    uri_worker.println("# If you want tomcat to serve all the resources (including static) that");
                    uri_worker.println("# are part of the " + path + " context, uncomment the following line");
                    uri_worker.println("#");                        
		            uri_worker.println("# " + path +"/*=$(default.worker)");

                    uri_worker.println("#######################################################");		    
                    uri_worker.println("# Auto configuration for the " + path + " context ends.");
                    uri_worker.println("#######################################################");		    
                    uri_worker.println();
		        }
	        }

	        regfile.close();
	        uri_worker.close();
	        
	    } catch(Exception ex) {
	        loghelper.log("Error generating automatic IIS configuration", ex);
	    }
    }
    
    protected String dubleSlash(String in) 
    {
        StringBuffer sb = new StringBuffer();
        
        for(int i = 0 ; i < in.length() ; i++) {
            char ch = in.charAt(i);
            if('\\' == ch) {
                sb.append("\\\\");
            } else {
                sb.append(ch);
            }
        }
        
        return sb.toString();
    }
}