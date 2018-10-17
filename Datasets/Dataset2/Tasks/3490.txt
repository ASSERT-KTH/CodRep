import org.apache.tomcat.util.log.*;

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

package org.apache.jasper.servlet;

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
 * This is a class loader that loads JSP files as though they were
 * Java classes. It calls the compiler to compile the JSP file into a
 * servlet and then loads the generated class. 
 *
 * This code is quite fragile and needs careful
 * treatment/handling/revisiting. I know this doesn't work very well
 * right now for:  
 * 
 * 	(a) inner classes
 *	(b) does not work at all for tag handlers that have inner
 *          classes; but that is likely to change with the new JSP PR2
 *          spec. 
 *
 * @author Anil K. Vijendran
 * @author Harish Prabandham
 */
public class JasperLoader extends org.apache.jasper.runtime.JspLoader {
//     ClassLoader parent;
//     Options options;
    Object pd;

    /*
     * This should be factoried out
     */
    public JasperLoader() {
	super();
    }

//     public void setParentClassLoader( ClassLoader cl) 
//     {
// 	this.parent = cl;
//     }
    
//     public void setOptions( Options options) {
// 	this.options = options;
//     }

    public void setProtectionDomain( Object pd ) {
	this.pd=pd;
    }
    
    protected synchronized Class loadClass(String name, boolean resolve)
	throws ClassNotFoundException
    {
	if( debug>0) log("load " + name );
	// First, check if the class has already been loaded
	Class c = findLoadedClass(name);
	if (c == null) {
	    try {
		if (parent != null) {
		    if(debug>0) log("load from parent " + name );
		    c = parent.loadClass(name);
                }
		else {
		    if(debug>0) log("load from system " + name );
		    c = findSystemClass(name);
                }
	    } catch (ClassNotFoundException e) {
		// If still not found, then call findClass in order
		// to find the class.
		try {
		    if(debug>0) log("local jsp loading " + name );
		    c = findClass(name);
		} catch (ClassNotFoundException ex) {
		    throw ex;
		}
	    }
	}
	if (resolve) {
	    resolveClass(c);
	}
	return c;
    }
    public InputStream getResourceAsStream(String name) {
	if( debug>0) log("getResourcesAsStream()" + name );
	URL url = getResource(name);
	try {
	    return url != null ? url.openStream() : null;
	} catch (IOException e) {
	    return null;
	}
    }
    
    public URL getResource(String name) {
	if( debug>0) log( "getResource() " + name );
	if( parent != null )
	    return parent.getResource(name);
	return super.getResource(name);
    }

    private static final int debug=0;

    private void log( String s ) {
	System.out.println("JspLoader: " + s );
    }
    
    protected Class findClass(String className) throws ClassNotFoundException {
	try {
	    int beg = className.lastIndexOf(".") == -1 ? 0 :
		className.lastIndexOf(".")+1;
	    int end = className.lastIndexOf("_jsp_");

	    if (end <= 0) {     
                // this is a class that the JSP file depends on 
                // (example: class in a tag library)
                byte[] classBytes = loadClassDataFromJar(className);
                if (classBytes == null)
                    throw new ClassNotFoundException(className);
                return defClass(className, classBytes);
	    } else {
                String fileName = null;
                String outputDir = options.getScratchDir().toString();
            
                if (className.indexOf('$', end) != -1) {
                    // this means we're loading an inner class
                    fileName = outputDir + File.separatorChar + 
                        className.replace('.', File.separatorChar) + ".class";
                } else {
                    fileName = className.substring(beg, end) + ".class";
                    fileName = outputDir + File.separatorChar + fileName;
                }
                byte [] classBytes = null;
                /**
                 * When using a SecurityManager and a JSP page itself triggers
                 * another JSP due to an errorPage or from a jsp:include,
                 * the loadClass must be performed with the Permissions of
                 * this class using doPriviledged because the parent JSP
                 * may not have sufficient Permissions.
                 */
		classBytes = loadClassDataFromFile(fileName);
                if( classBytes == null ) {
                    throw new ClassNotFoundException(Constants.getString(
                                             "jsp.error.unable.loadclass", 
                                              new Object[] {className})); 
                }
                return defClass(className, classBytes);
            }
	} catch (Exception ex) {
            throw new ClassNotFoundException(Constants.getString(
	    				     "jsp.error.unable.loadclass", 
					      new Object[] {className}));
	}
    }

    /**
     * Just a short hand for defineClass now... I suspect we might need to
     * make this public at some point of time. 
     */
    protected  Class defClass(String className, byte[] classData) {
        return defineClass(className, classData, 0, classData.length);
    }

    /**
     * Load JSP class data from file, method may be called from
     * within a doPriviledged if a SecurityManager is installed.
     */
    protected byte[] loadClassDataFromFile(String fileName) {
	return doLoadClassDataFromFile( fileName );
    }

    /**
     * Load JSP class data from file, method may be called from
     * within a doPriviledged if a SecurityManager is installed.
     */
    protected byte[] doLoadClassDataFromFile(String fileName) {
        byte[] classBytes = null;
        try {
            FileInputStream fin = new FileInputStream(fileName);
            ByteArrayOutputStream baos = new ByteArrayOutputStream();
            byte buf[] = new byte[1024];
            for(int i = 0; (i = fin.read(buf)) != -1; )
                baos.write(buf, 0, i);
            fin.close();
            baos.close();
            classBytes = baos.toByteArray();
        } catch(Exception ex) {
            return null;
        }
        return classBytes;
    }

//     private Vector jars = new Vector();
    
    private byte[] loadClassDataFromJar(String className) {
        String entryName = className.replace('.','/')+".class";
	InputStream classStream = null;
	//System.out.println("Loading " + className);

        for(int i = 0; i < jars.size(); i++) {
            File thisFile = new File((String) jars.elementAt(i));
            try {
                //System.out.println(" - trying " + thisFile.getAbsolutePath());
                // check if it exists...
                if (!thisFile.exists()) {
                    continue; 
                };
                
                if (thisFile.isFile()) {
                    ZipFile zip = new ZipFile(thisFile);
                    ZipEntry entry = zip.getEntry(entryName);
                    if (entry != null) {
			classStream = zip.getInputStream(entry);
                        byte[] classData = getClassData(classStream);
			zip.close();
			return classData;
		    } else {
			zip.close();
		    }
                } else { // its a directory...
                    File classFile = 
                        new File(thisFile,
                                 entryName.replace('/', File.separatorChar));
                    if (classFile.exists()) {
                        classStream = new FileInputStream(classFile);
                        byte[] classData = getClassData(classStream);
                        classStream.close();
                        return classData;
                    }
                }
            } catch (IOException ioe) {
                return null;
            }
        }
        
        return null;
    }

    private byte[] getClassData(InputStream istream) throws IOException {
	byte[] buf = new byte[1024];
	ByteArrayOutputStream bout = new ByteArrayOutputStream();
	int num = 0;
	while((num = istream.read(buf)) != -1) {
	    bout.write(buf, 0, num);
	}

	return bout.toByteArray();
    }

    public String toString() {
	return "JspLoader( " +  options.getScratchDir()   + " ) / " + parent;
    }

    boolean loadJSP(JspServlet jspS, String name, String classpath, 
		    boolean isErrorPage, HttpServletRequest req,
		    HttpServletResponse res) 
	throws JasperException, FileNotFoundException 
    {
	return jspS.doLoadJSP( name, classpath, isErrorPage, req, res );
    }

}