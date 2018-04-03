// 	response.setHeader("Status", Integer.toString(response.getStatus()));

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
import java.io.*;
import java.net.*;
import java.util.*;
import javax.servlet.http.*;

/**
 *  Will generate the output headers ( cookies, etc ) plus tomcat-specific headers.
 * 
 */
public class FixHeaders extends  BaseInterceptor implements RequestInterceptor {
    
    public FixHeaders() {
    }
	
    public int beforeBody( Request request, Response response ) {
	HttpDate date = new HttpDate(System.currentTimeMillis());
	response.setHeader("Date", date.toString());
	response.setHeader("Status", Integer.toString(response.getStatus()));
        response.setHeader("Content-Type", response.getContentType());

	String contentLanguage=response.getLocale().getLanguage();
	if (contentLanguage != null) {
            response.setHeader("Content-Language",contentLanguage);
        }

	// context is null if we are in a error handler before the context is
	// set ( i.e. 414, wrong request )
	if( request.getContext() != null)
	    response.setHeader("Servlet-Engine", request.getContext().getEngineHeader());


	int contentLength=response.getContentLength();
        if (contentLength != -1) {
            response.setHeader("Content-Length", Integer.toString(contentLength));
        }

	// XXX duplicated code, ugly
        Enumeration cookieEnum = response.getCookies();
        while (cookieEnum.hasMoreElements()) {
            Cookie c  = (Cookie)cookieEnum.nextElement();
            response.addHeader( CookieTools.getCookieHeaderName(c),
		       CookieTools.getCookieHeaderValue(c));
	    if( c.getVersion() == 1 ) {
		// add a version 0 header too.
		// XXX what if the user set both headers??
		Cookie c0 = (Cookie)c.clone();
		c0.setVersion(0);
		response.addHeader( CookieTools.getCookieHeaderName(c0),
				   CookieTools.getCookieHeaderValue(c0));
	    }
        }
	return 0;
    }

}