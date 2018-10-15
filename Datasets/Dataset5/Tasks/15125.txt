public byte[] serialize() throws SerializationException;

/****************************************************************************
 * Copyright (c) 2008 Composent, Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Composent, Inc. - initial API and implementation
 *****************************************************************************/

package org.eclipse.ecf.sync.doc;

/**
 * Document change message.  Instances of this interface
 * may be serialized to a byte [] so that they can be
 * communicated to remote processes.
 */
public interface IDocumentChangeMessage {

	public byte[] toByteArray() throws SerializationException;

}