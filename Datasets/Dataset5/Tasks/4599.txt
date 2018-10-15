protected boolean fNamespacesEnabled = true;

/*
 * The Apache Software License, Version 1.1
 *
 *
 * Copyright (c) 1999 The Apache Software Foundation.  All rights
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

package org.apache.xerces.framework;

import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.IOException;
import java.io.FileNotFoundException;
import java.io.Reader;
import java.net.URL;
import java.net.MalformedURLException;
import java.util.Locale;
import java.util.Hashtable;
import java.util.ResourceBundle;
import java.util.Stack;
import java.util.ListResourceBundle;

import org.apache.xerces.readers.DefaultReaderFactory;
import org.apache.xerces.readers.XMLDeclRecognizer;
import org.apache.xerces.readers.XMLEntityHandler;
import org.apache.xerces.readers.XMLEntityReaderFactory;
import org.apache.xerces.utils.ChunkyByteArray;
import org.apache.xerces.utils.ChunkyCharArray;
import org.apache.xerces.utils.NamespacesScope;
import org.apache.xerces.utils.StringPool;
import org.apache.xerces.utils.XMLCharacterProperties;
import org.apache.xerces.utils.XMLMessageProvider;
import org.apache.xerces.utils.XMLMessages;
import org.apache.xerces.utils.ImplementationMessages;

// REVISIT - use component factory
import org.apache.xerces.validators.dtd.DTDValidator;
import org.apache.xerces.validators.schema.XSchemaValidator;
import org.apache.xerces.validators.datatype.DatatypeMessageProvider;
import org.apache.xerces.validators.schema.SchemaMessageProvider;

import org.xml.sax.EntityResolver;
import org.xml.sax.ErrorHandler;
import org.xml.sax.InputSource;
import org.xml.sax.Locator;
import org.xml.sax.Parser;
import org.xml.sax.SAXException;
import org.xml.sax.SAXNotRecognizedException;
import org.xml.sax.SAXNotSupportedException;
import org.xml.sax.SAXParseException;
import org.xml.sax.helpers.LocatorImpl;

/**
 * This is the base class of all standard parsers.
 *
 * @version
 */
