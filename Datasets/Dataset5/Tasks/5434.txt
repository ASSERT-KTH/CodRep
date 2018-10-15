PrivateKey privateKey = (PrivateKey) keystore.getPrivateKey(certificateAlias, privateKeyPassword);

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
package org.eclipse.wst.xml.security.core.sign;

import java.io.File;
import java.io.FileInputStream;
import java.io.StringWriter;
import java.security.KeyStore;
import java.security.PrivateKey;
import java.security.cert.CertificateExpiredException;
import java.security.cert.CertificateNotYetValidException;
import java.security.cert.X509Certificate;
import java.util.ArrayList;

import javax.xml.namespace.NamespaceContext;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.stream.StreamResult;
import javax.xml.xpath.XPath;
import javax.xml.xpath.XPathConstants;
import javax.xml.xpath.XPathFactory;

import org.apache.xml.security.signature.ObjectContainer;
import org.apache.xml.security.signature.SignatureProperties;
import org.apache.xml.security.signature.SignatureProperty;
import org.apache.xml.security.signature.XMLSignature;
import org.apache.xml.security.transforms.Transforms;
import org.apache.xml.security.transforms.params.XPath2FilterContainer;
import org.apache.xml.security.utils.resolver.implementations.ResolverFragment;
import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.core.runtime.NullProgressMonitor;
import org.eclipse.jface.text.ITextSelection;
import org.eclipse.wst.xml.security.core.utils.Globals;
import org.eclipse.wst.xml.security.core.utils.Keystore;
import org.eclipse.wst.xml.security.core.utils.SignatureNamespaceContext;
import org.eclipse.wst.xml.security.core.utils.Utils;
import org.eclipse.wst.xml.security.core.utils.XmlSecurityConstants;
import org.w3c.dom.Document;
import org.w3c.dom.DocumentFragment;
import org.w3c.dom.Element;
import org.w3c.dom.Node;
import org.xml.sax.InputSource;


/**
 * <p>Creates the XML digital signature for the selected XML document (fragment) based
 * on the user settings in the <i>XML Digital Signature Wizard</i> or based on the stored
 * settings in the workspace preferences (<i>Quick Signature</i>).</p>
 *
 * @author Dominik Schadow
 * @version 0.5.0
 */
public class CreateSignature {
    /** The XML signature. */
    private XMLSignature sig = null;
    /** The XML file to sign. */
    private File xmlFile = null;
    /** The detached file to sign. */
    private File detachedFile = null;
    /** The base URI. */
    private String baseURI = null;
    /** The resource to sign. */
    private String resource = null;
    /** The XPath expression to sign. */
    private String expression = null;
    /** The signature type. */
    private String signatureType = null;
    /** The Java Keystore. */
    private Keystore keystore = null;
    /** The Java Keystore password. */
    private char[] keystorePassword = null;
    /** The certificate password. */
    private char[] privateKeyPassword = null;
    /** The certificate alias. */
    private String certificateAlias = null;
    /** The optional signature ID. */
    private String signatureId = null;
    /** The message digest algorithm. */
    private String messageDigestAlgorithm = null;
    /** The signature algorithm. */
    private String signatureAlgorithm = null;
    /** The canonicalization algorithm. */
    private String canonicalizationAlgorithm = null;
    /** The transformation algorithm. */
    private String transformationAlgorithm = null;
    /** The text selection in an editor. */
    private String textSelection = null;
    /** Additional signature properties for the digital signature. */
    private ArrayList<DigitalSignatureProperty> properties = null;

