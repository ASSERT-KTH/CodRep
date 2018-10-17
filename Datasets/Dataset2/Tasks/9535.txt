//	System.out.println("DECODING : " +data );

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

package org.apache.tomcat.util.http;

import  org.apache.tomcat.util.*;
import  org.apache.tomcat.util.collections.*;
import java.io.*;
import java.util.*;
import java.text.*;

/**
 * 
 * @author Costin Manolache
 */
public final class Parameters extends MultiMap {
    public static final int INITIAL_SIZE=4;

    private boolean isSet=false;
    private boolean isFormBased=false;
    
    /**
     * 
     */
    public Parameters() {
	super( INITIAL_SIZE );
    }

    public void recycle() {
	super.recycle();
	isSet=false;
	isFormBased=false;
    }

    /**
     */
    public boolean isEvaluated() {
	return isSet;
    }
    
    public void setEvaluated( boolean b ) {
	isSet=b;
    }
    
    // XXX need better name
    public boolean hasFormData() {
	return isFormBased;
    }
    public void setFormData(boolean b ) {
	isFormBased=b;
    }
    
    public void processParameters( byte bytes[], int start, int len ) {
	int end=start+len;
	int pos=start;
	
        do {
	    int nameStart=pos;
	    int nameEnd=ByteChunk.indexOf(bytes, nameStart, end, '=' );
	    if( nameEnd== -1 ) nameEnd=end;
	    
	    int valStart=nameEnd+1;
	    int valEnd=ByteChunk.indexOf(bytes, valStart, end, '&');
	    if( valEnd== -1 ) valEnd=end;
	    
	    pos=valEnd+1;
	    
	    if( nameEnd<=nameStart ) {
		continue;
		// invalid chunk - it's better to ignore
		// XXX log it ?
	    }
	    
	    int field=this.addField();
	    this.getName( field ).setBytes( bytes,
					    nameStart, nameEnd );
	    this.getValue( field ).setBytes( bytes,
					     valStart, valEnd );
	} while( pos<end );
    }

    public void processParameters( char chars[], int start, int len ) {
	int end=start+len;
	int pos=start;
	
        do {
	    int nameStart=pos;
	    int nameEnd=CharChunk.indexOf(chars, nameStart, end, '=' );
	    if( nameEnd== -1 ) nameEnd=end;

	    int valStart=nameEnd+1;
	    int valEnd=CharChunk.indexOf(chars, valStart, end, '&');
	    if( valEnd== -1 ) valEnd=end;
	    pos=valEnd+1;
	    
	    if( nameEnd<=nameStart ) {
		continue;
		// invalid chunk - no name, it's better to ignore
		// XXX log it ?
	    }
	    
	    int field=this.addField();
	    this.getName( field ).setChars( chars,
					    nameStart, nameEnd );
	    this.getValue( field ).setChars( chars,
					     valStart, valEnd );
	} while( pos<end );
    }

    
    public void processParameters( MessageBytes data ) {
	if( data==null || data.getLength() <= 0 ) return;

	if( data.getType() == MessageBytes.T_BYTES ) {
	    ByteChunk bc=data.getByteChunk();
	    processParameters( bc.getBytes(), bc.getOffset(),
			       bc.getLength());
	} else {
	    if (data.getType()!= MessageBytes.T_CHARS ) 
		data.toChars();
	    CharChunk cc=data.getCharChunk();
	    processParameters( cc.getChars(), cc.getOffset(),
			       cc.getLength());
	}
    }


    public void mergeParameters( Parameters extra ) {
	
    }


