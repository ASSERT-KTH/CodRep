import org.eclipse.wst.xml.vex.core.internal.provisional.dom.IVEXElement;

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

import org.eclipse.wst.xml.vex.core.internal.core.Caret;
import org.eclipse.wst.xml.vex.core.internal.core.ColorResource;
import org.eclipse.wst.xml.vex.core.internal.core.FontMetrics;
import org.eclipse.wst.xml.vex.core.internal.core.FontResource;
import org.eclipse.wst.xml.vex.core.internal.core.FontSpec;
import org.eclipse.wst.xml.vex.core.internal.core.Graphics;
import org.eclipse.wst.xml.vex.core.internal.css.Styles;
import org.eclipse.wst.xml.vex.core.internal.dom.Element;
import org.eclipse.wst.xml.vex.core.internal.dom.IVEXElement;

/**
 * An inline box containing text. The <code>getText</code> and
 * <code>splitAt</code> methods are abstract and must be implemented by
 * subclasses.
 */
public abstract class TextBox extends AbstractBox implements InlineBox {

	private IVEXElement element;
	private int baseline;

	public static final char NEWLINE_CHAR = 0xa;
	public static final String NEWLINE_STRING = "\n";

	/**
	 * Class constructor.
	 * 
	 * @param element
	 *            Element containing the text. This is used for styling
	 *            information.
	 */
	public TextBox(IVEXElement element) {
		this.element = element;
	}


	/**
	 * Causes the box to recalculate it size. Subclasses should call this from
	 * their constructors after they are initialized.
	 * 
	 * @param context
	 *            LayoutContext used to calculate size.
	 */
	protected void calculateSize(LayoutContext context) {
		String s = this.getText();
		if (s.endsWith(NEWLINE_STRING)) {
			s = s.substring(0, s.length() - 1);
		}

		Graphics g = context.getGraphics();
		Styles styles = context.getStyleSheet().getStyles(this.getElement());
		FontResource font = g.createFont(styles.getFont());
		FontResource oldFont = g.setFont(font);
		FontMetrics fm = g.getFontMetrics();
		this.setWidth(g.stringWidth(s));
		this.setHeight(styles.getLineHeight());
		int halfLeading = (this.getHeight() - (fm.getAscent() + fm.getDescent())) / 2;
		this.baseline = halfLeading + fm.getAscent();
		g.setFont(oldFont);
		font.dispose();
	}

	/**
	 * @see org.eclipse.wst.xml.vex.core.internal.layout.InlineBox#getBaseline()
	 */
	public int getBaseline() {
		return this.baseline;
	}

	/**
	 * @see org.eclipse.wst.xml.vex.core.internal.layout.Box#getCaret(org.eclipse.wst.xml.vex.core.internal.layout.LayoutContext,
	 *      int)
	 */
	public Caret getCaret(LayoutContext context, int offset) {
		Graphics g = context.getGraphics();
		Styles styles = context.getStyleSheet().getStyles(this.element);
		FontResource oldFont = g.getFont();
		FontResource font = g.createFont(styles.getFont());
		g.setFont(font);
		char[] chars = this.getText().toCharArray();
		int x = g.charsWidth(chars, 0, offset - this.getStartOffset());
		g.setFont(oldFont);
		font.dispose();
		return new TextCaret(x, 0, this.getHeight());
	}

	/**
	 * Returns the element that controls the styling for this text element.
	 */
	public IVEXElement getElement() {
		return this.element;
	}

	/**
	 * Return the text that comprises this text box. The actual text can come
	 * from the document content or from a static string.
	 */
	public abstract String getText();

	/**
	 * Returns true if the given character is one where a linebreak should
	 * occur, e.g. a space.
	 * 
	 * @param c
	 *            the character to test
	 */
	public static boolean isSplitChar(char c) {
		return Character.isWhitespace(c);
	}

	public boolean isEOL() {
		String s = this.getText();
		return s.length() > 0 && s.charAt(s.length() - 1) == NEWLINE_CHAR;
	}

