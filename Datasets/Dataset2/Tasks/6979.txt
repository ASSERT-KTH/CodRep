//	    log( "Recycle without conv ??");

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

import java.io.*;
import java.util.*;

/**
 * The buffer used by tomcat response. It allows writting chars and
 * bytes. It does the mixing in order to implement ServletOutputStream
 * ( which has both byte and char methods ) and to allow a number of
 * optimizations (like a jsp pre-computing the byte[], but using char for
 * non-static content).
 *
 * @author Costin Manolache
 */
public final class OutputBuffer extends Writer {
    public static final int DEFAULT_BUFFER_SIZE = 8*1024;
    int defaultBufferSize = DEFAULT_BUFFER_SIZE;
    int defaultCharBufferSize = DEFAULT_BUFFER_SIZE / 2 ;

    // The buffer can be used for byte[] and char[] writing
    // ( this is needed to support ServletOutputStream and for
    // efficient implementations of templating systems )
    public final int INITIAL_STATE=0;
    public final int CHAR_STATE=1;
    public final int BYTE_STATE=2;
    int state=0;

    static final int debug=0;
    int bytesWritten = 0;
    boolean closed=false;

    /** The buffer
     */
    public byte buf[];
    
    /**
     * The index one greater than the index of the last valid byte in 
     * the buffer. count==-1 for end of stream
     */
    public int count;


    Response resp;
    Request req;
    ContextManager cm;
    
    public OutputBuffer(Response resp) {
	buf=new byte[defaultBufferSize];
 	cbuf=new char[defaultCharBufferSize];
	this.resp=resp;
	req=resp.getRequest();
	cm=req.getContextManager();
    }

    void log( String s ) {
	System.out.println("OutputBuffer: " + s );
    }

    public void recycle() {
	if( debug > 0 ) log("recycle()");
	state=INITIAL_STATE;
	bytesWritten=0;
	charsWritten=0;
	ccount=0;
	count=0;
        closed=false;
	if( conv!= null ) {
	    conv.reset(); // reset ?
	} else {
	    log( "Recycle without conv ??");
	}
    }

    // -------------------- Adding bytes to the buffer -------------------- 
    // Like BufferedOutputStream, without sync

    public void write(byte b[], int off, int len) throws IOException {
	if( state==CHAR_STATE )
	    flushChars();
	state=BYTE_STATE;
	writeBytes( b, off, len );
    }

    public void writeBytes(byte b[], int off, int len) throws IOException {
        if( closed  ) return;
	if( debug > 0 ) log("write(b,off,len)");
	int avail=buf.length - count;

	bytesWritten += len;

	// fit in buffer, great.
	if( len <= avail ) {
	  // ??? should be < since if it's just barely full, we still
	  // want to flush now
	    System.arraycopy(b, off, buf, count, len);
	    count += len;
	}

	// Optimization:
	// If len-avail < length ( i.e. after we fill the buffer with
	// what we can, the remaining will fit in the buffer ) we'll just
	// copy the first part, flush, then copy the second part - 1 write
	// and still have some space for more. We'll still have 2 writes, but
	// we write more on the first.

	else if (len - avail < buf.length) {
	    /* If the request length exceeds the size of the output buffer,
    	       flush the output buffer and then write the data directly.
	       We can't avoid 2 writes, but we can write more on the second
	    */
	    System.arraycopy(b, off, buf, count, avail);
	    count += avail;
	    flushBytes();
	    
	    System.arraycopy(b, off+avail, buf, count, len - avail);
	    count+= len - avail;
	    bytesWritten += len - avail;
	}

	// len > buf.length + avail
	else {
	  flushBytes();
	  cm.doWrite( req, resp, b, off, len );
	}

	// if called from within flush(), then immediately flush
	// remaining bytes
	if (doFlush) {
	  flushBytes();
	}

	return;
    }

