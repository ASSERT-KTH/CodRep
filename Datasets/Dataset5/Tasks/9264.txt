content.insertString(this.content.getLength(), text);

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

import java.util.Iterator;
import java.util.List;

import org.eclipse.emf.common.util.BasicEList;
import org.eclipse.emf.common.util.EList;
import org.eclipse.wst.xml.vex.core.internal.core.ListenerList;
import org.eclipse.wst.xml.vex.core.internal.provisional.dom.I.Content;
import org.eclipse.wst.xml.vex.core.internal.provisional.dom.I.Position;
import org.eclipse.wst.xml.vex.core.internal.provisional.dom.I.VEXDocument;
import org.eclipse.wst.xml.vex.core.internal.provisional.dom.I.VEXDocumentFragment;
import org.eclipse.wst.xml.vex.core.internal.provisional.dom.I.VEXElement;
import org.eclipse.wst.xml.vex.core.internal.provisional.dom.I.VEXNode;
import org.eclipse.wst.xml.vex.core.internal.provisional.dom.I.Validator;
import org.eclipse.wst.xml.vex.core.internal.provisional.dom.impl.VEXDocumentImpl;
import org.eclipse.wst.xml.vex.core.internal.undo.CannotRedoException;
import org.eclipse.wst.xml.vex.core.internal.undo.CannotUndoException;
import org.eclipse.wst.xml.vex.core.internal.undo.IUndoableEdit;
import org.w3c.dom.Attr;
import org.w3c.dom.NamedNodeMap;
import org.w3c.dom.NodeList;

/**
 * Represents an XML document.
 * 
 */
public class Document extends VEXDocumentImpl implements VEXDocument {

	//private Content content;
	//private RootElement rootElement;
	private ListenerList listeners = new ListenerList(DocumentListener.class,
			DocumentEvent.class);
	private boolean undoEnabled = true;

	//private String publicID;
	protected String systemID;
	
	protected org.w3c.dom.Document domDocument;
	
	//private String encoding;
	//private Validator validator;

	/**
	 * Class constructor.
	 * 
	 * @param rootElement
	 *            root element of the document. The document property of this
	 *            RootElement is set by this constructor.
	 * 
	 */
	public Document(VEXElement rootElement) {
		content = new GapContent(100);
		content.insertString(0, "\0\0");

		this.rootElement = rootElement;
		rootElement.setDocument(this);
		rootElement.setContent(content, 0, 1);
		
	}
	
	public Document(org.w3c.dom.Document domDocument) {
		content = new GapContent(100);
		content.insertString(0, "\0\0");
		
		setDOMDocument(domDocument);
		rootElement.setDocument(this);
	}

	/**
	 * Class constructor. This constructor is used by the document builder and
	 * assumes that the content and root element have bee properly set up.
	 * 
	 * @param content
	 *            Content object used to store the document's content.
	 * @param rootElement
	 *            RootElement of the document.
	 * 
	 */
	public Document(Content content, VEXElement rootElement) {
		this.content = content;
		this.rootElement = rootElement;
	}

	/* (non-Javadoc)
	 * @see org.eclipse.wst.xml.vex.core.internal.dom.IVEXDocument#addDocumentListener(org.eclipse.wst.xml.vex.core.internal.dom.DocumentListener)
	 * 
	 */
	public void addDocumentListener(DocumentListener listener) {
		this.listeners.add(listener);
	}

	/* (non-Javadoc)
	 * @see org.eclipse.wst.xml.vex.core.internal.dom.IVEXDocument#canInsertFragment(int, org.eclipse.wst.xml.vex.core.internal.dom.DocumentFragment)
	 * 
	 */
	public boolean canInsertFragment(int offset, VEXDocumentFragment fragment) {

		if (this.validator == null) {
			return true;
		}

		VEXElement element = getElementAt(offset);
		EList<String> seq1 = getNodeNames(element.getStartOffset() + 1, offset);
		
		EList<String> seq2 = fragment.getNodeNames();
		
		EList<String> seq3 = getNodeNames(offset, element.getEndOffset());
		
		return this.validator.isValidSequence(element.getName(), seq1, seq2,
				seq3, true);
	}

