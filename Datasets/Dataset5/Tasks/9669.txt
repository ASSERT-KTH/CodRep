import org.eclipse.wst.xml.vex.core.internal.provisional.dom.I.VEXDocument;

/*******************************************************************************
 * Copyright (c) 2008 Standards for Technology in Automotive Retail and others
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors:
 *     David Carver (STAR) - initial API and implementation
 *******************************************************************************/
package org.eclipse.wst.xml.vex.core.internal.dom;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.Reader;
import java.io.StringReader;

import javax.xml.parsers.ParserConfigurationException;

import org.eclipse.wst.xml.core.internal.provisional.document.IDOMDocument;
import org.eclipse.wst.xml.vex.core.internal.provisional.dom.VEXDocument;
import org.xml.sax.InputSource;
import org.xml.sax.SAXException;

/**
 * Class for creating documents given a DOM Document.
 */
@SuppressWarnings("restriction")
public class DOMDocumentReader extends DocumentReader {

	/**
	 * Reads a document given a DOM Document
	 * 
	 * @param domDocument
	 *            IDOMDocument from which to load the document.
	 */
	public VEXDocument read(IDOMDocument domDocument) throws IOException,
			ParserConfigurationException, SAXException {
		Reader reader = new StringReader(domDocument.getSource());
		return read(new InputSource(new BufferedReader(reader)));
	}

}