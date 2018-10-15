private IContent content = new GapContent(100);

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
package org.eclipse.wst.xml.vex.core.internal.dom;

import java.util.LinkedList;
import org.xml.sax.Attributes;
import org.xml.sax.ContentHandler;
import org.xml.sax.Locator;
import org.xml.sax.SAXException;
import org.xml.sax.SAXParseException;
import org.xml.sax.ext.LexicalHandler;

/**
 * A SAX handler that builds a Vex document. This builder collapses whitespace
 * as it goes, according to the following rules.
 * 
 * <ul>
 * <li>Elements with style white-space: pre are left alone.</li>
 * <li>Runs of whitespace are replaced with a single space.</li>
 * <li>Space just inside the start and end of elements is removed.</li>
 * <li>Space just outside the start and end of block-formatted elements is
 * removed.</li>
 * </ul>
 */
public class DocumentBuilder implements ContentHandler, LexicalHandler {

	/**
	 * Class constructor.
	 * 
	 * @param policyFactory
	 *            Used to determine the WhitespacePolicy to use for a given
	 *            document type.
	 */
	public DocumentBuilder(IWhitespacePolicyFactory policyFactory) {
		this.policyFactory = policyFactory;
	}

	/**
	 * Returns the newly built <code>Document</code> object.
	 */
	public IVEXDocument getDocument() {
		return this.doc;
	}

	// ============================================= ContentHandler methods

	public void characters(char[] ch, int start, int length)
			throws SAXException {

		// Convert nuls to spaces, since we use nulls for element delimiters
		char[] chars = new char[length];
		System.arraycopy(ch, start, chars, 0, length);
		for (int i = 0; i < chars.length; i++) {
			if (Character.isISOControl(chars[i]) && chars[i] != '\n'
					&& chars[i] != '\r' && chars[i] != '\t') {
				chars[i] = ' ';
			}
			
		}
		this.pendingChars.append(chars);
	}

	public void endDocument() {
		this.doc = new Document(this.content, this.rootElement);
		this.doc.setPublicID(this.dtdPublicID);
		this.doc.setSystemID(this.dtdSystemID);
		this.rootElement.setDocument(this.doc);
	}

	public void endElement(String namespaceURI, String localName, String qName) {

		this.appendChars(true);

		StackEntry entry = (StackEntry) this.stack.removeLast();

		// we must insert the trailing sentinel first, else the insertion
		// pushes the end position of the element to after the sentinel
		this.content.insertString(content.getLength(), "\0");
		entry.element.setContent(this.content, entry.offset, content
				.getLength() - 1);

		if (this.isBlock(entry.element)) {
			this.trimLeading = true;
		}
	}

	public void endPrefixMapping(java.lang.String prefix) {
	}

	public void ignorableWhitespace(char[] ch, int start, int length) {
	}

	public void processingInstruction(String target, String data) {
	}

	public void setDocumentLocator(Locator locator) {
		this.locator = locator;
	}

	public void skippedEntity(java.lang.String name) {
	}

	public void startDocument() {
	}

	public void startElement(String namespaceURI, String localName,
			String qName, Attributes attrs)

	throws SAXException {

		try {
			Element element;
			if (stack.size() == 0) {
				this.rootElement = new RootElement(qName);
				element = this.rootElement;
				if (this.policyFactory != null) {
					this.policy = this.policyFactory
							.getPolicy(this.dtdPublicID);
				}
			} else {
				element = new Element(qName);
				IVEXElement parent = ((StackEntry) stack.getLast()).element;
				parent.addChild(element);
			}

			int n = attrs.getLength();
			for (int i = 0; i < n; i++) {
				element.setAttribute(attrs.getQName(i), attrs.getValue(i));
			}

			this.appendChars(this.isBlock(element));

			stack.add(new StackEntry(element, content.getLength(), this
					.isPre(element)));
			content.insertString(content.getLength(), "\0");

			this.trimLeading = true;

		} catch (DocumentValidationException ex) {
			throw new SAXParseException("DocumentValidationException",
					this.locator, ex);
		}

	}

	public void startPrefixMapping(String prefix, String uri) {
	}

	// ============================================== LexicalHandler methods

