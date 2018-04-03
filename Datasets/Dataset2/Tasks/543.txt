if(ct.getRoles() != null || ct.getTransport() != null ) {

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


package org.apache.tomcat.request;

import org.apache.tomcat.core.*;
import org.apache.tomcat.core.Constants;
import org.apache.tomcat.util.*;
import javax.servlet.http.*;
import java.util.*;

/**
 *  This class will set up the data structures used by a simple patern matching
 *  alghoritm and use it to extract the path components from the request URI.
 *
 *  The interceptor will be called in standalone case, for "integrated" mode
 *  we should have all the data from the web server - that means the performance
 *  of this code is not relevant for production mode if a web server is used.
 * 
 *  This particular implementation does the following:
 *  - extract the information that is relevant to matching from the Request object.
 *    The current implementation deals with the Host header and the request URI.
 *  - Use an external mapper to find the best match.
 *  - Adjust the request paths
 * 
 *  The execution time is proportional with the number of hosts, number of context, number of
 *  mappings and with the length of the request.
 *
 *  Security mappings are more complex ( method, transport are also part of the
 *  matching ). We can share the same mapping alghoritm or even the mapper - but
 *  until security code will be stable it's better to keep it separated.
 *  
 */
public class SimpleMapper1 extends  BaseInterceptor  {
    int debug=0;
    ContextManager cm;

    PrefixMapper map;

    // We store the extension maps as per/context notes.
    int ctExtMapNote=-1;

    // Property for the PrefixMapper - cache the mapping results
    boolean mapCacheEnabled=false;
    
    public SimpleMapper1() {
	map=new PrefixMapper();
    }

    /* -------------------- Support functions -------------------- */
    public void setDebug( int level ) {
	if(level!=0) log("SM: SimpleMapper - set debug " + level);
	debug=level;
    }

    void log( String msg ) {
	if( cm==null) 
	    System.out.println("SimpleMapper: " + msg );
	else
	    cm.log( msg );
    }

    /** Allow the mapper to cache mapping results - resulting in a
     *  faster match for frequent requests. ( treat this as experimental)
     */
    public void setMapCache( boolean v ) {
	mapCacheEnabled = v;
	map.setMapCache( v );
    }

    /* -------------------- Initialization -------------------- */
    
    /** Set the context manager. To keep it simple we don't support
     *  dynamic add/remove for this interceptor. 
     */
    public void setContextManager( ContextManager cm ) {
	this.cm=cm;
	
	// set-up a per/container note for maps
	try {
	    ctExtMapNote = cm.getNoteId( ContextManager.CONTAINER_NOTE, "map.extension");
	} catch( TomcatException ex ) {
	    ex.printStackTrace();
	    throw new RuntimeException( "Invalid state ");
	}
    }

    /** Called when a context is added.
     */
    public void addContext( ContextManager cm, Context ctx ) throws TomcatException
    {
	map.addMapping( ctx.getHost(), ctx.getPath(), ctx.getContainer());
    }

    /** Called when a context is removed from a CM - we must ask the mapper to
	remove all the maps related with this context
     */
    public void removeContext( ContextManager cm, Context ctx ) throws TomcatException
    {
	if(debug>0) log( "Removed from maps ");
	map.removeAllMappings( ctx.getHost(), ctx.getPath());
	// extension mappings are local to ctx, no need to do something about that
    }
    

    /**
     * Associate URL pattern  to a set of propreties.
     * 
     * Note that the order of resolution to handle a request is:
     *
     *    exact mapped servlet (eg /catalog)
     *    prefix mapped servlets (eg /foo/bar/*)
     *    extension mapped servlets (eg *jsp)
     *    default servlet
     *
     */
    public void addContainer( Container ct )
	throws TomcatException
    {
	Context ctx=ct.getContext();
	String vhost=ctx.getHost();
	String path=ct.getPath();
	String ctxP=ctx.getPath();

	if(ct.getHandler() == null ) {
	    // it was only a security map, no handler defined
	    return;
	}
	
	switch( ct.getMapType() ) {
	case Container.PREFIX_MAP:
	    // cut /* ( no need to do a string concat for every match )
	    map.addMapping( vhost, ctxP + path.substring( 0, path.length()-2 ), ct);
	    if( debug>0 ) log("SM: prefix map " + vhost + ":" +  ctxP + path + " -> " + ct + " " );
	    break;
	case Container.EXTENSION_MAP:
	    // Add it per/defaultContainer - as spec require ( it may also be
	    // possible to support type maps per/Container, i.e. /foo/*.jsp -
	    // but that would require changes in the spec.
	    Context mapCtx=ct.getContext();
	    Container defC=mapCtx.getContainer();
	    
	    SimpleHashtable eM=(SimpleHashtable) defC.getNote( ctExtMapNote );
	    if( eM==null ) {
		eM=new SimpleHashtable();
		defC.setNote( ctExtMapNote, eM );
	    }
	    // add it to the Container local maps
	    eM.put( path.substring( 1 ), ct );
	    if(debug>0) log( "SM: extension map " + ctxP + "/" + path + " " + ct + " " );
	    break;
	case Container.PATH_MAP:
	    map.addExactMapping( vhost, ctxP + path, ct);
	    if( debug>0 ) log("SM: exact map " + vhost + ":" + ctxP + path + " -> " + ct + " " );
	    break;
	}
    }

    // XXX not implemented - will deal with that after everything else works.
    // Remove context will still work
    public void removeContainer( Container ct )
	throws TomcatException
    {
	Context ctx=ct.getContext();
	String mapping=ct.getPath();
	String ctxP=ctx.getPath();
        mapping = mapping.trim();
	if(debug>0) log( "Remove mapping " + mapping );
    }


    /* -------------------- Request mapping -------------------- */


    /** First step of request porcessing is finding the Context.
     */
    public int contextMap( Request req ) {
	String path = req.getRequestURI();
	if( path==null) throw new RuntimeException("ASSERT: null path in request URI");
	if( path.indexOf("?") >=0 ) throw new RuntimeException("ASSERT: ? in requestURI");
	
	try {
	    String host=req.getServerName();
	    if(debug>0) cm.log("Host = " + host);

	    Context ctx = null;
	    Container container =(Container)map.getLongestPrefixMatch(  host, path );
	    
	    if( container == null ) throw new RuntimeException( "Assertion failed - container==null");
	    if( container.getHandler() == null ) throw new RuntimeException( "Assertion failed - container.handler==null");
	    
	    if(debug>0) cm.log("SM: Prefix match " + path + " -> " + container.getPath() + " " +
			       container.getHandler()  + " " + container.getRoles());

	    // Once - adjust for prefix and context path
	    // If cached - we don't need to do it again ( since it is the final Container,
	    // either prefix or extension )
	    fixRequestPaths( path, req, container );
	

	    // if it's default container - try extension match
	    if (  container.getMapType() == Container.DEFAULT_MAP ) {
		Container extC = matchExtension( req );
	
		if( extC != null ) {
		    // change the handler
		    if( extC.getHandler() != null ) {
			fixRequestPaths( path, req, extC );
			container=extC;
		    }
		    if( debug > 0 ) log("SM: Found extension mapping " + extC.getHandler());
		    // change security roles
		}
	    }
	    
	    if(debug>0) log("SM: After mapping " + req + " " + req.getWrapper());
	
	} catch(Exception ex ) {
	    ex.printStackTrace();
	    return HttpServletResponse.SC_INTERNAL_SERVER_ERROR;
	}
	return OK;
    }
    
    /** No need to do that - we finished everything in the first step.
     *  
     */
    public int requestMap(Request req) {
	// No op. All mapping is done in the first step - it's better because the
	// alghoritm is more efficient. The only case where those 2 are not called togheter
	// is in getContext( "path" ). 
	// 
	// We can split it again later if that creates problems - but right now it's important
	// to have a clear alghoritm.
	// Note that requestMap is _allways_ called after contextMap ( it was asserted in
	//  all implementations).
	
	return OK;
    }

    // -------------------- Implementation methods --------------------
    
    /** Will match an extension - note that Servlet API use special rules
     *  for mapping extension, different from what is used in existing web servers.
     *  That makes this code very easy ( only need to deal with the last component
     *  of the name ), but it's hard to integrate and you have no way to use pathInfo.
     */
    Container matchExtension( Request req ) {
	Context ctx=req.getContext();
	String ctxP=ctx.getPath();

	String path = req.getPathInfo(); // we haven't matched any prefix,
	if( path == null ) return null;

	String extension=URLUtil.getExtension( path );
	if( extension == null ) return null;

	if(debug>0) cm.log("SM: Extension match " + ctxP +  " " + path + " " + extension );

	// Find extension maps for the context
	SimpleHashtable extM=(SimpleHashtable)ctx.getContainer().getNote( ctExtMapNote );
	if( extM==null ) return null;
	
	// Find the container associated with that extension
	Container container= (Container)extM.get(extension);

	if (container == null)
	    return null;

	// This container doesn't change the mappings - it only 
	// has "other" properties ( in the current code security
	// constraints 
	if( container.getHandler() == null) return container;

	return container; 
    }

    /** Adjust the paths in request after matching a container
     */
    void fixRequestPaths( String path, Request req, Container container ) {
	// Set servlet path and path info
	// Found a match !
	// Adjust paths based on the match 
	String s=container.getPath();
	String ctxP=container.getContext().getPath();
	int sLen=s.length();
	int pathLen=path.length();
	int ctxPLen=ctxP.length();
	String pathI=null;
	
	switch( container.getMapType()) {
	case  Container.PREFIX_MAP: 
	    s=s.substring( 0, sLen -2 );
	    pathI= path.substring( ctxPLen + sLen - 2, pathLen);
	    break;
	case Container.DEFAULT_MAP:
	    s="/";
	    pathI= path.substring( ctxPLen ) ;
	    break;
	case Container.PATH_MAP:
	    pathI= path.substring( ctxPLen + sLen, pathLen);
	    break; // keep the path
	case Container.EXTENSION_MAP:
	    /*  adjust paths */
	    s= path.substring( ctxPLen );
	    pathI=null;

	}
	req.setServletPath( s );
	
	if( ! "".equals(pathI) ) 
	    req.setPathInfo(pathI);
	Context ctx=container.getContext();
	req.setContext(ctx);
	req.setWrapper( container.getHandler() );
	req.setContainer( container );
    }
    
}