	/* (non-Javadoc)
	 * @see org.eclipse.wst.xml.vex.core.internal.dom.IVEXDocument#canInsertText(int)
	 * 
	 */
	public boolean canInsertText(int offset) {

		if (this.validator == null) {
			return true;
		}

		VEXElement element = getElementAt(offset);
		EList<String> seq1 = getNodeNames(element.getStartOffset() + 1, offset);

		EList<String> seq2 = new BasicEList<String>();
		seq2.add("#PCDATA");
		
		EList<String> seq3 = getNodeNames(offset, element.getEndOffset());

		return this.validator.isValidSequence(element.getName(), seq1, seq2,
				seq3, true);
	}

	/* (non-Javadoc)
	 * @see org.eclipse.wst.xml.vex.core.internal.dom.IVEXDocument#createPosition(int)
	 * 
	 */
	public Position createPosition(int offset) {
		return this.content.createPosition(offset);
	}

	/* (non-Javadoc)
	 * @see org.eclipse.wst.xml.vex.core.internal.dom.IVEXDocument#delete(int, int)
	 * 
	 */
	public void delete(int startOffset, int endOffset)
			throws DocumentValidationException {

		VEXElement e1 = this.getElementAt(startOffset);
		VEXElement e2 = this.getElementAt(endOffset);
		if (e1 != e2) {
			throw new IllegalArgumentException("Deletion from " + startOffset
					+ " to " + endOffset + " is unbalanced");
		}

		Validator validator = this.getValidator();
		if (validator != null) {
			EList<String> seq1 = this.getNodeNames(e1.getStartOffset() + 1,
					startOffset);

			EList<String> seq2 = this.getNodeNames(endOffset, e1.getEndOffset());

			if (!validator
					.isValidSequence(e1.getName(), seq1, seq2, null, true)) {
				throw new DocumentValidationException("Unable to delete from "
						+ startOffset + " to " + endOffset);
			}
		}

		// Grab the fragment for the undoable edit while it's still here
		VEXDocumentFragment frag = getFragment(startOffset, endOffset);

		this.fireBeforeContentDeleted(new DocumentEvent(this, e1, startOffset,
				endOffset - startOffset, null));

		Iterator iter = e1.getChildNodes().iterator();
		if (e1 instanceof Element) {
			iter = ((Element) e1).getChildIterator();
		}
		while (iter.hasNext()) {
			VEXNode child = (VEXNode) iter.next();
			if (startOffset <= child.getStartOffset()
					&& child.getEndOffset() < endOffset) {
				iter.remove();
			}
		}

		this.content.remove(startOffset, endOffset - startOffset);

		IUndoableEdit edit = this.undoEnabled ? new DeleteEdit(startOffset,
				endOffset, frag) : null;

		this.fireContentDeleted(new DocumentEvent(this, e1, startOffset,
				endOffset - startOffset, edit));
	}

	/* (non-Javadoc)
	 * @see org.eclipse.wst.xml.vex.core.internal.dom.IVEXDocument#findCommonElement(int, int)
	 * 
	 */
	public VEXElement findCommonElement(int offset1, int offset2) {
		VEXElement element = this.rootElement;
		for (;;) {
			boolean tryAgain = false;
			EList<VEXElement> children = element.getChildElements();
			for (int i = 0; i < children.size(); i++) {
				if (offset1 > children.get(i).getStartOffset()
						&& offset2 > children.get(i).getStartOffset()
						&& offset1 <= children.get(i).getEndOffset()
						&& offset2 <= children.get(i).getEndOffset()) {

					element = children.get(i);
					tryAgain = true;
					break;
				}
			}
			if (!tryAgain) {
				break;
			}
		}
		return element;
	}

	/* (non-Javadoc)
	 * @see org.eclipse.wst.xml.vex.core.internal.dom.IVEXDocument#getCharacterAt(int)
	 * 
	 */
	public char getCharacterAt(int offset) {
		return this.content.getString(offset, 1).charAt(0);
	}

