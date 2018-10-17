zf.close();

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
package org.apache.tomcat.util.compat;

import java.io.*;
import java.lang.*;
import java.net.*;
import java.text.*;
import java.util.*;
import java.util.zip.*;
import java.security.*;

/**
 * This is a JDK1.1 equivalent of URLClassLoader. It have no dependency on
 * tomcat or any other api - just standard java. 
 *
 * Based on AdaptiveClassLoader from JServ1, with the dependency check
 * and reloading features removed ( and moved to an external component)
 *  This is based on the fact that class loading and dependency checking can
 * be separated and we want to support multiple forms of class loaders.
 *
 * The interface also changed to match URLClassLoader. 
 * This class should be used _only_ with JDK1.1, for JDK1.2 you
 * should use a class loader that is aware of Permissions and the
 * new rules ( sealing, etc )
 *
 * This class loader respects the standard order defined in the ClassLoader
 * documentation - for a different order you can plug in a different
 * class loader ( in the configurations ).
 *
 * Since this class loader will be visible to applications we need
 * to prevent exploits - we'll minimize the public method usage.
 * 
 * The class path can be set only when the object is constructed.
 */
public class SimpleClassLoader extends ClassLoader {
    private static final int debug=0;
    
    /**
     * The classpath which this classloader searches for class definitions.
     * Each element of the vector should be either a directory, a .zip
     * file, or a .jar file.
     * <p>
     * It may be empty when only system classes are controlled.
     */
    protected URL urls[];

    /**
     * A parent class loader for delegation of finding a class definition.
     * JDK 1.2 contains parent class loaders as part of java.lang.ClassLoader,
     * the parent being passed to a constructor, and retreived with
     * getParent() method. For JDK 1.1 compatibility, we'll duplicate the
     * 1.2 private member var.
     */
    protected ClassLoader parent;

    /** Reserved names - this class loader will not allow creation of
	classes that start with one of those strings.
    */
    protected String reserved[];

    SecurityManager sm;
    //------------------------------------------------------- Constructors

    public SimpleClassLoader( URL urls[]) {
	super(); // will check permissions 
	this.urls=urls;
	sm=System.getSecurityManager();
	checkURLs();
    }

    public SimpleClassLoader( URL urls[], ClassLoader parent ) {
	super(); // will check permissions 
	this.urls=urls;
	this.parent=parent;
	sm=System.getSecurityManager();
	checkURLs();
    }

    /** This is the prefered constructor to be used with this class loader
     */
    public SimpleClassLoader( URL urls[], ClassLoader parent,
				 String reserved[] ) {
	super(); // will check permissions 
	this.urls=urls;
	this.parent=parent;
	this.reserved=reserved;
	sm=System.getSecurityManager();
	checkURLs();
    }

    /** We can't declare a method "getParent" since it'll not compile in
	JDK1.2 - the method is final. But we don't have to - this will
	be used via JdkCompat
    */
    public ClassLoader getParentLoader() {
	return parent;
    }

    private void checkURLs() {
	int cnt=0;
	for( int i=0; i<urls.length; i++ ) {
	    URL cp = urls[i];
            String fileN = cp.getFile();
	    File file=new File( fileN );
	    if( ! file.exists() )
		urls[i]=null;
	    if( file.isDirectory() &&
		! fileN.endsWith("/") ) {
		try {
		    urls[i]=new URL("file", null,
				    fileN + "/" );
		} catch(MalformedURLException e ) {
		}
	    }
	}
    }
    
    // debug only 
    void log( String s ) {
	System.out.println("SimpleClassLoader: " + s );
    }

    //------------------------------------ Implementation of Classloader

    /*
     * XXX: The javadoc for java.lang.ClassLoader says that the
     * ClassLoader should cache classes so that it can handle repeated
     * requests for the same class.  On the other hand, the JLS seems
     * to imply that each classloader is only asked to load each class
     * once.  Is this a contradiction?
     *
     * Perhaps the second call only applies to classes which have been
     * garbage-collected?
     */

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
        if( debug>0) log( "loadClass() " + name + " " + resolve);
	// The class object that will be returned.
        Class c = null;

