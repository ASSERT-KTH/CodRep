super.out.write(fBuffer, 0, fBuffer.length);

/*
 * The Apache Software License, Version 1.1
 *
 *
 * Copyright (c) 2000 The Apache Software Foundation.  All rights 
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

package socket.io;

import java.io.DataOutputStream;
import java.io.FilterOutputStream;
import java.io.IOException;
import java.io.OutputStream;

/**
 * This output stream works in conjunction with the WrappedInputStream
 * to introduce a protocol for sending arbitrary length data in a
 * uniform way. This output stream allows variable length data to be
 * inserted into an existing output stream so that it can be read by
 * an input stream without reading too many bytes (in case of buffering
 * by the input stream).
 * <p>
 * This output stream is used like any normal output stream. The protocol
 * is introduced by the WrappedOutputStream and does not need to be known
 * by the user of this class. However, for those that are interested, the
 * method is described below.
 * <p>
 * The output stream writes the requested bytes as packets of binary
 * information. The packet consists of a header and payload. The header
 * is two bytes of a single unsigned short (written in network order) 
 * that specifies the length of bytes in the payload. A header value of
 * 0 indicates that the stream is "closed".
 * <p>
 * <strong>Note:</strong> For this wrapped output stream to be used,
 * the application <strong>must</strong> call <code>close()</code>
 * to end the output.
 *
 * @see WrappedInputStream
 *
 * @author Andy Clark, IBM
 *
 * @version $Id$
 */
public class WrappedOutputStream
    extends FilterOutputStream {

    //
    // Constants
    //

    /** Default buffer size (1024). */
    public static final int DEFAULT_BUFFER_SIZE = 1024;

    //
    // Data
    //

    /** Buffer. */
    protected byte[] fBuffer;

    /** Buffer position. */
    protected int fPosition;

    /** 
     * Data output stream. This stream is used to output the block sizes
     * into the data stream that are read by the WrappedInputStream.
     * <p>
     * <strong>Note:</strong> The data output stream is only used for
     * writing the byte count for performance reasons. We avoid the
     * method indirection for writing the byte data.
     */
    protected DataOutputStream fDataOutputStream;

    //
    // Constructors
    //

    /** Constructs a wrapper for the given output stream. */
    public WrappedOutputStream(OutputStream stream) {
        this(stream, DEFAULT_BUFFER_SIZE);
    } // <init>(OutputStream)

    /** 
     * Constructs a wrapper for the given output stream with the
     * given buffer size.
     */
    public WrappedOutputStream(OutputStream stream, int bufferSize) {
        super(stream);
        fBuffer = new byte[bufferSize];
        fDataOutputStream = new DataOutputStream(stream);
    } // <init>(OutputStream)

    //
    // OutputStream methods
    //

    /** 
     * Writes a single byte to the output. 
     * <p>
     * <strong>Note:</strong> Single bytes written to the output stream
     * will be buffered
     */
    public void write(int b) throws IOException {
        fBuffer[fPosition++] = (byte)b;
        if (fPosition == fBuffer.length) {
            fPosition = 0;
            fDataOutputStream.writeInt(fBuffer.length);
            write(fBuffer, 0, fBuffer.length);
        }
    } // write(int)

    /** Writes an array of bytes to the output. */
    public void write(byte[] b, int offset, int length) 
        throws IOException {

        // flush existing buffer
        if (fPosition > 0) {
            flush0();
        }

        // write header followed by actual bytes
        fDataOutputStream.writeInt(length);
        super.out.write(b, offset, length);

    } // write(byte[])

    /** 
     * Flushes the output buffer, writing all bytes currently in
     * the buffer to the output.
     */
    public void flush() throws IOException {
        flush0();
        super.out.flush();
    } // flush()

    /** 
     * Closes the output stream. This method <strong>must</strong> be
     * called when done writing all data to the output stream.
     * <p>
     * <strong>Note:</strong> This method does <em>not</em> close the
     * actual output stream, only makes the input stream see the stream
     * closed. Do not write bytes after closing the output stream.
     */
    public void close() throws IOException {
        flush0();
        fDataOutputStream.writeInt(0);
        super.out.flush();
    } // close()

    //
    // Protected methods
    //

    /** 
     * Flushes the output buffer, writing all bytes currently in
     * the buffer to the output. This method does not call the
     * flush() method of the output stream; it merely writes the
     * remaining bytes in the buffer.
     */
    public void flush0() throws IOException {
        int length = fPosition;
        fPosition = 0;
        if (length > 0) {
            fDataOutputStream.writeInt(length);
            super.out.write(fBuffer, 0, length);
        }
    } // flush0()

} // class WrappedOutputStream