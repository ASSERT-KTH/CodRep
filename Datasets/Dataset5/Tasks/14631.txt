Constants.XERCES_PROPERTY_PREFIX + Constants.XMLGRAMMAR_POOL_PROPERTY;

/*
 * The Apache Software License, Version 1.1
 *
 *
 * Copyright (c) 1999,2000,2001 The Apache Software Foundation.  
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

package org.apache.xerces.impl.dtd;

import org.apache.xerces.impl.Constants;
import org.apache.xerces.impl.XMLErrorReporter;
import org.apache.xerces.impl.validation.ValidationManager;
import org.apache.xerces.impl.msg.XMLMessageFormatter;

import org.apache.xerces.impl.validation.EntityState;
import org.apache.xerces.impl.dtd.models.ContentModelValidator;
import org.apache.xerces.impl.dv.dtd.DatatypeValidator;
import org.apache.xerces.impl.dv.dtd.DatatypeValidatorFactory;
import org.apache.xerces.impl.dv.dtd.DatatypeValidatorFactoryImpl;
import org.apache.xerces.impl.dv.dtd.ENTITYDatatypeValidator;
import org.apache.xerces.impl.dv.dtd.IDDatatypeValidator;
import org.apache.xerces.impl.dv.dtd.IDREFDatatypeValidator;
import org.apache.xerces.impl.dv.dtd.ListDatatypeValidator;
import org.apache.xerces.impl.dv.dtd.NOTATIONDatatypeValidator;
import org.apache.xerces.impl.dv.dtd.InvalidDatatypeFacetException;
import org.apache.xerces.impl.dv.dtd.InvalidDatatypeValueException;

import org.apache.xerces.util.SymbolTable;
import org.apache.xerces.util.XMLChar;

import org.apache.xerces.xni.Augmentations;
import org.apache.xerces.xni.QName;
import org.apache.xerces.xni.XMLString;
import org.apache.xerces.xni.XMLAttributes;
import org.apache.xerces.xni.XMLDocumentHandler;
import org.apache.xerces.xni.XMLDTDHandler;
import org.apache.xerces.xni.XMLDTDContentModelHandler;
import org.apache.xerces.xni.XMLLocator;
import org.apache.xerces.xni.XNIException;
import org.apache.xerces.xni.parser.XMLComponent;
import org.apache.xerces.xni.parser.XMLComponentManager;
import org.apache.xerces.xni.parser.XMLConfigurationException;
import org.apache.xerces.xni.parser.XMLDocumentFilter;
import org.apache.xerces.xni.parser.XMLDTDFilter;
import org.apache.xerces.xni.parser.XMLDTDContentModelFilter;

import java.util.Enumeration;
import java.util.Hashtable;
import java.util.Vector;
import java.util.StringTokenizer;

/**
 * The DTD validator. The validator implements a document
 * filter: receiving document events from the scanner; validating
 * the content and structure; augmenting the InfoSet, if applicable;
 * and notifying the parser of the information resulting from the
 * validation process.
 * <p>
 * This component requires the following features and properties from the
 * component manager that uses it:
 * <ul>
 *  <li>http://xml.org/sax/features/namespaces</li>
 *  <li>http://xml.org/sax/features/validation</li>
 *  <li>http://apache.org/xml/features/validation/dynamic</li>
 *  <li>http://apache.org/xml/properties/internal/symbol-table</li>
 *  <li>http://apache.org/xml/properties/internal/error-reporter</li>
 *  <li>http://apache.org/xml/properties/internal/grammar-pool</li>
 *  <li>http://apache.org/xml/properties/internal/datatype-validator-factory</li>
 * </ul>
 *
 * @author Eric Ye, IBM
 * @author Stubs generated by DesignDoc on Mon Sep 11 11:10:57 PDT 2000
 * @author Andy Clark, IBM
 * @author Jeffrey Rodriguez IBM
 *
 * @version $Id$
 */
