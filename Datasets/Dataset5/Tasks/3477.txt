private int skipAsciiCharData() throws Exception {

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
import org.apache.xerces.utils.CharDataChunk;
import org.apache.xerces.utils.QName;
import org.apache.xerces.utils.StringHasher;
import org.apache.xerces.utils.StringPool;
import org.apache.xerces.utils.XMLCharacterProperties;
import org.apache.xerces.utils.ImplementationMessages;
import org.xml.sax.SAXParseException;
import java.util.Vector;

/**
 * An abstract class for readers that process input data as characters.
 * <p>
 * This is the base class of the CharReader and UTF8CharReader classes.
 * The CharReader classes fills in the "chunks" of data to process from
 * a character stream (java.io.Reader).  The UTF8CharReader performs
 * its own UTF-8 transcoding to fill in the data from an InputStream.
 *
 * @version $Id$
 */
abstract class AbstractCharReader extends XMLEntityReader {

    /**
     * Subclass constructor
     *
     * @param entityHandler The entity handler.
     * @param errorReporter The error reporter.
     * @param sendCharDataAsCharArray true if char data should be reported using
     *                                char arrays instead of string handles.
     * @param stringPool The string pool.
     */
    protected AbstractCharReader(XMLEntityHandler entityHandler, XMLErrorReporter errorReporter, boolean sendCharDataAsCharArray, StringPool stringPool) {
        super(entityHandler, errorReporter, sendCharDataAsCharArray);
        fStringPool = stringPool;
        fCurrentChunk = CharDataChunk.createChunk(fStringPool, null);
    }

    //
    // These instance variables are referenced and updated directly
    // by our subclass from the fillCurrentChunk() method.
    //
    protected CharDataChunk fCurrentChunk = null;
    protected int fCurrentIndex = 0;
    protected char[] fMostRecentData = null;
    protected int fMostRecentChar = 0;
    protected int fLength = 0;

    /**
     * Fill the current chunk the next buffer worth of data.
     *
     * This method should replace any 0xD,0xA sequence with a single
     * 0xA character, and replace single 0xD characters with a 0xA
     * character.  This is described in the spec under section 2.11,
     * "End-of-Line Handling".
     * 
     * @return The value of the first character available for processing.
     * @exception java.lang.Exception
     */
    protected abstract int fillCurrentChunk() throws Exception;

    /**
     * Delay reporting an error message.
     *
     * If there is an error detected in the underlying input stream during
     * the fillCurrentChunk method, the error is described here and will be
     * reported when we reach that offset during normal processing.  The
     * subclass should place a character with a value of zero at that offset,
     * which will be detected here as an invalid character.  When the invalid
     * character is scanned, we will generate the deferred exception.
     *
     * @param errorCode the errorCode to report
     * @param args an array of arguments needed to generate a good error message
     * @param offset the position in the reader where the error occured
     */
    protected void deferException(int errorCode, Object[] args, int offset) {
        if (fDeferredErrors == null)
            fDeferredErrors = new Vector();
        DeferredError de = new DeferredError(errorCode, args, offset);
        fDeferredErrors.addElement(de);
    }

    /**
     * Change readers at end of input.
     *
     * We override our superclass method to release the final chunk
     * of the input data before handing off to the next reader.
     *
     * @return The next reader used to continue processing the document.
     */
    protected XMLEntityHandler.EntityReader changeReaders() throws Exception {
        XMLEntityHandler.EntityReader nextReader = super.changeReaders();
        fCurrentChunk.releaseChunk();
        fCurrentChunk = null;
        return nextReader;
    }

    //
    // XMLEntityHandler.EntityReader implementation
    //
    // The first five methods of the interface are implemented
    // in the XMLEntityHandler base class for us, namely
    //
    //    public int currentOffset();
    //    public int getLineNumber();
    //    public int getColumnNumber();
    //    public void setInCDSect(boolean inCDSect);
    //    public boolean getInCDSect();
    //

    /**
     * Append the characters processed by this reader associated with <code>offset</code> and
     * <code>length</code> to the <code>CharBuffer</code>.
     *
     * @param charBuffer The <code>CharBuffer</code> to append the characters to.
     * @param offset The offset within this reader where the copy should start.
     * @param length The length within this reader where the copy should stop.
     */
    public void append(XMLEntityHandler.CharBuffer charBuffer, int offset, int length) {
        fCurrentChunk.append(charBuffer, offset, length);
    }

    /**
     * Add a string to the <code>StringPool</code> from the characters scanned using this
     * reader as described by <code>offset</code> and <code>length</code>.
     *
     * @param offset The offset within this reader where the characters start.
     * @param length The length within this reader where the characters end.
     * @return The <code>StringPool</code> handle for the string.
     */
    public int addString(int offset, int length) {
        if (length == 0)
            return 0;
        return fCurrentChunk.addString(offset, length);
    }

    /**
     * Add a symbol to the <code>StringPool</code> from the characters scanned using this
     * reader as described by <code>offset</code> and <code>length</code>.
     *
     * @param offset The offset within this reader where the characters start.
     * @param length The length within this reader where the characters end.
     * @return The <code>StringPool</code> handle for the symbol.
     */
    public int addSymbol(int offset, int length) {
        if (length == 0)
            return 0;
        return fCurrentChunk.addSymbol(offset, length, 0);
    }

    /**
     *
     */
    public boolean lookingAtChar(char chr, boolean skipPastChar) throws Exception {
        int ch = fMostRecentChar;
        if (ch != chr) {
            if (ch == 0) {
                if (atEOF(fCurrentOffset + 1)) {
                    return changeReaders().lookingAtChar(chr, skipPastChar);
                }
            }
            return false;
        }
        if (skipPastChar) {
            fCharacterCounter++;
            fCurrentOffset++;
            if (++fCurrentIndex == CharDataChunk.CHUNK_SIZE)
                slowLoadNextChar();
            else
                fMostRecentChar = fMostRecentData[fCurrentIndex] & 0xFFFF;
        }
        return true;
    }

    /**
     *
     */
    public boolean lookingAtValidChar(boolean skipPastChar) throws Exception {
        int ch = fMostRecentChar;
        if (ch < 0xD800) {
            if (ch >= 0x20 || ch == 0x09) {
                if (skipPastChar) {
                    fCharacterCounter++;
                    loadNextChar();
                }
                return true;
            }
            if (ch == 0x0A) {
                if (skipPastChar) {
                    fLinefeedCounter++;
                    fCharacterCounter = 1;
                    loadNextChar();
                }
                return true;
            }
            if (ch == 0) {
                if (atEOF(fCurrentOffset + 1)) {
                    return changeReaders().lookingAtValidChar(skipPastChar);
                }
            }
            return false;
        }
        if (ch > 0xFFFD) {
            return false;
        }
        if (ch < 0xDC00) {
            CharDataChunk savedChunk = fCurrentChunk;
            int savedIndex = fCurrentIndex;
            int savedOffset = fCurrentOffset;
            ch = loadNextChar();
            boolean valid = (ch >= 0xDC00 && ch < 0xE000);
            if (!valid || !skipPastChar) {
                fCurrentChunk = savedChunk;
                fCurrentIndex = savedIndex;
                fCurrentOffset = savedOffset;
                fMostRecentData = savedChunk.toCharArray();
                fMostRecentChar = fMostRecentData[savedIndex] & 0xFFFF;
                return valid;
            }
        } else if (ch < 0xE000) {
            return false;
        }
        if (skipPastChar) {
            fCharacterCounter++;
            loadNextChar();
        }
        return true;
    }

    /**
     *
     */
    public boolean lookingAtSpace(boolean skipPastChar) throws Exception {
        int ch = fMostRecentChar;
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
        } else {
            if (ch == 0) { // REVISIT - should we be checking this here ?
                if (atEOF(fCurrentOffset + 1)) {
                    return changeReaders().lookingAtSpace(skipPastChar);
                }
            }
            return false;
        }
        fCurrentOffset++;
        if (++fCurrentIndex == CharDataChunk.CHUNK_SIZE)
            slowLoadNextChar();
        else
            fMostRecentChar = fMostRecentData[fCurrentIndex] & 0xFFFF;
        return true;
    }

    /**
     *
     */
    public void skipToChar(char chr) throws Exception {
        //
        // REVISIT - this will skip invalid characters without reporting them.
        //
        int ch = fMostRecentChar;
        while (true) {
            if (ch == chr)
                return;
            if (ch == 0) {
                if (atEOF(fCurrentOffset + 1)) {
                    changeReaders().skipToChar(chr);
                    return;
                }
                fCharacterCounter++;
            } else if (ch == 0x0A) {
                fLinefeedCounter++;
                fCharacterCounter = 1;
            } else if (ch >= 0xD800 && ch < 0xDC00) {
                fCharacterCounter++;
                ch = loadNextChar();
                if (ch < 0xDC00 || ch >= 0xE000)
                    continue;
            } else
                fCharacterCounter++;
            ch = loadNextChar();
        }
    }

    /**
     *
     */
    public void skipPastSpaces() throws Exception {
        int ch = fMostRecentChar;
        while (true) {
            if (ch == 0x20 || ch == 0x09) {
                fCharacterCounter++;
            } else if (ch == 0x0A) {
                fLinefeedCounter++;
                fCharacterCounter = 1;
            } else {
                if (ch == 0 && atEOF(fCurrentOffset + 1))
                    changeReaders().skipPastSpaces();
                return;
            }
            ch = loadNextChar();
        }
    }

    /**
     *
     */
    public void skipPastName(char fastcheck) throws Exception {
        int ch = fMostRecentChar;
        if (ch < 0x80) {
            if (XMLCharacterProperties.fgAsciiInitialNameChar[ch] == 0)
                return;
        } else {
            if ( ! fCalledCharPropInit) {
                XMLCharacterProperties.initCharFlags();
                fCalledCharPropInit = true;
            }
            if ((XMLCharacterProperties.fgCharFlags[ch] & XMLCharacterProperties.E_InitialNameCharFlag) == 0)
                return;
        }
        while (true) {
            fCharacterCounter++;
            ch = loadNextChar();
            if (fastcheck == ch)
                return;
            if (ch < 0x80) {
                if (XMLCharacterProperties.fgAsciiNameChar[ch] == 0)
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

    /**
     *
     */
    public void skipPastNmtoken(char fastcheck) throws Exception {
        int ch = fMostRecentChar;
        while (true) {
            if (fastcheck == ch)
                return;
            if (ch < 0x80) {
                if (XMLCharacterProperties.fgAsciiNameChar[ch] == 0)
                    return;
            } else {
                if (!fCalledCharPropInit) {
                    XMLCharacterProperties.initCharFlags();
                    fCalledCharPropInit = true;
                }
                if ((XMLCharacterProperties.fgCharFlags[ch] & XMLCharacterProperties.E_NameCharFlag) == 0)
                    return;
            }
            fCharacterCounter++;
            ch = loadNextChar();
        }
    }

    /**
     *
     */
    public boolean skippedString(char[] s) throws Exception {
        int length = s.length;
        char[] data = fMostRecentData;
        int index = fCurrentIndex;
        if (index + length <= CharDataChunk.CHUNK_SIZE) {
            for (int i = 0; i < length; i++) {
                if (data[index++] != s[i])
                    return false;
            }
            fCharacterCounter += length;
            fCurrentOffset += length;
            fCurrentIndex = index;
            if (index == CharDataChunk.CHUNK_SIZE)
                slowLoadNextChar();
            else
                fMostRecentChar = data[index] & 0xFFFF;
            return true;
        }
        CharDataChunk dataChunk = fCurrentChunk;
        int offset = fCurrentOffset;
        int savedIndex = index;
        int i = 0;
        while (index < CharDataChunk.CHUNK_SIZE) {
            if (data[index++] != s[i++])
                return false;
        }
        slowLoadNextChar();
        data = fMostRecentData;
        index = 0;
        while (i < length) {
            if (data[index++] != s[i++]) {
                fCurrentChunk = dataChunk;
                fCurrentIndex = savedIndex;
                fCurrentOffset = offset;
                fMostRecentData = dataChunk.toCharArray();
                fMostRecentChar = fMostRecentData[savedIndex] & 0xFFFF;
                return false;
            }
        }
        fCharacterCounter += length;
        fCurrentOffset += length;
        fCurrentIndex = index;
        if (index == CharDataChunk.CHUNK_SIZE)
            slowLoadNextChar();
        else
            fMostRecentChar = data[index] & 0xFFFF;
        return true;
    }

    /**
     *
     */
    public int scanInvalidChar() throws Exception {
        int ch = fMostRecentChar;
        if (ch == 0x0A) {
            fLinefeedCounter++;
            fCharacterCounter = 1;
            loadNextChar();
        } else if (ch == 0) {
            if (atEOF(fCurrentOffset + 1)) {
                return changeReaders().scanInvalidChar();
            }
            if (fDeferredErrors != null) {
                for (int i = 0; i < fDeferredErrors.size(); i++) {
                    DeferredError de = (DeferredError)fDeferredErrors.elementAt(i);
                    if (de.offset == fCurrentIndex) {
                        fErrorReporter.reportError(fErrorReporter.getLocator(),
                                                   ImplementationMessages.XERCES_IMPLEMENTATION_DOMAIN,
                                                   de.errorCode,
                                                   0,
                                                   de.args,
                                                   XMLErrorReporter.ERRORTYPE_FATAL_ERROR);
                        fDeferredErrors.removeElementAt(i);
                        fCharacterCounter++;
                        loadNextChar();
                        return -1;
                    }
                }
            }
            fCharacterCounter++;
            loadNextChar();
        } else {
            fCharacterCounter++;
            if (ch >= 0xD800 && ch < 0xDC00) {
                int ch2 = loadNextChar();
                if (ch2 >= 0xDC00 && ch2 < 0xE000) {
                    ch = ((ch-0xD800)<<10)+(ch2-0xDC00)+0x10000;
                    loadNextChar();
                }
            } else
                loadNextChar();
        }
        return ch;
    }

    /**
     *
     */
    public int scanCharRef(boolean hex) throws Exception {
        int ch = fMostRecentChar;
        if (ch == 0) {
            if (atEOF(fCurrentOffset + 1)) {
                return changeReaders().scanCharRef(hex);
            }
            return XMLEntityHandler.CHARREF_RESULT_INVALID_CHAR;
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
        loadNextChar();
        boolean toobig = false;
        while (true) {
            ch = fMostRecentChar;
            if (ch == 0)
                break;
            if (hex) {
                if (ch > 'f' || XMLCharacterProperties.fgAsciiXDigitChar[ch] == 0)
                    break;
            } else {
                if (ch < '0' || ch > '9')
                    break;
            }
            fCharacterCounter++;
            loadNextChar();
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
        loadNextChar();
        if (toobig)
            return XMLEntityHandler.CHARREF_RESULT_OUT_OF_RANGE;
        return num;
    }

    /**               
     *
     */
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
    /**
     *
     */
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
    /**
     *
     */
    public int scanEntityValue(int qchar, boolean createString) throws Exception
    {
        int offset = fCurrentOffset;
        while (true) {
            if (atEOF(fCurrentOffset + 1)) {
                changeReaders();
                return XMLEntityHandler.ENTITYVALUE_RESULT_END_OF_INPUT;
            }
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

    /**
     *
     */
    public int scanName(char fastcheck) throws Exception {
        int ch = fMostRecentChar;
        if (ch < 0x80) {
            if (XMLCharacterProperties.fgAsciiInitialNameChar[ch] == 0)
                return -1;
        } else {
            if (!fCalledCharPropInit) {
                XMLCharacterProperties.initCharFlags();
                fCalledCharPropInit = true;
            }
            if ((XMLCharacterProperties.fgCharFlags[ch] & XMLCharacterProperties.E_InitialNameCharFlag) == 0)
                return -1;
        }
        int offset = fCurrentOffset;
        int index = fCurrentIndex;
        char[] data = fMostRecentData;
        if (++index == CharDataChunk.CHUNK_SIZE) {
            slowLoadNextChar();
            index = 0;
            data = fMostRecentData;
        }
        fCharacterCounter++;
        fCurrentOffset++;
        int hashcode = 0;
        while (true) {
            hashcode = StringHasher.hashChar(hashcode, ch);
            ch = data[index] & 0xFFFF;
            if (fastcheck == ch)
                break;
            if (ch < 0x80) {
                if (XMLCharacterProperties.fgAsciiNameChar[ch] == 0)
                    break;
            } else {
                if (!fCalledCharPropInit) {
                    XMLCharacterProperties.initCharFlags();
                    fCalledCharPropInit = true;
                }
                if ((XMLCharacterProperties.fgCharFlags[ch] & XMLCharacterProperties.E_NameCharFlag) == 0)
                    break;
            }
            if (++index == CharDataChunk.CHUNK_SIZE) {
                slowLoadNextChar();
                index = 0;
                data = fMostRecentData;
            }
            fCharacterCounter++;
            fCurrentOffset++;
        }
        fCurrentIndex = index;
        fMostRecentChar = ch;
        hashcode = StringHasher.finishHash(hashcode);
        int length = fCurrentOffset - offset;
        int nameIndex = fCurrentChunk.addSymbol(offset, length, hashcode);
        return nameIndex;
    }

    /**
     *
     */
    public boolean scanExpectedName(char fastcheck, StringPool.CharArrayRange expectedName) throws Exception {
        char[] expected = expectedName.chars;
        int offset = expectedName.offset;
        int len = expectedName.length;
        int ch = fMostRecentChar;
        for (int i = 0; i < len; i++) {
            if (ch != expected[offset++]) {
                skipPastNmtoken(fastcheck);
                return false;
            }
            fCharacterCounter++;
            fCurrentOffset++;
            if (++fCurrentIndex == CharDataChunk.CHUNK_SIZE)
                ch = slowLoadNextChar();
            else
                ch = (fMostRecentChar = fMostRecentData[fCurrentIndex] & 0xFFFF);
        }
        if (ch == fastcheck)
            return true;
        if (ch < 0x80) {
            if (XMLCharacterProperties.fgAsciiNameChar[ch] == 0)
                return true;
        } else {
            if (!fCalledCharPropInit) {
                XMLCharacterProperties.initCharFlags();
                fCalledCharPropInit = true;
            }
            if ((XMLCharacterProperties.fgCharFlags[ch] & XMLCharacterProperties.E_NameCharFlag) == 0)
                return true;
        }
        skipPastNmtoken(fastcheck);
        return false;
    }

    /**
     *
     */
    public void scanQName(char fastcheck, QName qname) throws Exception {
        int ch = fMostRecentChar;
        if (ch < 0x80) {
            if (XMLCharacterProperties.fgAsciiInitialNameChar[ch] == 0) {
                qname.clear();
                return;
            }
            if (ch == ':') {
                qname.clear();
                return;
            }
        } else {
            if (!fCalledCharPropInit) {
                XMLCharacterProperties.initCharFlags();
                fCalledCharPropInit = true;
            }
            if ((XMLCharacterProperties.fgCharFlags[ch] & XMLCharacterProperties.E_InitialNameCharFlag) == 0) {
                qname.clear();
                return;
            }
        }
        int offset = fCurrentOffset;
        int index = fCurrentIndex;
        char[] data = fMostRecentData;
        if (++index == CharDataChunk.CHUNK_SIZE) {
            slowLoadNextChar();
            index = 0;
            data = fMostRecentData;
        }
        fCharacterCounter++;
        fCurrentOffset++;
        int hashcode = 0;
        int prefixend = -1;
        while (true) {
            hashcode = StringHasher.hashChar(hashcode, ch);
            ch = data[index] & 0xFFFF;
            if (fastcheck == ch)
                break;
            if (ch < 0x80) {
                if (XMLCharacterProperties.fgAsciiNameChar[ch] == 0)
                    break;
                if (ch == ':') {
                    if (prefixend != -1)
                        break;
                    prefixend = fCurrentOffset;
                    //
                    // We need to peek ahead one character.  If the next character is not a
                    // valid initial name character, or is another colon, then we cannot meet
                    // both the Prefix and LocalPart productions for the QName production,
                    // which means that there is no Prefix and we need to terminate the QName
                    // at the first colon.
                    //
                    if (index + 1 == CharDataChunk.CHUNK_SIZE) {
                        CharDataChunk savedChunk = fCurrentChunk;
                        int savedOffset = fCurrentOffset;
                        ch = slowLoadNextChar();
                        fCurrentChunk = savedChunk;
                        fCurrentOffset = savedOffset;
                        fMostRecentData = savedChunk.toCharArray();
                    } else
                        ch = data[index + 1] & 0xFFFF;
                    boolean lpok = true;
                    if (ch < 0x80) {
                        if (XMLCharacterProperties.fgAsciiInitialNameChar[ch] == 0 || ch == ':')
                            lpok = false;
                    } else {
                        if (!fCalledCharPropInit) {
                            XMLCharacterProperties.initCharFlags();
                            fCalledCharPropInit = true;
                        }
                        if ((XMLCharacterProperties.fgCharFlags[ch] & XMLCharacterProperties.E_InitialNameCharFlag) == 0)
                            lpok = false;
                    }
                    ch = ':';
                    if (!lpok) {
                        prefixend = -1;
                        break;
                    }
                }
            } else {
                if (!fCalledCharPropInit) {
                    XMLCharacterProperties.initCharFlags();
                    fCalledCharPropInit = true;
                }
                if ((XMLCharacterProperties.fgCharFlags[ch] & XMLCharacterProperties.E_NameCharFlag) == 0)
                    break;
            }
            if (++index == CharDataChunk.CHUNK_SIZE) {
                slowLoadNextChar();
                index = 0;
                data = fMostRecentData;
            }
            fCharacterCounter++;
            fCurrentOffset++;
        }
        fCurrentIndex = index;
        fMostRecentChar = ch;
        hashcode = StringHasher.finishHash(hashcode);
        int length = fCurrentOffset - offset;
        qname.rawname = fCurrentChunk.addSymbol(offset, length, hashcode);
        qname.prefix = prefixend == -1 ? -1 : addSymbol(offset, prefixend - offset);
        qname.localpart = prefixend == -1 ? qname.rawname : addSymbol(prefixend + 1, fCurrentOffset - (prefixend + 1));
        qname.uri = -1;

    } // scanQName(char,QName)

    //
    // [14] CharData ::= [^<&]* - ([^<&]* ']]>' [^<&]*)
    //
    /**
     *
     */
    public int scanContent(QName element) throws Exception {
        if (fCallClearPreviousChunk && fCurrentChunk.clearPreviousChunk())
            fCallClearPreviousChunk = false;
        int charDataOffset = fCurrentOffset;
        int ch = fMostRecentChar;
        if (ch < 0x80) {
            switch (XMLCharacterProperties.fgAsciiWSCharData[ch]) {
            case 0:
                fCharacterCounter++;
                ch = loadNextChar();
                break;
            case 1: // '<'
                fCharacterCounter++;
                ch = loadNextChar();
                if (!fInCDSect) {
                    return recognizeMarkup(ch);
                }
                break;
            case 2: // '&'
                fCharacterCounter++;
                ch = loadNextChar();
                if (!fInCDSect) {
                    return recognizeReference(ch);
                }
                break;
            case 3: // ']'
                fCharacterCounter++;
                ch = loadNextChar();
                if (ch != ']')
                    break;
                if (fCurrentIndex + 1 == CharDataChunk.CHUNK_SIZE) {
                    CharDataChunk dataChunk = fCurrentChunk;
                    int index = fCurrentIndex;
                    int offset = fCurrentOffset;
                    if (loadNextChar() != '>') {
                        fCurrentChunk = dataChunk;
                        fCurrentIndex = index;
                        fCurrentOffset = offset;
                        fMostRecentData = dataChunk.toCharArray();
                        fMostRecentChar = ']';
                        break;
                    }
                } else {
                    if (fMostRecentData[fCurrentIndex + 1] != '>')
                        break;
                    fCurrentIndex++;
                    fCurrentOffset++;
                }
                loadNextChar();
                fCharacterCounter += 2;
                return XMLEntityHandler.CONTENT_RESULT_END_OF_CDSECT;
            case 4: // invalid char
                if (ch == 0 && atEOF(fCurrentOffset + 1)) {
                    changeReaders();
                    return XMLEntityHandler.CONTENT_RESULT_INVALID_CHAR; // REVISIT - not quite...
                }
                return XMLEntityHandler.CONTENT_RESULT_INVALID_CHAR;
            case 5:
                do {
                    if (ch == 0x0A) {
                        fLinefeedCounter++;
                        fCharacterCounter = 1;
                    } else
                        fCharacterCounter++;
                    ch = loadNextChar();
                } while (ch == 0x20 || ch == 0x09 || ch == 0x0A);
                if (ch < 0x80) {
                    switch (XMLCharacterProperties.fgAsciiCharData[ch]) {
                    case 0:
                        fCharacterCounter++;
                        ch = loadNextChar();
                        break;
                    case 1: // '<'
                        if (!fInCDSect) {
                            callCharDataHandler(charDataOffset, fCurrentOffset, true);
                            fCharacterCounter++;
                            ch = loadNextChar();
                            return recognizeMarkup(ch);
                        }
                        fCharacterCounter++;
                        ch = loadNextChar();
                        break;
                    case 2: // '&'
                        if (!fInCDSect) {
                            callCharDataHandler(charDataOffset, fCurrentOffset, true);
                            fCharacterCounter++;
                            ch = loadNextChar();
                            return recognizeReference(ch);
                        }
                        fCharacterCounter++;
                        ch = loadNextChar();
                        break;
                    case 3: // ']'
                        int endOffset = fCurrentOffset;
                        ch = loadNextChar();
                        if (ch != ']') {
                            fCharacterCounter++;
                            break;
                        }
                        if (fCurrentIndex + 1 == CharDataChunk.CHUNK_SIZE) {
                            CharDataChunk dataChunk = fCurrentChunk;
                            int index = fCurrentIndex;
                            int offset = fCurrentOffset;
                            if (loadNextChar() != '>') {
                                fCurrentChunk = dataChunk;
                                fCurrentIndex = index;
                                fCurrentOffset = offset;
                                fMostRecentData = dataChunk.toCharArray();
                                fMostRecentChar = ']';
                                fCharacterCounter++;
                                break;
                            }
                        } else {
                            if (fMostRecentData[fCurrentIndex + 1] != '>') {
                                fCharacterCounter++;
                                break;
                            }
                            fCurrentIndex++;
                            fCurrentOffset++;
                        }
                        loadNextChar();
                        callCharDataHandler(charDataOffset, endOffset, true);
                        fCharacterCounter += 3;
                        return XMLEntityHandler.CONTENT_RESULT_END_OF_CDSECT;
                    case 4: // invalid char
                        callCharDataHandler(charDataOffset, fCurrentOffset, true);
                        if (ch == 0 && atEOF(fCurrentOffset + 1)) {
                            changeReaders();
                            return XMLEntityHandler.CONTENT_RESULT_INVALID_CHAR; // REVISIT - not quite...
                        }
                        return XMLEntityHandler.CONTENT_RESULT_INVALID_CHAR;
                    }
                } else if (!skipMultiByteCharData(ch)) {
                    callCharDataHandler(charDataOffset, fCurrentOffset, true);
                    return XMLEntityHandler.CONTENT_RESULT_INVALID_CHAR;
                }
                break;
            }
        } else if (!skipMultiByteCharData(ch)) {
            return XMLEntityHandler.CONTENT_RESULT_INVALID_CHAR;
        }
        ch = skipAsciiCharData();
        while (true) {
            if (ch < 0x80) {
                switch (XMLCharacterProperties.fgAsciiCharData[ch]) {
                case 0:
                    fCharacterCounter++;
                    ch = loadNextChar();
                    break;
                case 1: // '<'
                    if (!fInCDSect) {
                        callCharDataHandler(charDataOffset, fCurrentOffset, false);
                        fCharacterCounter++;
                        ch = loadNextChar();
                        return recognizeMarkup(ch);
                    }
                    fCharacterCounter++;
                    ch = loadNextChar();
                    break;
                case 2: // '&'
                    if (!fInCDSect) {
                        callCharDataHandler(charDataOffset, fCurrentOffset, false);
                        fCharacterCounter++;
                        ch = loadNextChar();
                        return recognizeReference(ch);
                    }
                    fCharacterCounter++;
                    ch = loadNextChar();
                    break;
                case 3: // ']'
                    int endOffset = fCurrentOffset;
                    ch = loadNextChar();
                    if (ch != ']') {
                        fCharacterCounter++;
                        break;
                    }
                    if (fCurrentIndex + 1 == CharDataChunk.CHUNK_SIZE) {
                        CharDataChunk dataChunk = fCurrentChunk;
                        int index = fCurrentIndex;
                        int offset = fCurrentOffset;
                        if (loadNextChar() != '>') {
                            fCurrentChunk = dataChunk;
                            fCurrentIndex = index;
                            fCurrentOffset = offset;
                            fMostRecentData = dataChunk.toCharArray();
                            fMostRecentChar = ']';
                            fCharacterCounter++;
                            break;
                        }
                    } else {
                        if (fMostRecentData[fCurrentIndex + 1] != '>') {
                            fCharacterCounter++;
                            break;
                        }
                        fCurrentIndex++;
                        fCurrentOffset++;
                    }
                    loadNextChar();
                    callCharDataHandler(charDataOffset, endOffset, false);
                    fCharacterCounter += 3;
                    return XMLEntityHandler.CONTENT_RESULT_END_OF_CDSECT;
                case 4: // invalid char
                    if (ch == 0x0A) {
                        fLinefeedCounter++;
                        fCharacterCounter = 1;
                        ch = loadNextChar();
                        break;
                    }
                    callCharDataHandler(charDataOffset, fCurrentOffset, false);
                    if (ch == 0 && atEOF(fCurrentOffset + 1)) {
                        changeReaders();
                        return XMLEntityHandler.CONTENT_RESULT_INVALID_CHAR; // REVISIT - not quite...
                    }
                    return XMLEntityHandler.CONTENT_RESULT_INVALID_CHAR;
                }
            } else {
                if (!skipMultiByteCharData(ch)) {
                    callCharDataHandler(charDataOffset, fCurrentOffset, false);
                    return XMLEntityHandler.CONTENT_RESULT_INVALID_CHAR;
                }
                ch = fMostRecentChar;
            }
        }
    }

    //
    // Private data members
    //
    private static final char[] cdata_string = { 'C','D','A','T','A','[' };
    private StringPool fStringPool = null;
    private boolean fCalledCharPropInit = false;
    private boolean fCallClearPreviousChunk = true;
    private Vector fDeferredErrors = null;

    //
    // Private classes
    //
    private class DeferredError {
        int errorCode;
        Object[] args;
        int offset;
        DeferredError(int ec, Object[] a, int o) {
            errorCode = ec;
            args = a;
            offset = o;
        }
    }

    //
    // Private methods
    //

    /*
     * Return a result code for scanContent when the character data
     * ends with a less-than character.
     */
    private int recognizeMarkup(int ch) throws Exception {
        switch (ch) {
        case 0:
            return XMLEntityHandler.CONTENT_RESULT_MARKUP_END_OF_INPUT;
        case '?':
            fCharacterCounter++;
            loadNextChar();
            return XMLEntityHandler.CONTENT_RESULT_START_OF_PI;
        case '!':
            fCharacterCounter++;
            ch = loadNextChar();
            if (ch == 0) {
                fCharacterCounter--;
                fCurrentOffset--;
                return XMLEntityHandler.CONTENT_RESULT_MARKUP_END_OF_INPUT;
            }
            if (ch == '-') {
                fCharacterCounter++;
                ch = loadNextChar();
                if (ch == 0) {
                    fCharacterCounter -= 2;
                    fCurrentOffset -= 2;
                    return XMLEntityHandler.CONTENT_RESULT_MARKUP_END_OF_INPUT;
                }
                if (ch == '-') {
                    fCharacterCounter++;
                    loadNextChar();
                    return XMLEntityHandler.CONTENT_RESULT_START_OF_COMMENT;
                }
                break;
            }
            if (ch == '[') {
                for (int i = 0; i < 6; i++) {
                    fCharacterCounter++;
                    ch = loadNextChar();
                    if (ch == 0) {
                        fCharacterCounter -= (2 + i);
                        fCurrentOffset -= (2 + i);
                        return XMLEntityHandler.CONTENT_RESULT_MARKUP_END_OF_INPUT;
                    }
                    if (ch != cdata_string[i]) {
                        return XMLEntityHandler.CONTENT_RESULT_MARKUP_NOT_RECOGNIZED;
                    }
                }
                fCharacterCounter++;
                loadNextChar();
                return XMLEntityHandler.CONTENT_RESULT_START_OF_CDSECT;
            }
            break;
        case '/':
            fCharacterCounter++;
            loadNextChar();
            return XMLEntityHandler.CONTENT_RESULT_START_OF_ETAG;
        default:
            return XMLEntityHandler.CONTENT_RESULT_START_OF_ELEMENT;
        }
        return XMLEntityHandler.CONTENT_RESULT_MARKUP_NOT_RECOGNIZED;
    }

    /*
     * Return a result code for scanContent when the character data
     * ends with an ampersand character.
     */
    private int recognizeReference(int ch) throws Exception {
        if (ch == 0) {
            return XMLEntityHandler.CONTENT_RESULT_REFERENCE_END_OF_INPUT;
        }
        //
        // [67] Reference ::= EntityRef | CharRef
        // [68] EntityRef ::= '&' Name ';'
        // [66] CharRef ::= '&#' [0-9]+ ';' | '&#x' [0-9a-fA-F]+ ';'
        //
        if (ch == '#') {
            fCharacterCounter++;
            loadNextChar();
            return XMLEntityHandler.CONTENT_RESULT_START_OF_CHARREF;
        } else {
            return XMLEntityHandler.CONTENT_RESULT_START_OF_ENTITYREF;
        }
    }

    /*
     * Skip over a multi-byte character.
     */
    private boolean skipMultiByteCharData(int ch) throws Exception {
        if (ch < 0xD800) {
            loadNextChar();
            return true;
        }
        if (ch > 0xFFFD)
            return false;
        if (ch >= 0xDC00 && ch < 0xE000)
            return false;
        if (ch >= 0xD800 && ch < 0xDC00) {
            CharDataChunk savedChunk = fCurrentChunk;
            int savedIndex = fCurrentIndex;
            int savedOffset = fCurrentOffset;
            ch = loadNextChar();
            if (ch < 0xDC00 || ch >= 0xE000) {
                fCurrentChunk = savedChunk;
                fCurrentIndex = savedIndex;
                fCurrentOffset = savedOffset;
                fMostRecentData = savedChunk.toCharArray();
                fMostRecentChar = fMostRecentData[savedIndex] & 0xFFFF;
                return false;
            }
        }
        loadNextChar();
        return true;
    }

    /*
     * Skip over contiguous ascii character data.
     *
     * @return the character skipped
     * @exception java.lang.Exception
     */
    private int fskipAsciiCharData() throws Exception {
        int index = fCurrentIndex;
        int offset = fCurrentOffset - index;
        while (true) {
            char[] data = fMostRecentData;
            while (index < CharDataChunk.CHUNK_SIZE) {
                int ch = data[index] & 0xFFFF;
                if (ch >= 0x80) {
                    fCurrentOffset = offset + index;
                    fCurrentIndex = index;
                    fMostRecentChar = ch;
                    return ch;
                }
                if (XMLCharacterProperties.fgAsciiCharData[ch] == 0) {
                    fCharacterCounter++;
                } else if (ch == 0x0A) {
                    fLinefeedCounter++;
                    fCharacterCounter = 1;
                } else {
                    fCurrentOffset = offset + index;
                    fCurrentIndex = index;
                    fMostRecentChar = ch;
                    return ch;
                }
                index++;
            }
            offset += index;
            slowLoadNextChar();
            index = 0;
        }
    }

    /*
     * Report character data to the parser through the entity handler interface.
     *
     * @param offset the offset of the start of the character data
     * @param endOffset the offset of the end of the character data
     * @param isWhitespace true if the character data is whitespace
     * @exception java.lang.Exception
     */
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

        CharDataChunk dataChunk = fCurrentChunk.chunkFor(offset);
        int index = offset & CharDataChunk.CHUNK_MASK;
        if (index + length <= CharDataChunk.CHUNK_SIZE) {
            //
            // All the chars are in the same chunk
            //
            if (length != 0) {
                if (isWhitespace)
                    fCharDataHandler.processWhitespace(dataChunk.toCharArray(), index, length);
                else
                    fCharDataHandler.processCharacters(dataChunk.toCharArray(), index, length);
            }
            return;
        }

        //
        // The data is spread across chunks.
        //
        int count = length;
        int nbytes = CharDataChunk.CHUNK_SIZE - index;
        if (isWhitespace)
            fCharDataHandler.processWhitespace(dataChunk.toCharArray(), index, nbytes);
        else
            fCharDataHandler.processCharacters(dataChunk.toCharArray(), index, nbytes);
        count -= nbytes;

        //
        // Use each Chunk in turn until we are done.
        //
        do {
            dataChunk = dataChunk.nextChunk();
            if (dataChunk == null) {
                throw new RuntimeException(new ImplementationMessages().createMessage(null, ImplementationMessages.INT_DCN, 0, null));
            }
            nbytes = count <= CharDataChunk.CHUNK_SIZE ? count : CharDataChunk.CHUNK_SIZE;
            if (isWhitespace)
                fCharDataHandler.processWhitespace(dataChunk.toCharArray(), 0, nbytes);
            else
                fCharDataHandler.processCharacters(dataChunk.toCharArray(), 0, nbytes);
            count -= nbytes;
        } while (count > 0);
    }

    /*
     * Advance the reader's notion of where it is, moving on to the next chunk.
     *
     * @return The next character that will be processed.
     * @exception java.lang.Exception
     */
    private int slowLoadNextChar() throws Exception {
        fCallClearPreviousChunk = true;
        if (fCurrentChunk.nextChunk() != null) {
            fCurrentChunk = fCurrentChunk.nextChunk();
            fCurrentIndex = 0;
            fMostRecentData = fCurrentChunk.toCharArray();
            return (fMostRecentChar = fMostRecentData[fCurrentIndex] & 0xFFFF);
        } else {
            fCurrentChunk = CharDataChunk.createChunk(fStringPool, fCurrentChunk);
            return fillCurrentChunk();
        }
    }

    /*
     * Advance the reader's notion of where it is
     *
     * @return The next character that will be processed.
     * @exception java.lang.Exception
     */
    private int loadNextChar() throws Exception {
        fCurrentOffset++;
        if (++fCurrentIndex == CharDataChunk.CHUNK_SIZE)
            return slowLoadNextChar();
        return (fMostRecentChar = fMostRecentData[fCurrentIndex] & 0xFFFF);
    }

    /*
     * Would the reader be at end of file at a given offset?
     *
     * @param offset the offset to test for being at EOF
     * @return true if being at offset would mean being at or beyond EOF
     */
    private boolean atEOF(int offset) {
        return (offset > fLength);
    }

}