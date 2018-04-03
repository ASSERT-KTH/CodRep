final static int debug=0;

/*
 * Copyright (c) 1997-1999 The Java Apache Project.  All rights reserved.
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
 * 3. All advertising materials mentioning features or use of this
 *    software must display the following acknowledgment:
 *    "This product includes software developed by the Java Apache 
 *    Project for use in the Apache JServ servlet engine project
 *    <http://java.apache.org/>."
 *
 * 4. The names "Apache JServ", "Apache JServ Servlet Engine" and 
 *    "Java Apache Project" must not be used to endorse or promote products 
 *    derived from this software without prior written permission.
 *
 * 5. Products derived from this software may not be called "Apache JServ"
 *    nor may "Apache" nor "Apache JServ" appear in their names without 
 *    prior written permission of the Java Apache Project.
 *
 * 6. Redistributions of any form whatsoever must retain the following
 *    acknowledgment:
 *    "This product includes software developed by the Java Apache 
 *    Project for use in the Apache JServ servlet engine project
 *    <http://java.apache.org/>."
 *    
 * THIS SOFTWARE IS PROVIDED BY THE JAVA APACHE PROJECT "AS IS" AND ANY
 * EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 * PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE JAVA APACHE PROJECT OR
 * ITS CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
 * NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 * LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
 * HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
 * STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
 * OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 * This software consists of voluntary contributions made by many
 * individuals on behalf of the Java Apache Group. For more information
 * on the Java Apache Project and the Apache JServ Servlet Engine project,
 * please see <http://java.apache.org/>.
 *
 */

package org.apache.tomcat.util.depend;

import java.io.*;
import java.lang.*;
import java.net.*;
import java.text.*;
import java.util.*;
import java.util.zip.*;
import java.security.*;

import org.apache.tomcat.util.compat.*;

/**
 * This is a wrapper class loader that will delegate all calls to
 * the parent. It will also generate events for every loaded class,
 * for use in maintaining dependencies.
 *
 * In order to keep this generic we'll use findResource() to find the
 * source of the class, and then forward to the class loader - that
 * means we duplicate the search operation.
 * 
 * Class loading happens only once per request, and this will have probably
 * little effect.
 * Also, the alternative is to use custom class loaders - there are many
 * reasons to avoid this.
 *
 * In "production" sites reloading should be turned off anyway, so the
 * class loader will not be "wrapped"
 * 
 */
public class DependClassLoader extends ClassLoader {
    protected ClassLoader parent;
    protected ClassLoader parent2;
    
    final static int debug=10;
    DependManager dependM;
    protected Object pd;
    static Jdk11Compat jdkCompat=Jdk11Compat.getJdkCompat();

    public static DependClassLoader getDependClassLoader( DependManager depM,
							  ClassLoader parent,
							  Object pd ) {
	if( jdkCompat.isJava2() ) {
	    try {
		Class c=Class.forName( "org.apache.tomcat.util.depend.DependClassLoader12");
		DependClassLoader dcl=(DependClassLoader)c.newInstance();
		dcl.init( depM, parent, pd );
		return dcl;
	    } catch(Exception ex ) {
		ex.printStackTrace();
	    }
	} 
	return new DependClassLoader( depM, parent, pd );
    }

    DependClassLoader() {
    }
    
    public DependClassLoader( DependManager depM, ClassLoader parent, Object pd ) {
	super(); // will check permissions
	init( depM, parent, pd );
    }

    void init(  DependManager depM, ClassLoader parent, Object pd ) {
	this.parent=parent;
	this.parent2=jdkCompat.getParentLoader( parent );
	dependM=depM;
	this.pd=pd;
    }

    // debug only
    final void log( String s ) {
	System.out.println("DependClassLoader: " + s );
    }

    /**
     * Resolves the specified name to a Class. The method loadClass()
     * is called by the virtual machine.  As an abstract method,
     * loadClass() must be defined in a subclass of ClassLoader.
     *
     * @param      name the name of the desired Class.
     * @param      resolve true if the Class needs to be resolved;
     *             false if the virtual machine just wants to determine
     *             whether the class exists or not
     * @return     the resulting Class.
     * @exception  ClassNotFoundException  if the class loader cannot
     *             find a the requested class.
     */
    protected synchronized Class loadClass(String name, boolean resolve)
        throws ClassNotFoundException
    {
	return loadClassInternal( name, resolve );
    }