    // XXX Char or byte ?
    public void writeByte(int b) throws IOException {
	if( state==CHAR_STATE )
	    flushChars();
	state=BYTE_STATE;
	if( debug > 0 ) log("write(b)");
	if (count >= buf.length) {
	    flushBytes();
	}
	buf[count++] = (byte)b;
	bytesWritten++;
    }


    // -------------------- Adding chars to the buffer
    String enc;
    boolean gotEnc=false;
    public char cbuf[];
    /** character count - first free possition */
    public int ccount;
    int charsWritten;


    public void write( int c ) throws IOException {
	state=CHAR_STATE;
	if( debug > 0 ) log("writeChar(b)");
	if (ccount >= cbuf.length) {
	    flushChars();
	}
	cbuf[ccount++] = (char)c;
	charsWritten++;
    }

    public void write( char c[] ) throws IOException {
	write( c, 0, c.length );
    }

    public void write(char c[], int off, int len) throws IOException {
	state=CHAR_STATE;
	if( debug > 0 ) log("write(c,off,len)" + ccount + " " + len);
	int avail=cbuf.length - ccount;

	charsWritten += len;

	// fit in buffer, great.
	if( len <= avail ) {
	  // ??? should be < since if it's just barely full, we still
	  // want to flush now
	    System.arraycopy(c, off, cbuf, ccount, len);
	    ccount += len;
	    return;
	}

	if (len - avail < cbuf.length) {
	    /* If the request length exceeds the size of the output buffer,
    	       flush the output buffer and then write the data directly.
	       We can't avoid 2 writes, but we can write more on the second
	    */
	    System.arraycopy(c, off, cbuf, ccount, avail);
	    ccount += avail;
	    flushChars();
	    
	    System.arraycopy(c, off+avail, cbuf, ccount, len - avail);
	    ccount+= len - avail;
	    charsWritten += len - avail;
	    return;
	}

	// len > buf.length + avail
	flushChars();
	cWrite(  c, off, len );

	return;
    }

    private int min(int a, int b) {
	if (a < b) return a;
	return b;
    }

    public void write( StringBuffer sb ) throws IOException {
	state=CHAR_STATE;
	if( debug > 1 ) log("write(s,off,len)");
	int len=sb.length();
	charsWritten += len;

	int off=0;
	int b = off;
	int t = off + len;
	while (b < t) {
	    int d = min(cbuf.length - ccount, t - b);
	    sb.getChars( b, b+d, cbuf, ccount);
	    b += d;
	    ccount += d;
	    if (ccount >= cbuf.length)
		flushChars();
	}
	return;
    }

    public void write(String s, int off, int len) throws IOException {
	state=CHAR_STATE;
	if( debug > 1 ) log("write(s,off,len)");
	charsWritten += len;
	if (s==null) s="null";
	
	// different strategy: we can't write more then cbuf[]
	// because of conversions. Writing in 8k chunks is not bad.
	int b = off;
	int t = off + len;
	while (b < t) {
	    int d = min(cbuf.length - ccount, t - b);
	    s.getChars( b, b+d, cbuf, ccount);
	    b += d;
	    ccount += d;
	    if (ccount >= cbuf.length)
		flushChars();
	}
	return;
    }
    
    public void write(String s) throws IOException {
	state=CHAR_STATE;
	if (s==null) s="null";
	write( s, 0, s.length() );
    } 

    public void flushChars() throws IOException {
	if( debug > 0 ) log("flushChars() " + ccount);
	if( ccount > 0) {
	    cWrite(  cbuf, 0, ccount );
	    ccount=0;
	}
    }

    public void close() throws IOException {
      flush();
      closed =true;
    }

  private boolean doFlush = false;

    synchronized public void flush() throws IOException {
        doFlush = true;
        if( state==CHAR_STATE )
            flushChars();
        else if (state==BYTE_STATE)
            flushBytes();
        else if (state==INITIAL_STATE)
            cm.doWrite( req, resp, null, 0, 0 );       // nothing written yet
        doFlush = false;
    }

