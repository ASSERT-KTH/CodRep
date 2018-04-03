Log loghelper = Log.getLog("tc_log", this);

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


package org.apache.tomcat.modules.server;

import org.apache.tomcat.core.*;
import org.apache.tomcat.util.http.*;
import org.apache.tomcat.util.buf.*;
import org.apache.tomcat.util.io.*;
import org.apache.tomcat.util.log.Log;
import java.io.*;
import java.net.*;
import java.util.*;

public class Http10 {
    private Socket socket;
    private boolean moreRequests = false;
    RecycleBufferedInputStream sin;
    protected OutputStream sout;

    byte[] buf;
    int bufSize=2048; // default
    int off=0;
    int count=0;
    public static final String DEFAULT_CHARACTER_ENCODING = "8859_1";

    protected static final int DEFAULT_HEAD_BUFFER_SIZE = 1024;
    protected byte[] oBuffer = new byte[DEFAULT_HEAD_BUFFER_SIZE];
    protected int oBufferCount = 0;

    static final byte CRLF[]= { (byte)'\r', (byte)'\n' };
    Log loghelper = new Log("tc_log", this);
    
    public Http10() {
        super();
	buf=new byte[bufSize];
    }

    public void setSocket(Socket socket) throws IOException {
	if( sin==null)
	    sin = new RecycleBufferedInputStream ( socket.getInputStream());
	else
	    sin.setInputStream( socket.getInputStream());
        this.socket = socket;
    	moreRequests = true;	
	sout=socket.getOutputStream();
    }

    public void recycle() {
	off=0;
	count=0;
	oBufferCount=0;
	if( sin!=null )  sin.recycle();
    }

    // -------------------- HTTP input methods --------------------
    
    public int doRead() throws IOException {
	return sin.read();
    }

    public int doRead(byte[] b, int off, int len) throws IOException {
	return sin.read(b, off, len);
    }

    /**
     * Reads header fields from the specified servlet input stream until
     * a blank line is encountered.
     * @param in the servlet input stream
     * @exception IllegalArgumentException if the header format was invalid 
     * @exception IOException if an I/O error has occurred
     */
    public int readHeaders( MimeHeaders headers )  throws IOException {
	// use pre-allocated buffer if possible
	off = count; // where the request line ended
	
	while (true) {
	    int start = off;

	    while (true) {
		int len = buf.length - off;

		if (len > 0) {
		    len = readLine(sin,buf, off, len);

		    if (len == -1) {
			return 400;
		    }
		}

		off += len;

		if (len == 0 || buf[off-1] == '\n') {
		    break;
		}

		// overflowed buffer, so temporarily expand and continue

		// XXX DOS - if the length is too big - stop and throw exception
		byte[] tmp = new byte[buf.length * 2];

		System.arraycopy(buf, 0, tmp, 0, buf.length);
		buf = tmp;
	    }

	    // strip off trailing "\r\n"
	    if (--off > start && buf[off-1] == '\r') {
		--off;
	    }

	    if (off == start) {
		break;
	    }
	    
	    // XXX this does not currently handle headers which
	    // are folded to take more than one line.
	    if( ! parseHeaderField(headers, buf, start, off - start) ) {
		// error parsing header
		return 200;
	    }
	}
	return 200;
    }

    /**
     * Parses a header field from a subarray of bytes.
     * @param b the bytes to parse
     * @param off the start offset of the bytes
     * @param len the length of the bytes
     * @exception IllegalArgumentException if the header format was invalid
     */
    public final boolean parseHeaderField(MimeHeaders headers, byte[] b,
					  int off, int len)
    {
	int start = off;
	byte c;

	while ((c = b[off++]) != ':' && c != ' ') {
	    if (c == '\n') {
		loghelper.log("Parse error, empty line: " +
			      new String( b, off, len ), Log.ERROR);
		return false;
	    }
	}

	int nS=start;
	int nE=off - start - 1;

	while (c == ' ') {
	    c = b[off++];
	}

	if (c != ':') {
	    loghelper.log("Parse error, missing : in  " +
			  new String( b, off, len ), Log.ERROR);
	    loghelper.log("Full  " + new String( b, 0, b.length ),
			  Log.ERROR);
	    return false;
	}

	while ((c = b[off++]) == ' ');

	headers.addValue( b, nS, nE).
	    setBytes(b, off-1, len - (off - start - 1));
	return true;
    }

