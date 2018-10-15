public Class[][] getSupportedParameterTypes() {

/*******************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.core.identity;

import java.security.SecureRandom;

import org.eclipse.ecf.core.util.Base64;

/**
 * Globally unique ID implementation class. Uses
 * {@link java.security.SecureRandom} to create a unique number of given byte
 * length. Default byte length for secure number is 20 bytes. Default algorithm
 * used for creating a SecureRandom instance is SHA1PRNG.
 */
public class GUID extends StringID {
	private static final long serialVersionUID = 3545794369039972407L;

	public static class GUIDNamespace extends Namespace {
		private static final long serialVersionUID = -8546568877571886386L;

		public GUIDNamespace() {
			super(GUID.class.getName(), "GUID Namespace");
		}

		public ID createInstance(Object[] args) throws IDCreateException {
			if (args == null || args.length <= 0)
				return new GUID(this);
			else if (args.length == 1 && args[0] instanceof Integer)
				return new GUID(this, ((Integer) args[0]).intValue());
			else
				return new GUID(this);
		}

		public String getScheme() {
			return GUID.class.getName();
		}

		/*
		 * (non-Javadoc)
		 * 
		 * @see org.eclipse.ecf.core.identity.Namespace#getSupportedParameterTypesForCreateInstance()
		 */
		public Class[][] getSupportedParameterTypesForCreateInstance() {
			return new Class[][] { {}, { Integer.class } };
		}

	}

	public static final String SR_DEFAULT_ALGO = null;

	public static final String SR_DEFAULT_PROVIDER = null;

	public static final int DEFAULT_BYTE_LENGTH = 20;

	// Class specific SecureRandom instance
	protected static transient SecureRandom random;

	/**
	 * Protected constructor for factory-based construction
	 * 
	 * @param n
	 *            the Namespace this identity will belong to
	 * @param provider
	 *            the name of the algorithm to use. See {@link SecureRandom}
	 * @param byteLength
	 *            the length of the target number (in bytes)
	 */
	protected GUID(Namespace n, String algo, String provider, int byteLength)
			throws IDCreateException {
		super(n, "");
		// Get SecureRandom instance for class
		try {
			getRandom(algo, provider);
		} catch (Exception e) {
			throw new IDCreateException("GUID creation failure: "
					+ e.getMessage());
		}
		// make sure we have reasonable byteLength
		if (byteLength <= 0)
			byteLength = 1;
		byte[] newBytes = new byte[byteLength];
		// Fill up random bytes
		random.nextBytes(newBytes);
		// Set value
		value = Base64.encode(newBytes);
	}

	protected GUID(Namespace n, int byteLength) throws IDCreateException {
		this(n, SR_DEFAULT_ALGO, SR_DEFAULT_PROVIDER, byteLength);
	}

	protected GUID(Namespace n) throws IDCreateException {
		this(n, DEFAULT_BYTE_LENGTH);
	}

	/**
	 * Get SecureRandom instance for creation of random number.
	 * 
	 * @param algo
	 *            the String algorithm specification (e.g. "SHA1PRNG") for
	 *            creation of the SecureRandom instance
	 * @param provider
	 *            the provider of the implementation of the given algorighm
	 *            (e.g. "SUN")
	 * @return SecureRandom
	 * @exception Exception
	 *                thrown if SecureRandom instance cannot be created/accessed
	 */
	protected static synchronized SecureRandom getRandom(String algo,
			String provider) throws Exception {
		// Given algo and provider, get SecureRandom instance
		if (random == null) {
			initializeRandom(algo, provider);
		}
		return random;
	}

	protected static synchronized void initializeRandom(String algo,
			String provider) throws Exception {
		if (provider == null) {
			if (algo == null) {
				try {
					random = SecureRandom.getInstance("IBMSECURERANDOM");
				} catch (Exception e) {
					random = SecureRandom.getInstance("SHA1PRNG");
				}
			} else
				random = SecureRandom.getInstance(algo);
		} else {
			random = SecureRandom.getInstance(algo, provider);
		}
	}

	public String toString() {
		StringBuffer sb = new StringBuffer("GUID[");
		sb.append(value).append("]");
		return sb.toString();
	}
}
 No newline at end of file