String ids = "Use first " + type + ";";

/*******************************************************************************
 * Copyright (c) 2008 Dominik Schadow - http://www.xml-sicherheit.de
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     Dominik Schadow - initial API and implementation
 *******************************************************************************/
package org.eclipse.wst.xml.security.core.utils;

import java.io.ByteArrayInputStream;
import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.io.StringReader;
import java.io.StringWriter;
import java.util.HashSet;
import java.util.Properties;
import java.util.regex.Pattern;

import javax.xml.namespace.NamespaceContext;
import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;
import javax.xml.transform.OutputKeys;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.stream.StreamResult;
import javax.xml.xpath.XPath;
import javax.xml.xpath.XPathConstants;
import javax.xml.xpath.XPathFactory;

import org.apache.xml.security.utils.EncryptionConstants;
import org.eclipse.core.resources.IFile;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Status;
import org.eclipse.wst.xml.security.core.XmlSecurityPlugin;
import org.w3c.dom.Document;
import org.w3c.dom.DocumentType;
import org.w3c.dom.Element;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import org.xml.sax.InputSource;
import org.xml.sax.SAXException;


/**
 * <p>This is the main utils class with different supporting methods used all over in the XML-Security
 * Plug-In.</p>
 *
 * @author Dominik Schadow
 * @version 0.5.0
 */
public final class Utils {
    /** Contains the XPath for every element of an XML document. */
    private static HashSet<String> xpathCollector = new HashSet<String>();
    /** Contains the XPath to the selected element content. */
    private static String xpathExpressionToContent = null;

    /**
     * Utility class, no instance required.
     */
    private Utils() {
    }

    /**
     * Parses the IFile in a W3C document.
     *
     * @param file The IFile to parse
     * @return The parsed XML document
     * @throws IOException during document preparation
     * @throws SAXException during document generation
     * @throws ParserConfigurationException during document builder factory initialization
     */
    public static Document parse(final IFile file) throws SAXException, IOException,
        ParserConfigurationException {
        DocumentBuilder db = prepareDocumentBuilder();
        return db.parse(file.getLocationURI().toString());
    }

    /**
     * Parses the File in a W3C document.
     *
     * @param file The file to parse
     * @return The parsed XML document
     * @throws IOException during document preparation
     * @throws SAXException during document generation
     * @throws ParserConfigurationException during document builder factory initialization
     */
    public static Document parse(final File file) throws SAXException, IOException,
        ParserConfigurationException {
        DocumentBuilder db = prepareDocumentBuilder();
        return db.parse(file);
    }

    /**
     * Parses the byte array in a W3C document.
     *
     * @param content The byte array to parse
     * @return The parsed XML document
     * @throws IOException during document preparation
     * @throws SAXException during document generation
     * @throws ParserConfigurationException during document builder factory initialization
     */
    public static Document parse(final byte[] content) throws SAXException, IOException,
        ParserConfigurationException {
        DocumentBuilder db = prepareDocumentBuilder();
        return db.parse(new ByteArrayInputStream(content));
    }

    /**
     * Parses the InputStream in a W3C document.
     *
     * @param content The InputStream to parse
     * @return The parsed XML document
     * @throws IOException during document preparation
     * @throws SAXException during document generation
     * @throws ParserConfigurationException during document builder factory initialization
     */
    public static Document parse(final InputStream content) throws SAXException, IOException,
        ParserConfigurationException {
        DocumentBuilder db = prepareDocumentBuilder();
        return db.parse(content);
    }

    /**
     * Parses the String in a W3C document. Adds a temporary root element
     * <code>xmlsectempelement</code> if the String only consists of character data (element
     * content) and doesn't start/end with &lt; and &gt;.
     *
     * @param content The String to parse
     * @return The parsed XML document
     * @throws IOException during document preparation
     * @throws SAXException during document generation
     * @throws ParserConfigurationException during document builder factory initialization
     */
    public static Document parse(String content) throws SAXException, IOException,
        ParserConfigurationException {
        DocumentBuilder db = prepareDocumentBuilder();
        if (!content.startsWith("<") && !content.endsWith(">")) {
            content = "<xmlsectempelement>" + content + "</xmlsectempelement>";
        }
        return db.parse(new InputSource(new StringReader(content)));
    }