    /** Parse a request line
     */
    public final int processRequestLine(MessageBytes methodMB,
					MessageBytes uriMB,
					MessageBytes queryMB,
					MessageBytes protocolMB)
	throws IOException
    {
	count = readLine(sin,buf, 0, buf.length);

	if (count < 0 ) {
	    return 400;
	}
	
	off=0;

	// if end of line is reached before we scan all 3 components -
	// we're fine, off=count and remain unchanged
	if( buf[count-1]!= '\r' && buf[count-1]!= '\n' ) {
	    return 414; //HttpServletResponse.SC_REQUEST_URI_TOO_LONG;
	}	    
	
	int startMethod=skipSpaces();
	int endMethod=findSpace();

	int startReq=skipSpaces();
	int endReq=findSpace();

	int startProto=skipSpaces();
	int endProto=findSpace();

	if( startReq < 0   ) {
	    // we don't have 2 "words", probably only method
	    // startReq>0 => method is fine, request has at least one char
	    return 400;
	}

	methodMB.setBytes( buf, startMethod, endMethod - startMethod );
	// optimization - detect common strings, no allocations
	// buf[startMethod] == 'g' ||, ignoreCase

	// the idea is that we don't allocate new strings - but set
	// to constants. ( probably not needed, it's has a tiny impact )
	if( buf[startMethod] == 'G') {
	    if( methodMB.equals( "GET" ))
		methodMB.setString("GET");
	}
	if( buf[startMethod] == 'P' ) {
	    if( methodMB.equals( "POST" ))
		methodMB.setString("POST");
	    if( methodMB.equals( "PUT" ))
		methodMB.setString("PUT");
	}

	if( endReq < 0 ) {
	    endReq=count;
	} else {
	    if( startProto > 0 ) {
		if( endProto < 0 ) endProto = count;
		protocolMB.setBytes( buf, startProto, endProto-startProto);
		if( protocolMB.equalsIgnoreCase( "http/1.0" ))
		    protocolMB.setString("HTTP/1.0");
		if( protocolMB.equalsIgnoreCase( "http/1.1" ))
		    protocolMB.setString("HTTP/1.1");
	    } else {
		protocolMB.setString("");
	    }
	}

	int qryIdx= findChar( '?', startReq, endReq );
	if( qryIdx <0 ) {
	    uriMB.setBytes(buf, startReq, endReq - startReq );
	    //= new String( buf, startReq, endReq - startReq );
	} else {
	    uriMB.setBytes( buf, startReq, qryIdx - startReq );
	    queryMB.setBytes( buf, qryIdx+1, endReq - qryIdx -1 );
	}

	// Perform URL decoding only if necessary
	if ((uriMB.indexOf('%') >= 0) || (uriMB.indexOf('+') >= 0)) {
	    try {
		uriMB.unescapeURL();
	    } catch (Exception e) {
		return 400;
	    }
	}

	// XXX what about query strings ?
	
	return 200;
    }

    // -------------------- Output methods --------------------

    /** Format and send the output headers
     */
    public void sendHeaders(MimeHeaders headers)  throws IOException 
    {
	int count=headers.size();
	for( int i=0; i<count; i++ ) {
	    // response headers are set by the servlet, so probably we have
	    // only Strings.
	    // XXX date, cookies, etc shoud be extracted from response
	    printHead( headers.getName( i ).toString() );
	    printHead(": ");
	    printHead( headers.getValue( i ).toString() );
	    printHead("\r\n");
	}
	
	printHead( "\r\n" );

	sout.write( oBuffer, 0, oBufferCount );
	sout.flush();
    }

