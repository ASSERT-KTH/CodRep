//	path.recycle();

/*
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
 * ====================================================================
 */ 
package org.apache.tomcat.util;

import java.io.*;


/**
 *  Server-side cookie representation.
 *   Allows recycling and uses MessageBytes as low-level
 *  representation ( and thus the byte-> char conversion can be delayed
 *  until we know the charset ).
 * 
 *  Tomcat.core uses this recyclable object to represent cookies,
 *  and the facade will convert it to the external representation.
 */
public class ServerCookie implements Serializable {
    private MessageBytes name=new MessageBytes();
    private MessageBytes value=new MessageBytes();

    private MessageBytes comment=new MessageBytes();    // ;Comment=VALUE
    
    private MessageBytes domain;    // ;Domain=VALUE ... 

    private int maxAge = -1;	// ;Max-Age=VALUE
				// ;Discard ... implied by maxAge < 0
    private MessageBytes path;	// ;Path=VALUE .
    private boolean secure;	// ;Secure 
    private int version = 0;	// ;Version=1

    
    public ServerCookie() {

    }

    public void recycle() {
	name.recycle();
	value.recycle();
	comment.recycle();
	maxAge=-1;
	path.recycle();
	version=0;
	secure=false;
    }

    public void parse( MessageBytes input ) {
	// Not implemented
    }
    
    
    public MessageBytes getComment() {
	return comment;
    }
    
    public MessageBytes getDomain() {
	return domain;
    }

    public void setMaxAge(int expiry) {
	maxAge = expiry;
    }

    public int getMaxAge() {
	return maxAge;
    }
    

    public MessageBytes getPath() {
	return path;
    }

    public void setSecure(boolean flag) {
	secure = flag;
    }

    public boolean getSecure() {
	return secure;
    }

    public MessageBytes getName() {
	return name;
    }

    public MessageBytes getValue() {
	return value;
    }

    public int getVersion() {
	return version;
    }


    public void setVersion(int v) {
	version = v;
    }

    // Note -- disabled for now to allow full Netscape compatibility
    // from RFC 2068, token special case characters
    // 
    // private static final String tspecials = "()<>@,;:\\\"/[]?={} \t";
    private static final String tspecials = ",;";

    /*
     * Tests a string and returns true if the string counts as a 
     * reserved token in the Java language.
     * 
     * @param value		the <code>String</code> to be tested
     *
     * @return			<code>true</code> if the <code>String</code> is
     *				a reserved token; <code>false</code>
     *				if it is not			
     */
    public static boolean isToken(String value) {
	int len = value.length();

	for (int i = 0; i < len; i++) {
	    char c = value.charAt(i);

	    if (c < 0x20 || c >= 0x7f || tspecials.indexOf(c) != -1)
		return false;
	}
	return true;
    }


    public static boolean checkName( String name ) {
	if (!isToken(name)
		|| name.equalsIgnoreCase("Comment")	// rfc2019
		|| name.equalsIgnoreCase("Discard")	// 2019++
		|| name.equalsIgnoreCase("Domain")
		|| name.equalsIgnoreCase("Expires")	// (old cookies)
		|| name.equalsIgnoreCase("Max-Age")	// rfc2019
		|| name.equalsIgnoreCase("Path")
		|| name.equalsIgnoreCase("Secure")
		|| name.equalsIgnoreCase("Version")
	    ) {
	    return false;
	}
	return true;
    }

}
