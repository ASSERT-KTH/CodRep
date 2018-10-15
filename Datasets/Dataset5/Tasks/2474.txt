public static String invalidXml, noDocument, noSignaturesInDocument, signaturesView;

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
package org.eclipse.wst.xml.security.core.actions;

import org.eclipse.osgi.util.NLS;

/**
 * <p>Externalized strings for the org.eclipse.wst.xml.security.core.actions package.</p>
 *
 * @author Dominik Schadow
 * @version 0.5.0
 */
public final class Messages extends NLS {
    /** The bundle name. */
    private static final String BUNDLE_NAME = "org.eclipse.wst.xml.security.core.actions.messages";

    /**
     * Private Constructor to avoid instantiation.
     */
    private Messages() {
    }

    static {
        // initialize resource bundle
        NLS.initializeMessages(BUNDLE_NAME, Messages.class);
    }

    /** General actions externalized strings. */
    public static String errorReasonUnavailable;

    /** Canonicalize action externalized strings. */
    public static String canonicalizationException, canonicalizationImpossible;

    /** Decryption action externalized strings. */
    public static String decryptingError, decryptionImpossible, decryptionTaskInfo, missingKeyStore,
    		missingKeyName,	quickDecryptionImpossible, quickDecryptionTitle;

    /** Encryption action externalized strings. */
    public static String encryptingError, encryptionImpossible, quickEncryptionImpossible,
            quickEncryptionImpossibleText, quickEncryptionTitle, encryptionTaskInfo;

    /** Verification action externalized strings. */
    public static String invalidCertificate, invalidValueElement, quickVerificationImpossible,
            quickVerificationTitle, signatureNotFound, verificationError, verificationImpossible;

    /** Signature action externalized strings. */
    public static String enterKeyStorePassword, enterKeyPassword, keyStore, keyStoreError,
    		keyStoreNotFound, keyStorePassword, missingCanonicalizationAlgorithm,
            missingKeystoreFile, missingKeyStorePassword, missingMDAlgorithm, missingParameter,
            missingKeyPassword, missingResource, missingSignatureAlgorithm, missingSignatureId,
            missingSignatureType, missingTransformationAlgorithm, missingXPathExpression, parsingError,
            parsingErrorText, keyPassword, protectedDoc, quickSignatureImpossible,
            quickSignatureImpossibleText, quickSignatureTitle, signatureImpossible, signingError, signatureTaskInfo;

    /** RefreshSignatures action externalized strings. */
    public static String invalidXml, noDocument, noSignaturesInDocument, refreshImpossible;

    /** MissingPreferenceDialog externalized strings. */
    public static String error, invalidTextSelection, invalidTextSelectionText, prefsDialogText, prefsLinkToolTip;

}