	/* (non-Javadoc)
	 * @see org.eclipse.wst.xml.vex.core.internal.dom.IVEXDocument#getElementAt(int)
	 * 
	 */
	public VEXElement getElementAt(int offset) {
		if (offset < 1 || offset >= this.getLength()) {
			throw new IllegalArgumentException("Illegal offset: " + offset
					+ ". Must be between 1 and n-1");
		}
		VEXElement element = this.rootElement;
		for (;;) {
			boolean tryAgain = false;
			EList<VEXElement> children = element.getChildElements();
			for (int i = 0; i < children.size(); i++) {
				VEXElement child = children.get(i);
				if (offset <= child.getStartOffset()) {
					return element;
				} else if (offset <= child.getEndOffset()) {
					element = child;
					tryAgain = true;
					break;
				}
			}
			if (!tryAgain) {
				break;
			}
		}
		return element;
	}

	/* (non-Javadoc)
	 * @see org.eclipse.wst.xml.vex.core.internal.dom.IVEXDocument#getEncoding()
	 * 
	 */
	public String getEncoding() {
		return this.encoding;
	}

	/* (non-Javadoc)
	 * @see org.eclipse.wst.xml.vex.core.internal.dom.IVEXDocument#getFragment(int, int)
	 * 
	 */
	public VEXDocumentFragment getFragment(int startOffset, int endOffset) {

		assertOffset(startOffset, 0, this.content.getLength());
		assertOffset(endOffset, 0, this.content.getLength());

		if (endOffset <= startOffset) {
			throw new IllegalArgumentException("Invalid range (" + startOffset
					+ ", " + endOffset + ")");
		}

		VEXElement e1 = this.getElementAt(startOffset);
		VEXElement e2 = this.getElementAt(endOffset);
		if (e1 != e2) {
			throw new IllegalArgumentException("Fragment from " + startOffset
					+ " to " + endOffset + " is unbalanced");
		}

		EList<VEXElement> children = e1.getChildElements();

		Content newContent = new GapContent(endOffset - startOffset);
		String s = content.getString(startOffset, endOffset - startOffset);
		newContent.insertString(0, s);
		EList<VEXElement> newChildren = new BasicEList<VEXElement>();
		for (int i = 0; i < children.size(); i++) {
			VEXElement child = children.get(i);
			if (child.getEndOffset() <= startOffset) {
				continue;
			} else if (child.getStartOffset() >= endOffset) {
				break;
			} else {
				newChildren.add(cloneElement(child, newContent,
						-startOffset, null));
			}
		}

		return new DocumentFragment(newContent, newChildren);
	}

	/* (non-Javadoc)
	 * @see org.eclipse.wst.xml.vex.core.internal.dom.IVEXDocument#getLength()
	 * 
	 */
	public int getLength() {
		return this.content.getLength();
	}

	/* (non-Javadoc)
	 * @see org.eclipse.wst.xml.vex.core.internal.dom.IVEXDocument#getNodeNames(int, int)
	 * 
	 */
	public EList<String> getNodeNames(int startOffset, int endOffset) {

		EList<VEXNode> nodes = this.getNodes(startOffset, endOffset);
		EList<String> names = new BasicEList(nodes.size());

		for (int i = 0; i < nodes.size(); i++) {
			VEXNode node = nodes.get(i);
			if (node instanceof Element) {
				names.add(((Element) node).getName());
			} else {
				names.add("#PCDATA");
			}
		}

		return names;
	}