    /**
     * Creates a new W3C document.
     *
     * @return The new XML document
     * @throws ParserConfigurationException during document builder factory initialization
     */
    public static Document createDocument() throws ParserConfigurationException {
        DocumentBuilder db = prepareDocumentBuilder();
        return db.newDocument();
    }

    /**
     * Prepares a <code>DocumentBuilder</code> to parse XML documents.
     *
     * @return The DocumentBuilder
     * @throws ParserConfigurationException during document builder factory initialization
     */
    private static DocumentBuilder prepareDocumentBuilder() throws ParserConfigurationException {
        DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
        dbf.setNamespaceAware(true);
        dbf.setValidating(false);
        return dbf.newDocumentBuilder();
    }

    /**
     * Collects all IDs (signature or encryption, based on the type) in the given XML document and
     * returns them in a String array.
     *
     * @param xml The XML document as an InputStream
     * @param type Indicates signature or encryption id search
     * @return All IDs in a String array
     */
    public static String[] getIds(final IFile xml, final String type) {
        String ids = "Use first " + type + " id;";

        try {
            Document doc = parse(xml);
            Element current = null;
            NodeList nodes = null;

            if (type != null && type.equals("encryption")) {
                nodes = doc.getElementsByTagNameNS(EncryptionConstants.EncryptionSpecNS,
                        EncryptionConstants._TAG_ENCRYPTEDDATA);
            } else if (type != null && type.equals("signature")) {
                XPath xpath = XPathFactory.newInstance().newXPath();
                NamespaceContext ns = new SignatureNamespaceContext();
                xpath.setNamespaceContext(ns);
                nodes = (NodeList) xpath.evaluate("//ds:Signature", new InputSource(xml.getContents()),
                        XPathConstants.NODESET);
            }

            if (nodes != null) {
                for (int i = 0, length = nodes.getLength(); i < length; i++) {
                    current = (Element) nodes.item(i);

                    if (null != current.getAttribute("Id")
                            && current.getAttribute("Id").trim().length() > 0) {
                        ids += current.getAttribute("Id") + ";";
                    }
                }
            }
        } catch (Exception ex) {
            logError(ex, Messages.errorDuringIdSearch);
        }
        return ids.split(";");
    }

    /**
     * Collects all IDs (no difference between signature or encryption id) in the given XML document
     * and stores them in a String array.
     *
     * @param xml The XML document as an InputStream
     * @return All IDs in a String array
     */
    public static String[] getAllIds(final IFile xml) {
        String ids = "";

        try {
            Document doc = parse(xml);
            Element current = null;

            NodeList encNodes = doc.getElementsByTagNameNS(EncryptionConstants.EncryptionSpecNS,
                    EncryptionConstants._TAG_ENCRYPTEDDATA);

            XPath xpath = XPathFactory.newInstance().newXPath();
            NamespaceContext ns = new SignatureNamespaceContext();
            xpath.setNamespaceContext(ns);
            NodeList sigNodes = (NodeList) xpath.evaluate("//ds:Signature", new InputSource(xml.getContents()),
                    XPathConstants.NODESET);

            for (int i = 0, length = encNodes.getLength(); i < length; i++) {
                current = (Element) encNodes.item(i);

                if (null != current.getAttribute("Id")
                        && current.getAttribute("Id").trim().length() > 0) {
                    ids += current.getAttribute("Id") + ";";
                }
            }

            for (int i = 0, length = sigNodes.getLength(); i < length; i++) {
                current = (Element) sigNodes.item(i);

                if (null != current.getAttribute("Id")
                        && current.getAttribute("Id").trim().length() > 0) {
                    ids += current.getAttribute("Id") + ";";
                }
            }
        } catch (Exception ex) {
            ex.printStackTrace();
            logError(ex, Messages.errorDuringIdSearch);
        }

        return ids.split(";");
    }

    /**
     * Returns the XPath for every element of the XML document as an <code>Object</code> array. Gets
     * the root element first, then calls the method <code>childNodes</code> to determine all
     * children of the element.
     *
     * @param doc The XML document
     * @return Object array with the XPath expressions for every node
     */
    public static Object[] getCompleteXpath(final Document doc) {
        Node root = doc.getDocumentElement();
        xpathCollector.add(getXPathExpression(root));

        childNodes(root);

        return xpathCollector.toArray();
    }

