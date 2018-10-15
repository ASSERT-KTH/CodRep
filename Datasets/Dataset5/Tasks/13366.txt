import org.eclipse.wst.xml.vex.core.internal.provisional.dom.IVEXDocumentFragment;

/*******************************************************************************
 * Copyright (c) 2004, 2008 John Krasnay and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors:
 *     John Krasnay - initial API and implementation
 *******************************************************************************/
package org.eclipse.wst.xml.vex.ui.internal.swt;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;

import org.eclipse.swt.dnd.ByteArrayTransfer;
import org.eclipse.swt.dnd.TransferData;
import org.eclipse.wst.xml.vex.core.internal.dom.DocumentFragment;
import org.eclipse.wst.xml.vex.core.internal.dom.IVEXDocumentFragment;

/**
 * Transfer object that handles Vex DocumentFragments.
 */
public class DocumentFragmentTransfer extends ByteArrayTransfer {

	/**
	 * Returns the singleton instance of the DocumentFragmentTransfer.
	 */
	public static DocumentFragmentTransfer getInstance() {
		if (instance == null) {
			instance = new DocumentFragmentTransfer();
		}
		return instance;
	}

	protected String[] getTypeNames() {
		return typeNames;
	}

	protected int[] getTypeIds() {
		return typeIds;
	}

	public void javaToNative(Object object, TransferData transferData) {
		if (object == null || !(object instanceof DocumentFragment))
			return;

		if (isSupportedType(transferData)) {
			IVEXDocumentFragment frag = (IVEXDocumentFragment) object;
			try {
				// write data to a byte array and then ask super to convert to
				// pMedium
				ByteArrayOutputStream out = new ByteArrayOutputStream();
				ObjectOutputStream oos = new ObjectOutputStream(out);
				oos.writeObject(frag);
				byte[] buffer = out.toByteArray();
				oos.close();
				super.javaToNative(buffer, transferData);
			} catch (IOException e) {
			}
		}
	}

	public Object nativeToJava(TransferData transferData) {

		if (isSupportedType(transferData)) {
			byte[] buffer = (byte[]) super.nativeToJava(transferData);
			if (buffer == null)
				return null;

			try {
				ByteArrayInputStream in = new ByteArrayInputStream(buffer);
				ObjectInputStream ois = new ObjectInputStream(in);
				Object object = ois.readObject();
				ois.close();
				return object;
			} catch (ClassNotFoundException ex) {
				return null;
			} catch (IOException ex) {
				return null;
			}
		}

		return null;
	}

	// =================================================== PRIVATE

	private static final String[] typeNames = { IVEXDocumentFragment.MIME_TYPE };
	private static final int[] typeIds = { ByteArrayTransfer
			.registerType(IVEXDocumentFragment.MIME_TYPE) };

	private static DocumentFragmentTransfer instance;

	private DocumentFragmentTransfer() {
	}
}