	/* (non-Javadoc)
	 * @see org.eclipse.wst.xml.vex.core.internal.dom.IVEXDocument#getNodes(int, int)
	 * 
	 */
	public EList<VEXNode> getNodes(int startOffset, int endOffset) {

		VEXElement element = this.getElementAt(startOffset);
		if (element != this.getElementAt(endOffset)) {
			throw new IllegalArgumentException("Offsets are unbalanced: "
					+ startOffset + " is in " + element.getName() + ", "
					+ endOffset + " is in "
					+ this.getElementAt(endOffset).getName());
		}

		EList list = new BasicEList();
		List<VEXNode> nodes = element.getChildNodes();
		for (int i = 0; i < nodes.size(); i++) {
			VEXNode node = nodes.get(i);
			if (node.getEndOffset() <= startOffset) {
				continue;
			} else if (node.getStartOffset() >= endOffset) {
				break;
			} else {
				if (node instanceof Element) {
					list.add(node);
				} else {
					Text text = (Text) node;
					if (text.getStartOffset() < startOffset) {
						text.setContent(text.getContent(), startOffset, text
								.getEndOffset());
					} else if (text.getEndOffset() > endOffset) {
						text.setContent(text.getContent(), text
								.getStartOffset(), endOffset);
					}
					list.add(text);
				}
			}
		}

		return list;
	}

	/**
	 * Creates an array of nodes for a given run of content. The returned array
	 * includes the given child elements and <code>Text</code> objects where
	 * text appears between elements.
	 * 
	 * @param content
	 *            Content object containing the content
	 * @param startOffset
	 *            start offset of the run
	 * @param endOffset
	 *            end offset of the run
	 * @param elements
	 *            child elements that are within the run
	 */
	static EList<VEXNode> createNodeList(Content content, int startOffset,
			int endOffset, EList<VEXNode> elements) {

		EList nodes = new BasicEList();
		int offset = startOffset;
		for (int i = 0; i < elements.size(); i++) {
			int start = elements.get(i).getStartOffset();
			if (offset < start) {
				nodes.add(new Text(content, offset, start));
			}
			nodes.add(elements.get(i));
			offset = elements.get(i).getEndOffset() + 1;
		}

		if (offset < endOffset) {
			nodes.add(new Text(content, offset, endOffset));
		}

		return nodes;
	}

	/* (non-Javadoc)
	 * @see org.eclipse.wst.xml.vex.core.internal.dom.IVEXDocument#getPublicID()
	 * 
	 */
	public String getPublicID() {
		return this.publicID;
	}

	/* (non-Javadoc)
	 * @see org.eclipse.wst.xml.vex.core.internal.dom.IVEXDocument#getRawText(int, int)
	 * 
	 */
	public String getRawText(int startOffset, int endOffset) {
		return this.content.getString(startOffset, endOffset - startOffset);
	}

	/* (non-Javadoc)
	 * @see org.eclipse.wst.xml.vex.core.internal.dom.IVEXDocument#getRootElement()
	 * 
	 */
	public VEXElement getRootElement() {
		return rootElement;
	}

	/* (non-Javadoc)
	 * @see org.eclipse.wst.xml.vex.core.internal.dom.IVEXDocument#getSystemID()
	 * 
	 */
	public String getSystemID() {
		return systemID;
	}

	/* (non-Javadoc)
	 * @see org.eclipse.wst.xml.vex.core.internal.dom.IVEXDocument#getText(int, int)
	 * 
	 */
	public String getText(int startOffset, int endOffset) {
		String raw = this.content.getString(startOffset, endOffset
				- startOffset);
		StringBuffer sb = new StringBuffer(raw.length());
		for (int i = 0; i < raw.length(); i++) {
			char c = raw.charAt(i);
			if (c != '\0') {
				sb.append(c);
			}
		}
		return sb.toString();
	}

	/* (non-Javadoc)
	 * @see org.eclipse.wst.xml.vex.core.internal.dom.IVEXDocument#getValidator()
	 * 
	 */
	public Validator getValidator() {
		return this.validator;
	}