	public void comment(char[] ch, int start, int length) {
	}

	public void endCDATA() {
	}

	public void endDTD() {
	}

	public void endEntity(String name) {
	}

	public void startCDATA() {
	}

	public void startDTD(String name, String publicId, String systemId) {
		this.dtdPublicID = publicId;
		this.dtdSystemID = systemId;
	}

	public void startEntity(java.lang.String name) {
	}

	// ======================================================== PRIVATE

	private IWhitespacePolicyFactory policyFactory;
	private IWhitespacePolicy policy;

	// Holds pending characters until we see another element boundary.
	// This is (a) so we can collapse spaces in multiple adjacent character
	// blocks, and (b) so we can trim trailing whitespace, if necessary.
	private StringBuffer pendingChars = new StringBuffer();

	// If true, trim the leading whitespace from the next received block of
	// text.
	private boolean trimLeading = false;

	// Content object to hold document content
	private Content content = new GapContent(100);

	// Stack of StackElement objects
	private LinkedList stack = new LinkedList();

	private RootElement rootElement;

	private String dtdPublicID;
	private String dtdSystemID;
	private Document doc;
	private Locator locator;

	// Append any pending characters to the content
	private void appendChars(boolean trimTrailing) {

		StringBuffer sb;

		StackEntry entry = this.stack.size() > 0 ? (StackEntry) this.stack
				.getLast() : null;

		if (entry != null && entry.pre) {

			sb = this.pendingChars;

		} else {

			// collapse the space in the pending characters
			sb = new StringBuffer(this.pendingChars.length());
			boolean ws = false; // true if we're in a run of whitespace
			for (int i = 0; i < this.pendingChars.length(); i++) {
				char c = this.pendingChars.charAt(i);
				if (Character.isWhitespace(c)) {
					ws = true;
				} else {
					if (ws) {
						sb.append(' ');
						ws = false;
					}
					sb.append(c);
				}
			}
			if (ws) {
				sb.append(' ');
			}
			// trim leading and trailing space, if necessary
			if (this.trimLeading && sb.length() > 0 && sb.charAt(0) == ' ') {
				sb.deleteCharAt(0);
			}
			if (trimTrailing && sb.length() > 0
					&& sb.charAt(sb.length() - 1) == ' ') {
				sb.setLength(sb.length() - 1);
			}
		}

		this.normalizeNewlines(sb);

		this.content.insertString(this.content.getLength(), sb.toString());

		this.pendingChars.setLength(0);
		this.trimLeading = false;
	}

	private boolean isBlock(IVEXElement element) {
		return this.policy != null && this.policy.isBlock(element);
	}

	private boolean isPre(IVEXElement element) {
		return this.policy != null && this.policy.isPre(element);
	}

	/**
	 * Convert lines that end in CR and CRLFs to plain newlines.
	 * 
	 * @param sb
	 *            StringBuffer to be normalized.
	 */
	private void normalizeNewlines(StringBuffer sb) {

		// State machine states
		final int START = 0;
		final int SEEN_CR = 1;

		int state = START;
		int i = 0;
		while (i < sb.length()) {
			// No simple 'for' here, since we may delete chars

			char c = sb.charAt(i);

			switch (state) {
			case START:
				if (c == '\r') {
					state = SEEN_CR;
				}
				i++;
				break;

			case SEEN_CR:
				if (c == '\n') {
					// CR-LF, just delete the previous CR
					sb.deleteCharAt(i - 1);
					state = START;
					// no need to advance i, since it's done implicitly
				} else if (c == '\r') {
					// CR line ending followed by another
					// Replace the first with a newline...
					sb.setCharAt(i - 1, '\n');
					i++;
					// ...and stay in the SEEN_CR state
				} else {
					// CR line ending, replace it with a newline
					sb.setCharAt(i - 1, '\n');
					i++;
					state = START;
				}
			}
		}

		if (state == SEEN_CR) {
			// CR line ending, replace it with a newline
		}
	}

	private static class StackEntry {
		public Element element;
		public int offset;
		public boolean pre;

		public StackEntry(Element element, int offset, boolean pre) {
			this.element = element;
			this.offset = offset;
			this.pre = pre;
		}
	}
}