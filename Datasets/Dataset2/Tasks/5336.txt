super("", "");

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


package org.apache.tomcat.facade;

import org.apache.tomcat.util.*;
import org.apache.tomcat.helper.RequestUtil;
import org.apache.tomcat.core.*;
import org.apache.tomcat.facade.*;
import java.io.*;
import java.net.*;
import java.security.*;
import java.util.*;
import javax.servlet.*;
import javax.servlet.http.*;

/**
 * Facade for a ServerCookie object. The ServerCookie is a recyclable
 * and efficient Cookie implementation. The Facades makes sure the
 * user "sees" only what's permited by the servlet spec.
 *
 * @author Costin Manolache
 */
final class CookieFacade extends Cookie {
    ServerCookie sC;
    
    CookieFacade( ServerCookie sC ) {
	// we can't reuse super anyway
	super(null, null);
	this.sC=sC;
    }
    public void setComment(String purpose) {
	sC.getComment().setString( purpose);
    }
    public String getComment() {
	return sC.getComment().toString();
    }
    public void setDomain(String pattern) {
	sC.getDomain().setString( pattern.toLowerCase());
	// IE allegedly needs this
    }
    public String getDomain() {
	return sC.getDomain().toString();
    }
    public void setMaxAge(int expiry) {
	sC.setMaxAge(expiry);
    }
    public int getMaxAge() {
	return sC.getMaxAge();
    }
    public void setPath(String uri) {
	sC.getPath().setString( uri );
    }
    public String getPath() {
	return sC.getPath().toString();
    }
    public void setSecure(boolean flag) {
	sC.setSecure( flag );
    }
    public boolean getSecure() {
	return sC.getSecure();
    }
    public String getName() {
	return sC.getName().toString();
    }
    public void setValue(String newValue) {
	sC.getValue().setString(newValue);
    }
    public String getValue() {
	return sC.getValue().toString();
    }
    public int getVersion() {
	return sC.getVersion();
    }
    public void setVersion(int v) {
	sC.setVersion(v);
    }
}