	// check if the class was already loaded
	c = findLoadedClass( name );
	if (c!= null ) {
	    if(resolve) resolveClass(c);
	    return c;
        }

	// Attempt to load the class from the parent class loader
	// (untrusted case)
	if (parent != null) {
	    try {
		c = parent.loadClass(name);
		if (c != null) {
		    if( debug>0) log( "loadClass() from parent " + name);
		    if (resolve) resolveClass(c);
		    return c;
		}
	    } catch (Exception e) {
		c = null;
	    }
	}

        // Attempt to load the class from the system class loader
	try {
	    c = findSystemClass(name);
	    if (c != null) {
		if( debug>0) log( "loadClass() from system " + name);
		if (resolve) resolveClass(c);
		return c;
	    }
	} catch (Exception e) {
	    c = null;
	}
	
        // Make sure we can access this class when using a SecurityManager
        if (sm != null) {
            int i = name.lastIndexOf('.');
            if (i >= 0) {
                sm.checkPackageAccess(name.substring(0,i)); 
                sm.checkPackageDefinition(name.substring(0,i));
	    }
	}

	// make sure the class is not in a "reserved" package.
	if( reserved!=null ) {
	    for( int i=0; i<reserved.length; i++ ) {
		if( name.startsWith( reserved[i] )) {
		    if( debug>0) log( "reserved: " + name + " " + reserved[i]);
		    throw new ClassNotFoundException(name);
		}
	    }
	}

	if( urls==null ) 
	    throw new ClassNotFoundException(name);
	
        // Translate class name to file name
        String classFileName =
            name.replace('.', '/') + ".class";
	// It's '/' not File.Separator - at least that's how URLClassLoader
	// does it and I suppose there are reasons ( costin )


	Resource r=doFindResource( classFileName );
	if( r==null )
	    throw new ClassNotFoundException(name);

	byte[] classData=null;

	if( r.file != null ) {
	    InputStream in=null;
            try {
		in = new FileInputStream(r.file);
                classData=loadBytesFromStream(in, (int) r.file.length());
            } catch (IOException ioex) {
                return null;
            } finally {
                try {
		    if( in!=null) in.close();
		} catch( IOException ex ) {}
            }
	} else if( r.zipEntry != null ) {
	    try {
                classData=loadBytesFromStream(r.zipFile.
					      getInputStream(r.zipEntry),
					      (int)r.zipEntry.getSize());
            } catch (IOException ioex) {
                return null;
	    } finally {
		try {
		    r.zipFile.close();
		} catch ( IOException ignored ) {
		}
	    }
	}

	if (classData != null) {
	    try {
		c = defineClass(name, classData, 0, classData.length );
		if (resolve) resolveClass(c);
		if( debug>0) log( "loadClass() from local repository " +
				  name);
		return c;
	    } catch(Throwable t ) {
		t.printStackTrace();
	    }
	}