public class XMLDTDValidator
implements XMLComponent, 
XMLDocumentFilter, XMLDTDFilter, XMLDTDContentModelFilter {

    //
    // Constants
    //

    /** Top level scope (-1). */
    private static final int TOP_LEVEL_SCOPE = -1;

    // feature identifiers

    /** Feature identifier: namespaces. */
    protected static final String NAMESPACES =
    Constants.SAX_FEATURE_PREFIX + Constants.NAMESPACES_FEATURE;

    /** Feature identifier: validation. */
    protected static final String VALIDATION =
    Constants.SAX_FEATURE_PREFIX + Constants.VALIDATION_FEATURE;

    /** Feature identifier: dynamic validation. */
    protected static final String DYNAMIC_VALIDATION = 
    Constants.XERCES_FEATURE_PREFIX + Constants.DYNAMIC_VALIDATION_FEATURE;

    /** Feature identifier: xml schema validation */
    protected static final String SCHEMA_VALIDATION = 
    Constants.XERCES_FEATURE_PREFIX +Constants.SCHEMA_VALIDATION_FEATURE;

    // property identifiers

    /** Property identifier: symbol table. */
    protected static final String SYMBOL_TABLE =
    Constants.XERCES_PROPERTY_PREFIX + Constants.SYMBOL_TABLE_PROPERTY;

    /** Property identifier: error reporter. */
    protected static final String ERROR_REPORTER =
    Constants.XERCES_PROPERTY_PREFIX + Constants.ERROR_REPORTER_PROPERTY;

    /** Property identifier: grammar pool. */
    protected static final String GRAMMAR_POOL =
    Constants.XERCES_PROPERTY_PREFIX + Constants.GRAMMAR_POOL_PROPERTY;

    /** Property identifier: datatype validator factory. */
    protected static final String DATATYPE_VALIDATOR_FACTORY =
    Constants.XERCES_PROPERTY_PREFIX + Constants.DATATYPE_VALIDATOR_FACTORY_PROPERTY;


    protected static final String VALIDATION_MANAGER =
    Constants.XERCES_PROPERTY_PREFIX + Constants.VALIDATION_MANAGER_PROPERTY;
    // recognized features and properties

    /** Recognized features. */
    protected static final String[] RECOGNIZED_FEATURES = {
        NAMESPACES,
        VALIDATION,
        DYNAMIC_VALIDATION,
        SCHEMA_VALIDATION
    };

    /** Recognized properties. */
    protected static final String[] RECOGNIZED_PROPERTIES = {
        SYMBOL_TABLE,       
        ERROR_REPORTER,
        GRAMMAR_POOL,       
        DATATYPE_VALIDATOR_FACTORY,
        VALIDATION_MANAGER
    };

    // debugging

    /** Compile to true to debug attributes. */
    private static final boolean DEBUG_ATTRIBUTES = false;

    /** Compile to true to debug element children. */
    private static final boolean DEBUG_ELEMENT_CHILDREN = false;

    //        
    // Data
    //

    // updated during reset
    protected ValidationManager fValidationManager = null;

    // features

    /** Namespaces. */
    protected boolean fNamespaces;

    /** Validation. */
    protected boolean fValidation;

    /** Validation against only DTD */
    protected boolean fDTDValidation;

    /** 
     * Dynamic validation. This state of this feature is only useful when
     * the validation feature is set to <code>true</code>.
     */
    protected boolean fDynamicValidation;

    // properties

    /** Symbol table. */
    protected SymbolTable fSymbolTable;

    /** Error reporter. */
    protected XMLErrorReporter fErrorReporter;

    /** Grammar bucket. */
    protected DTDGrammarBucket fGrammarBucket;

    /** Datatype validator factory. */
    protected DatatypeValidatorFactory fDatatypeValidatorFactory;

    // handlers

    /** Document handler. */
    protected XMLDocumentHandler fDocumentHandler;

    /** DTD handler. */
    protected XMLDTDHandler fDTDHandler;

    /** DTD content model handler. */
    protected XMLDTDContentModelHandler fDTDContentModelHandler;

    // grammars

    /** DTD Grammar. */
    protected DTDGrammar fDTDGrammar;

    // state

    /** Perform validation. */
    private boolean fPerformValidation;

    /** Skip validation. */
    private boolean fSkipValidation;

    /** True if in an ignore conditional section of the DTD. */
    protected boolean fInDTDIgnore;

    // information regarding the current element

    /** Current element name. */
    private final QName fCurrentElement = new QName();

    /** Current element index. */
    private int fCurrentElementIndex = -1;

    /** Current content spec type. */
    private int fCurrentContentSpecType = -1;

    /** The root element name. */
    private final QName fRootElement = new QName();

    /** True if seen DOCTYPE declaration. */
    private boolean fSeenDoctypeDecl = false;

    private boolean fInCDATASection = false;
    // element stack

    /** Element index stack. */
    private int[] fElementIndexStack = new int[8];

    /** Content spec type stack. */
    private int[] fContentSpecTypeStack = new int[8];

    /** Element name stack. */
    private QName[] fElementQNamePartsStack = new QName[8];

    // children list and offset stack

    /** 
     * Element children. This data structure is a growing stack that
     * holds the children of elements from the root to the current
     * element depth. This structure never gets "deeper" than the
     * deepest element. Space is re-used once each element is closed.
     * <p>
     * <strong>Note:</strong> This is much more efficient use of memory
     * than creating new arrays for each element depth.
     * <p>
     * <strong>Note:</strong> The use of this data structure is for
     * validation "on the way out". If the validation model changes to
     * "on the way in", then this data structure is not needed.
     */
    private QName[] fElementChildren = new QName[32];

    /** Element children count. */
    private int fElementChildrenLength = 0;

    /** 
     * Element children offset stack. This stack refers to offsets
     * into the <code>fElementChildren</code> array.
     * @see #fElementChildren
     */
    private int[] fElementChildrenOffsetStack = new int[32];

    /** Element depth. */
    private int fElementDepth = -1;

    // validation states

    /** Validation of a standalone document. */
    private boolean fStandaloneIsYes = false;

    /** True if seen the root element. */
    private boolean fSeenRootElement = false;

    /** True if inside of element content. */
    private boolean fInElementContent = false;

    /** Mixed. */
    private boolean fMixed;

    // temporary variables

    /** Temporary element declaration. */
    private XMLElementDecl fTempElementDecl = new XMLElementDecl();

    /** Temporary atribute declaration. */
    private XMLAttributeDecl fTempAttDecl = new XMLAttributeDecl();

    /** Temporary entity declaration. */
    private XMLEntityDecl fEntityDecl = new XMLEntityDecl();

    /** Temporary qualified name. */
    private QName fTempQName = new QName();

    /** Temporary string buffer for buffering datatype value. */
    //private StringBuffer fDatatypeBuffer = new StringBuffer();

    /** Notation declaration hash. */
    private Hashtable fNDataDeclNotations = new Hashtable();

    /** DTD element declaration name. */
    private String fDTDElementDeclName = null;

    /** Mixed element type "hash". */
    private Vector fMixedElementTypes = new Vector();

    /** Element declarations in DTD. */
    private Vector fDTDElementDecls = new Vector();

    /** Temporary string buffers. */
    private StringBuffer fBuffer = new StringBuffer();

    // symbols: general

    /** Symbol: "EMPTY". */
    private String fEMPTYSymbol;

    /** Symbol: "ANY". */
    private String fANYSymbol;

    /** Symbol: "MIXED". */
    private String fMIXEDSymbol;

    /** Symbol: "CHILDREN". */
    private String fCHILDRENSymbol;

    // symbols: DTD datatype

    /** Symbol: "CDATA". */
    private String fCDATASymbol;

    /** Symbol: "ID". */
    private String fIDSymbol;

    /** Symbol: "IDREF". */
    private String fIDREFSymbol;

    /** Symbol: "IDREFS". */
    private String fIDREFSSymbol;

    /** Symbol: "ENTITY". */
    private String fENTITYSymbol;

    /** Symbol: "ENTITIES". */
    private String fENTITIESSymbol;

    /** Symbol: "NMTOKEN". */
    private String fNMTOKENSymbol;

    /** Symbol: "NMTOKENS". */
    private String fNMTOKENSSymbol;

    /** Symbol: "NOTATION". */
    private String fNOTATIONSymbol;

    /** Symbol: "ENUMERATION". */
    private String fENUMERATIONSymbol;

    /** Symbol: "#IMPLIED. */
    private String fIMPLIEDSymbol;

    /** Symbol: "#REQUIRED". */
    private String fREQUIREDSymbol;

    /** Symbol: "#FIXED". */
    private String fFIXEDSymbol;

    /** Symbol: "&lt;&lt;datatypes>>". */
    private String fDATATYPESymbol;

    // attribute validators

    /** Datatype validator: ID. */
    private IDDatatypeValidator fValID;

    /** Datatype validator: IDREF. */
    private IDREFDatatypeValidator fValIDRef;

    /** Datatype validator: IDREFS. */
    private ListDatatypeValidator fValIDRefs;

    /** Datatype validator: ENTITY. */
    private ENTITYDatatypeValidator fValENTITY;

    /** Datatype validator: ENTITIES. */
    private ListDatatypeValidator fValENTITIES;

    /** Datatype validator: NMTOKEN. */
    private DatatypeValidator fValNMTOKEN;

    /** Datatype validator: NMTOKENS. */
    private DatatypeValidator fValNMTOKENS;

    /** Datatype validator: NOTATION. */
    private NOTATIONDatatypeValidator fValNOTATION;

    /**
     * This table has to be own by instance of XMLValidator and shared
     * among ID, IDREF and IDREFS. 
     * <p>
     * <strong>Note:</strong> Only ID has read/write access.
     * <p>
     * <strong>Note:</strong> Should revisit and replace with a ligther
     * structure.
     */
    private Hashtable fTableOfIDs; 

    // to check for duplicate ID or ANNOTATION attribute declare in
    // ATTLIST, and misc VCs

    /** ID attribute names. */
    private Hashtable fTableOfIDAttributeNames;

    /** NOTATION attribute names. */
    private Hashtable fTableOfNOTATIONAttributeNames;

    /** NOTATION enumeration values. */
    private Hashtable fNotationEnumVals;

    //
    // Constructors
    //

    /** Default constructor. */
    public XMLDTDValidator() {

        // initialize data
        for (int i = 0; i < fElementQNamePartsStack.length; i++) {
            fElementQNamePartsStack[i] = new QName();
        }

    } // <init>()

    //
    // XMLComponent methods
    //

    /*
     * Resets the component. The component can query the component manager
     * about any features and properties that affect the operation of the
     * component.
     * 
     * @param componentManager The component manager.
     *
     * @throws SAXException Thrown by component on finitialization error.
     *                      For example, if a feature or property is
     *                      required for the operation of the component, the
     *                      component manager may throw a 
     *                      SAXNotRecognizedException or a
     *                      SAXNotSupportedException.
     */
    public void reset(XMLComponentManager componentManager)
    throws XMLConfigurationException {

        // clear grammars
        fDTDGrammar = null;
        fSeenDoctypeDecl = false;
        fInCDATASection = false;
        // initialize state
        fInDTDIgnore = false;
        fStandaloneIsYes = false;
        fSeenRootElement = false;
        fInElementContent = false;
        fCurrentElementIndex = -1;
        fCurrentContentSpecType = -1;
        fSkipValidation=false;

        fRootElement.clear();

        fNDataDeclNotations.clear();

        // sax features
        try {
            fNamespaces = componentManager.getFeature(NAMESPACES);
        }
        catch (XMLConfigurationException e) {
            fNamespaces = true;
        }
        try {
            fValidation = componentManager.getFeature(VALIDATION);
        }
        catch (XMLConfigurationException e) {
            fValidation = false;
        }
        try {
            fDTDValidation = !(componentManager.getFeature(SCHEMA_VALIDATION));
        }
        catch (XMLConfigurationException e) {
            fValidation = false;
        }

        // Xerces features
        try {
            fDynamicValidation = componentManager.getFeature(DYNAMIC_VALIDATION);
        }
        catch (XMLConfigurationException e) {
            fDynamicValidation = false;
        }

        fValidationManager= (ValidationManager)componentManager.getProperty(VALIDATION_MANAGER);
        fValidationManager.reset();
        // get needed components
        fErrorReporter = (XMLErrorReporter)componentManager.getProperty(Constants.XERCES_PROPERTY_PREFIX+Constants.ERROR_REPORTER_PROPERTY);
        fSymbolTable = (SymbolTable)componentManager.getProperty(Constants.XERCES_PROPERTY_PREFIX+Constants.SYMBOL_TABLE_PROPERTY);
        fGrammarBucket = new DTDGrammarBucket();
        fDatatypeValidatorFactory = (DatatypeValidatorFactory)componentManager.getProperty(Constants.XERCES_PROPERTY_PREFIX + Constants.DATATYPE_VALIDATOR_FACTORY_PROPERTY);

        fElementDepth = -1;                      
        init();

    } // reset(XMLComponentManager)

    /**
     * Returns a list of feature identifiers that are recognized by
     * this component. This method may return null if no features
     * are recognized by this component.
     */
    public String[] getRecognizedFeatures() {
        return RECOGNIZED_FEATURES;
    } // getRecognizedFeatures():String[]

    /**
     * Sets the state of a feature. This method is called by the component
     * manager any time after reset when a feature changes state. 
     * <p>
     * <strong>Note:</strong> Components should silently ignore features
     * that do not affect the operation of the component.
     * 
     * @param featureId The feature identifier.
     * @param state     The state of the feature.
     *
     * @throws SAXNotRecognizedException The component should not throw
     *                                   this exception.
     * @throws SAXNotSupportedException The component should not throw
     *                                  this exception.
     */
    public void setFeature(String featureId, boolean state)
    throws XMLConfigurationException {
    } // setFeature(String,boolean)

    /**
     * Returns a list of property identifiers that are recognized by
     * this component. This method may return null if no properties
     * are recognized by this component.
     */
    public String[] getRecognizedProperties() {
        return RECOGNIZED_PROPERTIES;
    } // getRecognizedProperties():String[]

    /**
     * Sets the value of a property. This method is called by the component
     * manager any time after reset when a property changes value. 
     * <p>
     * <strong>Note:</strong> Components should silently ignore properties
     * that do not affect the operation of the component.
     * 
     * @param propertyId The property identifier.
     * @param value      The value of the property.
     *
     * @throws SAXNotRecognizedException The component should not throw
     *                                   this exception.
     * @throws SAXNotSupportedException The component should not throw
     *                                  this exception.
     */
    public void setProperty(String propertyId, Object value)
    throws XMLConfigurationException {
    } // setProperty(String,Object)

    //
    // XMLDocumentSource methods
    //

    /**
     * Sets the document handler to receive information about the document.
     * 
     * @param documentHandler The document handler.
     */
    public void setDocumentHandler(XMLDocumentHandler documentHandler) {
        fDocumentHandler = documentHandler;
    } // setDocumentHandler(XMLDocumentHandler)

    //
    // XMLDTDSource methods
    //

    /**
     * Sets the DTD handler.
     * 
     * @param dtdHandler The DTD handler.
     */
    public void setDTDHandler(XMLDTDHandler dtdHandler) {
        fDTDHandler = dtdHandler;
    } // setDTDHandler(XMLDTDHandler)

    //
    // XMLDTDContentModelSource methods
    //

    /**
     * Sets the DTD content model handler.
     * 
     * @param dtdContentModelHandler The DTD content model handler.
     */
    public void setDTDContentModelHandler(XMLDTDContentModelHandler dtdContentModelHandler) {
        fDTDContentModelHandler = dtdContentModelHandler;
    } // setDTDContentModelHandler(XMLDTDContentModelHandler)

    //
    // XMLDocumentHandler methods
    //

    /**
     * The start of the document.
     *
     * @param systemId The system identifier of the entity if the entity
     *                 is external, null otherwise.
     * @param encoding The auto-detected IANA encoding name of the entity
     *                 stream. This value will be null in those situations
     *                 where the entity encoding is not auto-detected (e.g.
     *                 internal entities or a document entity that is
     *                 parsed from a java.io.Reader).
     * @param augs   Additional information that may include infoset augmentations
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void startDocument(XMLLocator locator, String encoding, Augmentations augs) 
    throws XNIException {

        // call handlers
        if (fDocumentHandler != null) {
            fDocumentHandler.startDocument(locator, encoding, augs);
        }

    } // startDocument(XMLLocator,String)

    /**
     * Notifies of the presence of an XMLDecl line in the document. If
     * present, this method will be called immediately following the
     * startDocument call.
     * 
     * @param version    The XML version.
     * @param encoding   The IANA encoding name of the document, or null if
     *                   not specified.
     * @param standalone The standalone value, or null if not specified.     
     * @param augs   Additional information that may include infoset augmentations
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void xmlDecl(String version, String encoding, String standalone, Augmentations augs)
    throws XNIException {

        // save standalone state
        fStandaloneIsYes = standalone != null && standalone.equals("yes");

        // call handlers
        if (fDocumentHandler != null) {
            fDocumentHandler.xmlDecl(version, encoding, standalone, augs);
        }

    } // xmlDecl(String,String,String)

    /**
     * Notifies of the presence of the DOCTYPE line in the document.
     * 
     * @param rootElement The name of the root element.
     * @param publicId    The public identifier if an external DTD or null
     *                    if the external DTD is specified using SYSTEM.
     * @param systemId    The system identifier if an external DTD, null
     *                    otherwise.     
     * @param augs   Additional information that may include infoset augmentations
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void doctypeDecl(String rootElement, String publicId, String systemId, 
                            Augmentations augs)
    throws XNIException {

        // save root element state
        fSeenDoctypeDecl = true;
        fRootElement.setValues(null, rootElement, rootElement, null);

        // call handlers
        if (fDocumentHandler != null) {
            fDocumentHandler.doctypeDecl(rootElement, publicId, systemId, augs);
        }

    } // doctypeDecl(String,String,String)

    /**
     * The start of a namespace prefix mapping. This method will only be
     * called when namespace processing is enabled.
     * 
     * @param prefix The namespace prefix.
     * @param uri    The URI bound to the prefix.     
     * @param augs   Additional information that may include infoset augmentations
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void startPrefixMapping(String prefix, String uri, Augmentations augs)
    throws XNIException {

        // call handlers
        if (fDocumentHandler != null) {
            fDocumentHandler.startPrefixMapping(prefix, uri, augs);
        }

    } // startPrefixMapping(String,String)

    /**
     * The start of an element.
     * 
     * @param element    The name of the element.
     * @param attributes The element attributes.     
     * @param augs   Additional information that may include infoset augmentations
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void startElement(QName element, XMLAttributes attributes, Augmentations augs)
    throws XNIException {

        handleStartElement(element, attributes);

        // call handlers
        if (fDocumentHandler != null) {
            fDocumentHandler.startElement(element, attributes, augs);

        }

    } // startElement(QName,XMLAttributes)

    /**
     * An empty element.
     * 
     * @param element    The name of the element.
     * @param attributes The element attributes.     
     * @param augs   Additional information that may include infoset augmentations
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void emptyElement(QName element, XMLAttributes attributes, Augmentations augs)
    throws XNIException {

        handleStartElement(element, attributes);

        if (fDocumentHandler !=null) {
            fDocumentHandler.emptyElement(element, attributes, augs);
        }

        handleEndElement(element, augs, true);

    } // emptyElement(QName,XMLAttributes)

    /**
     * Character content.
     * 
     * @param text The content.
     *
     * @param augs   Additional information that may include infoset augmentations
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void characters(XMLString text, Augmentations augs) throws XNIException {

        boolean callNextCharacters = true;

        // REVISIT: [Q] Is there a more efficient way of doing this?
        //          Perhaps if the scanner told us so we don't have to
        //          look at the characters again. -Ac
        boolean allWhiteSpace = true;
        for (int i=text.offset; i< text.offset+text.length; i++) {
            if (!XMLChar.isSpace(text.ch[i])) {
                allWhiteSpace = false;
                break;
            }
        }
        // call the ignoreableWhiteSpace callback
        // never call ignorableWhitespace if we are in cdata section
        if (fInElementContent && allWhiteSpace && !fInCDATASection) {
            if (fDocumentHandler != null) {
                fDocumentHandler.ignorableWhitespace(text, augs);
                callNextCharacters = false;
            }
        }

        // validate
        if (fPerformValidation) {
            if (fInElementContent) {
                if (fStandaloneIsYes &&
                    fDTDGrammar.getElementDeclIsExternal(fCurrentElementIndex)) {
                    if (allWhiteSpace) {
                        fErrorReporter.reportError( XMLMessageFormatter.XML_DOMAIN,
                                                    "MSG_WHITE_SPACE_IN_ELEMENT_CONTENT_WHEN_STANDALONE",
                                                    null, XMLErrorReporter.SEVERITY_ERROR);
                    }
                }
                if (!allWhiteSpace) {
                    charDataInContent();
                }
            }

            if (fCurrentContentSpecType == XMLElementDecl.TYPE_EMPTY) {
                charDataInContent();
            }
        }

        // call handlers
        if (callNextCharacters && fDocumentHandler != null) {
            fDocumentHandler.characters(text, augs);
        }

    } // characters(XMLString)



    /**
     * Ignorable whitespace. For this method to be called, the document
     * source must have some way of determining that the text containing
     * only whitespace characters should be considered ignorable. For
     * example, the validator can determine if a length of whitespace
     * characters in the document are ignorable based on the element
     * content model.
     * 
     * @param text The ignorable whitespace.
     *
     * @param augs   Additional information that may include infoset augmentations
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void ignorableWhitespace(XMLString text, Augmentations augs) throws XNIException {

        // call handlers
        if (fDocumentHandler != null) {
            fDocumentHandler.ignorableWhitespace(text, augs);
        }

    } // ignorableWhitespace(XMLString)

    /**
     * The end of an element.
     * 
     * @param element The name of the element.
     * @param augs   Additional information that may include infoset augmentations
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void endElement(QName element, Augmentations augs) throws XNIException {

        handleEndElement(element,  augs, false);

    } // endElement(QName)

    /**
     * The end of a namespace prefix mapping. This method will only be
     * called when namespace processing is enabled.
     * 
     * @param prefix The namespace prefix.
     * @param augs   Additional information that may include infoset augmentations
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void endPrefixMapping(String prefix, Augmentations augs) throws XNIException {

        // call handlers
        if (fDocumentHandler != null) {
            fDocumentHandler.endPrefixMapping(prefix, augs);
        }

    } // endPrefixMapping(String)

    /** 
     * The start of a CDATA section. 
     * @param augs   Additional information that may include infoset augmentations
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void startCDATA(Augmentations augs) throws XNIException {

        if (fPerformValidation && fInElementContent) {
            charDataInContent();
        }
        fInCDATASection = true;
        // call handlers
        if (fDocumentHandler != null) {
            fDocumentHandler.startCDATA(augs);
        }

    } // startCDATA()

    /**
     * The end of a CDATA section. 
     * @param augs   Additional information that may include infoset augmentations
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void endCDATA(Augmentations augs) throws XNIException {

        fInCDATASection = false;
        // call handlers
        if (fDocumentHandler != null) {
            fDocumentHandler.endCDATA(augs);
        }

    } // endCDATA()

    /**
     * The end of the document.
     * @param augs   Additional information that may include infoset augmentations
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void endDocument(Augmentations augs) throws XNIException {

        // call handlers
        if (fDocumentHandler != null) {
            fDocumentHandler.endDocument(augs);
        }

    } // endDocument()

    //
    // XMLDocumentHandler and XMLDTDHandler methods
    //

    /**
     * This method notifies of the start of an entity. The DTD has the
     * pseudo-name of "[dtd]" parameter entity names start with '%'; and 
     * general entity names are just the entity name.
     * <p>
     * <strong>Note:</strong> This method is not called for entity references
     * appearing as part of attribute values.
     * 
     * @param name     The name of the entity.
     * @param publicId The public identifier of the entity if the entity
     *                 is external, null otherwise.
     * @param systemId The system identifier of the entity if the entity
     *                 is external, null otherwise.
     * @param baseSystemId The base system identifier of the entity if
     *                     the entity is external, null otherwise.
     * @param encoding The auto-detected IANA encoding name of the entity
     *                 stream. This value will be null in those situations
     *                 where the entity encoding is not auto-detected (e.g.
     *                 internal parameter entities).
     *
     * @param augs   Additional information that may include infoset augmentations
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void startEntity(String name, 
                            String publicId, String systemId,
                            String baseSystemId,
                            String encoding, 
                            Augmentations augs) throws XNIException {

        // check VC: Standalone Document Declartion, entities references appear in the document.
        if (fPerformValidation && fDTDGrammar != null) {
            if (fStandaloneIsYes && !name.startsWith("[")) {
                int entIndex = fDTDGrammar.getEntityDeclIndex(name);
                if (entIndex > -1) {
                    fDTDGrammar.getEntityDecl(entIndex, fEntityDecl);
                    if (fEntityDecl.inExternal) {
                        fErrorReporter.reportError( XMLMessageFormatter.XML_DOMAIN,
                                                    "MSG_REFERENCE_TO_EXTERNALLY_DECLARED_ENTITY_WHEN_STANDALONE",
                                                    new Object[]{name}, XMLErrorReporter.SEVERITY_ERROR);
                    }
                }
            }
        }

        if (fDocumentHandler != null) {
            fDocumentHandler.startEntity(name, publicId, systemId, 
                                         baseSystemId, encoding, augs);
        }


    } // startEntity(String,String,String,String,String, Augmentations)


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
    public void textDecl(String version, String encoding, Augmentations augs) throws XNIException {

        if (fDocumentHandler != null) {
            fDocumentHandler.textDecl(version, encoding, augs);
        }

    } // textDecl(String,String)


    /**
     * A comment.
     * 
     * @param text The text in the comment.
     *
     * @param augs   Additional information that may include infoset augmentations
     * @throws XNIException Thrown by application to signal an error.
     */
    public void comment(XMLString text, Augmentations augs) throws XNIException {

        // call handlers
        if (fDocumentHandler != null) {
            fDocumentHandler.comment(text, augs);
        }

    } // comment(XMLString)


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
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void processingInstruction(String target, XMLString data, Augmentations augs)
    throws XNIException {

        // call handlers
        if (fDocumentHandler != null) {
            fDocumentHandler.processingInstruction(target, data, augs);
        }
    } // processingInstruction(String,XMLString)


    /**
     * This method notifies the end of an entity.
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
    public void endEntity(String name, Augmentations augs) throws XNIException {

        // call handlers
        if (fDocumentHandler != null) {
            fDocumentHandler.endEntity(name, augs);
        }

    } // endEntity(String)



    //
    // XMLDTDHandler methods
    //

    /**
     * The start of the DTD.
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void startDTD(XMLLocator locator) throws XNIException {

        // initialize state
        fNDataDeclNotations.clear();
        fDTDElementDecls.removeAllElements();

        // create DTD grammar
        fDTDGrammar = createDTDGrammar();
        //fDTDGrammar.setDatatypeValidatorFactory(fDatatypeValidatorFactory);
        // REVISIT: should we use the systemId as the key instead?
        fGrammarBucket.putGrammar("", fDTDGrammar);

        // call handlers
        fDTDGrammar.startDTD(locator);
        if (fDTDHandler != null) {
            fDTDHandler.startDTD(locator);
        }

    } // startDTD(XMLLocator)

    /**
 * A comment.
 * 
 * @param text The text in the comment.
 *
 * @throws XNIException Thrown by application to signal an error.
 */
    public void comment(XMLString text) throws XNIException {

        // call handlers
        fDTDGrammar.comment(text);
        if (fDTDHandler != null) {
            fDTDHandler.comment(text);
        }
    }  

    /**
     * Character content.
     * 
     * @param text The content.
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void characters(XMLString text) throws XNIException {

        // ignored characters in DTD
        if (fDTDHandler != null) {
            fDTDHandler.characters(text);
        }
    }

    /**
     * Notifies of the presence of a TextDecl line in an entity. If present,
     * this method will be called immediately following the startEntity call.
     * <p>
     * <strong>Note:</strong> This method is only called for external
     * parameter entities referenced in the DTD.
     * 
     * @param version  The XML version, or null if not specified.
     * @param encoding The IANA encoding name of the entity.
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void textDecl(String version, String encoding) throws XNIException {

        // call handlers
        fDTDGrammar.textDecl(version, encoding);
        if (fDTDHandler != null) {
            fDTDHandler.textDecl(version, encoding);
        }
    }

    /**
     * This method notifies of the start of an entity. The DTD has the 
     * pseudo-name of "[dtd]" and parameter entity names start with '%'.
     * 
     * @param name     The name of the entity.
     * @param publicId The public identifier of the entity if the entity
     *                 is external, null otherwise.
     * @param systemId The system identifier of the entity if the entity
     *                 is external, null otherwise.
     * @param baseSystemId The base system identifier of the entity if
     *                     the entity is external, null otherwise.
     * @param encoding The auto-detected IANA encoding name of the entity
     *                 stream. This value will be null in those situations
     *                 where the entity encoding is not auto-detected (e.g.
     *                 internal parameter entities).
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void startEntity(String name, 
                            String publicId, String systemId,
                            String baseSystemId,
                            String encoding) throws XNIException {

        // call handlers
        fDTDGrammar.startEntity(name, publicId, systemId, 
                                baseSystemId, encoding);
        if (fDTDHandler != null) {
            fDTDHandler.startEntity(name, publicId, systemId, 
                                    baseSystemId, encoding);
        }
    }
    /**
     * This method notifies the end of an entity. The DTD has the pseudo-name
     * of "[dtd]" and parameter entity names start with '%'.
     * 
     * @param name The name of the entity.
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void endEntity(String name) throws XNIException {

        // call handlers
        fDTDGrammar.endEntity(name);
        if (fDTDHandler != null) {
            fDTDHandler.endEntity(name);
        }
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
     * @exception XNIException
     *                   Thrown by handler to signal an error.
     */
    public void processingInstruction(String target, XMLString data)
    throws XNIException {

        // call handlers
        fDTDGrammar.processingInstruction(target, data);
        if (fDTDHandler != null) {
            fDTDHandler.processingInstruction(target, data);
        }
    } 
    /**
     * An element declaration.
     * 
     * @param name         The name of the element.
     * @param contentModel The element content model.
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void elementDecl(String name, String contentModel)
    throws XNIException {

        //check VC: Unique Element Declaration
        if (fValidation) {
            if (fDTDElementDecls.contains(name)) {
                fErrorReporter.reportError(XMLMessageFormatter.XML_DOMAIN,
                                           "MSG_ELEMENT_ALREADY_DECLARED",
                                           new Object[]{ name},
                                           XMLErrorReporter.SEVERITY_ERROR);
            }
            else {
                fDTDElementDecls.addElement(name);
            }
        }

        // call handlers
        fDTDGrammar.elementDecl(name, contentModel);
        if (fDTDHandler != null) {
            fDTDHandler.elementDecl(name, contentModel);
        }

    } // elementDecl(String,String)

    /**
     * The start of an attribute list.
     * 
     * @param elementName The name of the element that this attribute
     *                    list is associated with.
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void startAttlist(String elementName) throws XNIException {

        // call handlers
        fDTDGrammar.startAttlist(elementName);
        if (fDTDHandler != null) {
            fDTDHandler.startAttlist(elementName);
        }

    } // startAttlist(String)

    /**
     * An attribute declaration.
     * 
     * @param elementName   The name of the element that this attribute
     *                      is associated with.
     * @param attributeName The name of the attribute.
     * @param type          The attribute type. This value will be one of
     *                      the following: "CDATA", "ENTITY", "ENTITIES",
     *                      "ENUMERATION", "ID", "IDREF", "IDREFS", 
     *                      "NMTOKEN", "NMTOKENS", or "NOTATION".
     * @param enumeration   If the type has the value "ENUMERATION", this
     *                      array holds the allowed attribute values;
     *                      otherwise, this array is null.
     * @param defaultType   The attribute default type. This value will be
     *                      one of the following: "#FIXED", "#IMPLIED",
     *                      "#REQUIRED", or null.
     * @param defaultValue  The attribute default value, or null if no
     *                      default value is specified.
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void attributeDecl(String elementName, String attributeName, 
                              String type, String[] enumeration, 
                              String defaultType, XMLString defaultValue)
    throws XNIException {

        if (type != fCDATASymbol && defaultValue != null) {
            normalizeDefaultAttrValue(defaultValue);
        }

        if (fValidation) {
            //
            // a) VC: One ID per Element Type, If duplicate ID attribute
            // b) VC: ID attribute Default. if there is a declareared attribute
            //        default for ID it should be of type #IMPLIED or #REQUIRED
            if (type == fIDSymbol) {
                if (defaultValue != null && defaultValue.length != 0) {
                    if (defaultType == null || 
                        !(defaultType == fIMPLIEDSymbol ||
                          defaultType == fREQUIREDSymbol)) {
                        fErrorReporter.reportError(XMLMessageFormatter.XML_DOMAIN,
                                                   "IDDefaultTypeInvalid",
                                                   new Object[]{ attributeName},
                                                   XMLErrorReporter.SEVERITY_ERROR);
                    }
                }

                if (!fTableOfIDAttributeNames.containsKey(elementName)) {
                    fTableOfIDAttributeNames.put(elementName, attributeName);
                }
                else {
                    String previousIDAttributeName = (String)fTableOfIDAttributeNames.get( elementName );//rule a)
                    fErrorReporter.reportError(XMLMessageFormatter.XML_DOMAIN,
                                               "MSG_MORE_THAN_ONE_ID_ATTRIBUTE",
                                               new Object[]{ elementName, previousIDAttributeName, attributeName},
                                               XMLErrorReporter.SEVERITY_ERROR);
                }
            }

            //
            //  VC: One Notaion Per Element Type, should check if there is a
            //      duplicate NOTATION attribute

            if (type == fNOTATIONSymbol) {
                // VC: Notation Attributes: all notation names in the
                //     (attribute) declaration must be declared.
                for (int i=0; i<enumeration.length; i++) {
                    fNotationEnumVals.put(enumeration[i], attributeName);
                }

                if (fTableOfNOTATIONAttributeNames.containsKey( elementName ) == false) {
                    fTableOfNOTATIONAttributeNames.put( elementName, attributeName);
                }
                else {
                    String previousNOTATIONAttributeName = (String) fTableOfNOTATIONAttributeNames.get( elementName );
                    fErrorReporter.reportError(XMLMessageFormatter.XML_DOMAIN,
                                               "MSG_MORE_THAN_ONE_NOTATION_ATTRIBUTE",
                                               new Object[]{ elementName, previousNOTATIONAttributeName, attributeName},
                                               XMLErrorReporter.SEVERITY_ERROR);
                }
            }

            // VC: Attribute Default Legal
            boolean ok = true;
            if (defaultValue != null && 
                (defaultType == null ||
                 (defaultType != null && defaultType == fFIXEDSymbol))) {

                String value = defaultValue.toString();
                if (type == fNMTOKENSSymbol ||
                    type == fENTITIESSymbol || type == fIDREFSSymbol) {

                    StringTokenizer tokenizer = new StringTokenizer(value);
                    if (tokenizer.hasMoreTokens()) {
                        while (true) {
                            String nmtoken = tokenizer.nextToken();
                            if (type == fNMTOKENSSymbol) {
                                if (!XMLChar.isValidNmtoken(nmtoken)) {
                                    ok = false;
                                    break;
                                }
                            }
                            else if (type == fENTITIESSymbol ||
                                     type == fIDREFSSymbol) {
                                if (!XMLChar.isValidName(nmtoken)) {
                                    ok = false;
                                    break;
                                }
                            }
                            if (!tokenizer.hasMoreTokens()) {
                                break;
                            }
                        }
                    }

                }
                else {
                    if (type == fENTITYSymbol ||
                        type == fIDSymbol ||
                        type == fIDREFSymbol ||
                        type == fNOTATIONSymbol) {

                        if (!XMLChar.isValidName(value)) {
                            ok = false;
                        }

                    }
                    else if (type == fNMTOKENSymbol ||
                             type == fENUMERATIONSymbol) {

                        if (!XMLChar.isValidNmtoken(value)) {
                            ok = false;
                        }
                    }

                    if (type == fNOTATIONSymbol ||
                        type == fENUMERATIONSymbol) {
                        ok = false;
                        for (int i=0; i<enumeration.length; i++) {
                            if (defaultValue.equals(enumeration[i])) {
                                ok = true;
                            }
                        }
                    }

                }
                if (!ok) {
                    fErrorReporter.reportError(XMLMessageFormatter.XML_DOMAIN,
                                               "MSG_ATT_DEFAULT_INVALID",
                                               new Object[]{attributeName, value},
                                               XMLErrorReporter.SEVERITY_ERROR);
                }
            }
        }

        // call handlers
        fDTDGrammar.attributeDecl(elementName, attributeName, 
                                  type, enumeration,
                                  defaultType, defaultValue);
        if (fDTDHandler != null) {
            fDTDHandler.attributeDecl(elementName, attributeName, 
                                      type, enumeration, 
                                      defaultType, defaultValue);
        }

    } // attributeDecl(String,String,String,String[],String,XMLString)

    /**
     * The end of an attribute list.
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void endAttlist() throws XNIException {

        // call handlers
        fDTDGrammar.endAttlist();
        if (fDTDHandler != null) {
            fDTDHandler.endAttlist();
        }

    } // endAttlist()

    /**
     * An internal entity declaration.
     * 
     * @param name The name of the entity. Parameter entity names start with
     *             '%', whereas the name of a general entity is just the 
     *             entity name.
     * @param text The value of the entity.
     * @param nonNormalizedText The non-normalized value of the entity. This
     *             value contains the same sequence of characters that was in 
     *             the internal entity declaration, without any entity
     *             references expanded.
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void internalEntityDecl(String name, XMLString text,
                                   XMLString nonNormalizedText) 
    throws XNIException {

        // call handlers
        fDTDGrammar.internalEntityDecl(name, text, nonNormalizedText);
        if (fDTDHandler != null) {
            fDTDHandler.internalEntityDecl(name, text, nonNormalizedText);
        }

    } // internalEntityDecl(String,XMLString,XMLString)

    /**
     * An external entity declaration.
     * 
     * @param name     The name of the entity. Parameter entity names start
     *                 with '%', whereas the name of a general entity is just
     *                 the entity name.
     * @param publicId The public identifier of the entity or null if the
     *                 the entity was specified with SYSTEM.
     * @param systemId The system identifier of the entity.
     * @param baseSystemId The base system identifier of where the entity
     *                     is declared.
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void externalEntityDecl(String name, 
                                   String publicId, String systemId,
                                   String baseSystemId) throws XNIException {

        // call handlers
        fDTDGrammar.externalEntityDecl(name, publicId, systemId, baseSystemId);
        if (fDTDHandler != null) {
            fDTDHandler.externalEntityDecl(name, publicId, systemId,
                                           baseSystemId);
        }

    } // externalEntityDecl(String,String,String,String)

    /**
     * An unparsed entity declaration.
     * 
     * @param name     The name of the entity.
     * @param publicId The public identifier of the entity, or null if not
     *                 specified.
     * @param systemId The system identifier of the entity, or null if not
     *                 specified.
     * @param notation The name of the notation.
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void unparsedEntityDecl(String name, 
                                   String publicId, String systemId, 
                                   String notation) throws XNIException {

        // VC: Notation declared,  in the production of NDataDecl
        if (fValidation) {
            fNDataDeclNotations.put(name, notation);
        }

        // call handlers
        fDTDGrammar.unparsedEntityDecl(name, publicId, systemId, notation);
        if (fDTDHandler != null) {
            fDTDHandler.unparsedEntityDecl(name, publicId, systemId, notation);
        }

    } // unparsedEntityDecl(String,String,String,String)

    /**
     * A notation declaration
     * 
     * @param name     The name of the notation.
     * @param publicId The public identifier of the notation, or null if not
     *                 specified.
     * @param systemId The system identifier of the notation, or null if not
     *                 specified.
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void notationDecl(String name, String publicId, String systemId)
    throws XNIException {

        // call handlers
        fDTDGrammar.notationDecl(name, publicId, systemId);
        if (fDTDHandler != null) {
            fDTDHandler.notationDecl(name, publicId, systemId);
        }

    } // notationDecl(String,String,String)

    /**
     * The start of a conditional section.
     * 
     * @param type The type of the conditional section. This value will
     *             either be CONDITIONAL_INCLUDE or CONDITIONAL_IGNORE.
     *
     * @throws XNIException Thrown by handler to signal an error.
     *
     * @see XMLDTDHandler#CONDITIONAL_INCLUDE
     * @see XMLDTDHandler#CONDITIONAL_IGNORE
     */
    public void startConditional(short type) throws XNIException {

        // set state
        fInDTDIgnore = type == XMLDTDHandler.CONDITIONAL_IGNORE;

        // call handlers
        fDTDGrammar.startConditional(type);
        if (fDTDHandler != null) {
            fDTDHandler.startConditional(type);
        }

    } // startConditional(short)

    /**
     * The end of a conditional section.
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void endConditional() throws XNIException {

        // set state
        fInDTDIgnore = false;

        // call handlers
        fDTDGrammar.endConditional();
        if (fDTDHandler != null) {
            fDTDHandler.endConditional();
        }

    } // endConditional()

    /**
     * The end of the DTD.
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void endDTD() throws XNIException {

        // save grammar
        fDTDGrammar.endDTD();

        // check VC: Notation declared,  in the production of NDataDecl
        if (fValidation) {

            fValENTITY.initialize(fDTDGrammar);//Initialize ENTITY, ENTITIES validators 
            fValENTITIES.initialize(fDTDGrammar);

            // VC : Notation Declared. for external entity declaration [Production 76].
            Enumeration entities = fNDataDeclNotations.keys();
            while (entities.hasMoreElements()) {
                String entity = (String) entities.nextElement();
                String notation = (String) fNDataDeclNotations.get(entity);
                if (fDTDGrammar.getNotationDeclIndex(notation) == -1) {
                    fErrorReporter.reportError(XMLMessageFormatter.XML_DOMAIN,
                                               "MSG_NOTATION_NOT_DECLARED_FOR_UNPARSED_ENTITYDECL",
                                               new Object[]{entity, notation},
                                               XMLErrorReporter.SEVERITY_ERROR);
                }
            }

            // VC: Notation Attributes:
            //     all notation names in the (attribute) declaration must be declared.
            Enumeration notationVals = fNotationEnumVals.keys();
            while (notationVals.hasMoreElements()) {
                String notation = (String) notationVals.nextElement();
                String attributeName = (String) fNotationEnumVals.get(notation);
                if (fDTDGrammar.getNotationDeclIndex(notation) == -1) {
                    fErrorReporter.reportError(XMLMessageFormatter.XML_DOMAIN,
                                               "MSG_NOTATION_NOT_DECLARED_FOR_NOTATIONTYPE_ATTRIBUTE",
                                               new Object[]{attributeName, notation},
                                               XMLErrorReporter.SEVERITY_ERROR);
                }
            }

            fTableOfIDAttributeNames = null;//should be safe to release these references
            fTableOfNOTATIONAttributeNames = null;
        }

        // call handlers
        if (fDTDHandler != null) {
            fDTDHandler.endDTD();
        }

    } // endDTD()

    //
    // XMLDTDContentModelHandler methods
    //

    /** Start content model. */
    public void startContentModel(String elementName) throws XNIException {

        if (fValidation) {
            fDTDElementDeclName = elementName;
            fMixedElementTypes.removeAllElements();
        }

        // call handlers
        fDTDGrammar.startContentModel(elementName);
        if (fDTDContentModelHandler != null) {
            fDTDContentModelHandler.startContentModel(elementName);
        }

    } // startContentModel(String)

    /** ANY. */
    public void any() throws XNIException {
        fDTDGrammar.any();
        if (fDTDContentModelHandler != null) {
            fDTDContentModelHandler.any();
        }
    } // any()

    /** EMPTY. */
    public void empty() throws XNIException {
        fDTDGrammar.empty();
        if (fDTDContentModelHandler != null) {
            fDTDContentModelHandler.empty();
        }
    } // empty()

    /** Start group. */
    public void startGroup() throws XNIException {

        fMixed = false;
        // call handlers
        fDTDGrammar.startGroup();
        if (fDTDContentModelHandler != null) {
            fDTDContentModelHandler.startGroup();
        }

    } // startGroup()

    /** #PCDATA. */
    public void pcdata() {
        fMixed = true;
        fDTDGrammar.pcdata();
        if (fDTDContentModelHandler != null) {
            fDTDContentModelHandler.pcdata();
        }
    } // pcdata()

    /** Element. */
    public void element(String elementName) throws XNIException {

        // check VC: No duplicate Types, in a single mixed-content declaration
        if (fMixed && fValidation) {
            if (fMixedElementTypes.contains(elementName)) {
                fErrorReporter.reportError(XMLMessageFormatter.XML_DOMAIN,
                                           "DuplicateTypeInMixedContent",
                                           new Object[]{fDTDElementDeclName, elementName},
                                           XMLErrorReporter.SEVERITY_ERROR);
            }
            else {
                fMixedElementTypes.addElement(elementName);
            }
        }

        // call handlers
        fDTDGrammar.element(elementName);
        if (fDTDContentModelHandler != null) {
            fDTDContentModelHandler.element(elementName);
        }

    } // childrenElement(String)

    /** Separator. */
    public void separator(short separator) throws XNIException {

        // call handlers
        fDTDGrammar.separator(separator);
        if (fDTDContentModelHandler != null) {
            fDTDContentModelHandler.separator(separator);
        }

    } // separator(short)

    /** Occurrence. */
    public void occurrence(short occurrence) throws XNIException {

        // call handlers
        fDTDGrammar.occurrence(occurrence);
        if (fDTDContentModelHandler != null) {
            fDTDContentModelHandler.occurrence(occurrence);
        }

    } // occurrence(short)

    /** End group. */
    public void endGroup() throws XNIException {

        // call handlers
        fDTDGrammar.endGroup();
        if (fDTDContentModelHandler != null) {
            fDTDContentModelHandler.endGroup();
        }

    } // endGroup()

    /** End content model. */
    public void endContentModel() throws XNIException {

        // call handlers
        fDTDGrammar.endContentModel();
        if (fDTDContentModelHandler != null) {
            fDTDContentModelHandler.endContentModel();
        }

    } // endContentModel()

    //
    // Private methods
    //

    /** Add default attributes and validate. */
    private void addDTDDefaultAttrsAndValidate(int elementIndex, 
                                               XMLAttributes attributes) 
    throws XNIException {

        // is there anything to do?
        if (elementIndex == -1 || fDTDGrammar == null) {
            return;
        }

        // get element info
        fDTDGrammar.getElementDecl(elementIndex,fTempElementDecl);
        QName element = fTempElementDecl.name;

        //
        // Check after all specified attrs are scanned
        // (1) report error for REQUIRED attrs that are missing (V_TAGc)
        // (2) add default attrs (FIXED and NOT_FIXED)
        //
        int attlistIndex = fDTDGrammar.getFirstAttributeDeclIndex(elementIndex);

        while (attlistIndex != -1) {

            fDTDGrammar.getAttributeDecl(attlistIndex, fTempAttDecl);

            if (DEBUG_ATTRIBUTES) {
                if (fTempAttDecl != null) {
                    XMLElementDecl elementDecl = new XMLElementDecl();
                    fDTDGrammar.getElementDecl(elementIndex, elementDecl);
                    System.out.println("element: "+(elementDecl.name.localpart));
                    System.out.println("attlistIndex " + attlistIndex + "\n"+
                                       "attName : '"+(fTempAttDecl.name.localpart) + "'\n"
                                       + "attType : "+fTempAttDecl.simpleType.type + "\n"
                                       + "attDefaultType : "+fTempAttDecl.simpleType.defaultType + "\n"
                                       + "attDefaultValue : '"+fTempAttDecl.simpleType.defaultValue + "'\n"
                                       + attributes.getLength() +"\n"
                                      );
                }
            }
            String attPrefix = fTempAttDecl.name.prefix;
            String attLocalpart = fTempAttDecl.name.localpart;
            String attRawName = fTempAttDecl.name.rawname;
            String attType = getAttributeTypeName(fTempAttDecl);
            int attDefaultType =fTempAttDecl.simpleType.defaultType;
            String attValue = null;

            if (fTempAttDecl.simpleType.defaultValue != null) {
                attValue = fTempAttDecl.simpleType.defaultValue;
            }
            boolean specified = false;
            boolean required = attDefaultType == XMLSimpleType.DEFAULT_TYPE_REQUIRED;
            boolean cdata = attType == fCDATASymbol;

            if (!cdata || required || attValue != null) {
                int attrCount = attributes.getLength();
                for (int i = 0; i < attrCount; i++) {
                    if (attributes.getQName(i) == attRawName) {
                        specified = true;
                        break;
                    }
                }
            }

            if (!specified) {
                if (required) {
                    if (fValidation) {
                        Object[] args = {element.localpart, attRawName};
                        fErrorReporter.reportError(XMLMessageFormatter.XML_DOMAIN,
                                                   "MSG_REQUIRED_ATTRIBUTE_NOT_SPECIFIED", args,
                                                   XMLErrorReporter.SEVERITY_ERROR);
                    }
                }
                else if (attValue != null) {
                    if (fPerformValidation && fStandaloneIsYes) {
                        if (fDTDGrammar.getAttributeDeclIsExternal(attlistIndex)) {

                            Object[] args = { element.localpart, attRawName};
                            fErrorReporter.reportError(XMLMessageFormatter.XML_DOMAIN,
                                                       "MSG_DEFAULTED_ATTRIBUTE_NOT_SPECIFIED", args,
                                                       XMLErrorReporter.SEVERITY_ERROR);
                        }
                    }

                    // add namespace information
                    if (fNamespaces) {
                        int index = attRawName.indexOf(':');
                        if (index != -1) {
                            attPrefix = attRawName.substring(0, index);
                            attPrefix = fSymbolTable.addSymbol(attPrefix);
                            attLocalpart = attRawName.substring(index + 1);
                            attLocalpart = fSymbolTable.addSymbol(attLocalpart);
                        }
                    }

                    // add attribute
                    fTempQName.setValues(attPrefix, attLocalpart, attRawName, fTempAttDecl.name.uri);
                    int newAttr = attributes.addAttribute(fTempQName, attType, attValue);
                }
            }
            // get next att decl in the Grammar for this element
            attlistIndex = fDTDGrammar.getNextAttributeDeclIndex(attlistIndex);
        }

        // now iterate through the expanded attributes for
        // 1. if every attribute seen is declared in the DTD
        // 2. check if the VC: default_fixed holds
        // 3. validate every attribute.
        int attrCount = attributes.getLength();
        for (int i = 0; i < attrCount; i++) {
            String attrRawName = attributes.getQName(i);
            boolean declared = false;
            if (fPerformValidation) {
                if (fStandaloneIsYes) {
                    // check VC: Standalone Document Declaration, entities
                    // references appear in the document.
                    // REVISIT: this can be combined to a single check in
                    // startEntity if we add one more argument in
                    // startEnity, inAttrValue
                    String nonNormalizedValue = attributes.getNonNormalizedValue(i);
                    if (nonNormalizedValue != null) {
                        String entityName = getExternalEntityRefInAttrValue(nonNormalizedValue);
                        if (entityName != null) {
                            fErrorReporter.reportError(XMLMessageFormatter.XML_DOMAIN,
                                                       "MSG_REFERENCE_TO_EXTERNALLY_DECLARED_ENTITY_WHEN_STANDALONE",
                                                       new Object[]{entityName},
                                                       XMLErrorReporter.SEVERITY_ERROR);
                        }
                    }
                }
            }
            int attDefIndex = -1;
            int position =
            fDTDGrammar.getFirstAttributeDeclIndex(elementIndex);
            while (position != -1) {
                fDTDGrammar.getAttributeDecl(position, fTempAttDecl);
                if (fTempAttDecl.name.rawname == attrRawName) {
                    // found the match att decl, 
                    attDefIndex = position;
                    declared = true;
                    break;
                }
                position = fDTDGrammar.getNextAttributeDeclIndex(position);
            }
            if (!declared) {
                if (fPerformValidation) {
                    // REVISIT - cache the elem/attr tuple so that we only
                    // give this error once for each unique occurrence
                    Object[] args = { element.rawname, attrRawName};

                    fErrorReporter.reportError(XMLMessageFormatter.XML_DOMAIN,
                                               "MSG_ATTRIBUTE_NOT_DECLARED",
                                               args,XMLErrorReporter.SEVERITY_ERROR);   
                }
                continue;
            }
            // attribute is declared

            // fTempAttDecl should have the right value set now, so
            // the following is not needed
            // fGrammar.getAttributeDecl(attDefIndex,fTempAttDecl);

            String type = getAttributeTypeName(fTempAttDecl);
            attributes.setType(i, type);

            boolean changedByNormalization = false;
            String oldValue = attributes.getValue(i);
            String attrValue = oldValue;
            if (attributes.isSpecified(i) && type != fCDATASymbol) {
                changedByNormalization = normalizeAttrValue(attributes, i);
                attrValue = attributes.getValue(i);
                if (fPerformValidation && fStandaloneIsYes
                    && changedByNormalization 
                    && fDTDGrammar.getAttributeDeclIsExternal(position)
                   ) {
                    // check VC: Standalone Document Declaration
                    fErrorReporter.reportError(XMLMessageFormatter.XML_DOMAIN,
                                               "MSG_ATTVALUE_CHANGED_DURING_NORMALIZATION_WHEN_STANDALONE",
                                               new Object[]{attrRawName, oldValue, attrValue},
                                               XMLErrorReporter.SEVERITY_ERROR);
                }
            }
            if (!fPerformValidation) {
                continue;
            }
            if (fTempAttDecl.simpleType.defaultType ==
                XMLSimpleType.DEFAULT_TYPE_FIXED) {
                String defaultValue = fTempAttDecl.simpleType.defaultValue;

                if (!attrValue.equals(defaultValue)) {
                    Object[] args = {element.localpart,
                        attrRawName,
                        attrValue,
                        defaultValue};
                    fErrorReporter.reportError(XMLMessageFormatter.XML_DOMAIN,
                                               "MSG_FIXED_ATTVALUE_INVALID",
                                               args, XMLErrorReporter.SEVERITY_ERROR);
                }
            }

            if (fTempAttDecl.simpleType.type == XMLSimpleType.TYPE_ENTITY ||
                fTempAttDecl.simpleType.type == XMLSimpleType.TYPE_ENUMERATION ||
                fTempAttDecl.simpleType.type == XMLSimpleType.TYPE_ID ||
                fTempAttDecl.simpleType.type == XMLSimpleType.TYPE_IDREF ||
                fTempAttDecl.simpleType.type == XMLSimpleType.TYPE_NMTOKEN ||
                fTempAttDecl.simpleType.type == XMLSimpleType.TYPE_NOTATION
               ) {
                validateDTDattribute(element, attrValue, fTempAttDecl);
            }
        } // for all attributes

    } // addDTDDefaultAttrsAndValidate(int,XMLAttrList)

    /** Checks entities in attribute values for standalone VC. */
    private String getExternalEntityRefInAttrValue(String nonNormalizedValue) {
        int valLength = nonNormalizedValue.length();
        int ampIndex = nonNormalizedValue.indexOf('&');
        while (ampIndex != -1) {
            if (ampIndex + 1 < valLength &&
                nonNormalizedValue.charAt(ampIndex+1) != '#') {
                int semicolonIndex = nonNormalizedValue.indexOf(';', ampIndex+1);
                String entityName = nonNormalizedValue.substring(ampIndex+1, semicolonIndex);
                entityName = fSymbolTable.addSymbol(entityName);
                int entIndex = fDTDGrammar.getEntityDeclIndex(entityName);
                if (entIndex > -1) {
                    fDTDGrammar.getEntityDecl(entIndex, fEntityDecl);
                    if (fEntityDecl.inExternal || 
                        (entityName = getExternalEntityRefInAttrValue(fEntityDecl.value)) != null) {
                        return entityName;
                    }
                }
            }
            ampIndex = nonNormalizedValue.indexOf('&', ampIndex+1);
        }
        return null;
    } // isExternalEntityRefInAttrValue(String):String

    /**
     * Validate attributes in DTD fashion.
     */
    private void validateDTDattribute(QName element, String attValue,
                                      XMLAttributeDecl attributeDecl) 
    throws XNIException {

        switch (attributeDecl.simpleType.type) {
        case XMLSimpleType.TYPE_ENTITY: {                            
                // NOTE: Save this information because invalidStandaloneAttDef
                boolean isAlistAttribute = attributeDecl.simpleType.list;

                try {
                    if (isAlistAttribute) {
                        fValENTITIES.validate(attValue, null);
                    }
                    else {
                        fValENTITY.validate(attValue, null);
                    }
                }
                catch (InvalidDatatypeValueException ex) {
                    String  key = ex.getKeyIntoReporter();
                    fErrorReporter.reportError(XMLMessageFormatter.XML_DOMAIN,
                                               key,
                                               new Object[]{ ex.getMessage()},
                                               XMLErrorReporter.SEVERITY_ERROR );

                }
                break;
            }

        case XMLSimpleType.TYPE_NOTATION:
        case XMLSimpleType.TYPE_ENUMERATION: {
                boolean found = false;
                String [] enumVals = attributeDecl.simpleType.enumeration;
                if (enumVals == null) {
                    found = false;
                }
                else
                    for (int i = 0; i < enumVals.length; i++) {
                        if (attValue == enumVals[i] || attValue.equals(enumVals[i])) {
                            found = true;
                            break;
                        }
                    }

                if (!found) {
                    StringBuffer enumValueString = new StringBuffer();
                    if (enumVals != null)
                        for (int i = 0; i < enumVals.length; i++) {
                            enumValueString.append(enumVals[i]+" ");
                        }
                    fErrorReporter.reportError(XMLMessageFormatter.XML_DOMAIN, 
                                               "MSG_ATTRIBUTE_VALUE_NOT_IN_LIST",
                                               new Object[]{attributeDecl.name.rawname, attValue, enumValueString},
                                               XMLErrorReporter.SEVERITY_ERROR);
                }
                break;
            }

        case XMLSimpleType.TYPE_ID: {
                try {
                    fValID.validate(attValue, null);
                }
                catch (InvalidDatatypeValueException ex) {
                    String  key = ex.getKeyIntoReporter();
                    fErrorReporter.reportError(XMLMessageFormatter.XML_DOMAIN,
                                               key,
                                               new Object[] { ex.getMessage()},
                                               XMLErrorReporter.SEVERITY_ERROR );
                }
                break;
            }

        case XMLSimpleType.TYPE_IDREF: {
                boolean isAlistAttribute = attributeDecl.simpleType.list;//Caveat - Save this information because invalidStandaloneAttDef

                try {
                    if (isAlistAttribute) {
                        //System.out.println("values = >>" + value + "<<" );
                        fValIDRefs.validate(attValue, null);
                    }
                    else {
                        fValIDRef.validate(attValue, null);
                    }
                }
                catch (InvalidDatatypeValueException ex) {
                    String key = ex.getKeyIntoReporter();
                    if (key == null) {
                        key = "IDREFSInvalid";
                    }
                    fErrorReporter.reportError(XMLMessageFormatter.XML_DOMAIN,
                                               key,
                                               new Object[]{ ex.getMessage()},
                                               XMLErrorReporter.SEVERITY_ERROR );

                }
                break;
            }

        case XMLSimpleType.TYPE_NMTOKEN: {
                boolean isAlistAttribute = attributeDecl.simpleType.list;//Caveat - Save this information because invalidStandaloneAttDef
                //changes fTempAttDef
                try {
                    if (isAlistAttribute) {
                        fValNMTOKENS.validate(attValue, null);
                    }
                    else {
                        fValNMTOKEN.validate(attValue, null);
                    }
                }
                catch (InvalidDatatypeValueException ex) {
                    if (isAlistAttribute) {
                        fErrorReporter.reportError(XMLMessageFormatter.XML_DOMAIN,
                                                   "NMTOKENSInvalid",
                                                   new Object[] { attValue},
                                                   XMLErrorReporter.SEVERITY_ERROR);
                    }
                    else {
                        fErrorReporter.reportError(XMLMessageFormatter.XML_DOMAIN,
                                                   "NMTOKENInvalid",
                                                   new Object[] { attValue},
                                                   XMLErrorReporter.SEVERITY_ERROR);
                    }
                }
                break;
            }

        } // switch

    } // validateDTDattribute(QName,String,XMLAttributeDecl)

    /** Returns true if invalid standalone attribute definition. */
    boolean invalidStandaloneAttDef(QName element, QName attribute) {
        // REVISIT: This obviously needs to be fixed! -Ac
        boolean state = true;
        /*
       if (fStandaloneReader == -1) {
          return false;
       }
       // we are normalizing a default att value...  this ok?
       if (element.rawname == -1) {
          return false;
       }
       return getAttDefIsExternal(element, attribute);
       */
        return state;
    }

    /**
     * Normalize the attribute value of a non CDATA attributes collapsing
     * sequences of space characters (x20)
     *
     * @param attributes The list of attributes
     * @param index The index of the attribute to normalize
     */
    private boolean normalizeAttrValue(XMLAttributes attributes, int index) {
        // vars
        boolean leadingSpace = true;
        boolean spaceStart = false;
        boolean readingNonSpace = false;
        int count = 0;
        int eaten = 0;
        String attrValue = attributes.getValue(index);
        char[] attValue = new char[attrValue.length()];

        fBuffer.setLength(0);
        attrValue.getChars(0, attrValue.length(), attValue, 0);
        for (int i = 0; i < attValue.length; i++) {

            if (attValue[i] == ' ') {

                // now the tricky part
                if (readingNonSpace) {
                    spaceStart = true;
                    readingNonSpace = false;
                }

                if (spaceStart && !leadingSpace) {
                    spaceStart = false;
                    fBuffer.append(attValue[i]);
                    count++;
                }
                else {
                    if (leadingSpace || !spaceStart) {
                        eaten ++;
                        /*** BUG #3512 ***
                        int entityCount = attributes.getEntityCount(index);
                        for (int j = 0;  j < entityCount; j++) {
                            int offset = attributes.getEntityOffset(index, j);
                            int length = attributes.getEntityLength(index, j);
                            if (offset <= i-eaten+1) {
                                if (offset+length >= i-eaten+1) {
                                    if (length > 0)
                                        length--;
                                }
                            } 
                            else {
                                if (offset > 0)
                                    offset--;
                            }
                            attributes.setEntityOffset(index, j, offset);
                            attributes.setEntityLength(index, j, length);
                        }
                        /***/
                    }
                }

            }
            else {
                readingNonSpace = true;
                spaceStart = false;
                leadingSpace = false;
                fBuffer.append(attValue[i]);
                count++;
            }
        }

        // check if the last appended character is a space.
        if (count > 0 && fBuffer.charAt(count-1) == ' ') {
            fBuffer.setLength(count-1);
            /*** BUG #3512 ***
            int entityCount = attributes.getEntityCount(index);
            for (int j=0;  j < entityCount; j++) {
                int offset = attributes.getEntityOffset(index, j);
                int length = attributes.getEntityLength(index, j);
                if (offset < count-1) {
                    if (offset+length == count) {
                        length--;
                    }
                } 
                else {
                    offset--;
                }
                attributes.setEntityOffset(index, j, offset);
                attributes.setEntityLength(index, j, length);
            }
            /***/
        }
        String newValue = fBuffer.toString();
        attributes.setValue(index, newValue);
        return ! attrValue.equals(newValue);
    }

    /**
     * Normalize the attribute value of a non CDATA default attribute
     * collapsing sequences of space characters (x20)
     *
     * @param value The value to normalize
     * @return Whether the value was changed or not.
     */
    private boolean normalizeDefaultAttrValue(XMLString value) {

        int oldLength = value.length;

        boolean skipSpace = true; // skip leading spaces
        int current = value.offset;
        int end = value.offset + value.length;
        for (int i = value.offset; i < end; i++) {
            if (value.ch[i] == ' ') {
                if (!skipSpace) {
                    // take the first whitespace as a space and skip the others
                    value.ch[current++] = ' ';
                    skipSpace = true;
                }
                else {
                    // just skip it.
                }
            }
            else {
                // simply shift non space chars if needed
                if (current != i) {
                    value.ch[current] = value.ch[i];
                }
                current++;
                skipSpace = false;
            }
        }
        if (current != end) {
            if (skipSpace) {
                // if we finished on a space trim it
                current--;
            }
            // set the new value length
            value.length = current - value.offset;
            return true;
        }
        return false;
    }

    /** Root element specified. */
    private void rootElementSpecified(QName rootElement) throws XNIException {
        if (fPerformValidation) {
            String root1 = fRootElement.rawname;
            String root2 = rootElement.rawname;
            if (root1 == null || !root1.equals(root2)) {
                fErrorReporter.reportError( XMLMessageFormatter.XML_DOMAIN, 
                                            "RootElementTypeMustMatchDoctypedecl", 
                                            new Object[]{root1, root2}, 
                                            XMLErrorReporter.SEVERITY_ERROR);
            }
        }
    } // rootElementSpecified(QName)

    /**
     * Check that the content of an element is valid.
     * <p>
     * This is the method of primary concern to the validator. This method is called
     * upon the scanner reaching the end tag of an element. At that time, the
     * element's children must be structurally validated, so it calls this method.
     * The index of the element being checked (in the decl pool), is provided as
     * well as an array of element name indexes of the children. The validator must
     * confirm that this element can have these children in this order.
     * <p>
     * This can also be called to do 'what if' testing of content models just to see
     * if they would be valid.
     * <p>
     * Note that the element index is an index into the element decl pool, whereas
     * the children indexes are name indexes, i.e. into the string pool.
     * <p>
     * A value of -1 in the children array indicates a PCDATA node. All other
     * indexes will be positive and represent child elements. The count can be
     * zero, since some elements have the EMPTY content model and that must be
     * confirmed.
     *
     * @param elementIndex The index within the <code>ElementDeclPool</code> of this
     *                     element.
     * @param childCount The number of entries in the <code>children</code> array.
     * @param children The children of this element.  
     *
     * @return The value -1 if fully valid, else the 0 based index of the child
     *         that first failed. If the value returned is equal to the number
     *         of children, then additional content is required to reach a valid
     *         ending state.
     *
     * @exception Exception Thrown on error.
     */
    private int checkContent(int elementIndex, 
                             QName[] children,
                             int childOffset, 
                             int childCount) throws XNIException {

        fDTDGrammar.getElementDecl(elementIndex, fTempElementDecl);

        // Get the element name index from the element
        final String elementType = fCurrentElement.rawname;

        // Get out the content spec for this element
        final int contentType = fCurrentContentSpecType;


        //
        //  Deal with the possible types of content. We try to optimized here
        //  by dealing specially with content models that don't require the
        //  full DFA treatment.
        //
        if (contentType == XMLElementDecl.TYPE_EMPTY) {
            //
            //  If the child count is greater than zero, then this is
            //  an error right off the bat at index 0.
            //
            if (childCount != 0) {
                return 0;
            }
        }
        else if (contentType == XMLElementDecl.TYPE_ANY) {
            //
            //  This one is open game so we don't pass any judgement on it
            //  at all. Its assumed to fine since it can hold anything.
            //
        }
        else if (contentType == XMLElementDecl.TYPE_MIXED ||  
                 contentType == XMLElementDecl.TYPE_CHILDREN) {
            // Get the content model for this element, faulting it in if needed
            ContentModelValidator cmElem = null;
            cmElem = fTempElementDecl.contentModelValidator;
            int result = cmElem.validate(children, childOffset, childCount);
            return result;
        }
        else if (contentType == -1) {
            //REVISIT
            /****
            reportRecoverableXMLError(XMLMessages.MSG_ELEMENT_NOT_DECLARED,
                                      XMLMessages.VC_ELEMENT_VALID,
                                      elementType);
            /****/
        }
        else if (contentType == XMLElementDecl.TYPE_SIMPLE) {

            //REVISIT
            // this should never be reached in the case of DTD validation.

        }
        else {
            //REVISIT
            /****
            fErrorReporter.reportError(fErrorReporter.getLocator(),
                                       ImplementationMessages.XERCES_IMPLEMENTATION_DOMAIN,
                                       ImplementationMessages.VAL_CST,
                                       0,
                                       null,
                                       XMLErrorReporter.ERRORTYPE_FATAL_ERROR);
            /****/
        }

        // We succeeded
        return -1;

    } // checkContent(int,int,QName[]):int

    /** Returns the content spec type for an element index. */
    private int getContentSpecType(int elementIndex) {

        int contentSpecType = -1;
        if (elementIndex > -1) {
            if (fDTDGrammar.getElementDecl(elementIndex,fTempElementDecl)) {
                contentSpecType = fTempElementDecl.type;
            }
        }
        return contentSpecType;
    }

    /** Character data in content. */
    private void charDataInContent() {

        if (DEBUG_ELEMENT_CHILDREN) {
            System.out.println("charDataInContent()");
        }
        if (fElementChildren.length <= fElementChildrenLength) {
            QName[] newarray = new QName[fElementChildren.length * 2];
            System.arraycopy(fElementChildren, 0, newarray, 0, fElementChildren.length);
            fElementChildren = newarray;
        }
        QName qname = fElementChildren[fElementChildrenLength];
        if (qname == null) {
            for (int i = fElementChildrenLength; i < fElementChildren.length; i++) {
                fElementChildren[i] = new QName();
            }
            qname = fElementChildren[fElementChildrenLength];
        }
        qname.clear();
        fElementChildrenLength++;

    } // charDataInCount()

    /** convert attribute type from ints to strings */
    private String getAttributeTypeName(XMLAttributeDecl attrDecl) {

        switch (attrDecl.simpleType.type) {
        case XMLSimpleType.TYPE_ENTITY: {
                return attrDecl.simpleType.list ? fENTITIESSymbol : fENTITYSymbol;
            }
        case XMLSimpleType.TYPE_ENUMERATION: {
                StringBuffer buffer = new StringBuffer();
                buffer.append('(');
                for (int i=0; i<attrDecl.simpleType.enumeration.length ; i++) {
                    if (i > 0) {
                        buffer.append("|");
                    }
                    buffer.append(attrDecl.simpleType.enumeration[i]);
                }
                buffer.append(')');
                return fSymbolTable.addSymbol(buffer.toString());
            }
        case XMLSimpleType.TYPE_ID: {
                return fIDSymbol;
            }
        case XMLSimpleType.TYPE_IDREF: {
                return attrDecl.simpleType.list ? fIDREFSSymbol : fIDREFSymbol;
            }
        case XMLSimpleType.TYPE_NMTOKEN: {
                return attrDecl.simpleType.list ? fNMTOKENSSymbol : fNMTOKENSymbol;
            }
        case XMLSimpleType.TYPE_NOTATION: {
                return fNOTATIONSymbol;
            }
        }
        return fCDATASymbol;

    } // getAttributeTypeName(XMLAttributeDecl):String

    /** intialization */
    private void init() {

        // symbols
        fEMPTYSymbol = fSymbolTable.addSymbol("EMPTY");
        fANYSymbol = fSymbolTable.addSymbol("ANY");
        fMIXEDSymbol = fSymbolTable.addSymbol("MIXED");
        fCHILDRENSymbol = fSymbolTable.addSymbol("CHILDREN");

        fCDATASymbol = fSymbolTable.addSymbol("CDATA");
        fIDSymbol = fSymbolTable.addSymbol("ID");
        fIDREFSymbol = fSymbolTable.addSymbol("IDREF");
        fIDREFSSymbol = fSymbolTable.addSymbol("IDREFS");
        fENTITYSymbol = fSymbolTable.addSymbol("ENTITY");
        fENTITIESSymbol = fSymbolTable.addSymbol("ENTITIES");
        fNMTOKENSymbol = fSymbolTable.addSymbol("NMTOKEN");
        fNMTOKENSSymbol = fSymbolTable.addSymbol("NMTOKENS");
        fNOTATIONSymbol = fSymbolTable.addSymbol("NOTATION");
        fENUMERATIONSymbol = fSymbolTable.addSymbol("ENUMERATION");
        fIMPLIEDSymbol = fSymbolTable.addSymbol("#IMPLIED");
        fREQUIREDSymbol = fSymbolTable.addSymbol("#REQUIRED");
        fFIXEDSymbol = fSymbolTable.addSymbol("#FIXED");
        fDATATYPESymbol = fSymbolTable.addSymbol("<<datatype>>");

        // datatype validators
        if (fValidation) {
            try {
                //REVISIT: datatypeRegistry + initialization of datatype 
                //         why do we cast to ListDatatypeValidator?
                ((DatatypeValidatorFactoryImpl)fDatatypeValidatorFactory).initializeDTDRegistry();
                fValID       = (IDDatatypeValidator)((DatatypeValidatorFactoryImpl)fDatatypeValidatorFactory).getDatatypeValidator("ID" );
                fValIDRef    = (IDREFDatatypeValidator)((DatatypeValidatorFactoryImpl)fDatatypeValidatorFactory).getDatatypeValidator("IDREF" );
                fValIDRefs   = (ListDatatypeValidator)((DatatypeValidatorFactoryImpl)fDatatypeValidatorFactory).getDatatypeValidator("IDREFS" );
                fValENTITY   = (ENTITYDatatypeValidator)((DatatypeValidatorFactoryImpl)fDatatypeValidatorFactory).getDatatypeValidator("ENTITY" );
                fValENTITIES = (ListDatatypeValidator)((DatatypeValidatorFactoryImpl)fDatatypeValidatorFactory).getDatatypeValidator("ENTITIES" );
                fValNMTOKEN  = ((DatatypeValidatorFactoryImpl)fDatatypeValidatorFactory).getDatatypeValidator("NMTOKEN");
                fValNMTOKENS = ((DatatypeValidatorFactoryImpl)fDatatypeValidatorFactory).getDatatypeValidator("NMTOKENS");
                fValNOTATION = (NOTATIONDatatypeValidator)((DatatypeValidatorFactoryImpl)fDatatypeValidatorFactory).getDatatypeValidator("NOTATION" );

            }
            catch (Exception e) {
                // should never happen
                e.printStackTrace(System.err);
            }

            //Initialize ID, IDREF, IDREFS validators
            if (fTableOfIDs == null) {
                fTableOfIDs = new Hashtable();//Initialize table of IDs
            }

            fTableOfIDs.clear();
            fValID.initialize(fTableOfIDs);
            fValIDRef.initialize(fTableOfIDs);
            fValIDRefs.initialize(fTableOfIDs);
            if (fNotationEnumVals == null) {
                fNotationEnumVals = new Hashtable(); 
            }
            fNotationEnumVals.clear();

            fTableOfIDAttributeNames = new Hashtable();
            fTableOfNOTATIONAttributeNames = new Hashtable();
        }

    } // init()

    /** ensure element stack capacity */
    private void ensureStackCapacity ( int newElementDepth) {
        if (newElementDepth == fElementQNamePartsStack.length) {
            int[] newStack = new int[newElementDepth * 2];

            QName[] newStackOfQueue = new QName[newElementDepth * 2];
            System.arraycopy(this.fElementQNamePartsStack, 0, newStackOfQueue, 0, newElementDepth );
            fElementQNamePartsStack      = newStackOfQueue;

            QName qname = fElementQNamePartsStack[newElementDepth];
            if (qname == null) {
                for (int i = newElementDepth; i < fElementQNamePartsStack.length; i++) {
                    fElementQNamePartsStack[i] = new QName();
                }
            }

            newStack = new int[newElementDepth * 2];
            System.arraycopy(fElementIndexStack, 0, newStack, 0, newElementDepth);
            fElementIndexStack = newStack;

            newStack = new int[newElementDepth * 2];
            System.arraycopy(fContentSpecTypeStack, 0, newStack, 0, newElementDepth);
            fContentSpecTypeStack = newStack;

        }
    } // ensureStackCapacity

    //
    // Protected methods
    //

    /** Handle element. */
    protected void handleStartElement(QName element, XMLAttributes attributes) throws XNIException {

        // REVISIT: Here are current assumptions about validation features
        //          given that XMLSchema validator is in the pipeline
        //
        // http://xml.org/sax/features/validation = true
        // http://apache.org/xml/features/validation/schema = true
        //
        //[1] XML instance document only has reference to a DTD 
        //  Outcome: report validation errors only against dtd.
        //
        //[2] XML instance document has only XML Schema grammars:
        //  Outcome: report validation errors only against schemas (no errors produced from DTD validator)
        //
        // [3] XML instance document has DTD and XML schemas:
        // Outcome: validation errors reported against both grammars: DTD and schemas.
        //
        //         
        //         if dynamic validation is on
        //            validate only against grammar we've found (depending on settings
        //            for schema feature)
        // 
        // set wether we're performing validation
        fPerformValidation = fValidation && (!fDynamicValidation || fSeenDoctypeDecl)  
                             && (fDTDValidation || fSeenDoctypeDecl);

        // VC: Root Element Type
        // see if the root element's name matches the one in DoctypeDecl 
        if (!fSeenRootElement) {
            fSeenRootElement = true;
            fValidationManager.getValidationState().setEntityState(fDTDGrammar);
            fValidationManager.setGrammarFound(fSeenDoctypeDecl);
            rootElementSpecified(element);
        }

        if (fDTDGrammar == null) {

            if (!fPerformValidation) {
                fCurrentElementIndex = -1;
                fCurrentContentSpecType = -1;
                fInElementContent = false;
            }
            if (fPerformValidation && !fSkipValidation) {
                fSkipValidation = true;
                fErrorReporter.reportError(XMLMessageFormatter.XML_DOMAIN, 
                                           "MSG_GRAMMAR_NOT_FOUND",
                                           new Object[]{ element.rawname},
                                           XMLErrorReporter.SEVERITY_ERROR);
            }
        }
        else {
            //  resolve the element
            fCurrentElementIndex = fDTDGrammar.getElementDeclIndex(element, -1);

            fCurrentContentSpecType = getContentSpecType(fCurrentElementIndex);
            if (fCurrentElementIndex == -1 && fPerformValidation) {
                fErrorReporter.reportError(XMLMessageFormatter.XML_DOMAIN, 
                                           "MSG_ELEMENT_NOT_DECLARED",
                                           new Object[]{ element.rawname},
                                           XMLErrorReporter.SEVERITY_ERROR);
            }
            else {
                //  0. insert default attributes
                //  1. normalize the attributes
                //  2. validate the attrivute list.
                // TO DO: 
                // 
                addDTDDefaultAttrsAndValidate(fCurrentElementIndex, attributes);
            }
        }

        // set element content state
        fInElementContent = fCurrentContentSpecType == XMLElementDecl.TYPE_CHILDREN;

        // increment the element depth, add this element's 
        // QName to its enclosing element 's children list
        fElementDepth++;
        if (fPerformValidation) {
            // push current length onto stack
            if (fElementChildrenOffsetStack.length < fElementDepth) {
                int newarray[] = new int[fElementChildrenOffsetStack.length * 2];
                System.arraycopy(fElementChildrenOffsetStack, 0, newarray, 0, fElementChildrenOffsetStack.length);
                fElementChildrenOffsetStack = newarray;
            }
            fElementChildrenOffsetStack[fElementDepth] = fElementChildrenLength;

            // add this element to children
            if (fElementChildren.length <= fElementChildrenLength) {
                QName[] newarray = new QName[fElementChildrenLength * 2];
                System.arraycopy(fElementChildren, 0, newarray, 0, fElementChildren.length);
                fElementChildren = newarray;
            }
            QName qname = fElementChildren[fElementChildrenLength];
            if (qname == null) {
                for (int i = fElementChildrenLength; i < fElementChildren.length; i++) {
                    fElementChildren[i] = new QName();
                }
                qname = fElementChildren[fElementChildrenLength];
            }
            qname.setValues(element);
            fElementChildrenLength++;
        }

        // save current element information
        fCurrentElement.setValues(element);
        ensureStackCapacity(fElementDepth);
        fElementQNamePartsStack[fElementDepth].setValues(fCurrentElement); 
        fElementIndexStack[fElementDepth] = fCurrentElementIndex;
        fContentSpecTypeStack[fElementDepth] = fCurrentContentSpecType;


    } // handleStartElement(QName,XMLAttributes,boolean)

    /** Handle end element. */
    protected void handleEndElement(QName element,  Augmentations augs, boolean isEmpty)
    throws XNIException {

        // decrease element depth
        fElementDepth--;

        // validate
        if (fPerformValidation) {
            int elementIndex = fCurrentElementIndex;
            if (elementIndex != -1 && fCurrentContentSpecType != -1) {
                QName children[] = fElementChildren;
                int childrenOffset = fElementChildrenOffsetStack[fElementDepth + 1] + 1;
                int childrenLength = fElementChildrenLength - childrenOffset;
                int result = checkContent(elementIndex, 
                                          children, childrenOffset, childrenLength);

                if (result != -1) {
                    fDTDGrammar.getElementDecl(elementIndex, fTempElementDecl);
                    if (fTempElementDecl.type == XMLElementDecl.TYPE_EMPTY) {
                        fErrorReporter.reportError(XMLMessageFormatter.XML_DOMAIN, 
                                                   "MSG_CONTENT_INVALID",
                                                   new Object[]{ element.rawname, "EMPTY"},
                                                   XMLErrorReporter.SEVERITY_ERROR);
                    }
                    else {
                        String messageKey = result != childrenLength ? 
                                            "MSG_CONTENT_INVALID" : "MSG_CONTENT_INCOMPLETE";
                        fErrorReporter.reportError(XMLMessageFormatter.XML_DOMAIN, 
                                                   messageKey,
                                                   new Object[]{ element.rawname, 
                                                       fDTDGrammar.getContentSpecAsString(elementIndex)},
                                                   XMLErrorReporter.SEVERITY_ERROR);
                    }
                }
            }
            fElementChildrenLength = fElementChildrenOffsetStack[fElementDepth + 1] + 1;
        }
        
        // call handlers
        if (fDocumentHandler != null && !isEmpty) {
            // NOTE: The binding of the element doesn't actually happen
            //       yet because the namespace binder does that. However,
            //       if it does it before this point, then the endPrefix-
            //       Mapping calls get made too soon! As long as the
            //       rawnames match, we know it'll have a good binding,
            //       so we can just use the current element. -Ac
            fDocumentHandler.endElement(fCurrentElement, augs);
        }
        
        // now pop this element off the top of the element stack
        if (fElementDepth < -1) {
            throw new RuntimeException("FWK008 Element stack underflow");
        }
        if (fElementDepth < 0) {
            fCurrentElement.clear();
            fCurrentElementIndex = -1;
            fCurrentContentSpecType = -1;
            fInElementContent = false;

            // TO DO : fix this
            //
            // Check after document is fully parsed
            // (1) check that there was an element with a matching id for every
            //   IDREF and IDREFS attr (V_IDREF0)
            //
            if (fPerformValidation) {
                try {
                    fValIDRef.validate();//Do final validation of IDREFS against IDs
                    fValIDRefs.validate();
                }
                catch (InvalidDatatypeValueException ex) {
                    String  key = ex.getKeyIntoReporter();

                    fErrorReporter.reportError( XMLMessageFormatter.XML_DOMAIN,
                                                key,
                                                new Object[]{ ex.getMessage()},
                                                XMLErrorReporter.SEVERITY_ERROR );
                }
                fTableOfIDs.clear();//Clear table of IDs
            }
            return;
        }

        // If Namespace enable then localName != rawName
        fCurrentElement.setValues(fElementQNamePartsStack[fElementDepth]);

        fCurrentElementIndex = fElementIndexStack[fElementDepth];
        fCurrentContentSpecType = fContentSpecTypeStack[fElementDepth];
        fInElementContent = (fCurrentContentSpecType == XMLElementDecl.TYPE_CHILDREN);

    } // handleEndElement(QName,boolean)

    /** Factory method for creating a DTD grammar. */
    protected DTDGrammar createDTDGrammar() {
        return new DTDGrammar(fSymbolTable);
    } // createDTDGrammar():DTDGrammar

} // class XMLDTDValidator