    /** Needed for AJP  support - the only difference between AJP response and
	HTTP response is the status line
    */
    public void sendStatus( int status, String message )
	throws IOException
    {
	printHead("HTTP/1.0 ");
	switch( status ) {
	case 200: printHead("200");
	    break;
	case 400: printHead("400");
	    break;
	case 404: printHead("404");
	    break;
	    
	default:
	    printHead(String.valueOf(status));
	}
	if(message!=null) {
	    printHead(" ");
	    printHead(message);
	}
	printHead("\r\n");
    }


    public void setHttpHeaders(Request req, MimeHeaders headers) {
	// Hack: set Date header.
	// This method is overriden by ajp11, ajp12 - so date will not be set
	// for any of those ( instead the server will generate the date )
	// This avoids redundant setting of date ( very expensive ).
	// XXX XXX Check if IIS, NES do generate the date
	if( false ) {
	    headers.setValue(  "Date" ).setTime( System.currentTimeMillis());
	}
	
	// Servlet Engine header will be set per/adapter - smarter adapters will
	// not send it every time ( have it in C side ), and we may also want
	// to add informations about the adapter used 
	if( req.getContext() != null)
	    headers.setValue("Servlet-Engine").setString(
		      req.getContext().getEngineHeader());
    }

    
    public void doWrite( byte buffer[], int pos, int count)
	throws IOException
    {
	sout.write( buffer, pos, count);
    }

    // -------------------- Parsing Utils --------------------
    /** Advance to first non-whitespace
     */
    private  final int skipSpaces() {
	while (off < count) {
	    if ((buf[off] != (byte) ' ') 
		&& (buf[off] != (byte) '\t')
		&& (buf[off] != (byte) '\r')
		&& (buf[off] != (byte) '\n')) {
		return off;
	    }
	    off++;
	}
	return -1;
    }

    /** Advance to the first whitespace character
     */
    private  int findSpace() {
	while (off < count) {
	    if ((buf[off] == (byte) ' ') 
		|| (buf[off] == (byte) '\t')
		|| (buf[off] == (byte) '\r')
		|| (buf[off] == (byte) '\n')) {
		return off;
	    }
	    off++;
	}
	return -1;
    }

    /** Find a character, no side effects
     */
    private  int findChar( char c, int start, int end ) {
	byte b=(byte)c;
	int offset = start;
	while (offset < end) {
	    if (buf[offset] == b) {
		return offset;
	    }
	    offset++;
	}
	return -1;
    }

    // cut&paste from ServletInputStream - but it's as inefficient as before
    public int readLine(InputStream in, byte[] b, int off, int len)
	throws IOException
    {
	if (len <= 0) {
	    return 0;
	}
	int count = 0, c;

	while ((c = in.read()) != -1) {
	    b[off++] = (byte)c;
	    count++;
	    if (c == '\n' || count == len) {
		break;
	    }
	}
	return count > 0 ? count : -1;
    }

    // From BufferedServletOutputStream
    // XXX will be moved in a new in/out system, temp. code
    // Right now it's not worse than BOS
    public void printHead( String s ) {
	if (s==null) s="null";

	int len = s.length();
	for (int i = 0; i < len; i++) {
	    char c = s.charAt (i);
	    
	    //
	    // XXX NOTE:  This is clearly incorrect for many strings,
	    // but is the only consistent approach within the current
	    // servlet framework.  It must suffice until servlet output
	    // streams properly encode their output.
	    //
	    if ((c & 0xff00) != 0) {	// high order byte must be zero
		// XXX will go away after we change the I/O system
		loghelper.log("Header character is not iso8859_1, " +
			      "not supported yet: " + c, Log.ERROR ) ;
	    }
	    if( oBufferCount >= oBuffer.length ) {
		byte bufferNew[]=new byte[ oBuffer.length * 2 ];
		System.arraycopy( oBuffer,0, bufferNew, 0, oBuffer.length );
		oBuffer=bufferNew;
	    }
	    oBuffer[oBufferCount] = (byte)c;
	    oBufferCount++;
	}
    }    


}