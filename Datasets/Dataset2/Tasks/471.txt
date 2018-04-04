public void reload( Request req, Context ctx)

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

import org.apache.tomcat.core.*;
import org.apache.tomcat.util.*;
import java.io.*;
import java.net.*;
import java.util.*;
import javax.servlet.http.*;

/**
 */
public class BaseInterceptor implements RequestInterceptor, ContextInterceptor {
    ContextManager cm; 
    protected String methods[]=new String[0];
    int debug=0;
    
    public BaseInterceptor() {
    }
    
    public void setDebug( int d ) {
	debug=d;
    }
    
    public void setContextManager( ContextManager cm ) {
	this.cm=cm;
    }
    
    // -------------------- Request notifications --------------------
    public int requestMap(Request request ) {
	return 0;
    }

    public int contextMap( Request rrequest ) {
	return 0;
    }

    public int authenticate(Request request, Response response) {
	return 0;
    }

    public int authorize(Request request, Response response) {
	return 0;
    }

    public int preService(Request request, Response response) {
	return 0;
    }

    public int beforeBody( Request rrequest, Response response ) {
	return 0;
    }

    public int newSessionRequest( Request request, Response response) {
	return 0;
    }
    
    public int beforeCommit( Request request, Response response) {
	return 0;
    }


    public int afterBody( Request request, Response response) {
	return 0;
    }

    public int postService(Request request, Response response) {
	return 0;
    }

    public String []getMethods()  {
	return methods;
    }

    // -------------------- Context notifications --------------------
    public void contextInit(Context ctx) throws TomcatException {
    }

    public void contextShutdown(Context ctx) throws TomcatException {
    }
    public void addContainer(Container container) throws TomcatException {
    }

    public void removeContainer(Container container) throws TomcatException {
    }

    /** 
     */
    public void addSecurityConstraint( Context ctx, String path, Container ct )
	throws TomcatException
    {
    }

    /** Called when the ContextManger is started
     */
    public void engineInit(ContextManager cm) throws TomcatException {
    }

    /** Called before the ContextManager is stoped.
     *  You need to stop any threads and remove any resources.
     */
    public void engineShutdown(ContextManager cm) throws TomcatException {
    }


    /** Called when a context is added to a CM
     */
    public void addContext( ContextManager cm, Context ctx ) throws TomcatException {
    }

    /** Called when a context is removed from a CM
     */
    public void removeContext( ContextManager cm, Context ctx ) throws TomcatException {
    }

    public void reload( Context ctx)
	throws TomcatException
    {
    }

    /** Servlet Init  notification
     */
    public void preServletInit( Context ctx, ServletWrapper sw ) throws TomcatException {
    }

    
    public void postServletInit( Context ctx, ServletWrapper sw ) throws TomcatException {
    }

    /** Servlet Destroy  notification
     */
    public void preServletDestroy( Context ctx, ServletWrapper sw ) throws TomcatException {
    }

    
    public void postServletDestroy( Context ctx, ServletWrapper sw ) throws TomcatException {
    }

}