        // If not found in any repository
        throw new ClassNotFoundException(name);
    }

    /**
     * Find a resource with a given name.  The return is a URL to the
     * resource. Doing a getContent() on the URL may return an Image,
     * an AudioClip,or an InputStream.
     *
     * @param   name    the name of the resource, to be used as is.
     * @return  an URL on the resource, or null if not found.
     */
    public URL getResource(String name) {
        if( debug > 0 ) log( "getResource() " + name );

	URL u = getSystemResource(name);
	if (u != null) {
	    return u;
	}

	Resource r=doFindResource( name );

	if( r==null )
	    return null;

	// Construct a file://-URL if the repository is a directory
	if( r.file != null ) { // Build a file:// URL form the file name
	    try {
		return new URL("file", null,
			       r.file.getAbsolutePath());
	    } catch(java.net.MalformedURLException badurl) {
		badurl.printStackTrace();
		return null;
	    }
	}

	// a jar:-URL *could* change even between minor releases, but
	// didn't between JVM's 1.1.6 and 1.3beta. Tested on JVM's from
	// IBM, Blackdown, Microsoft, Sun @ Windows and Sun @ Solaris
	if( r.zipEntry != null ) {
	    try {
		return new URL("jar:file:" +
			       r.repository.getPath() + "!/" +
			       name);
	    } catch(java.net.MalformedURLException badurl) {
		badurl.printStackTrace();
		return null;
	    } finally {
		try {
		    r.zipFile.close();
		} catch ( IOException ignored ) {
		}
	    }
	}
	// Not found
        return null;

    }

    /**
     * Get an InputStream on a given resource.  Will return null if no
     * resource with this name is found.
     * <p>
     * The JServClassLoader translate the resource's name to a file
     * or a zip entry. It looks for the resource in all its repository
     * entry.
     *
     * @see     java.lang.Class#getResourceAsStream(String)
     * @param   name    the name of the resource, to be used as is.
     * @return  an InputStream on the resource, or null if not found.
     */
    public InputStream getResourceAsStream(String name) {
        // Try to load it from the system class
        if( debug > 0 ) log( "getResourceAsStream() " + name );
	//	InputStream s = getSystemResourceAsStream(name);
	InputStream s = null;

	// Get this resource from system class loader 
	s = getSystemResourceAsStream(name);

        if( debug>0 ) log( "System resource " + s );
	if (s != null) {
	    return s;
	}
		
	Resource r=doFindResource( name );

	if( r==null ) return null;
	
	if( r.file!=null ) {
	    if( debug > 0 ) log( "Found "  + r.file);
	    try {
                InputStream res=new FileInputStream(r.file);
		return res;
            } catch (IOException shouldnothappen) {
		shouldnothappen.printStackTrace();
		return null;
            }
	} else if( r.zipEntry != null ) {
	    if( debug > 0 ) log( "Found "  + r.zipEntry);
	    // workaround - the better solution is to not close the
	    // zipfile !!!!
	    try {
		byte[] data= loadBytesFromStream(r.zipFile.
						 getInputStream(r.zipEntry),
						 (int) r.zipEntry.getSize());
		if(data != null) {
		    InputStream istream = new ByteArrayInputStream(data);
		    return istream;
		}
	    } catch(IOException e) {
	    } finally {
	    // if we close the zipfile bad things will happen -
		// we can't read the stream on some VMs
		if ( r.zipFile != null ) {
		    try {
			r.zipFile.close();
		    } catch ( IOException ignored ) {
		    }
		}
	    }
	}
        return s;
    }

    // -------------------- Private methods --------------------
    /** Private class used to store the result of the search 
     */
    private class Resource {
	/* Repository used to find the resource */
	File repository;
	/* File - if the resource is a file */
	File file;

	/* Zip file and entry if it's in a jar */
	ZipEntry zipEntry;
	ZipFile zipFile;
    }

    // common code to find the resource
    private Resource doFindResource( String name ) {
	Resource r=new Resource();
	
	for( int i=0; i<urls.length; i++ ) {
	    URL cp = urls[i];
	    if( cp==null ) continue;
            String fileN = cp.getFile();
	    File file=new File( fileN );
	    
	    if (fileN.endsWith("/")) {
                String fileName = name.replace('/', File.separatorChar);
                File resFile = new File(file, fileName);
                if (resFile.exists()) {
		    r.file=resFile;
		    r.repository=file;
		    return r;
                }
            } else {
                try {
                    ZipFile zf = new ZipFile(file.getAbsolutePath());
                    ZipEntry ze = zf.getEntry(name);
		    //if( debug > 0 ) log( "Searching " + file + " " + name );
					
                    if (ze != null) {
			r.zipEntry=ze;
			r.zipFile=zf;
			r.repository=file;
			return r;
                    }
                } catch (IOException ioe) {
                    ioe.printStackTrace();
		    System.out.println("Name= " + name + " " + file );
                    return null;
                }
            }   
        }
	return null;
    }
    
    /**
     * Loads all the bytes of an InputStream.
     */
    private byte[] loadBytesFromStream(InputStream in, int length)
        throws IOException
    {
        byte[] buf = new byte[length];
        int nRead, count = 0;

        while ((length > 0) && ((nRead = in.read(buf,count,length)) != -1)) {
            count += nRead;
            length -= nRead;
        }
        return buf;
    }

    public URL[] getURLs() {
        //TODO:  Add custom implementation.
        return urls;
    }

}