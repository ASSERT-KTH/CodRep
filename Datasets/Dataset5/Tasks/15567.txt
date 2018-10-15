attrMap.removeItem(attribute, false);

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
public class DOMNormalizer implements XMLGrammarPool  {

    
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

    protected String fEmptySymbol;
    protected String fXmlSymbol;
    protected String fXmlnsSymbol;

    // counter for new prefix names
    protected int fNamespaceCounter = 1;

    /** stores namespaces in scope */
    protected final NamespaceSupport fNamespaceBinder = new NamespaceSupport();

    /** stores all namespace bindings on the current element */
    protected final NamespaceSupport fLocalNSBinder = new NamespaceSupport();

    /** list of attributes */
    protected final Vector fAttributeList = new Vector(5,10);

    /** DOM Error object */
    protected final DOMErrorImpl fDOMError = new DOMErrorImpl();

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
        fNamespaceBinder.reset(fSymbolTable);
        fNamespaceBinder.declarePrefix(fEmptySymbol, fEmptySymbol);
        fNamespaceCounter = 1;
        fXmlSymbol = fSymbolTable.addSymbol("xml");
        fXmlnsSymbol = fSymbolTable.addSymbol("xmlns");
        fEmptySymbol=fSymbolTable.addSymbol("");

        if (fValidationHandler != null) {
            ((XMLComponent)fValidationHandler).reset(componentManager);
            // REVISIT: how to pass and reuse namespace binder in the XML Schema validator?
        }
    }

    protected void setValidationHandler (RevalidationHandler validator){
        this.fValidationHandler = validator;
        
    }

    /**
     * Normalizes document.
     * Note: reset() must be called before this method.
     */
    protected void normalizeDocument(CoreDocumentImpl document){
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
    protected Node normalizeNode (Node node){

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
                if ((fDocument.features & CoreDocumentImpl.NSPROCESSING) !=0) {
                    // fix namespaces
                    // normalize attribute values
                    // remove default attributes
                    namespaceFixUp(elem, attributes);
                } 
                else {
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
                            nextType == Node.CDATA_SECTION_NODE)){
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

    protected void expandEntityRef (Node node, Node parent, Node reference){
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

    protected void namespaceFixUp (ElementImpl element, AttributeMap attributes){
        if (DEBUG) {
            System.out.println("[ns-fixup] element:" +element.getNodeName()+
                               " uri: "+element.getNamespaceURI());
        }
        String uri = element.getNamespaceURI();
        String prefix = element.getPrefix();
        // ---------------------------------------------------------
        // Fix up namespaces for element: per DOM L3 
        // Need to consider the following cases:
        //
        // case 1: <foo:elem xmlns:ns1="myURI" xmlns="default"/> 
        // Assume "foo", "ns1" are declared on the parent. We should not miss 
        // redeclaration for both "ns1" and default namespace. To solve this 
        // we add a local binder that stores declaration only for current element.
        // This way we avoid outputing duplicate declarations for the same element
        // as well as we are not omitting redeclarations.
        //
        // case 2: <elem xmlns="" xmlns="default"/> 
        // We need to bind default namespace to empty string, to be able to 
        // omit duplicate declarations for the same element
        //
        // ---------------------------------------------------------
        // check if prefix/namespace is correct for current element
        // ---------------------------------------------------------
        if (uri != null) {  // Element has a namespace
            uri = fSymbolTable.addSymbol(uri);
            prefix = (prefix == null || 
                      prefix.length() == 0) ? fEmptySymbol :fSymbolTable.addSymbol(prefix);
            if (fNamespaceBinder.getURI(prefix) == uri) {
                // The xmlns:prefix=namespace or xmlns="default" was declared at parent.
                // The binder always stores mapping of empty prefix to "".
            }
            else {
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
        }
        else { // Element has no namespace
            String tagName = element.getNodeName();
            int colon = tagName.indexOf(':');
            if (colon > -1) {
                //  DOM Level 1 node!
                int colon2 = tagName.lastIndexOf(':');
                if (colon != colon2) {
                    //not a QName: report an error
                    if (fErrorHandler != null) {
                        // REVISIT: the namespace fix up will be done only in case namespace 
                        // processing was performed.
                        modifyDOMError("Element's name is not a QName: "+tagName, DOMError.SEVERITY_ERROR, element);
                        boolean continueProcess = fErrorHandler.handleError(fDOMError);
                        // REVISIT: should we terminate upon request?                        
                    }
                    
                }
                else {
                    // A valid QName however element is not bound to namespace
                    // REVISIT: should we report an error in case prefix is not bound to anything?
                    if (fErrorHandler != null) {
                        modifyDOMError("Element <"+tagName+
                                       "> does not belong to any namespace: prefix could be undeclared or bound to some namespace", 
                                       DOMError.SEVERITY_WARNING, element);
                        boolean continueProcess = fErrorHandler.handleError(fDOMError);
                        // REVISIT: should we terminate upon request?                        
                    }
                    
                }
            }
            else { // uri=null and no colon (DOM L2 node)
                uri = fNamespaceBinder.getURI(fEmptySymbol);
                if (uri !=null && uri.length() > 0) {
                    // undeclare default namespace declaration (before that element
                    // bound to non-zero length uir), but adding xmlns="" decl                    
                    addNamespaceDecl (fEmptySymbol, fEmptySymbol, element);
                    fLocalNSBinder.declarePrefix(fEmptySymbol, fEmptySymbol);
                    fNamespaceBinder.declarePrefix(fEmptySymbol, fEmptySymbol);
                    if (fValidationHandler != null) {
                        fValidationHandler.startPrefixMapping(fEmptySymbol, fEmptySymbol, null);
                    }
                }
            }
        }

        // -----------------------------------------
        // Fix up namespaces for attributes: per DOM L3 
        // check if prefix/namespace is correct the attributes
        // -----------------------------------------
        String localUri, value, name;
        if (attributes != null) {

            // REVISIT: common code for handling namespace attributes for DOM L2 nodes
            //          and DOM L1 nodes. Currently because we don't skip invalid declarations
            //          for L1, we might output more namespace declarations than we would have
            //          if namespace processing was performed (duplicate decls on different elements)
            // Open issues:
            // 1. Is it allowed to mix DOM L1 with DOM L2 nodes
            // 2. Should we skip invalid namespace declarations or attributes not with QName
            //    [what should be the default behaviour]
            // 3. What should happen if the tree is DOM L1 tree (no namespace processing was
            //    performed)? Should we attempt any fixup??
            //

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
                    value=fEmptySymbol;
                }

                if (uri != null) {  // attribute has namespace !=null
                    prefix = attr.getPrefix();
                    prefix = (prefix == null || 
                              prefix.length() == 0) ? fEmptySymbol :fSymbolTable.addSymbol(prefix);
                    String localpart = fSymbolTable.addSymbol( attr.getLocalName());

                    // check if attribute is a namespace decl 
                    if (prefix == fXmlnsSymbol) { //xmlns:prefix
                        uri =  fNamespaceBinder.getURI(localpart);    // global prefix mapping
                        localUri = fLocalNSBinder.getURI(localpart);  // local prefix mapping
                        value = fSymbolTable.addSymbol(value);
                        if (uri == null || localUri == null) {
                            if (value.length() != 0) { 
                                fNamespaceBinder.declarePrefix(localpart, value);
                                fLocalNSBinder.declarePrefix(localpart, value);

                                if (fValidationHandler != null) {
                                    fValidationHandler.startPrefixMapping(localpart, value, null);
                                }
                            } else {
                                // REVISIT: we issue error on invalid declarations
                                //          xmlns:foo = ""

                            }
                        }
                        removeDefault(attr, attributes);
                        continue;
                    }
                    else if (localpart == fXmlnsSymbol && prefix == fEmptySymbol) { // xmlns
                        // empty prefix is always bound ("" or some string)
                        uri = fNamespaceBinder.getURI(fEmptySymbol);
                        localUri=fLocalNSBinder.getURI(fEmptySymbol);
                        value = fSymbolTable.addSymbol(value);
                        if (localUri == null) {
                            // there was no local default ns decl
                            fLocalNSBinder.declarePrefix(fEmptySymbol, value);
                            fNamespaceBinder.declarePrefix(fEmptySymbol, value);

                            if (fValidationHandler != null) {
                                fValidationHandler.startPrefixMapping(fEmptySymbol, value, null);
                            }
                            
                        }
                        removeDefault(attr, attributes);
                        continue;
                    }
                    // we don't need to fix anything for default attributes
                    removeDefault(attr, attributes);
                    uri = fSymbolTable.addSymbol(uri);

                    // find if for this prefix a URI was already declared
                    String declaredURI =  fNamespaceBinder.getURI(prefix);

                    if (prefix == fEmptySymbol || declaredURI != uri) {
                        // attribute has no prefix (default namespace decl does not apply to attributes) 
                        // OR
                        // attribute prefix is not declared
                        // OR
                        // conflict: attr URI does not match the prefix in scope

                        name  = attr.getNodeName();
                        // Find if any prefix for attributes namespace URI is available
                        // in the scope
                        String declaredPrefix = fNamespaceBinder.getPrefix(uri);
                        if (declaredPrefix == null || declaredPrefix == fEmptySymbol) {
                            // could not find a prefix/prefix is empty string
                            if (DEBUG) {
                                System.out.println("==> cound not find prefix for the attribute: " +prefix);
                            }
                            if (prefix != fEmptySymbol) {
                                // no need to create a new prefix:
                                // use the one on the attribute
                            }
                            else {
                                // create new prefix
                                prefix = PREFIX +fNamespaceCounter++; 
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
                        else {
                            // use the prefix that was found (declared previously for this URI
                            prefix = declaredPrefix;
                        }
                        // change prefix for this attribute
                        attr.setPrefix(prefix);
                    }
                }
                else { // attribute uri == null

                    // data
                    int colon = name.indexOf(':');
                    int colon2 = name.lastIndexOf(':');
                    //
                    // process namespace declarations
                    //
                    if (name.startsWith(fXmlnsSymbol)) {
                        //
                        //  DOM Level 1 node!
                        // 
                        if (colon < 0) {  // xmlns decl
                            // empty prefix is always bound ("" or some string)
                            uri = fNamespaceBinder.getURI(fEmptySymbol); 
                            localUri=fLocalNSBinder.getURI(fEmptySymbol);
                            if (localUri == null) {
                                value = fSymbolTable.addSymbol(value);
                                fNamespaceBinder.declarePrefix(fEmptySymbol, value);
                                fLocalNSBinder.declarePrefix(fEmptySymbol, value);
                                removeDefault(attr, attributes);
                            }
                            continue;
                        }
                        else if (colon == colon2) { // xmlns:prefix decl
                            // get prefix
                            prefix = name.substring(6);
                            prefix = (prefix.length() ==0) ? fEmptySymbol :fSymbolTable.addSymbol(prefix);
                            if (prefix.length() == 0) {
                                // REVISIT: report an error - invalid namespace declaration
                                
                            }
                            else if (value.length() == 0) {
                                // REVISIT: report an error
                            }

                            uri =  fNamespaceBinder.getURI(prefix);    // global prefix mapping
                            localUri = fLocalNSBinder.getURI(prefix);  // local prefix mapping
                            if (uri == null || localUri == null) {
                                // REVISIT: we are skipping invalid decls
                                //          xmlns:foo = ""
                                if (value.length() != 0) { 
                                    value = fSymbolTable.addSymbol(value);
                                    fNamespaceBinder.declarePrefix(prefix, value);
                                    fLocalNSBinder.declarePrefix(prefix, value);
                                   
                                }
                                // REVISIT: only if we can skip continue;
                            }
                        }
                    }
                    // remove default attribute
                    removeDefault(attr, attributes);
                    if (colon > -1) {
                        //
                        //  DOM Level 1 node!
                        // 
                        if (colon != colon2) {
                            //REVISIT: not a QName: report an error
                            if (fErrorHandler != null) {
                                modifyDOMError("Attribute's name is not a QName: "+name, DOMError.SEVERITY_ERROR, attr);
                                boolean continueProcess = fErrorHandler.handleError(fDOMError);
                                // REVISIT: stop?
                            } 

                        }
                        else {
                            // REVISIT: if we got here no namespace processing was performed
                            // report warnings
                            if (fErrorHandler != null) {
                                modifyDOMError("Attribute '"+name+"' does not belong to any namespace: prefix could be undeclared or bound to some namespace", 
                                DOMError.SEVERITY_WARNING, attr);
                                boolean continueProcess = fErrorHandler.handleError(fDOMError);
                            }
                        }
                        
                    }
                    else { 
                        // uri=null and no colon
                        // no fix up is needed: default namespace decl does not 
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

    protected void addNamespaceDecl(String prefix, String uri, ElementImpl element){
        if (DEBUG) {
            System.out.println("[ns-fixup] addNamespaceDecl ["+prefix+"]");
        }
        if (prefix == fEmptySymbol) {
            if (DEBUG) {
                System.out.println("=>add xmlns=\""+uri+"\" declaration");
            }
            element.setAttributeNS(NamespaceSupport.XMLNS_URI, "xmlns", uri);             
        }
        else {
            if (DEBUG) {
                System.out.println("=>add xmlns:"+prefix+"=\""+uri+"\" declaration");
            }
            element.setAttributeNS(NamespaceSupport.XMLNS_URI, "xmlns"+":"+prefix, uri); 
        }
    }

    protected void removeDefault (Attr attribute, AttributeMap attrMap){
        if ((fDocument.features & CoreDocumentImpl.DEFAULTS) != 0) {
            // remove default attributes
            if (!attribute.getSpecified()) {
                if (DEBUG_ND) {
                    System.out.println("==>remove default attr: "+attribute.getNodeName());
                }
                attrMap.removeItem(attribute);
            }
        }
    }


    protected DOMError modifyDOMError(String message, short severity, Node node){
            fDOMError.reset();
            fDOMError.setMessage(message);
            fDOMError.setSeverity(severity);
            // REVISIT: do we need to create a new locator for each error??
            fDOMError.setLocator(new DOMLocatorImpl(-1, -1, -1, node, null));
            return fDOMError;
        
    }

    protected void updateQName (Node node, QName qname){

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
        implements XMLAttributes{
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
            return (fAttributes != null)?fAttributes.getLength():0;
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
                return (node != null)? node.getNodeValue():null;
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
            return ((Attr)fAttributes.getItem(attrIndex)).getSpecified();
        }

        public Augmentations getAugmentations (int attributeIndex){
            return (Augmentations)fAugmentations.elementAt(attributeIndex);
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