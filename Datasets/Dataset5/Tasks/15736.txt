if (axis.type == XPath.Axis.ATTRIBUTE &&

/*
 * The Apache Software License, Version 1.1
 *
 *
 * Copyright (c) 2001-2003 The Apache Software Foundation.  
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

package org.apache.xerces.impl.xs.identity;

import org.apache.xerces.impl.dv.XSSimpleType;
import org.apache.xerces.impl.xpath.XPathException;
import org.apache.xerces.impl.xs.XSComplexTypeDecl;
import org.apache.xerces.impl.xs.XSElementDecl;
import org.apache.xerces.impl.xs.psvi.XSTypeDefinition;
import org.apache.xerces.util.SymbolTable;
import org.apache.xerces.xni.NamespaceContext;

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
    // Unfortunately, a Field may conceivably match values of varying
    // datatypes.  Hence, this member no longer makes sense; see the IDValue class.
    // protected XSSimpleType fXSSimpleType;

    /** Identity constraint. */
    protected IdentityConstraint fIdentityConstraint;

    // whether this field can be matched; used to catch instance documents
    // that try and match a field several times in the same scope.
    protected boolean mayMatch = true;

    //
    // Constructors
    //

    /** Constructs a field. */
    public Field(Field.XPath xpath, 
                 IdentityConstraint identityConstraint) {
        fXPath = xpath;
        fIdentityConstraint = identityConstraint;
    } // <init>(Field.XPath,IdentityConstraint)

    //
    // Public methods
    //

    // sets mayMatch
    public void setMayMatch(boolean b) {
        mayMatch = b;
    } // setMayMatch(boolean);
    
    // returns mayMatch
    public boolean mayMatch() {
        return mayMatch;
    } // mayMatch():boolean
    
    /** Returns the field XPath. */
    public org.apache.xerces.impl.xpath.XPath getXPath() {
        return fXPath;
    } // getXPath():org.apache.xerces.impl.v1.schema.identity.XPath

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
        extends org.apache.xerces.impl.xpath.XPath {

        //
        // Constructors
        //

        /** Constructs a field XPath expression. */
        public XPath(String xpath, 
                     SymbolTable symbolTable,
                     NamespaceContext context) throws XPathException {
            // NOTE: We have to prefix the field XPath with "./" in
            //       order to handle selectors such as "@attr" that 
            //       select the attribute because the fields could be
            //       relative to the selector element. -Ac
            //       Unless xpath starts with a descendant node -Achille Fokoue
            //      ... or a / or a . - NG
            super(((xpath.trim().startsWith("/") ||xpath.trim().startsWith("."))?
                    xpath:"./"+xpath), 
                  symbolTable, context);
            
            // verify that only one attribute is selected per branch
            for (int i=0;i<fLocationPaths.length;i++) {
                for(int j=0; j<fLocationPaths[i].steps.length; j++) {
                    org.apache.xerces.impl.xpath.XPath.Axis axis =
                        fLocationPaths[i].steps[j].axis;
                    if (axis.type == axis.ATTRIBUTE &&
                            (j < fLocationPaths[i].steps.length-1)) {
                        throw new XPathException("c-fields-xpaths");
                    }
                }
            }
        } // <init>(String,SymbolTable,NamespacesContext)

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
        protected void matched(String content, XSSimpleType val, boolean isNil) {
            super.matched(content, val, isNil);
            if(isNil && (fIdentityConstraint.getCategory() == IdentityConstraint.IC_KEY)) {
                String code = "KeyMatchesNillable";
                fStore.reportError(code, new Object[]{fIdentityConstraint.getElementName()});
            }
            fStore.addValue(Field.this, new IDValue(content, val));
            // once we've stored the value for this field, we set the mayMatch
            // member to false so that, in the same scope, we don't match any more
            // values (and throw an error instead).
            mayMatch = false;
        } // matched(String)

        protected void handleContent(XSElementDecl eDecl, String value) { 
            // REVISIT:  make sure type is simple!
            XSSimpleType val=null;

            if (eDecl!=null) {
                XSTypeDefinition type = eDecl.fType;
                if (type != null) {
                    if (type.getTypeCategory() == XSTypeDefinition.COMPLEX_TYPE) {
                        XSComplexTypeDecl ctype = (XSComplexTypeDecl)type;
                        val = (XSSimpleType)ctype.getSimpleType();
                    }
                    else {
                        val = (XSSimpleType)(type);
                    }
                }
            }

            if(val == null ) {
                // must be a complexType with no simpleContent!
                String code = "cvc-id.3";
                String name = (eDecl == null?"null":eDecl.getName());
                fStore.reportError(code, new Object[]{fIdentityConstraint.getName(), name});
                return;
            }
            fMatchedString = value;
            if(eDecl != null) {
                matched(fMatchedString, val, (eDecl.getNillable()));
            } else {
                matched(fMatchedString, val, false); 
            }
        } // handleContent(XSElementDecl, String)

    } // class Matcher

} // class Field