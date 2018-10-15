fDocumentHandler.startElement(element, attributes, augs);

/*
 * Copyright 2001-2004 The Apache Software Foundation.
 * 
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * 
 *      http://www.apache.org/licenses/LICENSE-2.0
 * 
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package org.apache.xerces.xinclude;

import java.io.CharConversionException;
import java.io.IOException;
import java.util.Enumeration;
import java.util.Stack;
import java.util.StringTokenizer;
import java.util.Vector;

import org.apache.xerces.impl.Constants;
import org.apache.xerces.impl.XMLEntityManager;
import org.apache.xerces.impl.XMLErrorReporter;
import org.apache.xerces.impl.io.MalformedByteSequenceException;
import org.apache.xerces.impl.msg.XMLMessageFormatter;
import org.apache.xerces.util.AugmentationsImpl;
import org.apache.xerces.util.IntStack;
import org.apache.xerces.util.ParserConfigurationSettings;
import org.apache.xerces.util.SecurityManager;
import org.apache.xerces.util.URI;
import org.apache.xerces.util.XMLAttributesImpl;
import org.apache.xerces.util.XMLResourceIdentifierImpl;
import org.apache.xerces.util.XMLSymbols;
import org.apache.xerces.util.URI.MalformedURIException;
import org.apache.xerces.xni.Augmentations;
import org.apache.xerces.xni.NamespaceContext;
import org.apache.xerces.xni.QName;
import org.apache.xerces.xni.XMLAttributes;
import org.apache.xerces.xni.XMLDTDHandler;
import org.apache.xerces.xni.XMLDocumentHandler;
import org.apache.xerces.xni.XMLLocator;
import org.apache.xerces.xni.XMLResourceIdentifier;
import org.apache.xerces.xni.XMLString;
import org.apache.xerces.xni.XNIException;
import org.apache.xerces.xni.parser.XMLComponent;
import org.apache.xerces.xni.parser.XMLComponentManager;
import org.apache.xerces.xni.parser.XMLConfigurationException;
import org.apache.xerces.xni.parser.XMLDTDFilter;
import org.apache.xerces.xni.parser.XMLDTDSource;
import org.apache.xerces.xni.parser.XMLDocumentFilter;
import org.apache.xerces.xni.parser.XMLDocumentSource;
import org.apache.xerces.xni.parser.XMLEntityResolver;
import org.apache.xerces.xni.parser.XMLInputSource;
import org.apache.xerces.xni.parser.XMLParserConfiguration;

/**
 * <p>
 * This is a pipeline component which performs XInclude handling, according to the
 * W3C specification for XML Inclusions.
 * </p>
 * <p>
 * This component analyzes each event in the pipeline, looking for &lt;include&gt;
 * elements. An &lt;include&gt; element is one which has a namespace of
 * <code>http://www.w3.org/2001/XInclude</code> and a localname of <code>include</code>.
 * When it finds an &lt;include&gt; element, it attempts to include the file specified
 * in the <code>href</code> attribute of the element.  If inclusion succeeds, all
 * children of the &lt;include&gt; element are ignored (with the exception of
 * checking for invalid children as outlined in the specification).  If the inclusion
 * fails, the &lt;fallback&gt; child of the &lt;include&gt; element is processed.
 * </p>
 * <p>
 * See the <a href="http://www.w3.org/TR/xinclude/">XInclude specification</a> for
 * more information on how XInclude is to be used.
 * </p>
 * <p>
 * This component requires the following features and properties from the
 * component manager that uses it:
 * <ul>
 *  <li>http://xml.org/sax/features/allow-dtd-events-after-endDTD</li>
 *  <li>http://apache.org/xml/properties/internal/error-reporter</li>
 *  <li>http://apache.org/xml/properties/internal/entity-resolver</li>
 * </ul>
 * Optional property:
 * <ul>
 *  <li>http://apache.org/xml/properties/input-buffer-size</li>
 * </ul>
 * 
 * Furthermore, the <code>NamespaceContext</code> used in the pipeline is required
 * to be an instance of <code>XIncludeNamespaceSupport</code>.
 * </p>
 * <p>
 * Currently, this implementation has only partial support for the XInclude specification.
 * Specifically, it is missing support for XPointer document fragments.  Thus, only whole
 * documents can be included using this component in the pipeline.
 * </p>
 *
 * @author Peter McCracken, IBM
 * @author Michael Glavassevich, IBM
 *
 * @version $Id$
 *
 * @see XIncludeNamespaceSupport
 */
