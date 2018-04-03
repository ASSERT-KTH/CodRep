if( ct!=null && ct.getContext() == ctx ) {

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

package org.apache.tomcat.modules.mappers;

import org.apache.tomcat.core.*;
import org.apache.tomcat.util.buf.MessageBytes;
import org.apache.tomcat.util.io.FileUtil;
import org.apache.tomcat.util.collections.*;
import java.util.*;
import java.io.*;
/**
 *  This class will set up the data structures used by a simple patern matching
 *  alghoritm and use it to extract the path components from the request URI.
 *
 *  This particular implementation does the following:
 *  - extract the information that is relevant to matching from the Request
 *   object. The current implementation deals with the Host header and the
 *   request URI.
 *  - Use an external mapper to find the best match.
 *  - Adjust the request paths
 * 
 *  SimpleMapper1 will set 2 context notes - "map.extensions" is a
 *  SimpleHashtable containing the extension mappings, and "tomcat.map.default"
 *  for the default map, if defined explicitely.
 *
 *  It will also maintain a global mapping structure for all prefix mappings,
 *  including contexts. 
 * 
 *  The execution time is proportional with the number of hosts, number of
 *  context, number of mappings and with the length of the request.
 *
 */
public class SimpleMapper1 extends  BaseInterceptor  {
    ContextManager cm;

    PrefixMapper map;

    // We store the extension maps as per/context notes.
    int ctExtMapNote=-1;
    int defaultMapNOTE=-1;
    
    // Property for the PrefixMapper - cache the mapping results
    boolean mapCacheEnabled=false;
    
    
    public SimpleMapper1() {
	map=new PrefixMapper();
	ignoreCase= (File.separatorChar  == '\\');
	map.setIgnoreCase( ignoreCase );
    }

    /* -------------------- Support functions -------------------- */
    /** Allow the mapper to cache mapping results - resulting in a
     *  faster match for frequent requests. ( treat this as experimental)
     */
    public void setMapCache( boolean v ) {
	mapCacheEnabled = v;
	map.setMapCache( v );
    }

    // -------------------- Ingore case --------------------
    boolean ignoreCase=false;

    /** Use case insensitive match, for windows and
	similar platforms
    */
    public void setIgnoreCase( boolean b ) {
	ignoreCase=b;
	map.setIgnoreCase( b );
    }

    /* -------------------- Initialization -------------------- */
    
    /** Set the context manager. To keep it simple we don't support
     *  dynamic add/remove for this interceptor. 
     */
    public void engineInit( ContextManager cm )
	throws TomcatException
    {
	this.cm=cm;
	// set-up a per/container note for maps
	ctExtMapNote = cm.getNoteId( ContextManager.CONTAINER_NOTE,
				     "map.extension");
	defaultMapNOTE=cm.getNoteId( ContextManager.CONTAINER_NOTE,
				     "tomcat.map.default");
    }

    /** Called when a context is added.
     */
    public void addContext( ContextManager cm, Context ctx )
	throws TomcatException
    {
	map.addMapping( ctx.getHost(), ctx.getPath(), ctx.getContainer());
        map.addMappings( ctx.getHostAliases(), ctx.getPath(), ctx.getContainer());
    }

    /** Called when a context is removed from a CM - we must ask the mapper to
	remove all the maps related with this context
     */
    public void removeContext( ContextManager cm, Context ctx )
	throws TomcatException
    {
	if(debug>0) log( "Removed from maps ");
	map.removeAllMappings( ctx.getHost(), ctx);

        Enumeration vhostAliases=ctx.getHostAliases();
        while( vhostAliases.hasMoreElements() )
            map.removeAllMappings( (String)vhostAliases.nextElement(), ctx );

	// extension mappings are local to ctx, no need to do something
	// about that
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
        Enumeration vhostAliases=ctx.getHostAliases();
	String path=ct.getPath();
	String ctxP=ctx.getPath();

	// Special containers ( the default is url-mapping ).
	if( ct.isSpecial() ) return;
	if( ct.getNote( "type" ) != null )  return;
	
	if(ct.getRoles() != null || ct.getTransport() != null ) {
	    // it was only a security map, no handler defined
	    return;
	}

	switch( ct.getMapType() ) {
	case Container.PREFIX_MAP:
	    // cut /* ( no need to do a string concat for every match )
	    // workaround for frequent bug in web.xml ( backw. compat )
            if( ! path.startsWith( "/" ) ) {
                log("WARNING: Correcting error in web.xml for context \"" + ctxP +
                        "\". Mapping for path \"" + path + "\" is missing a leading '/'.");
                path="/" + path;
            }
            String prefixPath=ctxP + path.substring( 0, path.length()-2 );
	    map.addMapping( vhost, prefixPath, ct);
	    map.addMappings( vhostAliases, prefixPath, ct);

	    if( debug>0 )
		log("SM: prefix map " + vhost + ":" +  ctxP +
		    path + " -> " + ct + " " );
	    break;
	case Container.DEFAULT_MAP:
	    // This will be used if no other map match.
	    // AVOID USING IT - STATIC FILES SHOULD BE HANDLED BY
	    // APACHE ( or tomcat )
	    Container defMapC=ct.getContext().getContainer();

	    defMapC.setNote( defaultMapNOTE, ct );
	    if( debug>0 )
		log("SM: default map " + vhost + ":" +  ctxP +
		    path + " -> " + ct + " " );
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
	    if( ignoreCase )
		eM.put( path.substring( 1 ).toLowerCase() , ct );
	    else
		eM.put( path.substring( 1 ), ct );
	    if(debug>0)
		log( "SM: extension map " + ctxP + "/" +
		     path + " " + ct + " " );
	    break;
	case Container.PATH_MAP:
	    // workaround for frequent bug in web.xml
            if( ! path.startsWith( "/" ) ) {
                log("WARNING: Correcting error in web.xml for context \"" + ctxP +
                        "\". Mapping for path \"" + path + "\" is missing a leading '/'.");
                path="/" + path;
            }
	    map.addExactMapping( vhost, ctxP + path, ct);
	    map.addExactMappings( vhostAliases, ctxP + path, ct);
	    if( debug>0 )
		log("SM: exact map " + vhost + ":" + ctxP +
		    path + " -> " + ct + " " );
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


    /** First step of request processing is finding the Context.
     */
    public int contextMap( Request req ) {
	MessageBytes pathMB = req.requestURI();
	try {
	    //	    String host=null;
	    MessageBytes hostMB=req.serverName();

	    //	    host=req.serverName().toString();

	    if(debug>0) cm.log("Host = " + hostMB.toString());

	    Container container =(Container)map.
		getLongestPrefixMatch(  hostMB, pathMB);
	    
	    if( container == null )
		throw new RuntimeException( "Assertion failed: " +
					    "container==null");

	    if(debug>0)
		cm.log("SM: Prefix match " + pathMB.toString() + " -> " +
		       container.getPath() + " " + container.getHandler()  +
		       " " + container.getRoles());

	    // Once - adjust for prefix and context path
	    // If cached - we don't need to do it again ( since it is the
	    // final Container,
	    // either prefix or extension )
	    fixRequestPaths( pathMB.toString() /*XXX*/, req, container );
	

	    // if it's default container - try extension match
	    //	    if (  container.getMapType() == Container.DEFAULT_MAP ) {
	    if (  container.getHandler() == null ) {
		Container extC = matchExtension( req );
	
		if( extC != null ) {
		    // change the handler
		    if( extC.getHandler() != null ) {
			fixRequestPaths( pathMB.toString(), req, extC );
			container=extC;
		    }
		    if( debug > 0 )
			log("SM: Found extension mapping " +
			    extC.getHandler());
		    // change security roles
		}
	    }
	    
	    // Default map - if present
	    if( container.getHandler() == null ) {
		Container ctxDef=req.getContext().getContainer();
		Container defC=(Container)ctxDef.getNote( defaultMapNOTE );
		if( defC != null && defC.getHandler() !=null ) {
		    fixRequestPaths( pathMB.toString(), req, defC );

		    if( debug > 0 )
			log("SM: Found default mapping " +
			    defC.getHandler() + " " + defC.getPath() +
			     " " + defC.getMapType());
		}
	    }

	    if(debug>0) log("SM: After mapping " + req + " " +
			    req.getHandler());

	} catch(Exception ex ) {
	    log("Mapping " + req, ex);
	    return 500;
	}
	return 0;
    }
    
    /** No need to do that - we finished everything in the first step.
     *  
     */
    //    public int requestMap(Request req) {
	// No op. All mapping is done in the first step - it's better because
	// the alghoritm is more efficient. The only case where those 2 are
	// not called togheter is in getContext( "path" ). 
	// 
	// We can split it again later if that creates problems - but right
	// now it's important to have a clear alghoritm. Note that requestMap
	// is _allways_ called after contextMap ( it was asserted in  all
	// implementations).
	
    // 	return 0;
    //     }

    // -------------------- Implementation methods --------------------
    
    /** Will match an extension - note that Servlet API use special rules
     *  for mapping extension, different from what is used in existing web
     * servers. That makes this code very easy ( only need to deal with
     * the last component of the name ), but it's hard to integrate and you
     * have no way to use pathInfo.
     */
    Container matchExtension( Request req ) {
	Context ctx=req.getContext();
	String ctxP=ctx.getPath();
	
	// we haven't matched any prefix,
	String path = req.servletPath().toString(); 
	if( path == null ) return null;

	String extension=FileUtil.getExtension( path );
	if( extension == null ) return null;

	if(debug>0)
	    cm.log("SM: Extension match " + ctxP +  " " +
		   path + " " + extension );

	// Find extension maps for the context
	SimpleHashtable extM=(SimpleHashtable)ctx.
	    getContainer().getNote( ctExtMapNote );
	if( extM==null ) return null;

	// Find the container associated with that extension
	if( ignoreCase ) extension=extension.toLowerCase();
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
    void fixRequestPaths( String path, Request req, Container container )
	throws Exception
    {
	// Set servlet path and path info
	// Found a match !
	// Adjust paths based on the match
	String s=container.getPath();
	String ctxP=container.getContext().getPath();
	int sLen=s.length();
	int pathLen=path.length();
	int ctxPLen=ctxP.length();
	String pathI=null;
		// Perform URL decoding only if necessary

	switch( container.getMapType()) {
	case  Container.PREFIX_MAP: 
	    s=s.substring( 0, sLen -2 );
	    pathI= path.substring( ctxPLen + sLen - 2, pathLen);
	    if( debug>0 ) log( "Adjust for prefix map " + s + " " + pathI );
	    break;
	case Container.DEFAULT_MAP:
            s = path.substring( ctxPLen );
            pathI = null;
	    if( debug>0 ) log( "Default map " + s + " " + pathI );
	    break;
	case Container.PATH_MAP:
	    pathI= null;
	    // For exact matching - can't have path info ( or it's 
	    // a prefix map )
	    //path.substring( ctxPLen + sLen , pathLen);
	    if( debug>0 ) log( "Adjust for path map " +
			       s + " " + pathI + container.getPath());
	    break; // keep the path
	case Container.EXTENSION_MAP:
	    /*  adjust paths */
	    s= path.substring( ctxPLen );
	    pathI=null;

	}
	req.servletPath().setString( s );

	if( ! "".equals(pathI)) 
	    req.pathInfo().setString(pathI);
	Context ctx=container.getContext();
	req.setContext(ctx);
	req.setHandler( container.getHandler() );
	req.setContainer( container );
    }
    
}


/** Prefix and exact mapping alghoritm.
 *XXX finish factoring out the creation of the map ( right now direct field access is
 *  used, since the code was just cut out from SimpleMapper).
 *  XXX make sure the code is useable as a general path mapper - or at least a bridge
 *  can be created between SimpleMapper and a patern matcher like the one in XPath
 *
 * @author costin@costin.dnt.ro
 */
class PrefixMapper  {
    private static int debug=1;
    // host -> PrefixMapper for virtual hosts
    // hosts are stored in lower case ( the "common" case )
    SimpleHashtable vhostMaps=new SimpleHashtable();
    // host -> PrefixMapper for virtual hosts with leading '*'
    // host key has '*' removed
    SimpleHashtable vhostMapsWC=new SimpleHashtable();

    SimpleHashtable prefixMappedServlets;
    SimpleHashtable exactMappedServlets;

        // Cache the most recent mappings
    // Disabled by default ( since we haven't implemented
    // capacity and remove ). 
    SimpleHashtable mapCache;
    // By using TreeMap instead of SimpleMap you go from 143 to 161 RPS
    // ( at least on my machine )
    // Interesting - even if SimpleHashtable is faster than Hashtable
    // most of the time, the average is very close for both - it seems
    // that while the synchronization in Hashtable is locking, GC have
    // a chance to work, while in SimpleHashtable case GC creates big
    // peeks. That will go away with more reuse, so we should use SH.

    // An alternative to explore after everything works is to use specialized
    // mappers ( extending this one for example ) using 1.2 collections
    // TreeMap mapCache;
    boolean mapCacheEnabled=false;
    boolean ignoreCase=false;
    
    public PrefixMapper() {
	prefixMappedServlets=new SimpleHashtable();
	exactMappedServlets=new SimpleHashtable();
	mapCache=new SimpleHashtable();
    }

    public void setMapCache( boolean v ) {
	mapCacheEnabled=v;
    }

    public void setIgnoreCase( boolean b ) {
	ignoreCase=b;
    }
    
    /** Remove all mappings matching path
     */
    public void removeAllMappings( String host, Context ctx ) {
	PrefixMapper vmap=this;
	if( host!=null ) {
	    host=host.toLowerCase();
            if( host.startsWith( "*" ) )
                vmap=(PrefixMapper)vhostMapsWC.get(host.substring( 1 ));
            else
                vmap=(PrefixMapper)vhostMaps.get(host);
	}
	
	// remove all paths starting with path
	Enumeration en=vmap.prefixMappedServlets.keys();
	while( en.hasMoreElements() ) {
	    String s=(String)en.nextElement();
	    Container ct=(Container)vmap.prefixMappedServlets.get( s );
	    if( ct.getContext() == ctx ) {
		if(debug > 0 )
		    ctx.log( "Remove mapping " + s ); 
		vmap.prefixMappedServlets.remove( s );
	    }
	}
	
	en=vmap.exactMappedServlets.keys();
	while( en.hasMoreElements() ) {
	    String s=(String)en.nextElement();
	    Container ct=(Container)vmap.exactMappedServlets.get( s );
	    if( ct.getContext() == ctx ) {
		if(debug > 0 )
		    ctx.log( "Remove mapping " + s ); 
		vmap.exactMappedServlets.remove( s );
	    }
	}
	// reset the cache
	mapCache=new SimpleHashtable();
	
    }

    /**
     */
    void addMapping( String path, Object target ) {
	prefixMappedServlets.put( path, target);
    }

    /**
     */
    void addExactMapping( String path, Object target ) {
	exactMappedServlets.put( path, target);
    }
    
    /**
     */
    public void addMapping( String host, String path, Object target ) {
	if( host == null ) {
	    if( ignoreCase )
		prefixMappedServlets.put( path.toLowerCase(), target);
	    else
		prefixMappedServlets.put( path, target);
	} else {
	    host=host.toLowerCase();
            SimpleHashtable maps;
            if( host.startsWith( "*" ) ) {
                maps=vhostMapsWC;
                host=host.substring( 1 );
            } else {
                maps=vhostMaps;
            }
	    PrefixMapper vmap=(PrefixMapper)maps.get( host );
	    if( vmap == null ) {
		vmap=new PrefixMapper();
		vmap.setIgnoreCase( ignoreCase );
                maps.put( host, vmap );
		vmap.setMapCache( mapCacheEnabled );
	    }
	    if( ignoreCase ) 
		vmap.addMapping( path.toLowerCase(), target );
	    else
		vmap.addMapping( path, target );
	}
    }

    /**
     */
    public void addMappings( Enumeration hostAliases, String path, Object target ) {
        while ( hostAliases.hasMoreElements() )
            addMapping( (String)hostAliases.nextElement(), path, target );
    }

    /**
     */
    public void addExactMapping( String host, String path, Object target ) {
        if( host==null ) {
            if ( ignoreCase )
                exactMappedServlets.put( path.toLowerCase(), target);
            else
                exactMappedServlets.put( path, target);
        } else {
	    host=host.toLowerCase();
            SimpleHashtable maps;
            if( host.startsWith( "*" ) ) {
                maps = vhostMapsWC;
                host=host.substring( 1 );
            } else {
                maps = vhostMaps;
            }
	    PrefixMapper vmap=(PrefixMapper)maps.get( host );
	    if( vmap == null ) {
		vmap=new PrefixMapper();
		maps.put( host, vmap );
	    }
	    if( ignoreCase ) 
		vmap.addExactMapping( path.toLowerCase(), target );
	    else
		vmap.addExactMapping( path, target );
	}
    }

    /**
     */
    public void addExactMappings( Enumeration hostAliases, String path, Object target ) {
        while ( hostAliases.hasMoreElements() )
            addExactMapping( (String)hostAliases.nextElement(), path, target );
    }
   
    
    // -------------------- Implementation --------------------

    /** Match a prefix rule - /foo/bar/index.html/abc
     */
    public Object getLongestPrefixMatch( MessageBytes hostMB,
					 MessageBytes pathMB )
    {
	// XXX fixme
	String host=hostMB.toString();
	String path=pathMB.toString();
	Object container = null;

	PrefixMapper myMap=null;
	if( host!=null ) {
	    myMap=(PrefixMapper)vhostMaps.get( host );
	    if( myMap==null ) {
		myMap=(PrefixMapper)vhostMaps.get( host.toLowerCase() );
	    }
        }
        if( myMap==null ) {
            // Check host against virtual hosts that began with '*'
            Enumeration vhosts = vhostMapsWC.keys();
            while(vhosts.hasMoreElements()) {
                String vhostName = (String)vhosts.nextElement();
                if(host.endsWith(vhostName)) {
                    myMap = (PrefixMapper)vhostMapsWC.get(vhostName);
                    break;
                }
            }
	}
	
	if( myMap==null ) myMap = this; // default server

	if( ignoreCase ) path=path.toLowerCase();
	container=myMap.exactMappedServlets.get( path );
	if( container != null ) return container; // and we're done!

	/** Cache for request results - exploit the fact that few
	 *  request are more "popular" than other.
	 *  Disable it if you want to benchmark the mapper !!!
	 */
	if( myMap.mapCacheEnabled ) {
	    container=myMap.mapCache.get(path);
	    if( container!=null ) return container;
	}
		
        String s = path;
	while (s.length() >= 0) {
	    //if(debug>8) context.log( "Prefix: " + s  );
	    container = myMap.prefixMappedServlets.get(s);
	    
	    if (container == null) {
		// if empty string didn't map, time to give up
		if ( s.length() == 0 )
                    break;
		s=FileUtil.removeLast( s );
	    }  else {
		if( myMap.mapCacheEnabled ) {
		    // XXX implement LRU or another replacement alghoritm
		    myMap.mapCache.put( path, container );
		}
		return container;
	    }
	}
	return container;
    }

}

 