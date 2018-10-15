fNamespaceBinder.reset();

/*
 * The Apache Software License, Version 1.1
 *
 *
 * Copyright (c) 1999-2002 The Apache Software Foundation.  All rights 
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
 * originally based on software copyright (c) 2002, International
 * Business Machines, Inc., http://www.apache.org.  For more
 * information on the Apache Software Foundation, please see
 * <http://www.apache.org/>.
 */

package org.apache.xerces.dom;


import org.w3c.dom.DOMErrorHandler;

import org.apache.xerces.impl.Constants;
import org.apache.xerces.impl.RevalidationHandler;
import org.apache.xerces.util.AugmentationsImpl;
import org.apache.xerces.util.NamespaceSupport;
import org.apache.xerces.util.SymbolTable;
import org.apache.xerces.util.XMLSymbols;
import org.apache.xerces.parsers.AbstractXMLDocumentParser;


import org.apache.xerces.xni.Augmentations;
import org.apache.xerces.xni.QName;
import org.apache.xerces.xni.XMLDocumentHandler;
import org.apache.xerces.xni.XMLAttributes;
import org.apache.xerces.xni.XMLString;
import org.apache.xerces.xni.XNIException;
import org.apache.xerces.xni.parser.XMLComponent;
import org.apache.xerces.xni.parser.XMLComponentManager;
import org.apache.xerces.xni.parser.XMLErrorHandler;

import org.apache.xerces.xni.grammars.XMLGrammarDescription;
import org.apache.xerces.xni.grammars.XMLGrammarPool;
import org.apache.xerces.xni.grammars.Grammar;

import java.util.Vector;
import org.w3c.dom.*;

/**
 * This class adds implementation for normalizeDocument method.
 * It acts as if the document was going through a save and load cycle, putting
 * the document in a "normal" form. The actual result depends on the features being set
 * and governing what operations actually take place. See setNormalizationFeature for details.
 * Noticeably this method normalizes Text nodes, makes the document "namespace wellformed",
 * according to the algorithm described below in pseudo code, by adding missing namespace
 * declaration attributes and adding or changing namespace prefixes, updates the replacement
 * tree of EntityReference nodes, normalizes attribute values, etc.
 * Mutation events, when supported, are generated to reflect the changes occuring on the
 * document.
 * See Namespace normalization for details on how namespace declaration attributes and prefixes
 * are normalized.
 * 
 * NOTE: There is an initial support for DOM revalidation with XML Schema as a grammar.
 * The tree might not be validated correctly if entityReferences, CDATA sections are
 * present in the tree. The PSVI information is not exposed, normalized data (including element
 * default content is not available).
 * 
 * @author Elena Litani, IBM
 * @version $Id$
 */
public class DOMNormalizer implements XMLGrammarPool {


    //
    // REVISIT:  
    // 1. Send all appropriate calls for entity reference content.
    // 2. If datatype-normalization feature is on:
    //   a) replace values of text nodes with normalized value:
    //     need to pass to documentHandler augmentations that will be filled in 
    //     during validation process.
    //   b) add element default content: retrieve from augementations (PSVI Element schemaDefault)
    //   c) replace values of attributes: the augmentations for attributes have the values.
    //

    //
    // constants
    //
    /** Debug normalize document*/
    protected final static boolean DEBUG_ND = false;
    /** Debug namespace fix up algorithm*/
    protected final static boolean DEBUG = false;

    /** prefix added by namespace fixup algorithm should follow a pattern "NS" + index*/
    protected final static String PREFIX = "NS";


    /** Property identifier: error handler. */
    protected static final String ERROR_HANDLER = 
    Constants.XERCES_PROPERTY_PREFIX + Constants.ERROR_HANDLER_PROPERTY;

    /** Property identifier: symbol table. */
    protected static final String SYMBOL_TABLE = 
    Constants.XERCES_PROPERTY_PREFIX + Constants.SYMBOL_TABLE_PROPERTY;

    //
    // Data
    //
    protected CoreDocumentImpl fDocument = null;
    protected final XMLAttributesProxy fAttrProxy = new XMLAttributesProxy();
    protected final QName fQName = new QName();

    /** Validation handler represents validator instance. */
    protected RevalidationHandler fValidationHandler;

    /** symbol table */
    protected SymbolTable fSymbolTable;
    /** error handler */
    protected DOMErrorHandler fErrorHandler;

    // counter for new prefix names
    protected int fNamespaceCounter = 1;

    // Validation against namespace aware grammar
    protected boolean fNamespaceValidation = false;

