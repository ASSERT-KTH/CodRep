value + " \r\nGOT: " + respValue+ " HEADERS(" +

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
package org.apache.tomcat.util.test.matchers;

import org.apache.tomcat.util.test.*;
import java.net.*;
import java.io.*;
import java.util.*;
import java.net.*;

/** Check if the response has ( or has not ) some headers
 */
public class HeaderMatch extends Matcher {
    String name;
    String value;
    
    // the response should include the following headers
    Vector headerVector=new Vector(); // workaround for introspection problems
    Hashtable expectHeaders=new Hashtable();

    public HeaderMatch() {
    }

    // -------------------- 

    public void setName( String n ) {
	name=n;
    }

    public void setValue( String v ) {
	value=v;
    }

    // Multiple headers ?
    public void addHeader( Header rh ) {
	headerVector.addElement( rh );
    }

    /** Verify that response includes the expected headers.
     *  The value is a "|" separated list of headers to expect.
     *  ?? Do we need that ?
     */
    public void setExpectHeaders( String s ) {
       Header.parseHeadersAsString( s, headerVector );
    }

    public Hashtable getExpectHeaders() {
	if( name!=null ) {
	    headerVector.addElement( new Header( name, value ));
	}
	if( headerVector.size() > 0 ) {
	    Enumeration en=headerVector.elements();
	    while( en.hasMoreElements()) {
		Header rh=(Header)en.nextElement();
		expectHeaders.put( rh.getName(), rh );
	    }
	    headerVector=new Vector();
	}
	return expectHeaders;
    }
    
    public String getTestDescription() {
	StringBuffer desc=new StringBuffer();
	boolean needAND=false;
	
	if( getExpectHeaders().size() > 0 ) {
	    Enumeration e=expectHeaders.keys();
	    while( e.hasMoreElements()) {
		if( needAND ) desc.append( " && " );
		needAND=true;
		String key=(String)e.nextElement();
		Header h=(Header)expectHeaders.get(key);
		desc.append("( responseHeader '" + h.getName() +
			    ": " + h.getValue() + "' ) ");
	    }
	}

	desc.append( " == " ).append( magnitude );
	return desc.toString();
    }

    // -------------------- Execute the request --------------------

    public void execute() {
	try {
	    result=checkResponse( magnitude );
	} catch(Exception ex ) {
	    ex.printStackTrace();
	    result=false;
	}
    }

    private boolean checkResponse(boolean testCondition)
	throws Exception
    {
	String responseLine=response.getResponseLine();
	Hashtable headers=response.getHeaders();
	
        boolean responseStatus = true;
	
	getExpectHeaders();
	if( expectHeaders.size() > 0 ) {
	    // Check if we got the expected headers
	    if(headers==null) {
		log("ERROR no response header, expecting header");
	    }
	    Enumeration e=expectHeaders.keys();
	    while( e.hasMoreElements()) {
		String key=(String)e.nextElement();
		Header expH=(Header)expectHeaders.get(key);
		String value=expH.getValue();
		Header resH=(Header)headers.get(key);
		String respValue=(resH==null)? "": resH.getValue();
		if( respValue==null || respValue.indexOf( value ) <0 ) {
		    log("ERROR expecting header " + key + ":" +
			value + " \nGOT: " + respValue+ " HEADERS(" +
			Header.toString(headers) + ")");
		    
		    return false;
		}
	    }

	}
	
	return responseStatus;
    }
    
}