    protected Class loadClassInternal( String name, boolean resolve )
	throws ClassNotFoundException
    {
	if( debug>0) log( "loadClass() " + name + " " + resolve);
	// The class object that will be returned.
        Class c = null;

	// check if  we already loaded this class
	c = findLoadedClass( name );
	if (c!= null ) {
	    if(resolve) resolveClass(c);
	    return c;
        }

        String classFileName = name.replace('.', '/' ) + ".class";

	URL res=getResource( classFileName );

	// If it's in parent2, load it ( we'll not track sub-dependencies ).
	try {
	    c = parent2.loadClass(name);
	    if (c != null) {
		if (resolve) resolveClass(c);
		// No need, we can't reload anyway
		// dependency( c, res );
		return c;
	    }
	} catch (Exception e) {
	    c = null;
	}

	if( res==null ) 
	    throw new ClassNotFoundException(name);

	// This should work - SimpleClassLoader should be able to get
	// resources from jar files. 
	InputStream is=getResourceAsStream( classFileName );
	if( is==null ) 
	    throw new ClassNotFoundException(name);


	// It's in our parent. Our task is to track all class loads, the parent
	// should load anything ( otherwise the deps are lost ), but just resolve
	// resources.
	byte data[]=null;
	try {
	    data=readFully( is );
	    if( data.length==0 ) data=null;
	} catch(IOException ex ) {
	    if( debug > 0 ) ex.printStackTrace();
	    data=null;
	    throw new ClassNotFoundException( name + " error reading " + ex.toString());
	}
	if( data==null ) 
	    throw new ClassNotFoundException( name + " lenght==0");

	c=defineClassCompat( name, data, 0, data.length, res );
	dependency( c, res );
	
	if (resolve) resolveClass(c);

	return c;
    }

    protected Class defineClassCompat( String name, byte data[], int s, int end, URL res )
	throws ClassNotFoundException
    {
	return defineClass(data, s, end);
    }
    
    public URL getResource(String name) {
	return parent.getResource(name);
    }

    public InputStream getResourceAsStream(String name) {
	return parent.getResourceAsStream( name );
    }

    private void dependency( Class c, URL res ) {
	if( res==null) return;
	File f=null;
	if( "file".equals( res.getProtocol() )) {
	    f=new File( res.getFile());
	    if( debug > 0 ) log( "File dep "  +f );
	    if( ! f.exists()) f=null;
	}
	if( "jar".equals( res.getProtocol() )) {
	    String fileN=res.getFile();
	    int idx=fileN.indexOf( "!" );
	    if( idx>=0 )
		fileN=fileN.substring( 0, idx) ;
	    // Bojan Smojver <bojan@binarix.com>: remove jar:
	    if( fileN.startsWith( "jar:" ))
		fileN=fileN.substring( 4 );
	    f=new File(fileN);
	    if( debug > 0 ) log( "Jar dep "  +f + " " + f.exists() );
	    if( ! f.exists()) f=null;
	}

	if( f==null ) return;
	Dependency dep=new Dependency();
	dep.setLastModified( f.lastModified() );
	dep.setTarget( c );
	dep.setOrigin( f );

	dependM.addDependency( dep );
    }

    public ClassLoader getParentLoader() {
        return parent;
    }

    private byte[] readFully( InputStream is )
	throws IOException
    {
	byte b[]=new byte[1024];
	int count=0;

	int available=1024;
	
	while (true) {
	    int nRead = is.read(b,count,available);
	    if( nRead== -1 ) {
		// we're done reading
		byte result[]=new byte[count];
		System.arraycopy( b, 0, result, 0, count );
		return result;
	    }
	    // got a chunk
	    count += nRead;
            available -= nRead;
	    if( available == 0 ) {
		// buffer full
		byte b1[]=new byte[ b.length * 2 ];
		available=b.length;
		System.arraycopy( b, 0, b1, 0, b.length );
		b=b1;
	    }
        }
    }
}