    /** stores namespaces in scope */
    protected final NamespaceSupport fNamespaceBinder = new NamespaceSupport();

    /** stores all namespace bindings on the current element */
    protected final NamespaceSupport fLocalNSBinder = new NamespaceSupport();

    /** list of attributes */
    protected final Vector fAttributeList = new Vector(5,10);

    /** DOM Error object */
    protected final DOMErrorImpl fDOMError = new DOMErrorImpl();

    /** DOM Locator -  for namespace fixup algorithm */
    protected final DOMLocatorImpl fLocator = new DOMLocatorImpl();



    // 
    // Constructor
    // 

    public DOMNormalizer(){}


    protected void reset(XMLComponentManager componentManager){
        if (componentManager == null) {
            fSymbolTable = null;
            fValidationHandler = null;
            return;
        }
        fSymbolTable = (SymbolTable)componentManager.getProperty(SYMBOL_TABLE);
        if (fSymbolTable == null) {
            fSymbolTable = new SymbolTable();
        }

        fNamespaceValidation = componentManager.getFeature(DOMValidationConfiguration.SCHEMA);
        fNamespaceBinder.reset(fSymbolTable);
        fNamespaceBinder.declarePrefix(XMLSymbols.EMPTY_STRING, XMLSymbols.EMPTY_STRING);
        fNamespaceCounter = 1;

        if (fValidationHandler != null) {
            ((XMLComponent)fValidationHandler).reset(componentManager);
            // REVISIT: how to pass and reuse namespace binder in the XML Schema validator?
        }
    }

    protected final void setValidationHandler (RevalidationHandler validator){
        this.fValidationHandler = validator;

    }

    /**
     * Normalizes document.
     * Note: reset() must be called before this method.
     */
    protected final void normalizeDocument(CoreDocumentImpl document){
        if (fSymbolTable == null) {
            // reset was not called
            return;
        }

        fDocument = document;
        fErrorHandler = fDocument.getErrorHandler();

        if (fValidationHandler != null) {
            fValidationHandler.setBaseURI(fDocument.fDocumentURI);
            fValidationHandler.startDocument(null, fDocument.encoding, null);
        }

        Node kid, next;
        for (kid = fDocument.getFirstChild(); kid != null; kid = next) {
            next = kid.getNextSibling();
            kid = normalizeNode(kid);
            if (kid != null) {  // don't advance
                next = kid;
            }
        }

        if (fValidationHandler != null) {
            fValidationHandler.endDocument(null);
        }
        // reset symbol table
        fSymbolTable = null;
    }


