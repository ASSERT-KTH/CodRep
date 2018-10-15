if (elementValue == null || elementValue.length == 0) {

/*
 * Licensed to the Apache Software Foundation (ASF) under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The ASF licenses this file to You under the Apache License, Version 2.0
 * (the "License"); you may not use this file except in compliance with
 * the License.  You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package xni;

import java.io.IOException;
import java.util.Enumeration;
import java.util.HashMap;
import java.util.Stack;
import java.util.Vector;

import org.apache.xerces.dom.DocumentImpl;
import org.apache.xerces.impl.Constants;
import org.apache.xerces.impl.xs.SchemaSymbols;
import org.apache.xerces.util.DOMUtil;
import org.apache.xerces.util.NamespaceSupport;
import org.apache.xerces.util.XMLAttributesImpl;
import org.apache.xerces.util.XMLSymbols;
import org.apache.xerces.xni.Augmentations;
import org.apache.xerces.xni.NamespaceContext;
import org.apache.xerces.xni.QName;
import org.apache.xerces.xni.XMLAttributes;
import org.apache.xerces.xni.XMLDocumentHandler;
import org.apache.xerces.xni.XMLLocator;
import org.apache.xerces.xni.XMLResourceIdentifier;
import org.apache.xerces.xni.XMLString;
import org.apache.xerces.xni.XNIException;
import org.apache.xerces.xni.parser.XMLComponent;
import org.apache.xerces.xni.parser.XMLComponentManager;
import org.apache.xerces.xni.parser.XMLConfigurationException;
import org.apache.xerces.xni.parser.XMLDocumentFilter;
import org.apache.xerces.xni.parser.XMLDocumentSource;
import org.apache.xerces.xs.AttributePSVI;
import org.apache.xerces.xs.ElementPSVI;
import org.apache.xerces.xs.ItemPSVI;
import org.apache.xerces.xs.StringList;
import org.apache.xerces.xs.XSAnnotation;
import org.apache.xerces.xs.XSAttributeDeclaration;
import org.apache.xerces.xs.XSAttributeGroupDefinition;
import org.apache.xerces.xs.XSAttributeUse;
import org.apache.xerces.xs.XSComplexTypeDefinition;
import org.apache.xerces.xs.XSConstants;
import org.apache.xerces.xs.XSElementDeclaration;
import org.apache.xerces.xs.XSFacet;
import org.apache.xerces.xs.XSIDCDefinition;
import org.apache.xerces.xs.XSModel;
import org.apache.xerces.xs.XSModelGroup;
import org.apache.xerces.xs.XSModelGroupDefinition;
import org.apache.xerces.xs.XSMultiValueFacet;
import org.apache.xerces.xs.XSNamedMap;
import org.apache.xerces.xs.XSNamespaceItem;
import org.apache.xerces.xs.XSNamespaceItemList;
import org.apache.xerces.xs.XSNotationDeclaration;
import org.apache.xerces.xs.XSObject;
import org.apache.xerces.xs.XSObjectList;
import org.apache.xerces.xs.XSParticle;
import org.apache.xerces.xs.XSSimpleTypeDefinition;
import org.apache.xerces.xs.XSTypeDefinition;
import org.apache.xerces.xs.XSWildcard;
import org.w3c.dom.Attr;
import org.w3c.dom.Element;
import org.w3c.dom.Node;
import org.xml.sax.SAXNotRecognizedException;
import org.xml.sax.SAXNotSupportedException;

/**
 * This class is a intersepts XNI events and serialized
 * XML infoset and Post Schema Validation Infoset.
 *
 * @author Arun  Yadav,Sun Miscrosystem.
 * @author Peter McCracken, IBM
 * @version $Id$
 */
public class PSVIWriter implements XMLComponent, XMLDocumentFilter {

    public static final String XERCES_PSVI_NS =
        "http://apache.org/xml/2001/PSVInfosetExtension";

    /** Feature id: augment Post-Schema-Validation-Infoset */
    protected static final String PSVINFOSET =
        Constants.XERCES_FEATURE_PREFIX + Constants.SCHEMA_AUGMENT_PSVI;

    /** Feature id: include ignorable whitespace. */
    protected static final String INCLUDE_IGNORABLE_WHITESPACE =
        "http://apache.org/xml/features/dom/include-ignorable-whitespace";

    /** Include ignorable whitespace. */
    protected boolean fIncludeIgnorableWhitespace;

    /** Recognized features. */
    private static final String[] RECOGNIZED_FEATURES =
        { INCLUDE_IGNORABLE_WHITESPACE, PSVINFOSET, };

    /** Feature defaults. */
    private static final Boolean[] FEATURE_DEFAULTS = { null, null, };

    /** Recognized properties. */
    private static final String[] RECOGNIZED_PROPERTIES = {
    };

    /** Property defaults. */
    private static final Object[] PROPERTY_DEFAULTS = {
    };

    /** PSVInfoset */
    protected boolean fPSVInfoset;

    /** Document handler. */
    protected XMLDocumentHandler fDocumentHandler;

    /** Document source */
    protected XMLDocumentSource fDocumentSource;

    /** The namespace context for the received event stream */
    protected NamespaceContext fNamespaceContext;

    /** The namespace context for the new event stream */
    protected NamespaceContext fPSVINamespaceContext;

    /** Document Location */
    protected XMLLocator fDocumentLocation;

    /** Attributes and Element Info  is  cached in stack */
    private Stack _elementState = new Stack();

    /** The number used for anonymous types */
    protected int fAnonNum;

    /** The number that stores the indent level */
    protected int fIndent;

    /** The map used to store IDs for types and elements */
    protected HashMap fIDMap;

    /** A list of ids for defined XSObjects */
    protected Vector fDefined;

    private char[] fIndentChars =
        { '\t', '\t', '\t', '\t', '\t', '\t', '\t', '\t' };

    private XMLString newLine = new XMLString(new char[] { '\n' }, 0, 1);

    public PSVIWriter() {
        /*
        System.out.println(
            "Generating Schema Information Set Contribution (PSVI) \n"
                + "which follow as a consequence of validation and/or assessment.");

        System.out.println("NOTE: Requires use of -s and -v");
        System.out.println("Output: generated in " + PSVI_OUTPUT);
        */
    } // <init>()

    public void reset(XMLComponentManager componentManager)
        throws XNIException {

        try {
            fPSVInfoset = componentManager.getFeature(PSVINFOSET);
        }
        catch (XMLConfigurationException e) {
            fPSVInfoset = false;
        }
        fIncludeIgnorableWhitespace =
            componentManager.getFeature(INCLUDE_IGNORABLE_WHITESPACE);

        fAnonNum = 1000;
        fIDMap = new HashMap();
        fDefined = new Vector();
        fIndent = 0;
        fPSVINamespaceContext = new NamespaceSupport();
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
    public void setDocumentSource(XMLDocumentSource source) {
        fDocumentSource = source;
    } // setDocumentSource

    /** Returns the document source */
    public XMLDocumentSource getDocumentSource() {
        return fDocumentSource;
    } // getDocumentSource

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
    public void startGeneralEntity(
        String name,
        XMLResourceIdentifier identifier,
        String encoding,
        Augmentations augs)
        throws XNIException {
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
    } // textDecl(String,String)

    /**
     * The start of the document.
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void startDocument(
        XMLLocator locator,
        String encoding,
        NamespaceContext namespaceContext,
        Augmentations augs)
        throws XNIException {
        fNamespaceContext = namespaceContext;
        fDocumentLocation = locator;

        fPSVINamespaceContext.declarePrefix(
            "xsi",
            "http://www.w3.org/2001/XMLSchema-instance");
        fPSVINamespaceContext.declarePrefix("psv", XERCES_PSVI_NS);
        fPSVINamespaceContext.declarePrefix(
            "",
            "http://www.w3.org/2001/05/XMLInfoset");

        if (fDocumentHandler == null)
            return;

        fDocumentHandler.startDocument(
            locator,
            "UTF-8",
            fPSVINamespaceContext,
            null);

        Vector attributes = new Vector();
        attributes.add("xmlns:xsi");
        attributes.add("http://www.w3.org/2001/XMLSchema-instance");
        attributes.add(XMLSymbols.fCDATASymbol);
        attributes.add("xmlns:psv");
        attributes.add(XERCES_PSVI_NS);
        attributes.add(XMLSymbols.fCDATASymbol);
        attributes.add("xmlns");
        attributes.add("http://www.w3.org/2001/05/XMLInfoset");
        attributes.add(XMLSymbols.fCDATASymbol);
        sendIndentedElement("document", attributes);
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
    public void xmlDecl(
        String version,
        String encoding,
        String standalone,
        Augmentations augs)
        throws XNIException {
        if (fDocumentHandler == null)
            return;

        sendElementEvent("characterEncodingScheme", encoding);
        sendElementEvent("standalone", standalone);
        sendElementEvent("version", version);
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
    public void doctypeDecl(
        String rootElement,
        String publicId,
        String systemId,
        Augmentations augs)
        throws XNIException {
        if (fDocumentHandler == null)
            return;

        checkForChildren();
        sendIndentedElement("docTypeDeclaration");
        if (publicId != null)
            sendElementEvent("publicIdentifier", publicId);
        if (systemId != null)
            sendElementEvent("systemIdentifier", systemId);
        sendUnIndentedElement("docTypeDeclaration");
    } // doctypeDecl(String,String,String)

    /**
     * A comment.
     *
     * @param text The text in the comment.
     * @param augs   Additional information that may include infoset augmentations
     *
     * @throws XNIException Thrown by application to signal an error.
     */
    public void comment(XMLString text, Augmentations augs)
        throws XNIException {
        if (fDocumentHandler == null)
            return;

        checkForChildren();
        sendIndentedElement("comment");
        sendElementEvent("content", text);
        sendUnIndentedElement("comment");
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
    public void processingInstruction(
        String target,
        XMLString data,
        Augmentations augs)
        throws XNIException {
        if (fDocumentHandler == null)
            return;

        checkForChildren();
        sendIndentedElement("processingInstruction");
        sendElementEvent("target", target);
        sendElementEvent("content", data);
        sendUnIndentedElement("processingInstruction");
    } // processingInstruction(String,XMLString)

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
    public void startElement(
        QName element,
        XMLAttributes attributes,
        Augmentations augs)
        throws XNIException {
        if (fDocumentHandler == null)
            return;

        checkForChildren();

        _elementState.push(new ElementState(true));

        sendIndentedElement("element");
        sendElementEvent("namespaceName", element.uri);
        sendElementEvent("localName", element.localpart);
        sendElementEvent("prefix", element.prefix);
        processAttributes(attributes);
        processInScopeNamespaces();
        sendElementEvent("baseURI", fDocumentLocation.getBaseSystemId());
        if (fPSVInfoset) {
            processPSVIStartElement(augs);
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
    public void emptyElement(
        QName element,
        XMLAttributes attributes,
        Augmentations augs)
        throws XNIException {
        if (fDocumentHandler == null)
            return;

        checkForChildren();
        sendIndentedElement("element");
        sendElementEvent("namespaceName", element.uri);
        sendElementEvent("localName", element.localpart);
        sendElementEvent("prefix", element.prefix);
        processAttributes(attributes);
        processInScopeNamespaces();
        sendElementEvent("baseURI", fDocumentLocation.getBaseSystemId());
        if (fPSVInfoset) {
            processPSVIStartElement(augs);
        }
        sendEmptyElementEvent("children");
        if (fPSVInfoset) {
            processPSVIEndElement(augs);
        }
        sendUnIndentedElement("element");
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
        if (fDocumentHandler == null)
            return;

        checkForChildren();
        sendIndentedElement("character");
        sendElementEvent("textContent", text);
        // detecting whitespace is not relevant here
        // this is only useful if characters are output individually
        sendUnIndentedElement("character");
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
        if (fDocumentHandler == null)
            return;

        if (fIncludeIgnorableWhitespace) {
            this.characters(text, augs);
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
        if (fDocumentHandler == null)
            return;

        ElementState fElementState = (ElementState)_elementState.peek();
        if (fElementState.isEmpty) {
            sendEmptyElementEvent("children");
        }
        else {
            sendUnIndentedElement("children");
        }
        _elementState.pop();
        if (fPSVInfoset) {
            processPSVIStartElement(augs);
            processPSVIEndElement(augs);
        }
        sendUnIndentedElement("element");
    } // endElement(QName)

    /**
     * The start of a CDATA section.
     *
     * @param augs   Additional information that may include infoset augmentations
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void startCDATA(Augmentations augs) throws XNIException {
    } // startCDATA()

    /**
     * The end of a CDATA section.
     *
     * @param augs   Additional information that may include infoset augmentations
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void endCDATA(Augmentations augs) throws XNIException {
    } // endCDATA()

    /**
     * The end of the document.
     *
     * @param augs   Additional information that may include infoset augmentations
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void endDocument(Augmentations augs) throws XNIException {
        if (fDocumentHandler == null)
            return;

        sendUnIndentedElement("children");
        sendElementEvent("documentElement");
        // these aren't relevent for PSVI
        sendEmptyElementEvent("notations");
        sendEmptyElementEvent("unparsedEntities");

        sendElementEvent("baseURI", fDocumentLocation.getBaseSystemId());

        // do we ALWAYS process all declarations?  I think so - PJM
        // this isn't relevant to PSVI
        sendElementEvent("allDeclarationsProcessed", "true");
        sendUnIndentedElement("document");
        fDocumentHandler.endDocument(null);
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
    public void endGeneralEntity(String name, Augmentations augs)
        throws XNIException {
    } // endEntity(String)

    /**
     * Write an unordered set of attribute information items, one for each of
     * the attributes (specified or defaulted from the DTD) of this element.
     * Namespace declarations do not appear in this set. If the element has no
     * attributes, this set has no members.
     */
    private void processAttributes(XMLAttributes attributes) {
        boolean namespaceAttribute = false;
        boolean attrElement = false;

         int attrCount = attributes == null ? 0 : attributes.getLength();

        if (attrCount == 0) {
            sendEmptyElementEvent("attributes");
            sendEmptyElementEvent("namespaceAttributes");
            return;
        }

        for (int i = 0; i < attrCount; i++) {
            String localpart = attributes.getLocalName(i);
            String prefix = attributes.getPrefix(i);
            if (prefix.equals(XMLSymbols.PREFIX_XMLNS)
                || localpart.equals(XMLSymbols.PREFIX_XMLNS)) {
                namespaceAttribute = true;
                continue;
            }
            if (!attrElement)
                sendIndentedElement("attributes");

            sendIndentedElement("attribute");
            sendElementEvent("namespaceName", attributes.getURI(i));
            sendElementEvent("localName", attributes.getLocalName(i));
            sendElementEvent("prefix", attributes.getPrefix(i));
            sendElementEvent("normalizedValue", attributes.getValue(i));
            sendElementEvent(
                "specified",
                String.valueOf(attributes.isSpecified(i)));
            sendElementEvent("attributeType", attributes.getType(i));

            // this property isn't relevent to PSVI
            sendElementEvent("references");

            if (fPSVInfoset) {
                processPSVIAttribute(attributes.getAugmentations(i));
            }
            sendUnIndentedElement("attribute");
            attrElement = true;
        }
        if (attrElement) {
            sendUnIndentedElement("attributes");
        }
        else {
            sendEmptyElementEvent("attributes");
        }

        if (namespaceAttribute) {
            processNamespaceAttributes(attributes);
        }
        else {
            sendEmptyElementEvent("namespaceAttributes");
        }
    } //printAttributes

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
    private void processNamespaceAttributes(XMLAttributes attributes) {

        // we don't need to check for null, since that was checked for in processAttributes()
        int attrCount = attributes.getLength();

        sendIndentedElement("namespaceAttributes");
        for (int i = 0; i < attrCount; i++) {
            String localpart = attributes.getLocalName(i);
            String prefix = attributes.getPrefix(i);
            if (!(prefix.equals(XMLSymbols.PREFIX_XMLNS)
                || localpart.equals(XMLSymbols.PREFIX_XMLNS)))
                continue;
            sendIndentedElement("attribute");
            sendElementEvent("namespaceName", NamespaceContext.XMLNS_URI);
            sendElementEvent("localName", localpart);
            sendElementEvent("prefix", prefix);
            sendElementEvent("normalizedValue", attributes.getValue(i));
            sendElementEvent(
                "specified",
                String.valueOf(attributes.isSpecified(i)));
            sendElementEvent("attributeType", attributes.getType(i));
            // this property isn't relevent to PSVI
            sendElementEvent("references");
            if (fPSVInfoset) {
                processPSVIAttribute(attributes.getAugmentations(i));
            }
            sendUnIndentedElement("attribute");
        }
        sendUnIndentedElement("namespaceAttributes");

    } //printNamespacesAttributes()

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
    private void processInScopeNamespaces() {
        sendIndentedElement("inScopeNamespaces");
        sendIndentedElement("namespace");
        // print 'xml' binding
        sendElementEvent("prefix", "xml");
        sendElementEvent("namespaceName", NamespaceContext.XML_URI);
        sendUnIndentedElement("namespace");
        Enumeration prefixes = fNamespaceContext.getAllPrefixes();
        while (prefixes.hasMoreElements()) {
            sendIndentedElement("namespace");

            String prefix = (String)prefixes.nextElement();
            String uri = fNamespaceContext.getURI(prefix);
            sendElementEvent("prefix", prefix);
            sendElementEvent("namespaceName", uri);
            sendUnIndentedElement("namespace");

        }
        sendUnIndentedElement("inScopeNamespaces");
    } //printinScopeNamespaces()

    /* The following information will be available at the startElement call:
    * name, namespace, type, notation, validation context
    *
    * The following information will be available at the endElement call:
    * nil, specified, normalized value, member type, validity, error codes,
    * default
    */
    private void processPSVIStartElement(Augmentations augs) {
        if (augs == null)
            return;
        ElementPSVI elemPSVI =
            (ElementPSVI)augs.getItem(Constants.ELEMENT_PSVI);
        if (elemPSVI != null) {
            // Should we store the values till end element call? -- AY
            // I don't think so -- PJM
        }
    }

    /* The following information will be available at the startElement call:
    * name, namespace, type, notation, validation context
    *
    * The following information will be available at the endElement call:
    * nil, specified, normalized value, member type, validity, error codes,
    * default
    */
    private void processPSVIEndElement(Augmentations augs) {
        if (augs == null)
            return;
        ElementPSVI elemPSVI =
            (ElementPSVI)augs.getItem(Constants.ELEMENT_PSVI);
        if (elemPSVI != null) {

            processPSVISchemaInformation(elemPSVI);
            sendElementEvent(
                "psv:validationAttempted",
                this.translateValidationAttempted(
                    elemPSVI.getValidationAttempted()));
            // Would rather getValidationContext() return element info item.
            // This is non the same as XSV.
            sendElementEvent(
                "psv:validationContext",
                elemPSVI.getValidationContext());

            sendElementEvent(
                "psv:validity",
                this.translateValidity(elemPSVI.getValidity()));

            processPSVISchemaErrorCode(elemPSVI.getErrorCodes());
            sendElementEvent(
                "psv:schemaNormalizedValue",
                elemPSVI.getSchemaNormalizedValue());
            sendElementEvent(
                "psv:schemaSpecified",
                elemPSVI.getIsSchemaSpecified() ? "schema" : "infoset");
            sendElementEvent("psv:schemaDefault", elemPSVI.getSchemaDefault());

            processPSVITypeDefinitionRef(
                "psv:typeDefinition",
                elemPSVI.getTypeDefinition());
            processPSVITypeDefinitionRef(
                "psv:memberTypeDefinition",
                elemPSVI.getMemberTypeDefinition());
            // A value for nil is not necessary, since we output declaration, instead.
            // See http://www.w3.org/TR/xmlschema-1/#section-Element-Declaration-Information-Set-Contributions.
            sendElementEvent("psv:nil");

            sendIndentedElement("psv:declaration");
            processPSVIElementRef(
                "psv:elementDeclaration",
                elemPSVI.getElementDeclaration());
            sendUnIndentedElement("psv:declaration");
            processPSVIElementRef("psv:notation", elemPSVI.getNotation());
            // idref table does not have to be exposed, and is not exposed
            sendElementEvent("psv:idIdrefTable");
            // identity constraint table does not have to be exposed, and is not exposed
            sendElementEvent("psv:identityConstraintTable");
        }
    }

    private void processPSVIAttribute(Augmentations augs) {
        if (augs == null)
            return;
        AttributePSVI attrPSVI =
            (AttributePSVI)augs.getItem(Constants.ATTRIBUTE_PSVI);
        if (attrPSVI != null) {
            sendElementEvent(
                "psv:validationAttempted",
                this.translateValidationAttempted(
                    attrPSVI.getValidationAttempted()));
            // Would rather getValidationContext() return element info item.
            // This is not the same as XSV.
            sendElementEvent(
                "psv:validationContext",
                attrPSVI.getValidationContext());

            sendElementEvent(
                "psv:validity",
                this.translateValidity(attrPSVI.getValidity()));

            processPSVISchemaErrorCode(attrPSVI.getErrorCodes());
            sendElementEvent(
                "psv:schemaNormalizedValue",
                attrPSVI.getSchemaNormalizedValue());
            sendElementEvent(
                "psv:schemaSpecified",
                attrPSVI.getIsSchemaSpecified() ? "schema" : "infoset");
            sendElementEvent("psv:schemaDefault", attrPSVI.getSchemaDefault());

            processPSVITypeDefinitionRef(
                "psv:typeDefinition",
                attrPSVI.getTypeDefinition());
            processPSVITypeDefinitionRef(
                "psv:memberTypeDefinition",
                attrPSVI.getMemberTypeDefinition());

            if (attrPSVI.getAttributeDeclaration() == null) {
                sendElementEvent("psv:declaration");
            }
            else {
                sendIndentedElement("psv:declaration");
                processPSVIAttributeDeclarationRef(
                    attrPSVI.getAttributeDeclaration());
                sendUnIndentedElement("psv:declaration");
            }
        }
    }

    private void processPSVISchemaErrorCode(StringList errorCodes) {
        StringBuffer errorBuffer = new StringBuffer();
        if (errorCodes != null && errorCodes.getLength() > 0) {
            for (int i = 0; i < errorCodes.getLength() - 1; i++) {
                errorBuffer.append(errorCodes.item(i));
                errorBuffer.append(" ");
            }
            errorBuffer.append(errorCodes.item(errorCodes.getLength() - 1));
        }
        sendElementEvent("psv:schemaErrorCode", errorBuffer.toString());
    }

    private void processPSVISchemaInformation(ElementPSVI elemPSVI) {
        if (elemPSVI == null)
            return;
        XSModel schemaInfo = elemPSVI.getSchemaInformation();
        XSNamespaceItemList schemaNamespaces =
            schemaInfo == null ? null : schemaInfo.getNamespaceItems();
        if (schemaNamespaces == null || schemaNamespaces.getLength() == 0) {
            sendElementEvent("psv:schemaInformation");
        }
        else {
            sendIndentedElement("psv:schemaInformation");
            for (int i = 0; i < schemaNamespaces.getLength(); i++) {
                processPSVINamespaceItem(schemaNamespaces.item(i));
            }
            sendUnIndentedElement("psv:schemaInformation");
        }
    }

    private void processPSVINamespaceItem(XSNamespaceItem item) {
        if (item == null)
            return;

        String namespace = item.getSchemaNamespace();
        if (namespace != null && namespace.equals(Constants.NS_XMLSCHEMA)) {
            // we don't want to output information for schema for schemas
            return;
        }

        sendIndentedElement("psv:namespaceSchemaInformation");
        sendElementEvent("psv:schemaNamespace", namespace);

        // print out schema components
        processPSVISchemaComponents(item);

        // print out schema document information
        processPSVISchemaDocuments(item);

        // print out schema annotations
        processPSVISchemaAnnotations(item.getAnnotations());
        sendUnIndentedElement("psv:namespaceSchemaInformation");
    }

    private void processPSVISchemaDocuments(XSNamespaceItem item) {
        StringList locations =
            item == null ? null : item.getDocumentLocations();
        if (locations == null || locations.getLength() == 0) {
            sendEmptyElementEvent("psv:schemaDocuments");
            return;
        }
        sendIndentedElement("psv:schemaDocuments");
        for (int i = 0; i < locations.getLength(); i++) {
            sendIndentedElement("psv:schemaDocument");
            sendElementEvent("psv:documentLocation", locations.item(i));
            // It's supposed to point to a <document> element, and we're not really
            // dealing with those (except for the one at the root)
            sendElementEvent("psv:document");
            sendUnIndentedElement("psv:schemaDocument");
        }
        sendUnIndentedElement("psv:schemaDocuments");
    }

    private void processPSVISchemaComponents(XSNamespaceItem item) {
        if (item == null) {
            sendEmptyElementEvent("psv:schemaComponents");
            return;
        }

        // it we happen to not get any components, this will output a start tag
        // and a close tag, instead of an empty element tag.  This isn't a big
        // deal, though
        sendIndentedElement("psv:schemaComponents");

        // typeDefinitions
        XSNamedMap components = item.getComponents(XSConstants.TYPE_DEFINITION);
        for (int i = 0; i < components.getLength(); i++) {
            processPSVITypeDefinition((XSTypeDefinition)components.item(i));
        }
        // elementDeclarations
        components = item.getComponents(XSConstants.ELEMENT_DECLARATION);
        for (int i = 0; i < components.getLength(); i++) {
            processPSVIElementDeclaration(
                (XSElementDeclaration)components.item(i));
        }
        // attributeDeclarations
        components = item.getComponents(XSConstants.ATTRIBUTE_DECLARATION);
        for (int i = 0; i < components.getLength(); i++) {
            processPSVIAttributeDeclaration(
                (XSAttributeDeclaration)components.item(i));
        }
        // modelGroupDefinitions
        components = item.getComponents(XSConstants.MODEL_GROUP_DEFINITION);
        for (int i = 0; i < components.getLength(); i++) {
            processPSVIModelGroupDefinition(
                (XSModelGroupDefinition)components.item(i));
        }
        // attributeGroupDefinitions
        components = item.getComponents(XSConstants.ATTRIBUTE_GROUP);
        for (int i = 0; i < components.getLength(); i++) {
            processPSVIAttributeGroupDefinition(
                (XSAttributeGroupDefinition)components.item(i));
        }
        // notationDeclarations
        components = item.getComponents(XSConstants.NOTATION_DECLARATION);
        for (int i = 0; i < components.getLength(); i++) {
            processPSVINotationDeclaration(
                (XSNotationDeclaration)components.item(i));
        }
        sendUnIndentedElement("psv:schemaComponents");
    }

    private void processPSVITypeDefinition(XSTypeDefinition type) {
        if (type == null)
            return;
        if (type.getTypeCategory() == XSTypeDefinition.COMPLEX_TYPE) {
            processPSVIComplexTypeDefinition((XSComplexTypeDefinition)type);
        }
        else if (type.getTypeCategory() == XSTypeDefinition.SIMPLE_TYPE) {
            processPSVISimpleTypeDefinition((XSSimpleTypeDefinition)type);
        }
        else {
            throw new IllegalArgumentException(
                "Unknown type definition value: " + type.getType());
        }
    }

    private void processPSVIComplexTypeDefinition(XSComplexTypeDefinition type) {
        if (type == null)
            return;
        sendIndentedElementWithID("psv:complexTypeDefinition", type);
        sendElementEvent("psv:name", type.getName());
        sendElementEvent("psv:targetNamespace", type.getNamespace());
        processPSVITypeDefinitionOrRef(
            "psv:baseTypeDefinition",
            type.getBaseType());
        sendElementEvent(
            "psv:derivationMethod",
            this.translateDerivation(type.getDerivationMethod()));
        sendElementEvent("psv:final", this.translateBlockOrFinal(type.getFinal()));
        sendElementEvent("psv:abstract", String.valueOf(type.getAbstract()));
        processPSVIAttributeUses(type.getAttributeUses());
        processPSVIAttributeWildcard(type.getAttributeWildcard());
        sendIndentedElement("psv:contentType");
        sendElementEvent(
            "psv:variety",
            this.translateContentType(type.getContentType()));
        XSSimpleTypeDefinition simpleType = type.getSimpleType();
        if(simpleType == null || (!simpleType.getAnonymous() || fDefined.contains(this.getID(simpleType)))) {
            processPSVIElementRef("psv:simpleTypeDefinition", simpleType);
        }
        else {
            processPSVISimpleTypeDefinition(simpleType);
        }
        processPSVIParticle(type.getParticle());
        sendUnIndentedElement("psv:contentType");
        sendElementEvent(
            "psv:prohibitedSubstitutions",
            this.translateBlockOrFinal(type.getProhibitedSubstitutions()));
        processPSVIAnnotations(type.getAnnotations());
        sendUnIndentedElement("psv:complexTypeDefinition");
    }

    private void processPSVISimpleTypeDefinition(XSSimpleTypeDefinition type) {
        if (type == null) {
        	sendElementEvent("psv:simpleTypeDefinition");
            return;
        }
            
        sendIndentedElementWithID("psv:simpleTypeDefinition", type);
        sendElementEvent("psv:name", type.getName());
        sendElementEvent("psv:targetNamespace", type.getNamespace());
        processPSVITypeDefinitionOrRef(
            "psv:baseTypeDefinition",
            type.getBaseType());
        processPSVITypeDefinitionOrRef(
            "psv:primitiveTypeDefinition",
            type.getPrimitiveType());
        processPSVIFacets(type);

        sendIndentedElement("psv:fundamentalFacets");
        sendIndentedElement("psv:ordered");
        sendElementEvent("psv:value", this.translateOrdered(type.getOrdered()));
        sendUnIndentedElement("psv:ordered");
        sendIndentedElement("psv:bounded");
        sendElementEvent("psv:value", String.valueOf(type.getBounded()));
        sendUnIndentedElement("psv:bounded");
        sendIndentedElement("psv:cardinality");
        sendElementEvent("psv:value", String.valueOf(type.getFinite()));
        sendUnIndentedElement("psv:cardinality");
        sendIndentedElement("psv:numeric");
        sendElementEvent("psv:value", String.valueOf(type.getNumeric()));
        sendUnIndentedElement("psv:numeric");
        sendUnIndentedElement("psv:fundamentalFacets");

        sendElementEvent("psv:final", this.translateBlockOrFinal(type.getFinal()));
        sendElementEvent(
            "psv:variety",
            this.translateVariety(type.getVariety()));
        processPSVITypeDefinitionOrRef(
            "psv:itemTypeDefinition",
            type.getItemType());
        processPSVIMemberTypeDefinitions(type.getMemberTypes());
        processPSVIAnnotations(type.getAnnotations());
        sendUnIndentedElement("psv:simpleTypeDefinition");
    }

    private void processPSVIFacets(XSSimpleTypeDefinition type) {
        if (type == null)
            return;
        XSObjectList facets = type.getFacets();
        XSObjectList multiValueFacets = type.getMultiValueFacets();
        if ((facets == null || facets.getLength() == 0)
            && (multiValueFacets == null || multiValueFacets.getLength() == 0)) {
            sendElementEvent("psv:facets");
        }
        else {
            sendIndentedElement("psv:facets");
            if (facets != null) {
                for (int i = 0; i < facets.getLength(); i++) {
                    XSFacet facet = (XSFacet)facets.item(i);
                    String name = this.translateFacetKind(facet.getFacetKind());
                    sendIndentedElement("psv:" + name);
                    sendElementEvent("psv:value", facet.getLexicalFacetValue());
                    sendElementEvent(
                        "psv:fixed",
                        String.valueOf(facet.getFixed()));
                    processPSVIAnnotation(facet.getAnnotation());
                    sendUnIndentedElement("psv:" + name);
                }
            }
            if (multiValueFacets != null) {
                for (int i = 0; i < multiValueFacets.getLength(); i++) {
                    XSMultiValueFacet facet =
                        (XSMultiValueFacet)multiValueFacets.item(i);
                    String name = this.translateFacetKind(facet.getFacetKind());
                    sendIndentedElement("psv:" + name);
                    StringList values = facet.getLexicalFacetValues();
                    for (int j = 0; j < values.getLength(); j++) {
                        sendElementEvent("psv:value", values.item(j));
                    }
                    sendElementEvent("psv:fixed", "false");
                    processPSVIAnnotations(facet.getAnnotations());
                    sendUnIndentedElement("psv:" + name);
                }
            }
            sendUnIndentedElement("psv:facets");
        }
    }

    private void processPSVIMemberTypeDefinitions(XSObjectList memTypes) {
        if (memTypes == null || memTypes.getLength() == 0) {
            sendElementEvent("psv:memberTypeDefinitions");
        }
        else {
            sendIndentedElement("psv:memberTypeDefinitions");
            for (int i = 0; i < memTypes.getLength(); i++) {
                processPSVITypeDefinitionOrRef(
                    "psv:memberTypeDefinition",
                    (XSTypeDefinition)memTypes.item(i));
            }
            sendUnIndentedElement("psv:memberTypeDefinitions");
        }
    }

    /* It's possible that this method will send events for null annotations, i.e.
     * <psv:annotations>
     *     <psv:annotation xsi:nil="true"/>
     *     <psv:annotation>...</psv:annotation>
     * </psv:annotations>
     *
     * This is because of the way multi-value facet is implemented.  It represents
     * the annotation on each value of the facet, and if a value doesn't have one,
     * it's corresponding annotation is null.  Thus, it's possible for the first
     * annotation to be null, but the second one to be exist.
     *
     * An exception to this is if all of the annotations are null; then I output
     * <psv:annotations xsi:nil="true"/>
     */
    private void processPSVIAnnotations(XSObjectList annotations) {
        boolean empty = true;
        if (annotations != null && annotations.getLength() > 0) {
            for (int i = 0; i < annotations.getLength(); i++) {
                if (annotations.item(i) != null) {
                    empty = false;
                    break;
                }
            }
        }

        if (empty) {
            sendElementEvent("psv:annotations");
        }
        else {
            sendIndentedElement("psv:annotations");
            for (int i = 0; i < annotations.getLength(); i++) {
                processPSVIAnnotation((XSAnnotation)annotations.item(i));
            }
            sendUnIndentedElement("psv:annotations");
        }
    }

    private void processPSVISchemaAnnotations(XSObjectList annotations) {
        if (annotations == null || annotations.getLength() == 0) {
            sendElementEvent("psv:schemaAnnotations");
        }
        else {
            sendIndentedElement("psv:schemaAnnotations");
            for (int i = 0; i < annotations.getLength(); i++) {
                processPSVIAnnotation((XSAnnotation)annotations.item(i));
            }
            sendUnIndentedElement("psv:schemaAnnotations");
        }
    }

    private void processPSVIAttributeUses(XSObjectList uses) {
        if (uses == null || uses.getLength() == 0) {
            sendElementEvent("psv:attributeUses");
        }
        else {
            sendIndentedElement("psv:attributeUses");
            for (int i = 0; i < uses.getLength(); i++) {
                XSAttributeUse use = (XSAttributeUse)uses.item(i);
                sendIndentedElement("psv:attributeUse");
                sendElementEvent("psv:required", String.valueOf(use.getRequired()));
                processPSVIAttributeDeclarationOrRef(use.getAttrDeclaration());
                processPSVIValueConstraint(use.getConstraintType(), use.getConstraintValue());
                sendUnIndentedElement("psv:attributeUse");
            }
            sendUnIndentedElement("psv:attributeUses");
        }
    }

    private void processPSVIAttributeWildcard(XSWildcard wildcard) {
        if (wildcard == null) {
            sendElementEvent("psv:attributeWildcard");
        }
        else {
            sendIndentedElement("psv:attributeWildcard");
            processPSVIWildcard(wildcard);
            sendUnIndentedElement("psv:attributeWildcard");
        }
    }

    private void processPSVIWildcard(XSWildcard wildcard) {
        if (wildcard == null)
            return;
        sendIndentedElement("psv:wildcard");
        sendIndentedElement("psv:namespaceConstraint");
        sendElementEvent(
            "psv:variety",
            this.translateConstraintType(wildcard.getConstraintType()));

        StringBuffer constraintBuffer = new StringBuffer();
        StringList constraints = wildcard.getNsConstraintList();
        if (constraints != null && constraints.getLength() > 0) {
            for (int i = 0; i < constraints.getLength() - 1; i++) {
                constraintBuffer.append(constraints.item(i));
                constraintBuffer.append(" ");
            }
            constraintBuffer.append(
                constraints.item(constraints.getLength() - 1));
        }
        sendElementEvent("psv:namespaces", constraintBuffer.toString());

        sendUnIndentedElement("psv:namespaceConstraint");
        sendElementEvent(
            "psv:processContents",
            this.translateProcessContents(wildcard.getProcessContents()));
        processPSVIAnnotation(wildcard.getAnnotation());
        sendUnIndentedElement("psv:wildcard");
    }

    private void processPSVIAnnotation(XSAnnotation ann) {
        if (ann == null) {
            sendElementEvent("psv:annotation");
        }
        else {
            sendIndentedElement("psv:annotation");
            // We can't get all the information from DOM, but I've outputed what
            // we can get -- PJM
            Node dom = new DocumentImpl();
            ann.writeAnnotation(dom, XSAnnotation.W3C_DOM_DOCUMENT);

            // this child will be the annotation element
            Element annot = DOMUtil.getFirstChildElement(dom);

            processDOMElement(
                annot,
                SchemaSymbols.ELT_APPINFO,
                "psv:applicationInformation");
            processDOMElement(
                annot,
                SchemaSymbols.ELT_DOCUMENTATION,
                "psv:userInformation");
            processDOMAttributes(annot);
            sendUnIndentedElement("psv:annotation");
        }
    }

    private void processDOMElement(
        Node node,
        String elementName,
        String tagName) {
        if (node == null)
            return;
        boolean foundElem = false;
        for (Element child = DOMUtil.getFirstChildElement(node);
            child != null;
            child = DOMUtil.getNextSiblingElement(child)) {
            if (DOMUtil.getLocalName(child).equals(elementName)) {
                if (!foundElem) {
                    sendIndentedElement(tagName);
                    foundElem = true;
                }
                sendIndentedElement("element");
                sendElementEvent(
                    "namespaceName",
                    DOMUtil.getNamespaceURI(child));
                sendElementEvent("localName", DOMUtil.getLocalName(child));
                sendElementEvent("prefix", child.getPrefix());
                sendIndentedElement("children");
                sendIndentedElement("character");
                sendElementEvent("textContent", DOMUtil.getChildText(child));
                sendUnIndentedElement("character");
                sendUnIndentedElement("children");

                //Create XMLAttributes from DOM
                Attr[] atts = (Element) child == null ? null : DOMUtil.getAttrs((Element) child);
                XMLAttributes attrs = new XMLAttributesImpl();
                for (int i=0; i<atts.length; i++) {
                    Attr att = (Attr)atts[i];
                    attrs.addAttribute(
                            new QName(att.getPrefix(), att.getLocalName(), att.getName(), att.getNamespaceURI()),
                            "CDATA" ,att.getValue()
                            );
                }

                processAttributes(attrs);
                sendUnIndentedElement("element");
            }
        }
        if (foundElem) {
            sendUnIndentedElement(tagName);
        }
        else {
            sendEmptyElementEvent(tagName);
        }
    }

    private void processDOMAttributes(Element elem) {
        Attr[] atts = elem == null ? null : DOMUtil.getAttrs(elem);

        boolean namespaceAttribute = false;
        boolean attrElement = false;

        int attrCount = atts == null ? 0 : atts.length;

        if (attrCount == 0) {
            sendEmptyElementEvent("attributes");
            sendEmptyElementEvent("namespaceAttributes");
            return;
        }

        for (int i = 0; i < attrCount; i++) {
            Attr att = (Attr)atts[i];
            String localpart = DOMUtil.getLocalName(att);
            String prefix = att.getPrefix();
            if (localpart.equals(XMLSymbols.PREFIX_XMLNS)
                || prefix.equals(XMLSymbols.PREFIX_XMLNS)) {
                namespaceAttribute = true;
                continue;
            }
            if (!attrElement)
                sendIndentedElement("attributes");

            sendIndentedElement("attribute");
            sendElementEvent("namespaceName", DOMUtil.getNamespaceURI(att));
            sendElementEvent("localName", DOMUtil.getLocalName(att));
            sendElementEvent("prefix", att.getPrefix());
            sendElementEvent("normalizedValue", att.getValue());
            sendElementEvent(
                "specified",
                String.valueOf(att.getSpecified()));
            sendElementEvent("attributeType");

            // this property isn't relevent to PSVI
            sendElementEvent("references");

            sendUnIndentedElement("attribute");
            attrElement = true;
        }
        if (attrElement) {
            sendUnIndentedElement("attributes");
        }
        else {
            sendEmptyElementEvent("attributes");
        }

        if (namespaceAttribute) {
            sendIndentedElement("namespaceAttributes");
            for (int i = 0; i < attrCount; i++) {
                Attr att = (Attr)atts[i];
                String localpart = DOMUtil.getLocalName(att);
                String prefix = att.getPrefix();
                if (localpart.equals(XMLSymbols.PREFIX_XMLNS)
                    || prefix.equals(XMLSymbols.PREFIX_XMLNS)) {

                    sendIndentedElement("attribute");
                    sendElementEvent("namespaceName", DOMUtil.getNamespaceURI(att));
                    sendElementEvent("localName", DOMUtil.getLocalName(att));
                    sendElementEvent("prefix", att.getPrefix());
                    sendElementEvent("normalizedValue", att.getValue());
                    sendElementEvent(
                        "specified",
                        String.valueOf(att.getSpecified()));
                    sendElementEvent("attributeType");

                    // this property isn't relevent to PSVI
                    sendElementEvent("references");

                    sendUnIndentedElement("attribute");
                }
            }
            sendUnIndentedElement("namespaceAttributes");
        }
        else {
            sendEmptyElementEvent("namespaceAttributes");
        }
    }

    private void processPSVIElementDeclaration(XSElementDeclaration elem) {
        if (elem == null)
            return;
        sendIndentedElementWithID("psv:elementDeclaration", elem);
        sendElementEvent("psv:name", elem.getName());
        sendElementEvent("psv:targetNamespace", elem.getNamespace());
        processPSVITypeDefinitionOrRef(
            "psv:typeDefinition",
            elem.getTypeDefinition());
        processPSVIScope("psv:scope", elem.getEnclosingCTDefinition(), elem.getScope());
        processPSVIValueConstraint(elem.getConstraintType(), elem.getConstraintValue());
        sendElementEvent("psv:nillable", String.valueOf(elem.getNillable()));
        processPSVIIdentityConstraintDefinitions(elem.getIdentityConstraints());
        processPSVISubstitutionGroupAffiliation(elem);

        sendElementEvent(
            "psv:substitutionGroupExclusions",
            this.translateBlockOrFinal(elem.getSubstitutionGroupExclusions()));
        sendElementEvent(
            "psv:disallowedSubstitutions",
            this.translateBlockOrFinal(elem.getDisallowedSubstitutions()));
        sendElementEvent("psv:abstract", String.valueOf(elem.getAbstract()));
        processPSVIAnnotation(elem.getAnnotation());
        sendUnIndentedElement("psv:elementDeclaration");
    }

    private void processPSVIAttributeDeclaration(XSAttributeDeclaration attr) {
        if (attr == null)
            return;
        sendIndentedElementWithID("psv:attributeDeclaration", attr);
        sendElementEvent("psv:name", attr.getName());
        sendElementEvent("psv:targetNamespace", attr.getNamespace());
        processPSVITypeDefinitionOrRef(
            "psv:typeDefinition",
            attr.getTypeDefinition());
        processPSVIScope("psv:scope", attr.getEnclosingCTDefinition(), attr.getScope());
        processPSVIValueConstraint(attr.getConstraintType(), attr.getConstraintValue());
        processPSVIAnnotation(attr.getAnnotation());
        sendUnIndentedElement("psv:attributeDeclaration");
    }

    private void processPSVIAttributeGroupDefinition(XSAttributeGroupDefinition ag) {
        if (ag == null)
            return;
        sendIndentedElementWithID("psv:attributeGroupDefinition", ag);
        sendElementEvent("psv:name", ag.getName());
        sendElementEvent("psv:targetNamespace", ag.getNamespace());
        processPSVIAttributeUses(ag.getAttributeUses());
        processPSVIAttributeWildcard(ag.getAttributeWildcard());
        processPSVIAnnotation(ag.getAnnotation());
        sendUnIndentedElement("psv:attributeGroupDefinition");
    }

    private void processPSVIModelGroupDefinition(XSModelGroupDefinition mgd) {
        if (mgd == null) {
            sendElementEvent("psv:modelGroupDefinition");
        }
        else {
            sendIndentedElementWithID("psv:modelGroupDefinition", mgd);
            sendElementEvent("psv:name", mgd.getName());
            sendElementEvent("psv:targetNamespace", mgd.getNamespace());
            processPSVIModelGroup(mgd.getModelGroup());
            processPSVIAnnotation(mgd.getAnnotation());
            sendUnIndentedElement("psv:modelGroupDefinition");
        }
    }

    private void processPSVIModelGroup(XSModelGroup mg) {
        if (mg == null) {
            sendElementEvent("psv:modelGroup");
        }
        else {
            sendIndentedElement("psv:modelGroup");
            sendElementEvent(
                "psv:compositor",
                this.translateCompositor(mg.getCompositor()));
            processPSVIParticles(mg.getParticles());
            processPSVIAnnotation(mg.getAnnotation());
            sendUnIndentedElement("psv:modelGroup");
        }
    }

    private void processPSVINotationDeclaration(XSNotationDeclaration not) {
        if (not == null) {
            sendElementEvent("psv:notationDeclaration");
        }
        else {
            sendIndentedElementWithID("psv:notationDeclaration", not);
            sendElementEvent("psv:name", not.getName());
            sendElementEvent("psv:targetNamespace", not.getNamespace());
            sendElementEvent("systemIdentifier", not.getSystemId());
            sendElementEvent("publicIdentifier", not.getPublicId());
            processPSVIAnnotation(not.getAnnotation());
            sendUnIndentedElement("psv:notationDeclaration");
        }
    }

    private void processPSVIIdentityConstraintDefinitions(XSNamedMap constraints) {
        if (constraints == null || constraints.getLength() == 0) {
            sendElementEvent("psv:identityConstraintDefinitions");
        }
        else {
            sendIndentedElement("psv:identityConstraintDefinitions");
            for (int i = 0; i < constraints.getLength(); i++) {
                XSIDCDefinition constraint =
                    (XSIDCDefinition)constraints.item(i);
                sendIndentedElementWithID(
                    "psv:identityConstraintDefinition",
                    constraint);
                sendElementEvent("psv:name", constraint.getName());
                sendElementEvent(
                    "psv:targetNamespace",
                    constraint.getNamespace());
                sendElementEvent(
                    "psv:identityConstraintCategory",
                    this.translateCategory(constraint.getCategory()));
                sendIndentedElement("psv:selector");
                processPSVIXPath(constraint.getSelectorStr());
                sendUnIndentedElement("psv:selector");
                processPSVIFields(constraint.getFieldStrs());
                processPSVIElementRef(
                    "psv:referencedKey",
                    constraint.getRefKey());
                processPSVIAnnotations(constraint.getAnnotations());
                sendUnIndentedElement("psv:identityConstraintDefinition");
            }
            sendUnIndentedElement("psv:identityConstraintDefinitions");
        }
    }

    private void processPSVIFields(StringList fields) {
        if (fields == null || fields.getLength() == 0) {
            sendElementEvent("psv:fields");
        }
        else {
            sendIndentedElement("psv:fields");
            for (int i = 0; i < fields.getLength(); i++) {
                processPSVIXPath(fields.item(i));
            }
            sendUnIndentedElement("psv:fields");
        }
    }

    private void processPSVIXPath(String path) {
        sendIndentedElement("psv:xpath");
        sendElementEvent("psv:xpath", path);
        sendUnIndentedElement("psv:xpath");
    }

    private void processPSVIParticles(XSObjectList particles) {
        if (particles == null || particles.getLength() == 0) {
            sendElementEvent("psv:particles");
        }
        else {
            sendIndentedElement("psv:particles");
            for (int i = 0; i < particles.getLength(); i++) {
                processPSVIParticle((XSParticle)particles.item(i));
            }
            sendUnIndentedElement("psv:particles");
        }
    }

    private void processPSVIParticle(XSParticle part) {
        if (part == null) {
            sendElementEvent("psv:particle");
        }
        else {
            sendIndentedElement("psv:particle");
            sendElementEvent(
                "psv:minOccurs",
                String.valueOf(part.getMinOccurs()));
            sendElementEvent(
                "psv:maxOccurs",
                part.getMaxOccurs() == SchemaSymbols.OCCURRENCE_UNBOUNDED
                    ? "unbounded"
                    : String.valueOf(part.getMaxOccurs()));
            sendIndentedElement("psv:term");
            switch (part.getTerm().getType()) {
                case XSConstants.ELEMENT_DECLARATION :
                    processPSVIElementDeclarationOrRef(
                        (XSElementDeclaration)part.getTerm());
                    break;
                case XSConstants.MODEL_GROUP :
                    processPSVIModelGroup((XSModelGroup)part.getTerm());
                    break;
                case XSConstants.WILDCARD :
                    processPSVIWildcard((XSWildcard)part.getTerm());
                    break;
            }
            sendUnIndentedElement("psv:term");
            sendUnIndentedElement("psv:particle");
        }
    }

    private void processPSVIElementRef(String elementName, XSObject obj) {
        this.processPSVIElementRef(elementName, null, obj);
    }

    private void processPSVIElementRef(
        String elementName,
        Vector attributes,
        XSObject obj) {
        if (attributes == null) {
            attributes = new Vector();
        }
        String ref = this.getID(obj);
        if (ref != null) {
            attributes.add("ref");
            attributes.add(ref);
            attributes.add(XMLSymbols.fIDREFSymbol);
        }
        sendElementEvent(elementName, attributes, (XMLString) null);
    }

    private void processPSVIAttributeDeclarationOrRef(XSAttributeDeclaration att) {
        if (att == null)
            return;
        // for global attributes, and attributes that have already been printed,
        // we always want to print references
        if (att.getScope() == XSConstants.SCOPE_GLOBAL
            || fDefined.contains(this.getID(att))) {
            processPSVIAttributeDeclarationRef(att);
        }
        else {
            processPSVIAttributeDeclaration(att);
        }
    }

    private void processPSVIAttributeDeclarationRef(XSAttributeDeclaration att) {
        if (att == null)
            return;
        Vector attributes = new Vector();
        attributes.add("name");
        attributes.add(att.getName());
        attributes.add(XMLSymbols.fCDATASymbol);
        if (att.getNamespace() != null) {
            attributes.add("tns");
            attributes.add(att.getNamespace());
            attributes.add(XMLSymbols.fCDATASymbol);
        }
        processPSVIElementRef("psv:attributeDeclaration", attributes, att);
    }

    // always prints a reference
    private void processPSVITypeDefinitionRef(
        String enclose,
        XSTypeDefinition type) {
        if (type == null) {
        	sendElementEvent(enclose);
            return;
        }

        sendIndentedElement(enclose);
        if (type.getTypeCategory() == XSTypeDefinition.COMPLEX_TYPE) {
            processPSVIElementRef("psv:complexTypeDefinition", type);
        }
        else if (type.getTypeCategory() == XSTypeDefinition.SIMPLE_TYPE) {
            processPSVIElementRef("psv:simpleTypeDefinition", type);
        }
        else {
            throw new IllegalArgumentException(
                "Unknown type definition value: " + type.getTypeCategory());
        }
        sendUnIndentedElement(enclose);
    }

    // prints a reference if the type is anonymous and hasn't already been defined,
    // otherwise prints a definition
    private void processPSVITypeDefinitionOrRef(
        String enclose,
        XSTypeDefinition type) {
        if (type == null){
        	sendElementEvent(enclose);
            return;
        }

        // we'll check for anonymous types here, since they only occur in places where
        // a reference would be appropriate
        if (type.getAnonymous() && !fDefined.contains(this.getID(type))) {
            sendIndentedElement(enclose);
            processPSVITypeDefinition(type);
            sendUnIndentedElement(enclose);
        }
        else {
            processPSVITypeDefinitionRef(enclose, type);
        }
    }

    private void processPSVIElementDeclarationRef(XSElementDeclaration elem) {
        if (elem == null)
            return;
        processPSVIElementRef("psv:elementDeclaration", elem);
    }

    private void processPSVIElementDeclarationOrRef(XSElementDeclaration elem) {
        if (elem == null)
            return;
        // for global attributes, and attributes that have already been printed,
        // we always want to print references
        if (elem.getScope() == XSConstants.SCOPE_GLOBAL
            || fDefined.contains(this.getID(elem))) {
            processPSVIElementDeclarationRef(elem);
        }
        else {
            processPSVIElementDeclaration(elem);
        }
    }

    private void processPSVIScope(
        String enclose,
        XSComplexTypeDefinition enclosingCTD,
        short scope) {
        if (scope == XSConstants.SCOPE_ABSENT || scope == XSConstants.SCOPE_GLOBAL) {
            sendElementEvent(enclose, this.translateScope(scope));
        } else {  // XSConstants.SCOPE_LOCAL
            processPSVITypeDefinitionRef(enclose, enclosingCTD);
        }
    }

    private void processPSVIValueConstraint(
        short constraintType,
        String constraintValue) {
        if (constraintType == XSConstants.VC_NONE) {
            sendElementEvent("psv:valueConstraint");
        } else {
            sendIndentedElement("psv:valueConstraint");
            sendElementEvent("psv:variety", translateValueConstraintType(constraintType));
            sendElementEvent("psv:value", constraintValue);
            sendUnIndentedElement("psv:valueConstraint");
        }
    }

    private void processPSVISubstitutionGroupAffiliation(XSElementDeclaration elem) {
        if (elem.getSubstitutionGroupAffiliation() == null) {
            sendElementEvent("psv:substitutionGroupAffiliation");
        } else {
            sendIndentedElement("psv:substitutionGroupAffiliation");
            processPSVIElementRef("psv:elementDeclaration", elem.getSubstitutionGroupAffiliation());
            sendUnIndentedElement("psv:substitutionGroupAffiliation");
        }
    }

    /**
     * This method writes an empty element at the current indent level.
     *
     * @param tagname The name of the Element.
     *
     * @throws IOEXception
     */
    private void sendEmptyElementEvent(String tagname) {
        this.sendEmptyElementEvent(tagname, null);
    } //sendEmptyElementEvent

    private void sendEmptyElementEvent(String tagname, Vector attributes) {
        this.sendIndent();
        fDocumentHandler.emptyElement(
            createQName(tagname),
            createAttributes(attributes),
            null);
        this.sendNewLine();
    } //sendEmptyElementEvent

    /**
     * This method writes an empty element at the current indent level.
     *
     * @param tagname The name of the Element.
     *
     * @throws IOEXception
     */
    private void sendStartElementEvent(String tagname, Vector attributes) {
        fDocumentHandler.startElement(
            createQName(tagname),
            createAttributes(attributes),
            null);
    } //sendStartElementEvent

    /**
     * This method writes a closing tag at the current indent level.
     *
     * @param tagname The name of the Element.
     *
     * @throws IOEXception
     */
    private void sendEndElementEvent(String tagname) {
        fDocumentHandler.endElement(this.createQName(tagname), null);
    } //sendEndElementEvent

    /**
     * This method write the element at the current indent level and increase
     * the one level of indentation.
     *
     * @param The name of the Element.
     *
     * @throws IOException
     */
    private void sendIndentedElement(String tagName) {
        this.sendIndentedElement(tagName, null);
    } //sendIndentedElement

    private void sendIndentedElement(String tagName, Vector attributes) {
        this.sendIndent();
        this.sendStartElementEvent(tagName, attributes);
        this.sendNewLine();
        fIndent++;
    } //sendIndentedElement

    /**
     * This method write the element at the current indent level and decrease
     * one level of indentation.
     *
     * @param the name of the Element.
     *
     */
    private void sendUnIndentedElement(String tagName) {
        fIndent--;
        this.sendIndent();
        this.sendEndElementEvent(tagName);
        this.sendNewLine();
    } //sendUnIndentedElement

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
    private void sendElementEvent(String elementName) {
        this.sendElementEvent(elementName, null, (XMLString) null);
    } //sendElementEvents

    private void sendElementEvent(String elementName, String elementValue) {
        this.sendElementEvent(elementName, null, elementValue);
    } //sendElementEvents

    private void sendElementEvent(String elementName, XMLString elementValue) {
        this.sendElementEvent(elementName, null, elementValue);
    } //sendElementEvents

    private void sendElementEvent(
        String elementName,
        Vector attributes,
        String elementValue) {
        XMLString text =
            elementValue == null
                ? null
                : new XMLString(
                    elementValue.toCharArray(),
                    0,
                    elementValue.length());
        this.sendElementEvent(elementName, attributes, text);
    }

    private void sendElementEvent(
        String elementName,
        Vector attributes,
        XMLString elementValue) {
        if (elementValue == null || elementValue.equals("")) {
            if (attributes == null) {
                attributes = new Vector();
            }
            attributes.add("xsi:nil");
            attributes.add("true");
            attributes.add(XMLSymbols.fCDATASymbol);
            this.sendEmptyElementEvent(elementName, attributes);
        }
        else {
            this.sendIndent();
            this.sendStartElementEvent(elementName, attributes);
            fDocumentHandler.characters(elementValue, null);
            this.sendEndElementEvent(elementName);
            this.sendNewLine();
        }
    } //sendElementEvents

    private void sendIndentedElementWithID(String elementName, XSObject obj) {
        String id = this.getID(obj);
        // since this method is called everytime we define something with an ID,
        // may as well mark the ID as defined here
        fDefined.add(id);
        Vector attributes = new Vector();
        attributes.add("id");
        attributes.add(id);
        attributes.add(XMLSymbols.fIDSymbol);
        sendIndentedElement(elementName, attributes);
    }

    private void sendIndent() {
        if (fIndent > fIndentChars.length) {
            fIndentChars = new char[fIndentChars.length * 2];
            for (int i = 0; i < fIndentChars.length; i++) {
                fIndentChars[i] = '\t';
            }
        }
        XMLString text = new XMLString(fIndentChars, 0, fIndent);
        fDocumentHandler.characters(text, null);
    }

    private void sendNewLine() {
        fDocumentHandler.characters(newLine, null);
    }

    private QName createQName(String rawname) {
        int index = rawname.indexOf(':');
        String prefix, localpart;
        if (index == -1) {
            prefix = "";
            localpart = rawname;
        }
        else {
            prefix = rawname.substring(0, index);
            localpart = rawname.substring(index + 1);
        }
        String uri = fPSVINamespaceContext.getURI(prefix);
        return new QName(prefix, localpart, rawname, uri);
    }

    private XMLAttributes createAttributes(Vector atts) {
        XMLAttributes attributes = new XMLAttributesImpl();
        if (atts != null) {
            for (int i = 0; i < atts.size(); i += 3) {
                String rawname = (String)atts.elementAt(i);
                String value = (String)atts.elementAt(i + 1);
                String type = (String)atts.elementAt(i + 2);
                attributes.addAttribute(createQName(rawname), type, value);
            }
        }
        return attributes;
    }

    private String createID(XSObject obj) {
        String namespace = obj.getNamespace();
        String prefix = fNamespaceContext.getPrefix(obj.getNamespace());
        String name = obj.getName();
        String type = this.translateType(obj.getType());

        // must be anonymous
        if (name == null) {
            name = "anon_" + fAnonNum++;
        }
        // no namespace
        else if (namespace == null || namespace == XMLSymbols.EMPTY_STRING) {
            name = name + "." + fAnonNum++;
        }

        if (namespace == Constants.NS_XMLSCHEMA) {
            return name;
        }
        else {
            return (prefix == null ? "" : prefix + ".") + type + "." + name;
        }
    }

    private String getID(XSObject obj) {
        if (obj == null)
            return null;
        String id = (String)fIDMap.get(obj);
        if (id == null) {
            id = createID(obj);
            fIDMap.put(obj, id);
        }
        return id;
    }

    private String translateType(short type) {
        switch (type) {
            case XSConstants.TYPE_DEFINITION :
                return "type";
            case XSConstants.ANNOTATION :
                return "annot";
            case XSConstants.ATTRIBUTE_DECLARATION :
                return "attr";
            case XSConstants.ATTRIBUTE_GROUP :
                return "ag";
            case XSConstants.ATTRIBUTE_USE :
                return "au";
            case XSConstants.ELEMENT_DECLARATION :
                return "elt";
            case XSConstants.MODEL_GROUP_DEFINITION :
                return "mg";
            case XSConstants.NOTATION_DECLARATION :
                return "not";
            case XSConstants.IDENTITY_CONSTRAINT :
                return "idc";
            default :
                return "unknown";
        }
    }

    private String translateFacetKind(short kind) {
        switch (kind) {
            case XSSimpleTypeDefinition.FACET_WHITESPACE :
                return SchemaSymbols.ELT_WHITESPACE;
            case XSSimpleTypeDefinition.FACET_LENGTH :
                return SchemaSymbols.ELT_LENGTH;
            case XSSimpleTypeDefinition.FACET_MINLENGTH :
                return SchemaSymbols.ELT_MINLENGTH;
            case XSSimpleTypeDefinition.FACET_MAXLENGTH :
                return SchemaSymbols.ELT_MAXLENGTH;
            case XSSimpleTypeDefinition.FACET_TOTALDIGITS :
                return SchemaSymbols.ELT_TOTALDIGITS;
            case XSSimpleTypeDefinition.FACET_FRACTIONDIGITS :
                return SchemaSymbols.ELT_FRACTIONDIGITS;
            case XSSimpleTypeDefinition.FACET_PATTERN :
                return SchemaSymbols.ELT_PATTERN;
            case XSSimpleTypeDefinition.FACET_ENUMERATION :
                return SchemaSymbols.ELT_ENUMERATION;
            case XSSimpleTypeDefinition.FACET_MAXINCLUSIVE :
                return SchemaSymbols.ELT_MAXINCLUSIVE;
            case XSSimpleTypeDefinition.FACET_MAXEXCLUSIVE :
                return SchemaSymbols.ELT_MAXEXCLUSIVE;
            case XSSimpleTypeDefinition.FACET_MINEXCLUSIVE :
                return SchemaSymbols.ELT_MINEXCLUSIVE;
            case XSSimpleTypeDefinition.FACET_MININCLUSIVE :
                return SchemaSymbols.ELT_MININCLUSIVE;
            default :
                return "unknown";
        }
    }

    private String translateVariety(short var) {
        switch (var) {
            case XSSimpleTypeDefinition.VARIETY_LIST :
                return "list";
            case XSSimpleTypeDefinition.VARIETY_UNION :
                return "union";
            case XSSimpleTypeDefinition.VARIETY_ATOMIC :
                return "atomic";
            case XSSimpleTypeDefinition.VARIETY_ABSENT :
                return null;
            default :
                return "unknown";
        }
    }

    private String translateConstraintType(short type) {
        switch (type) {
            case XSWildcard.NSCONSTRAINT_ANY :
                return "any";
                // the spec says that when it's a list, the "type" shouldn't be there
            case XSWildcard.NSCONSTRAINT_LIST :
                return null;
            case XSWildcard.NSCONSTRAINT_NOT :
                return "not";
            default :
                return "unknown";
        }
    }

    private String translateValueConstraintType(short type) {
        switch (type) {
            case XSConstants.VC_DEFAULT :
                return "default";
            case XSConstants.VC_FIXED :
                return "fixed";
            default :
                return "unknown";
        }
    }

    private String translateBlockOrFinal(short val) {
        String ret = "";
        if ((val & XSConstants.DERIVATION_EXTENSION) != 0) {
            ret += SchemaSymbols.ATTVAL_EXTENSION;
        }
        if ((val & XSConstants.DERIVATION_LIST) != 0) {
            if (ret.length() != 0)
                ret += " ";
            ret += SchemaSymbols.ATTVAL_LIST;
        }
        if ((val & XSConstants.DERIVATION_RESTRICTION) != 0) {
            if (ret.length() != 0)
                ret += " ";
            ret += SchemaSymbols.ATTVAL_RESTRICTION;
        }
        if ((val & XSConstants.DERIVATION_UNION) != 0) {
            if (ret.length() != 0)
                ret += " ";
            ret += SchemaSymbols.ATTVAL_UNION;
        }
        if ((val & XSConstants.DERIVATION_SUBSTITUTION) != 0) {
            if (ret.length() != 0)
                ret += " ";
            ret += SchemaSymbols.ATTVAL_SUBSTITUTION;
        }
        return ret;
    }

    private String translateScope(short scope) {
        switch (scope) {
            case XSConstants.SCOPE_ABSENT :
                return null;
            case XSConstants.SCOPE_GLOBAL :
                return "global";
            case XSConstants.SCOPE_LOCAL :
                return "local";
            default :
                return "unknown";
        }
    }

    private String translateCompositor(short comp) {
        switch (comp) {
            case XSModelGroup.COMPOSITOR_SEQUENCE :
                return SchemaSymbols.ELT_SEQUENCE;
            case XSModelGroup.COMPOSITOR_CHOICE :
                return SchemaSymbols.ELT_CHOICE;
            case XSModelGroup.COMPOSITOR_ALL :
                return SchemaSymbols.ELT_ALL;
            default :
                return "unknown";
        }
    }

    private String translateContentType(short contentType) {
        switch (contentType) {
            case XSComplexTypeDefinition.CONTENTTYPE_ELEMENT :
                return "elementOnly";
            case XSComplexTypeDefinition.CONTENTTYPE_EMPTY :
                return "empty";
            case XSComplexTypeDefinition.CONTENTTYPE_MIXED :
                return "mixed";
            case XSComplexTypeDefinition.CONTENTTYPE_SIMPLE :
                return "simple";
            default :
                return "unknown";
        }
    }

    private String translateProcessContents(short process) {
        switch (process) {
            case XSWildcard.PC_LAX :
                return SchemaSymbols.ATTVAL_LAX;
            case XSWildcard.PC_SKIP :
                return SchemaSymbols.ATTVAL_SKIP;
            case XSWildcard.PC_STRICT :
                return SchemaSymbols.ATTVAL_STRICT;
            default :
                return "unknown";
        }
    }

    private String translateDerivation(short deriv) {
        switch (deriv) {
            case XSConstants.DERIVATION_EXTENSION :
                return SchemaSymbols.ELT_EXTENSION;
            case XSConstants.DERIVATION_LIST :
                return SchemaSymbols.ELT_LIST;
            case XSConstants.DERIVATION_RESTRICTION :
                return SchemaSymbols.ELT_RESTRICTION;
            case XSConstants.DERIVATION_SUBSTITUTION :
                return SchemaSymbols.ATTVAL_SUBSTITUTION;
            case XSConstants.DERIVATION_UNION :
                return SchemaSymbols.ELT_UNION;
            case XSConstants.DERIVATION_NONE :
                return null;
            default :
                return "unknown";
        }
    }

    private String translateCategory(short cat) {
        switch (cat) {
            case XSIDCDefinition.IC_KEY :
                return SchemaSymbols.ELT_KEY;
            case XSIDCDefinition.IC_KEYREF :
                return SchemaSymbols.ELT_KEYREF;
            case XSIDCDefinition.IC_UNIQUE :
                return SchemaSymbols.ELT_UNIQUE;
            default :
                return "unknown";
        }
    }

    private String translateOrdered(short ordered) {
        switch (ordered) {
            case XSSimpleTypeDefinition.ORDERED_FALSE :
                return "false";
            case XSSimpleTypeDefinition.ORDERED_PARTIAL :
                return "partial";
            case XSSimpleTypeDefinition.ORDERED_TOTAL :
                return "total";
            default :
                return "unknown";
        }
    }

    private String translateValidationAttempted(short val) {
        switch (val) {
            case ItemPSVI.VALIDATION_NONE :
                return "none";
            case ItemPSVI.VALIDATION_PARTIAL :
                return "partial";
            case ItemPSVI.VALIDATION_FULL :
                return "full";
            default :
                return "unknown";
        }
    }

    private String translateValidity(short val) {
        switch (val) {
            case ItemPSVI.VALIDITY_NOTKNOWN :
                return "notKnown";
            case ItemPSVI.VALIDITY_VALID :
                return "valid";
            case ItemPSVI.VALIDITY_INVALID :
                return "invalid";
            default :
                return "unknown";
        }
    }

    /**
     *  Check whether the calling event is  first in children list ,
     * if yes print the <children>.
     */
    private void checkForChildren() {
        if (!_elementState.empty()) {
            ElementState fElementState = (ElementState)_elementState.peek();
            if (fElementState.isEmpty == true) {
                sendIndentedElement("children");
                fElementState.isEmpty = false;
            }
        }
        else {
            sendIndentedElement("children");
            _elementState.push(new ElementState(false));
        }
    } //checkForChildren

    class ElementState {
        public boolean isEmpty;
        XMLAttributes fAttributes;

        public ElementState(XMLAttributes attributes) {
            fAttributes = attributes;
            isEmpty = true;
        }
        public ElementState(boolean value) {
            isEmpty = value;
        }
        public XMLAttributes getAttributes() {
            return fAttributes;
        }
        public void isEmpty(boolean value) {
            isEmpty = value;
        }
    } //class ElementState
} // class PSVIWriter