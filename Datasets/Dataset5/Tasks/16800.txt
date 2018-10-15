String normalized = (defaultValue!=null)?defaultValue.stringValue():"";

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

import org.apache.xerces.impl.RevalidationHandler;
import org.apache.xerces.impl.dv.XSSimpleType;
import org.apache.xerces.impl.dv.ValidatedInfo;
import org.apache.xerces.impl.dv.DatatypeException;
import org.apache.xerces.impl.dv.InvalidDatatypeValueException;
import org.apache.xerces.impl.xs.identity.*;
import org.apache.xerces.impl.Constants;
import org.apache.xerces.impl.validation.ValidationManager;
import org.apache.xerces.util.XMLGrammarPoolImpl;
import org.apache.xerces.impl.XMLErrorReporter;
import org.apache.xerces.impl.xs.traversers.XSAttributeChecker;
import org.apache.xerces.impl.xs.models.CMBuilder;
import org.apache.xerces.impl.xs.models.XSCMValidator;
import org.apache.xerces.impl.xs.psvi.XSConstants;
import org.apache.xerces.impl.xs.psvi.XSObjectList;
import org.apache.xerces.impl.msg.XMLMessageFormatter;
import org.apache.xerces.impl.validation.ValidationState;
import org.apache.xerces.impl.XMLEntityManager;


import org.apache.xerces.util.AugmentationsImpl;
import org.apache.xerces.util.SymbolTable;
import org.apache.xerces.util.XMLSymbols;
import org.apache.xerces.util.XMLChar;
import org.apache.xerces.util.IntStack;
import org.apache.xerces.util.XMLResourceIdentifierImpl;
import org.apache.xerces.util.XMLAttributesImpl;

import org.apache.xerces.xni.Augmentations;
import org.apache.xerces.xni.NamespaceContext;
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
import org.apache.xerces.xni.parser.XMLDocumentSource;
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
import java.io.IOException;

