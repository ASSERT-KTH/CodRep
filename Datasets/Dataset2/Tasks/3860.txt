import org.apache.tomcat.util.hooks.Hooks;

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

import org.apache.tomcat.util.hooks.*;
import java.util.Hashtable;
import java.util.Enumeration;

// XXX better names: Location, URLPattern,  

/**
 * A group of resources, with some common properties.
 * Container is similar with Apache "dir_conf" structue.
 *
 * Each Context has a default Container and one container for
 * each URL property ( mapping handlers and  security constraints ).
 *
 * The ContextManager has a defaultContainer containing global
 * properties.
 *
 * Each time a container is added to a Context, addContainer() hook is
 * called to notify all modules of a new URL property.
 *
 * Modules that implement contextMap/requestMap and security constraints
 * ( authenticate/authorize hooks ) will construct specialized data
 * structures. 
 * You can associate trees, hashtables or other data types with the
 * context using notes - no application/module should assume any
 * particular structure is in used, the user can choose any mapper.
 * See SimpleMapper1 for an example of such structures.
 *
 * A container will be selected by best-matching a request using the
 * alghoritms described in the servlet API. 
 */
public class Container implements Cloneable{
    /* It is not yet finalized - it is possible to use more
     * "rules" for matching ( if future APIs will define that ).
     * You can use notes or attributes to extend the model -
     * the attributes that are defined and have get/set methods
     * are the one defined in the API and with wide use.
     */

    // The "controler"
    private ContextManager contextM;

    // The webapp including this container, if any
    Context context;

    // The type of the mapping
    public static final int UNKNOWN_MAP=0;
    public static final int PATH_MAP=1;
    public static final int PREFIX_MAP=2;
    public static final int EXTENSION_MAP=3;
    public static final int DEFAULT_MAP=4;
    int mapType=0;


    // Common map parameters ( path prefix, ext, etc)
    String transport;
    String path;
    String proto;
    String vhosts[];

    // Container attributes - it's better to use
    // notes, as the access time is much smaller
    private Hashtable attributes = new Hashtable();

    /** The handler associated with this container.
     */
    Handler handler;
    String handlerName;
    
    /** Security constraints associated with this Container
     */
    String roles[]=null;

    String methods[]=null;
    
    public Container() {
	initHooks();
    }

    /** Get the context manager
     */
    public ContextManager getContextManager() {
	if( contextM==null && context==null ) {
	    /* assert */
	    throw new RuntimeException( "Assert: container.contextM==null" );
	}
	if( contextM==null )
	    contextM=context.getContextManager();
	return contextM;
    }

    public void setContextManager(ContextManager cm) {
	contextM=cm;
    }

    /** Set the context, if this container is part of a web application.
     *  Right now all container in use have a context.
     */
    public void setContext( Context ctx ) {
	this.context=ctx;
    }

    /** The parent web application, if any. 
     */
    public Context getContext() {
	return context;
    }
    
