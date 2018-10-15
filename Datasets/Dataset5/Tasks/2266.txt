throw new RuntimeException("No MD5 digest found"); //$NON-NLS-1$

/*******************************************************************************
 * Copyright (c) 2005, 2007 Remy Suen
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Remy Suen <remy.suen@gmail.com> - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.protocol.msn.internal.encode;

import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

public final class Challenge {

	public static final String PRODUCT_ID = "PROD0090YUAUV{2B"; //$NON-NLS-1$

	private static final String PRODUCT_KEY = "YMM8C_H7KCQ2S_KL"; //$NON-NLS-1$

	private static MessageDigest instance;

	static {
		try {
			instance = MessageDigest.getInstance("MD5"); //$NON-NLS-1$
		} catch (NoSuchAlgorithmException e) {
			throw new RuntimeException("No MD5 digest found");
		}
	}

	public static String createQuery(String challenge) {
		String[] s = computeMD5DigestAsStringArray((challenge + PRODUCT_KEY)
				.getBytes());
		String md5Hash = computeMD5Digest((challenge + PRODUCT_KEY).getBytes());
		int[] md5 = new int[4];
		for (int i = 0; i < 4; i++) {
			md5[i] = Integer.parseInt(s[i], 16);
		}

		String chl = challenge + PRODUCT_ID;
		while (chl.length() % 8 != 0) {
			chl += '0';
		}

		char[] array = chl.toCharArray();
		String[] values = new String[chl.length() / 4];
		for (int i = 0; i < array.length; i += 4) {
			int j = array[i + 3];
			String value = Integer.toHexString(j);
			j = array[i + 2];
			value += Integer.toHexString(j);
			j = array[i + 1];
			value += Integer.toHexString(j);
			j = array[i];
			value += Integer.toHexString(j);
			values[i / 4] = value;
		}

		int[] ints = new int[values.length];
		for (int i = 0; i < values.length; i++) {
			ints[i] = Integer.parseInt(values[i], 16);
		}

		long high = 0;
		long low = 0;
		for (int i = 0; i < ints.length; i += 2) {
			long temp = ints[i];
			temp = (temp * 0xe79a9c1L) % 0x7fffffff;
			temp += high;
			temp = md5[0] * temp + md5[1];
			temp = temp % 0x7fffffff;

			high = ints[i + 1];
			high = (high + temp) % 0x7fffffff;
			high = md5[2] * high + md5[3];
			high = high % 0x7fffffff;

			low = low + high + temp;
		}

		high = (high + md5[1]) % 0x7fffffff;
		low = (low + md5[3]) % 0x7fffffff;

		String highString = Long.toHexString(high);
		String lowString = Long.toHexString(low);

		while (highString.length() < 8) {
			highString = '0' + highString;
		}

		while (lowString.length() < 8) {
			lowString = '0' + lowString;
		}

		highString = highString.substring(6, 8) + highString.substring(4, 6)
				+ highString.substring(2, 4) + highString.substring(0, 2);
		lowString = lowString.substring(6, 8) + lowString.substring(4, 6)
				+ lowString.substring(2, 4) + lowString.substring(0, 2);

		high = Long.parseLong(highString, 16);
		low = Long.parseLong(lowString, 16);

		String first = Long.toHexString((Long.parseLong(
				md5Hash.substring(0, 8), 16) ^ high));
		String second = Long.toHexString((Long.parseLong(md5Hash.substring(8,
				16), 16) ^ low));
		String third = Long.toHexString((Long.parseLong(md5Hash.substring(16,
				24), 16) ^ high));
		String fourth = Long.toHexString((Long.parseLong(md5Hash.substring(24,
				32), 16) ^ low));

		while (first.length() < 8) {
			first = '0' + first;
		}

		while (second.length() < 8) {
			second = '0' + second;
		}

		while (third.length() < 8) {
			third = '0' + third;
		}

		while (fourth.length() < 8) {
			fourth = '0' + fourth;
		}

		return first + second + third + fourth;
	}

	/**
	 * Computes the MD5 digest of a string given its bytes.
	 * 
	 * @param bytes
	 *            the bytes of the string to be digested
	 * @return the MD5 digest of the original string
	 */
	private static final String computeMD5Digest(byte[] bytes) {
		byte[] hash = instance.digest(bytes);
		StringBuffer buffer = new StringBuffer();
		synchronized (buffer) {
			for (int i = 0; i < hash.length; i++) {
				int value = 0xff & hash[i];
				if (value < 16) {
					buffer.append('0').append(Integer.toHexString(value));
				} else {
					buffer.append(Integer.toHexString(value));
				}
			}
			return buffer.toString();
		}
	}

	private static final String[] computeMD5DigestAsStringArray(byte[] bytes) {
		byte[] hash = instance.digest(bytes);
		StringBuffer buffer = new StringBuffer();
		synchronized (buffer) {
			for (int i = 0; i < hash.length; i++) {
				int value = 0xff & hash[i];
				if (value < 16) {
					buffer.append('0').append(Integer.toHexString(value));
				} else {
					buffer.append(Integer.toHexString(value));
				}
			}
		}

		String result = buffer.toString();
		String[] results = new String[4];
		results[0] = result.substring(0, 8);
		results[1] = result.substring(8, 16);
		results[2] = result.substring(16, 24);
		results[3] = result.substring(24, 32);

		for (int i = 0; i < 4; i++) {
			char[] array = results[i].toCharArray();
			char[] swapped = new char[8];
			for (int j = 0; j < 8; j += 2) {
				swapped[7 - j] = array[j + 1];
				swapped[6 - j] = array[j];
			}
			results[i] = new String(swapped);
		}

		for (int i = 0; i < 4; i++) {
			long l = Long.parseLong(results[i], 16);
			l = l & 0x7fffffff;
			if (l < 0x10000000) {
				results[i] = '0' + Long.toHexString(l);
			} else {
				results[i] = Long.toHexString(l);
			}
		}

		return results;
	}
}