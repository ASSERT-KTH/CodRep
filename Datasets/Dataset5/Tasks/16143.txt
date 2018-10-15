if ((XMLCharacterProperties.fgCharFlags[ch] & XMLCharacterProperties.E_NameCharFlag) == 0) {

/*
 * The Apache Software License, Version 1.1
 *
 *
 * Copyright (c) 1999,2000 The Apache Software Foundation.  All rights 
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

package org.apache.xerces.readers;

import org.apache.xerces.framework.XMLErrorReporter;
import org.apache.xerces.utils.ChunkyByteArray;
import org.apache.xerces.utils.ChunkyCharArray;
import org.apache.xerces.utils.QName;
import org.apache.xerces.utils.StringHasher;
import org.apache.xerces.utils.StringPool;
import org.apache.xerces.utils.XMLCharacterProperties;
import java.io.IOException;

/**
 * Reader for UCS-2 and UCS-4 encodings.
 * <p>
 * This reader is created by the UCSRecognizer class when it decides that the
 * byte stream is encoded in a format supported by this class.  This class
 * was intended to be another example of an encoding sensitive reader that
 * could take advantage of the system design to improve performance and reduce
 * resource consumption, but the actual performance tuning remains to be done.
 *
 * @version $Id$
 */
final class UCSReader extends XMLEntityReader implements StringPool.StringProducer {

    //
    // Constants
    //

    // debugging
    
    /** Set to true to debug UTF-16, big-endian. */
    private static final boolean DEBUG_UTF16_BIG = false;

    //
    // Scanner encoding enumeration
    //
    static final int
        E_UCS4B = 0,            // UCS-4 big endian
        E_UCS4L = 1,            // UCS-4 little endian
        E_UCS2B = 2,            // UCS-2 big endian with byte order mark
        E_UCS2L = 3,            // UCS-2 little endian with byte order mark
        E_UCS2B_NOBOM = 4,      // UCS-2 big endian without byte order mark
        E_UCS2L_NOBOM = 5;      // UCS-2 little endian without byte order mark
    //
    //
    //
    private ChunkyByteArray fData = null;
    private int fEncoding = -1;
    private StringPool fStringPool = null;
    private int fBytesPerChar = -1;
    private boolean fBigEndian = true;
    private ChunkyCharArray fStringCharArray = null;
    private boolean fCalledCharPropInit = false;
    //
    //
    //
    UCSReader(XMLEntityHandler entityHandler, XMLErrorReporter errorReporter, boolean sendCharDataAsCharArray, ChunkyByteArray data, int encoding, StringPool stringPool) throws Exception {
        super(entityHandler, errorReporter, sendCharDataAsCharArray);
        fCurrentOffset = (encoding == E_UCS2B || encoding == E_UCS2L) ? 2 : 0;
        fData = data;
        fEncoding = encoding;
        fStringPool = stringPool;
        fBytesPerChar = (fEncoding == E_UCS4B || fEncoding == E_UCS4L) ? 4 : 2;
        fBigEndian = fEncoding == E_UCS4B || fEncoding == E_UCS2B || fEncoding == E_UCS2B_NOBOM;
    }
    //
    //
    //
    private int getChar(int offset) throws IOException {
        int b0 = fData.byteAt(offset++) & 0xff;
        if (b0 == 0xff && fData.atEOF(offset))
            return -1;
        int b1 = fData.byteAt(offset++) & 0xff;
        if (fBytesPerChar == 4) {
            int b2 = fData.byteAt(offset++) & 0xff;
            int b3 = fData.byteAt(offset++) & 0xff;
            if (fBigEndian)
                return (b0<<24)+(b1<<16)+(b2<<8)+b3;
            else
                return (b3<<24)+(b2<<16)+(b1<<8)+b0;
        } else {
            if (fBigEndian)
                return (b0<<8)+b1;
            else
                return (b1<<8)+b0;
        }
    }
    /**
     *
     */
    public int addString(int offset, int length) {
        if (length == 0)
            return 0;
        return fStringPool.addString(this, offset, length);
    }
    /**
     *
     */
    public int addSymbol(int offset, int length) {
        if (length == 0)
            return 0;
        return fStringPool.addSymbol(this, offset, length, getHashcode(offset, length));
    }
    //
    //
    //
    public void append(XMLEntityHandler.CharBuffer charBuffer, int offset, int length) {
        int endOffset = offset + length;
        while (offset < endOffset) {
            int ch;
            try {
                ch = getChar(offset);
            }
            catch (IOException ex) {
                ch = 0; // REVISIT
            }
            charBuffer.append((char)ch);
            offset += fBytesPerChar;
        }
    }
    //
    //
    //
    public void releaseString(int offset, int length) {
        // nothing to do...
    }
    //
    //
    //
    public String toString(int offset, int length) {
        //
        // REVISIT - we need to cache this operation !!
        //
        if (fStringCharArray == null)
            fStringCharArray = new ChunkyCharArray(fStringPool);
        int newOffset = fStringCharArray.length();
        append(fStringCharArray, offset, length);
        int newLength = fStringCharArray.length() - newOffset;
        int stringIndex = fStringCharArray.addString(newOffset, newLength);
        return fStringPool.toString(stringIndex);
    }
    //
    //
    //
    private int getHashcode(int offset, int length) {
        int endOffset = offset + length;
        int hashcode = 0;
        while (offset < endOffset) {
            int ch;
            try {
                ch = getChar(offset);
            }
            catch (IOException ex) {
                ch = 0; // REVISIT
            }
            hashcode = StringHasher.hashChar(hashcode, ch);
            offset += fBytesPerChar;
        }
        return StringHasher.finishHash(hashcode);
    }
    //
    public boolean equalsString(int offset, int length, char[] strChars, int strOffset, int strLength) {
        int endOffset = offset + length;
        int slen = strLength;
        while (offset < endOffset) {
            if (slen-- == 0)
                return false;
            int ch;
            try {
                ch = getChar(offset);
            }
            catch (IOException ex) {
                ch = 0; // REVISIT
            }
            if (ch != strChars[strOffset++])
                return false;
            offset += fBytesPerChar;
        }
        return slen == 0;
    }
    //
    //
    //
    private static char[] fCharacters = new char[256];
    private int fCharDataLength = 0;
    private void appendCharData(int ch) {
        if (fCharacters.length == fCharDataLength) {
            char[] newchars = new char[fCharacters.length * 2];
            System.arraycopy(fCharacters, 0, newchars, 0, fCharacters.length);
            fCharacters = newchars;
        }
        fCharacters[fCharDataLength++] = (char)ch;
    }
    public void callCharDataHandler(int offset, int length, boolean isWhitespace) throws Exception {
        int endOffset = offset + length;
        boolean skiplf = false;
        while (offset < endOffset) {
            int ch = getChar(offset);
            // fix for Bug23: Element Data not normalized...
            if (skiplf) {
                skiplf = false;
                if (ch == 0x0A) {
                    offset += fBytesPerChar;
                    continue;
                }
            }
            if (ch == 0x0D) {
                skiplf = true;
                ch = 0x0A;
            }
            appendCharData(ch);
            offset += fBytesPerChar;
        }
        if (fSendCharDataAsCharArray) {
            if (isWhitespace)
                fCharDataHandler.processWhitespace(fCharacters, 0, fCharDataLength);
            else
                fCharDataHandler.processCharacters(fCharacters, 0, fCharDataLength);
        } else {
            int stringIndex = fStringPool.addString(new String(fCharacters, 0, fCharDataLength));
            if (isWhitespace)
                fCharDataHandler.processWhitespace(stringIndex);
            else
                fCharDataHandler.processCharacters(stringIndex);
        }
        fCharDataLength = 0;
    }
    //
    //
    //
    public boolean lookingAtChar(char ch, boolean skipPastChar) throws Exception {
        int ch2 = getChar(fCurrentOffset);
        if (ch2 == ch) {
            if (skipPastChar) {
                fCharacterCounter++;
                fCurrentOffset += fBytesPerChar;
            }
            return true;
        }
        return false;
    }
    //
    //
    //
    public boolean lookingAtValidChar(boolean skipPastChar) throws Exception {
        int ch = getChar(fCurrentOffset);
        if (ch < 0x20) {
            if (ch == 0x09) {
                if (!skipPastChar)
                    return true;
                fCharacterCounter++;
            } else if (ch == 0x0A) {
                if (!skipPastChar)
                    return true;
                fLinefeedCounter++;
                fCharacterCounter = 1;
            } else if (ch == 0x0D) {
                if (!skipPastChar)
                    return true;
                fCarriageReturnCounter++;
                fCharacterCounter = 1;
            } else {
                if (ch == -1) {
                    return changeReaders().lookingAtValidChar(skipPastChar);
                }
                return false;
            }
            fCurrentOffset += fBytesPerChar;
            return true;
        }
        if (ch <= 0xD7FF) {
            if (skipPastChar) {
                fCharacterCounter++;
                fCurrentOffset += fBytesPerChar;
            }
            return true;
        }
        if (ch <= 0xDFFF) {
            // REVISIT - check that the surrogate pair is valid
            if (skipPastChar) {
                fCharacterCounter++;
                fCurrentOffset += fBytesPerChar;
            }
            return true;
        }
        if (ch <= 0xFFFD) {
            if (skipPastChar) {
                fCharacterCounter++;
                fCurrentOffset += fBytesPerChar;
            }
            return true;
        }
        return false;
    }
    //
    //
    //
    public boolean lookingAtSpace(boolean skipPastChar) throws Exception {
        int ch = getChar(fCurrentOffset);
        if (ch > 0x20)
            return false;
        if (ch == 0x20 || ch == 0x09) {
            if (!skipPastChar)
                return true;
            fCharacterCounter++;
        } else if (ch == 0x0A) {
            if (!skipPastChar)
                return true;
            fLinefeedCounter++;
            fCharacterCounter = 1;
        } else if (ch == 0x0D) {
            if (!skipPastChar)
                return true;
            fCarriageReturnCounter++;
            fCharacterCounter = 1;
        } else {
            if (ch == -1) { // REVISIT - should we be checking this here ?
                return changeReaders().lookingAtSpace(skipPastChar);
            }
            return false;
        }
        fCurrentOffset += fBytesPerChar;
        return true;
    }
    //
    //
    //
    public void skipToChar(char chr) throws Exception {
        while (true) {
            int ch = getChar(fCurrentOffset);
            if (ch == chr)
                return;
            if (ch == -1) {
                changeReaders().skipToChar(chr);
                return;
            }
            if (ch == 0x0A) {
                fLinefeedCounter++;
                fCharacterCounter = 1;
            } else if (ch == 0x0D) {
                fCarriageReturnCounter++;
                fCharacterCounter = 1;
            } else if (ch >= 0xD800 && ch < 0xDC00) {
                fCharacterCounter++;
                fCurrentOffset += fBytesPerChar;
                ch = getChar(fCurrentOffset);
                if (ch < 0xDC00 || ch >= 0xE000)
                    continue;
            } else
                fCharacterCounter++;
            fCurrentOffset += fBytesPerChar;
        }
    }
    //
    //
    //
    public void skipPastSpaces() throws Exception {
        while (true) {
            int ch = getChar(fCurrentOffset);
            if (ch > 0x20)
                return;
            if (ch == 0x20 || ch == 0x09) {
                fCharacterCounter++;
            } else if (ch == 0x0A) {
                fLinefeedCounter++;
                fCharacterCounter = 1;
            } else if (ch == 0x0D) {
                fCarriageReturnCounter++;
                fCharacterCounter = 1;
            } else {
                if (ch == -1)
                    changeReaders().skipPastSpaces();
                return;
            }
            fCurrentOffset += fBytesPerChar;
        }
    }
    //
    //
    //
    public void skipPastName(char fastcheck) throws Exception {
        int ch = getChar(fCurrentOffset);
        if (!fCalledCharPropInit) {
            XMLCharacterProperties.initCharFlags();
            fCalledCharPropInit = true;
        }
        if ((XMLCharacterProperties.fgCharFlags[ch] & XMLCharacterProperties.E_InitialNameCharFlag) == 0)
            return;
        while (true) {
            fCurrentOffset += fBytesPerChar;
            fCharacterCounter++;
            ch = getChar(fCurrentOffset);
            if (fastcheck == ch)
                return;
            if ((XMLCharacterProperties.fgCharFlags[ch] & XMLCharacterProperties.E_NameCharFlag) == 0)
                return;
        }
    }
    //
    //
    //
    public void skipPastNmtoken(char fastcheck) throws Exception {
        int ch = getChar(fCurrentOffset);
        if (!fCalledCharPropInit) {
            XMLCharacterProperties.initCharFlags();
            fCalledCharPropInit = true;
        }
        while (true) {
            if (fastcheck == ch)
                return;
            if ((XMLCharacterProperties.fgCharFlags[ch] & XMLCharacterProperties.E_NameCharFlag) == 0)
                return;
            fCurrentOffset += fBytesPerChar;
            fCharacterCounter++;
            ch = getChar(fCurrentOffset);
        }
    }
    //
    //
    //
    public boolean skippedString(char[] s) throws Exception {
        int offset = fCurrentOffset;
        for (int i = 0; i < s.length; i++) {
            if (getChar(offset) != s[i])
                return false;
            offset += fBytesPerChar;
        }
        fCurrentOffset = offset;
        fCharacterCounter += s.length;
        return true;
    }
    //
    //
    //
    public int scanInvalidChar() throws Exception {
        int ch = getChar(fCurrentOffset);
        if (ch == -1) {
            return changeReaders().scanInvalidChar();
        }
        fCurrentOffset += fBytesPerChar;
        if (ch == 0x0A) {
            fLinefeedCounter++;
            fCharacterCounter = 1;
        } else if (ch == 0x0D) {
            fCarriageReturnCounter++;
            fCharacterCounter = 1;
        } else {
            fCharacterCounter++;
            if (ch >= 0xD800 && ch < 0xDC00) {
                int ch2 = getChar(fCurrentOffset);
                if (ch2 >= 0xDC00 && ch2 < 0xE000) {
                    ch = ((ch-0xD800)<<10)+(ch2-0xDC00)+0x10000;
                    fCurrentOffset += fBytesPerChar;
                }
            }
        }
        return ch;
    }
    //
    //
    //
    public int scanCharRef(boolean hex) throws Exception {
        int ch = getChar(fCurrentOffset);
        if (ch == -1) {
            return changeReaders().scanCharRef(hex);
        }
        int num = 0;
        if (hex) {
            if (ch > 'f' || XMLCharacterProperties.fgAsciiXDigitChar[ch] == 0)
                return XMLEntityHandler.CHARREF_RESULT_INVALID_CHAR;
            num = ch - (ch < 'A' ? '0' : (ch < 'a' ? 'A' : 'a') - 10);
        } else {
            if (ch < '0' || ch > '9')
                return XMLEntityHandler.CHARREF_RESULT_INVALID_CHAR;
            num = ch - '0';
        }
        fCharacterCounter++;
        fCurrentOffset += fBytesPerChar;
        boolean toobig = false;
        while (true) {
            ch = getChar(fCurrentOffset);
            if (ch == -1)
                break;
            if (hex) {
                if (ch > 'f' || XMLCharacterProperties.fgAsciiXDigitChar[ch] == 0)
                    break;
            } else {
                if (ch < '0' || ch > '9')
                    break;
            }
            fCharacterCounter++;
            fCurrentOffset += fBytesPerChar;
            if (hex) {
                int dig = ch - (ch < 'A' ? '0' : (ch < 'a' ? 'A' : 'a') - 10);
                num = (num << 4) + dig;
            } else {
                int dig = ch - '0';
                num = (num * 10) + dig;
            }
            if (num > 0x10FFFF) {
                toobig = true;
                num = 0;
            }
        }
        if (ch != ';')
            return XMLEntityHandler.CHARREF_RESULT_SEMICOLON_REQUIRED;
        fCharacterCounter++;
        fCurrentOffset += fBytesPerChar;
        if (toobig)
            return XMLEntityHandler.CHARREF_RESULT_OUT_OF_RANGE;
        return num;
    }
    //
    //
    //
    public int scanStringLiteral() throws Exception {
        boolean single;
        if (!(single = lookingAtChar('\'', true)) && !lookingAtChar('\"', true)) {
            return XMLEntityHandler.STRINGLIT_RESULT_QUOTE_REQUIRED;
        }
        int offset = fCurrentOffset;
        char qchar = single ? '\'' : '\"';
        while (!lookingAtChar(qchar, false)) {
            if (!lookingAtValidChar(true)) {
                return XMLEntityHandler.STRINGLIT_RESULT_INVALID_CHAR;
            }
        }
        int stringIndex = addString(offset, fCurrentOffset - offset);
        lookingAtChar(qchar, true); // move past qchar
        return stringIndex;
    }
    //
    // [10] AttValue ::= '"' ([^<&"] | Reference)* '"'
    //                   | "'" ([^<&'] | Reference)* "'"
    //
    public int scanAttValue(char qchar, boolean asSymbol) throws Exception
    {
        int offset = fCurrentOffset;
        while (true) {
            if (lookingAtChar(qchar, false)) {
                break;
            }
            if (lookingAtChar(' ', true)) {
                continue;
            }
            if (lookingAtSpace(false)) {
                return XMLEntityHandler.ATTVALUE_RESULT_COMPLEX;
            }
            if (lookingAtChar('&', false)) {
                return XMLEntityHandler.ATTVALUE_RESULT_COMPLEX;
            }
            if (lookingAtChar('<', false)) {
                return XMLEntityHandler.ATTVALUE_RESULT_LESSTHAN;
            }
            if (!lookingAtValidChar(true)) {
                return XMLEntityHandler.ATTVALUE_RESULT_INVALID_CHAR;
            }
        }
        int result = asSymbol ? addSymbol(offset, fCurrentOffset - offset) : addString(offset, fCurrentOffset - offset);
        lookingAtChar(qchar, true);
        return result;
    }
    //
    //  [9] EntityValue ::= '"' ([^%&"] | PEReference | Reference)* '"'
    //                      | "'" ([^%&'] | PEReference | Reference)* "'"
    //
    public int scanEntityValue(int qchar, boolean createString) throws Exception
    {
        int offset = fCurrentOffset;
        while (true) {
            if (qchar != -1 && lookingAtChar((char)qchar, false)) {
                if (!createString)
                    return XMLEntityHandler.ENTITYVALUE_RESULT_FINISHED;
                break;
            }
            if (lookingAtChar('&', false)) {
                return XMLEntityHandler.ENTITYVALUE_RESULT_REFERENCE;
            }
            if (lookingAtChar('%', false)) {
                return XMLEntityHandler.ENTITYVALUE_RESULT_PEREF;
            }
            if (!lookingAtValidChar(true)) {
                return XMLEntityHandler.ENTITYVALUE_RESULT_INVALID_CHAR;
            }
        }
        int result = addString(offset, fCurrentOffset - offset);
        lookingAtChar((char)qchar, true);
        return result;
    }
    //
    //
    //
    public boolean scanExpectedName(char fastcheck, StringPool.CharArrayRange expectedName) throws Exception {
        int nameOffset = fCurrentOffset;
        skipPastName(fastcheck);
        int nameLength = fCurrentOffset - nameOffset;
        if (nameLength == 0)
            return false;
        int nameIndex = addSymbol(nameOffset, nameLength);
        // DEFECT !! check name against expected name
        return true;
    }

    public void scanQName(char fastcheck, QName qname) throws Exception {

        // REVISIT: possible bugs with surrogate characters  -el
        int nameOffset = fCurrentOffset;
        int ch;
        int prefixend=-1;
        int offset=fCurrentOffset;
        ch = getChar(fCurrentOffset);
        if (ch < 0x80) {
            if (XMLCharacterProperties.fgAsciiInitialNameChar[ch] == 0) {
                qname.clear();
                return;
            }
            if (ch == ':') {
                qname.clear();
                return;
            }
        }
        else {
            if (!fCalledCharPropInit) {
                XMLCharacterProperties.initCharFlags();
                fCalledCharPropInit = true;
            }
            if ((XMLCharacterProperties.fgCharFlags[ch] & XMLCharacterProperties.E_InitialNameCharFlag) == 0)
                return;
        }

        while (true) {
            fCurrentOffset += fBytesPerChar;
            fCharacterCounter++;
            ch = getChar(fCurrentOffset);
            if (fastcheck == ch) {
                break;
            }
            if (ch < 0x80) {
                if (XMLCharacterProperties.fgAsciiNameChar[ch] == 0) {
                    break;
                }
                if (ch == ':') {
                    if (prefixend != -1) {
                        break;
                    }
                    prefixend = fCurrentOffset;
                    //
                   // We need to peek ahead one character.  If the next character is not a
                   // valid initial name character, or is another colon, then we cannot meet
                   // both the Prefix and LocalPart productions for the QName production,
                   // which means that there is no Prefix and we need to terminate the QName
                   // at the first colon.  --JR's comments
                   //

                    ch = getChar(fCurrentOffset+fBytesPerChar);
                    boolean lpok = true;
                    if (ch < 0x80) {
                        if (XMLCharacterProperties.fgAsciiInitialNameChar[ch] == 0 || ch == ':') {
                            lpok = false;
                        }
                    }
                    else {
                        if (!fCalledCharPropInit) {
                            XMLCharacterProperties.initCharFlags();
                            fCalledCharPropInit = true;
                        }
                        if ((XMLCharacterProperties.fgCharFlags[ch] & XMLCharacterProperties.E_InitialNameCharFlag) == 0) {
                            lpok = false;
                        }
                    }
                    if (!lpok) {
                        prefixend = -1;
                        break;
                    }
                }
            }
            else {
                if (!fCalledCharPropInit) {
                    XMLCharacterProperties.initCharFlags();
                    fCalledCharPropInit = true;
                }
                if ((XMLCharacterProperties.fgCharFlags[ch] & XMLCharacterProperties.E_InitialNameCharFlag) == 0) {
                    break;
                }
            }
        }//end while loop
        int length = fCurrentOffset - offset;
        qname.prefix = prefixend == -1 ? -1 : addSymbol(offset, prefixend - offset);
        qname.rawname = addSymbol(offset, length);
        qname.localpart = prefixend == -1 ? qname.rawname : addSymbol(prefixend + fBytesPerChar, fCurrentOffset - (prefixend + fBytesPerChar));
        qname.uri = StringPool.EMPTY_STRING;



    } // scanQName(char,QName)

    public int scanName(char fastcheck) throws Exception {
        int nameOffset = fCurrentOffset;
        skipPastName(fastcheck);
        int nameLength = fCurrentOffset - nameOffset;
        if (nameLength == 0)
            return -1;
        int nameIndex = addSymbol(nameOffset, nameLength);
        return nameIndex;
    }
    //
    //
    //
    private static final char[] cdata_string = { 'C','D','A','T','A','[' };
    private int recognizeMarkup() throws Exception {
        int ch = getChar(fCurrentOffset);
        switch (ch) {
        case -1:
            return XMLEntityHandler.CONTENT_RESULT_MARKUP_END_OF_INPUT;
        case '?':
            fCharacterCounter++;
            fCurrentOffset += fBytesPerChar;
            return XMLEntityHandler.CONTENT_RESULT_START_OF_PI;
        case '!':
            fCharacterCounter++;
            fCurrentOffset += fBytesPerChar;
            ch = getChar(fCurrentOffset);
            if (ch == -1) {
                fCharacterCounter--;
                fCurrentOffset -= fBytesPerChar;;
                return XMLEntityHandler.CONTENT_RESULT_MARKUP_END_OF_INPUT;
            }
            if (ch == '-') {
                fCharacterCounter++;
                fCurrentOffset += fBytesPerChar;
                ch = getChar(fCurrentOffset);
                if (ch == -1) {
                    fCharacterCounter -= 2;
                    fCurrentOffset -= 2;
                    return XMLEntityHandler.CONTENT_RESULT_MARKUP_END_OF_INPUT;
                }
                if (ch == '-') {
                    fCharacterCounter++;
                    fCurrentOffset += fBytesPerChar;
                    return XMLEntityHandler.CONTENT_RESULT_START_OF_COMMENT;
                }
                break;
            }
            if (ch == '[') {
                fCharacterCounter++;
                fCurrentOffset += fBytesPerChar;
                for (int i = 0; i < 6; i++) {
                    ch = getChar(fCurrentOffset);
                    if (ch == -1) {
                        fCharacterCounter -= (2 + i);
                        fCurrentOffset -= ((2 + i) * fBytesPerChar);
                        return XMLEntityHandler.CONTENT_RESULT_MARKUP_END_OF_INPUT;
                    }
                    if (ch != cdata_string[i]) {
                        return XMLEntityHandler.CONTENT_RESULT_MARKUP_NOT_RECOGNIZED;
                    }
                    fCharacterCounter++;
                    fCurrentOffset += fBytesPerChar;
                }
                return XMLEntityHandler.CONTENT_RESULT_START_OF_CDSECT;
            }
            break;
        case '/':
            fCharacterCounter++;
            fCurrentOffset += fBytesPerChar;
            return XMLEntityHandler.CONTENT_RESULT_START_OF_ETAG;
        default:
            return XMLEntityHandler.CONTENT_RESULT_START_OF_ELEMENT;
        }
        return XMLEntityHandler.CONTENT_RESULT_MARKUP_NOT_RECOGNIZED;
    }
    private int recognizeReference() throws Exception {
        int ch = getChar(fCurrentOffset);
        if (ch == -1) {
            return XMLEntityHandler.CONTENT_RESULT_REFERENCE_END_OF_INPUT;
        }
        //
        // [67] Reference ::= EntityRef | CharRef
        // [68] EntityRef ::= '&' Name ';'
        // [66] CharRef ::= '&#' [0-9]+ ';' | '&#x' [0-9a-fA-F]+ ';'
        //
        if (ch == '#') {
            fCharacterCounter++;
            fCurrentOffset += fBytesPerChar;
            return XMLEntityHandler.CONTENT_RESULT_START_OF_CHARREF;
        } else {
            return XMLEntityHandler.CONTENT_RESULT_START_OF_ENTITYREF;
        }
    }
    public int scanContent(QName element) throws Exception {
        int offset = fCurrentOffset;
        int ch = getChar(fCurrentOffset);
        fCurrentOffset += fBytesPerChar;
        byte prop;
        if (!fCalledCharPropInit) {
            XMLCharacterProperties.initCharFlags();
            fCalledCharPropInit = true;
        }
        if (ch < 0x80) {
            if (ch == -1) {
                fCurrentOffset -= fBytesPerChar;
                return changeReaders().scanContent(element); // REVISIT - not quite...
            }
            prop = XMLCharacterProperties.fgCharFlags[ch];
            if ((prop & XMLCharacterProperties.E_CharDataFlag) == 0 && ch != 0x0A && ch != 0x0D) {
                if (ch == '<') {
                    fCharacterCounter++;
                    if (!fInCDSect) {
                        return recognizeMarkup();
                    }
                } else if (ch == '&') {
                    fCharacterCounter++;
                    if (!fInCDSect) {
                        return recognizeReference();
                    }
                } else if (ch == ']') {
                    if (getChar(fCurrentOffset) == ']' && getChar(fCurrentOffset + fBytesPerChar) == '>') {
                        fCharacterCounter += 3;
                        fCurrentOffset += (2 * fBytesPerChar);
                        return XMLEntityHandler.CONTENT_RESULT_END_OF_CDSECT;
                    }
                } else {
                    fCurrentOffset -= fBytesPerChar;
                    return XMLEntityHandler.CONTENT_RESULT_INVALID_CHAR;
                }
            } else if (ch == 0x20 || ch == 0x09 || ch == 0x0A || ch == 0x0D) {
                do {
                    if (ch == 0x0A) {
                        fLinefeedCounter++;
                        fCharacterCounter = 1;
                    } else if (ch == 0x0D) {
                        fCarriageReturnCounter++;
                        fCharacterCounter = 1;
                    } else {
                        fCharacterCounter++;
                    }
                    ch = getChar(fCurrentOffset);
                    fCurrentOffset += fBytesPerChar;
                } while (ch == 0x20 || ch == 0x09 || ch == 0x0A || ch == 0x0D);
                if (ch < 0x80) {
                    if (ch == -1) {
                        fCurrentOffset -= fBytesPerChar;
                        callCharDataHandler(offset, fCurrentOffset - offset, true);
                        return changeReaders().scanContent(element); // REVISIT - not quite...
                    }
                    prop = XMLCharacterProperties.fgCharFlags[ch];
                    if ((prop & XMLCharacterProperties.E_CharDataFlag) == 0) {
                        if (ch == '<') {
                            if (!fInCDSect) {
                                callCharDataHandler(offset, (fCurrentOffset - fBytesPerChar) - offset, true);
                                fCharacterCounter++;
                                return recognizeMarkup();
                            }
                            fCharacterCounter++;
                        } else if (ch == '&') {
                            if (!fInCDSect) {
                                callCharDataHandler(offset, (fCurrentOffset - fBytesPerChar) - offset, true);
                                fCharacterCounter++;
                                return recognizeReference();
                            }
                            fCharacterCounter++;
                        } else if (ch == ']') {
                            if (getChar(fCurrentOffset) == ']' && getChar(fCurrentOffset + fBytesPerChar) == '>') {
                                callCharDataHandler(offset, (fCurrentOffset - fBytesPerChar) - offset, true);
                                fCharacterCounter += 3;
                                fCurrentOffset += (2 * fBytesPerChar);
                                return XMLEntityHandler.CONTENT_RESULT_END_OF_CDSECT;
                            }
                        } else {
                            fCurrentOffset -= fBytesPerChar;
                            callCharDataHandler(offset, fCurrentOffset - offset, true);
                            return XMLEntityHandler.CONTENT_RESULT_INVALID_CHAR;
                        }
                    }
                } else {
                    if (ch >= 0xD800 && ch <= 0xDFFF) {
                        fCurrentOffset += fBytesPerChar;
                    } else if (ch == 0xFFFE || ch == 0xFFFF) {
                        fCurrentOffset -= fBytesPerChar;
                        callCharDataHandler(offset, fCurrentOffset - offset, true);
                        return XMLEntityHandler.CONTENT_RESULT_INVALID_CHAR;
                    }
                }
            }
        } else {
            if (ch >= 0xD800 && ch <= 0xDFFF) {
                fCurrentOffset += fBytesPerChar;
            } else if (ch == 0xFFFE || ch == 0xFFFF) {
                fCurrentOffset -= fBytesPerChar;
                return XMLEntityHandler.CONTENT_RESULT_INVALID_CHAR;
            }
        }
        fCharacterCounter++;
        while (true) {
            ch = getChar(fCurrentOffset);
            fCurrentOffset += fBytesPerChar;
            if (ch >= 0x80 || ch < 0)
                break;
            prop = XMLCharacterProperties.fgCharFlags[ch];
            if ((prop & XMLCharacterProperties.E_CharDataFlag) == 0) {
                if (ch == 0x0A) {
                    fLinefeedCounter++;
                    fCharacterCounter = 1;
                } else if (ch == 0x0D) {
                    fCarriageReturnCounter++;
                    fCharacterCounter = 1;
                } else
                    break;
            } else
                fCharacterCounter++;
        }
        while (true) { // REVISIT - EOF check ?
            if (ch < 0x80) {
                if (ch == -1) {
                    fCurrentOffset -= fBytesPerChar;
                    callCharDataHandler(offset, fCurrentOffset - offset, false);
                    return changeReaders().scanContent(element); // REVISIT - not quite...
                }
                prop = XMLCharacterProperties.fgCharFlags[ch];
                if ((prop & XMLCharacterProperties.E_CharDataFlag) == 0) {
                    if (ch == '<') {
                        if (!fInCDSect) {
                            callCharDataHandler(offset, (fCurrentOffset - fBytesPerChar) - offset, false);
                            fCharacterCounter++;
                            return recognizeMarkup();
                        }
                        fCharacterCounter++;
                    } else if (ch == '&') {
                        if (!fInCDSect) {
                            callCharDataHandler(offset, (fCurrentOffset - fBytesPerChar) - offset, false);
                            fCharacterCounter++;
                            return recognizeReference();
                        }
                        fCharacterCounter++;
                    } else if (ch == 0x0A) {
                        fLinefeedCounter++;
                        fCharacterCounter = 1;
                    } else if (ch == 0x0D) {
                        fCarriageReturnCounter++;
                        fCharacterCounter = 1;
                    } else if (ch == ']') {
                        if (getChar(fCurrentOffset) == ']' && getChar(fCurrentOffset + fBytesPerChar) == '>') {
                            callCharDataHandler(offset, (fCurrentOffset - fBytesPerChar) - offset, false);
                            fCharacterCounter += 3;
                            fCurrentOffset += (2 * fBytesPerChar);
                            return XMLEntityHandler.CONTENT_RESULT_END_OF_CDSECT;
                        }
                        fCharacterCounter++;
                    } else {
                        fCurrentOffset -= fBytesPerChar;
                        callCharDataHandler(offset, fCurrentOffset - offset, false);
                        return XMLEntityHandler.CONTENT_RESULT_INVALID_CHAR;
                    }
                } else {
                    fCharacterCounter++;
                }
            } else {
                if (ch >= 0xD800 && ch <= 0xDFFF) {
                    fCharacterCounter++;
                    fCurrentOffset += fBytesPerChar;
                } else if (ch == 0xFFFE || ch == 0xFFFF) {
                    fCurrentOffset -= fBytesPerChar;
                    callCharDataHandler(offset, fCurrentOffset - offset, false);
                    return XMLEntityHandler.CONTENT_RESULT_INVALID_CHAR;
                }
                fCharacterCounter++;
            }
            ch = getChar(fCurrentOffset);
            fCurrentOffset += fBytesPerChar;
        }
    }
}