    // -------------------- Mapping LHS --------------------
       
    
    /** Return the type of the mapping ( extension, prefix, default, etc)
     */
    public int getMapType() {
	if( mapType!=0) return mapType;
	// What happens with "" or null ?
	// XXX Which one is default servlet ? API doesn't say,
	// but people expect it to work.
	if( path==null ||
	    path.equals("" ) ||
	    path.equals( "/")) {
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

    /** The mapping string that creates this Container.
     *  Not that this is an un-parsed string, like a regexp.
     */
    public void setPath( String path ) {
	// XXX use a better name - setMapping for example
	if( path==null)
	    this.path=""; // default mapping
	else
	    this.path=path.trim();
    }

    /** Return the path
     */
    public String getPath() {
	return path;
    }

    /** Set the protocol - if it's set it will be used
     *  in mapping
     */
    public void setProtocol( String protocol ) {
	this.proto=protocol;
    }

    /** Protocol matching. With Servlet 2.2 the protocol
     * can be used only with security mappings, not with
     * handler ( servlet ) maps
    */
    public String getProtocol() {
	return proto;
    }

    /** The transport - another component of the matching.
     *  Defined only for security mappings.
     */
    public void setTransport(String transport ) {
	this.transport=transport;
    }

    /** The transport - another component of the matching.
     *  Defined only for security mappings.
     */
    public String getTransport() {
	return transport;
    }

    /** Any alias that can match a particular vhost
     */
    public String[] getVhosts() {
	return vhosts;
    }

    /** Any alias that can match a particular vhost
     */
    public void setVhosts(String vhosts[]) {
	this.vhosts=vhosts;
    }
    
    /** If not null, this container can only be accessed by users
     *  in roles.
     */
    public String []getMethods() {
	return methods;
    }

    /** If not null, this container can only be accessed by users
	in roles.
    */
    public void setMethods( String m[] ) {
	this.methods=m;
    }

    // -------------------- Mapping RHS --------------------
    
    public Handler getHandler() {
	return handler;
    }

    /** The handler ( servlet ) for this container
     */
    public void setHandler(Handler h) {
	handler=h;
    }

    public void setHandlerName(String hn) {
	handlerName=hn;
    }

    /** The handler name for this container.
     *  @return null if no handler is defined for this
     *          container ( this container defines only
     *          security or other type of properties, but
     *          not a handler )
     */
    public String getHandlerName() {
	if( handlerName != null ) 
	    return handlerName;
	if( handler != null )
	    return handler.getName();
	return null;
    }

    /** If not null, this container can only be accessed by users
     *  in roles.
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

    /** Per container attributes. Not used - can be removed
     *  ( it's here for analogy with the other components )
     */
    public Object getAttribute(String name) {
            return attributes.get(name);
    }

    /** Per container attributes. Not used - can be removed
     *  ( it's here for analogy with the other components )
     */
    public Enumeration getAttributeNames() {
        return attributes.keys();
    }

    /** Per container attributes. Not used - can be removed
     *  ( it's here for analogy with the other components )
     */
    public void setAttribute(String name, Object object) {
        attributes.put(name, object);
    }

    /** Per container attributes. Not used - can be removed
     *  ( it's here for analogy with the other components )
     */
    public void removeAttribute(String name) {
        attributes.remove(name);
    }

    // -------------------- Utils --------------------
    /** Print a short string describing the mapping
     */
    public String toString() {
	StringBuffer sb=new StringBuffer();
	sb.append( "Ct (" );
	sb.append(path ).append( " " );
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

    /** See ContextManager comments.
     */
    public void setNote( int pos, Object value ) {
	notes[pos]=value;
    }

    public Object getNote( int pos ) {
	return notes[pos];
    }

    // -------------------- Interceptors --------------------
    public static final int H_requestMap=0;
    public static final int H_contextMap=1;
    public static final int H_authenticate=2;
    public static final int H_authorize=3;
    public static final int H_preService=4;
    public static final int H_beforeBody=5;
    public static final int H_findSession=6;
    public static final int H_sessionState=7;
    public static final int H_beforeCommit=8;
    public static final int H_afterBody=9;
    public static final int H_postService=10;
    public static final int H_postRequest=11;
    public static final int H_handleError=12;
    public static final int H_engineInit=13;
    public static final int H_COUNT=14;

    Hooks hooks=new Hooks();
    BaseInterceptor hooksCache[][]=null;
    BaseInterceptor allHooksCache[]=null;

    private void initHooks() {
	hooks.registerHook( "requestMap", H_requestMap );
	hooks.registerHook( "contextMap", H_contextMap );
	hooks.registerHook( "authenticate", H_authenticate );
	hooks.registerHook( "authorize", H_authorize );
	hooks.registerHook( "preService", H_preService );
	hooks.registerHook( "beforeBody", H_beforeBody );
	hooks.registerHook( "findSession", H_findSession );
	hooks.registerHook( "sessionState", H_sessionState );
	hooks.registerHook( "beforeCommit", H_beforeCommit );
	hooks.registerHook( "afterBody", H_afterBody );
	hooks.registerHook( "postService", H_postService );
	hooks.registerHook( "postRequest", H_postRequest );
	hooks.registerHook( "handleError", H_handleError );
	hooks.registerHook( "engineInit", H_engineInit );
    }

    public Hooks getHooks() {
	return hooks;
    }

    /** Add the interceptor to all the hook chains it's interested
     *	in
     */
    public void addInterceptor( BaseInterceptor bi ) {
	bi.setContext( getContext() );

	if( Hooks.hasHook( bi, "registerHooks" ) ) {
	    bi.registerHooks( hooks, contextM, context );
	} else {
	    hooks.addModule( bi );
	}
	hooksCache=null;
	allHooksCache=null;
    }

    public void removeInterceptor( BaseInterceptor bi ) {
	hooks.removeModule( bi );
	hooksCache=null;
	allHooksCache=null;
    }
    
    public BaseInterceptor[] getInterceptors( int type )
    {
	if( hooksCache != null ) {
	    return hooksCache[type];
	}

	// load the cache with all the hooks
	Container globalIntContainer=getContextManager().getContainer();
	Hooks globals=globalIntContainer.getHooks();

	hooksCache=new BaseInterceptor[H_COUNT][];
	for( int i=0; i<H_COUNT; i++ ) {
	    Hooks locals=null;
	    if( this != globalIntContainer ) {
		hooksCache[i]=mergeHooks( globals.getModules(i),
					  getHooks().getModules(i));
	    } else {
		hooksCache[i]=mergeHooks( globals.getModules(i), null);
	    }
	}
	return hooksCache[type];
    }

    /** Get all interceptors
     */
    public BaseInterceptor[] getInterceptors()
    {
	if( allHooksCache != null ) {
	    return allHooksCache;
	}

	// load the cache with all the hooks
	Container globalIntContainer=getContextManager().getContainer();
	Hooks globals=globalIntContainer.getHooks();
	if( this == globalIntContainer ) {
	    allHooksCache=mergeHooks( globals.getModules(), null );
	} else {
	    allHooksCache=mergeHooks( globals.getModules(),
				      this.getHooks().getModules());
	}
	return allHooksCache;
    }

    private BaseInterceptor[] mergeHooks( Object globalM[], Object localM[] ) {
	BaseInterceptor hA[]=null;
	if( localM==null ) {
	    hA=new BaseInterceptor[ globalM.length ];
	    for( int j=0; j<globalM.length; j++ ) {
		hA[j]=(BaseInterceptor)globalM[j];
	    }
	} else {
	    hA=new BaseInterceptor[ globalM.length +
				    localM.length ];
	    int gsize=globalM.length;
	    for( int j=0; j<globalM.length; j++ ) {
		hA[j]=(BaseInterceptor)globalM[j];
	    }
	    for( int j=0; j<localM.length; j++ ) {
		hA[gsize+j]=(BaseInterceptor)localM[j];
	    }
	}
	return hA;
    }
    

    public void resetInterceptorCache( int id ) {
 	allHooksCache=null;
	hooksCache=null;
    }

    // debug
    public static final int dL=0;
    private void debug( String s ) {
	System.out.println("Container: " + s );
    }


}