if (fOutputOffset == CharDataChunk.CHUNK_SIZE) {

/*
 * The Apache Software License, Version 1.1
 *
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
import org.apache.xerces.utils.StringPool;
import java.io.Reader;

/**
 * General purpose character stream reader.
 *
 * This class is used when the input source for the document entity is
 * specified using a character stream, when the input source is specified
 * using a byte stream with an explicit encoding, or when a recognizer
 * scans the encoding decl from the byte stream and chooses to use this
 * reader class for that encoding.  For the latter two cases, the byte
 * stream is wrapped in the appropriate InputStreamReader using the
 * desired encoding.
 *
 * @version
 */
final class CharReader extends AbstractCharReader {
    //
    //
    //
    CharReader(XMLEntityHandler entityHandler, XMLErrorReporter errorReporter, boolean sendCharDataAsCharArray, Reader reader, StringPool stringPool) throws Exception {
        super(entityHandler, errorReporter, sendCharDataAsCharArray, stringPool);
        fCharacterStream = reader;
        fillCurrentChunk();
    }
    //
    //
    //
    private Reader fCharacterStream = null;
    //
    // When we fill a chunk there may be data that was read from the
    // input stream that has not been "processed".  We need to save
    // that data, and any in-progress state, between the calls to
    // fillCurrentChunk() in these instance variables.  
    //
    private boolean fCheckOverflow = false;
    private char[] fOverflow = null;
    private int fOverflowOffset = 0;
    private int fOverflowEnd = 0;
    private int fOutputOffset = 0;
    private boolean fSkipLinefeed = false;
    //
    //
    //
    protected int fillCurrentChunk() throws Exception {
        //
        // See if we can find a way to reuse the buffer that may have been returned
        // with a recyled data chunk.
        //
        char[] recycledData = fCurrentChunk.toCharArray();
        //
        // If we have overflow from the last call, normalize from where
        // we left off, copying into the front of the output buffer.
        //
        fOutputOffset = 0;
        if (fCheckOverflow) {
            //
            // The fOverflowEnd should always be equal to CHUNK_SIZE, unless we hit
            // EOF during the previous call.  Copy the remaining data to the front
            // of the buffer and return it as the final chunk.
            //
            fMostRecentData = recycledData;
            if (fOverflowEnd < CharDataChunk.CHUNK_SIZE) {
                recycledData = null;
                if (fOverflowEnd > 0) {
                    if (fMostRecentData == null || fMostRecentData.length < 1 + fOverflowEnd - fOverflowOffset)
                        fMostRecentData = new char[1 + fOverflowEnd - fOverflowOffset];
                    copyNormalize(fOverflow, fOverflowOffset, fMostRecentData, fOutputOffset);
                } else {
                    if (fMostRecentData == null)
                        fMostRecentData = new char[1];
                }
                fMostRecentData[fOutputOffset] = 0;
                //
                // Update our instance variables
                //
                fOverflow = null;
                fLength += fOutputOffset;
                fCurrentIndex = 0;
                fCurrentChunk.setCharArray(fMostRecentData);
                return (fMostRecentChar = fMostRecentData[0]);
            }
            if (fMostRecentData == null || fMostRecentData.length < CharDataChunk.CHUNK_SIZE)
                fMostRecentData = new char[CharDataChunk.CHUNK_SIZE];
            else
                recycledData = null;
            copyNormalize(fOverflow, fOverflowOffset, fMostRecentData, fOutputOffset);
            fCheckOverflow = false;
        } else {
            if (fOverflow == null) {
                fOverflow = recycledData;
                if (fOverflow == null || fOverflow.length < CharDataChunk.CHUNK_SIZE)
                    fOverflow = new char[CharDataChunk.CHUNK_SIZE];
                else
                    recycledData = null;
            }
            fMostRecentData = null;
        }
        while (true) {
            fOverflowOffset = 0;
            fOverflowEnd = 0;
            int capacity = CharDataChunk.CHUNK_SIZE;
            int result = 0;
            do {
                try {
                    result = fCharacterStream.read(fOverflow, fOverflowEnd, capacity);
                } catch (java.io.IOException ex) {
                    result = -1;
                }
                if (result == -1) {
                    //
                    // We have reached the end of the stream.
                    //
                    fCharacterStream.close();
                    fCharacterStream = null;
                    if (fMostRecentData == null) {
                        //
                        // There is no previous output data, so we know that all of the
                        // new input data will fit.
                        //
                        fMostRecentData = recycledData;
                        if (fMostRecentData == null || fMostRecentData.length < 1 + fOverflowEnd)
                            fMostRecentData = new char[1 + fOverflowEnd];
                        else
                            recycledData = null;
                        copyNormalize(fOverflow, fOverflowOffset, fMostRecentData, fOutputOffset);
                        fOverflow = null;
                        fMostRecentData[fOutputOffset] = 0;
                    } else {
                        //
                        // Copy the input data to the end of the output buffer.
                        //
                        boolean alldone = copyNormalize(fOverflow, fOverflowOffset, fMostRecentData, fOutputOffset);
                        if (alldone) {
                            if (fOverflowEnd == CharDataChunk.CHUNK_SIZE) {
                                //
                                // Special case - everything fit into the overflow buffer,
                                // except that there is no room for the nul char we use to
                                // indicate EOF.  Set the overflow buffer length to zero.
                                // On the next call to this method, we will detect this
                                // case and which we will handle above .
                                //
                                fCheckOverflow = true;
                                fOverflowOffset = 0;
                                fOverflowEnd = 0;
                            } else {
                                //
                                // It all fit into the output buffer.
                                //
                                fOverflow = null;
                                fMostRecentData[fOutputOffset] = 0;
                            }
                        } else {
                            //
                            // There is still input data left over, save the remaining data as
                            // the overflow buffer for the next call.
                            //
                            fCheckOverflow = true;
                        }
                    }
                    break;
                }
                if (result > 0) {
                    fOverflowEnd += result;
                    capacity -= result;
                }
            } while (capacity > 0);
            //
            //
            //
            if (result == -1)
                break;
            if (fMostRecentData != null) {
                boolean alldone = copyNormalize(fOverflow, fOverflowOffset, fMostRecentData, fOutputOffset);
                if (fOutputOffset == CharDataChunk.CHUNK_SIZE) {
                    //
                    // We filled the output buffer.
                    //
                    if (!alldone) {
                        //
                        // The input buffer will become the next overflow buffer.
                        //
                        fCheckOverflow = true;
                    }
                    break;
                }
            } else {
                //
                // Now normalize the end-of-line characters and see if we need to read more
                // chars to fill up the buffer.
                //
                fMostRecentData = recycledData;
                if (fMostRecentData == null || fMostRecentData.length < CharDataChunk.CHUNK_SIZE)
                    fMostRecentData = new char[CharDataChunk.CHUNK_SIZE];
                else
                    recycledData = null;
                copyNormalize(fOverflow, fOverflowOffset, fMostRecentData, fOutputOffset);
                if (fOutputOffset == CharDataChunk.CHUNK_SIZE) {
                    //
                    // The output buffer is full.  We can return now.
                    //
                    break;
                }
            }
            //
            // We will need to get another intput buffer to be able to fill the
            // overflow buffer completely.
            //
        }
        //
        // Update our instance variables
        //
        fLength += fOutputOffset;
        fCurrentIndex = 0;
        fCurrentChunk.setCharArray(fMostRecentData);
        return (fMostRecentChar = fMostRecentData[0]);
    }
    //
    // Copy and normalize chars from the overflow buffer into chars in our data buffer.
    //
    private boolean copyNormalize(char[] in, int inOffset, char[] out, int outOffset) throws Exception {
        //
        // Handle all edge cases before dropping into the inner loop.
        //
        int inEnd = fOverflowEnd;
        int outEnd = out.length;
        if (inOffset == inEnd)
            return true;
        char b = in[inOffset];
        if (fSkipLinefeed) {
            fSkipLinefeed = false;
            if (b == 0x0A) {
                if (++inOffset == inEnd)
                    return exitNormalize(inOffset, outOffset, true);
                b = in[inOffset];
            }
        }
        while (outOffset < outEnd) {
            //
            // Find the longest run that we can guarantee will not exceed the
            // bounds of the outer loop.
            //
            int inCount = inEnd - inOffset;
            int outCount = outEnd - outOffset;
            if (inCount > outCount)
                inCount = outCount;
            inOffset++;
            while (true) {
                while (b == 0x0D) {
                    out[outOffset++] = 0x0A;
                    if (inOffset == inEnd) {
                        fSkipLinefeed = true;
                        return exitNormalize(inOffset, outOffset, true);
                    }
                    b = in[inOffset];
                    if (b == 0x0A) {
                        if (++inOffset == inEnd)
                            return exitNormalize(inOffset, outOffset, true);
                        b = in[inOffset];
                    }
                    if (outOffset == outEnd)
                        return exitNormalize(inOffset, outOffset, false);
                    inCount = inEnd - inOffset;
                    outCount = outEnd - outOffset;
                    if (inCount > outCount)
                        inCount = outCount;
                    inOffset++;
                }
                while (true) {
                    out[outOffset++] = b;
                    if (--inCount == 0)
                        break;
                    b = in[inOffset++];
                    if (b == 0x0D)
                        break;
                }
                if (inCount == 0)
                    break;
            }
            if (inOffset == inEnd)
                break;
        }
        return exitNormalize(inOffset, outOffset, inOffset == inEnd);
    }
    //
    //
    //
    private boolean exitNormalize(int inOffset, int outOffset, boolean result) {
        fOverflowOffset = inOffset;
        fOutputOffset = outOffset;
        return result;
    }
}