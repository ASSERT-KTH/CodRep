setAttribute(FigureAttributeConstant.FILL_COLOR, ColorMap.color("None"));

/*
 * @(#)TextFigure.java
 *
 * Project:		JHotdraw - a GUI framework for technical drawings
 *				http://www.jhotdraw.org
 *				http://jhotdraw.sourceforge.net
 * Copyright:	© by the original author(s) and all contributors
 * License:		Lesser GNU Public License (LGPL)
 *				http://www.opensource.org/licenses/lgpl-license.html
 */

package CH.ifa.draw.figures;

import java.util.*;
import java.util.List;
import java.awt.*;
import java.io.*;
import CH.ifa.draw.framework.*;
import CH.ifa.draw.standard.*;
import CH.ifa.draw.util.*;

/**
 * A text figure.
 *
 * @see TextTool
 *
 * @version <$CURRENT_VERSION$>
 */
public  class TextFigure
		extends AttributeFigure
		implements FigureChangeListener, TextHolder {

	private int               fOriginX;
	private int               fOriginY;

	// cache of the TextFigure's size
	transient private boolean fSizeIsDirty = true;
	transient private int     fWidth;
	transient private int     fHeight;

	private String  fText;
	private Font    fFont;
	private boolean fIsReadOnly;

	private Figure  fObservedFigure = null;
	private OffsetLocator fLocator = null;

	private static String fgCurrentFontName  = "Helvetica";
	private static int    fgCurrentFontSize  = 12;
	private static int    fgCurrentFontStyle = Font.PLAIN;

	/*
	 * Serialization support.
	 */
	private static final long serialVersionUID = 4599820785949456124L;
	private int textFigureSerializedDataVersion = 1;

	public TextFigure() {
		fOriginX = 0;
		fOriginY = 0;
		fFont = createCurrentFont();
		setAttribute(FigureAttributeConstant.FILL_COLOR.getName(), ColorMap.color("None"));
		fText = new String("");
		fSizeIsDirty = true;
	}

	public void moveBy(int x, int y) {
		willChange();
		basicMoveBy(x, y);
		if (fLocator != null) {
			fLocator.moveBy(x, y);
		}
		changed();
	}

	protected void basicMoveBy(int x, int y) {
		fOriginX += x;
		fOriginY += y;
	}

	public void basicDisplayBox(Point newOrigin, Point newCorner) {
		fOriginX = newOrigin.x;
		fOriginY = newOrigin.y;
	}

	public Rectangle displayBox() {
		Dimension extent = textExtent();
		return new Rectangle(fOriginX, fOriginY, extent.width, extent.height);
	}

	public Rectangle textDisplayBox() {
		return displayBox();
	}

	/**
	 * Tests whether this figure is read only.
	 */
	public boolean readOnly() {
		return fIsReadOnly;
	}

	/**
	 * Sets the read only status of the text figure.
	 */
	public void setReadOnly(boolean isReadOnly) {
		fIsReadOnly = isReadOnly;
	}

	/**
	 * Gets the font.
	 */
	public Font getFont() {
		return fFont;
	}

	/**
	 * Sets the font.
	 */
	public void setFont(Font newFont) {
		willChange();
		fFont = newFont;
		markDirty();
		changed();
	}

	/**
	 * Updates the location whenever the figure changes itself.
	 */
	public void changed() {
		super.changed();
		updateLocation();
	}

	/**
	 * A text figure understands the "FontSize", "FontStyle", and "FontName"
	 * attributes.
	 *
	 * @deprecated use getAttribute(FigureAttributeConstant) instead
	 */
	public Object getAttribute(String name) {
		return getAttribute(FigureAttributeConstant.getConstant(name));
	}

	/**
	 * A text figure understands the "FontSize", "FontStyle", and "FontName"
	 * attributes.
	 */
	public Object getAttribute(FigureAttributeConstant attributeConstant) {
		Font font = getFont();
		if (attributeConstant.equals(FigureAttributeConstant.FONT_SIZE)) {
			return new Integer(font.getSize());
		}
		if (attributeConstant.equals(FigureAttributeConstant.FONT_STYLE)) {
			return new Integer(font.getStyle());
		}
		if (attributeConstant.equals(FigureAttributeConstant.FONT_NAME)) {
			return font.getName();
		}
		return super.getAttribute(attributeConstant);
	}

	/**
	 * A text figure understands the "FontSize", "FontStyle", and "FontName"
	 * attributes.
	 *
	 * @deprecated use setAttribute(FigureAttributeConstant, Object) instead
	 */
	public void setAttribute(String name, Object value) {
		setAttribute(FigureAttributeConstant.getConstant(name), value);
	}

	/**
	 * A text figure understands the "FontSize", "FontStyle", and "FontName"
	 * attributes.
	 */
	public void setAttribute(FigureAttributeConstant attributeConstant, Object value) {
		Font font = getFont();
		if (attributeConstant.equals(FigureAttributeConstant.FONT_SIZE)) {
			Integer s = (Integer)value;
			setFont(new Font(font.getName(), font.getStyle(), s.intValue()) );
		}
		else if (attributeConstant.equals(FigureAttributeConstant.FONT_STYLE)) {
			Integer s = (Integer)value;
			int style = font.getStyle();
			if (s.intValue() == Font.PLAIN) {
				style = font.PLAIN;
			}
			else {
				style = style ^ s.intValue();
			}
			setFont(new Font(font.getName(), style, font.getSize()) );
		}
		else if (attributeConstant.equals(FigureAttributeConstant.FONT_NAME)) {
			String n = (String)value;
			setFont(new Font(n, font.getStyle(), font.getSize()) );
		}
		else {
			super.setAttribute(attributeConstant, value);
		}
	}

	/**
	 * Gets the text shown by the text figure.
	 */
	public String getText() {
		return fText;
	}

	/**
	 * Sets the text shown by the text figure.
	 */
	public void setText(String newText) {
		if (!newText.equals(fText)) {
			willChange();
			fText = new String(newText);
			markDirty();
			changed();
		}
	}

	/**
	 * Tests whether the figure accepts typing.
	 */
	public boolean acceptsTyping() {
		return !fIsReadOnly;
	}

	public void drawBackground(Graphics g) {
		Rectangle r = displayBox();
		g.fillRect(r.x, r.y, r.width, r.height);
	}

	public void drawFrame(Graphics g) {
		g.setFont(fFont);
		g.setColor((Color) getAttribute(FigureAttributeConstant.TEXT_COLOR));
		FontMetrics metrics = g.getFontMetrics(fFont);
		g.drawString(fText, fOriginX, fOriginY + metrics.getAscent());
	}

	protected Dimension textExtent() {
		if (!fSizeIsDirty) {
			return new Dimension(fWidth, fHeight);
		}
		FontMetrics metrics = Toolkit.getDefaultToolkit().getFontMetrics(fFont);
		fWidth = metrics.stringWidth(fText);
		fHeight = metrics.getHeight();
		fSizeIsDirty = false;
		return new Dimension(metrics.stringWidth(fText), metrics.getHeight());
	}

	protected void markDirty() {
		fSizeIsDirty = true;
	}

	/**
	 * Gets the number of columns to be overlaid when the figure is edited.
	 */
	public int overlayColumns() {
		int length = getText().length();
		int columns = 20;
		if (length != 0) {
			columns = getText().length()+ 3;
		}
		return columns;
	}

	public HandleEnumeration handles() {
		List handles = CollectionsFactory.current().createList();
		handles.add(new NullHandle(this, RelativeLocator.northWest()));
		handles.add(new NullHandle(this, RelativeLocator.northEast()));
		handles.add(new NullHandle(this, RelativeLocator.southEast()));
		handles.add(new FontSizeHandle(this, RelativeLocator.southWest()));
		return new HandleEnumerator(handles);
	}

	public void write(StorableOutput dw) {
		super.write(dw);
		dw.writeInt(fOriginX);
		dw.writeInt(fOriginY);
		dw.writeString(fText);
		dw.writeString(fFont.getName());
		dw.writeInt(fFont.getStyle());
		dw.writeInt(fFont.getSize());
		dw.writeBoolean(fIsReadOnly);
		dw.writeStorable(fObservedFigure);
		dw.writeStorable(fLocator);
	}

	public void read(StorableInput dr) throws IOException {
		super.read(dr);
		markDirty();
		fOriginX = dr.readInt();
		fOriginY = dr.readInt();
		fText = dr.readString();
		fFont = new Font(dr.readString(), dr.readInt(), dr.readInt());
		fIsReadOnly = dr.readBoolean();

		fObservedFigure = (Figure)dr.readStorable();
		if (fObservedFigure != null) {
			fObservedFigure.addFigureChangeListener(this);
		}
		fLocator = (OffsetLocator)dr.readStorable();
	}

	private void readObject(ObjectInputStream s) throws ClassNotFoundException, IOException {

		s.defaultReadObject();

		if (fObservedFigure != null) {
			fObservedFigure.addFigureChangeListener(this);
		}
		markDirty();
	}

	public void connect(Figure figure) {
		if (fObservedFigure != null) {
			fObservedFigure.removeFigureChangeListener(this);
		}

		fObservedFigure = figure;
		fLocator = new OffsetLocator(figure.connectedTextLocator(this));
		fObservedFigure.addFigureChangeListener(this);
		updateLocation();
	}

	public void figureChanged(FigureChangeEvent e) {
		updateLocation();
	}

	public void figureRemoved(FigureChangeEvent e) {
		if (listener() != null) {
			listener().figureRequestRemove(new FigureChangeEvent(this));
		}
	}

	public void figureRequestRemove(FigureChangeEvent e) {}
	public void figureInvalidated(FigureChangeEvent e) {}
	public void figureRequestUpdate(FigureChangeEvent e) {}

	/**
	 * Updates the location relative to the connected figure.
	 * The TextFigure is centered around the located point.
	 */
	protected void updateLocation() {
		if (fLocator != null) {
			Point p = fLocator.locate(fObservedFigure);

			p.x -= size().width/2 + fOriginX;
			p.y -= size().height/2 + fOriginY;
			if (p.x != 0 || p.y != 0) {
				willChange();
				basicMoveBy(p.x, p.y);
				changed();
			}
		}
	}

	public void release() {
		super.release();
		disconnect(fObservedFigure);
		fObservedFigure = null;
	}

	/**
	 * Disconnects a text holder from a connect figure.
	 */
	public void disconnect(Figure disconnectFigure) {
		if (disconnectFigure != null) {
			disconnectFigure.removeFigureChangeListener(this);
		}
		fLocator = null;
	}


	/**
	 * Creates the current font to be used for new text figures.
	 */
	static public Font createCurrentFont() {
		return new Font(fgCurrentFontName, fgCurrentFontStyle, fgCurrentFontSize);
	}

	/**
	 * Sets the current font name
	 */
	static public void setCurrentFontName(String name) {
		fgCurrentFontName = name;
	}

	/**
	 * Sets the current font size.
	 */
	static public void setCurrentFontSize(int size) {
		fgCurrentFontSize = size;
	}

	/**
	 * Sets the current font style.
	 */
	static public void setCurrentFontStyle(int style) {
		fgCurrentFontStyle = style;
	}
}