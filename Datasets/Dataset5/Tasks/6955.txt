if (normalizedValue !=null)

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


import java.util.Vector;

import org.apache.xerces.dom3.DOMError;
import org.apache.xerces.dom3.DOMErrorHandler;
import org.apache.xerces.impl.Constants;
import org.apache.xerces.impl.RevalidationHandler;
import org.apache.xerces.impl.dv.XSSimpleType;
import org.apache.xerces.impl.xs.psvi.XSTypeDefinition;
import org.apache.xerces.util.AugmentationsImpl;
import org.apache.xerces.util.NamespaceSupport;
import org.apache.xerces.util.SymbolTable;
import org.apache.xerces.util.XMLSymbols;
import org.apache.xerces.xni.Augmentations;
import org.apache.xerces.xni.NamespaceContext;
import org.apache.xerces.xni.QName;
import org.apache.xerces.xni.XMLAttributes;
import org.apache.xerces.xni.XMLDocumentHandler;
import org.apache.xerces.xni.XMLLocator;
import org.apache.xerces.xni.XMLResourceIdentifier;
import org.apache.xerces.xni.XMLString;
import org.apache.xerces.xni.XNIException;
import org.apache.xerces.xni.grammars.XMLGrammarDescription;
import org.apache.xerces.xni.parser.XMLComponent;
import org.apache.xerces.xni.parser.XMLConfigurationException;
import org.apache.xerces.xni.parser.XMLDocumentSource;
import org.apache.xerces.xni.psvi.AttributePSVI;
import org.apache.xerces.xni.psvi.ElementPSVI;
import org.w3c.dom.Attr;
import org.w3c.dom.Element;
import org.w3c.dom.Node;
import org.w3c.dom.Text;

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
 * NOTE: the implementation is experimental and methods, functionality
 *       can be modified or removed in the future.
 * 
 * @author Elena Litani, IBM
 * @version $Id$
 */
public class DOMNormalizer implements XMLDocumentHandler {


    //
    // REVISIT: 
    // 1. For element content we need to perform "2.11 End-of-Line Handling",
    //    see normalizeAttributeValue, characterData()
    // 2. Send all appropriate calls for entity reference content (?).

    //
    // constants
    //
    /** Debug normalize document*/
    protected final static boolean DEBUG_ND = false;
    /** Debug namespace fix up algorithm*/
    protected final static boolean DEBUG = false;
    /** Debug document handler events */
    protected final static boolean DEBUG_EVENTS = false;

    /** prefix added by namespace fixup algorithm should follow a pattern "NS" + index*/
    protected final static String PREFIX = "NS";

    //
    // Data
    //
    protected DOMConfigurationImpl fConfiguration = null;
    protected CoreDocumentImpl fDocument = null;
    protected final XMLAttributesProxy fAttrProxy = new XMLAttributesProxy();
    protected final QName fQName = new QName();

    /** Validation handler represents validator instance. */
    protected RevalidationHandler fValidationHandler;

    /** symbol table */
    protected SymbolTable fSymbolTable;
    /** error handler */
    protected DOMErrorHandler fErrorHandler;

    // Validation against namespace aware grammar
    protected boolean fNamespaceValidation = false;

    // Update PSVI information in the tree
    protected boolean fPSVI = false;

    /** The namespace context of this document: stores namespaces in scope */
    protected final NamespaceContext fNamespaceContext = new NamespaceSupport();

    /** Stores all namespace bindings on the current element */
    protected final NamespaceContext fLocalNSBinder = new NamespaceSupport();

    /** list of attributes */
    protected final Vector fAttributeList = new Vector(5,10);

    /** DOM Error object */
    protected final DOMErrorImpl fDOMError = new DOMErrorImpl();

    /** DOM Locator -  for namespace fixup algorithm */
    protected final DOMLocatorImpl fLocator = new DOMLocatorImpl();

    /** for setting the PSVI */
    protected Node fCurrentNode = null;
    private QName fAttrQName = new QName();
    
