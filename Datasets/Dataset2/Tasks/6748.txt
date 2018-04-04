public static final int DEFAULT_MAP=4;

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


package org.apache.tomcat.core;

import org.apache.tomcat.context.*;
import org.apache.tomcat.util.*;
import java.io.*;
import java.net.*;
import java.util.*;
import javax.servlet.http.*;
import javax.servlet.*;

/**
 * A group of resources, with some common properties.
 * Container is similar with Apache "dir_conf" structue.
 *
 * In Servlet terminology there are many types of containers:
 * virtual host, context, prefix map, extension map, security
 * prefix and extension maps.
 * 
 * The most expensive operation is parsing the request and finding
 * the match. With ad-literam interpreation of the spec, we need to
 * parse at least 3 times: find context, find servlet, check security
 * constraints. There is no difference in those steps - except
 * the result of the mapping.
 *
 * Each Interceptor has the chance to alter the Container for a particular
 * map via addMapping() callback. It can set private informations as
 * attributes ( the Mapper or security interceptors will probably do so ).
 */
public class Container implements Cloneable {

    // The main difference between this container and Catalina
    // is that in Catalina, Container has an invoke() method.

    // The "controler"
    private ContextManager contextM;

    // The context including this container, if any
    Context context;

    // Location where this container is mapped
    String path;
    String proto;
    
    // Container attributes
    private Hashtable attributes = new Hashtable();

    // Interceptors. 
    private Vector contextInterceptors = new Vector();
    ContextInterceptor cInterceptors[];
    private Vector requestInterceptors = new Vector();
    RequestInterceptor rInterceptors[];
    
    // The handler
    ServletWrapper handler;

    public static final int UNKNOWN_MAP=0;
    public static final int PATH_MAP=1;
    public static final int PREFIX_MAP=2;
    public static final int EXTENSION_MAP=3;
    public static final int DEFAULT_MAP=3;
    int mapType=0;
    
    // XXX Per method constraints not implemented.
    String transport;
    String roles[]=null;
    
    public Container() {
    }
	
    public ContextManager getContextManager() {
	if( contextM==null ) {
	    if(context!=null) contextM=context.getContextManager();
	}
	return contextM;
    }

    public void setContextManager(ContextManager cm) {
	contextM=cm;
    }

    public int getMapType() {
	if( mapType!=0) return mapType;
	// What happens with "" or null ?
	// XXX Which one is default servlet ? API doesn't say,
	// but people expect it to work.
	if(path==null ||
	   path.equals("") ||
	   path.equals( "/") ||
	   path.equals("/*" ) ) {
	    mapType=DEFAULT_MAP;
	} else if (path.startsWith("/") &&
	    path.endsWith("/*")) {
	    mapType=PREFIX_MAP;
	} else if (path.startsWith("*.")) {
	    mapType=EXTENSION_MAP;
	} else {
	    mapType=PATH_MAP;
	}
	return mapType;
    }

    public void setContext( Context ctx ) {
	this.context=ctx;
    }

    public Context getContext() {
	return context;
    }
    
    /** The mapping string that creates this Container
     */
    public void setPath( String path ) {
	// XXX use a better name - setMapping for example
	if( path==null)
	    this.path=""; // default mapping
	else
	    this.path=path.trim();
    }

    public String getPath() {
	return path;
    }

    public void setProtocol( String protocol ) {
	this.proto=protocol;
    }

    public String getProtocol() {
	return proto;
    }
    
    public void addContextInterceptor( ContextInterceptor ci) {
	contextInterceptors.addElement( ci );
    }


    /** Return the context interceptors as an array.
	For performance reasons we use an array instead of
	returning the vector - the interceptors will not change at
	runtime and array access is faster and easier than vector
	access
    */
    public ContextInterceptor[] getContextInterceptors() {
	if( cInterceptors == null || cInterceptors.length != contextInterceptors.size()) {
	    cInterceptors=new ContextInterceptor[contextInterceptors.size()];
	    for( int i=0; i<cInterceptors.length; i++ ) {
		cInterceptors[i]=(ContextInterceptor)contextInterceptors.elementAt(i);
	    }
	}
	return cInterceptors;
    }

    public void addRequestInterceptor( RequestInterceptor ci) {
	requestInterceptors.addElement( ci );
    }

    /** Return the context interceptors as an array.
	For performance reasons we use an array instead of
	returning the vector - the interceptors will not change at
	runtime and array access is faster and easier than vector
	access
    */
    public RequestInterceptor[] getRequestInterceptors() {
	if( rInterceptors == null || rInterceptors.length != requestInterceptors.size()) {
	    rInterceptors=new RequestInterceptor[requestInterceptors.size()];
	    for( int i=0; i<rInterceptors.length; i++ ) {
		rInterceptors[i]=(RequestInterceptor)requestInterceptors.elementAt(i);
	    }
	}
	return rInterceptors;
    }

    public Object getAttribute(String name) {
            return attributes.get(name);
    }

    public Enumeration getAttributeNames() {
        return attributes.keys();
    }

    public void setAttribute(String name, Object object) {
        attributes.put(name, object);
    }

    public void removeAttribute(String name) {
        attributes.remove(name);
    }
    
    public ServletWrapper getHandler() {
        if (handler == null) handler=context.getDefaultServlet();
	return handler;
    }
    
    public void setHandler(ServletWrapper h) {
	handler=h;
    }

    public void setTransport(String transport ) {
	this.transport=transport;
    }

    public String getTransport() {
	return transport;
    }
    
    /** If not null, this container can only be accessed by users
	in roles.
    */
    public String []getRoles() {
	return roles;
    }

    /** If not null, this container can only be accessed by users
	in roles.
    */
    public void setRoles( String roles[] ) {
	this.roles=roles;
    }

    public String toString() {
	StringBuffer sb=new StringBuffer();
	sb.append( "Ct (" );
	if( handler!= null) sb.append( handler.toString() );
	if( roles!=null) {
	    	sb.append(" Roles: ");
		for( int i=0; i< roles.length; i++ )
		    sb.append(" ").append( roles[i]);
	}
	sb.append( " )");
	return sb.toString();
    }

    public Container getClone() {
	try {
	    return (Container)this.clone();
	} catch( CloneNotSupportedException ex ) {
	    return this;
	}
    }

    // -------------------- Per-Container "notes"
    Object notes[]=new Object[ContextManager.MAX_NOTES];

    public void setNote( int pos, Object value ) {
	notes[pos]=value;
    }

    public Object getNote( int pos ) {
	return notes[pos];
    }
}