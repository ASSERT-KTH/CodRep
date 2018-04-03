g.fillRoundRect(r.x, r.y, r.width-1, r.height-1, fArcWidth, fArcHeight);

/*
 * @(#)RoundRectangleFigure.java
 *
 * Project:		JHotdraw - a GUI framework for technical drawings
 *				http://www.jhotdraw.org
 *				http://jhotdraw.sourceforge.net
 * Copyright:	© by the original author(s) and all contributors
 * License:		Lesser GNU Public License (LGPL)
 *				http://www.opensource.org/licenses/lgpl-license.html
 */

package CH.ifa.draw.figures;

import java.awt.*;
import java.io.IOException;
import java.util.List;
import CH.ifa.draw.framework.*;
import CH.ifa.draw.standard.*;
import CH.ifa.draw.util.*;


/**
 * A round rectangle figure.
 *
 * @see RadiusHandle
 *
 * @version <$CURRENT_VERSION$>
 */
public class RoundRectangleFigure extends AttributeFigure {

	private Rectangle   fDisplayBox;
	private int         fArcWidth;
	private int         fArcHeight;
	private static final int DEFAULT_ARC = 8;

	/*
	 * Serialization support.
	 */
	private static final long serialVersionUID = 7907900248924036885L;
	private int roundRectangleSerializedDataVersion = 1;

	public RoundRectangleFigure() {
		this(new Point(0,0), new Point(0,0));
		fArcWidth = fArcHeight = DEFAULT_ARC;
	}

	public RoundRectangleFigure(Point origin, Point corner) {
		basicDisplayBox(origin,corner);
		fArcWidth = fArcHeight = DEFAULT_ARC;
	}

	public void basicDisplayBox(Point origin, Point corner) {
		fDisplayBox = new Rectangle(origin);
		fDisplayBox.add(corner);
	}

	/**
	 * Sets the arc's witdh and height.
	 */
	public void setArc(int width, int height) {
		willChange();
		fArcWidth = width;
		fArcHeight = height;
		changed();
	}

	/**
	 * Gets the arc's width and height.
	 */
	public Point getArc() {
		return new Point(fArcWidth, fArcHeight);
	}

	public HandleEnumeration handles() {
		List handles = CollectionsFactory.current().createList();
		BoxHandleKit.addHandles(this, handles);

		handles.add(new RadiusHandle(this));

		return new HandleEnumerator(handles);
	}

	public Rectangle displayBox() {
		return new Rectangle(
			fDisplayBox.x,
			fDisplayBox.y,
			fDisplayBox.width,
			fDisplayBox.height);
	}

	protected void basicMoveBy(int x, int y) {
		fDisplayBox.translate(x,y);
	}

	public void drawBackground(Graphics g) {
		Rectangle r = displayBox();
		g.fillRoundRect(r.x, r.y, r.width, r.height, fArcWidth, fArcHeight);
	}

	public void drawFrame(Graphics g) {
		Rectangle r = displayBox();
		g.drawRoundRect(r.x, r.y, r.width-1, r.height-1, fArcWidth, fArcHeight);
	}

	public Insets connectionInsets() {
		return new Insets(fArcHeight/2, fArcWidth/2, fArcHeight/2, fArcWidth/2);
	}

	public Connector connectorAt(int x, int y) {
		return new ShortestDistanceConnector(this); // just for demo purposes
	}

	public void write(StorableOutput dw) {
		super.write(dw);
		dw.writeInt(fDisplayBox.x);
		dw.writeInt(fDisplayBox.y);
		dw.writeInt(fDisplayBox.width);
		dw.writeInt(fDisplayBox.height);
		dw.writeInt(fArcWidth);
		dw.writeInt(fArcHeight);
	}

	public void read(StorableInput dr) throws IOException {
		super.read(dr);
		fDisplayBox = new Rectangle(
			dr.readInt(),
			dr.readInt(),
			dr.readInt(),
			dr.readInt());
		fArcWidth = dr.readInt();
		fArcHeight = dr.readInt();
	}

}