    // attribute value normalization
    final XMLString fNormalizedValue = new XMLString(new char[16], 0, 0);

    // 
    // Constructor
    // 

    public DOMNormalizer(){}



    /**
     * Normalizes document.
     * Note: reset() must be called before this method.
     */
	protected void normalizeDocument(CoreDocumentImpl document, DOMConfigurationImpl config) {

		fDocument = document;
		fConfiguration = config;

		// intialize and reset DOMNormalizer component
		// 
		fSymbolTable = (SymbolTable) fConfiguration.getProperty(DOMConfigurationImpl.SYMBOL_TABLE);
		// reset namespace context
		fNamespaceContext.reset();
		fNamespaceContext.declarePrefix(XMLSymbols.EMPTY_STRING, XMLSymbols.EMPTY_STRING);

		if ((fConfiguration.features & DOMConfigurationImpl.VALIDATE) != 0) {
			// REVISIT: currently we only support revalidation against XML Schemas
			fValidationHandler =
				CoreDOMImplementationImpl.singleton.getValidator(XMLGrammarDescription.XML_SCHEMA);
			fConfiguration.setFeature(DOMConfigurationImpl.XERCES_VALIDATION, true);
			fConfiguration.setFeature(DOMConfigurationImpl.SCHEMA, true);
			// report fatal error on DOM Level 1 nodes
			fNamespaceValidation = true;
            
			// check if we need to fill in PSVI
            fPSVI = ((fConfiguration.features & DOMConfigurationImpl.PSVI) !=0)?true:false;
            
            // reset ID table           
            fDocument.clearIdentifiers();
            
            // reset schema validator
			((XMLComponent) fValidationHandler).reset(fConfiguration);
		}

		fErrorHandler = (DOMErrorHandler) fConfiguration.getParameter("error-handler");
		if (fValidationHandler != null) {
			fValidationHandler.setBaseURI(fDocument.fDocumentURI);
			fValidationHandler.setDocumentHandler(this);
			fValidationHandler.startDocument(null, fDocument.encoding, fNamespaceContext, null);

		}
		try {
			Node kid, next;
			for (kid = fDocument.getFirstChild(); kid != null; kid = next) {
				next = kid.getNextSibling();
				kid = normalizeNode(kid);
				if (kid != null) { // don't advance
					next = kid;
				}
			}

			// release resources
			if (fValidationHandler != null) {
				fValidationHandler.endDocument(null);
				// REVISIT: only validation against XML Schema occurs
				CoreDOMImplementationImpl.singleton.releaseValidator(
					XMLGrammarDescription.XML_SCHEMA, fValidationHandler);
				fValidationHandler = null;
			}
		}
		catch (RuntimeException e) {
			// fatal error occured
			modifyDOMError(
				"Runtime exception: " + e.getMessage(),
				DOMError.SEVERITY_FATAL_ERROR,
				null);

			this.fErrorHandler.handleError(fDOMError);
			if (true) {
				e.printStackTrace();
			}
		}

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
     * @return  the normalized Node
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
                if ((fConfiguration.features & DOMConfigurationImpl.ENTITIES) == 0) {
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
                fNamespaceContext.pushContext();
                fLocalNSBinder.reset();

                ElementImpl elem = (ElementImpl)node;
                if (elem.needsSyncChildren()) {
                    elem.synchronizeChildren();
                }
                // REVISIT: need to optimize for the cases there normalization is not 
                //          needed and an element could be skipped.

                // Normalize all of the attributes & remove defaults
                AttributeMap attributes = (elem.hasAttributes()) ? (AttributeMap) elem.getAttributes() : null; 

                // fix namespaces and remove default attributes
                if ((fConfiguration.features & DOMConfigurationImpl.NAMESPACES) !=0) {
                    // fix namespaces
                    // normalize attribute values
                    // remove default attributes
                    namespaceFixUp(elem, attributes);
                } else {
                    if ( attributes!=null ) {
                        for ( int i=0; i<attributes.getLength(); ++i ) {
                            Attr attr = (Attr)attributes.item(i);
                            //removeDefault(attr, attributes);
                            attr.normalize();
                            // XML 1.0 attribute value normalization
                            //normalizeAttributeValue(attr.getValue(), attr);                            
                        }
                    }
                }
                if (fValidationHandler != null) {
                    // REVISIT: possible solutions to discard default content are:
                    //         either we pass some flag to XML Schema validator
                    //         or rely on the PSVI information.
                    fAttrProxy.setAttributes(attributes, fDocument, elem);
                    updateQName(elem, fQName); // updates global qname
                    // set error node in the dom error wrapper
                    // so if error occurs we can report an error node
                    fConfiguration.fErrorHandlerWrapper.fCurrentNode = node;
                    fCurrentNode = node;
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
                    fConfiguration.fErrorHandlerWrapper.fCurrentNode = node;
                    fCurrentNode = node;
                    fValidationHandler.endElement(fQName, null);
                }

                // pop namespace context
                fNamespaceContext.popContext();

                break;
            }

        case Node.COMMENT_NODE: {  
                if (DEBUG_ND) {
                    System.out.println("==>normalizeNode:{comments}");
                }

                if ((fConfiguration.features & DOMConfigurationImpl.COMMENTS) == 0) {
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

                if ((fConfiguration.features & DOMConfigurationImpl.ENTITIES) == 0) {
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
                if ((fConfiguration.features & DOMConfigurationImpl.CDATA) == 0) {
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
                    fConfiguration.fErrorHandlerWrapper.fCurrentNode = node;
                    fCurrentNode = node;
                    fValidationHandler.startCDATA(null);
                    fValidationHandler.characterData(node.getNodeValue(), null);
                    fValidationHandler.endCDATA(null);
                }

                if ((fConfiguration.features & DOMConfigurationImpl.SPLITCDATA) != 0) {
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
                        if (!(((fConfiguration.features & DOMConfigurationImpl.ENTITIES) == 0 &&
                               nextType == Node.ENTITY_NODE) ||
                              ((fConfiguration.features & DOMConfigurationImpl.COMMENTS) == 0 &&
                               nextType == Node.COMMENT_NODE) ||
                              ((fConfiguration.features & DOMConfigurationImpl.CDATA) == 0) &&
                              nextType == Node.CDATA_SECTION_NODE)) {

                            //
                            // set error node in the dom error wrapper
                            // so if error occurs we can report an error node
                            fConfiguration.fErrorHandlerWrapper.fCurrentNode = node;
                            fCurrentNode = node;
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
                if (uri != null && uri.equals(NamespaceContext.XMLNS_URI)) {
                    // namespace attribute
                    value = attr.getNodeValue();
                    if (value == null) {
                        value=XMLSymbols.EMPTY_STRING;
                    }

                    // Check for invalid namespace declaration:
                    if (value.equals(NamespaceContext.XMLNS_URI)) {
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
                        // XML 1.0 Attribute value normalization
                        // value = normalizeAttributeValue(value, attr);
                        prefix = attr.getPrefix();
                        prefix = (prefix == null || 
                                  prefix.length() == 0) ? XMLSymbols.EMPTY_STRING :fSymbolTable.addSymbol(prefix);
                        String localpart = fSymbolTable.addSymbol( attr.getLocalName());
                        if (prefix == XMLSymbols.PREFIX_XMLNS) { //xmlns:prefix

                            value = fSymbolTable.addSymbol(value);
                            if (value.length() != 0) {
                                fNamespaceContext.declarePrefix(localpart, value);
                            } else {
                                // REVISIT: issue error on invalid declarations
                                //          xmlns:foo = ""

                            }
                            //removeDefault (attr, attributes);
                            continue;
                        } else { // (localpart == fXmlnsSymbol && prefix == fEmptySymbol)  -- xmlns
                            // empty prefix is always bound ("" or some string)
                            value = fSymbolTable.addSymbol(value);
                            fNamespaceContext.declarePrefix(XMLSymbols.EMPTY_STRING, value);
                            //removeDefault (attr, attributes);
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
            if (fNamespaceContext.getURI(prefix) == uri) {
                // The xmlns:prefix=namespace or xmlns="default" was declared at parent.
                // The binder always stores mapping of empty prefix to "".
            } else {
                // the prefix is either undeclared 
                // or
                // conflict: the prefix is bound to another URI
                addNamespaceDecl(prefix, uri, element);
                fLocalNSBinder.declarePrefix(prefix, uri);
                fNamespaceContext.declarePrefix(prefix, uri);
            }
        } else { // Element has no namespace
            if (element.getLocalName() == null) {
                //  Error: DOM Level 1 node!
                boolean continueProcess = true;
                if (fErrorHandler != null) {
                    if (fNamespaceValidation) {
                        modifyDOMError("DOM Level 1 node: "+element.getNodeName(), DOMError.SEVERITY_FATAL_ERROR, element);
                        fErrorHandler.handleError(fDOMError);
                    } else {
                        modifyDOMError("DOM Level 1 node: "+element.getNodeName(), DOMError.SEVERITY_ERROR, element);
                        continueProcess = fErrorHandler.handleError(fDOMError);
                    }
                }
                if (fNamespaceValidation || !continueProcess) {
                    // stop the namespace fixup and validation
                    throw new RuntimeException("DOM Level 1 node: "+element.getNodeName());
                }
            } else { // uri=null and no colon (DOM L2 node)
                uri = fNamespaceContext.getURI(XMLSymbols.EMPTY_STRING);
                if (uri !=null && uri.length() > 0) {
                    // undeclare default namespace declaration (before that element
                    // bound to non-zero length uir), but adding xmlns="" decl                    
                    addNamespaceDecl (XMLSymbols.EMPTY_STRING, XMLSymbols.EMPTY_STRING, element);
                    fLocalNSBinder.declarePrefix(XMLSymbols.EMPTY_STRING, XMLSymbols.EMPTY_STRING);
                    fNamespaceContext.declarePrefix(XMLSymbols.EMPTY_STRING, XMLSymbols.EMPTY_STRING);
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

                if (DEBUG) {
                    System.out.println("==>[ns-fixup] process attribute: "+attr.getNodeName());
                }
                // normalize attribute value
                attr.normalize();                
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
                    if (uri != null && uri.equals(NamespaceContext.XMLNS_URI)) {
                        continue;
                    }

                    // ---------------------------------------
                    // remove default attributes
                    // ---------------------------------------
                    /* 
                    if (removeDefault(attr, attributes)) {
                        continue;
                    }
                    */
                    // XML 1.0 Attribute value normalization
                    //value = normalizeAttributeValue(value, attr);
                    
                    // reset id-attributes
                    ((AttrImpl)attr).setIdAttribute(false);


                    uri = fSymbolTable.addSymbol(uri);

                    // find if for this prefix a URI was already declared
                    String declaredURI =  fNamespaceContext.getURI(prefix);

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
                        String declaredPrefix = fNamespaceContext.getPrefix(uri);
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
                                int counter = 1;
                                prefix = fSymbolTable.addSymbol(PREFIX +counter++);
                                while (fLocalNSBinder.getURI(prefix)!=null) {
                                    prefix = fSymbolTable.addSymbol(PREFIX +counter++);
                                }

                            }
                            // add declaration for the new prefix
                            addNamespaceDecl(prefix, uri, element);
                            value = fSymbolTable.addSymbol(value);
                            fLocalNSBinder.declarePrefix(prefix, value);
                            fNamespaceContext.declarePrefix(prefix, uri);
                        }

                        // change prefix for this attribute
                        attr.setPrefix(prefix);
                    }
                } else { // attribute uri == null

                    // XML 1.0 Attribute value normalization
                    //value = normalizeAttributeValue(value, attr);
                    
                    // reset id-attributes
                    ((AttrImpl)attr).setIdAttribute(false);

                    if (attr.getLocalName() == null) {
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
                        // removeDefault(attr, attributes);
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
            element.setAttributeNS(NamespaceContext.XMLNS_URI, XMLSymbols.PREFIX_XMLNS, uri);             
        } else {
            if (DEBUG) {
                System.out.println("=>add xmlns:"+prefix+"=\""+uri+"\" declaration");
            }
            element.setAttributeNS(NamespaceContext.XMLNS_URI, "xmlns:"+prefix, uri); 
        }
    }

    /*protected final boolean removeDefault (Attr attribute, AttributeMap attrMap){
        if ((fConfiguration.features & DOMConfigurationImpl.DEFAULTS) != 0) {
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
    */


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

	/* REVISIT: remove this method if DOM does not change spec.
	 * Performs partial XML 1.0 attribute value normalization and replaces
     * attribute value if the value is changed after the normalization.
     * DOM defines that normalizeDocument acts as if the document was going 
     * through a save and load cycle, given that serializer will not escape
     * any '\n' or '\r' characters on load those will be normalized.
     * Thus during normalize document we need to do the following:
     * - perform "2.11 End-of-Line Handling"
     * - replace #xD, #xA, #x9 with #x20 (white space).
     * Note: This alg. won't attempt to resolve entity references or character entity 
     * references, since '&' will be escaped during serialization and during loading
     * this won't be recognized as entity reference, i.e. attribute value "&foo;" will 
     * be serialized as "&amp;foo;" and thus after loading will be "&foo;" again.
	 * @param value current attribute value
	 * @param attr current attribute
	 * @return String the value (could be original if normalization did not change 
     * the string)
	 */
    final String normalizeAttributeValue(String value, Attr attr) {
        if (!attr.getSpecified()){
            // specified attributes should already have a normalized form
            // since those were added by validator
            return value;
        }
        int end = value.length();
        // ensure capacity 
        if (fNormalizedValue.ch.length < end) {
            fNormalizedValue.ch = new char[end];
        }
        fNormalizedValue.length = 0;
        boolean normalized = false;
        for (int i = 0; i < end; i++) {
            char c = value.charAt(i);
            if (c==0x0009 || c==0x000A) {
               fNormalizedValue.ch[fNormalizedValue.length++] = ' '; 
               normalized = true;
            }
            else if(c==0x000D){
               normalized = true;
               fNormalizedValue.ch[fNormalizedValue.length++] = ' ';
               int next = i+1;
               if (next < end && value.charAt(next)==0x000A) i=next; // skip following xA
            }
            else {
                fNormalizedValue.ch[fNormalizedValue.length++] = c;
            }
        }
        if (normalized){
           value = fNormalizedValue.toString();
           attr.setValue(value);
        }
        return value;
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


		/**
         * This method adds default declarations
		 * @see org.apache.xerces.xni.XMLAttributes#addAttribute(QName, String, String)
		 */
		public int addAttribute(QName qname, String attrType, String attrValue) {
 			int index = fElement.getXercesAttribute(qname.uri, qname.localpart);
			// add defaults to the tree
			if (index < 0) {
                // the default attribute was removed by a user and needed to 
                // be added back
				AttrImpl attr = (AttrImpl)
					((CoreDocumentImpl) fElement.getOwnerDocument()).createAttributeNS(
						qname.uri,
						qname.rawname,
						qname.localpart);
                // REVISIT: the following should also update ID table
				index = fElement.setXercesAttributeNode(attr);
				attr.setNodeValue(attrValue);
				fAugmentations.insertElementAt(new AugmentationsImpl(), index);
                attr.setSpecified(false);
			}            
			else {
                // default attribute is in the tree
                // we don't need to do anything since prefix was already fixed
                // at the namespace fixup time and value must be same value, otherwise
                // attribute will be treated as specified and we will never reach 
                // this method.
                
            }
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
            // REVISIT: is this desired behaviour? 
            // The values are updated in the case datatype-normalization is turned on
            // in this case we need to make sure that specified attributes stay specified
            
            if (fAttributes != null){
                AttrImpl attr = (AttrImpl)fAttributes.getItem(attrIndex);
                boolean specified = attr.getSpecified();
                attr.setValue(attrValue);
                attr.setSpecified(specified);
            
            }
        }


        public String getValue(int index){
            return (fAttributes !=null)?fAttributes.item(index).getNodeValue():"";

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

        /**
         * Sets the augmentations of the attribute at the specified index.
         * 
         * @param attrIndex The attribute index.
         * @param augs      The augmentations.
         */
        public void setAugmentations(int attrIndex, Augmentations augs) {
            fAugmentations.setElementAt(augs, attrIndex);
        }
    }

    // 
    // XMLDocumentHandler methods
    //

    /**
     * The start of the document.
     * 
     * @param locator  The document locator, or null if the document
     *                 location cannot be reported during the parsing
     *                 of this document. However, it is <em>strongly</em>
     *                 recommended that a locator be supplied that can
     *                 at least report the system identifier of the
     *                 document.
     * @param encoding The auto-detected IANA encoding name of the entity
     *                 stream. This value will be null in those situations
     *                 where the entity encoding is not auto-detected (e.g.
     *                 internal entities or a document entity that is
     *                 parsed from a java.io.Reader).
     * @param namespaceContext
     *                 The namespace context in effect at the
     *                 start of this document.
     *                 This object represents the current context.
     *                 Implementors of this class are responsible
     *                 for copying the namespace bindings from the
     *                 the current context (and its parent contexts)
     *                 if that information is important.
     *                 
     * @param augs     Additional information that may include infoset augmentations
     * @exception XNIException
     *                   Thrown by handler to signal an error.
     */
    public void startDocument(XMLLocator locator, String encoding, 
                              NamespaceContext namespaceContext,
                              Augmentations augs) 
        throws XNIException{
    }

    /**
     * Notifies of the presence of an XMLDecl line in the document. If
     * present, this method will be called immediately following the
     * startDocument call.
     * 
     * @param version    The XML version.
     * @param encoding   The IANA encoding name of the document, or null if
     *                   not specified.
     * @param standalone The standalone value, or null if not specified.
     * @param augs       Additional information that may include infoset augmentations
     *                   
     * @exception XNIException
     *                   Thrown by handler to signal an error.
     */
    public void xmlDecl(String version, String encoding, String standalone, Augmentations augs)
        throws XNIException{
    }

    /**
     * Notifies of the presence of the DOCTYPE line in the document.
     * 
     * @param rootElement
     *                 The name of the root element.
     * @param publicId The public identifier if an external DTD or null
     *                 if the external DTD is specified using SYSTEM.
     * @param systemId The system identifier if an external DTD, null
     *                 otherwise.
     * @param augs     Additional information that may include infoset augmentations
     *                 
     * @exception XNIException
     *                   Thrown by handler to signal an error.
     */
    public void doctypeDecl(String rootElement, String publicId, String systemId, Augmentations augs)
        throws XNIException{
    }

    /**
     * A comment.
     * 
     * @param text   The text in the comment.
     * @param augs   Additional information that may include infoset augmentations
     *               
     * @exception XNIException
     *                   Thrown by application to signal an error.
     */
    public void comment(XMLString text, Augmentations augs) throws XNIException{
    }

    /**
     * A processing instruction. Processing instructions consist of a
     * target name and, optionally, text data. The data is only meaningful
     * to the application.
     * <p>
     * Typically, a processing instruction's data will contain a series
     * of pseudo-attributes. These pseudo-attributes follow the form of
     * element attributes but are <strong>not</strong> parsed or presented
     * to the application as anything other than text. The application is
     * responsible for parsing the data.
     * 
     * @param target The target.
     * @param data   The data or null if none specified.
     * @param augs   Additional information that may include infoset augmentations
     *               
     * @exception XNIException
     *                   Thrown by handler to signal an error.
     */
    public void processingInstruction(String target, XMLString data, Augmentations augs)
        throws XNIException{
    }

    /**
     * The start of an element.
     * 
     * @param element    The name of the element.
     * @param attributes The element attributes.
     * @param augs       Additional information that may include infoset augmentations
     *                   
     * @exception XNIException
     *                   Thrown by handler to signal an error.
     */
	public void startElement(QName element, XMLAttributes attributes, Augmentations augs)
		throws XNIException {
		//REVISIT: schema elements must be namespace aware.
		//         DTD re-validation is not implemented yet.. 
		Element currentElement = (Element) fCurrentNode;
		int attrCount = attributes.getLength();
        if (DEBUG_EVENTS) {
            System.out.println("==>startElement: " +element+
            " attrs.length="+attrCount);
        }

		for (int i = 0; i < attrCount; i++) {
			attributes.getName(i, fAttrQName);
			Attr attr = null;

			attr = currentElement.getAttributeNodeNS(fAttrQName.uri, fAttrQName.localpart);
            AttributePSVI attrPSVI =
				(AttributePSVI) attributes.getAugmentations(i).getItem(Constants.ATTRIBUTE_PSVI);

			if (attrPSVI != null) {
                //REVISIT: instead we should be using augmentations:
                // to set/retrieve Id attributes
                XSTypeDefinition decl = attrPSVI.getMemberTypeDefinition();
                boolean id = false;
                if (decl != null){
                    id = ((XSSimpleType)decl).isIDType();
                } else{
                    decl = attrPSVI.getTypeDefinition();
                    if (decl !=null){
                       id = ((XSSimpleType)decl).isIDType(); 
                    }
                }
                if (id){
                    ((ElementImpl)currentElement).setIdAttributeNode(attr, true);
                }
                
				if (fPSVI) {
					((PSVIAttrNSImpl) attr).setPSVI(attrPSVI);
				}
				if ((fConfiguration.features & DOMConfigurationImpl.DTNORMALIZATION) != 0) {
					// datatype-normalization
					// NOTE: The specified value MUST be set after we set
					//       the node value because that turns the "specified"
					//       flag to "true" which may overwrite a "false"
					//       value from the attribute list.
					boolean specified = attr.getSpecified();
					attr.setValue(attrPSVI.getSchemaNormalizedValue());
					if (!specified) {
						((AttrImpl) attr).setSpecified(specified);
					}
				}
			}
		}
	}


    /**
     * An empty element.
     * 
     * @param element    The name of the element.
     * @param attributes The element attributes.
     * @param augs       Additional information that may include infoset augmentations
     *                   
     * @exception XNIException
     *                   Thrown by handler to signal an error.
     */
	public void emptyElement(QName element, XMLAttributes attributes, Augmentations augs)
		throws XNIException {
        if (DEBUG_EVENTS) {
            System.out.println("==>emptyElement: " +element);
        }

		startElement(element, attributes, augs);
        endElement(element, augs);
	}

    /**
     * This method notifies the start of a general entity.
     * <p>
     * <strong>Note:</strong> This method is not called for entity references
     * appearing as part of attribute values.
     * 
     * @param name     The name of the general entity.
     * @param identifier The resource identifier.
     * @param encoding The auto-detected IANA encoding name of the entity
     *                 stream. This value will be null in those situations
     *                 where the entity encoding is not auto-detected (e.g.
     *                 internal entities or a document entity that is
     *                 parsed from a java.io.Reader).
     * @param augs     Additional information that may include infoset augmentations
     *                 
     * @exception XNIException Thrown by handler to signal an error.
     */
    public void startGeneralEntity(String name, 
                                   XMLResourceIdentifier identifier,
                                   String encoding,
                                   Augmentations augs) throws XNIException{
    }

    /**
     * Notifies of the presence of a TextDecl line in an entity. If present,
     * this method will be called immediately following the startEntity call.
     * <p>
     * <strong>Note:</strong> This method will never be called for the
     * document entity; it is only called for external general entities
     * referenced in document content.
     * <p>
     * <strong>Note:</strong> This method is not called for entity references
     * appearing as part of attribute values.
     * 
     * @param version  The XML version, or null if not specified.
     * @param encoding The IANA encoding name of the entity.
     * @param augs     Additional information that may include infoset augmentations
     *                 
     * @exception XNIException
     *                   Thrown by handler to signal an error.
     */
    public void textDecl(String version, String encoding, Augmentations augs) throws XNIException{
    }

    /**
     * This method notifies the end of a general entity.
     * <p>
     * <strong>Note:</strong> This method is not called for entity references
     * appearing as part of attribute values.
     * 
     * @param name   The name of the entity.
     * @param augs   Additional information that may include infoset augmentations
     *               
     * @exception XNIException
     *                   Thrown by handler to signal an error.
     */
    public void endGeneralEntity(String name, Augmentations augs) throws XNIException{
    }

    /**
     * Character content.
     * 
     * @param text   The content.
     * @param augs   Additional information that may include infoset augmentations
     *               
     * @exception XNIException
     *                   Thrown by handler to signal an error.
     */
    public void characters(XMLString text, Augmentations augs) throws XNIException{
    }

    /**
     * Ignorable whitespace. For this method to be called, the document
     * source must have some way of determining that the text containing
     * only whitespace characters should be considered ignorable. For
     * example, the validator can determine if a length of whitespace
     * characters in the document are ignorable based on the element
     * content model.
     * 
     * @param text   The ignorable whitespace.
     * @param augs   Additional information that may include infoset augmentations
     *               
     * @exception XNIException
     *                   Thrown by handler to signal an error.
     */
    public void ignorableWhitespace(XMLString text, Augmentations augs) throws XNIException{
    }

    /**
     * The end of an element.
     * 
     * @param element The name of the element.
     * @param augs    Additional information that may include infoset augmentations
     *                
     * @exception XNIException
     *                   Thrown by handler to signal an error.
     */
	public void endElement(QName element, Augmentations augs) throws XNIException {
		if (DEBUG_EVENTS) {
			System.out.println("==>endElement: " + element);
		}

		ElementPSVI elementPSVI = (ElementPSVI) augs.getItem(Constants.ELEMENT_PSVI);
		if (elementPSVI != null) {
			ElementImpl elementNode = (ElementImpl) fCurrentNode;
			if (fPSVI) {
				((PSVIElementNSImpl) fCurrentNode).setPSVI(elementPSVI);
			}
			// include element default content (if one is available)
			String normalizedValue = elementPSVI.getSchemaNormalizedValue();
			if ((fConfiguration.features & DOMConfigurationImpl.DTNORMALIZATION) != 0) {
                if (normalizedValue !=null)
				    elementNode.setTextContent(normalizedValue);
			}
			else {
				// NOTE: this is a hack: it is possible that DOM had an empty element
				// and validator sent default value using characters(), which we don't 
				// implement. Thus, here we attempt to add the default value.
				String text = elementNode.getTextContent();
				if (text.length() == 0) {
					// default content could be provided
					// REVISIT: should setTextConent(null) be allowed?
					elementNode.setTextContent(normalizedValue);
				}
			}
		}
	}


    /**
     * The start of a CDATA section.
     * 
     * @param augs   Additional information that may include infoset augmentations
     *               
     * @exception XNIException
     *                   Thrown by handler to signal an error.
     */
    public void startCDATA(Augmentations augs) throws XNIException{
    }

    /**
     * The end of a CDATA section.
     * 
     * @param augs   Additional information that may include infoset augmentations
     *               
     * @exception XNIException
     *                   Thrown by handler to signal an error.
     */
    public void endCDATA(Augmentations augs) throws XNIException{
    }

    /**
     * The end of the document.
     * 
     * @param augs   Additional information that may include infoset augmentations
     *               
     * @exception XNIException
     *                   Thrown by handler to signal an error.
     */
    public void endDocument(Augmentations augs) throws XNIException{
    }


    /** Sets the document source. */
    public void setDocumentSource(XMLDocumentSource source){
    }


    /** Returns the document source. */
    public XMLDocumentSource getDocumentSource(){
        return null;
    }

}  // DOMNormalizer class