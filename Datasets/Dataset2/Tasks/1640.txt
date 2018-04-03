public final class ServletInputStreamFacade extends ServletInputStream {

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

import java.io.*;
import javax.servlet.*;
import org.apache.tomcat.core.*;
import org.apache.tomcat.util.*;

/**
 * This is the input stream returned by ServletRequest.getInputStream().
 * It is the adapter between the ServletInputStream interface expected
 * by webapps and Request.doRead() methods. 
 *
 * This will also deal with the "contentLength" limit.
 * <b>Important</b> Only the methods in ServletInputStream can be public.
 */
final class ServletInputStreamFacade extends ServletInputStream {
    private int bytesRead = 0;
    // Stop after reading ContentLength bytes. 
    private int limit = -1;
    private boolean closed=false;

    private Request reqA;
    
    ServletInputStreamFacade() {
    }

    void prepare() {
	int contentLength = reqA.getContentLength();
	//System.out.println("ContentLength= " + contentLength);
	if (contentLength != -1) {
	    limit=contentLength;
	}
	bytesRead=0;
    }
    
    void setRequest(Request reqA ) {
	this.reqA=reqA;
    }

    void recycle() {
	limit=-1;
	closed=false;
    }

    // -------------------- ServletInputStream methods 

    public int read() throws IOException {
	if( dL>0) debug("read() " + limit + " " + bytesRead );
	if(closed)
	    throw new IOException("Stream closed");
	if (limit == -1) {
	    // Ask the adapter for more data. We are in the 'no content-length'
	    // case - i.e. chunked encoding ( acording to http spec CL is required
	    // for everything else.
	    int rd=reqA.doRead();
	    if( rd<0 ) {
		limit=0; // no more bytes can be read.
	    } else {
		bytesRead++; // for statistics
	    }
	    return rd;
	}

	// We have a limit
	if (bytesRead >= limit)
	    return -1;
	
	bytesRead++;
	int rd=reqA.doRead();
	if( rd<0 ) {
	    limit=0; // adapter detected EOF, before C-L finished.
	    // trust the adapter - if it returns EOF it's unlikely it'll give us
	    // any more data
	}
	return rd;
    }

    public int read(byte[] b) throws IOException {
	return read(b, 0, b.length);
    }

    public int read(byte[] b, int off, int len) throws IOException {
	if( dL>0) debug("read(" +  len + ") " + limit + " " + bytesRead );
	if(closed)
	    throw new IOException("Stream closed");
	if (limit == -1) {
	    int numRead = reqA.doRead(b, off, len);
	    if (numRead > 0) {
		bytesRead += numRead;
	    }
	    if( numRead< 0 ) {
		// EOF - stop reading
		limit=0;
	    }
	    return numRead;
	}

	if (bytesRead >= limit) {
	    return -1;
	}

	if (bytesRead + len > limit) {
	    len = limit - bytesRead;
	}
	int numRead = reqA.doRead(b, off, len);
	if (numRead > 0) {
	    bytesRead += numRead;
	}
	return numRead;
    }
    

    public int readLine(byte[] b, int off, int len) throws IOException {
	return super.readLine(b, off, len);
    }

    /** Close the stream
     *  Since we re-cycle, we can't allow the call to super.close()
     *  which would permantely disable us.
     */
    public void close() {
	closed=true;
    }

    private static int dL=0;
    private void debug( String s ) {
	System.out.println("ServletInputStreamFacade: " + s );
    }
}