    /**
     * Determines all child nodes and stores the XPath expression for every node in the HashSet.
     * Only element nodes are added to the HashSet.
     *
     * @param node The node to determine the XPath expression for and possible child nodes
     */
    private static void childNodes(final Node node) {
        NodeList childList = node.getChildNodes();
        Node childNode = null;

        for (int i = 0, length = childList.getLength(); i < length; i++) {
            childNode = childList.item(i);

            if (childNode.getNodeType() == Node.ELEMENT_NODE) {
                xpathCollector.add(getXPathExpression(childNode));
            }

            childNodes(childNode);
        }
    }

    /**
     * Returns the unique XPath expression for the given node.
     *
     * @param node The node to determine the XPath for
     * @return The XPath expression as string
     */
    private static String getXPathExpression(final Node node) {
        String xpathExpression = node.getNodeName();

        if (node.getParentNode() != null) {
            int index = 0;
            Node prec = node;

            while (prec != null) {
                if (prec.getNodeName().equals(node.getNodeName())) {
                    index++;
                }
                prec = prec.getPreviousSibling();
            }

            if (node.getParentNode() instanceof Document) {
                ; // do nothing
            } else {
                xpathExpression = getXPathExpression(node.getParentNode()) + "/" + xpathExpression
                        + "[" + String.valueOf(index) + "]";
            }
        }

        return xpathExpression;
    }

    /**
     * Determines the unique XPath expression for the selected element or element content in the
     * editor. Selected element content (character data) is indicated by the temporarily added root
     * element <code>xmlsectempelement</code>.
     *
     * @param doc The complete XML document
     * @param selection The selected element or element content as XML document
     * @return The unique XPath expression for the selection
     */
    public static String getUniqueXPathToNode(final Document doc, final Document selection) {
        String xpathExpression = "/";
        if (!selection.getDocumentElement().getLocalName().equals("xmlsectempelement")) {
            // a node is selected
            String selectionRootElement = selection.getDocumentElement().getLocalName();
            xpathExpression = "//" + selectionRootElement;
            NodeList matchingNodes = doc.getElementsByTagName(selectionRootElement);

            if (matchingNodes.getLength() == 1) {
                xpathExpression = getXPathExpression(matchingNodes.item(0));
            } else {
                for (int i = 0; i < matchingNodes.getLength(); i++) {
                    boolean foundNode = true;
                    NodeList selectionChildNodes = selection.getChildNodes();
                    for (int j = 0; j < selectionChildNodes.getLength(); j++) {
                        Node selectionNode = selectionChildNodes.item(j);
                        Node matchingNode = matchingNodes.item(i);
                        if (!matchingNode.toString().equals(selectionNode.toString())) {
                            foundNode = false;
                            break;
                        }
                        if (!matchingNode.getTextContent().trim().equals(
                                selectionNode.getTextContent().trim())) {
                            foundNode = false;
                            break;
                        }
                    }
                    if (foundNode) {
                        xpathExpression = getXPathExpression(matchingNodes.item(i));
                        break;
                    }
                }
            }
        } else { // only element content is selected
            xpathExpressionToContent = null;
            xpathExpression = getXPathToContent(doc.getDocumentElement(), selection
                    .getDocumentElement().getTextContent());
        }

        return xpathExpression;
    }

    /**
     * Determines the XPath expression to the selected character data (element content). The first
     * matching content is used, so this XPath may point to another element content.
     *
     * @param root The root element of the XML document
     * @param selectedContent The selected character data
     * @return The XPath expression to the selected character data
     */
    private static String getXPathToContent(final Node root, final String selectedContent) {
        NodeList childList = root.getChildNodes();
        Node childNode = null;

        for (int i = 0, length = childList.getLength(); i < length
                && xpathExpressionToContent == null; i++) {
            childNode = childList.item(i);
            if (childNode.getNodeType() == Node.TEXT_NODE) {
                if (childNode.getTextContent().equals(selectedContent)) {
                    xpathExpressionToContent = getXPathExpression(childNode.getParentNode());
                }
            }
            getXPathToContent(childNode, selectedContent);
        }

        return xpathExpressionToContent + "/text()";
    }