    /**
     * <p>Prepares the signing of the XML document (fragment) selected in an Eclipse view (like navigator or package
     * explorer) or in an opened editor based on the user settings in the <i>XML Digital Signature Wizard</i> or the
     * workspace preferences.</p>
     *
     * <p>Loads the Java Keystore and prepares the private key for the signature process.</p>
     *
     * @param signWizard SignWizard object with all settings from the wizard
     * @param selection The selected text in the editor
     * @param monitor Progress monitor indicating the signing progress
     * @throws Exception to indicate any exceptional condition
     * @return The signed XML document
     */
    public Document sign(Signature signWizard, ITextSelection selection, IProgressMonitor monitor)
        throws Exception {
        Document signedDoc = null;
        FileInputStream fis = null;

        try {
            if (monitor == null) {
                monitor = new NullProgressMonitor();
            }

            loadSettings(signWizard, selection);

            monitor.worked(1);

            // Load the KeyStore
            keystore.load();

            monitor.worked(1);

            // Get the private key for signing
            PrivateKey privateKey = (PrivateKey) keystore.getSecretKey(certificateAlias, privateKeyPassword);

            monitor.worked(1);

            Document doc = Utils.parse(xmlFile);

            ResolverFragment fragmentResolver = new ResolverFragment();

            sig = new XMLSignature(doc, baseURI, signatureAlgorithm, canonicalizationAlgorithm);
            sig.addResourceResolver(fragmentResolver);

            monitor.worked(1);

            if ("enveloping".equalsIgnoreCase(signatureType)) {
                signedDoc = envelopingSignature(privateKey, xmlFile);
            } else if ("enveloped".equalsIgnoreCase(signatureType)) {
                signedDoc = envelopedSignature(privateKey, doc);
            } else if ("detached".equalsIgnoreCase(signatureType)) {
                signedDoc = detachedSignature(privateKey, doc);
            }
        } catch (Exception ex) {
            throw ex;
        } finally {
            monitor.worked(1);

            if (fis != null) {
                fis.close();
            }
        }

        return signedDoc;
    }

    /**
     * <p>Loads the user settings from the <i>XML Digital Signature Wizard</i> out of the <code>SignatureWizard</code>
     * object into different member variables.</p>
     *
     * <p>Determines the correct and fully qualified names of the selected algorithms for direct use with the Apache XML
     * Security API.</p>
     *
     * @param signature The SignatureWizard object
     * @param selection A possibly existing text selection
     * @throws Exception to indicate any exceptional condition
     */
    private void loadSettings(Signature signature, ITextSelection selection) throws Exception {
        xmlFile = new File(signature.getFile());
        baseURI = xmlFile.toURI().toString();
        resource = signature.getResource();
        expression = null;

        if ("xpath".equalsIgnoreCase(resource)) {
            expression = signature.getXpath();
        } else if ("selection".equalsIgnoreCase(resource)) {
            textSelection = selection.getText();
        }

        signatureType = signature.getSignatureType();

        if ("detached".equalsIgnoreCase(signatureType)) {
            detachedFile = signature.getDetachedFile();
        }

        keystore = signature.getKeystore();
        keystorePassword = signature.getKeystorePassword();
        privateKeyPassword = signature.getKeyPassword();
        certificateAlias = signature.getKeyAlias();

        if (signature.getSignatureProperties() != null) {
            properties = signature.getSignatureProperties();
        }

        if (signature.getSignatureId() != null) {
            signatureId = signature.getSignatureId();
        }

        messageDigestAlgorithm = XmlSecurityConstants.getMessageDigestAlgorithm(signature.getMessageDigestAlgorithm());
        signatureAlgorithm = XmlSecurityConstants.getSignatureAlgorithm(signature.getSignatureAlgorithm());
        canonicalizationAlgorithm = XmlSecurityConstants.getCanonicalizationAlgorithm(signature
                .getCanonicalizationAlgorithm());
        transformationAlgorithm = XmlSecurityConstants.getTransformationAlgorithm(signature.getTransformationAlgorithm());
    }