	/* (non-Javadoc)
	 * @see org.eclipse.wst.xml.vex.core.internal.dom.IVEXDocument#insertElement(int, org.eclipse.wst.xml.vex.core.internal.dom.Element)
	 * 
	 */
	public void insertElement(int offset, VEXElement element)
			throws DocumentValidationException {

		if (offset < 1 || offset >= this.getLength()) {
			throw new IllegalArgumentException("Error inserting element <"
					+ element.getName() + ">: offset is " + offset
					+ ", but it must be between 1 and "
					+ (this.getLength() - 1));
		}

		Validator validator = this.getValidator();
		if (validator != null) {
			VEXElement parent = this.getElementAt(offset);
			EList<String> seq1 = this.getNodeNames(parent.getStartOffset() + 1,
					offset);
			EList<String> seq2 = new BasicEList();
			seq2.add(element.getName());
			EList<String> seq3 = this.getNodeNames(offset, parent.getEndOffset());

			if (!validator.isValidSequence(parent.getName(), seq1, seq2, seq3,
					true)) {
				throw new DocumentValidationException("Cannot insert element "
						+ element.getName() + " at offset " + offset);
			}
		}

		// find the parent, and the index into its children at which
		// this element should be inserted
		VEXElement parent = this.rootElement;
		int childIndex = -1;
		while (childIndex == -1) {
			boolean tryAgain = false;
			EList<VEXElement> children = parent.getChildElements();
			for (int i = 0; i < children.size(); i++) {
				VEXElement child = children.get(i);
				if (offset <= child.getStartOffset()) {
					childIndex = i;
					break;
				} else if (offset <= child.getEndOffset()) {
					parent = child;
					tryAgain = true;
					break;
				}
			}
			if (!tryAgain && childIndex == -1) {
				childIndex = children.size();
				break;
			}
		}

		this.fireBeforeContentInserted(new DocumentEvent(this, parent, offset,
				2, null));

		this.content.insertString(offset, "\0\0");

		element.setContent(this.content, offset, offset + 1);
		element.setParent(parent);
		parent.insertChild(childIndex, element);

		IUndoableEdit edit = this.undoEnabled ? new InsertElementEdit(offset,
				element) : null;

		this.fireContentInserted(new DocumentEvent(this, parent, offset, 2,
				edit));
	}

	/* (non-Javadoc)
	 * @see org.eclipse.wst.xml.vex.core.internal.dom.IVEXDocument#insertFragment(int, org.eclipse.wst.xml.vex.core.internal.dom.DocumentFragment)
	 * 
	 */
	public void insertFragment(int offset, VEXDocumentFragment fragment)
			throws DocumentValidationException {

		if (offset < 1 || offset >= this.getLength()) {
			throw new IllegalArgumentException(
					"Error inserting document fragment");
		}

		VEXElement parent = this.getElementAt(offset);

		if (this.validator != null) {
			EList<String> seq1 = this.getNodeNames(parent.getStartOffset() + 1,
					offset);
			
			EList<String> seq2 = fragment.getNodeNames();
			EList<String> seq3 = this.getNodeNames(offset, parent.getEndOffset());
			
			if (!validator.isValidSequence(parent.getName(), seq1, seq2, seq3,
					true)) {

				throw new DocumentValidationException(
						"Cannot insert document fragment");
			}
		}

		this.fireBeforeContentInserted(new DocumentEvent(this, parent, offset,
				2, null));

		Content c = fragment.getContent();
		String s = c.getString(0, c.getLength());
		this.content.insertString(offset, s);

		EList<VEXElement> children = parent.getChildElements();
		int index = 0;
		while (index < children.size()
				&& children.get(index).getEndOffset() < offset) {
			index++;
		}

		EList<VEXElement> elements = fragment.getElements();
		for (int i = 0; i < elements.size(); i++) {
			VEXElement newElement = this.cloneElement(elements.get(i), this.content,
					offset, parent);
			parent.insertChild(index, newElement);
			index++;
		}

		IUndoableEdit edit = this.undoEnabled ? new InsertFragmentEdit(offset,
				fragment) : null;

		this.fireContentInserted(new DocumentEvent(this, parent, offset,
				fragment.getContent().getLength(), edit));
	}

