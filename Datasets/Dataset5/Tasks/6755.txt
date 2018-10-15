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

import java.awt.Cursor;
import java.awt.Dimension;
import java.awt.Graphics;
import java.awt.Graphics2D;
import java.awt.GraphicsConfiguration;
import java.awt.GraphicsDevice;
import java.awt.GraphicsEnvironment;
import java.awt.Rectangle;
import java.awt.Toolkit;
import java.awt.datatransfer.Clipboard;
import java.awt.datatransfer.DataFlavor;
import java.awt.datatransfer.StringSelection;
import java.awt.datatransfer.Transferable;
import java.awt.datatransfer.UnsupportedFlavorException;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.ComponentAdapter;
import java.awt.event.ComponentEvent;
import java.awt.event.ComponentListener;
import java.awt.event.FocusEvent;
import java.awt.event.FocusListener;
import java.awt.event.KeyEvent;
import java.awt.event.KeyListener;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.awt.event.MouseListener;
import java.awt.event.MouseMotionAdapter;
import java.awt.event.MouseMotionListener;
import java.io.IOException;
import java.net.URL;
import java.util.MissingResourceException;
import java.util.ResourceBundle;

import javax.swing.AbstractAction;
import javax.swing.Action;
import javax.swing.ActionMap;
import javax.swing.InputMap;
import javax.swing.JComponent;
import javax.swing.JPopupMenu;
import javax.swing.KeyStroke;
import javax.swing.Scrollable;
import javax.swing.SwingUtilities;
import javax.swing.Timer;
import javax.swing.UIManager;
import javax.swing.undo.CannotRedoException;
import javax.swing.undo.CannotUndoException;
import javax.xml.parsers.ParserConfigurationException;

import org.eclipse.wst.xml.vex.core.internal.VEXCorePlugin;
import org.eclipse.wst.xml.vex.core.internal.core.Color;
import org.eclipse.wst.xml.vex.core.internal.core.ColorResource;
import org.eclipse.wst.xml.vex.core.internal.core.DisplayDevice;
import org.eclipse.wst.xml.vex.core.internal.css.StyleSheet;
import org.eclipse.wst.xml.vex.core.internal.dom.Document;
import org.eclipse.wst.xml.vex.core.internal.dom.DocumentFragment;
import org.eclipse.wst.xml.vex.core.internal.dom.DocumentValidationException;
import org.eclipse.wst.xml.vex.core.internal.dom.Element;
import org.eclipse.wst.xml.vex.core.internal.layout.Box;
import org.eclipse.wst.xml.vex.core.internal.layout.BoxFactory;
import org.eclipse.wst.xml.vex.core.internal.widget.HostComponent;
import org.eclipse.wst.xml.vex.core.internal.widget.IBoxFilter;
import org.eclipse.wst.xml.vex.core.internal.widget.VexWidgetImpl;
import org.xml.sax.SAXException;

/**
 * 
 */
