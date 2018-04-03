return bb.getEnd();

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

import java.io.Writer;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.io.IOException;
import java.io.UnsupportedEncodingException;

import java.util.Hashtable;

import org.apache.tomcat.util.buf.*;

/**
 * The buffer used by tomcat response. It allows writting chars and
 * bytes. It does the mixing in order to implement ServletOutputStream
 * ( which has both byte and char methods ) and to allow a number of
 * optimizations (like a jsp pre-computing the byte[], but using char for
 * non-static content).
 *
 * @author Costin Manolache
 */
public final class OutputBuffer extends Writer
    implements ByteChunk.ByteOutputChannel, CharChunk.CharOutputChannel 
        // sink for conversion bytes[]
{
    public static final String DEFAULT_ENCODING="ISO-8859-1";
    public static final int DEFAULT_BUFFER_SIZE = 8*1024;
    private int defaultBufferSize = DEFAULT_BUFFER_SIZE;
    private int defaultCharBufferSize = DEFAULT_BUFFER_SIZE / 2 ;

    // The buffer can be used for byte[] and char[] writing
    // ( this is needed to support ServletOutputStream and for
    // efficient implementations of templating systems )
    public final int INITIAL_STATE=0;
    public final int CHAR_STATE=1;
    public final int BYTE_STATE=2;
    private int state=0;

    static final int debug=0;

    // statistics
    private int bytesWritten = 0;
    private int charsWritten;
    
    private boolean closed=false;

    /** The buffer
     */
    private ByteChunk bb;
    private CharChunk cb;
    
    String enc;
    boolean gotEnc=false;

    private Response resp;
    private Request req;
    private ContextManager cm;
    
    public OutputBuffer() {
	this( DEFAULT_BUFFER_SIZE );
    }

    public OutputBuffer(int size) {
	//	buf=new byte[size];
	bb=new ByteChunk( size );
	bb.setLimit( size );
	bb.setByteOutputChannel( this );
 	cb=new CharChunk( size );
	cb.setCharOutputChannel( this );
	cb.setLimit( size );
    }

    public OutputBuffer(Response resp) {
	this( DEFAULT_BUFFER_SIZE );
	setResponse( resp );
    }

    public void setResponse( Response resp ) {
	this.resp=resp;
	req=resp.getRequest();
	cm=req.getContextManager();
    }

    public byte[] getBuffer() {
	return bb.getBuffer();
    }

    /** Return the first available position in the byte buffer
     *( or the number of bytes written ).
     *  @deprecated Used only in Ajp13Packet for a hack
     */
    public int getByteOff() {
	return bb.getOffset();
    }

    /** Set the write position in the byte buffer
     *  @deprecated Used only in Ajp13Packet for a hack
     */
    public void setByteOff(int c) {
	bb.setOffset(c);
    }

    void log( String s ) {
	System.out.println("OutputBuffer: " + s );
    }

    /** Sends the buffer data to the client output, checking the
	state of Response and calling the right interceptors.
    */
    public void realWriteBytes(byte buf[], int off, int cnt )
	throws IOException
    {
	if( debug > 2 ) log( "realWrite(b, " + off + ", " + cnt + ") " + resp);
	if( closed ) return;
	if( resp==null ) return;
	// If this is the first write ( or flush )
	if (!resp.isBufferCommitted()) {
	    resp.endHeaders();
	}
	// If we really have something to write
	if( cnt>0 ) {
	    // call the beforeCommit callback
	    BaseInterceptor reqI[]= req.getContainer().
		getInterceptors(Container.H_beforeCommit);
	    for( int i=0; i< reqI.length; i++ ) {
		reqI[i].beforeCommit( req, resp );
	    }

	    // real write to the adapter
	    resp.doWrite( buf, off, cnt );
	}
    }
    
    public void recycle() {
	if( debug > 0 ) log("recycle()");
	state=INITIAL_STATE;
	bytesWritten=0;
	charsWritten=0;
	
	cb.recycle();
	bb.recycle(); 
        closed=false;
	if( conv!= null ) {
	    conv.recycle();
	}
    }

    // -------------------- Adding bytes to the buffer -------------------- 
    // Like BufferedOutputStream, without sync

    public void write(byte b[], int off, int len) throws IOException {
	if( state==CHAR_STATE )
	    cb.flushBuffer();
	state=BYTE_STATE;
	writeBytes( b, off, len );
    }

    private void writeBytes(byte b[], int off, int len) throws IOException {
        if( closed  ) return;
	if( debug > 0 ) log("write(b,off,len)");

	bb.append( b, off, len );
	bytesWritten +=len;

	// if called from within flush(), then immediately flush
	// remaining bytes
	if (doFlush) {
	    bb.flushBuffer();
	}

	return;
    }

    // XXX Char or byte ?
    public void writeByte(int b) throws IOException {
	if( state==CHAR_STATE )
	    cb.flushBuffer();
	state=BYTE_STATE;
	if( debug > 0 ) log("write(b)");

	bb.append( (byte)b );
	bytesWritten++;
    }


    // -------------------- Adding chars to the buffer

    public void write( int c ) throws IOException {
	state=CHAR_STATE;
	if( debug > 0 ) log("writeChar(b)");
	cb.append( (char )c );
	charsWritten++;
    }

    public void write( char c[] ) throws IOException {
	write( c, 0, c.length );
    }

    public void write(char c[], int off, int len) throws IOException {
	state=CHAR_STATE;
	if( debug > 0 ) log("write(c,off,len)" + cb.getLength() + " " +
			    cb.getLimit());

	cb.append( c, off, len );
	charsWritten += len;
    }

    public void write( StringBuffer sb ) throws IOException {
	state=CHAR_STATE;
	if( debug > 1 ) log("write(s,off,len)");
	int len=sb.length();
	charsWritten += len;

	cb.append( sb );
    }

    /** Append a string to the buffer
     */
    public void write(String s, int off, int len) throws IOException {
	state=CHAR_STATE;
	if( debug > 1 ) log("write(s,off,len)");
	charsWritten += len;
	if (s==null) s="null";

	cb.append( s, off, len );
    }

    public void write(String s) throws IOException {
	state=CHAR_STATE;
	if (s==null) s="null";
	write( s, 0, s.length() );
    } 

    public void flushChars() throws IOException {
     	if( debug > 0 ) log("flushChars() " + cb.getLength());
	cb.flushBuffer();
	state=BYTE_STATE;
    }

    public boolean flushCharsNeeded() {
	return state == CHAR_STATE;
    }

    public void close() throws IOException {
      flush();
      closed =true;
    }

    private boolean doFlush = false;

    synchronized public void flush() throws IOException {
        doFlush = true;
        if( state==CHAR_STATE ){
            cb.flushBuffer();
            bb.flushBuffer();
	    state=BYTE_STATE;
        }else if (state==BYTE_STATE)
            bb.flushBuffer();
        else if (state==INITIAL_STATE)
            realWriteBytes( null, 0, 0 );       // nothing written yet
        doFlush = false;
    }

    Hashtable encoders=new Hashtable();
    C2BConverter conv;

    public void setEncoding(String s) {
	enc=s;
    }

    public void realWriteChars( char c[], int off, int len ) throws IOException {
	if( debug > 0 ) log("realWrite(c,o,l) " + cb.getOffset() + " " + len);
	if( !gotEnc ) setConverter();
	
	if( debug > 0 ) log("encoder:  " + conv + " " + gotEnc);
	conv.convert(c, off, len);
	conv.flushBuffer();	// ???
    }

    private void setConverter() {
	if( resp!=null ) 
	    enc = resp.getCharacterEncoding();
	gotEnc=true;
	if(enc==null) enc=DEFAULT_ENCODING;
	conv=(C2BConverter)encoders.get(enc);
	if(conv==null) {
	    try {
		conv=new C2BConverter(bb,enc);
		encoders.put(enc, conv);
	    } catch(IOException ex ) {
		conv=(C2BConverter)encoders.get(DEFAULT_ENCODING);
		if(conv==null) {
		    try {
			conv=new C2BConverter(bb, DEFAULT_ENCODING);
			encoders.put(DEFAULT_ENCODING, conv);
		    } catch( IOException e ) {}
		}
	    }
	}
    }
    
    // --------------------  BufferedOutputStream compatibility

    /** Real write - this buffer will be sent to the client
     */
    public void flushBytes() throws IOException {
	if( debug > 0 ) log("flushBytes() " + bb.getLength());
	bb.flushBuffer();
    }
    
    public int getBytesWritten() {
	return bytesWritten;
    }

    public int getCharsWritten() {
	return charsWritten;
    }

    /** True if this buffer hasn't been used ( since recycle() ) -
	i.e. no chars or bytes have been added to the buffer.  
    */
    public boolean isNew() {
	return bytesWritten==0 && charsWritten==0;
    }
    
    public void setBufferSize(int size) {
	if( size > bb.getLimit() ) {// ??????
	    bb.setLimit( size );
	}
    }

    public void reset() {
	//count=0;
	bb.recycle();
	bytesWritten=0;
        cb.recycle();
        charsWritten=0;
	gotEnc=false;
	enc=null;
    }

    public int getBufferSize() {
	return bb.getLimit();
    }
}