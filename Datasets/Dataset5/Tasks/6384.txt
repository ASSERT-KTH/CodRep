package org.eclipse.ecf.internal.ui.deprecated.views;

/*******************************************************************************
 * Copyright (c) 2005 IBM Corporation and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     IBM Corporation - initial API and implementation
 *******************************************************************************/
package org.eclipse.ecf.ui.views;

import java.util.ArrayList;
import java.util.List;

import org.eclipse.jface.resource.JFaceColors;
import org.eclipse.jface.text.ITextSelection;
import org.eclipse.jface.text.TextSelection;
import org.eclipse.jface.viewers.ISelection;
import org.eclipse.jface.viewers.ISelectionChangedListener;
import org.eclipse.jface.viewers.ISelectionProvider;
import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.StyleRange;
import org.eclipse.swt.custom.StyledText;
import org.eclipse.swt.events.MouseAdapter;
import org.eclipse.swt.events.MouseEvent;
import org.eclipse.swt.events.MouseMoveListener;
import org.eclipse.swt.graphics.Color;
import org.eclipse.swt.graphics.Cursor;
import org.eclipse.swt.graphics.Point;
import org.eclipse.swt.layout.FillLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.swt.widgets.Text;

/**
 * A simple link text viewer wraps a read-only SWT StyledText and allows plain
 * text and links to be appended to the text. For each link, a runnable is
 * maintained that will be run when the user clicks on the link.
 * 
 * @since 0.5.4
 * 
 */
public class SimpleLinkTextViewer implements ISelectionProvider {

	private Color hyperlinkColor = null;

	private Color getHyperlinkColor() {
		if (hyperlinkColor == null) {
			hyperlinkColor = JFaceColors.getActiveHyperlinkText(Display
					.getDefault());
			if (hyperlinkColor == null) {
				hyperlinkColor = new Color(Display.getDefault(), 0, 0, 255);
			}
		}
		return hyperlinkColor;
	}

	private Cursor cursor;

	private List links = new ArrayList();

	private StyledText styledText;

	private List listeners = new ArrayList();

	/**
	 * Creates a new chat text viewer in the given composite.
	 * 
	 * @param composite
	 */
	public SimpleLinkTextViewer(Composite composite, int style) {
		styledText = new StyledText(composite, style);
		styledText.addMouseListener(new MouseAdapter() {
			public void mouseUp(MouseEvent e) {
				LinkInfo linkInfo = null;
				synchronized (SimpleLinkTextViewer.this) {
					if (styledText.isDisposed())
						return;
					linkInfo = findLinkInfo(e);
				}
				if (linkInfo != null) {
					linkInfo.runnable.run();
				}
			}
		});
		styledText.addMouseMoveListener(new MouseMoveListener() {
			public void mouseMove(MouseEvent e) {
				synchronized (SimpleLinkTextViewer.this) {
					if (styledText.isDisposed())
						return;
					LinkInfo linkInfo = findLinkInfo(e);
					if (linkInfo != null) {
						setHandCursor();
					} else {
						resetCursor();
					}
				}
			}
		});
	}

	/**
	 * Appends the given text to the underlying StyledText widget.
	 * 
	 * @param text
	 */
	public synchronized void append(String text) {
		if (styledText.isDisposed())
			return;
		styledText.append(text);
	}

	/**
	 * Appends the given text as a link to the underlying StyledText widget. The
	 * given runnable will be run when the user clicks on the link.
	 * 
	 * @param text
	 */
	public synchronized void appendLink(String text, Runnable onClick) {
		if (styledText.isDisposed())
			return;
		int start = styledText.getCharCount();
		styledText.replaceTextRange(start, 0, text);
		StyleRange styleRange = new StyleRange();
		styleRange.start = start;
		styleRange.length = text.length();
		styleRange.foreground = getHyperlinkColor();
		styleRange.underline = true;
		styledText.setStyleRange(styleRange);
		links.add(new LinkInfo(start, text.length(), onClick));
	}

	private LinkInfo findLinkInfoFromOffset(int offset) {
		int low = -1;
		int high = links.size();
		while (high - low > 1) {
			int index = (high + low) / 2;
			LinkInfo linkInfo = (LinkInfo) links.get(index);
			if (offset < linkInfo.start) {
				high = index;
			} else {
				low = index;
			}
		}
		if (low == -1)
			return null;
		LinkInfo result = (LinkInfo) links.get(low);
		if (result.start <= offset && offset < result.start + result.length)
			return result;
		return null;
	}

	private LinkInfo findLinkInfo(MouseEvent e) {
		Point point = new Point(e.x, e.y);
		LinkInfo linkInfo = null;
		if (styledText.getBounds().contains(point)
				&& styledText.getCharCount() > 0) {
			try {
				int offset = styledText.getOffsetAtLocation(point);
				linkInfo = findLinkInfoFromOffset(offset);
			} catch (IllegalArgumentException ex) {
				// ignore - event was not over character
			}
		}
		return linkInfo;
	}

	private void resetCursor() {
		styledText.setCursor(null);
		if (cursor != null) {
			cursor.dispose();
			cursor = null;
		}
	}

	private void setHandCursor() {
		Display display = styledText.getDisplay();
		if (cursor == null)
			cursor = new Cursor(display, SWT.CURSOR_HAND);
		styledText.setCursor(cursor);
	}

	/**
	 * main method for testing purposes (right-click and select Run As->SWT
	 * Application)
	 * 
	 * @param args
	 */
	public static void main(String[] args) {
		Display display = new Display();
		Shell shell = new Shell(display);
		shell.setText(SimpleLinkTextViewer.class.getName());
		shell.setLayout(new FillLayout());
		SimpleLinkTextViewer chatTextViewer = new SimpleLinkTextViewer(shell,
				SWT.V_SCROLL | SWT.H_SCROLL | SWT.WRAP | SWT.BORDER
						| SWT.READ_ONLY);
		chatTextViewer.append("Hello world\n");
		chatTextViewer.append("Hello ");
		chatTextViewer.appendLink("linked", new Runnable() {

			public void run() {
				System.out.println("clicked!");
			}
		});
		chatTextViewer.append(" world\n");
		chatTextViewer.append("Hello world\n");
		Text secondText = new Text(shell, SWT.BORDER);
		secondText.setText("some other focusable text");
		secondText.forceFocus();
		shell.layout();
		shell.open();
		while (!shell.isDisposed()) {
			if (!display.readAndDispatch())
				display.sleep();
		}
		display.dispose();
	}

	private static class LinkInfo {
		private final int start;

		private final int length;

		private final Runnable runnable;

		private LinkInfo(int start, int length, Runnable runnable) {
			this.start = start;
			this.length = length;
			this.runnable = runnable;
		}
	}

	public StyledText getTextWidget() {

		return styledText;
	}

	public Control getControl() {
		return getTextWidget();
	}

	public void addSelectionChangedListener(ISelectionChangedListener listener) {
		if (!listeners.contains(listener)) {
			listeners.add(listener);
		}
	}

	public ISelection getSelection() {
		ISelection selection = new TextSelection(
				styledText.getSelectionRange().x, styledText
						.getSelectionRange().y);

		return selection;
	}

	public void removeSelectionChangedListener(
			ISelectionChangedListener listener) {
		if (listeners.contains(listener)) {
			listeners.remove(listener);
		}
	}

	public void setSelection(ISelection selection) {
		if (selection instanceof ITextSelection) {
			ITextSelection textSelection = (ITextSelection) selection;
			styledText.setSelection(textSelection.getOffset(), textSelection
					.getOffset()
					+ textSelection.getLength());
		}
	}

}