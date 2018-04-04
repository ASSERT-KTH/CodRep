import org.apache.tomcat.util.io.FileUtil;

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
 * Used by ContextManager to generate automatic Netscape configurations
 *
 * @author Gal Shachor shachor@il.ibm.com
 */
public class NSConfig  extends BaseInterceptor { 

    public static final String WORKERS_CONFIG = "/conf/jk/workers.properties";
    public static final String NS_CONFIG = "/conf/jk/obj.conf";
    public static final String JK_LOG_LOCATION = "/logs/netscape_redirect.log";

    Log loghelper = new Log("tc_log", this);
    
    public NSConfig() 
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

            PrintWriter objfile = new PrintWriter(new FileWriter(tomcatHome + NS_CONFIG + "-auto"));
           
            objfile.println("###################################################################");		    
            objfile.println("# Auto generated configuration. Dated: " +  new Date());
            objfile.println("###################################################################");		    
            objfile.println();

            objfile.println("#");        
            objfile.println("# You will need to merge the content of this file with your ");
            objfile.println("# regular obj.conf and then restart (=stop + start) your Netscape server. ");
            objfile.println("#");        
            objfile.println();
            
            objfile.println("#");                    
            objfile.println("# Loading the redirector into your server");
            objfile.println("#");        
            objfile.println();            
            objfile.println("Init fn=\"load-modules\" funcs=\"jk_init,jk_service\" shlib=\"<put full path to the redirector here>\"");
            objfile.println("Init fn=\"jk_init\" worker_file=\"" + 
                            new File(tomcatHome, WORKERS_CONFIG).toString().replace('\\', '/') +  
                            "\" log_level=\"debug\" log_file=\"" + 
                            new File(tomcatHome, JK_LOG_LOCATION).toString().replace('\\', '/') + 
                            "\"");
            objfile.println();
            
            objfile.println("<Object name=default>");            
            objfile.println("#");                    
            objfile.println("# Redirecting the root context requests to tomcat.");
            objfile.println("#");        
            objfile.println("NameTrans fn=\"assign-name\" from=\"/servlet/*\" name=\"servlet\""); 
            objfile.println("NameTrans fn=\"assign-name\" from=\"/*.jsp\" name=\"servlet\""); 
            objfile.println();

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
		            // Calculate the absolute path of the document base
		            String docBase = context.getDocBase();
		            if (!FileUtil.isAbsolute(docBase))
			        docBase = tomcatHome + "/" + docBase;
		            docBase = FileUtil.patch(docBase).replace('\\', '/');
		            
                    // Static files will be served by Apache
                    objfile.println("#########################################################");		    
                    objfile.println("# Auto configuration for the " + path + " context starts.");
                    objfile.println("#########################################################");		    
                    objfile.println();
            
                    objfile.println("#");		    
                    objfile.println("# The following line mounts all JSP file and the /servlet/ uri to tomcat");
                    objfile.println("#");                        
                    objfile.println("NameTrans fn=\"assign-name\" from=\"" + path + "/servlet/*\" name=\"servlet\""); 
                    objfile.println("NameTrans fn=\"assign-name\" from=\"" + path + "/*.jsp\" name=\"servlet\""); 
                    objfile.println("NameTrans fn=pfx2dir from=\"" + path + "\" dir=\"" + docBase + "\"");
                    objfile.println();            
                    objfile.println("#######################################################");		    
                    objfile.println("# Auto configuration for the " + path + " context ends.");
                    objfile.println("#######################################################");		    
                    objfile.println();
		        }
	        }

            objfile.println("#######################################################");		    
            objfile.println("# Protecting the web inf directory.");
            objfile.println("#######################################################");		    
            objfile.println("PathCheck fn=\"deny-existence\" path=\"*/WEB-INF/*\""); 
            objfile.println();
            
            objfile.println("</Object>");            
            objfile.println();
            
            
            objfile.println("#######################################################");		    
            objfile.println("# New object to execute your servlet requests.");
            objfile.println("#######################################################");		    
            objfile.println("<Object name=servlet>");
            objfile.println("ObjectType fn=force-type type=text/html");
            objfile.println("Service fn=\"jk_service\" worker=\"ajp12\" path=\"/*\"");
            objfile.println("</Object>");
            objfile.println();

	        
	        objfile.close();	        
	    } catch(Exception ex) {
	        loghelper.log("Error generating automatic Netscape configuration", ex);
	    }
    }    
}