if(pos >= blen) {

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

import java.io.*;
import java.net.*;
import java.util.*;
import org.apache.tomcat.core.*;
import org.apache.tomcat.util.*;

public class Ajp13
{
    public static final int MAX_PACKET_SIZE=8192;
    public static final int H_SIZE=4;

    public static final int  MAX_READ_SIZE = MAX_PACKET_SIZE - H_SIZE - 2;
    public static final int  MAX_SEND_SIZE = MAX_PACKET_SIZE - H_SIZE - 4;

    public static final byte JK_AJP13_FORWARD_REQUEST   = 2;
    public static final byte JK_AJP13_SHUTDOWN          = 7;
	
    public static final byte JK_AJP13_SEND_BODY_CHUNK   = 3;
    public static final byte JK_AJP13_SEND_HEADERS      = 4;
    public static final byte JK_AJP13_END_RESPONSE      = 5;
    
    public static final int SC_RESP_CONTENT_TYPE        = 0xA001;
    public static final int SC_RESP_CONTENT_LANGUAGE    = 0xA002;
    public static final int SC_RESP_CONTENT_LENGTH      = 0xA003;
    public static final int SC_RESP_DATE                = 0xA004;
    public static final int SC_RESP_LAST_MODIFIED       = 0xA005;
    public static final int SC_RESP_LOCATION            = 0xA006;
    public static final int SC_RESP_SET_COOKIE          = 0xA007;
    public static final int SC_RESP_SET_COOKIE2         = 0xA008;
    public static final int SC_RESP_SERVLET_ENGINE      = 0xA009;
    public static final int SC_RESP_STATUS              = 0xA00A;
    public static final int SC_RESP_WWW_AUTHENTICATE    = 0xA00B;
    
    public static final byte JK_AJP13_GET_BODY_CHUNK = 6;
	
    public static final byte SC_A_CONTEXT       = 1;
    public static final byte SC_A_SERVLET_PATH  = 2;
    public static final byte SC_A_REMOTE_USER   = 3;
    public static final byte SC_A_AUTH_TYPE     = 4;
    public static final byte SC_A_QUERY_STRING  = 5;
    public static final byte SC_A_JVM_ROUTE     = 6;
    public static final byte SC_A_SSL_CERT      = 7;
    public static final byte SC_A_SSL_CIPHER    = 8;
    public static final byte SC_A_SSL_SESSION   = 9;
    public static final byte SC_A_REQ_ATTRIBUTE = 10;
    public static final byte SC_A_ARE_DONE      = (byte)0xFF;

    public static final String []methodTransArray = {
        "OPTIONS",
        "GET",
        "HEAD",
        "POST",
        "PUT",
        "DELETE",
        "TRACE"
    };
    
    public static final String []headerTransArray = {
        "accept",
        "accept-charset",
        "accept-encoding",
        "accept-language",
        "authorization",
        "connection",
        "content-type",
        "content-length",
        "cookie",
        "cookie2",
        "host",
        "pragma",
        "referer",
        "user-agent"
    };

    OutputStream out;
    InputStream in;
	
    Ajp13Packet outBuf=new Ajp13Packet( MAX_PACKET_SIZE );;
    Ajp13Packet inBuf=new Ajp13Packet( MAX_PACKET_SIZE );;

    byte []bodyBuff = new byte[MAX_READ_SIZE];
    int blen;
    int pos;

    public Ajp13() 
    {
        super();
    }

    public void setSocket( Socket socket ) throws IOException {
	socket.setSoLinger( true, 100);
	out = socket.getOutputStream();
	in = socket.getInputStream();
	pos=0;
    }

    public int receiveNextRequest(Request req) throws IOException 
    {
	int err = receive(inBuf);
	if(err < 0) {
	    return 500;
	}
	
	// XXX right now the only incoming packet is "new request"
	// We need to deal with arbitrary calls
	int type = (int)inBuf.getByte();
	switch(type) {
	    
	case JK_AJP13_FORWARD_REQUEST:
	    return decodeRequest(req, inBuf);

	case JK_AJP13_SHUTDOWN:
	    return -2;
	}
	return 200;
    }

    private int decodeRequest( Request req, Ajp13Packet msg ) throws IOException
    {
	
        boolean isSSL = false;
        byte bsc;
        int  hCount = 0;

        /*
         * Read the method and translate it to a String
         */
        bsc        = msg.getByte();
        req.method().setString( methodTransArray[(int)bsc - 1] );
        req.setProtocol( msg.getString());
        req.requestURI().setString(  msg.getString());

        req.setRemoteAddr( msg.getString());
        req.setRemoteHost( msg.getString());
        req.setServerName( msg.getString());
        req.setServerPort( msg.getInt());

	bsc        = msg.getByte();
        if(bsc != 0) {
            isSSL = true;
        }

	// Decode headers
	MimeHeaders headers=req.getMimeHeaders();
	hCount     = msg.getInt();
        for(int i = 0 ; i < hCount ; i++) {
            String hName = null;

            int isc = msg.peekInt();
            int hId = isc & 0x000000FF;

            isc &= 0x0000FF00;
            if(0x0000A000 == isc) {
                msg.getInt();
                hName = headerTransArray[hId - 1];
            } else {
                hName = msg.getString().toLowerCase();
            }

            String hValue = msg.getString();
            headers.addValue( hName ).setString( hValue );
        }

        for(bsc = msg.getByte() ;
            bsc != SC_A_ARE_DONE ;
            bsc = msg.getByte()) {
            switch(bsc) {
	    case SC_A_CONTEXT      :
		//		contextPath = msg.getString();
                break;
		
	    case SC_A_SERVLET_PATH :
		//log("SC_A_SERVLET_PATH not in use " + msg.getString());
                break;
		
	    case SC_A_REMOTE_USER  :
		req.setRemoteUser( msg.getString());
                break;
		
	    case SC_A_AUTH_TYPE    :
		req.setAuthType( msg.getString());
                break;
		
	    case SC_A_QUERY_STRING :
		req.queryString().setString( msg.getString());
                break;
		
	    case SC_A_JVM_ROUTE    :
		req.setJvmRoute(msg.getString());
                break;
		
	    case SC_A_SSL_CERT     :
		isSSL = true;
		req.setAttribute("javax.servlet.request.X509Certificate",
				 msg.getString());
                break;
		
	    case SC_A_SSL_CIPHER   :
		isSSL = true;
		req.setAttribute("javax.servlet.request.cipher_suite",
				 msg.getString());
                break;
		
	    case SC_A_SSL_SESSION  :
		isSSL = true;
		req.setAttribute("javax.servlet.request.ssl_session",
				  msg.getString());
                break;
		
	    case SC_A_REQ_ATTRIBUTE :
		isSSL = true;
		req.setAttribute(msg.getString(), msg.getString());
                break;

	    default:
		return 500;
            }
        }

        if(isSSL) {
            req.scheme().setString("https");
        }

	MessageBytes clB=headers.getValue("content-length");
        int contentLength = (clB==null) ? -1 : clB.getInt();
    	if(contentLength > 0) {
	    req.setContentLength( contentLength );
	    /* Read present data */
	    int err = receive(msg);
            if(err < 0) {
            	return 500;
	    }
	    
	    blen = msg.peekInt();
	    msg.getBytes(bodyBuff);
    	}
    
        return 200;
    }
    
    public int doRead() throws IOException 
    {
        if(pos > blen) {
            refeelReadBuffer();
        }
        return bodyBuff[pos++];
    }
    
    public int doRead(byte[] b, int off, int len) throws IOException 
    {
        // XXXXXX Stupid, but the whole thing must be rewriten ( see super()! )
        for(int i = off ; i < (len + off) ; i++) {
            int a = doRead();
            if(-1 == a) {
                return i-off;
            }
            b[i] = (byte)a;
        }
        
        return len;
    }
    
    public void recycle() 
    {
    }
    
    public void refeelReadBuffer() throws IOException 
    {
	inBuf.reset();
	Ajp13Packet msg = inBuf;
	msg.appendByte(JK_AJP13_GET_BODY_CHUNK);
	msg.appendInt(MAX_READ_SIZE);
	send(msg);
	
	int err = receive(msg);
        if(err < 0) {
	    throw new IOException();
	}
	
    	blen = msg.peekInt();
    	pos = 0;
    	msg.getBytes(bodyBuff);
    }    

    // ==================== Output ====================
    
    // XXX if more headers that MAX_SIZE, send 2 packets!   
    public void sendHeaders(int status, MimeHeaders headers) throws IOException 
    {
	outBuf.reset();
        Ajp13Packet msg=outBuf;
        msg.reset();

        msg.appendByte(JK_AJP13_SEND_HEADERS);
        msg.appendInt(status);
        msg.appendString("");
        
        msg.appendInt(headers.size());
        
        Enumeration e = headers.names();
        while(e.hasMoreElements()) {
            String headerName = (String)e.nextElement();            
            int sc = headerNameToSc(headerName);
            if(-1 != sc) {
                msg.appendInt(sc);
            } else {
                msg.appendString(headerName);
            }
            msg.appendString(headers.getHeader(headerName));
        }

        msg.end();
        send(msg);
    } 
         
    public void finish() throws IOException 
    {
	outBuf.reset();
        Ajp13Packet msg = outBuf;
        msg.reset();
        msg.appendByte(JK_AJP13_END_RESPONSE);
        msg.appendByte((byte)1);        
        msg.end();
        send(msg);
    }
    
    protected int headerNameToSc(String name)
    {       
        switch(name.charAt(0)) {
	case 'c':
	case 'C':
	    if(name.equalsIgnoreCase("Content-Type")) {
		return SC_RESP_CONTENT_TYPE;
	    } else if(name.equalsIgnoreCase("Content-Language")) {
		return SC_RESP_CONTENT_LANGUAGE;
	    } else if(name.equalsIgnoreCase("Content-Length")) {
		return SC_RESP_CONTENT_LENGTH;
	    }
            break;
            
	case 'd':
	case 'D':
	    if(name.equalsIgnoreCase("Date")) {
                    return SC_RESP_DATE;
	    }
            break;
            
	case 'l':
	case 'L':
	    if(name.equalsIgnoreCase("Last-Modified")) {
		return SC_RESP_LAST_MODIFIED;
	    } else if(name.equalsIgnoreCase("Location")) {
		return SC_RESP_LOCATION;
	    }
            break;

	case 's':
	case 'S':
	    if(name.equalsIgnoreCase("Set-Cookie")) {
		return SC_RESP_SET_COOKIE;
	    } else if(name.equalsIgnoreCase("Set-Cookie2")) {
		return SC_RESP_SET_COOKIE2;
	    }
            break;
            
	case 'w':
	case 'W':
	    if(name.equalsIgnoreCase("WWW-Autheticate")) {
		return SC_RESP_WWW_AUTHENTICATE;
	    }
            break;          
        }
        
        return -1;
    }

    public void doWrite(  byte b[], int off, int len) throws IOException 
    {
	int sent = 0;
	while(sent < len) {
	    int to_send = len - sent;
	    to_send = to_send > MAX_SEND_SIZE ? MAX_SEND_SIZE : to_send;

	    outBuf.reset();
	    Ajp13Packet buf = outBuf;
	    buf.reset();
	    buf.appendByte(JK_AJP13_SEND_BODY_CHUNK);	        	
	    buf.appendBytes(b, off + sent, to_send);	        
	    send(buf);
	    sent += to_send;
	}
    }
    

    public int receive(Ajp13Packet msg) throws IOException {
	byte b[]=msg.getBuff();
	
	int rd=in.read( b, 0, H_SIZE );
	if( rd<=0 ) {
	    //	    System.out.println("Rd header returned: " + rd );
	    return rd;
	}
	
	int len=msg.checkIn();
	
	// XXX check if enough space - it's assert()-ed !!!
	// Can we have only one read ( with unblocking, it can read all at once - but maybe more ) ?
	//???	len-=4; // header
	
	rd=in.read( b, 4, len );
	if( rd != len ) {
	    System.out.println( "Incomplete read, deal with it " + len + " " + rd);
	    // ??? log
	}
	// 	msg.dump( "Incoming");
	return rd;
	//    System.out.println( "Incoming Packet len=" + len);
    }
	
    public void send( Ajp13Packet msg ) throws IOException {
	msg.end();
	byte b[]=msg.getBuff();
	int len=msg.getLen();
	out.write( b, 0, len );
    }
	
    public void close() throws IOException {
	if(null != out) {        
	    out.close();
	}
	if(null !=in) {
	    in.close();
	}
    }

    /** Encapsulated messages passed between Tomcat and Web servers
     */
    public static class Ajp13Packet {
	// previous name: MsgBuff
	byte buff[];
	int len;
	int pos;
	int maxlen;
	
	public Ajp13Packet( int size ) {
	    buff=new byte[size];
	    maxlen=size;
	}
	
	public Ajp13Packet( byte b[] ) {
	    buff=b;
	    maxlen=b.length;
	}
	
	public byte[] getBuff() {
	    return buff;
	}
	
	public void setBuff(byte[] b) {
	    buff=b;
	    maxlen = b.length;
	}
	
	public int getLen() {
	    return len;
	}
	
	public int getMaxLen() {
	    return maxlen;
	}
	
	/** Verify the buffer and read the len
	 */
	public int checkIn() {
	    pos=4;
	    int mark=BuffTool.getInt( buff,0 );
	    len=BuffTool.getInt( buff,2 );
	    if( mark != 0x1234 ) {
		System.out.println("BAD packet " + mark);
		dump( "In: " );
		return -1;
	    }
	    return len;
	}
	
	public void reset() {
	    len=4;
	    pos=4;
	    buff[0]=(byte)'A';
	    buff[1]=(byte)'B';
	}
	
	public void end() {
	    len=pos;
	    setInt( 2, len-4 );
	}
	
	public void setInt(int bpos, int val ) {
	    BuffTool.addInt( buff, bpos, val );
	}
	
	public void appendByte( byte val ) {
	    buff[pos] = val;
	    pos++;
	}
	
	public void appendInt( int val ) {
	    BuffTool.addInt( buff, pos, val );
	    pos+=2;
	}
	
	public void appendString( String val ) {
	    pos=BuffTool.addString( buff, pos, val );
	}
	
	public void appendBytes( byte b[], int off, int len ) {
	    BuffTool.addInt( buff, pos, len );
	    pos+=2;
	    if( pos + len > buff.length ) {
		System.out.println("Buffer overflow " + buff.length + " " + pos + " " + len );
	    }
	    System.arraycopy( b, off, buff, pos, len);
	    buff[pos+len]=0;
	    pos+=len;
	    pos++;
	}

	public int getInt() {
	    int res=BuffTool.getInt( buff, pos );
	    pos+=2;
	    return res;
	}

	public int peekInt() {
	    return BuffTool.getInt( buff, pos );
	}

	public byte getByte() {
	    byte res = buff[pos];
	    pos++;
	    return res;
	}

	public byte peekByte() {
	    return buff[pos];
	}

	public String getString() throws java.io.UnsupportedEncodingException {
	    int ll= getInt();
	    if( (ll == 0xFFFF) || (ll==-1) ) {
		//	    System.out.println("null string " + ll);
		return null;
	    }
	    String s=BuffTool.getString( buff, pos, ll );
	    pos +=ll;
	    pos++;
	    return s;
	}

	public int getBytes(byte dest[]) {
	    int ll= getInt();
	    if( ll > buff.length ) {
		System.out.println("XXX Assert failed, buff too small ");
	    }
	
	    if( (ll == 0xFFFF) || (ll==-1) ) {
		System.out.println("null string " + ll);
		return 0;
	    }

	    System.arraycopy( buff, pos,  dest, 0, ll );
	    pos +=ll;
	    pos++; // ??? 
	    return ll;
	}

	private String hex( int x ) {
	    //	    if( x < 0) x=256 + x;
	    String h=Integer.toHexString( x );
	    if( h.length() == 1 ) h = "0" + h;
	    return h.substring( h.length() - 2 );
	}

	private void hexLine( int start ) {
	    for( int i=start; i< start+16; i++ ) {
		System.out.print( hex( buff[i] ) + " ");
	    }
	    System.out.print(" | ");
	    for( int i=start; i< start+16; i++ ) {
		if( Character.isLetterOrDigit( (char)buff[i] ))
		    System.out.print( new Character((char)buff[i]) );
		else
		    System.out.print( "." );
	    }
	    System.out.println();
	}
    
	public void dump(String msg) {
	    System.out.println( msg + ": " + buff + " " + pos +"/" + len + "/" + maxlen );

	    for( int j=0; j<len + 16; j+=16 )
		hexLine( j );
	
	    System.out.println();
	}
    }


}