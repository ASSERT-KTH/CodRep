super.println( str );

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

import org.apache.tomcat.util.StringManager;
import java.io.*;
import javax.servlet.ServletOutputStream;

/**
 *  Facade to the PrintWriter returned by Response.
 *  This will grow to include more support for JSPs ( and other templating
 *  systems ) buffering requirements, provide support for accounting
 *  and will allow more control over char-to-byte conversion ( if it proves
 *  that we spend too much time in that area ).
 *
 *  This will also help us control the multi-buffering ( since all writers have
 *  8k or more of un-recyclable buffers). 
 *
 * @author Costin Manolache [costin@eng.sun.com]
 */
public class ServletWriterFacade extends PrintWriter {
    Response resA;
    RequestImpl req;
    
    protected ServletWriterFacade( Writer w, Response resp ) {
	super( w );
	this.resA=resp;
	req=(RequestImpl)resA.getRequest();
    }

    // -------------------- Write methods --------------------

    public void flush() {
	in();
	super.flush();
	out();
    }

    public void print( String str ) {
	in();
	super.print( str );
	out(); 
   }

    public void println( String str ) {
	in();
	super.print( str );
	out(); 
   }

    public void write( char buf[], int offset, int count ) {
	in();
	super.write( buf, offset, count );
	out();
    }

    public void write( String str ) {
	in();
	super.write( str );
	out();
    }

    private void in() {
	req.setAccount( RequestImpl.ACC_IN_OUT, System.currentTimeMillis() );
    }

    private void out() {
	long l=System.currentTimeMillis();
	long l1=req.getAccount( RequestImpl.ACC_IN_OUT);
	long l3=req.getAccount( RequestImpl.ACC_OUT_COUNT);
	req.setAccount( RequestImpl.ACC_OUT_COUNT, l - l1 + l3 );
    }

    /** Reuse the object instance, avoid GC
     *  Called from BSOS
     */
    void recycle() {
    }

}