	/* (non-Javadoc)
	 * @see org.eclipse.wst.xml.vex.core.internal.dom.IVEXDocument#insertText(int, java.lang.String)
	 * 
	 */
	public void insertText(int offset, String text)
			throws DocumentValidationException {

		if (offset < 1 || offset >= this.getLength()) {
			throw new IllegalArgumentException(
					"Offset must be between 1 and n-1");
		}

		VEXElement parent = this.getElementAt(offset);

		boolean isValid = false;
		if (this.getCharacterAt(offset - 1) != '\0') {
			isValid = true;
		} else if (this.getCharacterAt(offset) != '\0') {
			isValid = true;
		} else {
			Validator validator = this.getValidator();
			if (validator != null) {
				EList<String> seq1 = this.getNodeNames(parent.getStartOffset() + 1,
						offset);
				
				EList<String> seq2 = new BasicEList<String>();
				seq2.add("#PCDATA");
				
				EList<String> seq3 = this
						.getNodeNames(offset, parent.getEndOffset());
				
				isValid = validator.isValidSequence(parent.getName(), seq1,
						seq2, seq3, true);
			} else {
				isValid = true;
			}
		}

		if (!isValid) {
			throw new DocumentValidationException("Cannot insert text '" + text
					+ "' at offset " + offset);
		}

		// Convert control chars to spaces
		StringBuffer sb = new StringBuffer(text);
		for (int i = 0; i < sb.length(); i++) {
			if (Character.isISOControl(sb.charAt(i)) && sb.charAt(i) != '\n') {
				sb.setCharAt(i, ' ');
			}
		}

		String s = sb.toString();

		this.fireBeforeContentInserted(new DocumentEvent(this, parent, offset,
				2, null));

		this.content.insertString(offset, s);

		IUndoableEdit edit = this.undoEnabled ? new InsertTextEdit(offset, s)
				: null;

		this.fireContentInserted(new DocumentEvent(this, parent, offset, s
				.length(), edit));
	}

	/* (non-Javadoc)
	 * @see org.eclipse.wst.xml.vex.core.internal.dom.IVEXDocument#isUndoEnabled()
	 * 
	 */
	public boolean isUndoEnabled() {
		return this.undoEnabled;
	}

	/* (non-Javadoc)
	 * @see org.eclipse.wst.xml.vex.core.internal.dom.IVEXDocument#removeDocumentListener(org.eclipse.wst.xml.vex.core.internal.dom.DocumentListener)
	 * 
	 */
	public void removeDocumentListener(DocumentListener listener) {
		this.listeners.remove(listener);
	}

	/* (non-Javadoc)
	 * @see org.eclipse.wst.xml.vex.core.internal.dom.IVEXDocument#setPublicID(java.lang.String)
	 * 
	 */
//	public void setPublicID(String publicID) {
//		this.publicID = publicID;
//	}

	/* (non-Javadoc)
	 * @see org.eclipse.wst.xml.vex.core.internal.dom.IVEXDocument#setSystemID(java.lang.String)
	 * 
	 */
	public void setSystemID(String systemID) {
		this.systemID = systemID;
	}

	/* (non-Javadoc)
	 * @see org.eclipse.wst.xml.vex.core.internal.dom.IVEXDocument#setUndoEnabled(boolean)
	 * 
	 */
	public void setUndoEnabled(boolean undoEnabled) {
		this.undoEnabled = undoEnabled;
	}

	/* (non-Javadoc)
	 * @see org.eclipse.wst.xml.vex.core.internal.dom.IVEXDocument#setValidator(org.eclipse.wst.xml.vex.core.internal.dom.Validator)
	 * 
	 */
	public void setValidator(Validator validator) {
		this.validator = validator;
	}

	// ==================================================== PRIVATE

	/**
	 * Represents a deletion from a document that can be undone and redone.
	 */
	private class DeleteEdit implements IUndoableEdit {

		private int startOffset;
		private int endOffset;
		private VEXDocumentFragment frag;

		public DeleteEdit(int startOffset, int endOffset, VEXDocumentFragment frag) {
			this.startOffset = startOffset;
			this.endOffset = endOffset;
			this.frag = frag;
		}

		public boolean combine(IUndoableEdit edit) {
			return false;
		}

		public void undo() throws CannotUndoException {
			try {
				setUndoEnabled(false);
				insertFragment(this.startOffset, this.frag);
			} catch (DocumentValidationException ex) {
				throw new CannotUndoException();
			} finally {
				setUndoEnabled(true);
			}
		}

