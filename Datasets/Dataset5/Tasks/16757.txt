import org.apache.xerces.util.XMLGrammarPoolImpl;

/*
 * The Apache Software License, Version 1.1
 *
 *
 * Copyright (c) 1999-2002 The Apache Software Foundation.
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

package org.apache.xerces.impl.xs;

import org.apache.xerces.impl.dv.XSSimpleType;
import org.apache.xerces.impl.dv.ValidatedInfo;
import org.apache.xerces.impl.dv.DatatypeException;
import org.apache.xerces.impl.dv.InvalidDatatypeValueException;
import org.apache.xerces.impl.xs.identity.*;
import org.apache.xerces.impl.Constants;
import org.apache.xerces.impl.validation.ValidationManager;
import org.apache.xerces.impl.validation.XMLGrammarPoolImpl;
import org.apache.xerces.impl.XMLErrorReporter;
import org.apache.xerces.impl.xs.traversers.XSDHandler;
import org.apache.xerces.impl.xs.traversers.XSAttributeChecker;
import org.apache.xerces.impl.xs.models.CMBuilder;
import org.apache.xerces.impl.xs.models.XSCMValidator;
import org.apache.xerces.impl.xs.psvi.XSConstants;
import org.apache.xerces.impl.xs.psvi.XSObjectList;
import org.apache.xerces.impl.msg.XMLMessageFormatter;
import org.apache.xerces.impl.validation.ValidationState;
import org.apache.xerces.impl.XMLEntityManager;


import org.apache.xerces.util.AugmentationsImpl;
import org.apache.xerces.util.NamespaceSupport;
import org.apache.xerces.util.SymbolTable;
import org.apache.xerces.util.XMLChar;
import org.apache.xerces.util.IntStack;
import org.apache.xerces.util.XMLResourceIdentifierImpl;

import org.apache.xerces.xni.Augmentations;
import org.apache.xerces.xni.QName;
import org.apache.xerces.xni.XMLString;
import org.apache.xerces.xni.XMLAttributes;
import org.apache.xerces.xni.XMLDocumentHandler;
import org.apache.xerces.xni.parser.XMLDocumentFilter;
import org.apache.xerces.xni.XMLLocator;
import org.apache.xerces.xni.XMLResourceIdentifier;
import org.apache.xerces.xni.XNIException;
import org.apache.xerces.xni.parser.XMLComponent;
import org.apache.xerces.xni.parser.XMLComponentManager;
import org.apache.xerces.xni.parser.XMLConfigurationException;
import org.apache.xerces.xni.parser.XMLEntityResolver;
import org.apache.xerces.xni.parser.XMLInputSource;

import org.apache.xerces.xni.grammars.XMLGrammarPool;
import org.apache.xerces.xni.grammars.Grammar;
import org.apache.xerces.xni.grammars.XMLGrammarDescription;


import org.apache.xerces.xni.psvi.ElementPSVI;
import org.apache.xerces.xni.psvi.AttributePSVI;

import org.xml.sax.InputSource ;

import java.util.Enumeration;
import java.util.Hashtable;
import java.util.Stack;
import java.util.Vector;
import java.util.StringTokenizer;
import java.io.File;
import java.io.FileInputStream;
import java.io.BufferedInputStream;
import java.io.Reader;
import java.io.InputStream;
import java.io.FileNotFoundException;
import java.io.IOException;

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
 *  <li>http://xml.org/sax/features/validation</li>
 *  <li>http://apache.org/xml/properties/internal/symbol-table</li>
 *  <li>http://apache.org/xml/properties/internal/error-reporter</li>
 *  <li>http://apache.org/xml/properties/internal/entity-resolver</li>
 * </ul>
 *
 * @author Sandy Gao IBM
 * @author Elena Litani IBM
 * @author Andy Clark IBM
 * @author Neeraj Bajaj, Sun Microsystems, inc.
 * @version $Id$
 */
