final byte [] bTest = {(byte)'v', (byte)'a', (byte)'l', (byte)'i', (byte)'d'};

/*
 * The Apache Software License, Version 1.1
 *
 *
 * Copyright (c) 2000-2002 The Apache Software Foundation.  All rights 
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
 * 3. The end-user documentation included with the redistribution,
 *    if any, must include the following acknowledgment:  
 *       "This product includes software developed by the
 *        Apache Software Foundation (http://www.apache.org/)."
 *    Alternately, this acknowledgment may appear in the software itself,
 *    if and wherever such third-party acknowledgments normally appear.
 *
 * 4. The names "Xerces" and "Apache Software Foundation" must
 *    not be used to endorse or promote products derived from this
 *    software without prior written permission. For written 
 *    permission, please contact apache@apache.org.
 *
 * 5. Products derived from this software may not be called "Apache",
 *    nor may "Apache" appear in their name, without prior written
 *    permission of the Apache Software Foundation.
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
 * individuals on behalf of the Apache Software Foundation and was
 * originally based on software copyright (c) 1999, International
 * Business Machines, Inc., http://www.apache.org.  For more
 * information on the Apache Software Foundation, please see
 * <http://www.apache.org/>.
 */


package org.apache.xml.serialize;

import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.io.UnsupportedEncodingException;
import java.io.Writer;
import sun.io.CharToByteConverter;
import org.apache.xerces.util.EncodingMap;

/**
 * This class represents an encoding.
 *
 * @version $Id$
 */
public class EncodingInfo {

    // name of encoding as registered with IANA;
    // preferably a MIME name, but aliases are fine too.
    String ianaName;
    String javaName;
    int lastPrintable;
    // the charToByteConverter we test unusual characters
    // with
    CharToByteConverter fCToB = null;
    // is the converter null because it can't be instantiated
    // for some reason (perhaps we're running with insufficient authority as 
    // an applet?
    boolean fHaveTriedCToB = false;

    /**
     * Creates new <code>EncodingInfo</code> instance.
     */
    public EncodingInfo(String ianaName, String javaName, int lastPrintable) {
        this.ianaName = ianaName;
        this.javaName = EncodingMap.getIANA2JavaMapping(ianaName);
        this.lastPrintable = lastPrintable;
    }

    /**
     * Returns a MIME charset name of this encoding.
     */
    public String getIANAName() {
        return this.ianaName;
    }

    /**
     * Returns a writer for this encoding based on
     * an output stream.
     *
     * @return A suitable writer
     * @exception UnsupportedEncodingException There is no convertor
     *  to support this encoding
     */
    public Writer getWriter(OutputStream output)
        throws UnsupportedEncodingException {
        // this should always be true!
        if (javaName != null) 
            return new OutputStreamWriter(output, javaName);
        javaName = EncodingMap.getIANA2JavaMapping(ianaName);
        if(javaName == null) 
            // use UTF-8 as preferred encoding
            return new OutputStreamWriter(output, "UTF8");
        return new OutputStreamWriter(output, javaName);
    }
    /**
     * Checks whether the specified character is printable or not
     * in this encoding.
     *
     * @param ch a code point (0-0x10ffff)
     */
    public boolean isPrintable(char ch) {
        if(ch <= this.lastPrintable) 
            return true;
        
        if(fCToB == null) {
            if(fHaveTriedCToB) {
                // forget it; nothing we can do...
                return false;
            }
            // try and create it:
            try {
                fCToB = CharToByteConverter.getConverter(javaName);
            } catch(Exception e) {   
                // don't try it again...
                fHaveTriedCToB = true;
                return false;
            }
        }
        try {
            return fCToB.canConvert(ch); 
        } catch (Exception e) {
            // obviously can't use this converter; probably some kind of
            // security restriction
            fCToB = null;
            fHaveTriedCToB = false;
            return false;
        }
    }

    // is this an encoding name recognized by this JDK?
    // if not, will throw UnsupportedEncodingException
    public static void testJavaEncodingName(String name)  throws UnsupportedEncodingException {
        final byte [] bTest = {'v', 'a', 'l', 'i', 'd'};
        String s = new String(bTest, name);
    }
}