    /**
     * <p>Creates a detached signature. The selected XML document is regarded as context document and will contain the
     * reference to the signed XML document (detached document). The detached document won't be changed at all, only its
     * hash value will be calculated.</p>
     *
     * @param keystore The Java Keystore with the certificate used for signing
     * @param privateKey The private key to create the digital signature
     * @param doc The context XML document which contains the signature
     * @return The signed XML document
     * @throws Exception to indicate any exceptional condition
     */
    private Document detachedSignature(PrivateKey privateKey, Document doc) throws Exception {
        Element root = doc.getDocumentElement();
        Transforms transforms = null;
        root.appendChild(sig.getElement());

        if (transformationAlgorithm != null && !"None".equals(transformationAlgorithm)) {
            transforms = new Transforms(doc);
            transforms.addTransform(transformationAlgorithm);
        }

        sig.addDocument(detachedFile.toURI().toString(), transforms, messageDigestAlgorithm);

        addProperties(doc);

        if (!"".equals(signatureId)) {
            sig.setId(signatureId);
        }

        boolean doSign = addCertificate();

        if (doSign) {
            sig.sign(privateKey);
        }

        return doc;
    }

    /**
     * <p>Creates an enveloped signature. Adds the signature element to the current root element, so the signed document
     * (fragment) surrounds the signature.</p>
     *
     * @param keystore The Java Keystore with the certificate used for signing
     * @param privateKey The private key to create the digital signature
     * @param doc The XML document to sign
     * @return The signed XML document
     * @throws Exception to indicate any exceptional condition
     */
    private Document envelopedSignature(PrivateKey privateKey, Document doc) throws Exception {
        Element root = doc.getDocumentElement();

        if ("document".equalsIgnoreCase(resource)) {
            Transforms transforms = new Transforms(doc);
            transforms.addTransform(Transforms.TRANSFORM_ENVELOPED_SIGNATURE);
            if (transformationAlgorithm != null && !"None".equals(transformationAlgorithm)) {
                transforms.addTransform(transformationAlgorithm);
            }
            sig.addDocument("", transforms, messageDigestAlgorithm);
        } else if ("selection".equalsIgnoreCase(resource)) {
            Document selectionDoc = Utils.parse(textSelection);
            String finalXpath = Utils.getUniqueXPathToNode(doc, selectionDoc);

            Transforms transforms = new Transforms(doc);
            transforms.addTransform(Transforms.TRANSFORM_ENVELOPED_SIGNATURE);
            transforms.addTransform(Transforms.TRANSFORM_XPATH2FILTER, XPath2FilterContainer.newInstanceIntersect(doc,
                    finalXpath).getElement());
            if (transformationAlgorithm != null && !"None".equals(transformationAlgorithm)) {
                transforms.addTransform(transformationAlgorithm);
            }
            sig.addDocument("", transforms, messageDigestAlgorithm);
        } else if ("xpath".equalsIgnoreCase(resource)) {
            Transforms transforms = new Transforms(doc);
            transforms.addTransform(Transforms.TRANSFORM_ENVELOPED_SIGNATURE);
            transforms.addTransform(Transforms.TRANSFORM_XPATH2FILTER, XPath2FilterContainer.newInstanceIntersect(doc,
                    expression).getElement());
            if (transformationAlgorithm != null && !"None".equals(transformationAlgorithm)) {
                transforms.addTransform(transformationAlgorithm);
            }
            sig.addDocument("", transforms, messageDigestAlgorithm);
        }

        root.appendChild(sig.getElement());

        addProperties(doc);

        if (!"".equals(signatureId)) {
            sig.setId(signatureId);
        }

        boolean doSign = addCertificate();

        if (doSign) {
            sig.sign(privateKey);
        }

        return doc;
    }