    /**
     * 
     * This method acts as if the document was going through a save
     * and load cycle, putting the document in a "normal" form. The actual result
     * depends on the features being set and governing what operations actually
     * take place. See setNormalizationFeature for details. Noticeably this method
     * normalizes Text nodes, makes the document "namespace wellformed",
     * according to the algorithm described below in pseudo code, by adding missing
     * namespace declaration attributes and adding or changing namespace prefixes, updates
     * the replacement tree of EntityReference nodes,normalizes attribute values, etc.
     * 
     * @param node   Modified node or null. If node is returned, we need
     *               to normalize again starting on the node returned.
     * @return 
     */
    protected final Node normalizeNode (Node node){

        // REVISIT: should we support other DOM implementations?
        //          if so we should not depend on Xerces specific classes

        int type = node.getNodeType();
        switch (type) {
        case Node.DOCUMENT_TYPE_NODE: {
                if (DEBUG_ND) {
                    System.out.println("==>normalizeNode:{doctype}");
                }
                if ((fDocument.features & CoreDocumentImpl.ENTITIES) == 0) {
                    // remove all entity nodes
                    ((DocumentTypeImpl)node).entities.removeAll();
                }
                break;
            }

        case Node.ELEMENT_NODE: {  
                if (DEBUG_ND) {
                    System.out.println("==>normalizeNode:{element} "+node.getNodeName());
                }
                // push namespace context
                fNamespaceBinder.pushContext();

                ElementImpl elem = (ElementImpl)node;
                if (elem.needsSyncChildren()) {
                    elem.synchronizeChildren();
                }
                // REVISIT: need to optimize for the cases there normalization is not 
                //          needed and an element could be skipped.

                // Normalize all of the attributes & remove defaults
                AttributeMap attributes = (elem.hasAttributes()) ? (AttributeMap) elem.getAttributes() : null; 

                // fix namespaces and remove default attributes
                if ((fDocument.features & CoreDocumentImpl.NAMESPACES) !=0) {
                    // fix namespaces
                    // normalize attribute values
                    // remove default attributes
                    namespaceFixUp(elem, attributes);
                } else {
                    if ( attributes!=null ) {
                        for ( int i=0; i<attributes.getLength(); ++i ) {
                            Attr attr = (Attr)attributes.item(i);
                            removeDefault(attr, attributes);
                            attr.normalize();
                        }
                    }
                }
                if (fValidationHandler != null) {
                    // REVISIT: possible solutions to discard default content are:
                    //         either we pass some flag to XML Schema validator
                    //         or rely on the PSVI information.
                    fAttrProxy.setAttributes(attributes, fDocument, elem);
                    updateQName(elem, fQName); // updates global qname
                    //
                    // set error node in the dom error wrapper
                    // so if error occurs we can report an error node
                    fDocument.fErrorHandlerWrapper.fCurrentNode = node;
                    // call re-validation handler
                    fValidationHandler.startElement(fQName, fAttrProxy, null);
                }

                // normalize children
                Node kid, next;
                for (kid = elem.getFirstChild(); kid != null; kid = next) {
                    next = kid.getNextSibling();
                    kid = normalizeNode(kid);
                    if (kid !=null) {
                        next = kid;  // don't advance
                    }
                } 
                if (DEBUG_ND) {
                    // normalized subtree
                    System.out.println("   normalized children for{"+node.getNodeName()+"}");
                    for (kid = elem.getFirstChild(); kid != null; kid = next) {
                        next = kid.getNextSibling();
                        System.out.println(kid.getNodeName() +": "+kid.getNodeValue());
                    }

                }


                if (fValidationHandler != null) {
                    updateQName(elem, fQName); // updates global qname
                    //
                    // set error node in the dom error wrapper
                    // so if error occurs we can report an error node
                    fDocument.fErrorHandlerWrapper.fCurrentNode = node;

                    fValidationHandler.endElement(fQName, null);
                    int count = fNamespaceBinder.getDeclaredPrefixCount();
                    for (int i = count - 1; i >= 0; i--) {
                        String prefix = fNamespaceBinder.getDeclaredPrefixAt(i);
                        fValidationHandler.endPrefixMapping(prefix, null);
                    }
                }

                // pop namespace context
                fNamespaceBinder.popContext();

                break;
            }

        case Node.COMMENT_NODE: {  
                if (DEBUG_ND) {
                    System.out.println("==>normalizeNode:{comments}");
                }

                if ((fDocument.features & CoreDocumentImpl.COMMENTS) == 0) {
                    Node prevSibling = node.getPreviousSibling();
                    Node parent = node.getParentNode();
                    // remove the comment node
                    parent.removeChild(node);
                    if (prevSibling != null && prevSibling.getNodeType() == Node.TEXT_NODE) {
                        Node nextSibling = prevSibling.getNextSibling();
                        if (nextSibling != null && nextSibling.getNodeType() == Node.TEXT_NODE) {
                            ((TextImpl)nextSibling).insertData(0, prevSibling.getNodeValue());
                            parent.removeChild(prevSibling);
                            return nextSibling;
                        }
                    }
                }
                break;
            }
        case Node.ENTITY_REFERENCE_NODE: { 
                if (DEBUG_ND) {
                    System.out.println("==>normalizeNode:{entityRef} "+node.getNodeName());
                }

                if ((fDocument.features & CoreDocumentImpl.ENTITIES) == 0) {
                    Node prevSibling = node.getPreviousSibling();
                    Node parent = node.getParentNode();
                    ((EntityReferenceImpl)node).setReadOnly(false, true);
                    expandEntityRef (node, parent, node);
                    parent.removeChild(node);
                    Node next = (prevSibling != null)?prevSibling.getNextSibling():parent.getFirstChild();
                    // The list of children #text -> &ent;
                    // and entity has a first child as a text
                    // we should not advance
                    if (prevSibling !=null && prevSibling.getNodeType() == Node.TEXT_NODE && 
                        next.getNodeType() == Node.TEXT_NODE) {
                        return prevSibling;  // Don't advance                          
                    }
                    return next;
                } else {
                    // REVISIT: traverse entity reference and send appropriate calls to the validator
                    // (no normalization should be performed for the children).
                }
                break;
            }

        case Node.CDATA_SECTION_NODE: {
                if (DEBUG_ND) {
                    System.out.println("==>normalizeNode:{cdata}");
                }
                if ((fDocument.features & CoreDocumentImpl.CDATA) == 0) {
                    // convert CDATA to TEXT nodes
                    Text text = fDocument.createTextNode(node.getNodeValue());
                    Node parent = node.getParentNode();
                    Node prevSibling = node.getPreviousSibling();
                    node = parent.replaceChild(text, node);
                    if (prevSibling != null && prevSibling.getNodeType() == Node.TEXT_NODE) {

                        text.insertData(0, prevSibling.getNodeValue());
                        parent.removeChild(prevSibling);
                    }
                    return text; // Don't advance; 
                }
                // send characters call for CDATA
                if (fValidationHandler != null) {

                    //
                    // set error node in the dom error wrapper
                    // so if error occurs we can report an error node
                    fDocument.fErrorHandlerWrapper.fCurrentNode = node;
                    
                    fValidationHandler.startCDATA(null);
                    fValidationHandler.characterData(node.getNodeValue(), null);
                    fValidationHandler.endCDATA(null);
                }

                if ((fDocument.features & CoreDocumentImpl.SPLITCDATA) != 0) {
                    String value = node.getNodeValue();
                    int index = value.indexOf("]]>");
                    if (index >= 0) {
                        // REVISIT: issue warning
                    }
                    Node parent = node.getParentNode();
                    while ( index >= 0 ) {
                        node.setNodeValue(value.substring(0, index+2));
                        value = value.substring(index +2);
                        node = fDocument.createCDATASection(value);
                        parent.insertBefore(node, node.getNextSibling());
                        index = value.indexOf("]]>");
                    }
                }
                break;
            }

        case Node.TEXT_NODE: { 
                if (DEBUG_ND) {
                    System.out.println("==>normalizeNode(text):{"+node.getNodeValue()+"}");
                }
                // If node is a text node, we need to check for one of two
                // conditions:
                //   1) There is an adjacent text node
                //   2) There is no adjacent text node, but node is
                //      an empty text node.
                Node next = node.getNextSibling();
                // If an adjacent text node, merge it with this node
                if ( next!=null && next.getNodeType() == Node.TEXT_NODE ) {
                    ((Text)node).appendData(next.getNodeValue());
                    node.getParentNode().removeChild( next );
                    return node; // Don't advance;
                } else if (node.getNodeValue().length()==0) {
                    // If kid is empty, remove it
                    node.getParentNode().removeChild( node );
                } else {
                    // validator.characters() call
                    // Don't send characters in the following cases:
                    // 1. entities is false, next child is entity reference: expand tree first
                    // 2. comments is false, and next child is comment
                    // 3. cdata is false, and next child is cdata

                    if (fValidationHandler != null) {
                        short nextType = (next != null)?next.getNodeType():-1;
                        if (!(((fDocument.features & CoreDocumentImpl.ENTITIES) == 0 &&
                               nextType == Node.ENTITY_NODE) ||
                              ((fDocument.features & CoreDocumentImpl.COMMENTS) == 0 &&
                               nextType == Node.COMMENT_NODE) ||
                              ((fDocument.features & CoreDocumentImpl.CDATA) == 0) &&
                              nextType == Node.CDATA_SECTION_NODE)) {

                            //
                            // set error node in the dom error wrapper
                            // so if error occurs we can report an error node
                            fDocument.fErrorHandlerWrapper.fCurrentNode = node;
                            fValidationHandler.characterData(node.getNodeValue(), null);
                            if (DEBUG_ND) {
                                System.out.println("=====>characterData(),"+nextType);

                            }
                        } else {
                            if (DEBUG_ND) {
                                System.out.println("=====>don't send characters(),"+nextType);

                            }
                        }
                    }
                }
                break;
            }
        }
        return null;
    }

