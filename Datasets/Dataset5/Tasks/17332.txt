package org.apache.xerces.impl.v1.msg;

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

package org.apache.xerces.msg;

/**
 * <p>
 * This file contains error and warning messages used by the Apache
 * Xerces parser. The messages are arranged in key and value
 * tuples in a ListResourceBundle.
 *
 * @version
 */
public class ImplementationMessages
    extends java.util.ListResourceBundle
    {
    /** The list resource bundle contents. */
    public static final Object CONTENTS[][] = {
// Internal message formatter messages
        { "BadMajorCode", "The majorCode parameter to createMessage was out of bounds." },
        { "FormatFailed", "An internal error occurred while formatting the following message:\n  " },
// Xerces implementation defined errors
        { "ENC4", "Invalid UTF-8 code. (byte: 0x{0})" },
        { "ENC5", "Invalid UTF-8 code. (bytes: 0x{0} 0x{1})" },
        { "ENC6", "Invalid UTF-8 code. (bytes: 0x{0} 0x{1} 0x{2})" },
        { "ENC7", "Invalid UTF-8 code. (bytes: 0x{0} 0x{1} 0x{2} 0x{3})" },
        { "FileNotFound", "File \"{0}\" not found." },
        { "VAL_BST", "Invalid ContentSpecNode.NODE_XXX value for binary op CMNode" },
        { "VAL_CMSI", "Invalid CMStateSet bit index" },
        { "VAL_CST", "Unknown ContentSpecNode.NODE_XXX value" },
        { "VAL_LST", "Invalid ContentSpecNode.NODE_XXX value for leaf CMNode" },
        { "VAL_NIICM", "Only * unary ops should be in the internal content model tree"},
        { "VAL_NPCD", "PCData node found in non-mixed model content" },
        { "VAL_UST", "Invalid ContentSpecNode.NODE_XXX value for unary op CMNode" },
        { "VAL_WCGHI", "The input to whatCanGoHere() is inconsistent" },
        { "INT_DCN", "Internal Error: dataChunk == NULL" },
        { "INT_PCN", "Internal Error: fPreviousChunk == NULL" },
        { "FatalError", "Stopping after fatal error: {0}" },
    };

    /** Returns the list resource bundle contents. */
    public Object[][] getContents() {
        return CONTENTS;
    }

} // class Message