    /**
     * <p>Creates an enveloping signature. Removes the signed node(s) or text content from its original location
     * and stores it inside the <code>object</code> element in the XML digital signature. The nodes name is used
     * as id for the <code>object</code> element.</p>
     *
     * @param keystore The Java Keystore with the certificate used for signing
     * @param privateKey The private key to create the digital signature
     * @param file The XML document to sign
     * @return The signed XML document
     * @throws Exception to indicate any exceptional condition
     */
    private Document envelopingSignature(PrivateKey privateKey, File file) throws Exception {
        Document doc = Utils.parse(file);
        Element root = doc.getDocumentElement();
        ObjectContainer obj = new ObjectContainer(doc);
        String objectId = "";

        if ("document".equalsIgnoreCase(resource)) {
            TransformerFactory transformerFactory = TransformerFactory.newInstance();
            Transformer transformer = transformerFactory.newTransformer();
            StringWriter stringWriter = new StringWriter();
            transformer.transform(new DOMSource(doc), new StreamResult(stringWriter));
            objectId = root.getNodeName();
            String namespaceURI = root.getNamespaceURI();
            String prefix = root.getPrefix();
            DocumentFragment documentFragment = parseXml(doc, stringWriter.toString());

            // remove root node with all children
            doc.removeChild(doc.getDocumentElement());

            Element anElement = doc.createElementNS(prefix, objectId);

            if (namespaceURI != null && !"".equals(namespaceURI)) {
                anElement.setPrefix(prefix);
                anElement.setAttribute("xmlns:" + prefix, namespaceURI);
            }

            anElement.appendChild(documentFragment);

            obj.appendChild(anElement);
            obj.setId(objectId);

            doc.appendChild(sig.getElement());
        } else if ("selection".equalsIgnoreCase(resource)) {
            Document selectionDoc = Utils.parse(textSelection);
            String selectionXpath = Utils.getUniqueXPathToNode(doc, selectionDoc);
            XPath xpath = XPathFactory.newInstance().newXPath();
            NamespaceContext ns = new SignatureNamespaceContext();
            InputSource inputSource = new InputSource(new java.io.FileInputStream(file));
            xpath.setNamespaceContext(ns);
            Element node = (Element) xpath.evaluate(selectionXpath, inputSource, XPathConstants.NODE);
            Node parentNode = null;

            if (!doc.getDocumentElement().isSameNode(node)) {
                parentNode = node.getParentNode();
            }

            TransformerFactory tf = TransformerFactory.newInstance();
            Transformer tx = tf.newTransformer();
            StringWriter sw = new StringWriter();
            tx.transform(new DOMSource(selectionDoc), new StreamResult(sw));
            objectId = selectionDoc.getDocumentElement().getNodeName();
            String namespaceURI = root.getNamespaceURI();
            String prefix = root.getPrefix();
            DocumentFragment documentFragment = parseXml(doc, sw.toString());

            if (parentNode != null) {
                // remove the selected node
                parentNode.removeChild(node);
                // TODO remove whitespace node
            } else {
                // remove root node with all children
                doc.removeChild(doc.getDocumentElement());
            }

            Element anElement = doc.createElementNS(prefix, node.getNodeName());
            if (namespaceURI != null && !"".equals(namespaceURI)) {
                anElement.setPrefix(prefix);
                anElement.setAttribute("xmlns:" + prefix, namespaceURI);
            }

            anElement.appendChild(documentFragment);

            obj.appendChild(anElement);
            obj.setId(objectId);

            if (parentNode != null) {
                root.appendChild(sig.getElement());
            } else {
                doc.appendChild(sig.getElement());
            }
        } else if ("xpath".equalsIgnoreCase(resource)) {
            XPath xpath = XPathFactory.newInstance().newXPath();
            NamespaceContext ns = new SignatureNamespaceContext();
            InputSource inputSource = new InputSource(new java.io.FileInputStream(file));
            xpath.setNamespaceContext(ns);
            Element node = (Element) xpath.evaluate(expression, inputSource, XPathConstants.NODE);
            Node parentNode = null;

            if (!doc.getDocumentElement().isSameNode(node)) {
                parentNode = node.getParentNode();
            }

            objectId = node.getNodeName();

            DocumentFragment documentFragment = doc.createDocumentFragment();
            documentFragment.appendChild(node.cloneNode(true));

            if (parentNode != null) {
                // remove the selected node
                parentNode.removeChild(node);
                // TODO remove whitespace node
            } else {
                // remove root node with all children
                doc.removeChild(doc.getDocumentElement());
            }

            obj.appendChild(documentFragment);
            obj.setId(objectId);

            if (parentNode != null) {
                parentNode.appendChild(sig.getElement());
            } else {
                doc.appendChild(sig.getElement());
            }
        }

        sig.appendObject(obj);

        Transforms transforms = null;
        if (transformationAlgorithm != null && !"None".equals(transformationAlgorithm)) {
            transforms = new Transforms(doc);
            transforms.addTransform(transformationAlgorithm);
        }

        sig.addDocument("#" + objectId, transforms, messageDigestAlgorithm);

        addProperties(doc);

        if (!"".equals(signatureId)) {
            sig.setId(signatureId);
        }

        boolean doSign = addCertificate();

        if (doSign) {
            sig.sign(privateKey);
        }

        return doc;
    }

