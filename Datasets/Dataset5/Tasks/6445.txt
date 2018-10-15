super(xpath, true);

/*
 * The Apache Software License, Version 1.1
 *
 *
 * Copyright (c) 2001 The Apache Software Foundation.  
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

package org.apache.xerces.validators.schema.identity;

import org.apache.xerces.utils.NamespacesScope;
import org.apache.xerces.utils.StringPool;
import org.apache.xerces.validators.datatype.DatatypeValidator;

import org.xml.sax.SAXException;

/**
 * Schema identity constraint field.
 *
 * @author Andy Clark, IBM
 * @version $Id$
 */
public class Field {

    //
    // Data
    //

    /** Field XPath. */
    protected Field.XPath fXPath;

    /** Datatype. */
    protected DatatypeValidator fDatatypeValidator;

    /** Identity constraint. */
    protected IdentityConstraint fIdentityConstraint;

    //
    // Constructors
    //

    /** Constructs a selector. */
    public Field(Field.XPath xpath, DatatypeValidator datatypeValidator,
                 IdentityConstraint identityConstraint) {
        fXPath = xpath;
        fDatatypeValidator = datatypeValidator;
        fIdentityConstraint = identityConstraint;
    } // <init>(Field.XPath,DatatypeValidator,IdentityConstraint)

    //
    // Public methods
    //

    /** Returns the field XPath. */
    public org.apache.xerces.validators.schema.identity.XPath getXPath() {
        return fXPath;
    } // getXPath():org.apache.xerces.validators.schema.identity.XPath

    /** Returns the datatype validator. */
    public DatatypeValidator getDatatypeValidator() {
        return fDatatypeValidator;
    } // getDatatypeValidator():DatatypeValidator

    /** Returns the identity constraint. */
    public IdentityConstraint getIdentityConstraint() {
        return fIdentityConstraint;
    } // getIdentityConstraint():IdentityConstraint

    // factory method

    /** Creates a field matcher. */
    public XPathMatcher createMatcher(ValueStore store) {
        return new Field.Matcher(fXPath, store);
    } // createMatcher(ValueStore):XPathMatcher

    //
    // Object methods
    //

    /** Returns a string representation of this object. */
    public String toString() {
        return fXPath.toString();
    } // toString():String

    //
    // Classes
    //

    /**
     * Field XPath.
     *
     * @author Andy Clark, IBM
     */
    public static class XPath
        extends org.apache.xerces.validators.schema.identity.XPath {

        //
        // Constructors
        //

        /** Constructs a field XPath expression. */
        public XPath(String xpath, StringPool stringPool,
                     NamespacesScope context, int targetNamespace) 
            throws XPathException {
            // NOTE: We have to prefix the field XPath with "./" in
            //       order to handle selectors such as "@attr" that 
            //       select the attribute because the fields could be
            //       relative to the selector element. -Ac
            super("./"+xpath, stringPool, context, targetNamespace);
        } // <init>(String,StringPool,NamespacesScope)

    } // class XPath

    /**
     * Field matcher.
     *
     * @author Andy Clark, IBM
     */
    protected class Matcher
        extends XPathMatcher {

        //
        // Data
        //

        /** Value store for data values. */
        protected ValueStore fStore;

        //
        // Constructors
        //

        /** Constructs a field matcher. */
        public Matcher(Field.XPath xpath, ValueStore store) {
            super(xpath);
            fStore = store;
        } // <init>(Field.XPath,ValueStore)

        //
        // XPathHandler methods
        //

        /**
         * This method is called when the XPath handler matches the
         * XPath expression.
         */
        protected void matched(String content) throws Exception {
            super.matched(content);
            fStore.addValue(Field.this, content);
        } // matched(String)

    } // class Matcher

} // class Field