/**
 * The XML Schema validator. The validator implements a document
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
             implements XMLComponent, XMLDocumentFilter, FieldActivator, RevalidationHandler {

    //
    // Constants
    //
    private static final boolean DEBUG = false;

    // feature identifiers

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

    /** Feature identifier: augment PSVI */
    protected static final String SCHEMA_AUGMENT_PSVI =
    Constants.XERCES_FEATURE_PREFIX + Constants.SCHEMA_AUGMENT_PSVI;

    /** Feature identifier: whether to recognize java encoding names */
    protected static final String ALLOW_JAVA_ENCODINGS =
    Constants.XERCES_FEATURE_PREFIX + Constants.ALLOW_JAVA_ENCODINGS_FEATURE;

    /** Feature identifier: whether to continue parsing a schema after a fatal error is encountered */
    protected static final String CONTINUE_AFTER_FATAL_ERROR =
    Constants.XERCES_FEATURE_PREFIX + Constants.CONTINUE_AFTER_FATAL_ERROR_FEATURE;

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

    /** Property identifier: JAXP schema language. */
    protected static final String JAXP_SCHEMA_LANGUAGE =
    Constants.JAXP_PROPERTY_PREFIX + Constants.SCHEMA_LANGUAGE;

    // recognized features and properties

    /** Recognized features. */
    private static final String[] RECOGNIZED_FEATURES = {
        VALIDATION,
        SCHEMA_VALIDATION,
        DYNAMIC_VALIDATION,
        SCHEMA_FULL_CHECKING,
        ALLOW_JAVA_ENCODINGS,
        CONTINUE_AFTER_FATAL_ERROR,
    };

    /** Feature defaults. */
    private static final Boolean[] FEATURE_DEFAULTS = {
        null,
        // NOTE: The following defaults are nulled out on purpose.
        //       If they are set, then when the XML Schema validator
        //       is constructed dynamically, these values may override
        //       those set by the application. This goes against the
        //       whole purpose of XMLComponent#getFeatureDefault but
        //       it can't be helped in this case. -Ac
        null, //Boolean.FALSE,
        null, //Boolean.FALSE,
        null, //Boolean.FALSE,
        null, //Boolean.FALSE,
        null, //Boolean.FALSE,
    };

    /** Recognized properties. */
    private static final String[] RECOGNIZED_PROPERTIES = {
        SYMBOL_TABLE,
        ERROR_REPORTER,
        ENTITY_RESOLVER,
        VALIDATION_MANAGER,
        SCHEMA_LOCATION,
        SCHEMA_NONS_LOCATION,
        JAXP_SCHEMA_SOURCE, 
        JAXP_SCHEMA_LANGUAGE, 
    };

    /** Property defaults. */
    private static final Object[] PROPERTY_DEFAULTS = {
        null,
        null,
        null,
        null,
        null,
        null,
        null,
        null,
    };

    // this is the number of valuestores of each kind
    // we expect an element to have.  It's almost
    // never > 1; so leave it at that.
    protected static final int ID_CONSTRAINT_NUM = 1;

    //
    // Data
    //

    /** current PSVI element info */
    protected ElementPSVImpl fCurrentPSVI = new ElementPSVImpl();

    // since it is the responsibility of each component to an
    // Augmentations parameter if one is null, to save ourselves from
    // having to create this object continually, it is created here.
    // If it is not present in calls that we're passing on, we *must*
    // clear this before we introduce it into the pipeline.
    protected final AugmentationsImpl fAugmentations = new AugmentationsImpl();

    // this is included for the convenience of handleEndElement
    protected XMLString fDefaultValue;

    // Validation features
    protected boolean fDynamicValidation = false;
    protected boolean fDoValidation = false;
    protected boolean fFullChecking = false;
    protected boolean fNormalizeData = true;
    protected boolean fSchemaElementDefault = true;
    protected boolean fAugPSVI = true;
    
    // to indicate whether we are in the scope of entity reference or CData
    protected boolean fEntityRef = false;
    protected boolean fInCDATA = false;

    // properties

    /** Symbol table. */
    protected SymbolTable fSymbolTable;

    /**
     * A wrapper of the standard error reporter. We'll store all schema errors
     * in this wrapper object, so that we can get all errors (error codes) of
     * a specific element. This is useful for PSVI.
     */
    protected final class XSIErrorReporter {

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

        // should be called when starting process an element or an attribute.
        // store the starting position for the current context
        public void pushContext() {
            if (!fAugPSVI)
                return;
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
            if (!fAugPSVI)
                return null;
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

        // should be called when an attribute is done: get all errors of 
        // this attribute, but leave the errors to the containing element
        // also called after an element was strictly assessed.
        public String[] mergeContext() {
            if (!fAugPSVI)
                return null;
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
            // don't resize the vector: leave the errors for this attribute
            // to the containing element
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
    protected final XSIErrorReporter fXSIErrorReporter = new XSIErrorReporter();

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
    final XMLResourceIdentifierImpl fResourceIdentifier = new XMLResourceIdentifierImpl();

    /** Schema Grammar Description passed,  to give a chance to application to supply the Grammar */
    protected final XSDDescription fXSDDescription = new XSDDescription() ;
    protected final Hashtable fLocationPairs = new Hashtable() ;
    protected final XMLSchemaLoader.LocationArray fNoNamespaceLocationArray = new XMLSchemaLoader.LocationArray();

    /** Base URI for the DOM revalidation*/
    protected String fBaseURI = null;

    // handlers

    /** Document handler. */
    protected XMLDocumentHandler fDocumentHandler;

    protected XMLDocumentSource fDocumentSource;

    //
    // XMLComponent methods
    //

    /**
     * Returns a list of feature identifiers that are recognized by
     * this component. This method may return null if no features
     * are recognized by this component.
     */
    public String[] getRecognizedFeatures() {
        return (String[])(RECOGNIZED_FEATURES.clone());
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
        return (String[])(RECOGNIZED_PROPERTIES.clone());
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

    /** 
     * Returns the default state for a feature, or null if this
     * component does not want to report a default value for this
     * feature.
     *
     * @param featureId The feature identifier.
     *
     * @since Xerces 2.2.0
     */
    public Boolean getFeatureDefault(String featureId) {
        for (int i = 0; i < RECOGNIZED_FEATURES.length; i++) {
            if (RECOGNIZED_FEATURES[i].equals(featureId)) {
                return FEATURE_DEFAULTS[i];
            }
        }
        return null;
    } // getFeatureDefault(String):Boolean

    /** 
     * Returns the default state for a property, or null if this
     * component does not want to report a default value for this
     * property. 
     *
     * @param propertyId The property identifier.
     *
     * @since Xerces 2.2.0
     */
    public Object getPropertyDefault(String propertyId) {
        for (int i = 0; i < RECOGNIZED_PROPERTIES.length; i++) {
            if (RECOGNIZED_PROPERTIES[i].equals(propertyId)) {
                return PROPERTY_DEFAULTS[i];
            }
        }
        return null;
    } // getPropertyDefault(String):Object

    //
    // XMLDocumentSource methods
    //

    /** Sets the document handler to receive information about the document. */
    public void setDocumentHandler(XMLDocumentHandler documentHandler) {
        fDocumentHandler = documentHandler;
    } // setDocumentHandler(XMLDocumentHandler)

    /** Returns the document handler */
    public XMLDocumentHandler getDocumentHandler() {
        return fDocumentHandler;
    } // setDocumentHandler(XMLDocumentHandler)


    //
    // XMLDocumentHandler methods
    //

    /** Sets the document source */
    public void setDocumentSource(XMLDocumentSource source){
        fDocumentSource = source;
    } // setDocumentSource

    /** Returns the document source */
    public XMLDocumentSource getDocumentSource (){
        return fDocumentSource;
    } // getDocumentSource

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
     * @param namespaceContext
     *                 The namespace context in effect at the
     *                 start of this document.
     *                 This object represents the current context.
     *                 Implementors of this class are responsible
     *                 for copying the namespace bindings from the
     *                 the current context (and its parent contexts)
     *                 if that information is important.
     * @param augs     Additional information that may include infoset augmentations
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void startDocument(XMLLocator locator, String encoding, 
                              NamespaceContext namespaceContext, Augmentations augs)
    throws XNIException {

        fValidationState.setNamespaceSupport(namespaceContext);
        fState4XsiType.setNamespaceSupport(namespaceContext);
        fState4ApplyDefault.setNamespaceSupport(namespaceContext);

        handleStartDocument(locator, encoding);
        // call handlers
        if (fDocumentHandler != null) {
            fDocumentHandler.startDocument(locator, encoding, namespaceContext, augs);
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
        if (DEBUG) {
            System.out.println("startPrefixMapping("+prefix+","+uri+")");
        }

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

        // in the case where there is a {value constraint}, and the element
        // doesn't have any text content, change emptyElement call to
        // start + characters + end
        fDefaultValue = null;
        // fElementDepth == -2 indicates that the schema validator was removed
        // from the pipeline. then we don't need to call handleEndElement.
        if (fElementDepth != -2)
            modifiedAugs = handleEndElement(element, modifiedAugs);

        // call handlers
        if (fDocumentHandler != null) {
            if (!fSchemaElementDefault || fDefaultValue == null) {
                fDocumentHandler.emptyElement(element, attributes, modifiedAugs);
            } else {
                fDocumentHandler.startElement(element, attributes, modifiedAugs);
                fDocumentHandler.characters(fDefaultValue, null);
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

        text = handleCharacters(text);
        // call handlers
        if (fDocumentHandler != null) {
            if (fNormalizeData && fUnionType) {
               // for union types we can't normalize data
               // thus we only need to send augs information if any;
               // the normalized data for union will be send
               // after normalization is performed (at the endElement())
               if (augs != null)
                   fDocumentHandler.characters(fEmptyXMLStr, augs);
            }
            else {
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
        fDefaultValue = null;
        Augmentations modifiedAugs = handleEndElement(element, augs);
        // call handlers
        if (fDocumentHandler != null) {
            if (!fSchemaElementDefault || fDefaultValue == null) {
                fDocumentHandler.endElement(element, modifiedAugs);
            } else {
                fDocumentHandler.characters(fDefaultValue, null);
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

        if (DEBUG) {
            System.out.println("endPrefixMapping("+prefix+")");
        }
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

        // call handlers
        if (fDocumentHandler != null) {
            fDocumentHandler.endDocument(augs);
        }

    } // endDocument(Augmentations)

    //
    // DOMRevalidationHandler methods
    //

    public void setBaseURI (String base){
        fBaseURI = base;
    }

    public boolean characterData(String data, Augmentations augs){

        fSawText = fSawText || data.length() > 0;
        
        // REVISIT: this methods basically duplicates implementation of
        //          handleCharacters(). We should be able to reuse some code

        // if whitespace == -1 skip normalization, because it is a complexType
        // or a union type.
        if (fNormalizeData && fWhiteSpace != -1 && fWhiteSpace != XSSimpleType.WS_PRESERVE) {
            // normalize data
            normalizeWhitespace(data, fWhiteSpace == XSSimpleType.WS_COLLAPSE);
            fBuffer.append(fNormalizedStr.ch, fNormalizedStr.offset, fNormalizedStr.length);
        }
        else {
            if (fAppendBuffer)
                fBuffer.append(data);
        }

        // When it's a complex type with element-only content, we need to
        // find out whether the content contains any non-whitespace character.
        boolean allWhiteSpace = true;
        if (fCurrentType != null && fCurrentType.getTypeCategory() == XSTypeDecl.COMPLEX_TYPE) {
            XSComplexTypeDecl ctype = (XSComplexTypeDecl)fCurrentType;
            if (ctype.fContentType == XSComplexTypeDecl.CONTENTTYPE_ELEMENT) {
                // data outside of element content
                for (int i=0; i< data.length(); i++) {
                    if (!XMLChar.isSpace(data.charAt(i))) {
                        allWhiteSpace = false;
                        fSawCharacters = true;
                        break;
                    }
                }
            }
        }

        // we saw first chunk of characters
        fFirstChunk = false;

        return allWhiteSpace;
    }

    public void elementDefault(String data){
        // no-op
    }


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

    //
    // Data
    //


    // Schema Normalization

    private static final boolean DEBUG_NORMALIZATION = false;
    // temporary empty string buffer.
    private final XMLString fEmptyXMLStr = new XMLString(null, 0, -1);
    // temporary character buffer, and empty string buffer.
    private static final int BUFFER_SIZE = 20;
    private final XMLString fNormalizedStr = new XMLString();
    private boolean fFirstChunk = true; // got first chunk in characters() (SAX)
    private boolean fTrailing = false;  // Previous chunk had a trailing space
    private short fWhiteSpace = -1;  //whiteSpace: preserve/replace/collapse
    private boolean fUnionType = false;


    /** Schema grammar resolver. */
    final XSGrammarBucket fGrammarBucket;
    final SubstitutionGroupHandler fSubGroupHandler;

    // Schema grammar loader
    final XMLSchemaLoader fSchemaLoader;

    /** the DV usd to convert xsi:type to a QName */
    // REVISIT: in new simple type design, make things in DVs static,
    //          so that we can QNameDV.getCompiledForm()
    final XSSimpleType fQNameDV = (XSSimpleType)SchemaGrammar.SG_SchemaNS.getGlobalTypeDecl(SchemaSymbols.ATTVAL_QNAME);

    /** used to build content models */
    // REVISIT: create decl pool, and pass it to each traversers
    final CMBuilder fCMBuilder = new CMBuilder();

    // state

    /** String representation of the validation root. */
    // REVISIT: what do we store here? QName, XPATH, some ID? use rawname now.
    String fValidationRoot;

    /** Skip validation: anything below this level should be skipped */
    int fSkipValidationDepth;

    /** anything above this level has validation_attempted != full */
    int fNFullValidationDepth;

    /** anything above this level has validation_attempted != none */
    int fNNoneValidationDepth;

    /** Element depth: -2: validator not in pipeline; >= -1 current depth. */
    int fElementDepth;

    /** Seen sub elements. */
    boolean fSubElement;

    /** Seen sub elements stack. */
    boolean[] fSubElementStack = new boolean[INITIAL_STACK_SIZE];

    /** Current element declaration. */
    XSElementDecl fCurrentElemDecl;

    /** Element decl stack. */
    XSElementDecl[] fElemDeclStack = new XSElementDecl[INITIAL_STACK_SIZE];

    /** nil value of the current element */
    boolean fNil;

    /** nil value stack */
    boolean[] fNilStack = new boolean[INITIAL_STACK_SIZE];

    /** notation value of the current element */
    XSNotationDecl fNotation;

    /** notation stack */
    XSNotationDecl[] fNotationStack = new XSNotationDecl[INITIAL_STACK_SIZE];

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

    /** whether the curret element is strictly assessed */
    boolean fStrictAssess = true;
    
    /** strict assess stack */
    boolean[] fStrictAssessStack = new boolean[INITIAL_STACK_SIZE];
    
    /** Temporary string buffers. */
    final StringBuffer fBuffer = new StringBuffer();

    /** Whether need to append characters to fBuffer */
    boolean fAppendBuffer = true;
    
    /** Did we see any character data? */
    boolean fSawText = false;

    /** stack to record if we saw character data */
    boolean[] fSawTextStack = new boolean[INITIAL_STACK_SIZE];
    
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
     * active XPath matchers are notified of startElement
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
        // initialize the schema loader
        fSchemaLoader = new XMLSchemaLoader(fXSIErrorReporter.fErrorReporter, fGrammarBucket, fSubGroupHandler, fCMBuilder);

        fState4XsiType.setExtraChecking(false);
        fState4ApplyDefault.setFacetChecking(false);

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
        fSchemaLoader.setProperty(ERROR_REPORTER, fXSIErrorReporter.fErrorReporter);

        // get symbol table. if it's a new one, add symbols to it.
        SymbolTable symbolTable = (SymbolTable)componentManager.getProperty(SYMBOL_TABLE);
        if (symbolTable != fSymbolTable) {
            fSchemaLoader.setProperty(SYMBOL_TABLE, symbolTable);
            fSymbolTable = symbolTable;
        }


        try {
            fDynamicValidation = componentManager.getFeature(DYNAMIC_VALIDATION);
        }
        catch (XMLConfigurationException e) {
            fDynamicValidation = false;
        }

        if (fDynamicValidation) {
            fDoValidation = true;
        }
        else {
            try {
                fDoValidation = componentManager.getFeature(VALIDATION);
            }
            catch (XMLConfigurationException e) {
                fDoValidation = false;
            }
        }

        if (fDoValidation) {
            try {
                fDoValidation = componentManager.getFeature(this.SCHEMA_VALIDATION);
            }
            catch (XMLConfigurationException e) {
            }
        }

        try {
            fFullChecking = componentManager.getFeature(SCHEMA_FULL_CHECKING);
        }
        catch (XMLConfigurationException e) {
            fFullChecking = false;
        }
        // the validator will do full checking anyway; the loader should
        // not (and in fact cannot) concern itself with this.
        fSchemaLoader.setFeature(SCHEMA_FULL_CHECKING, false);

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

        try {
            fAugPSVI = componentManager.getFeature(SCHEMA_AUGMENT_PSVI);
        }
        catch (XMLConfigurationException e) {
            fAugPSVI = true;
        }
        
        fEntityResolver = (XMLEntityResolver)componentManager.getProperty(ENTITY_MANAGER);
        fSchemaLoader.setEntityResolver(fEntityResolver);

        fValidationManager = (ValidationManager)componentManager.getProperty(VALIDATION_MANAGER);
        fValidationManager.addValidationState(fValidationState);
        fValidationState.setSymbolTable(fSymbolTable);

        //reset XSDDescription
        fLocationPairs.clear();
        fNoNamespaceLocationArray.resize(0 , 2) ;

        // get schema location properties
        try {
            fExternalSchemas = (String)componentManager.getProperty(SCHEMA_LOCATION);
            fExternalNoNamespaceSchema = (String)componentManager.getProperty(SCHEMA_NONS_LOCATION);
        }
        catch (XMLConfigurationException e) {
            fExternalSchemas = null;
            fExternalNoNamespaceSchema = null;
        }
        fSchemaLoader.setProperty(SCHEMA_LOCATION, fExternalSchemas);
        fSchemaLoader.setProperty(SCHEMA_NONS_LOCATION, fExternalNoNamespaceSchema);
        // store the external schema locations. they are set when reset is called,
        // so any other schemaLocation declaration for the same namespace will be
        // effectively ignored. becuase we choose to take first location hint
        // available for a particular namespace.
        storeLocations(fExternalSchemas, fExternalNoNamespaceSchema) ;

        try {
            fJaxpSchemaSource = componentManager.getProperty(JAXP_SCHEMA_SOURCE);
        }
        catch (XMLConfigurationException e){
            fJaxpSchemaSource = null;

        }
        fSchemaLoader.setProperty(JAXP_SCHEMA_SOURCE, fJaxpSchemaSource);
        fResourceIdentifier.clear();

        // clear grammars, and put the one for schema namespace there
        try {
            fGrammarPool = (XMLGrammarPool)componentManager.getProperty(XMLGRAMMAR_POOL);
        }
        catch (XMLConfigurationException e){
            fGrammarPool = null;
        }
        fSchemaLoader.setProperty(XMLGRAMMAR_POOL, fGrammarPool);

        // Copy the allow-java-encoding feature to the grammar loader.
        // REVISIT: what other fetures/properties do we want to copy?
        try {
            boolean allowJavaEncodings = componentManager.getFeature(ALLOW_JAVA_ENCODINGS);
            fSchemaLoader.setFeature(ALLOW_JAVA_ENCODINGS, allowJavaEncodings);
        }
        catch (XMLConfigurationException e){
        }

        // get continue-after-fatal-error feature
        try {
            boolean fatalError = componentManager.getFeature(CONTINUE_AFTER_FATAL_ERROR);
            fSchemaLoader.setFeature(CONTINUE_AFTER_FATAL_ERROR, fatalError);
        }
        catch (XMLConfigurationException e){
        }

        // clear grammars, and put the one for schema namespace there
        // logic for resetting grammar-related components moved
        // to schema loader
        fSchemaLoader.reset();

        // initialize state
        fCurrentElemDecl = null;
        fCurrentCM = null;
        fCurrCMState = null;
        fSkipValidationDepth = -1;
        fNFullValidationDepth = -1;
        fNNoneValidationDepth = -1;
        fElementDepth = -1;
        fSubElement = false;

        // datatype normalization
        fEntityRef = false;
        fInCDATA = false;

        fMatcherStack.clear();
        fBaseURI = null;

        fState4XsiType.setSymbolTable(symbolTable);
        fState4ApplyDefault.setSymbolTable(symbolTable);

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
    public void startValueScopeFor(IdentityConstraint identityConstraint,
                int initialDepth)
    throws XNIException {

        ValueStoreBase valueStore = fValueStoreCache.getValueStoreFor(identityConstraint, initialDepth);
        valueStore.startValueScope();

    } // startValueScopeFor(IdentityConstraint identityConstraint)

    /**
     * Request to activate the specified field. This method returns the
     * matcher for the field.
     *
     * @param field The field to activate.
     */
    public XPathMatcher activateField(Field field, int initialDepth) {
        ValueStore valueStore = fValueStoreCache.getValueStoreFor(field.getIdentityConstraint(), initialDepth);
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
    public void endValueScopeFor(IdentityConstraint identityConstraint, int initialDepth)
    throws XNIException {

        ValueStoreBase valueStore = fValueStoreCache.getValueStoreFor(identityConstraint, initialDepth);
        valueStore.endValueScope();

    } // endValueScopeFor(IdentityConstraint)

    // a utility method for Idnetity constraints
    private void activateSelectorFor(IdentityConstraint ic) throws XNIException {
        Selector selector = ic.getSelector();
        FieldActivator activator = this;
        if (selector == null)
            return;
        XPathMatcher matcher = selector.createMatcher(activator, fElementDepth);
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
            boolean[] newArrayB = new boolean[newSize];
            System.arraycopy(fSubElementStack, 0, newArrayB, 0, fElementDepth);
            fSubElementStack = newArrayB;

            XSElementDecl[] newArrayE = new XSElementDecl[newSize];
            System.arraycopy(fElemDeclStack, 0, newArrayE, 0, fElementDepth);
            fElemDeclStack = newArrayE;

            newArrayB = new boolean[newSize];
            System.arraycopy(fNilStack, 0, newArrayB, 0, fElementDepth);
            fNilStack = newArrayB;

            XSNotationDecl[] newArrayN = new XSNotationDecl[newSize];
            System.arraycopy(fNotationStack, 0, newArrayN, 0, fElementDepth);
            fNotationStack = newArrayN;

            XSTypeDecl[] newArrayT = new XSTypeDecl[newSize];
            System.arraycopy(fTypeStack, 0, newArrayT, 0, fElementDepth);
            fTypeStack = newArrayT;

            XSCMValidator[] newArrayC = new XSCMValidator[newSize];
            System.arraycopy(fCMStack, 0, newArrayC, 0, fElementDepth);
            fCMStack = newArrayC;

            newArrayB = new boolean[newSize];
            System.arraycopy(fSawTextStack, 0, newArrayB, 0, fElementDepth);
            fSawTextStack = newArrayB;
            
            newArrayB = new boolean[newSize];
            System.arraycopy(fStringContent, 0, newArrayB, 0, fElementDepth);
            fStringContent = newArrayB;

            newArrayB = new boolean[newSize];
            System.arraycopy(fSawChildrenStack, 0, newArrayB, 0, fElementDepth);
            fSawChildrenStack = newArrayB;

            newArrayB = new boolean[newSize];
            System.arraycopy(fStrictAssessStack, 0, newArrayB, 0, fElementDepth);
            fStrictAssessStack = newArrayB;
            
            int[][] newArrayIA = new int[newSize][];
            System.arraycopy(fCMStateStack, 0, newArrayIA, 0, fElementDepth);
            fCMStateStack = newArrayIA;
        }

    } // ensureStackCapacity

    // handle start document
    void handleStartDocument(XMLLocator locator, String encoding) {
        fValueStoreCache.startDocument();
    } // handleStartDocument(XMLLocator,String)

    void handleEndDocument() {
        fValueStoreCache.endDocument();
    } // handleEndDocument()

    // handle character contents
    // returns the normalized string if possible, otherwise the original string
    XMLString handleCharacters(XMLString text) {

        if (fSkipValidationDepth >= 0)
            return text;

        fSawText = fSawText || text.length > 0;
        
        // Note: data in EntityRef and CDATA is normalized as well
        // if whitespace == -1 skip normalization, because it is a complexType
        // or a union type.
        if (fNormalizeData && fWhiteSpace != -1 && fWhiteSpace != XSSimpleType.WS_PRESERVE) {
            // normalize data
            normalizeWhitespace(text, fWhiteSpace == XSSimpleType.WS_COLLAPSE);
            text = fNormalizedStr;
        }
        if (fAppendBuffer)
            fBuffer.append(text.ch, text.offset, text.length);
        
        // When it's a complex type with element-only content, we need to
        // find out whether the content contains any non-whitespace character.
        if (fCurrentType != null && fCurrentType.getTypeCategory() == XSTypeDecl.COMPLEX_TYPE) {
            XSComplexTypeDecl ctype = (XSComplexTypeDecl)fCurrentType;
            if (ctype.fContentType == XSComplexTypeDecl.CONTENTTYPE_ELEMENT) {
                // data outside of element content
                for (int i=text.offset; i< text.offset+text.length; i++) {
                    if (!XMLChar.isSpace(text.ch[i])) {
                        fSawCharacters = true;
                        break;
                    }
                }
            }
        }

        // we saw first chunk of characters
        fFirstChunk = false;

        return text;
    } // handleCharacters(XMLString)

    /**
     * Normalize whitespace in an XMLString according to the rules defined
     * in XML Schema specifications.
     * @param value    The string to normalize.
     * @param collapse replace or collapse
     */
    private void normalizeWhitespace( XMLString value, boolean collapse) {
        boolean skipSpace = collapse;
        boolean sawNonWS = false;
        int leading = 0;
        int trailing = 0;
        char c;
        int size = value.offset+value.length;
        
        // ensure the ch array is big enough
        if (fNormalizedStr.ch == null || fNormalizedStr.ch.length < value.length+1) {
            fNormalizedStr.ch = new char[value.length+1];
        }
        // don't include the leading ' ' for now. might include it later.
        fNormalizedStr.offset = 1;
        fNormalizedStr.length = 1;
        
        for (int i = value.offset; i < size; i++) {
            c = value.ch[i];
            if (XMLChar.isSpace(c)) {
                if (!skipSpace) {
                    // take the first whitespace as a space and skip the others
                    fNormalizedStr.ch[fNormalizedStr.length++] = ' ';
                    skipSpace = collapse;
                }
                if (!sawNonWS) {
                    // this is a leading whitespace, record it
                    leading = 1;
                }
            }
            else {
                fNormalizedStr.ch[fNormalizedStr.length++] = c;
                skipSpace = false;
                sawNonWS = true;
            }
        }
        if (skipSpace) {
            if ( fNormalizedStr.length > 1) {
                // if we finished on a space trim it but also record it
                fNormalizedStr.length--;
                trailing = 2;
            }
            else if (leading != 0 && !sawNonWS) {
                // if all we had was whitespace we skipped record it as
                // trailing whitespace as well
                trailing = 2;
            }
        }

        // 0 if no triming is done or if there is neither leading nor
        //   trailing whitespace,
        // 1 if there is only leading whitespace,
        // 2 if there is only trailing whitespace,
        // 3 if there is both leading and trailing whitespace.
        int spaces = collapse ? leading + trailing : 0;
        if (fNormalizedStr.length > 1) {
            if (!fFirstChunk && (fWhiteSpace==XSSimpleType.WS_COLLAPSE) ) {
                if (fTrailing) {
                    // previous chunk ended on whitespace
                    // insert whitespace
                    fNormalizedStr.offset = 0;
                    fNormalizedStr.ch[0] = ' ';
                } else if (spaces == 1 || spaces == 3) {
                    // previous chunk ended on character,
                    // this chunk starts with whitespace
                    fNormalizedStr.offset = 0;
                    fNormalizedStr.ch[0] = ' ';
                }
            }
        }
        
        // The length includes the leading ' '. Now removing it.
        fNormalizedStr.length -= fNormalizedStr.offset;
        
        fTrailing = (spaces > 1)?true:false;
    }


    private void normalizeWhitespace( String value, boolean collapse) {
        boolean skipSpace = collapse;
        char c;
        int size = value.length();

        // ensure the ch array is big enough
        if (fNormalizedStr.ch == null || fNormalizedStr.ch.length < size) {
            fNormalizedStr.ch = new char[size];
        }
        fNormalizedStr.offset = 0;
        fNormalizedStr.length = 0;

        for (int i = 0; i < size; i++) {
            c = value.charAt(i);
            if (XMLChar.isSpace(c)) {
                if (!skipSpace) {
                    // take the first whitespace as a space and skip the others
                    fNormalizedStr.ch[fNormalizedStr.length++] = ' ';
                    skipSpace = collapse;
                }
            }
            else {
                fNormalizedStr.ch[fNormalizedStr.length++] = c;
                skipSpace = false;
            }
        }
        if (skipSpace) {
            if (fNormalizedStr.length != 0)
                // if we finished on a space trim it but also record it
                fNormalizedStr.length--;
        }
    }

    // handle ignorable whitespace
    void handleIgnorableWhitespace(XMLString text) {

        if (fSkipValidationDepth >= 0)
            return;

        // REVISIT: the same process needs to be performed as handleCharacters.
        // only it's simpler here: we know all characters are whitespaces.

    } // handleIgnorableWhitespace(XMLString)

    /** Handle element. */
    Augmentations handleStartElement(QName element, XMLAttributes attributes, Augmentations augs) {

        if (DEBUG) {
            System.out.println("==>handleStartElement: " +element);
        }

        // root element
        if (fElementDepth == -1 && fValidationManager.isGrammarFound()) {
            // if a DTD grammar is found, we do the same thing as Dynamic:
            // if a schema grammar is found, validation is performed;
            // otherwise, skip the whole document.
            fDynamicValidation = true;
        }

        // get xsi:schemaLocation and xsi:noNamespaceSchemaLocation attributes,
        // parse them to get the grammars

        String sLocation = attributes.getValue(SchemaSymbols.URI_XSI, SchemaSymbols.XSI_SCHEMALOCATION);
        String nsLocation = attributes.getValue(SchemaSymbols.URI_XSI, SchemaSymbols.XSI_NONAMESPACESCHEMALOCATION);
        //store the location hints..  we need to do it so that we can defer the loading of grammar until
        //there is a reference to a component from that namespace. To provide location hints to the
        //application for a namespace
        storeLocations(sLocation, nsLocation) ;

        // if we are in the content of "skip", then just skip this element
        // REVISIT:  is this the correct behaviour for ID constraints?  -NG
        if (fSkipValidationDepth >= 0) {
            fElementDepth++;
            if (fAugPSVI)
                augs = getEmptyAugs(augs);
            return augs;
        }

        //try to find schema grammar by different means..
        SchemaGrammar sGrammar = findSchemaGrammar(XSDDescription.CONTEXT_ELEMENT,
                                                   element.uri, null,
                                                   element, attributes);

        // if we are not skipping this element, and there is a content model,
        // we try to find the corresponding decl object for this element.
        // the reason we move this part of code here is to make sure the
        // error reported here (if any) is stored within the parent element's
        // context, instead of that of the current element.
        Object decl = null;
        if (fCurrentCM != null) {
            decl = fCurrentCM.oneTransition(element, fCurrCMState, fSubGroupHandler);
            // it could be an element decl or a wildcard decl
            if (fCurrCMState[0] == XSCMValidator.FIRST_ERROR) {
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
            fSubElementStack[fElementDepth] = true;
            fSubElement = false;
            fElemDeclStack[fElementDepth] = fCurrentElemDecl;
            fNilStack[fElementDepth] = fNil;
            fNotationStack[fElementDepth] = fNotation;
            fTypeStack[fElementDepth] = fCurrentType;
            fStrictAssessStack[fElementDepth] = fStrictAssess;
            fCMStack[fElementDepth] = fCurrentCM;
            fCMStateStack[fElementDepth] = fCurrCMState;
            fSawTextStack[fElementDepth] = fSawText;
            fStringContent[fElementDepth] = fSawCharacters;
            fSawChildrenStack[fElementDepth] = fSawChildren;
        }

        // increase the element depth after we've saved
        // all states for the parent element
        fElementDepth++;
        fCurrentElemDecl = null;
        XSWildcardDecl wildcard = null;
        fCurrentType = null;
        fStrictAssess = true;
        fNil = false;
        fNotation = null;

        // and the buffer to hold the value of the element
        fBuffer.setLength(0);
        fSawText = false;
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
            if (fAugPSVI)
                augs = getEmptyAugs(augs);
            return augs;
        }

        // try again to get the element decl:
        // case 1: find declaration for root element
        // case 2: find declaration for element from another namespace
        if (fCurrentElemDecl == null) {
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
        String xsiType = attributes.getValue(SchemaSymbols.URI_XSI, SchemaSymbols.XSI_TYPE);
        if (xsiType != null)
            fCurrentType = getAndCheckXsiType(element, xsiType, attributes);

        // if the element decl is not found
        if (fCurrentType == null) {
            // if this is the validation root, report an error, because
            // we can't find eith decl or type for this element
            // REVISIT: should we report error, or warning?
            if (fElementDepth == 0) {
                // for dynamic validation, skip the whole content,
                // because no grammar was found.
                if (fDynamicValidation) {
                    // no schema grammar was found, but it's either dynamic
                    // validation, or another kind of grammar was found (DTD,
                    // for example). The intended behavior here is to skip
                    // the whole document. To improve performance, we try to
                    // remove the validator from the pipeline, since it's not
                    // supposed to do anything.
                    if (fDocumentSource != null) {
                        fDocumentSource.setDocumentHandler(fDocumentHandler);
                        if (fDocumentHandler != null)
                            fDocumentHandler.setDocumentSource(fDocumentSource);
                        // indicate that the validator was removed.
                        fElementDepth = -2;
                        return augs;
                    }

                    fSkipValidationDepth = fElementDepth;
                    if (fAugPSVI)
                        augs = getEmptyAugs(augs);
                    return augs;
                }
                // We don't call reportSchemaError here, because the spec
                // doesn't think it's invalid not to be able to find a
                // declaration or type definition for an element. Xerces is
                // reporting it as an error for historical reasons, but in
                // PSVI, we shouldn't mark this element as invalid because
                // of this. - SG
                fXSIErrorReporter.fErrorReporter.reportError(XSMessageFormatter.SCHEMA_DOMAIN,
                                                             "cvc-elt.1",
                                                             new Object[]{element.rawname},
                                                             XMLErrorReporter.SEVERITY_ERROR);
            }
            // if wildcard = strict, report error
            else if (wildcard != null &&
                     wildcard.fProcessContents == XSWildcardDecl.PC_STRICT) {
                // report error, because wilcard = strict
                reportSchemaError("cvc-complex-type.2.4.c", new Object[]{element.rawname});
            }
            // no element decl or type found for this element.
            // Allowed by the spec, we can choose to either laxly assess this
            // element, or to skip it. Now we choose lax assessment.
            fCurrentType = SchemaGrammar.fAnyType;
            fStrictAssess = false;
            fNFullValidationDepth = fElementDepth;
            // any type has mixed content, so we don't need to append buffer
            fAppendBuffer = false;
        }
        else {
            fNNoneValidationDepth = fElementDepth;
            // if the element has a fixed value constraint, we need to append
            if (fCurrentElemDecl != null &&
                fCurrentElemDecl.getConstraintType() == XSConstants.VC_FIXED) {
                fAppendBuffer = true;
            }
            // if the type is simple, we need to append
            else if (fCurrentType.getTypeCategory() == XSTypeDecl.SIMPLE_TYPE) {
                fAppendBuffer = true;
            }
            else {
                // if the type is simple content complex type, we need to append
                XSComplexTypeDecl ctype = (XSComplexTypeDecl)fCurrentType;
                fAppendBuffer = (ctype.fContentType == XSComplexTypeDecl.CONTENTTYPE_SIMPLE);
            }
        }

        // make the current element validation root
        if (fElementDepth == 0) {
            fValidationRoot = element.rawname;
        }

        // update normalization flags
        if (fNormalizeData) {
            // reset values
            fFirstChunk = true;
            fTrailing = false;
            fUnionType = false;
            fWhiteSpace = -1;
        }

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
        // normalization: simple type
        else if (fNormalizeData) {
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
        String xsiNil = attributes.getValue(SchemaSymbols.URI_XSI, SchemaSymbols.XSI_NIL);
        // only deal with xsi:nil when there is an element declaration
        if (xsiNil != null && fCurrentElemDecl != null)
            fNil = getXsiNil(element, xsiNil);

        // now validate everything related with the attributes
        // first, get the attribute group
        XSAttributeGroupDecl attrGrp = null;
        if (fCurrentType.getTypeCategory() == XSTypeDecl.COMPLEX_TYPE) {
            XSComplexTypeDecl ctype = (XSComplexTypeDecl)fCurrentType;
            attrGrp = ctype.getAttrGrp();
        }
        processAttributes(element, attributes, attrGrp);

        // add default attributes
        if (attrGrp != null) {
            addDefaultAttributes(element, attributes, attrGrp);
        }

        // activate identity constraints
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

        if (fAugPSVI) {
            augs = getEmptyAugs(augs);

            // PSVI: add validation context
            fCurrentPSVI.fValidationContext = fValidationRoot;
            // PSVI: add element declaration
            fCurrentPSVI.fDeclaration = fCurrentElemDecl;
            // PSVI: add element type
            fCurrentPSVI.fTypeDecl = fCurrentType;
            // PSVI: add notation attribute
            fCurrentPSVI.fNotation = fNotation;
        }

        return augs;

    } // handleStartElement(QName,XMLAttributes,boolean)


    /**
     *  Handle end element. If there is not text content, and there is a
     *  {value constraint} on the corresponding element decl, then
     * set the fDefaultValue XMLString representing the default value.
     */
    Augmentations handleEndElement(QName element, Augmentations augs) {

        if (DEBUG) {
            System.out.println("==>handleEndElement:" +element);
        }
        // if we are skipping, return
        if (fSkipValidationDepth >= 0) {
            // but if this is the top element that we are skipping,
            // restore the states.
            if (fSkipValidationDepth == fElementDepth &&
                fSkipValidationDepth > 0) {
                // set the partial validation depth to the depth of parent
                fNFullValidationDepth = fSkipValidationDepth-1;
                fSkipValidationDepth = -1;
                fElementDepth--;
                fSubElement = fSubElementStack[fElementDepth];
                fCurrentElemDecl = fElemDeclStack[fElementDepth];
                fNil = fNilStack[fElementDepth];
                fNotation = fNotationStack[fElementDepth];
                fCurrentType = fTypeStack[fElementDepth];
                fCurrentCM = fCMStack[fElementDepth];
                fStrictAssess = fStrictAssessStack[fElementDepth];
                fCurrCMState = fCMStateStack[fElementDepth];
                fSawText = fSawTextStack[fElementDepth];
                fSawCharacters = fStringContent[fElementDepth];
                fSawChildren = fSawChildrenStack[fElementDepth];
            }
            else {
                fElementDepth--;
            }

            // PSVI: validation attempted:
            // use default values in psvi item for
            // validation attempted, validity, and error codes

            // check extra schema constraints on root element
            if (fElementDepth == -1 && fFullChecking) {
                XSConstraints.fullSchemaChecking(fGrammarBucket, fSubGroupHandler, fCMBuilder, fXSIErrorReporter.fErrorReporter);
            }

            if (fAugPSVI)
                augs = getEmptyAugs(augs);
            return augs;
        }

        // now validate the content of the element
        processElementContent(element);

        // Element Locally Valid (Element)
        // 6 The element information item must be valid with respect to each of the {identity-constraint definitions} as per Identity-constraint Satisfied (3.11.4).

        // call matchers and de-activate context
        int oldCount = fMatcherStack.getMatcherCount();
        for (int i = oldCount - 1; i >= 0; i--) {
            XPathMatcher matcher = fMatcherStack.getMatcherAt(i);
            matcher.endElement(element, fCurrentElemDecl,
                               fDefaultValue == null ?
                               fValidatedInfo.normalizedValue :
                               fCurrentElemDecl.fDefault.normalizedValue);
        }
        if (fMatcherStack.size() > 0) {
            fMatcherStack.popContext();
        }
        int newCount = fMatcherStack.getMatcherCount();
        // handle everything *but* keyref's.
        for (int i = oldCount - 1; i >= newCount; i--) {
            XPathMatcher matcher = fMatcherStack.getMatcherAt(i);
            if(matcher instanceof Selector.Matcher) {
                Selector.Matcher selMatcher = (Selector.Matcher)matcher;
                IdentityConstraint id;
                if ((id = selMatcher.getIdentityConstraint()) != null && id.getCategory() != IdentityConstraint.IC_KEYREF) {
                    fValueStoreCache.transplant(id, selMatcher.getInitialDepth());
                }
            }
        }
        // now handle keyref's/...
        for (int i = oldCount - 1; i >= newCount; i--) {
            XPathMatcher matcher = fMatcherStack.getMatcherAt(i);
            if(matcher instanceof Selector.Matcher) {
                Selector.Matcher selMatcher = (Selector.Matcher)matcher;
                IdentityConstraint id;
                if ((id = selMatcher.getIdentityConstraint()) != null && id.getCategory() == IdentityConstraint.IC_KEYREF) {
                    ValueStoreBase values = fValueStoreCache.getValueStoreFor(id, selMatcher.getInitialDepth());
                    if (values != null) // nothing to do if nothing matched!
                        values.endDocumentFragment();
                }
            }
        }
        fValueStoreCache.endElement();
        
        SchemaGrammar[] grammars = null;
        // have we reached the end tag of the validation root?
        if (fElementDepth == 0) {
            // 7 If the element information item is the validation root, it must be valid per Validation Root Valid (ID/IDREF) (3.3.4).
            String invIdRef = fValidationState.checkIDRefID();
            if (invIdRef != null) {
                reportSchemaError("cvc-id.1", new Object[]{invIdRef});
            }
            // check extra schema constraints
            if (fFullChecking) {
                XSConstraints.fullSchemaChecking(fGrammarBucket, fSubGroupHandler, fCMBuilder, fXSIErrorReporter.fErrorReporter);
            }
            fValidationState.resetIDTables();

            grammars = fGrammarBucket.getGrammars();
            // return the final set of grammars validator ended up with
            if (fGrammarPool != null) {
                fGrammarPool.cacheGrammars(XMLGrammarDescription.XML_SCHEMA, grammars);
            }
            augs = endElementPSVI(true, grammars, augs);
        }
        else {
            augs = endElementPSVI(false, grammars, augs);

            // decrease element depth and restore states
            fElementDepth--;

            // get the states for the parent element.
            fSubElement = fSubElementStack[fElementDepth];
            fCurrentElemDecl = fElemDeclStack[fElementDepth];
            fNil = fNilStack[fElementDepth];
            fNotation = fNotationStack[fElementDepth];
            fCurrentType = fTypeStack[fElementDepth];
            fCurrentCM = fCMStack[fElementDepth];
            fStrictAssess = fStrictAssessStack[fElementDepth];
            fCurrCMState = fCMStateStack[fElementDepth];
            fSawText = fSawTextStack[fElementDepth];
            fSawCharacters = fStringContent[fElementDepth];
            fSawChildren = fSawChildrenStack[fElementDepth];

            // We should have a stack for whitespace value, and pop it up here.
            // But when fWhiteSpace != -1, and we see a sub-element, it must be
            // an error (at least for Schema 1.0). So for valid documents, the
            // only value we are going to push/pop in the stack is -1.
            // Here we just mimic the effect of popping -1. -SG
            fWhiteSpace = -1;
            // Same for append buffer. Simple types and elements with fixed
            // value constraint don't allow sub-elements. -SG
            fAppendBuffer = false;
            // same here.
            fUnionType = false;
        }

        return augs;
    } // handleEndElement(QName,boolean)*/

    final Augmentations endElementPSVI (boolean root, SchemaGrammar[] grammars, 
                               Augmentations augs){

        if (fAugPSVI) {
            augs = getEmptyAugs(augs);

            // the 4 properties sent on startElement calls
            fCurrentPSVI.fDeclaration = this.fCurrentElemDecl;
            fCurrentPSVI.fTypeDecl = this.fCurrentType;
            fCurrentPSVI.fNotation = this.fNotation;
            fCurrentPSVI.fValidationContext = this.fValidationRoot;
            // PSVI: validation attempted
            // nothing below or at the same level has none or partial
            // (which means this level is strictly assessed, and all chidren
            // are full), so this one has full
            if (fElementDepth > fNFullValidationDepth) {
                fCurrentPSVI.fValidationAttempted = ElementPSVI.VALIDATION_FULL;
            }
            // nothing below or at the same level has full or partial
            // (which means this level is not strictly assessed, and all chidren
            // are none), so this one has none
            else if (fElementDepth > fNNoneValidationDepth) {
                fCurrentPSVI.fValidationAttempted = ElementPSVI.VALIDATION_NONE;
            }
            // otherwise partial, and anything above this level will be partial
            else {
                fCurrentPSVI.fValidationAttempted = ElementPSVI.VALIDATION_PARTIAL;
                fNFullValidationDepth = fNNoneValidationDepth = fElementDepth-1;
            }
            
            if (fDefaultValue != null)
                fCurrentPSVI.fSpecified = true;
            fCurrentPSVI.fNil = fNil;
            fCurrentPSVI.fMemberType = fValidatedInfo.memberType;
            fCurrentPSVI.fNormalizedValue = fValidatedInfo.normalizedValue;

            if (fStrictAssess) {
                // get all errors for the current element, its attribute,
                // and subelements (if they were strictly assessed).
                // any error would make this element invalid.
                // and we merge these errors to the parent element.
                String[] errors = fXSIErrorReporter.mergeContext();
    
                // PSVI: error codes
                fCurrentPSVI.fErrorCodes = errors;
                // PSVI: validity
                fCurrentPSVI.fValidity = (errors == null) ?
                                         ElementPSVI.VALIDITY_VALID :
                                         ElementPSVI.VALIDITY_INVALID;
            }
            else {
                // PSVI: validity
                fCurrentPSVI.fValidity = ElementPSVI.VALIDITY_UNKNOWN;
                // Discard the current context: ignore any error happened within
                // the sub-elements/attributes of this element, because those
                // errors won't affect the validity of the parent elements.
                fXSIErrorReporter.popContext();
            }

            if (root) {
                // store [schema information] in the PSVI
                fCurrentPSVI.fSchemaInformation = new XSModelImpl(grammars);
            }
        }

        return augs;

    }

    Augmentations getEmptyAugs(Augmentations augs) {
        if (augs == null) {
            augs = fAugmentations;
            augs.clear();
        }
        augs.putItem(Constants.ELEMENT_PSVI, fCurrentPSVI);
        fCurrentPSVI.reset();
        
        return augs;
    }
    
    void storeLocations(String sLocation, String nsLocation){
        if (sLocation != null) {
            if(!XMLSchemaLoader.tokenizeSchemaLocationStr(sLocation, fLocationPairs)) { // error!
                fXSIErrorReporter.reportError(XSMessageFormatter.SCHEMA_DOMAIN,
                                              "SchemaLocation",
                                              new Object[]{sLocation},
                                              XMLErrorReporter.SEVERITY_WARNING);
            }
        }
        if (nsLocation != null) {
            fNoNamespaceLocationArray.addLocation(nsLocation);
            fLocationPairs.put(XMLSymbols.EMPTY_STRING, fNoNamespaceLocationArray);
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
            if (fBaseURI != null) {
                fXSDDescription.setBaseSystemId(fBaseURI);
            }

            String[] temp = null ;
            if( namespace != null){
                Object locationArray = fLocationPairs.get(namespace) ;
                if(locationArray != null)
                    temp = ((XMLSchemaLoader.LocationArray)locationArray).getLocationArray() ;
            }else{
                temp = fNoNamespaceLocationArray.getLocationArray() ;
            }
            if (temp != null && temp.length != 0) {
                fXSDDescription.fLocationHints = new String [temp.length] ;
                System.arraycopy(temp, 0 , fXSDDescription.fLocationHints, 0, temp.length );
            }

            // give a chance to application to be able to retreive the grammar.
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
                try {
                    XMLInputSource xis = XMLSchemaLoader.resolveDocument(fXSDDescription, fLocationPairs, fEntityResolver);
                    grammar = fSchemaLoader.loadSchema(fXSDDescription, xis, fLocationPairs);
                } catch (IOException ex) {
                    fXSIErrorReporter.fErrorReporter.reportError(XSMessageFormatter.SCHEMA_DOMAIN,
                              "schema_reference.4",
                              new Object[]{fXSDDescription.getLocationHints()[0]},
                              XMLErrorReporter.SEVERITY_WARNING);
                }
            }
        }

        return grammar ;

    }//findSchemaGrammar

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
            reportSchemaError(e.getKey(), e.getArgs());
            reportSchemaError("cvc-elt.4.1", new Object[]{element.rawname, SchemaSymbols.URI_XSI+","+SchemaSymbols.XSI_TYPE, xsiType});
            return null;
        }

        // 4.2 The local name and namespace name (as defined in QName Interpretation (3.15.3)), of the actual value of that attribute information item must resolve to a type definition, as defined in QName resolution (Instance) (3.15.4)
        XSTypeDecl type = null;
        // if the namespace is schema namespace, first try built-in types
        if (typeName.uri == SchemaSymbols.URI_SCHEMAFORSCHEMA) {
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
            reportSchemaError("cvc-elt.3.1", new Object[]{element.rawname, SchemaSymbols.URI_XSI+","+SchemaSymbols.XSI_NIL});
        }
        // 3.2 If {nillable} is true and there is such an attribute information item and its actual value is true , then all of the following must be true:
        // 3.2.2 There must be no fixed {value constraint}.
        else {
            String value = xsiNil.trim();
            if (value.equals(SchemaSymbols.ATTVAL_TRUE) ||
                value.equals(SchemaSymbols.ATTVAL_TRUE_1)) {
                if (fCurrentElemDecl != null &&
                    fCurrentElemDecl.getConstraintType() == XSConstants.VC_FIXED) {
                    reportSchemaError("cvc-elt.3.2.2", new Object[]{element.rawname, SchemaSymbols.URI_XSI+","+SchemaSymbols.XSI_NIL});
                }
                return true;
            }
        }
        return false;
    }

    void processAttributes(QName element, XMLAttributes attributes, XSAttributeGroupDecl attrGrp) {

        if (DEBUG) {
            System.out.println("==>processAttributes: " +attributes.getLength());
        }

        // whether we have seen a Wildcard ID.
        String wildcardIDName = null;

        // for each present attribute
        int attCount = attributes.getLength();

        Augmentations augs = null;
        AttributePSVImpl attrPSVI = null;

        boolean isSimple = fCurrentType == null ||
                           fCurrentType.getTypeCategory() == XSTypeDecl.SIMPLE_TYPE;
        
        XSObjectList attrUses = null;
        int useCount = 0;
        XSWildcardDecl attrWildcard = null;
        if (!isSimple) {
            attrUses = attrGrp.getAttributeUses();
            useCount = attrUses.getLength();
            attrWildcard = attrGrp.fAttributeWC;
        }

        // Element Locally Valid (Complex Type)
        // 3 For each attribute information item in the element information item's [attributes] excepting those whose [namespace name] is identical to http://www.w3.org/2001/XMLSchema-instance and whose [local name] is one of type, nil, schemaLocation or noNamespaceSchemaLocation, the appropriate case among the following must be true:
        // get the corresponding attribute decl
        for (int index = 0; index < attCount; index++) {

            attributes.getName(index, fTempQName);

            if (DEBUG) {
                System.out.println("==>process attribute: "+fTempQName);
            }

            if (fAugPSVI) {
                augs = attributes.getAugmentations(index);
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

            // Element Locally Valid (Type)
            // 3.1.1 The element information item's [attributes] must be empty, excepting those
            // whose [namespace name] is identical to http://www.w3.org/2001/XMLSchema-instance and
            // whose [local name] is one of type, nil, schemaLocation or noNamespaceSchemaLocation.
    
            // for the 4 xsi attributes, get appropriate decl, and validate
            if (fTempQName.uri == SchemaSymbols.URI_XSI) {
                XSAttributeDecl attrDecl = null;
                if (fTempQName.localpart == SchemaSymbols.XSI_SCHEMALOCATION)
                    attrDecl = SchemaGrammar.SG_XSI.getGlobalAttributeDecl(SchemaSymbols.XSI_SCHEMALOCATION);
                else if (fTempQName.localpart == SchemaSymbols.XSI_NONAMESPACESCHEMALOCATION)
                    attrDecl = SchemaGrammar.SG_XSI.getGlobalAttributeDecl(SchemaSymbols.XSI_NONAMESPACESCHEMALOCATION);
                else if (fTempQName.localpart == SchemaSymbols.XSI_NIL)
                    attrDecl = SchemaGrammar.SG_XSI.getGlobalAttributeDecl(SchemaSymbols.XSI_NIL);
                else if (fTempQName.localpart == SchemaSymbols.XSI_TYPE)
                    attrDecl = SchemaGrammar.SG_XSI.getGlobalAttributeDecl(SchemaSymbols.XSI_TYPE);
                if (attrDecl != null) {
                    processOneAttribute(element, attributes, index,
                                        attrDecl, null, attrPSVI);
                    continue;
                }
            }

            // for namespace attributes, no_validation/unknow_validity
            if (fTempQName.rawname == XMLSymbols.PREFIX_XMLNS || fTempQName.rawname.startsWith("xmlns:")) {
                continue;
            }

            // simple type doesn't allow any other attributes
            if (isSimple) {
                reportSchemaError("cvc-type.3.1.1", new Object[]{element.rawname});
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
                        }
                        else
                            wildcardIDName = currDecl.fName;
                    }
                }
            }

            processOneAttribute(element, attributes, index,
                                currDecl, currUse, attrPSVI);
        } // end of for (all attributes)

        // 5.2 If wild IDs is non-empty, there must not be any attribute uses among the {attribute uses} whose {attribute declaration}'s {type definition} is or is derived from ID.
        if (!isSimple && attrGrp.fIDAttrName != null && wildcardIDName != null){
            reportSchemaError("cvc-complex-type.5.2", new Object[]{element.rawname, wildcardIDName, attrGrp.fIDAttrName});
        }

    } //processAttributes

    void processOneAttribute(QName element, XMLAttributes attributes, int index,
                             XSAttributeDecl currDecl, XSAttributeUseImpl currUse,
                             AttributePSVImpl attrPSVI) {

        String attrValue = attributes.getValue(index);
        fXSIErrorReporter.pushContext();
        
        // Attribute Locally Valid
        // For an attribute information item to be locally valid with respect to an attribute declaration all of the following must be true:
        // 1 The declaration must not be absent (see Missing Sub-components (5.3) for how this can fail to be the case).
        // 2 Its {type definition} must not be absent.
        // 3 The item's normalized value must be locally valid with respect to that {type definition} as per String Valid (3.14.4).
        // get simple type
        XSSimpleType attDV = currDecl.fType;
        
        Object actualValue = null;
        try {
            actualValue = attDV.validate(attrValue, fValidationState, fValidatedInfo);
            // store the normalized value
            if (fNormalizeData)
                attributes.setValue(index, fValidatedInfo.normalizedValue);
            if (attributes instanceof XMLAttributesImpl) {
                XMLAttributesImpl attrs = (XMLAttributesImpl)attributes;
                boolean schemaId = fValidatedInfo.memberType != null ?
                                   fValidatedInfo.memberType.isIDType() :
                                   attDV.isIDType();
                attrs.setSchemaId(index, schemaId);
            }
    
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

                if (grammar != null) {
                    fNotation = grammar.getGlobalNotationDecl(qName.localpart);
                }
            }
        }
        catch (InvalidDatatypeValueException idve) {
            reportSchemaError(idve.getKey(), idve.getArgs());
            reportSchemaError("cvc-attribute.3", new Object[]{element.rawname, fTempQName.rawname, attrValue});
        }

        // get the value constraint from use or decl
        // 4 The item's actual value must match the value of the {value constraint}, if it is present and fixed.                 // now check the value against the simpleType
        if (actualValue != null &&
            currDecl.getConstraintType() == XSConstants.VC_FIXED) {
            if (!actualValue.equals(currDecl.fDefault.actualValue)){
                reportSchemaError("cvc-attribute.4", new Object[]{element.rawname, fTempQName.rawname, attrValue});
            }
        }

        // 3.1 If there is among the {attribute uses} an attribute use with an {attribute declaration} whose {name} matches the attribute information item's [local name] and whose {target namespace} is identical to the attribute information item's [namespace name] (where an absent {target namespace} is taken to be identical to a [namespace name] with no value), then the attribute information must be valid with respect to that attribute use as per Attribute Locally Valid (Use) (3.5.4). In this case the {attribute declaration} of that attribute use is the context-determined declaration for the attribute information item with respect to Schema-Validity Assessment (Attribute) (3.2.4) and Assessment Outcome (Attribute) (3.2.5).
        if (actualValue != null &&
            currUse != null && currUse.fConstraintType == XSConstants.VC_FIXED) {
            if (!actualValue.equals(currUse.fDefault.actualValue)){
                reportSchemaError("cvc-complex-type.3.1", new Object[]{element.rawname, fTempQName.rawname, attrValue});
            }
        }

        if (fAugPSVI) {
            // PSVI: attribute declaration
            attrPSVI.fDeclaration = currDecl;
            if (currDecl != null && currDecl.fDefault != null)
                attrPSVI.fSchemaDefault = currDecl.fDefault.toString();
            // PSVI: attribute type
            attrPSVI.fTypeDecl = attDV;

            // PSVI: attribute memberType
            attrPSVI.fMemberType = fValidatedInfo.memberType;
            // PSVI: attribute normalized value
            // NOTE: we always store the normalized value, even if it's invlid,
            // because it might still be useful to the user. But when the it's
            // not valid, the normalized value is not trustable.
            attrPSVI.fNormalizedValue = fValidatedInfo.normalizedValue;

            // PSVI: validation attempted:
            attrPSVI.fValidationAttempted = AttributePSVI.VALIDATION_FULL;

            String[] errors = fXSIErrorReporter.mergeContext();
            // PSVI: error codes
            attrPSVI.fErrorCodes = errors;
            // PSVI: validity
            attrPSVI.fValidity = (errors == null) ?
                                 AttributePSVI.VALIDITY_VALID :
                                 AttributePSVI.VALIDITY_INVALID;
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
            System.out.println("==>addDefaultAttributes: " + element);
        }
        XSObjectList attrUses = attrGrp.getAttributeUses();
        int useCount = attrUses.getLength();
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
                String normalized = (defaultValue!=null)?defaultValue.toString():"";
                int attrIndex = attributes.addAttribute(attName, "CDATA", normalized);
                if (attributes instanceof XMLAttributesImpl) {
                    XMLAttributesImpl attrs = (XMLAttributesImpl)attributes;
                    boolean schemaId = defaultValue != null &&
                                       defaultValue.memberType != null ?
                                       defaultValue.memberType.isIDType() :
                                       currDecl.fType.isIDType();
                    attrs.setSchemaId(attrIndex, schemaId);
                }

                if (fAugPSVI) {
                    // PSVI: attribute is "schema" specified
                    Augmentations augs = attributes.getAugmentations(attrIndex);

                    AttributePSVImpl attrPSVI = new AttributePSVImpl();
                    augs.putItem(Constants.ATTRIBUTE_PSVI, attrPSVI);

                    attrPSVI.fDeclaration = currDecl;
                    attrPSVI.fTypeDecl = currDecl.fType;
                    attrPSVI.fMemberType = defaultValue.memberType;
                    attrPSVI.fNormalizedValue = normalized;
                    attrPSVI.fSchemaDefault = normalized;
                    attrPSVI.fValidationContext = fValidationRoot;
                    attrPSVI.fValidity = AttributePSVI.VALIDITY_VALID;
                    attrPSVI.fValidationAttempted = AttributePSVI.VALIDATION_FULL;
                    attrPSVI.fSpecified = true;
                }
            }

        } // for
    } // addDefaultAttributes

    /**
     *  If there is not text content, and there is a
     *  {value constraint} on the corresponding element decl, then return
     *  an XMLString representing the default value.
     */
    void processElementContent(QName element) {
        // 1 If the item is ?valid? with respect to an element declaration as per Element Locally Valid (Element) (?3.3.4) and the {value constraint} is present, but clause 3.2 of Element Locally Valid (Element) (?3.3.4) above is not satisfied and the item has no element or character information item [children], then schema. Furthermore, the post-schema-validation infoset has the canonical lexical representation of the {value constraint} value as the item's [schema normalized value] property.
        if (fCurrentElemDecl != null && fCurrentElemDecl.fDefault != null &&
            !fSawText && !fSubElement && !fNil) {

            String strv = fCurrentElemDecl.fDefault.stringValue();
            int bufLen = strv.length();
            if (fNormalizedStr.ch == null || fNormalizedStr.ch.length < bufLen) {
                fNormalizedStr.ch = new char[bufLen];
            }
            strv.getChars(0, bufLen, fNormalizedStr.ch, 0);
            fNormalizedStr.offset = 0;
            fNormalizedStr.length = bufLen;
            fDefaultValue = fNormalizedStr;
        }
        // fixed values are handled later, after xsi:type determined.

        fValidatedInfo.normalizedValue = null;

        // Element Locally Valid (Element)
        // 3.2.1 The element information item must have no character or element information item [children].
        if (fNil) {
            if (fSubElement || fSawText){
                reportSchemaError("cvc-elt.3.2.1", new Object[]{element.rawname, SchemaSymbols.URI_XSI+","+SchemaSymbols.XSI_NIL});
            }
        }

        this.fValidatedInfo.reset();
        
        // 5 The appropriate case among the following must be true:
        // 5.1 If the declaration has a {value constraint}, the item has neither element nor character [children] and clause 3.2 has not applied, then all of the following must be true:
        if (fCurrentElemDecl != null &&
            fCurrentElemDecl.getConstraintType() != XSConstants.VC_NONE &&
            !fSubElement && !fSawText && !fNil) {
            // 5.1.1 If the actual type definition is a local type definition then the canonical lexical representation of the {value constraint} value must be a valid default for the actual type definition as defined in Element Default Valid (Immediate) (3.3.6).
            if (fCurrentType != fCurrentElemDecl.fType) {
                //REVISIT:we should pass ValidatedInfo here.
                if (XSConstraints.ElementDefaultValidImmediate(fCurrentType, fCurrentElemDecl.fDefault.stringValue(), fState4XsiType, null) == null)
                    reportSchemaError("cvc-elt.5.1.1", new Object[]{element.rawname, fCurrentType.getName(), fCurrentElemDecl.fDefault.stringValue()});
            }
            // 5.1.2 The element information item with the canonical lexical representation of the {value constraint} value used as its normalized value must be valid with respect to the actual type definition as defined by Element Locally Valid (Type) (3.3.4).
            // REVISIT: don't use toString, but validateActualValue instead
            //          use the fState4ApplyDefault
            elementLocallyValidType(element, fCurrentElemDecl.fDefault.stringValue());
        }
        else {
            // The following method call also deal with clause 1.2.2 of the constraint
            // Validation Rule: Schema-Validity Assessment (Element)

            // 5.2 If the declaration has no {value constraint} or the item has either element or character [children] or clause 3.2 has applied, then all of the following must be true:
            // 5.2.1 The element information item must be valid with respect to the actual type definition as defined by Element Locally Valid (Type) (3.3.4).
            Object actualValue = elementLocallyValidType(element, fBuffer);
            // 5.2.2 If there is a fixed {value constraint} and clause 3.2 has not applied, all of the following must be true:
            if (fCurrentElemDecl != null &&
                fCurrentElemDecl.getConstraintType() == XSConstants.VC_FIXED &&
                !fNil) {
                String content = fBuffer.toString();
                // 5.2.2.1 The element information item must have no element information item [children].
                if (fSubElement)
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
                            !actualValue.equals(fCurrentElemDecl.fDefault.actualValue))
                            reportSchemaError("cvc-elt.5.2.2.2.2", new Object[]{element.rawname, content, fCurrentElemDecl.fDefault.stringValue()});
                    }
                }
                else if (fCurrentType.getTypeCategory() == XSTypeDecl.SIMPLE_TYPE) {
                    XSSimpleType sType = (XSSimpleType)fCurrentType;
                    if (actualValue != null &&
                        !actualValue.equals(fCurrentElemDecl.fDefault.actualValue))
                        // REVISIT: the spec didn't mention this case: fixed
                        //          value with simple type
                        reportSchemaError("cvc-elt.5.2.2.2.2", new Object[]{element.rawname, content, fCurrentElemDecl.fDefault.stringValue()});
                }
            }
        }

        if (fDefaultValue == null && fNormalizeData &&
            fDocumentHandler != null && fUnionType) {
            // for union types we need to send data because we delayed sending
            // this data when we received it in the characters() call.
            String content = fValidatedInfo.normalizedValue;
            if (content == null)
                content = fBuffer.toString();
            
            int bufLen = content.length();
            if (fNormalizedStr.ch == null || fNormalizedStr.ch.length < bufLen) {
                fNormalizedStr.ch = new char[bufLen];
            }
            content.getChars(0, bufLen, fNormalizedStr.ch, 0);
            fNormalizedStr.offset = 0;
            fNormalizedStr.length = bufLen;
            fDocumentHandler.characters(fNormalizedStr, null);
        }
    } // processElementContent

    Object elementLocallyValidType(QName element, Object textContent) {
        if (fCurrentType == null)
            return null;

        Object retValue = null;
        // Element Locally Valid (Type)
        // 3 The appropriate case among the following must be true:
        // 3.1 If the type definition is a simple type definition, then all of the following must be true:
        if (fCurrentType.getTypeCategory() == XSTypeDecl.SIMPLE_TYPE) {
            // 3.1.2 The element information item must have no element information item [children].
            if (fSubElement)
                reportSchemaError("cvc-type.3.1.2", new Object[]{element.rawname});
            // 3.1.3 If clause 3.2 of Element Locally Valid (Element) (3.3.4) did not apply, then the normalized value must be valid with respect to the type definition as defined by String Valid (3.14.4).
            if (!fNil) {
                XSSimpleType dv = (XSSimpleType)fCurrentType;
                try {
                    if (!fNormalizeData || fUnionType) {
                        fValidationState.setNormalizationRequired(true);
                    }
                    retValue = dv.validate(textContent, fValidationState, fValidatedInfo);
                }
                catch (InvalidDatatypeValueException e) {
                    reportSchemaError(e.getKey(), e.getArgs());
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

    Object elementLocallyValidComplexType(QName element, Object textContent) {
        Object actualValue = null;
        XSComplexTypeDecl ctype = (XSComplexTypeDecl)fCurrentType;

        // Element Locally Valid (Complex Type)
        // For an element information item to be locally valid with respect to a complex type definition all of the following must be true:
        // 1 {abstract} is false.
        // 2 If clause 3.2 of Element Locally Valid (Element) (3.3.4) did not apply, then the appropriate case among the following must be true:
        if (!fNil) {
            // 2.1 If the {content type} is empty, then the element information item has no character or element information item [children].
            if (ctype.fContentType == XSComplexTypeDecl.CONTENTTYPE_EMPTY &&
                (fSubElement || fSawText || fSawChildren)) {
                reportSchemaError("cvc-complex-type.2.1", new Object[]{element.rawname});
            }
            // 2.2 If the {content type} is a simple type definition, then the element information item has no element information item [children], and the normalized value of the element information item is valid with respect to that simple type definition as defined by String Valid (3.14.4).
            else if (ctype.fContentType == XSComplexTypeDecl.CONTENTTYPE_SIMPLE) {
                if (fSubElement)
                    reportSchemaError("cvc-complex-type.2.2", new Object[]{element.rawname});
                XSSimpleType dv = ctype.fXSSimpleType;
                try {
                    if (!fNormalizeData || fUnionType) {
                        fValidationState.setNormalizationRequired(true);
                    }
                    actualValue = dv.validate(textContent, fValidationState, fValidatedInfo);
                }
                catch (InvalidDatatypeValueException e) {
                    reportSchemaError(e.getKey(), e.getArgs());
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
                    reportSchemaError("cvc-complex-type.2.4.b", new Object[]{element.rawname, ((XSParticleDecl)ctype.getParticle()).toString()});
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
        public void clear() {
            fValuesCount = 0;
            fValues.clear();
            fValueTuples.removeAllElements();
        } // end clear():void

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

        public void reportError(String key, Object[] args) {
            reportSchemaError(key, args);
        } // reportError(String,Object[])

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
                    String name = fIdentityConstraint.getName();
                    reportSchemaError(code, new Object[]{name, value,element});
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

        /**
         * Values stores associated to specific identity constraints.
         * This hashtable maps IdentityConstraints and
         * the 0-based element on which their selectors first matched to
         * a corresponding ValueStore.  This should take care
         * of all cases, including where ID constraints with
         * descendant-or-self axes occur on recursively-defined
         * elements.
         */
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
            // only clone the hashtable when there are elements
            if (fGlobalIDConstraintMap.size() > 0)
                fGlobalMapStack.push(fGlobalIDConstraintMap.clone());
            else
                fGlobalMapStack.push(null);
            fGlobalIDConstraintMap.clear();
        } // startElement(void)

        // endElement():  merges contents of fGlobalIDConstraintMap with the
        // top of fGlobalMapStack into fGlobalIDConstraintMap.
        public void endElement() {
            if (fGlobalMapStack.isEmpty()) return; // must be an invalid doc!
            Hashtable oldMap = (Hashtable)fGlobalMapStack.pop();
            // return if there is no element
            if (oldMap == null) return;

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
                    }
                }
            }
        } // endElement()

        /**
         * Initializes the value stores for the specified element
         * declaration.
         */
        public void initValueStoresFor(XSElementDecl eDecl) {
            // initialize value stores for unique fields
            IdentityConstraint [] icArray = eDecl.fIDConstraints;
            int icCount = eDecl.fIDCPos;
            for (int i = 0; i < icCount; i++) {
                switch (icArray[i].getCategory()) {
                case (IdentityConstraint.IC_UNIQUE):
                    // initialize value stores for unique fields
                    UniqueOrKey unique = (UniqueOrKey)icArray[i];
                    LocalIDKey toHash = new LocalIDKey (unique, fElementDepth);
                    UniqueValueStore  uniqueValueStore = (UniqueValueStore)fIdentityConstraint2ValueStoreMap.get(toHash);
                    if (uniqueValueStore == null) {
                        uniqueValueStore = new UniqueValueStore(unique);
                        fIdentityConstraint2ValueStoreMap.put(toHash, uniqueValueStore);
                    } else {
                        uniqueValueStore.clear();
                    }
                    fValueStores.addElement(uniqueValueStore);
                    break;
                case (IdentityConstraint.IC_KEY):
                    // initialize value stores for key fields
                    UniqueOrKey key = (UniqueOrKey)icArray[i];
                    toHash = new LocalIDKey(key, fElementDepth);
                    KeyValueStore  keyValueStore = (KeyValueStore)fIdentityConstraint2ValueStoreMap.get(toHash);
                    if (keyValueStore == null) {
                        keyValueStore = new KeyValueStore(key);
                        fIdentityConstraint2ValueStoreMap.put(toHash, keyValueStore);
                    } else {
                        keyValueStore.clear();
                    }
                    fValueStores.addElement(keyValueStore);
                    break;
                case (IdentityConstraint.IC_KEYREF):
                    // initialize value stores for keyRef fields
                    KeyRef keyRef = (KeyRef)icArray[i];
                    toHash = new LocalIDKey(keyRef, fElementDepth);
                    KeyRefValueStore  keyRefValueStore = (KeyRefValueStore)fIdentityConstraint2ValueStoreMap.get(toHash);
                    if (keyRefValueStore == null) {
                        keyRefValueStore = new KeyRefValueStore(keyRef, null);
                        fIdentityConstraint2ValueStoreMap.put(toHash, keyRefValueStore);
                    } else {
                        keyRefValueStore.clear();
                    }
                    fValueStores.addElement(keyRefValueStore);
                    break;
                }
            }
        } // initValueStoresFor(XSElementDecl)

        /** Returns the value store associated to the specified IdentityConstraint. */
        public ValueStoreBase getValueStoreFor(IdentityConstraint id, int initialDepth) {
            ValueStoreBase vb = (ValueStoreBase)fIdentityConstraint2ValueStoreMap.get(new LocalIDKey(id, initialDepth));
            // vb should *never* be null!
            return vb;
        } // getValueStoreFor(IdentityConstraint, int):ValueStoreBase

        /** Returns the global value store associated to the specified IdentityConstraint. */
        public ValueStoreBase getGlobalValueStoreFor(IdentityConstraint id) {
            return(ValueStoreBase)fGlobalIDConstraintMap.get(id);
        } // getValueStoreFor(IdentityConstraint):ValueStoreBase
        // This method takes the contents of the (local) ValueStore
        // associated with id and moves them into the global
        // hashtable, if id is a <unique> or a <key>.
        // If it's a <keyRef>, then we leave it for later.
        public void transplant(IdentityConstraint id, int initialDepth) {
            ValueStoreBase newVals = (ValueStoreBase)fIdentityConstraint2ValueStoreMap.get(new LocalIDKey(id, initialDepth));
            if (id.getCategory() == IdentityConstraint.IC_KEYREF) return;
            ValueStoreBase currVals = (ValueStoreBase)fGlobalIDConstraintMap.get(id);
            if (currVals != null) {
                currVals.append(newVals);
                fGlobalIDConstraintMap.put(id, currVals);
            }
            else
                fGlobalIDConstraintMap.put(id, newVals);

        } // transplant(id)

        /** Check identity constraints. */
        public void endDocument() {

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

    // the purpose of this class is to enable IdentityConstraint,int
    // pairs to be used easily as keys in Hashtables.
    protected class LocalIDKey {
        private IdentityConstraint fId;
        private int fDepth;

        public LocalIDKey (IdentityConstraint id, int depth) {
            fId = id;
            fDepth = depth;
        } // init(IdentityConstraint, int)

        // object method
        public int hashCode() {
            return fId.hashCode()+fDepth;
        }

        public boolean equals(Object localIDKey) {
            if(localIDKey instanceof LocalIDKey) {
                LocalIDKey lIDKey = (LocalIDKey)localIDKey;
                return (lIDKey.fId == fId && lIDKey.fDepth == fDepth);
            }
            return false;
        }
    } // class LocalIDKey

} // class SchemaValidator