public abstract class XMLParser
    implements XMLErrorReporter,
               XMLEntityHandler,
               XMLDocumentScanner.EventHandler,
               DTDValidator.EventHandler,
               Locator {

    //
    // Constants
    //

    // protected

    /** SAX2 features prefix (http://xml.org/sax/features/). */
    protected static final String SAX2_FEATURES_PREFIX = "http://xml.org/sax/features/";

    /** SAX2 properties prefix (http://xml.org/sax/properties/). */
    protected static final String SAX2_PROPERTIES_PREFIX = "http://xml.org/sax/properties/";

    /** Xerces features prefix (http://apache.org/xml/features/). */
    protected static final String XERCES_FEATURES_PREFIX = "http://apache.org/xml/features/";

    /** Xerces properties prefix (http://apache.org/xml/properties/). */
    protected static final String XERCES_PROPERTIES_PREFIX = "http://apache.org/xml/properties/";

    // private

    /** Features recognized by this parser. */
    private static final String RECOGNIZED_FEATURES[] = {
        // SAX2 core
        "http://xml.org/sax/features/validation",
        "http://xml.org/sax/features/external-general-entities",
        "http://xml.org/sax/features/external-parameter-entities",
        "http://xml.org/sax/features/namespaces",
        // Xerces
        "http://apache.org/xml/features/validation/dynamic",
        "http://apache.org/xml/features/validation/default-attribute-values",
        "http://apache.org/xml/features/validation/validate-content-models",
        "http://apache.org/xml/features/validation/validate-datatypes",
        "http://apache.org/xml/features/validation/warn-on-duplicate-attdef",
        "http://apache.org/xml/features/validation/warn-on-undeclared-elemdef",
        "http://apache.org/xml/features/allow-java-encodings",
        "http://apache.org/xml/features/continue-after-fatal-error",
    };

    /** Properties recognized by this parser. */
    private static final String RECOGNIZED_PROPERTIES[] = {
        // SAX2 core
        //"http://xml.org/sax/properties/namespace-sep",
        "http://xml.org/sax/properties/xml-string",
        // Xerces
    };

    // debugging

    /** Set to true and recompile to print exception stack trace. */
    private static final boolean PRINT_EXCEPTION_STACK_TRACE = false;

    //
    // Data
    //

    // state

    private XMLAttrList fAttrList = null;
    protected boolean fParseInProgress = false;
    private boolean fNeedReset = false;

    // features

    /** Continue after fatal error. */
    private boolean fContinueAfterFatalError;

    // properties

    /** Error handler. */
    private ErrorHandler fErrorHandler;

    // literal strings

    private char[] fCharRefData = null;
    private int[] fElementTypeStack = new int[8];
    private int[] fElementEntityStack = new int[8];
    private boolean fCalledStartDocument = false;
    private int fXMLLang = -1;
    protected String fNamespaceSep = "";

    // validators

    protected XMLValidator fValidator = null;
    protected DTDValidator fDTDValidator = null;
    protected XSchemaValidator fSchemaValidator = null;
    private boolean fCheckedForSchema = false;

    // other

    private Locator fLocator = null;
    private Locale fLocale = null;
    private LocatorImpl fAttrNameLocator = null;
    private boolean fSeenRootElement = false;
    private boolean fStandaloneDocument = false;
    private int fCDATASymbol = -1;
    protected boolean fNamespacesEnabled = false;
    private boolean fSendCharDataAsCharArray = false;
    private boolean fValidating = false;
    private boolean fScanningDTD = false;
    private StringPool.CharArrayRange fCurrentElementCharArrayRange = null;

    // error information

    private static XMLMessageProvider fgXMLMessages = new XMLMessages();
    private static XMLMessageProvider fgImplementationMessages = new ImplementationMessages();
    private static XMLMessageProvider fgSchemaMessages = new SchemaMessageProvider();
    private static XMLMessageProvider fgDatatypeMessages= new DatatypeMessageProvider();

    //
    //
    //
    protected XMLDocumentScanner fScanner = null;
    protected StringPool fStringPool = null;
    protected XMLErrorReporter fErrorReporter = null;
    protected XMLEntityHandler fEntityHandler = null;
    protected XMLEntityReaderFactory fReaderFactory = null;
    protected int fElementDepth = 0;
    protected int fCurrentElementType = -1;
    protected int fCurrentElementEntity = -1;
    protected boolean fInElementContent = false;

    //
    // Constructors
    //

    /**
     * Constructor
     */
    protected XMLParser() {

        fStringPool = new StringPool();
        fErrorReporter = this;
        fEntityHandler = this;

        // set framework properties
        fScanner = new XMLDocumentScanner(/*XMLDocumentScanner.EventHandler*/this, fStringPool, fErrorReporter, fEntityHandler, new ChunkyCharArray(fStringPool));

        // other inits
        XMLCharacterProperties.initCharFlags();
        fAttrList = new XMLAttrList(fStringPool);
        fLocator = this;
        fReaderFactory = new DefaultReaderFactory();

        // REVISIT - add all other instance variables...

        fCDATASymbol = fStringPool.addSymbol("CDATA");
        fDTDValidator = new DTDValidator(/*DTDValidator.EventHandler*/this, fStringPool, fErrorReporter, fEntityHandler);

        // set features
        try { setContinueAfterFatalError(false); }
        catch (SAXException e) {} // ignore

    } // <init>()

    //
    // Public methods
    //

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
        return RECOGNIZED_FEATURES;
    }

    /**
     * Returns true if the specified feature is recognized.
     *
     * @see #getFeaturesRecognized
     * @see #setFeature
     * @see #getFeature
     */
    public boolean isFeatureRecognized(String featureId) {
        String[] recognizedFeatures = getFeaturesRecognized();
        for (int i = 0; i < recognizedFeatures.length; i++) {
            if (featureId.equals(recognizedFeatures[i]))
                return true;
        }
        return false;
    }

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
        return RECOGNIZED_PROPERTIES;
    }

    /**
     * Returns true if the specified property is recognized.
     *
     * @see #getPropertiesRecognized
     * @see #setProperty
     * @see #getProperty
     */
    public boolean isPropertyRecognized(String propertyId) {
        String[] recognizedProperties = getPropertiesRecognized();
        for (int i = 0; i < recognizedProperties.length; i++) {
            if (propertyId.equals(recognizedProperties[i]))
                return true;
        }
        return false;
    }

    // initialization

    /**
     * Setup for application-driven parsing.
     *
     * @param source the input source to be parsed.
     * @see #parseSome
     */
    public boolean parseSomeSetup(InputSource source) throws Exception {
        if (fNeedReset)
            resetOrCopy();
        fParseInProgress = true;
        fNeedReset = true;
        return fEntityHandler.startReadingFromDocument(source);
    }

    /**
     * Application-driven parsing.
     *
     * @see #parseSomeSetup
     */
    public boolean parseSome() throws Exception {
        if (!fScanner.parseSome(false)) {
            fParseInProgress = false;
            return false;
        }
        return true;
    }

    // resetting

    /** Reset parser instance so that it can be reused. */
    public void reset() throws Exception {
        fStringPool.reset();
        fAttrList.reset(fStringPool);
        resetCommon();

    } // reset()

    // properties (the normal kind)

    /**
     * Sets the locator.
     *
     * @param locator The new locator.
     */
    public void setLocator(Locator locator) {
        fLocator = locator;
    }

    /**
     * return the locator being used by the parser
     *
     * @return the parser's active locator
     */
    public final Locator getLocator() {
        return fLocator;
    }

    /**
     * Set the reader factory.
     */
    public void setReaderFactory(XMLEntityReaderFactory readerFactory) {
        fReaderFactory = readerFactory;
        fReaderFactory.setSendCharDataAsCharArray(fSendCharDataAsCharArray);
    }

    // DTD callbacks

    /**
     * Callback for processing instruction in DTD.
     *
     * @param target the string pool index of the PI's target
     * @param data the string pool index of the PI's data
     * @exception java.lang.Exception
     */
    public void processingInstructionInDTD(int target, int data) throws Exception {
        fStringPool.releaseString(target);
        fStringPool.releaseString(data);
    }

    /**
     * Callback for comment in DTD.
     *
     * @param comment the string pool index of the comment text
     * @exception java.lang.Exception
     */
    public void commentInDTD(int comment) throws Exception {
        fStringPool.releaseString(comment);
    }

    //
    // Public abstract methods
    //

    // document callbacks

    /**
     * Callback for start of document
     *
     * If the there is no version info, encoding info, or standalone info,
     * the corresponding argument will be set to -1.
     *
     * @param version string pool index of the version attribute's value
     * @param encoding string pool index of the encoding attribute's value
     * @param standAlone string pool index of the standalone attribute's value
     * @exception java.lang.Exception
     */
    public abstract void startDocument(int version, int encoding, int standAlone)  throws Exception;

    /**
     * callback for the end of document.
     *
     * @exception java.lang.Exception
     */
    public abstract void endDocument() throws Exception;

    /**
     * callback for the start of a namespace declaration scope.
     *
     * @param prefix string pool index of the namespace prefix being declared
     * @param uri string pool index of the namespace uri begin bound
     * @param java.lang.Exception
     */
    public abstract void startNamespaceDeclScope(int prefix, int uri) throws Exception;

    /**
     * callback for the end a namespace declaration scope.
     *
     * @param prefix string pool index of the namespace prefix being declared
     * @exception java.lang.Exception
     */
    public abstract void endNamespaceDeclScope(int prefix) throws Exception;
    
    /**
     * Supports DOM Level 2 internalSubset additions.
     * Called when the internal subset is completely scanned.
     */
    public abstract void internalSubset(int internalSubset);
    

    /**
     * callback for the start of element.
     *
     * @param elementType element handle for the element being scanned
     * @param attrList attrList containing the attributes of the element
     * @param attrListHandle handle into attrList.  Allows attributes to be retreived.
     * @exception java.lang.Exception
     */
    public abstract void startElement(int elementType, XMLAttrList attrList, int attrListHandle) throws Exception;

    /**
     * callback for end of element.
     *
     * @param elementType element handle for the element being scanned
     * @exception java.lang.Exception
     */
    public abstract void endElement(int elementType) throws Exception;

    /**
     * callback for start of entity reference.
     *
     * @param entityName string pool index of the entity name
     * @param entityType the XMLEntityHandler.ENTITYTYPE_* type
     * @see org.apache.xerces.readers.XMLEntityHandler
     * @param entityContext the XMLEntityHandler.CONTEXT_* type for where
     *        the entity reference appears
     * @see org.apache.xerces.readers.XMLEntityHandler
     * @exception java.lang.Exception
     */
    public abstract void startEntityReference(int entityName, int entityType, int entityContext) throws Exception;

    /**
     * callback for end of entity reference.
     *
     * @param entityName string pool index of the entity anem
     * @param entityType the XMLEntityHandler.ENTITYTYPE_* type
     * @see org.apache.xerces.readers.XMLEntityHandler
     * @param entityContext the XMLEntityHandler.CONTEXT_* type for where
     *        the entity reference appears
     * @see org.apache.xerces.readers.XMLEntityHandler
     * @exception java.lang.Exception
     */
    public abstract void endEntityReference(int entityName, int entityType, int entityContext) throws Exception;

    /**
     * callback for start of CDATA section.
     * this callback marks the start of a CDATA section
     *
     * @exception java.lang.Exception
     */
    public abstract void startCDATA() throws Exception;

    /**
     * callback for end of CDATA section.
     * this callback marks the end of a CDATA section
     *
     * @exception java.lang.Exception
     */
    public abstract void endCDATA() throws Exception;

    /**
     * callback for processing instruction.
     *
     * @param target string pool index of the PI target
     * @param data string pool index of the PI data
     * @exception java.lang.Exception
     */
    public abstract void processingInstruction(int target, int data) throws Exception;

    /**
     * callback for comment.
     *
     * @param comment string pool index of the comment text
     * @exception java.lang.Exception
     */
    public abstract void comment(int comment) throws Exception;

    /**
     * callback for characters (string pool form).
     *
     * @param data string pool index of the characters that were scanned
     * @exception java.lang.Exception
     */
    public abstract void characters(int data) throws Exception;

    /**
     * callback for characters.
     *
     * @param ch character array containing the characters that were scanned
     * @param start offset in ch where scanned characters begin
     * @param length length of scanned characters in ch
     * @exception java.lang.Exception
     */
    public abstract void characters(char ch[], int start, int length) throws Exception;

    /**
     * callback for ignorable whitespace.
     *
     * @param data string pool index of ignorable whitespace
     * @exception java.lang.Exception
     */
    public abstract void ignorableWhitespace(int data) throws Exception;

    /**
     * callback for ignorable whitespace.
     *
     * @param ch character array containing the whitespace that was scanned
     * @param start offset in ch where scanned whitespace begins
     * @param length length of scanned whitespace in ch
     * @exception java.lang.Exception
     */
    public abstract void ignorableWhitespace(char ch[], int start, int length) throws Exception;

    // DTD callbacks

    /**
     * callback for the start of the DTD
     * This function will be called when a &lt;!DOCTYPE...&gt; declaration is
     * encountered.
     *
     * @param rootElementType element handle for the root element of the document
     * @param publicId string pool index of the DTD's public ID
     * @param systemId string pool index of the DTD's system ID
     * @exception java.lang.Exception
     */
    public abstract void startDTD(int rootElementType, int publicId, int systemId) throws Exception;

    /**
     * callback for the end of the DTD
     * This function will be called at the end of the DTD.
     */
    public abstract void endDTD() throws Exception;

    /**
     * callback for an element declaration.
     *
     * @param elementType element handle of the element being declared
     * @param contentSpec contentSpec for the element being declared
     * @see XMLValidator.ContentSpec
     * @exception java.lang.Exception
     */
    public abstract void elementDecl(int elementType, XMLValidator.ContentSpec contentSpec) throws Exception;

    /**
     * callback for an attribute list declaration.
     *
     * @param elementType element handle for the attribute's element
     * @param attrName string pool index of the attribute name
     * @param attType type of attribute
     * @param enumString String representing the values of the enumeration,
     *        if the attribute is of enumerated type, or null if it is not.
     * @param attDefaultType an integer value denoting the DefaultDecl value
     * @param attDefaultValue string pool index of this attribute's default value
     *        or -1 if there is no defaultvalue
     * @exception java.lang.Exception
     */
    public abstract void attlistDecl(int elementType,
                                     int attrName, int attType,
                                     String enumString,
                                     int attDefaultType,
                                     int attDefaultValue) throws Exception;

    /**
     * callback for an internal parameter entity declaration.
     *
     * @param entityName string pool index of the entity name
     * @param entityValue string pool index of the entity replacement text
     * @exception java.lang.Exception
     */
    public abstract void internalPEDecl(int entityName, int entityValue) throws Exception;

    /**
     * callback for an external parameter entity declaration.
     *
     * @param entityName string pool index of the entity name
     * @param publicId string pool index of the entity's public id.
     * @param systemId string pool index of the entity's system id.
     * @exception java.lang.Exception
     */
    public abstract void externalPEDecl(int entityName, int publicId, int systemId) throws Exception;

    /**
     * callback for internal general entity declaration.
     *
     * @param entityName string pool index of the entity name
     * @param entityValue string pool index of the entity replacement text
     * @exception java.lang.Exception
     */
    public abstract void internalEntityDecl(int entityName, int entityValue) throws Exception;

    /**
     * callback for external general entity declaration.
     *
     * @param entityName string pool index of the entity name
     * @param publicId string pool index of the entity's public id.
     * @param systemId string pool index of the entity's system id.
     * @exception java.lang.Exception
     */
    public abstract void externalEntityDecl(int entityName, int publicId, int systemId) throws Exception;

    /**
     * callback for an unparsed entity declaration.
     *
     * @param entityName string pool index of the entity name
     * @param publicId string pool index of the entity's public id.
     * @param systemId string pool index of the entity's system id.
     * @param notationName string pool index of the notation name.
     * @exception java.lang.Exception
     */
    public abstract void unparsedEntityDecl(int entityName, int publicId, int systemId,
                                            int notationName) throws Exception;

    /**
     * callback for a notation declaration.
     *
     * @param notationName string pool index of the notation name
     * @param publicId string pool index of the notation's public id.
     * @param systemId string pool index of the notation's system id.
     * @exception java.lang.Exception
     */
    public abstract void notationDecl(int notationName, int publicId, int systemId) throws Exception;

    //
    // Protected methods
    //

    // SAX2 core features

    /**
     * Sets whether the parser validates.
     * <p>
     * This method is the equivalent to the feature:
     * <pre>
     * http://xml.org/sax/features/validation
     * </pre>
     *
     * @param validate True to validate; false to not validate.
     *
     * @see #getValidation
     * @see #setFeature
     */
    protected void setValidation(boolean validate) 
        throws SAXNotRecognizedException, SAXNotSupportedException {
        if (fParseInProgress) {
            throw new SAXNotSupportedException("PAR004 Cannot setFeature(http://xml.org/sax/features/validation): parse is in progress.\n"+
                                               "http://xml.org/sax/features/validation");
        }
        try {
            fDTDValidator.setValidationEnabled(validate);
            getSchemaValidator().setValidationEnabled(validate);
        }
        catch (Exception ex) {
            throw new SAXNotSupportedException(ex.getMessage());
        }
    }

    /**
     * Returns true if validation is turned on.
     *
     * @see #setValidation
     */
    protected boolean getValidation() 
        throws SAXNotRecognizedException, SAXNotSupportedException {
        return fDTDValidator.getValidationEnabled();
    }

    /**
     * <b>Note: Currently, this parser always expands external general
     * entities.</b> Setting this feature to false will throw a
     * SAXNotSupportedException.
     * <p>
     * Sets whether external general entities are expanded.
     * <p>
     * This method is the equivalent to the feature:
     * <pre>
     * http://xml.org/sax/features/external-general-entities
     * </pre>
     *
     * @param expand True to expand external general entities; false
     *               to not expand.
     *
     * @see #getExternalGeneralEntities
     * @see #setFeature
     */
    protected void setExternalGeneralEntities(boolean expand)
        throws SAXNotRecognizedException, SAXNotSupportedException {
        if (fParseInProgress) {
            throw new SAXNotSupportedException("PAR004 Cannot setFeature(http://xml.org/sax/features/external-general-entities): parse is in progress.\n"+
                                               "http://xml.org/sax/features/external-general-entities");
        }
        if (!expand) {
            throw new SAXNotSupportedException("http://xml.org/sax/features/external-general-entities");
        }
    }

    /**
     * <b>Note: This feature is always true.</b>
     * <p>
     * Returns true if external general entities are expanded.
     *
     * @see #setExternalGeneralEntities
     */
    protected boolean getExternalGeneralEntities() 
        throws SAXNotRecognizedException, SAXNotSupportedException {
        return true;
    }

    /**
     * <b>Note: Currently, this parser always expands external parameter
     * entities.</b> Setting this feature to false will throw a
     * SAXNotSupportedException.
     * <p>
     * Sets whether external parameter entities are expanded.
     * <p>
     * This method is the equivalent to the feature:
     * <pre>
     * http://xml.org/sax/features/external-parameter-entities
     * </pre>
     *
     * @param expand True to expand external parameter entities; false
     *               to not expand.
     *
     * @see #getExternalParameterEntities
     * @see #setFeature
     */
    protected void setExternalParameterEntities(boolean expand)
        throws SAXNotRecognizedException, SAXNotSupportedException {
        if (fParseInProgress) {
            throw new SAXNotSupportedException("PAR004 Cannot setFeature(http://xml.org/sax/features/external-general-entities): parse is in progress.\n"+
                                               "http://xml.org/sax/features/external-general-entities");
        }
        if (!expand) {
            throw new SAXNotSupportedException("http://xml.org/sax/features/external-parameter-entities");
        }
    }

    /**
     * <b>Note: This feature is always true.</b>
     * <p>
     * Returns true if external parameter entities are expanded.
     *
     * @see #setExternalParameterEntities
     */
    protected boolean getExternalParameterEntities() 
        throws SAXNotRecognizedException, SAXNotSupportedException {
        return true;
    }

    /**
     * Sets whether the parser preprocesses namespaces.
     * <p>
     * This method is the equivalent to the feature:
     * <pre>
     * http://xml.org/sax/features/namespaces
     * </pre>
     *
     * @param process True to process namespaces; false to not process.
     *
     * @see #getNamespaces
     * @see #setFeature
     */
    protected void setNamespaces(boolean process) 
        throws SAXNotRecognizedException, SAXNotSupportedException {
        if (fParseInProgress) {
            throw new SAXNotSupportedException("PAR004 Cannot setFeature(http://xml.org/sax/features/namespaces): parse is in progress.\n"+
                                               "http://xml.org/sax/features/namespaces");
        }
        fNamespacesEnabled = process;
        fDTDValidator.setNamespacesEnabled(process);
        getSchemaValidator().setNamespacesEnabled(process);
    }

    /**
     * Returns true if the parser preprocesses namespaces.
     *
     * @see #setNamespaces
     */
    protected boolean getNamespaces() 
        throws SAXNotRecognizedException, SAXNotSupportedException {
        return fNamespacesEnabled;
    }

    // Xerces features

    /**
     * Allows the parser to validate a document only when it contains a
     * grammar. Validation is turned on/off based on each document
     * instance, automatically.
     * <p>
     * This method is the equivalent to the feature:
     * <pre>
     * http://apache.org/xml/features/validation/dynamic
     * </pre>
     *
     * @param dynamic True to dynamically validate documents; false to
     *                validate based on the validation feature.
     *
     * @see #getValidationDynamic
     * @see #setFeature
     */
    protected void setValidationDynamic(boolean dynamic) 
        throws SAXNotRecognizedException, SAXNotSupportedException {
        if (fParseInProgress) {
            // REVISIT: Localize this message. -Ac
            throw new SAXNotSupportedException("http://apache.org/xml/features/validation/dynamic: parse is in progress");
        }
        try {
            fDTDValidator.setDynamicValidationEnabled(dynamic);
            getSchemaValidator().setDynamicValidationEnabled(dynamic);
        }
        catch (Exception ex) {
            throw new SAXNotSupportedException(ex.getMessage());
        }
    }

    /**
     * Returns true if validation is based on whether a document
     * contains a grammar.
     *
     * @see #setValidationDynamic
     */
    protected boolean getValidationDynamic() 
        throws SAXNotRecognizedException, SAXNotSupportedException {
        return fDTDValidator.getDynamicValidationEnabled();
    }

    /**
     * Sets whether an error is emitted when an attribute is redefined
     * in the grammar.
     * <p>
     * This method is the equivalent to the feature:
     * <pre>
     * http://apache.org/xml/features/validation/warn-on-duplicate-attdef
     * </pre>
     *
     * @param warn True to warn; false to not warn.
     *
     * @see #getValidationWarnOnDuplicateAttdef
     * @see #setFeature
     */
    protected void setValidationWarnOnDuplicateAttdef(boolean warn)
        throws SAXNotRecognizedException, SAXNotSupportedException {
        fDTDValidator.setWarningOnDuplicateAttDef(warn);
        getSchemaValidator().setWarningOnDuplicateAttDef(warn);
    }

    /**
     * Returns true if an error is emitted when an attribute is redefined
     * in the grammar.
     *
     * @see #setValidationWarnOnDuplicateAttdef
     */
    protected boolean getValidationWarnOnDuplicateAttdef()
        throws SAXNotRecognizedException, SAXNotSupportedException {
        return fDTDValidator.getWarningOnDuplicateAttDef();
    }

    /**
     * Sets whether the parser emits an error when an element's content
     * model references an element by name that is not declared in the
     * grammar.
     * <p>
     * This method is the equivalent to the feature:
     * <pre>
     * http://apache.org/xml/features/validation/warn-on-undeclared-elemdef
     * </pre>
     *
     * @param warn True to warn; false to not warn.
     *
     * @see #getValidationWarnOnUndeclaredElemdef
     * @see #setFeature
     */
    protected void setValidationWarnOnUndeclaredElemdef(boolean warn)
        throws SAXNotRecognizedException, SAXNotSupportedException {
        fDTDValidator.setWarningOnUndeclaredElements(warn);
        getSchemaValidator().setWarningOnUndeclaredElements(warn);
    }

    /**
     * Returns true if the parser emits an error when an undeclared
     * element is referenced in the grammar.
     *
     * @see #setValidationWarnOnUndeclaredElemdef
     */
    protected boolean getValidationWarnOnUndeclaredElemdef()
        throws SAXNotRecognizedException, SAXNotSupportedException {
        return fDTDValidator.getWarningOnUndeclaredElements();
    }

    /**
     * Allows the use of Java encoding names in the XMLDecl and TextDecl
     * lines in an XML document.
     * <p>
     * This method is the equivalent to the feature:
     * <pre>
     * http://apache.org/xml/features/allow-java-encodings
     * </pre>
     *
     * @param allow True to allow Java encoding names; false to disallow.
     *
     * @see #getAllowJavaEncodings
     * @see #setFeature
     */
    protected void setAllowJavaEncodings(boolean allow) 
        throws SAXNotRecognizedException, SAXNotSupportedException {
        fReaderFactory.setAllowJavaEncodingName(allow);
    }

    /**
     * Returns true if Java encoding names are allowed in the XML document.
     *
     * @see #setAllowJavaEncodings
     */
    protected boolean getAllowJavaEncodings() 
        throws SAXNotRecognizedException, SAXNotSupportedException {
        return fReaderFactory.getAllowJavaEncodingName();
    }

    /**
     * Allows the parser to continue after a fatal error. Normally, a
     * fatal error would stop the parse.
     * <p>
     * This method is the equivalent to the feature:
     * <pre>
     * http://apache.org/xml/features/continue-after-fatal-error
     * </pre>
     *
     * @param continueAfterFatalError True to continue; false to stop on
     *                                fatal error.
     *
     * @see #getContinueAfterFatalError
     * @see #setFeature
     */
    protected void setContinueAfterFatalError(boolean continueAfterFatalError)
        throws SAXNotRecognizedException, SAXNotSupportedException {
        fContinueAfterFatalError = continueAfterFatalError;
    }

    /**
     * Returns true if the parser continues after a fatal error.
     *
     * @see #setContinueAfterFatalError
     */
    protected boolean getContinueAfterFatalError() 
        throws SAXNotRecognizedException, SAXNotSupportedException {
        return fContinueAfterFatalError;
    }

    // SAX2 core properties

    /**
     * Set the separator to be used between the URI part of a name and the
     * local part of a name when namespace processing is being performed
     * (see the http://xml.org/sax/features/namespaces feature).  By default,
     * the separator is a single space.
     * <p>
     * This property may not be set while a parse is in progress (throws a
     * SAXNotSupportedException).
     * <p>
     * This method is the equivalent to the property:
     * <pre>
     * http://xml.org/sax/properties/namespace-sep
     * </pre>
     *
     * @param separator The new namespace separator.
     *
     * @see #getNamespaceSep
     * @see #setProperty
     */
    /***
    protected void setNamespaceSep(String separator) 
        throws SAXNotRecognizedException, SAXNotSupportedException {
        // REVISIT: Ask someone what it could possibly hurt to allow
        //          the application to change this in mid-parse.
        if (fParseInProgress) {
            // REVISIT: Localize this message.
            throw new SAXNotSupportedException("http://xml.org/sax/properties/namespace-sep: parse is in progress");
        }
        fNamespaceSep = separator;
    }
    /***/

    /**
     * Returns the namespace separator.
     *
     * @see #setNamespaceSep
     */
    /***
    protected String getNamespaceSep() 
        throws SAXNotRecognizedException, SAXNotSupportedException {
        return fNamespaceSep;
    }
    /***/

    /**
     * <b>Note: This property is currently not supported because it is
     * not well defined.</b> Querying its value will throw a
     * SAXNotSupportedException.
     * <p>
     * This method is the equivalent to the property:
     * <pre>
     * http://xml.org/sax/properties/xml-string
     * </pre>
     *
     * @see #getProperty
     */
    /***
    protected String getXMLString() 
        throws SAXNotRecognizedException, SAXNotSupportedException {
        throw new SAXNotSupportedException("http://xml.org/sax/properties/xml-string");
    }
    /***/

    // resetting

    /**
     * Reset or copy parser
     * Allows parser instance reuse
     */
    protected void resetOrCopy() throws Exception {
        fStringPool = new StringPool();
        fAttrList = new XMLAttrList(fStringPool);
        resetCommon();
    } // resetOrCopy()

    private void resetCommon() throws Exception {
        fScanner.reset(fStringPool, new ChunkyCharArray(fStringPool));
        fValidating = false;
        fScanningDTD = false;
        resetEntityHandler();
        fValidator = null;
        fDTDValidator.reset(fStringPool);
        if (fSchemaValidator != null)
            fSchemaValidator.reset(fStringPool, fErrorReporter, fEntityHandler);
        fCheckedForSchema = false;
        fNeedReset = false;
        fCalledStartDocument = false;
        fSeenRootElement = false;
        fStandaloneDocument = false;
        fCDATASymbol = fStringPool.addSymbol("CDATA");
        fXMLLang = -1;
        // REVISIT - add all other instance variables...
        fElementDepth = 0;
        fCurrentElementType = -1;
        fCurrentElementEntity = -1;
        fInElementContent = false;
    }

    // properties

    /** Returns the XML Schema validator. */
    protected XSchemaValidator getSchemaValidator() {
        if (fSchemaValidator == null)
            fSchemaValidator = new XSchemaValidator(fStringPool, fErrorReporter, fEntityHandler);
        return fSchemaValidator;
    }

    /**
     * Set char data processing preference.
     */
    protected void setSendCharDataAsCharArray(boolean flag) {
        fSendCharDataAsCharArray = flag;
        fReaderFactory.setSendCharDataAsCharArray(fSendCharDataAsCharArray);
    }

    //
    // Parser/XMLReader methods
    //
    // NOTE: This class does *not* implement the org.xml.sax.Parser
    //       interface but it does share some common methods. -Ac

    // handlers

    /**
     * Sets the resolver used to resolve external entities. The EntityResolver
     * interface supports resolution of public and system identifiers.
     *
     * @param resolver The new entity resolver. Passing a null value will
     *                 uninstall the currently installed resolver.
     */
    public void setEntityResolver(EntityResolver resolver) {
        fEntityResolver = resolver;
    }

    /**
     * Return the current entity resolver.
     *
     * @return The current entity resolver, or null if none
     *         has been registered.
     * @see #setEntityResolver
     */
    public EntityResolver getEntityResolver() {
        return fEntityResolver;
    }

    /**
     * Sets the error handler.
     *
     * @param handler The new error handler.
     */
    public void setErrorHandler(ErrorHandler handler) {
        fErrorHandler = handler;
    }

    /**
     * Return the current error handler.
     *
     * @return The current error handler, or null if none
     *         has been registered.
     * @see #setErrorHandler
     */
    public ErrorHandler getErrorHandler() {
        return fErrorHandler;
    }

    // parsing

    /**
     * Parses the specified input source.
     *
     * @param source The input source.
     *
     * @exception org.xml.sax.SAXException Throws exception on SAX error.
     * @exception java.io.IOException Throws exception on i/o error.
     */
    public void parse(InputSource source)
        throws SAXException, IOException {

        if (fParseInProgress) {
            throw new org.xml.sax.SAXException("FWK005 parse may not be called while parsing."); // REVISIT - need to add new error message
        }

        try {
            if (parseSomeSetup(source)) {
                fScanner.parseSome(true);
            }
            fParseInProgress = false;
        } catch (org.xml.sax.SAXException ex) {
            fParseInProgress = false;
            if (PRINT_EXCEPTION_STACK_TRACE)
                ex.printStackTrace();
            throw ex;
        } catch (IOException ex) {
            fParseInProgress = false;
            if (PRINT_EXCEPTION_STACK_TRACE)
                ex.printStackTrace();
            throw ex;
        } catch (Exception ex) {
            fParseInProgress = false;
            if (PRINT_EXCEPTION_STACK_TRACE)
                ex.printStackTrace();
            throw new org.xml.sax.SAXException(ex);
        }

    } // parse(InputSource)

    /**
     * Parses the input source specified by the given system identifier.
     * <p>
     * This method is equivalent to the following:
     * <pre>
     *     parse(new InputSource(systemId));
     * </pre>
     *
     * @param source The input source.
     *
     * @exception org.xml.sax.SAXException Throws exception on SAX error.
     * @exception java.io.IOException Throws exception on i/o error.
     */
    public void parse(String systemId)
        throws SAXException, IOException {

        InputSource source = new InputSource(systemId);
        parse(source);
        try {
            Reader reader = source.getCharacterStream();
            if (reader != null) {
                reader.close();
            }
            else {
                InputStream is = source.getByteStream();
                if (is != null) {
                    is.close();
                }
            }
        }
        catch (IOException e) {
            // ignore
        }

    } // parse(String)

    // locale

    /**
     * Set the locale to use for messages.
     *
     * @param locale The locale object to use for localization of messages.
     *
     * @exception SAXException An exception thrown if the parser does not
     *                         support the specified locale.
     *
     * @see org.xml.sax.Parser
     */
    public void setLocale(Locale locale) throws SAXException {

        if (fParseInProgress) {
            throw new org.xml.sax.SAXException("FWK006 setLocale may not be called while parsing"); // REVISIT - need to add new error message
        }

        fLocale = locale;
        fgXMLMessages.setLocale(locale);
        fgImplementationMessages.setLocale(locale);

    } // setLocale(Locale)

    // resolver

    //
    // XMLErrorReporter methods
    //

    /**
     * Report an error.
     *
     * @param locator Location of error.
     * @param errorDomain The error domain.
     * @param majorCode The major code of the error.
     * @param minorCode The minor code of the error.
     * @param args Arguments for replacement text.
     * @param errorType The type of the error.
     *
     * @exception Exception Thrown on error.
     *
     * @see XMLErrorReporter#ERRORTYPE_WARNING
     * @see XMLErrorReporter#ERRORTYPE_FATAL_ERROR
     */
    public void reportError(Locator locator, String errorDomain,
                            int majorCode, int minorCode, Object args[],
                            int errorType) throws Exception {

        // create the appropriate message
        SAXParseException spe;
        if (errorDomain.equals(XMLMessages.XML_DOMAIN)) {
            spe = new SAXParseException(fgXMLMessages.createMessage(fLocale, majorCode, minorCode, args), locator);
        }
        else if (errorDomain.equals(XMLMessages.XMLNS_DOMAIN)) {
            spe = new SAXParseException(fgXMLMessages.createMessage(fLocale, majorCode, minorCode, args), locator);
        }
        else if (errorDomain.equals(ImplementationMessages.XERCES_IMPLEMENTATION_DOMAIN)) {
            spe = new SAXParseException(fgImplementationMessages.createMessage(fLocale, majorCode, minorCode, args), locator);
        } else if (errorDomain.equals(SchemaMessageProvider.SCHEMA_DOMAIN)) {
            spe = new SAXParseException(fgSchemaMessages.createMessage(fLocale, majorCode, minorCode, args), locator);
        } else if (errorDomain.equals(DatatypeMessageProvider.DATATYPE_DOMAIN)) {
            spe = new SAXParseException(fgDatatypeMessages.createMessage(fLocale, majorCode, minorCode, args), locator);
        } else {
            throw new RuntimeException("FWK007 Unknown error domain \"" + errorDomain + "\"."+"\n"+errorDomain);
        }

        // default error handling
        if (fErrorHandler == null) {
            if (errorType == XMLErrorReporter.ERRORTYPE_FATAL_ERROR &&
                !fContinueAfterFatalError) {
                throw spe;
            }
            return;
        }

        // make appropriate callback
        if (errorType == XMLErrorReporter.ERRORTYPE_WARNING) {
            fErrorHandler.warning(spe);
        }
        else if (errorType == XMLErrorReporter.ERRORTYPE_FATAL_ERROR) {
            fErrorHandler.fatalError(spe);
            if (!fContinueAfterFatalError) {
                Object[] fatalArgs = { spe.getMessage() };
                throw new SAXException(fgImplementationMessages.createMessage(fLocale, ImplementationMessages.FATAL_ERROR, 0, fatalArgs));
            }
        }
        else {
            fErrorHandler.error(spe);
        }

    } // reportError(Locator,String,int,int,Object[],int)

    //
    // Configurable methods
    //
    // This interface is no longer a part of SAX2. These methods have
    // been added directly to the new XMLReader interface. In addition,
    // the throws clause has changed from throws SAXException to throws
    // SAXNotRecognizedException, SAXNotSupportedException
    //

    /**
     * Set the state of a feature.
     *
     * Set the state of any feature in a SAX2 parser.  The parser
     * might not recognize the feature, and if it does recognize
     * it, it might not be able to fulfill the request.
     *
     * @param featureId The unique identifier (URI) of the feature.
     * @param state The requested state of the feature (true or false).
     *
     * @exception org.xml.sax.SAXNotRecognizedException If the
     *            requested feature is not known.
     * @exception org.xml.sax.SAXNotSupportedException If the
     *            requested feature is known, but the requested
     *            state is not supported.
     * @exception org.xml.sax.SAXException If there is any other
     *            problem fulfilling the request.
     */
    public void setFeature(String featureId, boolean state)
        throws SAXNotRecognizedException, SAXNotSupportedException {

        //
        // SAX2 Features
        //

        if (featureId.startsWith(SAX2_FEATURES_PREFIX)) {
            String feature = featureId.substring(SAX2_FEATURES_PREFIX.length());
            //
            // http://xml.org/sax/features/validation
            //   Validate (true) or don't validate (false).
            //
            if (feature.equals("validation")) {
                setValidation(state);
                return;
            }
            //
            // http://xml.org/sax/features/external-general-entities
            //   Expand external general entities (true) or don't expand (false).
            //
            if (feature.equals("external-general-entities")) {
                setExternalGeneralEntities(state);
                return;
            }
            //
            // http://xml.org/sax/features/external-parameter-entities
            //   Expand external parameter entities (true) or don't expand (false).
            //
            if (feature.equals("external-parameter-entities")) {
                setExternalParameterEntities(state);
                return;
            }
            //
            // http://xml.org/sax/features/namespaces
            //   Preprocess namespaces (true) or don't preprocess (false).  See also
            //   the http://xml.org/sax/properties/namespace-sep property.
            //
            if (feature.equals("namespaces")) {
                setNamespaces(state);
                return;
            }
            //
            // Not recognized
            //
        }

        //
        // Xerces Features
        //

        else if (featureId.startsWith(XERCES_FEATURES_PREFIX)) {
            String feature = featureId.substring(XERCES_FEATURES_PREFIX.length());
            //
            // http://apache.org/xml/features/validation/dynamic
            //   Allows the parser to validate a document only when it
            //   contains a grammar. Validation is turned on/off based
            //   on each document instance, automatically.
            //
            if (feature.equals("validation/dynamic")) {
                setValidationDynamic(state);
                return;
            }
            //
            // http://apache.org/xml/features/validation/default-attribute-values
            //
            if (feature.equals("validation/default-attribute-values")) {
                // REVISIT
                throw new SAXNotSupportedException(featureId);
            }
            //
            // http://apache.org/xml/features/validation/default-attribute-values
            //
            if (feature.equals("validation/validate-content-models")) {
                // REVISIT
                throw new SAXNotSupportedException(featureId);
            }
            //
            // http://apache.org/xml/features/validation/default-attribute-values
            //
            if (feature.equals("validation/validate-datatypes")) {
                // REVISIT
                throw new SAXNotSupportedException(featureId);
            }
            //
            // http://apache.org/xml/features/validation/warn-on-duplicate-attdef
            //   Emits an error when an attribute is redefined.
            //
            if (feature.equals("validation/warn-on-duplicate-attdef")) {
                setValidationWarnOnDuplicateAttdef(state);
                return;
            }
            //
            // http://apache.org/xml/features/validation/warn-on-undeclared-elemdef
            //   Emits an error when an element's content model
            //   references an element, by name, that is not declared
            //   in the grammar.
            //
            if (feature.equals("validation/warn-on-undeclared-elemdef")) {
                setValidationWarnOnUndeclaredElemdef(state);
                return;
            }
            //
            // http://apache.org/xml/features/allow-java-encodings
            //   Allows the use of Java encoding names in the XML
            //   and TextDecl lines.
            //
            if (feature.equals("allow-java-encodings")) {
                setAllowJavaEncodings(state);
                return;
            }
            //
            // http://apache.org/xml/features/continue-after-fatal-error
            //   Allows the parser to continue after a fatal error.
            //   Normally, a fatal error would stop the parse.
            //
            if (feature.equals("continue-after-fatal-error")) {
                setContinueAfterFatalError(state);
                return;
            }
            //
            // Not recognized
            //
        }

        //
        // Not recognized
        //

        throw new SAXNotRecognizedException(featureId);

    } // setFeature(String,boolean)

    /**
     * Query the state of a feature.
     *
     * Query the current state of any feature in a SAX2 parser.  The
     * parser might not recognize the feature.
     *
     * @param featureId The unique identifier (URI) of the feature
     *                  being set.
     * @return The current state of the feature.
     * @exception org.xml.sax.SAXNotRecognizedException If the
     *            requested feature is not known.
     * @exception org.xml.sax.SAXException If there is any other
     *            problem fulfilling the request.
     */
    public boolean getFeature(String featureId) 
        throws SAXNotRecognizedException, SAXNotSupportedException {

        //
        // SAX2 Features
        //

        if (featureId.startsWith(SAX2_FEATURES_PREFIX)) {
            String feature = featureId.substring(SAX2_FEATURES_PREFIX.length());
            //
            // http://xml.org/sax/features/validation
            //   Validate (true) or don't validate (false).
            //
            if (feature.equals("validation")) {
                return getValidation();
            }
            //
            // http://xml.org/sax/features/external-general-entities
            //   Expand external general entities (true) or don't expand (false).
            //
            if (feature.equals("external-general-entities")) {
                return getExternalGeneralEntities();
            }
            //
            // http://xml.org/sax/features/external-parameter-entities
            //   Expand external parameter entities (true) or don't expand (false).
            //
            if (feature.equals("external-parameter-entities")) {
                return getExternalParameterEntities();
            }
            //
            // http://xml.org/sax/features/namespaces
            //   Preprocess namespaces (true) or don't preprocess (false).  See also
            //   the http://xml.org/sax/properties/namespace-sep property.
            //
            if (feature.equals("namespaces")) {
                return getNamespaces();
            }
            //
            // Not recognized
            //
        }

        //
        // Xerces Features
        //

        else if (featureId.startsWith(XERCES_FEATURES_PREFIX)) {
            String feature = featureId.substring(XERCES_FEATURES_PREFIX.length());
            //
            // http://apache.org/xml/features/validation/dynamic
            //   Allows the parser to validate a document only when it
            //   contains a grammar. Validation is turned on/off based
            //   on each document instance, automatically.
            //
            if (feature.equals("validation/dynamic")) {
                return getValidationDynamic();
            }
            //
            // http://apache.org/xml/features/validation/default-attribute-values
            //
            if (feature.equals("validation/default-attribute-values")) {
                // REVISIT
                throw new SAXNotRecognizedException(featureId);
            }
            //
            // http://apache.org/xml/features/validation/validate-content-models
            //
            if (feature.equals("validation/validate-content-models")) {
                // REVISIT
                throw new SAXNotRecognizedException(featureId);
            }
            //
            // http://apache.org/xml/features/validation/validate-datatypes
            //
            if (feature.equals("validation/validate-datatypes")) {
                // REVISIT
                throw new SAXNotRecognizedException(featureId);
            }
            //
            // http://apache.org/xml/features/validation/warn-on-duplicate-attdef
            //   Emits an error when an attribute is redefined.
            //
            if (feature.equals("validation/warn-on-duplicate-attdef")) {
                return getValidationWarnOnDuplicateAttdef();
            }
            //
            // http://apache.org/xml/features/validation/warn-on-undeclared-elemdef
            //   Emits an error when an element's content model
            //   references an element, by name, that is not declared
            //   in the grammar.
            //
            if (feature.equals("validation/warn-on-undeclared-elemdef")) {
                return getValidationWarnOnUndeclaredElemdef();
            }
            //
            // http://apache.org/xml/features/allow-java-encodings
            //   Allows the use of Java encoding names in the XML
            //   and TextDecl lines.
            //
            if (feature.equals("allow-java-encodings")) {
                return getAllowJavaEncodings();
            }
            //
            // http://apache.org/xml/features/continue-after-fatal-error
            //   Allows the parser to continue after a fatal error.
            //   Normally, a fatal error would stop the parse.
            //
            if (feature.equals("continue-after-fatal-error")) {
                return getContinueAfterFatalError();
            }
            //
            // Not recognized
            //
        }

        //
        // Not recognized
        //

        throw new SAXNotRecognizedException(featureId);

    } // getFeature(String):boolean

    /**
     * Set the value of a property.
     *
     * Set the value of any property in a SAX2 parser.  The parser
     * might not recognize the property, and if it does recognize
     * it, it might not support the requested value.
     *
     * @param propertyId The unique identifier (URI) of the property
     *                   being set.
     * @param Object The value to which the property is being set.
     * @exception org.xml.sax.SAXNotRecognizedException If the
     *            requested property is not known.
     * @exception org.xml.sax.SAXNotSupportedException If the
     *            requested property is known, but the requested
     *            value is not supported.
     * @exception org.xml.sax.SAXException If there is any other
     *            problem fulfilling the request.
     */
    public void setProperty(String propertyId, Object value)
        throws SAXNotRecognizedException, SAXNotSupportedException {

        //
        // SAX2 Properties
        //

        if (propertyId.startsWith(SAX2_PROPERTIES_PREFIX)) {
            String property = propertyId.substring(SAX2_PROPERTIES_PREFIX.length());
            //
            // http://xml.org/sax/properties/namespace-sep
            // Value type: String
            // Access: read/write, pre-parse only
            //   Set the separator to be used between the URI part of a name and the
            //   local part of a name when namespace processing is being performed
            //   (see the http://xml.org/sax/features/namespaces feature).  By
            //   default, the separator is a single space.  This property may not be
            //   set while a parse is in progress (throws a SAXNotSupportedException).
            //
            /***
            if (property.equals("namespace-sep")) {
                try {
                    setNamespaceSep((String)value);
                }
                catch (ClassCastException e) {
                    throw new SAXNotSupportedException(propertyId);
                }
                return;
            }
            /***/
            
            //
            // http://xml.org/sax/properties/xml-string
            // Value type: String
            // Access: read-only
            //   Get the literal string of characters associated with the current
            //   event.  If the parser recognises and supports this property but is
            //   not currently parsing text, it should return null (this is a good
            //   way to check for availability before the parse begins).
            //
            if (property.equals("xml-string")) {
                // REVISIT - we should probably ask xml-dev for a precise definition
                // of what this is actually supposed to return, and in exactly which
                // circumstances.
                throw new SAXNotSupportedException(propertyId);
            }
            //
            // Not recognized
            //
        }

        //
        // SAX2 Handlers
        //

        /*
        else if (propertyId.startsWith(SAX2_HANDLERS_PREFIX)) {
            //
            // No handlers defined yet that are common to all parsers.
            //
        }
        */

        //
        // Xerces Properties
        //

        /*
        else if (propertyId.startsWith(XERCES_PROPERTIES_PREFIX)) {
            //
            // No properties defined yet that are common to all parsers.
            //
        }
        */

        //
        // Not recognized
        //

        throw new SAXNotRecognizedException(propertyId);

    } // setProperty(String,Object)

    /**
     * Query the value of a property.
     *
     * Return the current value of a property in a SAX2 parser.
     * The parser might not recognize the property.
     *
     * @param propertyId The unique identifier (URI) of the property
     *                   being set.
     * @return The current value of the property.
     * @exception org.xml.sax.SAXNotRecognizedException If the
     *            requested property is not known.
     * @exception org.xml.sax.SAXException If there is any other
     *            problem fulfilling the request.
     * @see org.xml.sax.Configurable#getProperty
     */
    public Object getProperty(String propertyId) 
        throws SAXNotRecognizedException, SAXNotSupportedException {

        //
        // SAX2 Properties
        //

        if (propertyId.startsWith(SAX2_PROPERTIES_PREFIX)) {
            String property = propertyId.substring(SAX2_PROPERTIES_PREFIX.length());
            //
            // http://xml.org/sax/properties/namespace-sep
            // Value type: String
            // Access: read/write, pre-parse only
            //   Set the separator to be used between the URI part of a name and the
            //   local part of a name when namespace processing is being performed
            //   (see the http://xml.org/sax/features/namespaces feature).  By
            //   default, the separator is a single space.  This property may not be
            //   set while a parse is in progress (throws a SAXNotSupportedException).
            //
            /***
            if (property.equals("namespace-sep")) {
                return getNamespaceSep();
            }
            /***/
            //
            // http://xml.org/sax/properties/xml-string
            // Value type: String
            // Access: read-only
            //   Get the literal string of characters associated with the current
            //   event.  If the parser recognises and supports this property but is
            //   not currently parsing text, it should return null (this is a good
            //   way to check for availability before the parse begins).
            //
            if (property.equals("xml-string")) {
                //return getXMLString();
                throw new SAXNotSupportedException(
                    "PAR019 Property, \"http://xml.org/sax/properties/xml-string\", is not supported.\n"+
                    "http://xml.org/sax/properties/xml-string"
                    );
            }
            //
            // Not recognized
            //
        }

        //
        // SAX2 Handlers
        //

        /*
        else if (propertyId.startsWith(SAX2_HANDLERS_PREFIX)) {
            //
            // No handlers defined yet that are common to all parsers.
            //
        }
        */

        //
        // Xerces Properties
        //

        /*
        else if (propertyId.startsWith(XERCES_PROPERTIES_PREFIX)) {
            //
            // No properties defined yet that are common to all parsers.
            //
        }
        */

        //
        // Not recognized
        //

        throw new SAXNotRecognizedException(propertyId);

    } // getProperty(String):Object

    //
    // XMLDocumentScanner methods
    //

    /**
     * Returns true if the specified version is valid.
     *
     */
    public boolean validVersionNum(String version) {
        return XMLCharacterProperties.validVersionNum(version);
    }

    /**
     * Returns true if the specified encoding is valid.
     *
     */
    public boolean validEncName(String encoding) {
        return XMLCharacterProperties.validEncName(encoding);
    }

    // callbacks

    /**
     * Call the start document callback.
     */
    public void callStartDocument(int version, int encoding, int standalone) throws Exception {
        if (!fCalledStartDocument) {
            startDocument(version, encoding, standalone);
            fCalledStartDocument = true;
        }
    }

    /**
     * Call the end document callback.
     */
    public void callEndDocument() throws Exception {
        if (fCalledStartDocument)
            endDocument();
    }

    /** Call the start element callback. */
    public void callStartElement(int elementType) throws Exception {

        //
        // Check after all specified attrs are scanned
        // (1) report error for REQUIRED attrs that are missing (V_TAGc)
        // (2) add default attrs (FIXED and NOT_FIXED)
        //
        if (!fSeenRootElement) {
            fSeenRootElement = true;
            if (fValidator == null) {
                fValidator = fDTDValidator;
            }
            fValidator.rootElementSpecified(elementType);
            fStringPool.resetShuffleCount();
        }
        fInElementContent = fValidator.startElement(elementType, fAttrList);
        int attrListHandle = fAttrList.attrListHandle();
        if (attrListHandle != -1) {
            fAttrList.endAttrList();
            // REVISIT - we should check for this more efficiently...
            if (fXMLLang == -1)
                fXMLLang = fStringPool.addSymbol("xml:lang");
            int index = fAttrList.getFirstAttr(attrListHandle);
            while (index != -1) {
                if (fStringPool.equalNames(fAttrList.getAttrName(index), fXMLLang)) {
                    fScanner.checkXMLLangAttributeValue(fAttrList.getAttValue(index));
                    break;
                }
                index = fAttrList.getNextAttr(index);
            }
        }
        startElement(elementType, fAttrList, attrListHandle);
        int elementEntity = fEntityHandler.getReaderId();
        if (fElementDepth == fElementTypeStack.length) {
            int[] newStack = new int[fElementDepth * 2];
            System.arraycopy(fElementTypeStack, 0, newStack, 0, fElementDepth);
            fElementTypeStack = newStack;
            newStack = new int[fElementDepth * 2];
            System.arraycopy(fElementEntityStack, 0, newStack, 0, fElementDepth);
            fElementEntityStack = newStack;
        }
        fCurrentElementType = elementType;
        fCurrentElementEntity = elementEntity;
        fElementTypeStack[fElementDepth] = elementType;
        fElementEntityStack[fElementDepth] = elementEntity;
        fElementDepth++;
    } // callStartElement(int)

    /** Call the end element callback. */
    public boolean callEndElement(int readerId) throws Exception {
        int elementType = fCurrentElementType;
        if (fCurrentElementEntity != readerId) {
            fErrorReporter.reportError(fErrorReporter.getLocator(),
                                       XMLMessages.XML_DOMAIN,
                                       XMLMessages.MSG_ELEMENT_ENTITY_MISMATCH,
                                       XMLMessages.P78_NOT_WELLFORMED,
                                       new Object[] { fStringPool.toString(elementType) },
                                       XMLErrorReporter.ERRORTYPE_FATAL_ERROR);
        }
        endElement(elementType);
        fInElementContent = fValidator.endElement(elementType);
        if (fElementDepth-- == 0) {
            throw new RuntimeException("FWK008 Element stack underflow");
        }
        if (fElementDepth == 0) {
            fCurrentElementType = - 1;
            fCurrentElementEntity = -1;
            return true;
        }
        fCurrentElementType = fElementTypeStack[fElementDepth - 1];
        fCurrentElementEntity = fElementEntityStack[fElementDepth - 1];
        return false;
    }

    /** Call the processing instruction callback. */
    public void callProcessingInstruction(int target, int data)
        throws Exception {
        processingInstruction(target, data);
    }

    /** Call the comment callback. */
    public void callComment(int comment) throws Exception {
        comment(comment);
    }

    /** Call the characters callback. */
    public void callCharacters(int ch) throws Exception {
        if (fCharRefData == null)
            fCharRefData = new char[2];
        int count = (ch < 0x10000) ? 1 : 2;
        if (count == 1)
            fCharRefData[0] = (char)ch;
        else {
            fCharRefData[0] = (char)(((ch-0x00010000)>>10)+0xd800);
            fCharRefData[1] = (char)(((ch-0x00010000)&0x3ff)+0xdc00);
        }
        if (fSendCharDataAsCharArray) {
            if (!fInElementContent)
                fValidator.characters(fCharRefData, 0, count);
            characters(fCharRefData, 0, count);
        }
        else {
            int index = fStringPool.addString(new String(fCharRefData, 0, count));
            if (!fInElementContent)
                fValidator.characters(index);
            characters(index);
        }
    }

    // scanning

    /**
     * Scan an attribute value.
     *
     * @param elementType
     * @param attrName
     * @return XMLDocumentScanner.RESULT_SUCCESS if the attribute was created,
     *         XMLDocumentScanner.RESULT_NOT_WELL_FORMED if the scan failed, or
     *         XMLDocumentScanner.RESULT_DUPLICATE_ATTR if the attribute is a duplicate.
     * @exception java.lang.Exception
     */
    public int scanAttValue(int elementType, int attrName) throws Exception {

        fAttrNameLocator = getLocatorImpl(fAttrNameLocator);
        int attValue = fScanner.scanAttValue(elementType, attrName, fValidating/* && attType != fCDATASymbol*/);
        if (attValue == -1) {
            return XMLDocumentScanner.RESULT_FAILURE;
        }
        if (!fCheckedForSchema) {
            fCheckedForSchema = true;
            if (getValidation() == true && // default namespacedecl
		attrName == fStringPool.addSymbol("xmlns")) {
                fValidator = getSchemaValidator();
		String fs =
		 fEntityHandler.expandSystemId(fStringPool.toString(attValue));
		InputSource is = fEntityResolver == null ?
		    null : fEntityResolver.resolveEntity(null, fs);
		if (is == null) {
		    is = new InputSource(fs);
						}
                fSchemaValidator.loadSchema(is);
            }
        }
        if (!fValidator.attributeSpecified(elementType, fAttrList, attrName, fAttrNameLocator, attValue)) {
            return XMLDocumentScanner.RESULT_DUPLICATE_ATTR;
        }
        return XMLDocumentScanner.RESULT_SUCCESS;

    }

    /** Scans an element type. */
    public int scanElementType(XMLEntityHandler.EntityReader entityReader, char fastchar) throws Exception {

        if (!fNamespacesEnabled) {
            return entityReader.scanName(fastchar);
        }
        int elementType = entityReader.scanQName(fastchar);
        if (fNamespacesEnabled && entityReader.lookingAtChar(':', false)) {
            fErrorReporter.reportError(fErrorReporter.getLocator(),
                                       XMLMessages.XML_DOMAIN,
                                       XMLMessages.MSG_TWO_COLONS_IN_QNAME,
                                       XMLMessages.P5_INVALID_CHARACTER,
                                       null,
                                       XMLErrorReporter.ERRORTYPE_FATAL_ERROR);
            entityReader.skipPastNmtoken(' ');
        }
        return elementType;
    }

    /** Scans an expected element type. */
    public boolean scanExpectedElementType(XMLEntityHandler.EntityReader entityReader, char fastchar) throws Exception {
        if (fCurrentElementCharArrayRange == null)
            fCurrentElementCharArrayRange = fStringPool.createCharArrayRange();
        fStringPool.getCharArrayRange(fCurrentElementType, fCurrentElementCharArrayRange);
        return entityReader.scanExpectedName(fastchar, fCurrentElementCharArrayRange);
    }

    /** Scans an attribute name. */
    public int scanAttributeName(XMLEntityHandler.EntityReader entityReader, int elementType) throws Exception {

        if (!fSeenRootElement) {
            fSeenRootElement = true;
            if (fValidator == null) {
                fValidator = fDTDValidator;
            }
            fValidator.rootElementSpecified(elementType);
            fStringPool.resetShuffleCount();
        }
        if (!fNamespacesEnabled) {
            return entityReader.scanName('=');
        }
        int attrName = entityReader.scanQName('=');
        if (entityReader.lookingAtChar(':', false)) {
            fErrorReporter.reportError(fErrorReporter.getLocator(),
                                       XMLMessages.XML_DOMAIN,
                                       XMLMessages.MSG_TWO_COLONS_IN_QNAME,
                                       XMLMessages.P5_INVALID_CHARACTER,
                                       null,
                                       XMLErrorReporter.ERRORTYPE_FATAL_ERROR);
            entityReader.skipPastNmtoken(' ');
        }
        return attrName;

    }

    /** Scan doctype decl. */
    public void scanDoctypeDecl(boolean standalone) throws Exception {
        fScanningDTD = true;
        fCheckedForSchema = true;
        fStandaloneDocument = standalone;
        fValidator = fDTDValidator;
        fDTDValidator.scanDoctypeDecl(standalone);
        fScanningDTD = false;
    }

    /**
     * Tell the parser that we are validating
     */
    public void setValidating(boolean flag) throws Exception {
        fValidating = flag;
    }
    //
    //
    //
    private LocatorImpl getLocatorImpl(LocatorImpl fillin) {
        if (fillin == null)
            return new LocatorImpl(this);
        fillin.setPublicId(getPublicId());
        fillin.setSystemId(getSystemId());
        fillin.setLineNumber(getLineNumber());
        fillin.setColumnNumber(getColumnNumber());
        return fillin;
    }

    //
    // XMLEntityHandler methods
    //

    /**
     * Character data.
     */
    public void processCharacters(char[] chars, int offset, int length)
        throws Exception {

        if (fValidating && !fInElementContent)
            fValidator.characters(chars, offset, length);
        characters(chars, offset, length);

    }

    /**
     * Character data.
     */
    public void processCharacters(int data)
        throws Exception {

        if (fValidating && !fInElementContent)
            fValidator.characters(data);
        characters(data);

    }

    /**
     * White space.
     */
    public void processWhitespace(char[] chars, int offset, int length)
        throws Exception {

        if (fInElementContent) {
            if (fStandaloneDocument && fValidating)
                fValidator.ignorableWhitespace(chars, offset, length);
            ignorableWhitespace(chars, offset, length);
        } else {
            if (fValidating && !fInElementContent)
                fValidator.characters(chars, offset, length);
            characters(chars, offset, length);
        }

    }

    /**
     * White space.
     */
    public void processWhitespace(int data) throws Exception {

        if (fInElementContent) {
            if (fStandaloneDocument && fValidating)
                fValidator.ignorableWhitespace(data);
            ignorableWhitespace(data);
        } else {
            if (fValidating && !fInElementContent)
                fValidator.characters(data);
            characters(data);
        }

    }

    //
    // Data
    //
    private class ReaderState {
        XMLEntityHandler.EntityReader reader;
        InputSource source;
        int entityName;
        int entityType;
        int entityContext;
        String publicId;
        String systemId;
        int readerId;
        int depth;
        ReaderState nextReaderState;
    }
    private ReaderState fReaderStateFreeList = null;
    //
    //
    //
    private EntityResolver fEntityResolver = null;
    private byte[] fEntityTypeStack = null;
    private int[] fEntityNameStack = null;
    private int fEntityStackDepth = 0;
    private Stack fReaderStack = new Stack();
    private XMLEntityHandler.EntityReader fReader = null;
    private InputSource fSource = null;
    private int fEntityName = -1;
    private int fEntityType = -1;
    private int fEntityContext = -1;
    private String fPublicId = null;
    private String fSystemId = null;
    private int fReaderId = -1;
    private int fReaderDepth = -1;
    private int fNextReaderId = 0;
    private NullReader fNullReader = null;

    /**
     * Resets the entity handler.
     */
    private void resetEntityHandler() {
        fReaderStack.removeAllElements();
        fEntityStackDepth = 0;
        fReader = null;
        fSource = null;
        fEntityName = -1;
        fEntityType = -1;
        fEntityContext = -1;
        fPublicId = null;
        fSystemId = null;
        fReaderId = -1;
        fReaderDepth = -1;
        fNextReaderId = 0;
    }

    //
    //
    //

    /**
     * get the Entity reader.
     */
    public XMLEntityHandler.EntityReader getEntityReader() {
        return fReader;
    }

    /**
     * Adds a recognizer.
     *
     * @param recognizer The XML recognizer to add.
     */
    public void addRecognizer(XMLDeclRecognizer recognizer) {
        fReaderFactory.addRecognizer(recognizer);
    }

    /**
     * Expands a system id and returns the system id as a URL, if
     * it can be expanded. A return value of null means that the
     * identifier is already expanded. An exception thrown
     * indicates a failure to expand the id.
     *
     * @param systemId The systemId to be expanded.
     *
     * @return Returns the URL object representing the expanded system
     *         identifier. A null value indicates that the given
     *         system identifier is already expanded.
     *
     */
    public String expandSystemId(String systemId) {
        return expandSystemId(systemId, fSystemId);
    }
    private String expandSystemId(String systemId, String currentSystemId) {
        String id = systemId;

        // check for bad parameters id
        if (id == null || id.length() == 0) {
            return systemId;
        }

        // if id already expanded, return
        try {
            URL url = new URL(id);
            if (url != null) {
                return systemId;
            }
        }
        catch (MalformedURLException e) {
            // continue on...
        }

        // normalize id
        id = fixURI(id);

        // normalize base
        URL base = null;
        URL url = null;
        try {
            if (currentSystemId == null) {
                String dir;
                try {
                    dir = fixURI(System.getProperty("user.dir"));
                }
                catch (SecurityException se) {
                    dir = "";
                }
                if (!dir.endsWith("/")) {
                    dir = dir + "/";
                }
                base = new URL("file", "", dir);
            }
            else {
                base = new URL(currentSystemId);
            }

            // expand id
            url = new URL(base, id);
        }
        catch (Exception e) {
            // let it go through
        }
        if (url == null) {
            return systemId;
        }
        return url.toString();
    }

    //
    // Private methods
    //

    /**
     * Fixes a platform dependent filename to standard URI form.
     *
     * @param str The string to fix.
     *
     * @return Returns the fixed URI string.
     */
    private static String fixURI(String str) {

        // handle platform dependent strings
        str = str.replace(java.io.File.separatorChar, '/');

        // Windows fix
        if (str.length() >= 2) {
            char ch1 = str.charAt(1);
            if (ch1 == ':') {
                char ch0 = Character.toUpperCase(str.charAt(0));
                if (ch0 >= 'A' && ch0 <= 'Z') {
                    str = "/" + str;
                }
            }
        }

        // done
        return str;
    }

    //
    //
    //
    private void sendEndOfInputNotifications() throws Exception {
        boolean moreToFollow = fReaderStack.size() > 1;
        fScanner.endOfInput(fEntityName, moreToFollow);
        if (fScanningDTD)
            fDTDValidator.endOfInput(fEntityName, moreToFollow);
    }
    private void sendReaderChangeNotifications() throws Exception {
        fScanner.readerChange(fReader, fReaderId);
        if (fScanningDTD)
            fDTDValidator.readerChange(fReader, fReaderId);
    }
    private void sendStartEntityNotifications() throws Exception {
        startEntityReference(fEntityName, fEntityType, fEntityContext);
    }
    private void sendEndEntityNotifications() throws Exception {
        endEntityReference(fEntityName, fEntityType, fEntityContext);
    }
    /**
     * set up the reader stack to read from the document entity
     */
    public boolean startReadingFromDocument(InputSource source) throws Exception {
        pushEntity(false, -2); // Document Entity
        fSystemId = null;
        pushNullReader();
        fEntityName = -2; // Document Entity
        fEntityType = ENTITYTYPE_DOCUMENT;
        fEntityContext = CONTEXT_DOCUMENT;
        fReaderDepth = 0;
        fReaderId = fNextReaderId++;
        fPublicId = source.getPublicId();
        fSystemId = source.getSystemId();
        sendStartEntityNotifications();
        fSystemId = expandSystemId(fSystemId, null);
        fSource = source;
        boolean xmlDecl = true; // xmlDecl if true, textDecl if false
        try {
            fReader = fReaderFactory.createReader(fEntityHandler, fErrorReporter, source, fSystemId, xmlDecl, fStringPool);
        } catch (MalformedURLException mu) {
            fReader = null;
            String errorSystemId = fSystemId;
            sendEndEntityNotifications();
            popReader();
            popEntity();
            Object[] args = { errorSystemId };
            fErrorReporter.reportError(fErrorReporter.getLocator(),
                                        ImplementationMessages.XERCES_IMPLEMENTATION_DOMAIN,
                                        ImplementationMessages.IO0,
                                        0,
                                        args,
                                        XMLErrorReporter.ERRORTYPE_FATAL_ERROR);
        } catch (FileNotFoundException fnf) {
            fReader = null;
            String errorSystemId = fSystemId;
            sendEndEntityNotifications();
            popReader();
            popEntity();
            Object[] args = { errorSystemId };
            fErrorReporter.reportError(fErrorReporter.getLocator(),
                                        ImplementationMessages.XERCES_IMPLEMENTATION_DOMAIN,
                                        ImplementationMessages.IO0,
                                        0,
                                        args,
                                        XMLErrorReporter.ERRORTYPE_FATAL_ERROR);
        } catch (java.io.UnsupportedEncodingException uee) {
            fReader = null;
            sendEndEntityNotifications();
            popReader();
            popEntity();
            String encoding = uee.getMessage();
            if (encoding == null) {
                fErrorReporter.reportError(fErrorReporter.getLocator(),
                                           XMLMessages.XML_DOMAIN,
                                           XMLMessages.MSG_ENCODING_REQUIRED,
                                           XMLMessages.P81_REQUIRED,
                                           null,
                                           XMLErrorReporter.ERRORTYPE_FATAL_ERROR);
            } else if (!XMLCharacterProperties.validEncName(encoding)) {
                Object[] args = { encoding };
                fErrorReporter.reportError(fErrorReporter.getLocator(),
                                           XMLMessages.XML_DOMAIN,
                                           XMLMessages.MSG_ENCODINGDECL_INVALID,
                                           XMLMessages.P81_INVALID_VALUE,
                                           args,
                                           XMLErrorReporter.ERRORTYPE_FATAL_ERROR);
            } else {
                Object[] args = { encoding };
                fErrorReporter.reportError(fErrorReporter.getLocator(),
                                           XMLMessages.XML_DOMAIN,
                                           XMLMessages.MSG_ENCODING_NOT_SUPPORTED,
                                           XMLMessages.P81_NOT_SUPPORTED,
                                           args,
                                           XMLErrorReporter.ERRORTYPE_FATAL_ERROR);
            }
        }
        sendReaderChangeNotifications();
        return fReader != null;
    }
    /**
     * start reading from an external DTD subset
     */
    public void startReadingFromExternalSubset(String publicId, String systemId, int readerDepth) throws Exception {
        pushEntity(true, -1);
        pushReader();
        pushNullReader();
        fEntityName = -1; // External Subset
        fEntityType = ENTITYTYPE_EXTERNAL_SUBSET;
        fEntityContext = CONTEXT_EXTERNAL_SUBSET;
        fReaderDepth = readerDepth;
        fReaderId = fNextReaderId++;
        fPublicId = publicId;
        fSystemId = systemId;
        startReadingFromExternalEntity(false);
    }
    /**
     * stop reading from an external DTD subset
     */
    public void stopReadingFromExternalSubset() throws Exception {
        if (!(fReader instanceof NullReader))
            throw new RuntimeException("FWK004 cannot happen 18"+"\n18");
        popReader();
        sendReaderChangeNotifications();
    }

    /**
     * start reading from an external entity
     */
    public boolean startReadingFromEntity(int entityName, int readerDepth, int context) throws Exception {
        if (context > XMLEntityHandler.CONTEXT_IN_CONTENT)
            return startReadingFromParameterEntity(entityName, readerDepth, context);
        int entityHandle = fValidator.lookupEntity(entityName);
        if (entityHandle < 0) {
            int minorCode = XMLMessages.VC_ENTITY_DECLARED;
            int errorType = XMLErrorReporter.ERRORTYPE_RECOVERABLE_ERROR;
            // REVISIT - the following test in insufficient...
            if (fEntityContext == CONTEXT_DOCUMENT || fEntityContext == CONTEXT_IN_ATTVALUE) {
                minorCode = XMLMessages.WFC_ENTITY_DECLARED;
                errorType = XMLErrorReporter.ERRORTYPE_FATAL_ERROR;
            }
            Object[] args = { fStringPool.toString(entityName) };
            fErrorReporter.reportError(fErrorReporter.getLocator(),
                                       XMLMessages.XML_DOMAIN,
                                       XMLMessages.MSG_ENTITY_NOT_DECLARED,
                                       minorCode,
                                       args,
                                       errorType);
            return false;
        }
        if (context == CONTEXT_IN_CONTENT) {
            if (fValidator.isUnparsedEntity(entityHandle)) {
                Object[] args = { fStringPool.toString(entityName) };
                fErrorReporter.reportError(fErrorReporter.getLocator(),
                                           XMLMessages.XML_DOMAIN,
                                           XMLMessages.MSG_REFERENCE_TO_UNPARSED_ENTITY,
                                           XMLMessages.WFC_PARSED_ENTITY,
                                           args,
                                           XMLErrorReporter.ERRORTYPE_FATAL_ERROR);
                return false;
            }
        } else {
            if (fValidator.isExternalEntity(entityHandle)) {
                Object[] args = { fStringPool.toString(entityName) };
                fErrorReporter.reportError(fErrorReporter.getLocator(),
                                           XMLMessages.XML_DOMAIN,
                                           XMLMessages.MSG_REFERENCE_TO_EXTERNAL_ENTITY,
                                           XMLMessages.WFC_NO_EXTERNAL_ENTITY_REFERENCES,
                                           args,
                                           XMLErrorReporter.ERRORTYPE_FATAL_ERROR);
                return false;
            }
        }
        if (!pushEntity(false, entityName)) {
            Object[] args = { fStringPool.toString(entityName),
                              entityReferencePath(false, entityName) };
            fErrorReporter.reportError(fErrorReporter.getLocator(),
                                       XMLMessages.XML_DOMAIN,
                                       XMLMessages.MSG_RECURSIVE_REFERENCE,
                                       XMLMessages.WFC_NO_RECURSION,
                                       args,
                                       XMLErrorReporter.ERRORTYPE_FATAL_ERROR);
            return false;
        }
        pushReader();
        fEntityName = entityName;
        fEntityContext = context;
        fReaderDepth = readerDepth;
        fReaderId = fNextReaderId++;
        if (context != CONTEXT_IN_CONTENT || !fValidator.externalReferenceInContent(entityHandle)) {
            fEntityType = ENTITYTYPE_INTERNAL;
            fPublicId = null/*"Internal Entity: " + fStringPool.toString(entityName)*/;
            fSystemId = fSystemId; // keep expandSystemId happy
            int value = -1;
            if (context == CONTEXT_IN_CONTENT || context == CONTEXT_IN_DEFAULTATTVALUE)
                value = fValidator.getEntityValue(entityHandle);
            else
                value = fValidator.valueOfReferenceInAttValue(entityHandle);
            startReadingFromInternalEntity(value, false);
            return false;
        }
        fEntityType = ENTITYTYPE_EXTERNAL;
        fPublicId = fValidator.getPublicIdOfEntity(entityHandle);
        fSystemId = fValidator.getSystemIdOfEntity(entityHandle);
        return startReadingFromExternalEntity(true);
    }
    private boolean startReadingFromParameterEntity(int peName, int readerDepth, int context) throws Exception {
        int entityHandle = fValidator.lookupParameterEntity(peName);
        if (entityHandle == -1) {
            // The error is generated by the validator (strange... it is a VC, not a WFC...)
            return false;
        }
        if (!pushEntity(true, peName)) {
            Object[] args = { fStringPool.toString(peName),
                              entityReferencePath(true, peName) };
            fErrorReporter.reportError(fErrorReporter.getLocator(),
                                       XMLMessages.XML_DOMAIN,
                                       XMLMessages.MSG_RECURSIVE_PEREFERENCE,
                                       XMLMessages.WFC_NO_RECURSION,
                                       args,
                                       XMLErrorReporter.ERRORTYPE_FATAL_ERROR);
            return false;
        }
        pushReader();
        fEntityName = peName;
        fEntityContext = context;
        fReaderDepth = readerDepth;
        fReaderId = fNextReaderId++;
        if (!fValidator.isExternalParameterEntity(entityHandle)) {
            fEntityType = ENTITYTYPE_INTERNAL_PE;
            fPublicId = null/*"Internal Entity: %" + fStringPool.toString(peName)*/;
            fSystemId = fSystemId; // keep expandSystemId happy
            int value = fValidator.getParameterEntityValue(entityHandle);
            startReadingFromInternalEntity(value, fEntityContext == CONTEXT_IN_ENTITYVALUE ? false : true);
            return false;
        }
        fEntityType = ENTITYTYPE_EXTERNAL_PE;
        fPublicId = fValidator.getPublicIdOfParameterEntity(entityHandle);
        fSystemId = fValidator.getSystemIdOfParameterEntity(entityHandle);
        return startReadingFromExternalEntity(true);
    }
    private void startReadingFromInternalEntity(int value, boolean addSpaces) throws Exception {
        if (fEntityContext == CONTEXT_IN_ENTITYVALUE) {
            //
            // REVISIT - consider optimizing the case where the entire entity value
            // consists of a single reference to a parameter entity and do not append
            // the value to fLiteralData again, but re-use the offset/length of the
            // referenced entity for the value of this entity.
            //
        }
        fSource = null;
        sendStartEntityNotifications();
        fReader = fReaderFactory.createStringReader(this, fErrorReporter, fSendCharDataAsCharArray, getLineNumber(), getColumnNumber(), value, fStringPool, addSpaces); // REVISIT - string reader needs better location support
        sendReaderChangeNotifications();
    }
    private boolean startReadingFromExternalEntity(boolean checkForTextDecl) throws Exception {
        if (fEntityContext == CONTEXT_IN_ENTITYVALUE) {
            //
            // REVISIT - Can we get the spec changed ?
            // There is a perverse edge case to handle here...  We have a reference
            // to an external PE within a literal EntityValue.  For the PE to be
            // well-formed, it must match the extPE production, but the code that
            // appends the replacement text to the entity value is in no position
            // to do a complete well-formedness check !!
            //
        }
        if (fEntityContext == CONTEXT_IN_DTD_WITHIN_MARKUP) {
            //
            // REVISIT - Can we get the spec changed ?
            // There is a perverse edge case to handle here...  We have a reference
            // to an external PE within markup.  For the PE to be well-formed, it
            // must match the extPE production, which is probably not going to be
            // very useful expanded in the middle of a markup declaration.  The
            // problem is that an empty file, a file containing just whitespace or
            // another PE that is just empty or whitespace, matches extPE !!
            //
        }
        sendStartEntityNotifications();
        ReaderState rs = (ReaderState) fReaderStack.peek();
        fSystemId = expandSystemId(fSystemId, rs.systemId);
        fSource = fEntityResolver == null ? null : fEntityResolver.resolveEntity(fPublicId, fSystemId);
        if (fSource == null) {
            fSource = new InputSource(fSystemId);
            if (fPublicId != null)
                fSource.setPublicId(fPublicId);
        }
        boolean textDecl = false; // xmlDecl if true, textDecl if false
        try {
            fReader = fReaderFactory.createReader(fEntityHandler, fErrorReporter, fSource, fSystemId, textDecl, fStringPool);
        } catch (MalformedURLException mu) {
            fReader = null;
            String errorSystemId = fSystemId;
            sendEndEntityNotifications();
            popReader();
            popEntity();
            Object[] args = { errorSystemId };
            fErrorReporter.reportError(fErrorReporter.getLocator(),
                                        ImplementationMessages.XERCES_IMPLEMENTATION_DOMAIN,
                                        ImplementationMessages.IO0,
                                        0,
                                        args,
                                        XMLErrorReporter.ERRORTYPE_FATAL_ERROR);
        } catch (FileNotFoundException fnf) {
            fReader = null;
            String errorSystemId = fSystemId;
            sendEndEntityNotifications();
            popReader();
            popEntity();
            Object[] args = { errorSystemId };
            fErrorReporter.reportError(fErrorReporter.getLocator(),
                                        ImplementationMessages.XERCES_IMPLEMENTATION_DOMAIN,
                                        ImplementationMessages.IO0,
                                        0,
                                        args,
                                        XMLErrorReporter.ERRORTYPE_FATAL_ERROR);
        } catch (java.io.UnsupportedEncodingException uee) {
            fReader = null;
            sendEndEntityNotifications();
            popReader();
            popEntity();
            String encoding = uee.getMessage();
            if (encoding == null) {
                fErrorReporter.reportError(fErrorReporter.getLocator(),
                                           XMLMessages.XML_DOMAIN,
                                           XMLMessages.MSG_ENCODING_REQUIRED,
                                           XMLMessages.P81_REQUIRED,
                                           null,
                                           XMLErrorReporter.ERRORTYPE_FATAL_ERROR);
            } else if (!XMLCharacterProperties.validEncName(encoding)) {
                Object[] args = { encoding };
                fErrorReporter.reportError(fErrorReporter.getLocator(),
                                           XMLMessages.XML_DOMAIN,
                                           XMLMessages.MSG_ENCODINGDECL_INVALID,
                                           XMLMessages.P81_INVALID_VALUE,
                                           args,
                                           XMLErrorReporter.ERRORTYPE_FATAL_ERROR);
            } else {
                Object[] args = { encoding };
                fErrorReporter.reportError(fErrorReporter.getLocator(),
                                           XMLMessages.XML_DOMAIN,
                                           XMLMessages.MSG_ENCODING_NOT_SUPPORTED,
                                           XMLMessages.P81_NOT_SUPPORTED,
                                           args,
                                           XMLErrorReporter.ERRORTYPE_FATAL_ERROR);
            }
        }
        if (fReader == null || !checkForTextDecl) {
            sendReaderChangeNotifications();
            return false;
        }
        int readerId = fReaderId;
        sendReaderChangeNotifications();
        boolean parseTextDecl = fReader.lookingAtChar('<', false);
        if (readerId != fReaderId)
            parseTextDecl = false;
        return parseTextDecl;
    }

    //
    // reader stack
    //
    private void pushNullReader() {
        ReaderState rs = fReaderStateFreeList;
        if (rs == null)
            rs = new ReaderState();
        else
            fReaderStateFreeList = rs.nextReaderState;
        if (fNullReader == null)
            fNullReader = new NullReader();
        rs.reader = fNullReader;
        rs.source = null;
        rs.entityName = -1; // Null Entity
        rs.entityType = -1; // Null Entity
        rs.entityContext = -1; // Null Entity
        rs.publicId = "Null Entity";
        rs.systemId = fSystemId;
        rs.readerId = fNextReaderId++;
        rs.depth = -1;
        rs.nextReaderState = null;
        fReaderStack.push(rs);
    }
    private void pushReader() {
        ReaderState rs = fReaderStateFreeList;
        if (rs == null)
            rs = new ReaderState();
        else
            fReaderStateFreeList = rs.nextReaderState;
        rs.reader = fReader;
        rs.source = fSource;
        rs.entityName = fEntityName;
        rs.entityType = fEntityType;
        rs.entityContext = fEntityContext;
        rs.publicId = fPublicId;
        rs.systemId = fSystemId;
        rs.readerId = fReaderId;
        rs.depth = fReaderDepth;
        rs.nextReaderState = null;
        fReaderStack.push(rs);
    }
    private void popReader() {
        if (fReaderStack.empty())
            throw new RuntimeException("FWK004 cannot happen 19"+"\n19");
        ReaderState rs = (ReaderState) fReaderStack.pop();
        fReader = rs.reader;
        fSource = rs.source;
        fEntityName = rs.entityName;
        fEntityType = rs.entityType;
        fEntityContext = rs.entityContext;
        fPublicId = rs.publicId;
        fSystemId = rs.systemId;
        fReaderId = rs.readerId;
        fReaderDepth = rs.depth;
        rs.nextReaderState = fReaderStateFreeList;
        fReaderStateFreeList = rs;
    }

    //
    // entity stack
    //
    /**
     * start an entity declaration
     */
    public boolean startEntityDecl(boolean isPE, int entityName) throws Exception {
        if (!pushEntity(isPE, entityName)) {
            int majorCode = isPE ? XMLMessages.MSG_RECURSIVE_PEREFERENCE : XMLMessages.MSG_RECURSIVE_REFERENCE;
            Object[] args = { fStringPool.toString(entityName),
                              entityReferencePath(isPE, entityName) };
            fErrorReporter.reportError(fErrorReporter.getLocator(),
                                       XMLMessages.XML_DOMAIN,
                                       majorCode,
                                       XMLMessages.WFC_NO_RECURSION,
                                       args,
                                       XMLErrorReporter.ERRORTYPE_FATAL_ERROR);
            return false;
        }
        return true;
    }
    /**
     * end an entity declaration
     */
    public void endEntityDecl() throws Exception {
        popEntity();
    }
    private boolean pushEntity(boolean isPE, int entityName) throws Exception {
        if (entityName >= 0) {
            for (int i = 0; i < fEntityStackDepth; i++) {
                if (fEntityNameStack[i] == entityName && fEntityTypeStack[i] == (isPE ? 1 : 0)) {
                    return false;
                }
            }
        }
        if (fEntityTypeStack == null) {
            fEntityTypeStack = new byte[8];
            fEntityNameStack = new int[8];
        } else if (fEntityStackDepth == fEntityTypeStack.length) {
            byte[] newTypeStack = new byte[fEntityStackDepth * 2];
            System.arraycopy(fEntityTypeStack, 0, newTypeStack, 0, fEntityStackDepth);
            fEntityTypeStack = newTypeStack;
            int[] newNameStack = new int[fEntityStackDepth * 2];
            System.arraycopy(fEntityNameStack, 0, newNameStack, 0, fEntityStackDepth);
            fEntityNameStack = newNameStack;
        }
        fEntityTypeStack[fEntityStackDepth] = (byte)(isPE ? 1 : 0);
        fEntityNameStack[fEntityStackDepth] = entityName;
        fEntityStackDepth++;
        return true;
    }
    private String entityReferencePath(boolean isPE, int entityName) {
        StringBuffer sb = new StringBuffer();
        sb.append("(top-level)");
        for (int i = 0; i < fEntityStackDepth; i++) {
            if (fEntityNameStack[i] >= 0) {
                sb.append('-');
                sb.append(fEntityTypeStack[i] == 1 ? '%' : '&');
                sb.append(fStringPool.toString(fEntityNameStack[i]));
                sb.append(';');
            }
        }
        sb.append('-');
        sb.append(isPE ? '%' : '&');
        sb.append(fStringPool.toString(entityName));
        sb.append(';');
        return sb.toString();
    }
    private void popEntity() throws Exception {
        fEntityStackDepth--;
    }

    //
    //
    //
    /**
     * This method is provided for scanner implementations.
     */
    public int getReaderId() {
        return fReaderId;
    }
    /**
     * This method is provided for scanner implementations.
     */
    public void setReaderDepth(int depth) {
        fReaderDepth = depth;
    }
    /**
     * This method is provided for scanner implementations.
     */
    public int getReaderDepth() {
        return fReaderDepth;
    }
    /**
     * Return the public identifier of the <code>InputSource</code> that we are processing.
     *
     * @return The public identifier, or null if not provided.
     */
    public String getPublicId() {
        return fPublicId;
    }
    /**
     * Return the system identifier of the <code>InputSource</code> that we are processing.
     *
     * @return The system identifier, or null if not provided.
     */
    public String getSystemId() {
        return fSystemId;
    }
    /**
     * Return the line number of the current position within the document that we are processing.
     *
     * @return The current line number.
     */
    public int getLineNumber() {
        return fReader.getLineNumber();
    }
    /**
     * Return the column number of the current position within the document that we are processing.
     *
     * @return The current column number.
     */
    public int getColumnNumber() {
        return fReader.getColumnNumber();
    }
    /**
     * This method is called by the reader subclasses at the
     * end of input, and also by the scanner directly to force
     * a reader change during error recovery.
     */
    public XMLEntityHandler.EntityReader changeReaders() throws Exception {
        sendEndOfInputNotifications();
        sendEndEntityNotifications();
        popReader();
        sendReaderChangeNotifications();
        popEntity();
        return fReader;
    }

    //
    // We use the null reader after we have reached the
    // end of input for the document or external subset.
    //
    private final class NullReader implements XMLEntityHandler.EntityReader {
        //
        //
        //
        public NullReader() {
        }
        public int currentOffset() {
            return -1;
        }
        public int getLineNumber() {
            return -1;
        }
        public int getColumnNumber() {
            return -1;
        }
        public void setInCDSect(boolean inCDSect) {
        }
        public boolean getInCDSect() {
            return false;
        }
        public void append(XMLEntityHandler.CharBuffer charBuffer, int offset, int length) {
        }
        public int addString(int offset, int length) {
            return -1;
        }
        public int addSymbol(int offset, int length) {
            return -1;
        }
        public boolean lookingAtChar(char ch, boolean skipPastChar) {
            return false;
        }
        public boolean lookingAtValidChar(boolean skipPastChar) {
            return false;
        }
        public boolean lookingAtSpace(boolean skipPastChar) {
            return false;
        }
        public void skipToChar(char ch) {
        }
        public void skipPastSpaces() {
        }
        public void skipPastName(char fastcheck) {
        }
        public void skipPastNmtoken(char fastcheck) {
        }
        public boolean skippedString(char[] s) {
            return false;
        }
        public int scanInvalidChar() {
            return -1;
        }
        public int scanCharRef(boolean hex) {
            return XMLEntityHandler.CHARREF_RESULT_INVALID_CHAR;
        }
        public int scanStringLiteral() {
            return XMLEntityHandler.STRINGLIT_RESULT_QUOTE_REQUIRED;
        }
        public int scanAttValue(char qchar, boolean asSymbol) {
            return XMLEntityHandler.ATTVALUE_RESULT_INVALID_CHAR;
        }
        public int scanEntityValue(int qchar, boolean createString) {
            return XMLEntityHandler.ENTITYVALUE_RESULT_INVALID_CHAR;
        }
        public boolean scanExpectedName(char fastcheck, StringPool.CharArrayRange expectedName) {
            return false;
        }
        public int scanQName(char fastcheck) {
            return -1;
        }
        public int scanName(char fastcheck) {
            return -1;
        }
        public int scanContent(int elementType) throws Exception {
            return XMLEntityHandler.CONTENT_RESULT_INVALID_CHAR;
        }
    }

} // class XMLParser