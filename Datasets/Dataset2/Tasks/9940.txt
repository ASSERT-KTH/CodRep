for( int j=0; j< roles.length; j ++ )

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

package org.apache.tomcat.modules.aaa;

import org.apache.tomcat.core.*;
import org.apache.tomcat.util.*;
import java.util.*;
import java.io.*;

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
    ContextManager cm;

    // Security mapping note
    int secMapNote;

    // Required roles attribute
    int reqRolesNote;
    int reqTransportNote;

    public AccessInterceptor() {
    }

    /* -------------------- Initialization -------------------- */
    
    /** Set the context manager. To keep it simple we don't support
     *  dynamic add/remove for this interceptor. 
     */
    public void engineInit(ContextManager cm) throws TomcatException {
	
	super.engineInit( cm );
	
	this.cm=cm;
	// set-up a per/container note for maps
	secMapNote = cm.getNoteId( ContextManager.CONTAINER_NOTE,
				   "map.security");
	// Used for inter-module communication - required role, tr
	reqRolesNote = cm.getNoteId( ContextManager.REQUEST_NOTE,
				     "required.roles");
	reqTransportNote = cm.getNoteId( ContextManager.REQUEST_NOTE,
					 "required.transport");
    }

    public void contextInit( Context ctx)
	throws TomcatException
    {
	String login_type=ctx.getAuthMethod();
	if( debug > 0 ) log( "Init  " + ctx.getHost() + " " +
			     ctx.getPath() + " " + login_type );
	
	if( "FORM".equals( login_type )) {
	    String page=ctx.getFormLoginPage();
	    String errorPage = ctx.getFormErrorPage();
	    
	    if(page==null || errorPage==null) {
		ctx.log( "Form login without form pages, defaulting to basic "
			 + page + " " + errorPage);
		BasicAuthHandler baH=new BasicAuthHandler();
		baH.setModule( this );
		ctx.addServlet( baH );
		ctx.addErrorPage( "401", "tomcat.basicAuthHandler");
		return;
	    }

	    // Workaround for common error - no "/" at start of page
	    if( ! page.startsWith("/")) {
		ctx.log("FORM: login page doesn't start with / " + page );
		page="/" + page;
	    }
	    if( ! errorPage.startsWith("/")) {
		ctx.log("FORM: error page doesn't start with / " + errorPage );
		errorPage="/" + errorPage;
	    }

	    String cpath=ctx.getPath();
	    
	    // Workaround for common error - ctx path included
	    if( page.startsWith( cpath ) ) {
		if( ! ("".equals(cpath) || "/".equals(cpath)) )
		    ctx.log("FORM: WARNING, login page starts with " +
			    "context path " + page + " " + cpath );
	    } else
		page= cpath + page;


	    if( errorPage.startsWith( cpath ) ) {
		if( ! ("/".equals(cpath) || "".equals( cpath )) )
		    ctx.log("FORM: WARNING, error page starts with " +
			    "context path " + errorPage);
	    } else
		errorPage= cpath + errorPage;

	    // Adjust login and error paths - avoid computations in handlers
	    ctx.setFormLoginPage( page );
	    ctx.setFormErrorPage( errorPage );

	    FormAuthHandler formH=new FormAuthHandler();
	    formH.setModule( this );
	    ctx.addServlet( formH );
	    FormSecurityCheckHandler fscH=new FormSecurityCheckHandler();
	    fscH.setModule( this );
	    ctx.addServlet( fscH );
	    ctx.addErrorPage( "401", "tomcat.formAuthHandler");

	    // Add mapping for the POST handler
	    String pageP=page.substring( cpath.length());
	    int lastS=pageP.lastIndexOf( "/" );
	    String location="/j_security_check";
	    if( lastS > 0 ) {
		location=pageP.substring( 0, lastS) +
		    "/j_security_check";
	    }
	    ctx.addServletMapping( location,
				   "tomcat.formSecurityCheck");
	    if( debug > 0 )
		ctx.log( "Map " + location +
			 " to tomcat.formSecurityCheck for " +
			 page);
	} else if( "BASIC".equals( login_type )) {
	    BasicAuthHandler baH=new BasicAuthHandler();
	    baH.setModule( this );
	    ctx.addServlet( baH );
	    ctx.addErrorPage( "401", "tomcat.basicAuthHandler");
	} else {
	    // if unknown, leave the normal 404 error handler to deal
	    // with unauthorized access.
	}
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
	// XXX add the note only if we have a security constraint
	SecurityConstraints ctxSecurityC=(SecurityConstraints)ctxCt.
	    getNote( secMapNote );
	if( ctxSecurityC==null) {
	    ctxSecurityC= new SecurityConstraints();
	    ctxCt.setNote( secMapNote, ctxSecurityC );
	}

	if( ct.getRoles()!=null || ct.getTransport()!=null ) {
	    if( debug > 0 )
		log( "addContainer() " + ctx.getHost() + " " +
		     ctx.getPath() + " " +
		     ct.getPath() );
	    ctxSecurityC.addContainer( ct );
	}
    }

    /* -------------------- Request mapping -------------------- */

    /** Check if this request requires auth, and if so check the roles.
     */
    public int requestMap( Request req )
    {
	Context ctx=req.getContext();
	SecurityConstraints ctxSec=(SecurityConstraints)ctx.getContainer().
	    getNote( secMapNote );
	if( ctxSec==null || ctxSec.patterns==0 ) return 0; // fast exit

	MessageBytes reqURIMB=req.requestURI();
	if (reqURIMB.indexOf('%') >= 0 || reqURIMB.indexOf( '+' ) >= 0) {
	    log("Shouldn't happen - the request is decoded earlier");
	    reqURIMB.unescapeURL();
	}
	String reqURI = req.requestURI().toString();
	String ctxPath= ctx.getPath();
	String path=reqURI.substring( ctxPath.length());
	String method=req.method().toString();
	
	if( debug > 1 ) log( "checking " + path );
	
	for( int i=0; i< ctxSec.patterns ; i++ ) {
	    Container ct=ctxSec.securityPatterns[i];
	    if( match( ct, path, method ) ) {
		String roles[]=ct.getRoles();
		String methods[]=ct.getMethods();
		String transport=ct.getTransport();
		if( debug>0) {
		    StringBuffer sb=new StringBuffer("matched ");
		    sb.append(ct.getPath()).append(" ");
		    if(methods!=null)
			for( int j=0; j< methods.length; j++ )
			    sb.append(methods[j]).append(" ");
		    sb.append(transport).append(" ");
		    if( roles!=null)
			for( int j=0; j< roles.length; j++ )
			    sb.append( roles[j]).append(" ");
		    log( sb.toString());
		}
		if( transport != null &&
		    ! "NONE".equals( transport )) {
		    req.setNote( reqTransportNote, transport );
		}
		
		// roles will be checked by a different interceptor
		if( roles!= null  && roles.length > 0) 
		    req.setRequiredRoles( roles );
	    }
	}
 	return 0;
    }

    /** Handle authorization for requests where certain roles are
     *  requires, and a user/password scheme is used to authenticate
     *  the user ( BASIC, FORM ) and find the user roles.
     */
    public int authorize( Request req, Response response, String roles[] )
    {
        if( roles==null || roles.length==0 ) {
            // request doesn't need authentication
            return OK;
        }

	// will call authenticate() hooks to get the user
        String user=req.getRemoteUser();
        if( user==null )
	    return DECLINED; // we know only about user/password auth

        if( debug > 0 ) log( "Controled access for " + user + " " +
                     req + " " + req.getContainer() );

        String userRoles[]= req.getUserRoles();
        if ( userRoles == null )
            return DECLINED; // no user roles - can't handle

	for( int i=0; i< userRoles.length; i ++ ) {
	    for( int j=0; j< roles.length; i ++ )
		if( userRoles[i]!=null && userRoles[i].equals( roles[j] ))
		    return OK; // found the right role
	}

        if( debug > 0 ) log( "UnAuthorized " + roles[0] );
        return DECLINED; // couldn't find the role - maybe someone else can
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
	    // original code: 
	    // return path.startsWith( ctPath.substring(0, ctPathL - 2  ));
	    // changed to eliminate the allocation ( will be changed again
	    // when MessageBytes will be used in intercepotrs, now they are
	    // in core
	    if( path.length() < ctPathL - 2  )
		return false;
	    for( int i=0; i< ctPathL - 2 ; i++ ) {
		if( path.charAt( i ) != ctPath.charAt( i ))
		    return false;
	    }
	    return true;
	case Container.EXTENSION_MAP:
	    return ctPath.substring( 1 ).equals(FileUtil.getExtension( path ));
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

class BasicAuthHandler extends Handler {
    int sbNote=0;
    
    BasicAuthHandler() {
	//	setOrigin( Handler.ORIGIN_INTERNAL );
	name="tomcat.basicAuthHandler";
    }

    public void doService(Request req, Response res)
	throws Exception
    {
	Context ctx=req.getContext();
	String realm=ctx.getRealmName();
	if(realm==null) realm="default";
	res.setStatus( 401 );
	res.setHeader( "WWW-Authenticate",
		       "Basic realm=\"" + realm + "\"");
        // return some content to prevent error 500
	// and notify the user they are not authorized if BasicAuth fails
        res.setContentType("text/html");        // ISO-8859-1 default  

	if( sbNote==0 ) {
	    sbNote=req.getContextManager().getNoteId(ContextManager.REQUEST_NOTE,
						     "BasicAuthHandler.buff");
	}

	// we can recycle it because
	// we don't call toString();
	StringBuffer buf=(StringBuffer)req.getNote( sbNote );
	if( buf==null ) {
	    buf = new StringBuffer();
	    req.setNote( sbNote, buf );
	}
 
        buf.append("<html><head><title>Not Authorized</title></head>");
        buf.append("<body>Not Authorized</body></html>");

        res.setContentLength(buf.length());
	res.getBuffer().write( buf );
    }
}

/** 401 - access denied. Will check if we have an authenticated user
    or not.
    XXX If we have user/pass, but still no permission  - display
    error page.
*/
class FormAuthHandler extends Handler {
    
    FormAuthHandler() {
	//	setOrigin( Handler.ORIGIN_INTERNAL );
	name="tomcat.formAuthHandler";
    }

    public void doService(Request req, Response res)
	throws Exception
    {
	Context ctx=req.getContext();

	ServerSession session=req.getSession( false );
	if( session == null ) {
	}
	
	String page=ctx.getFormLoginPage();
	String errorPage=ctx.getFormErrorPage();
	// assert errorPage!=null ( AccessInterceptor will check
	// that and enable form login only if everything is ok

	session=(ServerSession)req.getSession( true );
	String username=(String)session.getAttribute( "j_username" );

	if( debug>0) log( "Username = " + username);
	if( username != null ) {
	    // 401 with existing j_username - that means wrong credentials.
	    // Next time we'll have a fresh start
	    session.removeAttribute( "j_username");
	    session.removeAttribute( "j_password");
	    req.setAttribute("javax.servlet.error.message",
			     errorPage );
	    contextM.handleStatus( req, res, 302 ); // redirect
	    return;
	}

	String originalLocation = req.requestURI().toString();
	if (req.queryString().toString() != null)
	    originalLocation += "?" + req.queryString().toString();
	session.setAttribute( "tomcat.auth.originalLocation",
			      originalLocation);
	if( debug > 0 )
	    log("Redirect1: " + page  + " originalUri=" +
		req.requestURI().toString());

	req.setAttribute("javax.servlet.error.message",
			 page );
	contextM.handleStatus( req, res, 302 ); // redirect
	return; 
    }
}

/** 
    j_security_check handler

    This is called after the user POST the form login page.
*/
class FormSecurityCheckHandler extends Handler {
    
    FormSecurityCheckHandler() {
	//	setOrigin( Handler.ORIGIN_INTERNAL );
	name="tomcat.formSecurityCheck";
    }

    /** Will set the j_username and j_password attributes
	in the session, and redirect to the original
	location.
	No need to validate user/pass and display error page
	if wrong user/pass. Will be done by normal 401 handler,
	if user/pass are wrong.
    */
    public void doService(Request req, Response res)
	throws Exception
    {
	String username=req.getParameter( "j_username" );
	String password=req.getParameter( "j_password" );

	Context ctx=req.getContext();
	String errorPage=ctx.getFormErrorPage();
	// assert errorPage!=null ( AccessInterceptor will check
	// that and enable form login only if everything is ok
	
	if( debug > 0 )
	    log( " user/pass= " + username + " " + password );
	    
	ServerSession session=(ServerSession)req.getSession( false );
	if( session == null ) {
	    ctx.log("From login without a session ");
	    req.setAttribute("javax.servlet.error.message",
			     errorPage );
	    contextM.handleStatus( req, res, 302 ); // redirect
	    return;
	}
	session.setAttribute( "j_username", username );
	session.setAttribute( "j_password", password );
	    
	String origLocation=(String)session.
	    getAttribute( "tomcat.auth.originalLocation");

	if( debug > 0)
	    log("Redirect2: " + origLocation);
	
	req.setAttribute("javax.servlet.error.message",
			 origLocation );
	contextM.handleStatus( req, res, 302 ); // redirect
    }
}