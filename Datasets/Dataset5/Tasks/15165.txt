verifyKeystorePassword, wrongKeyAlgorithm, keyStoreNotFound;

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

import org.eclipse.osgi.util.NLS;

/**
 * <p>Externalized strings for the org.eclipse.wst.xml.security.core.sign package.</p>
 *
 * @author Dominik Schadow
 * @version 0.5.0
 */
public final class Messages extends NLS {
    /** The bundle name. */
    private static final String BUNDLE_NAME = "org.eclipse.wst.xml.security.core.sign.messages";

    /**
     * Private Constructor to avoid instantiation.
     */
    private Messages() {
    }

    static {
        // initialize resource bundle
        NLS.initializeMessages(BUNDLE_NAME, Messages.class);
    }

    /** Wizard launcher externalized strings. */
    public static String signatureWizard;
    /** PageResource externalized strings. */
    public static String basicSecurityProfile, browse, bspCompliant, createKey, createKeystoreAndKey, detached,
            detachedFile, document, enterXPath, enveloped, enveloping, key, resource, resourceDescription,
            signatureTitle, select, selection, signatureType, useKey, verifyDetachedFile, xpath, xpathAttribute,
            xpathMultipleElements, xpathNoElement, xpathPopup, documentInvalid, keystoreAndKey;
    /** PageOpenCertificate externalized strings. */
    public static String enterKeyAlias, enterKeyPassword, enterKeystorePassword, open, password, selectKeyFile,
            useKeyDescription, verifyAll, verifyKeyAlias, verifyKeyPassword, verifyKeystore,
            verifyKeystorePassword, wrongKeyAlgorithm;
    /** PageCreateCertificate externalized strings. */
    public static String commonName, country, createKeyButton, createKeyDescription, certificate,
            enterCommonName, enterNewKeyAlias, enterNewKeyPassword, enterNewKeystoreName, enterNewKeystorePassword,
            keyAlgorithm, keyExistsInKeystore, keyGenerated, keyGenerationFailed, keyStore, keystoreAlreadyExists,
            location, organization, organizationalUnit, selectKeyAlgorithm, state;
    /** PageCreateKeystore externalized strings. */
    public static String createKeyStoreButton, createKeystoreDescription, keystoreGenerated,
            keystoreGenerationFailed, name;
    /** PageAlgorithms externalized strings. */
    public static String algorithmsDescription, ambiguousSignatureId, buttonAddProperty,
            buttonRemoveProperty, canonicalizationTransformation, encryptionWizard, messageDigestSignature,
            selectCanonicalization, selectMessageDigest, selectSignature, selectTransformation, signatureId,
            properties, signaturePropertyContent, signaturePropertyContentToolTip, signaturePropertyId,
            signaturePropertyIdToolTip, signaturePropertyTarget, signaturePropertyTargetToolTip, startEncryptionWizard;
}