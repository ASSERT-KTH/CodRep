return StringPool.EMPTY_STRING;

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

package org.apache.xerces.utils;

/**
 * NamespacesScope provides a data structure for mapping namespace prefixes
 * to their URI's.  The mapping accurately reflects the scoping of namespaces
 * at a particular instant in time.
 */
public class NamespacesScope {
    /**
     * NamespacesHandler allows a client to be notified when namespace scopes change
     */
    public interface NamespacesHandler {
        /**
         * startNamespaceDeclScope is called when a new namespace scope is created
         *
         * @param prefix the StringPool handle of the namespace prefix being declared
         * @param uri the StringPool handle of the namespace's URI
         * @exception java.lang.Exception
         */
        public void startNamespaceDeclScope(int prefix, int uri) throws Exception;
        /**
         * endNamespaceDeclScope is called when a namespace scope ends
         * 
         * @param prefix the StringPool handle of the namespace prefix going out of scope
         * @exception java.lang.Exception
         */
        public void endNamespaceDeclScope(int prefix) throws Exception;
    }
    public NamespacesScope() {
        this(new NamespacesHandler() {
            public void startNamespaceDeclScope(int prefix, int uri) throws Exception {
            }
            public void endNamespaceDeclScope(int prefix) throws Exception {
            }
        });
    }
    public NamespacesScope(NamespacesHandler handler) {
        fHandler = handler;
        fNamespaceMappings[0] = new int[9];
        fNamespaceMappings[0][0] = 1;
    }
    /**
     * set the namespace URI for given prefix
     *
     * @param prefix the StringPool handler of the prefix
     * @param namespace the StringPool handle of the namespace URI
     */
    public void setNamespaceForPrefix(int prefix, int namespace) throws Exception {
        int offset = fNamespaceMappings[fElementDepth][0];
        if (offset == fNamespaceMappings[fElementDepth].length) {
            int[] newMappings = new int[offset + 8];
            System.arraycopy(fNamespaceMappings[fElementDepth], 0, newMappings, 0, offset);
            fNamespaceMappings[fElementDepth] = newMappings;
        }
        fNamespaceMappings[fElementDepth][offset++] = prefix;
        fNamespaceMappings[fElementDepth][offset++] = namespace;
        fNamespaceMappings[fElementDepth][0] = offset;
        if (fElementDepth > 0)
            fHandler.startNamespaceDeclScope(prefix, namespace);
    }
    /**
     * retreive the namespace URI for a prefix
     *
     * @param prefix the StringPool handle of the prefix
     */
    public int getNamespaceForPrefix(int prefix) {
        for (int depth = fElementDepth; depth >= 0; depth--) {
            int offset = fNamespaceMappings[depth][0];
            for (int i = 1; i < offset; i += 2) {
                if (prefix == fNamespaceMappings[depth][i]) {
                    return fNamespaceMappings[depth][i+1];
                }
            }
        }
        return -1;
    }
    /**
     *  Add a new namespace mapping
     */
    public void increaseDepth() throws Exception {
        fElementDepth++;
        if (fElementDepth == fNamespaceMappings.length) {
            int[][] newMappings = new int[fElementDepth + 8][];
            System.arraycopy(fNamespaceMappings, 0, newMappings, 0, fElementDepth);
            fNamespaceMappings = newMappings;
        }
        if (fNamespaceMappings[fElementDepth] == null)
            fNamespaceMappings[fElementDepth] = new int[9];
        fNamespaceMappings[fElementDepth][0] = 1;
    }
    /**
     *  Remove a namespace mappng
     */
    public void decreaseDepth() throws Exception {
        if (fElementDepth > 0) {
            int offset = fNamespaceMappings[fElementDepth][0];
            while (offset > 1) {
                offset -= 2;
                fHandler.endNamespaceDeclScope(fNamespaceMappings[fElementDepth][offset]);
            }
        }
        fElementDepth--;
    }
    private NamespacesHandler fHandler = null;
    private int fElementDepth = 0;
    private int[][] fNamespaceMappings = new int[8][];
}