	/**
	 * Paints a string as selected text.
	 * 
	 * @param context
	 *            LayoutContext to be used. It is assumed that the contained
	 *            Graphics object is set up with the proper font.
	 * @param s
	 *            String to draw
	 * @param x
	 *            x-coordinate at which to draw the text
	 * @param y
	 *            y-coordinate at which to draw the text
	 */
	protected void paintSelectedText(LayoutContext context, String s, int x,
			int y) {
		Graphics g = context.getGraphics();

		boolean inSelectedBlock = false;
		IVEXElement e = this.getElement();
		while (e != null) {
			Styles styles = context.getStyleSheet().getStyles(e);
			if (styles.isBlock()) {
				if (context.isElementSelected(e)) {
					inSelectedBlock = true;
				}
				break;
			}
			e = e.getParent();
		}

		if (inSelectedBlock) {
			g.setColor(g.getSystemColor(ColorResource.SELECTION_BACKGROUND));
			g.drawString(s, x, y);
		} else {
			int width = g.stringWidth(s);
			g.setColor(g.getSystemColor(ColorResource.SELECTION_BACKGROUND));
			g.fillRect(x, y, width, this.getHeight());
			g.setColor(g.getSystemColor(ColorResource.SELECTION_FOREGROUND));
			g.drawString(s, x, y);
		}
	}

	protected void paintTextDecoration(LayoutContext context, Styles styles,
			String s, int x, int y) {
		int fontStyle = styles.getFont().getStyle();
		Graphics g = context.getGraphics();
		FontMetrics fm = g.getFontMetrics();

		if ((fontStyle & FontSpec.UNDERLINE) != 0) {
			int lineWidth = fm.getAscent() / 12;
			int ypos = y + fm.getAscent() + lineWidth;
			paintBaseLine(g, s, x, ypos);
		}
		if ((fontStyle & FontSpec.OVERLINE) != 0) {
			int lineWidth = fm.getAscent() / 12;
			int ypos = y + lineWidth / 2;
			paintBaseLine(g, s, x, ypos);
		}
		if ((fontStyle & FontSpec.LINE_THROUGH) != 0) {
			int ypos = y + fm.getHeight() / 2;
			paintBaseLine(g, s, x, ypos);
		}
	}

	/**
	 * Paint a line along the baseline of the text, for showing underline,
	 * overline and strike-through formatting.
	 * 
	 * @param context
	 *            LayoutContext to be used. It is assumed that the contained
	 *            Graphics object is set up with the proper font.
	 * @param x
	 *            x-coordinate at which to start drawing baseline
	 * @param y
	 *            x-coordinate at which to start drawing baseline (adjusted to
	 *            produce the desired under/over/though effect)
	 */
	protected void paintBaseLine(Graphics g, String s, int x, int y) {
		FontMetrics fm = g.getFontMetrics();
		int width = g.stringWidth(s);
		int lineWidth = fm.getAscent() / 12;
		g.setLineStyle(Graphics.LINE_SOLID);
		g.setLineWidth(lineWidth);
		g.drawLine(x, y, x + width, y);
	}

	/**
	 * @see org.eclipse.wst.xml.vex.core.internal.layout.InlineBox#split(org.eclipse.wst.xml.vex.core.internal.layout.LayoutContext,
	 *      int, boolean)
	 */
	public Pair split(LayoutContext context, int maxWidth, boolean force) {

		char[] chars = this.getText().toCharArray();

		if (chars.length == 0) {
			throw new IllegalStateException();
		}

		Graphics g = context.getGraphics();
		Styles styles = context.getStyleSheet().getStyles(this.element);
		FontResource font = g.createFont(styles.getFont());
		FontResource oldFont = g.setFont(font);

		int split = 0;
		int next = 1;
		boolean eol = false; // end of line found
		while (next < chars.length) {
			if (isSplitChar(chars[next - 1])) {
				if (g.charsWidth(chars, 0, next) <= maxWidth) {
					split = next;
					if (chars[next - 1] == NEWLINE_CHAR) {
						eol = true;
						break;
					}
				} else {
					break;
				}
			}
			next++;
		}

		if (force && split == 0) {
			// find some kind of split
			split = 1;
			while (split < chars.length) {
				if (g.charsWidth(chars, 0, split + 1) > maxWidth) {
					break;
				}
				split++;
			}

		}

		// include any trailing spaces in the split
		// this also grabs any leading spaces when split==0
		if (!eol) {
			while (split < chars.length - 1 && chars[split] == ' ') {
				split++;
			}
		}

		g.setFont(oldFont);
		font.dispose();

		return this.splitAt(context, split);
	}

	/**
	 * Return a pair of boxes representing a split at the given offset. If split
	 * is zero, then the returned left box should be null. If the split is equal
	 * to the length of the text, then the right box should be null.
	 * 
	 * @param context
	 *            LayoutContext used to calculate the sizes of the resulting
	 *            boxes.
	 * @param offset
	 *            location of the split, relative to the start of the text box.
	 * @return
	 */
	public abstract Pair splitAt(LayoutContext context, int offset);

	/**
	 * @see java.lang.Object#toString()
	 */
	public String toString() {
		return this.getText();
	}

}