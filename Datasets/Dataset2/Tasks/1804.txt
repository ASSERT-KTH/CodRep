HttpSession session=(HttpSession)req.getSession( false );

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
package org.apache.tomcat.helper;

import org.apache.tomcat.core.*;
import org.apache.tomcat.util.*;
import org.apache.tomcat.util.xml.*;
import javax.servlet.http.HttpSession;
import java.io.*;
import java.net.*;
import java.util.*;
import org.xml.sax.*;

/**
 *  Various tools used to implement security.
 * 
 */
public class SecurityTools {
    
    static int base64[]= {
	    64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64,
	    64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64,
	    64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 62, 64, 64, 64, 63,
	    52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 64, 64, 64, 64, 64, 64,
	    64,  0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14,
	    15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 64, 64, 64, 64, 64,
	    64, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40,
	    41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 64, 64, 64, 64, 64,
	    64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64,
	    64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64,
	    64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64,
	    64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64,
	    64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64,
	    64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64,
	    64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64,
	    64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64, 64
    };

    public static String base64Decode( String orig ) {
	char chars[]=orig.toCharArray();
	StringBuffer sb=new StringBuffer();
	int i=0;

	int shift = 0;   // # of excess bits stored in accum
	int acc = 0;
	
	for (i=0; i<chars.length; i++) {
	    int v = base64[ chars[i] & 0xFF ];
	    
	    if ( v >= 64 ) {
		if( chars[i] != '=' )
		    System.out.println("Wrong char in base64: " + chars[i]);
	    } else {
		acc= ( acc << 6 ) | v;
		shift += 6;
		if ( shift >= 8 ) {
		    shift -= 8;
		    sb.append( (char) ((acc >> shift) & 0xff));
		}
	    }
	}
	return sb.toString();
    }

    /** Extract the credentails from req
     */
    public static void credentials( Request req , Hashtable credentials ) {
	Context ctx=req.getContext();
	String login_type=ctx.getAuthMethod();
	if( "BASIC".equals( login_type )) {
	    basicCredentials( req, credentials );
	}
	if( "FORM".equals( login_type )) {
	    formCredentials( req, credentials );
	}
    }
	
    
    // XXX use more efficient structures instead of StringBuffer ?
    // ( after everything is stable - not very important if web server is used)

    /** Extract userName and password from a request using basic authentication.
     *  Can be used in a JAAS callback or as it is. 
     */
    public static void basicCredentials( Request req, Hashtable credentials )
    {
	Context ctx=req.getContext();

	String authMethod=ctx.getAuthMethod();
	if( authMethod==null || "BASIC".equals(authMethod) ) {

	    String authorization = req.getHeader("Authorization");

	    if (authorization == null )
		return; // no credentials
	    if( ! authorization.startsWith("Basic "))
		return; // wrong syntax

	    authorization = authorization.substring(6).trim();
	    String unencoded=SecurityTools.base64Decode( authorization );

	    int colon = unencoded.indexOf(':');
	    if (colon < 0)
		return;

	    credentials.put( "username" , unencoded.substring(0, colon));
	    credentials.put( "password" , unencoded.substring(colon + 1));

	}
	return;
    }


    public static void formCredentials( Request req, Hashtable credentials ) {
	Context ctx=req.getContext();
	String authMethod=ctx.getAuthMethod();

	if( "FORM".equals( authMethod ) ) {
	    HttpSession session=req.getSession( false );

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
		credentials.put( "username" , username );
		credentials.put( "password", password);
	    }
	}
    }

    public static boolean haveRole( String userRoles[], String requiredRoles[] ) {
	for( int i=0; i< userRoles.length; i ++ ) {
	    if( haveRole( userRoles[i], requiredRoles )) return true;
	}
	return false;
    }

    public static boolean haveRole( String element, String set[] ) {
	for( int i=0; i< set.length; i ++ ) {
	    if( element!=null && element.equals( set[i] ))
		return true;
	}
	return false;
    }
}
