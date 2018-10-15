private static class UndoableAndOffset {

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
package org.eclipse.wst.xml.vex.core.internal.widget;

import java.io.IOException;
import java.net.URL;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;

import javax.xml.parsers.ParserConfigurationException;

import org.eclipse.emf.common.util.BasicEList;
import org.eclipse.emf.common.util.EList;
import org.eclipse.wst.xml.vex.core.internal.core.Caret;
import org.eclipse.wst.xml.vex.core.internal.core.Color;
import org.eclipse.wst.xml.vex.core.internal.core.Graphics;
import org.eclipse.wst.xml.vex.core.internal.core.IntRange;
import org.eclipse.wst.xml.vex.core.internal.core.Rectangle;
import org.eclipse.wst.xml.vex.core.internal.css.CSS;
import org.eclipse.wst.xml.vex.core.internal.css.StyleSheet;
import org.eclipse.wst.xml.vex.core.internal.css.StyleSheetReader;
import org.eclipse.wst.xml.vex.core.internal.css.Styles;
import org.eclipse.wst.xml.vex.core.internal.dom.Document;
import org.eclipse.wst.xml.vex.core.internal.dom.DocumentEvent;
import org.eclipse.wst.xml.vex.core.internal.dom.DocumentListener;
import org.eclipse.wst.xml.vex.core.internal.dom.DocumentReader;
import org.eclipse.wst.xml.vex.core.internal.dom.DocumentValidationException;
import org.eclipse.wst.xml.vex.core.internal.dom.Element;
import org.eclipse.wst.xml.vex.core.internal.layout.BlockBox;
import org.eclipse.wst.xml.vex.core.internal.layout.Box;
import org.eclipse.wst.xml.vex.core.internal.layout.BoxFactory;
import org.eclipse.wst.xml.vex.core.internal.layout.CssBoxFactory;
import org.eclipse.wst.xml.vex.core.internal.layout.LayoutContext;
import org.eclipse.wst.xml.vex.core.internal.layout.RootBox;
import org.eclipse.wst.xml.vex.core.internal.provisional.dom.I.Position;
import org.eclipse.wst.xml.vex.core.internal.provisional.dom.I.VEXDocument;
import org.eclipse.wst.xml.vex.core.internal.provisional.dom.I.VEXDocumentFragment;
import org.eclipse.wst.xml.vex.core.internal.provisional.dom.I.VEXElement;
import org.eclipse.wst.xml.vex.core.internal.provisional.dom.I.Validator;
import org.eclipse.wst.xml.vex.core.internal.provisional.dom.IWhitespacePolicy;
import org.eclipse.wst.xml.vex.core.internal.provisional.dom.IWhitespacePolicyFactory;
import org.eclipse.wst.xml.vex.core.internal.undo.CannotRedoException;
import org.eclipse.wst.xml.vex.core.internal.undo.CannotUndoException;
import org.eclipse.wst.xml.vex.core.internal.undo.CompoundEdit;
import org.eclipse.wst.xml.vex.core.internal.undo.IUndoableEdit;
import org.xml.sax.SAXException;

/**
 * A component that allows the display and edit of an XML document with an
 * associated CSS stylesheet.
 */
public class VexWidgetImpl implements IVexWidget {

	/**
	 * Number of pixel rows above and below the caret that are rendered at a
	 * time.
	 */
	private static final int LAYOUT_WINDOW = 5000;

	/**
	 * Because the height of each BlockElementBox is initially estimated, we
	 * sometimes have to try several times before the band being laid out is
	 * properly positioned about the offset. When the position of the offset
	 * changes by less than this amount between subsequent layout calls, the
	 * layout is considered stable.
	 */
	private static final int LAYOUT_TOLERANCE = 500;

	/**
	 * Minimum layout width, in pixels. Prevents performance problems when width
	 * is very small.
	 */
	private static final int MIN_LAYOUT_WIDTH = 200;

	private boolean debugging;

	private HostComponent hostComponent;
	private int layoutWidth = 500; // something reasonable to handle a document
	// being set before the widget is sized

	private VEXDocument document;
	private StyleSheet styleSheet;
	private BoxFactory boxFactory = new CssBoxFactory();

	private RootBox rootBox;

	/** Stacks of UndoableEditEvents; items added and removed from end of list */
	private LinkedList undoList = new LinkedList();
	private LinkedList redoList = new LinkedList();
	private static final int MAX_UNDO_STACK_SIZE = 100;
	private int undoDepth;

	/** Support for beginWork/endWork */
	private int beginWorkCount = 0;
	private int beginWorkCaretOffset;
	private CompoundEdit compoundEdit;

	private int caretOffset;
	private int mark;
	private int selectionStart;
	private int selectionEnd;

	private VEXElement currentElement;

	private boolean caretVisible = true;
	private Caret caret;
	private Color caretColor;

	// x offset to be maintained when moving vertically
	private int magicX = -1;

	private boolean antiAliased = false;

	// ======================================================= LISTENERS

	private DocumentListener documentListener = new DocumentListener() {

		public void attributeChanged(DocumentEvent e) {
			invalidateElementBox(e.getParentElement());

			// flush cached styles, since they might depend attribute values
			// via conditional selectors
			getStyleSheet().flushStyles(e.getParentElement());

			if (beginWorkCount == 0) {
				VexWidgetImpl.this.relayout();
			}

			addEdit(e.getUndoableEdit(), getCaretOffset());
			hostComponent.fireSelectionChanged();
		}

		public void beforeContentDeleted(DocumentEvent e) {
		}

		public void beforeContentInserted(DocumentEvent e) {
		}

		public void contentDeleted(DocumentEvent e) {
			invalidateElementBox(e.getParentElement());

			if (beginWorkCount == 0) {
				VexWidgetImpl.this.relayout();
			}

			addEdit(e.getUndoableEdit(), getCaretOffset());
		}

		public void contentInserted(DocumentEvent e) {
			invalidateElementBox(e.getParentElement());

			if (beginWorkCount == 0) {
				VexWidgetImpl.this.relayout();
			}

			addEdit(e.getUndoableEdit(), getCaretOffset());
		}

	};

	// ======================================================= PUBLIC INTERFACE

	/**
	 * Class constructor.
	 */
	public VexWidgetImpl(HostComponent hostComponent) {
		this.hostComponent = hostComponent;
	}

	public void beginWork() {
		if (this.beginWorkCount == 0) {
			this.beginWorkCaretOffset = this.getCaretOffset();
			this.compoundEdit = new CompoundEdit();
		}
		this.beginWorkCount++;
	}

	/**
	 * Returns true if the given fragment can be inserted at the current caret
	 * position.
	 * 
	 * @param frag
	 *            DocumentFragment to be inserted.
	 */
	public boolean canInsertFragment(VEXDocumentFragment frag) {

		VEXDocument doc = this.getDocument();
		if (doc == null) {
			return false;
		}

		Validator validator = doc.getValidator();
		if (validator == null) {
			return true;
		}

		int startOffset = this.getCaretOffset();
		int endOffset = this.getCaretOffset();
		if (this.hasSelection()) {
			startOffset = this.getSelectionStart();
			endOffset = this.getSelectionEnd();
		}

		VEXElement parent = this.getDocument().getElementAt(startOffset);
		EList<String> seq1 = doc.getNodeNames(parent.getStartOffset() + 1,
				startOffset);

		EList<String> seq2 = frag.getNodeNames();
		
		EList<String> seq3 = doc.getNodeNames(endOffset, parent.getEndOffset());


		return validator.isValidSequence(parent.getName(), seq1, seq2, seq3,
				true);
	}

	/**
	 * Returns true if text can be inserted at the current position.
	 */
	public boolean canInsertText() {

		VEXDocument doc = this.getDocument();
		if (doc == null) {
			return false;
		}

		Validator validator = this.document.getValidator();
		if (validator == null) {
			return true;
		}

		int startOffset = this.getCaretOffset();
		int endOffset = this.getCaretOffset();
		if (this.hasSelection()) {
			startOffset = this.getSelectionStart();
			endOffset = this.getSelectionEnd();
		}

		VEXElement parent = this.getDocument().getElementAt(startOffset);
		EList<String> seq1 = doc.getNodeNames(parent.getStartOffset() + 1,
				startOffset);

		EList<String> seq2 = new BasicEList<String>();
		seq2.add(Validator.PCDATA);
		
		EList<String> seq3 = doc.getNodeNames(endOffset, parent.getEndOffset());


		return validator.isValidSequence(parent.getName(), seq1, seq2, seq3,
				true);
	}

	public boolean canPaste() {
		throw new UnsupportedOperationException(
				"Must be implemented in tookit-specific widget.");
	}

	public boolean canPasteText() {
		throw new UnsupportedOperationException(
				"Must be implemented in tookit-specific widget.");
	}

	public boolean canRedo() {
		return this.redoList.size() > 0;
	}

	public boolean canUndo() {
		return this.undoList.size() > 0;
	}

	public boolean canUnwrap() {
		VEXDocument doc = this.getDocument();
		if (doc == null) {
			return false;
		}

		Validator validator = doc.getValidator();
		if (validator == null) {
			return false;
		}

		VEXElement element = doc.getElementAt(this.getCaretOffset());
		VEXElement parent = element.getParent();
		if (parent == null) {
			// can't unwrap the root
			return false;
		}

		EList<String> seq1 = doc.getNodeNames(parent.getStartOffset() + 1, element
				.getStartOffset());
		
		EList<String> seq2 = doc.getNodeNames(element.getStartOffset() + 1, element
				.getEndOffset());

		EList<String> seq3 = doc.getNodeNames(element.getEndOffset() + 1, parent
				.getEndOffset());


		return validator.isValidSequence(parent.getName(), seq1, seq2, seq3,
				true);
	}

	public void copySelection() {
		throw new UnsupportedOperationException(
				"Must be implemented in tookit-specific widget.");
	}

	public void cutSelection() {
		throw new UnsupportedOperationException(
				"Must be implemented in tookit-specific widget.");
	}

	public void deleteNextChar() throws DocumentValidationException {
		if (this.hasSelection()) {
			this.deleteSelection();
		} else {
			int offset = this.getCaretOffset();
			VEXDocument doc = this.getDocument();
			int n = doc.getLength() - 1;
			VEXElement element = doc.getElementAt(offset);

			if (offset == n) {
				// nop
			} else if (this.isBetweenMatchingElements(offset)) {
				this.joinElementsAt(offset);
			} else if (this.isBetweenMatchingElements(offset + 1)) {
				this.joinElementsAt(offset + 1);
			} else if (element.isEmpty()) {
				// deleting the right sentinel of an empty element
				// so just delete the whole element an move on
				this.moveTo(offset - 1, false);
				this.moveTo(offset + 1, true);
				this.deleteSelection();
			} else if (doc.getElementAt(offset + 1).isEmpty()) {
				// deleting the left sentinel of an empty element
				// so just delete the whole element an move on
				this.moveTo(offset + 2, true);
				this.deleteSelection();
			} else {
				if (doc.getCharacterAt(offset) != 0) {
					this.moveTo(offset, false);
					this.moveTo(offset + 1, true);
					this.deleteSelection();
				}
			}
		}
	}

	public void deletePreviousChar() throws DocumentValidationException {

		if (this.hasSelection()) {
			this.deleteSelection();
		} else {
			int offset = this.getCaretOffset();
			VEXDocument doc = this.getDocument();
			VEXElement element = doc.getElementAt(offset);

			if (offset == 1) {
				// nop
			} else if (this.isBetweenMatchingElements(offset)) {
				this.joinElementsAt(offset);
			} else if (this.isBetweenMatchingElements(offset - 1)) {
				this.joinElementsAt(offset - 1);
			} else if (element.isEmpty()) {
				// deleting the left sentinel of an empty element
				// so just delete the whole element an move on
				this.moveTo(offset - 1, false);
				this.moveTo(offset + 1, true);
				this.deleteSelection();
			} else if (doc.getElementAt(offset - 1).isEmpty()) {
				// deleting the right sentinel of an empty element
				// so just delete the whole element an move on
				this.moveTo(offset - 2, true);
				this.deleteSelection();
			} else {
				offset--;
				if (doc.getCharacterAt(offset) != 0) {
					this.moveTo(offset, false);
					this.moveTo(offset + 1, true);
					this.deleteSelection();
				}
			}
		}

	}

	public void deleteSelection() {
		try {
			if (this.hasSelection()) {
				this.document.delete(this.getSelectionStart(), this
						.getSelectionEnd());
				this.moveTo(this.getSelectionStart());
			}
		} catch (DocumentValidationException ex) {
			ex.printStackTrace(); // This should never happen, because we
			// constrain the selection
		}
	}

	public void doWork(Runnable runnable) {
		this.doWork(false, runnable);
	}

	public void doWork(boolean savePosition, Runnable runnable) {
		Position position = null;

		if (savePosition) {
			position = this.getDocument().createPosition(this.getCaretOffset());
		}

		boolean success = false;
		try {
			this.beginWork();
			runnable.run();
			success = true;
		} catch (Exception ex) {
			ex.printStackTrace();
		} finally {
			this.endWork(success);
			if (position != null) {
				this.moveTo(position.getOffset());
			}
		}
	}

	public void endWork(boolean success) {
		this.beginWorkCount--;
		if (this.beginWorkCount == 0) {
			// this.compoundEdit.end();
			if (success) {
				this.undoList.add(new UndoableAndOffset(this.compoundEdit,
						this.beginWorkCaretOffset));
				this.undoDepth++;
				if (undoList.size() > MAX_UNDO_STACK_SIZE) {
					undoList.removeFirst();
				}
				this.redoList.clear();
				this.relayout();
				this.hostComponent.fireSelectionChanged();
			} else {
				try {
					this.compoundEdit.undo();
					this.moveTo(this.beginWorkCaretOffset);
				} catch (CannotUndoException e) {
					// TODO: handle exception
				}
			}
			this.compoundEdit = null;
		}
	}

	public Box findInnermostBox(IBoxFilter filter) {
		return this.findInnermostBox(filter, this.getCaretOffset());
	}

	/**
	 * Returns the innermost box containing the given offset that matches the
	 * given filter.
	 * 
	 * @param filter
	 *            IBoxFilter that determines which box to return
	 * @param offset
	 *            Document offset around which to search.
	 */
	private Box findInnermostBox(IBoxFilter filter, int offset) {

		Box box = this.rootBox.getChildren()[0];
		Box matchingBox = null;

		for (;;) {
			if (filter.matches(box)) {
				matchingBox = box;
			}

			Box original = box;
			Box[] children = box.getChildren();
			for (int i = 0; i < children.length; i++) {

				Box child = children[i];

				if (child.hasContent() && offset >= child.getStartOffset()
						&& offset <= child.getEndOffset()) {
					box = child;
					break;
				}
			}

			if (box == original) {
				// No child found containing offset,
				// so just return the latest match.
				return matchingBox;
			}
		}

	}

	/**
	 * Returns the background color for the control, which is the same as the
	 * background color of the root element.
	 */
	public Color getBackgroundColor() {
		return this.styleSheet.getStyles(this.document.getRootElement())
				.getBackgroundColor();
	}

	public BoxFactory getBoxFactory() {
		return this.boxFactory;
	}

	/**
	 * Returns the current caret.
	 */
	public Caret getCaret() {
		return this.caret;
	}

	public int getCaretOffset() {
		return this.caretOffset;
	}

	public VEXElement getCurrentElement() {
		return this.currentElement;
	}

	public VEXDocument getDocument() {
		return this.document;
	}

	/**
	 * Returns the natural height of the widget based on the current layout
	 * width.
	 */
	public int getHeight() {
		return this.rootBox.getHeight();
	}

	public String[] getValidInsertElements() {

		VEXDocument doc = this.getDocument();
		if (doc == null) {
			return new String[0];
		}

		Validator validator = doc.getValidator();
		if (validator == null) {
			return new String[0];
		}

		int startOffset = this.getCaretOffset();
		int endOffset = this.getCaretOffset();
		if (this.hasSelection()) {
			startOffset = this.getSelectionStart();
			endOffset = this.getSelectionEnd();
		}

		VEXElement parent = doc.getElementAt(startOffset);
//		List<String> prefix = doc.getNodeNames(parent.getStartOffset() + 1,
//				startOffset);
//		List<String> suffix = doc.getNodeNames(endOffset, parent.getEndOffset());
		
		
		List candidates = new ArrayList();
		candidates.addAll(validator.getValidItems(parent.getName()));
		candidates.remove(Validator.PCDATA);

		// If there's a selection, root out those candidates that can't
		// contain it.
		if (this.hasSelection()) {
			EList<String> selectedNodes = doc.getNodeNames(startOffset, endOffset);

			for (Iterator iter = candidates.iterator(); iter.hasNext();) {
				String candidate = (String) iter.next();
				if (!validator.isValidSequence(candidate, selectedNodes, true)) {
					iter.remove();
				}
			}
		}

		Collections.sort(candidates);
		return (String[]) candidates.toArray(new String[candidates.size()]);
	}

	/**
	 * Returns the value of the antiAliased flag.
	 */
	public boolean isAntiAliased() {
		return this.antiAliased;
	}

	public boolean isDebugging() {
		return debugging;
	}

	public String[] getValidMorphElements() {

		VEXDocument doc = this.getDocument();
		if (doc == null) {
			return new String[0];
		}

		Validator validator = doc.getValidator();
		if (validator == null) {
			return new String[0];
		}

		VEXElement element = doc.getElementAt(this.getCaretOffset());
		VEXElement parent = element.getParent();
		if (parent == null) {
			// can't morph the root
			return new String[0];
		}

		List<String> listprefix = doc.getNodeNames(parent.getStartOffset() + 1, element
				.getStartOffset());
		String[] prefix = new String[listprefix.size()];
		listprefix.toArray(prefix);

		
//		List<String> listsuffix = doc.getNodeNames(element.getEndOffset() + 1, parent
//				.getEndOffset());
//		String[] suffix = new String[listsuffix.size()];
//		listprefix.toArray(suffix);
		

		List candidates = new ArrayList();
		candidates.addAll(validator.getValidItems(parent.getName()));
		candidates.remove(Validator.PCDATA);

		// root out those that can't contain the current content
		EList<String> content = doc.getNodeNames(element.getStartOffset() + 1,
				element.getEndOffset());
		
		for (Iterator iter = candidates.iterator(); iter.hasNext();) {
			String candidate = (String) iter.next();
			if (!validator.isValidSequence(candidate, content, true)) {
				iter.remove();
			}
		}

		Collections.sort(candidates);
		return (String[]) candidates.toArray(new String[candidates.size()]);
	}

	public int getSelectionEnd() {
		return this.selectionEnd;
	}

	public int getSelectionStart() {
		return this.selectionStart;
	}

	public VEXDocumentFragment getSelectedFragment() {
		if (this.hasSelection()) {
			return this.document.getFragment(this.getSelectionStart(), this
					.getSelectionEnd());
		} else {
			return null;
		}
	}

	public String getSelectedText() {
		if (this.hasSelection()) {
			return this.document.getText(this.getSelectionStart(), this
					.getSelectionEnd());
		} else {
			return "";
		}
	}

	public StyleSheet getStyleSheet() {
		return this.styleSheet;
	}

	public int getUndoDepth() {
		return this.undoDepth;
	}

	public int getLayoutWidth() {
		return this.layoutWidth;
	}

	public RootBox getRootBox() {
		return this.rootBox;
	}

	public boolean hasSelection() {
		return this.getSelectionStart() != this.getSelectionEnd();
	}

	public void insertChar(char c) throws DocumentValidationException {
		if (this.hasSelection()) {
			this.deleteSelection();
		}
		this.document.insertText(this.getCaretOffset(), Character.toString(c));
		this.moveBy(+1);
	}

	public void insertFragment(VEXDocumentFragment frag)
			throws DocumentValidationException {

		if (this.hasSelection()) {
			this.deleteSelection();
		}

		this.document.insertFragment(this.getCaretOffset(), frag);
		this.moveTo(this.getCaretOffset() + frag.getLength());
	}

	public void insertElement(Element element)
			throws DocumentValidationException {

		boolean success = false;
		try {
			this.beginWork();

			VEXDocumentFragment frag = null;
			if (this.hasSelection()) {
				frag = this.getSelectedFragment();
				this.deleteSelection();
			}

			this.document.insertElement(this.getCaretOffset(), element);
			this.moveTo(this.getCaretOffset() + 1);
			if (frag != null) {
				this.insertFragment(frag);
			}
			this.scrollCaretVisible();
			success = true;
		} finally {
			this.endWork(success);
		}
	}

	public void insertText(String text) throws DocumentValidationException {

		if (this.hasSelection()) {
			this.deleteSelection();
		}

		boolean success = false;
		try {
			this.beginWork();
			int i = 0;
			for (;;) {
				int j = text.indexOf('\n', i);
				if (j == -1) {
					break;
				}
				this.document.insertText(this.getCaretOffset(), text.substring(
						i, j));
				this.moveTo(this.getCaretOffset() + (j - i));
				this.split();
				i = j + 1;
			}

			if (i < text.length()) {
				this.document.insertText(this.getCaretOffset(), text
						.substring(i));
				this.moveTo(this.getCaretOffset() + (text.length() - i));
			}
			success = true;
		} finally {
			this.endWork(success);
		}
	}

	public void morph(Element element) throws DocumentValidationException {

		VEXDocument doc = this.getDocument();
		int offset = this.getCaretOffset();
		VEXElement currentElement = doc.getElementAt(offset);

		if (currentElement == doc.getRootElement()) {
			throw new DocumentValidationException(
					"Cannot morph the root element.");
		}

		boolean success = false;
		try {
			this.beginWork();
			this.moveTo(currentElement.getStartOffset() + 1, false);
			this.moveTo(currentElement.getEndOffset(), true);
			VEXDocumentFragment frag = this.getSelectedFragment();
			this.deleteSelection();
			this.moveBy(-1, false);
			this.moveBy(2, true);
			this.deleteSelection();
			this.insertElement(element);
			if (frag != null) {
				this.insertFragment(frag);
			}
			this.moveTo(offset, false);
			success = true;
		} finally {
			this.endWork(success);
		}

	}

	public void moveBy(int distance) {
		this.moveTo(this.getCaretOffset() + distance, false);
	}

	public void moveBy(int distance, boolean select) {
		this.moveTo(this.getCaretOffset() + distance, select);
	}

	public void moveTo(int offset) {
		this.moveTo(offset, false);
	}

	public void moveTo(int offset, boolean select) {

		if (offset >= 1 && offset <= this.document.getLength() - 1) {

			// repaint the selection area, if any
			this.repaintCaret();
			this.repaintRange(this.getSelectionStart(), this.getSelectionEnd());

			VEXElement oldElement = this.currentElement;

			this.caretOffset = offset;

			this.currentElement = this.document.getElementAt(offset);

			if (select) {
				this.selectionStart = Math.min(this.mark, this.caretOffset);
				this.selectionEnd = Math.max(this.mark, this.caretOffset);

				// move selectionStart and selectionEnd to make sure we don't
				// select a partial element
				VEXElement commonElement = this.document.findCommonElement(
						this.selectionStart, this.selectionEnd);

				VEXElement element = this.document
						.getElementAt(this.selectionStart);
				while (element != commonElement) {
					this.selectionStart = element.getStartOffset();
					element = this.document.getElementAt(this.selectionStart);
				}

				element = this.document.getElementAt(this.selectionEnd);
				while (element != commonElement) {
					this.selectionEnd = element.getEndOffset() + 1;
					element = this.document.getElementAt(this.selectionEnd);
				}

			} else {
				this.mark = offset;
				this.selectionStart = offset;
				this.selectionEnd = offset;
			}

			if (this.beginWorkCount == 0) {
				this.relayout();
			}

			Graphics g = this.hostComponent.createDefaultGraphics();
			LayoutContext context = this.createLayoutContext(g);
			this.caret = this.rootBox.getCaret(context, offset);

			VEXElement element = this.getCurrentElement();
			if (element != oldElement) {
				this.caretColor = Color.BLACK;
				while (element != null) {
					Color bgColor = this.styleSheet.getStyles(element)
							.getBackgroundColor();
					if (bgColor != null) {
						int red = ~bgColor.getRed() & 0xff;
						int green = ~bgColor.getGreen() & 0xff;
						int blue = ~bgColor.getBlue() & 0xff;
						this.caretColor = new Color(red, green, blue);
						break;
					}
					element = element.getParent();
				}
			}

			g.dispose();

			this.magicX = -1;

			this.scrollCaretVisible();

			this.hostComponent.fireSelectionChanged();

			this.caretVisible = true;

			this.repaintRange(this.getSelectionStart(), this.getSelectionEnd());
		}
	}

	public void moveToLineEnd(boolean select) {
		this.moveTo(this.rootBox.getLineEndOffset(this.getCaretOffset()),
				select);
	}

	public void moveToLineStart(boolean select) {
		this.moveTo(this.rootBox.getLineStartOffset(this.getCaretOffset()),
				select);
	}

	public void moveToNextLine(boolean select) {
		int x = this.magicX == -1 ? this.caret.getBounds().getX() : this.magicX;

		Graphics g = this.hostComponent.createDefaultGraphics();
		int offset = this.rootBox.getNextLineOffset(
				this.createLayoutContext(g), this.getCaretOffset(), x);
		g.dispose();

		this.moveTo(offset, select);
		this.magicX = x;
	}

	public void moveToNextPage(boolean select) {
		int x = this.magicX == -1 ? this.caret.getBounds().getX() : this.magicX;
		int y = this.caret.getY()
				+ Math
						.round(this.hostComponent.getViewport().getHeight() * 0.9f);
		this.moveTo(this.viewToModel(x, y), select);
		this.magicX = x;
	}

	public void moveToNextWord(boolean select) {
		VEXDocument doc = this.getDocument();
		int n = doc.getLength() - 1;
		int offset = this.getCaretOffset();
		while (offset < n
				&& !Character.isLetterOrDigit(doc.getCharacterAt(offset))) {
			offset++;
		}

		while (offset < n
				&& Character.isLetterOrDigit(doc.getCharacterAt(offset))) {
			offset++;
		}

		this.moveTo(offset, select);
	}

	public void moveToPreviousLine(boolean select) {
		int x = this.magicX == -1 ? this.caret.getBounds().getX() : this.magicX;

		Graphics g = this.hostComponent.createDefaultGraphics();
		int offset = this.rootBox.getPreviousLineOffset(this
				.createLayoutContext(g), this.getCaretOffset(), x);
		g.dispose();

		this.moveTo(offset, select);
		this.magicX = x;
	}

	public void moveToPreviousPage(boolean select) {
		int x = this.magicX == -1 ? this.caret.getBounds().getX() : this.magicX;
		int y = this.caret.getY()
				- Math
						.round(this.hostComponent.getViewport().getHeight() * 0.9f);
		this.moveTo(this.viewToModel(x, y), select);
		this.magicX = x;
	}

	public void moveToPreviousWord(boolean select) {
		VEXDocument doc = this.getDocument();
		int offset = this.getCaretOffset();
		while (offset > 1
				&& !Character.isLetterOrDigit(doc.getCharacterAt(offset - 1))) {
			offset--;
		}

		while (offset > 1
				&& Character.isLetterOrDigit(doc.getCharacterAt(offset - 1))) {
			offset--;
		}

		this.moveTo(offset, select);
	}

	/**
	 * Paints the contents of the widget in the given Graphics at the given
	 * point.
	 * 
	 * @param g
	 *            Graphics in which to draw the widget contents
	 * @param x
	 *            x-coordinate at which to draw the widget
	 * @param y
	 *            y-coordinate at which to draw the widget
	 */
	public void paint(Graphics g, int x, int y) {

		if (this.rootBox == null) {
			return;
		}

		LayoutContext context = this.createLayoutContext(g);

		// Since we may be scrolling to sections of the document that have
		// yet to be layed out, lay out any exposed area.
		//
		// TODO: this will probably be inaccurate, since we should really
		// iterate the layout, but we don't have an offset around which
		// to iterate...what to do, what to do....
		Rectangle rect = g.getClipBounds();
		int oldHeight = this.rootBox.getHeight();
		this.rootBox.layout(context, rect.getY(), rect.getY()
				+ rect.getHeight());
		if (this.rootBox.getHeight() != oldHeight) {
			this.hostComponent.setPreferredSize(this.rootBox.getWidth(),
					this.rootBox.getHeight());
		}

		this.rootBox.paint(context, 0, 0);
		if (this.caretVisible) {
			this.caret.draw(g, this.caretColor);
		}

		// Debug hash marks
		/*
		 * ColorResource grey = g.createColor(new Color(160, 160, 160));
		 * ColorResource oldColor = g.setColor(grey); for (int y2 = rect.getY()
		 * - rect.getY() % 50; y2 < rect.getY() + rect.getHeight(); y2 += 50) {
		 * g.drawLine(x, y + y2, x+10, y + y2);
		 * g.drawString(Integer.toString(y2), x + 15, y + y2 - 10); }
		 * g.setColor(oldColor); grey.dispose();
		 */
	}

	public void paste() throws DocumentValidationException {
		throw new UnsupportedOperationException(
				"Must be implemented in tookit-specific widget.");
	}

	public void pasteText() throws DocumentValidationException {
		throw new UnsupportedOperationException(
				"Must be implemented in tookit-specific widget.");
	}

	public void redo() {
		if (redoList.size() == 0) {
			throw new CannotRedoException();
		}
		UndoableAndOffset event = (UndoableAndOffset) redoList.removeLast();
		this.moveTo(event.caretOffset, false);
		event.edit.redo();
		this.undoList.add(event);
		undoDepth++;
	}

	public void removeAttribute(String attributeName) {
		try {
			VEXElement element = this.getCurrentElement();
			if (element.getAttribute(attributeName) != null) {
				element.removeAttribute(attributeName);
			}
		} catch (DocumentValidationException ex) {
			ex.printStackTrace(); // TODO: when can this happen?
		}
	}

	public void savePosition(Runnable runnable) {
		Position pos = this.getDocument().createPosition(this.getCaretOffset());
		try {
			runnable.run();
		} finally {
			this.moveTo(pos.getOffset());
		}
	}

	public void selectAll() {
		this.moveTo(1);
		this.moveTo(this.getDocument().getLength() - 1, true);
	}

	public void selectWord() {
		VEXDocument doc = this.getDocument();
		int startOffset = this.getCaretOffset();
		int endOffset = this.getCaretOffset();
		while (startOffset > 1
				&& Character.isLetterOrDigit(doc
						.getCharacterAt(startOffset - 1))) {
			startOffset--;
		}
		int n = doc.getLength() - 1;
		while (endOffset < n
				&& Character.isLetterOrDigit(doc.getCharacterAt(endOffset))) {
			endOffset++;
		}

		if (startOffset < endOffset) {
			this.moveTo(startOffset, false);
			this.moveTo(endOffset, true);
		}
	}

	/**
	 * Sets the value of the antiAliased flag.
	 * 
	 * @param antiAliased
	 *            if true, text is rendered using antialiasing.
	 */
	public void setAntiAliased(boolean antiAliased) {
		this.antiAliased = antiAliased;
	}

	public void setAttribute(String attributeName, String value) {
		try {
			VEXElement element = this.getCurrentElement();
			if (value == null) {
				this.removeAttribute(attributeName);
			} else if (!value.equals(element.getAttribute(attributeName))) {
				element.setAttribute(attributeName, value);
			}
		} catch (DocumentValidationException ex) {
			ex.printStackTrace(); // TODO: mebbe throw the exception instead
		}
	}

	public void setBoxFactory(BoxFactory boxFactory) {
		this.boxFactory = boxFactory;
		if (this.document != null) {
			this.relayout();
		}
	}

	public void setDebugging(boolean debugging) {
		this.debugging = debugging;
	}

	public void setDocument(VEXDocument document, StyleSheet styleSheet) {
		if (this.document != null) {
			Document doc = (Document)document;
			doc.removeDocumentListener(this.documentListener);
		}

		this.document = document;
		this.styleSheet = styleSheet;

		this.undoList = new LinkedList();
		this.undoDepth = 0;
		this.redoList = new LinkedList();
		this.beginWorkCount = 0;
		this.compoundEdit = null;

		this.createRootBox();

		this.moveTo(1);
		((Document)this.document).addDocumentListener(this.documentListener);
	}

	public void setDocument(URL docUrl, URL ssURL) throws IOException,
			ParserConfigurationException, SAXException {

		StyleSheetReader ssReader = new StyleSheetReader();
		final StyleSheet ss = ssReader.read(ssURL);

		DocumentReader reader = new DocumentReader();

		reader.setWhitespacePolicyFactory(new IWhitespacePolicyFactory() {
			public IWhitespacePolicy getPolicy(String publicId) {
				return new CssWhitespacePolicy(ss);
			}
		});

		VEXDocument doc = reader.read(docUrl);
		this.setDocument(doc, ss);
	}

	/**
	 * Called by the host component when it gains or loses focus.
	 * 
	 * @param focus
	 *            true if the host component has focus
	 */
	public void setFocus(boolean focus) {
		this.caretVisible = true;
		this.repaintCaret();
	}

	public void setLayoutWidth(int width) {
		width = Math.max(width, MIN_LAYOUT_WIDTH);
		if (this.getDocument() != null && width != this.getLayoutWidth()) {
			// this.layoutWidth is set by relayoutAll
			this.relayoutAll(width, this.styleSheet);
		} else {
			// maybe doc is null. Let's store layoutWidth so it's right
			// when we set a doc
			this.layoutWidth = width;
		}
	}

	public void setStyleSheet(StyleSheet styleSheet) {
		if (this.getDocument() != null) {
			this.relayoutAll(this.layoutWidth, styleSheet);
		}
	}

	public void setStyleSheet(URL ssUrl) throws IOException {
		StyleSheetReader reader = new StyleSheetReader();
		StyleSheet ss = reader.read(ssUrl);
		this.setStyleSheet(ss);
	}

	public void split() throws DocumentValidationException {

		long start = System.currentTimeMillis();

		VEXDocument doc = this.getDocument();
		VEXElement element = doc.getElementAt(this.getCaretOffset());
		Styles styles = this.getStyleSheet().getStyles(element);
		while (!styles.isBlock()) {
			element = element.getParent();
			styles = this.getStyleSheet().getStyles(element);
		}

		boolean success = false;
		try {
			this.beginWork();
			if (styles.getWhiteSpace().equals(CSS.PRE)) {
				// can't call this.insertText() or we'll get an infinite loop
				int offset = this.getCaretOffset();
				doc.insertText(offset, "\n");
				this.moveTo(offset + 1);
			} else {
				VEXDocumentFragment frag = null;
				int offset = this.getCaretOffset();
				boolean atEnd = (offset == element.getEndOffset());
				if (!atEnd) {
					this.moveTo(element.getEndOffset(), true);
					frag = this.getSelectedFragment();
					this.deleteSelection();
				}

				// either way, we are now at the end offset for the element
				// let's move just outside
				this.moveTo(this.getCaretOffset() + 1);

				this.insertElement(new Element(element.getName()));
				// TODO: clone attributes

				if (!atEnd) {
					offset = this.getCaretOffset();
					this.insertFragment(frag);
					this.moveTo(offset, false);
				}
			}
			success = true;
		} finally {
			this.endWork(success);
		}

		if (this.isDebugging()) {
			long end = System.currentTimeMillis();
			System.out.println("split() took " + (end - start) + "ms");
		}
	}

	/**
	 * Toggles the caret to produce a flashing caret effect. This method should
	 * be called from the GUI event thread at regular intervals.
	 */
	public void toggleCaret() {
		this.caretVisible = !this.caretVisible;
		this.repaintCaret();
	}

	public void undo() {
		if (undoList.size() == 0) {
			throw new CannotUndoException();
		}
		UndoableAndOffset event = (UndoableAndOffset) undoList.removeLast();
		this.undoDepth--;
		event.edit.undo();
		this.moveTo(event.caretOffset, false);
		this.redoList.add(event);
	}

	public int viewToModel(int x, int y) {
		Graphics g = this.hostComponent.createDefaultGraphics();
		LayoutContext context = this.createLayoutContext(g);
		int offset = this.rootBox.viewToModel(context, x, y);
		g.dispose();
		return offset;
	}

	// ================================================== PRIVATE

	/**
	 * Captures an UndoableAction and the offset at which it occurred.
	 */
	private class UndoableAndOffset {
		public IUndoableEdit edit;
		public int caretOffset;

		public UndoableAndOffset(IUndoableEdit edit, int caretOffset) {
			this.edit = edit;
			this.caretOffset = caretOffset;
		}
	}

	/**
	 * Processes the given edit, adding it to the undo stack.
	 * 
	 * @param edit
	 *            The edit to process.
	 * @param caretOffset
	 *            Offset of the caret before the edit occurred. If the edit is
	 *            undone, the caret is returned to this offset.
	 */
	private void addEdit(IUndoableEdit edit, int caretOffset) {

		if (edit == null) {
			return;
		}

		if (this.compoundEdit != null) {
			this.compoundEdit.addEdit(edit);
		} else {
			if (this.undoList.size() > 0
					&& ((UndoableAndOffset) this.undoList.getLast()).edit
							.combine(edit)) {
				return;
			} else {
				this.undoList.add(new UndoableAndOffset(edit, caretOffset));
				this.undoDepth++;
				if (undoList.size() > MAX_UNDO_STACK_SIZE) {
					undoList.removeFirst();
				}
				this.redoList.clear();
			}
		}
	}

	/**
	 * Creates a layout context given a particular graphics context.
	 * 
	 * @param g
	 *            The graphics context to use for the layout context.
	 * @return the new layout context
	 */
	private LayoutContext createLayoutContext(Graphics g) {
		LayoutContext context = new LayoutContext();
		context.setBoxFactory(this.getBoxFactory());
		context.setDocument(this.getDocument());
		context.setGraphics(g);
		context.setStyleSheet(this.getStyleSheet());

		if (this.hasSelection()) {
			context.setSelectionStart(this.getSelectionStart());
			context.setSelectionEnd(this.getSelectionEnd());
		} else {
			context.setSelectionStart(this.getCaretOffset());
			context.setSelectionEnd(this.getCaretOffset());
		}

		return context;
	}

	private void createRootBox() {
		Graphics g = this.hostComponent.createDefaultGraphics();
		LayoutContext context = this.createLayoutContext(g);
		this.rootBox = new RootBox(context, this.document.getRootElement(),
				this.getLayoutWidth());
		g.dispose();
	}

	/**
	 * Invalidates the box tree due to document changes. The lowest box that
	 * completely encloses the changed element is invalidated.
	 * 
	 * @param element
	 *            Element for which to search.
	 */
	private void invalidateElementBox(final VEXElement element) {

		BlockBox elementBox = (BlockBox) this
				.findInnermostBox(new IBoxFilter() {
					public boolean matches(Box box) {
						return box instanceof BlockBox
								&& box.getElement() != null
								&& box.getStartOffset() <= element
										.getStartOffset() + 1
								&& box.getEndOffset() >= element.getEndOffset();
					}
				});

		if (elementBox != null) {
			elementBox.invalidate(true);
		}
	}

	/**
	 * Returns true if the given offset represents the boundary between two
	 * different elements with the same name and parent. This is used to
	 * determine if the elements can be joined via joinElementsAt.
	 * 
	 * @param int offset The offset to check.
	 */
	private boolean isBetweenMatchingElements(int offset) {
		if (offset <= 1 || offset >= this.getDocument().getLength() - 1) {
			return false;
		}
		VEXElement e1 = this.getDocument().getElementAt(offset - 1);
		VEXElement e2 = this.getDocument().getElementAt(offset + 1);
		return e1 != e2 && e1.getParent() == e2.getParent()
				&& e1.getName().equals(e2.getName());
	}

	/**
	 * Calls layout() on the rootBox until the y-coordinate of a caret at the
	 * given offset converges, i.e. is less than LAYOUT_TOLERANCE pixels from
	 * the last call.
	 * 
	 * @param offset
	 *            Offset around which we should lay out boxes.
	 */
	private void iterateLayout(int offset) {

		int repaintStart = Integer.MAX_VALUE;
		int repaintEnd = 0;
		Graphics g = this.hostComponent.createDefaultGraphics();
		LayoutContext context = this.createLayoutContext(g);
		int layoutY = this.rootBox.getCaret(context, offset).getY();

		while (true) {

			int oldLayoutY = layoutY;
			IntRange repaintRange = this.rootBox.layout(context, layoutY
					- LAYOUT_WINDOW / 2, layoutY + LAYOUT_WINDOW / 2);
			if (repaintRange != null) {
				repaintStart = Math.min(repaintStart, repaintRange.getStart());
				repaintEnd = Math.max(repaintEnd, repaintRange.getEnd());
			}

			layoutY = this.rootBox.getCaret(context, offset).getY();
			if (Math.abs(layoutY - oldLayoutY) < LAYOUT_TOLERANCE) {
				break;
			}
		}
		g.dispose();

		if (repaintStart < repaintEnd) {
			Rectangle viewport = this.hostComponent.getViewport();
			if (repaintStart < viewport.getY() + viewport.getHeight()
					&& repaintEnd > viewport.getY()) {
				int start = Math.max(repaintStart, viewport.getY());
				int end = Math.min(repaintEnd, viewport.getY()
						+ viewport.getHeight());
				this.hostComponent.repaint(viewport.getX(), start, viewport
						.getWidth(), end - start);
			}
		}
	}

	/**
	 * Joins the elements at the given offset. Only works if
	 * isBetweenMatchingElements returns true for the same offset. Afterwards,
	 * the caret is left at the point where the join occurred.
	 * 
	 * @param offset
	 *            Offset where the two elements meet.
	 */
	private void joinElementsAt(int offset) throws DocumentValidationException {

		if (!isBetweenMatchingElements(offset)) {
			throw new DocumentValidationException(
					"Cannot join elements at offset " + offset);
		}

		boolean success = false;
		try {
			this.beginWork();
			this.moveTo(offset + 1);
			VEXElement element = this.getCurrentElement();
			boolean moveContent = !element.isEmpty();
			VEXDocumentFragment frag = null;
			if (moveContent) {
				this.moveTo(element.getEndOffset(), true);
				frag = this.getSelectedFragment();
				this.deleteSelection();
			}
			this.moveBy(-1);
			this.moveBy(2, true);
			this.deleteSelection();
			this.moveBy(-1);
			if (moveContent) {
				int savedOffset = this.getCaretOffset();
				this.insertFragment(frag);
				this.moveTo(savedOffset, false);
			}
			success = true;
		} finally {
			this.endWork(success);
		}
	}

	/**
	 * Lay out the area around the caret.
	 */
	private void relayout() {

		long start = System.currentTimeMillis();

		int oldHeight = this.rootBox.getHeight();

		this.iterateLayout(this.getCaretOffset());

		if (this.rootBox.getHeight() != oldHeight) {
			this.hostComponent.setPreferredSize(this.rootBox.getWidth(),
					this.rootBox.getHeight());
		}

		Graphics g = this.hostComponent.createDefaultGraphics();
		LayoutContext context = this.createLayoutContext(g);
		this.caret = this.rootBox.getCaret(context, this.getCaretOffset());
		g.dispose();

		if (this.isDebugging()) {
			long end = System.currentTimeMillis();
			System.out.println("VexWidget layout took " + (end - start) + "ms");
		}
	}

	/**
	 * Re-layout the entire widget, due to either a layout width change or a
	 * stylesheet range. This method does the actual setting of the width and
	 * stylesheet, since it needs to know where the caret is <i>before</i> the
	 * change, so that it can do a reasonable job of restoring the position of
	 * the viewport after the change.
	 * 
	 * @param newWidth
	 *            New width for the widget.
	 * @param newStyleSheet
	 *            New stylesheet for the widget.
	 */
	private void relayoutAll(int newWidth, StyleSheet newStyleSheet) {

		Graphics g = this.hostComponent.createDefaultGraphics();
		LayoutContext context = this.createLayoutContext(g);

		Rectangle viewport = this.hostComponent.getViewport();

		// true if the caret is within the viewport
		//
		// TODO: incorrect if caret near the bottom and the viewport is
		// shrinking
		// To fix, we probably need to save the viewport height, just like
		// we now store viewport width (as layout width).
		boolean caretVisible = viewport.intersects(this.caret.getBounds());

		// distance from the top of the viewport to the top of the caret
		// use this if the caret is visible in the viewport
		int relCaretY = 0;

		// offset around which we are laying out
		// this is also where we put the top of the viewport if the caret
		// isn't visible
		int offset;

		if (caretVisible) {
			relCaretY = this.caret.getY() - viewport.getY();
			offset = this.getCaretOffset();
		} else {
			offset = this.rootBox.viewToModel(context, 0, viewport.getY());
		}

		this.layoutWidth = newWidth;
		this.styleSheet = newStyleSheet;

		// Re-create the context, since it holds the old stylesheet
		context = this.createLayoutContext(g);

		this.createRootBox();

		this.iterateLayout(offset);

		this.hostComponent.setPreferredSize(this.rootBox.getWidth(),
				this.rootBox.getHeight());

		this.caret = this.rootBox.getCaret(context, this.getCaretOffset());

		if (caretVisible) {
			int viewportY = this.caret.getY()
					- Math.min(relCaretY, viewport.getHeight());
			viewportY = Math.min(this.rootBox.getHeight()
					- viewport.getHeight(), viewportY);
			viewportY = Math.max(0, viewportY); // this must appear after the
												// above line, since
			// that line might set viewportY negative
			this.hostComponent.scrollTo(viewport.getX(), viewportY);
			this.scrollCaretVisible();
		} else {
			int viewportY = this.rootBox.getCaret(context, offset).getY();
			this.hostComponent.scrollTo(viewport.getX(), viewportY);
		}

		this.hostComponent.repaint();

		g.dispose();

	}

	/**
	 * Repaints the area of the caret.
	 */
	private void repaintCaret() {
		if (this.caret != null) {
			// caret may be null when document is first set
			Rectangle bounds = this.caret.getBounds();
			this.hostComponent.repaint(bounds.getX(), bounds.getY(), bounds
					.getWidth(), bounds.getHeight());
		}
	}

	/**
	 * Repaints area of the control corresponding to a range of offsets in the
	 * document.
	 * 
	 * @param startOffset
	 *            Starting offset of the range.
	 * @param endOffset
	 *            Ending offset of the range.
	 */
	private void repaintRange(int startOffset, int endOffset) {

		Graphics g = this.hostComponent.createDefaultGraphics();

		LayoutContext context = this.createLayoutContext(g);

		Rectangle startBounds = this.rootBox.getCaret(context, startOffset)
				.getBounds();
		int top1 = startBounds.getY();
		int bottom1 = top1 + startBounds.getHeight();

		Rectangle endBounds = this.rootBox.getCaret(context, endOffset)
				.getBounds();
		int top2 = endBounds.getY();
		int bottom2 = top2 + endBounds.getHeight();

		int top = Math.min(top1, top2);
		int bottom = Math.max(bottom1, bottom2);
		if (top == bottom) {
			// Account for zero-height horizontal carets
			this.hostComponent.repaint(0, top - 1, this.getLayoutWidth(),
					bottom - top + 1);
		} else {
			this.hostComponent.repaint(0, top, this.getLayoutWidth(), bottom
					- top);
		}

		g.dispose();
	}

	private void scrollCaretVisible() {

		Rectangle caretBounds = this.caret.getBounds();
		Rectangle viewport = this.hostComponent.getViewport();

		int x = viewport.getX();
		int y = 0;
		int offset = getCaretOffset();
		if (offset == 1) {
			y = 0;
		} else if (offset == getDocument().getLength() - 1) {
			if (this.rootBox.getHeight() < viewport.getHeight()) {
				y = 0;
			} else {
				y = this.rootBox.getHeight() - viewport.getHeight();
			}
		} else if (caretBounds.getY() < viewport.getY()) {
			y = caretBounds.getY();
		} else if (caretBounds.getY() + caretBounds.getHeight() > viewport
				.getY()
				+ viewport.getHeight()) {
			y = caretBounds.getY() + caretBounds.getHeight()
					- viewport.getHeight();
		} else {
			// no scrolling required
			return;
		}
		this.hostComponent.scrollTo(x, y);
	}

}