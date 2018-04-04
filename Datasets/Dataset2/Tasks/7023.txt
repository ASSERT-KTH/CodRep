public final class ServletOutputStreamFacade extends ServletOutputStream {

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

import org.apache.tomcat.core.*;
import org.apache.tomcat.util.*;
import java.io.*;
import javax.servlet.ServletOutputStream;

/**
 * 
 */
final class ServletOutputStreamFacade extends ServletOutputStream {
    protected boolean closed = false;

    Response resA;
    OutputBuffer ob;
    
    /** Encoding - first time print() is used.
	IMPORTANT: print() is _bad_, if you want to write Strings and mix
	bytes you'd better use a real writer ( it's faster ).
	But _don't_ use the servlet writer - since you'll not be able to write
	bytes.
    */
    String enc;
    /** True if we already called getEncoding() - cache result */
    boolean gotEnc=false;
    
    protected ServletOutputStreamFacade( Response resA) {
	this.resA=resA;
	ob=resA.getBuffer();
    }

    // -------------------- Write methods --------------------
    
    public void write(int i) throws IOException {
	ob.writeByte(i);
    }

    public void write(byte[] b) throws IOException {
	write(b,0,b.length);
    }
    
    public void write(byte[] b, int off, int len) throws IOException {
	ob.write( b, off, len );
    }

    // -------------------- Servlet Output Stream methods --------------------
    
    /** Alternate implementation for print, using String.getBytes(enc).
	It seems to be a bit faster for small strings, but it's 10..20% slower
	for larger texts ( nor very large - 5..10k )

	That seems to be mostly because of byte b[] - the writer has an
	internal ( and fixed ) buffer.

	Please use getWriter() if you want to send strings.
    */
    public void print(String s) throws IOException {
// 	if (s==null) s="null";
// 	byte b[]=null;
// 	if( !gotEnc ) {
// 	    enc = resA.getCharacterEncoding();
// 	    gotEnc=true;
// 	    if ( Constants.DEFAULT_CHAR_ENCODING.equals(enc) )
// 		enc=null;
// 	}
// 	if( enc==null) 
// 	    b=s.getBytes();
// 	else 
// 	    try {
// 		b=s.getBytes( enc );
// 	    } catch (java.io.UnsupportedEncodingException ex) {
// 		b=s.getBytes();
// 		enc=null;
// 	    } 
	
// 	write( b );
	ob.write(s);
    } 

    /** Will send the buffer to the client.
     */
    public void flush() throws IOException {
	if( ob.flushCharsNeeded() )
	    ob.flushChars();
	ob.flushBytes();
    }

    public void close() throws IOException {
	if( ob.flushCharsNeeded() )
	    ob.flushChars();
	ob.flushBytes();
	closed = true;
    }

    /** Reuse the object instance, avoid GC
     *  Called from BSOS
     */
    void recycle() {
	closed = false;
	enc=null;
	gotEnc=false;
    }
}
