Key secretKey = keyStore.getPrivateKey(encryption.getKeyName(), encryption.getKeyPassword());

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
package org.eclipse.wst.xml.security.core.encrypt;

import java.io.File;
import java.io.FileOutputStream;
import java.security.Key;

import javax.xml.namespace.NamespaceContext;
import javax.xml.xpath.XPath;
import javax.xml.xpath.XPathConstants;
import javax.xml.xpath.XPathFactory;

import org.apache.xml.security.encryption.CipherData;
import org.apache.xml.security.encryption.EncryptedData;
import org.apache.xml.security.encryption.EncryptedKey;
import org.apache.xml.security.encryption.EncryptionMethod;
import org.apache.xml.security.encryption.XMLCipher;
import org.apache.xml.security.keys.KeyInfo;
import org.apache.xml.security.utils.EncryptionConstants;
import org.apache.xml.security.utils.XMLUtils;
import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.core.runtime.NullProgressMonitor;
import org.eclipse.wst.xml.security.core.utils.Keystore;
import org.eclipse.wst.xml.security.core.utils.SignatureNamespaceContext;
import org.eclipse.wst.xml.security.core.utils.Utils;
import org.eclipse.wst.xml.security.core.utils.XmlSecurityConstants;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.NodeList;
import org.xml.sax.InputSource;

/**
 * <p>Encrypts the XML document (fragment) based on the user settings in the
 * <i>XML Encryption Wizard</i> or stored in the preferences (Quick Encryption).</p>
 *
 * @author Dominik Schadow
 * @version 0.5.0
 */
public class CreateEncryption {
    /** The XML file to encrypt. */
    private File xmlFile = null;
    /** The detached XML file to encrypt. */
    private File detachedFile = null;
    /** The detached XML document to encrypt. */
    private Document detachedDoc = null;
    /** True encrypts only the element content, false encrypts everything (default). */
    private boolean content;
    /** The encryption type. */
    private String encryptionType = null;
    /** The Java KeyStore. */
    private Keystore keyStore = null;
    /** Document (fragment) to encrypt. */
    private String encrypt = null;
    /** XPath to encrypt (can be null). */
    private String expression = null;
    /** Optional encryption id. */
    private String encryptionId = null;
    /** The encryption algorithm used in the EncryptionMethod element. */
    private String encryptionAlgorithm = null;
    /** The key cipher algorithm. */
    private String keyCipherAlgorithm = null;
    /** The name of the key. */
    private String keyName = "";

    /**
     * Encrypts the document selected in an Eclipse view (like navigator or package explorer) or in an opened editor
     * based on the chosen settings in the <i>XML Encryption Wizard</i> or stored in the preferences.
     *
     * @param encryption Encryption object with all the settings from the wizard
     * @param selection The selected text in the editor
     * @param monitor Progress monitor indicating the encryption progress
     * @return Document The XML document containing the encryption
     * @throws Exception to indicate any exceptional condition
     */
    public Document encrypt(Encryption encryption, String selection, IProgressMonitor monitor) throws Exception {
        Document doc = null;

        if (monitor == null) {
            monitor = new NullProgressMonitor();
        }

        monitor.worked(1);

        loadSettings(encryption, selection);
        keyStore.load();

        Key secretKey = keyStore.getSecretKey(encryption.getKeyName(), encryption.getKeyPassword());

        monitor.worked(1);

        if (encryptionType.equalsIgnoreCase("enveloping")) {
            doc = envelopingEncryption(xmlFile, selection, secretKey);
        } else if (encryptionType.equalsIgnoreCase("detached")) {
            doc = detachedEncryption(xmlFile, secretKey);
        }

        monitor.worked(1);

        return doc;
    }

    /**
     * Loads the settings from the <i>XML Encryption Wizard</i> out of the <code>EncryptionWizard</code> object into
     * different member variables.
     *
     * @param encryption Contains all user settings
     * @param selection A possibly existing text selection
     * @throws Exception to indicate any exceptional condition
     */
    private void loadSettings(Encryption encryption, String selection) throws Exception {
        xmlFile = new File(encryption.getFile());
        encryptionType = encryption.getEncryptionType();
        content = encryption.getContent();
        keyStore = encryption.getKeyStore();
        keyName = encryption.getKeyName();
        encrypt = encryption.getResource();
        expression = encryption.getXpath();
        detachedFile = encryption.getFileDetached();

        if (detachedFile != null) {
            detachedDoc = Utils.parse(detachedFile);
        }

        if (null != encryption.getEncryptionId()) {
            encryptionId = encryption.getEncryptionId();
        }

        // get the constant names for all algorithms
        encryptionAlgorithm = XmlSecurityConstants.getEncryptionAlgorithm(encryption.getEncryptionAlgorithm());
        keyCipherAlgorithm = XmlSecurityConstants.getKeyCipherAlgorithm(encryption.getKeyCipherAlgorithm());
    }

