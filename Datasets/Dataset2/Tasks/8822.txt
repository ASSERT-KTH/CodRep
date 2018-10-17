//	System.out.println("JspLoader12: " + className + " " + pd );

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
 */ 

package org.apache.jasper.runtime;

import java.io.FileInputStream;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.InputStream;
import java.io.IOException;

import java.util.Hashtable;
import java.util.Vector;
import java.util.zip.ZipFile;
import java.util.zip.ZipEntry;
import java.net.URL;

import java.security.*;

import org.apache.jasper.JasperException;
import org.apache.jasper.Constants;
import org.apache.jasper.JspCompilationContext;
import org.apache.jasper.JspEngineContext;
import org.apache.jasper.Options;
import org.apache.jasper.compiler.Compiler;

import org.apache.tomcat.logging.Logger;
import javax.servlet.http.*;
/**
 * 1.2 version of the JspLoader
 * 
 * @author Anil K. Vijendran
 * @author Harish Prabandham
 * @author Costin Manolache 
 */
public class JspLoader12 extends JspLoader {

    JspLoader12()
    {
	super();
    }

    /**
     */
    protected  Class defClass(String className, byte[] classData) {
        // If a SecurityManager is being used, set the ProtectionDomain
        // for this clas when it is defined.
        Object pd = options.getProtectionDomain();
        if( pd != null ) {
	    return defineClass(className, classData, 0,
			       classData.length,
			       (ProtectionDomain)pd);
	}
        return defineClass(className, classData, 0, classData.length);
    }

    protected byte[] loadClassDataFromFile( String fileName ) {
	/**
	 * When using a SecurityManager and a JSP page itself triggers
	 * another JSP due to an errorPage or from a jsp:include,
	 * the loadClass must be performed with the Permissions of
	 * this class using doPriviledged because the parent JSP
	 * may not have sufficient Permissions.
	 */
	if( System.getSecurityManager() != null ) {
	    class doInit implements PrivilegedAction {
		private String fileName;
		public doInit(String file) {
		    fileName = file;
		}
		public Object run() {
		    return doLoadClassDataFromFile(fileName);
		}
	    }
	    doInit di = new doInit(fileName);
	    return (byte [])AccessController.doPrivileged(di);
	} else {
	    return doLoadClassDataFromFile( fileName );
	}
    }

    // Hack - we want to keep JDK1.2 dependencies in fewer places,
    // and same for doPriviledged.
    boolean loadJSP(JspServlet jspS, String name, String classpath, 
		    boolean isErrorPage, HttpServletRequest req,
		    HttpServletResponse res) 
	throws JasperException, FileNotFoundException 
    {
        if( System.getSecurityManager() == null ) {
	    return jspS.doLoadJSP( name, classpath, isErrorPage, req, res );
	}

	final JspServlet jspServlet=jspS;
	final String nameF=name;
	final String classpathF=classpath;
	final boolean isErrorPageF=isErrorPage;
	final HttpServletRequest reqF=req;
	final HttpServletResponse resF=res;
	try {
	    Boolean b = (Boolean)AccessController.doPrivileged(new
		PrivilegedExceptionAction() {
		    public Object run() throws Exception
		    {
			return new Boolean(jspServlet.doLoadJSP( nameF,
								 classpathF,
								 isErrorPageF,
								 reqF, resF ));
		    } 
		});
	    return b.booleanValue();
	} catch( Exception ex ) {
	    if( ex instanceof JasperException )
		throw (JasperException)ex;
	    if( ex instanceof FileNotFoundException )
		throw (FileNotFoundException) ex;
	    throw new JasperException( ex );
	}
    }

}