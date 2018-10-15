List<VEXNode> nodes = getDocument().getNodes(getSelectionStart(),

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

import java.io.IOException;
import java.net.URL;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import javax.swing.undo.CannotRedoException;
import javax.swing.undo.CannotUndoException;
import javax.xml.parsers.ParserConfigurationException;

import org.eclipse.jface.action.IAction;
import org.eclipse.jface.viewers.ISelection;
import org.eclipse.jface.viewers.ISelectionChangedListener;
import org.eclipse.jface.viewers.ISelectionProvider;
import org.eclipse.jface.viewers.SelectionChangedEvent;
import org.eclipse.jface.viewers.StructuredSelection;
import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.PopupList;
import org.eclipse.swt.dnd.Clipboard;
import org.eclipse.swt.dnd.TextTransfer;
import org.eclipse.swt.dnd.Transfer;
import org.eclipse.swt.events.ControlEvent;
import org.eclipse.swt.events.ControlListener;
import org.eclipse.swt.events.FocusEvent;
import org.eclipse.swt.events.FocusListener;
import org.eclipse.swt.events.KeyEvent;
import org.eclipse.swt.events.KeyListener;
import org.eclipse.swt.events.MouseEvent;
import org.eclipse.swt.events.MouseListener;
import org.eclipse.swt.events.MouseMoveListener;
import org.eclipse.swt.events.PaintEvent;
import org.eclipse.swt.events.PaintListener;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.events.SelectionListener;
import org.eclipse.swt.graphics.GC;
import org.eclipse.swt.graphics.Point;
import org.eclipse.swt.widgets.Canvas;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.ScrollBar;
import org.eclipse.wst.xml.vex.core.internal.core.Color;
import org.eclipse.wst.xml.vex.core.internal.core.ColorResource;
import org.eclipse.wst.xml.vex.core.internal.core.DisplayDevice;
import org.eclipse.wst.xml.vex.core.internal.core.Graphics;
import org.eclipse.wst.xml.vex.core.internal.core.Rectangle;
import org.eclipse.wst.xml.vex.core.internal.css.StyleSheet;
import org.eclipse.wst.xml.vex.core.internal.dom.DocumentValidationException;
import org.eclipse.wst.xml.vex.core.internal.dom.Element;
import org.eclipse.wst.xml.vex.core.internal.layout.Box;
import org.eclipse.wst.xml.vex.core.internal.layout.BoxFactory;
import org.eclipse.wst.xml.vex.core.internal.provisional.dom.VEXDocument;
import org.eclipse.wst.xml.vex.core.internal.provisional.dom.VEXDocumentFragment;
import org.eclipse.wst.xml.vex.core.internal.provisional.dom.VEXElement;
import org.eclipse.wst.xml.vex.core.internal.provisional.dom.VEXNode;
import org.eclipse.wst.xml.vex.core.internal.widget.HostComponent;
import org.eclipse.wst.xml.vex.core.internal.widget.IBoxFilter;
import org.eclipse.wst.xml.vex.core.internal.widget.IVexWidget;
import org.eclipse.wst.xml.vex.core.internal.widget.VexWidgetImpl;
import org.eclipse.wst.xml.vex.ui.internal.action.AbstractVexAction;
import org.eclipse.wst.xml.vex.ui.internal.action.DuplicateSelectionAction;
import org.eclipse.wst.xml.vex.ui.internal.action.IVexAction;
import org.eclipse.wst.xml.vex.ui.internal.action.NextTableCellAction;
import org.eclipse.wst.xml.vex.ui.internal.action.PreviousTableCellAction;
import org.eclipse.wst.xml.vex.ui.internal.action.RemoveElementAction;
import org.eclipse.wst.xml.vex.ui.internal.action.SplitAction;
import org.eclipse.wst.xml.vex.ui.internal.action.SplitItemAction;
import org.xml.sax.SAXException;

/**
 * An implementation of the Vex widget based on SWT.
 */
public class VexWidget extends Canvas implements IVexWidget, ISelectionProvider {

	public VexWidget(Composite parent, int style) {
		super(parent, style);

		if (DisplayDevice.getCurrent() == null) {
			DisplayDevice.setCurrent(new SwtDisplayDevice());
		}

		this.impl = new VexWidgetImpl(hostComponent);
		this.setBackground(this.getDisplay().getSystemColor(SWT.COLOR_WHITE));

		ScrollBar vbar = this.getVerticalBar();
		if (vbar != null) {
			vbar.setIncrement(20);
			vbar.addSelectionListener(selectionListener);
		}

		this.addControlListener(this.controlListener);
		this.addFocusListener(this.focusListener);
		this.addKeyListener(this.keyListener);
		this.addMouseListener(this.mouseListener);
		this.addMouseMoveListener(this.mouseMoveListener);
		this.addPaintListener(this.painter);
	}

	public void dispose() {
		super.dispose();
		this.impl.setFocus(false); // This stops the caret timer, in case the
									// control
		// is disposed before focus is lost.
	}

	// ----------------------------------------- IInputProvider methods

	public Object getInput() {
		return this.impl.getDocument();
	}

	// ----------------------------------------- ISelectionProvider methods

	public void addSelectionChangedListener(ISelectionChangedListener listener) {
		this.selectionListeners.add(listener);
	}

	public ISelection getSelection() {
		return this.selection;
	}

	public void removeSelectionChangedListener(
			ISelectionChangedListener listener) {
		this.selectionListeners.remove(listener);
	}

	public void setSelection(ISelection selection) {
		throw new RuntimeException("Unexpected call to setSelection");
	}

	public void beginWork() {
		this.impl.beginWork();
	}

	public boolean canPaste() {
		// TODO Auto-generated method stub
		return false;
	}

	/**
	 * @see org.eclipse.wst.xml.vex.core.internal.widget.IVexWidget#canPasteText()
	 */
	public boolean canPasteText() {
		// TODO Auto-generated method stub
		return false;
	}

	public boolean canRedo() {
		return this.impl.canRedo();
	}

	public boolean canUndo() {
		return this.impl.canUndo();
	}

	public boolean canUnwrap() {
		return this.impl.canUnwrap();
	}

	public Point computeSize(int wHint, int hHint, boolean changed) {
		org.eclipse.swt.graphics.Rectangle r = this.getClientArea();
		int height = r.height;

		ScrollBar vbar = this.getVerticalBar();
		if (vbar != null) {
			height = vbar.getMaximum();
		}
		return new Point(r.width, height);
	}

	public void copySelection() {
		Clipboard clipboard = new Clipboard(this.getDisplay());
		Object[] data = { this.getSelectedFragment(), this.getSelectedText() };
		Transfer[] transfers = { DocumentFragmentTransfer.getInstance(),
				TextTransfer.getInstance() };
		clipboard.setContents(data, transfers);
	}

	public void cutSelection() {
		this.copySelection();
		this.deleteSelection();
	}

	public void deleteNextChar() throws DocumentValidationException {
		this.impl.deleteNextChar();
	}

	public void deletePreviousChar() throws DocumentValidationException {
		this.impl.deletePreviousChar();
	}

	public void deleteSelection() {
		this.impl.deleteSelection();
	}

	public void doWork(Runnable runnable) {
		this.impl.doWork(runnable);
	}

	public void doWork(boolean savePosition, Runnable runnable) {
		this.impl.doWork(savePosition, runnable);
	}

	public void endWork(boolean success) {
		this.impl.endWork(success);
	}

	public Box findInnermostBox(IBoxFilter filter) {
		return this.impl.findInnermostBox(filter);
	}

	public BoxFactory getBoxFactory() {
		return this.impl.getBoxFactory();
	}

	public int getCaretOffset() {
		return this.impl.getCaretOffset();
	}

	public VEXElement getCurrentElement() {
		return this.impl.getCurrentElement();
	}

	public VEXDocument getDocument() {
		return this.impl.getDocument();
	}

	public int getLayoutWidth() {
		return this.impl.getLayoutWidth();
	}

	public int getSelectionEnd() {
		return this.impl.getSelectionEnd();
	}

	public int getSelectionStart() {
		return this.impl.getSelectionStart();
	}

	public VEXDocumentFragment getSelectedFragment() {
		return this.impl.getSelectedFragment();
	}

	public String getSelectedText() {
		return this.impl.getSelectedText();
	}

	public StyleSheet getStyleSheet() {
		return this.impl.getStyleSheet();
	}

	public int getUndoDepth() {
		return this.impl.getUndoDepth();
	}

	public String[] getValidInsertElements() {
		return this.impl.getValidInsertElements();
	}

	public String[] getValidMorphElements() {
		return this.impl.getValidMorphElements();
	}

	public boolean hasSelection() {
		return this.impl.hasSelection();
	}

	public void insertChar(char c) throws DocumentValidationException {
		this.impl.insertChar(c);
	}

	public void insertFragment(VEXDocumentFragment frag)
			throws DocumentValidationException {
		this.impl.insertFragment(frag);
	}

	public void insertElement(Element element)
			throws DocumentValidationException {
		this.impl.insertElement(element);
	}

	public void insertText(String text) throws DocumentValidationException {
		this.impl.insertText(text);
	}

	public boolean isDebugging() {
		return impl.isDebugging();
	}

	public void morph(Element element) throws DocumentValidationException {
		this.impl.morph(element);
	}

	public void moveBy(int distance) {
		this.impl.moveBy(distance);
	}

	public void moveBy(int distance, boolean select) {
		this.impl.moveBy(distance, select);
	}

	public void moveTo(int offset) {
		this.impl.moveTo(offset);
	}

	public void moveTo(int offset, boolean select) {
		this.impl.moveTo(offset, select);
	}

	public void moveToLineEnd(boolean select) {
		this.impl.moveToLineEnd(select);
	}

	public void moveToLineStart(boolean select) {
		this.impl.moveToLineStart(select);
	}

	public void moveToNextLine(boolean select) {
		this.impl.moveToNextLine(select);
	}

	public void moveToNextPage(boolean select) {
		this.impl.moveToNextPage(select);
	}

	public void moveToNextWord(boolean select) {
		this.impl.moveToNextWord(select);
	}

	public void moveToPreviousLine(boolean select) {
		this.impl.moveToPreviousLine(select);
	}

	public void moveToPreviousPage(boolean select) {
		this.impl.moveToPreviousPage(select);
	}

	public void moveToPreviousWord(boolean select) {
		this.impl.moveToPreviousWord(select);
	}

	public IAction[] getValidInsertActions() {
		String[] names = this.getValidInsertElements();
		IAction[] actions = new IAction[names.length];
		for (int i = 0; i < names.length; i++) {
			actions[i] = new InsertElementAction(names[i]);
		}
		return actions;
	}

	public IAction[] getValidMorphActions() {
		String[] names = this.getValidMorphElements();
		IAction[] actions = new IAction[names.length];
		for (int i = 0; i < names.length; i++) {
			actions[i] = new MorphElementAction(names[i]);
		}
		return actions;
	}

	/**
	 * @see org.eclipse.wst.xml.vex.core.internal.widget.IVexWidget#paste()
	 */
	public void paste() throws DocumentValidationException {
		Clipboard clipboard = new Clipboard(this.getDisplay());
		VEXDocumentFragment frag = (VEXDocumentFragment) clipboard
				.getContents(DocumentFragmentTransfer.getInstance());
		if (frag != null) {
			this.insertFragment(frag);
		} else {
			this.pasteText();
		}
	}

	/**
	 * @see org.eclipse.wst.xml.vex.core.internal.widget.IVexWidget#pasteText()
	 */
	public void pasteText() throws DocumentValidationException {
		Clipboard clipboard = new Clipboard(this.getDisplay());
		String text = (String) clipboard
				.getContents(TextTransfer.getInstance());
		if (text != null) {
			this.insertText(text);
		}
	}

	public void redo() throws CannotRedoException {
		this.impl.redo();
	}

	public void removeAttribute(String attributeName) {
		this.impl.removeAttribute(attributeName);
	}

	public void savePosition(Runnable runnable) {
		this.impl.savePosition(runnable);
	}

	public void selectAll() {
		this.impl.selectAll();
	}

	public void selectWord() {
		this.impl.selectWord();
	}

	public void setAttribute(String attributeName, String value) {
		this.impl.setAttribute(attributeName, value);
	}

	public void setBoxFactory(BoxFactory boxFactory) {
		this.impl.setBoxFactory(boxFactory);
	}

	public void setDebugging(boolean debugging) {
		impl.setDebugging(debugging);
	}

	public void setDocument(VEXDocument doc, StyleSheet styleSheet) {
		this.impl.setDocument(doc, styleSheet);
	}

	public void setDocument(URL docUrl, URL ssURL) throws IOException,
			ParserConfigurationException, SAXException {
		this.impl.setDocument(docUrl, ssURL);
	}

	public void setLayoutWidth(int width) {
		this.impl.setLayoutWidth(width);
	}

	public void setStyleSheet(StyleSheet styleSheet) {
		this.impl.setStyleSheet(styleSheet);
	}

	public void setStyleSheet(URL ssUrl) throws IOException {
		this.impl.setStyleSheet(ssUrl);
	}

	/**
	 * Show a popup list of elements that are valid to be inserted at the
	 * current position. If one of the elements is selected, it is inserted
	 * before returning.
	 */
	public void showInsertElementPopup() {
		PopupList list = new PopupList(this.getShell());
		list.setItems(this.getValidInsertElements());

		Rectangle caret = this.impl.getCaret().getBounds();
		Point display = this.toDisplay(caret.getX() + 10, caret.getY());
		String selected = list.open(new org.eclipse.swt.graphics.Rectangle(
				display.x, display.y, 200, 0));
		if (selected != null) {
			try {
				this.insertElement(new Element(selected));
			} catch (DocumentValidationException e) {
				e.printStackTrace();
			}
		}
	}

	/**
	 * Show a popup list of elements to which it is valid to morph the current
	 * element. If one of the elements is selected, the current element is
	 * morphed before returning.
	 */
	public void showMorphElementPopup() {
		PopupList list = new PopupList(this.getShell());
		list.setItems(this.getValidMorphElements());

		Rectangle caret = this.impl.getCaret().getBounds();
		Point display = this.toDisplay(caret.getX() + 10, caret.getY());
		String selected = list.open(new org.eclipse.swt.graphics.Rectangle(
				display.x, display.y, 200, 0));
		if (selected != null) {
			try {
				this.morph(new Element(selected));
			} catch (DocumentValidationException e) {
				e.printStackTrace();
			}
		}
	}

	public void split() throws DocumentValidationException {
		this.impl.split();
	}

	public void undo() throws CannotUndoException {
		this.impl.undo();
	}

	public int viewToModel(int x, int y) {
		return this.impl.viewToModel(x, y);
	}

	// ====================================================== PRIVATE

	// ------------------------------------------------------ Fields

	private static final char CHAR_NONE = 0;
	private static Map keyMap;

	private VexWidgetImpl impl;

	// Fields controlling scrolling
	int originX = 0;
	int originY = 0;

	private List selectionListeners = new ArrayList();
	private ISelection selection;

	// ------------------------------------------------------ Inner Classes

	private Runnable caretTimerRunnable = new Runnable() {
		public void run() {
			impl.toggleCaret();
		}
	};
	private Timer caretTimer = new Timer(500, this.caretTimerRunnable);

	private ControlListener controlListener = new ControlListener() {
		public void controlMoved(ControlEvent e) {
		}

		public void controlResized(ControlEvent e) {
			org.eclipse.swt.graphics.Rectangle r = getClientArea();
			// There seems to be a bug in SWT (at least on Linux/GTK+)
			// When maximizing the editor, the width is first set to 1,
			// then to the correct width
			if (r.width == 1) {
				return;
			}
			impl.setLayoutWidth(r.width);

			ScrollBar vbar = getVerticalBar();
			if (vbar != null) {
				vbar.setThumb(r.height);
				vbar.setPageIncrement(Math.round(r.height * 0.9f));
			}
		}
	};

	private FocusListener focusListener = new FocusListener() {
		public void focusGained(FocusEvent e) {
			impl.setFocus(true);
			caretTimer.start();
		}

		public void focusLost(FocusEvent e) {
			impl.setFocus(false);
			caretTimer.stop();
		}
	};

	private HostComponent hostComponent = new HostComponent() {

		public Graphics createDefaultGraphics() {
			if (VexWidget.this.isDisposed()) {
				System.out.println("*** Woot! VexWidget is disposed!");
			}
			return new SwtGraphics(new GC(VexWidget.this));
		}

		public void fireSelectionChanged() {

			if (hasSelection()) {
				VEXNode[] nodes = getDocument().getNodes(getSelectionStart(),
						getSelectionEnd());
				selection = new StructuredSelection(nodes);
			} else {
				selection = new StructuredSelection(getCurrentElement());
			}

			SelectionChangedEvent e = new SelectionChangedEvent(VexWidget.this,
					selection);
			for (int i = 0; i < selectionListeners.size(); i++) {
				ISelectionChangedListener listener = (ISelectionChangedListener) selectionListeners
						.get(i);
				listener.selectionChanged(e);
			}
			caretTimer.reset();
		}

		public Rectangle getViewport() {
			return new Rectangle(getClientArea().x - originX, getClientArea().y
					- originY, getClientArea().width, getClientArea().height);
		}

		public void invokeLater(Runnable runnable) {
			VexWidget.this.getDisplay().asyncExec(runnable);
		}

		public void repaint() {
			if (!VexWidget.this.isDisposed()) {
				// We can sometimes get a repaint from the VexWidgetImpl's
				// caret timer thread after the Widget is disposed.
				VexWidget.this.redraw();
			}
		}

		public void repaint(int x, int y, int width, int height) {
			VexWidget.this
					.redraw(x + originX, y + originY, width, height, true);
		}

		public void scrollTo(int left, int top) {
			ScrollBar vbar = getVerticalBar();
			if (vbar != null) {
				vbar.setSelection(top);
			}
			setOrigin(-left, -top);
		}

		public void setPreferredSize(int width, int height) {
			ScrollBar vbar = getVerticalBar();
			if (vbar != null) {
				vbar.setMaximum(height);
			}
		}

	};

	private static abstract class Action extends AbstractVexAction {

		public void run(IVexWidget vexWidget) {
			try {
				this.runEx(vexWidget);
			} catch (Exception ex) {
				ex.printStackTrace();
			}
		}

		public abstract void runEx(IVexWidget w) throws Exception;
	}

	private KeyListener keyListener = new KeyListener() {

		public void keyPressed(KeyEvent e) {
			// System.out.println("Key pressed, keyCode is " + e.keyCode +
			// ", keyChar is " + ((int) e.character) + ", stateMask is " +
			// e.stateMask);
			KeyStroke keyStroke = new KeyStroke(e);
			Map map = getKeyMap();
			if (map.containsKey(keyStroke)) {
				Object action = map.get(keyStroke);
				if (action instanceof IVexAction) {
					((IVexAction) action).run(VexWidget.this);
				} else {
					try {
						((Action) map.get(keyStroke)).runEx(VexWidget.this);
					} catch (Exception ex) {
						ex.printStackTrace();
					}
				}
			} else if (!Character.isISOControl(e.character)) {
				try {
					insertChar(e.character);
				} catch (DocumentValidationException e1) {
					// TODO Auto-generated catch block
					e1.printStackTrace();
				}
			}
		}

		public void keyReleased(KeyEvent e) {
		}
	};

	private MouseListener mouseListener = new MouseListener() {
		public void mouseDoubleClick(MouseEvent e) {
			if (e.button == 1) {
				selectWord();
			}
		}

		public void mouseDown(MouseEvent e) {
			if (e.button == 1) {
				int offset = viewToModel(e.x - originX, e.y - originY);
				boolean select = (e.stateMask == SWT.SHIFT);
				moveTo(offset, select);
			}
		}

		public void mouseUp(MouseEvent e) {
		}
	};

	private MouseMoveListener mouseMoveListener = new MouseMoveListener() {
		public void mouseMove(MouseEvent e) {
			if ((e.stateMask & SWT.BUTTON1) > 0) {
				int offset = viewToModel(e.x - originX, e.y - originY);
				moveTo(offset, true);
			}
		}
	};

	private PaintListener painter = new PaintListener() {
		public void paintControl(PaintEvent e) {

			SwtGraphics g = new SwtGraphics(e.gc);
			g.setOrigin(originX, originY);

			Color bgColor = impl.getBackgroundColor();
			if (bgColor == null) {
				bgColor = new Color(255, 255, 255);
			}

			ColorResource color = g.createColor(bgColor);
			ColorResource oldColor = g.setColor(color);
			Rectangle r = g.getClipBounds();
			g.fillRect(r.getX(), r.getY(), r.getWidth(), r.getHeight());
			g.setColor(oldColor);
			color.dispose();

			impl.paint(g, 0, 0);
		}
	};

	private SelectionListener selectionListener = new SelectionListener() {
		public void widgetSelected(SelectionEvent e) {
			ScrollBar vbar = getVerticalBar();
			if (vbar != null) {
				int y = -vbar.getSelection();
				setOrigin(0, y);
			}
		}

		public void widgetDefaultSelected(SelectionEvent e) {
		}
	};

	private class InsertElementAction extends org.eclipse.jface.action.Action {
		public InsertElementAction(String name) {
			this.name = name;
			this.setText(name);
		}

		public void run() {
			try {
				insertElement(new Element(name));
			} catch (DocumentValidationException e) {
			}
		}

		private String name;
	}

	private class MorphElementAction extends org.eclipse.jface.action.Action {
		public MorphElementAction(String elementName) {
			this.elementName = elementName;
			this.setText(elementName);
		}

		public void run() {
			try {
				morph(new Element(elementName));
			} catch (DocumentValidationException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		}

		private String elementName;
	}

	// ------------------------------------------------------ Methods

	private static void addKey(char character, int keyCode, int stateMask,
			Action action) {
		keyMap.put(new KeyStroke(character, keyCode, stateMask), action);
	}

	private static void addKey(char character, int keyCode, int stateMask,
			IVexAction action) {
		keyMap.put(new KeyStroke(character, keyCode, stateMask), action);
	}

	private static void buildKeyMap() {
		addKey(CHAR_NONE, SWT.ARROW_DOWN, SWT.NONE, new Action() {
			public void runEx(IVexWidget w) {
				w.moveToNextLine(false);
			}
		});
		addKey(CHAR_NONE, SWT.ARROW_DOWN, SWT.SHIFT, new Action() {
			public void runEx(IVexWidget w) {
				w.moveToNextLine(true);
			}
		});

		addKey(CHAR_NONE, SWT.ARROW_LEFT, SWT.NONE, new Action() {
			public void runEx(IVexWidget w) {
				w.moveBy(-1);
			}
		});
		addKey(CHAR_NONE, SWT.ARROW_LEFT, SWT.SHIFT, new Action() {
			public void runEx(IVexWidget w) {
				w.moveBy(-1, true);
			}
		});
		addKey(CHAR_NONE, SWT.ARROW_LEFT, SWT.CONTROL, new Action() {
			public void runEx(IVexWidget w) {
				w.moveToPreviousWord(false);
			}
		});
		addKey(CHAR_NONE, SWT.ARROW_LEFT, SWT.SHIFT | SWT.CONTROL,
				new Action() {
					public void runEx(IVexWidget w) {
						w.moveToPreviousWord(true);
					}
				});

		addKey(CHAR_NONE, SWT.ARROW_RIGHT, SWT.NONE, new Action() {
			public void runEx(IVexWidget w) {
				w.moveBy(+1);
			}
		});
		addKey(CHAR_NONE, SWT.ARROW_RIGHT, SWT.SHIFT, new Action() {
			public void runEx(IVexWidget w) {
				w.moveBy(+1, true);
			}
		});
		addKey(CHAR_NONE, SWT.ARROW_RIGHT, SWT.CONTROL, new Action() {
			public void runEx(IVexWidget w) {
				w.moveToNextWord(false);
			}
		});
		addKey(CHAR_NONE, SWT.ARROW_RIGHT, SWT.SHIFT | SWT.CONTROL,
				new Action() {
					public void runEx(IVexWidget w) {
						w.moveToNextWord(true);
					}
				});

		addKey(CHAR_NONE, SWT.ARROW_UP, SWT.NONE, new Action() {
			public void runEx(IVexWidget w) {
				w.moveToPreviousLine(false);
			}
		});
		addKey(CHAR_NONE, SWT.ARROW_UP, SWT.SHIFT, new Action() {
			public void runEx(IVexWidget w) {
				w.moveToPreviousLine(true);
			}
		});

		addKey(SWT.BS, SWT.BS, SWT.NONE, new Action() {
			public void runEx(IVexWidget w) throws Exception {
				w.deletePreviousChar();
			}
		});
		addKey(SWT.DEL, SWT.DEL, SWT.NONE, new Action() {
			public void runEx(IVexWidget w) throws Exception {
				w.deleteNextChar();
			}
		});

		addKey(SWT.TAB, SWT.TAB, SWT.NONE, new NextTableCellAction());
		addKey(SWT.TAB, SWT.TAB, SWT.SHIFT, new PreviousTableCellAction());

		addKey(CHAR_NONE, SWT.END, SWT.NONE, new Action() {
			public void runEx(IVexWidget w) {
				w.moveToLineEnd(false);
			}
		});
		addKey(CHAR_NONE, SWT.END, SWT.SHIFT, new Action() {
			public void runEx(IVexWidget w) {
				w.moveToLineEnd(true);
			}
		});
		addKey(CHAR_NONE, SWT.END, SWT.CONTROL, new Action() {
			public void runEx(IVexWidget w) {
				w.moveTo(w.getDocument().getLength() - 1);
			}
		});
		addKey(CHAR_NONE, SWT.END, SWT.SHIFT | SWT.CONTROL, new Action() {
			public void runEx(IVexWidget w) {
				w.moveTo(w.getDocument().getLength() - 1, true);
			}
		});

		addKey(CHAR_NONE, SWT.HOME, SWT.NONE, new Action() {
			public void runEx(IVexWidget w) {
				w.moveToLineStart(false);
			}
		});
		addKey(CHAR_NONE, SWT.HOME, SWT.SHIFT, new Action() {
			public void runEx(IVexWidget w) {
				w.moveToLineStart(true);
			}
		});
		addKey(CHAR_NONE, SWT.HOME, SWT.CONTROL, new Action() {
			public void runEx(IVexWidget w) {
				w.moveTo(1);
			}
		});
		addKey(CHAR_NONE, SWT.HOME, SWT.SHIFT | SWT.CONTROL, new Action() {
			public void runEx(IVexWidget w) {
				w.moveTo(1, true);
			}
		});

		addKey(CHAR_NONE, SWT.PAGE_DOWN, SWT.NONE, new Action() {
			public void runEx(IVexWidget w) {
				w.moveToNextPage(false);
			}
		});
		addKey(CHAR_NONE, SWT.PAGE_DOWN, SWT.SHIFT, new Action() {
			public void runEx(IVexWidget w) {
				w.moveToNextPage(true);
			}
		});

		addKey(CHAR_NONE, SWT.PAGE_UP, SWT.NONE, new Action() {
			public void runEx(IVexWidget w) {
				w.moveToPreviousPage(false);
			}
		});
		addKey(CHAR_NONE, SWT.PAGE_UP, SWT.SHIFT, new Action() {
			public void runEx(IVexWidget w) {
				w.moveToPreviousPage(true);
			}
		});

		addKey(' ', 0, SWT.CONTROL, new Action() { // Ctrl-Space
					public void runEx(IVexWidget w) {
						((VexWidget) w).showInsertElementPopup();
					}
				});
		addKey('\r', 0, SWT.CONTROL, new Action() { // Ctrl-M
					public void runEx(IVexWidget w) {
						((VexWidget) w).showMorphElementPopup();
					}
				});
		addKey((char) 23, 0, SWT.CONTROL, new RemoveElementAction());
		// addKey('\r', '\r', SWT.NONE, new Action() { // Enter key
		// public void runEx(IVexWidget w) throws Exception { w.split(); } });
		addKey('\r', '\r', SWT.NONE, new SplitAction());
		addKey('\r', '\r', SWT.SHIFT, new SplitItemAction());

		addKey((char) 4, 100, SWT.CONTROL, new DuplicateSelectionAction()); // Ctrl-D
	}

	private static Map getKeyMap() {
		if (keyMap == null) {
			keyMap = new HashMap();
			buildKeyMap();
		}
		return keyMap;
	}

	/**
	 * Scrolls to the given position in the widget.
	 * 
	 * @param x
	 *            x-coordinate of the position to which to scroll
	 * @param y
	 *            y-coordinate of the position to which to scroll
	 */
	private void setOrigin(int x, int y) {
		int destX = x - originX;
		int destY = y - originY;
		org.eclipse.swt.graphics.Rectangle ca = getClientArea();
		scroll(destX, destY, 0, 0, ca.width, ca.height, false);
		originX = x;
		originY = y;
	}

}