protected static final String PSVI_OUTPUT ="psvi_output.xml";

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
 * originally based on software copyright (c) 2001, International
 * Business Machines, Inc., http://www.apache.org.  For more
 * information on the Apache Software Foundation, please see
 * <http://www.apache.org/>.
 */

package xni;

import org.apache.xerces.impl.Constants;
import org.apache.xerces.impl.XMLNamespaceBinder;

import org.apache.xerces.util.SymbolTable;
import org.apache.xerces.util.DefaultErrorHandler;
import org.apache.xerces.util.MessageFormatter;
import org.apache.xerces.util.XMLAttributesImpl;

//for testing
import org.apache.xerces.impl.xs.psvi.*;
import org.apache.xerces.impl.xs.XSTypeDecl;
import org.apache.xerces.impl.xs.ElementPSVImpl;
import org.apache.xerces.impl.xs.AttributePSVImpl;

import org.apache.xml.serialize.IndentPrinter;
import org.apache.xml.serialize.EncodingInfo;
import org.apache.xml.serialize.OutputFormat;
import org.apache.xml.serialize.Printer;
import org.apache.xml.serialize.LineSeparator;

import org.apache.xerces.xni.Augmentations;
import org.apache.xerces.xni.NamespaceContext;
import org.apache.xerces.xni.QName;
import org.apache.xerces.xni.XMLAttributes;
import org.apache.xerces.xni.XMLDocumentHandler;
import org.apache.xerces.xni.XMLLocator;
import org.apache.xerces.xni.XMLResourceIdentifier;
import org.apache.xerces.xni.XMLString;
import org.apache.xerces.xni.XNIException;

import org.apache.xerces.xni.psvi.ItemPSVI;
import org.apache.xerces.xni.psvi.ElementPSVI;
import org.apache.xerces.xni.psvi.AttributePSVI;
import org.apache.xerces.xni.parser.XMLComponent;
import org.apache.xerces.xni.parser.XMLComponentManager;
import org.apache.xerces.xni.parser.XMLDocumentFilter;
import org.apache.xerces.xni.parser.XMLConfigurationException;
import org.apache.xerces.xni.parser.XMLErrorHandler;
import org.apache.xerces.xni.parser.XMLInputSource;
import org.apache.xerces.xni.parser.XMLParseException;

import java.io.*;
import java.util.*;


/**
 * This class is a intersepts XNI events and serialized
 * XML infoset and Post Schema Validation Infoset.
 * 
 * @author Arun  Yadav,Sun Miscrosystem.
 * @version $Id$
 */
