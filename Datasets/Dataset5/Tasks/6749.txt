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

import java.awt.BasicStroke;
import java.awt.GraphicsEnvironment;
import java.awt.Stroke;
import java.util.HashSet;
import java.util.Set;

import javax.swing.UIManager;

import org.eclipse.wst.xml.vex.core.internal.core.Color;
import org.eclipse.wst.xml.vex.core.internal.core.ColorResource;
import org.eclipse.wst.xml.vex.core.internal.core.FontMetrics;
import org.eclipse.wst.xml.vex.core.internal.core.FontResource;
import org.eclipse.wst.xml.vex.core.internal.core.FontSpec;
import org.eclipse.wst.xml.vex.core.internal.core.Graphics;
import org.eclipse.wst.xml.vex.core.internal.core.Rectangle;

/**
 * Implementation of the Vex Graphics interface, mapping it to a
 * org.eclipse.swt.graphics.GC object.
 */
public class AwtGraphics implements Graphics {

	private java.awt.Graphics2D g;
	private int originX;
	private int originY;

	private static Set availableFontFamilies = new HashSet();

	static {
		GraphicsEnvironment ge = GraphicsEnvironment
				.getLocalGraphicsEnvironment();
		String[] names = ge.getAvailableFontFamilyNames();
		for (int i = 0; i < names.length; i++) {
			availableFontFamilies.add(names[i].toLowerCase());
		}
	}

	/**
	 * Class constructor.
	 * 
	 * @param gc
	 *            SWT GC to which we are drawing.
	 */
	public AwtGraphics(java.awt.Graphics2D g) {
		this.g = g;
	}

	public void dispose() {
	}

	public void drawChars(char[] chars, int offset, int length, int x, int y) {
		this.g.drawString(new String(chars, offset, length), x + originX, y
				+ originY + this.g.getFontMetrics().getAscent());
	}

	public void drawLine(int x1, int y1, int x2, int y2) {
		this.g.drawLine(x1 + originX, y1 + originY, x2 + originX, y2 + originY);
	}

	public void drawOval(int x, int y, int width, int height) {
		this.g.drawOval(x + originX, y + originY, width, height);
	}

	public void drawRect(int x, int y, int width, int height) {
		this.g.drawRect(x + originX, y + originY, width, height);
	}

	public void drawString(String s, int x, int y) {
		this.g.drawString(s, x + originX, y + originY
				+ this.g.getFontMetrics().getAscent());
	}

	public void fillOval(int x, int y, int width, int height) {
		this.g.fillOval(x + originX, y + originY, width, height);
	}

	public void fillRect(int x, int y, int width, int height) {
		this.g.fillRect(x + originX, y + originY, width, height);
	}

	public Rectangle getClipBounds() {
		java.awt.Rectangle r = this.g.getClipBounds();
		return new Rectangle(r.x - originX, r.y - originY, r.width, r.height);
	}

	public ColorResource getColor() {
		return new AwtColor(this.g.getColor());
	}

	public FontResource getFont() {
		return new AwtFont(this.g.getFont());
	}

	public FontMetrics getFontMetrics() {
		return new AwtFontMetrics(this.g.getFontMetrics());
	}

	public int getLineStyle() {
		return this.lineStyle;
	}

	public int getLineWidth() {
		return this.lineWidth;
	}

	public boolean isAntiAliased() {
		return false;
	}

	public void setAntiAliased(boolean antiAliased) {
	}

	public ColorResource setColor(ColorResource color) {
		ColorResource oldColor = this.getColor();
		this.g.setColor(((AwtColor) color).getAwtColor());
		return oldColor;
	}

	public FontResource setFont(FontResource font) {
		FontResource oldFont = this.getFont();
		this.g.setFont(((AwtFont) font).getAwtFont());
		return oldFont;
	}

	public void setLineStyle(int lineStyle) {
		this.lineStyle = lineStyle;
		this.makeStroke();
	}

	public void setLineWidth(int lineWidth) {
		this.lineWidth = lineWidth;
		this.makeStroke();
	}

	public int charsWidth(char[] data, int offset, int length) {
		return this.stringWidth(new String(data, offset, length));
	}

	public void setOrigin(int x, int y) {
		this.originX = x;
		this.originY = y;
	}

	public ColorResource createColor(Color rgb) {
		return new AwtColor(new java.awt.Color(rgb.getRed(), rgb.getGreen(),
				rgb.getBlue()));
	}

	public FontResource createFont(FontSpec fontSpec) {
		int style = java.awt.Font.PLAIN;
		if ((fontSpec.getStyle() & FontSpec.BOLD) > 0) {
			style |= java.awt.Font.BOLD;
		}
		if ((fontSpec.getStyle() & FontSpec.ITALIC) > 0) {
			style |= java.awt.Font.ITALIC;
		}
		int size = Math.round(fontSpec.getSize());

		String name = "sans-serif";
		String[] names = fontSpec.getNames();
		for (int i = 0; i < names.length; i++) {
			if (availableFontFamilies.contains(names[i])) {
				name = names[i];
				break;
			}
		}
		return new AwtFont(new java.awt.Font(name, style, size));
	}

	public ColorResource getSystemColor(int id) {

		if (id == ColorResource.SELECTION_BACKGROUND) {
			return new AwtColor(UIManager
					.getColor("TextPane.selectionBackground"));
		} else if (id == ColorResource.SELECTION_FOREGROUND) {
			return new AwtColor(UIManager
					.getColor("TextPane.selectionForeground"));
		} else {
			return new AwtColor(java.awt.Color.BLACK);
		}
	}

	public int stringWidth(String s) {
		return this.g.getFontMetrics().stringWidth(s);
	}

	// ============================================================= PRIVATE

	private int lineWidth = 1;
	private int lineStyle;

	private void makeStroke() {

		float dashLength = this.lineWidth;
		if (this.lineStyle == LINE_DASH) {
			dashLength = 3 * this.lineWidth;
		}

		Stroke stroke = new BasicStroke((float) this.lineWidth,
				BasicStroke.CAP_SQUARE, // to be compatible with SWT GC
				BasicStroke.JOIN_MITER, 1.0f, new float[] { dashLength,
						dashLength }, 0.0f);

		this.g.setStroke(stroke);
	}

}