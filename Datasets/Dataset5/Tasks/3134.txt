setFeature(NOTIFY_BUILTIN_REFS, true);

/*
 * The Apache Software License, Version 1.1
 *
 *
 * Copyright (c) 2001 The Apache Software Foundation.  
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

package org.apache.xerces.parsers;

import java.io.IOException;
import java.util.Locale;

import org.apache.xerces.impl.Constants;
import org.apache.xerces.impl.XMLDocumentScannerImpl;
import org.apache.xerces.impl.XMLDTDScannerImpl;
import org.apache.xerces.impl.XMLErrorReporter;
import org.apache.xerces.impl.XMLEntityManager;
import org.apache.xerces.impl.dtd.XMLDTDValidator;
import org.apache.xerces.impl.XMLNamespaceBinder;
import org.apache.xerces.impl.msg.XMLMessageFormatter;
import org.apache.xerces.impl.validation.ValidationManager;
import org.apache.xerces.impl.dv.dtd.DatatypeValidatorFactory;
import org.apache.xerces.impl.dv.dtd.DatatypeValidatorFactoryImpl;
import org.apache.xerces.impl.validation.GrammarPool;

import org.apache.xerces.impl.xs.XSMessageFormatter;
import org.apache.xerces.impl.xs.XMLSchemaValidator;
import org.apache.xerces.util.SymbolTable;
import org.apache.xerces.xni.XMLLocator;
import org.apache.xerces.xni.XNIException;
import org.apache.xerces.xni.parser.XMLComponent;
import org.apache.xerces.xni.parser.XMLComponentManager;
import org.apache.xerces.xni.parser.XMLConfigurationException;
import org.apache.xerces.xni.parser.XMLDocumentScanner;
import org.apache.xerces.xni.parser.XMLDTDScanner;
import org.apache.xerces.xni.parser.XMLInputSource;
import org.apache.xerces.xni.parser.XMLPullParserConfiguration;

/**
 * This is the "standard" parser configuration. It extends the basic
 * configuration with the standard set of parser components. Since
 * the Xerces2 reference implementation document and DTD scanner
 * implementations are capable of acting as pull parsers, the
 * standard configuration implements the 
 * <code>XMLPullParserConfiguration</code> interface.
 * <p>
 * In addition to the features and properties recognized by the base
 * parser configuration, this class recognizes these additional 
 * features and properties:
 * <ul>
 * <li>Features
 *  <ul>
 *   <li>http://apache.org/xml/features/validation/warn-on-duplicate-attdef</li>
 *   <li>http://apache.org/xml/features/validation/warn-on-undeclared-elemdef</li>
 *   <li>http://apache.org/xml/features/allow-java-encodings</li>
 *   <li>http://apache.org/xml/features/continue-after-fatal-error</li>
 *   <li>http://apache.org/xml/features/load-external-dtd</li>
 *  </ul>
 * <li>Properties
 *  <ul>
 *   <li>http://apache.org/xml/properties/internal/error-reporter</li>
 *   <li>http://apache.org/xml/properties/internal/entity-manager</li>
 *   <li>http://apache.org/xml/properties/internal/document-scanner</li>
 *   <li>http://apache.org/xml/properties/internal/dtd-scanner</li>
 *   <li>http://apache.org/xml/properties/internal/grammar-pool</li>
 *   <li>http://apache.org/xml/properties/internal/validator/dtd</li>
 *   <li>http://apache.org/xml/properties/internal/datatype-validator-factory</li>
 *  </ul>
 * </ul>
 *
 * @author Arnaud  Le Hors, IBM
 * @author Andy Clark, IBM
 *
 * @version $Id$
 */