    /**
     * <p>Generates an enveloping encryption. Distinguishes between encrypting the whole
     * document, selected element(s) or element content and an XPath expression to an element
     * to encrypt.</p>
     *
     * <p>A <code>CipherValue</code> element is created inside the current XML document to
     * contain the encrypted data.</p>
     *
     * @param file The XML document to encrypt
     * @param selection The text selection
     * @param secretKey The data encryption key
     * @return The encrypted XML document
     * @throws Exception to indicate any exceptional condition
     */
    private Document envelopingEncryption(File file, String selection, Key secretKey)
        throws Exception {
        Document doc = Utils.parse(xmlFile);
        Element root = doc.getDocumentElement();

        XMLCipher keyCipher = XMLCipher.getInstance(keyCipherAlgorithm);
        keyCipher.init(XMLCipher.WRAP_MODE, secretKey);

        XMLCipher xmlCipher = XMLCipher.getInstance(encryptionAlgorithm);
        xmlCipher.init(XMLCipher.ENCRYPT_MODE, secretKey);

        EncryptedKey encryptedKey = keyCipher.encryptKey(doc, secretKey);
        EncryptedData encryptedData = xmlCipher.getEncryptedData();

        KeyInfo keyInfo = new KeyInfo(doc);
        keyInfo.addKeyName(keyName);
        keyInfo.add(encryptedKey);

        encryptedData.setKeyInfo(keyInfo);

        if (!"".equals(encryptionId)) {
            encryptedData.setId(encryptionId);
        }

        if ("document".equalsIgnoreCase(encrypt)) {
            xmlCipher.doFinal(doc, root, content);
        } else if ("selection".equalsIgnoreCase(encrypt)) {
            Document selectionDoc = Utils.parse(selection);
            String tempXPath = Utils.getUniqueXPathToNode(doc, selectionDoc);
            XPath xpath = XPathFactory.newInstance().newXPath();
            NamespaceContext ns = new SignatureNamespaceContext();
            InputSource inputSource = new InputSource(new java.io.FileInputStream(file));
            xpath.setNamespaceContext(ns);
            Element selectedElement = (Element) xpath.evaluate(tempXPath, inputSource, XPathConstants.NODE);
            xmlCipher.doFinal(doc, selectedElement, content);
        } else if ("xpath".equalsIgnoreCase(encrypt)) {
            XPath xpath = XPathFactory.newInstance().newXPath();
            NamespaceContext ns = new SignatureNamespaceContext();
            InputSource inputSource = new InputSource(new java.io.FileInputStream(file));
            xpath.setNamespaceContext(ns);
            Element selectedElement = (Element) xpath.evaluate(expression, inputSource, XPathConstants.NODE);
            xmlCipher.doFinal(doc, selectedElement, content);
        }

        return doc;
    }

    /**
     * <p>Generates a detached encryption. A detached encryption only encrypts the complete detached XML document.</p>
     *
     * <p>A <code>CipherReference</code> element is appended to the current XML document (called context document) to
     * contain the reference (URI) to the encrypted data in the detached (and totally encrypted) XML document (called
     * source document).</p>
     *
     * @param file The selected XML document to contain the reference to the encrypted document
     * @param secretKey The data encryption key
     * @return The encrypted XML document
     * @throws Exception to indicate any exceptional condition
     */
    private Document detachedEncryption(File file, Key secretKey) throws Exception {
        Document contextDoc = Utils.parse(xmlFile);

        XMLCipher keyCipher = XMLCipher.getInstance(keyCipherAlgorithm);
        keyCipher.init(XMLCipher.WRAP_MODE, secretKey);

        XMLCipher xmlCipher = XMLCipher.getInstance(encryptionAlgorithm);
        xmlCipher.init(XMLCipher.ENCRYPT_MODE, secretKey);


        if ("document".equalsIgnoreCase(encrypt)) {
            // update the context XML document
            XMLCipher contextCipher = XMLCipher.getInstance();

            Element contextRoot = contextDoc.getDocumentElement();

            EncryptedKey encryptedKey = keyCipher.encryptKey(contextDoc, secretKey);
            EncryptedData encryptedData = contextCipher.createEncryptedData(CipherData.REFERENCE_TYPE, detachedFile
                    .toURI().toString());
            KeyInfo keyInfo = new KeyInfo(contextDoc);
            keyInfo.addKeyName(keyName);
            keyInfo.add(encryptedKey);
            encryptedData.setKeyInfo(keyInfo);
            EncryptionMethod em = contextCipher.createEncryptionMethod(encryptionAlgorithm);
            encryptedData.setEncryptionMethod(em);

            if (!"".equals(encryptionId)) {
                encryptedData.setId(encryptionId);
            }

            Element contextEncryption = contextCipher.martial(contextDoc, encryptedData);
            contextRoot.appendChild(contextEncryption);

            // encrypt the source XML document
            Document enc = xmlCipher.doFinal(detachedDoc, detachedDoc.getDocumentElement());
            NodeList encrypted = enc.getElementsByTagNameNS(EncryptionConstants.EncryptionSpecNS,
                    EncryptionConstants._TAG_CIPHERVALUE);

            String encryptedContent = "";
            if (encrypted.getLength() > 0) {
                encryptedContent = encrypted.item(0).getTextContent();
            }

            if (!"".equals(encryptedContent)) {
                Document encryptedDoc = Utils.createDocument();
                Element docElement = encryptedDoc.createElement("EncryptedDoc");
                docElement.setTextContent(encryptedContent);
                encryptedDoc.appendChild(docElement);

                FileOutputStream fosSource = new FileOutputStream(detachedFile);
                XMLUtils.outputDOM(encryptedDoc, fosSource);

                fosSource.flush();
                fosSource.close();
            }
        }

        return contextDoc;
    }
}