    protected final void expandEntityRef (Node node, Node parent, Node reference){
        Node kid, next;
        for (kid = node.getFirstChild(); kid != null; kid = next) {
            next = kid.getNextSibling();
            if (node.getNodeType() == Node.TEXT_NODE) {
                expandEntityRef(kid, parent, reference);
            } else {
                parent.insertBefore(kid, reference);
            }
        }
    }

    protected final void namespaceFixUp (ElementImpl element, AttributeMap attributes){
        if (DEBUG) {
            System.out.println("[ns-fixup] element:" +element.getNodeName()+
                               " uri: "+element.getNamespaceURI());
        }

        // ------------------------------------
        // pick up local namespace declarations
        // <xsl:stylesheet xmlns:xsl="http://xslt">
        //   <!-- add the following via DOM 
        //          body is bound to http://xslt
        //    -->
        //   <xsl:body xmlns:xsl="http://bound"/>
        //
        // ------------------------------------

        String localUri, value, name, uri, prefix;
        if (attributes != null) {

            // Record all valid local declarations
            for (int k=0; k < attributes.getLength(); k++) {
                Attr attr = (Attr)attributes.getItem(k);
                uri = attr.getNamespaceURI();
                if (uri != null && uri.equals(NamespaceSupport.XMLNS_URI)) {
                    // namespace attribute
                    value = attr.getNodeValue();
                    if (value == null) {
                        value=XMLSymbols.EMPTY_STRING;
                    }

                    // Check for invalid namespace declaration:
                    if (value.equals(NamespaceSupport.XMLNS_URI)) {
                        if (fErrorHandler != null) {
                            modifyDOMError("No prefix other than 'xmlns' can be bound to 'http://www.w3.org/2000/xmlns/' namespace name", 
                                           DOMError.SEVERITY_ERROR, attr);
                            boolean continueProcess = fErrorHandler.handleError(fDOMError);
                            if (!continueProcess) {
                                // stop the namespace fixup and validation
                                throw new RuntimeException("Stopped at user request");
                            }
                        }
                    } else {
                        prefix = attr.getPrefix();
                        prefix = (prefix == null || 
                                  prefix.length() == 0) ? XMLSymbols.EMPTY_STRING :fSymbolTable.addSymbol(prefix);
                        String localpart = fSymbolTable.addSymbol( attr.getLocalName());
                        if (prefix == XMLSymbols.EMPTY_STRING) { //xmlns:prefix

                            value = fSymbolTable.addSymbol(value);
                            if (value.length() != 0) {
                                fNamespaceBinder.declarePrefix(localpart, value);
                                fLocalNSBinder.declarePrefix(localpart, value);

                                if (fValidationHandler != null) {
                                    fValidationHandler.startPrefixMapping(localpart, value, null);
                                }
                            } else {
                                // REVISIT: issue error on invalid declarations
                                //          xmlns:foo = ""

                            }
                            removeDefault (attr, attributes);
                            continue;
                        } else { // (localpart == fXmlnsSymbol && prefix == fEmptySymbol)  -- xmlns
                            // empty prefix is always bound ("" or some string)
                            value = fSymbolTable.addSymbol(value);
                            fLocalNSBinder.declarePrefix(XMLSymbols.EMPTY_STRING, value);
                            fNamespaceBinder.declarePrefix(XMLSymbols.EMPTY_STRING, value);

                            if (fValidationHandler != null) {
                                fValidationHandler.startPrefixMapping(XMLSymbols.EMPTY_STRING, value, null);
                            }
                            removeDefault (attr, attributes);
                            continue;
                        }
                    }  // end-else: valid declaration
                } // end-if: namespace attribute

            }
        }



        // ---------------------------------------------------------
        // Fix up namespaces for element: per DOM L3 
        // Need to consider the following cases:
        //
        // case 1: <xsl:stylesheet xmlns:xsl="http://xsl">
        // We create another element body bound to the "http://xsl" namespace
        // as well as namespace attribute rebounding xsl to another namespace.
        // <xsl:body xmlns:xsl="http://another">
        // Need to make sure that the new namespace decl value is changed to 
        // "http://xsl"
        //
        // ---------------------------------------------------------
        // check if prefix/namespace is correct for current element
        // ---------------------------------------------------------

        uri = element.getNamespaceURI();
        prefix = element.getPrefix();
        if (uri != null) {  // Element has a namespace
            uri = fSymbolTable.addSymbol(uri);
            prefix = (prefix == null || 
                      prefix.length() == 0) ? XMLSymbols.EMPTY_STRING :fSymbolTable.addSymbol(prefix);
            if (fNamespaceBinder.getURI(prefix) == uri) {
                // The xmlns:prefix=namespace or xmlns="default" was declared at parent.
                // The binder always stores mapping of empty prefix to "".
            } else {
                // the prefix is either undeclared 
                // or
                // conflict: the prefix is bound to another URI
                addNamespaceDecl(prefix, uri, element);
                fLocalNSBinder.declarePrefix(prefix, uri);
                fNamespaceBinder.declarePrefix(prefix, uri);
                // send startPrefixMapping call 
                if (fValidationHandler != null) {
                    fValidationHandler.startPrefixMapping(prefix, uri, null);
                }
            }
        } else { // Element has no namespace
            String tagName = element.getNodeName();
            int colon = tagName.indexOf(':');
            if (colon > -1) {
                //  Error situation: DOM Level 1 node!
                boolean continueProcess = true;
                if (fErrorHandler != null) {
                    if (fNamespaceValidation) {
                        modifyDOMError("DOM Level 1 node: "+tagName, DOMError.SEVERITY_FATAL_ERROR, element);
                        fErrorHandler.handleError(fDOMError);
                    } else {
                        modifyDOMError("DOM Level 1 node: "+tagName, DOMError.SEVERITY_ERROR, element);
                        continueProcess = fErrorHandler.handleError(fDOMError);
                    }
                }
                if (fNamespaceValidation || !continueProcess) {
                    // stop the namespace fixup and validation
                    throw new RuntimeException("DOM Level 1 node: "+tagName);
                }
            } else { // uri=null and no colon (DOM L2 node)
                uri = fNamespaceBinder.getURI(XMLSymbols.EMPTY_STRING);
                if (uri !=null && uri.length() > 0) {
                    // undeclare default namespace declaration (before that element
                    // bound to non-zero length uir), but adding xmlns="" decl                    
                    addNamespaceDecl (XMLSymbols.EMPTY_STRING, XMLSymbols.EMPTY_STRING, element);
                    fLocalNSBinder.declarePrefix(XMLSymbols.EMPTY_STRING, XMLSymbols.EMPTY_STRING);
                    fNamespaceBinder.declarePrefix(XMLSymbols.EMPTY_STRING, XMLSymbols.EMPTY_STRING);
                    if (fValidationHandler != null) {
                        fValidationHandler.startPrefixMapping(XMLSymbols.EMPTY_STRING, XMLSymbols.EMPTY_STRING, null);
                    }
                }
            }
        }

        // -----------------------------------------
        // Fix up namespaces for attributes: per DOM L3 
        // check if prefix/namespace is correct the attributes
        // -----------------------------------------
        if (attributes != null) {

            // clone content of the attributes
            attributes.cloneMap(fAttributeList);
            for (int i = 0; i < fAttributeList.size(); i++) {

                Attr attr = (Attr) fAttributeList.elementAt(i);
                // normalize attribute value
                attr.normalize();

                if (DEBUG) {
                    System.out.println("==>[ns-fixup] process attribute: "+attr.getNodeName());
                }
                value = attr.getValue();
                name = attr.getNodeName();                
                uri = attr.getNamespaceURI();

                // make sure that value is never null.
                if (value == null) {
                    value=XMLSymbols.EMPTY_STRING;
                }

                if (uri != null) {  // attribute has namespace !=null
                    prefix = attr.getPrefix();
                    prefix = (prefix == null || 
                              prefix.length() == 0) ? XMLSymbols.EMPTY_STRING :fSymbolTable.addSymbol(prefix);
                    String localpart = fSymbolTable.addSymbol( attr.getLocalName());

                    // ---------------------------------------
                    // skip namespace declarations 
                    // ---------------------------------------
                    // REVISIT: can we assume that "uri" is from some symbol
                    // table, and compare by reference? -SG
                    if (uri != null && uri.equals(NamespaceSupport.XMLNS_URI)) {
                        continue;
                    }


                    // ---------------------------------------
                    // remove default attributes
                    // ---------------------------------------
                    if (removeDefault(attr, attributes)) {
                        continue;
                    }


                    uri = fSymbolTable.addSymbol(uri);

                    // find if for this prefix a URI was already declared
                    String declaredURI =  fNamespaceBinder.getURI(prefix);

                    if (prefix == XMLSymbols.EMPTY_STRING || declaredURI != uri) {
                        // attribute has no prefix (default namespace decl does not apply to attributes) 
                        // OR
                        // attribute prefix is not declared
                        // OR
                        // conflict: attribute has a prefix that conficlicts with a binding
                        //           already active in scope

                        name  = attr.getNodeName();
                        // Find if any prefix for attributes namespace URI is available
                        // in the scope
                        String declaredPrefix = fNamespaceBinder.getPrefix(uri);
                        if (declaredPrefix !=null && declaredPrefix !=XMLSymbols.EMPTY_STRING) {

                            // use the prefix that was found (declared previously for this URI
                            prefix = declaredPrefix;
                        } else {
                            if (prefix != XMLSymbols.EMPTY_STRING && fLocalNSBinder.getURI(prefix) == null) {
                                // the current prefix is not null and it has no in scope declaration

                                // use this prefix
                            } else {

                                // find a prefix following the pattern "NS" +index (starting at 1)
                                // make sure this prefix is not declared in the current scope.
                                prefix = fSymbolTable.addSymbol(PREFIX +fNamespaceCounter++);
                                while (fLocalNSBinder.getURI(prefix)!=null) {
                                    prefix = fSymbolTable.addSymbol(PREFIX +fNamespaceCounter++);
                                }

                            }
                            // add declaration for the new prefix
                            addNamespaceDecl(prefix, uri, element);
                            value = fSymbolTable.addSymbol(value);
                            fLocalNSBinder.declarePrefix(prefix, value);
                            fNamespaceBinder.declarePrefix(prefix, uri);

                            if (fValidationHandler != null) {
                                fValidationHandler.startPrefixMapping(prefix, uri, null);
                            }
                        }

                        // change prefix for this attribute
                        attr.setPrefix(prefix);
                    }
                } else { // attribute uri == null

                    // data
                    int colon = name.indexOf(':');

                    if (colon > -1) {
                        // It is an error if document has DOM L1 nodes.
                        boolean continueProcess = true;
                        if (fErrorHandler != null) {
                            if (fNamespaceValidation) {
                                modifyDOMError("DOM Level 1 node: "+name, DOMError.SEVERITY_FATAL_ERROR, attr);
                                fErrorHandler.handleError(fDOMError);
                            } else {
                                modifyDOMError("DOM Level 1 node: "+name, DOMError.SEVERITY_ERROR, attr);
                                continueProcess = fErrorHandler.handleError(fDOMError);
                            }
                        }
                        if (fNamespaceValidation || !continueProcess) {
                            // stop the namespace fixup and validation
                            throw new RuntimeException("DOM Level 1 node");
                        }

                    } else {
                        // uri=null and no colon
                        // no fix up is needed: default namespace decl does not 

                        // ---------------------------------------
                        // remove default attributes
                        // ---------------------------------------
                        removeDefault(attr, attributes);
                    }
                }
            }
        } // end loop for attributes
    }