public class XIncludeHandler
    implements XMLComponent, XMLDocumentFilter, XMLDTDFilter {

    public final static String XINCLUDE_DEFAULT_CONFIGURATION =
        "org.apache.xerces.parsers.XIncludeParserConfiguration";
    public final static String HTTP_ACCEPT = "Accept";
    public final static String HTTP_ACCEPT_LANGUAGE = "Accept-Language";
    public final static String XPOINTER = "xpointer";

    public final static String XINCLUDE_NS_URI =
        "http://www.w3.org/2001/XInclude".intern();
    public final static String XINCLUDE_INCLUDE = "include".intern();
    public final static String XINCLUDE_FALLBACK = "fallback".intern();

    public final static String XINCLUDE_PARSE_XML = "xml".intern();
    public final static String XINCLUDE_PARSE_TEXT = "text".intern();

    public final static String XINCLUDE_ATTR_HREF = "href".intern();
    public final static String XINCLUDE_ATTR_PARSE = "parse".intern();
    public final static String XINCLUDE_ATTR_ENCODING = "encoding".intern();
    public final static String XINCLUDE_ATTR_ACCEPT = "accept".intern();
    public final static String XINCLUDE_ATTR_ACCEPT_LANGUAGE = "accept-language".intern();

    // Top Level Information Items have [included] property in infoset
    public final static String XINCLUDE_INCLUDED = "[included]".intern();

    /** The identifier for the Augmentation that contains the current base URI */
    public final static String CURRENT_BASE_URI = "currentBaseURI";

    // used for adding [base URI] attributes
    public final static String XINCLUDE_BASE = "base";
    public final static QName XML_BASE_QNAME =
        new QName(
            XMLSymbols.PREFIX_XML,
            XINCLUDE_BASE,
            XMLSymbols.PREFIX_XML + ":" + XINCLUDE_BASE,
            NamespaceContext.XML_URI);
    
    // used for adding [language] attributes
    public final static String XINCLUDE_LANG = "lang";
    public final static QName XML_LANG_QNAME = 
        new QName(
                XMLSymbols.PREFIX_XML,
                XINCLUDE_LANG,
                XMLSymbols.PREFIX_XML + ":" + XINCLUDE_LANG,
                NamespaceContext.XML_URI);

    public final static QName NEW_NS_ATTR_QNAME =
        new QName(
            XMLSymbols.PREFIX_XMLNS,
            "",
            XMLSymbols.PREFIX_XMLNS + ":",
            NamespaceContext.XMLNS_URI);

    // Processing States
    private final static int STATE_NORMAL_PROCESSING = 1;
    // we go into this state after a successful include (thus we ignore the children
    // of the include) or after a fallback
    private final static int STATE_IGNORE = 2;
    // we go into this state after a failed include.  If we don't encounter a fallback
    // before we reach the end include tag, it's a fatal error
    private final static int STATE_EXPECT_FALLBACK = 3;

    // recognized features and properties
    
    /** Feature identifier: validation. */
    protected static final String VALIDATION =
        Constants.SAX_FEATURE_PREFIX + Constants.VALIDATION_FEATURE;
    
    /** Feature identifier: schema validation. */
    protected static final String SCHEMA_VALIDATION =
        Constants.XERCES_FEATURE_PREFIX + Constants.SCHEMA_VALIDATION_FEATURE;
    
    /** Feature identifier: dynamic validation. */
    protected static final String DYNAMIC_VALIDATION = 
        Constants.XERCES_FEATURE_PREFIX + Constants.DYNAMIC_VALIDATION_FEATURE;

    /** Feature identifier: allow notation and unparsed entity events to be sent out of order. */
    protected static final String ALLOW_UE_AND_NOTATION_EVENTS =
        Constants.SAX_FEATURE_PREFIX
            + Constants.ALLOW_DTD_EVENTS_AFTER_ENDDTD_FEATURE;

    /** Property identifier: error reporter. */
    protected static final String ERROR_REPORTER =
        Constants.XERCES_PROPERTY_PREFIX + Constants.ERROR_REPORTER_PROPERTY;

    /** Property identifier: entity resolver. */
    protected static final String ENTITY_RESOLVER =
        Constants.XERCES_PROPERTY_PREFIX + Constants.ENTITY_RESOLVER_PROPERTY;

    /** property identifier: security manager. */
    protected static final String SECURITY_MANAGER =
        Constants.XERCES_PROPERTY_PREFIX + Constants.SECURITY_MANAGER_PROPERTY;
    
    /** property identifier: buffer size. */
    public static final String BUFFER_SIZE =
        Constants.XERCES_PROPERTY_PREFIX + Constants.BUFFER_SIZE_PROPERTY;

    /** Recognized features. */
    private static final String[] RECOGNIZED_FEATURES =
        { ALLOW_UE_AND_NOTATION_EVENTS };

    /** Feature defaults. */
    private static final Boolean[] FEATURE_DEFAULTS = { Boolean.TRUE };

    /** Recognized properties. */
    private static final String[] RECOGNIZED_PROPERTIES =
        { ERROR_REPORTER, ENTITY_RESOLVER, SECURITY_MANAGER, BUFFER_SIZE };

    /** Property defaults. */
    private static final Object[] PROPERTY_DEFAULTS = { null, null, null, new Integer(XMLEntityManager.DEFAULT_BUFFER_SIZE) };

    // instance variables

    // for XMLDocumentFilter
    protected XMLDocumentHandler fDocumentHandler;
    protected XMLDocumentSource fDocumentSource;

    // for XMLDTDFilter
    protected XMLDTDHandler fDTDHandler;
    protected XMLDTDSource fDTDSource;

    // for XIncludeHandler
    protected XIncludeHandler fParentXIncludeHandler;
    
    // for buffer size in XIncludeTextReader
    protected int fBufferSize = XMLEntityManager.DEFAULT_BUFFER_SIZE;

    // It "feels wrong" to store this value here.  However,
    // calculating it can be time consuming, so we cache it.
    // It's never going to change in the lifetime of this XIncludeHandler
    protected String fParentRelativeURI;

    // we cache the child parser configuration, so we don't have to re-create
    // the objects when the parser is re-used
    protected XMLParserConfiguration fChildConfig;

    protected XMLLocator fDocLocation;
    protected XIncludeNamespaceSupport fNamespaceContext;
    protected XMLErrorReporter fErrorReporter;
    protected XMLEntityResolver fEntityResolver;
    protected SecurityManager fSecurityManager;
    
    // these are needed for text include processing
    protected XIncludeTextReader fXInclude10TextReader;
    protected XIncludeTextReader fXInclude11TextReader;

    // these are needed for XML Base processing
    protected XMLResourceIdentifier fCurrentBaseURI;
    protected IntStack fBaseURIScope;
    protected Stack fBaseURI;
    protected Stack fLiteralSystemID;
    protected Stack fExpandedSystemID;
    
    // these are needed for Language Fixup
    protected IntStack fLanguageScope;
    protected Stack fLanguageStack;
    protected String fCurrentLanguage;

    // used for passing features on to child XIncludeHandler objects
    protected ParserConfigurationSettings fSettings;

    // The current element depth.  We start at depth 0 (before we've reached any elements)
    // The first element is at depth 1.
    private int fDepth;

    // this value must be at least 1
    private static final int INITIAL_SIZE = 8;

    // Used to ensure that fallbacks are always children of include elements,
    // and that include elements are never children of other include elements.
    // An index contains true if the ancestor of the current element which resides
    // at that depth was an include element.
    private boolean[] fSawInclude = new boolean[INITIAL_SIZE];

    // Ensures that only one fallback element can be at a single depth.
    // An index contains true if we have seen any fallback elements at that depth,
    // and it is only reset to false when the end tag of the parent is encountered.
    private boolean[] fSawFallback = new boolean[INITIAL_SIZE];

    // The state of the processor at each given depth.
    private int[] fState = new int[INITIAL_SIZE];

    // buffering the necessary DTD events
    private Vector fNotations;
    private Vector fUnparsedEntities;

    // for SAX compatibility.
    // Has the value of the ALLOW_UE_AND_NOTATION_EVENTS feature
    private boolean fSendUEAndNotationEvents;

    // track the version of the document being parsed
    private boolean fIsXML11;

    // track whether a DTD is being parsed
    private boolean fInDTD;

    // Constructors

    public XIncludeHandler() {
        fDepth = 0;

        fSawFallback[fDepth] = false;
        fSawInclude[fDepth] = false;
        fState[fDepth] = STATE_NORMAL_PROCESSING;
        fNotations = new Vector();
        fUnparsedEntities = new Vector();

        fBaseURIScope = new IntStack();
        fBaseURI = new Stack();
        fLiteralSystemID = new Stack();
        fExpandedSystemID = new Stack();
        fCurrentBaseURI = new XMLResourceIdentifierImpl();
        
        fLanguageScope = new IntStack();
        fLanguageStack = new Stack();
        fCurrentLanguage = null;
    }

    // XMLComponent methods

    public void reset(XMLComponentManager componentManager)
        throws XNIException {
        fNamespaceContext = null;
        fDepth = 0;
        fNotations = new Vector();
        fUnparsedEntities = new Vector();
        fParentRelativeURI = null;
        fIsXML11 = false;
        fInDTD = false;

        fBaseURIScope.clear();
        fBaseURI.clear();
        fLiteralSystemID.clear();
        fExpandedSystemID.clear();

        // REVISIT: Find a better method for maintaining
        // the state of the XInclude processor. These arrays
        // can potentially grow quite large. Cleaning them
        // out on reset may be very time consuming. -- mrglavas
        //
        // clear the previous settings from the arrays
        for (int i = 0; i < fState.length; ++i) {
            fState[i] = STATE_NORMAL_PROCESSING;
        }
        for (int i = 0; i < fSawFallback.length; ++i) {
            fSawFallback[i] = false;
        }
        for (int i = 0; i < fSawInclude.length; ++i) {
            fSawInclude[i] = false;
        }

        try {
            fSendUEAndNotationEvents =
                componentManager.getFeature(ALLOW_UE_AND_NOTATION_EVENTS);
            if (fChildConfig != null) {
                fChildConfig.setFeature(
                    ALLOW_UE_AND_NOTATION_EVENTS,
                    fSendUEAndNotationEvents);
            }
        }
        catch (XMLConfigurationException e) {
        }

        // Get error reporter.
        try {
            XMLErrorReporter value =
                (XMLErrorReporter)componentManager.getProperty(ERROR_REPORTER);
            if (value != null) {
                setErrorReporter(value);
                if (fChildConfig != null) {
                    fChildConfig.setProperty(ERROR_REPORTER, value);
                }
            }
        }
        catch (XMLConfigurationException e) {
            fErrorReporter = null;
        }

        // Get entity resolver.
        try {
            XMLEntityResolver value =
                (XMLEntityResolver)componentManager.getProperty(
                    ENTITY_RESOLVER);

            if (value != null) {
                fEntityResolver = value;
                if (fChildConfig != null) {
                    fChildConfig.setProperty(ENTITY_RESOLVER, value);
                }
            }
        }
        catch (XMLConfigurationException e) {
            fEntityResolver = null;
        }

        // Get security manager.
        try {
            SecurityManager value =
                (SecurityManager)componentManager.getProperty(
                    SECURITY_MANAGER);

            if (value != null) {
                fSecurityManager = value;
                if (fChildConfig != null) {
                    fChildConfig.setProperty(SECURITY_MANAGER, value);
                }
            }
        }
        catch (XMLConfigurationException e) {
            fSecurityManager = null;
        }
        
        // Get buffer size.
        try {
            Integer value =
                (Integer)componentManager.getProperty(
                    BUFFER_SIZE);

            if (value != null && value.intValue() > 0) {
                fBufferSize = value.intValue();
            }
            else {
            	fBufferSize = ((Integer)getPropertyDefault(BUFFER_SIZE)).intValue();
            }
        }
        catch (XMLConfigurationException e) {
        	fBufferSize = ((Integer)getPropertyDefault(BUFFER_SIZE)).intValue();
        }
        
        // Reset XML 1.0 text reader.
        if (fXInclude10TextReader != null) {
        	fXInclude10TextReader.setBufferSize(fBufferSize);
        }
        // Reset XML 1.1 text reader.
        if (fXInclude11TextReader != null) {
            fXInclude11TextReader.setBufferSize(fBufferSize);   
        }

        fSettings = new ParserConfigurationSettings();
        copyFeatures(componentManager, fSettings);
        
        // we don't want a schema validator on the new pipeline,
        // so if it was enabled, we set the feature to false as 
        // well as other validation features.
        try {
            if (componentManager.getFeature(SCHEMA_VALIDATION)) {
                fSettings.setFeature(SCHEMA_VALIDATION, false);
                fSettings.setFeature(DYNAMIC_VALIDATION, false);
                fSettings.setFeature(VALIDATION, false);
            }
        }
        catch (XMLConfigurationException e) {}
        
        // Don't reset fChildConfig -- we don't want it to share the same components.
        // It will be reset when it is actually used to parse something.
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
        if (featureId.equals(ALLOW_UE_AND_NOTATION_EVENTS)) {
            fSendUEAndNotationEvents = state;
        }
        if (fSettings != null) {
            fSettings.setFeature(featureId, state);
        }
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
        if (propertyId.equals(ERROR_REPORTER)) {
            setErrorReporter((XMLErrorReporter)value);
            if (fChildConfig != null) {
                fChildConfig.setProperty(propertyId, value);
            }
            return;
        }
        if (propertyId.equals(ENTITY_RESOLVER)) {
            fEntityResolver = (XMLEntityResolver)value;
            if (fChildConfig != null) {
                fChildConfig.setProperty(propertyId, value);
            }
            return;
        }
        if (propertyId.equals(SECURITY_MANAGER)) {
            fSecurityManager = (SecurityManager)value;
            if (fChildConfig != null) {
                fChildConfig.setProperty(propertyId, value);
            }
            return;
        }
        if (propertyId.equals(BUFFER_SIZE)) {
            Integer bufferSize = (Integer) value;
            if (bufferSize != null && bufferSize.intValue() > 0) {
                fBufferSize = bufferSize.intValue();
                // Reset XML 1.0 text reader.
                if (fXInclude10TextReader != null) {
                    fXInclude10TextReader.setBufferSize(fBufferSize);
                }
                // Reset XML 1.1 text reader.
                if (fXInclude11TextReader != null) {
                    fXInclude11TextReader.setBufferSize(fBufferSize);
                }
            }
            return;
        }

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

    public void setDocumentHandler(XMLDocumentHandler handler) {
        fDocumentHandler = handler;
    }

    public XMLDocumentHandler getDocumentHandler() {
        return fDocumentHandler;
    }

    // XMLDocumentHandler methods

    /**
     * Event sent at the start of the document.
     *
     * A fatal error will occur here, if it is detected that this document has been processed
     * before.
     *
     * This event is only passed on to the document handler if this is the root document.
     */
    public void startDocument(
        XMLLocator locator,
        String encoding,
        NamespaceContext namespaceContext,
        Augmentations augs)
        throws XNIException {

        // we do this to ensure that the proper location is reported in errors
        // otherwise, the locator from the root document would always be used
        fErrorReporter.setDocumentLocator(locator);

        if (!isRootDocument()
            && fParentXIncludeHandler.searchForRecursiveIncludes(locator)) {
            reportFatalError(
                "RecursiveInclude",
                new Object[] { locator.getExpandedSystemId()});
        }

        if (!(namespaceContext instanceof XIncludeNamespaceSupport)) {
            reportFatalError("IncompatibleNamespaceContext");
        }
        fNamespaceContext = (XIncludeNamespaceSupport)namespaceContext;
        fDocLocation = locator;

        // initialize the current base URI
        fCurrentBaseURI.setBaseSystemId(locator.getBaseSystemId());
        fCurrentBaseURI.setExpandedSystemId(locator.getExpandedSystemId());
        fCurrentBaseURI.setLiteralSystemId(locator.getLiteralSystemId());
        saveBaseURI();
        if (augs == null) {
            augs = new AugmentationsImpl();
        }
        augs.putItem(CURRENT_BASE_URI, fCurrentBaseURI);
        
        // initialize the current language
        fCurrentLanguage = XMLSymbols.EMPTY_STRING;
        saveLanguage(fCurrentLanguage);

        if (isRootDocument() && fDocumentHandler != null) {
            fDocumentHandler.startDocument(
                locator,
                encoding,
                namespaceContext,
                augs);
        }
    }

    public void xmlDecl(
        String version,
        String encoding,
        String standalone,
        Augmentations augs)
        throws XNIException {
        fIsXML11 = "1.1".equals(version);
        if (isRootDocument() && fDocumentHandler != null) {
            fDocumentHandler.xmlDecl(version, encoding, standalone, augs);
        }
    }

    public void doctypeDecl(
        String rootElement,
        String publicId,
        String systemId,
        Augmentations augs)
        throws XNIException {
        if (isRootDocument() && fDocumentHandler != null) {
            fDocumentHandler.doctypeDecl(rootElement, publicId, systemId, augs);
        }
    }

    public void comment(XMLString text, Augmentations augs)
        throws XNIException {
        if (!fInDTD) {
            if (fDocumentHandler != null
                && getState() == STATE_NORMAL_PROCESSING) {
                fDepth++;
                augs = modifyAugmentations(augs);
                fDocumentHandler.comment(text, augs);
                fDepth--;
            }
        }
        else if (fDTDHandler != null) {
            fDTDHandler.comment(text, augs);
        }
    }

    public void processingInstruction(
        String target,
        XMLString data,
        Augmentations augs)
        throws XNIException {
        if (!fInDTD) {
            if (fDocumentHandler != null
                && getState() == STATE_NORMAL_PROCESSING) {
                // we need to change the depth like this so that modifyAugmentations() works
                fDepth++;
                augs = modifyAugmentations(augs);
                fDocumentHandler.processingInstruction(target, data, augs);
                fDepth--;
            }
        }
        else if (fDTDHandler != null) {
            fDTDHandler.processingInstruction(target, data, augs);
        }
    }

    public void startElement(
        QName element,
        XMLAttributes attributes,
        Augmentations augs)
        throws XNIException {
        fDepth++;
        setState(getState(fDepth - 1));

        // we process the xml:base and xml:lang attributes regardless
        // of what type of element it is.
        processXMLBaseAttributes(attributes);
        processXMLLangAttributes(attributes);

        if (isIncludeElement(element)) {
            boolean success = this.handleIncludeElement(attributes);
            if (success) {
                setState(STATE_IGNORE);
            }
            else {
                setState(STATE_EXPECT_FALLBACK);
            }
        }
        else if (isFallbackElement(element)) {
            this.handleFallbackElement();
        }
        else if (hasXIncludeNamespace(element)) {
            if (getSawInclude(fDepth - 1)) {
                reportFatalError(
                    "IncludeChild",
                    new Object[] { element.rawname });
            }
            if (getSawFallback(fDepth - 1)) {
                reportFatalError(
                    "FallbackChild",
                    new Object[] { element.rawname });
            }
            if (fDocumentHandler != null
                    && getState() == STATE_NORMAL_PROCESSING) {
                augs = modifyAugmentations(augs);
                attributes = processAttributes(attributes);
                fDocumentHandler.emptyElement(element, attributes, augs);
            }
        }
        else if (
            fDocumentHandler != null
                && getState() == STATE_NORMAL_PROCESSING) {
            augs = modifyAugmentations(augs);
            attributes = processAttributes(attributes);
            fDocumentHandler.startElement(element, attributes, augs);
        }
    }

    public void emptyElement(
        QName element,
        XMLAttributes attributes,
        Augmentations augs)
        throws XNIException {
        fDepth++;
        setState(getState(fDepth - 1));

        // we process the xml:base and xml:lang attributes regardless
        // of what type of element it is.
        processXMLBaseAttributes(attributes);
        processXMLLangAttributes(attributes);

        if (isIncludeElement(element)) {
            boolean success = this.handleIncludeElement(attributes);
            if (success) {
                setState(STATE_IGNORE);
            }
            else {
                reportFatalError("NoFallback");
            }
        }
        else if (isFallbackElement(element)) {
            this.handleFallbackElement();
        }
        else if (hasXIncludeNamespace(element)) {
            if (getSawInclude(fDepth - 1)) {
                reportFatalError(
                    "IncludeChild",
                    new Object[] { element.rawname });
            }
            if (getSawFallback(fDepth - 1)) {
                reportFatalError(
                    "FallbackChild",
                    new Object[] { element.rawname });
            }
            if (fDocumentHandler != null
                    && getState() == STATE_NORMAL_PROCESSING) {
                augs = modifyAugmentations(augs);
                attributes = processAttributes(attributes);
                fDocumentHandler.emptyElement(element, attributes, augs);
            }
        }
        else if (
            fDocumentHandler != null
                && getState() == STATE_NORMAL_PROCESSING) {
            augs = modifyAugmentations(augs);
            attributes = processAttributes(attributes);
            fDocumentHandler.emptyElement(element, attributes, augs);
        }
        // reset the out of scope stack elements
        setSawFallback(fDepth + 1, false);
        setSawInclude(fDepth + 1, false);

        // check if an xml:base has gone out of scope
        if (fBaseURIScope.size() > 0 && fDepth == fBaseURIScope.peek()) {
            // pop the values from the stack
            restoreBaseURI();
        }
        fDepth--;
    }

    public void endElement(QName element, Augmentations augs)
        throws XNIException {

        if (isIncludeElement(element)) {
            // if we're ending an include element, and we were expecting a fallback
            // we check to see if the children of this include element contained a fallback
            if (getState() == STATE_EXPECT_FALLBACK
                && !getSawFallback(fDepth + 1)) {
                reportFatalError("NoFallback");
            }
        }
        if (isFallbackElement(element)) {
            // the state would have been set to normal processing if we were expecting the fallback element
            // now that we're done processing it, we should ignore all the other children of the include element
            if (getState() == STATE_NORMAL_PROCESSING) {
                setState(STATE_IGNORE);
            }
        }
        else if (
            fDocumentHandler != null
                && getState() == STATE_NORMAL_PROCESSING) {
            fDocumentHandler.endElement(element, augs);
        }

        // reset the out of scope stack elements
        setSawFallback(fDepth + 1, false);
        setSawInclude(fDepth + 1, false);

        // check if an xml:base has gone out of scope
        if (fBaseURIScope.size() > 0 && fDepth == fBaseURIScope.peek()) {
            // pop the values from the stack
            restoreBaseURI();
        }
        
        // check if an xml:lang has gone out of scope
        if (fLanguageScope.size() > 0 && fDepth == fLanguageScope.peek()) {
            // pop the language from the stack
            fCurrentLanguage = restoreLanguage();
        }
        
        fDepth--;
    }

    public void startGeneralEntity(
        String name,
        XMLResourceIdentifier resId,
        String encoding,
        Augmentations augs)
        throws XNIException {
        if (fDocumentHandler != null
            && getState() == STATE_NORMAL_PROCESSING) {
            fDocumentHandler.startGeneralEntity(name, resId, encoding, augs);
        }
    }

    public void textDecl(String version, String encoding, Augmentations augs)
        throws XNIException {
        if (fDocumentHandler != null
            && getState() == STATE_NORMAL_PROCESSING) {
            fDocumentHandler.textDecl(version, encoding, augs);
        }
    }

    public void endGeneralEntity(String name, Augmentations augs)
        throws XNIException {
        if (fDocumentHandler != null
            && getState() == STATE_NORMAL_PROCESSING) {
            fDocumentHandler.endGeneralEntity(name, augs);
        }
    }

    public void characters(XMLString text, Augmentations augs)
        throws XNIException {
        if (fDocumentHandler != null
            && getState() == STATE_NORMAL_PROCESSING) {
            // we need to change the depth like this so that modifyAugmentations() works
            fDepth++;
            augs = modifyAugmentations(augs);
            fDocumentHandler.characters(text, augs);
            fDepth--;
        }
    }

    public void ignorableWhitespace(XMLString text, Augmentations augs)
        throws XNIException {
        if (fDocumentHandler != null
            && getState() == STATE_NORMAL_PROCESSING) {
            fDocumentHandler.ignorableWhitespace(text, augs);
        }
    }

    public void startCDATA(Augmentations augs) throws XNIException {
        if (fDocumentHandler != null
            && getState() == STATE_NORMAL_PROCESSING) {
            fDocumentHandler.startCDATA(augs);
        }
    }

    public void endCDATA(Augmentations augs) throws XNIException {
        if (fDocumentHandler != null
            && getState() == STATE_NORMAL_PROCESSING) {
            fDocumentHandler.endCDATA(augs);
        }
    }

    public void endDocument(Augmentations augs) throws XNIException {
        if (isRootDocument() && fDocumentHandler != null) {
            fDocumentHandler.endDocument(augs);
        }
    }

    public void setDocumentSource(XMLDocumentSource source) {
        fDocumentSource = source;
    }

    public XMLDocumentSource getDocumentSource() {
        return fDocumentSource;
    }

    // DTDHandler methods
    // We are only interested in the notation and unparsed entity declarations,
    // the rest we just pass on

    /* (non-Javadoc)
     * @see org.apache.xerces.xni.XMLDTDHandler#attributeDecl(java.lang.String, java.lang.String, java.lang.String, java.lang.String[], java.lang.String, org.apache.xerces.xni.XMLString, org.apache.xerces.xni.XMLString, org.apache.xerces.xni.Augmentations)
     */
    public void attributeDecl(
        String elementName,
        String attributeName,
        String type,
        String[] enumeration,
        String defaultType,
        XMLString defaultValue,
        XMLString nonNormalizedDefaultValue,
        Augmentations augmentations)
        throws XNIException {
        if (fDTDHandler != null) {
            fDTDHandler.attributeDecl(
                elementName,
                attributeName,
                type,
                enumeration,
                defaultType,
                defaultValue,
                nonNormalizedDefaultValue,
                augmentations);
        }
    }

    /* (non-Javadoc)
     * @see org.apache.xerces.xni.XMLDTDHandler#elementDecl(java.lang.String, java.lang.String, org.apache.xerces.xni.Augmentations)
     */
    public void elementDecl(
        String name,
        String contentModel,
        Augmentations augmentations)
        throws XNIException {
        if (fDTDHandler != null) {
            fDTDHandler.elementDecl(name, contentModel, augmentations);
        }
    }

    /* (non-Javadoc)
     * @see org.apache.xerces.xni.XMLDTDHandler#endAttlist(org.apache.xerces.xni.Augmentations)
     */
    public void endAttlist(Augmentations augmentations) throws XNIException {
        if (fDTDHandler != null) {
            fDTDHandler.endAttlist(augmentations);
        }
    }

    /* (non-Javadoc)
     * @see org.apache.xerces.xni.XMLDTDHandler#endConditional(org.apache.xerces.xni.Augmentations)
     */
    public void endConditional(Augmentations augmentations)
        throws XNIException {
        if (fDTDHandler != null) {
            fDTDHandler.endConditional(augmentations);
        }
    }

    /* (non-Javadoc)
     * @see org.apache.xerces.xni.XMLDTDHandler#endDTD(org.apache.xerces.xni.Augmentations)
     */
    public void endDTD(Augmentations augmentations) throws XNIException {
        if (fDTDHandler != null) {
            fDTDHandler.endDTD(augmentations);
        }
        fInDTD = false;
    }

    /* (non-Javadoc)
     * @see org.apache.xerces.xni.XMLDTDHandler#endExternalSubset(org.apache.xerces.xni.Augmentations)
     */
    public void endExternalSubset(Augmentations augmentations)
        throws XNIException {
        if (fDTDHandler != null) {
            fDTDHandler.endExternalSubset(augmentations);
        }
    }

    /* (non-Javadoc)
     * @see org.apache.xerces.xni.XMLDTDHandler#endParameterEntity(java.lang.String, org.apache.xerces.xni.Augmentations)
     */
    public void endParameterEntity(String name, Augmentations augmentations)
        throws XNIException {
        if (fDTDHandler != null) {
            fDTDHandler.endParameterEntity(name, augmentations);
        }
    }

    /* (non-Javadoc)
     * @see org.apache.xerces.xni.XMLDTDHandler#externalEntityDecl(java.lang.String, org.apache.xerces.xni.XMLResourceIdentifier, org.apache.xerces.xni.Augmentations)
     */
    public void externalEntityDecl(
        String name,
        XMLResourceIdentifier identifier,
        Augmentations augmentations)
        throws XNIException {
        if (fDTDHandler != null) {
            fDTDHandler.externalEntityDecl(name, identifier, augmentations);
        }
    }

    /* (non-Javadoc)
     * @see org.apache.xerces.xni.XMLDTDHandler#getDTDSource()
     */
    public XMLDTDSource getDTDSource() {
        return fDTDSource;
    }

    /* (non-Javadoc)
     * @see org.apache.xerces.xni.XMLDTDHandler#ignoredCharacters(org.apache.xerces.xni.XMLString, org.apache.xerces.xni.Augmentations)
     */
    public void ignoredCharacters(XMLString text, Augmentations augmentations)
        throws XNIException {
        if (fDTDHandler != null) {
            fDTDHandler.ignoredCharacters(text, augmentations);
        }
    }

    /* (non-Javadoc)
     * @see org.apache.xerces.xni.XMLDTDHandler#internalEntityDecl(java.lang.String, org.apache.xerces.xni.XMLString, org.apache.xerces.xni.XMLString, org.apache.xerces.xni.Augmentations)
     */
    public void internalEntityDecl(
        String name,
        XMLString text,
        XMLString nonNormalizedText,
        Augmentations augmentations)
        throws XNIException {
        if (fDTDHandler != null) {
            fDTDHandler.internalEntityDecl(
                name,
                text,
                nonNormalizedText,
                augmentations);
        }
    }

    /* (non-Javadoc)
     * @see org.apache.xerces.xni.XMLDTDHandler#notationDecl(java.lang.String, org.apache.xerces.xni.XMLResourceIdentifier, org.apache.xerces.xni.Augmentations)
     */
    public void notationDecl(
        String name,
        XMLResourceIdentifier identifier,
        Augmentations augmentations)
        throws XNIException {
        this.addNotation(name, identifier, augmentations);
        if (fDTDHandler != null) {
            fDTDHandler.notationDecl(name, identifier, augmentations);
        }
    }

    /* (non-Javadoc)
     * @see org.apache.xerces.xni.XMLDTDHandler#setDTDSource(org.apache.xerces.xni.parser.XMLDTDSource)
     */
    public void setDTDSource(XMLDTDSource source) {
        fDTDSource = source;
    }

    /* (non-Javadoc)
     * @see org.apache.xerces.xni.XMLDTDHandler#startAttlist(java.lang.String, org.apache.xerces.xni.Augmentations)
     */
    public void startAttlist(String elementName, Augmentations augmentations)
        throws XNIException {
        if (fDTDHandler != null) {
            fDTDHandler.startAttlist(elementName, augmentations);
        }
    }

    /* (non-Javadoc)
     * @see org.apache.xerces.xni.XMLDTDHandler#startConditional(short, org.apache.xerces.xni.Augmentations)
     */
    public void startConditional(short type, Augmentations augmentations)
        throws XNIException {
        if (fDTDHandler != null) {
            fDTDHandler.startConditional(type, augmentations);
        }
    }

    /* (non-Javadoc)
     * @see org.apache.xerces.xni.XMLDTDHandler#startDTD(org.apache.xerces.xni.XMLLocator, org.apache.xerces.xni.Augmentations)
     */
    public void startDTD(XMLLocator locator, Augmentations augmentations)
        throws XNIException {
        fInDTD = true;
        if (fDTDHandler != null) {
            fDTDHandler.startDTD(locator, augmentations);
        }
    }

    /* (non-Javadoc)
     * @see org.apache.xerces.xni.XMLDTDHandler#startExternalSubset(org.apache.xerces.xni.XMLResourceIdentifier, org.apache.xerces.xni.Augmentations)
     */
    public void startExternalSubset(
        XMLResourceIdentifier identifier,
        Augmentations augmentations)
        throws XNIException {
        if (fDTDHandler != null) {
            fDTDHandler.startExternalSubset(identifier, augmentations);
        }
    }

    /* (non-Javadoc)
     * @see org.apache.xerces.xni.XMLDTDHandler#startParameterEntity(java.lang.String, org.apache.xerces.xni.XMLResourceIdentifier, java.lang.String, org.apache.xerces.xni.Augmentations)
     */
    public void startParameterEntity(
        String name,
        XMLResourceIdentifier identifier,
        String encoding,
        Augmentations augmentations)
        throws XNIException {
        if (fDTDHandler != null) {
            fDTDHandler.startParameterEntity(
                name,
                identifier,
                encoding,
                augmentations);
        }
    }

    /* (non-Javadoc)
     * @see org.apache.xerces.xni.XMLDTDHandler#unparsedEntityDecl(java.lang.String, org.apache.xerces.xni.XMLResourceIdentifier, java.lang.String, org.apache.xerces.xni.Augmentations)
     */
    public void unparsedEntityDecl(
        String name,
        XMLResourceIdentifier identifier,
        String notation,
        Augmentations augmentations)
        throws XNIException {
        this.addUnparsedEntity(name, identifier, notation, augmentations);
        if (fDTDHandler != null) {
            fDTDHandler.unparsedEntityDecl(
                name,
                identifier,
                notation,
                augmentations);
        }
    }

    /* (non-Javadoc)
     * @see org.apache.xerces.xni.parser.XMLDTDSource#getDTDHandler()
     */
    public XMLDTDHandler getDTDHandler() {
        return fDTDHandler;
    }

    /* (non-Javadoc)
     * @see org.apache.xerces.xni.parser.XMLDTDSource#setDTDHandler(org.apache.xerces.xni.XMLDTDHandler)
     */
    public void setDTDHandler(XMLDTDHandler handler) {
        fDTDHandler = handler;
    }

    // XIncludeHandler methods

    private void setErrorReporter(XMLErrorReporter reporter) {
        fErrorReporter = reporter;
        if (fErrorReporter != null) {
            fErrorReporter.putMessageFormatter(
                XIncludeMessageFormatter.XINCLUDE_DOMAIN,
                new XIncludeMessageFormatter());
            // this ensures the proper location is displayed in error messages
            if (fDocLocation != null) {
                fErrorReporter.setDocumentLocator(fDocLocation);
            }
        }
    }

    protected void handleFallbackElement() {
        setSawInclude(fDepth, false);
        fNamespaceContext.setContextInvalid();
        if (!getSawInclude(fDepth - 1)) {
            reportFatalError("FallbackParent");
        }

        if (getSawFallback(fDepth)) {
            reportFatalError("MultipleFallbacks");
        }
        else {
            setSawFallback(fDepth, true);
        }

        // Either the state is STATE_EXPECT_FALLBACK or it's STATE_IGNORE.
        // If we're ignoring, we want to stay ignoring. But if we're expecting this fallback element,
        // we want to signal that we should process the children.
        if (getState() == STATE_EXPECT_FALLBACK) {
            setState(STATE_NORMAL_PROCESSING);
        }
    }

    protected boolean handleIncludeElement(XMLAttributes attributes)
        throws XNIException {
        setSawInclude(fDepth, true);
        fNamespaceContext.setContextInvalid();
        if (getSawInclude(fDepth - 1)) {
            reportFatalError("IncludeChild", new Object[] { XINCLUDE_INCLUDE });
        }
        if (getState() == STATE_IGNORE)
            return true;

        // TODO: does Java use IURIs by default?
        //       [Definition: An internationalized URI reference, or IURI, is a URI reference that directly uses [Unicode] characters.]
        // TODO: figure out what section 4.1.1 of the XInclude spec is talking about
        //       has to do with disallowed ASCII character escaping
        //       this ties in with the above IURI section, but I suspect Java already does it
        
        String href = attributes.getValue(XINCLUDE_ATTR_HREF);
        String parse = attributes.getValue(XINCLUDE_ATTR_PARSE);
        String xpointer =  attributes.getValue(XPOINTER);
        String accept = attributes.getValue(XINCLUDE_ATTR_ACCEPT);
        String acceptLanguage = attributes.getValue(XINCLUDE_ATTR_ACCEPT_LANGUAGE);
        
        if (href == null && xpointer == null) {
            reportFatalError("XpointerMissing");
        }
        if (parse == null) {
            parse = XINCLUDE_PARSE_XML;
        }
        
        // Verify that if an accept and/or an accept-language attribute exist
        // that the value(s) don't contain disallowed characters.
        if (accept != null && !isValidInHTTPHeader(accept)) {
        	reportFatalError("AcceptMalformed", null);
        }
        if (acceptLanguage != null && !isValidInHTTPHeader(acceptLanguage)) {
            reportFatalError("AcceptLanguageMalformed", null);
        }

        XMLInputSource includedSource = null;
        if (fEntityResolver != null) {
            try {
                XMLResourceIdentifier resourceIdentifier =
                    new XMLResourceIdentifierImpl(
                        null,
                        href,
                        fCurrentBaseURI.getExpandedSystemId(),
                        XMLEntityManager.expandSystemId(
                            href,
                            fCurrentBaseURI.getExpandedSystemId(),
                            false));

                includedSource =
                    fEntityResolver.resolveEntity(resourceIdentifier);
            }
            catch (IOException e) {
                reportResourceError(
                    "XMLResourceError",
                    new Object[] { href, e.getMessage()});
                return false;
            }
        }

        if (includedSource == null) {
            includedSource =
                new XMLInputSource(
                    null,
                    href,
                    fCurrentBaseURI.getExpandedSystemId());
        }
        if (parse.equals(XINCLUDE_PARSE_XML)) {
            // Instead of always creating a new configuration, the first one can be reused
            if (fChildConfig == null) {
                String parserName = XINCLUDE_DEFAULT_CONFIGURATION;

                fChildConfig =
                    (XMLParserConfiguration)ObjectFactory.newInstance(
                        parserName,
                        ObjectFactory.findClassLoader(),
                        true);

                // use the same error reporter, entity resolver, and security manager.
                if (fErrorReporter != null) fChildConfig.setProperty(ERROR_REPORTER, fErrorReporter);
                if (fEntityResolver != null) fChildConfig.setProperty(ENTITY_RESOLVER, fEntityResolver);
                if (fSecurityManager != null) fChildConfig.setProperty(SECURITY_MANAGER, fSecurityManager);

                // use the same namespace context
                fChildConfig.setProperty(
                    Constants.XERCES_PROPERTY_PREFIX
                        + Constants.NAMESPACE_CONTEXT_PROPERTY,
                    fNamespaceContext);

                XIncludeHandler newHandler =
                    (XIncludeHandler)fChildConfig.getProperty(
                        Constants.XERCES_PROPERTY_PREFIX
                            + Constants.XINCLUDE_HANDLER_PROPERTY);
                newHandler.setParent(this);
                newHandler.setDocumentHandler(this.getDocumentHandler());
            }

            // set all features on parserConfig to match this parser configuration
            copyFeatures(fSettings, fChildConfig);

            try {
                // REVISIT: If we're going to support content negotation for
                // parse=xml we need to find a clean way to propogate the
                // parameters to the child parser. We cannot set those parameters
                // here because we may lose some information if we process the
                // URLConnection and then open a stream. The parser needs a
                // URLConnection to follow HTTP redirects and may also need
                // this object in the future to read external encoding information
                // which may be available in the Content-Type. -- mrglavas

                fNamespaceContext.pushScope();
                fChildConfig.parse(includedSource);
                // necessary to make sure proper location is reported in errors
                if (fErrorReporter != null) {
                    fErrorReporter.setDocumentLocator(fDocLocation);
                }
            }
            catch (XNIException e) {
                // necessary to make sure proper location is reported in errors
                if (fErrorReporter != null) {
                    fErrorReporter.setDocumentLocator(fDocLocation);
                }
                reportFatalError("XMLParseError", new Object[] { href });
            }
            catch (IOException e) {
                // necessary to make sure proper location is reported in errors
                if (fErrorReporter != null) {
                    fErrorReporter.setDocumentLocator(fDocLocation);
                }
                // An IOException indicates that we had trouble reading the file, not
                // that it was an invalid XML file.  So we send a resource error, not a
                // fatal error.
                reportResourceError(
                    "XMLResourceError",
                    new Object[] { href, e.getMessage()});
                return false;
            }
            finally {
                fNamespaceContext.popScope();
            }
        }
        else if (parse.equals(XINCLUDE_PARSE_TEXT)) {
            // we only care about encoding for parse="text"
            String encoding = attributes.getValue(XINCLUDE_ATTR_ENCODING);
            includedSource.setEncoding(encoding);
            XIncludeTextReader textReader = null;
            
            try {
                // Setup the appropriate text reader.
                if (!fIsXML11) {
                    if (fXInclude10TextReader == null) {
                        fXInclude10TextReader = new XIncludeTextReader(includedSource, this, fBufferSize);
                    }
                    else {
                        fXInclude10TextReader.setInputSource(includedSource);
                    }
                    textReader = fXInclude10TextReader;
                }
                else {
                    if (fXInclude11TextReader == null) {
                        fXInclude11TextReader = new XInclude11TextReader(includedSource, this, fBufferSize);
                    }
                    else {
                        fXInclude11TextReader.setInputSource(includedSource);
                    }
                    textReader = fXInclude11TextReader;
                }
                if (includedSource.getCharacterStream() == null
                    && includedSource.getByteStream() == null) {
                	textReader.setHttpProperties(accept, acceptLanguage);
                }
                textReader.setErrorReporter(fErrorReporter);
                textReader.parse();
            }
            // encoding errors
            catch (MalformedByteSequenceException ex) {
                fErrorReporter.reportError(ex.getDomain(), ex.getKey(), 
                    ex.getArguments(), XMLErrorReporter.SEVERITY_FATAL_ERROR);
            }
            catch (CharConversionException e) {
                fErrorReporter.reportError(XMLMessageFormatter.XML_DOMAIN,
                    "CharConversionFailure", null, XMLErrorReporter.SEVERITY_FATAL_ERROR);
            }
            catch (IOException e) {
                reportResourceError(
                    "TextResourceError",
                    new Object[] { href, e.getMessage()});
                return false;
            }
            finally {
                if (textReader != null) {
                    try {
                        textReader.close();
                    }
                    catch (IOException e) {
                        reportResourceError(
                            "TextResourceError",
                            new Object[] { href, e.getMessage()});
                        return false;
                    }
                }
            }
        }
        else {
            reportFatalError("InvalidParseValue", new Object[] { parse });
        }
        return true;
    }

    /**
     * Returns true if the element has the namespace "http://www.w3.org/2001/XInclude"
     * @param element the element to check
     * @return true if the element has the namespace "http://www.w3.org/2001/XInclude"
     */
    protected boolean hasXIncludeNamespace(QName element) {
        // REVISIT: The namespace of this element should be bound
        // already. Why are we looking it up from the namespace
        // context? -- mrglavas
        return element.uri == XINCLUDE_NS_URI
            || fNamespaceContext.getURI(element.prefix) == XINCLUDE_NS_URI;
    }

    /**
     * Checks if the element is an &lt;include&gt; element.  The element must have
     * the XInclude namespace, and a local name of "include".
     *
     * @param element the element to check
     * @return true if the element is an &lt;include&gt; element
     * @see #hasXIncludeNamespace(QName)
     */
    protected boolean isIncludeElement(QName element) {
        return element.localpart.equals(XINCLUDE_INCLUDE) && 
            hasXIncludeNamespace(element);
    }

    /**
     * Checks if the element is an &lt;fallback&gt; element.  The element must have
     * the XInclude namespace, and a local name of "fallback".
     *
     * @param element the element to check
     * @return true if the element is an &lt;fallback; element
     * @see #hasXIncludeNamespace(QName)
     */
    protected boolean isFallbackElement(QName element) {
        return element.localpart.equals(XINCLUDE_FALLBACK) &&
            hasXIncludeNamespace(element);
    }

    /**
     * Returns true if the current [base URI] is the same as the [base URI] that
     * was in effect on the include parent.  This method should <em>only</em> be called
     * when the current element is a top level included element, i.e. the direct child
     * of a fallback element, or the root elements in an included document.
     * The "include parent" is the element which, in the result infoset, will be the
     * direct parent of the current element.
     * @return true if the [base URIs] are the same string
     */
    protected boolean sameBaseURIAsIncludeParent() {
        String parentBaseURI = getIncludeParentBaseURI();
        String baseURI = fCurrentBaseURI.getExpandedSystemId();
        // REVISIT: should we use File#sameFile() ?
        //          I think the benefit of using it is that it resolves host names
        //          instead of just doing a string comparison.
        // TODO: [base URI] is still an open issue with the working group.
        //       They're deciding if xml:base should be added if the [base URI] is different in terms
        //       of resolving relative references, or if it should be added if they are different at all.
        //       Revisit this after a final decision has been made.
        //       The decision also affects whether we output the file name of the URI, or just the path.
        return parentBaseURI != null && parentBaseURI.equals(baseURI);
    }
    
    /**
     * Returns true if the current [language] is equivalent to the [language] that
     * was in effect on the include parent, taking case-insensitivity into account
     * as per [RFC 3066].  This method should <em>only</em> be called when the
     * current element is a top level included element, i.e. the direct child
     * of a fallback element, or the root elements in an included document.
     * The "include parent" is the element which, in the result infoset, will be the
     * direct parent of the current element.
     * 
     * @return true if the [language] properties have the same value
     * taking case-insensitivity into account as per [RFC 3066].
     */
    protected boolean sameLanguageAsIncludeParent() {
        String parentLanguage = getIncludeParentLanguage();
        return parentLanguage != null && parentLanguage.equalsIgnoreCase(fCurrentLanguage);
    }

    /**
     * Checks if the file indicated by the given XMLLocator has already been included
     * in the current stack.
     * @param includedSource the source to check for inclusion
     * @return true if the source has already been included
     */
    protected boolean searchForRecursiveIncludes(XMLLocator includedSource) {
        String includedSystemId = includedSource.getExpandedSystemId();

        if (includedSystemId == null) {
            try {
                includedSystemId =
                    XMLEntityManager.expandSystemId(
                        includedSource.getLiteralSystemId(),
                        includedSource.getBaseSystemId(),
                        false);
            }
            catch (MalformedURIException e) {
                reportFatalError("ExpandedSystemId");
            }
        }

        if (includedSystemId.equals(fCurrentBaseURI.getExpandedSystemId())) {
            return true;
        }

        if (fParentXIncludeHandler == null) {
            return false;
        }
        return fParentXIncludeHandler.searchForRecursiveIncludes(
            includedSource);
    }

    /**
     * Returns true if the current element is a top level included item.  This means
     * it's either the child of a fallback element, or the top level item in an
     * included document
     * @return true if the current element is a top level included item
     */
    protected boolean isTopLevelIncludedItem() {
        return isTopLevelIncludedItemViaInclude()
            || isTopLevelIncludedItemViaFallback();
    }

    protected boolean isTopLevelIncludedItemViaInclude() {
        return fDepth == 1 && !isRootDocument();
    }

    protected boolean isTopLevelIncludedItemViaFallback() {
        // Technically, this doesn't check if the parent was a fallback, it also
        // would return true if any of the parent's sibling elements were fallbacks.
        // However, this doesn't matter, since we will always be ignoring elements
        // whose parent's siblings were fallbacks.
        return getSawFallback(fDepth - 1);
    }

    /**
     * Processes the XMLAttributes object of startElement() calls.  Performs the following tasks:
     * <ul>
     * <li> If the element is a top level included item whose [base URI] is different from the
     * [base URI] of the include parent, then an xml:base attribute is added to specify the
     * true [base URI]
     * <li> For all namespace prefixes which are in-scope in an included item, but not in scope
     * in the include parent, a xmlns:prefix attribute is added
     * <li> For all attributes with a type of ENTITY, ENTITIES or NOTATIONS, the notations and
     * unparsed entities are processed as described in the spec, sections 4.5.1 and 4.5.2
     * </ul>
     * @param attributes
     * @return
     */
    protected XMLAttributes processAttributes(XMLAttributes attributes) {
        if (isTopLevelIncludedItem()) {
            // Modify attributes to fix the base URI (spec 4.5.5).
            // We only do it to top level included elements, which have a different
            // base URI than their include parent.
            if (!sameBaseURIAsIncludeParent()) {
                if (attributes == null) {
                    attributes = new XMLAttributesImpl();
                }

                // This causes errors with schema validation, if the schema doesn't
                // specify that these elements can have an xml:base attribute
                // TODO: add a user option to turn this off?
                String uri = null;
                try {
                    uri = this.getRelativeBaseURI();
                }
                catch (MalformedURIException e) {
                    // this shouldn't ever happen, since by definition, we had to traverse
                    // the same URIs to even get to this place
                    uri = fCurrentBaseURI.getExpandedSystemId();
                }
                int index =
                    attributes.addAttribute(
                        XML_BASE_QNAME,
                        XMLSymbols.fCDATASymbol,
                        uri);
                attributes.setSpecified(index, true);
            }
            
            // Modify attributes to perform language-fixup (spec 4.5.6).
            // We only do it to top level included elements, which have a different
            // [language] than their include parent.
            if (!sameLanguageAsIncludeParent()) {
                if (attributes == null) {
                    attributes = new XMLAttributesImpl();
                }
                int index =
                    attributes.addAttribute(
                        XML_LANG_QNAME,
                        XMLSymbols.fCDATASymbol,
                        fCurrentLanguage);
                attributes.setSpecified(index, true);
            }

            // Modify attributes of included items to do namespace-fixup. (spec 4.5.4)
            Enumeration inscopeNS = fNamespaceContext.getAllPrefixes();
            while (inscopeNS.hasMoreElements()) {
                String prefix = (String)inscopeNS.nextElement();
                String parentURI =
                    fNamespaceContext.getURIFromIncludeParent(prefix);
                String uri = fNamespaceContext.getURI(prefix);
                if (parentURI != uri && attributes != null) {
                    if (prefix == XMLSymbols.EMPTY_STRING) {
                        if (attributes
                            .getValue(
                                NamespaceContext.XMLNS_URI,
                                XMLSymbols.PREFIX_XMLNS)
                            == null) {
                            if (attributes == null) {
                                attributes = new XMLAttributesImpl();
                            }

                            QName ns = (QName)NEW_NS_ATTR_QNAME.clone();
                            ns.localpart = XMLSymbols.PREFIX_XMLNS;
                            ns.rawname = XMLSymbols.PREFIX_XMLNS;
                            attributes.addAttribute(
                                ns,
                                XMLSymbols.fCDATASymbol,
                                uri);
                        }
                    }
                    else if (
                        attributes.getValue(NamespaceContext.XMLNS_URI, prefix)
                            == null) {
                        if (attributes == null) {
                            attributes = new XMLAttributesImpl();
                        }

                        QName ns = (QName)NEW_NS_ATTR_QNAME.clone();
                        ns.localpart = prefix;
                        ns.rawname += prefix;
                        attributes.addAttribute(
                            ns,
                            XMLSymbols.fCDATASymbol,
                            uri);
                    }
                }
            }
        }

        if (attributes != null) {
            int length = attributes.getLength();
            for (int i = 0; i < length; i++) {
                String type = attributes.getType(i);
                String value = attributes.getValue(i);
                if (type == XMLSymbols.fENTITYSymbol) {
                    this.checkUnparsedEntity(value);
                }
                if (type == XMLSymbols.fENTITIESSymbol) {
                    // 4.5.1 - Unparsed Entities
                    StringTokenizer st = new StringTokenizer(value);
                    while (st.hasMoreTokens()) {
                        String entName = st.nextToken();
                        this.checkUnparsedEntity(entName);
                    }
                }
                else if (type == XMLSymbols.fNOTATIONSymbol) {
                    // 4.5.2 - Notations
                    this.checkNotation(value);
                }
                /* We actually don't need to do anything for 4.5.3, because at this stage the
                 * value of the attribute is just a string. It will be taken care of later
                 * in the pipeline, when the IDREFs are actually resolved against IDs.
                 *
                 * if (type == XMLSymbols.fIDREFSymbol || type == XMLSymbols.fIDREFSSymbol) { }
                 */
            }
        }

        return attributes;
    }

    /**
     * Returns a URI, relative to the include parent's base URI, of the current
     * [base URI].  For instance, if the current [base URI] was "dir1/dir2/file.xml"
     * and the include parent's [base URI] was "dir/", this would return "dir2/file.xml".
     * @return the relative URI
     */
    protected String getRelativeBaseURI() throws MalformedURIException {
        int includeParentDepth = getIncludeParentDepth();
        String relativeURI = this.getRelativeURI(includeParentDepth);
        if (isRootDocument()) {
            return relativeURI;
        }
        else {
            if (relativeURI.equals("")) {
                relativeURI = fCurrentBaseURI.getLiteralSystemId();
            }

            if (includeParentDepth == 0) {
                if (fParentRelativeURI == null) {
                    fParentRelativeURI =
                        fParentXIncludeHandler.getRelativeBaseURI();
                }
                if (fParentRelativeURI.equals("")) {
                    return relativeURI;
                }
                URI uri = new URI("file", fParentRelativeURI);
                uri = new URI(uri, relativeURI);
                return uri.getPath();
            }
            else {
                return relativeURI;
            }
        }
    }

    /**
     * Returns the [base URI] of the include parent.
     * @return the base URI of the include parent.
     */
    private String getIncludeParentBaseURI() {
        int depth = getIncludeParentDepth();
        if (!isRootDocument() && depth == 0) {
            return fParentXIncludeHandler.getIncludeParentBaseURI();
        }
        else {
            return this.getBaseURI(depth);
        }
    }
    
    /**
     * Returns the [language] of the include parent.
     * 
     * @return the language property of the include parent.
     */
    private String getIncludeParentLanguage() {
        int depth = getIncludeParentDepth();
        if (!isRootDocument() && depth == 0) {
            return fParentXIncludeHandler.getIncludeParentLanguage();
        }
        else {
            return getLanguage(depth);
        }
    }

    /**
     * Returns the depth of the include parent.  Here, the include parent is
     * calculated as the last non-include or non-fallback element. It is assumed
     * this method is called when the current element is a top level included item.
     * Returning 0 indicates that the top level element in this document
     * was an include element.
     * @return the depth of the top level include element
     */
    private int getIncludeParentDepth() {
        // We don't start at fDepth, since it is either the top level included item,
        // or an include element, when this method is called.
        for (int i = fDepth - 1; i >= 0; i--) {
            // This technically might not always return the first non-include/fallback
            // element that it comes to, since sawFallback() returns true if a fallback
            // was ever encountered at that depth.  However, if a fallback was encountered
            // at that depth, and it wasn't the direct descendant of the current element
            // then we can't be in a situation where we're calling this method (because
            // we'll always be in STATE_IGNORE)
            if (!getSawInclude(i) && !getSawFallback(i)) {
                return i;
            }
        }
        // shouldn't get here, since depth 0 should never have an include element or
        // a fallback element
        return 0;
    }

    /**
     * Modify the augmentations.  Add an [included] infoset item, if the current
     * element is a top level included item.
     * @param augs the Augmentations to modify.
     * @return the modified Augmentations
     */
    protected Augmentations modifyAugmentations(Augmentations augs) {
        return modifyAugmentations(augs, false);
    }

    /**
     * Modify the augmentations.  Add an [included] infoset item, if <code>force</code>
     * is true, or if the current element is a top level included item.
     * @param augs the Augmentations to modify.
     * @param force whether to force modification
     * @return the modified Augmentations
     */
    protected Augmentations modifyAugmentations(
        Augmentations augs,
        boolean force) {
        if (force || isTopLevelIncludedItem()) {
            if (augs == null) {
                augs = new AugmentationsImpl();
            }
            augs.putItem(XINCLUDE_INCLUDED, Boolean.TRUE);
        }
        return augs;
    }

    protected int getState(int depth) {
        return fState[depth];
    }

    protected int getState() {
        return fState[fDepth];
    }

    protected void setState(int state) {
        if (fDepth >= fState.length) {
            int[] newarray = new int[fDepth * 2];
            System.arraycopy(fState, 0, newarray, 0, fState.length);
            fState = newarray;
        }
        fState[fDepth] = state;
    }

    /**
     * Records that an &lt;fallback&gt; was encountered at the specified depth,
     * as an ancestor of the current element, or as a sibling of an ancestor of the
     * current element.
     *
     * @param depth
     * @param val
     */
    protected void setSawFallback(int depth, boolean val) {
        if (depth >= fSawFallback.length) {
            boolean[] newarray = new boolean[depth * 2];
            System.arraycopy(fSawFallback, 0, newarray, 0, fSawFallback.length);
            fSawFallback = newarray;
        }
        fSawFallback[depth] = val;
    }

    /**
     * Returns whether an &lt;fallback&gt; was encountered at the specified depth,
     * as an ancestor of the current element, or as a sibling of an ancestor of the
     * current element.
     *
     * @param depth
     */
    protected boolean getSawFallback(int depth) {
        if (depth >= fSawFallback.length) {
            return false;
        }
        return fSawFallback[depth];
    }

    /**
     * Records that an &lt;include&gt; was encountered at the specified depth,
     * as an ancestor of the current item.
     *
     * @param depth
     * @param val
     */
    protected void setSawInclude(int depth, boolean val) {
        if (depth >= fSawInclude.length) {
            boolean[] newarray = new boolean[depth * 2];
            System.arraycopy(fSawInclude, 0, newarray, 0, fSawInclude.length);
            fSawInclude = newarray;
        }
        fSawInclude[depth] = val;
    }

    /**
     * Return whether an &lt;include&gt; was encountered at the specified depth,
     * as an ancestor of the current item.
     *
     * @param depth
     * @return
     */
    protected boolean getSawInclude(int depth) {
        if (depth >= fSawInclude.length) {
            return false;
        }
        return fSawInclude[depth];
    }

    protected void reportResourceError(String key) {
        this.reportFatalError(key, null);
    }

    protected void reportResourceError(String key, Object[] args) {
        this.reportError(key, args, XMLErrorReporter.SEVERITY_WARNING);
    }

    protected void reportFatalError(String key) {
        this.reportFatalError(key, null);
    }

    protected void reportFatalError(String key, Object[] args) {
        this.reportError(key, args, XMLErrorReporter.SEVERITY_FATAL_ERROR);
    }

    private void reportError(String key, Object[] args, short severity) {
        if (fErrorReporter != null) {
            fErrorReporter.reportError(
                XIncludeMessageFormatter.XINCLUDE_DOMAIN,
                key,
                args,
                severity);
        }
        // we won't worry about when error reporter is null, since there should always be
        // at least the default error reporter
    }

    /**
     * Set the parent of this XIncludeHandler in the tree
     * @param parent
     */
    protected void setParent(XIncludeHandler parent) {
        fParentXIncludeHandler = parent;
    }

    // used to know whether to pass declarations to the document handler
    protected boolean isRootDocument() {
        return fParentXIncludeHandler == null;
    }

    /**
     * Caches an unparsed entity.
     * @param name the name of the unparsed entity
     * @param identifier the location of the unparsed entity
     * @param augmentations any Augmentations that were on the original unparsed entity declaration
     */
    protected void addUnparsedEntity(
        String name,
        XMLResourceIdentifier identifier,
        String notation,
        Augmentations augmentations) {
        UnparsedEntity ent = new UnparsedEntity();
        ent.name = name;
        ent.systemId = identifier.getLiteralSystemId();
        ent.publicId = identifier.getPublicId();
        ent.baseURI = identifier.getBaseSystemId();
        ent.notation = notation;
        ent.augmentations = augmentations;
        fUnparsedEntities.add(ent);
    }

    /**
     * Caches a notation.
     * @param name the name of the notation
     * @param identifier the location of the notation
     * @param augmentations any Augmentations that were on the original notation declaration
     */
    protected void addNotation(
        String name,
        XMLResourceIdentifier identifier,
        Augmentations augmentations) {
        Notation not = new Notation();
        not.name = name;
        not.systemId = identifier.getLiteralSystemId();
        not.publicId = identifier.getPublicId();
        not.baseURI = identifier.getBaseSystemId();
        not.augmentations = augmentations;
        fNotations.add(not);
    }

    /**
     * Checks if an UnparsedEntity with the given name was declared in the DTD of the document
     * for the current pipeline.  If so, then the notation for the UnparsedEntity is checked.
     * If that turns out okay, then the UnparsedEntity is passed to the root pipeline to
     * be checked for conflicts, and sent to the root DTDHandler.
     *
     * @param entName the name of the UnparsedEntity to check
     */
    protected void checkUnparsedEntity(String entName) {
        UnparsedEntity ent = new UnparsedEntity();
        ent.name = entName;
        int index = fUnparsedEntities.indexOf(ent);
        if (index != -1) {
            ent = (UnparsedEntity)fUnparsedEntities.get(index);
            // first check the notation of the unparsed entity
            checkNotation(ent.notation);
            checkAndSendUnparsedEntity(ent);
        }
    }

    /**
     * Checks if a Notation with the given name was declared in the DTD of the document
     * for the current pipeline.  If so, that Notation is passed to the root pipeline to
     * be checked for conflicts, and sent to the root DTDHandler
     *
     * @param notName the name of the Notation to check
     */
    protected void checkNotation(String notName) {
        Notation not = new Notation();
        not.name = notName;
        int index = fNotations.indexOf(not);
        if (index != -1) {
            not = (Notation)fNotations.get(index);
            checkAndSendNotation(not);
        }
    }

    /**
     * The purpose of this method is to check if an UnparsedEntity conflicts with a previously
     * declared entity in the current pipeline stack.  If there is no conflict, the
     * UnparsedEntity is sent by the root pipeline.
     *
     * @param ent the UnparsedEntity to check for conflicts
     */
    protected void checkAndSendUnparsedEntity(UnparsedEntity ent) {
        if (isRootDocument()) {
            int index = fUnparsedEntities.indexOf(ent);
            if (index == -1) {
                // There is no unparsed entity with the same name that we have sent.
                // Calling unparsedEntityDecl() will add the entity to our local store,
                // and also send the unparsed entity to the DTDHandler
                XMLResourceIdentifier id =
                    new XMLResourceIdentifierImpl(
                        ent.publicId,
                        ent.systemId,
                        ent.baseURI,
                        null);
                this.addUnparsedEntity(
                    ent.name,
                    id,
                    ent.notation,
                    ent.augmentations);
                if (fSendUEAndNotationEvents && fDTDHandler != null) {
                    fDTDHandler.unparsedEntityDecl(
                        ent.name,
                        id,
                        ent.notation,
                        ent.augmentations);
                }
            }
            else {
                UnparsedEntity localEntity =
                    (UnparsedEntity)fUnparsedEntities.get(index);
                if (!ent.isDuplicate(localEntity)) {
                    reportFatalError(
                        "NonDuplicateUnparsedEntity",
                        new Object[] { ent.name });
                }
            }
        }
        else {
            fParentXIncludeHandler.checkAndSendUnparsedEntity(ent);
        }
    }

    /**
     * The purpose of this method is to check if a Notation conflicts with a previously
     * declared notation in the current pipeline stack.  If there is no conflict, the
     * Notation is sent by the root pipeline.
     *
     * @param not the Notation to check for conflicts
     */
    protected void checkAndSendNotation(Notation not) {
        if (isRootDocument()) {
            int index = fNotations.indexOf(not);
            if (index == -1) {
                // There is no notation with the same name that we have sent.
                XMLResourceIdentifier id =
                    new XMLResourceIdentifierImpl(
                        not.publicId,
                        not.systemId,
                        not.baseURI,
                        null);
                this.addNotation(not.name, id, not.augmentations);
                if (fSendUEAndNotationEvents && fDTDHandler != null) {
                    fDTDHandler.notationDecl(not.name, id, not.augmentations);
                }
            }
            else {
                Notation localNotation = (Notation)fNotations.get(index);
                if (!not.isDuplicate(localNotation)) {
                    reportFatalError(
                        "NonDuplicateNotation",
                        new Object[] { not.name });
                }
            }
        }
        else {
            fParentXIncludeHandler.checkAndSendNotation(not);
        }
    }

    // It would be nice if we didn't have to repeat code like this, but there's no interface that has
    // setFeature() and addRecognizedFeatures() that the objects have in common.
    protected void copyFeatures(
        XMLComponentManager from,
        ParserConfigurationSettings to) {
        Enumeration features = Constants.getXercesFeatures();
        copyFeatures1(features, Constants.XERCES_FEATURE_PREFIX, from, to);
        features = Constants.getSAXFeatures();
        copyFeatures1(features, Constants.SAX_FEATURE_PREFIX, from, to);
    }

    protected void copyFeatures(
        XMLComponentManager from,
        XMLParserConfiguration to) {
        Enumeration features = Constants.getXercesFeatures();
        copyFeatures1(features, Constants.XERCES_FEATURE_PREFIX, from, to);
        features = Constants.getSAXFeatures();
        copyFeatures1(features, Constants.SAX_FEATURE_PREFIX, from, to);
    }

    private void copyFeatures1(
        Enumeration features,
        String featurePrefix,
        XMLComponentManager from,
        ParserConfigurationSettings to) {
        while (features.hasMoreElements()) {
            String featureId = featurePrefix + (String)features.nextElement();

            to.addRecognizedFeatures(new String[] { featureId });

            try {
                to.setFeature(featureId, from.getFeature(featureId));
            }
            catch (XMLConfigurationException e) {
                // componentManager doesn't support this feature,
                // so we won't worry about it
            }
        }
    }

    private void copyFeatures1(
        Enumeration features,
        String featurePrefix,
        XMLComponentManager from,
        XMLParserConfiguration to) {
        while (features.hasMoreElements()) {
            String featureId = featurePrefix + (String)features.nextElement();
            boolean value = from.getFeature(featureId);

            try {
                to.setFeature(featureId, value);
            }
            catch (XMLConfigurationException e) {
                // componentManager doesn't support this feature,
                // so we won't worry about it
            }
        }
    }

    // This is a storage class to hold information about the notations.
    // We're not using XMLNotationDecl because we don't want to lose the augmentations.
    protected class Notation {
        public String name;
        public String systemId;
        public String baseURI;
        public String publicId;
        public Augmentations augmentations;

        // equals() returns true if two Notations have the same name.
        // Useful for searching Vectors for notations with the same name
        public boolean equals(Object obj) {
            if (obj == null) {
                return false;
            }
            if (obj instanceof Notation) {
                Notation other = (Notation)obj;
                return name.equals(other.name);
            }
            return false;
        }

        // from 4.5.2
        // Notation items with the same [name], [system identifier],
        // [public identifier], and [declaration base URI] are considered
        // to be duplicate
        public boolean isDuplicate(Object obj) {
            if (obj != null && obj instanceof Notation) {
                Notation other = (Notation)obj;
                return name.equals(other.name)
                    && (systemId == other.systemId
                        || (systemId != null && systemId.equals(other.systemId)))
                    && (publicId == other.publicId
                        || (publicId != null && publicId.equals(other.publicId)))
                    && (baseURI == other.baseURI
                        || (baseURI != null && baseURI.equals(other.baseURI)));
            }
            return false;
        }
    }

    // This is a storage class to hold information about the unparsed entities.
    // We're not using XMLEntityDecl because we don't want to lose the augmentations.
    protected class UnparsedEntity {
        public String name;
        public String systemId;
        public String baseURI;
        public String publicId;
        public String notation;
        public Augmentations augmentations;

        // equals() returns true if two UnparsedEntities have the same name.
        // Useful for searching Vectors for entities with the same name
        public boolean equals(Object obj) {
            if (obj == null) {
                return false;
            }
            if (obj instanceof UnparsedEntity) {
                UnparsedEntity other = (UnparsedEntity)obj;
                return name.equals(other.name);
            }
            return false;
        }

        // from 4.5.1:
        // Unparsed entity items with the same [name], [system identifier],
        // [public identifier], [declaration base URI], [notation name], and
        // [notation] are considered to be duplicate
        public boolean isDuplicate(Object obj) {
            if (obj != null && obj instanceof UnparsedEntity) {
                UnparsedEntity other = (UnparsedEntity)obj;
                return name.equals(other.name)
                    && (systemId == other.systemId
                        || (systemId != null && systemId.equals(other.systemId)))
                    && (publicId == other.publicId
                        || (publicId != null && publicId.equals(other.publicId)))
                    && (baseURI == other.baseURI
                        || (baseURI != null && baseURI.equals(other.baseURI)))
                    && (notation == other.notation
                        || (notation != null && notation.equals(other.notation)));
            }
            return false;
        }
    }

    // The following methods are used for XML Base processing

    /**
     * Saves the current base URI to the top of the stack.
     */
    protected void saveBaseURI() {
        fBaseURIScope.push(fDepth);
        fBaseURI.push(fCurrentBaseURI.getBaseSystemId());
        fLiteralSystemID.push(fCurrentBaseURI.getLiteralSystemId());
        fExpandedSystemID.push(fCurrentBaseURI.getExpandedSystemId());
    }

    /**
     * Discards the URIs at the top of the stack, and restores the ones beneath it.
     */
    protected void restoreBaseURI() {
        fBaseURI.pop();
        fLiteralSystemID.pop();
        fExpandedSystemID.pop();
        fBaseURIScope.pop();
        fCurrentBaseURI.setBaseSystemId((String)fBaseURI.peek());
        fCurrentBaseURI.setLiteralSystemId((String)fLiteralSystemID.peek());
        fCurrentBaseURI.setExpandedSystemId((String)fExpandedSystemID.peek());
    }
    
    // The following methods are used for language processing
    
    /**
     * Saves the given language on the top of the stack.
     * 
     * @param lanaguage the language to push onto the stack.
     */
    protected void saveLanguage(String language) {
        fLanguageScope.push(fDepth);
        fLanguageStack.push(language);
    }
    
    /**
     * Discards the language at the top of the stack, and returns the one beneath it.
     */
    public String restoreLanguage() {
        fLanguageStack.pop();
        fLanguageScope.pop();
        return (String) fLanguageStack.peek();
    }

    /**
     * Gets the base URI that was in use at that depth
     * @param depth
     * @return the base URI
     */
    public String getBaseURI(int depth) {
        int scope = scopeOfBaseURI(depth);
        return (String)fExpandedSystemID.elementAt(scope);
    }
    
    /**
     * Gets the language that was in use at that depth.
     * @param depth
     * @return the language
     */
    public String getLanguage(int depth) {
        int scope = scopeOfLanguage(depth);
        return (String)fLanguageStack.elementAt(scope);
    }

    /**
     * Returns a relative URI, which when resolved against the base URI at the
     * specified depth, will create the current base URI.
     * This is accomplished by merged the literal system IDs.
     * @param depth the depth at which to start creating the relative URI
     * @return a relative URI to convert the base URI at the given depth to the current
     *         base URI
     */
    public String getRelativeURI(int depth) throws MalformedURIException {
        // The literal system id at the location given by "start" is *in focus* at
        // the given depth. So we need to adjust it to the next scope, so that we
        // only process out of focus literal system ids
        int start = scopeOfBaseURI(depth) + 1;
        if (start == fBaseURIScope.size()) {
            // If that is the last system id, then we don't need a relative URI
            return "";
        }
        URI uri = new URI("file", (String)fLiteralSystemID.elementAt(start));
        for (int i = start + 1; i < fBaseURIScope.size(); i++) {
            uri = new URI(uri, (String)fLiteralSystemID.elementAt(i));
        }
        return uri.getPath();
    }

    // We need to find two consecutive elements in the scope stack,
    // such that the first is lower than 'depth' (or equal), and the
    // second is higher.
    private int scopeOfBaseURI(int depth) {
        for (int i = fBaseURIScope.size() - 1; i >= 0; i--) {
            if (fBaseURIScope.elementAt(i) <= depth)
                return i;
        }
        // we should never get here, because 0 was put on the stack in startDocument()
        return -1;
    }
    
    private int scopeOfLanguage(int depth) {
        for (int i = fLanguageScope.size() - 1; i >= 0; i--) {
            if (fLanguageScope.elementAt(i) <= depth)
                return i;
        }
        // we should never get here, because 0 was put on the stack in startDocument()
        return -1;
    }

    /**
     * Search for a xml:base attribute, and if one is found, put the new base URI into
     * effect.
     */
    protected void processXMLBaseAttributes(XMLAttributes attributes) {
        String baseURIValue =
            attributes.getValue(NamespaceContext.XML_URI, "base");
        if (baseURIValue != null) {
            try {
                String expandedValue =
                    XMLEntityManager.expandSystemId(
                        baseURIValue,
                        fCurrentBaseURI.getExpandedSystemId(),
                        false);
                fCurrentBaseURI.setLiteralSystemId(baseURIValue);
                fCurrentBaseURI.setBaseSystemId(
                    fCurrentBaseURI.getExpandedSystemId());
                fCurrentBaseURI.setExpandedSystemId(expandedValue);

                // push the new values on the stack
                saveBaseURI();
            }
            catch (MalformedURIException e) {
                // REVISIT: throw error here
            }
        }
    }
    
    /**
     * Search for a xml:lang attribute, and if one is found, put the new 
     * [language] into effect.
     */
    protected void processXMLLangAttributes(XMLAttributes attributes) {
        String language = attributes.getValue(NamespaceContext.XML_URI, "lang");
        if (language != null) {
            fCurrentLanguage = language;
            saveLanguage(fCurrentLanguage);
        }
    }
    
    /**
     * Returns <code>true</code> if the given string 
     * would be valid in an HTTP header.
     * 
     * @param value string to check
     * @return <code>true</code> if the given string
     * would be valid in an HTTP header
     */
    private boolean isValidInHTTPHeader (String value) {
        char ch;
        for (int i = value.length() - 1; i >= 0; --i) {
            ch = value.charAt(i);
            if (ch < 0x20 || ch > 0x7E) {
                return false;
            }
        }
        return true;
    }
    
}