    // XXX Generic code moved from RequestUtil - will be replaced
    // with more efficient code.
        /** Combine 2 hashtables into a new one.
     *  XXX Will move to the MimeHeaders equivalent for params.
     */
    public static Hashtable mergeParameters(Hashtable one, Hashtable two) {
	// Try some shortcuts
	if (one.size() == 0) {
	    return two;
	}

	if (two.size() == 0) {
	    return one;
	}

	Hashtable combined = (Hashtable) one.clone();

        Enumeration e = two.keys();

	while (e.hasMoreElements()) {
	    String name = (String) e.nextElement();
	    String[] oneValue = (String[]) one.get(name);
	    String[] twoValue = (String[]) two.get(name);
	    String[] combinedValue;

	    if (oneValue == null) {
		combinedValue = twoValue;
	    }

	    else {
		combinedValue = new String[oneValue.length + twoValue.length];

	        System.arraycopy(oneValue, 0, combinedValue, 0,
                    oneValue.length);
	        System.arraycopy(twoValue, 0, combinedValue,
                    oneValue.length, twoValue.length);
	    }

	    combined.put(name, combinedValue);
	}

	return combined;
    }
    
    public static void processFormData(String data, Hashtable parameters) {
        // XXX
        // there's got to be a faster way of doing this.
	if( data==null ) return; // no parameters
        StringTokenizer tok = new StringTokenizer(data, "&", false);
        while (tok.hasMoreTokens()) {
            String pair = tok.nextToken();
	    int pos = pair.indexOf('=');
	    if (pos != -1) {
		String key = unUrlDecode(pair.substring(0, pos));
		String value = unUrlDecode(pair.substring(pos+1,
							  pair.length()));
		String values[];
		if (parameters.containsKey(key)) {
		    String oldValues[] = (String[])parameters.get(key);
		    values = new String[oldValues.length + 1];
		    for (int i = 0; i < oldValues.length; i++) {
			values[i] = oldValues[i];
		    }
		    values[oldValues.length] = value;
		} else {
		    values = new String[1];
		    values[0] = value;
		}
		parameters.put(key, values);
	    } else {
		// we don't have a valid chunk of form data, ignore
	    }
        }
    }

    // from RequestUtil
    public static Hashtable processFormData(byte data[]   ) {
	Hashtable postParameters =  new Hashtable();

	try {
	    String postedBody = new String(data, 0, data.length,
					   "8859_1");
	    
	    Parameters.processFormData( postedBody, postParameters);
	    return postParameters;
	} catch( UnsupportedEncodingException ex ) {
	    return postParameters;
	}
    }

    /** Decode a URL-encoded string. Inefficient.
     */
    private static String unUrlDecode(String data) {
	System.out.println("DECODING : " +data );
	StringBuffer buf = new StringBuffer();
	for (int i = 0; i < data.length(); i++) {
	    char c = data.charAt(i);
	    switch (c) {
	    case '+':
		buf.append(' ');
		break;
	    case '%':
		// XXX XXX 
		try {
		    buf.append((char) Integer.parseInt(data.substring(i+1,
                        i+3), 16));
		    i += 2;
		} catch (NumberFormatException e) {
                    String msg = "Decode error ";
		    // XXX no need to add sm just for that
		    // sm.getString("serverRequest.urlDecode.nfe", data);

		    throw new IllegalArgumentException(msg);
		} catch (StringIndexOutOfBoundsException e) {
		    String rest  = data.substring(i);
		    buf.append(rest);
		    if (rest.length()==2)
			i++;
		}
		
		break;
	    default:
		buf.append(c);
		break;
	    }
	}
	return buf.toString();
    }           

    // XXX Ugly, most be rewritten
    /** Process the POST data from a request.
     */
    public static int formContentLength( String contentType,
					 int contentLength )
    {

	if (contentType != null) {
            if (contentType.indexOf(";")>0)
                contentType=contentType.substring(0,contentType.indexOf(";"));
            contentType = contentType.toLowerCase().trim();
        }

	if (contentType != null &&
            contentType.startsWith("application/x-www-form-urlencoded")) {
	    
	    if( contentLength >0 ) return contentLength;
	}
	return 0;
    }

    

    
}