public class XMLSchemaValidator
             implements XMLComponent, XMLDocumentFilter, FieldActivator {

    //
    // Constants
    //
    private static final boolean DEBUG = false;
    // feature identifiers


    protected static final String NAMESPACES =
    Constants.SAX_FEATURE_PREFIX + Constants.NAMESPACES_FEATURE;

    /** Feature identifier: validation. */
    protected static final String VALIDATION =
    Constants.SAX_FEATURE_PREFIX + Constants.VALIDATION_FEATURE;

    /** Feature identifier: validation. */
    protected static final String SCHEMA_VALIDATION =
    Constants.XERCES_FEATURE_PREFIX + Constants.SCHEMA_VALIDATION_FEATURE;

    /** Feature identifier: schema full checking*/
    protected static final String SCHEMA_FULL_CHECKING =
    Constants.XERCES_FEATURE_PREFIX + Constants.SCHEMA_FULL_CHECKING;

    /** Feature identifier: dynamic validation. */
    protected static final String DYNAMIC_VALIDATION =
    Constants.XERCES_FEATURE_PREFIX + Constants.DYNAMIC_VALIDATION_FEATURE;

    /** Feature identifier: expose schema normalized value */
    protected static final String NORMALIZE_DATA =
    Constants.XERCES_FEATURE_PREFIX + Constants.SCHEMA_NORMALIZED_VALUE;


    /** Feature identifier: send element default value via characters() */
    protected static final String SCHEMA_ELEMENT_DEFAULT =
    Constants.XERCES_FEATURE_PREFIX + Constants.SCHEMA_ELEMENT_DEFAULT;


    // property identifiers

    /** Property identifier: symbol table. */
    public static final String SYMBOL_TABLE =
    Constants.XERCES_PROPERTY_PREFIX + Constants.SYMBOL_TABLE_PROPERTY;

    /** Property identifier: error reporter. */
    public static final String ERROR_REPORTER =
    Constants.XERCES_PROPERTY_PREFIX + Constants.ERROR_REPORTER_PROPERTY;

    /** Property identifier: entity resolver. */
    public static final String ENTITY_RESOLVER =
    Constants.XERCES_PROPERTY_PREFIX + Constants.ENTITY_RESOLVER_PROPERTY;

    /** Property identifier: grammar pool. */
    public static final String XMLGRAMMAR_POOL =
        Constants.XERCES_PROPERTY_PREFIX + Constants.XMLGRAMMAR_POOL_PROPERTY;

    protected static final String VALIDATION_MANAGER =
    Constants.XERCES_PROPERTY_PREFIX + Constants.VALIDATION_MANAGER_PROPERTY;

    protected static final String ENTITY_MANAGER =
    Constants.XERCES_PROPERTY_PREFIX + Constants.ENTITY_MANAGER_PROPERTY;

    /** Property identifier: schema location. */
    protected static final String SCHEMA_LOCATION =
    Constants.XERCES_PROPERTY_PREFIX + Constants.SCHEMA_LOCATION;

    /** Property identifier: no namespace schema location. */
    protected static final String SCHEMA_NONS_LOCATION =
    Constants.XERCES_PROPERTY_PREFIX + Constants.SCHEMA_NONS_LOCATION;

    /** Property identifier: JAXP schema source. */
    protected static final String JAXP_SCHEMA_SOURCE =
    Constants.JAXP_PROPERTY_PREFIX + Constants.SCHEMA_SOURCE;

    // recognized features and properties

    /** Recognized features. */
    protected static final String[] RECOGNIZED_FEATURES = {
        VALIDATION,
        NAMESPACES,
        SCHEMA_VALIDATION,
        DYNAMIC_VALIDATION,
        SCHEMA_FULL_CHECKING,
    };

    /** Recognized properties. */
    protected static final String[] RECOGNIZED_PROPERTIES = {
        SYMBOL_TABLE,
        ERROR_REPORTER,
        ENTITY_RESOLVER,
        VALIDATION_MANAGER,
        SCHEMA_LOCATION,
        SCHEMA_NONS_LOCATION,
        JAXP_SCHEMA_SOURCE
    };

    //
    // Data
    //
    protected boolean fSeenRoot = false;
    // features
    // REVISIT: what does it mean if namespaces is off
    //          while schema validation is on?
    protected boolean fNamespaces = false;

    /** PSV infoset information for element */
    protected final  ElementPSVImpl fElemPSVI = new ElementPSVImpl();

    /** current PSVI element info */
    protected ElementPSVImpl fCurrentPSVI = null;


    // since it is the responsibility of each component to an
    // Augmentations parameter if one is null, to save ourselves from
    // having to create this object continually, it is created here.
    // If it is not present in calls that we're passing on, we *must*
    // clear this before we introduce it into the pipeline.
    protected final AugmentationsImpl fAugmentations = new AugmentationsImpl();

    // this is included for the convenience of handleEndElement
    protected XMLString fDefaultValue;

    /** Validation. */
    protected boolean fValidation = false;
    protected boolean fDynamicValidation = false;
    protected boolean fDoValidation = false;
    protected boolean fFullChecking = false;
    protected boolean fNormalizeData = true;
    protected boolean fSchemaElementDefault = true;
    protected boolean fEntityRef = false;
    protected boolean fInCDATA = false;

    // properties

    /** Symbol table. */
    protected SymbolTable fSymbolTable;
    protected final XSDeclarationPool fDeclPool = new XSDeclarationPool();

    /**
     * A wrapper of the standard error reporter. We'll store all schema errors
     * in this wrapper object, so that we can get all errors (error codes) of
     * a specific element. This is useful for PSVI.
     */
    class XSIErrorReporter {

        // the error reporter property
        XMLErrorReporter fErrorReporter;

        // store error codes; starting position of the errors for each element;
        // number of element (depth); and whether to record error
        Vector  fErrors = new Vector(INITIAL_STACK_SIZE, INC_STACK_SIZE);
        int[]   fContext = new int[INITIAL_STACK_SIZE];
        int     fContextCount;

        // set the external error reporter, clear errors
        public void reset(XMLErrorReporter errorReporter) {
            fErrorReporter = errorReporter;
            fErrors.removeAllElements();
            fContextCount = 0;
        }

        // should be called on startElement: store the starting position
        // for the current element
        public void pushContext() {
            // resize array if necessary
            if (fContextCount == fContext.length) {
                int newSize = fContextCount + INC_STACK_SIZE;
                int[] newArray = new int[newSize];
                System.arraycopy(fContext, 0, newArray, 0, fContextCount);
                fContext = newArray;
            }

            fContext[fContextCount++] = fErrors.size();
        }

        // should be called on endElement: get all errors of the current element
        public String[] popContext() {
            // get starting position of the current element
            int contextPos = fContext[--fContextCount];
            // number of errors of the current element
            int size = fErrors.size() - contextPos;
            // if no errors, return null
            if (size == 0)
                return null;
            // copy errors from the list to an string array
            String[] errors = new String[size];
            for (int i = 0; i < size; i++) {
                errors[i] = (String)fErrors.elementAt(contextPos + i);
            }
            // remove errors of the current element
            fErrors.setSize(contextPos);
            return errors;
        }

        public void reportError(String domain, String key, Object[] arguments,
                                short severity) throws XNIException {
            fErrorReporter.reportError(domain, key, arguments, severity);
            fErrors.addElement(key);
        } // reportError(String,String,Object[],short)

        public void reportError(XMLLocator location,
                                String domain, String key, Object[] arguments,
                                short severity) throws XNIException {
            fErrorReporter.reportError(location, domain, key, arguments, severity);
            fErrors.addElement(key);
        } // reportError(XMLLocator,String,String,Object[],short)
    }

    /** Error reporter. */
    protected XSIErrorReporter fXSIErrorReporter = new XSIErrorReporter();

    /** Entity resolver */
    protected XMLEntityResolver fEntityResolver;

    // updated during reset
    protected ValidationManager fValidationManager = null;
    protected ValidationState fValidationState = new ValidationState();
    protected XMLGrammarPool fGrammarPool;

    // schema location property values
    protected String fExternalSchemas = null;
    protected String fExternalNoNamespaceSchema = null;

    //JAXP Schema Source property
    protected Object fJaxpSchemaSource = null ;

    //ResourceIdentifier for use in calling EntityResolver
    XMLResourceIdentifierImpl fResourceIdentifier = new XMLResourceIdentifierImpl();

    /** Schema Grammar Description passed,  to give a chance to application to supply the Grammar */
    protected final XSDDescription fXSDDescription = new XSDDescription() ;
    protected final Hashtable fLocationPairs = new Hashtable() ;
    protected final LocationArray fNoNamespaceLocationArray = new LocationArray();

    // handlers

    /** Document handler. */
    protected XMLDocumentHandler fDocumentHandler;

    //
    // XMLComponent methods
    //

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
    // XMLDocumentHandler methods
    //

    /**
     * The start of the document.
     *
     * @param locator The system identifier of the entity if the entity
     *                 is external, null otherwise.
     * @param encoding The auto-detected IANA encoding name of the entity
     *                 stream. This value will be null in those situations
     *                 where the entity encoding is not auto-detected (e.g.
     *                 internal entities or a document entity that is
     *                 parsed from a java.io.Reader).
     * @param augs     Additional information that may include infoset augmentations
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void startDocument(XMLLocator locator, String encoding, Augmentations augs)
    throws XNIException {

        handleStartDocument(locator, encoding);
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
     * @param augs     Additional information that may include infoset augmentations
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void xmlDecl(String version, String encoding, String standalone, Augmentations augs)
    throws XNIException {

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
     * @param augs     Additional information that may include infoset augmentations
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void doctypeDecl(String rootElement, String publicId, String systemId,
                            Augmentations augs)
    throws XNIException {

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
     * @param augs     Additional information that may include infoset augmentations
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void startPrefixMapping(String prefix, String uri, Augmentations augs)
    throws XNIException {

        handleStartPrefix(prefix, uri);
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
     * @param augs     Additional information that may include infoset augmentations
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void startElement(QName element, XMLAttributes attributes, Augmentations augs)
    throws XNIException {

        Augmentations modifiedAugs = handleStartElement(element, attributes, augs);
        // call handlers
        if (fDocumentHandler != null) {
            fDocumentHandler.startElement(element, attributes, modifiedAugs );
        }

    } // startElement(QName,XMLAttributes, Augmentations)

    /**
     * An empty element.
     *
     * @param element    The name of the element.
     * @param attributes The element attributes.
     * @param augs     Additional information that may include infoset augmentations
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void emptyElement(QName element, XMLAttributes attributes, Augmentations augs)
    throws XNIException {

        Augmentations modifiedAugs = handleStartElement(element, attributes, augs);

        // we need to save PSVI information: because it will be reset in the
        // handleEndElement(): decl, type, notation, validation context
        XSElementDecl decl = fCurrentPSVI.fDeclaration;
        XSTypeDecl type = fCurrentPSVI.fTypeDecl;
        XSNotationDecl notation = fCurrentPSVI.fNotation;
        String vContext = fCurrentPSVI.fValidationContext;

        // in the case where there is a {value constraint}, and the element
        // doesn't have any text content, change emptyElement call to
        // start + characters + end
        modifiedAugs = handleEndElement(element, modifiedAugs);

        // call handlers
        if (fDocumentHandler != null) {
            fCurrentPSVI.fDeclaration = decl;
            fCurrentPSVI.fTypeDecl = type;
            fCurrentPSVI.fNotation = notation;
            fCurrentPSVI.fValidationContext = vContext;
            if (!fSchemaElementDefault || fDefaultValue == null) {
                fDocumentHandler.emptyElement(element, attributes, modifiedAugs);
            } else {
                fDocumentHandler.startElement(element, attributes, modifiedAugs);
                fDocumentHandler.characters(fDefaultValue, modifiedAugs);
                fDocumentHandler.endElement(element, modifiedAugs);
            }
       }
    } // emptyElement(QName,XMLAttributes, Augmentations)

    /**
     * Character content.
     *
     * @param text The content.
     * @param augs     Additional information that may include infoset augmentations
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void characters(XMLString text, Augmentations augs) throws XNIException {

        boolean emptyAug = false;
        if (augs == null) {
            emptyAug = true;
            augs = fAugmentations;
            augs.clear();
        }
        // get PSVI object
        fCurrentPSVI = (ElementPSVImpl)augs.getItem(Constants.ELEMENT_PSVI);
        if (fCurrentPSVI == null) {
            fCurrentPSVI = fElemPSVI;
            augs.putItem(Constants.ELEMENT_PSVI, fCurrentPSVI);
        }
        else {
            fCurrentPSVI.reset();
        }

        handleCharacters(text);
        // call handlers
        if (fDocumentHandler != null) {
            if (fUnionType) {
                // for union types we can't normalize data
                // thus we only need to send augs information if any;
                // the normalized data for union will be send
                // after normalization is performed (at the endElement())
                if (!emptyAug) {
                    fDocumentHandler.characters(fEmptyXMLStr, augs);
                }
            } else {
                fDocumentHandler.characters(text, augs);
            }
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
     * @param augs     Additional information that may include infoset augmentations
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void ignorableWhitespace(XMLString text, Augmentations augs) throws XNIException {

        handleIgnorableWhitespace(text);
        // call handlers
        if (fDocumentHandler != null) {
            fDocumentHandler.ignorableWhitespace(text, augs);
        }

    } // ignorableWhitespace(XMLString)

    /**
     * The end of an element.
     *
     * @param element The name of the element.
     * @param augs     Additional information that may include infoset augmentations
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void endElement(QName element, Augmentations augs) throws XNIException {

        // in the case where there is a {value constraint}, and the element
        // doesn't have any text content, add a characters call.
        Augmentations modifiedAugs = handleEndElement(element, augs);
        // call handlers
        if (fDocumentHandler != null) {
            if (fSchemaElementDefault || fDefaultValue == null) {
                   fDocumentHandler.endElement(element, modifiedAugs);
            } else {
                fDocumentHandler.characters(fDefaultValue, modifiedAugs);
                fDocumentHandler.endElement(element, modifiedAugs);
            }
        }
    } // endElement(QName, Augmentations)

    /**
     * The end of a namespace prefix mapping. This method will only be
     * called when namespace processing is enabled.
     *
     * @param prefix The namespace prefix.
     * @param augs     Additional information that may include infoset augmentations
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
     *
     * @param augs     Additional information that may include infoset augmentations
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void startCDATA(Augmentations augs) throws XNIException {

        // REVISIT: what should we do here if schema normalization is on??
        fInCDATA = true;
        // call handlers
        if (fDocumentHandler != null) {
            fDocumentHandler.startCDATA(augs);
        }

    } // startCDATA()

    /**
     * The end of a CDATA section.
     *
     * @param augs     Additional information that may include infoset augmentations
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void endCDATA(Augmentations augs) throws XNIException {

        // call handlers
        fInCDATA = false;
        if (fDocumentHandler != null) {
            fDocumentHandler.endCDATA(augs);
        }

    } // endCDATA()

    /**
     * The end of the document.
     *
     * @param augs     Additional information that may include infoset augmentations
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void endDocument(Augmentations augs) throws XNIException {

        handleEndDocument();

        //return the final set of grammars validator ended up with
        if(fGrammarPool != null){
            fGrammarPool.cacheGrammars(XMLGrammarDescription.XML_SCHEMA , fGrammarBucket.getGrammars() ) ;
        }

        // call handlers
        if (fDocumentHandler != null) {
            fDocumentHandler.endDocument(augs);
        }

    } // endDocument(Augmentations)

    //
    // XMLDocumentHandler and XMLDTDHandler methods
    //

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
                                   Augmentations augs) throws XNIException {

        // REVISIT: what should happen if normalize_data_ is on??
        fEntityRef = true;
        // call handlers
        if (fDocumentHandler != null) {
            fDocumentHandler.startGeneralEntity(name, identifier, encoding, augs);
        }

    } // startEntity(String,String,String,String,String)

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
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void textDecl(String version, String encoding, Augmentations augs) throws XNIException {

        // call handlers
        if (fDocumentHandler != null) {
            fDocumentHandler.textDecl(version, encoding, augs);
        }

    } // textDecl(String,String)

    /**
     * A comment.
     *
     * @param text The text in the comment.
     * @param augs     Additional information that may include infoset augmentations
     *
     * @throws XNIException Thrown by application to signal an error.
     */
    public void comment(XMLString text, Augmentations augs) throws XNIException {

        // record the fact that there is a comment child.
        fSawChildren = true;

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
     * @param augs     Additional information that may include infoset augmentations
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void processingInstruction(String target, XMLString data, Augmentations augs)
    throws XNIException {

        // record the fact that there is a PI child.
        fSawChildren = true;

        // call handlers
        if (fDocumentHandler != null) {
            fDocumentHandler.processingInstruction(target, data, augs);
        }

    } // processingInstruction(String,XMLString)

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
    public void endGeneralEntity(String name, Augmentations augs) throws XNIException {

        // call handlers
        fEntityRef = false;
        if (fDocumentHandler != null) {
            fDocumentHandler.endGeneralEntity(name, augs);
        }

    } // endEntity(String)

    // constants

    static final int INITIAL_STACK_SIZE = 8;
    static final int INC_STACK_SIZE     = 8;

    // some constants that'll be added into the symbol table
    String XMLNS;
    String URI_XSI;
    String XSI_SCHEMALOCATION;
    String XSI_NONAMESPACESCHEMALOCATION;
    String XSI_TYPE;
    String XSI_NIL;
    String URI_SCHEMAFORSCHEMA;

    //
    // Data
    //


    // Schema Normalization

    private static final boolean DEBUG_NORMALIZATION = false;
    // temporary empty string buffer.
    private final XMLString fEmptyXMLStr = new XMLString(null, 0, -1);
    // temporary character buffer, and empty string buffer.
    private static final int BUFFER_SIZE = 20;
    private char[] fCharBuffer =  new char[BUFFER_SIZE];
    private final StringBuffer fNormalizedStr = new StringBuffer();
    private final XMLString fXMLString = new XMLString(fCharBuffer, 0, -1);
    private boolean fFirstChunk = true; // got first chunk in characters() (SAX)
    private boolean fTrailing = false;  // Previous chunk had a trailing space
    private short fWhiteSpace = -1;  //whiteSpace: preserve/replace/collapse
    private boolean fUnionType = false;


    /** Schema grammar resolver. */
    final XSGrammarBucket fGrammarBucket;
    final SubstitutionGroupHandler fSubGroupHandler;

    /** Schema handler */
    final XSDHandler fSchemaHandler;

    /** Namespace support. */
    final NamespaceSupport fNamespaceSupport = new NamespaceSupport();
    /** this flag is used to indicate whether the next prefix binding
     *  should start a new context (.pushContext)
     */
    boolean fPushForNextBinding;
    /** the DV usd to convert xsi:type to a QName */
    // REVISIT: in new simple type design, make things in DVs static,
    //          so that we can QNameDV.getCompiledForm()
    final XSSimpleType fQNameDV = (XSSimpleType)SchemaGrammar.SG_SchemaNS.getGlobalTypeDecl(SchemaSymbols.ATTVAL_QNAME);

    /** used to build content models */
    // REVISIT: create decl pool, and pass it to each traversers
    final CMBuilder fCMBuilder = new CMBuilder(new XSDeclarationPool());

    // state

    /** String representation of the validation root. */
    // REVISIT: what do we store here? QName, XPATH, some ID? use rawname now.
    String fValidationRoot;

    /** Skip validation. */
    int fSkipValidationDepth;

    /** Partial validation depth */
    int fPartialValidationDepth;

    /** Element depth. */
    int fElementDepth;

    /** Child count. */
    int fChildCount;

    /** Element decl stack. */
    int[] fChildCountStack = new int[INITIAL_STACK_SIZE];

    /** Current element declaration. */
    XSElementDecl fCurrentElemDecl;

    /** Element decl stack. */
    XSElementDecl[] fElemDeclStack = new XSElementDecl[INITIAL_STACK_SIZE];

    /** nil value of the current element */
    boolean fNil;

    /** nil value stack */
    boolean[] fNilStack = new boolean[INITIAL_STACK_SIZE];

    /** Current type. */
    XSTypeDecl fCurrentType;

    /** type stack. */
    XSTypeDecl[] fTypeStack = new XSTypeDecl[INITIAL_STACK_SIZE];

    /** Current content model. */
    XSCMValidator fCurrentCM;

    /** Content model stack. */
    XSCMValidator[] fCMStack = new XSCMValidator[INITIAL_STACK_SIZE];

    /** the current state of the current content model */
    int[] fCurrCMState;

    /** stack to hold content model states */
    int[][] fCMStateStack = new int[INITIAL_STACK_SIZE][];

    /** Temporary string buffers. */
    final StringBuffer fBuffer = new StringBuffer();

    /** Did we see non-whitespace character data? */
    boolean fSawCharacters = false;

    /** Stack to record if we saw character data outside of element content*/
    boolean[] fStringContent = new boolean[INITIAL_STACK_SIZE];

    /** Did we see children that are neither characters nor elements? */
    boolean fSawChildren = false;

    /** Stack to record if we other children that character or elements */
    boolean[] fSawChildrenStack = new boolean[INITIAL_STACK_SIZE];

    /** temprory qname */
    final QName fTempQName = new QName();

    /** temprory validated info */
    ValidatedInfo fValidatedInfo = new ValidatedInfo();

    // used to validate default/fixed values against xsi:type
    // only need to check facets, so we set extraChecking to false (in reset)
    private ValidationState fState4XsiType = new ValidationState();

    // used to apply default/fixed values
    // only need to check id/idref/entity, so we set checkFacets to false
    private ValidationState fState4ApplyDefault = new ValidationState();

    // identity constraint information

    /**
     * Stack of active XPath matchers for identity constraints. All
     * active XPath matchers are notified of startElement, characters
     * and endElement callbacks in order to perform their matches.
     * <p>
     * For each element with identity constraints, the selector of
     * each identity constraint is activated. When the selector matches
     * its XPath, then all the fields of the identity constraint are
     * activated.
     * <p>
     * <strong>Note:</strong> Once the activation scope is left, the
     * XPath matchers are automatically removed from the stack of
     * active matchers and no longer receive callbacks.
     */
    protected XPathMatcherStack fMatcherStack = new XPathMatcherStack();

    /** Cache of value stores for identity constraint fields. */
    protected ValueStoreCache fValueStoreCache = new ValueStoreCache();

    //
    // Constructors
    //

    /** Default constructor. */
    public XMLSchemaValidator() {

        fGrammarBucket = new XSGrammarBucket();
        fSubGroupHandler = new SubstitutionGroupHandler(fGrammarBucket);
        fSchemaHandler = new XSDHandler(fGrammarBucket);

    } // <init>()


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
    public void reset(XMLComponentManager componentManager) throws XMLConfigurationException {

        // get error reporter
        fXSIErrorReporter.reset((XMLErrorReporter)componentManager.getProperty(ERROR_REPORTER));

        // get symbol table. if it's a new one, add symbols to it.
        SymbolTable symbolTable = (SymbolTable)componentManager.getProperty(SYMBOL_TABLE);
        if (symbolTable != fSymbolTable) {
            XMLNS = symbolTable.addSymbol(SchemaSymbols.O_XMLNS);
            URI_XSI = symbolTable.addSymbol(SchemaSymbols.URI_XSI);
            XSI_SCHEMALOCATION = symbolTable.addSymbol(SchemaSymbols.OXSI_SCHEMALOCATION);
            XSI_NONAMESPACESCHEMALOCATION = symbolTable.addSymbol(SchemaSymbols.OXSI_NONAMESPACESCHEMALOCATION);
            XSI_TYPE = symbolTable.addSymbol(SchemaSymbols.OXSI_TYPE);
            XSI_NIL = symbolTable.addSymbol(SchemaSymbols.OXSI_NIL);
            URI_SCHEMAFORSCHEMA = symbolTable.addSymbol(SchemaSymbols.OURI_SCHEMAFORSCHEMA);
        }
        fSymbolTable = symbolTable;

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

        // Xerces features
        try {
            fValidation = fValidation && componentManager.getFeature(SCHEMA_VALIDATION);
        }
        catch (XMLConfigurationException e) {
            fValidation = false;
        }

        try {
            fFullChecking = componentManager.getFeature(SCHEMA_FULL_CHECKING);
        }
        catch (XMLConfigurationException e) {
            fFullChecking = false;
        }

        try {
            fDynamicValidation = componentManager.getFeature(DYNAMIC_VALIDATION);
        }
        catch (XMLConfigurationException e) {
            fDynamicValidation = false;
        }

        try {
           fNormalizeData = componentManager.getFeature(NORMALIZE_DATA);
        }
        catch (XMLConfigurationException e) {
            fNormalizeData = false;
        }

        try {
           fSchemaElementDefault = componentManager.getFeature(SCHEMA_ELEMENT_DEFAULT);
        }
        catch (XMLConfigurationException e) {
            fSchemaElementDefault = false;
        }

        fEntityResolver = (XMLEntityResolver)componentManager.getProperty(ENTITY_MANAGER);

        // initialize namespace support
        fNamespaceSupport.reset(fSymbolTable);
        fPushForNextBinding = true;
        fValidationManager = (ValidationManager)componentManager.getProperty(VALIDATION_MANAGER);
        fValidationManager.addValidationState(fValidationState);
        fValidationState.setNamespaceSupport(fNamespaceSupport);
        fValidationState.setSymbolTable(fSymbolTable);

        // get schema location properties
        fExternalSchemas = (String)componentManager.getProperty(SCHEMA_LOCATION);
        fExternalNoNamespaceSchema = (String)componentManager.getProperty(SCHEMA_NONS_LOCATION);

        // get JAXP schema source property
        fJaxpSchemaSource = componentManager.getProperty(JAXP_SCHEMA_SOURCE);
        fResourceIdentifier.clear();

        // clear grammars, and put the one for schema namespace there
        fGrammarBucket.reset();
        fGrammarPool = (XMLGrammarPool)componentManager.getProperty(XMLGRAMMAR_POOL);

        //we should retreive the initial grammar set given by the applicaion
        //to the parser and put it in local grammar bucket.

        if(fGrammarPool != null) {

            Grammar [] initialGrammars = fGrammarPool.retrieveInitialGrammarSet(XMLGrammarDescription.XML_SCHEMA);
            for (int i = 0; i < initialGrammars.length; i++) {
                // put this grammar into the bucket, along with grammars
                // imported by it (directly or indirectly)
                if (!fGrammarBucket.putGrammar((SchemaGrammar)(initialGrammars[i]), true)) {
                    // REVISIT: a conflict between new grammar(s) and grammars
                    // in the bucket. What to do? A warning? An exception?
                    fXSIErrorReporter.fErrorReporter.reportError(XSMessageFormatter.SCHEMA_DOMAIN,
                                                                 "GrammarConflict", null,
                                                                 XMLErrorReporter.SEVERITY_WARNING);
                }
            }
        }

        // clear things in substitution group handler
        fSubGroupHandler.reset();

        //REVISIT: we are passing externalSchema and noNamespaceExternalSchema locations to XSDHandler , where
        //it stores namespace and location values.. now we are doing the same in XMLSchemaValidator,
        //we can pass the refernce of fLocationPairs and noNamespaceLocationPairs -nb
        // REVISIT: should we process these two properties here? why not just
        //  them on to xsdhandler.

        // reset schema handler and all traversal objects
        fSchemaHandler.reset(fXSIErrorReporter.fErrorReporter,
                             fEntityResolver, fSymbolTable,
                             fExternalSchemas, fExternalNoNamespaceSchema,
                             fGrammarPool);
        
        // register declaration pool
        fDeclPool.reset();
        if (fGrammarPool == null) {
            fCMBuilder.setDeclPool(fDeclPool);
            fSchemaHandler.setDeclPool(fDeclPool);
        } else {
            fCMBuilder.setDeclPool(null);
            fSchemaHandler.setDeclPool(null);
        } 

        //reset XSDDescripton
        fXSDDescription.reset() ;
        fLocationPairs.clear();
        fNoNamespaceLocationArray.resize(0 , 2) ;

        // initialize state
        fCurrentElemDecl = null;
        fNil = false;
        fCurrentPSVI = null;
        fCurrentType = null;
        fCurrentCM = null;
        fCurrCMState = null;
        fBuffer.setLength(0);
        fSawCharacters=false;
        fSawChildren=false;
        fValidationRoot = null;
        fSkipValidationDepth = -1;
        fPartialValidationDepth = -1;
        fElementDepth = -1;
        fChildCount = 0;

        // datatype normalization
        fFirstChunk = true;
        fTrailing = false;
        fNormalizedStr.setLength(0);
        fWhiteSpace = -1;
        fUnionType = false;
        fWhiteSpace = -1;
        fAugmentations.clear();
        fEntityRef = false;
        fInCDATA = false;

        fMatcherStack.clear();

        fValueStoreCache = new ValueStoreCache();

        fState4XsiType.setExtraChecking(false);
        fState4XsiType.setSymbolTable(symbolTable);
        fState4XsiType.setSymbolTable(symbolTable);
        fState4XsiType.setNamespaceSupport(fNamespaceSupport);

        fState4ApplyDefault.setFacetChecking(false);
        fState4ApplyDefault.setSymbolTable(symbolTable);
        fState4ApplyDefault.setSymbolTable(symbolTable);
        fState4ApplyDefault.setNamespaceSupport(fNamespaceSupport);

    } // reset(XMLComponentManager)

    //
    // FieldActivator methods
    //

    /**
     * Start the value scope for the specified identity constraint. This
     * method is called when the selector matches in order to initialize
     * the value store.
     *
     * @param identityConstraint The identity constraint.
     */
    public void startValueScopeFor(IdentityConstraint identityConstraint)
    throws XNIException {

        for (int i=0; i<identityConstraint.getFieldCount(); i++) {
            Field field = identityConstraint.getFieldAt(i);
            ValueStoreBase valueStore = fValueStoreCache.getValueStoreFor(field);
            valueStore.startValueScope();
        }

    } // startValueScopeFor(IdentityConstraint identityConstraint)

    /**
     * Request to activate the specified field. This method returns the
     * matcher for the field.
     *
     * @param field The field to activate.
     */
    public XPathMatcher activateField(Field field) throws XNIException {
        ValueStore valueStore = fValueStoreCache.getValueStoreFor(field);
        field.setMayMatch(true);
        XPathMatcher matcher = field.createMatcher(valueStore);
        fMatcherStack.addMatcher(matcher);
        matcher.startDocumentFragment(fSymbolTable);
        return matcher;
    } // activateField(Field):XPathMatcher

    /**
     * Ends the value scope for the specified identity constraint.
     *
     * @param identityConstraint The identity constraint.
     */
    public void endValueScopeFor(IdentityConstraint identityConstraint)
    throws XNIException {

        ValueStoreBase valueStore = fValueStoreCache.getValueStoreFor(identityConstraint);
        valueStore.endValueScope();

    } // endValueScopeFor(IdentityConstraint)

    // a utility method for Idnetity constraints
    private void activateSelectorFor(IdentityConstraint ic) throws XNIException {
        Selector selector = ic.getSelector();
        FieldActivator activator = this;
        if (selector == null)
            return;
        XPathMatcher matcher = selector.createMatcher(activator);
        fMatcherStack.addMatcher(matcher);
        matcher.startDocumentFragment(fSymbolTable);
    }

    //
    // Protected methods
    //

    /** ensure element stack capacity */
    void ensureStackCapacity() {

        if (fElementDepth == fElemDeclStack.length) {
            int newSize = fElementDepth + INC_STACK_SIZE;
            int[] newArrayI = new int[newSize];
            System.arraycopy(fChildCountStack, 0, newArrayI, 0, fElementDepth);
            fChildCountStack = newArrayI;

            XSElementDecl[] newArrayE = new XSElementDecl[newSize];
            System.arraycopy(fElemDeclStack, 0, newArrayE, 0, fElementDepth);
            fElemDeclStack = newArrayE;

            boolean[] newArrayB = new boolean[newSize];
            System.arraycopy(fNilStack, 0, newArrayB, 0, fElementDepth);
            fNilStack = newArrayB;

            XSTypeDecl[] newArrayT = new XSTypeDecl[newSize];
            System.arraycopy(fTypeStack, 0, newArrayT, 0, fElementDepth);
            fTypeStack = newArrayT;

            XSCMValidator[] newArrayC = new XSCMValidator[newSize];
            System.arraycopy(fCMStack, 0, newArrayC, 0, fElementDepth);
            fCMStack = newArrayC;

            boolean[] newArrayD = new boolean[newSize];
            System.arraycopy(fStringContent, 0, newArrayD, 0, fElementDepth);
            fStringContent = newArrayD;

            newArrayD = new boolean[newSize];
            System.arraycopy(fSawChildrenStack, 0, newArrayD, 0, fElementDepth);
            fSawChildrenStack = newArrayD;

            int[][] newArrayIA = new int[newSize][];
            System.arraycopy(fCMStateStack, 0, newArrayIA, 0, fElementDepth);
            fCMStateStack = newArrayIA;
        }

    } // ensureStackCapacity

    // handle start document
    void handleStartDocument(XMLLocator locator, String encoding) {

        if (fValidation)
            fValueStoreCache.startDocument();

    } // handleStartDocument(XMLLocator,String)

    void handleEndDocument() {

        if (fValidation)
            fValueStoreCache.endDocument();

    } // handleEndDocument()

    // handle character contents
    void handleCharacters(XMLString text) {

        fCurrentPSVI.fNormalizedValue = null;
        if (fSkipValidationDepth >= 0)
            return;

        String normalizedStr = null;
        boolean allWhiteSpace = true;

        // find out if type is union, what is whitespace,
        // determine if there is a need to do normalization
        if (fNormalizeData && !fEntityRef && !fInCDATA) {
            // if whitespace == -1 skip normalization, because it is a complexType
            if (fWhiteSpace != -1 && !fUnionType && fWhiteSpace != XSSimpleType.WS_PRESERVE) {
                // normalize data
                int spaces = normalizeWhitespace(text, fWhiteSpace == XSSimpleType.WS_COLLAPSE);
                int length = fNormalizedStr.length();
                if (length > 0) {
                    if (!fFirstChunk && (fWhiteSpace==XSSimpleType.WS_COLLAPSE) ) {
                        if (fTrailing) {
                            // previous chunk ended on whitespace
                            // insert whitespace
                         fNormalizedStr.insert(0, ' ');
                        } else if (spaces == 1 || spaces == 3) {
                            // previous chunk ended on character,
                            // this chunk starts with whitespace
                            fNormalizedStr.insert(0, ' ');
                        }
                    }
                }
                normalizedStr = fNormalizedStr.toString();
                fCurrentPSVI.fNormalizedValue = normalizedStr;
                fTrailing = (spaces > 1)?true:false;
            }
        }

        boolean mixed = false;
        if (fCurrentType != null && fCurrentType.getTypeCategory() == XSTypeDecl.COMPLEX_TYPE) {
              XSComplexTypeDecl ctype = (XSComplexTypeDecl)fCurrentType;
              if (ctype.fContentType == XSComplexTypeDecl.CONTENTTYPE_MIXED) {
                    mixed = true;
              }
        }

        if (DEBUG) {
         System.out.println("==>characters()"+fCurrentType.getName()+":"+mixed);
        }

        if (mixed || fWhiteSpace !=-1 || fUnionType) {
            // don't check characters: since it is either
            // a) mixed content model - we don't care if there were some characters
            // b) simpleType/simpleContent - in which case it is data in ELEMENT content
        }
        else  {

            if (DEBUG) {
             System.out.println("==>check for whitespace");
            }
            // data outside of element content
            for (int i=text.offset; i< text.offset+text.length; i++) {
                if (!XMLChar.isSpace(text.ch[i])) {
                    allWhiteSpace = false;
                    break;
                }
            }
        }


        // we saw first chunk of characters
        fFirstChunk = false;

        // save normalized value for validation purposes
        if (fNil) {
            // if element was nil and there is some character data
            // we should expose it to the user
            // otherwise error does not make much sense
            fCurrentPSVI.fNormalizedValue = null;
            fBuffer.append(text.toString());
        }
        if (normalizedStr != null) {
            fBuffer.append(normalizedStr);
        } else {
            fBuffer.append(text.toString());
        }


        if (!allWhiteSpace) {
            fSawCharacters = true;
        }

        // call all active identity constraints
        int count = fMatcherStack.getMatcherCount();
        for (int i = 0; i < count; i++) {
            XPathMatcher matcher = fMatcherStack.getMatcherAt(i);
            matcher.characters(text);
        }
    } // handleCharacters(XMLString)

    /**
     * Normalize whitespace in an XMLString according to the rules defined
     * in XML Schema specifications.
     * @param value    The string to normalize.
     * @param collapse replace or collapse
     * @returns 0 if no triming is done or if there is neither leading nor
     *            trailing whitespace,
     *          1 if there is only leading whitespace,
     *          2 if there is only trailing whitespace,
     *          3 if there is both leading and trailing whitespace.
     */
    private int normalizeWhitespace( XMLString value, boolean collapse) {
        boolean skipSpace = collapse;
        boolean sawNonWS = false;
        int leading = 0;
        int trailing = 0;
        int c;
        int size = value.offset+value.length;
        fNormalizedStr.setLength(0);
        for (int i = value.offset; i < size; i++) {
            c = value.ch[i];
            if (c == 0x20 || c == 0x0D || c == 0x0A || c == 0x09) {
                if (!skipSpace) {
                    // take the first whitespace as a space and skip the others
                    fNormalizedStr.append(' ');
                    skipSpace = collapse;
                }
                if (!sawNonWS) {
                    // this is a leading whitespace, record it
                    leading = 1;
                }
            }
            else {
                fNormalizedStr.append((char)c);
                skipSpace = false;
                sawNonWS = true;
            }
        }
        if (skipSpace) {
            c = fNormalizedStr.length();
            if ( c != 0) {
                // if we finished on a space trim it but also record it
                fNormalizedStr.setLength (--c);
                trailing = 2;
            }
            else if (leading != 0 && !sawNonWS) {
                // if all we had was whitespace we skipped record it as
                // trailing whitespace as well
                trailing = 2;
            }
        }
        return collapse ? leading + trailing : 0;
    }


    // handle ignorable whitespace
    void handleIgnorableWhitespace(XMLString text) {

        if (fSkipValidationDepth >= 0)
            return;

        // call all active identity constraints
        int count = fMatcherStack.getMatcherCount();
        for (int i = 0; i < count; i++) {
            XPathMatcher matcher = fMatcherStack.getMatcherAt(i);
            matcher.characters(text);
        }

    } // handleIgnorableWhitespace(XMLString)

    /** Handle element. */
    Augmentations handleStartElement(QName element, XMLAttributes attributes, Augmentations augs) {

        if (DEBUG) {
            System.out.println("==>handleStartElement: " +element);
        }
        // should really determine whether a null augmentation is to
        // be returned on a case-by-case basis, rather than assuming
        // this method will always produce augmentations...
        if(augs == null) {
            augs = fAugmentations;
            augs.clear();
        }


        // we receive prefix binding events before this one,
        // so at this point, the prefix bindings for this element is done,
        // and we need to push context when we receive another prefix binding.

        // but if fPushForNextBinding is still true, that means there has
        // been no prefix binding for this element. we still need to push
        // context, because the context is always popped in end element.
        if (fPushForNextBinding)
            fNamespaceSupport.pushContext();
        else
            fPushForNextBinding = true;

        // root element
        if (fElementDepth == -1) {
            // at this point we assume that no XML schemas found in the instance document
            // thus we will not validate in the case dynamic feature is on or we found dtd grammar
            fDoValidation = fValidation && !(fValidationManager.isGrammarFound() || fDynamicValidation);

            //store the external schema locations, these locations will be set at root element, so any other
            // schemaLocation declaration for the same namespace will be effectively ignored.. becuase we
            // choose to take first location hint available for a particular namespace.
            storeLocations(fExternalSchemas, fExternalNoNamespaceSchema) ;

            //REVISIT: this JAXP processing shouldn't be done
            //in XMLSchemaValidator but in a separate component responsible for pre-parsing grammars
            // and SchemaValidator should be given these preParsed grammars before this component
            //attempts to validate -nb.
            processJAXPSchemaSource( fJaxpSchemaSource , fEntityResolver );
        }

        fCurrentPSVI = (ElementPSVImpl)augs.getItem(Constants.ELEMENT_PSVI);
        if (fCurrentPSVI == null) {
            fCurrentPSVI = fElemPSVI;
            augs.putItem(Constants.ELEMENT_PSVI, fCurrentPSVI);
        }
        fCurrentPSVI.reset();

        // get xsi:schemaLocation and xsi:noNamespaceSchemaLocation attributes,
        // parse them to get the grammars

        String sLocation = attributes.getValue(URI_XSI, XSI_SCHEMALOCATION);
        String nsLocation = attributes.getValue(URI_XSI, XSI_NONAMESPACESCHEMALOCATION);
        //store the location hints..  we need to do it so that we can defer the loading of grammar until
        //there is a reference to a component from that namespace. To provide location hints to the
        //application for a namespace
        storeLocations(sLocation, nsLocation) ;

        //REVISIT: We should do the same in XSDHandler also... we should not
        //load the actual grammar (eg. import) unless there is reference to it.

        // REVISIT: we should not rely on presence of
        //          schemaLocation or noNamespaceSchemaLocation
        //          attributes
        if (sLocation !=null || nsLocation !=null) {
            // if we found grammar we should attempt to validate
            // based on values of validation & schema features
            // only

            fDoValidation = fValidation;
        }
        
        // update normalization flags
        if (fNormalizeData) {
            // reset values
            fFirstChunk = true;
            fUnionType  = false;
            fWhiteSpace = -1;
        }

        // if we are in the content of "skip", then just skip this element
        // REVISIT:  is this the correct behaviour for ID constraints?  -NG
        if (fSkipValidationDepth >= 0) {
            fElementDepth++;
            return augs;
        }

        // if we are not skipping this element, and there is a content model,
        // we try to find the corresponding decl object for this element.
        // the reason we move this part of code here is to make sure the
        // error reported here (if any) is stored within the parent element's
        // context, instead of that of the current element.
        Object decl = null;
        if (fSkipValidationDepth < 0 && fCurrentCM != null) {
            decl = fCurrentCM.oneTransition(element, fCurrCMState, fSubGroupHandler);
            // it could be an element decl or a wildcard decl
            if (fCurrCMState[0] == XSCMValidator.FIRST_ERROR && fDoValidation) {
                XSComplexTypeDecl ctype = (XSComplexTypeDecl)fCurrentType;
                //REVISIT: is it the only case we will have particle = null?
                if (ctype.fParticle != null) {
                    reportSchemaError("cvc-complex-type.2.4.a", new Object[]{element.rawname, ctype.fParticle.toString()});
                }
                else {
                    reportSchemaError("cvc-complex-type.2.4.a", new Object[]{element.rawname, "mixed with no element content"});
                }
            }
        }

        // push error reporter context: record the current position
        fXSIErrorReporter.pushContext();

        // if it's not the root element, we push the current states in the stacks
        if (fElementDepth != -1) {
            ensureStackCapacity();
            fChildCountStack[fElementDepth] = fChildCount+1;
            fChildCount = 0;
            fElemDeclStack[fElementDepth] = fCurrentElemDecl;
            fNilStack[fElementDepth] = fNil;
            fTypeStack[fElementDepth] = fCurrentType;
            fCMStack[fElementDepth] = fCurrentCM;
            fCMStateStack[fElementDepth] = fCurrCMState;
            fStringContent[fElementDepth] = fSawCharacters;
            fSawChildrenStack[fElementDepth] = fSawChildren;
        }
        
        // increase the element depth after we've saved 
        // all states for the parent element
        fElementDepth++;
        fCurrentElemDecl = null;
        XSWildcardDecl wildcard = null;
        fCurrentType = null;
        fNil = false;

        // and the buffer to hold the value of the element
        fBuffer.setLength(0);
        fSawCharacters = false;
        fSawChildren = false;

        // check what kind of declaration the "decl" from 
        // oneTransition() maps to
        if (decl != null) {
            if (decl instanceof XSElementDecl) {
                fCurrentElemDecl = (XSElementDecl)decl;
            }
            else {
                wildcard = (XSWildcardDecl)decl;
            }
        }

        // if the wildcard is skip, then return
        if (wildcard != null && wildcard.fProcessContents == XSWildcardDecl.PC_SKIP) {
            fSkipValidationDepth = fElementDepth;
            return augs;
        }

        // try again to get the element decl:
        // case 1: find declaration for root element
        // case 2: find declaration for element from another namespace
        if (fCurrentElemDecl == null) {
            //try to find schema grammar by different means..
            SchemaGrammar sGrammar = findSchemaGrammar(XSDDescription.CONTEXT_ELEMENT , 
                                                       element.uri , null , element, attributes ) ;

            if (sGrammar != null){
                fCurrentElemDecl = sGrammar.getGlobalElementDecl(element.localpart);
            }

        }

        // Element Locally Valid (Element)
        // 2 Its {abstract} must be false.
        if (fCurrentElemDecl != null && fCurrentElemDecl.getIsAbstract())
            reportSchemaError("cvc-elt.2", new Object[]{element.rawname});

        if (fCurrentElemDecl != null) {
            // then get the type
            fCurrentType = fCurrentElemDecl.fType;
        }

        // get type from xsi:type
        String xsiType = attributes.getValue(URI_XSI, XSI_TYPE);
        if (xsiType != null)
            fCurrentType = getAndCheckXsiType(element, xsiType, attributes);

        // if the element decl is not found
        if (fCurrentType == null) {
            if (fDoValidation) {
                // if this is the validation root, report an error, because
                // we can't find eith decl or type for this element
                // REVISIT: should we report error, or warning?
                if (fElementDepth == 0) {
                    // report error, because it's root element
                    reportSchemaError("cvc-elt.1", new Object[]{element.rawname});
                }
                // if wildcard = strict, report error
                else if (wildcard != null &&
                         wildcard.fProcessContents == XSWildcardDecl.PC_STRICT) {
                    // report error, because wilcard = strict
                    reportSchemaError("cvc-complex-type.2.4.c", new Object[]{element.rawname});
                }
            }
            // no element decl or type found for this element.
            // Allowed by the spec, we can choose to either laxly assess this
            // element, or to skip it. Now we choose lax assessment.
            // REVISIT: IMO, we should perform lax assessment when validation
            // feature is on, and skip when dynamic validation feature is on.
            fCurrentType = SchemaGrammar.fAnyType;
        }

        // make the current element validation root
        if (fElementDepth == 0) {
            fValidationRoot = element.rawname;
        }

        // PSVI: add validation context
        fCurrentPSVI.fValidationContext = fValidationRoot;
        // PSVI: add element declaration
        fCurrentPSVI.fDeclaration = fCurrentElemDecl;
        // PSVI: add element type
        fCurrentPSVI.fTypeDecl = fCurrentType;

        // Element Locally Valid (Type)
        // 2 Its {abstract} must be false.
        if (fCurrentType.getTypeCategory() == XSTypeDecl.COMPLEX_TYPE) {
            XSComplexTypeDecl ctype = (XSComplexTypeDecl)fCurrentType;
            if (ctype.getIsAbstract()) {
                reportSchemaError("cvc-type.2", new Object[]{"Element " + element.rawname + " is declared with a type that is abstract.  Use xsi:type to specify a non-abstract type"});
            }
            if (fNormalizeData) {
                // find out if the content type is simple and if variety is union
                // to be able to do character normalization
                if (ctype.fContentType == XSComplexTypeDecl.CONTENTTYPE_SIMPLE) {
                        if (ctype.fXSSimpleType.getVariety() == XSSimpleType.VARIETY_UNION) {
                            fUnionType = true;
                        } else {
                            try {
                                fWhiteSpace = ctype.fXSSimpleType.getWhitespace();
                            } catch (DatatypeException e){
                                // do nothing
                            }
                        }
                }
            }
        }
        // normalization
        if (fNormalizeData && fCurrentType.getTypeCategory() == XSTypeDecl.SIMPLE_TYPE) {
            // if !union type
             XSSimpleType dv = (XSSimpleType)fCurrentType;
             if (dv.getVariety() == XSSimpleType.VARIETY_UNION) {
                    fUnionType = true;
             } else {
                 try {
                    fWhiteSpace = dv.getWhitespace();
                 } catch (DatatypeException e){
                     // do nothing
                 }
             }
        }


        // then try to get the content model
        fCurrentCM = null;
        if (fCurrentType.getTypeCategory() == XSTypeDecl.COMPLEX_TYPE) {
            fCurrentCM = ((XSComplexTypeDecl)fCurrentType).getContentModel(fCMBuilder);
        }

        // and get the initial content model state
        fCurrCMState = null;
        if (fCurrentCM != null)
            fCurrCMState = fCurrentCM.startContentModel();

        // get information about xsi:nil
        String xsiNil = attributes.getValue(URI_XSI, XSI_NIL);
        // only deal with xsi:nil when there is an element declaration
        if (xsiNil != null && fCurrentElemDecl != null)
            fNil = getXsiNil(element, xsiNil);

        // now validate everything related with the attributes
        // first, get the attribute group
        XSAttributeGroupDecl attrGrp = null;
        if (fCurrentType.getTypeCategory() == XSTypeDecl.COMPLEX_TYPE) {
            XSComplexTypeDecl ctype = (XSComplexTypeDecl)fCurrentType;
            attrGrp = ctype.fAttrGrp;
        }
        processAttributes(element, attributes, attrGrp);

        // activate identity constraints
        if (fDoValidation) {
            fValueStoreCache.startElement();
            fMatcherStack.pushContext();
            if (fCurrentElemDecl != null) {
                fValueStoreCache.initValueStoresFor(fCurrentElemDecl);
                int icCount = fCurrentElemDecl.fIDCPos;
                int uniqueOrKey = 0;
                for (;uniqueOrKey < icCount; uniqueOrKey++) {
                    if (fCurrentElemDecl.fIDConstraints[uniqueOrKey].getCategory() != IdentityConstraint.IC_KEYREF) {
                        activateSelectorFor(fCurrentElemDecl.fIDConstraints[uniqueOrKey]);
                    }
                    else
                        break;
                }
                for (int keyref = uniqueOrKey; keyref < icCount; keyref++) {
                    activateSelectorFor((IdentityConstraint)fCurrentElemDecl.fIDConstraints[keyref]);
                }
            }

            // call all active identity constraints
            int count = fMatcherStack.getMatcherCount();
            for (int i = 0; i < count; i++) {
                XPathMatcher matcher = fMatcherStack.getMatcherAt(i);
                matcher.startElement(element, attributes, fCurrentElemDecl);
            }
        }
        return augs;

    } // handleStartElement(QName,XMLAttributes,boolean)


    /**
     *  Handle end element. If there is not text content, and there is a
     *  {value constraint} on the corresponding element decl, then
     * set the fDefaultValue XMLString representing the default value.
     */
    Augmentations handleEndElement(QName element, Augmentations augs) {

        if(augs == null) { // again, always assume adding augmentations...
            augs = fAugmentations;
            augs.clear();
        }

        fCurrentPSVI = (ElementPSVImpl)augs.getItem(Constants.ELEMENT_PSVI);
        if (fCurrentPSVI == null) {
            fCurrentPSVI = fElemPSVI;
            augs.putItem(Constants.ELEMENT_PSVI, fCurrentPSVI);
        }
        fCurrentPSVI.reset();

        // if we are skipping, return
        if (fSkipValidationDepth >= 0) {
            // but if this is the top element that we are skipping,
            // restore the states.
            if (fSkipValidationDepth == fElementDepth &&
                fSkipValidationDepth > 0) {
                // set the partial validation depth to the depth of parent
                fPartialValidationDepth = fSkipValidationDepth-1;
                fSkipValidationDepth = -1;
                fElementDepth--;
                fChildCount = fChildCountStack[fElementDepth];
                fCurrentElemDecl = fElemDeclStack[fElementDepth];
                fNil = fNilStack[fElementDepth];
                fCurrentType = fTypeStack[fElementDepth];
                fCurrentCM = fCMStack[fElementDepth];
                fCurrCMState = fCMStateStack[fElementDepth];
                fSawCharacters = fStringContent[fElementDepth];
                fSawChildren = fSawChildrenStack[fElementDepth];
            }
            else {
                fElementDepth--;
            }

            // need to pop context so that the bindings for this element is
            // discarded.
            fNamespaceSupport.popContext();

            // pop error reporter context: get all errors for the current
            // element, and remove them from the error list
            // String[] errors = fXSIErrorReporter.popContext();

            // PSVI: validation attempted:
            // use default values in psvi item for
            // validation attempted, validity, and error codes

            // check extra schema constraints on root element
            if (fElementDepth == -1 && fDoValidation && fFullChecking) {
                XSConstraints.fullSchemaChecking(fGrammarBucket, fSubGroupHandler, fCMBuilder, fXSIErrorReporter.fErrorReporter);
            }

            fDefaultValue = null;
            return augs;
        }

        // now validate the content of the element
        XMLString defaultValue = processElementContent(element);

        // Element Locally Valid (Element)
        // 6 The element information item must be valid with respect to each of the {identity-constraint definitions} as per Identity-constraint Satisfied (3.11.4).

        // call matchers and de-activate context
        int oldCount = fMatcherStack.getMatcherCount();
        for (int i = oldCount - 1; i >= 0; i--) {
            XPathMatcher matcher = fMatcherStack.getMatcherAt(i);
            matcher.endElement(element, fCurrentElemDecl);
        }
        if (fMatcherStack.size() > 0) {
            fMatcherStack.popContext();
        }
        int newCount = fMatcherStack.getMatcherCount();
        // handle everything *but* keyref's.
        for (int i = oldCount - 1; i >= newCount; i--) {
            XPathMatcher matcher = fMatcherStack.getMatcherAt(i);
            IdentityConstraint id;
            if ((id = matcher.getIDConstraint()) != null && id.getCategory() != IdentityConstraint.IC_KEYREF) {
                matcher.endDocumentFragment();
                fValueStoreCache.transplant(id);
            }
            else if (id == null)
                matcher.endDocumentFragment();
        }
        // now handle keyref's/...
        for (int i = oldCount - 1; i >= newCount; i--) {
            XPathMatcher matcher = fMatcherStack.getMatcherAt(i);
            IdentityConstraint id;
            if ((id = matcher.getIDConstraint()) != null && id.getCategory() == IdentityConstraint.IC_KEYREF) {
                ValueStoreBase values = fValueStoreCache.getValueStoreFor(id);
                if (values != null) // nothing to do if nothing matched!
                    values.endDocumentFragment();
                matcher.endDocumentFragment();
            }
        }
        fValueStoreCache.endElement();

        // have we reached the end tag of the validation root?
        if (fElementDepth == 0) {
            if (fDoValidation) {
                // 7 If the element information item is the validation root, it must be valid per Validation Root Valid (ID/IDREF) (3.3.4).
                String invIdRef = fValidationState.checkIDRefID();
                if (invIdRef != null) {
                    reportSchemaError("cvc-id.1", new Object[]{invIdRef});
                }
            }
            fValidationState.resetIDTables();
        }

        // PSVI: validation attempted
        if (fElementDepth <= fPartialValidationDepth) {
            // the element had child with a content skip.
            fCurrentPSVI.fValidationAttempted = ElementPSVI.PARTIAL_VALIDATION;
            if (fElementDepth == fPartialValidationDepth) {
                // set depth to the depth of the parent
                fPartialValidationDepth--;
            }
        }
        else {
            fCurrentPSVI.fValidationAttempted = ElementPSVI.FULL_VALIDATION;
        }


        // decrease element depth and restore states
        fElementDepth--;
        if (fElementDepth == -1) {
            if (fDoValidation) {
                // check extra schema constraints
                if (fFullChecking) {
                    XSConstraints.fullSchemaChecking(fGrammarBucket, fSubGroupHandler, fCMBuilder, fXSIErrorReporter.fErrorReporter);
                }
            }
        }
        else {
            // get the states for the parent element.
            fChildCount = fChildCountStack[fElementDepth];
            fCurrentElemDecl = fElemDeclStack[fElementDepth];
            fNil = fNilStack[fElementDepth];
            fCurrentType = fTypeStack[fElementDepth];
            fCurrentCM = fCMStack[fElementDepth];
            fCurrCMState = fCMStateStack[fElementDepth];
            fSawCharacters = fStringContent[fElementDepth];
            fSawChildren = fSawChildrenStack[fElementDepth];
        }

        // need to pop context so that the bindings for this element is
        // discarded.
        fNamespaceSupport.popContext();

        // pop error reporter context: get all errors for the current
        // element, and remove them from the error list
        String[] errors = fXSIErrorReporter.popContext();

        // PSVI: error codes
        fCurrentPSVI.fErrorCodes = errors;
        // PSVI: validity
        fCurrentPSVI.fValidity = (errors == null) ? ElementPSVI.VALID_VALIDITY
                                                  : ElementPSVI.INVALID_VALIDITY;

        fDefaultValue = defaultValue;


        // reset normalization values
        if (fNormalizeData) {
            fTrailing = false;
            fUnionType = false;
            fWhiteSpace = -1;
        }

        return augs;
    } // handleEndElement(QName,boolean)*/

    void handleStartPrefix(String prefix, String uri) {
        // push namespace context if necessary
        if (fPushForNextBinding) {
            fNamespaceSupport.pushContext();
            fPushForNextBinding = false;
        }

        // add prefix declaration to the namespace support
        fNamespaceSupport.declarePrefix(prefix, uri.length() != 0 ? uri : null);
    }

    private class LocationArray{

        int length ;
        String [] locations = new String[2];

        public void resize(int oldLength , int newLength){
            String [] temp = new String[newLength] ;
            System.arraycopy(locations, 0, temp, 0, Math.min(oldLength, newLength));
            locations = temp ;
            length = Math.min(oldLength, newLength);
        }

        public void setLocation(String location){
            if(length >= locations.length ){
                resize(length, Math.max(1, length*2));
            }
            locations[length++] = location;
        }//setLocation()

        public String [] getLocationArray(){
            if(length < locations.length ){
                resize(locations.length, length);
            }
            return locations;
        }//getLocationArray()

        public String getFirstLocation(){
            return length > 0 ? locations[0] : null;
        }

        public int getLength(){
            return length ;
        }

    } //locationArray

    void storeLocations(String sLocation, String nsLocation){

        if (sLocation != null) {
            StringTokenizer t = new StringTokenizer(sLocation, " \n\t\r");
            String namespace, location;
            while (t.hasMoreTokens()) {
                namespace = fSymbolTable.addSymbol(t.nextToken ());

                if (!t.hasMoreTokens()) {
                    fXSIErrorReporter.reportError(XSMessageFormatter.SCHEMA_DOMAIN,
                                                  "SchemaLocation",
                                                  new Object[]{sLocation},
                                                  XMLErrorReporter.SEVERITY_WARNING);
                    break;
                }

                Object locationArray = fLocationPairs.get(namespace) ;

                if(locationArray == null){
                    locationArray = new LocationArray() ;
                    //add it into hashtable...
                    fLocationPairs.put(namespace, locationArray);
                }

                location = t.nextToken();
                ((LocationArray)locationArray).setLocation(location);
            }

        }
        if (nsLocation != null) {
            fNoNamespaceLocationArray.setLocation(nsLocation);
        }

    }//storeLocations


    //this is the function where logic of retrieving grammar is written , parser first tries to get the grammar from
    //the local pool, if not in local pool, it gives chance to application to be able to retrieve the grammar, then it
    //tries to parse the grammar using location hints from the give namespace.
    SchemaGrammar findSchemaGrammar(short contextType , String namespace , QName enclosingElement, QName triggeringComponet, XMLAttributes attributes ){
        SchemaGrammar grammar = null ;
        //get the grammar from local pool...
        grammar = fGrammarBucket.getGrammar(namespace);
        if (grammar == null){
            fXSDDescription.reset();
            fXSDDescription.fContextType = contextType ;
            fXSDDescription.fTargetNamespace = namespace ;
            fXSDDescription.fEnclosedElementName = enclosingElement ;
            fXSDDescription.fTriggeringComponent = triggeringComponet ;
            fXSDDescription.fAttributes = attributes ;

            Object locationArray = null ;
            if( namespace != null){
                locationArray = fLocationPairs.get(namespace) ;
                if(locationArray != null){
                    String [] temp = ((LocationArray)locationArray).getLocationArray() ;
                    fXSDDescription.fLocationHints = new String [temp.length] ;
                    System.arraycopy(temp, 0 , fXSDDescription.fLocationHints, 0, temp.length );
                }
            }else{
                String [] temp = fNoNamespaceLocationArray.getLocationArray() ;
                fXSDDescription.fLocationHints = new String [temp.length] ;
                System.arraycopy(temp, 0 , fXSDDescription.fLocationHints, 0, temp.length );
            }

            // give a chance to application to be able to retreive the grammar.
            //REVISIT: construct empty pool... we dont have to check for the null condition
            //give a chance to application to be able to retreive the grammar.
            if (fGrammarPool != null){
                grammar = (SchemaGrammar)fGrammarPool.retrieveGrammar(fXSDDescription);
                if (grammar != null) {
                    // put this grammar into the bucket, along with grammars
                    // imported by it (directly or indirectly)
                    if (!fGrammarBucket.putGrammar(grammar, true)) {
                        // REVISIT: a conflict between new grammar(s) and grammars
                        // in the bucket. What to do? A warning? An exception?
                        fXSIErrorReporter.fErrorReporter.reportError(XSMessageFormatter.SCHEMA_DOMAIN,
                                                                     "GrammarConflict", null,
                                                                     XMLErrorReporter.SEVERITY_WARNING);
                        grammar = null;
                    }
                }
            }
            if (grammar == null) {
                // try to parse the grammar using location hints from that namespace..
                grammar = fSchemaHandler.parseSchema(fXSDDescription);
            }
        }

        return grammar ;

    }//findSchemaGrammar

    /**
     * Translate the various JAXP SchemaSource property types to XNI
     * XMLInputSource.  Valid types are: String, org.xml.sax.InputSource,
     * InputStream, File, or Object[] of any of previous types.
     */
    private void processJAXPSchemaSource(Object val, XMLEntityResolver xer) {
        if (val == null) {
            return;
        }

        Class componentType = val.getClass().getComponentType();
        XMLInputSource xis = null;
        String sid = null;
        if (componentType == null) {
            // Not an array
            xis = XSD2XMLInputSource(val, xer);
            sid = xis.getSystemId();
            fXSDDescription.reset();
            fXSDDescription.fContextType = XSDDescription.CONTEXT_PREPARSE;
            if (sid != null) {
                fXSDDescription.setLiteralSystemId(sid);
                fXSDDescription.setExpandedSystemId(sid);
                fXSDDescription.fLocationHints = new String[]{sid};
            }
            fSchemaHandler.parseSchema(xis, fXSDDescription);
            return ;
        } else if (componentType != Object.class) {
            // Not an Object[]
            throw new XMLConfigurationException(
                XMLConfigurationException.NOT_SUPPORTED, JAXP_SCHEMA_SOURCE);
        }

        Object[] objArr = (Object[]) val;
        for (int i = 0; i < objArr.length; i++) {
            xis = XSD2XMLInputSource(objArr[i], xer);
            sid = xis.getSystemId();
            fXSDDescription.reset();
            fXSDDescription.fContextType = XSDDescription.CONTEXT_PREPARSE;
            if (sid != null) {
                fXSDDescription.setLiteralSystemId(sid);
                fXSDDescription.setExpandedSystemId(sid);
                fXSDDescription.fLocationHints = new String[]{sid};
            }
            fSchemaHandler.parseSchema(xis, fXSDDescription);
        }
    }

    private XMLInputSource XSD2XMLInputSource(
            Object val, XMLEntityResolver entityResolver)
    {
        if (val instanceof String) {
            // String value is treated as a URI that is passed through the
            // EntityResolver
            String loc = (String) val;

            if (entityResolver != null) {

                fResourceIdentifier.setValues(null, loc, null, null);
                XMLInputSource xis = null;
                try {
                    xis = entityResolver.resolveEntity(fResourceIdentifier);
                } catch (IOException ex) {
                    reportSchemaError("schema_reference.4",
                                      new Object[] { loc });
                }
                if (xis == null) {
                    // REVISIT: can this happen?
                    // Treat value as a URI and pass in as systemId
                    return new XMLInputSource(null, loc, null);
                }
                return xis;
            }
        } else if (val instanceof InputSource) {
            return SAX2XMLInputSource((InputSource) val);
        } else if (val instanceof InputStream) {
            return new XMLInputSource(null, null, null,
                                      (InputStream) val, null);
        } else if (val instanceof File) {
            File file = (File) val;
            InputStream is = null;
            try {
                is = new BufferedInputStream(new FileInputStream(file));
            } catch (FileNotFoundException ex) {
                reportSchemaError("schema_reference.4",
                                  new Object[] { file.toString() });
            }
            return new XMLInputSource(null, null, null, is, null);
        }
        throw new XMLConfigurationException(
            XMLConfigurationException.NOT_SUPPORTED, JAXP_SCHEMA_SOURCE);
    }


     //Convert a SAX InputSource to an equivalent XNI XMLInputSource

    private static XMLInputSource SAX2XMLInputSource(InputSource sis) {
        String publicId = sis.getPublicId();
        String systemId = sis.getSystemId();

        Reader charStream = sis.getCharacterStream();
        if (charStream != null) {
            return new XMLInputSource(publicId, systemId, null, charStream,
                                      null);
        }

        InputStream byteStream = sis.getByteStream();
        if (byteStream != null) {
            return new XMLInputSource(publicId, systemId, null, byteStream,
                                      sis.getEncoding());
        }

        return new XMLInputSource(publicId, systemId, null);
    }

    XSTypeDecl getAndCheckXsiType(QName element, String xsiType, XMLAttributes attributes) {
        // This method also deals with clause 1.2.1.2 of the constraint
        // Validation Rule: Schema-Validity Assessment (Element)

        // Element Locally Valid (Element)
        // 4 If there is an attribute information item among the element information item's [attributes] whose [namespace name] is identical to http://www.w3.org/2001/XMLSchema-instance and whose [local name] is type, then all of the following must be true:
        // 4.1 The normalized value of that attribute information item must be valid with respect to the built-in QName simple type, as defined by String Valid (3.14.4);
        QName typeName = null;
        try {
            typeName = (QName)fQNameDV.validate(xsiType, fValidationState, null);
        }
        catch (InvalidDatatypeValueException e) {
            reportSchemaError("cvc-elt.4.1", new Object[]{element.rawname, URI_XSI+","+XSI_TYPE, xsiType});
            return null;
        }

        // 4.2 The local name and namespace name (as defined in QName Interpretation (3.15.3)), of the actual value of that attribute information item must resolve to a type definition, as defined in QName resolution (Instance) (3.15.4)
        XSTypeDecl type = null;
        // if the namespace is schema namespace, first try built-in types
        if (typeName.uri == URI_SCHEMAFORSCHEMA) {
            type = SchemaGrammar.SG_SchemaNS.getGlobalTypeDecl(typeName.localpart);
        }
        // if it's not schema built-in types, then try to get a grammar
        if (type == null) {
            //try to find schema grammar by different means....
            SchemaGrammar grammar = findSchemaGrammar( XSDDescription.CONTEXT_XSITYPE , typeName.uri , element , typeName , attributes);

            if (grammar != null)
                type = grammar.getGlobalTypeDecl(typeName.localpart);
        }
        // still couldn't find the type, report an error
        if (type == null) {
            reportSchemaError("cvc-elt.4.2", new Object[]{element.rawname, xsiType});
            return null;
        }

        // if there is no current type, set this one as current.
        // and we don't need to do extra checking
        if (fCurrentType != null) {
            // 4.3 The local type definition must be validly derived from the {type definition} given the union of the {disallowed substitutions} and the {type definition}'s {prohibited substitutions}, as defined in Type Derivation OK (Complex) (3.4.6) (if it is a complex type definition), or given {disallowed substitutions} as defined in Type Derivation OK (Simple) (3.14.6) (if it is a simple type definition).
            short block = fCurrentElemDecl.fBlock;
            if (fCurrentType.getTypeCategory() == XSTypeDecl.COMPLEX_TYPE)
                block |= ((XSComplexTypeDecl)fCurrentType).fBlock;
            if (!XSConstraints.checkTypeDerivationOk(type, fCurrentType, block))
                reportSchemaError("cvc-elt.4.3", new Object[]{element.rawname, xsiType});
        }

        return type;
    }//getAndCheckXsiType

    boolean getXsiNil(QName element, String xsiNil) {
        // Element Locally Valid (Element)
        // 3 The appropriate case among the following must be true:
        // 3.1 If {nillable} is false, then there must be no attribute information item among the element information item's [attributes] whose [namespace name] is identical to http://www.w3.org/2001/XMLSchema-instance and whose [local name] is nil.
        if (fCurrentElemDecl != null && !fCurrentElemDecl.getIsNillable()) {
            reportSchemaError("cvc-elt.3.1", new Object[]{element.rawname, URI_XSI+","+XSI_NIL});
        }
        // 3.2 If {nillable} is true and there is such an attribute information item and its actual value is true , then all of the following must be true:
        // 3.2.2 There must be no fixed {value constraint}.
        else {
            String value = xsiNil.trim();
            if (value.equals(SchemaSymbols.ATTVAL_TRUE) ||
                value.equals(SchemaSymbols.ATTVAL_TRUE_1)) {
                if (fCurrentElemDecl != null &&
                    fCurrentElemDecl.getConstraintType() == XSConstants.VC_FIXED) {
                    reportSchemaError("cvc-elt.3.2.2", new Object[]{element.rawname, URI_XSI+","+XSI_NIL});
                }
                return true;
            }
        }
        return false;
    }

    void processAttributes(QName element, XMLAttributes attributes, XSAttributeGroupDecl attrGrp) {

        // REVISIT: should we assume that XMLAttributeImpl removes
        //          all augmentations from Augmentations? if yes.. we loose objects
        //         if no - we always produce attribute psvi objects which may not be filled in
        //         in this case we need to create/reset here all objects
        Augmentations augs = null;
        AttributePSVImpl attrPSVI = null;
        for (int k=0;k<attributes.getLength();k++) {
            augs = attributes.getAugmentations(k);
            attrPSVI = (AttributePSVImpl) augs.getItem(Constants.ATTRIBUTE_PSVI);
            if (attrPSVI != null) {
                attrPSVI.reset();
            } else {
                attrPSVI= new AttributePSVImpl();
                augs.putItem(Constants.ATTRIBUTE_PSVI, attrPSVI);
            }
            // PSVI attribute: validation context
            attrPSVI.fValidationContext = fValidationRoot;
        }
 


        
        // add default attributes
        if (attrGrp != null) {
            addDefaultAttributes(element, attributes, attrGrp);
        }

        // if we don't do validation, we don't need to validate the attributes
        if (!fDoValidation || attributes.getLength() == 0){
            // PSVI: validity is unknown, and validation attempted is none
            // this is a default value thus we should not set anything else here.
            return;
        }

        // Element Locally Valid (Type)
        // 3.1.1 The element information item's [attributes] must be empty, excepting those
        // whose [namespace name] is identical to http://www.w3.org/2001/XMLSchema-instance and
        // whose [local name] is one of type, nil, schemaLocation or noNamespaceSchemaLocation.
        if (fCurrentType == null || fCurrentType.getTypeCategory() == XSTypeDecl.SIMPLE_TYPE) {
            int attCount = attributes.getLength();

            for (int index = 0; index < attCount; index++) {
                attributes.getName(index, fTempQName);

                // get attribute PSVI
                attrPSVI = (AttributePSVImpl)attributes.getAugmentations(index).getItem(Constants.ATTRIBUTE_PSVI);
                
                // for the 4 xsi attributes, get appropriate decl, and validate
                if (fTempQName.uri == URI_XSI) {
                    XSAttributeDecl attrDecl = null;
                    if (fTempQName.localpart == XSI_SCHEMALOCATION)
                        attrDecl = SchemaGrammar.SG_XSI.getGlobalAttributeDecl(XSI_SCHEMALOCATION);
                    else if (fTempQName.localpart == XSI_NONAMESPACESCHEMALOCATION)
                        attrDecl = SchemaGrammar.SG_XSI.getGlobalAttributeDecl(XSI_NONAMESPACESCHEMALOCATION);
                    else if (fTempQName.localpart == XSI_NIL)
                        attrDecl = SchemaGrammar.SG_XSI.getGlobalAttributeDecl(XSI_NIL);
                    else if (fTempQName.localpart == XSI_TYPE)
                        attrDecl = SchemaGrammar.SG_XSI.getGlobalAttributeDecl(XSI_TYPE);
                    if (attrDecl != null) {
                        processOneAttribute(element, attributes.getValue(index),
                                            attrDecl, null, attrPSVI);
                        continue;
                    }
                }

                // for all other attributes, no_validation/unknow_validity
                if (fTempQName.rawname != XMLNS && !fTempQName.rawname.startsWith("xmlns:")) {
                    reportSchemaError("cvc-type.3.1.1", new Object[]{element.rawname});
                }
            }
            return;
        }

        XSObjectList attrUses = attrGrp.getAttributeUses();
        int useCount = attrUses.getListLength();
        XSWildcardDecl attrWildcard = attrGrp.fAttributeWC;

        // whether we have seen a Wildcard ID.
        String wildcardIDName = null;

        // for each present attribute
        int attCount = attributes.getLength();

        // Element Locally Valid (Complex Type)
        // 3 For each attribute information item in the element information item's [attributes] excepting those whose [namespace name] is identical to http://www.w3.org/2001/XMLSchema-instance and whose [local name] is one of type, nil, schemaLocation or noNamespaceSchemaLocation, the appropriate case among the following must be true:
        // get the corresponding attribute decl
        for (int index = 0; index < attCount; index++) {
            attributes.getName(index, fTempQName);
            
            // get attribute PSVI 
            attrPSVI = (AttributePSVImpl)attributes.getAugmentations(index).getItem(Constants.ATTRIBUTE_PSVI);
            
            // for the 4 xsi attributes, get appropriate decl, and validate
            if (fTempQName.uri == URI_XSI) {
                XSAttributeDecl attrDecl = null;
                if (fTempQName.localpart == XSI_SCHEMALOCATION)
                    attrDecl = SchemaGrammar.SG_XSI.getGlobalAttributeDecl(XSI_SCHEMALOCATION);
                else if (fTempQName.localpart == XSI_NONAMESPACESCHEMALOCATION)
                    attrDecl = SchemaGrammar.SG_XSI.getGlobalAttributeDecl(XSI_NONAMESPACESCHEMALOCATION);
                else if (fTempQName.localpart == XSI_NIL)
                    attrDecl = SchemaGrammar.SG_XSI.getGlobalAttributeDecl(XSI_NIL);
                else if (fTempQName.localpart == XSI_TYPE)
                    attrDecl = SchemaGrammar.SG_XSI.getGlobalAttributeDecl(XSI_TYPE);
                if (attrDecl != null) {
                    processOneAttribute(element, attributes.getValue(index),
                                        attrDecl, null, attrPSVI);
                    continue;
                }
            }
            
            // for namespace attributes, no_validation/unknow_validity
            if (fTempQName.rawname == XMLNS || fTempQName.rawname.startsWith("xmlns:")) {
                continue;
            }
            
            // it's not xmlns, and not xsi, then we need to find a decl for it
            XSAttributeUseImpl currUse = null, oneUse;
            for (int i = 0; i < useCount; i++) {
                oneUse = (XSAttributeUseImpl)attrUses.getItem(i);
                if (oneUse.fAttrDecl.fName == fTempQName.localpart &&
                    oneUse.fAttrDecl.fTargetNamespace == fTempQName.uri) {
                    currUse = oneUse;
                    break;
                }
            }

            // 3.2 otherwise all of the following must be true:
            // 3.2.1 There must be an {attribute wildcard}.
            // 3.2.2 The attribute information item must be valid with respect to it as defined in Item Valid (Wildcard) (3.10.4).

            // if failed, get it from wildcard
            if (currUse == null) {
                //if (attrWildcard == null)
                //    reportSchemaError("cvc-complex-type.3.2.1", new Object[]{element.rawname, fTempQName.rawname});
                if (attrWildcard == null ||
                    !attrWildcard.allowNamespace(fTempQName.uri)) {
                    // so this attribute is not allowed
                    reportSchemaError("cvc-complex-type.3.2.2", new Object[]{element.rawname, fTempQName.rawname});
                    continue;
                }
            }

            XSAttributeDecl currDecl = null;
            if (currUse != null) {
                currDecl = currUse.fAttrDecl;
            }
            else {
                // which means it matches a wildcard
                // skip it if processContents is skip
                if (attrWildcard.fProcessContents == XSWildcardDecl.PC_SKIP)
                    continue;

                //try to find grammar by different means...
                SchemaGrammar grammar = findSchemaGrammar( XSDDescription.CONTEXT_ATTRIBUTE , fTempQName.uri , element , fTempQName , attributes);

                if (grammar != null){
                    currDecl = grammar.getGlobalAttributeDecl(fTempQName.localpart);
                }

                // if can't find
                if (currDecl == null) {
                    // if strict, report error
                    if (attrWildcard.fProcessContents == XSWildcardDecl.PC_STRICT){
                        reportSchemaError("cvc-complex-type.3.2.2", new Object[]{element.rawname, fTempQName.rawname});
                    }

                    // then continue to the next attribute
                    continue;
                }
                else {
                    // 5 Let [Definition:]  the wild IDs be the set of all attribute information item to which clause 3.2 applied and whose validation resulted in a context-determined declaration of mustFind or no context-determined declaration at all, and whose [local name] and [namespace name] resolve (as defined by QName resolution (Instance) (3.15.4)) to an attribute declaration whose {type definition} is or is derived from ID. Then all of the following must be true:
                    // 5.1 There must be no more than one item in wild IDs.
                    if (currDecl.fType.getTypeCategory() == XSTypeDecl.SIMPLE_TYPE &&
                        ((XSSimpleType)currDecl.fType).isIDType()) {
                        if (wildcardIDName != null){
                            reportSchemaError("cvc-complex-type.5.1", new Object[]{element.rawname, currDecl.fName, wildcardIDName});

                            // PSVI: attribute is invalid, record errors
                            attrPSVI.fValidity = AttributePSVI.INVALID_VALIDITY;
                            attrPSVI.addErrorCode("cvc-complex-type.5.1");
                        }
                        else
                            wildcardIDName = currDecl.fName;
                    }
                }
            }
    
            processOneAttribute(element, attributes.getValue(index),
                                currDecl, currUse, attrPSVI);
        } // end of for (all attributes)

        // 5.2 If wild IDs is non-empty, there must not be any attribute uses among the {attribute uses} whose {attribute declaration}'s {type definition} is or is derived from ID.
        if (attrGrp.fIDAttrName != null && wildcardIDName != null){
            // PSVI: attribute is invalid, record errors
            reportSchemaError("cvc-complex-type.5.2", new Object[]{element.rawname, wildcardIDName, attrGrp.fIDAttrName});
        }

    } //processAttributes

    void processOneAttribute(QName element, String attrValue,
                             XSAttributeDecl currDecl, XSAttributeUseImpl currUse,
                             AttributePSVImpl attrPSVI) {
        // Attribute Locally Valid
        // For an attribute information item to be locally valid with respect to an attribute declaration all of the following must be true:
        // 1 The declaration must not be absent (see Missing Sub-components (5.3) for how this can fail to be the case).
        // 2 Its {type definition} must not be absent.
        // 3 The item's normalized value must be locally valid with respect to that {type definition} as per String Valid (3.14.4).
        // get simple type
        XSSimpleType attDV = currDecl.fType;
    
        // PSVI: attribute declaration
        attrPSVI.fDeclaration = currDecl;
        // PSVI: attribute type
        attrPSVI.fTypeDecl = attDV;
    
        // PSVI: validation attempted:
        attrPSVI.fValidationAttempted = AttributePSVI.FULL_VALIDATION;
        attrPSVI.fValidity = AttributePSVI.VALID_VALIDITY;
    
        Object actualValue = null;
        try {
            actualValue = attDV.validate(attrValue, fValidationState, fValidatedInfo);
            // PSVI: attribute memberType
            attrPSVI.fMemberType = fValidatedInfo.memberType;
            // PSVI: element notation
            if (attDV.getVariety() == XSSimpleType.VARIETY_ATOMIC &&
                attDV.getPrimitiveKind() == XSSimpleType.PRIMITIVE_NOTATION){
               QName qName = (QName)actualValue;
               SchemaGrammar grammar = fGrammarBucket.getGrammar(qName.uri);
    
               //REVISIT: is it possible for the notation to be in different namespace than the attribute
               //with which it is associated, CHECK !!  <fof n1:att1 = "n2:notation1" ..>
               // should we give chance to the application to be able to  retrieve a grammar - nb
               //REVISIT: what would be the triggering component here.. if it is attribute value that
               // triggered the loading of grammar ?? -nb
    
               if (grammar != null)
                   fCurrentPSVI.fNotation = grammar.getNotationDecl(qName.localpart);
            }
        }
        catch (InvalidDatatypeValueException idve) {
    
            // PSVI: attribute is invalid, record errors
            attrPSVI.fValidity = AttributePSVI.INVALID_VALIDITY;
            attrPSVI.addErrorCode("cvc-attribute.3");
            reportSchemaError("cvc-attribute.3", new Object[]{element.rawname, fTempQName.rawname, attrValue});
        }
        // PSVI: attribute normalized value
        // NOTE: we always store the normalized value, even if it's invlid,
        // because it might still be useful to the user. But when the it's
        // not valid, the normalized value is not trustable.
        attrPSVI.fNormalizedValue = fValidatedInfo.normalizedValue;
    
        // get the value constraint from use or decl
        // 4 The item's actual value must match the value of the {value constraint}, if it is present and fixed.                 // now check the value against the simpleType
        if (actualValue != null &&
            currDecl.getConstraintType() == XSConstants.VC_FIXED) {
            if (!attDV.isEqual(actualValue, currDecl.fDefault.actualValue)){
    
                // PSVI: attribute is invalid, record errors
                attrPSVI.fValidity = AttributePSVI.INVALID_VALIDITY;
                attrPSVI.addErrorCode("cvc-attribute.4");
                reportSchemaError("cvc-attribute.4", new Object[]{element.rawname, fTempQName.rawname, attrValue});
            }
        }
    
        // 3.1 If there is among the {attribute uses} an attribute use with an {attribute declaration} whose {name} matches the attribute information item's [local name] and whose {target namespace} is identical to the attribute information item's [namespace name] (where an absent {target namespace} is taken to be identical to a [namespace name] with no value), then the attribute information must be valid with respect to that attribute use as per Attribute Locally Valid (Use) (3.5.4). In this case the {attribute declaration} of that attribute use is the context-determined declaration for the attribute information item with respect to Schema-Validity Assessment (Attribute) (3.2.4) and Assessment Outcome (Attribute) (3.2.5).
        if (actualValue != null &&
            currUse != null && currUse.fConstraintType == XSConstants.VC_FIXED) {
            if (!attDV.isEqual(actualValue, currUse.fDefault.actualValue)){
                // PSVI: attribute is invalid, record errors
                attrPSVI.fValidity = AttributePSVI.INVALID_VALIDITY;
                attrPSVI.addErrorCode("cvc-complex-type.3.1");
                reportSchemaError("cvc-complex-type.3.1", new Object[]{element.rawname, fTempQName.rawname, attrValue});
            }
        }
    }
    
    void addDefaultAttributes(QName element, XMLAttributes attributes, XSAttributeGroupDecl attrGrp) {
        // Check after all specified attrs are scanned
        // (1) report error for REQUIRED attrs that are missing (V_TAGc)
        // REVISIT: should we check prohibited attributes?
        // (2) report error for PROHIBITED attrs that are present (V_TAGc)
        // (3) add default attrs (FIXED and NOT_FIXED)
        //
        if (DEBUG) {
            System.out.println("addDefaultAttributes: " + element);
        }
        XSObjectList attrUses = attrGrp.getAttributeUses();
        int useCount = attrUses.getListLength();
        XSAttributeUseImpl currUse;
        XSAttributeDecl currDecl;
        short constType;
        ValidatedInfo defaultValue;
        boolean isSpecified;
        QName attName;
        // for each attribute use
        for (int i = 0; i < useCount; i++) {

            currUse = (XSAttributeUseImpl)attrUses.getItem(i);
            currDecl = currUse.fAttrDecl;
            // get value constraint
            constType = currUse.fConstraintType;
            defaultValue = currUse.fDefault;
            if (constType == XSConstants.VC_NONE) {
                constType = currDecl.getConstraintType();
                defaultValue = currDecl.fDefault;
            }
            // whether this attribute is specified
            isSpecified = attributes.getValue(currDecl.fTargetNamespace, currDecl.fName) != null;

            // Element Locally Valid (Complex Type)
            // 4 The {attribute declaration} of each attribute use in the {attribute uses} whose
            // {required} is true matches one of the attribute information items in the element
            // information item's [attributes] as per clause 3.1 above.
            if (currUse.fUse == SchemaSymbols.USE_REQUIRED) {
                if (!isSpecified)
                    reportSchemaError("cvc-complex-type.4", new Object[]{element.rawname, currDecl.fName});
            }
            // if the attribute is not specified, then apply the value constraint
            if (!isSpecified && constType != XSConstants.VC_NONE) {
                attName = new QName(null, currDecl.fName, currDecl.fName, currDecl.fTargetNamespace);

                int attrIndex = attributes.addAttribute(attName, "CDATA", (defaultValue!=null)?defaultValue.normalizedValue:"");

                // PSVI: attribute is "schema" specified
                Augmentations augs = attributes.getAugmentations(attrIndex);

                AttributePSVImpl attrPSVI = (AttributePSVImpl)augs.getItem(Constants.ATTRIBUTE_PSVI);

                // check if PSVIAttribute was added to Augmentations.
                // it is possible that we just created new chunck of attributes
                // in this case PSVI attribute are not there.
                if (attrPSVI != null) {
                    attrPSVI.reset();
                } else {
                    attrPSVI = new AttributePSVImpl();
                    augs.putItem(Constants.ATTRIBUTE_PSVI, attrPSVI);
                }

                attrPSVI.fSpecified = false;
                // PSVI attribute: validation context
                attrPSVI.fValidationContext = fValidationRoot;
            }

        } // for
    } // addDefaultAttributes

    /**
     *  If there is not text content, and there is a
     *  {value constraint} on the corresponding element decl, then return
     *  an XMLString representing the default value.
     */
    XMLString processElementContent(QName element) {
        // fCurrentElemDecl: default value; ...
        XMLString defaultValue = null;
        // 1 If the item is ?valid? with respect to an element declaration as per Element Locally Valid (Element) (?3.3.4) and the {value constraint} is present, but clause 3.2 of Element Locally Valid (Element) (?3.3.4) above is not satisfied and the item has no element or character information item [children], then schema. Furthermore, the post-schema-validation infoset has the canonical lexical representation of the {value constraint} value as the item's [schema normalized value] property.
        if (fCurrentElemDecl != null && fCurrentElemDecl.fDefault != null &&
            fBuffer.toString().length() == 0 && fChildCount == 0 && !fNil) {

            // PSVI: specified
            fCurrentPSVI.fSpecified = false;

            int bufLen = fCurrentElemDecl.fDefault.normalizedValue.length();
            char [] chars = new char[bufLen];
            fCurrentElemDecl.fDefault.normalizedValue.getChars(0, bufLen, chars, 0);
            defaultValue = new XMLString(chars, 0, bufLen);
            // call all active identity constraints
            int count = fMatcherStack.getMatcherCount();
            for (int i = 0; i < count; i++) {
                XPathMatcher matcher = fMatcherStack.getMatcherAt(i);
                matcher.characters(defaultValue);
            }

        }
        // fixed values are handled later, after xsi:type determined.

        if (DEBUG) {
            System.out.println("processElementContent:" +element);
        }

        if (fCurrentElemDecl != null &&
            fCurrentElemDecl.getConstraintType() == XSConstants.VC_DEFAULT) {
        }

        if (fDoValidation) {
            String content = fBuffer.toString();

            // Element Locally Valid (Element)
            // 3.2.1 The element information item must have no character or element information item [children].
            if (fNil) {
                if (fChildCount != 0 || content.length() != 0){
                    reportSchemaError("cvc-elt.3.2.1", new Object[]{element.rawname, URI_XSI+","+XSI_NIL});
                    // PSVI: nil
                    fCurrentPSVI.fNil = false;
                } else {
                    fCurrentPSVI.fNil = true;
                }
            }

            // 5 The appropriate case among the following must be true:
            // 5.1 If the declaration has a {value constraint}, the item has neither element nor character [children] and clause 3.2 has not applied, then all of the following must be true:
            if (fCurrentElemDecl != null &&
                fCurrentElemDecl.getConstraintType() != XSConstants.VC_NONE &&
                fChildCount == 0 && content.length() == 0 && !fNil) {
                // 5.1.1 If the actual type definition is a local type definition then the canonical lexical representation of the {value constraint} value must be a valid default for the actual type definition as defined in Element Default Valid (Immediate) (3.3.6).
                if (fCurrentType != fCurrentElemDecl.fType) {
                    //REVISIT:we should pass ValidatedInfo here.
                    if (XSConstraints.ElementDefaultValidImmediate(fCurrentType, fCurrentElemDecl.fDefault, fState4XsiType, null) == null)
                        reportSchemaError("cvc-elt.5.1.1", new Object[]{element.rawname, fCurrentType.getName(), fCurrentElemDecl.fDefault.normalizedValue});
                }
                // 5.1.2 The element information item with the canonical lexical representation of the {value constraint} value used as its normalized value must be valid with respect to the actual type definition as defined by Element Locally Valid (Type) (3.3.4).
                // REVISIT: don't use toString, but validateActualValue instead
                //          use the fState4ApplyDefault
                elementLocallyValidType(element, fCurrentElemDecl.fDefault.normalizedValue);
            }
            else {
                // The following method call also deal with clause 1.2.2 of the constraint
                // Validation Rule: Schema-Validity Assessment (Element)

                // 5.2 If the declaration has no {value constraint} or the item has either element or character [children] or clause 3.2 has applied, then all of the following must be true:
                // 5.2.1 The element information item must be valid with respect to the actual type definition as defined by Element Locally Valid (Type) (3.3.4).
                Object actualValue = elementLocallyValidType(element, content);
                // 5.2.2 If there is a fixed {value constraint} and clause 3.2 has not applied, all of the following must be true:
                if (fCurrentElemDecl != null &&
                    fCurrentElemDecl.getConstraintType() == XSConstants.VC_FIXED &&
                    !fNil) {
                    // 5.2.2.1 The element information item must have no element information item [children].
                    if (fChildCount != 0)
                        reportSchemaError("cvc-elt.5.2.2.1", new Object[]{element.rawname});
                    // 5.2.2.2 The appropriate case among the following must be true:
                    if (fCurrentType.getTypeCategory() == XSTypeDecl.COMPLEX_TYPE) {
                        XSComplexTypeDecl ctype = (XSComplexTypeDecl)fCurrentType;
                        // 5.2.2.2.1 If the {content type} of the actual type definition is mixed, then the initial value of the item must match the canonical lexical representation of the {value constraint} value.
                        if (ctype.fContentType == XSComplexTypeDecl.CONTENTTYPE_MIXED) {
                            // REVISIT: how to get the initial value, does whiteSpace count?
                            if (!fCurrentElemDecl.fDefault.normalizedValue.equals(content))
                                reportSchemaError("cvc-elt.5.2.2.2.1", new Object[]{element.rawname, content, fCurrentElemDecl.fDefault.normalizedValue});
                        }
                        // 5.2.2.2.2 If the {content type} of the actual type definition is a simple type definition, then the actual value of the item must match the canonical lexical representation of the {value constraint} value.
                        else if (ctype.fContentType == XSComplexTypeDecl.CONTENTTYPE_SIMPLE) {
                            if (actualValue != null &&
                                !ctype.fXSSimpleType.isEqual(actualValue, fCurrentElemDecl.fDefault.actualValue))
                                reportSchemaError("cvc-elt.5.2.2.2.2", new Object[]{element.rawname, content, fCurrentElemDecl.fDefault.normalizedValue});
                        }
                    }
                    else if (fCurrentType.getTypeCategory() == XSTypeDecl.SIMPLE_TYPE) {
                        XSSimpleType sType = (XSSimpleType)fCurrentType;
                        if (!sType.isEqual(actualValue, fCurrentElemDecl.fDefault.actualValue))
                            reportSchemaError("cvc-elt.5.2.2.2.2", new Object[]{element.rawname, content, fCurrentElemDecl.fDefault.normalizedValue});
                    }
                }
            }
        } // if fDoValidation

        return defaultValue;
    } // processElementContent

    Object elementLocallyValidType(QName element, String textContent) {
        if (fCurrentType == null)
            return null;

        if (fUnionType) {
            // for union types we need to send data because we delayed sending this data
            // when we received it in the characters() call.
            // XMLString will inlude non-normalized value, PSVIElement will include
            // normalized value
            int bufLen = textContent.length();
            if (bufLen >= BUFFER_SIZE) {
                fCharBuffer = new char[bufLen*2];
            }
            textContent.getChars(0, bufLen, fCharBuffer, 0);
            fXMLString.setValues(fCharBuffer, 0, bufLen);
        }

        Object retValue = null;
        // Element Locally Valid (Type)
        // 3 The appropriate case among the following must be true:
        // 3.1 If the type definition is a simple type definition, then all of the following must be true:
        if (fCurrentType.getTypeCategory() == XSTypeDecl.SIMPLE_TYPE) {
            // 3.1.2 The element information item must have no element information item [children].
            if (fChildCount != 0)
                reportSchemaError("cvc-type.3.1.2", new Object[]{element.rawname});
            // 3.1.3 If clause 3.2 of Element Locally Valid (Element) (3.3.4) did not apply, then the normalized value must be valid with respect to the type definition as defined by String Valid (3.14.4).
            if (!fNil) {
                XSSimpleType dv = (XSSimpleType)fCurrentType;
                try {

                    if (!fNormalizeData || fUnionType) {
                        fValidationState.setNormalizationRequired(true);
                    }
                    retValue = dv.validate(textContent, fValidationState, fValidatedInfo);
                    // PSVI: schema normalized value
                    //
                    fCurrentPSVI.fNormalizedValue = fValidatedInfo.normalizedValue;
                    // PSVI: memberType
                    fCurrentPSVI.fMemberType = fValidatedInfo.memberType;

                    if (fDocumentHandler != null && fUnionType) {
                        // send normalized values
                        // at this point we should only rely on normalized value
                        // available via PSVI
                        fAugmentations.putItem(Constants.ELEMENT_PSVI, fCurrentPSVI);
                        fDocumentHandler.characters(fXMLString, fAugmentations);
                    }
                }
                catch (InvalidDatatypeValueException e) {
                    if (fDocumentHandler != null && fUnionType) {
                        fCurrentPSVI.fNormalizedValue = null;
                        fAugmentations.putItem(Constants.ELEMENT_PSVI, fCurrentPSVI);
                        fDocumentHandler.characters(fXMLString, fAugmentations);

                    }
                    reportSchemaError("cvc-type.3.1.3", new Object[]{element.rawname, textContent});
                }
            }
        }
        else {
            // 3.2 If the type definition is a complex type definition, then the element information item must be valid with respect to the type definition as per Element Locally Valid (Complex Type) (3.4.4);
            retValue = elementLocallyValidComplexType(element, textContent);
        }

        return retValue;
    } // elementLocallyValidType

    Object elementLocallyValidComplexType(QName element, String textContent) {
        Object actualValue = null;
        XSComplexTypeDecl ctype = (XSComplexTypeDecl)fCurrentType;

        // Element Locally Valid (Complex Type)
        // For an element information item to be locally valid with respect to a complex type definition all of the following must be true:
        // 1 {abstract} is false.
        // 2 If clause 3.2 of Element Locally Valid (Element) (3.3.4) did not apply, then the appropriate case among the following must be true:
        if (!fNil) {
            // 2.1 If the {content type} is empty, then the element information item has no character or element information item [children].
            if (ctype.fContentType == XSComplexTypeDecl.CONTENTTYPE_EMPTY &&
                (fChildCount != 0 || textContent.length() != 0 || fSawChildren)) {
                reportSchemaError("cvc-complex-type.2.1", new Object[]{element.rawname});
            }
            // 2.2 If the {content type} is a simple type definition, then the element information item has no element information item [children], and the normalized value of the element information item is valid with respect to that simple type definition as defined by String Valid (3.14.4).
            else if (ctype.fContentType == XSComplexTypeDecl.CONTENTTYPE_SIMPLE) {
                if (fChildCount != 0)
                    reportSchemaError("cvc-complex-type.2.2", new Object[]{element.rawname});
                XSSimpleType dv = ctype.fXSSimpleType;
                try {

                    if (!fNormalizeData || fUnionType) {
                        fValidationState.setNormalizationRequired(true);
                    }
                    actualValue = dv.validate(textContent, fValidationState, fValidatedInfo);

                    // PSVI: schema normalized value
                    //
                    fCurrentPSVI.fNormalizedValue = fValidatedInfo.normalizedValue;
                    // PSVI: memberType
                    fCurrentPSVI.fMemberType = fValidatedInfo.memberType;

                    if (fDocumentHandler != null && fUnionType) {
                        fDocumentHandler.characters(fXMLString, fAugmentations);
                    }
                }
                catch (InvalidDatatypeValueException e) {
                    if (fDocumentHandler != null && fUnionType) {
                        fCurrentPSVI.fNormalizedValue = null;
                        fDocumentHandler.characters(fXMLString, fAugmentations);

                    }
                    reportSchemaError("cvc-complex-type.2.2", new Object[]{element.rawname});
                }
                // REVISIT: eventually, this method should return the same actualValue as elementLocallyValidType...
                // obviously it'll return null when the content is complex.
            }
            // 2.3 If the {content type} is element-only, then the element information item has no character information item [children] other than those whose [character code] is defined as a white space in [XML 1.0 (Second Edition)].
            else if (ctype.fContentType == XSComplexTypeDecl.CONTENTTYPE_ELEMENT) {
                if (fSawCharacters) {
                    reportSchemaError("cvc-complex-type.2.3", new Object[]{element.rawname});
                }
            }
            // 2.4 If the {content type} is element-only or mixed, then the sequence of the element information item's element information item [children], if any, taken in order, is valid with respect to the {content type}'s particle, as defined in Element Sequence Locally Valid (Particle) (3.9.4).
            if (ctype.fContentType == XSComplexTypeDecl.CONTENTTYPE_ELEMENT ||
                ctype.fContentType == XSComplexTypeDecl.CONTENTTYPE_MIXED) {
                // if the current state is a valid state, check whether
                // it's one of the final states.
                if (DEBUG) {
                    System.out.println(fCurrCMState);
                }
                if (fCurrCMState[0] >= 0 &&
                    !fCurrentCM.endContentModel(fCurrCMState)) {
                    reportSchemaError("cvc-complex-type.2.4.b", new Object[]{element.rawname, ctype.fParticle.toString()});
                }
            }
        }
        return actualValue;
    } // elementLocallyValidComplexType

    void reportSchemaError(String key, Object[] arguments) {
        if (fDoValidation)
            fXSIErrorReporter.reportError(XSMessageFormatter.SCHEMA_DOMAIN,
                                          key, arguments,
                                          XMLErrorReporter.SEVERITY_ERROR);
    }

    /**********************************/

    // xpath matcher information

    /**
     * Stack of XPath matchers for identity constraints.
     *
     * @author Andy Clark, IBM
     */
    protected static class XPathMatcherStack {

        //
        // Data
        //

        /** Active matchers. */
        protected XPathMatcher[] fMatchers = new XPathMatcher[4];

        /** Count of active matchers. */
        protected int fMatchersCount;

        /** Offset stack for contexts. */
        protected IntStack fContextStack = new IntStack();

        //
        // Constructors
        //

        public XPathMatcherStack() {
        } // <init>()

        //
        // Public methods
        //

        /** Resets the XPath matcher stack. */
        public void clear() {
            for (int i = 0; i < fMatchersCount; i++) {
                fMatchers[i] = null;
            }
            fMatchersCount = 0;
            fContextStack.clear();
        } // clear()

        /** Returns the size of the stack. */
        public int size() {
            return fContextStack.size();
        } // size():int

        /** Returns the count of XPath matchers. */
        public int getMatcherCount() {
            return fMatchersCount;
        } // getMatcherCount():int

        /** Adds a matcher. */
        public void addMatcher(XPathMatcher matcher) {
            ensureMatcherCapacity();
            fMatchers[fMatchersCount++] = matcher;
        } // addMatcher(XPathMatcher)

        /** Returns the XPath matcher at the specified index. */
        public XPathMatcher getMatcherAt(int index) {
            return fMatchers[index];
        } // getMatcherAt(index):XPathMatcher

        /** Pushes a new context onto the stack. */
        public void pushContext() {
            fContextStack.push(fMatchersCount);
        } // pushContext()

        /** Pops a context off of the stack. */
        public void popContext() {
            fMatchersCount = fContextStack.pop();
        } // popContext()

        //
        // Private methods
        //

        /** Ensures the size of the matchers array. */
        private void ensureMatcherCapacity() {
            if (fMatchersCount == fMatchers.length) {
                XPathMatcher[] array = new XPathMatcher[fMatchers.length * 2];
                System.arraycopy(fMatchers, 0, array, 0, fMatchers.length);
                fMatchers = array;
            }
        } // ensureMatcherCapacity()

    } // class XPathMatcherStack

    // value store implementations

    /**
     * Value store implementation base class. There are specific subclasses
     * for handling unique, key, and keyref.
     *
     * @author Andy Clark, IBM
     */
    protected abstract class ValueStoreBase
    implements ValueStore {

        //
        // Constants
        //

        /** Not a value (Unicode: #FFFF). */
        protected IDValue NOT_AN_IDVALUE = new IDValue("\uFFFF", null);

        //
        // Data
        //

        /** Identity constraint. */
        protected IdentityConstraint fIdentityConstraint;

        /** Current data values. */
        protected final OrderedHashtable fValues = new OrderedHashtable();

        /** Current data value count. */
        protected int fValuesCount;

        /** Data value tuples. */
        protected final Vector fValueTuples = new Vector();

        //
        // Constructors
        //

        /** Constructs a value store for the specified identity constraint. */
        protected ValueStoreBase(IdentityConstraint identityConstraint) {
            fIdentityConstraint = identityConstraint;
        } // <init>(IdentityConstraint)

        //
        // Public methods
        //

        // destroys this ValueStore; useful when, for instance, a
        // locally-scoped ID constraint is involved.
        public void destroy() {
            fValuesCount = 0;
            fValues.clear();
            fValueTuples.removeAllElements();
        } // end destroy():void

        // appends the contents of one ValueStore to those of us.
        public void append(ValueStoreBase newVal) {
            for (int i = 0; i < newVal.fValueTuples.size(); i++) {
                OrderedHashtable o = (OrderedHashtable)newVal.fValueTuples.elementAt(i);
                if (!contains(o))
                    fValueTuples.addElement(o);
            }
        } // append(ValueStoreBase)

        /** Start scope for value store. */
        public void startValueScope() throws XNIException {
            fValuesCount = 0;
            int count = fIdentityConstraint.getFieldCount();
            for (int i = 0; i < count; i++) {
                fValues.put(fIdentityConstraint.getFieldAt(i), NOT_AN_IDVALUE);
            }
        } // startValueScope()

        /** Ends scope for value store. */
        public void endValueScope() throws XNIException {

            // is there anything to do?
            // REVISIT: This check solves the problem with field matchers
            //          that get activated because they are at the same
            //          level as the declaring element (e.g. selector xpath
            //          is ".") but never match.
            //          However, this doesn't help us catch the problem
            //          when we expect a field value but never see it. A
            //          better solution has to be found. -Ac
            // REVISIT: Is this a problem? -Ac
            // Yes - NG
            if (fValuesCount == 0) {
                if (fIdentityConstraint.getCategory() == IdentityConstraint.IC_KEY) {
                    String code = "AbsentKeyValue";
                    String eName = fIdentityConstraint.getElementName();
                    reportSchemaError(code, new Object[]{eName});
                }
                return;
            }

            // do we have enough values?
            if (fValuesCount != fIdentityConstraint.getFieldCount()) {
                switch (fIdentityConstraint.getCategory()) {
                case IdentityConstraint.IC_UNIQUE: {
                        String code = "UniqueNotEnoughValues";
                        String ename = fIdentityConstraint.getElementName();
                        reportSchemaError(code, new Object[]{ename});
                        break;
                    }
                case IdentityConstraint.IC_KEY: {
                        String code = "KeyNotEnoughValues";
                        UniqueOrKey key = (UniqueOrKey)fIdentityConstraint;
                        String ename = fIdentityConstraint.getElementName();
                        String kname = key.getIdentityConstraintName();
                        reportSchemaError(code, new Object[]{ename,kname});
                        break;
                    }
                case IdentityConstraint.IC_KEYREF: {
                        String code = "KeyRefNotEnoughValues";
                        KeyRef keyref = (KeyRef)fIdentityConstraint;
                        String ename = fIdentityConstraint.getElementName();
                        String kname = (keyref.getKey()).getIdentityConstraintName();
                        reportSchemaError(code, new Object[]{ename,kname});
                        break;
                    }
                }
                return;
            }


        } // endValueScope()

        // This is needed to allow keyref's to look for matched keys
        // in the correct scope.  Unique and Key may also need to
        // override this method for purposes of their own.
        // This method is called whenever the DocumentFragment
        // of an ID Constraint goes out of scope.
        public void endDocumentFragment() throws XNIException {
        } // endDocumentFragment():void

        /**
         * Signals the end of the document. This is where the specific
         * instances of value stores can verify the integrity of the
         * identity constraints.
         */
        public void endDocument() throws XNIException {
        } // endDocument()

        //
        // ValueStore methods
        //

        /* reports an error if an element is matched
         * has nillable true and is matched by a key.
         */

        public void reportNilError(IdentityConstraint id) {
            if (id.getCategory() == IdentityConstraint.IC_KEY) {
                String code = "KeyMatchesNillable";
                reportSchemaError(code, new Object[]{id.getElementName()});
            }
        } // reportNilError

        /**
         * Adds the specified value to the value store.
         *
         * @param value The value to add.
         * @param field The field associated to the value. This reference
         *              is used to ensure that each field only adds a value
         *              once within a selection scope.
         */
        public void addValue(Field field, IDValue value) {
            if (!field.mayMatch()) {
                String code = "FieldMultipleMatch";
                reportSchemaError(code, new Object[]{field.toString()});
            }

            // do we even know this field?
            int index = fValues.indexOf(field);
            if (index == -1) {
                String code = "UnknownField";
                reportSchemaError(code, new Object[]{field.toString()});
                return;
            }

            // store value
            IDValue storedValue = fValues.valueAt(index);
            if (storedValue.isDuplicateOf(NOT_AN_IDVALUE)) {
                fValuesCount++;
            }
            fValues.put(field, value);

            if (fValuesCount == fValues.size()) {
                // is this value as a group duplicated?
                if (contains(fValues)) {
                    duplicateValue(fValues);
                }

                // store values
                OrderedHashtable values = (OrderedHashtable)fValues.clone();
                fValueTuples.addElement(values);
            }

        } // addValue(String,Field)

        /**
         * Returns true if this value store contains the specified
         * values tuple.
         */
        public boolean contains(OrderedHashtable tuple) {

            // do sizes match?
            int tcount = tuple.size();

            // iterate over tuples to find it
            int count = fValueTuples.size();
            LOOP: for (int i = 0; i < count; i++) {
                OrderedHashtable vtuple = (OrderedHashtable)fValueTuples.elementAt(i);
                // compare values
                for (int j = 0; j < tcount; j++) {
                    IDValue value1 = vtuple.valueAt(j);
                    IDValue value2 = tuple.valueAt(j);
                    if (!(value1.isDuplicateOf(value2))) {
                        continue LOOP;
                    }
                }

                // found it
                return true;
            }

            // didn't find it
            return false;

        } // contains(Hashtable):boolean

        //
        // Protected methods
        //

        /**
         * Called when a duplicate value is added. Subclasses should override
         * this method to perform error checking.
         *
         * @param tuple The duplicate value tuple.
         */
        protected void duplicateValue(OrderedHashtable tuple)
        throws XNIException {
            // no-op
        } // duplicateValue(Hashtable)

        /** Returns a string of the specified values. */
        protected String toString(OrderedHashtable tuple) {

            // no values
            int size = tuple.size();
            if (size == 0) {
                return "";
            }

            // construct value string
            StringBuffer str = new StringBuffer();
            for (int i = 0; i < size; i++) {
                if (i > 0) {
                    str.append(',');
                }
                str.append(tuple.valueAt(i));
            }
            return str.toString();

        } // toString(OrderedHashtable):String

        //
        // Object methods
        //

        /** Returns a string representation of this object. */
        public String toString() {
            String s = super.toString();
            int index1 = s.lastIndexOf('$');
            if (index1 != -1) {
                s = s.substring(index1 + 1);
            }
            int index2 = s.lastIndexOf('.');
            if (index2 != -1) {
                s = s.substring(index2 + 1);
            }
            return s + '[' + fIdentityConstraint + ']';
        } // toString():String

    } // class ValueStoreBase

    /**
     * Unique value store.
     *
     * @author Andy Clark, IBM
     */
    protected class UniqueValueStore
    extends ValueStoreBase {

        //
        // Constructors
        //

        /** Constructs a unique value store. */
        public UniqueValueStore(UniqueOrKey unique) {
            super(unique);
        } // <init>(Unique)

        //
        // ValueStoreBase protected methods
        //

        /**
         * Called when a duplicate value is added.
         *
         * @param tuple The duplicate value tuple.
         */
        protected void duplicateValue(OrderedHashtable tuple)
        throws XNIException {
            String code = "DuplicateUnique";
            String value = toString(tuple);
            String ename = fIdentityConstraint.getElementName();
            reportSchemaError(code, new Object[]{value,ename});
        } // duplicateValue(Hashtable)

    } // class UniqueValueStore

    /**
     * Key value store.
     *
     * @author Andy Clark, IBM
     */
    protected class KeyValueStore
    extends ValueStoreBase {

        // REVISIT: Implement a more efficient storage mechanism. -Ac

        //
        // Constructors
        //

        /** Constructs a key value store. */
        public KeyValueStore(UniqueOrKey key) {
            super(key);
        } // <init>(Key)

        //
        // ValueStoreBase protected methods
        //

        /**
         * Called when a duplicate value is added.
         *
         * @param tuple The duplicate value tuple.
         */
        protected void duplicateValue(OrderedHashtable tuple)
        throws XNIException {
            String code = "DuplicateKey";
            String value = toString(tuple);
            String ename = fIdentityConstraint.getElementName();
            reportSchemaError(code, new Object[]{value,ename});
        } // duplicateValue(Hashtable)

    } // class KeyValueStore

    /**
     * Key reference value store.
     *
     * @author Andy Clark, IBM
     */
    protected class KeyRefValueStore
    extends ValueStoreBase {

        //
        // Data
        //

        /** Key value store. */
        protected ValueStoreBase fKeyValueStore;

        //
        // Constructors
        //

        /** Constructs a key value store. */
        public KeyRefValueStore(KeyRef keyRef, KeyValueStore keyValueStore) {
            super(keyRef);
            fKeyValueStore = keyValueStore;
        } // <init>(KeyRef)

        //
        // ValueStoreBase methods
        //

        // end the value Scope; here's where we have to tie
        // up keyRef loose ends.
        public void endDocumentFragment () throws XNIException {

            // do all the necessary management...
            super.endDocumentFragment ();

            // verify references
            // get the key store corresponding (if it exists):
            fKeyValueStore = (ValueStoreBase)fValueStoreCache.fGlobalIDConstraintMap.get(((KeyRef)fIdentityConstraint).getKey());

            if (fKeyValueStore == null) {
                // report error
                String code = "KeyRefOutOfScope";
                String value = fIdentityConstraint.toString();
                reportSchemaError(code, new Object[]{value});
                return;
            }

            int count = fValueTuples.size();
            for (int i = 0; i < count; i++) {
                OrderedHashtable values = (OrderedHashtable)fValueTuples.elementAt(i);
                if (!fKeyValueStore.contains(values)) {
                    String code = "KeyNotFound";
                    String value = toString(values);
                    String element = fIdentityConstraint.getElementName();
                    reportSchemaError(code, new Object[]{value,element});
                }
            }

        } // endDocumentFragment()

        /** End document. */
        public void endDocument() throws XNIException {
            super.endDocument();

        } // endDocument()

    } // class KeyRefValueStore

    // value store management

    /**
     * Value store cache. This class is used to store the values for
     * identity constraints.
     *
     * @author Andy Clark, IBM
     */
    protected class ValueStoreCache {

        //
        // Data
        //

        // values stores

        /** stores all global Values stores. */
        protected final Vector fValueStores = new Vector();

        /** Values stores associated to specific identity constraints. */
        protected final Hashtable fIdentityConstraint2ValueStoreMap = new Hashtable();

        // sketch of algorithm:
        // - when a constraint is first encountered, its
        //  values are stored in the (local) fIdentityConstraint2ValueStoreMap;
        // - Once it is validated (i.e., wen it goes out of scope),
        //  its values are merged into the fGlobalIDConstraintMap;
        // - as we encounter keyref's, we look at the global table to
        //  validate them.
        // the fGlobalIDMapStack has the following structure:
        // - validation always occurs against the fGlobalIDConstraintMap
        // (which comprises all the "eligible" id constraints);
        // When an endelement is found, this Hashtable is merged with the one
        // below in the stack.
        // When a start tag is encountered, we create a new
        // fGlobalIDConstraintMap.
        // i.e., the top of the fGlobalIDMapStack always contains
        // the preceding siblings' eligible id constraints;
        // the fGlobalIDConstraintMap contains descendants+self.
        // keyrefs can only match descendants+self.
        protected final Stack fGlobalMapStack = new Stack();
        protected final Hashtable fGlobalIDConstraintMap = new Hashtable();

        //
        // Constructors
        //

        /** Default constructor. */
        public ValueStoreCache() {
        } // <init>()

        //
        // Public methods
        //

        /** Resets the identity constraint cache. */
        public void startDocument() throws XNIException {
            fValueStores.removeAllElements();
            fIdentityConstraint2ValueStoreMap.clear();
            fGlobalIDConstraintMap.clear();
            fGlobalMapStack.removeAllElements();
        } // startDocument()

        // startElement:  pushes the current fGlobalIDConstraintMap
        // onto fGlobalMapStack and clears fGlobalIDConstraint map.
        public void startElement() {
            fGlobalMapStack.push(fGlobalIDConstraintMap.clone());
            fGlobalIDConstraintMap.clear();
        } // startElement(void)

        // endElement():  merges contents of fGlobalIDConstraintMap with the
        // top of fGlobalMapStack into fGlobalIDConstraintMap.
        public void endElement() {
            if (fGlobalMapStack.isEmpty()) return; // must be an invalid doc!
            Hashtable oldMap = (Hashtable)fGlobalMapStack.pop();
            Enumeration keys = oldMap.keys();
            while (keys.hasMoreElements()) {
                IdentityConstraint id = (IdentityConstraint)keys.nextElement();
                ValueStoreBase oldVal = (ValueStoreBase)oldMap.get(id);
                if (oldVal != null) {
                    ValueStoreBase currVal = (ValueStoreBase)fGlobalIDConstraintMap.get(id);
                    if (currVal == null)
                        fGlobalIDConstraintMap.put(id, oldVal);
                    else {
                        currVal.append(oldVal);
                        fGlobalIDConstraintMap.put(id, currVal);
                    }
                }
            }
        } // endElement()

        /**
         * Initializes the value stores for the specified element
         * declaration.
         */
        public void initValueStoresFor(XSElementDecl eDecl)
        throws XNIException {
            // initialize value stores for unique fields
            IdentityConstraint [] icArray = eDecl.fIDConstraints;
            int icCount = eDecl.fIDCPos;
            for (int i = 0; i < icCount; i++) {
                switch (icArray[i].getCategory()) {
                case (IdentityConstraint.IC_UNIQUE):
                    // initialize value stores for unique fields
                    UniqueOrKey unique = (UniqueOrKey)icArray[i];
                    UniqueValueStore uniqueValueStore = (UniqueValueStore)fIdentityConstraint2ValueStoreMap.get(unique);
                    if (uniqueValueStore != null) {
                        // NOTE: If already initialized, don't need to
                        //       do it again. -Ac
                        continue;
                    }
                    uniqueValueStore = new UniqueValueStore(unique);
                    fValueStores.addElement(uniqueValueStore);
                    fIdentityConstraint2ValueStoreMap.put(unique, uniqueValueStore);
                    break;
                case (IdentityConstraint.IC_KEY):
                    // initialize value stores for key fields
                    UniqueOrKey key = (UniqueOrKey)icArray[i];
                    KeyValueStore keyValueStore = (KeyValueStore)fIdentityConstraint2ValueStoreMap.get(key);
                    if (keyValueStore != null) {
                        // NOTE: If already initialized, don't need to
                        //       do it again. -Ac
                        continue;
                    }
                    keyValueStore = new KeyValueStore(key);
                    fValueStores.addElement(keyValueStore);
                    fIdentityConstraint2ValueStoreMap.put(key, keyValueStore);
                    break;
                case (IdentityConstraint.IC_KEYREF):
                    // initialize value stores for key reference fields
                    KeyRef keyRef = (KeyRef)icArray[i];
                    KeyRefValueStore keyRefValueStore = (KeyRefValueStore)fIdentityConstraint2ValueStoreMap.get(keyRef);
                    if (keyRefValueStore != null) {
                        // NOTE: If already initialized, don't need to
                        //       do it again. -Ac
                        continue;
                    }
                    keyRefValueStore = new KeyRefValueStore(keyRef, null);
                    fValueStores.addElement(keyRefValueStore);
                    fIdentityConstraint2ValueStoreMap.put(keyRef, keyRefValueStore);
                    break;
                }
            }
        } // initValueStoresFor(XSElementDecl)

        /** Returns the value store associated to the specified field. */
        public ValueStoreBase getValueStoreFor(Field field) {
            IdentityConstraint identityConstraint = field.getIdentityConstraint();
            return(ValueStoreBase)fIdentityConstraint2ValueStoreMap.get(identityConstraint);
        } // getValueStoreFor(Field):ValueStoreBase

        /** Returns the value store associated to the specified IdentityConstraint. */
        public ValueStoreBase getValueStoreFor(IdentityConstraint id) {
            return(ValueStoreBase)fIdentityConstraint2ValueStoreMap.get(id);
        } // getValueStoreFor(IdentityConstraint):ValueStoreBase

        /** Returns the global value store associated to the specified IdentityConstraint. */
        public ValueStoreBase getGlobalValueStoreFor(IdentityConstraint id) {
            return(ValueStoreBase)fGlobalIDConstraintMap.get(id);
        } // getValueStoreFor(IdentityConstraint):ValueStoreBase
        // This method takes the contents of the (local) ValueStore
        // associated with id and moves them into the global
        // hashtable, if id is a <unique> or a <key>.
        // If it's a <keyRef>, then we leave it for later.
        public void transplant(IdentityConstraint id) {
            if (id.getCategory() == IdentityConstraint.IC_KEYREF) return;
            ValueStoreBase newVals = (ValueStoreBase)fIdentityConstraint2ValueStoreMap.get(id);
            fIdentityConstraint2ValueStoreMap.remove(id);
            ValueStoreBase currVals = (ValueStoreBase)fGlobalIDConstraintMap.get(id);
            if (currVals != null) {
                currVals.append(newVals);
                fGlobalIDConstraintMap.put(id, currVals);
            }
            else
                fGlobalIDConstraintMap.put(id, newVals);

        } // transplant(id)

        /** Check identity constraints. */
        public void endDocument() throws XNIException {

            int count = fValueStores.size();
            for (int i = 0; i < count; i++) {
                ValueStoreBase valueStore = (ValueStoreBase)fValueStores.elementAt(i);
                valueStore.endDocument();
            }

        } // endDocument()

        //
        // Object methods
        //

        /** Returns a string representation of this object. */
        public String toString() {
            String s = super.toString();
            int index1 = s.lastIndexOf('$');
            if (index1 != -1) {
                return s.substring(index1 + 1);
            }
            int index2 = s.lastIndexOf('.');
            if (index2 != -1) {
                return s.substring(index2 + 1);
            }
            return s;
        } // toString():String

    } // class ValueStoreCache

    // utility classes

    /**
     * Ordered hashtable. This class acts as a hashtable with
     * <code>put()</code> and <code>get()</code> operations but also
     * allows values to be queried via the order that they were
     * added to the hashtable.
     * <p>
     * <strong>Note:</strong> This class does not perform any error
     * checking.
     * <p>
     * <strong>Note:</strong> This class is <em>not</em> efficient but
     * is assumed to be used for a very small set of values.
     *
     * @author Andy Clark, IBM
     */
    static final class OrderedHashtable
    implements Cloneable {

        //
        // Data
        //

        /** Size. */
        private int fSize;

        /** Hashtable entries. */
        private Entry[] fEntries = null;

        //
        // Public methods
        //

        /** Returns the number of entries in the hashtable. */
        public int size() {
            return fSize;
        } // size():int

        /** Puts an entry into the hashtable. */
        public void put(Field key, IDValue value) {
            int index = indexOf(key);
            if (index == -1) {
                ensureCapacity(fSize);
                index = fSize++;
                fEntries[index].key = key;
            }
            fEntries[index].value = value;
        } // put(Field,String)

        /** Returns the value associated to the specified key. */
        public IDValue get(Field key) {
            return fEntries[indexOf(key)].value;
        } // get(Field):String

        /** Returns the index of the entry with the specified key. */
        public int indexOf(Field key) {
            for (int i = 0; i < fSize; i++) {
                // NOTE: Only way to be sure that the keys are the
                //       same is by using a reference comparison. In
                //       order to rely on the equals method, each
                //       field would have to take into account its
                //       position in the identity constraint, the
                //       identity constraint, the declaring element,
                //       and the grammar that it is defined in.
                //       Otherwise, you have the possibility that
                //       the equals method would return true for two
                //       fields that look *very* similar.
                //       The reference compare isn't bad, actually,
                //       because the field objects are cacheable. -Ac
                if (fEntries[i].key == key) {
                    return i;
                }
            }
            return -1;
        } // indexOf(Field):int

        /** Returns the key at the specified index. */
        public Field keyAt(int index) {
            return fEntries[index].key;
        } // keyAt(int):Field

        /** Returns the value at the specified index. */
        public IDValue valueAt(int index) {
            return fEntries[index].value;
        } // valueAt(int):String

        /** Removes all of the entries from the hashtable. */
        public void clear() {
            fSize = 0;
        } // clear()

        //
        // Private methods
        //

        /** Ensures the capacity of the entries array. */
        private void ensureCapacity(int size) {

            // sizes
            int osize = -1;
            int nsize = -1;

            // create array
            if (fEntries == null) {
                osize = 0;
                nsize = 2;
                fEntries = new Entry[nsize];
            }

            // resize array
            else if (fEntries.length <= size) {
                osize = fEntries.length;
                nsize = 2 * osize;
                Entry[] array = new Entry[nsize];
                System.arraycopy(fEntries, 0, array, 0, osize);
                fEntries = array;
            }

            // create new entries
            for (int i = osize; i < nsize; i++) {
                fEntries[i] = new Entry();
            }

        } // ensureCapacity(int)

        //
        // Cloneable methods
        //

        /** Clones this object. */
        public Object clone() {

            OrderedHashtable hashtable = new OrderedHashtable();
            for (int i = 0; i < fSize; i++) {
                hashtable.put(fEntries[i].key, fEntries[i].value);
            }
            return hashtable;

        } // clone():Object

        //
        // Object methods
        //

        /** Returns a string representation of this object. */
        public String toString() {
            if (fSize == 0) {
                return "[]";
            }
            StringBuffer str = new StringBuffer();
            str.append('[');
            for (int i = 0; i < fSize; i++) {
                if (i > 0) {
                    str.append(',');
                }
                str.append('{');
                str.append(fEntries[i].key);
                str.append(',');
                str.append(fEntries[i].value);
                str.append('}');
            }
            str.append(']');
            return str.toString();
        } // toString():String

        //
        // Classes
        //

        /**
         * Hashtable entry.
         */
        public static final class Entry {

            //
            // Data
            //

            /** Key. */
            public Field key;

            /** Value. */
            public IDValue value;

        } // class Entry

    } // class OrderedHashtable
} // class SchemaValidator