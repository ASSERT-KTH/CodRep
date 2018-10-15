import org.eclipse.wst.xml.vex.core.internal.provisional.dom.I.VEXElement;

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
package org.eclipse.wst.xml.vex.core.internal.layout;

import org.eclipse.wst.xml.vex.core.internal.core.ColorResource;
import org.eclipse.wst.xml.vex.core.internal.core.FontResource;
import org.eclipse.wst.xml.vex.core.internal.core.Graphics;
import org.eclipse.wst.xml.vex.core.internal.css.Styles;
import org.eclipse.wst.xml.vex.core.internal.dom.Element;
import org.eclipse.wst.xml.vex.core.internal.provisional.dom.VEXElement;

/**
 * A TextBox representing a static string. Represents text which is not editable
 * within the VexWidget, such as enumerated list markers.
 */
public class StaticTextBox extends TextBox {

	public static final byte NO_MARKER = 0;
	public static final byte START_MARKER = 1;
	public static final byte END_MARKER = 2;

	private String text;
	private byte marker;

	/**
	 * Class constructor.
	 * 
	 * @param context
	 *            LayoutContext used to calculate the box's size.
	 * @param element
	 *            Element used to style the text.
	 * @param text
	 *            Static text to display
	 */
	public StaticTextBox(LayoutContext context, VEXElement element, String text) {
		this(context, element, text, NO_MARKER);
		if (text.length() == 0) {
			throw new IllegalArgumentException(
					"StaticTextBox cannot have an empty text string.");
		}
	}

	/**
	 * Class constructor. This constructor is used when generating a static text
	 * box representing a marker for the start or end of an inline element. If
	 * the selection spans the related marker, the text is drawn in the
	 * platform's text selection colours.
	 * 
	 * @param context
	 *            LayoutContext used to calculate the box's size
	 * @param element
	 *            Element used to style the text
	 * @param text
	 *            Static text to display
	 * @param marker
	 *            START_MARKER or END_MARKER, depending on whether the text
	 *            represents the start sentinel or the end sentinel of the
	 *            element
	 */
	public StaticTextBox(LayoutContext context, VEXElement element, String text,
			byte marker) {
		super(element);
		this.text = text;
		this.marker = marker;
		this.calculateSize(context);
	}

	/**
	 * @see org.eclipse.wst.xml.vex.core.internal.layout.TextBox#getText()
	 */
	public String getText() {
		return this.text;
	}

	/**
	 * @see org.eclipse.wst.xml.vex.core.internal.layout.Box#hasContent()
	 */
	public boolean hasContent() {
		return false;
	}

	/**
	 * @see org.eclipse.wst.xml.vex.core.internal.layout.Box#paint(org.eclipse.wst.xml.vex.core.internal.layout.LayoutContext,
	 *      int, int)
	 */
	public void paint(LayoutContext context, int x, int y) {

		Styles styles = context.getStyleSheet().getStyles(this.getElement());
		Graphics g = context.getGraphics();

		boolean drawSelected = false;
		if (this.marker == START_MARKER) {
			drawSelected = this.getElement().getStartOffset() >= context
					.getSelectionStart()
					&& this.getElement().getStartOffset() + 1 <= context
							.getSelectionEnd();
		} else if (this.marker == END_MARKER) {
			drawSelected = this.getElement().getEndOffset() >= context
					.getSelectionStart()
					&& this.getElement().getEndOffset() + 1 <= context
							.getSelectionEnd();
		}

		FontResource font = g.createFont(styles.getFont());
		ColorResource color = g.createColor(styles.getColor());

		FontResource oldFont = g.setFont(font);
		ColorResource oldColor = g.setColor(color);

		if (drawSelected) {
			this.paintSelectedText(context, this.getText(), x, y);
		} else {
			g.drawString(this.getText(), x, y);
		}
		paintTextDecoration(context, styles, this.getText(), x, y);

		g.setFont(oldFont);
		g.setColor(oldColor);
		font.dispose();
		color.dispose();
	}

	/**
	 * @see org.eclipse.wst.xml.vex.core.internal.layout.TextBox#splitAt(int)
	 */
	public Pair splitAt(LayoutContext context, int offset) {

		StaticTextBox left;
		if (offset == 0) {
			left = null;
		} else {
			left = new StaticTextBox(context, this.getElement(), this.getText()
					.substring(0, offset), this.marker);
		}

		StaticTextBox right;
		if (offset == this.getText().length()) {
			right = null;
		} else {
			right = new StaticTextBox(context, this.getElement(), this
					.getText().substring(offset), this.marker);
		}
		return new Pair(left, right);
	}

}