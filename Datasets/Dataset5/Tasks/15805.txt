reportGenericSchemaError("an <annotation> can only contain <appinfo> and <documentation> elements");

/*
 * The Apache Software License, Version 1.1
 *
 *
 * Copyright (c) 2001 The Apache Software Foundation.  All rights
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
 * originally based on software copyright (c) 2001, International
 * Business Machines, Inc., http://www.apache.org.  For more
 * information on the Apache Software Foundation, please see
 * <http://www.apache.org/>.
 */

package org.apache.xerces.impl.v2;

import org.apache.xerces.impl.XMLErrorReporter;
import org.apache.xerces.util.SymbolTable;
import org.w3c.dom.Element;
import java.util.Hashtable;
import org.apache.xerces.util.DOMUtil;

/**
 * Class <code>XSDAbstractTraverser</code> serves as the base class for all
 * other <code>XSD???Traverser</code>s. It holds the common data and provide
 * a unified way to initialize these data.
 *
 * @version $Id$
 */
abstract class XSDAbstractTraverser {

    //Shared data
    protected XSDHandler            fSchemaHandler = null;
    protected SymbolTable           fSymbolTable = null;
    protected XSAttributeChecker    fAttrChecker = null;
    protected XMLErrorReporter      fErrorReporter = null;

    //REVISIT: should we add global fSchemaGrammar field

    XSDAbstractTraverser (XSDHandler handler,
                          XMLErrorReporter errorReporter,
                          XSAttributeChecker attrChecker) {        
        fSchemaHandler = handler;
        fErrorReporter = errorReporter;
        fAttrChecker = attrChecker;
    }

    //REVISIT: Implement
    void reset() {
    }

    // REVISIT: should symbol table passed as parameter to constractor or
    // be set using the following method?
    void setSymbolTable (SymbolTable table) {
        fSymbolTable = table;
    }

    // traver the annotation declaration
    // REVISIT: store annotation information for PSVI
    int traverseAnnotationDecl(Element annotationDecl, Hashtable parentAttrs) {
        // General Attribute Checking
        // There is no difference between global or local annotation,
        // so we assume it's always global.
        Hashtable attrValues = fAttrChecker.checkAttributes(annotationDecl, true);

        for(Element child = DOMUtil.getFirstChildElement(annotationDecl);
            child != null;
            child = DOMUtil.getNextSiblingElement(child)) {
            String name = child.getLocalName();

            // the only valid children of "annotation" are
            // "appinfo" and "documentation"
            if(!((name.equals(SchemaSymbols.ELT_APPINFO)) ||
                 (name.equals(SchemaSymbols.ELT_DOCUMENTATION)))) {
                reportSchemaError("an <annotation> can only contain <appinfo> and <documentation> elements", null);
            }

            // General Attribute Checking
            // There is no difference between global or local appinfo/documentation,
            // so we assume it's always global.
            attrValues = fAttrChecker.checkAttributes(child, true);
        }

        // REVISIT: an annotation index should be returned when we support PSVI
        return -1;
    }

    // REVISIT: is it how we want to handle error reporting?
    void reportGenericSchemaError (String error) {
    }

    //
    // Evaluates content of Annotation if present.
    //
    // @param: elm - parent element
    // @param: content - the first child of <code>elm</code> that needs to be checked
    // @param: isEmpty: -- true if the content allowed is (annotation?) only
    //                     false if must have some element (with possible preceding <annotation?>)
    //

    //REVISIT: Implement
    Element checkContent( Element elm, Element content, boolean isEmpty ) {
        return null;
    }
    //REVISIT: Implement
    int parseFinalSet (String finalString){
        return -1;
    }
}