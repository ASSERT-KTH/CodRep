attrPSVI.getValidationAttempted() == AttributePSVI.VALIDATION_FULL) {

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

import java.io.InputStream;
import java.io.IOException;
import java.io.Reader;
import java.util.Hashtable;
import java.util.Locale;

import org.apache.xerces.impl.Constants;

import org.apache.xerces.util.EntityResolverWrapper;
import org.apache.xerces.util.ErrorHandlerWrapper;

import org.apache.xerces.xni.Augmentations;
import org.apache.xerces.xni.QName;
import org.apache.xerces.xni.XMLAttributes;
import org.apache.xerces.xni.XMLLocator;
import org.apache.xerces.xni.XMLResourceIdentifier;
import org.apache.xerces.xni.XMLString;
import org.apache.xerces.xni.XNIException;
import org.apache.xerces.xni.parser.XMLParseException;
import org.apache.xerces.xni.parser.XMLConfigurationException;
import org.apache.xerces.xni.parser.XMLEntityResolver;
import org.apache.xerces.xni.parser.XMLErrorHandler;
import org.apache.xerces.xni.parser.XMLInputSource;
import org.apache.xerces.xni.parser.XMLParserConfiguration;
import org.apache.xerces.xni.psvi.ElementPSVI;
import org.apache.xerces.xni.psvi.AttributePSVI;

import org.xml.sax.AttributeList;
import org.xml.sax.Attributes;
import org.xml.sax.ContentHandler;
import org.xml.sax.DTDHandler;
import org.xml.sax.DocumentHandler;
import org.xml.sax.EntityResolver;
import org.xml.sax.ErrorHandler;
import org.xml.sax.InputSource;
import org.xml.sax.Locator;
import org.xml.sax.Parser;
import org.xml.sax.SAXException;
import org.xml.sax.SAXParseException;
import org.xml.sax.SAXNotRecognizedException;
import org.xml.sax.SAXNotSupportedException;
import org.xml.sax.XMLReader;
import org.xml.sax.ext.DeclHandler;
import org.xml.sax.ext.LexicalHandler;
import org.xml.sax.helpers.LocatorImpl;

/**
 * This is the base class of all SAX parsers. It implements both the
 * SAX1 and SAX2 parser functionality, while the actual pipeline is
 * defined in the parser configuration.
 *
 * @author Arnaud Le Hors, IBM
 * @author Andy Clark, IBM
 *
 * @version $Id$
 */
public abstract class AbstractSAXParser
    extends AbstractXMLDocumentParser
    implements Parser, XMLReader // SAX1, SAX2
{

    //
    // Constants
    //

    // features

    /** Feature identifier: namespaces. */
    protected static final String NAMESPACES =
        Constants.SAX_FEATURE_PREFIX + Constants.NAMESPACES_FEATURE;

    /** Feature identifier: namespace prefixes. */
    protected static final String NAMESPACE_PREFIXES =
        Constants.SAX_FEATURE_PREFIX + Constants.NAMESPACE_PREFIXES_FEATURE;

    /** Expose XML Schema normalize value */
    protected static final String NORMALIZE_DATA = 
        Constants.XERCES_FEATURE_PREFIX + Constants.SCHEMA_NORMALIZED_VALUE;

    /** Feature id: string interning. */
    protected static final String STRING_INTERNING =
        Constants.SAX_FEATURE_PREFIX + Constants.STRING_INTERNING_FEATURE;
    
    /** Recognized features. */
    private static final String[] RECOGNIZED_FEATURES = {
        NAMESPACES,
        NAMESPACE_PREFIXES,
        NORMALIZE_DATA,
        STRING_INTERNING,
    };

    // properties

    /** Property id: lexical handler. */
    protected static final String LEXICAL_HANDLER = 
        Constants.SAX_PROPERTY_PREFIX + Constants.LEXICAL_HANDLER_PROPERTY;

    /** Property id: declaration handler. */
    protected static final String DECLARATION_HANDLER =
        Constants.SAX_PROPERTY_PREFIX + Constants.DECLARATION_HANDLER_PROPERTY;

    /** Property id: DOM node. */
    protected static final String DOM_NODE = 
        Constants.SAX_PROPERTY_PREFIX + Constants.DOM_NODE_PROPERTY;

    /** Recognized properties. */
    private static final String[] RECOGNIZED_PROPERTIES = {
        LEXICAL_HANDLER,
        DECLARATION_HANDLER,
        DOM_NODE,
    };

    //
    // Data
    //

    // features

    /** Namespaces. */
    protected boolean fNamespaces;

    /** Namespace prefixes. */
    protected boolean fNamespacePrefixes = false;

    /** Expose XML Schema schema_normalize_values via DOM*/
    protected boolean fNormalizeData = true;

    // parser handlers

    /** Content handler. */
    protected ContentHandler fContentHandler;

    /** Document handler. */
    protected DocumentHandler fDocumentHandler;

    /** DTD handler. */
    protected org.xml.sax.DTDHandler fDTDHandler;

    /** Decl handler. */
    protected DeclHandler fDeclHandler;

    /** Lexical handler. */
    protected LexicalHandler fLexicalHandler;

    protected QName fQName = new QName();

    // state

    /**
     * True if a parse is in progress. This state is needed because
     * some features/properties cannot be set while parsing (e.g.
     * validation and namespaces).
     */
    protected boolean fParseInProgress = false;

    // temp vars
    private final AttributesProxy fAttributesProxy = new AttributesProxy();

    // temporary buffer for sending normalized values
    // REVISIT: what should be the size of the buffer?
    private static final int BUFFER_SIZE = 20;
    private char[] fCharBuffer =  new char[BUFFER_SIZE];

    //
    // Constructors
    //

    /** Default constructor. */
    protected AbstractSAXParser(XMLParserConfiguration config) {
        super(config);

        config.addRecognizedFeatures(RECOGNIZED_FEATURES);
        config.addRecognizedProperties(RECOGNIZED_PROPERTIES);

    } // <init>(XMLParserConfiguration)

    //
    // XMLDocumentHandler methods
    //

    /**
     * The start of the document.
     *
     * @param locator The document locator, or null if the document
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
     * @param augs     Additional information that may include infoset augmentations
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void startDocument(XMLLocator locator, String encoding, Augmentations augs)
        throws XNIException {

        try {
            // SAX1
            if (fDocumentHandler != null) {
                if (locator != null) {
                    fDocumentHandler.setDocumentLocator(new LocatorProxy(locator));
                }
                fDocumentHandler.startDocument();
            }

            // SAX2
            if (fContentHandler != null) {
                if (locator != null) {
                    fContentHandler.setDocumentLocator(new LocatorProxy(locator));
                }
                fContentHandler.startDocument();
            }
        }
        catch (SAXException e) {
            throw new XNIException(e);
        }

    } // startDocument(locator,encoding,augs)

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
    public void doctypeDecl(String rootElement,
                            String publicId, String systemId, Augmentations augs)
        throws XNIException {
        fInDTD = true;

        try {
            // SAX2 extension
            if (fLexicalHandler != null) {
                fLexicalHandler.startDTD(rootElement, publicId, systemId);
            }
        }
        catch (SAXException e) {
            throw new XNIException(e);
        }

    } // doctypeDecl(String,String,String)

        /**
     * This method notifies of the start of an entity. The DTD has the
     * pseudo-name of "[dtd]" parameter entity names start with '%'; and
     * general entity names are just the entity name.
     * <p>
     * <strong>Note:</strong> Since the document is an entity, the handler
     * will be notified of the start of the document entity by calling the
     * startEntity method with the entity name "[xml]" <em>before</em> calling
     * the startDocument method. When exposing entity boundaries through the
     * SAX API, the document entity is never reported, however.
     * <p>
     * <strong>Note:</strong> This method is not called for entity references
     * appearing as part of attribute values.
     *
     * @param name     The name of the entity.
     * @param identifier The resource identifier.
     * @param encoding The auto-detected IANA encoding name of the entity
     *                 stream. This value will be null in those situations
     *                 where the entity encoding is not auto-detected (e.g.
     *                 internal parameter entities).
     * @param augs     Additional information that may include infoset augmentations
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void startGeneralEntity(String name, XMLResourceIdentifier identifier, 
                                   String encoding, Augmentations augs)
        throws XNIException {
        
        startParameterEntity(name, identifier, encoding, augs);

    } // startGeneralEntity(String,String,String,String,String)

    /**
     * This method notifies the end of an entity. The DTD has the pseudo-name
     * of "[dtd]" parameter entity names start with '%'; and general entity
     * names are just the entity name.
     * <p>
     * <strong>Note:</strong> Since the document is an entity, the handler
     * will be notified of the end of the document entity by calling the
     * endEntity method with the entity name "[xml]" <em>after</em> calling
     * the endDocument method. When exposing entity boundaries through the
     * SAX API, the document entity is never reported, however.
     * <p>
     * <strong>Note:</strong> This method is not called for entity references
     * appearing as part of attribute values.
     *
     * @param name The name of the entity.
     * @param augs     Additional information that may include infoset augmentations
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void endGeneralEntity(String name, Augmentations augs) throws XNIException {

        endParameterEntity(name, augs);

    } // endEntity(String)

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

        try {
            // SAX2
            if (fContentHandler != null) {
                fContentHandler.startPrefixMapping(prefix, uri);
            }
        }
        catch (SAXException e) {
            throw new XNIException(e);
        }

    } // startPrefixMapping(String prefix, String uri)

    /**
     * The start of an element. If the document specifies the start element
     * by using an empty tag, then the startElement method will immediately
     * be followed by the endElement method, with no intervening methods.
     *
     * @param element    The name of the element.
     * @param attributes The element attributes.
     * @param augs     Additional information that may include infoset augmentations
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void startElement(QName element, XMLAttributes attributes, Augmentations augs)
        throws XNIException {

        try {
            // SAX1
            if (fDocumentHandler != null) {
                // REVISIT: should we support schema-normalized-value for SAX1 events
                // 
                fAttributesProxy.setAttributes(attributes);
                fDocumentHandler.startElement(element.rawname, fAttributesProxy);
            }

            // SAX2
            if (fContentHandler != null) {

                int len = attributes.getLength();
                for (int i = len - 1; i >= 0; i--) {
                    attributes.getName(i, fQName);
                    // change attribute value to normalized value
                    // REVISIT: should this happen here? why not in schema validator?
                    if (fNormalizeData) {
                        AttributePSVI attrPSVI = (AttributePSVI)attributes.getAugmentations(i).getItem(Constants.ATTRIBUTE_PSVI);
                        if (attrPSVI != null &&
                            attrPSVI.getValidationAttempted() == AttributePSVI.FULL_VALIDATION) {
                            attributes.setValue(i, attrPSVI.getSchemaNormalizedValue());
                        }
                    }

                    if ((fQName.prefix != null && fQName.prefix.equals("xmlns")) || 
                        fQName.rawname.equals("xmlns")) {
                        if (!fNamespacePrefixes) {
                            // remove namespace declaration attributes
                            attributes.removeAttributeAt(i);
                        }
                        if (fNamespaces && fNamespacePrefixes) {
                            // localpart should be empty string as per SAX documentation:
                            // http://www.saxproject.org/?selected=namespaces
                            fQName.prefix = "";
                            fQName.uri = "";
                            fQName.localpart = "";
                            attributes.setName(i, fQName);
                        }
                    } 
                }
                
                String uri = element.uri != null ? element.uri : "";
                String localpart = fNamespaces ? element.localpart : "";
                fAttributesProxy.setAttributes(attributes);
                fContentHandler.startElement(uri, localpart, element.rawname,
                                             fAttributesProxy);
            }
        }
        catch (SAXException e) {
            throw new XNIException(e);
        }

    } // startElement(QName,XMLAttributes)

    /**
     * Character content.
     *
     * @param text The content.
     * @param augs     Additional information that may include infoset augmentations
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void characters(XMLString text, Augmentations augs) throws XNIException {
        
        // if type is union (XML Schema) it is possible that we receive
        // character call with empty data
        if (text.length == 0) {
            return;
        }


        try {
            // SAX1
            if (fDocumentHandler != null) {
                // REVISIT: should we support schema-normalized-value for SAX1 events
                // 
                fDocumentHandler.characters(text.ch, text.offset, text.length);
            }

            // SAX2
            if (fContentHandler != null) {
                String value = null;
                // normalized value for element is stored in schema_normalize_value property
                // of PSVI element.
                // REVISIT: should this happen here? why not in schema validator?
                // REVISIT: how to determine whether the value is trustable?
                if (fNormalizeData && augs != null) {
                    ElementPSVI elemPSVI = (ElementPSVI)augs.getItem(Constants.ELEMENT_PSVI);
                    if (elemPSVI != null) {
                        value = elemPSVI.getSchemaNormalizedValue();
                    }
                }

                int length = 0;
                if (value != null) {
                     // if normalized value is available copy it into a temp buffer
                     length = value.length();
                     if (length >= BUFFER_SIZE) {
                        fCharBuffer = new char[length*2];
                     }
                     value.getChars(0, length, fCharBuffer, 0);
                }
                if (value == null) {                
                    fContentHandler.characters(text.ch, text.offset, text.length);
                }
                else {
                    fContentHandler.characters(fCharBuffer, 0, length);
                }
            }
        }
        catch (SAXException e) {
            throw new XNIException(e);
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

        try {
            // SAX1
            if (fDocumentHandler != null) {
                fDocumentHandler.ignorableWhitespace(text.ch, text.offset, text.length);
            }

            // SAX2
            if (fContentHandler != null) {
                fContentHandler.ignorableWhitespace(text.ch, text.offset, text.length);
            }
        }
        catch (SAXException e) {
            throw new XNIException(e);
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
        

        try {
            // SAX1
            if (fDocumentHandler != null) {
                fDocumentHandler.endElement(element.rawname);
            }

            // SAX2
            if (fContentHandler != null) {
                String uri = element.uri != null ? element.uri : "";
                String localpart = fNamespaces ? element.localpart : "";
                fContentHandler.endElement(uri, localpart,
                                           element.rawname);
            }
        }
        catch (SAXException e) {
            throw new XNIException(e);
        }

    } // endElement(QName)

    /**
     * The end of a namespace prefix mapping. This method will only be
     * called when namespace processing is enabled.
     *
     * @param prefix The namespace prefix.
     * @param augs     Additional information that may include infoset augmentations
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void endPrefixMapping(String prefix, Augmentations augs)  throws XNIException {

        try {
            // SAX2
            if (fContentHandler != null) {
                fContentHandler.endPrefixMapping(prefix);
            }
        }
        catch (SAXException e) {
            throw new XNIException(e);
        }

    } // endPrefixMapping(String)

        /**
     * The start of a CDATA section.
     * @param augs     Additional information that may include infoset augmentations
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void startCDATA(Augmentations augs) throws XNIException {

        try {
            // SAX2 extension
            if (fLexicalHandler != null) {
                fLexicalHandler.startCDATA();
            }
        }
        catch (SAXException e) {
            throw new XNIException(e);
        }

    } // startCDATA()

    /**
     * The end of a CDATA section.
     * @param augs     Additional information that may include infoset augmentations
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void endCDATA(Augmentations augs) throws XNIException {

        try {
            // SAX2 extension
            if (fLexicalHandler != null) {
                fLexicalHandler.endCDATA();
            }
        }
        catch (SAXException e) {
            throw new XNIException(e);
        }

    } // endCDATA()

    /**
     * A comment.
     *
     * @param text The text in the comment.
     * @param augs     Additional information that may include infoset augmentations
     *
     * @throws XNIException Thrown by application to signal an error.
     */
    public void comment(XMLString text, Augmentations augs) throws XNIException {

        try {
            // SAX2 extension
            if (fLexicalHandler != null) {
                fLexicalHandler.comment(text.ch, 0, text.length);
            }
        }
        catch (SAXException e) {
            throw new XNIException(e);
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

        //
        // REVISIT - I keep running into SAX apps that expect
        //   null data to be an empty string, which is contrary
        //   to the comment for this method in the SAX API.
        //

        try {
            // SAX1
            if (fDocumentHandler != null) {
                fDocumentHandler.processingInstruction(target,
                                                       data.toString());
            }

            // SAX2
            if (fContentHandler != null) {
                fContentHandler.processingInstruction(target, data.toString());
            }
        }
        catch (SAXException e) {
            throw new XNIException(e);
        }

    } // processingInstruction(String,XMLString)


    /**
     * The end of the document.
     * @param augs     Additional information that may include infoset augmentations
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void endDocument(Augmentations augs) throws XNIException {

        try {
            // SAX1
            if (fDocumentHandler != null) {
                fDocumentHandler.endDocument();
            }

            // SAX2
            if (fContentHandler != null) {
                fContentHandler.endDocument();
            }
        }
        catch (SAXException e) {
            throw new XNIException(e);
        }

    } // endDocument()

    //
    // XMLDTDHandler methods
    //

    /**
     * The start of the DTD external subset.
     *
     * @param augs Additional information that may include infoset
     *                      augmentations.
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void startExternalSubset(XMLResourceIdentifier identifier, 
                                    Augmentations augs) throws XNIException {
        startParameterEntity("[dtd]", null, null, augs);
    }

    /**
     * The end of the DTD external subset.
     *
     * @param augs Additional information that may include infoset
     *                      augmentations.
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void endExternalSubset(Augmentations augs) throws XNIException {
        endParameterEntity("[dtd]", augs);
    }

    /**
     * This method notifies of the start of parameter entity. The DTD has the
     * pseudo-name of "[dtd]" parameter entity names start with '%'; and
     * general entity names are just the entity name.
     * <p>
     * <strong>Note:</strong> Since the document is an entity, the handler
     * will be notified of the start of the document entity by calling the
     * startEntity method with the entity name "[xml]" <em>before</em> calling
     * the startDocument method. When exposing entity boundaries through the
     * SAX API, the document entity is never reported, however.
     * <p>
     * <strong>Note:</strong> This method is not called for entity references
     * appearing as part of attribute values.
     *
     * @param name     The name of the parameter entity.
     * @param identifier The resource identifier.
     * @param encoding The auto-detected IANA encoding name of the entity
     *                 stream. This value will be null in those situations
     *                 where the entity encoding is not auto-detected (e.g.
     *                 internal parameter entities).
     * @param augs Additional information that may include infoset
     *                      augmentations.
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void startParameterEntity(String name, 
                                     XMLResourceIdentifier identifier,
                                     String encoding, Augmentations augs)
        throws XNIException {

        try {
            // SAX2 extension
            if (fLexicalHandler != null) {
                fLexicalHandler.startEntity(name);
            }
        }
        catch (SAXException e) {
            throw new XNIException(e);
        }

    } // startParameterEntity(String,identifier,String,Augmentation)

    /**
     * This method notifies the end of an entity. The DTD has the pseudo-name
     * of "[dtd]" parameter entity names start with '%'; and general entity
     * names are just the entity name.
     * <p>
     * <strong>Note:</strong> Since the document is an entity, the handler
     * will be notified of the end of the document entity by calling the
     * endEntity method with the entity name "[xml]" <em>after</em> calling
     * the endDocument method. When exposing entity boundaries through the
     * SAX API, the document entity is never reported, however.
     * <p>
     * <strong>Note:</strong> This method is not called for entity references
     * appearing as part of attribute values.
     *
     * @param name The name of the parameter entity.
     * @param augs Additional information that may include infoset
     *                      augmentations.
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void endParameterEntity(String name, Augmentations augs) throws XNIException {

        try {
            // SAX2 extension
            if (fLexicalHandler != null) {
                fLexicalHandler.endEntity(name);
            }
        }
        catch (SAXException e) {
            throw new XNIException(e);
        }

    } // endEntity(String)

    /**
     * An element declaration.
     *
     * @param name         The name of the element.
     * @param contentModel The element content model.
     *
     * @param augs Additional information that may include infoset
     *                      augmentations.
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void elementDecl(String name, String contentModel, Augmentations augs)
        throws XNIException {

        try {
            // SAX2 extension
            if (fDeclHandler != null) {
                fDeclHandler.elementDecl(name, contentModel);
            }
        }
        catch (SAXException e) {
            throw new XNIException(e);
        }

    } // elementDecl(String,String)

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
     * @param enumeration   If the type has the value "ENUMERATION" or
     *                      "NOTATION", this array holds the allowed attribute
     *                      values; otherwise, this array is null.
     * @param defaultType   The attribute default type. This value will be
     *                      one of the following: "#FIXED", "#IMPLIED",
     *                      "#REQUIRED", or null.
     * @param defaultValue  The attribute default value, or null if no
     *                      default value is specified.
     *
     * @param nonNormalizedDefaultValue  The attribute default value with no normalization 
     *                      performed, or null if no default value is specified.
     * @param augs Additional information that may include infoset
     *                      augmentations.
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void attributeDecl(String elementName, String attributeName,
                              String type, String[] enumeration,
                              String defaultType, XMLString defaultValue,
                              XMLString nonNormalizedDefaultValue, Augmentations augs) throws XNIException {

        try {
            // SAX2 extension
            if (fDeclHandler != null) {
                if (type.equals("NOTATION") || 
                    type.equals("ENUMERATION")) {

                    StringBuffer str = new StringBuffer();
                    if (type.equals("NOTATION")) {
                      str.append(type);
                      str.append(" (");
                    }
                    else {
                      str.append("(");
                    }
                    for (int i = 0; i < enumeration.length; i++) {
                        str.append(enumeration[i]);
                        if (i < enumeration.length - 1) {
                            str.append('|');
                        }
                    }
                    str.append(')');
                    type = str.toString();
                }
                String value = (defaultValue==null) ? null : defaultValue.toString();
                fDeclHandler.attributeDecl(elementName, attributeName,
                                           type, defaultType, value);
            }
        }
        catch (SAXException e) {
            throw new XNIException(e);
        }

    } // attributeDecl(String,String,String,String[],String,XMLString, XMLString, Augmentations)

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
     * @param augs Additional information that may include infoset
     *                      augmentations.
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void internalEntityDecl(String name, XMLString text,
                                   XMLString nonNormalizedText,
                                   Augmentations augs) throws XNIException {

        try {
            // SAX2 extensions
            if (fDeclHandler != null) {
                fDeclHandler.internalEntityDecl(name, text.toString());
            }
        }
        catch (SAXException e) {
            throw new XNIException(e);
        }

    } // internalEntityDecl(String,XMLString,XMLString)

    /**
     * An external entity declaration.
     *
     * @param name     The name of the entity. Parameter entity names start
     *                 with '%', whereas the name of a general entity is just
     *                 the entity name.
     * @param identifier    An object containing all location information 
     *                      pertinent to this entity.
     * @param augs Additional information that may include infoset
     *                      augmentations.
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void externalEntityDecl(String name, XMLResourceIdentifier identifier,
                                   Augmentations augs) throws XNIException {

        String publicId = identifier.getPublicId();
        String literalSystemId = identifier.getLiteralSystemId();
        try {
            // SAX2 extension
            if (fDeclHandler != null) {
                fDeclHandler.externalEntityDecl(name, publicId, literalSystemId);
            }
        }
        catch (SAXException e) {
            throw new XNIException(e);
        }

    } // externalEntityDecl(String,,XMLResourceIdentifier, Augmentations)

    /**
     * An unparsed entity declaration.
     *
     * @param name     The name of the entity.
     * @param identifier    An object containing all location information 
     *                      pertinent to this entity.
     * @param notation The name of the notation.
     *
     * @param augs Additional information that may include infoset
     *                      augmentations.
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void unparsedEntityDecl(String name, XMLResourceIdentifier identifier, 
                                   String notation,
                                   Augmentations augs) throws XNIException {

        String publicId = identifier.getPublicId();
        String expandedSystemId = identifier.getExpandedSystemId(); 
        try {
            // SAX2 extension
            if (fDTDHandler != null) {
                fDTDHandler.unparsedEntityDecl(name, publicId,
                                               expandedSystemId, notation);
            }
        }
        catch (SAXException e) {
            throw new XNIException(e);
        }

    } // unparsedEntityDecl(String,XMLResourceIdentifier, String, Augmentations)

    /**
     * A notation declaration
     *
     * @param name     The name of the notation.
     * @param identifier    An object containing all location information 
     *                      pertinent to this notation.
     * @param augs Additional information that may include infoset
     *                      augmentations.
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void notationDecl(String name, XMLResourceIdentifier identifier,
                             Augmentations augs) throws XNIException {

        String publicId = identifier.getPublicId();
        String expandedSystemId = identifier.getExpandedSystemId();
        try {
            // SAX1 and SAX2
            if (fDTDHandler != null) {
                fDTDHandler.notationDecl(name, publicId, expandedSystemId);
            }
        }
        catch (SAXException e) {
            throw new XNIException(e);
        }

    } // notationDecl(String,XMLResourceIdentifier, Augmentations)

    /**
     * The end of the DTD.
     *
     * @param augs Additional information that may include infoset
     *                      augmentations.
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void endDTD(Augmentations augs) throws XNIException {
        fInDTD = false;

        try {
            // SAX2 extension
            if (fLexicalHandler != null) {
                fLexicalHandler.endDTD();
            }
        }
        catch (SAXException e) {
            throw new XNIException(e);
        }

    } // endDTD()

    //
    // Parser and XMLReader methods
    //

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
    public void parse(String systemId) throws SAXException, IOException {

        // parse document
        XMLInputSource source = new XMLInputSource(null, systemId, null);
        try {
            parse(source);
        }

        // wrap XNI exceptions as SAX exceptions
        catch (XMLParseException e) {
            Exception ex = e.getException();
            if (ex == null) {
                // must be a parser exception; mine it for locator info and throw
                // a SAXParseException
                LocatorImpl locatorImpl = new LocatorImpl();
                locatorImpl.setPublicId(e.getPublicId());
                locatorImpl.setSystemId(e.getExpandedSystemId());
                locatorImpl.setLineNumber(e.getLineNumber());
                locatorImpl.setColumnNumber(e.getColumnNumber());
                throw new SAXParseException(e.getMessage(), locatorImpl);
            }
            if (ex instanceof SAXException) {
                // why did we create an XMLParseException?
                throw (SAXException)ex;
            }
            if (ex instanceof IOException) {
                throw (IOException)ex;
            }
            throw new SAXException(ex);
        }
        catch (XNIException e) {
            Exception ex = e.getException();
            if (ex == null) {
                throw new SAXException(e.getMessage());
            }
            if (ex instanceof SAXException) {
                throw (SAXException)ex;
            }
            if (ex instanceof IOException) {
                throw (IOException)ex;
            }
            throw new SAXException(ex);
        }

    } // parse(String)

    /**
     * parse
     *
     * @param inputSource
     *
     * @exception org.xml.sax.SAXException
     * @exception java.io.IOException
     */
    public void parse(InputSource inputSource)
        throws SAXException, IOException {

        // parse document
        try {
            XMLInputSource xmlInputSource =
                new XMLInputSource(inputSource.getPublicId(),
                                   inputSource.getSystemId(),
                                   null);
            xmlInputSource.setByteStream(inputSource.getByteStream());
            xmlInputSource.setCharacterStream(inputSource.getCharacterStream());
            xmlInputSource.setEncoding(inputSource.getEncoding());
            parse(xmlInputSource);
        }

        // wrap XNI exceptions as SAX exceptions
        catch (XMLParseException e) {
            Exception ex = e.getException();
            if (ex == null) {
                // must be a parser exception; mine it for locator info and throw
                // a SAXParseException
                LocatorImpl locatorImpl = new LocatorImpl();
                locatorImpl.setPublicId(e.getPublicId());
                locatorImpl.setSystemId(e.getExpandedSystemId());
                locatorImpl.setLineNumber(e.getLineNumber());
                locatorImpl.setColumnNumber(e.getColumnNumber());
                throw new SAXParseException(e.getMessage(), locatorImpl);
            }
            if (ex instanceof SAXException) {
                // why did we create an XMLParseException?
                throw (SAXException)ex;
            }
            if (ex instanceof IOException) {
                throw (IOException)ex;
            }
            throw new SAXException(ex);
        }
        catch (XNIException e) {
            Exception ex = e.getException();
            if (ex == null) {
                throw new SAXException(e.getMessage());
            }
            if (ex instanceof SAXException) {
                throw (SAXException)ex;
            }
            if (ex instanceof IOException) {
                throw (IOException)ex;
            }
            throw new SAXException(ex);
        }

    } // parse(InputSource)

    /**
     * Sets the resolver used to resolve external entities. The EntityResolver
     * interface supports resolution of public and system identifiers.
     *
     * @param resolver The new entity resolver. Passing a null value will
     *                 uninstall the currently installed resolver.
     */
    public void setEntityResolver(EntityResolver resolver) {

        try {
            fConfiguration.setProperty(ENTITY_RESOLVER,
                                       new EntityResolverWrapper(resolver));
        }
        catch (XMLConfigurationException e) {
            // do nothing
        }

    } // setEntityResolver(EntityResolver)

    /**
     * Return the current entity resolver.
     *
     * @return The current entity resolver, or null if none
     *         has been registered.
     * @see #setEntityResolver
     */
    public EntityResolver getEntityResolver() {

        EntityResolver entityResolver = null;
        try {
            XMLEntityResolver xmlEntityResolver =
                (XMLEntityResolver)fConfiguration.getProperty(ENTITY_RESOLVER);
            if (xmlEntityResolver != null &&
                xmlEntityResolver instanceof EntityResolverWrapper) {
                entityResolver = ((EntityResolverWrapper)xmlEntityResolver).getEntityResolver();
            }
        }
        catch (XMLConfigurationException e) {
            // do nothing
        }
        return entityResolver;

    } // getEntityResolver():EntityResolver

    /**
     * Allow an application to register an error event handler.
     *
     * <p>If the application does not register an error handler, all
     * error events reported by the SAX parser will be silently
     * ignored; however, normal processing may not continue.  It is
     * highly recommended that all SAX applications implement an
     * error handler to avoid unexpected bugs.</p>
     *
     * <p>Applications may register a new or different handler in the
     * middle of a parse, and the SAX parser must begin using the new
     * handler immediately.</p>
     *
     * @param errorHandler The error handler.
     * @exception java.lang.NullPointerException If the handler
     *            argument is null.
     * @see #getErrorHandler
     */
    public void setErrorHandler(ErrorHandler errorHandler) {

        try {
            fConfiguration.setProperty(ERROR_HANDLER,
                                       new ErrorHandlerWrapper(errorHandler));
        }
        catch (XMLConfigurationException e) {
            // do nothing
        }

    } // setErrorHandler(ErrorHandler)

    /**
     * Return the current error handler.
     *
     * @return The current error handler, or null if none
     *         has been registered.
     * @see #setErrorHandler
     */
    public ErrorHandler getErrorHandler() {

        ErrorHandler errorHandler = null;
        try {
            XMLErrorHandler xmlErrorHandler =
                (XMLErrorHandler)fConfiguration.getProperty(ERROR_HANDLER);
            if (xmlErrorHandler != null &&
                xmlErrorHandler instanceof ErrorHandlerWrapper) {
                errorHandler = ((ErrorHandlerWrapper)xmlErrorHandler).getErrorHandler();
            }
        }
        catch (XMLConfigurationException e) {
            // do nothing
        }
        return errorHandler;

    } // getErrorHandler():ErrorHandler

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
        //REVISIT:this methods is not part of SAX2 interfaces, we should throw exception
        //if any application uses SAX2 and sets locale also. -nb
        fConfiguration.setLocale(locale);

    } // setLocale(Locale)

    /**
     * Allow an application to register a DTD event handler.
     * <p>
     * If the application does not register a DTD handler, all DTD
     * events reported by the SAX parser will be silently ignored.
     * <p>
     * Applications may register a new or different handler in the
     * middle of a parse, and the SAX parser must begin using the new
     * handler immediately.
     *
     * @param dtdHandler The DTD handler.
     *
     * @exception java.lang.NullPointerException If the handler
     *            argument is null.
     *
     * @see #getDTDHandler
     */
    public void setDTDHandler(DTDHandler dtdHandler) {
        // REVISIT: SAX1 doesn't require a null pointer exception
        //          to be thrown but SAX2 does. [Q] How do we
        //          resolve this? Currently I'm erring on the side
        //          of SAX2. -Ac
        if (dtdHandler == null) {
            throw new NullPointerException();
        }
        fDTDHandler = dtdHandler;
    } // setDTDHandler(DTDHandler)

    //
    // Parser methods
    //

    /**
     * Allow an application to register a document event handler.
     * <p>
     * If the application does not register a document handler, all
     * document events reported by the SAX parser will be silently
     * ignored (this is the default behaviour implemented by
     * HandlerBase).
     * <p>
     * Applications may register a new or different handler in the
     * middle of a parse, and the SAX parser must begin using the new
     * handler immediately.
     *
     * @param documentHandler The document handler.
     */
    public void setDocumentHandler(DocumentHandler documentHandler) {
        fDocumentHandler = documentHandler;
    } // setDocumentHandler(DocumentHandler)

    //
    // XMLReader methods
    //

    /**
     * Allow an application to register a content event handler.
     * <p>
     * If the application does not register a content handler, all
     * content events reported by the SAX parser will be silently
     * ignored.
     * <p>
     * Applications may register a new or different handler in the
     * middle of a parse, and the SAX parser must begin using the new
     * handler immediately.
     *
     * @param contentHandler The content handler.
     *
     * @exception java.lang.NullPointerException If the handler
     *            argument is null.
     *
     * @see #getContentHandler
     */
    public void setContentHandler(ContentHandler contentHandler) {
        fContentHandler = contentHandler;
    } // setContentHandler(ContentHandler)

    /**
     * Return the current content handler.
     *
     * @return The current content handler, or null if none
     *         has been registered.
     *
     * @see #setContentHandler
     */
    public ContentHandler getContentHandler() {
        return fContentHandler;
    } // getContentHandler():ContentHandler

    /**
     * Return the current DTD handler.
     *
     * @return The current DTD handler, or null if none
     *         has been registered.
     * @see #setDTDHandler
     */
    public DTDHandler getDTDHandler() {
        return fDTDHandler;
    } // getDTDHandler():DTDHandler

    /**
     * Set the state of any feature in a SAX2 parser.  The parser
     * might not recognize the feature, and if it does recognize
     * it, it might not be able to fulfill the request.
     *
     * @param featureId The unique identifier (URI) of the feature.
     * @param state The requested state of the feature (true or false).
     *
     * @exception SAXNotRecognizedException If the
     *            requested feature is not known.
     * @exception SAXNotSupportedException If the
     *            requested feature is known, but the requested
     *            state is not supported.
     */
    public void setFeature(String featureId, boolean state)
        throws SAXNotRecognizedException, SAXNotSupportedException {

        try {
            //
            // SAX2 Features
            //

            if (featureId.startsWith(Constants.SAX_FEATURE_PREFIX)) {
                String feature = featureId.substring(Constants.SAX_FEATURE_PREFIX.length());

                // http://xml.org/sax/features/namespaces
                if (feature.equals(Constants.NAMESPACES_FEATURE)) {
                    fConfiguration.setFeature(featureId, state);
                    fNamespaces = state;
                    return;
                }
                // http://xml.org/sax/features/namespace-prefixes
                //   controls the reporting of raw prefixed names and Namespace
                //   declarations (xmlns* attributes): when this feature is false
                //   (the default), raw prefixed names may optionally be reported,
                //   and xmlns* attributes must not be reported.
                //
                if (feature.equals(Constants.NAMESPACE_PREFIXES_FEATURE)) {
                    fConfiguration.setFeature(featureId, state);
                    fNamespacePrefixes = state;
                    return;
                }
                // http://xml.org/sax/features/string-interning
                //   controls the use of java.lang.String#intern() for strings
                //   passed to SAX handlers.
                //
                if (feature.equals(Constants.STRING_INTERNING_FEATURE)) {
                    if (!state) {
                        // REVISIT: Localize this error message. -Ac
                        throw new SAXNotSupportedException(
                            "PAR018 " + state + " state for feature \"" + featureId
                            + "\" is not supported.\n" + state + '\t' + featureId);
                    }
                    return;
                }

                //
                // Drop through and perform default processing
                //
            }

            //
            // Xerces Features
            //

            /*
            else if (featureId.startsWith(XERCES_FEATURES_PREFIX)) {
                String feature = featureId.substring(XERCES_FEATURES_PREFIX.length());
                //
                // Drop through and perform default processing
                //
            }
            */

            //
            // Default handling
            //

            fConfiguration.setFeature(featureId, state);
        }
        catch (XMLConfigurationException e) {
            String message = e.getMessage();
            if (e.getType() == XMLConfigurationException.NOT_RECOGNIZED) {
                throw new SAXNotRecognizedException(message);
            }
            else {
                throw new SAXNotSupportedException(message);
            }
        }

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
     * @exception SAXNotSupportedException If the
     *            requested feature is known but not supported.
     */
    public boolean getFeature(String featureId)
        throws SAXNotRecognizedException, SAXNotSupportedException {

        try {
            //
            // SAX2 Features
            //

            if (featureId.startsWith(Constants.SAX_FEATURE_PREFIX)) {
                String feature =
                    featureId.substring(Constants.SAX_FEATURE_PREFIX.length());

                // http://xml.org/sax/features/namespace-prefixes
                //   controls the reporting of raw prefixed names and Namespace
                //   declarations (xmlns* attributes): when this feature is false
                //   (the default), raw prefixed names may optionally be reported,
                //   and xmlns* attributes must not be reported.
                //
                if (feature.equals(Constants.NAMESPACE_PREFIXES_FEATURE)) {
                    boolean state = fConfiguration.getFeature(featureId);
                    return state;
                }
                // http://xml.org/sax/features/string-interning
                //   controls the use of java.lang.String#intern() for strings
                //   passed to SAX handlers.
                //
                if (feature.equals(Constants.STRING_INTERNING_FEATURE)) {
                    return true;
                }

                //
                // Drop through and perform default processing
                //
            }

            //
            // Xerces Features
            //

            /*
            else if (featureId.startsWith(XERCES_FEATURES_PREFIX)) {
                //
                // Drop through and perform default processing
                //
            }
            */

            return fConfiguration.getFeature(featureId);
        }
        catch (XMLConfigurationException e) {
            String message = e.getMessage();
            if (e.getType() == XMLConfigurationException.NOT_RECOGNIZED) {
                throw new SAXNotRecognizedException(message);
            }
            else {
                throw new SAXNotSupportedException(message);
            }
        }

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
     * @exception SAXNotRecognizedException If the
     *            requested property is not known.
     * @exception SAXNotSupportedException If the
     *            requested property is known, but the requested
     *            value is not supported.
     */
    public void setProperty(String propertyId, Object value)
        throws SAXNotRecognizedException, SAXNotSupportedException {

        try {
            //
            // SAX2 core properties
            //

            if (propertyId.startsWith(Constants.SAX_PROPERTY_PREFIX)) {
                String property =
                    propertyId.substring(Constants.SAX_PROPERTY_PREFIX.length());
                //
                // http://xml.org/sax/properties/lexical-handler
                // Value type: org.xml.sax.ext.LexicalHandler
                // Access: read/write, pre-parse only
                //   Set the lexical event handler.
                //
                if (property.equals(Constants.LEXICAL_HANDLER_PROPERTY)) {
                    try {
                        setLexicalHandler((LexicalHandler)value);
                    }
                    catch (ClassCastException e) {
                        // REVISIT: Localize this error message. -ac
                        throw new SAXNotSupportedException(
                        "PAR012 For propertyID \""
                        +propertyId+"\", the value \""
                        +value+"\" cannot be cast to LexicalHandler."
                        +'\n'+propertyId+'\t'+value+"\tLexicalHandler");
                    }
                    return;
                }
                //
                // http://xml.org/sax/properties/declaration-handler
                // Value type: org.xml.sax.ext.DeclHandler
                // Access: read/write, pre-parse only
                //   Set the DTD declaration event handler.
                //
                if (property.equals(Constants.DECLARATION_HANDLER_PROPERTY)) {
                    try {
                        setDeclHandler((DeclHandler)value);
                    }
                    catch (ClassCastException e) {
                        // REVISIT: Localize this error message. -ac
                        throw new SAXNotSupportedException(
                        "PAR012 For propertyID \""
                        +propertyId+"\", the value \""
                        +value+"\" cannot be cast to DeclHandler."
                        +'\n'+propertyId+'\t'+value+"\tDeclHandler"
                        );
                    }
                    return;
                }
                //
                // http://xml.org/sax/properties/dom-node
                // Value type: DOM Node
                // Access: read-only
                //   Get the DOM node currently being visited, if the SAX parser is
                //   iterating over a DOM tree.  If the parser recognises and
                //   supports this property but is not currently visiting a DOM
                //   node, it should return null (this is a good way to check for
                //   availability before the parse begins).
                //
                if (property.equals(Constants.DOM_NODE_PROPERTY)) {
                    // REVISIT: Localize this error message. -ac
                    throw new SAXNotSupportedException(
                        "PAR013 Property \""+propertyId+"\" is read only."
                        +'\n'+propertyId
                        ); // read-only property
                }
                //
                // Drop through and perform default processing
                //
            }

            //
            // Xerces Properties
            //

            /*
            else if (propertyId.startsWith(XERCES_PROPERTIES_PREFIX)) {
                //
                // Drop through and perform default processing
                //
            }
            */

            //
            // Perform default processing
            //

            fConfiguration.setProperty(propertyId, value);
        }
        catch (XMLConfigurationException e) {
            String message = e.getMessage();
            if (e.getType() == XMLConfigurationException.NOT_RECOGNIZED) {
                throw new SAXNotRecognizedException(message);
            }
            else {
                throw new SAXNotSupportedException(message);
            }
        }

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
     * @exception SAXNotSupportedException If the
     *            requested property is known but not supported.
     */
    public Object getProperty(String propertyId)
        throws SAXNotRecognizedException, SAXNotSupportedException {

        try {
            //
            // SAX2 core properties
            //

            if (propertyId.startsWith(Constants.SAX_PROPERTY_PREFIX)) {
                String property =
                    propertyId.substring(Constants.SAX_PROPERTY_PREFIX.length());
                //
                // http://xml.org/sax/properties/lexical-handler
                // Value type: org.xml.sax.ext.LexicalHandler
                // Access: read/write, pre-parse only
                //   Set the lexical event handler.
                //
                if (property.equals(Constants.LEXICAL_HANDLER_PROPERTY)) {
                    return getLexicalHandler();
                }
                //
                // http://xml.org/sax/properties/declaration-handler
                // Value type: org.xml.sax.ext.DeclHandler
                // Access: read/write, pre-parse only
                //   Set the DTD declaration event handler.
                //
                if (property.equals(Constants.DECLARATION_HANDLER_PROPERTY)) {
                    return getDeclHandler();
                }
                //
                // http://xml.org/sax/properties/dom-node
                // Value type: DOM Node
                // Access: read-only
                //   Get the DOM node currently being visited, if the SAX parser is
                //   iterating over a DOM tree.  If the parser recognises and
                //   supports this property but is not currently visiting a DOM
                //   node, it should return null (this is a good way to check for
                //   availability before the parse begins).
                //
                if (property.equals(Constants.DOM_NODE_PROPERTY)) {
                    // REVISIT: Localize this error message. -Ac
                    throw new SAXNotSupportedException(
                    "PAR014 Cannot getProperty(\""+propertyId
                    +"\". No DOM Tree exists.\n"+propertyId
                    ); // we are not iterating a DOM tree
                }
                //
                // Drop through and perform default processing
                //
            }

            //
            // Xerces properties
            //

            /*
            else if (propertyId.startsWith(XERCES_PROPERTIES_PREFIX)) {
                //
                // Drop through and perform default processing
                //
            }
            */

            //
            // Perform default processing
            //

            return fConfiguration.getProperty(propertyId);
        }
        catch (XMLConfigurationException e) {
            String message = e.getMessage();
            if (e.getType() == XMLConfigurationException.NOT_RECOGNIZED) {
                throw new SAXNotRecognizedException(message);
            }
            else {
                throw new SAXNotSupportedException(message);
            }
        }

    } // getProperty(String):Object

    //
    // Protected methods
    //

    // SAX2 core properties

    /**
     * Set the DTD declaration event handler.
     * <p>
     * This method is the equivalent to the property:
     * <pre>
     * http://xml.org/sax/properties/declaration-handler
     * </pre>
     *
     * @param handler The new handler.
     *
     * @see #getDeclHandler
     * @see #setProperty
     */
    protected void setDeclHandler(DeclHandler handler)
        throws SAXNotRecognizedException, SAXNotSupportedException {

        if (fParseInProgress) {
            // REVISIT: Localize this error message. -Ac
            throw new SAXNotSupportedException(
                "PAR011 Feature: http://xml.org/sax/properties/declaration-handler"
                +" is not supported during parse."
                +"\nhttp://xml.org/sax/properties/declaration-handler");
        }
        fDeclHandler = handler;

    } // setDeclHandler(DeclHandler)

    /**
     * Returns the DTD declaration event handler.
     *
     * @see #setDeclHandler
     */
    protected DeclHandler getDeclHandler()
        throws SAXNotRecognizedException, SAXNotSupportedException {
        return fDeclHandler;
    } // getDeclHandler():DeclHandler

    /**
     * Set the lexical event handler.
     * <p>
     * This method is the equivalent to the property:
     * <pre>
     * http://xml.org/sax/properties/lexical-handler
     * </pre>
     *
     * @param handler lexical event handler
     *
     * @see #getLexicalHandler
     * @see #setProperty
     */
    protected void setLexicalHandler(LexicalHandler handler)
        throws SAXNotRecognizedException, SAXNotSupportedException {

        if (fParseInProgress) {
            // REVISIT: Localize this error message. -Ac
            throw new SAXNotSupportedException(
            "PAR011 Feature: http://xml.org/sax/properties/lexical-handler"
            +" is not supported during parse."
            +"\nhttp://xml.org/sax/properties/lexical-handler");
        }
        fLexicalHandler = handler;

    } // setLexicalHandler(LexicalHandler)

    /**
     * Returns the lexical handler.
     *
     * @see #setLexicalHandler
     */
    protected LexicalHandler getLexicalHandler()
        throws SAXNotRecognizedException, SAXNotSupportedException {
        return fLexicalHandler;
    } // getLexicalHandler():LexicalHandler

    //
    // XMLDocumentParser methods
    //

    /**
     * Reset all components before parsing.
     *
     * @throws XNIException Thrown if an error occurs during initialization.
     */
    public void reset() throws XNIException {
        super.reset();

        // reset state
        fInDTD = false;

        // features
        fNamespaces = fConfiguration.getFeature(NAMESPACES);           
        fNamespacePrefixes = fConfiguration.getFeature(NAMESPACE_PREFIXES);
        try {
            fNormalizeData = fConfiguration.getFeature(NORMALIZE_DATA);
        }
        catch (XMLConfigurationException e) {
            fNormalizeData = false;
        }
        
    } // reset()

    //
    // Classes
    //

    protected static class LocatorProxy
        implements Locator {

        //
        // Data
        //

        /** XML locator. */
        protected XMLLocator fLocator;

        //
        // Constructors
        //

        /** Constructs an XML locator proxy. */
        public LocatorProxy(XMLLocator locator) {
            fLocator = locator;
        }

        //
        // Locator methods
        //

        /** Public identifier. */
        public String getPublicId() {
            return fLocator.getPublicId();
        }

        /** System identifier. */
        public String getSystemId() {
            return fLocator.getExpandedSystemId();
        }
        /** Line number. */
        public int getLineNumber() {
            return fLocator.getLineNumber();
        }

        /** Column number. */
        public int getColumnNumber() {
            return fLocator.getColumnNumber();
        }

    } // class LocatorProxy

    protected static final class AttributesProxy
        implements AttributeList, Attributes {

        //
        // Data
        //

        /** XML attributes. */
        protected XMLAttributes fAttributes;

        //
        // Public methods
        //

        /** Sets the XML attributes. */
        public void setAttributes(XMLAttributes attributes) {
            fAttributes = attributes;
        } // setAttributes(XMLAttributes)

        public int getLength() {
            return fAttributes.getLength();
        }

        public String getName(int i) {
            return fAttributes.getQName(i);
        }

        public String getQName(int index) {
            return fAttributes.getQName(index);
        }

        public String getURI(int index) {
            // REVISIT: this hides the fact that internally we use
            //          null instead of empty string
            //          SAX requires URI to be a string or an empty string
            String uri= fAttributes.getURI(index);
            return uri != null ? uri : "";
        }

        public String getLocalName(int index) {
            return fAttributes.getLocalName(index);
        }

        public String getType(int i) {
            return fAttributes.getType(i);
        }

        public String getType(String name) {
            return fAttributes.getType(name);
        }

        public String getType(String uri, String localName) {
            return uri.equals("") ? fAttributes.getType(null, localName) :
                                    fAttributes.getType(uri, localName);
        }

        public String getValue(int i) {
            return fAttributes.getValue(i);
        }

        public String getValue(String name) {
            return fAttributes.getValue(name);
        }

        public String getValue(String uri, String localName) {
            return uri.equals("") ? fAttributes.getValue(null, localName) :
                                    fAttributes.getValue(uri, localName);
        }

        public int getIndex(String qName) {
            return fAttributes.getIndex(qName);
        }

        public int getIndex(String uri, String localPart) {
            return uri.equals("") ? fAttributes.getIndex(null, localPart) :
                                    fAttributes.getIndex(uri, localPart);
        }

    } // class AttributesProxy

} // class AbstractSAXParser