str.append(fStringPool.toString(entityValueIndex));

/*
 * The Apache Software License, Version 1.1
 *
 *
 * Copyright (c) 1999,2000 The Apache Software Foundation.  All rights 
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

package org.apache.xerces.parsers;

import java.io.IOException;
import java.util.Enumeration;
import java.util.Hashtable;
import java.util.StringTokenizer;

import org.apache.xerces.dom.TextImpl;
import org.apache.xerces.framework.XMLAttrList;
import org.apache.xerces.framework.XMLContentSpec;
import org.apache.xerces.framework.XMLDocumentHandler;
import org.apache.xerces.framework.XMLParser;
import org.apache.xerces.readers.XMLEntityHandler;
import org.apache.xerces.utils.QName;
import org.apache.xerces.utils.StringPool;
import org.apache.xerces.validators.common.XMLAttributeDecl;
import org.apache.xerces.validators.common.XMLElementDecl;
import org.apache.xerces.validators.schema.XUtil;
import org.apache.xerces.validators.schema.SchemaSymbols;

import org.apache.xerces.dom.DeferredDocumentImpl;
import org.apache.xerces.dom.DocumentImpl;
import org.apache.xerces.dom.DocumentTypeImpl;
import org.apache.xerces.dom.NodeImpl;
import org.apache.xerces.dom.EntityImpl;
import org.apache.xerces.dom.NotationImpl;
import org.apache.xerces.dom.ElementDefinitionImpl;
import org.apache.xerces.dom.AttrImpl;
import org.apache.xerces.dom.TextImpl;
import org.apache.xerces.dom.ElementImpl;
import org.apache.xerces.dom.EntityImpl;
import org.apache.xerces.dom.EntityReferenceImpl;

import org.w3c.dom.Attr;
import org.w3c.dom.Comment;
import org.w3c.dom.Document;
import org.w3c.dom.DocumentType;
import org.w3c.dom.Element;
import org.w3c.dom.Entity;
import org.w3c.dom.EntityReference;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import org.w3c.dom.NamedNodeMap;
import org.w3c.dom.ProcessingInstruction;
import org.w3c.dom.Text;

import org.xml.sax.SAXException;
import org.xml.sax.SAXNotRecognizedException;
import org.xml.sax.SAXNotSupportedException;

/**
 * DOMParser provides a parser which produces a W3C DOM tree as its output
 *
 * 
 * @version $Id$
 */