public class StandardParserConfiguration
    extends BasicParserConfiguration 
    implements XMLPullParserConfiguration {

    //
    // Constants
    //

    // feature identifiers

    /** Feature identifier: warn on duplicate attribute definition. */
    protected static final String WARN_ON_DUPLICATE_ATTDEF =
        Constants.XERCES_FEATURE_PREFIX + Constants.WARN_ON_DUPLICATE_ATTDEF_FEATURE;
    
    /** Feature identifier: warn on undeclared element definition. */
    protected static final String WARN_ON_UNDECLARED_ELEMDEF =
        Constants.XERCES_FEATURE_PREFIX + Constants.WARN_ON_UNDECLARED_ELEMDEF_FEATURE;
    
    /** Feature identifier: allow Java encodings. */
    protected static final String ALLOW_JAVA_ENCODINGS = 
        Constants.XERCES_FEATURE_PREFIX + Constants.ALLOW_JAVA_ENCODINGS_FEATURE;
    
    /** Feature identifier: continue after fatal error. */
    protected static final String CONTINUE_AFTER_FATAL_ERROR = 
        Constants.XERCES_FEATURE_PREFIX + Constants.CONTINUE_AFTER_FATAL_ERROR_FEATURE;

    /** Feature identifier: load external DTD. */
    protected static final String LOAD_EXTERNAL_DTD =
        Constants.XERCES_FEATURE_PREFIX + Constants.LOAD_EXTERNAL_DTD_FEATURE;

    /** Feature identifier: notify built-in refereces. */
    protected static final String NOTIFY_BUILTIN_REFS =
        Constants.XERCES_FEATURE_PREFIX + Constants.NOTIFY_BUILTIN_REFS_FEATURE;
    
    /** Feature identifier: notify character refereces. */
    protected static final String NOTIFY_CHAR_REFS =
        Constants.XERCES_FEATURE_PREFIX + Constants.NOTIFY_CHAR_REFS_FEATURE;
    
    // property identifiers

    /** Property identifier: error reporter. */
    protected static final String ERROR_REPORTER = 
        Constants.XERCES_PROPERTY_PREFIX + Constants.ERROR_REPORTER_PROPERTY;

    /** Property identifier: entity manager. */
    protected static final String ENTITY_MANAGER = 
        Constants.XERCES_PROPERTY_PREFIX + Constants.ENTITY_MANAGER_PROPERTY;
    
    /** Property identifier document scanner: */
    protected static final String DOCUMENT_SCANNER = 
        Constants.XERCES_PROPERTY_PREFIX + Constants.DOCUMENT_SCANNER_PROPERTY;

    /** Property identifier: DTD scanner. */
    protected static final String DTD_SCANNER = 
        Constants.XERCES_PROPERTY_PREFIX + Constants.DTD_SCANNER_PROPERTY;

    /** Property identifier: grammar pool. */
    protected static final String GRAMMAR_POOL = 
        Constants.XERCES_PROPERTY_PREFIX + Constants.GRAMMAR_POOL_PROPERTY;
    
    /** Property identifier: DTD validator. */
    protected static final String DTD_VALIDATOR = 
        Constants.XERCES_PROPERTY_PREFIX + Constants.DTD_VALIDATOR_PROPERTY;

    /** Property identifier: namespace binder. */
    protected static final String NAMESPACE_BINDER =
        Constants.XERCES_PROPERTY_PREFIX + Constants.NAMESPACE_BINDER_PROPERTY;

    /** Property identifier: datatype validator factory. */
    protected static final String DATATYPE_VALIDATOR_FACTORY = 
        Constants.XERCES_PROPERTY_PREFIX + Constants.DATATYPE_VALIDATOR_FACTORY_PROPERTY;

    protected static final String VALIDATION_MANAGER =
        Constants.XERCES_PROPERTY_PREFIX + Constants.VALIDATION_MANAGER_PROPERTY;

    /** Property identifier: XML Schema validator. */
    protected static final String SCHEMA_VALIDATOR =
        Constants.XERCES_PROPERTY_PREFIX + Constants.SCHEMA_VALIDATOR_PROPERTY;


    // debugging

    /** Set to true and recompile to print exception stack trace. */
    private static final boolean PRINT_EXCEPTION_STACK_TRACE = false;

    //
    // Data
    //

    // components (non-configurable)

    /** Grammar pool. */
    protected GrammarPool fGrammarPool;

    /** Datatype validator factory. */
    protected DatatypeValidatorFactory fDatatypeValidatorFactory;

    // components (configurable)

    /** Error reporter. */
    protected XMLErrorReporter fErrorReporter;

    /** Entity manager. */
    protected XMLEntityManager fEntityManager;

    /** Document scanner. */
    protected XMLDocumentScanner fScanner;

    /** Input Source */
    protected XMLInputSource fInputSource;

    /** DTD scanner. */
    protected XMLDTDScanner fDTDScanner;

    /** DTD Validator. */
    protected XMLDTDValidator fDTDValidator;

    /** Namespace binder. */
    protected XMLNamespaceBinder fNamespaceBinder;

    /** XML Schema Validator. */
    protected XMLSchemaValidator fSchemaValidator;

    protected ValidationManager fValidationManager;
    // state

    /** Locator */
    protected XMLLocator fLocator;

    /** 
     * True if a parse is in progress. This state is needed because
     * some features/properties cannot be set while parsing (e.g.
     * validation and namespaces).
     */
    protected boolean fParseInProgress = false;

    //
    // Constructors
    //

    /** Default constructor. */
    public StandardParserConfiguration() {
        this(null, null, null);
    } // <init>()

    /** 
     * Constructs a parser configuration using the specified symbol table. 
     *
     * @param symbolTable The symbol table to use.
     */
    public StandardParserConfiguration(SymbolTable symbolTable) {
        this(symbolTable, null, null);
    } // <init>(SymbolTable)

    /**
     * Constructs a parser configuration using the specified symbol table and
     * grammar pool.
     * <p>
     * <strong>REVISIT:</strong> 
     * Grammar pool will be updated when the new validation engine is
     * implemented.
     *
     * @param symbolTable The symbol table to use.
     * @param grammarPool The grammar pool to use.
     */
    public StandardParserConfiguration(SymbolTable symbolTable,
                                       GrammarPool grammarPool) {
        this(symbolTable, grammarPool, null);
    } // <init>(SymbolTable,GrammarPool)

    /**
     * Constructs a parser configuration using the specified symbol table,
     * grammar pool, and parent settings.
     * <p>
     * <strong>REVISIT:</strong> 
     * Grammar pool will be updated when the new validation engine is
     * implemented.
     *
     * @param symbolTable    The symbol table to use.
     * @param grammarPool    The grammar pool to use.
     * @param parentSettings The parent settings.
     */
    public StandardParserConfiguration(SymbolTable symbolTable,
                                       GrammarPool grammarPool,
                                       XMLComponentManager parentSettings) {
        super(symbolTable, parentSettings);

        // add default recognized features
        final String[] recognizedFeatures = {
            WARN_ON_DUPLICATE_ATTDEF,   WARN_ON_UNDECLARED_ELEMDEF,
            ALLOW_JAVA_ENCODINGS,       CONTINUE_AFTER_FATAL_ERROR,
            LOAD_EXTERNAL_DTD,          NOTIFY_BUILTIN_REFS,
            NOTIFY_CHAR_REFS,
        };
        addRecognizedFeatures(recognizedFeatures);

        // set state for default features
        setFeature(WARN_ON_DUPLICATE_ATTDEF, false);
        setFeature(WARN_ON_UNDECLARED_ELEMDEF, false);
        setFeature(ALLOW_JAVA_ENCODINGS, false);
        setFeature(CONTINUE_AFTER_FATAL_ERROR, false);
        setFeature(LOAD_EXTERNAL_DTD, true);
        setFeature(NOTIFY_BUILTIN_REFS, false);
        setFeature(NOTIFY_CHAR_REFS, false);

        // add default recognized properties
        final String[] recognizedProperties = {
            ERROR_REPORTER,             
            ENTITY_MANAGER, 
            DOCUMENT_SCANNER,
            DTD_SCANNER,
            DTD_VALIDATOR,
            NAMESPACE_BINDER,
            GRAMMAR_POOL,   
            DATATYPE_VALIDATOR_FACTORY,
            VALIDATION_MANAGER
        };
        addRecognizedProperties(recognizedProperties);

        // create and register missing components
        if (grammarPool == null) {
            grammarPool = new GrammarPool();
        }
        fGrammarPool = grammarPool;
        setProperty(GRAMMAR_POOL, fGrammarPool);

        fEntityManager = createEntityManager();
        setProperty(ENTITY_MANAGER, fEntityManager);
        addComponent(fEntityManager);

        fErrorReporter = createErrorReporter();
        fErrorReporter.setDocumentLocator(fEntityManager.getEntityScanner());
        setProperty(ERROR_REPORTER, fErrorReporter);
        addComponent(fErrorReporter);

        fScanner = createDocumentScanner();
        setProperty(DOCUMENT_SCANNER, fScanner);
        if (fScanner instanceof XMLComponent) {
            addComponent((XMLComponent)fScanner);
        }

        fDTDScanner = createDTDScanner();
        if (fDTDScanner != null) {
            setProperty(DTD_SCANNER, fDTDScanner);
            if (fDTDScanner instanceof XMLComponent) {
                addComponent((XMLComponent)fDTDScanner);
            }
        }

        fDTDValidator = createDTDValidator();
        if (fDTDValidator != null) {
            setProperty(DTD_VALIDATOR, fDTDValidator);
            addComponent(fDTDValidator);
        }

        fNamespaceBinder = createNamespaceBinder();
        if (fNamespaceBinder != null) {
            setProperty(NAMESPACE_BINDER, fNamespaceBinder);
            addComponent(fNamespaceBinder);
        }
        
        fDatatypeValidatorFactory = createDatatypeValidatorFactory();
        if (fDatatypeValidatorFactory != null) {
            setProperty(DATATYPE_VALIDATOR_FACTORY,
                        fDatatypeValidatorFactory);
        }
        fValidationManager = createValidationManager();

        if (fValidationManager != null) {
            setProperty (VALIDATION_MANAGER, fValidationManager);
        }
        // add message formatters
        if (fErrorReporter.getMessageFormatter(XMLMessageFormatter.XML_DOMAIN) == null) {
            XMLMessageFormatter xmft = new XMLMessageFormatter();
            fErrorReporter.putMessageFormatter(XMLMessageFormatter.XML_DOMAIN, xmft);
            fErrorReporter.putMessageFormatter(XMLMessageFormatter.XMLNS_DOMAIN, xmft);
        }

        // set locale
        try {
            setLocale(Locale.getDefault());
        }
        catch (XNIException e) {
            // do nothing
            // REVISIT: What is the right thing to do? -Ac
        }

    } // <init>(SymbolTable,GrammarPool)

    //
    // Public methods
    //

    /**
     * Set the locale to use for messages.
     *
     * @param locale The locale object to use for localization of messages.
     *
     * @exception XNIException Thrown if the parser does not support the
     *                         specified locale.
     */
    public void setLocale(Locale locale) throws XNIException {
        fErrorReporter.setLocale(locale);
    } // setLocale(Locale)

    //
    // XMLPullParserConfiguration methods
    //

    // parsing

    /**
     * Sets the input source for the document to parse.
     *
     * @param inputSource The document's input source.
     *
     * @exception XMLConfigurationException Thrown if there is a 
     *                        configuration error when initializing the
     *                        parser.
     * @exception IOException Thrown on I/O error.
     *
     * @see #parse(boolean)
     */
    public void setInputSource(XMLInputSource inputSource)
        throws XMLConfigurationException, IOException {
        
        // REVISIT: this method used to reset all the components and
        //          construct the pipeline. Now reset() is called
        //          in parse (boolean) just before we parse the document
        //          Should this method still throw exceptions..?

        fInputSource = inputSource;
        
    } // setInputSource(XMLInputSource)

    /**
     * Parses the document in a pull parsing fashion.
     *
     * @param complete True if the pull parser should parse the
     *                 remaining document completely.
     *
     * @returns True if there is more document to parse.
     *
     * @exception XNIException Any XNI exception, possibly wrapping 
     *                         another exception.
     * @exception IOException  An IO exception from the parser, possibly
     *                         from a byte stream or character stream
     *                         supplied by the parser.
     *
     * @see #setInputSource
     */
    public boolean parse(boolean complete) throws XNIException, IOException {
        //
        // reset and configure pipeline and set InputSource.
        if (fInputSource !=null) {
            try {
                // resets and sets the pipeline.
                reset();
                fScanner.setInputSource(fInputSource);
                fInputSource = null;
            } 
            catch (XNIException ex) {
                if (PRINT_EXCEPTION_STACK_TRACE)
                    ex.printStackTrace();
                throw ex;
            } 
            catch (IOException ex) {
                if (PRINT_EXCEPTION_STACK_TRACE)
                    ex.printStackTrace();
                throw ex;
            } 
            catch (RuntimeException ex) {
                if (PRINT_EXCEPTION_STACK_TRACE)
                    ex.printStackTrace();
                throw ex;
            }
            catch (Exception ex) {
                if (PRINT_EXCEPTION_STACK_TRACE)
                    ex.printStackTrace();
                throw new XNIException(ex);
            }
        }

        try {
            return fScanner.scanDocument(complete);
        } 
        catch (XNIException ex) {
            if (PRINT_EXCEPTION_STACK_TRACE)
                ex.printStackTrace();
            throw ex;
        } 
        catch (IOException ex) {
            if (PRINT_EXCEPTION_STACK_TRACE)
                ex.printStackTrace();
            throw ex;
        } 
        catch (RuntimeException ex) {
            if (PRINT_EXCEPTION_STACK_TRACE)
                ex.printStackTrace();
            throw ex;
        }
        catch (Exception ex) {
            if (PRINT_EXCEPTION_STACK_TRACE)
                ex.printStackTrace();
            throw new XNIException(ex);
        }

    } // parse(boolean):boolean

    //
    // XMLParserConfiguration methods
    //

    /**
     * Parses the specified input source.
     *
     * @param source The input source.
     *
     * @exception XNIException Throws exception on XNI error.
     * @exception java.io.IOException Throws exception on i/o error.
     */
    public void parse(XMLInputSource source) throws XNIException, IOException {

        if (fParseInProgress) {
            // REVISIT - need to add new error message
            throw new XNIException("FWK005 parse may not be called while parsing.");
        }
        fParseInProgress = true;

        try {
            setInputSource(source);
            parse(true);
        } 
        catch (XNIException ex) {
            if (PRINT_EXCEPTION_STACK_TRACE)
                ex.printStackTrace();
            throw ex;
        } 
        catch (IOException ex) {
            if (PRINT_EXCEPTION_STACK_TRACE)
                ex.printStackTrace();
            throw ex;
        } 
        catch (Exception ex) {
            if (PRINT_EXCEPTION_STACK_TRACE)
                ex.printStackTrace();
            throw new XNIException(ex);
        }
        finally {
            fParseInProgress = false;
        }

    } // parse(InputSource)

    //
    // Protected methods
    //
    
    /** 
     * Reset all components before parsing. 
     *
     * @throws XNIException Thrown if an error occurs during initialization.
     */
    protected void reset() throws XNIException {

        // configure the pipeline and initialize the components
        configurePipeline();
        super.reset();

    } // reset()

    /** Configures the pipeline. */
    protected void configurePipeline() {

        // REVISIT: This should be better designed. In other words, we
        //          need to figure out what is the best way for people to
        //          re-use *most* of the standard configuration but do 
        //          things common things such as remove a component (e.g.
        //          the validator), insert a new component (e.g. XInclude), 
        //          etc... -Ac

        // setup document pipeline
        if (fDTDValidator != null) {
            fScanner.setDocumentHandler(fDTDValidator);
            fDTDValidator.setDocumentHandler(fNamespaceBinder);
            fNamespaceBinder.setDocumentHandler(fDocumentHandler);
        }
        else {
            fScanner.setDocumentHandler(fNamespaceBinder);
            fNamespaceBinder.setDocumentHandler(fDocumentHandler);
        }

        // setup dtd pipeline
        if (fDTDScanner != null) {
            if (fDTDValidator != null) {
                fDTDScanner.setDTDHandler(fDTDValidator);
                fDTDValidator.setDTDHandler(fDTDHandler);
                
                fDTDScanner.setDTDContentModelHandler(fDTDValidator);
                fDTDValidator.setDTDContentModelHandler(fDTDContentModelHandler);
            }
            else {
                fDTDScanner.setDTDHandler(fDTDHandler);
                fDTDScanner.setDTDContentModelHandler(fDTDContentModelHandler);
            }
        }

        if ( getFeature(Constants.XERCES_FEATURE_PREFIX + Constants.SCHEMA_VALIDATION_FEATURE)) {
            // If schema validator was not in the pipeline insert it.
            if (fSchemaValidator == null) {
                fSchemaValidator = new XMLSchemaValidator(); 
            
                // add schema component
                fProperties.put(SCHEMA_VALIDATOR, fSchemaValidator);
                addComponent(fSchemaValidator);
                 // add schema message formatter
                if (fErrorReporter.getMessageFormatter(XSMessageFormatter.SCHEMA_DOMAIN) == null) {
                    XSMessageFormatter xmft = new XSMessageFormatter();
                    fErrorReporter.putMessageFormatter(XSMessageFormatter.SCHEMA_DOMAIN, xmft);
                }

            }
            fNamespaceBinder.setDocumentHandler(fSchemaValidator);
            fSchemaValidator.setDocumentHandler(fDocumentHandler);
            

            // REVISIT: we probably should not remove schema validator from the pipeline
            // if schema feature is off, since user might want to have some PSVI 
            // of the document.
            // On the other hand, if user constructed a parser with the default config,
            // turned schema on before first parse(), and then turned it off, is it possible
            // that user would assume that we will remove XML Schema validator?
        } 


    } // configurePipeline()

    // features and properties

    /**
     * Check a feature. If feature is know and supported, this method simply
     * returns. Otherwise, the appropriate exception is thrown.
     *
     * @param featureId The unique identifier (URI) of the feature.
     *
     * @throws XMLConfigurationException Thrown for configuration error.
     *                                   In general, components should
     *                                   only throw this exception if
     *                                   it is <strong>really</strong>
     *                                   a critical error.
     */
    protected void checkFeature(String featureId)
        throws XMLConfigurationException {

        //
        // Xerces Features
        //

        if (featureId.startsWith(Constants.XERCES_FEATURE_PREFIX)) {
            String feature = featureId.substring(Constants.XERCES_FEATURE_PREFIX.length());
            //
            // http://apache.org/xml/features/validation/schema
            //   Lets the user turn Schema validation support on/off.
            //
            if (feature.equals(Constants.SCHEMA_VALIDATION_FEATURE)) {
                return;
            }
            //
            // http://apache.org/xml/features/validation/dynamic
            //   Allows the parser to validate a document only when it
            //   contains a grammar. Validation is turned on/off based
            //   on each document instance, automatically.
            //
            if (feature.equals(Constants.DYNAMIC_VALIDATION_FEATURE)) {
                return;
            }

            // activate full schema checking
            if (feature.equals(Constants.SCHEMA_FULL_CHECKING)) {
                return;
            }
            //
            // http://apache.org/xml/features/validation/default-attribute-values
            //
            if (feature.equals(Constants.DEFAULT_ATTRIBUTE_VALUES_FEATURE)) {
                // REVISIT
                short type = XMLConfigurationException.NOT_SUPPORTED;
                throw new XMLConfigurationException(type, featureId);
            }
            //
            // http://apache.org/xml/features/validation/default-attribute-values
            //
            if (feature.equals(Constants.VALIDATE_CONTENT_MODELS_FEATURE)) {
                // REVISIT
                short type = XMLConfigurationException.NOT_SUPPORTED;
                throw new XMLConfigurationException(type, featureId);
            }
            //
            // http://apache.org/xml/features/validation/nonvalidating/load-dtd-grammar
            //
            if (feature.equals(Constants.LOAD_DTD_GRAMMAR_FEATURE)) {
                return;
            }
            //
            // http://apache.org/xml/features/validation/nonvalidating/load-external-dtd
            //
            if (feature.equals(Constants.LOAD_EXTERNAL_DTD_FEATURE)) {
                return;
            }

            //
            // http://apache.org/xml/features/validation/default-attribute-values
            //
            if (feature.equals(Constants.VALIDATE_DATATYPES_FEATURE)) {
                short type = XMLConfigurationException.NOT_SUPPORTED;
                throw new XMLConfigurationException(type, featureId);
            }
        }

        //
        // Not recognized
        //

        super.checkFeature(featureId);

    } // checkFeature(String)

    /**
     * Check a property. If the property is know and supported, this method
     * simply returns. Otherwise, the appropriate exception is thrown.
     *
     * @param propertyId The unique identifier (URI) of the property
     *                   being set.
     *
     * @throws XMLConfigurationException Thrown for configuration error.
     *                                   In general, components should
     *                                   only throw this exception if
     *                                   it is <strong>really</strong>
     *                                   a critical error.
     */
    protected void checkProperty(String propertyId)
        throws XMLConfigurationException {

        //
        // Xerces Properties
        //

        if (propertyId.startsWith(Constants.XERCES_PROPERTY_PREFIX)) {
            String property = propertyId.substring(Constants.XERCES_PROPERTY_PREFIX.length());
            if (property.equals(Constants.DTD_SCANNER_PROPERTY)) {
                return;
            }
        }

        //
        // Not recognized
        //

        super.checkProperty(propertyId);

    } // checkProperty(String)

    // factory methods

    /** Creates an entity manager. */
    protected XMLEntityManager createEntityManager() {
        return new XMLEntityManager();
    } // createEntityManager():XMLEntityManager

    /** Creates an error reporter. */
    protected XMLErrorReporter createErrorReporter() {
        return new XMLErrorReporter();
    } // createErrorReporter():XMLErrorReporter

    /** Create a document scanner. */
    protected XMLDocumentScanner createDocumentScanner() {
        return new XMLDocumentScannerImpl();
    } // createDocumentScanner():XMLDocumentScanner

    /** Create a DTD scanner. */
    protected XMLDTDScanner createDTDScanner() {
        return new XMLDTDScannerImpl();
    } // createDTDScanner():XMLDTDScanner

    /** Create a DTD validator. */
    protected XMLDTDValidator createDTDValidator() {
        return new XMLDTDValidator();
    } // createDTDValidator():XMLDTDValidator

    /** Create a namespace binder. */
    protected XMLNamespaceBinder createNamespaceBinder() {
        return new XMLNamespaceBinder();
    } // createNamespaceBinder():XMLNamespaceBinder

    /** Create a datatype validator factory. */
    protected DatatypeValidatorFactory createDatatypeValidatorFactory() {
        return new DatatypeValidatorFactoryImpl();
    } // createDatatypeValidatorFactory():DatatypeValidatorFactory
    protected ValidationManager createValidationManager(){
        return new ValidationManager();
    }

} // class StandardParserConfiguration