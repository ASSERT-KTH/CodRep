//    implements ServletLoader

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
package org.apache.tomcat.loader;

import org.apache.tomcat.util.*;
import org.apache.tomcat.core.*;
import java.io.*;
import java.net.*;
import java.util.*;
import java.security.*;

// XXX extends ClassLoader is need only to allow access to protected loadClass
// method in ClassLoader. The alternative is to require a public method with
// the equivalent functionality

/**
 * @deprecated No longer needed.
 */
public class AdaptiveServletLoader  extends AdaptiveClassLoader
    implements ServletLoader
{
    AdaptiveClassLoader classL;
    static boolean jdk12=false;
    static {
	try {
	    Class.forName( "java.security.PrivilegedAction" );
	    jdk12=true;
	} catch(Throwable ex ) {
	}
    }
    Vector classP;
    ClassLoader parent;
    
    public AdaptiveServletLoader() {
	super(); // dumy -
	// this class will not be used as a class loader, it's just a trick for
	// protected loadClass()
	classP=new Vector();
    }

    public void setParentLoader( ClassLoader p ) {
	parent=p;
    }

    public ClassLoader getParentLoader() {
	if( true || parent==null ) return getClassLoader();
	return parent;
    }
    
    /** Check if we need to reload one particular class.
     *  No check is done for dependent classes.
     *  The final decision about reloading is left to the caller.
     */
    public boolean shouldReload( String className ) {
	if( classL==null )
	    getClassLoader();
	boolean should=classL.shouldReload(className);// check for _any_ change, including beans.
	//System.out.println("Should reload " + className + " = " + should);
	return should;
	// Very slow !!! (name)
    }

    
    /** Check if we need to reload. All loaded classes are
     *  checked.
     *  The final decision about reloading is left to the caller.
     */
    public boolean shouldReload() {
	if( classL==null )
	    getClassLoader();
	boolean should=classL.shouldReload();// check for _any_ change, including beans.
	//	System.out.println("Should reload  = " + should);
	return should;
	// Very slow !!! (name)
    }

    

    /** Reset the class loader. The caller should take all actions
     *  required by this step ( free resources for GC, etc)
     */
    public void reload() {
	if( classL==null )
	    getClassLoader();
	else
	    classL= classL.reinstantiate();
    }
		

    /** Return a real class loader
     */
    public ClassLoader getClassLoader() {
	if( classL!=null)
	    return classL;
	if( jdk12 ) {
	    try {
		Class ld=Class.forName("org.apache.tomcat.loader.AdaptiveClassLoader12");
		classL=(AdaptiveClassLoader)ld.newInstance();
	    } catch(Throwable t ) {
		t.printStackTrace();
	    }
	}

	if( classL==null ) {
	    // jdk1.1 or error
	    classL= new AdaptiveClassLoader();
	}
	classL.setParent( parent );
	classL.setRepository( classP );
	return classL;
    }

    
    /** Handle servlet loading. Same as getClassLoader().loadClass(name, true); 
     */
    public Class loadClass( String name)
	throws ClassNotFoundException
    {
	if( classL==null )
	    getClassLoader();
	return classL.loadClass( name, true );
    }


    /** Return the class loader view of the class path
     */
    public String getClassPath() {
        String separator = System.getProperty("path.separator", ":");
        String cpath = "";

        for(Enumeration e = classP.elements() ; e.hasMoreElements(); ) {
            ClassRepository cp = (ClassRepository) e.nextElement();
            File f = cp.getFile();
            if (cpath.length()>0) cpath += separator;
            cpath += f;
        }

        return cpath;
    }


    /** Add a new directory or jar to the class loader.
     *  Optionally, a SecurityManager ProtectionDomain can
     *  be specified for use by the ClassLoader when defining
     *  a class loaded from this entry in the repository.
     *  Not all loaders can add resources dynamically -
     *  that may require a reload.
     */
    public void addRepository( File f, Object pd ) {
	try {
            classP.addElement(
                new ClassRepository( new File(FileUtil.patch(f.getCanonicalPath())), pd )
                );
	} catch( IOException ex) {
            ex.printStackTrace();
	}
    }

    /** Add a new remote repository. Not all class loader will
     *  support remote resources, use File if it's a local resource.
     */
    public void addRepository( URL url ) {
	return;// no support for URLs in AdaptiveClassLoader
    }

    public String toString() {
	return "AdaptiveServletLoader( " + getClassPath()  + " ) using " + classL;
    }
    
}










