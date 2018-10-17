return OK;

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

package org.apache.tomcat.modules.loggers;

import org.apache.tomcat.core.*;
import org.apache.tomcat.util.*;
import org.apache.tomcat.util.hooks.*;
import java.io.*;
import java.net.*;
import java.util.*;

/** Log all hook events during tomcat execution.
 *  Use debug>0 to log addContainer ( since this generates a lot of
 *  output )
 */
public class LogEvents extends BaseInterceptor {
    boolean enabled=false;
    
    public LogEvents() {
    }

    public void setEnabled( boolean b ) {
	enabled=b;
    }
    
    public int registerHooks( Hooks hooks, ContextManager cm, Context ctx ) {
	if( enabled || cm.getDebug() > 5 ) {
	    enabled=true;
	    log( "Adding LogEvents, cm.debug=" + cm.getDebug() + " "
		 + enabled);
	    hooks.addModule( this );
	}
	return DECLINED;
    }
    
    // -------------------- Request notifications --------------------
    public int requestMap(Request request ) {
	log( "requestMap " + request);
	return 0;
    }

    public int contextMap( Request request ) {
	log( "contextMap " + request);
	return 0;
    }

    public int preService(Request request, Response response) {
	log( "preService " + request);
	return 0;
    }

    public int authenticate(Request request, Response response) {
	log( "authenticate " + request);
	return DECLINED;
    }

    public int authorize(Request request, Response response,
			 String reqRoles[])
    {
	StringBuffer sb=new StringBuffer();
	appendSA( sb, reqRoles, " ");
	log( "authorize " + request + " " + sb.toString() );
	return DECLINED;
    }

    public int beforeBody( Request request, Response response ) {
	log( "beforeBody " + request);
	return 0;
    }

    public int beforeCommit( Request request, Response response) {
	log( "beforeCommit " + request);
	return 0;
    }


    public int afterBody( Request request, Response response) {
	log( "afterBody " + request);
	return 0;
    }

    public int postRequest( Request request, Response response) {
	log( "postRequest " + request);
	return 0;
    }

    public int handleError( Request request, Response response, Throwable t) {
	log( "handleError " + request +  " " + t);
	return 0;
    }

    public int postService(Request request, Response response) {
	log( "postService " + request);
	return 0;
    }

    public int newSessionRequest( Request req, Response res ) {
	log( "newSessionRequest " + req );
	return 0;
    }
    
    // -------------------- Context notifications --------------------
    public void contextInit(Context ctx) throws TomcatException {
	log( "contextInit " + ctx);
    }

    public void contextShutdown(Context ctx) throws TomcatException {
	log( "contextShutdown " + ctx);
    }

    /** Notify when a new servlet is added
     */
    public void addServlet( Context ctx, Handler sw) throws TomcatException {
	log( "addServlet " + ctx + " " + sw );
    }
    
    /** Notify when a servlet is removed from context
     */
    public void removeServlet( Context ctx, Handler sw) throws TomcatException {
	log( "removeServlet " + ctx + " " + sw);
    }

    public void addMapping( Context ctx, String path, Handler servlet)
	throws TomcatException
    {
	log( "addMapping " + ctx + " " + path + "->" + servlet);
    }


    public void removeMapping( Context ctx, String path )
	throws TomcatException
    {
	log( "removeMapping " + ctx + " " + path);
    }

    private void appendSA( StringBuffer sb, String s[], String sep) {
	for( int i=0; i<s.length; i++ ) {
	    sb.append( sep ).append( s[i] );
	}
    }
    
    /** 
     */
    public void addSecurityConstraint( Context ctx, String path[],
				       String methods[], String transport,
				       String roles[] )
	throws TomcatException
    {
	StringBuffer sb=new StringBuffer();
	sb.append("addSecurityConstraint " + ctx + " " );
	if( methods!=null ) {
	    sb.append("Methods: ");
	    appendSA( sb, methods, " " );
	}
	if( path!=null) {
	    sb.append(" Paths: ");
	    appendSA( sb, path, " " );
	}
	if( roles!=null) {
	    sb.append(" Roles: ");
	    appendSA( sb, roles, " " );
	}
	sb.append(" Transport " + transport );
	log(sb.toString());
    }

    public void addInterceptor( ContextManager cm, Context ctx,
				BaseInterceptor i )
	throws TomcatException
    {
	if( ! enabled ) return;
	if( ctx==null)
	    log( "addInterceptor " + i );
	else {
	    log( "addInterceptor " + ctx + " " + i);
	}
    }
    
    /** Called when the ContextManger is started
     */
    public void engineInit(ContextManager cm) throws TomcatException {
	log( "engineInit ");
    }

    /** Called before the ContextManager is stoped.
     *  You need to stop any threads and remove any resources.
     */
    public void engineShutdown(ContextManager cm) throws TomcatException {
	log( "engineShutdown ");
    }


    /** Called when a context is added to a CM
     */
    public void addContext( ContextManager cm, Context ctx )
	throws TomcatException
    {
	log( "addContext " + ctx );
    }

    public void addContainer( Container ct )
	throws TomcatException
    {
	if( debug > 0 )
	    log( "addContainer " + ct.getContext() + " " + ct );
    }

    public void engineState( ContextManager cm , int state )
	throws TomcatException
    {
	log( "engineState " + state );
    }

    public void engineStart( ContextManager cm )
	throws TomcatException
    {
	log( "engineStart " );
    }

    /** Called when a context is removed from a CM
     */
    public void removeContext( ContextManager cm, Context ctx )
	throws TomcatException
    {
	log( "removeContext" + ctx);
    }

    /** Servlet Init  notification
     */
    public void preServletInit( Context ctx, Handler sw )
	throws TomcatException
    {
	log( "preServletInit " + ctx + " " + sw);
    }

    
    public void postServletInit( Context ctx, Handler sw )
	throws TomcatException
    {
	log( "postServletInit " + ctx + " " + sw);
    }

    /** Servlet Destroy  notification
     */
    public void preServletDestroy( Context ctx, Handler sw )
	throws TomcatException
    {
	log( "preServletDestroy " + ctx + " " + sw);
    }

    
    public void postServletDestroy( Context ctx, Handler sw )
	throws TomcatException
    {
	log( "postServletDestroy " + ctx +  " " + sw);
    }

}