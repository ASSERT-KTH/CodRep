fSchemaHandler.reset(fErrorReporter, fEntityManager, fSymbolTable, externalSchemas, noNamespaceExternalSchemas, null, fGrammarPool);

/*
 * The Apache Software License, Version 1.1
 *
 *
 * Copyright (c) 2001, 2002 The Apache Software Foundation.  
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

import org.apache.xerces.impl.Constants;
import org.apache.xerces.xni.grammars.XMLGrammarPool;
import org.apache.xerces.xni.grammars.XMLGrammarDescription;
import org.apache.xerces.xni.grammars.Grammar;
import org.apache.xerces.impl.Constants;
import org.apache.xerces.impl.validation.XMLGrammarPoolImpl;
import org.apache.xerces.impl.xs.traversers.XSDHandler;
import org.apache.xerces.impl.xs.models.CMBuilder;
import org.apache.xerces.impl.xs.SchemaSymbols;
import org.apache.xerces.impl.xs.SchemaGrammar;
import org.apache.xerces.impl.xs.XSDeclarationPool;
import org.apache.xerces.impl.xs.XSDDescription;
import org.apache.xerces.impl.xs.XSConstraints;
import org.apache.xerces.impl.xs.SubstitutionGroupHandler;
import org.apache.xerces.impl.xs.XSGrammarBucket;
import org.apache.xerces.util.SymbolTable;
import org.apache.xerces.util.SynchronizedSymbolTable;
import org.apache.xerces.xni.XNIException;
import org.apache.xerces.xni.parser.XMLComponent;
import org.apache.xerces.xni.parser.XMLComponentManager;
import org.apache.xerces.xni.parser.XMLConfigurationException;
import org.apache.xerces.xni.parser.XMLInputSource;

/**
 * <p> This configuration provides a generic way of using
 * Xerces's grammar caching facilities.  It extends the
 * StandardParserConfiguration and thus may validate documents
 * according to XML schemas or DTD's.  It also allows the user to
 * preparse a grammar, and to lock the grammar pool
 * implementation such that no more grammars will be added.</p>
 * <p> Using the org.apache.xerces.xni.parser property, an
 * application may instantiate a Xerces SAX or DOM parser with
 * this configuration.  When invoked in this manner, the default
 * behaviour will be elicited; to use this configuration's
 * specific facilities, the user will need to reference it
 * directly.</p>
 * <p>
 * In addition to the features and properties recognized by the base
 * parser configuration, this class recognizes these additional 
 * features and properties:
 * <ul>
 * </ul>
 *
 * @author Neil Graham, IBM
 *
 * @version $Id$
 */
