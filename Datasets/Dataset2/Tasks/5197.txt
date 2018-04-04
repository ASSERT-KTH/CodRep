if( ctx.getDebug() > 0 ) log( "ACCESS: Adding " + ctx.getHost() + " " + ctx.getPath() + " " + ct.getPath() );

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

// XXX maybe it's a good idea to use a different model for adding secuirty
// constraints - we use Container now because we want to generalize all
// per/URL properties. 

/**
 *  Access control - find if a request matches any web-resource-collection
 *  and set the "required" attributes.
 *
 *  The spec requires additive checking ( i.e. there is no "best match"
 *  defined, but "all requests that contain a request path that mathces the
 *  URL pattern in the resource collection are subject to the constraing" ).
 *
 *  In "integrated" mode this interceptor will be no-op, we'll use the
 *  web server ( assuming we can map the security to web-server equivalent
 *  concepts - I think we can do that, but need to experiment with that)
 */
public class AccessInterceptor extends  BaseInterceptor  {
    int debug=0;
    ContextManager cm;

    // Security mapping note
    int secMapNote;

    // Required roles attribute
    int reqRolesNote;
    
    public AccessInterceptor() {
    }

    /* -------------------- Support functions -------------------- */
    public void setDebug( int level ) {
	if(level!=0) log("SM: AccessInterceptor - set debug " + level);
	debug=level;
    }

    void log( String msg ) {
	if( cm==null) 
	    System.out.println("AccessInterceptor: " + msg );
	else
	    cm.log( msg );
    }


    /* -------------------- Initialization -------------------- */
    
    /** Set the context manager. To keep it simple we don't support
     *  dynamic add/remove for this interceptor. 
     */
    public void setContextManager( ContextManager cm ) {
	super.setContextManager( cm );
	
	this.cm=cm;
	// set-up a per/container note for maps
	try {
	    secMapNote = cm.getNoteId( ContextManager.CONTAINER_NOTE, "map.security");
	    reqRolesNote = cm.getNoteId( ContextManager.REQUEST_NOTE, "required.roles");
	} catch( TomcatException ex ) {
	    ex.printStackTrace();
	    throw new RuntimeException( "Invalid state ");
	}
    }

    /** Called when a context is added.
     */
    public void addContext( ContextManager cm, Context ctx ) throws TomcatException
    {
	Container ct=ctx.getContainer();
	ct.setNote( secMapNote, new SecurityConstraints() );
    }

    /** Called when a context is removed from a CM - we must ask the mapper to
	remove all the maps related with this context
     */
    public void removeContext( ContextManager cm, Context ctx ) throws TomcatException
    {
	// nothing - will go away with the ctx
    }
    

    // XXX not implemented - will deal with that after everything else works.
    public void removeContainer( Container ct )
	throws TomcatException
    {
    }

    /**
     */
    public void addContainer( Container ct )
	throws TomcatException
    {
	Context ctx=ct.getContext();
	Container ctxCt=ctx.getContainer();
	SecurityConstraints ctxSecurityC=(SecurityConstraints)ctxCt.getNote( secMapNote );
	
	if( ct.getRoles()!=null || ct.getTransport()!=null ) {
	    log( "ACCESS: Adding " + ctx.getHost() + " " + ctx.getPath() + " " + ct.getPath() );
	    ctxSecurityC.addContainer( ct );
	}
    }

    /* -------------------- Request mapping -------------------- */

    /** Check if this request requires auth, and if so check the roles.
     *  This interceptor needs to be "up-chain" from security check interceptor.
     *  It is also possible to move this check at requestMap stage.
     */
    public int authorize( Request req, Response response )
    {
	Context ctx=req.getContext();
	SecurityConstraints ctxSec=(SecurityConstraints)ctx.getContainer().getNote( secMapNote );
	if( ctxSec.patterns==0 ) return 0; // fast exit
	
	String reqURI = req.getRequestURI();
	String ctxPath= ctx.getPath();
	String path=reqURI.substring( ctxPath.length());
	String method=req.getMethod();

	log( "ACCESS: checking " + path );
	
	for( int i=0; i< ctxSec.patterns ; i++ ) {
	    Container ct=ctxSec.securityPatterns[i];
	    if( match( ct, path, method ) ) {
		log( "ACCESS: matched " + ct.getPath() + " " + ct.getMethods() + " " +
		     ct.getTransport() + " " + ct.getRoles());
		String roles[]=ct.getRoles();
		String transport=ct.getTransport();

		if( transport != null && (
					  "INTEGRAL".equals( transport ) ||
					  "CONFIDENTAIL".equals( transport ))) {
		    // check if SSL is used
		    log( "ACCESS: SSL required " + req );
		}

		// roles will be checked by a different interceptor
		req.setNote( reqRolesNote, roles );
	    }
	}
 	return 0;
    }

    /** Find if a pattern is matched by a container
     */
    boolean match( Container ct, String path, String method ) {
	String ctPath=ct.getPath();
	int ctPathL=ctPath.length();
	String ctMethods[]=ct.getMethods();
	
	if( ctMethods != null && ctMethods.length > 0 ) {
	    boolean ok=false;
	    for( int i=0; i< ctMethods.length; i++ ) {
		if( method.equals( ctMethods[i] ) ) {
		    ok=true;
		    break;
		}
	    }
	    if( ! ok ) return false; // no method matched
	}

	// either method is any or we matched the method
	
	switch( ct.getMapType() ) {
	case Container.PREFIX_MAP:
	    return path.startsWith( ctPath.substring(0, ctPathL - 2  ));
	case Container.EXTENSION_MAP:
	    return ctPath.substring( 1 ).equals( URLUtil.getExtension( path ));
	case Container.PATH_MAP:
	    return path.equals( ctPath );
	}
	return false;
    }
    // -------------------- Implementation methods --------------------
}

class SecurityConstraints {
    Container []securityPatterns;
    int patterns=0;
    // implement re-sizeable array later
    static final int MAX_CONSTRAINTS=30;

    public SecurityConstraints() {
	securityPatterns=new Container[MAX_CONSTRAINTS];
    }

    // It's called in a single thread anyway
    public synchronized void addContainer(Container ct) {
	securityPatterns[ patterns ]= ct;
	patterns++;
    }
}