public class DOMParser
    extends XMLParser
    implements XMLDocumentHandler
    {

    //
    // Constants
    //

    // public

    /** Default programmatic document class name (org.apache.xerces.dom.DocumentImpl). */
    public static final String DEFAULT_DOCUMENT_CLASS_NAME = "org.apache.xerces.dom.DocumentImpl";

    /** Default deferred document class name (org.apache.xerces.dom.DeferredDocumentImpl). */
    public static final String DEFAULT_DEFERRED_DOCUMENT_CLASS_NAME = "org.apache.xerces.dom.DeferredDocumentImpl";

    // debugging

    /** Set to true to debug attribute list declaration calls. */
    private static final boolean DEBUG_ATTLIST_DECL = false;

    // features and properties

    /** Features recognized by this parser. */
    private static final String RECOGNIZED_FEATURES[] = {
        // SAX2 core features
        // Xerces features
        "http://apache.org/xml/features/dom/defer-node-expansion",
        "http://apache.org/xml/features/dom/create-entity-ref-nodes",
        "http://apache.org/xml/features/dom/include-ignorable-whitespace",
        // Experimental features
        "http://apache.org/xml/features/domx/grammar-access",
    };

    /** Properties recognized by this parser. */
    private static final String RECOGNIZED_PROPERTIES[] = {
        // SAX2 core properties
        // Xerces properties
        "http://apache.org/xml/properties/dom/document-class-name",
        "http://apache.org/xml/properties/dom/current-element-node",
    };

    //
    // Data
    //

    // common data

    protected Document fDocument;

    // deferred expansion data

    protected DeferredDocumentImpl fDeferredDocumentImpl;
    protected int                  fDocumentIndex;
    protected int                  fDocumentTypeIndex;
    protected int                  fCurrentNodeIndex;
    
    //DOM Level 3 WD - experimental
    
    protected int                  fCurrentEntityName; //name of current entity reference
    protected int                  fCurrentEntityNode; //index of entity node corresponding to current entity reference
    
    // full expansion data

    protected DocumentImpl fDocumentImpl;
    protected DocumentType fDocumentType;
    protected Node         fCurrentElementNode;

    // state

    protected boolean fInDTD;
    protected boolean fWithinElement;
    protected boolean fInCDATA;

    // features
    private boolean fGrammarAccess;

    // properties

    // REVISIT: Even though these have setters and getters, should they
    //          be protected visibility? -Ac
    private String  fDocumentClassName;
    private boolean fDeferNodeExpansion;
    private boolean fCreateEntityReferenceNodes;
    private boolean fIncludeIgnorableWhitespace;

    // built-in entities

    protected int fAmpIndex;
    protected int fLtIndex;
    protected int fGtIndex;
    protected int fAposIndex;
    protected int fQuotIndex;

    private boolean fSeenRootElement;

    private boolean fStringPoolInUse;

    private XMLAttrList fAttrList;

    //
    // Constructors
    //

    /** Default constructor. */
    public DOMParser() {

        initHandlers(false, this, this);

        // setup parser state
        init();

        // set default values
        try {
            setDocumentClassName(DEFAULT_DOCUMENT_CLASS_NAME);
            setCreateEntityReferenceNodes(true);
            setDeferNodeExpansion(true);
            setIncludeIgnorableWhitespace(true);
        } catch (SAXException e) {
            throw new RuntimeException("PAR001 Fatal error constructing DOMParser.");
        }

    } // <init>()

    //
    // Public methods
    //

    // document

    /** Returns the document. */
    public Document getDocument() {
        return fDocument;
    }

    // features and properties

    /**
     * Returns a list of features that this parser recognizes.
     * This method will never return null; if no features are
     * recognized, this method will return a zero length array.
     *
     * @see #isFeatureRecognized
     * @see #setFeature
     * @see #getFeature
     */
    public String[] getFeaturesRecognized() {

        // get features that super/this recognizes
        String superRecognized[] = super.getFeaturesRecognized();
        String thisRecognized[] = RECOGNIZED_FEATURES;

        // is one or the other the empty set?
        int thisLength = thisRecognized.length;
        if (thisLength == 0) {
            return superRecognized;
        }
        int superLength = superRecognized.length;
        if (superLength == 0) {
            return thisRecognized;
        }

        // combine the two lists and return
        String recognized[] = new String[superLength + thisLength];
        System.arraycopy(superRecognized, 0, recognized, 0, superLength);
        System.arraycopy(thisRecognized, 0, recognized, superLength, thisLength);
        return recognized;

    } // getFeaturesRecognized():String[]

    /**
     * Returns a list of properties that this parser recognizes.
     * This method will never return null; if no properties are
     * recognized, this method will return a zero length array.
     *
     * @see #isPropertyRecognized
     * @see #setProperty
     * @see #getProperty
     */
    public String[] getPropertiesRecognized() {

        // get properties that super/this recognizes
        String superRecognized[] = super.getPropertiesRecognized();
        String thisRecognized[] = RECOGNIZED_PROPERTIES;

        // is one or the other the empty set?
        int thisLength = thisRecognized.length;
        if (thisLength == 0) {
            return superRecognized;
        }
        int superLength = superRecognized.length;
        if (superLength == 0) {
            return thisRecognized;
        }

        // combine the two lists and return
        String recognized[] = new String[superLength + thisLength];
        System.arraycopy(superRecognized, 0, recognized, 0, superLength);
        System.arraycopy(thisRecognized, 0, recognized, superLength, thisLength);
        return recognized;

    }

    // resetting

    /** Resets the parser. */
    public void reset() throws Exception {
        if (fStringPoolInUse) {
            // we can't reuse the string pool, let's create another one
            fStringPool = new StringPool();
            fStringPoolInUse = false;
        }
        super.reset();
        init();
    }

    /** Resets or copies the parser. */
    public void resetOrCopy() throws Exception {
        super.resetOrCopy();
        init();
    }

    //
    // Protected methods
    //

    // initialization

    /**
     * Initializes the parser to a pre-parse state. This method is
     * called between calls to <code>parse()</code>.
     */
    protected void init() {

        // init common
        fDocument = null;

        // init deferred expansion
        fDeferredDocumentImpl = null;
        fDocumentIndex = -1;
        fDocumentTypeIndex = -1;
        fCurrentNodeIndex = -1;
        
        //DOM Level 3 WD - experimental
        fCurrentEntityNode = -1;  
        fCurrentEntityName = -1; 

        // init full expansion
        fDocumentImpl = null;
        fDocumentType = null;
        fCurrentElementNode = null;

        // state
        fInDTD = false;
        fWithinElement = false;
        fInCDATA = false;

        // built-in entities
        fAmpIndex = fStringPool.addSymbol("amp");
        fLtIndex = fStringPool.addSymbol("lt");
        fGtIndex = fStringPool.addSymbol("gt");
        fAposIndex = fStringPool.addSymbol("apos");
        fQuotIndex = fStringPool.addSymbol("quot");

        fSeenRootElement = false;
        fStringPoolInUse = false;

        fAttrList = new XMLAttrList(fStringPool);

    } // init()

    // features

    /**
     * This method sets whether the expansion of the nodes in the default
     * DOM implementation are deferred.
     *
     * @see #getDeferNodeExpansion
     * @see #setDocumentClassName
     */
    protected void setDeferNodeExpansion(boolean deferNodeExpansion) 
        throws SAXNotRecognizedException, SAXNotSupportedException {
        fDeferNodeExpansion = deferNodeExpansion;
    }

    /**
     * Returns true if the expansion of the nodes in the default DOM
     * implementation are deferred.
     *
     * @see #setDeferNodeExpansion
     */
    protected boolean getDeferNodeExpansion() 
        throws SAXNotRecognizedException, SAXNotSupportedException {
        return fDeferNodeExpansion;
    }

    /**
     * This feature determines whether entity references within
     * the document are included in the document tree as
     * EntityReference nodes.
     * <p>
     * Note: The children of the entity reference are always
     * added to the document. This feature only affects
     * whether an EntityReference node is also included
     * as the parent of the entity reference children.
     *
     * @param create True to create entity reference nodes; false
     *               to only insert the entity reference children.
     *
     * @see #getCreateEntityReferenceNodes
     */
    protected void setCreateEntityReferenceNodes(boolean create) 
        throws SAXNotRecognizedException, SAXNotSupportedException {
        fCreateEntityReferenceNodes = create;
    }

    /**
     * Returns true if entity references within the document are
     * included in the document tree as EntityReference nodes.
     *
     * @see #setCreateEntityReferenceNodes
     */
    public boolean getCreateEntityReferenceNodes() 
        throws SAXNotRecognizedException, SAXNotSupportedException {
        return fCreateEntityReferenceNodes;
    }

    /**
     * This feature determines whether text nodes that can be
     * considered "ignorable whitespace" are included in the DOM
     * tree.
     * <p>
     * Note: The only way that the parser can determine if text
     * is ignorable is by reading the associated grammar
     * and having a content model for the document. When
     * ignorable whitespace text nodes *are* included in
     * the DOM tree, they will be flagged as ignorable.
     * The ignorable flag can be queried by calling the
     * TextImpl#isIgnorableWhitespace():boolean method.
     *
     * @param include True to include ignorable whitespace text nodes;
     *                false to not include ignorable whitespace text
     *                nodes.
     *
     * @see #getIncludeIgnorableWhitespace
     */
    public void setIncludeIgnorableWhitespace(boolean include) 
        throws SAXNotRecognizedException, SAXNotSupportedException {
        fIncludeIgnorableWhitespace = include;
    }

    /**
     * Returns true if ignorable whitespace text nodes are included
     * in the DOM tree.
     *
     * @see #setIncludeIgnorableWhitespace
     */
    public boolean getIncludeIgnorableWhitespace() 
        throws SAXNotRecognizedException, SAXNotSupportedException {
        return fIncludeIgnorableWhitespace;
    }
    
    // properties

    /**
     * This method allows the programmer to decide which document
     * factory to use when constructing the DOM tree. However, doing
     * so will lose the functionality of the default factory. Also,
     * a document class other than the default will lose the ability
     * to defer node expansion on the DOM tree produced.
     *
     * @param documentClassName The fully qualified class name of the
     *                      document factory to use when constructing
     *                      the DOM tree.
     *
     * @see #getDocumentClassName
     * @see #setDeferNodeExpansion
     * @see #DEFAULT_DOCUMENT_CLASS_NAME
     */
    protected void setDocumentClassName(String documentClassName) 
        throws SAXNotRecognizedException, SAXNotSupportedException {

        // normalize class name
        if (documentClassName == null) {
            documentClassName = DEFAULT_DOCUMENT_CLASS_NAME;
        }

        // verify that this class exists and is of the right type
        try {
            Class _class = Class.forName(documentClassName);
            //if (!_class.isAssignableFrom(Document.class)) {
            if (!Document.class.isAssignableFrom(_class)) {
                throw new IllegalArgumentException("PAR002 Class, \""+documentClassName+"\", is not of type org.w3c.dom.Document."+"\n"+documentClassName);
            }
        }
        catch (ClassNotFoundException e) {
            throw new IllegalArgumentException("PAR003 Class, \""+documentClassName+"\", not found."+"\n"+documentClassName);
        }

        // set document class name
        fDocumentClassName = documentClassName;
        if (!documentClassName.equals(DEFAULT_DOCUMENT_CLASS_NAME)) {
            setDeferNodeExpansion(false);
        }

    } // setDocumentClassName(String)

    /**
     * Returns the fully qualified class name of the document factory
     * used when constructing the DOM tree.
     *
     * @see #setDocumentClassName
     */
    protected String getDocumentClassName() 
        throws SAXNotRecognizedException, SAXNotSupportedException {
        return fDocumentClassName;
    }

    /**
     * Returns the current element node.
     * <p>
     * Note: This method is not supported when the "deferNodeExpansion"
     *       property is set to true and the document factory is set to
     *       the default factory.
     */
    protected Element getCurrentElementNode() 
        throws SAXNotRecognizedException, SAXNotSupportedException {

        if (fCurrentElementNode != null &&
            fCurrentElementNode.getNodeType() == Node.ELEMENT_NODE) {
            return (Element)fCurrentElementNode;
        }
        return null;

    } // getCurrentElementNode():Element

    //
    // Configurable methods
    //

    /**
     * Set the state of any feature in a SAX2 parser.  The parser
     * might not recognize the feature, and if it does recognize
     * it, it might not be able to fulfill the request.
     *
     * @param featureId The unique identifier (URI) of the feature.
     * @param state The requested state of the feature (true or false).
     *
     * @exception SAXNotRecognizedException If the requested feature is
     *                                      not known.
     * @exception SAXNotSupportedException If the requested feature is
     *                                     known, but the requested state
     *                                     is not supported.
     */
    public void setFeature(String featureId, boolean state)
        throws SAXNotRecognizedException, SAXNotSupportedException {

        //
        // SAX2 core features
        //

        if (featureId.startsWith(SAX2_FEATURES_PREFIX)) {
            //
            // No additional SAX properties defined for DOMParser.
            // Pass request off to XMLParser for the common cases.
            //
        }

        //
        // Xerces features
        //

        else if (featureId.startsWith(XERCES_FEATURES_PREFIX)) {
            String feature = featureId.substring(XERCES_FEATURES_PREFIX.length());
            //
            // http://apache.org/xml/features/dom/defer-node-expansion
            //   Allows the document tree returned by getDocument()
            //   to be constructed lazily. In other words, the DOM
            //   nodes are constructed as the tree is traversed.
            //   This allows the document to be returned sooner with
            //   the expense of holding all of the blocks of character
            //   data held in memory. Then again, lots of DOM nodes
            //   use a lot of memory as well.
            //
            if (feature.equals("dom/defer-node-expansion")) {
                if (fParseInProgress) {
                    throw new SAXNotSupportedException("PAR004 Cannot setFeature("+featureId + "): parse is in progress."+"\n"+featureId);
                }
                setDeferNodeExpansion(state);
                return;
            }
            //
            // http://apache.org/xml/features/dom/create-entity-ref-nodes
            //   This feature determines whether entity references within
            //   the document are included in the document tree as
            //   EntityReference nodes.
            //   Note: The children of the entity reference are always
            //         added to the document. This feature only affects
            //         whether an EntityReference node is also included
            //         as the parent of the entity reference children.
            //
            if (feature.equals("dom/create-entity-ref-nodes")) {
                setCreateEntityReferenceNodes(state);
                return;
            }

            //
            // http://apache.org/xml/features/dom/include-ignorable-whitespace
            //   This feature determines whether text nodes that can be
            //   considered "ignorable whitespace" are included in the DOM
            //   tree.
            //   Note: The only way that the parser can determine if text
            //         is ignorable is by reading the associated grammar
            //         and having a content model for the document. When
            //         ignorable whitespace text nodes *are* included in
            //         the DOM tree, they will be flagged as ignorable.
            //         The ignorable flag can be queried by calling the
            //         TextImpl#isIgnorableWhitespace():boolean method.
            //
            if (feature.equals("dom/include-ignorable-whitespace")) {
                setIncludeIgnorableWhitespace(state);
                return;
            }
            
            //
            // Experimental features
            //

            //
            // http://apache.org/xml/features/domx/grammar-access
            //   Allows grammar access in the DOM tree. Currently, this
            //   means that there is an XML Schema document tree as a
            //   child of the Doctype node.
            //
            if (feature.equals("domx/grammar-access")) {
                fGrammarAccess = state;
                return;
            }

            //
            // Pass request off to XMLParser for the common cases.
            //
        }

        //
        // Pass request off to XMLParser for the common cases.
        //
        super.setFeature(featureId, state);

    } // setFeature(String,boolean)

    /**
     * Query the current state of any feature in a SAX2 parser.  The
     * parser might not recognize the feature.
     *
     * @param featureId The unique identifier (URI) of the feature
     *                  being set.
     *
     * @return The current state of the feature.
     *
     * @exception SAXNotRecognizedException If the requested feature is
     *                                      not known.
     */
    public boolean getFeature(String featureId) 
        throws SAXNotRecognizedException, SAXNotSupportedException {

        //
        // SAX2 core features
        //

        if (featureId.startsWith(SAX2_FEATURES_PREFIX)) {
            //
            // No additional SAX properties defined for DOMParser.
            // Pass request off to XMLParser for the common cases.
            //
        }

        //
        // Xerces features
        //

        else if (featureId.startsWith(XERCES_FEATURES_PREFIX)) {
            String feature = featureId.substring(XERCES_FEATURES_PREFIX.length());
            //
            // http://apache.org/xml/features/dom/defer-node-expansion
            //   Allows the document tree returned by getDocument()
            //   to be constructed lazily. In other words, the DOM
            //   nodes are constructed as the tree is traversed.
            //   This allows the document to be returned sooner with
            //   the expense of holding all of the blocks of character
            //   data held in memory. Then again, lots of DOM nodes
            //   use a lot of memory as well.
            //
            if (feature.equals("dom/defer-node-expansion")) {
                return getDeferNodeExpansion();
            }
            //
            // http://apache.org/xml/features/dom/create-entity-ref-nodes
            //   This feature determines whether entity references within
            //   the document are included in the document tree as
            //   EntityReference nodes.
            //   Note: The children of the entity reference are always
            //         added to the document. This feature only affects
            //         whether an EntityReference node is also included
            //         as the parent of the entity reference children.
            //
            else if (feature.equals("dom/create-entity-ref-nodes")) {
                return getCreateEntityReferenceNodes();
            }

            //
            // http://apache.org/xml/features/dom/include-ignorable-whitespace
            //   This feature determines whether text nodes that can be
            //   considered "ignorable whitespace" are included in the DOM
            //   tree.
            //   Note: The only way that the parser can determine if text
            //         is ignorable is by reading the associated grammar
            //         and having a content model for the document. When
            //         ignorable whitespace text nodes *are* included in
            //         the DOM tree, they will be flagged as ignorable.
            //         The ignorable flag can be queried by calling the
            //         TextImpl#isIgnorableWhitespace():boolean method.
            //
            if (feature.equals("dom/include-ignorable-whitespace")) {
                return getIncludeIgnorableWhitespace();
            }

            //
            // Experimental features
            //

            //
            // http://apache.org/xml/features/domx/grammar-access
            //   Allows grammar access in the DOM tree. Currently, this
            //   means that there is an XML Schema document tree as a
            //   child of the Doctype node.
            //
            if (feature.equals("domx/grammar-access")) {
                return fGrammarAccess;
            }

            //
            // Pass request off to XMLParser for the common cases.
            //
        }

        //
        // Pass request off to XMLParser for the common cases.
        //
        return super.getFeature(featureId);

    } // getFeature(String):boolean

    /**
     * Set the value of any property in a SAX2 parser.  The parser
     * might not recognize the property, and if it does recognize
     * it, it might not support the requested value.
     *
     * @param propertyId The unique identifier (URI) of the property
     *                   being set.
     * @param Object The value to which the property is being set.
     *
     * @exception SAXNotRecognizedException If the requested property is
     *                                      not known.
     * @exception SAXNotSupportedException If the requested property is
     *                                     known, but the requested
     *                                     value is not supported.
     */
    public void setProperty(String propertyId, Object value)
        throws SAXNotRecognizedException, SAXNotSupportedException {

        //
        // Xerces properties
        //

        if (propertyId.startsWith(XERCES_PROPERTIES_PREFIX)) {
            String property = propertyId.substring(XERCES_PROPERTIES_PREFIX.length());
            //
            // http://apache.org/xml/properties/dom/current-element-node
            //   Returns the current element node as the DOM Parser is
            //   parsing. This property is useful for determining the
            //   relative location of the document when an error is
            //   encountered. Note that this feature does *not* work
            //   when the http://apache.org/xml/features/dom/defer-node-expansion
            //   is set to true.
            //
            if (property.equals("dom/current-element-node")) {
                throw new SAXNotSupportedException("PAR005 Property, \""+propertyId+"\" is read-only.\n"+propertyId);
            }
            //
            // http://apache.org/xml/properties/dom/document-class-name
            //   This property can be used to set/query the name of the
            //   document factory.
            //
            else if (property.equals("dom/document-class-name")) {
                if (value != null && !(value instanceof String)) {
                    throw new SAXNotSupportedException("PAR006 Property value must be of type java.lang.String.");
                }
                setDocumentClassName((String)value);
                return;
            }
        }

        //
        // Pass request off to XMLParser for the common cases.
        //
        super.setProperty(propertyId, value);

    } // setProperty(String,Object)

    /**
     * Return the current value of a property in a SAX2 parser.
     * The parser might not recognize the property.
     *
     * @param propertyId The unique identifier (URI) of the property
     *                   being set.
     *
     * @return The current value of the property.
     *
     * @exception SAXNotRecognizedException If the requested property is
     *                                      not known.
     *
     * @see Configurable#getProperty
     */
    public Object getProperty(String propertyId) 
        throws SAXNotRecognizedException, SAXNotSupportedException {

        //
        // Xerces properties
        //

        if (propertyId.startsWith(XERCES_PROPERTIES_PREFIX)) {
            String property = propertyId.substring(XERCES_PROPERTIES_PREFIX.length());
            //
            // http://apache.org/xml/properties/dom/current-element-node
            //   Returns the current element node as the DOM Parser is
            //   parsing. This property is useful for determining the
            //   relative location of the document when an error is
            //   encountered. Note that this feature does *not* work
            //   when the http://apache.org/xml/features/dom/defer-node-expansion
            //   is set to true.
            //
            if (property.equals("dom/current-element-node")) {
                boolean throwException = false;
                try {
                    throwException = getFeature(XERCES_FEATURES_PREFIX+"dom/defer-node-expansion");
                }
                catch (SAXNotSupportedException e) {
                    // ignore
                }
                catch (SAXNotRecognizedException e) {
                    // ignore
                }
                if (throwException) {
                    throw new SAXNotSupportedException("PAR007 Current element node cannot be queried when node expansion is deferred.");
                }
                return getCurrentElementNode();
            }
            //
            // http://apache.org/xml/properties/dom/document-class-name
            //   This property can be used to set/query the name of the
            //   document factory.
            //
            else if (property.equals("dom/document-class-name")) {
                return getDocumentClassName();
            }
        }

        //
        // Pass request off to XMLParser for the common cases.
        //
        return super.getProperty(propertyId);

    } // getProperty(String):Object

    //
    // XMLParser methods
    //

    /** Start document. */
    public void startDocument() {

        // deferred expansion
        String documentClassName = null;
        try {
            documentClassName = getDocumentClassName();
        } catch (SAXException e) {
            throw new RuntimeException("PAR008 Fatal error getting document factory.");
        }
        boolean deferNodeExpansion = true;
        try {
            deferNodeExpansion = getDeferNodeExpansion();
        } catch (SAXException e) {
            throw new RuntimeException("PAR009 Fatal error reading expansion mode.");
        }
        try {
            boolean isDocumentImpl = fDocumentClassName.equals(DEFAULT_DOCUMENT_CLASS_NAME);
            boolean isDeferredImpl = fDocumentClassName.equals(DEFAULT_DEFERRED_DOCUMENT_CLASS_NAME);
            if (deferNodeExpansion && (isDocumentImpl || isDeferredImpl)) {
                boolean nsEnabled = false;
                try { nsEnabled = getNamespaces(); }
                catch (SAXException s) {}
                fDeferredDocumentImpl = new DeferredDocumentImpl(fStringPool, nsEnabled, fGrammarAccess);
                fStringPoolInUse = true;
                fDocument = fDeferredDocumentImpl;
                fDocumentIndex = fDeferredDocumentImpl.createDocument();
                fCurrentNodeIndex = fDocumentIndex;
            }

            // full expansion
            else {
                if (isDocumentImpl) {
                    fDocumentImpl = new DocumentImpl(fGrammarAccess);
                    fDocument = fDocumentImpl;
                    // set DOM error checking off
                    fDocumentImpl.setErrorChecking(false);
                }
                else {
                    Class documentClass = Class.forName(documentClassName);
                    try {
                        fDocument = (Document)documentClass.newInstance();
                    }
                    catch (Exception e) {
                        // REVISIT: Localize this message.
                        throw new RuntimeException(
                                 "Failed to create document object of class: "
                                 + documentClassName);
                    }
                    // if subclass of our own class that's cool too
                    Class defaultDocClass =
                        Class.forName(DEFAULT_DOCUMENT_CLASS_NAME);
                    if (defaultDocClass.isAssignableFrom(documentClass)) {
                        fDocumentImpl = (DocumentImpl)fDocument;
                        // set DOM error checking off
                        fDocumentImpl.setErrorChecking(false);
                    }
                }
                fCurrentElementNode = fDocument;
            }
        }
        catch (ClassNotFoundException e) {
            // REVISIT: Localize this message.
            throw new RuntimeException(documentClassName);
        }

    } // startDocument()

    /** End document. */
    public void endDocument() throws Exception {
        // set DOM error checking back on
        if (fDocumentImpl != null) {
            fDocumentImpl.setErrorChecking(true);
        
            if (fDocumentType!=null) {
                // set entities and notations read_only per DOM spec
                ((DocumentTypeImpl)fDocumentType).setReadOnly(true, false);
            }
        }
    }

    /** XML declaration. */
    public void xmlDecl(int versionIndex, int encodingIndex, int standaloneIndex) throws Exception {
        boolean standalone = (standaloneIndex!=-1)?(fStringPool.toString(standaloneIndex).equals("yes"))?true:false:false;
        if (fDocumentImpl != null) { //full node expansion
             fDocumentImpl.setVersion(fStringPool.toString(versionIndex));
             fDocumentImpl.setEncoding(fStringPool.toString(encodingIndex));
             fDocumentImpl.setStandalone(standalone);
         }
         else if (fDeferredDocumentImpl != null) {              
             fDeferredDocumentImpl.setVersion(fStringPool.toString(versionIndex));
             fDeferredDocumentImpl.setEncoding(fStringPool.toString(encodingIndex));
             fDeferredDocumentImpl.setStandalone(standalone);
         }
         else{
          //non xerces implementation
         }
         
         
    }

    /** Text declaration. 
     * added DOM Level 3 WD support - experimental
    */    
    public void textDecl(int versionIndex, int encodingIndex) throws Exception {
        if (fDeferredDocumentImpl != null)   {
            String name = fStringPool.toString(fCurrentEntityName);
            // we only support one context for entity references (name !=null)
            if (fDocumentTypeIndex != -1 && name != null) {
                // find Entity decl for fCurrentEntityName.
                int entityDecl = fDeferredDocumentImpl.getLastChild(fDocumentTypeIndex, false);
                while (entityDecl != -1) {
                    if (fDeferredDocumentImpl.getNodeType(entityDecl, false) == Node.ENTITY_NODE
                    && fDeferredDocumentImpl.getNodeNameString(entityDecl, false).equals(name)) { 
                        break;
                    }
                    entityDecl = fDeferredDocumentImpl.getPrevSibling(entityDecl, false);
                }
                fCurrentEntityNode = entityDecl;
                fDeferredDocumentImpl.setEntityInfo(entityDecl, versionIndex, encodingIndex);
            }    
        }
       // full node expansion
       else if (fDocumentImpl !=null){ 
            NamedNodeMap entities = fDocumentType.getEntities();
            if (entities!=null) {
                EntityImpl entityNode = (EntityImpl)entities.getNamedItem(fCurrentElementNode.getNodeName());
                if (entityNode !=null) {
                    entityNode.setVersion(fStringPool.toString(versionIndex));
                    entityNode.setEncoding(fStringPool.toString(encodingIndex));
                }
            }
        }
        else {
           //non xerces implementation
        }
    }

    /** Report the start of the scope of a namespace declaration. */
    public void startNamespaceDeclScope(int prefix, int uri) throws Exception {}

    /** Report the end of the scope of a namespace declaration. */
    public void endNamespaceDeclScope(int prefix) throws Exception {}
    
    

    /** Start element. */
    public void startElement(QName elementQName,
                             XMLAttrList xmlAttrList, int attrListIndex)
        throws Exception {

        // deferred expansion
        if (fDeferredDocumentImpl != null) {

            // copy schema grammar, if needed
            if (!fSeenRootElement) {
                fSeenRootElement = true;
                // REVISIT: How do we know which grammar is in use?
                //Document schemaDocument = fValidator.getSchemaDocument();
                if (fGrammarAccess && fGrammarResolver.size() > 0) {
                    if (fDocumentTypeIndex == -1) {
                        fDocumentTypeIndex = fDeferredDocumentImpl.createDocumentType(elementQName.rawname, -1, -1);
                        fDeferredDocumentImpl.appendChild(0, fDocumentTypeIndex);
                    }
                    Enumeration schemas = fGrammarResolver.nameSpaceKeys();
                    Document schemaDocument = fGrammarResolver.getGrammar((String)schemas.nextElement()).getGrammarDocument();
                    if (schemaDocument != null) {
                        Element schema = schemaDocument.getDocumentElement();
                        copyInto(schema, fDocumentTypeIndex);
                    }
                }
            }

            int element =
                fDeferredDocumentImpl.createElement(elementQName.rawname,
                                                    elementQName.uri,
                                                    xmlAttrList,
                                                    attrListIndex);
            fDeferredDocumentImpl.appendChild(fCurrentNodeIndex, element);
            fCurrentNodeIndex = element;
            fWithinElement = true;

            // identifier registration
            int index = xmlAttrList.getFirstAttr(attrListIndex);
            while (index != -1) {
                if (xmlAttrList.getAttType(index) == fStringPool.addSymbol("ID")) {
                    int nameIndex = xmlAttrList.getAttValue(index);
                    fDeferredDocumentImpl.putIdentifier(nameIndex, element);
                }
                index = xmlAttrList.getNextAttr(index);
            }
        }

        // full expansion
        else {

            boolean nsEnabled = false;
            try { nsEnabled = getNamespaces(); }
            catch (SAXException s) {}

            String elementName = fStringPool.toString(elementQName.rawname);

            // copy schema grammar, if needed
            if (!fSeenRootElement) {
                fSeenRootElement = true;
                if (fDocumentImpl != null
                    && fGrammarAccess && fGrammarResolver.size() > 0) {
                    if (fDocumentType == null) {
                        String rootName = elementName;
                        String systemId = ""; // REVISIT: How do we get this value? -Ac
                        String publicId = ""; // REVISIT: How do we get this value? -Ac
                        fDocumentType = fDocumentImpl.createDocumentType(rootName, publicId, systemId);
                        fDocument.appendChild(fDocumentType);
                        // REVISIT: We could use introspection to get the
                        //          DOMImplementation#createDocumentType method
                        //          for DOM Level 2 implementations. The only
                        //          problem is that the owner document for the
                        //          node created is null. How does it get set
                        //          for document when appended? A cursory look
                        //          at the DOM Level 2 CR didn't yield any
                        //          information. -Ac
                    }
                    Enumeration schemas = fGrammarResolver.nameSpaceKeys();
                    Document schemaDocument = fGrammarResolver.getGrammar((String)schemas.nextElement()).getGrammarDocument();
                    if (schemaDocument != null) {
                        Element schema = schemaDocument.getDocumentElement();
                        XUtil.copyInto(schema, fDocumentType);
                    }
                }
            }

            Element e;
            if (nsEnabled) {
                e = fDocument.createElementNS(
                        // REVISIT: Make sure uri is filled in by caller.
                        fStringPool.toString(elementQName.uri), elementName);
            } else {
                e = fDocument.createElement(elementName);
            }
            int attrHandle = xmlAttrList.getFirstAttr(attrListIndex);
            while (attrHandle != -1) {
                int attName = xmlAttrList.getAttrName(attrHandle);
                String attrName = fStringPool.toString(attName);
                String attrValue =
                    fStringPool.toString(xmlAttrList.getAttValue(attrHandle));
                if (nsEnabled) {
		    int nsURIIndex = xmlAttrList.getAttrURI(attrHandle);
		    String namespaceURI = fStringPool.toString(nsURIIndex);
		    // DOM Level 2 wants all namespace declaration attributes
		    // to be bound to "http://www.w3.org/2000/xmlns/"
		    // So as long as the XML parser doesn't do it, it needs to
		    // done here.
		    int prefixIndex = xmlAttrList.getAttrPrefix(attrHandle);
		    String prefix = fStringPool.toString(prefixIndex);
		    if (namespaceURI == null || namespaceURI.length() == 0) {
			if (prefix != null) {
			    if (prefix.equals("xmlns")) {
				namespaceURI = "http://www.w3.org/2000/xmlns/";
			    }
			} else if (attrName.equals("xmlns")) {
			    namespaceURI = "http://www.w3.org/2000/xmlns/";
			}
		    }
                    e.setAttributeNS(namespaceURI, attrName, attrValue);
                } else {
                    e.setAttribute(attrName, attrValue);
                }
                if (fDocumentImpl != null
                    && !xmlAttrList.isSpecified(attrHandle)) {
                    ((AttrImpl)e.getAttributeNode(attrName))
                        .setSpecified(false);
                }
                attrHandle = xmlAttrList.getNextAttr(attrHandle);
            }
            fCurrentElementNode.appendChild(e);
            fCurrentElementNode = e;
            fWithinElement = true;

            // identifier registration
            if (fDocumentImpl != null) {
                int index = xmlAttrList.getFirstAttr(attrListIndex);
                while (index != -1) {
                    if (xmlAttrList.getAttType(index) == fStringPool.addSymbol("ID")) {
                        String name = fStringPool.toString(xmlAttrList.getAttValue(index));
                        fDocumentImpl.putIdentifier(name, e);
                    }
                    index = xmlAttrList.getNextAttr(index);
                }
            }

            // release attributes
            xmlAttrList.releaseAttrList(attrListIndex);
        }

    } // startElement(QName,XMLAttrList,int)

    /** End element. */
    public void endElement(QName elementQName)
        throws Exception {

        // deferred node expansion
        if (fDeferredDocumentImpl != null) {
            fCurrentNodeIndex = fDeferredDocumentImpl.getParentNode(fCurrentNodeIndex, false);
            fWithinElement = false;
        }

        // full node expansion
        else {
            fCurrentElementNode = fCurrentElementNode.getParentNode();
            fWithinElement = false;
        }

    } // endElement(QName)

    /** Characters. */
    public void characters(int dataIndex)
        throws Exception {

        // deferred node expansion
        if (fDeferredDocumentImpl != null) {

            int text;

            if (fInCDATA) {
                text = fDeferredDocumentImpl.createCDATASection(dataIndex, false);
            } else {
                // The Text normalization is taken care of within the Text Node
                // in the DEFERRED case.
                text = fDeferredDocumentImpl.createTextNode(dataIndex, false);
            }
            fDeferredDocumentImpl.appendChild(fCurrentNodeIndex, text);
        }

        // full node expansion
        else {

            Text text;

            if (fInCDATA) {
                text = fDocument.createCDATASection(fStringPool.orphanString(dataIndex));
            }
            else {

                if (fWithinElement && fCurrentElementNode.getNodeType() == Node.ELEMENT_NODE) {
                    Node lastChild = fCurrentElementNode.getLastChild();
                    if (lastChild != null
                        && lastChild.getNodeType() == Node.TEXT_NODE) {
                        // Normalization of Text Nodes - append rather than create.
                        ((Text)lastChild).appendData(fStringPool.orphanString(dataIndex));
                        return;
                    }
                }
                text = fDocument.createTextNode(fStringPool.orphanString(dataIndex));
            }

            fCurrentElementNode.appendChild(text);

        }

    } // characters(int)

    /** Ignorable whitespace. */
    public void ignorableWhitespace(int dataIndex) throws Exception {

        // ignore the whitespace
        if (!fIncludeIgnorableWhitespace) {
            fStringPool.orphanString(dataIndex);
            return;
        }

        // deferred node expansion
        if (fDeferredDocumentImpl != null) {

            int text;

            if (fInCDATA) {
                text = fDeferredDocumentImpl.createCDATASection(dataIndex, true);
            } else {
                // The Text normalization is taken care of within the Text Node
                // in the DEFERRED case.
                text = fDeferredDocumentImpl.createTextNode(dataIndex, true);
            }
            fDeferredDocumentImpl.appendChild(fCurrentNodeIndex, text);
        }

        // full node expansion
        else {

            Text text;

            if (fInCDATA) {
                text = fDocument.createCDATASection(fStringPool.orphanString(dataIndex));
            }
            else {

                if (fWithinElement && fCurrentElementNode.getNodeType() == Node.ELEMENT_NODE) {
                    Node lastChild = fCurrentElementNode.getLastChild();
                    if (lastChild != null
                        && lastChild.getNodeType() == Node.TEXT_NODE) {
                        // Normalization of Text Nodes - append rather than create.
                        ((Text)lastChild).appendData(fStringPool.orphanString(dataIndex));
                        return;
                    }
                }
                text = fDocument.createTextNode(fStringPool.orphanString(dataIndex));
            }

            if (fDocumentImpl != null) {
                ((TextImpl)text).setIgnorableWhitespace(true);
            }

            fCurrentElementNode.appendChild(text);

        }

    } // ignorableWhitespace(int)

    /** Processing instruction. */
    public void processingInstruction(int targetIndex, int dataIndex)
        throws Exception {

        // deferred node expansion
        if (fDeferredDocumentImpl != null) {
            int pi = fDeferredDocumentImpl.createProcessingInstruction(targetIndex, dataIndex);
            fDeferredDocumentImpl.appendChild(fCurrentNodeIndex, pi);
        }

        // full node expansion
        else {
            String target = fStringPool.orphanString(targetIndex);
            String data = fStringPool.orphanString(dataIndex);
            ProcessingInstruction pi = fDocument.createProcessingInstruction(target, data);
            fCurrentElementNode.appendChild(pi);
        }

    } // processingInstruction(int,int)

    /** Comment. */
    public void comment(int dataIndex) throws Exception {

        if (fInDTD && !fGrammarAccess) {
            fStringPool.orphanString(dataIndex);
        }
        else {
            // deferred node expansion
            if (fDeferredDocumentImpl != null) {
                int comment = fDeferredDocumentImpl.createComment(dataIndex);
                fDeferredDocumentImpl.appendChild(fCurrentNodeIndex, comment);
            }

            // full node expansion
            else {
                Comment comment = fDocument.createComment(fStringPool.orphanString(dataIndex));
                fCurrentElementNode.appendChild(comment);
            }
        }

    } // comment(int)

    // Callers who know they're interacting with this parser should use
    // characters(int); callers who don't know which parser they 
    // are interacting with, or who can't be sure of sharing
    // the same stringPool, should use this method.
    public void characters(char ch[], int start, int length) throws Exception { 
        characters(fStringPool.addSymbol(new String(ch, start, length)));
    } // characters(char[], int, int)

    /** Not called. */
    public void ignorableWhitespace(char ch[], int start, int length) throws Exception {}

    //
    // XMLDocumentScanner methods
    //

    /** Start CDATA section. */
    public void startCDATA() throws Exception {
        fInCDATA = true;
    }

    /** End CDATA section. */
    public void endCDATA() throws Exception {
        fInCDATA = false;
    }

    //
    // XMLEntityHandler methods
    //

    /** Start entity reference. */
    public void startEntityReference(int entityName, int entityType,
                                     int entityContext) throws Exception {
        
        fCurrentEntityName = entityName;
        // are we ignoring entity reference nodes?
        if (!fCreateEntityReferenceNodes) {
            return;
        }
        

        // ignore built-in entities
        if (entityName == fAmpIndex ||
            entityName == fGtIndex ||
            entityName == fLtIndex ||
            entityName == fAposIndex ||
            entityName == fQuotIndex) {
            return;
        }
         
        // we only support one context for entity references right now...
        if (entityContext != XMLEntityHandler.ENTITYREF_IN_CONTENT) {
            return;
        }
        
        // deferred node expansion
        
        if (fDeferredDocumentImpl != null) {
            
            int entityRefIndex = fDeferredDocumentImpl.createEntityReference(entityName);
            fDeferredDocumentImpl.appendChild(fCurrentNodeIndex, entityRefIndex);
            
            fCurrentNodeIndex = entityRefIndex;
            
        }

        // full node expansion
        else {

            EntityReference er =
             fDocument.createEntityReference(fStringPool.toString(entityName));

            fCurrentElementNode.appendChild(er);
            fCurrentElementNode = er;
        }

    } // startEntityReference(int,int,int)

    /** End entity reference. */
    public void endEntityReference(int entityName, int entityType,
                                   int entityContext) throws Exception {
        // are we ignoring entity reference nodes?
        if (!fCreateEntityReferenceNodes) {
            return;
        }

        // ignore built-in entities
        if (entityName == fAmpIndex ||
            entityName == fGtIndex ||
            entityName == fLtIndex ||
            entityName == fAposIndex ||
            entityName == fQuotIndex) {
            return;
        }

        // we only support one context for entity references right now...
        if (entityContext != XMLEntityHandler.ENTITYREF_IN_CONTENT) {
            return;
        }

        // deferred node expansion
        if (fDeferredDocumentImpl != null) {

            String name = fStringPool.toString(entityName);

            int erChild = fCurrentNodeIndex;
            fCurrentNodeIndex = fDeferredDocumentImpl.getParentNode(erChild, false);

            // should never be true - we should not return here.
            if (fDeferredDocumentImpl.getNodeType(erChild, false) != Node.ENTITY_REFERENCE_NODE)  return;

            erChild = fDeferredDocumentImpl.getLastChild(erChild, false); // first Child of EntityReference
            if (fDocumentTypeIndex != -1) {
                // if we have seen <?xml..> decl then Entity decl was found and 
                // set in textDecl() using fCurrentEntityNode
                if (fCurrentEntityNode  == -1) {
                    // find Entity decl for this EntityReference.
                    int entityDecl = fDeferredDocumentImpl.getLastChild(fDocumentTypeIndex, false);
                    while (entityDecl != -1) {
                        if (fDeferredDocumentImpl.getNodeType(entityDecl, false) == Node.ENTITY_NODE
                            && fDeferredDocumentImpl.getNodeNameString(entityDecl, false).equals(name)) // string compare...
                        {
                            break;
                        }
                        entityDecl = fDeferredDocumentImpl.getPrevSibling(entityDecl, false);
                    }
                    fCurrentEntityNode = entityDecl;
                }
                 if (fCurrentEntityNode != -1
                    && fDeferredDocumentImpl.getLastChild(fCurrentEntityNode, false) == -1) {
                    // found entityDecl with same name as this reference
                    // AND it doesn't have any children.

                    // we don't need to iterate, because the whole structure
                    // should already be connected to the 1st child.
                    fDeferredDocumentImpl.setAsLastChild(fCurrentEntityNode, erChild);
                }
                 // done with current entity reference.
                 // reset values
                 fCurrentEntityNode  = -1; 
                 fCurrentEntityName = -1;
            }

        }

        // full node expansion
        else {

            Node erNode = fCurrentElementNode;//fCurrentElementNode.getParentNode();
            fCurrentElementNode = erNode.getParentNode();

            // if necessary populate the related entity now
            if (fDocumentImpl != null) {
                EntityReferenceImpl xer = (EntityReferenceImpl) erNode;

                NamedNodeMap entities = fDocumentType.getEntities();
                String name = fStringPool.toString(entityName);
                Node entityNode = entities.getNamedItem(name);

                // simply return here if there is no entity for
                // the reference or if the entity is already populated.
                if (entityNode == null || entityNode.hasChildNodes()) {
                    return;
                }

                EntityImpl entity = (EntityImpl) entityNode;
                for (Node child = erNode.getFirstChild();
                     child != null;
                     child = child.getNextSibling()) {
                    Node childClone = child.cloneNode(true);
                    entity.appendChild(childClone);
                }
            }
        }

    } // endEntityReference(int,int,int)

    //
    // DTDValidator.EventHandler methods
    //

    /**
     *  This function will be called when a &lt;!DOCTYPE...&gt; declaration is
     *  encountered.
     */
    public void startDTD(QName rootElement, int publicId, int systemId)
        throws Exception {

        fInDTD = true;

        // full expansion
        if (fDocumentImpl != null) {
            String rootElementName = fStringPool.toString(rootElement.rawname);
            String publicString = fStringPool.toString(publicId);
            String systemString = fStringPool.toString(systemId);
            fDocumentType = fDocumentImpl.
                createDocumentType(rootElementName, publicString, systemString);
            fDocumentImpl.appendChild(fDocumentType);

            if (fGrammarAccess) {
                Element schema = fDocument.createElement("schema");
                // REVISIT: What should the namespace be? -Ac
                schema.setAttribute("xmlns", SchemaSymbols.URI_SCHEMAFORSCHEMA);
                ((AttrImpl)schema.getAttributeNode("xmlns")).setSpecified(false);
                schema.setAttribute("finalDefault", "");
                ((AttrImpl)schema.getAttributeNode("finalDefault")).setSpecified(false);
                schema.setAttribute("exactDefault", "");
                ((AttrImpl)schema.getAttributeNode("exactDefault")).setSpecified(false);
                fDocumentType.appendChild(schema);
                fCurrentElementNode = schema;
            }
        }

        // deferred expansion
        else if (fDeferredDocumentImpl != null) {
            fDocumentTypeIndex =
                fDeferredDocumentImpl.
                    createDocumentType(rootElement.rawname, publicId, systemId);
            fDeferredDocumentImpl.appendChild(fDocumentIndex, fDocumentTypeIndex);

            if (fGrammarAccess) {
                int handle = fAttrList.startAttrList();
                fAttrList.addAttr(
                    fStringPool.addSymbol("xmlns"),
                    fStringPool.addString(SchemaSymbols.URI_SCHEMAFORSCHEMA),
                    fStringPool.addSymbol("CDATA"),
                    false,
                    false); // search
                fAttrList.addAttr(
                    fStringPool.addSymbol("finalDefault"),
                    fStringPool.addString(""),
                    fStringPool.addSymbol("CDATA"),
                    false,
                    false); // search
                fAttrList.addAttr(
                    fStringPool.addSymbol("exactDefault"),
                    fStringPool.addString(""),
                    fStringPool.addSymbol("CDATA"),
                    false,
                    false); // search
                fAttrList.endAttrList();
                int schemaIndex = fDeferredDocumentImpl.createElement(fStringPool.addSymbol("schema"), fAttrList, handle);
                // REVISIT: What should the namespace be? -Ac
                fDeferredDocumentImpl.appendChild(fDocumentTypeIndex, schemaIndex);
                fCurrentNodeIndex = schemaIndex;
            }
        }

    } // startDTD(int,int,int)
    
    /**
     * Supports DOM Level 2 internalSubset additions.
     * Called when the internal subset is completely scanned.
     */
    public  void internalSubset(int internalSubset) {
        
        //System.out.println("internalSubset callback:"+fStringPool.toString(internalSubset));
        
        // full expansion
        if (fDocumentImpl != null && fDocumentType != null) {
            ((DocumentTypeImpl)fDocumentType).setInternalSubset(fStringPool.toString(internalSubset));
        }

        // deferred expansion
        else if (fDeferredDocumentImpl != null) {
            fDeferredDocumentImpl.setInternalSubset(fDocumentTypeIndex, internalSubset);
        }
        
    }
    

    /**
     *  This function will be called at the end of the DTD.
     */
    public void endDTD() throws Exception {

        fInDTD = false;

        if (fGrammarAccess) {
            if (fDocumentImpl != null) {
                fCurrentElementNode = fDocumentImpl;
            }
            else if (fDeferredDocumentImpl != null) {
                fCurrentNodeIndex = 0;
            }
        }

    } // endDTD()

    /**
     * &lt;!ELEMENT Name contentspec&gt;
     */
    public void elementDecl(QName elementDecl, 
                            int contentSpecType, 
                            int contentSpecIndex,
                            XMLContentSpec.Provider contentSpecProvider) throws Exception {

        if (DEBUG_ATTLIST_DECL) {
            String contentModel = XMLContentSpec.toString(contentSpecProvider, fStringPool, contentSpecIndex);
            System.out.println("elementDecl(" + fStringPool.toString(elementDecl.rawname) + ", " +
                                                contentModel + ")");
        }

        //
        // Create element declaration
        //
        if (fGrammarAccess) {

            if (fDeferredDocumentImpl != null) {

                //
                // Build element
                //

                // get element declaration; create if necessary
                int schemaIndex = getLastChildElement(fDocumentTypeIndex, "schema");
                String elementName = fStringPool.toString(elementDecl.rawname);
                int elementIndex = getLastChildElement(schemaIndex, "element", "name", elementName);
                if (elementIndex == -1) {
                    int handle = fAttrList.startAttrList();
                    fAttrList.addAttr(
                        fStringPool.addSymbol("name"),
                        fStringPool.addString(elementName),
                        fStringPool.addSymbol("NMTOKEN"),
                        true,
                        false); // search
                    fAttrList.addAttr(
                        fStringPool.addSymbol("minOccurs"), // name
                        fStringPool.addString("1"), // value
                        fStringPool.addSymbol("NMTOKEN"), // type
                        false, // specified
                        false); // search
                    fAttrList.addAttr(
                        fStringPool.addSymbol("nullable"), // name
                        fStringPool.addString("false"), // value
                        fStringPool.addSymbol("ENUMERATION"), // type
                        false, // specified
                        false); // search
                    fAttrList.addAttr(
                        fStringPool.addSymbol("abstract"), // name
                        fStringPool.addString("false"), // value
                        fStringPool.addSymbol("ENUMERATION"), // type
                        false, // specified
                        false); // search
                    fAttrList.addAttr(
                        fStringPool.addSymbol("final"), // name
                        fStringPool.addString("false"), // value
                        fStringPool.addSymbol("ENUMERATION"), // type
                        false, // specified
                        false); // search
                    fAttrList.endAttrList();
                    elementIndex = fDeferredDocumentImpl.createElement(fStringPool.addSymbol("element"), fAttrList, handle);
                    fDeferredDocumentImpl.appendChild(schemaIndex, elementIndex);
                }

                //
                // Build content model
                //

                // get type element; create if necessary
                int typeIndex = getLastChildElement(elementIndex, "complexType");
                if (typeIndex == -1 && contentSpecType != XMLElementDecl.TYPE_MIXED_SIMPLE) {
                    typeIndex = fDeferredDocumentImpl.createElement(fStringPool.addSymbol("complexType"), null, -1);
                    // REVISIT: Check for type redeclaration? -Ac
                    fDeferredDocumentImpl.insertBefore(elementIndex, typeIndex, getFirstChildElement(elementIndex));
                }

                // create models
                switch (contentSpecType) {
                    case XMLElementDecl.TYPE_EMPTY: {
                        int attributeIndex = fDeferredDocumentImpl.createAttribute(fStringPool.addSymbol("content"), fStringPool.addString("empty"), true);
                        fDeferredDocumentImpl.setAttributeNode(typeIndex, attributeIndex);
                        break;
                    }
                    case XMLElementDecl.TYPE_ANY: {
                        int anyIndex = fDeferredDocumentImpl.createElement(fStringPool.addSymbol("any"), null, -1);
                        fDeferredDocumentImpl.insertBefore(typeIndex, anyIndex, getFirstChildElement(typeIndex));
                        break;
                    }
                    case XMLElementDecl.TYPE_MIXED_SIMPLE: {
                        XMLContentSpec contentSpec = new XMLContentSpec();
                        contentSpecProvider.getContentSpec(contentSpecIndex, contentSpec);
                        contentSpecIndex = contentSpec.value;
                        if (contentSpecIndex == -1) {
                            int attributeIndex = fDeferredDocumentImpl.createAttribute(fStringPool.addSymbol("type"), fStringPool.addString("string"), true);
                            fDeferredDocumentImpl.setAttributeNode(elementIndex, attributeIndex);
                        }
                        else {
                            if (typeIndex == -1) {
                                typeIndex = fDeferredDocumentImpl.createElement(fStringPool.addSymbol("complexType"), null, -1);
                                // REVISIT: Check for type redeclaration? -Ac
                                fDeferredDocumentImpl.insertBefore(elementIndex, typeIndex, getFirstChildElement(elementIndex));
                            }
                            int attributeIndex = fDeferredDocumentImpl.createAttribute(fStringPool.addSymbol("content"), fStringPool.addString("mixed"), true);
                            fDeferredDocumentImpl.setAttributeNode(typeIndex, attributeIndex);
                            int handle = fAttrList.startAttrList();
                            fAttrList.addAttr(
                                fStringPool.addSymbol("minOccurs"),
                                fStringPool.addString("0"),
                                fStringPool.addSymbol("NMTOKEN"),
                                true,
                                false); // search
                            fAttrList.addAttr(
                                fStringPool.addSymbol("maxOccurs"),
                                fStringPool.addString("unbounded"),
                                fStringPool.addSymbol("CDATA"),
                                true,
                                false); // search
                            fAttrList.endAttrList();
                            int choiceIndex = fDeferredDocumentImpl.createElement(fStringPool.addSymbol("choice"), fAttrList, handle);
                            fDeferredDocumentImpl.appendChild(typeIndex, choiceIndex);
                            while (contentSpecIndex != -1) {

                                // get node
                                contentSpecProvider.getContentSpec(contentSpecIndex, contentSpec);
                                int type  = contentSpec.type;
                                int left  = contentSpec.value;
                                int right = contentSpec.otherValue;

                                // if leaf, skip "#PCDATA" and stop
                                if (type == XMLContentSpec.CONTENTSPECNODE_LEAF) {
                                    break;
                                }

                                // add right hand leaf
                                contentSpecProvider.getContentSpec(right, contentSpec);
                                handle = fAttrList.startAttrList();
                                fAttrList.addAttr(
                                    fStringPool.addSymbol("ref"),
                                    fStringPool.addString(fStringPool.toString(contentSpec.value)),
                                    fStringPool.addSymbol("NMTOKEN"),
                                    true,
                                    false); //search
                                fAttrList.endAttrList();
                                int rightIndex = fDeferredDocumentImpl.createElement(fStringPool.addSymbol("element"), fAttrList, handle);
                                int refIndex = getFirstChildElement(choiceIndex);
                                fDeferredDocumentImpl.insertBefore(choiceIndex, rightIndex, refIndex);

                                // go to next node
                                contentSpecIndex = left;
                            }
                        }
                        break;
                    }
                    case XMLElementDecl.TYPE_CHILDREN: {
                        int attributeIndex = fDeferredDocumentImpl.createAttribute(fStringPool.addSymbol("content"), fStringPool.addString("elementOnly"), true);
                        fDeferredDocumentImpl.setAttributeNode(typeIndex, attributeIndex);
                        int children = createChildren(contentSpecProvider,
                                                      contentSpecIndex,
                                                      new XMLContentSpec(),
                                                      fDeferredDocumentImpl,
                                                      -1);
                        fDeferredDocumentImpl.insertBefore(typeIndex, children, getFirstChildElement(typeIndex));
                        break;
                    }
                }

            } // if defer-node-expansion

            else if (fDocumentImpl != null) {

                //
                // Build element
                //

                // get element declaration; create if necessary
                Element schema = XUtil.getLastChildElement(fDocumentType, "schema");
                String elementName = fStringPool.toString(elementDecl.rawname);
                Element element = XUtil.getLastChildElement(schema, "element", "name", elementName);
                if (element == null) {
                    element = fDocumentImpl.createElement("element");
                    element.setAttribute("name", elementName);
                    element.setAttribute("minOccurs", "1");
                    ((AttrImpl)element.getAttributeNode("minOccurs")).setSpecified(false);
                    element.setAttribute("nullable", "false");
                    ((AttrImpl)element.getAttributeNode("nullable")).setSpecified(false);
                    element.setAttribute("abstract", "false");
                    ((AttrImpl)element.getAttributeNode("abstract")).setSpecified(false);
                    element.setAttribute("final", "false");
                    ((AttrImpl)element.getAttributeNode("final")).setSpecified(false);
                    schema.appendChild(element);
                }

                //
                // Build content model
                //

                // get type element; create if necessary
                Element type = XUtil.getLastChildElement(element, "complexType");
                if (type == null && contentSpecType != XMLElementDecl.TYPE_MIXED_SIMPLE) {
                    type = fDocumentImpl.createElement("complexType");
                    // REVISIT: Check for type redeclaration? -Ac
                    element.insertBefore(type, XUtil.getFirstChildElement(element));
                }

                // create models
                switch (contentSpecType) {
                    case XMLElementDecl.TYPE_EMPTY: {
                        type.setAttribute("content", "empty");
                        break;
                    }
                    case XMLElementDecl.TYPE_ANY: {
                        Element any = fDocumentImpl.createElement("any");
                        type.insertBefore(any, XUtil.getFirstChildElement(type));
                        break;
                    }
                    case XMLElementDecl.TYPE_MIXED_SIMPLE: {
                        XMLContentSpec contentSpec = new XMLContentSpec();
                        contentSpecProvider.getContentSpec(contentSpecIndex, contentSpec);
                        contentSpecIndex = contentSpec.value;
                        if (contentSpecIndex == -1) {
                            element.setAttribute("type", "string");
                        }
                        else {
                            if (type == null) {
                                type = fDocumentImpl.createElement("complexType");
                                // REVISIT: Check for type redeclaration? -Ac
                                element.insertBefore(type, XUtil.getFirstChildElement(element));
                            }
                            type.setAttribute("content", "mixed");
                            Element choice = fDocumentImpl.createElement("choice");
                            choice.setAttribute("minOccurs", "0");
                            choice.setAttribute("maxOccurs", "unbounded");
                            type.appendChild(choice);
                            while (contentSpecIndex != -1) {

                                // get node
                                contentSpecProvider.getContentSpec(contentSpecIndex, contentSpec);
                                int cstype  = contentSpec.type;
                                int csleft  = contentSpec.value;
                                int csright = contentSpec.otherValue;

                                // if leaf, skip "#PCDATA" and stop
                                if (cstype == XMLContentSpec.CONTENTSPECNODE_LEAF) {
                                    break;
                                }

                                // add right hand leaf
                                contentSpecProvider.getContentSpec(csright, contentSpec);
                                Element right = fDocumentImpl.createElement("element");
                                right.setAttribute("ref", fStringPool.toString(contentSpec.value));
                                Element ref = XUtil.getFirstChildElement(choice);
                                choice.insertBefore(right, ref);

                                // go to next node
                                contentSpecIndex = csleft;
                            }
                        }
                        break;
                    }
                    case XMLElementDecl.TYPE_CHILDREN: {
                        type.setAttribute("content", "elementOnly");
                        Element children = createChildren(contentSpecProvider,
                                                          contentSpecIndex,
                                                          new XMLContentSpec(),
                                                          fDocumentImpl,
                                                          null);
                        type.insertBefore(children, XUtil.getFirstChildElement(type));
                        break;
                    }
                }

            } // if NOT defer-node-expansion

        } // if grammar-access

    } // elementDecl(int,String)

    /**
     * &lt;!ATTLIST Name AttDef&gt;
     */
    public void attlistDecl(QName elementDecl, QName attributeDecl, 
                            int attType, boolean attList, String enumString,
                            int attDefaultType, int attDefaultValue)
        throws Exception {

        if (DEBUG_ATTLIST_DECL) {
            System.out.println("attlistDecl(" + fStringPool.toString(elementDecl.rawname) + ", " +
                                                fStringPool.toString(attributeDecl.rawname) + ", " +
                                                fStringPool.toString(attType) + ", " +
                                                enumString + ", " +
                                                fStringPool.toString(attDefaultType) + ", " +
                                                fStringPool.toString(attDefaultValue) + ")");
        }

        // deferred expansion
        if (fDeferredDocumentImpl != null) {

            // get the default value
            if (attDefaultValue != -1) {
                if (DEBUG_ATTLIST_DECL) {
                    System.out.println("  adding default attribute value: "+
                                       fStringPool.toString(attDefaultValue));
                }

                // get element definition
                int elementDefIndex  = fDeferredDocumentImpl.lookupElementDefinition(elementDecl.rawname);

                // create element definition if not already there
                if (elementDefIndex == -1) {
                    elementDefIndex = fDeferredDocumentImpl.createElementDefinition(elementDecl.rawname);
                    fDeferredDocumentImpl.appendChild(fDocumentTypeIndex, elementDefIndex);
                }

                // add default attribute
                int attrIndex =
                   fDeferredDocumentImpl.createAttribute(attributeDecl.rawname,
                                                         attributeDecl.uri,
                                                         attDefaultValue,
                                                         false);
                fDeferredDocumentImpl.appendChild(elementDefIndex, attrIndex);

            }

            //
            // Create attribute declaration
            //
            if (fGrammarAccess) {

                // get element declaration; create it if necessary
                int schemaIndex = getLastChildElement(fDocumentTypeIndex, "schema");
                String elementName = fStringPool.toString(elementDecl.rawname);
                int elementIndex = getLastChildElement(schemaIndex, "element", "name", elementName);
                if (elementIndex == -1) {
                    int handle = fAttrList.startAttrList();
                    fAttrList.addAttr(
                        fStringPool.addSymbol("name"),
                        fStringPool.addString(elementName),
                        fStringPool.addSymbol("NMTOKEN"),
                        true,
                        false); //search
                    fAttrList.endAttrList();
                    elementIndex = fDeferredDocumentImpl.createElement(fStringPool.addSymbol("element"), fAttrList, handle);
                    fDeferredDocumentImpl.appendChild(schemaIndex, elementIndex);
                }

                // get type element; create it if necessary
                int typeIndex = getLastChildElement(elementIndex, "complexType");
                if (typeIndex == -1) {
                    typeIndex = fDeferredDocumentImpl.createElement(fStringPool.addSymbol("complexType"), null, -1);
                    fDeferredDocumentImpl.insertBefore(elementIndex, typeIndex, getLastChildElement(elementIndex));
                }

                // create attribute and set its attributes
                String attributeName = fStringPool.toString(attributeDecl.rawname);
                int attributeIndex = getLastChildElement(elementIndex, "attribute", "name", attributeName);
                if (attributeIndex == -1) {
                    int handle = fAttrList.startAttrList();
                    fAttrList.addAttr(
                        fStringPool.addSymbol("name"),
                        fStringPool.addString(attributeName),
                        fStringPool.addSymbol("NMTOKEN"),
                        true,
                        false); // search
                    fAttrList.addAttr(
                        fStringPool.addSymbol("maxOccurs"),
                        fStringPool.addString("1"),
                        fStringPool.addSymbol("CDATA"),
                        false,
                        false); // search
                    fAttrList.endAttrList();
                    attributeIndex = fDeferredDocumentImpl.createElement(fStringPool.addSymbol("attribute"), fAttrList, handle);
                    fDeferredDocumentImpl.appendChild(typeIndex, attributeIndex);

                    // attribute type: CDATA, ENTITY, ... , NMTOKENS; ENUMERATION
                    if (attType == XMLAttributeDecl.TYPE_ENUMERATION) {
                        handle = fAttrList.startAttrList();
                        fAttrList.addAttr(
                            fStringPool.addSymbol("base"),
                            fStringPool.addString("NMTOKEN"),
                            fStringPool.addSymbol("NMTOKEN"),
                            true,
                            false); // search
                        fAttrList.endAttrList();
                        int simpleTypeIndex = fDeferredDocumentImpl.createElement(fStringPool.addSymbol("simpleType"), fAttrList, handle);
                        fDeferredDocumentImpl.appendChild(attributeIndex, simpleTypeIndex);
                        String tokenizerString = enumString.substring(1, enumString.length() - 1);
                        StringTokenizer tokenizer = new StringTokenizer(tokenizerString, "|");
                        while (tokenizer.hasMoreTokens()) {
                            handle = fAttrList.startAttrList();
                            fAttrList.addAttr(
                                fStringPool.addSymbol("value"),
                                fStringPool.addString(tokenizer.nextToken()),
                                fStringPool.addSymbol("CDATA"),
                                true,
                                false); // search
                            fAttrList.endAttrList();
                            int enumerationIndex = fDeferredDocumentImpl.createElement(fStringPool.addSymbol("enumeration"), fAttrList, handle);
                            fDeferredDocumentImpl.appendChild(simpleTypeIndex, enumerationIndex);
                        }
                    }
                    else {
                        int typeNameIndex = -1;
                        switch (attType) {
                            case XMLAttributeDecl.TYPE_ENTITY: {
                                typeNameIndex = fStringPool.addString(attList?"ENTITIES":"ENTITY");
                                break;
                            }
                            case XMLAttributeDecl.TYPE_ID: {
                                typeNameIndex = fStringPool.addString("ID");
                                break;
                            }
                            case XMLAttributeDecl.TYPE_IDREF: {
                                typeNameIndex = fStringPool.addString(attList?"IDREFS":"IDREF");
                                break;
                            }
                            case XMLAttributeDecl.TYPE_NMTOKEN: {
                                typeNameIndex = fStringPool.addString(attList?"NMTOKENS":"NMTOKEN");
                                break;
                            }
                            case XMLAttributeDecl.TYPE_NOTATION: {
                                typeNameIndex = fStringPool.addString("NOTATION");
                                break;
                            }
                            case XMLAttributeDecl.TYPE_CDATA: 
                            default: {
                                typeNameIndex = fStringPool.addString("string");
                                break;
                            }
                        }
                        int attrIndex = fDeferredDocumentImpl.createAttribute(fStringPool.addSymbol("type"), typeNameIndex, true);
                        fDeferredDocumentImpl.setAttributeNode(attributeIndex, attrIndex);
                    }

                    // attribute default type: #IMPLIED, #REQUIRED, #FIXED
                    boolean fixed = false;
                    switch (attDefaultType) {
                        case XMLAttributeDecl.DEFAULT_TYPE_REQUIRED: {
                            int useAttrIndex = fDeferredDocumentImpl.createAttribute(fStringPool.addSymbol("use"), fStringPool.addString("required"), true);
                            fDeferredDocumentImpl.setAttributeNode(attributeIndex, useAttrIndex);
                            break;
                        }
                        case XMLAttributeDecl.DEFAULT_TYPE_FIXED: {
                            fixed = true;
                            int useAttrIndex = fDeferredDocumentImpl.createAttribute(fStringPool.addSymbol("use"), fStringPool.addString("fixed"), true);
                            fDeferredDocumentImpl.setAttributeNode(attributeIndex, useAttrIndex);
                            break;
                        }
                    }

                    // attribute default value
                    if (attDefaultValue != -1) {
                        if (!fixed) {
                            int useAttrIndex = fDeferredDocumentImpl.createAttribute(fStringPool.addSymbol("use"), fStringPool.addString("default"), true);
                            fDeferredDocumentImpl.setAttributeNode(attributeIndex, useAttrIndex);
                        }
                        int valueAttrIndex = fDeferredDocumentImpl.createAttribute(fStringPool.addSymbol("value"), attDefaultValue, true);
                        fDeferredDocumentImpl.setAttributeNode(attributeIndex, valueAttrIndex);
                    }
                }
            }
        }

        // full expansion
        else if (fDocumentImpl != null) {

            // get the default value
            if (attDefaultValue != -1) {
                if (DEBUG_ATTLIST_DECL) {
                    System.out.println("  adding default attribute value: "+
                                       fStringPool.toString(attDefaultValue));
                }

                // get element name
                String elementName = fStringPool.toString(elementDecl.rawname);

                // get element definition node
                NamedNodeMap elements = ((DocumentTypeImpl)fDocumentType).getElements();
                ElementDefinitionImpl elementDef = (ElementDefinitionImpl)elements.getNamedItem(elementName);
                if (elementDef == null) {
                    elementDef = fDocumentImpl.createElementDefinition(elementName);
                    ((DocumentTypeImpl)fDocumentType).getElements().setNamedItem(elementDef);
                }

                // REVISIT: Check for uniqueness of element name? -Ac

                // get attribute name and value index
                String attrName      = fStringPool.toString(attributeDecl.rawname);
                String attrValue     = fStringPool.toString(attDefaultValue);

                // create attribute and set properties
                boolean nsEnabled = false;
                try { nsEnabled = getNamespaces(); }
                catch (SAXException s) {}
                AttrImpl attr;
                if (nsEnabled) {
		    String namespaceURI = fStringPool.toString(attributeDecl.uri);
		    // DOM Level 2 wants all namespace declaration attributes
		    // to be bound to "http://www.w3.org/2000/xmlns/"
		    // So as long as the XML parser doesn't do it, it needs to
		    // done here.
		    String prefix = fStringPool.toString(attributeDecl.prefix);
		    if (namespaceURI == null || namespaceURI.length() == 0) {
			if (prefix != null) {
			    if (prefix.equals("xmlns")) {
				namespaceURI = "http://www.w3.org/2000/xmlns/";
			    }
			} else if (attrName.equals("xmlns")) {
			    namespaceURI = "http://www.w3.org/2000/xmlns/";
			}
		    }
                    attr = (AttrImpl)fDocumentImpl.createAttributeNS(namespaceURI,attrName);
                }
                else{
                    attr = (AttrImpl)fDocumentImpl.createAttribute(attrName);
                }
                attr.setValue(attrValue);
                attr.setSpecified(false);

                // add default attribute to element definition
                if(nsEnabled){
                    elementDef.getAttributes().setNamedItemNS(attr);
                }
                else{
                    elementDef.getAttributes().setNamedItem(attr);
                }
            }

            //
            // Create attribute declaration
            //
            try {
            if (fGrammarAccess) {

                // get element declaration; create it if necessary
                Element schema = XUtil.getLastChildElement(fDocumentType, "schema");
                String elementName = fStringPool.toString(elementDecl.rawname);
                Element element = XUtil.getLastChildElement(schema, "element", "name", elementName);
                if (element == null) {
                    element = fDocumentImpl.createElement("element");
                    element.setAttribute("name", elementName);
                    schema.appendChild(element);
                }

                // get type element; create it if necessary
                Element type = XUtil.getLastChildElement(element, "complexType");
                if (type == null) {
                    type = fDocumentImpl.createElement("complexType");
                    element.insertBefore(type, XUtil.getLastChildElement(element));
                }

                // create attribute and set its attributes
                String attributeName = fStringPool.toString(attributeDecl.rawname);
                Element attribute = XUtil.getLastChildElement(element, "attribute", "name", attributeName);
                if (attribute == null) {
                    attribute = fDocumentImpl.createElement("attribute");
                    attribute.setAttribute("name", attributeName);
                    attribute.setAttribute("maxOccurs", "1");
                    ((AttrImpl)attribute.getAttributeNode("maxOccurs")).setSpecified(false);
                    type.appendChild(attribute);

                    // attribute type: CDATA, ENTITY, ... , NMTOKENS; ENUMERATION
                    if (attType == XMLAttributeDecl.TYPE_ENUMERATION) {
                        Element simpleType = fDocumentImpl.createElement("simpleType");
                        simpleType.setAttribute("base", "NMTOKEN");
                        attribute.appendChild(simpleType);
                        String tokenizerString = enumString.substring(1, enumString.length() - 1);
                        StringTokenizer tokenizer = new StringTokenizer(tokenizerString, "|");
                        while (tokenizer.hasMoreTokens()) {
                            Element enumeration = fDocumentImpl.createElement("enumeration");
                            enumeration.setAttribute("value", tokenizer.nextToken());
                            simpleType.appendChild(enumeration);
                        }
                    }
                    else {
                        String typeName = null;
                        switch (attType) {
                            case XMLAttributeDecl.TYPE_ENTITY: {
                                typeName = attList ? "ENTITIES" : "ENTITY";
                                break;
                            }
                            case XMLAttributeDecl.TYPE_ID: {
                                typeName = "ID";
                                break;
                            }
                            case XMLAttributeDecl.TYPE_IDREF: {
                                typeName = attList ? "IDREFS" : "IDREF";
                                break;
                            }
                            case XMLAttributeDecl.TYPE_NMTOKEN: {
                                typeName = attList ? "NMTOKENS" : "NMTOKEN";
                                break;
                            }
                            case XMLAttributeDecl.TYPE_NOTATION: {
                                typeName = "NOTATION";
                                break;
                            }
                            case XMLAttributeDecl.TYPE_CDATA: 
                            default: {
                                typeName = "string";
                                break;
                            }
                        }
                        attribute.setAttribute("type", typeName);
                    }

                    // attribute default type: #IMPLIED, #REQUIRED, #FIXED
                    boolean fixed = false;
                    switch (attDefaultType) {
                        case XMLAttributeDecl.DEFAULT_TYPE_REQUIRED: {
                            attribute.setAttribute("use", "required");
                            break;
                        }
                        case XMLAttributeDecl.DEFAULT_TYPE_FIXED: {
                            attribute.setAttribute("use", "fixed");
                            fixed = true;
                            break;
                        }
                    }

                    // attribute default value
                    if (attDefaultValue != -1) {
                        if (!fixed) {
                            attribute.setAttribute("use", "default");
                        }
                        attribute.setAttribute("value", fStringPool.toString(attDefaultValue));
                    }
                }
            }
            }
            catch (Exception e) {
                e.printStackTrace(System.err);
            }

        } // if NOT defer-node-expansion

    } // attlistDecl(int,int,int,String,int,int)

    /**
     * &lt;!ENTITY % Name EntityValue&gt; (internal)
     */
    public void internalPEDecl(int entityNameIndex, int entityValueIndex) throws Exception {
        if (fDeferredDocumentImpl != null) {
            if (fGrammarAccess) {
                StringBuffer str = new StringBuffer();
                str.append("<!ENTITY % ");
                str.append(fStringPool.toString(entityNameIndex));
                str.append(" \"");
                str.append(fStringPool.toString(entityValueIndex));
                str.append("\">");
                int commentIndex = fStringPool.addString(str.toString());
                int internalPEEntityIndex = fDeferredDocumentImpl.createComment(commentIndex);
                int schemaIndex = getFirstChildElement(fDocumentTypeIndex, "schema");
                fDeferredDocumentImpl.appendChild(schemaIndex, internalPEEntityIndex);
            }
        }
        else if (fDocumentImpl != null) {
            if (fGrammarAccess) {
                StringBuffer str = new StringBuffer();
                str.append("<!ENTITY % ");
                str.append(fStringPool.toString(entityNameIndex));
                str.append(" \"");
                str.append(fStringPool.orphanString(entityValueIndex));
                str.append("\">");
                Node internalPEEntity = fDocumentImpl.createComment(str.toString());
                Node schema = XUtil.getFirstChildElement(fDocumentType, "schema");
                schema.appendChild(internalPEEntity);
            }
        }
        else {
            fStringPool.orphanString(entityValueIndex);
        }
    }

    /**
     * &lt;!ENTITY % Name ExternalID>                (external)
     */
    public void externalPEDecl(int entityNameIndex, int publicIdIndex, int systemIdIndex) throws Exception {
        if (fDeferredDocumentImpl != null) {
            if (fGrammarAccess) {
                StringBuffer str = new StringBuffer();
                str.append("<!ENTITY ");
                str.append(fStringPool.toString(entityNameIndex));
                str.append(' ');
                if (publicIdIndex != -1) {
                    str.append("PUBLIC \"");
                    str.append(fStringPool.toString(publicIdIndex));
                    str.append('"');
                    if (systemIdIndex != -1) {
                        str.append(" \"");
                        str.append(fStringPool.toString(systemIdIndex));
                        str.append('"');
                    }
                }
                else if (systemIdIndex != -1) {
                    str.append("SYSTEM \"");
                    str.append(fStringPool.toString(systemIdIndex));
                    str.append('"');
                }
                str.append('>');
                int commentIndex = fStringPool.addString(str.toString());
                int externalPEEntityIndex = fDeferredDocumentImpl.createComment(commentIndex);
                int schemaIndex = getFirstChildElement(fDocumentTypeIndex, "schema");
                fDeferredDocumentImpl.appendChild(schemaIndex, externalPEEntityIndex);
            }
        }
        else if (fDocumentImpl != null) {
            if (fGrammarAccess) {
                StringBuffer str = new StringBuffer();
                str.append("<!ENTITY ");
                str.append(fStringPool.toString(entityNameIndex));
                str.append(' ');
                if (publicIdIndex != -1) {
                    str.append("PUBLIC \"");
                    str.append(fStringPool.toString(publicIdIndex));
                    str.append('"');
                    if (systemIdIndex != -1) {
                        str.append(" \"");
                        str.append(fStringPool.toString(systemIdIndex));
                        str.append('"');
                    }
                }
                else if (systemIdIndex != -1) {
                    str.append("SYSTEM \"");
                    str.append(fStringPool.toString(systemIdIndex));
                    str.append('"');
                }
                str.append('>');
                Node externalPEEntity = fDocumentImpl.createComment(str.toString());
                Node schema = XUtil.getFirstChildElement(fDocumentType, "schema");
                schema.appendChild(externalPEEntity);
            }
        }
    }

    /**
     * &lt;!ENTITY Name EntityValue&gt; (internal)
     */
    public void internalEntityDecl(int entityNameIndex, int entityValueIndex)
        throws Exception {

        // deferred expansion
        if (fDeferredDocumentImpl != null) {

            if (fDocumentTypeIndex == -1) return; //revisit: should never happen. Exception?

            //revisit: how to check if entity was already declared.
            // XML spec says that 1st Entity decl is binding.

            int newEntityIndex = fDeferredDocumentImpl.createEntity(entityNameIndex, -1, -1, -1);
            fDeferredDocumentImpl.appendChild(fDocumentTypeIndex, newEntityIndex);

            // REVISIT: Entities were removed from latest working draft. -Ac
            // create internal entity declaration
            if (fGrammarAccess) {
                StringBuffer str = new StringBuffer();
                str.append("<!ENTITY ");
                str.append(fStringPool.toString(entityNameIndex));
                str.append(" \"");
                str.append(fStringPool.toString(entityValueIndex));
                str.append("\">");
                int commentIndex = fStringPool.addString(str.toString());
                int textEntityIndex = fDeferredDocumentImpl.createComment(commentIndex);
                int schemaIndex = getFirstChildElement(fDocumentTypeIndex, "schema");
                fDeferredDocumentImpl.appendChild(schemaIndex, textEntityIndex);
            }
        }

        // full expansion
        else if (fDocumentImpl != null) {
            if (fDocumentType == null) return; //revisit: should never happen. Exception?

            //revisit: how to check if entity was already declared.
            // XML spec says that 1st Entity decl is binding.

            String entityName = fStringPool.toString(entityNameIndex);

            Entity entity = fDocumentImpl.createEntity(entityName);
            fDocumentType.getEntities().setNamedItem(entity);

            // REVISIT: Entities were removed from latest working draft. -Ac
            // create internal entity declaration
            if (fGrammarAccess) {
                StringBuffer str = new StringBuffer();
                str.append("<!ENTITY ");
                str.append(fStringPool.toString(entityNameIndex));
                str.append(" \"");
                str.append(fStringPool.toString(entityValueIndex));
                str.append("\">");
                Node textEntity = fDocumentImpl.createComment(str.toString());
                Node schema = XUtil.getFirstChildElement(fDocumentType, "schema");
                schema.appendChild(textEntity);
            }
        }

    } // internalEntityDecl(int,int)

    /**
     * &lt;!ENTITY Name ExternalID>                (external)
     */
    public void externalEntityDecl(int entityNameIndex, int publicIdIndex, int systemIdIndex)
        throws Exception {

        // deferred expansion
        if (fDeferredDocumentImpl != null) {

            //revisit: how to check if entity was already declared.
            // XML spec says that 1st Entity decl is binding.

            int newEntityIndex = fDeferredDocumentImpl.createEntity(entityNameIndex, publicIdIndex, systemIdIndex, -1);

            fDeferredDocumentImpl.appendChild(fDocumentTypeIndex, newEntityIndex);

            // REVISIT: Entities were removed from latest working draft. -Ac
            // create external entity declaration
            if (fGrammarAccess) {
                StringBuffer str = new StringBuffer();
                str.append("<!ENTITY ");
                str.append(fStringPool.toString(entityNameIndex));
                str.append(' ');
                if (publicIdIndex != -1) {
                    str.append("PUBLIC \"");
                    str.append(fStringPool.toString(publicIdIndex));
                    str.append('"');
                    if (systemIdIndex != -1) {
                        str.append(" \"");
                        str.append(fStringPool.toString(systemIdIndex));
                        str.append('"');
                    }
                }
                else if (systemIdIndex != -1) {
                    str.append("SYSTEM \"");
                    str.append(fStringPool.toString(systemIdIndex));
                    str.append('"');
                }
                str.append('>');
                int commentIndex = fStringPool.addString(str.toString());
                int externalEntityIndex = fDeferredDocumentImpl.createComment(commentIndex);
                int schemaIndex = getFirstChildElement(fDocumentTypeIndex, "schema");
                fDeferredDocumentImpl.appendChild(schemaIndex, externalEntityIndex);
            }
        }

        // full expansion
        else if (fDocumentImpl != null) {

            //revisit: how to check if entity was already declared.
            // XML spec says that 1st Entity decl is binding.

            String entityName = fStringPool.toString(entityNameIndex);
            String publicId = fStringPool.toString(publicIdIndex);
            String systemId = fStringPool.toString(systemIdIndex);

            EntityImpl entity = (EntityImpl)fDocumentImpl.createEntity(entityName);
            if (publicIdIndex != -1) {
                entity.setPublicId(publicId);
            }
            entity.setSystemId(systemId);
            fDocumentType.getEntities().setNamedItem(entity);

            // REVISIT: Entities were removed from latest working draft. -Ac
            // create external entity declaration
            if (fGrammarAccess) {
                StringBuffer str = new StringBuffer();
                str.append("<!ENTITY ");
                str.append(fStringPool.toString(entityNameIndex));
                str.append(' ');
                if (publicIdIndex != -1) {
                    str.append("PUBLIC \"");
                    str.append(fStringPool.toString(publicIdIndex));
                    str.append('"');
                    if (systemIdIndex != -1) {
                        str.append(" \"");
                        str.append(fStringPool.toString(systemIdIndex));
                        str.append('"');
                    }
                }
                else if (systemIdIndex != -1) {
                    str.append("SYSTEM \"");
                    str.append(fStringPool.toString(systemIdIndex));
                    str.append('"');
                }
                str.append('>');
                Node externalEntity = fDocumentImpl.createComment(str.toString());
                Node schema = XUtil.getFirstChildElement(fDocumentType, "schema");
                schema.appendChild(externalEntity);
            }
        }

    } // externalEntityDecl(int,int,int)

    /**
     * &lt;!ENTITY Name ExternalID NDataDecl>      (unparsed)
     */
    public void unparsedEntityDecl(int entityNameIndex,
                                   int publicIdIndex, int systemIdIndex,
                                   int notationNameIndex) throws Exception {

        // deferred expansion
        if (fDeferredDocumentImpl != null) {

            //revisit: how to check if entity was already declared.
            // XML spec says that 1st Entity decl is binding.

            int newEntityIndex = fDeferredDocumentImpl.createEntity(entityNameIndex, publicIdIndex, systemIdIndex, notationNameIndex);

            fDeferredDocumentImpl.appendChild(fDocumentTypeIndex, newEntityIndex);

            // REVISIT: Entities were removed from latest working draft. -Ac
            // add unparsed entity declaration
            if (fGrammarAccess) {
                StringBuffer str = new StringBuffer();
                str.append("<!ENTITY ");
                str.append(fStringPool.toString(entityNameIndex));
                str.append(' ');
                if (publicIdIndex != -1) {
                    str.append("PUBLIC \"");
                    str.append(fStringPool.toString(publicIdIndex));
                    str.append('"');
                    if (systemIdIndex != -1) {
                        str.append(" \"");
                        str.append(fStringPool.toString(systemIdIndex));
                        str.append('"');
                    }
                }
                else if (systemIdIndex != -1) {
                    str.append("SYSTEM \"");
                    str.append(fStringPool.toString(systemIdIndex));
                    str.append('"');
                }
                str.append(" NDATA ");
                str.append(fStringPool.toString(notationNameIndex));
                str.append('>');
                int commentIndex = fStringPool.addString(str.toString());
                int unparsedEntityIndex = fDeferredDocumentImpl.createComment(commentIndex);
                int schemaIndex = getFirstChildElement(fDocumentTypeIndex, "schema");
                fDeferredDocumentImpl.appendChild(schemaIndex, unparsedEntityIndex);
            }
        }

        // full expansion
        else if (fDocumentImpl != null) {

            //revisit: how to check if entity was already declared.
            // XML spec says that 1st Entity decl is binding.

            String entityName = fStringPool.toString(entityNameIndex);
            String publicId = fStringPool.toString(publicIdIndex);
            String systemId = fStringPool.toString(systemIdIndex);
            String notationName = fStringPool.toString(notationNameIndex);

            EntityImpl entity = (EntityImpl)fDocumentImpl.createEntity(entityName);
            if (publicIdIndex != -1) {
                entity.setPublicId(publicId);
            }
            entity.setSystemId(systemId);
            entity.setNotationName(notationName);
            fDocumentType.getEntities().setNamedItem(entity);

            // REVISIT: Entities were removed from latest working draft. -Ac
            // add unparsed entity declaration
            if (fGrammarAccess) {
                StringBuffer str = new StringBuffer();
                str.append("<!ENTITY ");
                str.append(fStringPool.toString(entityNameIndex));
                str.append(' ');
                if (publicIdIndex != -1) {
                    str.append("PUBLIC \"");
                    str.append(fStringPool.toString(publicIdIndex));
                    str.append('"');
                    if (systemIdIndex != -1) {
                        str.append(" \"");
                        str.append(fStringPool.toString(systemIdIndex));
                        str.append('"');
                    }
                }
                else if (systemIdIndex != -1) {
                    str.append("SYSTEM \"");
                    str.append(fStringPool.toString(systemIdIndex));
                    str.append('"');
                }
                str.append(" NDATA ");
                str.append(fStringPool.toString(notationNameIndex));
                str.append('>');
                Node unparsedEntity = fDocumentImpl.createComment(str.toString());
                Node schema = XUtil.getFirstChildElement(fDocumentType, "schema");
                schema.appendChild(unparsedEntity);
            }
        }

    } // unparsedEntityDecl(int,int,int,int)

    /**
     * &lt;!NOTATION Name ExternalId>
     */
    public void notationDecl(int notationNameIndex, int publicIdIndex, int systemIdIndex)
        throws Exception {

        // deferred expansion
        if (fDeferredDocumentImpl != null) {

            //revisit: how to check if entity was already declared.
            // XML spec says that 1st Entity decl is binding.

            int newNotationIndex = fDeferredDocumentImpl.createNotation(notationNameIndex, publicIdIndex, systemIdIndex);

            fDeferredDocumentImpl.appendChild(fDocumentTypeIndex, newNotationIndex);

            // create notation declaration
            if (fGrammarAccess) {
                int schemaIndex = getLastChildElement(fDocumentTypeIndex, "schema");
                String notationName = fStringPool.toString(notationNameIndex);
                int notationIndex = getLastChildElement(schemaIndex, "notation", "name", notationName);
                if (notationIndex == -1) {
                    int handle = fAttrList.startAttrList();
                    fAttrList.addAttr(
                        fStringPool.addSymbol("name"),
                        fStringPool.addString(notationName),
                        fStringPool.addSymbol("NMTOKEN"),
                        true,
                        false); // search
                    if (publicIdIndex != -1) {
                        fAttrList.addAttr(
                            fStringPool.addSymbol("public"),
                            publicIdIndex,
                            fStringPool.addSymbol("CDATA"),
                            true,
                            false); // search
                    }
                    if (systemIdIndex != -1) {
                        fAttrList.addAttr(
                            fStringPool.addSymbol("system"),
                            systemIdIndex,
                            fStringPool.addSymbol("CDATA"),
                            true,
                            false); // search
                    }
                    fAttrList.endAttrList();
                    notationIndex = fDeferredDocumentImpl.createElement(fStringPool.addSymbol("notation"), fAttrList, handle);
                    fDeferredDocumentImpl.appendChild(schemaIndex, notationIndex);
                }
            }
        }

        // full expansion
        else if (fDocumentImpl != null) {

            // REVISIT: how to check if entity was already declared.
            // XML spec says that 1st Entity decl is binding.

            String notationName = fStringPool.toString(notationNameIndex);
            String publicId = fStringPool.toString(publicIdIndex);
            String systemId = fStringPool.toString(systemIdIndex);

            NotationImpl notationImpl = (NotationImpl)fDocumentImpl.createNotation(notationName);
            notationImpl.setPublicId(publicId);
            if (systemIdIndex != -1) {
                notationImpl.setSystemId(systemId);
            }

            fDocumentType.getNotations().setNamedItem(notationImpl);

            // create notation declaration
            if (fGrammarAccess) {
                Element schema = XUtil.getFirstChildElement(fDocumentType, "schema");
                Element notation = XUtil.getFirstChildElement(schema, "notation", "name", notationName);
                if (notation == null) {
                    notation = fDocument.createElement("notation");
                    notation.setAttribute("name", notationName);
                    //notation.setAttribute("export", "true");
                    //((AttrImpl)notation.getAttributeNode("export")).setSpecified(false);
                    if (publicId != null) {
                        notation.setAttribute("public", publicId);
                    }
                    if (systemIdIndex != -1) {
                        notation.setAttribute("system", systemId);
                    }
                    schema.appendChild(notation);
                }
            }
        }

    } // notationDecl(int,int,int)

    //
    // Private methods
    //

    /** Returns the first child element of the specified node. */
    private int getFirstChildElement(int nodeIndex) {
        int childIndex = getLastChildElement(nodeIndex);
        while (childIndex != -1) {
            int prevIndex = getPrevSiblingElement(childIndex);
            if (prevIndex == -1) {
                break;
            }
            childIndex = prevIndex;
        }
        return childIndex;
    }

    /** Returns the first child element of the specified node. */
    private int getFirstChildElement(int nodeIndex, String name) {
        int childIndex = getLastChildElement(nodeIndex);
        if (childIndex != -1) {
            int nameIndex = fStringPool.addSymbol(name);
            while (childIndex != -1) {
                if (fDeferredDocumentImpl.getNodeName(childIndex, false) == nameIndex) {
                    break;
                }
                int prevIndex = getPrevSiblingElement(childIndex);
                childIndex = prevIndex;
            }
        }
        return childIndex;
    }

    /** Returns the last child element of the specified node. */
    private int getLastChildElement(int nodeIndex) {
        int childIndex = fDeferredDocumentImpl.getLastChild(nodeIndex, false);
        while (childIndex != -1) {
            if (fDeferredDocumentImpl.getNodeType(childIndex, false) == Node.ELEMENT_NODE) {
                return childIndex;
            }
            childIndex = fDeferredDocumentImpl.getPrevSibling(childIndex, false);
        }
        return -1;
    }

    /** Returns the previous sibling element of the specified node. */
    private int getPrevSiblingElement(int nodeIndex) {
        int siblingIndex = fDeferredDocumentImpl.getPrevSibling(nodeIndex, false);
        while (siblingIndex != -1) {
            if (fDeferredDocumentImpl.getNodeType(siblingIndex, false) == Node.ELEMENT_NODE) {
                return siblingIndex;
            }
            siblingIndex = fDeferredDocumentImpl.getPrevSibling(siblingIndex, false);
        }
        return -1;
    }

    /** Returns the first child element with the given name. */
    private int getLastChildElement(int nodeIndex, String elementName) {
        int childIndex = getLastChildElement(nodeIndex);
        if (childIndex != -1) {
            while (childIndex != -1) {
                String nodeName = fDeferredDocumentImpl.getNodeNameString(childIndex, false);
                if (nodeName.equals(elementName)) {
                    return childIndex;
                }
                childIndex = getPrevSiblingElement(childIndex);
            }
        }
        return -1;
    }

    /** Returns the next sibling element with the given name. */
    private int getPrevSiblingElement(int nodeIndex, String elementName) {
        int siblingIndex = getPrevSiblingElement(nodeIndex);
        if (siblingIndex != -1) {
            while (siblingIndex != -1) {
                String nodeName = fDeferredDocumentImpl.getNodeNameString(siblingIndex, false);
                if (nodeName.equals(elementName)) {
                    return siblingIndex;
                }
                siblingIndex = getPrevSiblingElement(siblingIndex);
            }
        }
        return -1;
    }

    /** Returns the first child element with the given name. */
    private int getLastChildElement(int nodeIndex, String elemName, String attrName, String attrValue) {
        int childIndex = getLastChildElement(nodeIndex, elemName);
        if (childIndex != -1) {
            while (childIndex != -1) {
                int attrIndex = fDeferredDocumentImpl.getNodeValue(childIndex, false);
                while (attrIndex != -1) {
                    String nodeName = fDeferredDocumentImpl.getNodeNameString(attrIndex, false);
                    if (nodeName.equals(attrName)) {
                        // REVISIT: Do we need to normalize the text? -Ac
                        int textIndex = fDeferredDocumentImpl.getLastChild(attrIndex, false);
                        String nodeValue = fDeferredDocumentImpl.getNodeValueString(textIndex, false);
                        if (nodeValue.equals(attrValue)) {
                            return childIndex;
                        }
                    }
                    attrIndex = fDeferredDocumentImpl.getPrevSibling(attrIndex, false);
                }
                childIndex = getPrevSiblingElement(childIndex, elemName);
            }
        }
        return -1;
    }

    /** Returns the next sibling element with the given name and attribute. */
    private int getPrevSiblingElement(int nodeIndex, String elemName, String attrName, String attrValue) {
        int siblingIndex = getPrevSiblingElement(nodeIndex, elemName);
        if (siblingIndex != -1) {
            int attributeNameIndex = fStringPool.addSymbol(attrName);
            while (siblingIndex != -1) {
                int attrIndex = fDeferredDocumentImpl.getNodeValue(siblingIndex, false);
                while (attrIndex != -1) {
                    int attrValueIndex = fDeferredDocumentImpl.getNodeValue(attrIndex, false);
                    if (attrValue.equals(fStringPool.toString(attrValueIndex))) {
                        return siblingIndex;
                    }
                    attrIndex = fDeferredDocumentImpl.getPrevSibling(attrIndex, false);
                }
                siblingIndex = getPrevSiblingElement(siblingIndex, elemName);
            }
        }
        return -1;
    }

    /**
     * Copies the source tree into the specified place in a destination
     * tree. The source node and its children are appended as children
     * of the destination node.
     * <p>
     * <em>Note:</em> This is an iterative implementation.
     */
    private void copyInto(Node src, int destIndex) throws Exception {

        // for ignorable whitespace features
        boolean domimpl = src != null && src instanceof DocumentImpl;

        // placement variables
        Node start  = src;
        Node parent = src;
        Node place  = src;

        // traverse source tree
        while (place != null) {

            // copy this node
            int nodeIndex = -1;
            short type = place.getNodeType();
            switch (type) {
                case Node.CDATA_SECTION_NODE: {
                    boolean ignorable = domimpl && ((TextImpl)place).isIgnorableWhitespace();
                    nodeIndex = fDeferredDocumentImpl.createCDATASection(fStringPool.addString(place.getNodeValue()), ignorable);
                    break;
                }
                case Node.COMMENT_NODE: {
                    nodeIndex = fDeferredDocumentImpl.createComment(fStringPool.addString(place.getNodeValue()));
                    break;
                }
                case Node.ELEMENT_NODE: {
                    XMLAttrList attrList = null;
                    int handle = -1;
                    NamedNodeMap attrs = place.getAttributes();
                    if (attrs != null) {
                        int length = attrs.getLength();
                        if (length > 0) {
                            handle = fAttrList.startAttrList();
                            for (int i = 0; i < length; i++) {
                                Attr attr = (Attr)attrs.item(i);
                                String attrName = attr.getNodeName();
                                String attrValue = attr.getNodeValue();
                                fAttrList.addAttr(
                                    fStringPool.addSymbol(attrName),
                                    fStringPool.addString(attrValue),
                                    fStringPool.addSymbol("CDATA"), // REVISIT
                                    attr.getSpecified(),
                                    false); // search
                            }
                            fAttrList.endAttrList();
                            attrList = fAttrList;
                        }
                    }
                    nodeIndex = fDeferredDocumentImpl.createElement(fStringPool.addSymbol(place.getNodeName()), attrList, handle);
                    break;
                }
                case Node.ENTITY_REFERENCE_NODE: {
                    nodeIndex = fDeferredDocumentImpl.createEntityReference(fStringPool.addSymbol(place.getNodeName()));
                    break;
                }
                case Node.PROCESSING_INSTRUCTION_NODE: {
                    nodeIndex = fDeferredDocumentImpl.createProcessingInstruction(fStringPool.addSymbol(place.getNodeName()), fStringPool.addString(place.getNodeValue()));
                    break;
                }
                case Node.TEXT_NODE: {
                    boolean ignorable = domimpl && ((TextImpl)place).isIgnorableWhitespace();
                    nodeIndex = fDeferredDocumentImpl.createTextNode(fStringPool.addString(place.getNodeValue()), ignorable);
                    break;
                }
                default: {
                    throw new IllegalArgumentException("PAR010 Can't copy node type, "+
                                                       type+" ("+
                                                       place.getNodeName()+')'
                                                       +"\n"+type+"\t"+place.getNodeName());
                }
            }
            fDeferredDocumentImpl.appendChild(destIndex, nodeIndex);

            // iterate over children
            if (place.hasChildNodes()) {
                parent = place;
                place = place.getFirstChild();
                destIndex = nodeIndex;
            }

            // advance
            else {
                place = place.getNextSibling();
                while (place == null && parent != start) {
                    place = parent.getNextSibling();
                    parent = parent.getParentNode();
                    destIndex = fDeferredDocumentImpl.getParentNode(destIndex, false);
                }
            }

        }

    } // copyInto(Node,int)

    /**
     * Sets the appropriate occurrence count attributes on the specified
     * model element.
     */
    private void setOccurrenceCount(Element model, int minOccur, int maxOccur) {

        // min
        model.setAttribute("minOccurs", Integer.toString(minOccur));
        if (minOccur == 1) {
            ((AttrImpl)model.getAttributeNode("minOccurs")).setSpecified(false);
        }

        // max
        if (maxOccur == -1) {
            model.setAttribute("maxOccurs", "*");
        }
        else if (maxOccur != 1) {
            model.setAttribute("maxOccurs", Integer.toString(maxOccur));
        }

    } // setOccurrenceCount(Element,int,int)

    /** Creates the children for the element decl. */
    private Element createChildren(XMLContentSpec.Provider provider, 
                                   int index, XMLContentSpec node,
                                   DocumentImpl factory,
                                   Element parent) throws Exception {

        // get occurrence count
        provider.getContentSpec(index, node);
        int occurs = -1;
        switch (node.type) {
            case XMLContentSpec.CONTENTSPECNODE_ONE_OR_MORE: {
                occurs = '+';
                provider.getContentSpec(node.value, node);
                break;
            }
            case XMLContentSpec.CONTENTSPECNODE_ZERO_OR_MORE: {
                occurs = '*';
                provider.getContentSpec(node.value, node);
                break;
            }
            case XMLContentSpec.CONTENTSPECNODE_ZERO_OR_ONE: {
                occurs = '?';
                provider.getContentSpec(node.value, node);
                break;
            }
        }

        // flatten model
        int nodeType = node.type;
        switch (nodeType) {

            // CHOICE or SEQUENCE
            case XMLContentSpec.CONTENTSPECNODE_CHOICE:
            case XMLContentSpec.CONTENTSPECNODE_SEQ: {

                // go down left side
                int leftIndex  = node.value;
                int rightIndex = node.otherValue;
                Element left = createChildren(provider, leftIndex, node, 
                                              factory, parent);

                // go down right side
                Element right = createChildren(provider, rightIndex, node, 
                                               factory, null);

                // append left children
                boolean choice = nodeType == XMLContentSpec.CONTENTSPECNODE_CHOICE;
                String type = choice ? "choice" : "sequence";
                Element model = left;
                if (!left.getNodeName().equals(type)) {
                    String minOccurs = left.getAttribute("minOccurs");
                    String maxOccurs = left.getAttribute("maxOccurs");
                    boolean min1 = minOccurs.length() == 0 || minOccurs.equals("1");
                    boolean max1 = maxOccurs.length() == 0 || maxOccurs.equals("1");
                    if (parent == null || (min1 && max1)) {
                        model = factory.createElement(type);
                        model.appendChild(left);
                    }
                    else {
                        model = parent;
                    }
                }

                // set occurrence count
                switch (occurs) {
                    case '+': {
                        model.setAttribute("maxOccurs", "unbounded");
                        break;
                    }
                    case '*': {
                        model.setAttribute("minOccurs", "0");
                        model.setAttribute("maxOccurs", "unbounded");
                        break;
                    }
                    case '?': {
                        model.setAttribute("minOccurs", "0");
                        break;
                    }
                }

                // append right children
                model.appendChild(right);

                // return model
                return model;
            }

            // LEAF
            case XMLContentSpec.CONTENTSPECNODE_LEAF: {
                Element leaf = factory.createElement("element");
                leaf.setAttribute("ref", fStringPool.toString(node.value));
                switch (occurs) {
                    case '+': {
                        leaf.setAttribute("maxOccurs", "unbounded");
                        break;
                    }
                    case '*': {
                        leaf.setAttribute("minOccurs", "0");
                        leaf.setAttribute("maxOccurs", "unbounded");
                        break;
                    }
                    case '?': {
                        leaf.setAttribute("minOccurs", "0");
                        break;
                    }
                }
                return leaf;
            }

        } // switch node type

        // error
        return null;

    } // createChildren(XMLContentSpec.Provider,int,XMLContentSpec,DocumentImpl,Element):Element

    /** Creates the children for the deferred element decl. */
    private int createChildren(XMLContentSpec.Provider provider, 
                               int index, XMLContentSpec node,
                               DeferredDocumentImpl factory,
                               int parent) throws Exception {

        // get occurrence count
        provider.getContentSpec(index, node);
        int occurs = -1;
        switch (node.type) {
            case XMLContentSpec.CONTENTSPECNODE_ONE_OR_MORE: {
                occurs = '+';
                provider.getContentSpec(node.value, node);
                break;
            }
            case XMLContentSpec.CONTENTSPECNODE_ZERO_OR_MORE: {
                occurs = '*';
                provider.getContentSpec(node.value, node);
                break;
            }
            case XMLContentSpec.CONTENTSPECNODE_ZERO_OR_ONE: {
                occurs = '?';
                provider.getContentSpec(node.value, node);
                break;
            }
        }

        // flatten model
        int nodeType = node.type;
        switch (nodeType) {

            // CHOICE or SEQUENCE
            case XMLContentSpec.CONTENTSPECNODE_CHOICE:
            case XMLContentSpec.CONTENTSPECNODE_SEQ: {

                // go down left side
                int leftIndex  = node.value;
                int rightIndex = node.otherValue;
                int left = createChildren(provider, leftIndex, node, 
                                          factory, parent);

                // go down right side
                int right = createChildren(provider, rightIndex, node, 
                                           factory, -1);

                // append left children
                boolean choice = nodeType == XMLContentSpec.CONTENTSPECNODE_CHOICE;
                int type = fStringPool.addSymbol(choice ? "choice" : "sequence");
                int model = left;
                if (factory.getNodeName(left, false) != type) {
                    int minOccurs = factory.getAttribute(left, fStringPool.addSymbol("minOccurs"));
                    int maxOccurs = factory.getAttribute(left, fStringPool.addSymbol("maxOccurs"));
                    boolean min1 = minOccurs == -1 || fStringPool.toString(minOccurs).equals("1");
                    boolean max1 = maxOccurs == -1 || fStringPool.toString(maxOccurs).equals("1");
                    if (parent == -1 || (min1 && max1)) {
                        model = factory.createElement(type, null, -1);
                        factory.appendChild(model, left);
                    }
                    else {
                        model = parent;
                    }
                }

                // set occurrence count
                switch (occurs) {
                    case '+': {
                        int maxOccurs = factory.createAttribute(fStringPool.addSymbol("maxOccurs"),
                                                                fStringPool.addString("unbounded"),
                                                                true);
                        factory.setAttributeNode(model, maxOccurs);
                        break;
                    }
                    case '*': {
                        int minOccurs = factory.createAttribute(fStringPool.addSymbol("minOccurs"),
                                                                fStringPool.addString("0"),
                                                                true);
                        factory.setAttributeNode(model, minOccurs);
                        int maxOccurs = factory.createAttribute(fStringPool.addSymbol("maxOccurs"),
                                                                fStringPool.addString("unbounded"),
                                                                true);
                        factory.setAttributeNode(model, maxOccurs);
                        break;
                    }
                    case '?': {
                        int minOccurs = factory.createAttribute(fStringPool.addSymbol("minOccurs"),
                                                                fStringPool.addString("0"),
                                                                true);
                        factory.setAttributeNode(model, minOccurs);
                        break;
                    }
                }

                // append right children
                factory.appendChild(model, right);

                // return model
                return model;
            }

            // LEAF
            case XMLContentSpec.CONTENTSPECNODE_LEAF: {
                int handle = fAttrList.startAttrList();
                fAttrList.addAttr(
                    fStringPool.addSymbol("ref"),
                    fStringPool.addString(fStringPool.toString(node.value)),
                    fStringPool.addSymbol("NMTOKEN"),
                    true,
                    false); // search
                switch (occurs) {
                    case '+': {
                        fAttrList.addAttr(
                            fStringPool.addSymbol("maxOccurs"),
                            fStringPool.addString("unbounded"),
                            fStringPool.addSymbol("CDATA"),
                            true,
                            false); // search
                        break;
                    }
                    case '*': {
                        fAttrList.addAttr(
                            fStringPool.addSymbol("minOccurs"),
                            fStringPool.addString("0"),
                            fStringPool.addSymbol("NMTOKEN"),
                            true,
                            false); // search
                        fAttrList.addAttr(
                            fStringPool.addSymbol("maxOccurs"),
                            fStringPool.addString("unbounded"),
                            fStringPool.addSymbol("CDATA"),
                            true,
                            false); // search
                        break;
                    }
                    case '?': {
                        fAttrList.addAttr(
                            fStringPool.addSymbol("minOccurs"),
                            fStringPool.addString("0"),
                            fStringPool.addSymbol("NMTOKEN"),
                            true,
                            false); // search
                        break;
                    }
                }
                fAttrList.endAttrList();
                int leaf = factory.createElement(fStringPool.addSymbol("element"), fAttrList, handle);
                return leaf;
            }

        } // switch node type

        // error
        return -1;

    } // createChildren(XMLContentSpec.Provider,int,XMLContentSpec,DeferredDocumentImpl,int):int

} // class DOMParser