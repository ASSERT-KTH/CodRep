package org.apache.xerces.impl.xs.util;

/*
 * The Apache Software License, Version 1.1
 *
 *
 * Copyright (c) 1999-2001 The Apache Software Foundation.  All rights
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

package org.apache.xerces.impl.v2.util;

/**
 * format validation
 *
 * This class encodes/decodes hexadecimal data
 * @author Jeffrey Rodriguez
 * @version $Id$
 */
public final class  HexBin {
    static private final int  BASELENGTH   = 255;
    static private final int  LOOKUPLENGTH = 16;
    static private byte [] hexNumberTable       = new byte[BASELENGTH];
    static private byte [] lookUpHexAlphabet = new byte[LOOKUPLENGTH];


    static {
        for (int i = 0; i<BASELENGTH; i++ ) {
            hexNumberTable[i] = -1;
        }
        for ( int i = '9'; i >= '0'; i--) {
            hexNumberTable[i] = (byte) (i-'0');
        }
        for ( int i = 'F'; i>= 'A'; i--) {
            hexNumberTable[i] = (byte) ( i-'A' + 10 );
        }
        for ( int i = 'f'; i>= 'a'; i--) {
           hexNumberTable[i] = (byte) ( i-'a' + 10 );
        }

        for(int i = 0; i<10; i++ )
            lookUpHexAlphabet[i] = (byte) ('0'+i );
        for(int i = 10; i<=15; i++ )
            lookUpHexAlphabet[i] = (byte) ('A'+i -10);
    }

    /**
     * byte to be tested if it is Base64 alphabet
     *
     * @param octect
     * @return
     */
    static boolean isHex( byte octect ) {
        //shall we ignore white space? JEFF??
        return( hexNumberTable[octect] != -1 );
    }


    /**
     *       Array of bytes to check against Hex Table
     *
     * @param arrayOctect
     * @return
     */
    static boolean isArrayByteHex( byte[] arrayOctect ) {
        if (arrayOctect == null)
            return false;
        int length = arrayOctect.length;
        if (length % 2 != 0)
            return false;
        for( int i=0; i < length; i++ ){
            if( HexBin.isHex( arrayOctect[i] ) == false)
                return false;
       }
       return true;
   }

    public static boolean isHex( String isValidString ){
      if (isValidString == null)
        return false;
      return( isArrayByteHex( isValidString.getBytes()));
  }

    /**
     * array of byte to encode
     *
     * @param binaryData
     * @return return encode binary array
     */
    static public byte[] encode( byte[] binaryData ) {
        if (binaryData == null)
            return null;
        int lengthData   = binaryData.length;
        int lengthEncode = lengthData * 2;
        byte[] encodedData = new byte[lengthEncode];
        for( int i = 0; i<lengthData; i++ ){
            encodedData[i*2] = lookUpHexAlphabet[ binaryData[i] >> 4];
            encodedData[i*2+1] = lookUpHexAlphabet[ binaryData[i] & 0xf];
        }
        return encodedData;
    }

    static public  byte[] decode ( byte[]  binaryData ) {
        if (binaryData == null)
            return null;
        int lengthData   = binaryData.length;
        if (lengthData % 2 != 0)
            return null;

        int lengthDecode = lengthData / 2;
        byte[] decodedData = new byte[lengthDecode];
        for( int i = 0; i<lengthDecode; i++ ){
            decodedData[i] = (byte)((hexNumberTable[binaryData[i*2]] << 4) | hexNumberTable[binaryData[i*2+1]]);
        }
        return decodedData;
    }

    static public int getDecodedDataLength (byte[] hexData) {
        if (!isArrayByteHex(hexData))
            return -1;

        return hexData.length / 2;
    }
}