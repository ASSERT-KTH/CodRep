public XmlSecurityCertificate(String type) {

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

import java.security.InvalidKeyException;
import java.security.NoSuchAlgorithmException;
import java.security.NoSuchProviderException;
import java.security.PublicKey;
import java.security.SignatureException;
import java.security.cert.Certificate;
import java.security.cert.CertificateEncodingException;
import java.security.cert.CertificateException;

/**
 * <p>Generates a new X.509 certificate. This certificate may be stored in a Java KeyStore.</p>
 *
 * @author Dominik Schadow
 * @version 0.5.0
 */
public class XmlSecurityCertificate extends Certificate {
    protected XmlSecurityCertificate(String type) {
        super(type);
    }

    /**
     * Default constructor. Generates a new certificate with the default
     * type <b>X.509</b>. The supported types depend on the Java 2 SDK Security API.
     */
    public XmlSecurityCertificate() {
        super("X.509");
    }

    @Override
    public byte[] getEncoded() throws CertificateEncodingException {
        return "PKCS#8".getBytes();
    }

    @Override
    public PublicKey getPublicKey() {
        // TODO Auto-generated method stub
        return null;
    }

    @Override
    public String toString() {
        // TODO Auto-generated method stub
        return "dummy";
    }

    @Override
    public void verify(PublicKey key) throws CertificateException, NoSuchAlgorithmException,
            InvalidKeyException, NoSuchProviderException, SignatureException {
        // TODO Auto-generated method stub

    }

    @Override
    public void verify(PublicKey key, String sigProvider) throws CertificateException,
            NoSuchAlgorithmException, InvalidKeyException, NoSuchProviderException,
            SignatureException {
        // TODO Auto-generated method stub

    }
}