		public void redo() throws CannotRedoException {
			try {
				setUndoEnabled(false);
				delete(this.startOffset, this.endOffset);
			} catch (DocumentValidationException ex) {
				throw new CannotUndoException();
			} finally {
				setUndoEnabled(true);
			}
		}

	}

	/**
	 * Represents an insertion of an element into the document.
	 */
	private class InsertElementEdit implements IUndoableEdit {

		private int offset;
		private VEXElement element;

		public InsertElementEdit(int offset, VEXElement element2) {
			this.offset = offset;
			this.element = element2;
		}

		public boolean combine(IUndoableEdit edit) {
			return false;
		}

		public void undo() throws CannotUndoException {
			try {
				setUndoEnabled(false);
				delete(this.offset, this.offset + 2);
			} catch (DocumentValidationException ex) {
				throw new CannotUndoException();
			} finally {
				setUndoEnabled(true);
			}
		}

		public void redo() throws CannotRedoException {
			try {
				setUndoEnabled(false);
				insertElement(this.offset, this.element);
			} catch (DocumentValidationException ex) {
				throw new CannotUndoException();
			} finally {
				setUndoEnabled(true);
			}
		}

	}

	/**
	 * Represents an insertion of a fragment into the document.
	 */
	private class InsertFragmentEdit implements IUndoableEdit {

		private int offset;
		private VEXDocumentFragment frag;

		public InsertFragmentEdit(int offset, VEXDocumentFragment frag) {
			this.offset = offset;
			this.frag = frag;
		}

		public boolean combine(IUndoableEdit edit) {
			return false;
		}

		public void undo() throws CannotUndoException {
			try {
				setUndoEnabled(false);
				int length = this.frag.getContent().getLength();
				delete(this.offset, this.offset + length);
			} catch (DocumentValidationException ex) {
				throw new CannotUndoException();
			} finally {
				setUndoEnabled(true);
			}
		}

		public void redo() throws CannotRedoException {
			try {
				setUndoEnabled(false);
				insertFragment(this.offset, this.frag);
			} catch (DocumentValidationException ex) {
				throw new CannotUndoException();
			} finally {
				setUndoEnabled(true);
			}
		}

	}

	/**
	 * Represents an insertion of text into the document.
	 */
	private class InsertTextEdit implements IUndoableEdit {

		private int offset;
		private String text;

		public InsertTextEdit(int offset, String text) {
			this.offset = offset;
			this.text = text;
		}

		public boolean combine(IUndoableEdit edit) {
			if (edit instanceof InsertTextEdit) {
				InsertTextEdit ite = (InsertTextEdit) edit;
				if (ite.offset == this.offset + this.text.length()) {
					this.text = this.text + ite.text;
					return true;
				}
			}
			return false;
		}

		public void undo() throws CannotUndoException {
			try {
				setUndoEnabled(false);
				delete(this.offset, this.offset + this.text.length());
			} catch (DocumentValidationException ex) {
				throw new CannotUndoException();
			} finally {
				setUndoEnabled(true);
			}
		}

		public void redo() throws CannotRedoException {
			try {
				setUndoEnabled(false);
				insertText(this.offset, this.text);
			} catch (DocumentValidationException ex) {
				throw new CannotUndoException();
			} finally {
				setUndoEnabled(true);
			}
		}

	}

	/**
	 * Assert that the given offset is within the given range, throwing
	 * IllegalArgumentException if not.
	 */
	private static void assertOffset(int offset, int min, int max) {
		if (offset < min || offset > max) {
			throw new IllegalArgumentException("Bad offset " + offset
					+ "must be between " + min + " and " + max);
		}
	}