    /**
     * Validates the XPath expression entered by the user in a wizard. The user can only continue
     * with the entered XPath if <i>single</i> is returned.
     *
     * @param doc The XML document
     * @param xpathExpression The XPath expression
     * @return <i>single</i>, <i>multiple</i>, <i>none</i> or <i>attribute</i> depending on the
     *         entered XPath expression
     */
    public static String validateXPath(final Document doc, final String xpathExpression) {
        try {
            XPath xpath = XPathFactory.newInstance().newXPath();
            NodeList nodes = (NodeList) xpath
                    .evaluate(xpathExpression, doc, XPathConstants.NODESET);

            if (nodes.getLength() == 1) {
                if (nodes.item(0).getNodeType() == Node.ATTRIBUTE_NODE) {
                    return "attribute";
                } else if (nodes.item(0).getNodeType() == Node.ELEMENT_NODE) {
                    return "single";
                }
            } else if (nodes.getLength() > 1) {
                return "multiple";
            }

            return "none";
        } catch (Exception ex) {
            return "none";
        }
    }

    /**
     * Returns the XML document parsed as a String. The output String can be pretty printed or not
     * (never pretty print a signed XML document, this will break the signature).
     *
     * @param doc The XML document to convert
     * @param prettyPrint Pretty print the output String
     * @return The Document as a String
     * @exception Exception to indicate any exceptional condition
     */
    public static String docToString(final Document doc, final boolean prettyPrint) throws Exception {
        StringWriter writer = new StringWriter();
        boolean indentFallback = false;

        TransformerFactory factory = TransformerFactory.newInstance();
        if (prettyPrint) {
            try {
                factory.setAttribute("indent-number", "4");
            } catch (IllegalArgumentException e) {
                indentFallback = true;
            }
        }

        Transformer transformer = factory.newTransformer();
        Properties props = new Properties();
        props.setProperty(OutputKeys.METHOD, "xml");
        props.setProperty(OutputKeys.STANDALONE, "yes");
        props.setProperty(OutputKeys.OMIT_XML_DECLARATION, "no");
        if (prettyPrint) {
            props.setProperty(OutputKeys.INDENT, "yes");

            if (indentFallback) {
                props.setProperty("{http://xml.apache.org/xslt}indent-amount", String.valueOf(4));
            }
        }

        DocumentType type = doc.getDoctype();
        if (type != null) {
            String publicId = type.getPublicId();
            if (publicId != null) {
                props.setProperty(OutputKeys.DOCTYPE_PUBLIC, publicId);
            }
            String systemId = type.getSystemId();
            if (systemId != null) {
                props.setProperty(OutputKeys.DOCTYPE_SYSTEM, systemId);
            }
        }

        transformer.setOutputProperties(props);
        transformer.transform(new DOMSource(doc), new StreamResult(writer));

        return writer.toString();
    }

    /**
     * Validates the ID (signature ID or encryption ID) entered by the user. An ID containing &lt;,
     * &gt;, &qout;, &apos; or &amp; or whitespace is invalid.
     *
     * @param id The entered ID
     * @return Validity of the ID
     */
    public static boolean validateId(final String id) {
        return Pattern.matches("[^<>&\"\'\\s]+", id);
    }

    /**
     * Checks whether the valid ID is unique in the current XML document.
     *
     * @param newId The entered ID
     * @param ids All existing IDs in the XML document
     * @return Uniqueness of the ID
     */
    public static boolean ensureIdIsUnique(final String newId, final String[] ids) {
        boolean uniqueId = true;

        for (String currentId : ids) {
            if (currentId.equals(newId)) {
                uniqueId = false;
            }
        }
        return uniqueId;
    }

    /**
     * Logs the given error message to the workspace default log file.
     *
     * @param ex The error message to log
     * @param message The error message
     */
    public static void logError(final Exception ex, final String message) {
        XmlSecurityPlugin plugin = XmlSecurityPlugin.getDefault();
        IStatus status = new Status(IStatus.ERROR, plugin.getBundle().getSymbolicName(), 0,
                message, ex);
        plugin.getLog().log(status);
    }


}