    /**
     * <p>Adds the entered signature properties to the signature element. The additional reference per property element
     * causes every property to be signed as well.</p>
     *
     * <p>A signature property is only used if and only if the id and target value are not empty.</p>
     *
     * <p>IDs must be unique in the selected XML document!</p>
     *
     * @param doc The XML document to add the properties to
     * @throws Exception to indicate any exceptional condition
     */
    private void addProperties(Document doc) throws Exception {
        if (properties != null && properties.size() > 0) {
            SignatureProperties props = new SignatureProperties(doc);

            for (int i = 0, size = properties.size(); i < size; i++) {
                if (!"".equals(properties.get(i).getId()) && !"".equals(properties.get(i).getTarget())) {
                    SignatureProperty prop = new SignatureProperty(doc, properties.get(i).getTarget(), properties
                            .get(i).getId());
                    prop.getElement().appendChild(doc.createTextNode("\n " + properties.get(i).getContent() + "\n"));
                    props.addSignatureProperty(prop);
                    sig.addDocument("#" + properties.get(i).getId());
                }
            }

            ObjectContainer object = new ObjectContainer(doc);
            object.appendChild(doc.createTextNode("\n"));
            object.appendChild(props.getElement());
            object.appendChild(doc.createTextNode("\n"));
            sig.appendObject(object);
        }
    }

    /**
     * <p>Adds the certificate and public key information from the keystore. All certificate information is needed for
     * successful verification with the <b>XML Security Tools</b>.</p>
     *
     * <p>Aborts the adding if the certificate expired or is not yet valid.</p>
     *
     * @param keystore The Java Keystore with the certificate used for signing
     * @return Certificate successfully added
     * @throws Exception to indicate any exceptional condition
     */
    private boolean addCertificate() throws Exception {
        boolean addedCertificate = false;
        X509Certificate cert = (X509Certificate) keystore.getCertificate(certificateAlias);

        if (cert != null) {
            try {
                cert.checkValidity();
            } catch (CertificateExpiredException cee) {
                addedCertificate = false;
            } catch (CertificateNotYetValidException cnyve) {
                addedCertificate = false;
            }

            sig.addKeyInfo(cert);
            sig.addKeyInfo(cert.getPublicKey());
            addedCertificate = true;
        }

        return addedCertificate;
    }

    /**
     * <p>Imports the nodes of the document fragment into the old one (context document) so that they will be compatible
     * with it. Creates the document fragment node to hold the new nodes and moves the nodes into the fragment.</p>
     *
     * @param doc The context XML document
     * @param fragment The fragment to import into the context document
     * @return The merged document fragment
     * @throws Exception to indicate any exceptional condition
     */
    private DocumentFragment parseXml(Document doc, String fragment) throws Exception {
        Document include = Utils.parse(fragment);
        Node node = doc.importNode(include.getDocumentElement(), true);
        DocumentFragment documentFragment = doc.createDocumentFragment();
        while (node.hasChildNodes()) {
            documentFragment.appendChild(node.removeChild(node.getFirstChild()));
        }

        return documentFragment;
    }
}