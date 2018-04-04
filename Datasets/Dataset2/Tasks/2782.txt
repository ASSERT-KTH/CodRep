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
import java.io.*;
import java.net.*;
import java.util.*;
import java.security.*;

import org.apache.tomcat.util.log.*;

/**
 * Set policy-based access to tomcat.
 * Must be hooked before class loader setter.
 * The context will have a single protection domain, pointing to the doc root.
 *  That will include all classes loaded that belong to the context
 * ( jsps, WEB-INF/classes, WEB-INF/lib/
 *
 * @author  Glenn Nielsen 
 * @author costin@dnt.ro
 */
public class PolicyInterceptor extends PolicyLoader { //  BaseInterceptor {
    // PolicyLoader is used to load PolicyInterceptor
    String securityManagerClass="java.lang.SecurityManager";
    String policyFile=null;
    
    public PolicyInterceptor() {
    }

    public void setSecurityManagerClass(String cls) {
	securityManagerClass=cls;
    }

    public void setPolicyFile( String pf) {
	policyFile=pf;
    }

    public void addInterceptor(ContextManager cm, Context ctx,
			       BaseInterceptor module)
	throws TomcatException
    {
    }

    /** Set the security manager, so that policy will be used
     */
    public void engineInit(ContextManager cm) throws TomcatException {
	if( System.getSecurityManager() != null ) return;
	try {
	    if( null == System.getProperty("java.security.policy")) {
		File f=null;
		if( policyFile==null ) {
		    policyFile="conf/tomcat.policy";
		} 
		    
		if( FileUtil.isAbsolute(policyFile)) 
		    f=new File(policyFile);
		else
		    f=new File(cm.getHome() + File.separator +
			       policyFile);
		try {
		    policyFile=f.getCanonicalPath();
		} catch(IOException ex ) {}
		log("Setting policy file to " + policyFile);
		System.setProperty("java.security.policy",
				   policyFile);
		
	    }
	    Class c=Class.forName(securityManagerClass);
	    Object o=c.newInstance();
	    System.setSecurityManager((SecurityManager)o);
	    if (debug>0) log("Security Manager set to " +
		securityManagerClass, Logger.DEBUG);
	} catch( ClassNotFoundException ex ) {
	    log("SecurityManager Class not found: " +
			       securityManagerClass, Logger.ERROR);
	} catch( Exception ex ) {
            log("SecurityManager Class could not be loaded: " +
			       securityManagerClass, Logger.ERROR);
	}
    }

    
    /** Add a default set of permissions to the context
     */
    protected void addDefaultPermissions( Context context,String base,
					  Permissions p )
    {
	if( context.isTrusted() ) {
	    AllPermission aP=new AllPermission();
	    p.add( aP );
	    return;
	}

	// Add default read "-" FilePermission for docBase, classes, lib
	FilePermission fp = new FilePermission(base + File.separator + "-",
					       "read");
	p.add(fp);

	// Add default write "-" FilePermission for docBase 
	fp = new FilePermission(base + File.separator + "-",
				"write");
	p.add(fp);
	fp = new FilePermission(context.getWorkDir() + File.separator + "-",
				"read");
	p.add(fp);
	fp = new FilePermission(context.getWorkDir() + File.separator + "-",
				"write");
	p.add(fp);
	
	// JspFactory.getPageContext() runs in JSP Context and needs the below
	// permission during the init of a servlet generated from a JSP.
	PropertyPermission pp = new PropertyPermission("line.separator","read");
	if( pp != null )
	    p.add((Permission)pp);
	pp = new PropertyPermission("file.separator", "read");
	if( pp != null )
	    p.add((Permission)pp);
	pp = new PropertyPermission("path.separator", "read");
	if( pp != null )
	    p.add((Permission)pp);
    }
    
    public void contextInit( Context context)
	throws TomcatException
    {
	ContextManager cm = context.getContextManager();
	String base = context.getAbsolutePath();
	//	File wd = context.getWorkDir();
	    
	try {	
	    File dir = new File(base);
	    URL url = new URL("file:" + dir.getAbsolutePath());
	    CodeSource cs = new CodeSource(url,null);
	    
	    /* We'll construct permissions for Jasper. 
	       Tomcat uses normal policy and URLClassLoader.

	       We may add fancy config later, if needed
	     */
	    Permissions p = new Permissions();
	    
	    
	    // 	    // Add global permissions ( from context manager )
	    // 	    // XXX maybe use imply or something like that
	    // 	    Permissions perms = (Permissions)cm.getPermissions();
	    // 	    if( perms!= null ) {
	    // 		Enumeration enum=perms.elements();
	    // 		while(enum.hasMoreElements()) {
	    // 		    p.add((Permission)enum.nextElement());
	    // 		}
	    // 	    }
	    
	    addDefaultPermissions( context, dir.getAbsolutePath(), p);
	
	    /** Add whatever permissions are specified in the policy file
	     */
	    Policy.getPolicy().refresh();
	    PermissionCollection pFileP=Policy.getPolicy().getPermissions(cs);
	    if( pFileP!= null ) {
		Enumeration enum=pFileP.elements();
		while(enum.hasMoreElements()) {
		    p.add((Permission)enum.nextElement());
		}
	    }

	    // This is used only for Jasper ! Should be replaced by
	    // a standard URLClassLoader.
	    ProtectionDomain pd = new ProtectionDomain(cs,p);
	    // 	    context.setProtectionDomain(pd);

	    context.setAttribute( Context.ATTRIB_PROTECTION_DOMAIN,
				  pd);

	    // new permissions - added context manager and file to whatever was
	    // specified by default
	    //	    context.setPermissions( p );

	} catch(Exception ex) {
	    log("Security init for Context " + base + " failed", ex);
	}

    }
}