	/**
	 * Clone an element tree, pointing to a new Content object.
	 * 
	 * @param original
	 *            Element to be cloned
	 * @param content
	 *            new Content object to which the clone will point
	 * @param shift
	 *            amount to shift offsets to be valid in the new Content.
	 * @param parent
	 *            parent for the cloned Element
	 */
	private VEXElement cloneElement(VEXElement original, Content content, int shift,
			VEXElement parent) {

		Element clone = new Element(original.getName());
		clone.setContent(content, original.getStartOffset() + shift, original
				.getEndOffset()
				+ shift);
		EList<String> attrNames = original.getAttributeNames();
		for (int i = 0; i < attrNames.size(); i++) {
			try {
				clone.setAttribute(attrNames.get(i), original
						.getAttribute(attrNames.get(i)));
			} catch (DocumentValidationException ex) {
				throw new RuntimeException("Unexpected exception: " + ex);
			}
		}
		clone.setParent(parent);

		EList<VEXElement> children = original.getChildElements();
		for (int i = 0; i < children.size(); i++) {
			VEXElement cloneChild = this.cloneElement(children.get(i), content, shift,
					clone);
			clone.insertChild(i, cloneChild);
		}

		return clone;
	}

	public void fireAttributeChanged(DocumentEvent e) {
		this.listeners.fireEvent("attributeChanged", e);
	}

	private void fireBeforeContentDeleted(DocumentEvent e) {
		this.listeners.fireEvent("beforeContentDeleted", e);
	}

	private void fireBeforeContentInserted(DocumentEvent e) {
		this.listeners.fireEvent("beforeContentInserted", e);
	}

	private void fireContentDeleted(DocumentEvent e) {
		this.listeners.fireEvent("contentDeleted", e);
	}

	private void fireContentInserted(DocumentEvent e) {
		this.listeners.fireEvent("contentInserted", e);
	}
	
	@Override
	public void setDOMDocument(org.w3c.dom.Document domDocument) {
		this.domDocument = domDocument;
		synchronizeDocuments();
	}
	
	@Override
	public org.w3c.dom.Document getDOMDocument() {
		return domDocument;
	}
	
	private void synchronizeDocuments() {
		synchronizeRootElement();
	}
	
	private void synchronizeRootElement() {
		rootElement = null;
		org.w3c.dom.Element domRootElement = domDocument.getDocumentElement(); 
		String rootElementName = domRootElement.getNodeName();
		rootElement = new RootElement(rootElementName);
		rootElement.setElement(domRootElement);
		rootElement.setContent(content, 0, 1);
		synchronizeAttributeNodes(rootElement, domRootElement);
		synchronizeChildNodes(rootElement, domRootElement);
	}
	
	private void synchronizeAttributeNodes(VEXElement vexElement, org.w3c.dom.Element domElement) {
		NamedNodeMap domAttrNodes = domElement.getAttributes();
		if (domAttrNodes == null || domAttrNodes.getLength() == 0) {
			return;
		}
		for (int nodeCount = 0; nodeCount < domAttrNodes.getLength(); nodeCount++ ) {
			Attr attrNode = (Attr)domAttrNodes.item(nodeCount);
			String attrName = attrNode.getName();
			String attrValue = attrNode.getValue();
			vexElement.setAttribute(attrName, attrValue);
		}
	}
	
	private void synchronizeChildNodes(VEXElement vexElement, org.w3c.dom.Element domElement) {
		NodeList domNodes = domElement.getChildNodes();
		if (domNodes.getLength() > 0) {
			for (int nodeCount = 0; nodeCount < domNodes.getLength(); nodeCount++) {
				org.w3c.dom.Node domNode = domNodes.item(nodeCount);
				if (domNode.getNodeType() == org.w3c.dom.Node.ELEMENT_NODE) {
					VEXElement element = new Element(domNode.getNodeName());
					synchronizeChildNodes(element, (org.w3c.dom.Element) domNode);
					synchronizeAttributeNodes(element, (org.w3c.dom.Element) domNode);
					element.setElement((org.w3c.dom.Element) domNode);
					vexElement.addChild(element);
				}
				if (domNode.getNodeType() == org.w3c.dom.Node.TEXT_NODE) {
					int offset = content.getLength();
					String text = domNode.getNodeValue();
					content.insertString(this.content.getLength(), domNode.getNodeValue());
					content.insertString(content.getLength(), "\0");
					vexElement.setContent(content, offset, content.getLength() - 1);
				}
			}
		}
	}

}