public class VexComponent extends JComponent implements Scrollable,
		SelectionProvider {

	private VexWidgetImpl impl;

	private ActionMap staticActionMap = createActionMap();
	private static InputMap staticInputMap = createInputMap();

	private Timer caretTimer;

	private int originX = 0;
	private int originY = 0;

	// Temporary clipboard is used during begin/end work
	private Clipboard clipboard = Toolkit.getDefaultToolkit()
			.getSystemClipboard();

	private SelectionProviderImpl selectionProvider = new SelectionProviderImpl();

	private static ResourceBundle uiStringBundle;

	// Last VexComponent that had the focus. We need this sometimes to
	// determine the target of an action.
	private static VexComponent lastFocusedComponent;

	// ======================================================= LISTENERS

	private ActionListener caretTimerListener = new ActionListener() {
		public void actionPerformed(ActionEvent e) {
			VexComponent.this.impl.toggleCaret();
		}
	};

	private ComponentListener componentListener = new ComponentAdapter() {
		public void componentResized(ComponentEvent e) {
			int width = VexComponent.this.getWidth();
			VexComponent.this.impl.setLayoutWidth(width);
		}
	};

	private FocusListener focusListener = new FocusListener() {
		public void focusGained(FocusEvent e) {
			lastFocusedComponent = VexComponent.this;
			impl.setFocus(true);
			VexComponent.this.caretTimer.start();
		}

		public void focusLost(FocusEvent e) {
			impl.setFocus(false);
			VexComponent.this.caretTimer.stop();
		}
	};

	private KeyListener keyListener = new KeyListener() {
		public void keyPressed(KeyEvent e) {

			// final char NEWLINE = 0xa;

			if (VexComponent.this.impl.getDocument() == null) {
				Toolkit.getDefaultToolkit().beep();
				return;
			}

			if (e.getKeyCode() == KeyEvent.VK_SHIFT) {
				return;
			}

			try {
				InputMap map = VexComponent.staticInputMap;
				KeyStroke keyStroke = KeyStroke.getKeyStrokeForEvent(e);
				Object keyStrokeBinding = map.get(keyStroke);
				if (keyStrokeBinding != null) {
					BaseAction action = (BaseAction) VexComponent.this.staticActionMap
							.get(map.get(keyStroke));
					action.actionPerformed(new ActionEvent(VexComponent.this,
							0, ""), VexComponent.this.impl);
				} else if (!Character.isISOControl(e.getKeyChar())
						&& !e.isControlDown()) {
					// We check e.isControlDown() to ensure Ctrl-Space does not
					// also enter a space.
					if (VexComponent.this.impl.hasSelection()) {
						VexComponent.this.impl.deleteSelection();
					}
					insertChar(e.getKeyChar());
				}
			} catch (DocumentValidationException ex) {
				Toolkit.getDefaultToolkit().beep();
			} catch (Exception ex) {
				Toolkit.getDefaultToolkit().beep();
				ex.printStackTrace();
			}

		}

		public void keyReleased(KeyEvent e) {
		}

		public void keyTyped(KeyEvent e) {
		}

	};

	private MouseListener mouseListener = new MouseAdapter() {
		public void mousePressed(MouseEvent e) {

			boolean isButton1 = (e.getModifiers() & MouseEvent.BUTTON1_MASK) > 0;

			if (VexComponent.this.impl.getRootBox() != null && isButton1) {
				if (hasFocus()) {
					int offset = VexComponent.this.impl.viewToModel(e.getX()
							- originX, e.getY() - originY);
					moveTo(offset);

					if (e.getClickCount() == 2) {
						selectWord();
					}
				}
				requestFocus();
			}
		}
	};

	private MouseMotionListener mouseMotionListener = new MouseMotionAdapter() {
		public void mouseDragged(MouseEvent e) {
			boolean isButton1 = (e.getModifiers() & MouseEvent.BUTTON1_MASK) > 0;

			if (VexComponent.this.impl.getRootBox() != null && isButton1) {
				int offset = VexComponent.this.viewToModel(e.getX(), e.getY());
				moveTo(offset, true);
				requestFocus();
			}
		}
	};

	/*
	 * (non-Javadoc)
	 * 
	 * @seeorg.eclipse.wst.xml.vex.core.internal.swing.SelectionProvider#
	 * addSelectionListener
	 * (org.eclipse.wst.xml.vex.core.internal.swing.SelectionListener)
	 */
	public void addSelectionListener(SelectionListener listener) {
		this.selectionProvider.addSelectionListener(listener);
	}

	public boolean canPaste() {

		// TODO: sacrifice paste toolbar button state for performance
		// (see note below).
		if (true) {
			return true;
		}

		// TODO: This next line takes a looong time in X11
		// ~130ms on a Pentum-M 1.6GHz on Linux 2.4.21/XFree86 4.3.0
		Transferable tfbl = this.clipboard.getContents(null);
		DataFlavor flavor = VexSelection.VEX_DOCUMENT_FRAGMENT_FLAVOR;
		if (!tfbl.isDataFlavorSupported(flavor)) {
			return this.canPasteText();
		}

		DocumentFragment frag;
		try {
			frag = (DocumentFragment) tfbl.getTransferData(flavor);
		} catch (UnsupportedFlavorException ex) {
			return false;
		} catch (IOException ex) {
			return false;
		}

		return this.impl.canInsertFragment(frag);
	}

	/**
	 * Returns true if the clipboard has plain text content that can be pasted.
	 * Used to enable/disable the "paste text" action of a containing
	 * application.
	 */
	public boolean canPasteText() {

		// TODO: sacrifice paste toolbar button state for performance
		// (see note below).
		if (true) {
			return true;
		}

		// TODO: This next line takes a looong time in X11
		// ~130ms on a Pentum-M 1.6GHz on Linux 2.4.21/XFree86 4.3.0
		Transferable tfbl = this.clipboard.getContents(null);
		DataFlavor plainText = new DataFlavor(String.class, "text/plain");
		return tfbl.isDataFlavorSupported(plainText)
				&& this.impl.canPasteText();
	}

	/**
	 * Copy the current selection to the clipboard.
	 */
	public void copySelection() {
		if (this.impl.hasSelection()) {
			StringSelection sel = new VexSelection(this.impl.getSelectedText(),
					this.impl.getSelectedFragment());
			this.clipboard.setContents(sel, sel);
		}
	}

	public void cutSelection() {
		this.copySelection();
		this.deleteSelection();
	}

	public void deleteSelection() {
		this.impl.deleteSelection();
	}

	/**
	 * Returns the VexComponent that last had focus.
	 */
	public static VexComponent getLastFocusedComponent() {
		return lastFocusedComponent;
	}

	/**
	 * Returns a string from the resource bundle for the current locale. If the
	 * string is not found in the resource bundle, returns null.
	 * 
	 * @param name
	 *            property for which to return the string.
	 */
	public static String getUIString(String name) {
		if (uiStringBundle == null) {
			uiStringBundle = ResourceBundle
					.getBundle("org.eclipse.wst.vex.app.UIStrings");
		}

		try {
			return uiStringBundle.getString(name);
		} catch (MissingResourceException ex) {
			return null;
		}
	}

	// ------------------------------------------------ Scrollable methods

	public Dimension getPreferredScrollableViewportSize() {
		return this.getPreferredSize();
	}

	public int getScrollableBlockIncrement(Rectangle visibleRect,
			int orientation, int direction) {
		return Math.max(visibleRect.height - 40, 40);
	}

	public boolean getScrollableTracksViewportHeight() {
		return false;
	}

	public boolean getScrollableTracksViewportWidth() {
		return true;
	}

	public int getScrollableUnitIncrement(Rectangle visibleRect,
			int orientation, int direction) {
		return 20; // TODO: fix scrolling increment
	}

	public VexComponent() {
		ActionMap customActionMap = new ActionMap();
		customActionMap.setParent(staticActionMap);
		this.setActionMap(customActionMap);

		InputMap customInputMap = new InputMap();
		customInputMap.setParent(staticInputMap);
		this.setInputMap(JComponent.WHEN_FOCUSED, customInputMap);

		this.addComponentListener(this.componentListener);
		this.addFocusListener(this.focusListener);
		this.addKeyListener(this.keyListener);
		this.addMouseListener(this.mouseListener);
		this.addMouseMotionListener(this.mouseMotionListener);
		this.setCursor(Cursor.getPredefinedCursor(Cursor.TEXT_CURSOR));

		this.caretTimer = new Timer(
				UIManager.getInt("TextPane.caretBlinkRate"),
				this.caretTimerListener);
		this.caretTimer.start();

		DisplayDevice.setCurrent(new AwtDisplayDevice());

		impl = new VexWidgetImpl(this.hostComponent);

	}

	public void insertElement(Element element)
			throws DocumentValidationException {
		this.impl.insertElement(element);
	}

	public void morph(Element element) throws DocumentValidationException {
		this.impl.morph(element);
	}

	public void paint(Graphics g) {
		this.paintComponent(g);
	}

	protected void paintComponent(Graphics g) {

		long start = 0;
		if (VEXCorePlugin.getInstance().isDebugging()) {
			start = System.currentTimeMillis();
		}

		if (this.impl.getDocument() == null) {
			return;
		}

		AwtGraphics awtg = new AwtGraphics((Graphics2D) g);
		awtg.setOrigin(0, this.originY);

		Color bgColor = impl.getBackgroundColor();
		if (bgColor == null) {
			bgColor = new Color(255, 255, 255);
		}

		ColorResource color = awtg.createColor(bgColor);
		ColorResource oldColor = awtg.setColor(color);
		Rectangle r = g.getClipBounds();
		awtg.fillRect((int) r.getX() - this.originX, (int) r.getY()
				- this.originY, (int) r.getWidth(), (int) r.getHeight());
		awtg.setColor(oldColor);
		color.dispose();

		this.impl.paint(awtg, 0, 0);

		/*
		 * Graphics2D g2d = (Graphics2D) g; if (this.isAntiAliased()) {
		 * g2d.setRenderingHint( RenderingHints.KEY_ANTIALIASING,
		 * RenderingHints.VALUE_ANTIALIAS_ON); }
		 * 
		 * impl.paint(new AwtGraphics(g2d), 0, 0);
		 * 
		 * if (this.caretVisible && this.isEnabled()) { if (this.hasFocus()) {
		 * g.setColor(Color.black); } else { g.setColor(Color.gray); }
		 * g2d.setStroke(caretStroke); g2d.draw(this.caretShapes[0]); }
		 */

		if (VEXCorePlugin.getInstance().isDebugging()) {
			long end = System.currentTimeMillis();
			System.out.println("paint took " + (end - start) + "ms");
		}
	}

	public void paste() throws DocumentValidationException {

		if (!this.canPaste()) {
			return;
		}

		try {
			Transferable tfbl = this.clipboard.getContents(null);
			DataFlavor flavor = VexSelection.VEX_DOCUMENT_FRAGMENT_FLAVOR;
			if (tfbl.isDataFlavorSupported(flavor)) {
				DocumentFragment frag = (DocumentFragment) tfbl
						.getTransferData(flavor);
				this.impl.insertFragment(frag);
			} else {
				this.pasteText();
			}
		} catch (IOException ex) {
			ex.printStackTrace();
		} catch (UnsupportedFlavorException ex) {
			ex.printStackTrace();
		}
	}

	public void pasteText() throws DocumentValidationException {

		try {
			Transferable tfbl = this.clipboard.getContents(null);
			DataFlavor plainText = new DataFlavor(String.class, "text/plain");
			if (tfbl.isDataFlavorSupported(plainText)) {
				String text = (String) tfbl.getTransferData(plainText);
				this.impl.insertText(text);
			}
		} catch (IOException ex) {
			ex.printStackTrace();
		} catch (UnsupportedFlavorException ex) {
			ex.printStackTrace();
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

	public void deleteNextChar() throws DocumentValidationException {
		this.impl.deleteNextChar();
	}

	public void deletePreviousChar() throws DocumentValidationException {
		this.impl.deletePreviousChar();
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

	public Element getCurrentElement() {
		return this.impl.getCurrentElement();
	}

	public Document getDocument() {
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

	public DocumentFragment getSelectedFragment() {
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

	public void insertFragment(DocumentFragment frag)
			throws DocumentValidationException {
		this.impl.insertFragment(frag);
	}

	public void insertText(String text) throws DocumentValidationException {
		this.impl.insertText(text);
	}

	public boolean isDebugging() {
		return impl.isDebugging();
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

	public void setDocument(Document doc, StyleSheet styleSheet) {
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
	 * @see SelectionProvider#removeSelectionListener
	 */
	public void removeSelectionListener(SelectionListener listener) {
		this.selectionProvider.removeSelectionListener(listener);
	}

	public Action[] getInsertElementActions() {
		String[] names = this.getValidInsertElements();
		Action[] actions = new Action[names.length];
		for (int i = 0; i < names.length; i++) {
			actions[i] = new InsertElementAction(names[i]);
		}
		return actions;
	}

	public Action[] getMorphElementActions() {
		String[] names = this.getValidMorphElements();
		Action[] actions = new Action[names.length];
		for (int i = 0; i < names.length; i++) {
			actions[i] = new MorphAction(names[i]);
		}
		return actions;
	}

	/**
	 * Display a popup menu of valid elements to insert at the current caret
	 * position.
	 */
	public void showInsertElementPopup() {

		JPopupMenu popup = new JPopupMenu();

		Action[] actions = this.getInsertElementActions();

		if (actions.length == 0) {
			return;
		}

		for (int i = 0; i < actions.length; i++) {
			popup.add(actions[i]);
		}

		org.eclipse.wst.xml.vex.core.internal.core.Rectangle caretBounds = this.impl
				.getCaret().getBounds();
		popup.show(this, caretBounds.getX() + 10, caretBounds.getY());
	}

	/**
	 * Display a popup menu of valid elements to which the current element can
	 * be morphed.
	 */
	public void showMorphElementPopup() {

		JPopupMenu popup = new JPopupMenu();

		Action[] actions = this.getMorphElementActions();

		if (actions.length == 0) {
			return;
		}

		for (int i = 0; i < actions.length; i++) {
			popup.add(actions[i]);
		}

		org.eclipse.wst.xml.vex.core.internal.core.Rectangle caretBounds = this.impl
				.getCaret().getBounds();
		popup.show(this, caretBounds.getX() + 10, caretBounds.getY());
	}

	// ========================================================= PRIVATE

	private HostComponent hostComponent = new HostComponent() {

		// This is needed to create a default Graphics object,
		// but creating these is really slow, so we cache 'em.
		private GraphicsEnvironment graphicsEnvironment = null;
		private java.awt.image.BufferedImage dummyImage = null;

		public org.eclipse.wst.xml.vex.core.internal.core.Graphics createDefaultGraphics() {
			if (graphicsEnvironment == null) {
				graphicsEnvironment = GraphicsEnvironment
						.getLocalGraphicsEnvironment();

				GraphicsDevice gdev = graphicsEnvironment
						.getDefaultScreenDevice();
				GraphicsConfiguration gconf = gdev.getDefaultConfiguration();
				dummyImage = gconf.createCompatibleImage(1, 1);
			}
			Graphics g = graphicsEnvironment.createGraphics(dummyImage);
			return new AwtGraphics((Graphics2D) g);
		}

		public void fireSelectionChanged() {
			VexComponent.this.fireSelectionChanged();
		}

		public void invokeLater(Runnable runnable) {
			SwingUtilities.invokeLater(runnable);
		}

		public void repaint() {
			VexComponent.this.repaint();
		}

		public void repaint(int x, int y, int width, int height) {
			VexComponent.this.repaint();// VexComponent.this.repaint(x , y,
										// width, height);
		}

		public void scrollTo(int left, int top) {
			VexComponent.this.setOrigin(-left, -top);
		}

		public void setPreferredSize(int width, int height) {
			/*
			 * Dimension size = new Dimension(width, height);
			 * VexComponent.this.setPreferredSize(size);
			 * VexComponent.this.setSize(size);
			 */
		}

		public org.eclipse.wst.xml.vex.core.internal.core.Rectangle getViewport() {

			return new org.eclipse.wst.xml.vex.core.internal.core.Rectangle(
					0 - VexComponent.this.originX,
					0 - VexComponent.this.originY,
					VexComponent.this.getWidth(), VexComponent.this.getHeight());

		}
	};

	/**
	 * Action for inserting an element into the document at the current offset.
	 */
	private class InsertElementAction extends AbstractAction {

		private String name;

		/**
		 * Class constructor.
		 * 
		 * @param name
		 *            Name of the element to insert.
		 */
		public InsertElementAction(String name) {
			super(name);
			this.name = name;
		}

		public void actionPerformed(ActionEvent e) {
			try {
				insertElement(new Element(this.name));
			} catch (DocumentValidationException ex) {
				Toolkit.getDefaultToolkit().beep();
			}
		}
	}

	/**
	 * Action for morphing offset.
	 */
	private class MorphAction extends AbstractAction {

		private String name;

		/**
		 * Class constructor.
		 * 
		 * @param name
		 *            Name of the element to which the current element is to be
		 *            morphed.
		 */
		public MorphAction(String name) {
			super(name);
			this.name = name;
		}

		public void actionPerformed(ActionEvent e) {
			try {
				morph(new Element(this.name));
			} catch (DocumentValidationException ex) {
				Toolkit.getDefaultToolkit().beep();
			}
		}
	}

	/**
	 * Runnable to layout the control.
	 */
	// private class LayoutRunnable implements Runnable {
	// private boolean force;
	// public LayoutRunnable(boolean force) {
	// this.force = force;
	// }
	//
	// public void run() {
	// relayout(force);
	// }
	// }

	/**
	 * Base class for actions in the action map. Overloads the actionPerformed
	 * method to pass a VexComponent and allow a DocumentValidationException to
	 * be returned.
	 */
	private abstract static class BaseAction extends AbstractAction {
		/**
		 * Calls <code>actionPerformed(ActionEvent e, VexComponent c)</code>,
		 * and beeps if an exception is thrown.
		 * 
		 * @param e
		 *            ActionEvent
		 */
		public void actionPerformed(ActionEvent e) {
			try {
				if (e.getSource() instanceof VexWidgetImpl) {
					this.actionPerformed(e, (VexWidgetImpl) e.getSource());
				}
			} catch (Exception ex) {
				ex.printStackTrace(); // TODO: log this
				Toolkit.getDefaultToolkit().beep();
			}
		}

		/**
		 * Performs the action. The corresponding VexComponent is provided, and
		 * any exception can be thrown.
		 * 
		 * @param e
		 *            the ActionEvent
		 * @param c
		 *            the VexComponent
		 */
		public abstract void actionPerformed(ActionEvent e, VexWidgetImpl c)
				throws Exception;

	}

	public int getHeight() {
		return impl.getHeight();
	}

	public void scrollBy(int x, int y) {
		setOrigin(originX - x, originY - y);
	}

	public void scrollTo(int x, int y) {
		setOrigin(-x, -y);
	}

	private void setOrigin(int x, int y) {
		this.originX = x;
		this.originY = y;
	}

	/**
	 * Creates the ActionMap for the component.
	 */
	private ActionMap createActionMap() {
		ActionMap am = new ActionMap();

		am.put("copy-selection", new BaseAction() {
			public void actionPerformed(ActionEvent e, VexWidgetImpl c)
					throws DocumentValidationException {
				copySelection();
			}
		});
		am.put("cut-selection", new BaseAction() {
			public void actionPerformed(ActionEvent e, VexWidgetImpl c)
					throws DocumentValidationException {
				cutSelection();
			}
		});
		am.put("delete-next-char", new BaseAction() {
			public void actionPerformed(ActionEvent e, VexWidgetImpl c)
					throws DocumentValidationException {
				c.deleteNextChar();
			}
		});
		am.put("delete-previous-char", new BaseAction() {
			public void actionPerformed(ActionEvent e, VexWidgetImpl c)
					throws DocumentValidationException {
				c.deletePreviousChar();
			}
		});
		am.put("move-to-document-end", new BaseAction() {
			public void actionPerformed(ActionEvent e, VexWidgetImpl c)
					throws DocumentValidationException {
				c.moveTo(c.getDocument().getLength() - 1, false);
			}
		});
		am.put("move-to-document-start", new BaseAction() {
			public void actionPerformed(ActionEvent e, VexWidgetImpl c)
					throws DocumentValidationException {
				c.moveTo(1, false);
			}
		});
		am.put("move-to-line-end", new BaseAction() {
			public void actionPerformed(ActionEvent e, VexWidgetImpl c)
					throws DocumentValidationException {
				c.moveToLineEnd(false);
			}
		});
		am.put("move-to-line-start", new BaseAction() {
			public void actionPerformed(ActionEvent e, VexWidgetImpl c)
					throws DocumentValidationException {
				c.moveToLineStart(false);
			}
		});
		am.put("move-to-next-char", new BaseAction() {
			public void actionPerformed(ActionEvent e, VexWidgetImpl c)
					throws DocumentValidationException {
				int offset = c.getCaretOffset();
				if (offset < c.getDocument().getLength() - 1) {
					c.moveTo(offset + 1, false);
				}
			}
		});
		am.put("move-to-next-line", new BaseAction() {
			public void actionPerformed(ActionEvent e, VexWidgetImpl c)
					throws DocumentValidationException {
				c.moveToNextLine(false);
			}
		});
		am.put("move-to-next-word", new BaseAction() {
			public void actionPerformed(ActionEvent e, VexWidgetImpl c)
					throws DocumentValidationException {
				c.moveToNextWord(false);
			}
		});
		am.put("move-to-previous-char", new BaseAction() {
			public void actionPerformed(ActionEvent e, VexWidgetImpl c)
					throws DocumentValidationException {
				int offset = c.getCaretOffset();
				if (offset > 1) {
					c.moveTo(offset - 1, false);
				}
			}
		});
		am.put("move-to-previous-line", new BaseAction() {
			public void actionPerformed(ActionEvent e, VexWidgetImpl c)
					throws DocumentValidationException {
				c.moveToPreviousLine(false);
			}
		});
		am.put("move-to-previous-word", new BaseAction() {
			public void actionPerformed(ActionEvent e, VexWidgetImpl c)
					throws DocumentValidationException {
				c.moveToPreviousWord(false);
			}
		});
		am.put("paste", new BaseAction() {
			public void actionPerformed(ActionEvent e, VexWidgetImpl c)
					throws DocumentValidationException {
				paste();
			}
		});
		am.put("paste-text", new BaseAction() {
			public void actionPerformed(ActionEvent e, VexWidgetImpl c)
					throws DocumentValidationException {
				pasteText();
			}
		});
		am.put("redo", new BaseAction() {
			public void actionPerformed(ActionEvent e, VexWidgetImpl c)
					throws DocumentValidationException {
				c.redo();
			}
		});
		am.put("select-to-document-end", new BaseAction() {
			public void actionPerformed(ActionEvent e, VexWidgetImpl c)
					throws DocumentValidationException {
				c.moveTo(c.getDocument().getLength() - 1, true);
			}
		});
		am.put("select-to-document-start", new BaseAction() {
			public void actionPerformed(ActionEvent e, VexWidgetImpl c)
					throws DocumentValidationException {
				c.moveTo(1, true);
			}
		});
		am.put("select-to-line-end", new BaseAction() {
			public void actionPerformed(ActionEvent e, VexWidgetImpl c)
					throws DocumentValidationException {
				c.moveToLineEnd(true);
			}
		});
		am.put("select-to-line-start", new BaseAction() {
			public void actionPerformed(ActionEvent e, VexWidgetImpl c)
					throws DocumentValidationException {
				c.moveToLineStart(true);
			}
		});
		am.put("select-to-next-char", new BaseAction() {
			public void actionPerformed(ActionEvent e, VexWidgetImpl c)
					throws DocumentValidationException {
				int offset = c.getCaretOffset();
				if (offset < c.getDocument().getLength() - 1) {
					c.moveTo(offset + 1, true);
				}
			}
		});
		am.put("select-to-next-line", new BaseAction() {
			public void actionPerformed(ActionEvent e, VexWidgetImpl c)
					throws DocumentValidationException {
				c.moveToNextLine(true);
			}
		});
		am.put("select-to-next-word", new BaseAction() {
			public void actionPerformed(ActionEvent e, VexWidgetImpl c)
					throws DocumentValidationException {
				c.moveToNextWord(true);
			}
		});
		am.put("select-to-previous-char", new BaseAction() {
			public void actionPerformed(ActionEvent e, VexWidgetImpl c)
					throws DocumentValidationException {
				int offset = c.getCaretOffset();
				if (offset > 1) {
					c.moveTo(offset - 1, true);
				}
			}
		});
		am.put("select-to-previous-line", new BaseAction() {
			public void actionPerformed(ActionEvent e, VexWidgetImpl c)
					throws DocumentValidationException {
				c.moveToPreviousLine(true);
			}
		});
		am.put("select-to-previous-word", new BaseAction() {
			public void actionPerformed(ActionEvent e, VexWidgetImpl c)
					throws DocumentValidationException {
				c.moveToPreviousWord(true);
			}
		});

		am.put("move-to-previous-page", new BaseAction() {
			public void actionPerformed(ActionEvent e, VexWidgetImpl c)
					throws DocumentValidationException {
				c.moveToPreviousPage(false);
			}
		});

		am.put("select-to-previous-page", new BaseAction() {
			public void actionPerformed(ActionEvent e, VexWidgetImpl c)
					throws DocumentValidationException {
				c.moveToPreviousPage(true);
			}
		});

		am.put("move-to-next-page", new BaseAction() {
			public void actionPerformed(ActionEvent e, VexWidgetImpl c)
					throws DocumentValidationException {
				c.moveToNextPage(false);
			}
		});

		am.put("select-to-next-page", new BaseAction() {
			public void actionPerformed(ActionEvent e, VexWidgetImpl c)
					throws DocumentValidationException {
				c.moveToNextPage(true);
			}
		});

		am.put("show-insert-element-popup", new BaseAction() {
			public void actionPerformed(ActionEvent e, VexWidgetImpl c)
					throws DocumentValidationException {

				VexComponent.this.showInsertElementPopup();
			}
		});
		am.put("show-morph-element-popup", new BaseAction() {
			public void actionPerformed(ActionEvent e, VexWidgetImpl c)
					throws DocumentValidationException {
				VexComponent.this.showMorphElementPopup();
			}
		});
		am.put("split", new BaseAction() {
			public void actionPerformed(ActionEvent e, VexWidgetImpl c)
					throws DocumentValidationException {
				c.split();
			}
		});
		am.put("undo", new BaseAction() {
			public void actionPerformed(ActionEvent e, VexWidgetImpl c)
					throws DocumentValidationException {
				c.undo();
			}
		});

		return am;
	}

	/**
	 * Create the input map for the control. This input map can reference both
	 * static and non-static actions.
	 */
	public static InputMap createInputMap() {
		InputMap im = new InputMap();
		im.put(KeyStroke.getKeyStroke("LEFT"), "move-to-previous-char");
		im.put(KeyStroke.getKeyStroke("RIGHT"), "move-to-next-char");
		im.put(KeyStroke.getKeyStroke("shift LEFT"), "select-to-previous-char");
		im.put(KeyStroke.getKeyStroke("shift RIGHT"), "select-to-next-char");

		im.put(KeyStroke.getKeyStroke("control LEFT"), "move-to-previous-word");
		im.put(KeyStroke.getKeyStroke("control RIGHT"), "move-to-next-word");
		im.put(KeyStroke.getKeyStroke("shift control LEFT"),
				"select-to-previous-word");
		im.put(KeyStroke.getKeyStroke("shift control RIGHT"),
				"select-to-next-word");

		im.put(KeyStroke.getKeyStroke("HOME"), "move-to-line-start");
		im.put(KeyStroke.getKeyStroke("END"), "move-to-line-end");
		im.put(KeyStroke.getKeyStroke("shift HOME"), "select-to-line-start");
		im.put(KeyStroke.getKeyStroke("shift END"), "select-to-line-end");

		im.put(KeyStroke.getKeyStroke("PAGE_UP"), "move-to-previous-page");
		im.put(KeyStroke.getKeyStroke("PAGE_DOWN"), "move-to-next-page");
		im.put(KeyStroke.getKeyStroke("shift PAGE_UP"),
				"select-to-previous-page");
		im
				.put(KeyStroke.getKeyStroke("shift PAGE_DOWN"),
						"select-to-next-page");

		im
				.put(KeyStroke.getKeyStroke("control HOME"),
						"move-to-document-start");
		im.put(KeyStroke.getKeyStroke("control END"), "move-to-document-end");
		im.put(KeyStroke.getKeyStroke("shift control HOME"),
				"select-to-document-start");
		im.put(KeyStroke.getKeyStroke("shift control END"),
				"select-to-document-end");

		im.put(KeyStroke.getKeyStroke("UP"), "move-to-previous-line");
		im.put(KeyStroke.getKeyStroke("DOWN"), "move-to-next-line");
		im.put(KeyStroke.getKeyStroke("shift UP"), "select-to-previous-line");
		im.put(KeyStroke.getKeyStroke("shift DOWN"), "select-to-next-line");

		im.put(KeyStroke.getKeyStroke("BACK_SPACE"), "delete-previous-char");
		im.put(KeyStroke.getKeyStroke("DELETE"), "delete-next-char");
		im.put(KeyStroke.getKeyStroke("ENTER"), "split");

		im.put(KeyStroke.getKeyStroke("control C"), "copy-selection");
		im.put(KeyStroke.getKeyStroke("control X"), "cut-selection");
		im.put(KeyStroke.getKeyStroke("control V"), "paste");
		im.put(KeyStroke.getKeyStroke("shift control V"), "paste-text");

		im.put(KeyStroke.getKeyStroke("control Y"), "redo");
		im.put(KeyStroke.getKeyStroke("control Z"), "undo");

		im.put(KeyStroke.getKeyStroke("control U"), "unwrap");

		im.put(KeyStroke.getKeyStroke("control SPACE"),
				"show-insert-element-popup");
		im.put(KeyStroke.getKeyStroke("control M"), "show-morph-element-popup");

		return im;
	}

	/**
	 * Fires a selection changed event to registered selection change listeners.
	 * This method suppresses events that occur while there are outstanding
	 * beginWork calls.
	 */
	private void fireSelectionChanged() {
		// if (this.beginWorkCount == 0) {
		// this.selectionProvider.fireSelectionChanged(
		// new VexComponentSelection(this));
		// }
	}

	/**
	 * Calls relayout from the Swing event loop rather than immediately.
	 * 
	 * @param force
	 *            Layout should be forced, e.g. when the width of the component
	 *            changed.
	 */
	// public void relayoutLater(boolean force) {
	// if (this.rootBox != null) {
	// SwingUtilities.invokeLater(new LayoutRunnable(force));
	// }
	// }

}