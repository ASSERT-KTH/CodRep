public void reset() {

/*
 * The Apache Software License, Version 1.1
 *
 *
 * Copyright (c) 2000-2002 The Apache Software Foundation.  
 * All rights reserved.
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

package org.apache.xerces.util;

import org.apache.xerces.xni.NamespaceContext;
import org.apache.xerces.util.XMLSymbols;

/**
 * Namespace support for XML document handlers. This class doesn't 
 * perform any error checking and assumes that all strings passed
 * as arguments to methods are unique symbols. The SymbolTable class
 * can be used for this purpose.
 *
 * @author Andy Clark, IBM
 *
 * @version $Id$
 */
public class NamespaceSupport 
    implements NamespaceContext {

    //
    // Data
    //

    /** 
     * Namespace binding information. This array is composed of a
     * series of tuples containing the namespace binding information:
     * &lt;prefix, uri&gt;. The default size can be set to anything
     * as long as it is a power of 2 greater than 1.
     *
     * @see #fNamespaceSize
     * @see #fContext
     */
    protected String[] fNamespace = new String[16 * 2];

    /** The top of the namespace information array. */
    protected int fNamespaceSize;

    // NOTE: The constructor depends on the initial context size 
    //       being at least 1. -Ac

    /** 
     * Context indexes. This array contains indexes into the namespace
     * information array. The index at the current context is the start
     * index of declared namespace bindings and runs to the size of the
     * namespace information array.
     *
     * @see #fNamespaceSize
     */
    protected int[] fContext = new int[8];

    /** The current context. */
    protected int fCurrentContext;

    //
    // Constructors
    //

    /** Default constructor. */
    public NamespaceSupport() {
    } // <init>()

    /** 
     * Constructs a namespace context object and initializes it with
     * the prefixes declared in the specified context.
     */
    public NamespaceSupport(NamespaceContext context) {
        pushContext();
        while (context != null) {
            int count = context.getDeclaredPrefixCount();
            for (int i = 0; i < count; i++) {
                String prefix = context.getDeclaredPrefixAt(i);
                String uri = getURI(prefix);
                if (uri == null) {
                    uri = context.getURI(prefix);
                    declarePrefix(prefix, uri);
                }
            }
            context = context.getParentContext();
        }
    } // <init>(NamespaceContext)

    //
    // Public methods
    //

    // context management
    
    /**
     * Reset this Namespace support object for reuse.
     *
     * <p>It is necessary to invoke this method before reusing the
     * Namespace support object for a new session.</p>
     */
    public void reset(SymbolTable symbolTable) {

        // reset namespace and context info
        fNamespaceSize = 0;
        fCurrentContext = 0;
        fContext[fCurrentContext] = fNamespaceSize;

        // bind "xml" prefix to the XML uri
        fNamespace[fNamespaceSize++] = XMLSymbols.PREFIX_XML;
        fNamespace[fNamespaceSize++] = XML_URI;
        // bind "xmlns" prefix to the XMLNS uri
        fNamespace[fNamespaceSize++] = XMLSymbols.PREFIX_XMLNS;
        fNamespace[fNamespaceSize++] = XMLNS_URI;
        ++fCurrentContext;

    } // reset(SymbolTable)

    /**
     * Start a new Namespace context.
     * <p>
     * Normally, you should push a new context at the beginning
     * of each XML element: the new context will automatically inherit
     * the declarations of its parent context, but it will also keep
     * track of which declarations were made within this context.
     * <p>
     * The Namespace support object always starts with a base context
     * already in force: in this context, only the "xml" prefix is
     * declared.
     *
     * @see #popContext
     */
    public void pushContext() {

        // extend the array, if necessary
        if (fCurrentContext + 1 == fContext.length) {
            int[] contextarray = new int[fContext.length * 2];
            System.arraycopy(fContext, 0, contextarray, 0, fContext.length);
            fContext = contextarray;
        }

        // push context
        fContext[++fCurrentContext] = fNamespaceSize;

    } // pushContext()


    /**
     * Revert to the previous Namespace context.
     * <p>
     * Normally, you should pop the context at the end of each
     * XML element.  After popping the context, all Namespace prefix
     * mappings that were previously in force are restored.
     * <p>
     * You must not attempt to declare additional Namespace
     * prefixes after popping a context, unless you push another
     * context first.
     *
     * @see #pushContext
     */
    public void popContext() {
        fNamespaceSize = fContext[fCurrentContext--];
    } // popContext()

    // operations within a context.

    /**
     * Declare a Namespace prefix.
     * <p>
     * This method declares a prefix in the current Namespace
     * context; the prefix will remain in force until this context
     * is popped, unless it is shadowed in a descendant context.
     * <p>
     * To declare a default Namespace, use the empty string.  The
     * prefix must not be "xml" or "xmlns".
     * <p>
     * Note that you must <em>not</em> declare a prefix after
     * you've pushed and popped another Namespace.
     *
     * @param prefix The prefix to declare, or null for the empty
     *        string.
     * @param uri The Namespace URI to associate with the prefix.
     *
     * @return true if the prefix was legal, false otherwise
     *
     * @see #getURI
     * @see #getDeclaredPrefixAt
     */
    public boolean declarePrefix(String prefix, String uri) {

        // ignore "xml" and "xmlns" prefixes
        if (prefix == XMLSymbols.PREFIX_XML || prefix == XMLSymbols.PREFIX_XMLNS) {
            return false;
        }

        // see if prefix already exists in current context
        for (int i = fNamespaceSize; i > fContext[fCurrentContext]; i -= 2) {
            if (fNamespace[i - 2] == prefix) {
                // REVISIT: [Q] Should the new binding override the
                //          previously declared binding or should it
                //          it be ignored? -Ac
                // NOTE:    The SAX2 "NamespaceSupport" helper allows
                //          re-bindings with the new binding overwriting
                //          the previous binding. -Ac
                fNamespace[i - 1] = uri;
                return true;
            }
        }

        // resize array, if needed
        if (fNamespaceSize == fNamespace.length) {
            String[] namespacearray = new String[fNamespaceSize * 2];
            System.arraycopy(fNamespace, 0, namespacearray, 0, fNamespaceSize);
            fNamespace = namespacearray;
        }

        // bind prefix to uri in current context
        fNamespace[fNamespaceSize++] = prefix;
        fNamespace[fNamespaceSize++] = uri;

        return true;

    } // declarePrefix(String,String):boolean

    /**
     * Look up a prefix and get the currently-mapped Namespace URI.
     * <p>
     * This method looks up the prefix in the current context.
     * Use the empty string ("") for the default Namespace.
     *
     * @param prefix The prefix to look up.
     *
     * @return The associated Namespace URI, or null if the prefix
     *         is undeclared in this context.
     *
     * @see #getDeclaredPrefixAt
     */
    public String getURI(String prefix) {

        // find prefix in current context
        for (int i = fNamespaceSize; i > 0; i -= 2) {
            if (fNamespace[i - 2] == prefix) {
                return fNamespace[i - 1];
            }
        }

        // prefix not found
        return null;

    } // getURI(String):String



    /**
     * Look up a namespace URI and get one of the mapped prefix.
     * <p>
     * This method looks up the namespace URI in the current context.
     *
     * @param uri The namespace URI to look up.
     *
     * @return one of the associated prefixes, or null if the uri
     *         does not map to any prefix.
     *
     * @see #getPrefix
     */
    public String getPrefix(String uri) {

        // find uri in current context
        for (int i = fNamespaceSize; i > 0; i -= 2) {
            if (fNamespace[i - 1] == uri) {
                return fNamespace[i - 2];
            }
        }

        // uri not found
        return null;

    } // getURI(String):String


    /**
     * Return a count of all prefixes currently declared, including
     * the default prefix if bound.
     */
    public int getDeclaredPrefixCount() {
        return (fNamespaceSize - fContext[fCurrentContext]) / 2;
    } // getDeclaredPrefixCount():int

    /** 
     * Returns the prefix at the specified index in the current context.
     */
    public String getDeclaredPrefixAt(int index) {
        return fNamespace[fContext[fCurrentContext] + index * 2];
    } // getDeclaredPrefixAt(int):String

    /**
     * Returns the parent namespace context or null if there is no
     * parent context. The total depth of the namespace contexts 
     * matches the element depth in the document.
     * <p>
     * <strong>Note:</strong> This method <em>may</em> return the same 
     * NamespaceContext object reference. The caller is responsible for
     * saving the declared prefix mappings before calling this method.
     */
    public NamespaceContext getParentContext() {
        if (fCurrentContext == 1) {
            return null;
        }
        return new Context(fCurrentContext - 1);
    } // getParentContext():NamespaceContext

    //
    // Classes
    //

    /**
     * Namespace context information. The current context is always
     * handled directly by the NamespaceSupport class. This class is
     * used when a user queries the parent context.
     *
     * @author Andy Clark, IBM
     */
    final class Context 
        implements NamespaceContext {
    
        //
        // Data
        //

        /** The current context. */
        private int fCurrentContext;

        //
        // Constructors
        //

        /** 
         * Constructs a new context. Once constructed, this object will
         * be re-used when the application calls <code>getParentContext</code.
         */
        public Context(int currentContext) {
            setCurrentContext(currentContext);
        } // <init>(int)

        //
        // Public methods
        //

        /** Sets the current context. */
        public void setCurrentContext(int currentContext) {
            fCurrentContext = currentContext;
        } // setCurrentContext(int)

        //
        // NamespaceContext methods
        //

        /**
         * Look up a prefix and get the currently-mapped Namespace URI.
         * <p>
         * This method looks up the prefix in the current context.
         * Use the empty string ("") for the default Namespace.
         *
         * @param prefix The prefix to look up.
         *
         * @return The associated Namespace URI, or null if the prefix
         *         is undeclared in this context.
         *
         * @see #getPrefix
         */
        public String getURI(String prefix) {

            // find prefix in current context
            for (int i = fNamespaceSize; i > 0; i -= 2) {
                if (fNamespace[i - 2] == prefix) {
                    return fNamespace[i - 1];
                }
            }

            // prefix not found
            return null;

        } // getURI(String):String

        /**
         * Return a count of all prefixes currently declared, including
         * the default prefix if bound.
         */
        public int getDeclaredPrefixCount() {
            return (fNamespaceSize - fContext[fCurrentContext]) / 2;
        } // getDeclaredPrefixCount():int

        /** 
         * Returns the prefix at the specified index in the current context.
         */
        public String getDeclaredPrefixAt(int index) {
            return fNamespace[fContext[fCurrentContext] + index * 2];
        } // getDeclaredPrefixAt(int):String

        /**
         * Returns the parent namespace context or null if there is no
         * parent context. The total depth of the namespace contexts 
         * matches the element depth in the document.
         * <p>
         * <strong>Note:</strong> This method <em>may</em> return the same 
         * NamespaceContext object reference. The caller is responsible for
         * saving the declared prefix mappings before calling this method.
         */
        public NamespaceContext getParentContext() {
            if (fCurrentContext == 1) {
                return null;
            }
            setCurrentContext(fCurrentContext - 1);
            return this;
        } // getParentContext():NamespaceContext

    } // class Context


} // class NamespaceSupport