public class PSVIWriter
implements XMLComponent, XMLDocumentFilter {


    public static final String XERCES_PSVI_NS = "http://apache.org/xml/2001/PSVInfosetExtension";

    /** Property identifier: Namespace Binder  */
    protected static final String NAMESPACE_BINDER =
    Constants.XERCES_PROPERTY_PREFIX + Constants.NAMESPACE_BINDER_PROPERTY;

    /** Property identifier: symbol table. */
    protected static final String SYMBOL_TABLE =
    Constants.XERCES_PROPERTY_PREFIX + Constants.SYMBOL_TABLE_PROPERTY;


    /** Feature id: include ignorable whitespace. */
    protected static final String INCLUDE_IGNORABLE_WHITESPACE =
    "http://apache.org/xml/features/dom/include-ignorable-whitespace";

    protected static final String PSVI_OUTPUT ="e:\\psvi_output.xml";

    /** Include ignorable whitespace. */
    protected boolean fIncludeIgnorableWhitespace;

    /** Recognized features. */
    protected static final String[] RECOGNIZED_FEATURES = {
        NAMESPACE_BINDER,
        INCLUDE_IGNORABLE_WHITESPACE,
        //  PSVINFOSET,
    };
    /** Recognized properties. */
    protected static final String[] RECOGNIZED_PROPERTIES={
        SYMBOL_TABLE,
    };

    /** PSVInfoset */
    protected boolean fPSVInfoset;

    /** Symbol: "". */
    private String fEmptySymbol;

    /** Symbol: "xml". */
    private String fXmlSymbol;

    /** Symbol: "xmlns". */
    private String fXmlnsSymbol;

    /** XMLNS namespace: XML-Infoset */
    public static final String XMLNS_URI ="http://www.w3.org/2000/xmlns/";

    /** Document handler. */
    protected XMLDocumentHandler fDocumentHandler;

    /** Symbol table. */
    protected SymbolTable fSymbolTable;

    /** NamespaceBinder*/
    protected XMLNamespaceBinder fNamespaceBinder;

    /** Attribute QName. */
    private QName fAttrQName = new QName();

    /** Attributes and Element Info  is  cached in stack */
    private Stack  _elementState =new Stack();

    /** The output stream. */
    private OutputStream    _output;

    /** The underlying writer. */
    private java.io.Writer _writer;

    private EncodingInfo    _encodingInfo;

    private final StringBuffer fErrorBuffer = new StringBuffer();

    /** The printer used for printing text parts. */
    protected Printer       _printer;


    public PSVIWriter() {
        System.out.println("Generating Schema Information Set Contribution (PSVI) \n"
                           + "which follow as a consequence of validation and/or assessment.");

        System.out.println("NOTE: Requires use of -s and -v");
        System.out.println("Output: generated in "+PSVI_OUTPUT);

    } // <init>()

    //REVISIT
    // 1. where to output the PSVI info to user( output console or file)?
    // 2. Is there any other  better way to format the output.
    public void reset(XMLComponentManager componentManager)
    throws XNIException {

        // Feature's name for PSVIWriter is not yet decided.
/*      try {
            fPSVInfoset = componentManager.getFeature(PSVINFOSET);
        }
        catch (XMLConfigurationException e) {
            fPSVInfoset = false;
        }*/
        /**For Testing */
        fPSVInfoset = true;

        fNamespaceBinder = (XMLNamespaceBinder)componentManager.getProperty(NAMESPACE_BINDER);
        fSymbolTable = (SymbolTable)componentManager.getProperty(SYMBOL_TABLE);
        fIncludeIgnorableWhitespace = componentManager.getFeature(INCLUDE_IGNORABLE_WHITESPACE);

        // save built-in entity names
        fEmptySymbol = fSymbolTable.addSymbol("");
        fXmlSymbol = fSymbolTable.addSymbol("xml");
        fXmlnsSymbol = fSymbolTable.addSymbol("xmlns");
        fErrorBuffer.setLength(0);
        try {
            OutputFormat outputFormat = new OutputFormat();
            outputFormat.setIndenting(true);
            outputFormat.setLineSeparator(LineSeparator.Windows);
            outputFormat.setLineWidth(150);
            outputFormat.setOmitComments(false);
            outputFormat.setOmitDocumentType(false);
            outputFormat.setOmitXMLDeclaration(false);

            FileOutputStream fos = new FileOutputStream(PSVI_OUTPUT);
            _output = new BufferedOutputStream(fos);

            _encodingInfo = outputFormat.getEncodingInfo();
            _writer = _encodingInfo.getWriter(_output);

            _printer = new IndentPrinter( _writer, outputFormat );
        }
        catch (Exception e) {
            e.printStackTrace();
        }
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
     * @param augs   Additional information that may include infoset augmentations
     */
    public void setDocumentHandler(XMLDocumentHandler documentHandler) {
        fDocumentHandler = documentHandler;
    } // setDocumentHandler(XMLDocumentHandler)


    //
    // XMLDocumentHandler methods
    //

    /**
     * This method notifies the start of an entity. General entities are just
     * specified by their name.
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
     *                 internal entities or a document entity that is
     *                 parsed from a java.io.Reader).
     * @param augs   Additional information that may include infoset augmentations
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void startGeneralEntity(String name,
                            XMLResourceIdentifier identifier,
                            String encoding, Augmentations augs)
    throws XNIException {
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
     * @param augs   Additional information that may include infoset augmentations
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void textDecl(String version, String encoding, Augmentations augs)
    throws XNIException {
        if (fDocumentHandler != null) {
            fDocumentHandler.textDecl(version, encoding, augs);
        }
    } // textDecl(String,String)

    /**
     * The start of the document.
     *
     * @param augs   Additional information that may include infoset augmentations
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void startDocument(XMLLocator locator, String encoding, Augmentations augs)
    throws XNIException {
        if (fPSVInfoset) {
            printIndentTag("<document"+
                           " xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance'"+
                           " xmlns:psv='"+ XERCES_PSVI_NS+"'"+
                           " xmlns='http://www.w3.org/2001/05/XMLInfoset'>");
        }
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
        if (fPSVInfoset) {
            printElement("characterEncodingScheme",encoding);
            printElement("standalone",standalone);
            printElement("version",version);
        }
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
    public void doctypeDecl(String rootElement,
                            String publicId, String systemId, Augmentations augs)
    throws XNIException {
        if (fPSVInfoset) {
            checkForChildren();
            printIndentTag("<docTypeDeclaration>");
            if (publicId != null)
                printElement("publicIdentifier", publicId);
            if (systemId != null)
                printElement("systemIdentifier", systemId);
            printUnIndentTag("</docTypeDeclaration>");
        }
        if (fDocumentHandler != null) {
            fDocumentHandler.doctypeDecl(rootElement, publicId, systemId, augs);
        }
    } // doctypeDecl(String,String,String)

    /**
     * A comment.
     *
     * @param text The text in the comment.
     * @param augs   Additional information that may include infoset augmentations
     *
     * @throws XNIException Thrown by application to signal an error.
     */
    public void comment(XMLString text, Augmentations augs) throws XNIException {
        if (fPSVInfoset) {
            checkForChildren();
            printIndentTag("<comment>");
            printElement("content", text.toString());
            printUnIndentTag("</comment>");
        }
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
    public void processingInstruction(String target,
                                      XMLString data, Augmentations augs)
    throws XNIException {
        if (fPSVInfoset) {
            checkForChildren();
            printIndentTag("<processingInstruction>");
            printElement("target",target);
            printElement("content",data.toString());
            printUnIndentTag("</processingInstruction>");
        }
        if (fDocumentHandler != null) {
            fDocumentHandler.processingInstruction(target, data, augs);
        }
    } // processingInstruction(String,XMLString)

    /**
     * The start of a namespace prefix mapping. This method will only be
     * called when namespace processing is enabled.
     *
     * @param prefix The namespace prefix.
     * @param uri    The URI bound to the prefix.
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void startPrefixMapping(String prefix, String uri, Augmentations augs)
    throws XNIException {
        if (fDocumentHandler != null) {
            fDocumentHandler.startPrefixMapping(prefix, uri, augs);
        }
    } // startPrefixMapping(String,String)

    /**
     * Binds the namespaces. This method will handle calling the
     * document handler to start the prefix mappings.
     * <p>
     * <strong>Note:</strong> This method makes use of the
     * fAttributeQName variable. Any contents of the variable will
     * be destroyed. Caller should copy the values out of this
     * temporary variable before calling this method.
     *
     * @param element    The name of the element.
     * @param attributes The element attributes.
     * @param augs   Additional information that may include infoset augmentations
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void startElement(QName element,
                             XMLAttributes attributes, Augmentations augs)
    throws XNIException {
        if (fPSVInfoset) {
            checkForChildren();

            _elementState.push(new ElementState(true));

            printIndentTag("<element>");
            printElement("namespaceName" , element.uri);
            printElement("localName" , element.localpart);
            printElement("prefix" , element.prefix);
            printAttributes(attributes);
            printPSVIStartElement(augs);
        }
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
        if (fPSVInfoset) {
            printIndentTag("<element>");
            printElement("namespaceName" , element.uri);
            printElement("localName" , element.localpart);
            printElement("prefix" , element.prefix);
            printAttributes(attributes);
            printTag("<children/>");
            printPSVIStartElement(augs);
            printPSVIEndElement(augs);
            printUnIndentTag("</element>");
        }
        if (fDocumentHandler != null) {
            fDocumentHandler.emptyElement(element, attributes, augs);
        }

    } // emptyElement(QName,XMLAttributes)

    /**
     * Character content.
     *
     * @param text The content.
     * @param augs   Additional information that may include infoset augmentations
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void characters(XMLString text, Augmentations augs)
    throws XNIException {
        // REVISIT: 2.6. Character Information Items requires character property for 
        //          each character. However, it also says:
        // "Each character is a logically separate information item, 
        //  but XML applications are free to chunk characters into larger 
        //  groups as necessary or desirable"
        //  XSV outputs each character separately.
        ElementPSVI elemPSVI = (ElementPSVI)augs.getItem(Constants.ELEMENT_PSVI);
        
        checkForChildren();
        if (elemPSVI != null) {
            if (!elemPSVI.getIsSchemaSpecified()){  // value was specified in the instance!
                printIndentTag("<character>");
                printElement("characterCode", text.toString());
                printElement("elementContentWhitespace", "false");
                printUnIndentTag("</character>");
            }
        }

        if (fDocumentHandler != null) {
            fDocumentHandler.characters(text,augs);
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
     * @param augs   Additional information that may include infoset augmentations
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void ignorableWhitespace(XMLString text, Augmentations augs)
    throws XNIException {
        if (fPSVInfoset && fIncludeIgnorableWhitespace) {
            int textLength = text.length;
            checkForChildren();
            // REVISIT: see characters()
            printIndentTag("<character>");
            printElement("characterCode", text.toString());
            printElement("elementContentWhitespace", "true");
            printUnIndentTag("</character>");

        }
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
    public void endElement(QName element, Augmentations augs)
    throws XNIException {
        if (fPSVInfoset) {
            ElementState fElementState =(ElementState)_elementState.peek();
            if (fElementState.isEmpty) {
                printTag("<children/>");
            }
            else {
                printUnIndentTag("</children>");
            }
            _elementState.pop();
            printinScopeNamespaces();
            printPSVIEndElement(augs);
            printUnIndentTag("</element>");
        }
        if (fDocumentHandler != null) {
            fDocumentHandler.endElement(element, augs);
        }
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
    public void endPrefixMapping(String prefix, Augmentations augs)
    throws XNIException {
        if (fDocumentHandler != null) {
            fDocumentHandler.endPrefixMapping(prefix, augs);
        }

    } // endPrefixMapping(String)

    /**
     * The start of a CDATA section.
     *
     * @param augs   Additional information that may include infoset augmentations
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void startCDATA(Augmentations augs) throws XNIException {
        if (fDocumentHandler != null) {
            fDocumentHandler.startCDATA(augs);
        }
    } // startCDATA()

    /**
     * The end of a CDATA section.
     *
     * @param augs   Additional information that may include infoset augmentations
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void endCDATA( Augmentations augs ) throws XNIException {
        if (fDocumentHandler != null) {
            fDocumentHandler.endCDATA(augs);
        }
    } // endCDATA()

    /**
     * The end of the document.
     *
     * @param augs   Additional information that may include infoset augmentations
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void endDocument( Augmentations augs ) throws XNIException {
        if (fPSVInfoset) {
            try {
                printUnIndentTag("</children>");
                printElement("documentElement","");
                //REVISIT : needs to implement the XMLDTDHandler
                printTag("<notations/>");
                printTag("<unparsedEntities/>");

                // REVISIT: how can we find out what is the baseURI?
                printElement("baseURI","");
                
                //REVISIT:
                printElement("allDeclarationsProcessed","true");
                printUnIndentTag("</document>");
                _printer.flush();
            }
            catch (IOException ex) {
                ex.printStackTrace();
            }
        }
        if (fDocumentHandler != null) {
            fDocumentHandler.endDocument(augs);
        }
    } // endDocument()

    /**
     * This method notifies the end of an entity. General entities are just
     * specified by their name.
     * <p>
     * <strong>Note:</strong> This method is not called for entity references
     * appearing as part of attribute values.
     *
     * @param name The name of the entity.
     * @param augs   Additional information that may include infoset augmentations
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void endGeneralEntity(String name, Augmentations augs) throws XNIException {
        if (fDocumentHandler != null) {
            fDocumentHandler.endGeneralEntity(name, augs);
        }
    } // endEntity(String)

    
    /* The following information will be available at the startElement call:
    * name, namespace, type, notation, validation context
    *
    * The following information will be available at the endElement call:
    * nil, specified, normalized value, member type, validity, error codes,
    * default
    */
    public void printPSVIStartElement(Augmentations augs) {
        ElementPSVI elemPSVI =(ElementPSVI)augs.getItem(Constants.ELEMENT_PSVI);
        if (elemPSVI != null) {

            // REVISIT: Should we store the values till end element call?
            printElement("psv:validationContext",elemPSVI.getValidationContext());

            XSTypeDefinition type = elemPSVI.getTypeDefinition();
            short definationType = type.getTypeCategory();
            if (definationType == XSTypeDecl.SIMPLE_TYPE) {
                printElement("psv:typeDefinitionType","simple");
            }
            else if (definationType == XSTypeDecl.COMPLEX_TYPE) {
                printElement("psv:typeDefinitionType","complex");
            }
            printElement("psv:typeDefinitionNamespace ",type.getNamespace());
            printElement("psv:typeDefinitionAnonymous",String.valueOf(type.getIsAnonymous()));
            printElement("psv:typeDefinitionName",type.getName());

            XSSimpleTypeDefinition memtype = elemPSVI.getMemberTypeDefinition();
            if (memtype != null) {
                printElement("psv:memberTypeDefinitionAnonymous",String.valueOf(memtype.getIsAnonymous()));
                printElement("psv:memberTypeDefinitionName",memtype.getName());
                printElement("psv:memberTypeDefinitionNamespace",memtype.getNamespace());
            }
            
            XSNotationDeclaration notation = elemPSVI.getNotation();
            if (notation != null) {
                printElement("psv:notationSystem",notation.getSystemId());
                printElement("psv:notationPublic",notation.getPublicId());
            }
        }
    }

    /* The following information will be available at the startElement call:
    * name, namespace, type, notation, validation context
    *
    * The following information will be available at the endElement call:
    * nil, specified, normalized value, member type, validity, error codes,
    * default
    */
    public void printPSVIEndElement(Augmentations augs) {
        ElementPSVI elemPSVI = (ElementPSVI)augs.getItem(Constants.ELEMENT_PSVI);
        if (elemPSVI != null) {


            short validation = elemPSVI.getValidationAttempted();
            if (validation == ItemPSVI.VALIDATION_NONE) {
                printElement("psv:validationAttempted","none");
            }
            else if (validation == ItemPSVI.VALIDATION_PARTIAL) {
                printElement("psv:validationAttempted","partial");
            }
            else if (validation == ItemPSVI.VALIDATION_FULL) {
                printElement("psv:validationAttempted","full");
            }


            short validity = elemPSVI.getValidity();
            if (validity == ItemPSVI.VALIDITY_UNKNOWN) {
                printElement("psv:validity","unknown");
            }
            else if (validity == ItemPSVI.VALIDITY_VALID) {
                printElement("psv:validity","valid");
            }
            else if (validity == ItemPSVI.VALIDITY_INVALID) {
                printElement("psv:validity","invalid");
            }
            //revisit
            Enumeration errorCode = elemPSVI.getErrorCodes();
            if (errorCode != null) {
                fErrorBuffer.append(errorCode.nextElement());
                
                while (errorCode.hasMoreElements()) {
                    fErrorBuffer.append(" ");
                    fErrorBuffer.append(errorCode.nextElement());
                }
                printElement("psv:schemaErrorCode",fErrorBuffer.toString());
                fErrorBuffer.setLength(0);
            }
            else {
                printElement("psv:schemaErrorCode","");
            }
            //printElement("psv:nil", String.valueOf(elemPSVI.getIsNil()));
            printElement("psv:schemaNormalizedValue",elemPSVI.getSchemaNormalizedValue());
            String specified = elemPSVI.getIsSchemaSpecified()?"schema":"infoset";
            printElement("psv:schemaSpecified",specified);

        }
    }

    public void printPSVIAttribute(Augmentations augs) {
        AttributePSVI attrPSVI =(AttributePSVI)augs.getItem(Constants.ATTRIBUTE_PSVI);
        if (attrPSVI !=null) {

            short validation = attrPSVI.getValidationAttempted();
            if (validation == ItemPSVI.VALIDATION_NONE) {
                printElement("psv:validationAttempted","none");
            }
            else if (validation == ItemPSVI.VALIDATION_FULL) {
                printElement("psv:validationAttempted","full");
            }

            printElement("psv:validationContext",attrPSVI.getValidationContext());

            short validity = attrPSVI.getValidity();
            if (validity == ItemPSVI.VALIDITY_UNKNOWN) {
                printElement("psv:validity","unknown");
            }
            else if (validity == ItemPSVI.VALIDITY_VALID) {
                printElement("psv:validity","valid");
            }
            else if (validity == ItemPSVI.VALIDITY_INVALID) {
                printElement("psv:validity","invalid");
            }

            //REVISIT
            Enumeration errorCode = attrPSVI.getErrorCodes();
            if (errorCode == null) {
                printElement("psv:schemaErrorCode","");
            }
            else {
                fErrorBuffer.append(errorCode.nextElement());
                while(errorCode.hasMoreElements()) {
                    fErrorBuffer.append(" ");
                    fErrorBuffer.append(errorCode.nextElement());
                }
                printElement("psv:schemaErrorCode",fErrorBuffer.toString());
                fErrorBuffer.setLength(0);

            }

            printElement("psv:schemaNormalizedValue",attrPSVI.getSchemaNormalizedValue());
            printElement("psv:schemaSpecified", (attrPSVI.getIsSchemaSpecified())?"schema":"infoset");

            XSTypeDefinition type = attrPSVI.getTypeDefinition();
            XSSimpleTypeDefinition memtype = attrPSVI.getMemberTypeDefinition();
            short definationType = type.getTypeCategory();
            if (definationType == XSTypeDecl.SIMPLE_TYPE) {
                printElement("psv:typeDefinitionType","simple");
            }

            printElement("psv:typeDefinitionNamespace",type.getNamespace());
            printElement("psv:typeDefinitionAnonymous",String.valueOf(type.getIsAnonymous()));
            printElement("psv:typeDefinitionName",type.getName());
            
            if (memtype != null) {
                printElement("psv:memberTypeDefinitionAnonymous",String.valueOf(memtype.getIsAnonymous()));
                printElement("psv:memberTypeDefinitionName",memtype.getName());
                printElement("psv:memberTypeDefinitionNamespace",memtype.getNamespace());
            }
        }
    }
    /**
     * This method write the element at the currrnt indent  level.
     *
     * @param tagname The name of the Element.
     *
     * @throws IOEXception
     */
    private void printTag(String tagname) {
        try {
            _printer.printText(tagname);
            _printer.breakLine();
        }
        catch (IOException ex) {
            ex.printStackTrace();
        }
    }//printTag
    /**
     * This method write the element at the current indent level and increase
     * the one level of indentation.
     *
     * @param The name of the Element.
     *
     * @throws IOException
     */
    private void printIndentTag(String tagname) {
        try {
            _printer.indent();
            _printer.printText(tagname);
            _printer.breakLine();
        }
        catch (IOException ex) {
            ex.printStackTrace();
        }
    }//printIndentTag
    /**
     * This method write the element at the current indent level and decrease
     * one level of indentation.
     *
     * @param the name of the Element.
     *
     */
    private void printUnIndentTag(String tagName) {
        try {
            _printer.unindent();
            _printer.printText(tagName);
            _printer.breakLine();
        }
        catch (IOException ex) {
            ex.printStackTrace();
        }
    }//printUnIndentTag

    /**
     * Write the Element Information Item for each element appearing in the XML
     * document. One of the element information items is the value of the
     * [document element] property of the document information item, corresponding
     * to the root of the element tree, and all other element information items
     * are accessible by recursively following its [children] property.
     *
     * @elementName  Name of the elment.
     * @elemmentValue  Value of the element
     */
    private void printElement(String elementName, String elementValue) {
        try {

            if (elementValue == null || elementValue == "") {
                _printer.printText("<"+elementName+" xsi:nil='true'/>");
                _printer.breakLine();
                return;
            }
            _printer.printText("<"+elementName+">");
            _printer.printText(elementValue);
            _printer.printText("</"+elementName+">");
            _printer.breakLine();
        }
        catch (IOException ex) {
            ex.printStackTrace();
        }
    }//printElement

    /**
     * Write an unordered set of attribute information items, one for each of
     * the attributes (specified or defaulted from the DTD) of this element.
     * Namespace declarations do not appear in this set. If the element has no
     * attributes, this set has no members.
     */
    private void printAttributes(XMLAttributes attributes) {
        boolean namespaceAttribute = false;
        boolean attrElement = false;

        int attrCount = attributes.getLength();

        if (attrCount == 0) {
            printTag("<attributes/>");
            printTag("<namespaceAttributes/>");
            return;
        }

        for (int i = 0; i < attrCount; i++) {
            String localpart = attributes.getLocalName(i);
            String prefix = attributes.getPrefix(i);
            if (prefix == fXmlnsSymbol || localpart == fXmlnsSymbol) {
                namespaceAttribute=true;
                continue;
            }
            if (!attrElement)
                printIndentTag("<attributes>");
            
            boolean psviAvailable =  (attributes.getAugmentations(i).getItem(Constants.ATTRIBUTE_PSVI)!=null);

            // REVISIT: in XSV attributes that are defaulted from XML Schema 
            // still appear as an item from XML Infoset and has the same properties
            // It looks  wrong.
            //
            printIndentTag("<attribute>");
            printElement("namespaceName",attributes.getURI(i));
            printElement("localName",attributes.getLocalName(i));
            printElement("prefix",attributes.getPrefix(i));
            printElement("normalizedValue",attributes.getValue(i));
            if (!psviAvailable) {
                // REVISIT: this attribute was defaulted from XML Schema
                // The following properties become unavailable/ not specified.
                printElement("specified",String.valueOf(attributes.isSpecified(i)));
                printElement("attributeType", attributes.getType(i));
            }  else{
                printElement("attributeType", null);
            }
            
            // REVISIT: how do we populate this property?
            printElement("references","");
            
            printPSVIAttribute(attributes.getAugmentations(i));
            printUnIndentTag("</attribute>");
            attrElement = true;
        }
        if (attrElement) {
            printUnIndentTag("</attributes>");
        }
        else {
            printTag("<attributes/>");
        }

        if (namespaceAttribute) {
            printNamespaceAttributes(attributes);
        }
        else {
            printTag("<namespaceAttributes/>");
        }
    }//printAttributes


        /**
     * Write an unordered set of attribute information items, one for each of
     * the namespace declarations (specified or defaulted from the DTD) of this
     * element. A declaration of the form xmlns="", which undeclares the default
     * namespace, counts as a namespace declaration. By definition, all
     * namespace attributes (including those named xmlns, whose [prefix]
     * property has no value) have a namespace URI of
     * http://www.w3.org/2000/xmlns/. If the element has no namespace
     * declarations, this set has no members
     */
    private void printNamespaceAttributes(XMLAttributes attributes) {
        
        int attrCount = attributes.getLength();

        printIndentTag("<namespaceAttributes>");
        for (int i = 0; i < attrCount; i++) {
            String localpart = attributes.getLocalName(i);
            String prefix = attributes.getPrefix(i);
            if (!(prefix == fXmlnsSymbol || localpart == fXmlnsSymbol))
                continue;
            printIndentTag("<attribute>");
            printElement("namespaceName",XMLNS_URI);
            printElement("localName",localpart);
            printElement("prefix",prefix);
            printElement("normalizedValue",attributes.getValue(i));
            printElement("specified",String.valueOf(attributes.isSpecified(i)));
            printElement("attributeType",attributes.getType(i));
            // REVISIT: how do we populate this property?
            printElement("references","");
            printPSVIAttribute(attributes.getAugmentations(i));
            printUnIndentTag("</attribute>");
        }
        printUnIndentTag("</namespaceAttributes>");
        
         
    }//printNamespacesAttributes()


    /**
     * Write an unordered set of namespace information items, one for each of the
     * namespaces in effect for this element. This set always contains an item
     * with the prefix xml which is implicitly bound to the namespace name
     * http://www.w3.org/XML/1998/namespace. It does not contain an item with the
     * prefix xmlns (used for declaring namespaces), since an application can
     * never encounter an element or attribute with that prefix. The set will
     * include namespace items corresponding to all of the members of
     * [namespace attributes], except for any representing a declaration of the
     * form xmlns="", which does not declare a namespace but rather undeclares
     * the default namespace
     */
    private void printinScopeNamespaces() {
        NamespaceContext namespaceContext = fNamespaceBinder.getNamespaceContext();
        NamespaceContext temp;
        String prefix;

        printIndentTag("<inScopeNamespaces>");
        while (namespaceContext!=null) {
            temp = namespaceContext.getParentContext();
            if (temp == null) {
                int prefixCount = namespaceContext.getDeclaredPrefixCount();
                for (int i=0;i<prefixCount;i++) {
                    printIndentTag("<namespace>");
                    prefix=namespaceContext.getDeclaredPrefixAt(i);
                    printElement("prefix",prefix);
                    printElement("namespaceName",namespaceContext.getURI(prefix));
                    printUnIndentTag("</namespace>");
                }
            }
            namespaceContext = temp;
        }
        printUnIndentTag("</inScopeNamespaces>");
    }//printinScopeNamespaces()

    /**
     *  Check whether the calling event is  first in children list ,
     * if yes print the <children>.
     */
    private  void checkForChildren() {
        if (!_elementState.empty()) {
            ElementState fElementState =(ElementState) _elementState.peek();
            if (fElementState.isEmpty == true) {
                printIndentTag("<children>");
                fElementState.isEmpty = false;
            }
        }
        else {
            printIndentTag("<children>");
            _elementState.push(new ElementState(false));
        }
    }//checkForChildren



    class ElementState {

        public boolean isEmpty;
        XMLAttributes fAttributes;

        public ElementState(XMLAttributes attributes) {
            fAttributes = attributes;
            isEmpty=true;
        }
        public ElementState(boolean value) {
            isEmpty=value;
        }
        public XMLAttributes getAttributes() {
            return fAttributes;
        }
        public void isEmpty(boolean value) {
            isEmpty = value;
        }
    }//class ElementState


} // class PSVIWriter