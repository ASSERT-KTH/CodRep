//import org.apache.tomcat.session.ServerSession;

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
import org.apache.tomcat.util.*;
import org.apache.tomcat.session.ServerSession;
import org.apache.tomcat.util.xml.*;
import java.io.*;
import java.net.*;
import java.util.*;
import org.xml.sax.*;

/**
 *  Extract user/password credentials from a request.
 *  This module is specialized in detecting BASIC and FORM authentication, and
 *  will set 2 notes in the request: "credentials.user" and
 *  "credentials.password".
 *
 *  A "Realm" module may use the 2 notes in authenticating the user. 
 * 
 *  This module must will act on the "authenticate" callback - the action
 *  will happen _only_ for requests requiring authentication, not for
 *  every request.
 *
 *  It must be configured before the Realm module.
 */
public class CredentialsInterceptor extends BaseInterceptor
{
    int userNote;
    int passwordNote;

    /** The module will set a note with this name on the request for
	the extracted user, if Basic or Form authentication is used
    */
    public static final String USER_NOTE="credentials.user";
    /** The module will set a note with this name on the request for
	the extracted password, if Basic or Form authentication is used
    */
    public static final String PASSWORD_NOTE="credentials.password";
    
    public CredentialsInterceptor() {
    }

    public void engineInit( ContextManager cm )
	throws TomcatException
    {
	userNote=cm.getNoteId( ContextManager.REQUEST_NOTE, USER_NOTE);
	passwordNote=cm.getNoteId( ContextManager.REQUEST_NOTE, PASSWORD_NOTE);
    }

    /** Extract the credentails from req
     */
    public int authenticate( Request req , Response res ) {
	Context ctx=req.getContext();
	String login_type=ctx.getAuthMethod();
	if( "BASIC".equals( login_type )) {
	    basicCredentials( req );
	}
	if( "FORM".equals( login_type )) {
	    formCredentials( req );
	}
	return 0;
    }
	
    
    /** Extract userName and password from a request using basic
     *  authentication.
     */
    private void basicCredentials( Request req )
    {
	String authorization = req.getHeader("Authorization");
	
	if (authorization == null )
	    return; // no credentials
	if( ! authorization.startsWith("Basic ")) {
	    log( "Wrong syntax for basic authentication " + req + " " +
		 authorization);
	    return; // wrong syntax
	}
	
	authorization = authorization.substring(6).trim();
	String unencoded=Base64.base64Decode( authorization );
	
	int colon = unencoded.indexOf(':');
	if (colon < 0) {
	    log( "Wrong syntax for basic authentication " + req + " " +
		 authorization);
	    return;
	}
	
	req.setNote( userNote, unencoded.substring(0, colon));
	req.setNote( passwordNote , unencoded.substring(colon + 1));
    }


    private void formCredentials( Request req  ) {
	ServerSession session=(ServerSession)req.getSession( false );

	if( session == null )
	    return; // not authenticated

	// XXX The attributes are set on the first access.
	// It is possible for a servlet to set the attributes and
	// bypass the security checking - but that's ok, since
	// everything happens inside a web application and all servlets
	// are in the same domain.
	String username=(String)session.getAttribute("j_username");
	String password=(String)session.getAttribute("j_password");

	if( username!=null && password!=null) {
	    req.setNote( userNote , username );
	    req.setNote( passwordNote, password);
	}
    }
}
