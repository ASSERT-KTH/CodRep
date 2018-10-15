char[] escChs = {' ', '<', '>', '#', '%', '"', '{', '}',

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

package org.apache.xerces.impl;

import java.io.EOFException;
import java.io.FileInputStream;
import java.io.FilterReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.IOException;
import java.io.Reader;
import java.io.StringReader;
import java.net.URL;
import java.util.Hashtable;
import java.util.Locale;
import java.util.Stack;
import java.util.Vector;

import org.apache.xerces.impl.XMLErrorReporter;
import org.apache.xerces.impl.io.ASCIIReader;
import org.apache.xerces.impl.io.UCSReader;
import org.apache.xerces.impl.io.UTF8Reader;
import org.apache.xerces.impl.msg.XMLMessageFormatter;
import org.apache.xerces.impl.validation.ValidationManager;

import org.apache.xerces.util.EncodingMap;
import org.apache.xerces.util.XMLStringBuffer;
import org.apache.xerces.util.SymbolTable;
import org.apache.xerces.util.URI;
import org.apache.xerces.util.XMLChar;
import org.apache.xerces.util.XMLResourceIdentifierImpl;

import org.apache.xerces.xni.QName;
import org.apache.xerces.xni.XMLResourceIdentifier;
import org.apache.xerces.xni.XMLString;
import org.apache.xerces.xni.XNIException;
import org.apache.xerces.xni.parser.XMLComponent;
import org.apache.xerces.xni.parser.XMLComponentManager;
import org.apache.xerces.xni.parser.XMLConfigurationException;
import org.apache.xerces.xni.parser.XMLEntityResolver;
import org.apache.xerces.xni.parser.XMLInputSource;

/**
 * The entity manager handles the registration of general and parameter
 * entities; resolves entities; and starts entities. The entity manager
 * is a central component in a standard parser configuration and this
 * class works directly with the entity scanner to manage the underlying
 * xni.
 * <p>
 * This component requires the following features and properties from the
 * component manager that uses it:
 * <ul>
 *  <li>http://xml.org/sax/features/validation</li>
 *  <li>http://xml.org/sax/features/external-general-entities</li>
 *  <li>http://xml.org/sax/features/external-parameter-entities</li>
 *  <li>http://apache.org/xml/features/allow-java-encodings</li>
 *  <li>http://apache.org/xml/properties/internal/symbol-table</li>
 *  <li>http://apache.org/xml/properties/internal/error-reporter</li>
 *  <li>http://apache.org/xml/properties/internal/entity-resolver</li>
 * </ul>
 *
 *
 * @author Andy Clark, IBM
 * @author Arnaud  Le Hors, IBM
 *
 * @version $Id$
 */
public class XMLEntityManager
    implements XMLComponent, XMLEntityResolver {

    //
    // Constants
    //

    /** Default buffer size (2048). */
    public static final int DEFAULT_BUFFER_SIZE = 2048;

    /** Default buffer size before we've finished with the XMLDecl:  */
    public static final int DEFAULT_XMLDECL_BUFFER_SIZE = 64;

    /** Default internal entity buffer size (1024). */
    public static final int DEFAULT_INTERNAL_BUFFER_SIZE = 1024;

    // feature identifiers

    /** Feature identifier: validation. */
    protected static final String VALIDATION =
        Constants.SAX_FEATURE_PREFIX + Constants.VALIDATION_FEATURE;

    /** Feature identifier: external general entities. */
    protected static final String EXTERNAL_GENERAL_ENTITIES =
        Constants.SAX_FEATURE_PREFIX + Constants.EXTERNAL_GENERAL_ENTITIES_FEATURE;

    /** Feature identifier: external parameter entities. */
    protected static final String EXTERNAL_PARAMETER_ENTITIES =
        Constants.SAX_FEATURE_PREFIX + Constants.EXTERNAL_PARAMETER_ENTITIES_FEATURE;

    /** Feature identifier: allow Java encodings. */
    protected static final String ALLOW_JAVA_ENCODINGS =
        Constants.XERCES_FEATURE_PREFIX + Constants.ALLOW_JAVA_ENCODINGS_FEATURE;

    /** Feature identifier: warn on duplicate EntityDef */
    protected static final String WARN_ON_DUPLICATE_ENTITYDEF =
    Constants.XERCES_FEATURE_PREFIX +Constants.WARN_ON_DUPLICATE_ENTITYDEF_FEATURE;

    // property identifiers

    /** Property identifier: symbol table. */
    protected static final String SYMBOL_TABLE =
        Constants.XERCES_PROPERTY_PREFIX + Constants.SYMBOL_TABLE_PROPERTY;

    /** Property identifier: error reporter. */
    protected static final String ERROR_REPORTER =
        Constants.XERCES_PROPERTY_PREFIX + Constants.ERROR_REPORTER_PROPERTY;

    /** Property identifier: entity resolver. */
    protected static final String ENTITY_RESOLVER =
        Constants.XERCES_PROPERTY_PREFIX + Constants.ENTITY_RESOLVER_PROPERTY;

    // property identifier:  ValidationManager
    protected static final String VALIDATION_MANAGER =
        Constants.XERCES_PROPERTY_PREFIX + Constants.VALIDATION_MANAGER_PROPERTY;

    /** property identifier: buffer size. */
    protected static final String BUFFER_SIZE =
        Constants.XERCES_PROPERTY_PREFIX + Constants.BUFFER_SIZE_PROPERTY;

    // recognized features and properties

    /** Recognized features. */
    private static final String[] RECOGNIZED_FEATURES = {
        VALIDATION,
        EXTERNAL_GENERAL_ENTITIES,
        EXTERNAL_PARAMETER_ENTITIES,
        ALLOW_JAVA_ENCODINGS,
        WARN_ON_DUPLICATE_ENTITYDEF
    };

    /** Feature defaults. */
    private static final Boolean[] FEATURE_DEFAULTS = {
        null,
        Boolean.TRUE,
        Boolean.TRUE,
        Boolean.FALSE,
        Boolean.FALSE,
    };

    /** Recognized properties. */
    private static final String[] RECOGNIZED_PROPERTIES = {
        SYMBOL_TABLE,
        ERROR_REPORTER,
        ENTITY_RESOLVER,
        VALIDATION_MANAGER,
        BUFFER_SIZE
    };

    /** Property defaults. */
    private static final Object[] PROPERTY_DEFAULTS = {
        null,
        null,
        null,
        null,
        new Integer(DEFAULT_BUFFER_SIZE),
    };

    private static final String XMLEntity = "[xml]".intern();
    private static final String DTDEntity = "[dtd]".intern();
    
    // debugging

    /**
     * Debug printing of buffer. This debugging flag works best when you
     * resize the DEFAULT_BUFFER_SIZE down to something reasonable like
     * 64 characters.
     */
    private static final boolean DEBUG_BUFFER = false;

    /** Debug some basic entities. */
    private static final boolean DEBUG_ENTITIES = false;

    /** Debug switching readers for encodings. */
    private static final boolean DEBUG_ENCODINGS = false;

    // should be diplayed trace resolving messages
    private static final boolean DEBUG_RESOLVER = false;

    //
    // Data
    //

    // features

    /**
     * Validation. This feature identifier is:
     * http://xml.org/sax/features/validation
     */
    protected boolean fValidation;

    /**
     * External general entities. This feature identifier is:
     * http://xml.org/sax/features/external-general-entities
     */
    protected boolean fExternalGeneralEntities;

    /**
     * External parameter entities. This feature identifier is:
     * http://xml.org/sax/features/external-parameter-entities
     */
    protected boolean fExternalParameterEntities;

    /**
     * Allow Java encoding names. This feature identifier is:
     * http://apache.org/xml/features/allow-java-encodings
     */
    protected boolean fAllowJavaEncodings;

    /** warn on duplicate Entity declaration.
     *  http://apache.org/xml/features/warn-on-duplicate-entitydef
     */
    protected boolean fWarnDuplicateEntityDef;

    // properties

    /**
     * Symbol table. This property identifier is:
     * http://apache.org/xml/properties/internal/symbol-table
     */
    protected SymbolTable fSymbolTable;

    /**
     * Error reporter. This property identifier is:
     * http://apache.org/xml/properties/internal/error-reporter
     */
    protected XMLErrorReporter fErrorReporter;

    /**
     * Entity resolver. This property identifier is:
     * http://apache.org/xml/properties/internal/entity-resolver
     */
    protected XMLEntityResolver fEntityResolver;

    /**
     * Validation manager. This property identifier is:
     * http://apache.org/xml/properties/internal/validation-manager
     */
    protected ValidationManager fValidationManager;

    // settings

    /**
     * Buffer size. We get this value from a property. The default size
     * is used if the input buffer size property is not specified.
     * REVISIT: do we need a property for internal entity buffer size?
     */
    protected int fBufferSize = DEFAULT_BUFFER_SIZE;

    /**
     * True if the document entity is standalone. This should really
     * only be set by the document source (e.g. XMLDocumentScanner).
     */
    protected boolean fStandalone;

    // are the entities being parsed in the external subset?
    // NOTE:  this *is not* the same as whether they're external entities!
    protected boolean fInExternalSubset = false;

    // handlers

    /** Entity handler. */
    protected XMLEntityHandler fEntityHandler;

    // scanner

    /** Entity scanner. */
    protected XMLEntityScanner fEntityScanner;

    // entities

    /** Entities. */
    protected Hashtable fEntities = new Hashtable();

    /** Entity stack. */
    protected Stack fEntityStack = new Stack();

    /** Current entity. */
    protected ScannedEntity fCurrentEntity;

    // shared context

    /** Shared declared entities. */
    protected Hashtable fDeclaredEntities;

    // temp vars

    /** Resource identifer. */
    private final XMLResourceIdentifierImpl fResourceIdentifier = new XMLResourceIdentifierImpl();

    //
    // Constructors
    //

    /** Default constructor. */
    public XMLEntityManager() {
        this(null);
    } // <init>()

    /**
     * Constructs an entity manager that shares the specified entity
     * declarations during each parse.
     * <p>
     * <strong>REVISIT:</strong> We might want to think about the "right"
     * way to expose the list of declared entities. For now, the knowledge
     * how to access the entity declarations is implicit.
     */
    public XMLEntityManager(XMLEntityManager entityManager) {

        // create scanner
        fEntityScanner = createEntityScanner();

        // save shared entity declarations
        fDeclaredEntities = entityManager != null
                          ? entityManager.getDeclaredEntities() : null;

    } // <init>(XMLEntityManager)

    //
    // Public methods
    //

    /**
     * Sets whether the document entity is standalone.
     *
     * @param standalone True if document entity is standalone.
     */
    public void setStandalone(boolean standalone) {
        fStandalone = standalone;
    } // setStandalone(boolean)

    /** Returns true if the document entity is standalone. */
    public boolean isStandalone() {
        return fStandalone;
    } // isStandalone():boolean

    /**
     * Sets the entity handler. When an entity starts and ends, the
     * entity handler is notified of the change.
     *
     * @param entityHandler The new entity handler.
     */
    public void setEntityHandler(XMLEntityHandler entityHandler) {
        fEntityHandler = entityHandler;
    } // setEntityHandler(XMLEntityHandler)

    /**
     * Adds an internal entity declaration.
     * <p>
     * <strong>Note:</strong> This method ignores subsequent entity
     * declarations.
     * <p>
     * <strong>Note:</strong> The name should be a unique symbol. The
     * SymbolTable can be used for this purpose.
     *
     * @param name The name of the entity.
     * @param text The text of the entity.
     *
     * @see SymbolTable
     */
    public void addInternalEntity(String name, String text) {
        if (!fEntities.containsKey(name)) {
            Entity entity = new InternalEntity(name, text, fInExternalSubset);
            fEntities.put(name, entity);
        }
        else{
            if(fWarnDuplicateEntityDef){
                fErrorReporter.reportError(XMLMessageFormatter.XML_DOMAIN,
                                             "MSG_DUPLICATE_ENTITY_DEFINITION",
                                             new Object[]{ name },
                                             XMLErrorReporter.SEVERITY_WARNING );
            }
        }

    } // addInternalEntity(String,String)

    /**
     * Adds an external entity declaration.
     * <p>
     * <strong>Note:</strong> This method ignores subsequent entity
     * declarations.
     * <p>
     * <strong>Note:</strong> The name should be a unique symbol. The
     * SymbolTable can be used for this purpose.
     *
     * @param name         The name of the entity.
     * @param publicId     The public identifier of the entity.
     * @param literalSystemId     The system identifier of the entity.
     * @param baseSystemId The base system identifier of the entity.
     *                     This is the system identifier of the entity
     *                     where <em>the entity being added</em> and
     *                     is used to expand the system identifier when
     *                     the system identifier is a relative URI.
     *                     When null the system identifier of the first
     *                     external entity on the stack is used instead.
     *
     * @see SymbolTable
     */
    public void addExternalEntity(String name,
                                  String publicId, String literalSystemId,
                                  String baseSystemId) {
        if (!fEntities.containsKey(name)) {
            if (baseSystemId == null) {
                // search for the first external entity on the stack
                int size = fEntityStack.size();
                if (size == 0 && fCurrentEntity != null && fCurrentEntity.entityLocation != null) {
                    baseSystemId = fCurrentEntity.entityLocation.getExpandedSystemId();
                }
                for (int i = size - 1; i >= 0 ; i--) {
                    ScannedEntity externalEntity =
                        (ScannedEntity)fEntityStack.elementAt(i);
                    if (externalEntity.entityLocation != null && externalEntity.entityLocation.getExpandedSystemId() != null) {
                        baseSystemId = externalEntity.entityLocation.getExpandedSystemId();
                        break;
                    }
                }
            }
            Entity entity = new ExternalEntity(name,
                    new XMLResourceIdentifierImpl(publicId, literalSystemId, baseSystemId, expandSystemId(literalSystemId, baseSystemId)), null, fInExternalSubset);
            fEntities.put(name, entity);
        }
        else{
            if(fWarnDuplicateEntityDef){
                fErrorReporter.reportError(XMLMessageFormatter.XML_DOMAIN,
                                             "MSG_DUPLICATE_ENTITY_DEFINITION",
                                             new Object[]{ name },
                                             XMLErrorReporter.SEVERITY_WARNING );
            }
        }

    } // addExternalEntity(String,String,String,String)

    /**
     * Checks whether an entity given by name is external.
     *
     * @param entityName The name of the entity to check.
     * @returns True if the entity is external, false otherwise
     *           (including when the entity is not declared).
     */
    public boolean isExternalEntity(String entityName) {

        Entity entity = (Entity)fEntities.get(entityName);
        if (entity == null) {
            return false;
        }
        return entity.isExternal();
    }

    /**
     * Checks whether the declaration of an entity given by name is 
     // in the external subset. 
     *
     * @param entityName The name of the entity to check.
     * @returns True if the entity was declared in the external subset, false otherwise
     *           (including when the entity is not declared).
     */
    public boolean isEntityDeclInExternalSubset(String entityName) {

        Entity entity = (Entity)fEntities.get(entityName);
        if (entity == null) {
            return false;
        }
        return entity.isEntityDeclInExternalSubset();
    }

    /**
     * Adds an unparsed entity declaration.
     * <p>
     * <strong>Note:</strong> This method ignores subsequent entity
     * declarations.
     * <p>
     * <strong>Note:</strong> The name should be a unique symbol. The
     * SymbolTable can be used for this purpose.
     *
     * @param name     The name of the entity.
     * @param publicId The public identifier of the entity.
     * @param systemId The system identifier of the entity.
     * @param notation The name of the notation.
     *
     * @see SymbolTable
     */
    public void addUnparsedEntity(String name,
                                  String publicId, String systemId,
                                  String baseSystemId, String notation) {
        if (!fEntities.containsKey(name)) {
            Entity entity = new ExternalEntity(name, new XMLResourceIdentifierImpl(publicId, systemId, baseSystemId, null), notation, fInExternalSubset);
            fEntities.put(name, entity);
        }
        else{
            if(fWarnDuplicateEntityDef){
                fErrorReporter.reportError(XMLMessageFormatter.XML_DOMAIN,
                                             "MSG_DUPLICATE_ENTITY_DEFINITION",
                                             new Object[]{ name },
                                             XMLErrorReporter.SEVERITY_WARNING );
            }
        }
    } // addUnparsedEntity(String,String,String,String)

    /**
     * Checks whether an entity given by name is unparsed.
     *
     * @param entityName The name of the entity to check.
     * @returns True if the entity is unparsed, false otherwise
     *          (including when the entity is not declared).
     */
    public boolean isUnparsedEntity(String entityName) {

        Entity entity = (Entity)fEntities.get(entityName);
        if (entity == null) {
            return false;
        }
        return entity.isUnparsed();
    }

    /**
     * Checks whether an entity given by name is declared.
     *
     * @param entityName The name of the entity to check.
     * @returns True if the entity is declared, false otherwise.
     */
    public boolean isDeclaredEntity(String entityName) {

        Entity entity = (Entity)fEntities.get(entityName);
        return entity != null;
    }

    /**
     * Resolves the specified public and system identifiers. This
     * method first attempts to resolve the entity based on the
     * EntityResolver registered by the application. If no entity
     * resolver is registered or if the registered entity handler
     * is unable to resolve the entity, then default entity
     * resolution will occur.
     *
     * @param publicId     The public identifier of the entity.
     * @param systemId     The system identifier of the entity.
     * @param baseSystemId The base system identifier of the entity.
     *                     This is the system identifier of the current
     *                     entity and is used to expand the system
     *                     identifier when the system identifier is a
     *                     relative URI.
     *
     * @return Returns an input source that wraps the resolved entity.
     *         This method will never return null.
     *
     * @throws IOException  Thrown on i/o error.
     * @throws XNIException Thrown by entity resolver to signal an error.
     */
    public XMLInputSource resolveEntity(XMLResourceIdentifier resourceIdentifier)
            throws IOException, XNIException {
        if(resourceIdentifier == null ) return null;
        String publicId = resourceIdentifier.getPublicId();
        String literalSystemId = resourceIdentifier.getLiteralSystemId();
        String baseSystemId = resourceIdentifier.getBaseSystemId();
        String expandedSystemId = resourceIdentifier.getExpandedSystemId();
        // if no base systemId given, assume that it's relative
        // to the systemId of the current scanned entity
        // Sometimes the system id is not (properly) expanded.
        // We need to expand the system id if:
        // a. the expanded one was null; or
        // b. the base system id was null, but becomes non-null from the current entity.
        boolean needExpand = (expandedSystemId == null);
        // REVISIT:  why would the baseSystemId ever be null?  if we
        // didn't have to make this check we wouldn't have to reuse the
        // fXMLResourceIdentifier object...
        if (baseSystemId == null && fCurrentEntity != null && fCurrentEntity.entityLocation != null) {
            baseSystemId = fCurrentEntity.entityLocation.getExpandedSystemId();
            if (baseSystemId != null)
                needExpand = true;
         }
         if (needExpand)
            expandedSystemId = expandSystemId(literalSystemId, baseSystemId);

       // give the entity resolver a chance
        XMLInputSource xmlInputSource = null;
        if (fEntityResolver != null) {
            XMLResourceIdentifierImpl ri = null;
            if (resourceIdentifier instanceof XMLResourceIdentifierImpl) {
                ri = (XMLResourceIdentifierImpl)resourceIdentifier;
            }
            else {
                fResourceIdentifier.clear();
                ri = fResourceIdentifier;
            }
            ri.setValues(publicId, literalSystemId, baseSystemId, expandedSystemId);
            xmlInputSource = fEntityResolver.resolveEntity(ri);
        }

        // do default resolution
        // REVISIT: what's the correct behavior if the user provided an entity
        // resolver (fEntityResolver != null), but resolveEntity doesn't return
        // an input source (xmlInputSource == null)?
        // do we do default resolution, or do we just return null? -SG
        if (xmlInputSource == null) {
            // REVISIT: when systemId is null, I think we should return null.
            //          is this the right solution? -SG
            //if (systemId != null)
            xmlInputSource = new XMLInputSource(publicId, literalSystemId, baseSystemId);
        }

        if (DEBUG_RESOLVER) {
            System.err.println("XMLEntityManager.resolveEntity(" + publicId + ")");
            System.err.println(" = " + xmlInputSource);
        }

        return xmlInputSource;

    } // resolveEntity(XMLResourceIdentifier):XMLInputSource

    /**
     * Starts a named entity.
     *
     * @param entityName The name of the entity to start.
     * @param literal    True if this entity is started within a literal
     *                   value.
     *
     * @throws IOException  Thrown on i/o error.
     * @throws XNIException Thrown by entity handler to signal an error.
     */
    public void startEntity(String entityName, boolean literal)
        throws IOException, XNIException {

        // was entity declared?
        Entity entity = (Entity)fEntities.get(entityName);
        if (entity == null) {
            if (fEntityHandler != null) {
                String encoding = null;
                fResourceIdentifier.clear();
                fEntityHandler.startEntity(entityName, fResourceIdentifier, encoding);
                fEntityHandler.endEntity(entityName);
            }
            return;
        }

        // should we skip external entities?
        boolean external = entity.isExternal();
        if (external && (fValidationManager == null || !fValidationManager.isCachedDTD())) {
            boolean unparsed = entity.isUnparsed();
            boolean parameter = entityName.startsWith("%");
            boolean general = !parameter;
            if (unparsed || (general && !fExternalGeneralEntities) ||
                (parameter && !fExternalParameterEntities)) {
                if (fEntityHandler != null) {
                    fResourceIdentifier.clear();
                    final String encoding = null;
                    ExternalEntity externalEntity = (ExternalEntity)entity;
                    //REVISIT:  since we're storing expandedSystemId in the
                    // externalEntity, how could this have got here if it wasn't already
                    // expanded??? - neilg
                    String extLitSysId = (externalEntity.entityLocation != null ? externalEntity.entityLocation.getLiteralSystemId() : null);
                    String extBaseSysId = (externalEntity.entityLocation != null ? externalEntity.entityLocation.getBaseSystemId() : null);
                    String expandedSystemId = expandSystemId(extLitSysId, extBaseSysId);
                    fResourceIdentifier.setValues(
                            (externalEntity.entityLocation != null ? externalEntity.entityLocation.getPublicId() : null),
                            extLitSysId, extBaseSysId, expandedSystemId);
                    fEntityHandler.startEntity(entityName, fResourceIdentifier, encoding);
                    fEntityHandler.endEntity(entityName);
                }
                return;
            }
        }

        // is entity recursive?
        int size = fEntityStack.size();
        for (int i = size; i >= 0; i--) {
            Entity activeEntity = i == size
                                ? fCurrentEntity
                                : (Entity)fEntityStack.elementAt(i);
            if (activeEntity.name == entityName) {
                String path = entityName;
                for (int j = i + 1; j < size; j++) {
                    activeEntity = (Entity)fEntityStack.elementAt(j);
                    path = path + " -> " + activeEntity.name;
                }
                path = path + " -> " + fCurrentEntity.name;
                path = path + " -> " + entityName;
                fErrorReporter.reportError(XMLMessageFormatter.XML_DOMAIN,
                                           "RecursiveReference",
                                           new Object[] { entityName, path },
                                           XMLErrorReporter.SEVERITY_FATAL_ERROR);
                if (fEntityHandler != null) {
                    fResourceIdentifier.clear();
                    final String encoding = null;
                    if (external) {
                        ExternalEntity externalEntity = (ExternalEntity)entity;
                        // REVISIT:  for the same reason above...
                        String extLitSysId = (externalEntity.entityLocation != null ? externalEntity.entityLocation.getLiteralSystemId() : null);
                        String extBaseSysId = (externalEntity.entityLocation != null ? externalEntity.entityLocation.getBaseSystemId() : null);
                        String expandedSystemId = expandSystemId(extLitSysId, extBaseSysId);
                        fResourceIdentifier.setValues(
                                (externalEntity.entityLocation != null ? externalEntity.entityLocation.getPublicId() : null),
                                extLitSysId, extBaseSysId, expandedSystemId);
                    }
                    fEntityHandler.startEntity(entityName, fResourceIdentifier, encoding);
                    fEntityHandler.endEntity(entityName);
                }
                return;
            }
        }

        // resolve external entity
        XMLInputSource xmlInputSource = null;
        if (external) {
            ExternalEntity externalEntity = (ExternalEntity)entity;
            xmlInputSource = resolveEntity(externalEntity.entityLocation);
        }

        // wrap internal entity
        else {
            InternalEntity internalEntity = (InternalEntity)entity;
            Reader reader = new StringReader(internalEntity.text);
            xmlInputSource = new XMLInputSource(null, null, null, reader, null);
        }

        // start the entity
        startEntity(entityName, xmlInputSource, literal, external);

    } // startEntity(String,boolean)

    /**
     * Starts the document entity. The document entity has the "[xml]"
     * pseudo-name.
     *
     * @param xmlInputSource The input source of the document entity.
     *
     * @throws IOException  Thrown on i/o error.
     * @throws XNIException Thrown by entity handler to signal an error.
     */
    public void startDocumentEntity(XMLInputSource xmlInputSource)
        throws IOException, XNIException {
        startEntity(XMLEntity, xmlInputSource, false, true);
    } // startDocumentEntity(XMLInputSource)

    /**
     * Starts the DTD entity. The DTD entity has the "[dtd]"
     * pseudo-name.
     *
     * @param xmlInputSource The input source of the DTD entity.
     *
     * @throws IOException  Thrown on i/o error.
     * @throws XNIException Thrown by entity handler to signal an error.
     */
    public void startDTDEntity(XMLInputSource xmlInputSource)
        throws IOException, XNIException {
        startEntity(DTDEntity, xmlInputSource, false, true);
    } // startDTDEntity(XMLInputSource)

    // indicate start of external subset so that
    // location of entity decls can be tracked
    public void startExternalSubset() {
        fInExternalSubset = true;
    }

    public void endExternalSubset() {
        fInExternalSubset = false;
    }

    /**
     * Starts an entity.
     * <p>
     * This method can be used to insert an application defined XML
     * entity stream into the parsing stream.
     *
     * @param name           The name of the entity.
     * @param xmlInputSource The input source of the entity.
     * @param literal        True if this entity is started within a
     *                       literal value.
     * @param isExternal    whether this entity should be treated as an internal or external entity.
     *
     * @throws IOException  Thrown on i/o error.
     * @throws XNIException Thrown by entity handler to signal an error.
     */
    public void startEntity(String name,
                            XMLInputSource xmlInputSource,
                            boolean literal, boolean isExternal)
        throws IOException, XNIException {
        // get information

        final String publicId = xmlInputSource.getPublicId();
        final String literalSystemId = xmlInputSource.getSystemId();
        String baseSystemId = xmlInputSource.getBaseSystemId();
        String encoding = xmlInputSource.getEncoding();
        Boolean isBigEndian = null;

        // create reader
        InputStream stream = null;
        Reader reader = xmlInputSource.getCharacterStream();
        String expandedSystemId = expandSystemId(literalSystemId, baseSystemId);
        if (baseSystemId == null) {
            baseSystemId = expandedSystemId;
        }
        if (reader == null) {
            stream = xmlInputSource.getByteStream();
            if (stream == null) {
                stream = new URL(expandedSystemId).openStream();
            }
            // wrap this stream in RewindableInputStream
            stream = new RewindableInputStream(stream);

            // perform auto-detect of encoding if necessary
            if (encoding == null) {
                // read first four bytes and determine encoding
                final byte[] b4 = new byte[4];
                int count = 0;
                for (; count<4; count++ ) {
                    b4[count] = (byte)stream.read();
                }
                if (count == 4) {
                    Object [] encodingDesc = getEncodingName(b4, count);
                    encoding = (String)(encodingDesc[0]);
                    isBigEndian = (Boolean)(encodingDesc[1]);

                    // removed use of pushback inputstream--neilg
                    /*****
                    // push back the characters we read
                    if (DEBUG_ENCODINGS) {
                        System.out.println("$$$ wrapping input stream in PushbackInputStream");
                    }
                    PushbackInputStream pbstream = new PushbackInputStream(stream, 4);
                    *****/
                    stream.reset();
                    int offset = 0;
                    // Special case UTF-8 files with BOM created by Microsoft
                    // tools. It's more efficient to consume the BOM than make
                    // the reader perform extra checks. -Ac
                    if (count > 2 && encoding.equals("UTF-8")) {
                        int b0 = b4[0] & 0xFF;
                        int b1 = b4[1] & 0xFF;
                        int b2 = b4[2] & 0xFF;
                        if (b0 == 0xEF && b1 == 0xBB && b2 == 0xBF) {
                            // ignore first three bytes...
                            stream.skip(3);
                            /********
                            offset = 3;
                            count -= offset;
                            ***/
                        }
                    }
                    reader = createReader(stream, encoding, isBigEndian);
                }
                else {
                    reader = createReader(stream, encoding, isBigEndian);
                }
            }

            // use specified encoding
            else {
                reader = createReader(stream, encoding, isBigEndian);
            }

            // read one character at a time so we don't jump too far
            // ahead, converting characters from the byte stream in
            // the wrong encoding
            if (DEBUG_ENCODINGS) {
                System.out.println("$$$ no longer wrapping reader in OneCharReader");
            }
            //reader = new OneCharReader(reader);
        }

        // we've seen a new Reader. put it in a list, so that
        // we can close it later.
        fOwnReaders.addElement(reader);

        // push entity on stack
        if (fCurrentEntity != null) {
            fEntityStack.push(fCurrentEntity);
        }

        // create entity
        fCurrentEntity = new ScannedEntity(name,
                new XMLResourceIdentifierImpl(publicId, literalSystemId, baseSystemId, expandedSystemId),
                stream, reader, encoding, literal, false, isExternal);

        // call handler
        if (fEntityHandler != null) {
            fResourceIdentifier.setValues(publicId, literalSystemId, baseSystemId, expandedSystemId);
            fEntityHandler.startEntity(name, fResourceIdentifier, encoding);
        }

    } // startEntity(String,XMLInputSource)

    /** Returns the entity scanner. */
    public XMLEntityScanner getEntityScanner() {
        return fEntityScanner;
    } // getEntityScanner():XMLEntityScanner

    // a list of Readers ever seen
    protected Vector fOwnReaders = new Vector();

    /**
     * Close all opened InputStreams and Readers opened by this parser.
     */
    public void closeReaders() {
        // close all readers
        for (int i = fOwnReaders.size()-1; i >= 0; i--) {
            try {
                ((Reader)fOwnReaders.elementAt(i)).close();
            } catch (IOException e) {
                // ignore
            }
        }
        // and clear the list
        fOwnReaders.removeAllElements();
    }

    //
    // XMLComponent methods
    //

    /**
     * Resets the component. The component can query the component manager
     * about any features and properties that affect the operation of the
     * component.
     *
     * @param componentManager The component manager.
     *
     * @throws SAXException Thrown by component on initialization error.
     *                      For example, if a feature or property is
     *                      required for the operation of the component, the
     *                      component manager may throw a
     *                      SAXNotRecognizedException or a
     *                      SAXNotSupportedException.
     */
    public void reset(XMLComponentManager componentManager)
        throws XMLConfigurationException {

        // sax features
        try {
            fValidation = componentManager.getFeature(VALIDATION);
        }
        catch (XMLConfigurationException e) {
            fValidation = false;
        }
        try {
            fExternalGeneralEntities = componentManager.getFeature(EXTERNAL_GENERAL_ENTITIES);
        }
        catch (XMLConfigurationException e) {
            fExternalGeneralEntities = true;
        }
        try {
            fExternalParameterEntities = componentManager.getFeature(EXTERNAL_PARAMETER_ENTITIES);
        }
        catch (XMLConfigurationException e) {
            fExternalParameterEntities = true;
        }

        // xerces features
        try {
            fAllowJavaEncodings = componentManager.getFeature(ALLOW_JAVA_ENCODINGS);
        }
        catch (XMLConfigurationException e) {
            fAllowJavaEncodings = false;
        }

        try {
            fWarnDuplicateEntityDef = componentManager.getFeature(WARN_ON_DUPLICATE_ENTITYDEF);
        }
        catch (XMLConfigurationException e) {
            fWarnDuplicateEntityDef = false;
        }

        // xerces properties
        fSymbolTable = (SymbolTable)componentManager.getProperty(SYMBOL_TABLE);
        fErrorReporter = (XMLErrorReporter)componentManager.getProperty(ERROR_REPORTER);
        try {
            fEntityResolver = (XMLEntityResolver)componentManager.getProperty(ENTITY_RESOLVER);
        }
        catch (XMLConfigurationException e) {
            fEntityResolver = null;
        }
        try {
            fValidationManager = (ValidationManager)componentManager.getProperty(VALIDATION_MANAGER);
        }
        catch (XMLConfigurationException e) {
            fValidationManager = null;
        }
        
        // initialize state
        fStandalone = false;
        fEntities.clear();
        fEntityStack.removeAllElements();

        fCurrentEntity = null;

        // DEBUG
        if (DEBUG_ENTITIES) {
            addInternalEntity("text", "Hello, World.");
            addInternalEntity("empty-element", "<foo/>");
            addInternalEntity("balanced-element", "<foo></foo>");
            addInternalEntity("balanced-element-with-text", "<foo>Hello, World</foo>");
            addInternalEntity("balanced-element-with-entity", "<foo>&text;</foo>");
            addInternalEntity("unbalanced-entity", "<foo>");
            addInternalEntity("recursive-entity", "<foo>&recursive-entity2;</foo>");
            addInternalEntity("recursive-entity2", "<bar>&recursive-entity3;</bar>");
            addInternalEntity("recursive-entity3", "<baz>&recursive-entity;</baz>");

            addExternalEntity("external-text", null, "external-text.ent", "test/external-text.xml");
            addExternalEntity("external-balanced-element", null, "external-balanced-element.ent", "test/external-balanced-element.xml");
            addExternalEntity("one", null, "ent/one.ent", "test/external-entity.xml");
            addExternalEntity("two", null, "ent/two.ent", "test/ent/one.xml");
        }

        // copy declared entities
        if (fDeclaredEntities != null) {
            java.util.Enumeration keys = fDeclaredEntities.keys();
            while (keys.hasMoreElements()) {
                Object key = keys.nextElement();
                Object value = fDeclaredEntities.get(key);
                fEntities.put(key, value);
            }
        }

    } // reset(XMLComponentManager)

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

        // xerces features
        if (featureId.startsWith(Constants.XERCES_FEATURE_PREFIX)) {
            String feature = featureId.substring(Constants.XERCES_FEATURE_PREFIX.length());
            if (feature.equals(Constants.ALLOW_JAVA_ENCODINGS_FEATURE)) {
                fAllowJavaEncodings = state;
            }
        }

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

        // Xerces properties
        if (propertyId.startsWith(Constants.XERCES_PROPERTY_PREFIX)) {
            String property = propertyId.substring(Constants.XERCES_PROPERTY_PREFIX.length());
            if (property.equals(Constants.SYMBOL_TABLE_PROPERTY)) {
                fSymbolTable = (SymbolTable)value;
                return;
            }
            if (property.equals(Constants.ERROR_REPORTER_PROPERTY)) {
                fErrorReporter = (XMLErrorReporter)value;
                return;
            }
            if (property.equals(Constants.ENTITY_RESOLVER_PROPERTY)) {
                fEntityResolver = (XMLEntityResolver)value;
                return;
            }
            if (property.equals(Constants.BUFFER_SIZE_PROPERTY)) {
                Integer bufferSize = (Integer)value;
                if (bufferSize != null &&
                    bufferSize.intValue() > DEFAULT_XMLDECL_BUFFER_SIZE) {
                    fBufferSize = bufferSize.intValue();
                }
            }
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

    //
    // Public static methods
    //

    /**
     * Expands a system id and returns the system id as a URI, if
     * it can be expanded. A return value of null means that the
     * identifier is already expanded. An exception thrown
     * indicates a failure to expand the id.
     *
     * @param systemId The systemId to be expanded.
     *
     * @return Returns the URI string representing the expanded system
     *         identifier. A null value indicates that the given
     *         system identifier is already expanded.
     *
     */
    public static String expandSystemId(String systemId) {
        return expandSystemId(systemId, null);
    } // expandSystemId(String):String

    // current value of the "user.dir" property
    private static String gUserDir;
    // escaped value of the current "user.dir" property
    private static String gEscapedUserDir;
    // which ASCII characters need to be escaped
    private static boolean gNeedEscaping[] = new boolean[128];
    // the first hex character if a character needs to be escaped
    private static char gAfterEscaping1[] = new char[128];
    // the second hex character if a character needs to be escaped
    private static char gAfterEscaping2[] = new char[128];
    private static char[] gHexChs = {'0', '1', '2', '3', '4', '5', '6', '7',
                                     '8', '9', 'A', 'B', 'C', 'D', 'E', 'F'};
    // initialize the above 3 arrays
    static {
        for (int i = 0; i <= 0x1f; i++) {
            gNeedEscaping[i] = true;
            gAfterEscaping1[i] = gHexChs[i >> 4];
            gAfterEscaping2[i] = gHexChs[i & 0xf];
        }
        gNeedEscaping[0x7f] = true;
        gAfterEscaping1[0x7f] = '7';
        gAfterEscaping2[0x7f] = 'F';
        char[] escChs = {' ', '<', '>', '#', '%', '"', '"', '}',
                         '|', '\\', '^', '~', '[', ']', '`'};
        int len = escChs.length;
        char ch;
        for (int i = 0; i < len; i++) {
            ch = escChs[i];
            gNeedEscaping[ch] = true;
            gAfterEscaping1[ch] = gHexChs[ch >> 4];
            gAfterEscaping2[ch] = gHexChs[ch & 0xf];
        }
    }
    // To escape the "user.dir" system property, by using %HH to represent
    // special ASCII characters: 0x00~0x1F, 0x7F, ' ', '<', '>', '#', '%'
    // and '"'. It's a static method, so needs to be synchronized.
    // this method looks heavy, but since the system property isn't expected
    // to change often, so in most cases, we only need to return the string
    // that was escaped before.
    // According to the URI spec, non-ASCII characters (whose value >= 128)
    // need to be escaped too.
    // REVISIT: don't know how to escape non-ASCII characters, especially
    // which encoding to use. Leave them for now.
    private static synchronized String getUserDir() {
        // get the user.dir property
        String userDir = "";
        try {
            userDir = System.getProperty("user.dir");
        }
        catch (SecurityException se) {
        }

        // return empty string if property value is empty string.
        if (userDir.length() == 0)
            return "";
        
        // compute the new escaped value if the new property value doesn't
        // match the previous one
        if (userDir.equals(gUserDir)) {
            return gEscapedUserDir;
        }

        // record the new value as the global property value
        gUserDir = userDir;

        char separator = java.io.File.separatorChar;
        userDir = userDir.replace(separator, '/');

        int len = userDir.length(), ch;
        StringBuffer buffer = new StringBuffer(len*3);
        // change C:/blah to /C:/blah
        if (len >= 2 && userDir.charAt(1) == ':') {
            ch = Character.toUpperCase(userDir.charAt(0));
            if (ch >= 'A' && ch <= 'Z') {
                buffer.append('/');
            }
        }

        // for each character in the path
        int i = 0;
        for (; i < len; i++) {
            ch = userDir.charAt(i);
            // if it's not an ASCII character, break here, and use UTF-8 encoding
            if (ch >= 128)
                break;
            if (gNeedEscaping[ch]) {
                buffer.append('%');
                buffer.append(gAfterEscaping1[ch]);
                buffer.append(gAfterEscaping2[ch]);
                // record the fact that it's escaped
            }
            else {
                buffer.append((char)ch);
            }
        }

        // we saw some non-ascii character
        if (i < len) {
            // get UTF-8 bytes for the remaining sub-string
            byte[] bytes = null;
            byte b;
            try {
                bytes = userDir.substring(i).getBytes("UTF-8");
            } catch (java.io.UnsupportedEncodingException e) {
                // should never happen
                return userDir;
            }
            len = bytes.length;

            // for each byte
            for (i = 0; i < len; i++) {
                b = bytes[i];
                // for non-ascii character: make it positive, then escape
                if (b < 0) {
                    ch = b + 256;
                    buffer.append('%');
                    buffer.append(gHexChs[ch >> 4]);
                    buffer.append(gHexChs[ch & 0xf]);
                }
                else if (gNeedEscaping[b]) {
                    buffer.append('%');
                    buffer.append(gAfterEscaping1[b]);
                    buffer.append(gAfterEscaping2[b]);
                }
                else {
                    buffer.append((char)b);
                }
            }
        }

        // change blah/blah to blah/blah/
        if (!userDir.endsWith("/"))
            buffer.append('/');
        
        gEscapedUserDir = buffer.toString();

        return gEscapedUserDir;
    }

    /**
     * Expands a system id and returns the system id as a URI, if
     * it can be expanded. A return value of null means that the
     * identifier is already expanded. An exception thrown
     * indicates a failure to expand the id.
     *
     * @param systemId The systemId to be expanded.
     *
     * @return Returns the URI string representing the expanded system
     *         identifier. A null value indicates that the given
     *         system identifier is already expanded.
     *
     */
    public static String expandSystemId(String systemId, String baseSystemId) {

        // check for bad parameters id
        if (systemId == null || systemId.length() == 0) {
            return systemId;
        }
        // if id already expanded, return
        try {
            URI uri = new URI(systemId);
            if (uri != null) {
                return systemId;
            }
        }
        catch (URI.MalformedURIException e) {
            // continue on...
        }
        // normalize id
        String id = fixURI(systemId);

        // normalize base
        URI base = null;
        URI uri = null;
        try {
            if (baseSystemId == null || baseSystemId.length() == 0 ||
                baseSystemId.equals(systemId)) {
                String dir = getUserDir();
                base = new URI("file", "", dir, null, null);
            }
            else {
                try {
                    base = new URI(fixURI(baseSystemId));
                }
                catch (URI.MalformedURIException e) {
                    if (baseSystemId.indexOf(':') != -1) {
                        // for xml schemas we might have baseURI with
                        // a specified drive
                        base = new URI("file", "", fixURI(baseSystemId), null, null);
                    }
                    else {
                        String dir = getUserDir();
                        dir = dir + fixURI(baseSystemId);
                        base = new URI("file", "", dir, null, null);
                    }
                }
             }
             // expand id
             uri = new URI(base, id);
        }
        catch (Exception e) {
            // let it go through

        }

        if (uri == null) {
            return systemId;
        }
        return uri.toString();

    } // expandSystemId(String,String):String

    //
    // Protected methods
    //

    /**
     * Ends an entity.
     *
     * @throws XNIException Thrown by entity handler to signal an error.
     */
    protected void endEntity() throws XNIException {

        // call handler
        if (DEBUG_BUFFER) {
            System.out.print("(endEntity: ");
            print();
            System.out.println();
        }
        if (fEntityHandler != null) {
            fEntityHandler.endEntity(fCurrentEntity.name);
        }

        // pop stack
        // REVISIT: we are done with the current entity, should close
        //          the associated reader
        //fCurrentEntity.reader.close();
        // Now we close all readers after we finish parsing
        fCurrentEntity = fEntityStack.size() > 0
                       ? (ScannedEntity)fEntityStack.pop() : null;
        if (DEBUG_BUFFER) {
            System.out.print(")endEntity: ");
            print();
            System.out.println();
        }

    } // endEntity()

    /**
     * Returns the IANA encoding name that is auto-detected from
     * the bytes specified, with the endian-ness of that encoding where appropriate.
     *
     * @param b4    The first four bytes of the input.
     * @param count The number of bytes actually read.
     * @return a 2-element array:  the first element, an IANA-encoding string,
     *  the second element a Boolean which is true iff the document is big endian, false
     *  if it's little-endian, and null if the distinction isn't relevant.
     */
    protected Object[] getEncodingName(byte[] b4, int count) {

        if (count < 2) {
            return new Object[]{"UTF-8", null};
        }

        // UTF-16, with BOM
        int b0 = b4[0] & 0xFF;
        int b1 = b4[1] & 0xFF;
        if (b0 == 0xFE && b1 == 0xFF) {
            // UTF-16, big-endian
            return new Object [] {"UTF-16BE", new Boolean(true)};
        }
        if (b0 == 0xFF && b1 == 0xFE) {
            // UTF-16, little-endian
            return new Object [] {"UTF-16LE", new Boolean(false)};
        }

        // default to UTF-8 if we don't have enough bytes to make a
        // good determination of the encoding
        if (count < 3) {
            return new Object [] {"UTF-8", null};
        }

        // UTF-8 with a BOM
        int b2 = b4[2] & 0xFF;
        if (b0 == 0xEF && b1 == 0xBB && b2 == 0xBF) {
            return new Object [] {"UTF-8", null};
        }

        // default to UTF-8 if we don't have enough bytes to make a
        // good determination of the encoding
        if (count < 4) {
            return new Object [] {"UTF-8", null};
        }

        // other encodings
        int b3 = b4[3] & 0xFF;
        if (b0 == 0x00 && b1 == 0x00 && b2 == 0x00 && b3 == 0x3C) {
            // UCS-4, big endian (1234)
            return new Object [] {"ISO-10646-UCS-4", new Boolean(true)};
        }
        if (b0 == 0x3C && b1 == 0x00 && b2 == 0x00 && b3 == 0x00) {
            // UCS-4, little endian (4321)
            return new Object [] {"ISO-10646-UCS-4", new Boolean(false)};
        }
        if (b0 == 0x00 && b1 == 0x00 && b2 == 0x3C && b3 == 0x00) {
            // UCS-4, unusual octet order (2143)
            // REVISIT: What should this be?
            return new Object [] {"ISO-10646-UCS-4", null};
        }
        if (b0 == 0x00 && b1 == 0x3C && b2 == 0x00 && b3 == 0x00) {
            // UCS-4, unusual octect order (3412)
            // REVISIT: What should this be?
            return new Object [] {"ISO-10646-UCS-4", null};
        }
        if (b0 == 0x00 && b1 == 0x3C && b2 == 0x00 && b3 == 0x3F) {
            // UTF-16, big-endian, no BOM
            // (or could turn out to be UCS-2...
            // REVISIT: What should this be?
            return new Object [] {"UTF-16BE", new Boolean(true)};
        }
        if (b0 == 0x3C && b1 == 0x00 && b2 == 0x3F && b3 == 0x00) {
            // UTF-16, little-endian, no BOM
            // (or could turn out to be UCS-2...
            return new Object [] {"UTF-16LE", new Boolean(false)};
        }
        if (b0 == 0x4C && b1 == 0x6F && b2 == 0xA7 && b3 == 0x94) {
            // EBCDIC
            // a la xerces1, return CP037 instead of EBCDIC here
            return new Object [] {"CP037", null};
        }

        // default encoding
        return new Object [] {"UTF-8", null};

    } // getEncodingName(byte[],int):Object[]

    /**
     * Creates a reader capable of reading the given input stream in
     * the specified encoding.
     *
     * @param inputStream  The input stream.
     * @param encoding     The encoding name that the input stream is
     *                     encoded using. If the user has specified that
     *                     Java encoding names are allowed, then the
     *                     encoding name may be a Java encoding name;
     *                     otherwise, it is an ianaEncoding name.
     * @param isBigEndian   For encodings (like uCS-4), whose names cannot
     *                      specify a byte order, this tells whether the order is bigEndian.  null menas
     *                      unknown or not relevant.
     *
     * @return Returns a reader.
     */
    protected Reader createReader(InputStream inputStream, String encoding, Boolean isBigEndian)
        throws IOException {

        // normalize encoding name
        if (encoding == null) {
            encoding = "UTF-8";
        }

        // try to use an optimized reader
        String ENCODING = encoding.toUpperCase(Locale.ENGLISH);
        if (ENCODING.equals("UTF-8")) {
            if (DEBUG_ENCODINGS) {
                System.out.println("$$$ creating UTF8Reader");
            }
            return new UTF8Reader(inputStream, fBufferSize, fErrorReporter.getMessageFormatter(XMLMessageFormatter.XML_DOMAIN), fErrorReporter.getLocale() );
        }
        if (ENCODING.equals("US-ASCII")) {
            if (DEBUG_ENCODINGS) {
                System.out.println("$$$ creating ASCIIReader");
            }
            return new ASCIIReader(inputStream, fBufferSize, fErrorReporter.getMessageFormatter(XMLMessageFormatter.XML_DOMAIN), fErrorReporter.getLocale());
        }
        if(ENCODING.equals("ISO-10646-UCS-4")) {
            if(isBigEndian != null) {
                boolean isBE = isBigEndian.booleanValue();
                if(isBE) {
                    return new UCSReader(inputStream, UCSReader.UCS4BE);
                } else {
                    return new UCSReader(inputStream, UCSReader.UCS4LE);
                }
            } else {
                fErrorReporter.reportError(XMLMessageFormatter.XML_DOMAIN,
                                       "EncodingByteOrderUnsupported",
                                       new Object[] { encoding },
                                       XMLErrorReporter.SEVERITY_FATAL_ERROR);
            }
        }
        if(ENCODING.equals("ISO-10646-UCS-2")) {
            if(isBigEndian != null) { // sould never happen with this encoding...
                boolean isBE = isBigEndian.booleanValue();
                if(isBE) {
                    return new UCSReader(inputStream, UCSReader.UCS2BE);
                } else {
                    return new UCSReader(inputStream, UCSReader.UCS2LE);
                }
            } else {
                fErrorReporter.reportError(XMLMessageFormatter.XML_DOMAIN,
                                       "EncodingByteOrderUnsupported",
                                       new Object[] { encoding },
                                       XMLErrorReporter.SEVERITY_FATAL_ERROR);
            }
        }

        // check for valid name
        boolean validIANA = XMLChar.isValidIANAEncoding(encoding);
        boolean validJava = XMLChar.isValidJavaEncoding(encoding);
        if (!validIANA || (fAllowJavaEncodings && !validJava)) {
            fErrorReporter.reportError(XMLMessageFormatter.XML_DOMAIN,
                                       "EncodingDeclInvalid",
                                       new Object[] { encoding },
                                       XMLErrorReporter.SEVERITY_FATAL_ERROR);
            // NOTE: AndyH suggested that, on failure, we use ISO Latin 1
            //       because every byte is a valid ISO Latin 1 character.
            //       It may not translate correctly but if we failed on
            //       the encoding anyway, then we're expecting the content
            //       of the document to be bad. This will just prevent an
            //       invalid UTF-8 sequence to be detected. This is only
            //       important when continue-after-fatal-error is turned
            //       on. -Ac
            encoding = "ISO-8859-1";
        }

        // try to use a Java reader
        String javaEncoding = EncodingMap.getIANA2JavaMapping(ENCODING);
        if (javaEncoding == null) {
            if(fAllowJavaEncodings) {
            javaEncoding = encoding;
            } else {
                fErrorReporter.reportError(XMLMessageFormatter.XML_DOMAIN,
                                       "EncodingDeclInvalid",
                                       new Object[] { encoding },
                                       XMLErrorReporter.SEVERITY_FATAL_ERROR);
                // see comment above.
                javaEncoding = "ISO8859_1";
            }
        }
        if (DEBUG_ENCODINGS) {
            System.out.print("$$$ creating Java InputStreamReader: encoding="+javaEncoding);
            if (javaEncoding == encoding) {
                System.out.print(" (IANA encoding)");
            }
            System.out.println();
        }
        return new InputStreamReader(inputStream, javaEncoding);

    } // createReader(InputStream,String, Boolean): Reader

    // returns an instance of XMLEntityScanner
    protected XMLEntityScanner createEntityScanner() {
        return new EntityScanner();
    } // createEntityScanner():  XMLEntityScanner

    //
    // Protected static methods
    //

    /**
     * Fixes a platform dependent filename to standard URI form.
     *
     * @param str The string to fix.
     *
     * @return Returns the fixed URI string.
     */
    protected static String fixURI(String str) {

        // handle platform dependent strings
        str = str.replace(java.io.File.separatorChar, '/');

        // Windows fix
        if (str.length() >= 2) {
            char ch1 = str.charAt(1);
            // change "C:blah" to "/C:blah"
            if (ch1 == ':') {
                char ch0 = Character.toUpperCase(str.charAt(0));
                if (ch0 >= 'A' && ch0 <= 'Z') {
                    str = "/" + str;
                }
            }
            // change "//blah" to "file://blah"
            else if (ch1 == '/' && str.charAt(0) == '/') {
                str = "file:" + str;
            }
        }

        // done
        return str;

    } // fixURI(String):String

    //
    // Package visible methods
    //

    /**
     * Returns the hashtable of declared entities.
     * <p>
     * <strong>REVISIT:</strong>
     * This should be done the "right" way by designing a better way to
     * enumerate the declared entities. For now, this method is needed
     * by the constructor that takes an XMLEntityManager parameter.
     */
    Hashtable getDeclaredEntities() {
        return fEntities;
    } // getDeclaredEntities():Hashtable

    /** Prints the contents of the buffer. */
    final void print() {
        if (DEBUG_BUFFER) {
            if (fCurrentEntity != null) {
                System.out.print('[');
                System.out.print(fCurrentEntity.count);
                System.out.print(' ');
                System.out.print(fCurrentEntity.position);
                if (fCurrentEntity.count > 0) {
                    System.out.print(" \"");
                    for (int i = 0; i < fCurrentEntity.count; i++) {
                        if (i == fCurrentEntity.position) {
                            System.out.print('^');
                        }
                        char c = fCurrentEntity.ch[i];
                        switch (c) {
                            case '\n': {
                                System.out.print("\\n");
                                break;
                            }
                            case '\r': {
                                System.out.print("\\r");
                                break;
                            }
                            case '\t': {
                                System.out.print("\\t");
                                break;
                            }
                            case '\\': {
                                System.out.print("\\\\");
                                break;
                            }
                            default: {
                                System.out.print(c);
                            }
                        }
                    }
                    if (fCurrentEntity.position == fCurrentEntity.count) {
                        System.out.print('^');
                    }
                    System.out.print('"');
                }
                System.out.print(']');
                System.out.print(" @ ");
                System.out.print(fCurrentEntity.lineNumber);
                System.out.print(',');
                System.out.print(fCurrentEntity.columnNumber);
            }
            else {
                System.out.print("*NO CURRENT ENTITY*");
            }
        }
    } // print()

    //
    // Classes
    //

    /**
     * Entity information.
     *
     * @author Andy Clark, IBM
     */
    protected static abstract class Entity {

        //
        // Data
        //

        /** Entity name. */
        public String name;

        // whether this entity's declaration was found in the internal
        // or external subset
        public boolean inExternalSubset; 

        //
        // Constructors
        //

        /** Default constructor. */
        public Entity() {
            clear();
        } // <init>()

        /** Constructs an entity. */
        public Entity(String name, boolean inExternalSubset) {
            this.name = name;
            this.inExternalSubset = inExternalSubset;
        } // <init>(String)

        //
        // Public methods
        //

        /** Returns true if this entity was declared in the external subset. */
        public boolean isEntityDeclInExternalSubset () {
            return inExternalSubset;
        } 

        /** Returns true if this is an external entity. */
        public abstract boolean isExternal();

        /** Returns true if this is an unparsed entity. */
        public abstract boolean isUnparsed();

        /** Clears the entity. */
        public void clear() {
            name = null;
            inExternalSubset = false;
        } // clear()

        /** Sets the values of the entity. */
        public void setValues(Entity entity) {
            name = entity.name;
            inExternalSubset = entity.inExternalSubset;
        } // setValues(Entity)

    } // class Entity

    /**
     * Internal entity.
     *
     * @author Andy Clark, IBM
     */
    protected static class InternalEntity
        extends Entity {

        //
        // Data
        //

        /** Text value of entity. */
        public String text;

        //
        // Constructors
        //

        /** Default constructor. */
        public InternalEntity() {
            clear();
        } // <init>()

        /** Constructs an internal entity. */
        public InternalEntity(String name, String text, boolean inExternalSubset) {
            super(name,inExternalSubset);
            this.text = text;
        } // <init>(String,String)

        //
        // Entity methods
        //

        /** Returns true if this is an external entity. */
        public final boolean isExternal() {
            return false;
        } // isExternal():boolean

        /** Returns true if this is an unparsed entity. */
        public final boolean isUnparsed() {
            return false;
        } // isUnparsed():boolean

        /** Clears the entity. */
        public void clear() {
            super.clear();
            text = null;
        } // clear()

        /** Sets the values of the entity. */
        public void setValues(Entity entity) {
            super.setValues(entity);
            text = null;
        } // setValues(Entity)

        /** Sets the values of the entity. */
        public void setValues(InternalEntity entity) {
            super.setValues(entity);
            text = entity.text;
        } // setValues(InternalEntity)

    } // class InternalEntity

    /**
     * External entity.
     *
     * @author Andy Clark, IBM
     */
    protected static class ExternalEntity
        extends Entity {

        //
        // Data
        //

        /** container for all relevant entity location information. */
        public XMLResourceIdentifier entityLocation;

        /** Notation name for unparsed entity. */
        public String notation;

        //
        // Constructors
        //

        /** Default constructor. */
        public ExternalEntity() {
            clear();
        } // <init>()

        /** Constructs an internal entity. */
        public ExternalEntity(String name, XMLResourceIdentifier entityLocation,
                              String notation, boolean inExternalSubset) {
            super(name,inExternalSubset);
            this.entityLocation = entityLocation;
            this.notation = notation;
        } // <init>(String,XMLResourceIdentifier, String)

        //
        // Entity methods
        //

        /** Returns true if this is an external entity. */
        public final boolean isExternal() {
            return true;
        } // isExternal():boolean

        /** Returns true if this is an unparsed entity. */
        public final boolean isUnparsed() {
            return notation != null;
        } // isUnparsed():boolean

        /** Clears the entity. */
        public void clear() {
            super.clear();
            entityLocation = null;
            notation = null;
        } // clear()

        /** Sets the values of the entity. */
        public void setValues(Entity entity) {
            super.setValues(entity);
            entityLocation = null;
            notation = null;
        } // setValues(Entity)

        /** Sets the values of the entity. */
        public void setValues(ExternalEntity entity) {
            super.setValues(entity);
            entityLocation = entity.entityLocation;
            notation = entity.notation;
        } // setValues(ExternalEntity)

    } // class ExternalEntity

    /**
     * Entity state.
     *
     * @author Andy Clark, IBM
     */
    protected class ScannedEntity
        extends Entity {

        //
        // Data
        //

        // i/o

        /** Input stream. */
        public InputStream stream;

        /** Reader. */
        public Reader reader;

        // locator information

        /** entity location information */
        public XMLResourceIdentifier entityLocation;

        /** Line number. */
        public int lineNumber = 1;

        /** Column number. */
        public int columnNumber = 1;

        // encoding

        /** Auto-detected encoding. */
        public String encoding;

        // status

        /** True if in a literal.  */
        public boolean literal;

        // whether this is an external or internal scanned entity
        public boolean isExternal;

        // buffer

        /** Character buffer. */
        public char[] ch = null;

        /** Position in character buffer. */
        public int position;

        /** Count of characters in buffer. */
        public int count;

        // to allow the reader/inputStream to behave efficiently:
        public boolean mayReadChunks;

        //
        // Constructors
        //

        /** Constructs a scanned entity. */
        public ScannedEntity(String name,
                             XMLResourceIdentifier entityLocation,
                             InputStream stream, Reader reader,
                             String encoding, boolean literal, boolean mayReadChunks, boolean isExternal) {
            super(name,XMLEntityManager.this.fInExternalSubset);
            this.entityLocation = entityLocation;
            this.stream = stream;
            this.reader = reader;
            this.encoding = encoding;
            this.literal = literal;
            this.mayReadChunks = mayReadChunks;
            this.isExternal = isExternal;
            this.ch = new char[isExternal ? fBufferSize : DEFAULT_INTERNAL_BUFFER_SIZE];
        } // <init>(StringXMLResourceIdentifier,InputStream,Reader,String,boolean, boolean)

        //
        // Entity methods
        //

        /** Returns true if this is an external entity. */
        public final boolean isExternal() {
            return isExternal;
        } // isExternal():boolean

        /** Returns true if this is an unparsed entity. */
        public final boolean isUnparsed() {
            return false;
        } // isUnparsed():boolean

        //
        // Object methods
        //

        /** Returns a string representation of this object. */
        public String toString() {

            StringBuffer str = new StringBuffer();
            str.append("name=\""+name+'"');
            str.append(",ch="+ch);
            str.append(",position="+position);
            str.append(",count="+count);
            return str.toString();

        } // toString():String

    } // class ScannedEntity

    /**
     * Implements the entity scanner methods.
     *
     * @author Andy Clark, IBM
     */
    protected class EntityScanner
        extends XMLEntityScanner {

        //
        // Constructors
        //

        /** Default constructor. */
        public EntityScanner() {
        } // <init>()

        //
        // XMLEntityScanner methods
        //

        /**
         * Returns the base system identifier of the currently scanned
         * entity, or null if none is available.
         */
        public String getBaseSystemId() {
            return (fCurrentEntity != null && fCurrentEntity.entityLocation != null) ? fCurrentEntity.entityLocation.getExpandedSystemId() : null;
        } // getBaseSystemId():String

        /**
         * Sets the encoding of the scanner. This method is used by the
         * scanners if the XMLDecl or TextDecl line contains an encoding
         * pseudo-attribute.
         * <p>
         * <strong>Note:</strong> The underlying character reader on the
         * current entity will be changed to accomodate the new encoding.
         * However, the new encoding is ignored if the current reader was
         * not constructed from an input stream (e.g. an external entity
         * that is resolved directly to the appropriate java.io.Reader
         * object).
         *
         * @param encoding The IANA encoding name of the new encoding.
         *
         * @throws IOException Thrown if the new encoding is not supported.
         *
         * @see org.apache.xerces.util.EncodingMap
         */
        public void setEncoding(String encoding) throws IOException {

            if (DEBUG_ENCODINGS) {
                System.out.println("$$$ setEncoding: "+encoding);
            }

            if (fCurrentEntity.stream != null) {
                // if the encoding is the same, don't change the reader and
                // re-use the original reader used by the OneCharReader
                // NOTE: Besides saving an object, this overcomes deficiencies
                //       in the UTF-16 reader supplied with the standard Java
                //       distribution (up to and including 1.3). The UTF-16
                //       decoder buffers 8K blocks even when only asked to read
                //       a single char! -Ac
                if (fCurrentEntity.encoding == null ||
                    !fCurrentEntity.encoding.equals(encoding)) {
                    // UTF-16 is a bit of a special case.  If the encoding is UTF-16,
                    // and we know the endian-ness, we shouldn't change readers.
                    // If it's ISO-10646-UCS-(2|4), then we'll have to deduce
                    // the endian-ness from the encoding we presently have.
                    if(fCurrentEntity.encoding != null && fCurrentEntity.encoding.startsWith("UTF-16")) {
                        String ENCODING = encoding.toUpperCase(Locale.ENGLISH);
                        if(ENCODING.equals("UTF-16")) return;
                        if(ENCODING.equals("ISO-10646-UCS-4")) {
                            if(fCurrentEntity.encoding.equals("UTF-16BE")) {
                                fCurrentEntity.reader = new UCSReader(fCurrentEntity.stream, UCSReader.UCS4BE);
                            } else {
                                fCurrentEntity.reader = new UCSReader(fCurrentEntity.stream, UCSReader.UCS4LE);
                            }
                            return;
                        }
                        if(ENCODING.equals("ISO-10646-UCS-2")) {
                            if(fCurrentEntity.encoding.equals("UTF-16BE")) {
                                fCurrentEntity.reader = new UCSReader(fCurrentEntity.stream, UCSReader.UCS2BE);
                            } else {
                                fCurrentEntity.reader = new UCSReader(fCurrentEntity.stream, UCSReader.UCS2LE);
                            }
                            return;
                        }
                    }
                    // wrap a new reader around the input stream, changing
                    // the encoding
                    if (DEBUG_ENCODINGS) {
                        System.out.println("$$$ creating new reader from stream: "+
                                        fCurrentEntity.stream);
                    }
                    //fCurrentEntity.stream.reset();
                    fCurrentEntity.reader = createReader(fCurrentEntity.stream, encoding, null);
                } else {
                    if (DEBUG_ENCODINGS)
                        System.out.println("$$$ reusing old reader on stream");
                }
            }

        } // setEncoding(String)

        /** Returns true if the current entity being scanned is external. */
        public boolean isExternal() {
            return fCurrentEntity.isExternal();
        } // isExternal():boolean

        /**
         * Returns the next character on the input.
         * <p>
         * <strong>Note:</strong> The character is <em>not</em> consumed.
         *
         * @throws IOException  Thrown if i/o error occurs.
         * @throws EOFException Thrown on end of file.
         */
        public int peekChar() throws IOException {
            if (DEBUG_BUFFER) {
                System.out.print("(peekChar: ");
                print();
                System.out.println();
            }

            // load more characters, if needed
            if (fCurrentEntity.position == fCurrentEntity.count) {
                load(0, true);
            }

            // peek at character
            int c = fCurrentEntity.ch[fCurrentEntity.position];

            // return peeked character
            if (DEBUG_BUFFER) {
                System.out.print(")peekChar: ");
                print();
                if (fCurrentEntity.isExternal()) {
                    System.out.println(" -> '"+(c!='\r'?(char)c:'\n')+"'");
                }
                else {
                    System.out.println(" -> '"+(char)c+"'");
                }
            }
            if (fCurrentEntity.isExternal()) {
                return c != '\r' ? c : '\n';
            }
            else {
                return c;
            }

        } // peekChar():int

        /**
         * Returns the next character on the input.
         * <p>
         * <strong>Note:</strong> The character is consumed.
         *
         * @throws IOException  Thrown if i/o error occurs.
         * @throws EOFException Thrown on end of file.
         */
        public int scanChar() throws IOException {
            if (DEBUG_BUFFER) {
                System.out.print("(scanChar: ");
                print();
                System.out.println();
            }

            // load more characters, if needed
            if (fCurrentEntity.position == fCurrentEntity.count) {
                load(0, true);
            }

            // scan character
            int c = fCurrentEntity.ch[fCurrentEntity.position++];
            boolean external = false;
            if (c == '\n' ||
                (c == '\r' && (external = fCurrentEntity.isExternal()))) {
                fCurrentEntity.lineNumber++;
                fCurrentEntity.columnNumber = 1;
                if (fCurrentEntity.position == fCurrentEntity.count) {
                    fCurrentEntity.ch[0] = (char)c;
                    load(1, false);
                }
                if (c == '\r' && external) {
                    if (fCurrentEntity.ch[fCurrentEntity.position++] != '\n') {
                        fCurrentEntity.position--;
                    }
                    c = '\n';
                }
            }

            // return character that was scanned
            if (DEBUG_BUFFER) {
                System.out.print(")scanChar: ");
                print();
                System.out.println(" -> '"+(char)c+"'");
            }
            fCurrentEntity.columnNumber++;
            return c;

        } // scanChar():int

        /**
         * Returns a string matching the NMTOKEN production appearing immediately
         * on the input as a symbol, or null if NMTOKEN Name string is present.
         * <p>
         * <strong>Note:</strong> The NMTOKEN characters are consumed.
         * <p>
         * <strong>Note:</strong> The string returned must be a symbol. The
         * SymbolTable can be used for this purpose.
         *
         * @throws IOException  Thrown if i/o error occurs.
         * @throws EOFException Thrown on end of file.
         *
         * @see org.apache.xerces.util.SymbolTable
         * @see org.apache.xerces.util.XMLChar#isName
         */
        public String scanNmtoken() throws IOException {
            if (DEBUG_BUFFER) {
                System.out.print("(scanNmtoken: ");
                print();
                System.out.println();
            }

            // load more characters, if needed
            if (fCurrentEntity.position == fCurrentEntity.count) {
                load(0, true);
            }

            // scan nmtoken
            int offset = fCurrentEntity.position;
            while (XMLChar.isName(fCurrentEntity.ch[fCurrentEntity.position])) {
                if (++fCurrentEntity.position == fCurrentEntity.count) {
                    int length = fCurrentEntity.position - offset;
                    if (length == fBufferSize) {
                        // bad luck we have to resize our buffer
                        char[] tmp = new char[fBufferSize * 2];
                        System.arraycopy(fCurrentEntity.ch, offset,
                                         tmp, 0, length);
                        fCurrentEntity.ch = tmp;
                        fBufferSize *= 2;
                    }
                    else {
                        System.arraycopy(fCurrentEntity.ch, offset,
                                         fCurrentEntity.ch, 0, length);
                    }
                    offset = 0;
                    if (load(length, false)) {
                        break;
                    }
                }
            }
            int length = fCurrentEntity.position - offset;
            fCurrentEntity.columnNumber += length;

            // return nmtoken
            String symbol = null;
            if (length > 0) {
                symbol = fSymbolTable.addSymbol(fCurrentEntity.ch, offset, length);
            }
            if (DEBUG_BUFFER) {
                System.out.print(")scanNmtoken: ");
                print();
                System.out.println(" -> "+String.valueOf(symbol));
            }
            return symbol;

        } // scanNmtoken():String

        /**
         * Returns a string matching the Name production appearing immediately
         * on the input as a symbol, or null if no Name string is present.
         * <p>
         * <strong>Note:</strong> The Name characters are consumed.
         * <p>
         * <strong>Note:</strong> The string returned must be a symbol. The
         * SymbolTable can be used for this purpose.
         *
         * @throws IOException  Thrown if i/o error occurs.
         * @throws EOFException Thrown on end of file.
         *
         * @see org.apache.xerces.util.SymbolTable
         * @see org.apache.xerces.util.XMLChar#isName
         * @see org.apache.xerces.util.XMLChar#isNameStart
         */
        public String scanName() throws IOException {
            if (DEBUG_BUFFER) {
                System.out.print("(scanName: ");
                print();
                System.out.println();
            }

            // load more characters, if needed
            if (fCurrentEntity.position == fCurrentEntity.count) {
                load(0, true);
            }

            // scan name
            int offset = fCurrentEntity.position;
            if (XMLChar.isNameStart(fCurrentEntity.ch[offset])) {
                if (++fCurrentEntity.position == fCurrentEntity.count) {
                    fCurrentEntity.ch[0] = fCurrentEntity.ch[offset];
                    offset = 0;
                    if (load(1, false)) {
                        fCurrentEntity.columnNumber++;
                        String symbol = fSymbolTable.addSymbol(fCurrentEntity.ch, 0, 1);
                        if (DEBUG_BUFFER) {
                            System.out.print(")scanName: ");
                            print();
                            System.out.println(" -> "+String.valueOf(symbol));
                        }
                        return symbol;
                    }
                }
                while (XMLChar.isName(fCurrentEntity.ch[fCurrentEntity.position])) {
                    if (++fCurrentEntity.position == fCurrentEntity.count) {
                        int length = fCurrentEntity.position - offset;
                        if (length == fBufferSize) {
                            // bad luck we have to resize our buffer
                            char[] tmp = new char[fBufferSize * 2];
                            System.arraycopy(fCurrentEntity.ch, offset,
                                             tmp, 0, length);
                            fCurrentEntity.ch = tmp;
                            fBufferSize *= 2;
                        }
                        else {
                            System.arraycopy(fCurrentEntity.ch, offset,
                                             fCurrentEntity.ch, 0, length);
                        }
                        offset = 0;
                        if (load(length, false)) {
                            break;
                        }
                    }
                }
            }
            int length = fCurrentEntity.position - offset;
            fCurrentEntity.columnNumber += length;

            // return name
            String symbol = null;
            if (length > 0) {
                symbol = fSymbolTable.addSymbol(fCurrentEntity.ch, offset, length);
            }
            if (DEBUG_BUFFER) {
                System.out.print(")scanName: ");
                print();
                System.out.println(" -> "+String.valueOf(symbol));
            }
            return symbol;

        } // scanName():String

        /**
         * Scans a qualified name from the input, setting the fields of the
         * QName structure appropriately.
         * <p>
         * <strong>Note:</strong> The qualified name characters are consumed.
         * <p>
         * <strong>Note:</strong> The strings used to set the values of the
         * QName structure must be symbols. The SymbolTable can be used for
         * this purpose.
         *
         * @param qname The qualified name structure to fill.
         *
         * @return Returns true if a qualified name appeared immediately on
         *         the input and was scanned, false otherwise.
         *
         * @throws IOException  Thrown if i/o error occurs.
         * @throws EOFException Thrown on end of file.
         *
         * @see org.apache.xerces.util.SymbolTable
         * @see org.apache.xerces.util.XMLChar#isName
         * @see org.apache.xerces.util.XMLChar#isNameStart
         */
        public boolean scanQName(QName qname) throws IOException {
            if (DEBUG_BUFFER) {
                System.out.print("(scanQName, "+qname+": ");
                print();
                System.out.println();
            }

            // load more characters, if needed
            if (fCurrentEntity.position == fCurrentEntity.count) {
                load(0, true);
            }

            // scan qualified name
            int offset = fCurrentEntity.position;
            if (XMLChar.isNameStart(fCurrentEntity.ch[offset])) {
                if (++fCurrentEntity.position == fCurrentEntity.count) {
                    fCurrentEntity.ch[0] = fCurrentEntity.ch[offset];
                    offset = 0;
                    if (load(1, false)) {
                        fCurrentEntity.columnNumber++;
                        String name =
                            fSymbolTable.addSymbol(fCurrentEntity.ch, 0, 1);
                        qname.setValues(null, name, name, null);
                        if (DEBUG_BUFFER) {
                            System.out.print(")scanQName, "+qname+": ");
                            print();
                            System.out.println(" -> true");
                        }
                        return true;
                    }
                }
                int index = -1;
                while (XMLChar.isName(fCurrentEntity.ch[fCurrentEntity.position])) {
                    char c = fCurrentEntity.ch[fCurrentEntity.position];
                    if (c == ':') {
                        if (index != -1) {
                            break;
                        }
                        index = fCurrentEntity.position;
                    }
                    if (++fCurrentEntity.position == fCurrentEntity.count) {
                        int length = fCurrentEntity.position - offset;
                        if (length == fBufferSize) {
                            // bad luck we have to resize our buffer
                            char[] tmp = new char[fBufferSize * 2];
                            System.arraycopy(fCurrentEntity.ch, offset,
                                             tmp, 0, length);
                            fCurrentEntity.ch = tmp;
                            fBufferSize *= 2;
                        }
                        else {
                            System.arraycopy(fCurrentEntity.ch, offset,
                                             fCurrentEntity.ch, 0, length);
                        }
                        if (index != -1) {
                            index = index - offset;
                        }
                        offset = 0;
                        if (load(length, false)) {
                            break;
                        }
                    }
                }
                int length = fCurrentEntity.position - offset;
                fCurrentEntity.columnNumber += length;
                if (length > 0) {
                    String prefix = null;
                    String localpart = null;
                    String rawname = fSymbolTable.addSymbol(fCurrentEntity.ch,
                                                            offset, length);
                    if (index != -1) {
                        int prefixLength = index - offset;
                        prefix = fSymbolTable.addSymbol(fCurrentEntity.ch,
                                                        offset, prefixLength);
                        int len = length - prefixLength - 1;
                        localpart = fSymbolTable.addSymbol(fCurrentEntity.ch,
                                                           index + 1, len);

                    }
                    else {
                        localpart = rawname;
                    }
                    qname.setValues(prefix, localpart, rawname, null);
                    if (DEBUG_BUFFER) {
                        System.out.print(")scanQName, "+qname+": ");
                        print();
                        System.out.println(" -> true");
                    }
                    return true;
                }
            }

            // no qualified name found
            if (DEBUG_BUFFER) {
                System.out.print(")scanQName, "+qname+": ");
                print();
                System.out.println(" -> false");
            }
            return false;

        } // scanQName(QName):boolean

        /**
         * Scans a range of parsed character data, setting the fields of the
         * XMLString structure, appropriately.
         * <p>
         * <strong>Note:</strong> The characters are consumed.
         * <p>
         * <strong>Note:</strong> This method does not guarantee to return
         * the longest run of parsed character data. This method may return
         * before markup due to reaching the end of the input buffer or any
         * other reason.
         * <p>
         * <strong>Note:</strong> The fields contained in the XMLString
         * structure are not guaranteed to remain valid upon subsequent calls
         * to the entity scanner. Therefore, the caller is responsible for
         * immediately using the returned character data or making a copy of
         * the character data.
         *
         * @param content The content structure to fill.
         *
         * @return Returns the next character on the input, if known. This
         *         value may be -1 but this does <em>note</em> designate
         *         end of file.
         *
         * @throws IOException  Thrown if i/o error occurs.
         * @throws EOFException Thrown on end of file.
         */
        public int scanContent(XMLString content) throws IOException {
            if (DEBUG_BUFFER) {
                System.out.print("(scanContent: ");
                print();
                System.out.println();
            }

            // load more characters, if needed
            if (fCurrentEntity.position == fCurrentEntity.count) {
                load(0, true);
            }
            else if (fCurrentEntity.position == fCurrentEntity.count - 1) {
                fCurrentEntity.ch[0] = fCurrentEntity.ch[fCurrentEntity.count - 1];
                load(1, false);
                fCurrentEntity.position = 0;
            }

            // normalize newlines
            int offset = fCurrentEntity.position;
            int c = fCurrentEntity.ch[offset];
            int newlines = 0;
            boolean external = fCurrentEntity.isExternal();
            if (c == '\n' || (c == '\r' && external)) {
                if (DEBUG_BUFFER) {
                    System.out.print("[newline, "+offset+", "+fCurrentEntity.position+": ");
                    print();
                    System.out.println();
                }
                do {
                    c = fCurrentEntity.ch[fCurrentEntity.position++];
                    if (c == '\r' && external) {
                        newlines++;
                        fCurrentEntity.lineNumber++;
                        fCurrentEntity.columnNumber = 1;
                        if (fCurrentEntity.position == fCurrentEntity.count) {
                            offset = 0;
                            fCurrentEntity.position = newlines;
                            if (load(newlines, false)) {
                                break;
                            }
                        }
                        if (fCurrentEntity.ch[fCurrentEntity.position] == '\n') {
                            fCurrentEntity.position++;
                            offset++;
                        }
                        /*** NEWLINE NORMALIZATION ***/
                        else {
                            newlines++;
                        }
                    }
                    else if (c == '\n') {
                        newlines++;
                        fCurrentEntity.lineNumber++;
                        fCurrentEntity.columnNumber = 1;
                        if (fCurrentEntity.position == fCurrentEntity.count) {
                            offset = 0;
                            fCurrentEntity.position = newlines;
                            if (load(newlines, false)) {
                                break;
                            }
                        }
                    }
                    else {
                        fCurrentEntity.position--;
                        break;
                    }
                } while (fCurrentEntity.position < fCurrentEntity.count - 1);
                for (int i = offset; i < fCurrentEntity.position; i++) {
                    fCurrentEntity.ch[i] = '\n';
                }
                int length = fCurrentEntity.position - offset;
                if (fCurrentEntity.position == fCurrentEntity.count - 1) {
                    content.setValues(fCurrentEntity.ch, offset, length);
                    if (DEBUG_BUFFER) {
                        System.out.print("]newline, "+offset+", "+fCurrentEntity.position+": ");
                        print();
                        System.out.println();
                    }
                    return -1;
                }
                if (DEBUG_BUFFER) {
                    System.out.print("]newline, "+offset+", "+fCurrentEntity.position+": ");
                    print();
                    System.out.println();
                }
            }

            // inner loop, scanning for content
            while (fCurrentEntity.position < fCurrentEntity.count) {
                c = fCurrentEntity.ch[fCurrentEntity.position++];
                if (!XMLChar.isContent(c)) {
                    fCurrentEntity.position--;
                    break;
                }
            }
            int length = fCurrentEntity.position - offset;
            fCurrentEntity.columnNumber += length - newlines;
            content.setValues(fCurrentEntity.ch, offset, length);

            // return next character
            if (fCurrentEntity.position != fCurrentEntity.count) {
                c = fCurrentEntity.ch[fCurrentEntity.position];
                // REVISIT: Does this need to be updated to fix the
                //          #x0D ^#x0A newline normalization problem? -Ac
                if (c == '\r' && external) {
                    c = '\n';
                }
            }
            else {
                c = -1;
            }
            if (DEBUG_BUFFER) {
                System.out.print(")scanContent: ");
                print();
                System.out.println(" -> '"+(char)c+"'");
            }
            return c;

        } // scanContent(XMLString):int

        /**
         * Scans a range of attribute value data, setting the fields of the
         * XMLString structure, appropriately.
         * <p>
         * <strong>Note:</strong> The characters are consumed.
         * <p>
         * <strong>Note:</strong> This method does not guarantee to return
         * the longest run of attribute value data. This method may return
         * before the quote character due to reaching the end of the input
         * buffer or any other reason.
         * <p>
         * <strong>Note:</strong> The fields contained in the XMLString
         * structure are not guaranteed to remain valid upon subsequent calls
         * to the entity scanner. Therefore, the caller is responsible for
         * immediately using the returned character data or making a copy of
         * the character data.
         *
         * @param quote   The quote character that signifies the end of the
         *                attribute value data.
         * @param content The content structure to fill.
         *
         * @return Returns the next character on the input, if known. This
         *         value may be -1 but this does <em>note</em> designate
         *         end of file.
         *
         * @throws IOException  Thrown if i/o error occurs.
         * @throws EOFException Thrown on end of file.
         */
        public int scanLiteral(int quote, XMLString content)
            throws IOException {
            if (DEBUG_BUFFER) {
                System.out.print("(scanLiteral, '"+(char)quote+"': ");
                print();
                System.out.println();
            }

            // load more characters, if needed
            if (fCurrentEntity.position == fCurrentEntity.count) {
                load(0, true);
            }
            else if (fCurrentEntity.position == fCurrentEntity.count - 1) {
                fCurrentEntity.ch[0] = fCurrentEntity.ch[fCurrentEntity.count - 1];
                load(1, false);
                fCurrentEntity.position = 0;
            }

            // normalize newlines
            int offset = fCurrentEntity.position;
            int c = fCurrentEntity.ch[offset];
            int newlines = 0;
            boolean external = fCurrentEntity.isExternal();
            if (c == '\n' || (c == '\r' && external)) {
                if (DEBUG_BUFFER) {
                    System.out.print("[newline, "+offset+", "+fCurrentEntity.position+": ");
                    print();
                    System.out.println();
                }
                do {
                    c = fCurrentEntity.ch[fCurrentEntity.position++];
                    if (c == '\r' && external) {
                        newlines++;
                        fCurrentEntity.lineNumber++;
                        fCurrentEntity.columnNumber = 1;
                        if (fCurrentEntity.position == fCurrentEntity.count) {
                            offset = 0;
                            fCurrentEntity.position = newlines;
                            if (load(newlines, false)) {
                                break;
                            }
                        }
                        if (fCurrentEntity.ch[fCurrentEntity.position] == '\n') {
                            fCurrentEntity.position++;
                            offset++;
                        }
                        /*** NEWLINE NORMALIZATION ***/
                        else {
                            newlines++;
                        }
                        /***/
                    }
                    else if (c == '\n') {
                        newlines++;
                        fCurrentEntity.lineNumber++;
                        fCurrentEntity.columnNumber = 1;
                        if (fCurrentEntity.position == fCurrentEntity.count) {
                            offset = 0;
                            fCurrentEntity.position = newlines;
                            if (load(newlines, false)) {
                                break;
                            }
                        }
                        /*** NEWLINE NORMALIZATION ***
                        if (fCurrentEntity.ch[fCurrentEntity.position] == '\r'
                            && external) {
                            fCurrentEntity.position++;
                            offset++;
                        }
                        /***/
                    }
                    else {
                        fCurrentEntity.position--;
                        break;
                    }
                } while (fCurrentEntity.position < fCurrentEntity.count - 1);
                for (int i = offset; i < fCurrentEntity.position; i++) {
                    fCurrentEntity.ch[i] = '\n';
                }
                int length = fCurrentEntity.position - offset;
                if (fCurrentEntity.position == fCurrentEntity.count - 1) {
                    content.setValues(fCurrentEntity.ch, offset, length);
                    if (DEBUG_BUFFER) {
                        System.out.print("]newline, "+offset+", "+fCurrentEntity.position+": ");
                        print();
                        System.out.println();
                    }
                    return -1;
                }
                if (DEBUG_BUFFER) {
                    System.out.print("]newline, "+offset+", "+fCurrentEntity.position+": ");
                    print();
                    System.out.println();
                }
            }

            // scan literal value
            while (fCurrentEntity.position < fCurrentEntity.count) {
                c = fCurrentEntity.ch[fCurrentEntity.position++];
                if ((c == quote &&
                     (!fCurrentEntity.literal || external))
                    || c == '%' || !XMLChar.isContent(c)) {
                    fCurrentEntity.position--;
                    break;
                }
            }
            int length = fCurrentEntity.position - offset;
            fCurrentEntity.columnNumber += length - newlines;
            content.setValues(fCurrentEntity.ch, offset, length);

            // return next character
            if (fCurrentEntity.position != fCurrentEntity.count) {
                c = fCurrentEntity.ch[fCurrentEntity.position];
                // NOTE: We don't want to accidentally signal the
                //       end of the literal if we're expanding an
                //       entity appearing in the literal. -Ac
                if (c == quote && fCurrentEntity.literal) {
                    c = -1;
                }
            }
            else {
                c = -1;
            }
            if (DEBUG_BUFFER) {
                System.out.print(")scanLiteral, '"+(char)quote+"': ");
                print();
                System.out.println(" -> '"+(char)c+"'");
            }
            return c;

        } // scanLiteral(int,XMLString):int

        /**
         * Scans a range of character data up to the specified delimiter,
         * setting the fields of the XMLString structure, appropriately.
         * <p>
         * <strong>Note:</strong> The characters are consumed.
         * <p>
         * <strong>Note:</strong> This assumes that the internal buffer is
         * at least the same size, or bigger, than the length of the delimiter
         * and that the delimiter contains at least one character.
         * <p>
         * <strong>Note:</strong> This method does not guarantee to return
         * the longest run of character data. This method may return before
         * the delimiter due to reaching the end of the input buffer or any
         * other reason.
         * <p>
         * <strong>Note:</strong> The fields contained in the XMLString
         * structure are not guaranteed to remain valid upon subsequent calls
         * to the entity scanner. Therefore, the caller is responsible for
         * immediately using the returned character data or making a copy of
         * the character data.
         *
         * @param delimiter The string that signifies the end of the character
         *                  data to be scanned.
         * @param data      The data structure to fill.
         *
         * @return Returns true if there is more data to scan, false otherwise.
         *
         * @throws IOException  Thrown if i/o error occurs.
         * @throws EOFException Thrown on end of file.
         */
        public boolean scanData(String delimiter, XMLStringBuffer buffer)
            throws IOException {

            boolean done = false;
            int delimLen = delimiter.length();
            char charAt0 = delimiter.charAt(0);
            boolean external = fCurrentEntity.isExternal();
            do {
                if (DEBUG_BUFFER) {
                    System.out.print("(scanData: ");
                    print();
                    System.out.println();
                }
    
                // load more characters, if needed
    
                if (fCurrentEntity.position == fCurrentEntity.count) {
                    load(0, true);
                }
                else if (fCurrentEntity.position >= fCurrentEntity.count - delimLen) {
                    System.arraycopy(fCurrentEntity.ch, fCurrentEntity.position,
                                     fCurrentEntity.ch, 0, fCurrentEntity.count - fCurrentEntity.position);
                    load(fCurrentEntity.count - fCurrentEntity.position, false);
                    fCurrentEntity.position = 0;
                } 
                if (fCurrentEntity.position >= fCurrentEntity.count - delimLen) {
                    // something must be wrong with the input:  e.g., file ends  an unterminated comment
                    int length = fCurrentEntity.count - fCurrentEntity.position;
                    buffer.append (fCurrentEntity.ch, fCurrentEntity.position, length); 
                    fCurrentEntity.columnNumber += fCurrentEntity.count;
                    fCurrentEntity.position = fCurrentEntity.count;
                    load(0,true);
                    return false;
                }
    
                // normalize newlines
                int offset = fCurrentEntity.position;
                int c = fCurrentEntity.ch[offset];
                int newlines = 0;
                if (c == '\n' || (c == '\r' && external)) {
                    if (DEBUG_BUFFER) {
                        System.out.print("[newline, "+offset+", "+fCurrentEntity.position+": ");
                        print();
                        System.out.println();
                    }
                    do {
                        c = fCurrentEntity.ch[fCurrentEntity.position++];
                        if (c == '\r' && external) {
                            newlines++;
                            fCurrentEntity.lineNumber++;
                            fCurrentEntity.columnNumber = 1;
                            if (fCurrentEntity.position == fCurrentEntity.count) {
                                offset = 0;
                                fCurrentEntity.position = newlines;
                                if (load(newlines, false)) {
                                    break;
                                }
                            }
                            if (fCurrentEntity.ch[fCurrentEntity.position] == '\n') {
                                fCurrentEntity.position++;
                                offset++;
                            }
                            /*** NEWLINE NORMALIZATION ***/
                            else {
                                newlines++;
                            }
                        }
                        else if (c == '\n') {
                            newlines++;
                            fCurrentEntity.lineNumber++;
                            fCurrentEntity.columnNumber = 1;
                            if (fCurrentEntity.position == fCurrentEntity.count) {
                                offset = 0;
                                fCurrentEntity.position = newlines;
                                fCurrentEntity.count = newlines;
                                if (load(newlines, false)) {
                                    break;
                                }
                            }
                        }
                        else {
                            fCurrentEntity.position--;
                            break;
                        }
                    } while (fCurrentEntity.position < fCurrentEntity.count - 1);
                    for (int i = offset; i < fCurrentEntity.position; i++) {
                        fCurrentEntity.ch[i] = '\n';
                    }
                    int length = fCurrentEntity.position - offset;
                    if (fCurrentEntity.position == fCurrentEntity.count - 1) {
                        buffer.append(fCurrentEntity.ch, offset, length);
                        if (DEBUG_BUFFER) {
                            System.out.print("]newline, "+offset+", "+fCurrentEntity.position+": ");
                            print();
                            System.out.println();
                        }
                        return true;
                    }
                    if (DEBUG_BUFFER) {
                        System.out.print("]newline, "+offset+", "+fCurrentEntity.position+": ");
                        print();
                        System.out.println();
                    }
                }
    
                // iterate over buffer looking for delimiter
                OUTER: while (fCurrentEntity.position < fCurrentEntity.count) {
                    c = fCurrentEntity.ch[fCurrentEntity.position++];
                    if (c == charAt0) {
                        // looks like we just hit the delimiter
                        int delimOffset = fCurrentEntity.position - 1;
                        for (int i = 1; i < delimLen; i++) {
                            if (fCurrentEntity.position == fCurrentEntity.count) {
                                fCurrentEntity.position -= i;
                                break OUTER;
                            }
                            c = fCurrentEntity.ch[fCurrentEntity.position++];
                            if (delimiter.charAt(i) != c) {
                                fCurrentEntity.position--;
                                break;
                            }
                        }
                        if (fCurrentEntity.position == delimOffset + delimLen) {
                            done = true;
                            break;
                        }
                    }
                    else if (c == '\n' || (external && c == '\r')) {
                        fCurrentEntity.position--;
                        break;
                    }
                    else if (XMLChar.isInvalid(c)) {
                        fCurrentEntity.position--;
                        int length = fCurrentEntity.position - offset;
                        fCurrentEntity.columnNumber += length - newlines;
                        buffer.append(fCurrentEntity.ch, offset, length); 
                        return true;
                    }
                }
                int length = fCurrentEntity.position - offset;
                fCurrentEntity.columnNumber += length - newlines;
                if (done) {
                    length -= delimLen;
                }
                buffer.append (fCurrentEntity.ch, offset, length);
    
                // return true if string was skipped
                if (DEBUG_BUFFER) {
                    System.out.print(")scanData: ");
                    print();
                    System.out.println(" -> " + done);
                }
            } while (!done);
            return !done;

        } // scanData(String,XMLString)

        /**
         * Skips a character appearing immediately on the input.
         * <p>
         * <strong>Note:</strong> The character is consumed only if it matches
         * the specified character.
         *
         * @param c The character to skip.
         *
         * @return Returns true if the character was skipped.
         *
         * @throws IOException  Thrown if i/o error occurs.
         * @throws EOFException Thrown on end of file.
         */
        public boolean skipChar(int c) throws IOException {
            if (DEBUG_BUFFER) {
                System.out.print("(skipChar, '"+(char)c+"': ");
                print();
                System.out.println();
            }

            // load more characters, if needed
            if (fCurrentEntity.position == fCurrentEntity.count) {
                load(0, true);
            }

            // skip character
            int cc = fCurrentEntity.ch[fCurrentEntity.position];
            if (cc == c) {
                fCurrentEntity.position++;
                if (c == '\n') {
                    fCurrentEntity.lineNumber++;
                    fCurrentEntity.columnNumber = 1;
                }
                else {
                    fCurrentEntity.columnNumber++;
                }
                if (DEBUG_BUFFER) {
                    System.out.print(")skipChar, '"+(char)c+"': ");
                    print();
                    System.out.println(" -> true");
                }
                return true;
            }
            else if (c == '\n' && cc == '\r' && fCurrentEntity.isExternal()) {
                // handle newlines
                if (fCurrentEntity.position == fCurrentEntity.count) {
                    fCurrentEntity.ch[0] = (char)cc;
                    load(1, false);
                }
                fCurrentEntity.position++;
                if (fCurrentEntity.ch[fCurrentEntity.position] == '\n') {
                    fCurrentEntity.position++;
                }
                fCurrentEntity.lineNumber++;
                fCurrentEntity.columnNumber = 1;
                if (DEBUG_BUFFER) {
                    System.out.print(")skipChar, '"+(char)c+"': ");
                    print();
                    System.out.println(" -> true");
                }
                return true;
            }

            // character was not skipped
            if (DEBUG_BUFFER) {
                System.out.print(")skipChar, '"+(char)c+"': ");
                print();
                System.out.println(" -> false");
            }
            return false;

        } // skipChar(int):boolean

        /**
         * Skips space characters appearing immediately on the input.
         * <p>
         * <strong>Note:</strong> The characters are consumed only if they are
         * space characters.
         *
         * @return Returns true if at least one space character was skipped.
         *
         * @throws IOException  Thrown if i/o error occurs.
         * @throws EOFException Thrown on end of file.
         *
         * @see org.apache.xerces.util.XMLChar#isSpace
         */
        public boolean skipSpaces() throws IOException {
            if (DEBUG_BUFFER) {
                System.out.print("(skipSpaces: ");
                print();
                System.out.println();
            }

            // load more characters, if needed
            if (fCurrentEntity.position == fCurrentEntity.count) {
                load(0, true);
            }

            // skip spaces
            int c = fCurrentEntity.ch[fCurrentEntity.position];
            if (XMLChar.isSpace(c)) {
                boolean external = fCurrentEntity.isExternal();
                do {
                    boolean entityChanged = false;
                    // handle newlines
                    if (c == '\n' || (external && c == '\r')) {
                        fCurrentEntity.lineNumber++;
                        fCurrentEntity.columnNumber = 1;
                        if (fCurrentEntity.position == fCurrentEntity.count - 1) {
                            fCurrentEntity.ch[0] = (char)c;
                            entityChanged = load(1, true);
                            if (!entityChanged)
                                // the load change the position to be 1,
                                // need to restore it when entity not changed
                                fCurrentEntity.position = 0;
                        }
                        if (c == '\r' && external) {
                            // REVISIT: Does this need to be updated to fix the
                            //          #x0D ^#x0A newline normalization problem? -Ac
                            if (fCurrentEntity.ch[++fCurrentEntity.position] != '\n') {
                                fCurrentEntity.position--;
                            }
                        }
                        /*** NEWLINE NORMALIZATION ***
                        else {
                            if (fCurrentEntity.ch[fCurrentEntity.position + 1] == '\r'
                                && external) {
                                fCurrentEntity.position++;
                            }
                        }
                        /***/
                    }
                    else {
                        fCurrentEntity.columnNumber++;
                    }
                    // load more characters, if needed
                    if (!entityChanged)
                        fCurrentEntity.position++;
                    if (fCurrentEntity.position == fCurrentEntity.count) {
                        load(0, true);
                    }
                } while (XMLChar.isSpace(c = fCurrentEntity.ch[fCurrentEntity.position]));
                if (DEBUG_BUFFER) {
                    System.out.print(")skipSpaces: ");
                    print();
                    System.out.println(" -> true");
                }
                return true;
            }

            // no spaces were found
            if (DEBUG_BUFFER) {
                System.out.print(")skipSpaces: ");
                print();
                System.out.println(" -> false");
            }
            return false;

        } // skipSpaces():boolean

        /**
         * Skips the specified string appearing immediately on the input.
         * <p>
         * <strong>Note:</strong> The characters are consumed only if they are
         * space characters.
         *
         * @param s The string to skip.
         *
         * @return Returns true if the string was skipped.
         *
         * @throws IOException  Thrown if i/o error occurs.
         * @throws EOFException Thrown on end of file.
         */
        public boolean skipString(String s) throws IOException {
            if (DEBUG_BUFFER) {
                System.out.print("(skipString, \""+s+"\": ");
                print();
                System.out.println();
            }

            // load more characters, if needed
            if (fCurrentEntity.position == fCurrentEntity.count) {
                load(0, true);
            }

            // skip string
            final int length = s.length();
            for (int i = 0; i < length; i++) {
                char c = fCurrentEntity.ch[fCurrentEntity.position++];
                if (c != s.charAt(i)) {
                    fCurrentEntity.position -= i + 1;
                    if (DEBUG_BUFFER) {
                        System.out.print(")skipString, \""+s+"\": ");
                        print();
                        System.out.println(" -> false");
                    }
                    return false;
                }
                if (i < length - 1 && fCurrentEntity.position == fCurrentEntity.count) {
                    System.arraycopy(fCurrentEntity.ch, fCurrentEntity.count - i - 1, fCurrentEntity.ch, 0, i + 1);
                    // REVISIT: Can a string to be skipped cross an
                    //          entity boundary? -Ac
                    if (load(i + 1, false)) {
                        fCurrentEntity.position -= i + 1;
                        if (DEBUG_BUFFER) {
                            System.out.print(")skipString, \""+s+"\": ");
                            print();
                            System.out.println(" -> false");
                        }
                        return false;
                    }
                }
            }
            if (DEBUG_BUFFER) {
                System.out.print(")skipString, \""+s+"\": ");
                print();
                System.out.println(" -> true");
            }
            fCurrentEntity.columnNumber += length;
            return true;

        } // skipString(String):boolean

        //
        // Locator methods
        //

        /**
         * Return the public identifier for the current document event.
         * <p>
         * The return value is the public identifier of the document
         * entity or of the external parsed entity in which the markup
         * triggering the event appears.
         *
         * @return A string containing the public identifier, or
         *         null if none is available.
         */
        public String getPublicId() {
            return (fCurrentEntity != null && fCurrentEntity.entityLocation != null) ? fCurrentEntity.entityLocation.getPublicId() : null;
        } // getPublicId():String

        /**
         * Return the expanded system identifier for the current document event.
         * <p>
         * The return value is the expanded system identifier of the document
         * entity or of the external parsed entity in which the markup
         * triggering the event appears.
         * <p>
         * If the system identifier is a URL, the parser must resolve it
         * fully before passing it to the application.
         *
         * @return A string containing the expanded system identifier, or null
         *         if none is available.
         */
        public String getExpandedSystemId() {
            if (fCurrentEntity != null) {
                if (fCurrentEntity.entityLocation != null &&
                        fCurrentEntity.entityLocation.getExpandedSystemId() != null ) {
                    return fCurrentEntity.entityLocation.getExpandedSystemId();
                }
                else {
                    // search for the first external entity on the stack
                    int size = fEntityStack.size();
                    for (int i = size - 1; i >= 0 ; i--) {
                        ScannedEntity externalEntity =
                            (ScannedEntity)fEntityStack.elementAt(i);

                        if (externalEntity.entityLocation != null &&
                                externalEntity.entityLocation.getExpandedSystemId() != null) {
                            return externalEntity.entityLocation.getExpandedSystemId();
                        }
                    }
                }
            }
            return null;
        } // getExpandedSystemId():String

        /**
         * Return the literal system identifier for the current document event.
         * <p>
         * The return value is the literal system identifier of the document
         * entity or of the external parsed entity in which the markup
         * triggering the event appears.
         * <p>
         * @return A string containing the literal system identifier, or null
         *         if none is available.
         */
        public String getLiteralSystemId() {
            if (fCurrentEntity != null) {
                if (fCurrentEntity.entityLocation != null &&
                        fCurrentEntity.entityLocation.getLiteralSystemId() != null ) {
                    return fCurrentEntity.entityLocation.getLiteralSystemId();
                }
                else {
                    // search for the first external entity on the stack
                    int size = fEntityStack.size();
                    for (int i = size - 1; i >= 0 ; i--) {
                        ScannedEntity externalEntity =
                            (ScannedEntity)fEntityStack.elementAt(i);

                        if (externalEntity.entityLocation != null &&
                                externalEntity.entityLocation.getLiteralSystemId() != null) {
                            return externalEntity.entityLocation.getLiteralSystemId();
                        }
                    }
                }
            }
            return null;
        } // getLiteralSystemId():String

        /**
         * Return the line number where the current document event ends.
         * <p>
         * <strong>Warning:</strong> The return value from the method
         * is intended only as an approximation for the sake of error
         * reporting; it is not intended to provide sufficient information
         * to edit the character content of the original XML document.
         * <p>
         * The return value is an approximation of the line number
         * in the document entity or external parsed entity where the
         * markup triggering the event appears.
         * <p>
         * If possible, the SAX driver should provide the line position
         * of the first character after the text associated with the document
         * event.  The first line in the document is line 1.
         *
         * @return The line number, or -1 if none is available.
         */
        public int getLineNumber() {
            if (fCurrentEntity != null) {
                if (fCurrentEntity.isExternal()) {
                    return fCurrentEntity.lineNumber;
                }
                else {
                    // search for the first external entity on the stack
                    int size = fEntityStack.size();
                    for (int i=size-1; i>0 ; i--) {
                        ScannedEntity firstExternalEntity = (ScannedEntity)fEntityStack.elementAt(i);
                        if (firstExternalEntity.isExternal()) {
                            return firstExternalEntity.lineNumber;
                        }
                    }
                }
            }

            return -1;

        } // getLineNumber():int

        /**
         * Return the column number where the current document event ends.
         * <p>
         * <strong>Warning:</strong> The return value from the method
         * is intended only as an approximation for the sake of error
         * reporting; it is not intended to provide sufficient information
         * to edit the character content of the original XML document.
         * <p>
         * The return value is an approximation of the column number
         * in the document entity or external parsed entity where the
         * markup triggering the event appears.
         * <p>
         * If possible, the SAX driver should provide the line position
         * of the first character after the text associated with the document
         * event.
         * <p>
         * If possible, the SAX driver should provide the line position
         * of the first character after the text associated with the document
         * event.  The first column in each line is column 1.
         *
         * @return The column number, or -1 if none is available.
         */
        public int getColumnNumber() {
            if (fCurrentEntity != null) {
                if (fCurrentEntity.isExternal()) {
                    return fCurrentEntity.columnNumber;
                }
                else {
                    // search for the first external entity on the stack
                    int size = fEntityStack.size();
                    for (int i=size-1; i>0 ; i--) {
                        ScannedEntity firstExternalEntity = (ScannedEntity)fEntityStack.elementAt(i);
                        if (firstExternalEntity.isExternal()) {
                            return firstExternalEntity.columnNumber;
                        }
                    }
                }
            }

            return -1;
        } // getColumnNumber():int

        //
        // Private methods
        //

        /**
         * Loads a chunk of text.
         *
         * @param offset       The offset into the character buffer to
         *                     read the next batch of characters.
         * @param changeEntity True if the load should change entities
         *                     at the end of the entity, otherwise leave
         *                     the current entity in place and the entity
         *                     boundary will be signaled by the return
         *                     value.
         *
         * @returns Returns true if the entity changed as a result of this
         *          load operation.
         */
        final boolean load(int offset, boolean changeEntity)
            throws IOException {
            if (DEBUG_BUFFER) {
                System.out.print("(load, "+offset+": ");
                print();
                System.out.println();
            }

            // read characters
            int length = fCurrentEntity.mayReadChunks?
                    (fCurrentEntity.ch.length - offset):
                    (DEFAULT_XMLDECL_BUFFER_SIZE);
            if (DEBUG_BUFFER) System.out.println("  length to try to read: "+length);
            int count = fCurrentEntity.reader.read(fCurrentEntity.ch, offset, length);
            if (DEBUG_BUFFER) System.out.println("  length actually read:  "+count);

            // reset count and position
            boolean entityChanged = false;
            if (count != -1) {
                if (count != 0) {
                    fCurrentEntity.count = count + offset;
                    fCurrentEntity.position = offset;
                }
            }

            // end of this entity
            else {
                fCurrentEntity.count = offset;
                fCurrentEntity.position = offset;
                entityChanged = true;
                if (changeEntity) {
                    endEntity();
                    if (fCurrentEntity == null) {
                        throw new EOFException();
                    }
                    // handle the trailing edges
                    if (fCurrentEntity.position == fCurrentEntity.count) {
                        load(0, true);
                    }
                }
            }
            if (DEBUG_BUFFER) {
                System.out.print(")load, "+offset+": ");
                print();
                System.out.println();
            }

            return entityChanged;

        } // load(int, boolean):boolean

    } // class EntityScanner


    // This class wraps the byte inputstreams we're presented with.
    // We need it because java.io.InputStreams don't provide
    // functionality to reread processed bytes, and they have a habit
    // of reading more than one character when you call their read()
    // methods.  This means that, once we discover the true (declared)
    // encoding of a document, we can neither backtrack to read the
    // whole doc again nor start reading where we are with a new
    // reader.
    //
    // This class allows rewinding an inputStream by allowing a mark
    // to be set, and the stream reset to that position.  <strong>The
    // class assumes that it needs to read one character per
    // invocation when it's read() method is inovked, but uses the
    // underlying InputStream's read(char[], offset length) method--it
    // won't buffer data read this way!</strong>
    //
    // @author Neil Graham, IBM
    // @author Glenn Marcy, IBM

    protected final class RewindableInputStream extends InputStream {

        private InputStream fInputStream;
        private byte[] fData;
        private int fStartOffset;
        private int fEndOffset;
        private int fOffset;
        private int fLength;
        private int fMark;

        public RewindableInputStream(InputStream is) {
            fData = new byte[DEFAULT_XMLDECL_BUFFER_SIZE];
            fInputStream = is;
            fStartOffset = 0;
            fEndOffset = -1;
            fOffset = 0;
            fLength = 0;
            fMark = 0;
        }

        public void setStartOffset(int offset) {
            fStartOffset = offset;
        }

        public void rewind() {
            fOffset = fStartOffset;
        }

        public int read() throws IOException {
            int b = 0;
            if (fOffset < fLength) {
                return fData[fOffset++] & 0xff;
            }
            if (fOffset == fEndOffset) {
                return -1;
            }
            if (fOffset == fData.length) {
                byte[] newData = new byte[fOffset << 1];
                System.arraycopy(fData, 0, newData, 0, fOffset);
                fData = newData;
            }
            b = fInputStream.read();
            if (b == -1) {
                fEndOffset = fOffset;
                return -1;
            }
            fData[fLength++] = (byte)b;
            fOffset++;
            return b & 0xff;
        }

        public int read(byte[] b, int off, int len) throws IOException {
            int bytesLeft = fLength - fOffset;
            if (bytesLeft == 0) {
                if (fOffset == fEndOffset) {
                    return -1;
                }
                // better get some more for the voracious reader...
                if(fCurrentEntity.mayReadChunks) {
                    return fInputStream.read(b, off, len);
                }
                int returnedVal = read();
                if(returnedVal == -1) {
                    fEndOffset = fOffset;
                    return -1;
                }
                b[off] = (byte)returnedVal;
                return 1;
            }
            if (len < bytesLeft) {
                if (len <= 0) {
                    return 0;
                }
            }
            else {
                len = bytesLeft;
            }
            if (b != null) {
                System.arraycopy(fData, fOffset, b, off, len);
            }
            fOffset += len;
            return len;
        }

        public long skip(long n)
            throws IOException
        {
            int bytesLeft;
            if (n <= 0) {
                return 0;
            }
            bytesLeft = fLength - fOffset;
            if (bytesLeft == 0) {
                if (fOffset == fEndOffset) {
                    return 0;
                }
                return fInputStream.skip(n);
            }
            if (n <= bytesLeft) {
                fOffset += n;
                return n;
            }
            fOffset += bytesLeft;
            if (fOffset == fEndOffset) {
                return bytesLeft;
            }
            n -= bytesLeft;
           /*
            * In a manner of speaking, when this class isn't permitting more
            * than one byte at a time to be read, it is "blocking".  The
            * available() method should indicate how much can be read without
            * blocking, so while we're in this mode, it should only indicate
            * that bytes in its buffer are available; otherwise, the result of
            * available() on the underlying InputStream is appropriate.
            */
            return fInputStream.skip(n) + bytesLeft;
        }

        public int available() throws IOException {
            int bytesLeft = fLength - fOffset;
            if (bytesLeft == 0) {
                if (fOffset == fEndOffset) {
                    return -1;
                }
                return fCurrentEntity.mayReadChunks ? fInputStream.available()
                                                    : 0;
            }
            return bytesLeft;
        }

        public void mark(int howMuch) {
            fMark = fOffset;
        }

        public void reset() {
            fOffset = fMark;
        }

        public boolean markSupported() {
            return true;
        }

        public void close() throws IOException {
            if (fInputStream != null) {
                fInputStream.close();
                fInputStream = null;
            }
        }
    } // end of RewindableInputStream class

} // class XMLEntityManager