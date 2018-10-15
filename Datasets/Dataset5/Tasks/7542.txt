localPart = fData.substring( index + 1, lenfData );

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
import org.apache.xerces.utils.QName;
import org.apache.xerces.utils.StringPool;
import org.apache.xerces.utils.XMLCharacterProperties;

import org.xml.sax.Locator;
import org.xml.sax.InputSource;
import java.io.IOException;

/**
 * Reader for processing internal entity replacement text.
 * <p>
 * This reader processes data contained within strings kept
 * in the string pool.  It provides the support for both
 * general and parameter entities.  The location support
 * as we are processing the replacement text is somewhat
 * poor and needs to be updated when "nested locations"
 * have been implemented.
 * <p>
 * For efficiency, we return instances of this class to a
 * free list and reuse those instances to process other
 * strings.
 *
 * @version $id$
 */
final class StringReader extends XMLEntityReader {
    /**
     * Allocate a string reader
     *
     * @param entityHandler The current entity handler.
     * @param errorReporter The current error reporter.
     * @param sendCharDataAsCharArray true if char data should be reported using
     *                                char arrays instead of string handles.
     * @param lineNumber The line number to return as our position.
     * @param columnNumber The column number to return as our position.
     * @param stringHandle The StringPool handle for the data to process.
     * @param stringPool The string pool.
     * @param addEnclosingSpaces If true, treat the data to process as if
     *                           there were a leading and trailing space
     *                           character enclosing the string data.
     * @return The reader that will process the string data.
     */
    public static StringReader createStringReader(XMLEntityHandler entityHandler,
                                                  XMLErrorReporter errorReporter,
                                                  boolean sendCharDataAsCharArray,
                                                  int lineNumber,
                                                  int columnNumber,
                                                  int stringHandle,
                                                  StringPool stringPool,
                                                  boolean addEnclosingSpaces)
    {
        StringReader reader = null;
        synchronized (StringReader.class) {
            reader = fgFreeReaders;
            if (reader == null) {
                return new StringReader(entityHandler, errorReporter, sendCharDataAsCharArray, lineNumber, columnNumber,
                                        stringHandle, stringPool, addEnclosingSpaces);
            }
            fgFreeReaders = reader.fNextFreeReader;
        }
        reader.init(entityHandler, errorReporter, sendCharDataAsCharArray, lineNumber, columnNumber,
                    stringHandle, stringPool, addEnclosingSpaces);
        return reader;
    }
    //
    //
    //
    private StringReader(XMLEntityHandler entityHandler, XMLErrorReporter errorReporter,
                         boolean sendCharDataAsCharArray, int lineNumber, int columnNumber,
                         int stringHandle, StringPool stringPool, boolean addEnclosingSpaces)
    {
        super(entityHandler, errorReporter, sendCharDataAsCharArray, lineNumber, columnNumber);
        fStringPool = stringPool;
        fData = fStringPool.toString(stringHandle);
        fCurrentOffset = 0;
        fEndOffset = fData.length();
        if (addEnclosingSpaces) {
            fMostRecentChar = ' ';
            fCurrentOffset--;
            oweTrailingSpace = hadTrailingSpace = true;
        } else {
            fMostRecentChar = fEndOffset == 0 ? -1 : fData.charAt(0);
        }
    }
    private void init(XMLEntityHandler entityHandler, XMLErrorReporter errorReporter,
                      boolean sendCharDataAsCharArray, int lineNumber, int columnNumber,
                      int stringHandle, StringPool stringPool, boolean addEnclosingSpaces)
    {
        super.init(entityHandler, errorReporter, sendCharDataAsCharArray, lineNumber, columnNumber);
        fStringPool = stringPool;
        fData = fStringPool.toString(stringHandle);
        fCurrentOffset = 0;
        fEndOffset = fData.length();
        fNextFreeReader = null;
        if (addEnclosingSpaces) {
            fMostRecentChar = ' ';
            fCurrentOffset--;
            oweTrailingSpace = hadTrailingSpace = true;
        } else {
            fMostRecentChar = fEndOffset == 0 ? -1 : fData.charAt(0);
            oweTrailingSpace = hadTrailingSpace = false;
        }
    }
    //
    //
    //
    public int addString(int offset, int length) {
        if (length == 0)
            return 0;
        return fStringPool.addString(fData.substring(offset, offset + length));
    }
    //
    //
    //
    public int addSymbol(int offset, int length) {
        if (length == 0)
            return 0;
        return fStringPool.addSymbol(fData.substring(offset, offset + length));
    }
    //
    //
    //
    public void append(XMLEntityHandler.CharBuffer charBuffer, int offset, int length) {
        boolean addSpace = false;
        for (int i = 0; i < length; i++) {
            try {
                charBuffer.append(fData.charAt(offset++));
            } catch (StringIndexOutOfBoundsException ex) {
                if (offset == fEndOffset + 1 && hadTrailingSpace) {
                    charBuffer.append(' ');
                } else {
                    System.err.println("StringReader.append()");
                    throw ex;
                }
            }
        }
    }
    //
    //
    //
    private int loadNextChar() {
        if (++fCurrentOffset >= fEndOffset) {
            if (oweTrailingSpace) {
                oweTrailingSpace = false;
                fMostRecentChar = ' ';
            } else {
                fMostRecentChar = -1;
            }
        } else {
            fMostRecentChar = fData.charAt(fCurrentOffset);
        }
        return fMostRecentChar;
    }
    //
    //
    //
    public XMLEntityHandler.EntityReader changeReaders() throws Exception {
        XMLEntityHandler.EntityReader nextReader = super.changeReaders();
        synchronized (StringReader.class) {
            fNextFreeReader = fgFreeReaders;
            fgFreeReaders = this;
        }
        return nextReader;
    }
    //
    //
    //
    public boolean lookingAtChar(char chr, boolean skipPastChar) throws Exception {
        int ch = fMostRecentChar;
        if (ch != chr) {
            if (ch == -1) {
                return changeReaders().lookingAtChar(chr, skipPastChar);
            }
            return false;
        }
        if (skipPastChar) {
            if (++fCurrentOffset >= fEndOffset) {
                if (oweTrailingSpace) {
                    oweTrailingSpace = false;
                    fMostRecentChar = ' ';
                } else {
                    fMostRecentChar = -1;
                }
            } else {
                fMostRecentChar = fData.charAt(fCurrentOffset);
            }
        }
        return true;
    }
    //
    //
    //
    public boolean lookingAtValidChar(boolean skipPastChar) throws Exception {
        int ch = fMostRecentChar;
        if (ch < 0xD800) {
            if (ch < 0x20 && ch != 0x09 && ch != 0x0A && ch != 0x0D) {
                if (ch == -1)
                    return changeReaders().lookingAtValidChar(skipPastChar);
                return false;
            }
            if (skipPastChar) {
                if (++fCurrentOffset >= fEndOffset) {
                    if (oweTrailingSpace) {
                        oweTrailingSpace = false;
                        fMostRecentChar = ' ';
                    } else {
                        fMostRecentChar = -1;
                    }
                } else {
                    fMostRecentChar = fData.charAt(fCurrentOffset);
                }
            }
            return true;
        }
        if (ch > 0xFFFD) {
            return false;
        }
        if (ch < 0xDC00) {
            if (fCurrentOffset + 1 >= fEndOffset) {
                return false;
            }
            ch = fData.charAt(fCurrentOffset + 1);
            if (ch < 0xDC00 || ch >= 0xE000) {
                return false;
            } else if (!skipPastChar) {
                return true;
            } else {
                fCurrentOffset++;
            }
        } else if (ch < 0xE000) {
            return false;
        }
        if (skipPastChar) {
            if (++fCurrentOffset >= fEndOffset) {
                if (oweTrailingSpace) {
                    oweTrailingSpace = false;
                    fMostRecentChar = ' ';
                } else {
                    fMostRecentChar = -1;
                }
            } else {
                fMostRecentChar = fData.charAt(fCurrentOffset);
            }
        }
        return true;
    }
    //
    //
    //
    public boolean lookingAtSpace(boolean skipPastChar) throws Exception {
        int ch = fMostRecentChar;
        if (ch > 0x20)
            return false;
        if (ch == 0x20 || ch == 0x0A || ch == 0x0D || ch == 0x09) {
            if (skipPastChar) {
                loadNextChar();
            }
            return true;
        }
        if (ch == -1) {
            return changeReaders().lookingAtSpace(skipPastChar);
        }
        return false;
    }
    //
    //
    //
    public void skipToChar(char chr) throws Exception {
        //
        // REVISIT - this will skip invalid characters without reporting them.
        //
        int ch = fMostRecentChar;
        while (true) {
            if (ch == chr)
                return;
            if (ch == -1) {
                changeReaders().skipToChar(chr);
                return;
            }
            ch = loadNextChar();
        }
    }
    //
    //
    //
    public void skipPastSpaces() throws Exception {
        int ch = fMostRecentChar;
        if (ch == -1) {
            changeReaders().skipPastSpaces();
            return;
        }
        while (true) {
            if (ch > 0x20 || (ch != 0x20 && ch != 0x0A && ch != 0x09 && ch != 0x0D)) {
                fMostRecentChar = ch;
                return;
            }
            if (++fCurrentOffset >= fEndOffset) {
                changeReaders().skipPastSpaces();
                return;
            }
            ch = fData.charAt(fCurrentOffset);
        }
    }
    //
    //
    //
    public void skipPastName(char fastcheck) throws Exception {
        int ch = fMostRecentChar;
        if (ch < 0x80) {
            if (ch == -1 || XMLCharacterProperties.fgAsciiInitialNameChar[ch] == 0)
                return;
        } else {
            if (!fCalledCharPropInit) {
                XMLCharacterProperties.initCharFlags();
                fCalledCharPropInit = true;
            }
            if ((XMLCharacterProperties.fgCharFlags[ch] & XMLCharacterProperties.E_InitialNameCharFlag) == 0)
                return;
        }
        while (true) {
            ch = loadNextChar();
            if (fastcheck == ch)
                return;
            if (ch < 0x80) {
                if (ch == -1 || XMLCharacterProperties.fgAsciiNameChar[ch] == 0)
                    return;
            } else {
                if (!fCalledCharPropInit) {
                    XMLCharacterProperties.initCharFlags();
                    fCalledCharPropInit = true;
                }
                if ((XMLCharacterProperties.fgCharFlags[ch] & XMLCharacterProperties.E_NameCharFlag) == 0)
                    return;
            }
        }
    }
    //
    //
    //
    public void skipPastNmtoken(char fastcheck) throws Exception {
        int ch = fMostRecentChar;
        while (true) {
            if (fastcheck == ch)
                return;
            if (ch < 0x80) {
                if (ch == -1 || XMLCharacterProperties.fgAsciiNameChar[ch] == 0)
                    return;
            } else {
                if (!fCalledCharPropInit) {
                    XMLCharacterProperties.initCharFlags();
                    fCalledCharPropInit = true;
                }
                if ((XMLCharacterProperties.fgCharFlags[ch] & XMLCharacterProperties.E_NameCharFlag) == 0)
                    return;
            }
            ch = loadNextChar();
        }
    }
    //
    //
    //
    public boolean skippedString(char[] s) throws Exception {
        int ch = fMostRecentChar;
        if (ch != s[0]) {
            if (ch == -1)
                return changeReaders().skippedString(s);
            return false;
        }
        if (fCurrentOffset + s.length > fEndOffset)
            return false;
        for (int i = 1; i < s.length; i++) {
            if (fData.charAt(fCurrentOffset + i) != s[i])
                return false;
        }
        fCurrentOffset += (s.length - 1);
        loadNextChar();
        return true;
    }
    //
    //
    //
    public int scanInvalidChar() throws Exception {
        int ch = fMostRecentChar;
        if (ch == -1)
            return changeReaders().scanInvalidChar();
        loadNextChar();
        return ch;
    }
    //
    //
    //
    public int scanCharRef(boolean hex) throws Exception {
        int ch = fMostRecentChar;
        if (ch == -1)
            return changeReaders().scanCharRef(hex);
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
        boolean toobig = false;
        while (true) {
            ch = loadNextChar();
            if (ch == -1)
                return XMLEntityHandler.CHARREF_RESULT_SEMICOLON_REQUIRED;
            if (hex) {
                if (ch > 'f' || XMLCharacterProperties.fgAsciiXDigitChar[ch] == 0)
                    break;
            } else {
                if (ch < '0' || ch > '9')
                    break;
            }
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
        loadNextChar();
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
    // The values in the following table are defined as:
    //
    //      0 - not special
    //      1 - quote character
    //      2 - reference
    //      3 - peref
    //      4 - invalid
    //
    public static final byte fgAsciiEntityValueChar[] = {
        4, 4, 4, 4, 4, 4, 4, 4, 4, 0, 0, 4, 4, 0, 4, 4,
        4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4,
        0, 0, 1, 0, 0, 3, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, // '\"', '%', '&', '\''
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    };
    public int scanEntityValue(int qchar, boolean createString) throws Exception
    {
        int offset = fCurrentOffset;
        int ch = fMostRecentChar;
        while (true) {
            if (ch == -1) {
                changeReaders(); // do not call next reader, our caller may need to change the parameters
                return XMLEntityHandler.ENTITYVALUE_RESULT_END_OF_INPUT;
            }
            if (ch < 0x80) {
                switch (fgAsciiEntityValueChar[ch]) {
                case 1: // quote char
                    if (ch == qchar) {
                        if (!createString)
                            return XMLEntityHandler.ENTITYVALUE_RESULT_FINISHED;
                        int length = fCurrentOffset - offset;
                        int result = length == 0 ? StringPool.EMPTY_STRING : addString(offset, length);
                        loadNextChar();
                        return result;
                    }
                    // the other quote character is not special
                    // fall through
                case 0: // non-special char
                    if (++fCurrentOffset >= fEndOffset) {
                        if (oweTrailingSpace) {
                            oweTrailingSpace = false;
                            ch = fMostRecentChar = ' ';
                        } else {
                            ch = fMostRecentChar = -1;
                        }
                    } else {
                        ch = fMostRecentChar = fData.charAt(fCurrentOffset);
                    }
                    continue;
                case 2: // reference
                    return XMLEntityHandler.ENTITYVALUE_RESULT_REFERENCE;
                case 3: // peref
                    return XMLEntityHandler.ENTITYVALUE_RESULT_PEREF;
                case 4: // invalid
                    return XMLEntityHandler.ENTITYVALUE_RESULT_INVALID_CHAR;
                }
            } else if (ch < 0xD800) {
                ch = loadNextChar();
            } else if (ch >= 0xE000 && (ch <= 0xFFFD || (ch >= 0x10000 && ch <= 0x10FFFF))) {
                //
                // REVISIT - needs more code to check surrogates.
                //
                ch = loadNextChar();
            } else {
                return XMLEntityHandler.ENTITYVALUE_RESULT_INVALID_CHAR;
            }
        }
    }
    //
    //
    //
    public boolean scanExpectedName(char fastcheck, StringPool.CharArrayRange expectedName) throws Exception {
        int ch = fMostRecentChar;
        if (ch == -1) {
            return changeReaders().scanExpectedName(fastcheck, expectedName);
        }
        if (!fCalledCharPropInit) {
            XMLCharacterProperties.initCharFlags();
            fCalledCharPropInit = true;
        }
        int nameOffset = fCurrentOffset;
        if ((XMLCharacterProperties.fgCharFlags[ch] & XMLCharacterProperties.E_InitialNameCharFlag) == 0)
            return false;
        while (true) {
            ch = loadNextChar();
            if (fastcheck == ch)
                break;
            if (ch == -1)
                break;
            if ((XMLCharacterProperties.fgCharFlags[ch] & XMLCharacterProperties.E_NameCharFlag) == 0)
                break;
        }
        int nameIndex = fStringPool.addSymbol(fData.substring(nameOffset, fCurrentOffset));
        // DEFECT !! check name against expected name

        return true;
    }
    //
    //
    //
    public void scanQName(char fastcheck, QName qname) throws Exception {
        int ch = fMostRecentChar;
        if (ch == -1) {
            changeReaders().scanQName(fastcheck, qname);
            return;
        }
        if (!fCalledCharPropInit) {
            XMLCharacterProperties.initCharFlags();
            fCalledCharPropInit = true;
        }
        int nameOffset = fCurrentOffset;
        if ((XMLCharacterProperties.fgCharFlags[ch] & XMLCharacterProperties.E_InitialNameCharFlag) == 0) {
            qname.clear();
            return;
        }
        while (true) {
            ch = loadNextChar();
            if (fastcheck == ch)
                break;
            if (ch == -1)
                break;
            if ((XMLCharacterProperties.fgCharFlags[ch] & XMLCharacterProperties.E_NameCharFlag) == 0)
                break;
        }

        qname.clear();
        qname.rawname = fStringPool.addSymbol(fData.substring(nameOffset, fCurrentOffset));
       
        int index = fData.indexOf(':', nameOffset);
        if (index != -1) {
            qname.prefix = fStringPool.addSymbol(fData.substring(nameOffset, index));
            int indexOfSpaceChar = fData.indexOf( ' ', index + 1 );//one past : look for blank
            String localPart;
            if( indexOfSpaceChar != -1 ){//found one
                localPart = fData.substring(index+1, indexOfSpaceChar );
                qname.localpart  = fStringPool.addSymbol(localPart);
            } else{//then get up to end of String
                int lenfData     = fData.length();
                localPart = fData.substring( index + 1, fData.length );
                qname.localpart  = fStringPool.addSymbol(localPart);
            }
            qname.localpart  = fStringPool.addSymbol(localPart);
        }
        else {
            qname.localpart  = qname.rawname;
        }

    } // scanQName(char,QName)

    //
    //
    //
    public int scanName(char fastcheck) throws Exception {
        int ch = fMostRecentChar;
        if (ch == -1) {
            return changeReaders().scanName(fastcheck);
        }
        if (!fCalledCharPropInit) {
            XMLCharacterProperties.initCharFlags();
            fCalledCharPropInit = true;
        }
        int nameOffset = fCurrentOffset;
        if ((XMLCharacterProperties.fgCharFlags[ch] & XMLCharacterProperties.E_InitialNameCharFlag) == 0)
            return -1;
        while (true) {
            if (++fCurrentOffset >= fEndOffset) {
                if (oweTrailingSpace) {
                    oweTrailingSpace = false;
                    fMostRecentChar = ' ';
                } else {
                    fMostRecentChar = -1;
                }
                break;
            }
            ch = fMostRecentChar = fData.charAt(fCurrentOffset);
            if (fastcheck == ch)
                break;
            if ((XMLCharacterProperties.fgCharFlags[ch] & XMLCharacterProperties.E_NameCharFlag) == 0)
                break;
        }
        int nameIndex = fStringPool.addSymbol(fData.substring(nameOffset, fCurrentOffset));
        return nameIndex;
    }
    //
    // There are no leading/trailing space checks here because scanContent cannot
    // be called on a parameter entity reference value.
    //
    private int recognizeMarkup(int ch) throws Exception {
        if (ch == -1) {
            return XMLEntityHandler.CONTENT_RESULT_MARKUP_END_OF_INPUT;
        }
        switch (ch) {
        case '?':
            loadNextChar();
            return XMLEntityHandler.CONTENT_RESULT_START_OF_PI;
        case '!':
            ch = loadNextChar();
            if (ch == -1) {
                fCurrentOffset -= 2;
                loadNextChar();
                return XMLEntityHandler.CONTENT_RESULT_MARKUP_END_OF_INPUT;
            }
            if (ch == '-') {
                ch = loadNextChar();
                if (ch == -1) {
                    fCurrentOffset -= 3;
                    loadNextChar();
                    return XMLEntityHandler.CONTENT_RESULT_MARKUP_END_OF_INPUT;
                }
                if (ch == '-') {
                    loadNextChar();
                    return XMLEntityHandler.CONTENT_RESULT_START_OF_COMMENT;
                }
                break;
            }
            if (ch == '[') {
                for (int i = 0; i < 6; i++) {
                    ch = loadNextChar();
                    if (ch == -1) {
                        fCurrentOffset -= (3 + i);
                        loadNextChar();
                        return XMLEntityHandler.CONTENT_RESULT_MARKUP_END_OF_INPUT;
                    }
                    if (ch != cdata_string[i]) {
                        return XMLEntityHandler.CONTENT_RESULT_MARKUP_NOT_RECOGNIZED;
                    }
                }
                loadNextChar();
                return XMLEntityHandler.CONTENT_RESULT_START_OF_CDSECT;
            }
            break;
        case '/':
            loadNextChar();
            return XMLEntityHandler.CONTENT_RESULT_START_OF_ETAG;
        default:
            return XMLEntityHandler.CONTENT_RESULT_START_OF_ELEMENT;
        }
        return XMLEntityHandler.CONTENT_RESULT_MARKUP_NOT_RECOGNIZED;
    }
    private int recognizeReference(int ch) throws Exception {
        if (ch == -1) {
            return XMLEntityHandler.CONTENT_RESULT_MARKUP_END_OF_INPUT;
        }
        //
        // [67] Reference ::= EntityRef | CharRef
        // [68] EntityRef ::= '&' Name ';'
        // [66] CharRef ::= '&#' [0-9]+ ';' | '&#x' [0-9a-fA-F]+ ';'
        //
        if (ch == '#') {
            loadNextChar();
            return XMLEntityHandler.CONTENT_RESULT_START_OF_CHARREF;
        } else {
            return XMLEntityHandler.CONTENT_RESULT_START_OF_ENTITYREF;
        }
    }
    public int scanContent(QName element) throws Exception {
        int ch = fMostRecentChar;
        if (ch == -1) {
            return changeReaders().scanContent(element);
        }
        int offset = fCurrentOffset;
        if (ch < 0x80) {
            switch (XMLCharacterProperties.fgAsciiWSCharData[ch]) {
            case 0:
                ch = loadNextChar();
                break;
            case 1:
                ch = loadNextChar();
                if (!fInCDSect) {
                    return recognizeMarkup(ch);
                }
                break;
            case 2:
                ch = loadNextChar();
                if (!fInCDSect) {
                    return recognizeReference(ch);
                }
                break;
            case 3:
                ch = loadNextChar();
                if (ch == ']' && fCurrentOffset + 1 < fEndOffset && fData.charAt(fCurrentOffset + 1) == '>') {
                    loadNextChar();
                    loadNextChar();
                    return XMLEntityHandler.CONTENT_RESULT_END_OF_CDSECT;
                }
                break;
            case 4:
                return XMLEntityHandler.CONTENT_RESULT_INVALID_CHAR;
            case 5:
                do {
                    ch = loadNextChar();
                    if (ch == -1) {
                        callCharDataHandler(offset, fEndOffset, true);
                        return changeReaders().scanContent(element);
                    }
                } while (ch == 0x20 || ch == 0x0A || ch == 0x0D || ch == 0x09);
                if (ch < 0x80) {
                    switch (XMLCharacterProperties.fgAsciiCharData[ch]) {
                    case 0:
                        ch = loadNextChar();
                        break;
                    case 1:
                        ch = loadNextChar();
                        if (!fInCDSect) {
                            callCharDataHandler(offset, fCurrentOffset - 1, true);
                            return recognizeMarkup(ch);
                        }
                        break;
                    case 2:
                        ch = loadNextChar();
                        if (!fInCDSect) {
                            callCharDataHandler(offset, fCurrentOffset - 1, true);
                            return recognizeReference(ch);
                        }
                        break;
                    case 3:
                        ch = loadNextChar();
                        if (ch == ']' && fCurrentOffset + 1 < fEndOffset && fData.charAt(fCurrentOffset + 1) == '>') {
                            callCharDataHandler(offset, fCurrentOffset - 1, true);
                            loadNextChar();
                            loadNextChar();
                            return XMLEntityHandler.CONTENT_RESULT_END_OF_CDSECT;
                        }
                        break;
                    case 4:
                        callCharDataHandler(offset, fCurrentOffset, true);
                        return XMLEntityHandler.CONTENT_RESULT_INVALID_CHAR;
                    }
                } else {
                    if (ch == 0xFFFE || ch == 0xFFFF) {
                        callCharDataHandler(offset, fCurrentOffset, true);
                        return XMLEntityHandler.CONTENT_RESULT_INVALID_CHAR;
                    }
                    ch = loadNextChar();
                }
            }
        } else {
            if (ch == 0xFFFE || ch == 0xFFFF) {
                callCharDataHandler(offset, fCurrentOffset, false);
                return XMLEntityHandler.CONTENT_RESULT_INVALID_CHAR;
            }
            ch = loadNextChar();
        }
        while (true) {
            if (ch == -1) {
                callCharDataHandler(offset, fEndOffset, false);
                return changeReaders().scanContent(element);
            }
            if (ch >= 0x80)
                break;
            if (XMLCharacterProperties.fgAsciiCharData[ch] != 0)
                break;
            ch = loadNextChar();
        }
        while (true) { // REVISIT - EOF check ?
            if (ch < 0x80) {
                switch (XMLCharacterProperties.fgAsciiCharData[ch]) {
                case 0:
                    ch = loadNextChar();
                    break;
                case 1:
                    ch = loadNextChar();
                    if (!fInCDSect) {
                        callCharDataHandler(offset, fCurrentOffset - 1, false);
                        return recognizeMarkup(ch);
                    }
                    break;
                case 2:
                    ch = loadNextChar();
                    if (!fInCDSect) {
                        callCharDataHandler(offset, fCurrentOffset - 1, false);
                        return recognizeReference(ch);
                    }
                    break;
                case 3:
                    ch = loadNextChar();
                    if (ch == ']' && fCurrentOffset + 1 < fEndOffset && fData.charAt(fCurrentOffset + 1) == '>') {
                        callCharDataHandler(offset, fCurrentOffset - 1, false);
                        loadNextChar();
                        loadNextChar();
                        return XMLEntityHandler.CONTENT_RESULT_END_OF_CDSECT;
                    }
                    break;
                case 4:
                    callCharDataHandler(offset, fCurrentOffset, false);
                    return XMLEntityHandler.CONTENT_RESULT_INVALID_CHAR;
                }
            } else {
                if (ch == 0xFFFE || ch == 0xFFFF) {
                    callCharDataHandler(offset, fCurrentOffset, false);
                    return XMLEntityHandler.CONTENT_RESULT_INVALID_CHAR;
                }
                ch = loadNextChar();
            }
            if (ch == -1) {
                callCharDataHandler(offset, fCurrentOffset, false);
                return changeReaders().scanContent(element);
            }
        }
    }
    //
    //
    //
    private void callCharDataHandler(int offset, int endOffset, boolean isWhitespace) throws Exception {
        int length = endOffset - offset;
        if (!fSendCharDataAsCharArray) {
            int stringIndex = addString(offset, length);
            if (isWhitespace)
                fCharDataHandler.processWhitespace(stringIndex);
            else
                fCharDataHandler.processCharacters(stringIndex);
            return;
        }
        if (isWhitespace)
            fCharDataHandler.processWhitespace(fData.toCharArray(), offset, length);
        else
            fCharDataHandler.processCharacters(fData.toCharArray(), offset, length);
    }
    //
    //
    //
    private static final char[] cdata_string = { 'C','D','A','T','A','[' };
    //
    //
    //
    private StringPool fStringPool = null;
    private String fData = null;
    private int fEndOffset;
    private boolean hadTrailingSpace = false;
    private boolean oweTrailingSpace = false;
    private int fMostRecentChar;
    private StringReader fNextFreeReader = null;
    private static StringReader fgFreeReaders = null;
    private boolean fCalledCharPropInit = false;
}