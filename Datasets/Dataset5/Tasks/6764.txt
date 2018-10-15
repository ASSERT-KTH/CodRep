package org.eclipse.wst.xml.vex.ui.internal.swt;

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
package org.eclipse.wst.xml.vex.core.internal.swt;

import org.eclipse.swt.SWT;
import org.eclipse.swt.graphics.FontData;
import org.eclipse.swt.graphics.GC;
import org.eclipse.swt.widgets.Display;
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
 * 
 * <p>
 * The GC given to us by SWT is that of the Canvas, which is just a viewport
 * into the document. This class therefore implements an "origin", which
 * represents the top-left corner of the document relative to the top-left
 * corner of the canvas. The x- and y-coordinates of the origin are always
 * negative.
 * </p>
 * .
 */
public class SwtGraphics implements Graphics {

	private GC gc;
	private int originX;
	private int originY;

	/**
	 * Class constructor.
	 * 
	 * @param gc
	 *            SWT GC to which we are drawing.
	 */
	public SwtGraphics(GC gc) {
		this.gc = gc;
	}

	public void dispose() {
		this.gc.dispose();
	}

	public void drawChars(char[] chars, int offset, int length, int x, int y) {
		this.drawString(new String(chars, offset, length), x, y);

	}

	public void drawLine(int x1, int y1, int x2, int y2) {
		this.gc
				.drawLine(x1 + originX, y1 + originY, x2 + originX, y2
						+ originY);
	}

	public void drawOval(int x, int y, int width, int height) {
		this.gc.drawOval(x + originX, y + originY, width, height);
	}

	public void drawRect(int x, int y, int width, int height) {
		this.gc.drawRectangle(x + originX, y + originY, width, height);
	}

	public void drawString(String s, int x, int y) {
		this.gc.drawString(s, x + originX, y + originY, true);
	}

	/**
	 * Fills the given oval with the <em>foreground</em> color. This overrides
	 * the default SWT behaviour to be more like Swing.
	 */
	public void fillOval(int x, int y, int width, int height) {
		this.gc.fillOval(x + originX, y + originY, width, height);
	}

	/**
	 * Fills the given rectangle with the <em>foreground</em> color. This
	 * overrides the default SWT behaviour to be more like Swing.
	 */
	public void fillRect(int x, int y, int width, int height) {
		this.gc.fillRectangle(x + originX, y + originY, width, height);
	}

	public Rectangle getClipBounds() {
		org.eclipse.swt.graphics.Rectangle r = this.gc.getClipping();
		return new Rectangle(r.x - this.originX, r.y - this.originY, r.width,
				r.height);
	}

	public ColorResource getColor() {
		return new SwtColor(this.gc.getForeground());
	}

	public FontResource getFont() {
		return new SwtFont(this.gc.getFont());
	}

	public FontMetrics getFontMetrics() {
		return new SwtFontMetrics(this.gc.getFontMetrics());
	}

	public int getLineStyle() {
		return this.lineStyle;
	}

	public int getLineWidth() {
		return this.gc.getLineWidth();
	}

	public boolean isAntiAliased() {
		return false;
	}

	public void setAntiAliased(boolean antiAliased) {
	}

	public ColorResource setColor(ColorResource color) {
		ColorResource oldColor = this.getColor();
		this.gc.setForeground(((SwtColor) color).getSwtColor());
		this.gc.setBackground(((SwtColor) color).getSwtColor());
		return oldColor;
	}

	public FontResource setFont(FontResource font) {
		FontResource oldFont = this.getFont();
		this.gc.setFont(((SwtFont) font).getSwtFont());
		return oldFont;
	}

	public void setLineStyle(int lineStyle) {
		this.lineStyle = lineStyle;
		switch (lineStyle) {
		case LINE_DASH:
			this.gc.setLineStyle(SWT.LINE_DASH);
			break;
		case LINE_DOT:
			this.gc.setLineStyle(SWT.LINE_DOT);
			break;
		default:
			this.gc.setLineStyle(SWT.LINE_SOLID);
			break;
		}
	}

	public void setLineWidth(int lineWidth) {
		this.gc.setLineWidth(lineWidth);
	}

	public int charsWidth(char[] data, int offset, int length) {
		return this.stringWidth(new String(data, offset, length));
	}

	public ColorResource createColor(Color rgb) {
		return new SwtColor(new org.eclipse.swt.graphics.Color(null, rgb
				.getRed(), rgb.getGreen(), rgb.getBlue()));
	}

	public FontResource createFont(FontSpec fontSpec) {
		int style = SWT.NORMAL;
		if ((fontSpec.getStyle() & FontSpec.BOLD) > 0) {
			style |= SWT.BOLD;
		}
		if ((fontSpec.getStyle() & FontSpec.ITALIC) > 0) {
			style |= SWT.ITALIC;
		}
		int size = Math.round(fontSpec.getSize() * 72 / 90); // TODO: fix. SWT
																// uses pts, AWT
																// uses device
																// units
		String[] names = fontSpec.getNames();
		FontData[] fd = new FontData[names.length];
		for (int i = 0; i < names.length; i++) {
			fd[i] = new FontData(names[i], size, style);
		}
		return new SwtFont(new org.eclipse.swt.graphics.Font(null, fd));
	}

	public ColorResource getSystemColor(int id) {

		if (id == ColorResource.SELECTION_BACKGROUND) {
			return new SwtColor(Display.getCurrent().getSystemColor(
					SWT.COLOR_LIST_SELECTION));
		} else if (id == ColorResource.SELECTION_FOREGROUND) {
			return new SwtColor(Display.getCurrent().getSystemColor(
					SWT.COLOR_LIST_SELECTION_TEXT));
		} else {
			return new SwtColor(Display.getCurrent().getSystemColor(-1));
		}
	}

	/**
	 * Sets the origin of this graphics object. See the class description for
	 * more details.
	 * 
	 * @param x
	 *            x-coordinate of the origin, relative to the viewport.
	 * @param y
	 *            y-coordinate of the origin, relative to the viewport.
	 */
	public void setOrigin(int x, int y) {
		this.originX = x;
		this.originY = y;
	}

	public int stringWidth(String s) {
		return this.gc.stringExtent(s).x;
	}

	// ========================================================== PRIVATE

	private int lineStyle = LINE_SOLID;

}