    Hashtable encoders=new Hashtable();
    WriteConvertor conv;

    void cWrite( char c[], int off, int len ) throws IOException {
	if( debug > 0 ) log("cWrite(c,o,l) " + ccount + " " + len);
	if( !gotEnc ) setConverter();
	
	if( debug > 0 ) log("encoder:  " + conv + " " + gotEnc);
	conv.write(c, off, len);
	conv.flush();	// ???
    }

    private void setConverter() {
	enc = resp.getCharacterEncoding();
	gotEnc=true;
	if(enc==null) enc="8859_1";
	conv=(WriteConvertor)encoders.get(enc);
	if(conv==null) {
	    IntermediateOutputStream ios=new IntermediateOutputStream(this);
	    try {
		conv=new WriteConvertor(ios,enc);
		encoders.put(enc, conv);
	    } catch(UnsupportedEncodingException ex ) {
		conv=(WriteConvertor)encoders.get("8859_1");
		if(conv==null) {
		    try {
			conv=new WriteConvertor(ios, "8859_1");
			encoders.put("8859_1", conv);
		    } catch( UnsupportedEncodingException e ) {}
		}
	    }
	}
    }
    
    // --------------------  BufferedOutputStream compatibility

    /** Real write - this buffer will be sent to the client
     */
    public void flushBytes() throws IOException {
	if( debug > 0 ) log("flushBytes() " + count);
	if( count > 0) {
	    cm.doWrite( req, resp, buf, 0, count );
	    count=0;
	}
    }
    
    public int getBytesWritten() {
	return bytesWritten;
    }

    public void setBufferSize(int size) {
	if( size > buf.length ) {
	    buf=new byte[size];
	}
    }

    public void reset() {
	count=0;
	bytesWritten=0;
        ccount=0;
        charsWritten=0;

    }

    public int getBufferSize() {
	return buf.length;
    }


    // -------------------- Utils

}

class WriteConvertor extends OutputStreamWriter {
    IntermediateOutputStream ios;
    
    /* Has a private, internal byte[8192]
     */
    public WriteConvertor( IntermediateOutputStream out, String enc )
	throws UnsupportedEncodingException
    {
	super( out, enc );
	ios=out;
    }

    public void close() throws IOException {
	// NOTHING
	// Calling super.close() would reset out and cb.
    }

    public void flush() throws IOException {
	// Will flushBuffer and out()
	// flushBuffer put any remaining chars in the byte[] 
	super.flush();
    }

    public void write(char cbuf[], int off, int len) throws IOException {
	// will do the conversion and call write on the output stream
	super.write( cbuf, off, len );
    }

    void reset() {
	ios.resetFlag=true;
	try {
	    //	    System.out.println("Reseting writer");
	    flush();
	} catch( Exception ex ) {
	    ex.printStackTrace();
	}
	ios.resetFlag=false;
    }
	
}


class IntermediateOutputStream extends OutputStream {
    OutputBuffer tbuff;
    boolean resetFlag=false;
    
    public IntermediateOutputStream(OutputBuffer tbuff) {
	this.tbuff=tbuff;
    }

    public void close() throws IOException {
	// shouldn't be called - we filter it out in writer
	System.out.println("close() called - shouldn't happen ");
	throw new IOException("close() called - shouldn't happen ");
    }

    public void flush() throws IOException {
	// nothing - write will go directly to the buffer,
	// we don't keep any state
    }

    public void write(byte cbuf[], int off, int len) throws IOException {
	//	System.out.println("IOS: " + len );
	// will do the conversion and call write on the output stream
	if( resetFlag ) {
	    //	    System.out.println("Reseting buffer ");
	} else {
	    tbuff.writeBytes( cbuf, off, len );
	}
    }

    public void write( int i ) throws IOException {
	System.out.println("write(int ) called - shouldn't happen ");
	throw new IOException("write(int ) called - shouldn't happen ");
    }
}