    /**
     * Adds a namespace attribute or replaces the value of existing namespace
     * attribute with the given prefix and value for URI.
     * In case prefix is empty will add/update default namespace declaration.
     * 
     * @param prefix
     * @param uri
     * @exception IOException
     */

    protected final void addNamespaceDecl(String prefix, String uri, ElementImpl element){
        if (DEBUG) {
            System.out.println("[ns-fixup] addNamespaceDecl ["+prefix+"]");
        }
        if (prefix == XMLSymbols.EMPTY_STRING) {
            if (DEBUG) {
                System.out.println("=>add xmlns=\""+uri+"\" declaration");
            }
            element.setAttributeNS(NamespaceSupport.XMLNS_URI, XMLSymbols.PREFIX_XMLNS, uri);             
        } else {
            if (DEBUG) {
                System.out.println("=>add xmlns:"+prefix+"=\""+uri+"\" declaration");
            }
            element.setAttributeNS(NamespaceSupport.XMLNS_URI, "xmlns:"+prefix, uri); 
        }
    }

    protected final boolean removeDefault (Attr attribute, AttributeMap attrMap){
        if ((fDocument.features & CoreDocumentImpl.DEFAULTS) != 0) {
            // remove default attributes
            if (!attribute.getSpecified()) {
                if (DEBUG_ND) {
                    System.out.println("==>remove default attr: "+attribute.getNodeName());
                }
                attrMap.removeItem(attribute, false);
                return true;
            }
        }
        return false;
    }


