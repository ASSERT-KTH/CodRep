package org.eclipse.ecf.internal.provisional.docshare.messages;

/****************************************************************************
 * Copyright (c) 2007 Composent, Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Composent, Inc. - initial API and implementation
 *****************************************************************************/

package org.eclipse.ecf.docshare.messages;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.io.Serializable;

/**
 *
 */
public class Message implements Serializable {

	private static final long serialVersionUID = 4858801311305630711L;

	public byte[] serialize() throws Exception {
		final ByteArrayOutputStream bos = new ByteArrayOutputStream();
		final ObjectOutputStream oos = new ObjectOutputStream(bos);
		oos.writeObject(this);
		return bos.toByteArray();
	}

	public static Message deserialize(byte[] bytes) throws Exception {
		final ByteArrayInputStream bins = new ByteArrayInputStream(bytes);
		final ObjectInputStream oins = new ObjectInputStream(bins);
		return (Message) oins.readObject();
	}
}