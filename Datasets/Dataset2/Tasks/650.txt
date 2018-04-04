if( scontainer==null ) {

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
import java.util.*;

/** Parse request URI and find ContextPath, ServletPath, PathInfo and QueryString
 *  Use a simple alghoritm - no optimizations or tricks.
 *  Also, no special features - no VirtualHost, user directories, etc.
 *
 *  For "production" environment you should use either an optimized version
 *  or a real web server parser.
 */
public class SimpleMapper extends  BaseInterceptor  {
    int debug=0;
    ContextManager cm;
    // String context prefix -> Mappings context maps
    Hashtable contextPaths=new Hashtable();

    // security restrictions 
    Hashtable securityConstraints=new Hashtable();
    
    class Mappings {
	Context ctx;
	Container defaultContainer;
	Hashtable prefixMappedServlets;
	Hashtable extensionMappedServlets;
	Hashtable pathMappedServlets;
    }

    
    public SimpleMapper() {
    }

    public void setContextManager( ContextManager cm ) {
	this.cm=cm;
	// Add all context that are set in CM
	Enumeration enum=cm.getContextNames();
	while( enum.hasMoreElements() ) {
	    String name=(String) enum.nextElement();
	    try {
		Context ctx=cm.getContext( name );
		if(debug>0) ctx.log("Adding existing context " + name );
		addContext( cm, ctx );
	    } catch (TomcatException ex ) {
		ex.printStackTrace();
	    }
	}
    }

    public void setDebug( int level ) {
	if(level!=0) System.out.println("SimpleMapper - set debug " + level);
	debug=level;
    }

    void log( String msg ) {
	if( cm==null) 
	    System.out.println("SimpleMapper: " + msg );
	else
	    cm.getContext("").log( msg );
    }

    /** First step of request porcessing is finding the Context.
     *  Advanced mappers will do only one parsing.
     */
    public int contextMap( Request rrequest ) {
	// someone else set it up, no need to worry
	if( rrequest.getContext() != null )
	    return OK;
	
	// resolve the server that we are for
	String path = rrequest.getRequestURI();
	
	Context ctx= this.getContextByPath(path);
	rrequest.setContext(ctx);
	
	// final fix on response & request
	//		rresponse.setServerHeader(server.getServerHeader());
	String ctxPath = ctx.getPath();
	String lookupPath=rrequest.getLookupPath();

	// do not set it if it is already set or we have no
	// URI - the case of a sub-request generated internally
	if( path!=null && lookupPath==null ) 
	    lookupPath= path.substring(ctxPath.length(),
				       path.length());

	// check for ? string on lookuppath
	int qindex = lookupPath.indexOf("?");
	
	if (qindex > -1) {
	    lookupPath=lookupPath.substring(0, qindex);
	}
	
	if (lookupPath.length() < 1) {
	    lookupPath = "/";
	}

	rrequest.setLookupPath( lookupPath );
	return OK;
    }

    /** 
     */
    public int requestMap(Request req) {
	Context context=req.getContext();
	String path=req.getLookupPath();
        Container container = null;

	String ctxP=context.getPath();
	Mappings m=(Mappings)contextPaths.get(ctxP);

	if(debug>0) context.log( "Mapping: " + req );

	container=findContainer( m, path, context, req );
	
	// set default container, return
	if (container == null) {
	    container=m.defaultContainer;
	    if( m.defaultContainer.getHandler() == null ) {
		ServletWrapper sw=context.getDefaultServlet();
		m.defaultContainer.setHandler( sw );
	    }
	    req.setWrapper( m.defaultContainer.getHandler() );
	    req.setServletPath( "" );
	    req.setPathInfo( path);
	    if(debug>0) context.log("Default mapper " + "\n    " + req);
	}  else {
	    req.setWrapper( container.getHandler() );
	    
	    if(debug>0) context.log("Found wrapper using getMapPath " + "\n    " + req);
	}
	req.setContainer( container );

	// the container already has security properties
	// in it, no need to search again
	if( container.getRoles() != null ) {
	    if(debug>0) context.log("Existing security constraint " + "\n    " + container.getRoles());
	    return OK;
	}
	
	// Now find the security restrictions for req
	m=(Mappings)securityConstraints.get(ctxP);
	if( m==null) return OK;
	Container scontainer=findContainer( m, path, context, req);
	if( m==null ) {
	    // no security
	    return OK;
	}
	// Merge the security info into the container
	//
	if(debug>0) context.log("Found security constraing " + "\n    " + scontainer.getRoles());
	container.setRoles( scontainer.getRoles());
	container.setTransport( scontainer.getTransport());
	
	return OK;
    }


    private Container findContainer( Mappings m, String path, Context context, Request req )
    {
	Container container = getPathMatch(m, context, path, req);

	// try a prefix match
	if( container == null ) 
	    container = getPrefixMatch(m, context, path, req);

	// try an extension match
	if (container == null) 
	    container = getExtensionMatch(m, context, path, req);
	return container;
    }

    // -------------------- Internal representation of mappings --------------------
    /* Implementation:
       We will create an internal representation of mappings ( context path and internal mappings
       and security mappings). Advanced ( optimized ) mappers will sort the list and will do
       efficient char[] matching ( instead of creating a lot of String garbage ).

    */

    /** Called when a context is removed from a CM
     */
    public void removeContext( ContextManager cm, Context ctx ) throws TomcatException
    {
	String ctxP=ctx.getPath();
	Mappings m=(Mappings)contextPaths.get(ctxP);

	if(debug>0) ctx.log( "Removed from maps ");
	contextPaths.remove( ctxP );
	// m will be GC ( we may want to set all to null and clean the
	// Hashtable to help a bit)
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
	String path=ct.getPath();
	String ctxP=ctx.getPath();

	// add the mapping in the "securityContraints"
	// or in contextPaths if it's a servlet mapping
	Hashtable mtable=securityConstraints;
	if( ct.getHandler() != null )
	    mtable=contextPaths;
	//	System.out.println("XXX " + path + " " + ctx.getDebug() + " " + ctxP + " " + ct.getHandler() + " " + ct.getRoles());
	
	Mappings m=(Mappings)mtable.get(ctxP);
	if( m==null ) {
	    m=new Mappings();
	    m.ctx=ctx;
	    m.prefixMappedServlets=new Hashtable();
	    m.extensionMappedServlets=new Hashtable();
	    m.pathMappedServlets=new Hashtable();
	    mtable.put( ctxP, m );
	    Container def=new Container();
	    def.setContext( ctx );
	    ServletWrapper wrapper = ctx.getDefaultServlet();
	    def.setHandler( wrapper );
	    m.defaultContainer=def;
	}
	if(debug>0) ctx.log( "Add mapping " + path + " " + ct + " " + m );
	
	path = path.trim();

	if ((path.length() == 0))
	    return;
	if (path.startsWith("/") &&
	    path.endsWith("/*")){
	    m.prefixMappedServlets.put(path, ct);
	    //	    System.out.println("Map " + path + " -> " + sw );
	} else if (path.startsWith("*.")) {
	    m.extensionMappedServlets.put(path, ct);
	} else if (! path.equals("/")) {
	    m.pathMappedServlets.put(path, ct);
	} 
    }

    public void removeContainer( Container ct )
	throws TomcatException
    {
	Context ctx=ct.getContext();
	String mapping=ct.getPath();
	String ctxP=ctx.getPath();
        mapping = mapping.trim();
	if(debug>0) ctx.log( "Remove mapping " + mapping );

	Mappings m=(Mappings)contextPaths.get(ctxP);
	m.prefixMappedServlets.remove(mapping);
	m.extensionMappedServlets.remove(mapping);
	m.pathMappedServlets.remove(mapping);

	m=(Mappings)securityConstraints.get(ctxP);
	m.prefixMappedServlets.remove(mapping);
	m.extensionMappedServlets.remove(mapping);
	m.pathMappedServlets.remove(mapping);
    }

    // -------------------- Implementation --------------------
    /** Get an exact match ( /catalog ) - rule 1 in 10.1
     */
    private Container getPathMatch(Mappings m, Context context, String path, Request req) {
        Container wrapper = null;
	wrapper = (Container)m.pathMappedServlets.get(path);

	if (wrapper != null) {
	    req.setServletPath( path );
	    // No path info - it's an exact match
	    if(debug>1) context.log("path match " + path );
	}
        return wrapper;
    }


    /** Match a prefix rule - /foo/bar/index.html/abc
     */
    private Container getPrefixMatch(Mappings m, Context context, String path, Request req) {
	Container wrapper = null;
        String s = path;

	// /baz/== /baz ==/baz/* 
	if( s.endsWith( "/" ))
	    s=removeLast(s);
	
	while (s.length() > 0) {
	    // XXX we can remove /* in prefix map when we add it, so no need
	    // for another string creation
	    if(debug>2) context.log( "Prefix: " + s  );
	    wrapper = (Container)m.prefixMappedServlets.get(s + "/*" );
	    //Enumeration en=m.prefixMappedServlets.keys();
	    //while( en.hasMoreElements() ) {
	    //System.out.println("XXX: " + en.nextElement());
	    //}
	    
	    if (wrapper == null)
		s=removeLast( s );
	    else
		break;
	}
		
	// Set servlet path and path info
	if( wrapper != null ) {
	    // Found a match !
	    req.setServletPath( s );
	    String pathI = path.substring(s.length(), path.length());
	    if( ! "".equals(pathI) ) 
		req.setPathInfo(pathI);
	    if(debug>0) context.log("prefix match " + path );
	}
	return wrapper;
    }

    // It looks like it's broken: try /foo/bar.jsp/test/a.baz -> will not match it
    // as baz, but neither as .jsp, which is wrong.
    // XXX Fix this code - I don't think evolution will work in this class.
    private Container getExtensionMatch(Mappings m, Context context, String path, Request req) {
	String extension=getExtension( path );
	if( extension == null ) return null;

	// XXX need to store the extensions without *, to avoid extra
	// string creation
	Container wrapper= (Container)m.extensionMappedServlets.get("*" + extension);
	if (wrapper == null)
	    return null;

	// fix paths
	// /a/b/c.jsp/d/e
        int i = path.lastIndexOf(".");
	int j = path.lastIndexOf("/");
	if (j > i) {
	    int k = i + path.substring(i).indexOf("/");
	    String s = path.substring(0, k);
	    req.setServletPath( s );

	    s = path.substring(k);
	    req.setPathInfo(  s  );
	} else {
	    req.setServletPath( path );
	}
		
	if(debug>0) context.log("extension match " + path );
	return wrapper; 
    }

    // -------------------- String utilities --------------------

    private String getExtension( String path ) {
        int i = path.lastIndexOf(".");
	int j = path.lastIndexOf("/");

	if (i > -1) {
	    String extension = path.substring(i);
	    int k = extension.indexOf("/");
	    if( k>=0 )
		extension = extension.substring(0, k);
	    return extension;
	}
	return null;
    }
    
    private String removeLast( String s) {
	int i = s.lastIndexOf("/");
	
	if (i > 0) {
	    s = s.substring(0, i);
	} else if (i == 0 && ! s.equals("/")) {
	    s = "/";
	} else {
	    s = "";
	}
	return s;
    }

    String getFirst( String path ) {
	if (path.startsWith("/")) 
	    path = path.substring(1);
	
	int i = path.indexOf("/");
	if (i > -1) {
	    path = path.substring(0, i);
	}

	return  "/" + path;
    }


    // XXX XXX XXX need to fix this - it is used by getContext(String path) (costin)
    
    /**
     * Gets the context that is responsible for requests for a
     * particular path.  If no specifically assigned Context can be
     * identified, returns the default Context.
     *
     * @param path The path for which a Context is requested
     */
    Context getContextByPath(String path) {
	String realPath = path;
	Context ctx = null;

	// XXX
	// needs help ... this needs to be optimized out.

        lookup:
	do {
	    ctx = cm.getContext(path);
	    if (ctx == null) {
	        int i = path.lastIndexOf('/');
		if (i > -1 && path.length() > 1) {
		    path = path.substring(0, i);
		    if (path.length() == 0) {
		        path = "/";
		    }
		} else {
		    // path too short
		    break lookup;
		}
	    } else {
	    }
	} while (ctx == null);

	// no map - root context
	if (ctx == null) {
	    ctx = cm.getContext( "" );
	}

	return ctx;
    }

}
    