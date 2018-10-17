URL baseURL = context.getDocumentBase();

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

/**
 * This class now extends NetworkClassLoader. Previous
 * implementation of ServletClassLoader was called ServletLoader.
 * This implementation is a complete rewrite of the earlier
 * class loader. This should speed up performance compared
 * to the earlier class loader.
 *
 * @author Harish Prabandham
 */
//
// WARNING: Some of the APIs in this class are used by J2EE. 
// Please talk to harishp@eng.sun.com before making any changes.
//
public class ServletClassLoaderImpl extends NetworkClassLoader implements ServletClassLoader {
    private Context  context;
    
    public ServletClassLoaderImpl(Context context) {
        super(context.getClassLoader());
	this.context = context;
        initURLs(); 
    }

    private void initURLs() {
        URL baseURL = context.getServletBase();
        String protocol = baseURL.getProtocol();
        int port = baseURL.getPort();
        String hostname = baseURL.getHost();
        
        String basepath = baseURL.getFile();

        // The classes directory...
        for(Enumeration e = context.getClassPaths();
            e.hasMoreElements(); ) {
            String cpath = (String) e.nextElement();
            try {
                URL classesURL = new URL(protocol,hostname,port,
                                         basepath + "/" + cpath + "/");
                addURL(classesURL);
            }catch(MalformedURLException mue) {
            }
        }

        // The jars in the lib directory...
        // This will not work if the URL is not a file URL.
        // An alternate way of figuring out the jar files should
        // be specified in the spec. Probably in the deployment
        // descriptor's web.xml ???
        for(Enumeration e = context.getLibPaths();
            e.hasMoreElements(); ) {
            String libpath = (String) e.nextElement();
            File f =  new File(basepath + "/" + libpath + "/");
            Vector jars = new Vector();
            getJars(jars, f);
            
            for(int i=0; i < jars.size(); ++i) {
                try {
                    String jarfile = (String) jars.elementAt(i);
                    URL jarURL = new URL(protocol,hostname,port,
                                         basepath + "/" + libpath + "/" + jarfile);
                    addURL(jarURL);
                }catch(MalformedURLException mue) {
                }
            }
        }
    }

    public synchronized Class loadServlet(ServletWrapper wrapper, String name)
        throws ClassNotFoundException {
	Class clazz = loadClass(name, true);
	// do whatever marking we need to do
	return clazz;
    }

    protected synchronized Class loadClass(String name, boolean resolve)
        throws ClassNotFoundException {
        // This is a bad idea. Unfortunately the class loader may
        // be set on the context at any point.
        setParent(context.getClassLoader());
        return super.loadClass(name, resolve);
    }

    public String getClassPath() {
        String separator = System.getProperty("path.separator", ":");
        String cpath = "";

        for(Enumeration e = getURLs(); e.hasMoreElements(); ) {
            URL url = (URL) e.nextElement();
            cpath = cpath + separator + url.getFile();
        }

        return cpath;
    }

    private void getJars(Vector v, File f) {
        FilenameFilter jarfilter = new JarFileFilter();
        FilenameFilter dirfilter = new DirectoryFilter();
        
        if(f.exists() && f.isDirectory() && f.isAbsolute()) {
            String[] jarlist = f.list(jarfilter);

            for(int i=0; (jarlist != null) && (i < jarlist.length); ++i) {
                v.addElement(jarlist[i]);
            }

            String[] dirlist = f.list(dirfilter);

            for(int i=0; (dirlist != null) && (i < dirlist.length); ++i) {
                File dir = new File(f, dirlist[i]);
                getJars(v, dir);
            }
        }
    }
}


class JarFileFilter implements FilenameFilter {

    public boolean accept(File dir, String fname) {
        if(fname.endsWith(".jar"))
            return true;

        return false;
    }
}

class DirectoryFilter implements FilenameFilter {

    public boolean accept(File dir, String fname) {
        File f = new File(dir, fname);
        if(f.isDirectory())
            return true;

        return false;
    }
}