    protected final DOMError modifyDOMError(String message, short severity, Node node){
        fDOMError.reset();
        fDOMError.fMessage = message;
        fDOMError.fSeverity = severity;
        fDOMError.fLocator = fLocator;
        fLocator.fErrorNode = node;
        return fDOMError;
    }

    protected final void updateQName (Node node, QName qname){

        String prefix    = node.getPrefix();
        String namespace = node.getNamespaceURI();
        String localName = node.getLocalName();
        // REVISIT: the symbols are added too often: start/endElement
        //          and in the namespaceFixup. Should reduce number of calls to symbol table.
        qname.prefix = (prefix!=null && prefix.length()!=0)?fSymbolTable.addSymbol(prefix):null;
        qname.localpart = (localName != null)?fSymbolTable.addSymbol(localName):null;
        qname.rawname = fSymbolTable.addSymbol(node.getNodeName()); 
        qname.uri =  (namespace != null)?fSymbolTable.addSymbol(namespace):null;
    }

    protected final class XMLAttributesProxy 
    implements XMLAttributes {
        protected AttributeMap fAttributes;
        protected CoreDocumentImpl fDocument;
        protected ElementImpl fElement;

        protected final Vector fAugmentations = new Vector(5);


        public void setAttributes(AttributeMap attributes, CoreDocumentImpl doc, ElementImpl elem) {
            fDocument = doc;
            fAttributes = attributes;
            fElement = elem;
            if (attributes != null) {
                int length = attributes.getLength();

                fAugmentations.setSize(length);
                // REVISIT: this implementation does not store any value in augmentations
                //          and basically not keeping augs in parallel to attributes map
                //          untill all attributes are added (default attributes)
                for (int i = 0; i < length; i++) {
                    fAugmentations.setElementAt(new AugmentationsImpl(), i);
                }
            } else {
                fAugmentations.setSize(0);
            }
        }


        public int addAttribute(QName attrQName, String attrType, String attrValue){
            Attr attr = fDocument.createAttributeNS(attrQName.uri,
                                                    attrQName.rawname,
                                                    attrQName.localpart);
            attr.setValue(attrValue);
            if (fAttributes == null) {
                fAttributes = (AttributeMap)fElement.getAttributes();
            }
            int index = fElement.setXercesAttributeNode(attr);
            fAugmentations.insertElementAt(new AugmentationsImpl(), index);
            return index;
        }


        public void removeAllAttributes(){
            // REVISIT: implement
        }


        public void removeAttributeAt(int attrIndex){
            // REVISIT: implement
        }


        public int getLength(){
            return(fAttributes != null)?fAttributes.getLength():0;
        }


        public int getIndex(String qName){        
            // REVISIT: implement
            return -1;
        }

        public int getIndex(String uri, String localPart){
            // REVISIT: implement
            return -1;
        }

        public void setName(int attrIndex, QName attrName){
            // REVISIT: implement
        }

        public void getName(int attrIndex, QName attrName){
            if (fAttributes !=null) {
                updateQName((Node)fAttributes.getItem(attrIndex), attrName);
            }
        }

        public String getPrefix(int index){
            // REVISIT: implement
            return null;
        }


        public String getURI(int index){
            // REVISIT: implement
            return null;
        }


        public String getLocalName(int index){
            // REVISIT: implement
            return null;
        }


        public String getQName(int index){
            // REVISIT: implement
            return null;
        }


        public void setType(int attrIndex, String attrType){            
            // REVISIT: implement
        }


        public String getType(int index){
            return "CDATA";
        }


        public String getType(String qName){
            return "CDATA";
        }


        public String getType(String uri, String localName){
            return "CDATA";
        }


        public void setValue(int attrIndex, String attrValue){
            // REVISIT: implement
        }


        public String getValue(int index){
            return fAttributes.item(index).getNodeValue();

        }


        public String getValue(String qName){
            // REVISIT: implement
            return null;
        }


        public String getValue(String uri, String localName){            
            if (fAttributes != null) {
                Node node =  fAttributes.getNamedItemNS(uri, localName);
                return(node != null)? node.getNodeValue():null;
            }
            return null;
        }


        public void setNonNormalizedValue(int attrIndex, String attrValue){
            // REVISIT: implement

        }


        public String getNonNormalizedValue(int attrIndex){
            // REVISIT: implement
            return null;
        }


        public void setSpecified(int attrIndex, boolean specified){
            // REVISIT: this will be called after add attributes is called
            AttrImpl attr = (AttrImpl)fAttributes.getItem(attrIndex);
            attr.setSpecified(specified);
        }

        public boolean isSpecified(int attrIndex){
            return((Attr)fAttributes.getItem(attrIndex)).getSpecified();
        }

        public Augmentations getAugmentations (int attributeIndex){
            return(Augmentations)fAugmentations.elementAt(attributeIndex);
        }

        public Augmentations getAugmentations (String uri, String localPart){ 
            // REVISIT: implement
            return null;
        }

        public Augmentations getAugmentations(String qName){
            // REVISIT: implement
            return null;
        }
    }


    //
    // XML GrammarPool methods
    //
    protected final Grammar[] fGrammarPool = new Grammar[1];

    public Grammar[] retrieveInitialGrammarSet(String grammarType){
        // REVISIT: should take into account grammarType
        fGrammarPool[0] = fDocument.fGrammar;
        return null;

    }


    public void cacheGrammars(String grammarType, Grammar[] grammars){
        // REVISIT: implement
    }


    public Grammar retrieveGrammar(XMLGrammarDescription desc){
        return null;
    }

    public void lockPool(){
        // REVISIT: implement
    }


    public void unlockPool(){
        // REVISIT: implement
    }

    public void clear(){
        // REVISIT: implement
    }

    // 
    // XMLDocumentHandler methods
    //


}  // DOMNormalizer class