package org.eclipse.wst.xml.vex.ui.internal.swing;

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
package org.eclipse.wst.xml.vex.core.internal.swing;

import java.awt.datatransfer.DataFlavor;
import java.awt.datatransfer.StringSelection;
import java.awt.datatransfer.UnsupportedFlavorException;
import java.io.IOException;

import org.eclipse.wst.xml.vex.core.internal.dom.DocumentFragment;

/**
 * Represents a selection of a Vex document, which can be viewed as plaintext or
 * as a document fragment.
 */
public class VexSelection extends StringSelection {

	/**
	 * DataFlavor representing a Vex document fragment.
	 */
	public static final DataFlavor VEX_DOCUMENT_FRAGMENT_FLAVOR = new DataFlavor(
			DocumentFragment.class, DocumentFragment.MIME_TYPE);

	private DataFlavor[] flavors;
	private DocumentFragment frag;

	/**
	 * Class constructor.
	 * 
	 * @param s
	 *            String representing the selection.
	 * @param frag
	 *            Document fragment representing the selection.
	 */
	public VexSelection(String s, DocumentFragment frag) {
		super(s);
		this.frag = frag;

		DataFlavor[] superFlavors = super.getTransferDataFlavors();
		this.flavors = new DataFlavor[superFlavors.length + 1];
		System.arraycopy(superFlavors, 0, this.flavors, 0, superFlavors.length);
		this.flavors[this.flavors.length - 1] = VEX_DOCUMENT_FRAGMENT_FLAVOR;
	}

	public Object getTransferData(DataFlavor flavor)
			throws UnsupportedFlavorException, IOException {

		if (flavor.equals(VEX_DOCUMENT_FRAGMENT_FLAVOR)) {
			return this.frag;
		} else {
			return super.getTransferData(flavor);
		}
	}

	public DataFlavor[] getTransferDataFlavors() {
		return this.flavors;
	}

	public boolean isDataFlavorSupported(DataFlavor flavor) {
		if (flavor.equals(VEX_DOCUMENT_FRAGMENT_FLAVOR)) {
			return true;
		} else {
			return super.isDataFlavorSupported(flavor);
		}
	}

}