public class XMLGrammarCachingConfiguration 
    extends StandardParserConfiguration {

    //
    // Constants
    //

    // a larg(ish) prime to use for a symbol table to be shared
    // among
    // potentially man parsers.  Start one as close to 2K (20
    // times larger than normal) and see what happens...
    public static final int BIG_PRIME = 2039;

    // the static symbol table to be shared amongst parsers
    protected static final SynchronizedSymbolTable fStaticSymbolTable = 
            new SynchronizedSymbolTable(BIG_PRIME);

    // the Grammar Pool to be shared similarly
    protected static final XMLGrammarPoolImpl fStaticGrammarPool =
            new XMLGrammarPoolImpl();

    // schema full checking constant
    protected static final String SCHEMA_FULL_CHECKING =
            Constants.XERCES_FEATURE_PREFIX+Constants.SCHEMA_FULL_CHECKING;

    // Data

    // some constants that need to be added into the symbol table
    String XMLNS = null;
    String URI_XSI = null;
    String XSI_SCHEMALOCATION = null;
    String XSI_NONAMESPACESCHEMALOCATION = null;
    String XSI_TYPE = null;
    String XSI_NIL = null;
    String URI_SCHEMAFORSCHEMA = null;

    // variables needed for caching schema grammars.  
    // REVISIT:  surely this can be simplified so that interfaces like this don't need to 
    // import *sooo* many classes...
    protected XSDHandler fSchemaHandler;
    protected XSGrammarBucket fXSGrammarBucket;
    protected SubstitutionGroupHandler fSubGroupHandler;
    protected CMBuilder fCMBuilder;

    //
    // Constructors
    //

    /** Default constructor. */
    public XMLGrammarCachingConfiguration() {
        this(fStaticSymbolTable, fStaticGrammarPool, null);
    } // <init>()

    /** 
     * Constructs a parser configuration using the specified symbol table. 
     *
     * @param symbolTable The symbol table to use.
     */
    public XMLGrammarCachingConfiguration(SymbolTable symbolTable) {
        this(symbolTable, fStaticGrammarPool, null);
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
    public XMLGrammarCachingConfiguration(SymbolTable symbolTable,
                                       XMLGrammarPool grammarPool) {
        this(symbolTable, grammarPool, null);
    } // <init>(SymbolTable,XMLGrammarPool)

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
    public XMLGrammarCachingConfiguration(SymbolTable symbolTable,
                                       XMLGrammarPool grammarPool,
                                       XMLComponentManager parentSettings) {
        super(symbolTable, grammarPool, parentSettings);

       // symbolTable is assumed to be static here...
       XMLNS = fSymbolTable.addSymbol(SchemaSymbols.O_XMLNS);
       URI_XSI = fSymbolTable.addSymbol(SchemaSymbols.URI_XSI);
       XSI_SCHEMALOCATION = fSymbolTable.addSymbol(SchemaSymbols.OXSI_SCHEMALOCATION);
       XSI_NONAMESPACESCHEMALOCATION = fSymbolTable.addSymbol(SchemaSymbols.OXSI_NONAMESPACESCHEMALOCATION);
       XSI_TYPE = fSymbolTable.addSymbol(SchemaSymbols.OXSI_TYPE);
       XSI_NIL = fSymbolTable.addSymbol(SchemaSymbols.OXSI_NIL);
       URI_SCHEMAFORSCHEMA = fSymbolTable.addSymbol(SchemaSymbols.OURI_SCHEMAFORSCHEMA);

        // REVISIT:  may need to add some features/properties
        // specific to this configuration at some point...

        // add default recognized features
        // set state for default features
        // add default recognized properties
        // create and register missing components
    } // <init>(SymbolTable,XMLGrammarPool, XMLComponentManager)

    //
    // Public methods
    //

    /*
     * lock the XMLGrammarPoolImpl object so that it does not
     * accept any more grammars from the validators.  This isn't
     * a part of the XMLGrammarPool interface, so this method
     * returns true if the operation succeeded, false otherwise
     * (i.e., the grammar pool isn't our XMLGrammarPoolImpl)
     * @return:  true on success, false on failure
     */
    public boolean lockGrammarPool() {
        if(fGrammarPool instanceof org.apache.xerces.impl.validation.XMLGrammarPoolImpl) {
            // call appropriate method on class
            return true;
        }
        return false;
    } // lockGrammarPool()

    /**
     * Parse a grammar from a location identified by an URI.
     * This method also adds this grammar to the XMLGrammarPool
     *
     * @param type The type of the grammar to be constructed
     * @param uri The location of the grammar to be constructed.
     * <strong>The parser will not expand this URI or make it
     * available to the EntityResolver</strong>
     * @return The newly created <code>Grammar</code>.
     * @exception XNIException thrown on an error in grammar
     * construction
     * @exception IOException thrown if an error is encountered
     * in reading the file
     */
    public Grammar parseGrammar(String type, String uri)
                              throws XNIException, IOException {
        XMLInputSource source = new XMLInputSource(null, uri, null);
        return parseGrammar(type, source);

    }

    /**
     * Parse a grammar from a location identified by an
     * XMLInputSource.  
     * This method also adds this grammar to the XMLGrammarPool
     *
     * @param type The type of the grammar to be constructed
     * @param source The XMLInputSource containing this grammar's
     * information
     * <strong>If a URI is included in the systemId field, the parser will not expand this URI or make it
     * available to the EntityResolver</strong>
     * @return The newly created <code>Grammar</code>.
     * @exception XNIException thrown on an error in grammar
     * construction
     * @exception IOException thrown if an error is encountered
     * in reading the file
     */
    public Grammar parseGrammar(String type, XMLInputSource
                is) throws XNIException, IOException {
       // REVISIT:  for now, don't know what to do with DTD's...
       if(!type.equals(XMLGrammarDescription.XML_SCHEMA))
            return null;
       if (fSchemaHandler == null) {
           fXSGrammarBucket = new XSGrammarBucket();
           fSubGroupHandler = new SubstitutionGroupHandler(fXSGrammarBucket);
           fSchemaHandler = new XSDHandler(fXSGrammarBucket);
           fCMBuilder = new CMBuilder(new XSDeclarationPool());
       }

       // we already have an error reporter, entityManager, entity resolver, etc.

       String externalSchemas =
            (String)(getProperty(Constants.XERCES_PROPERTY_PREFIX+Constants.SCHEMA_LOCATION));
       String noNamespaceExternalSchemas =
            (String)(getProperty(Constants.XERCES_PROPERTY_PREFIX+Constants.SCHEMA_NONS_LOCATION));

       fXSGrammarBucket.reset();
       // by default, make all XMLGrammarPoolImpl's schema grammars available to fSchemaHandler
       SchemaGrammar [] grammars = (SchemaGrammar [])(fGrammarPool.retrieveInitialGrammarSet(XMLGrammarDescription.XML_SCHEMA));
       for(int i=0; i<grammars.length; i++ )
            fXSGrammarBucket.putGrammar(grammars[i]);
       fSubGroupHandler.reset();
       fSchemaHandler.reset(fErrorReporter, fEntityManager, fSymbolTable, externalSchemas, noNamespaceExternalSchemas, null);

       // Should check whether the grammar with this namespace is already in
       // the grammar resolver. But since we don't know the target namespace
       // of the document here, we leave such check to XSDHandler
       SchemaGrammar grammar = fSchemaHandler.parseSchema(null, is,
                                                          XSDDescription.CONTEXT_PREPARSE);

       if (getFeature(SCHEMA_FULL_CHECKING)) {
           XSConstraints.fullSchemaChecking(fXSGrammarBucket, fSubGroupHandler, fCMBuilder, fErrorReporter);
       }
       // by default, hand it off to the grammar pool
       fGrammarPool.cacheGrammars(XMLGrammarDescription.XML_SCHEMA, new Grammar [] {grammar});
       return grammar;

    }

    //
    // Protected methods
    //
    
    // features and properties

    /**
     * Check a feature. If feature is known and supported, this method simply
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

        super.checkFeature(featureId);

    } // checkFeature(String)

    /**
     * Check a property. If the property is known and supported, this method
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
        super.checkProperty(propertyId);

    } // checkProperty(String)

} // class StandardParserConfiguration