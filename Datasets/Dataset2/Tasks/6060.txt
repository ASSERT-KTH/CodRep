Rectangle r = new Rectangle();

/*
 * @(#)PolyLineFigure.java
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
import java.util.*;
import java.io.IOException;
import CH.ifa.draw.framework.*;
import CH.ifa.draw.standard.*;
import CH.ifa.draw.util.*;

/**
 * A poly line figure consists of a list of points.
 * It has an optional line decoration at the start and end.
 *
 * @see LineDecoration
 *
 * @version <$CURRENT_VERSION$>
 */
public  class PolyLineFigure extends AbstractFigure {

	public final static int ARROW_TIP_NONE  = 0;
	public final static int ARROW_TIP_START = 1;
	public final static int ARROW_TIP_END   = 2;
	public final static int ARROW_TIP_BOTH  = 3;

	protected Vector              fPoints;
	protected LineDecoration      fStartDecoration = null;
	protected LineDecoration      fEndDecoration = null;
	protected Color               fFrameColor = Color.black;

	/*
	 * Serialization support.
	 */
	private static final long serialVersionUID = -7951352179906577773L;
	private int polyLineFigureSerializedDataVersion = 1;

	public PolyLineFigure() {
		fPoints = new Vector(4);
	}

	public PolyLineFigure(int size) {
		fPoints = new Vector(size);
	}

	public PolyLineFigure(int x, int y) {
		fPoints = new Vector();
		fPoints.addElement(new Point(x, y));
	}

	public Rectangle displayBox() {
		Enumeration k = points();
		Rectangle r = new Rectangle((Point) k.nextElement());

		while (k.hasMoreElements()) {
			r.add((Point) k.nextElement());
		}

		return r;
	}

	public boolean isEmpty() {
		return (size().width < 3) && (size().height < 3);
	}

	public Vector handles() {
		Vector handles = new Vector(fPoints.size());
		for (int i = 0; i < fPoints.size(); i++) {
			handles.addElement(new PolyLineHandle(this, locator(i), i));
		}
		return handles;
	}

	public void basicDisplayBox(Point origin, Point corner) {
	}

	/**
	 * Adds a node to the list of points.
	 */
	public void addPoint(int x, int y) {
		fPoints.addElement(new Point(x, y));
		changed();
	}

	public Enumeration points() {
		return fPoints.elements();
	}

	public int pointCount() {
		return fPoints.size();
	}

	protected void basicMoveBy(int dx, int dy) {
		Enumeration k = fPoints.elements();
		while (k.hasMoreElements()) {
			((Point) k.nextElement()).translate(dx, dy);
		}
	}

	/**
	 * Changes the position of a node.
	 */
	public void setPointAt(Point p, int i) {
		willChange();
		fPoints.setElementAt(p, i);
		changed();
	}

	/**
	 * Insert a node at the given point.
	 */
	public void insertPointAt(Point p, int i) {
		fPoints.insertElementAt(p, i);
		changed();
	}

	public void removePointAt(int i) {
		willChange();
		fPoints.removeElementAt(i);
		changed();
	}

	/**
	 * Splits the segment at the given point if a segment was hit.
	 * @return the index of the segment or -1 if no segment was hit.
	 */
	public int splitSegment(int x, int y) {
		int i = findSegment(x, y);
		if (i != -1) {
			insertPointAt(new Point(x, y), i+1);
		}
		return i+1;
	}

	public Point pointAt(int i) {
		return (Point)fPoints.elementAt(i);
	}

	/**
	 * Joins to segments into one if the given point hits a node
	 * of the polyline.
	 * @return true if the two segments were joined.
	 */
	public boolean joinSegments(int x, int y) {
		for (int i= 1; i < fPoints.size()-1; i++) {
			Point p = pointAt(i);
			if (Geom.length(x, y, p.x, p.y) < 3) {
				removePointAt(i);
				return true;
			}
		}
		return false;
	}

	public Connector connectorAt(int x, int y) {
		return new PolyLineConnector(this);
	}

	/**
	 * Sets the start decoration.
	 */
	public void setStartDecoration(LineDecoration l) {
		fStartDecoration = l;
	}

	/**
	 * Returns the start decoration.
	 */
	public LineDecoration getStartDecoration() {
		return fStartDecoration;
	}

	/**
	 * Sets the end decoration.
	 */
	public void setEndDecoration(LineDecoration l) {
		fEndDecoration = l;
	}

	/**
	 * Returns the end decoration.
	 */
	public LineDecoration getEndDecoration() {
		return fEndDecoration;
	}

	public void draw(Graphics g) {
		g.setColor(getFrameColor());
		Point p1, p2;
		for (int i = 0; i < fPoints.size()-1; i++) {
			p1 = (Point) fPoints.elementAt(i);
			p2 = (Point) fPoints.elementAt(i+1);
			drawLine(g, p1.x, p1.y, p2.x, p2.y);
		}
		decorate(g);
	}

	/**
	 * Can be overriden in subclasses to draw different types of lines
	 * (e.g. dotted lines)
	 */
	protected void drawLine(Graphics g, int x1, int y1, int x2, int y2) {
		g.drawLine(x1, y1, x2, y2);
	}

	public boolean containsPoint(int x, int y) {
		Rectangle bounds = displayBox();
		bounds.grow(4,4);
		if (!bounds.contains(x, y)) {
			return false;
		}

		Point p1, p2;
		for (int i = 0; i < fPoints.size()-1; i++) {
			p1 = (Point) fPoints.elementAt(i);
			p2 = (Point) fPoints.elementAt(i+1);
			if (Geom.lineContainsPoint(p1.x, p1.y, p2.x, p2.y, x, y)) {
				return true;
			}
		}
		return false;
	}

	/**
	 * Gets the segment of the polyline that is hit by
	 * the given point.
	 * @return the index of the segment or -1 if no segment was hit.
	 */
	public int findSegment(int x, int y) {
		Point p1, p2;
		for (int i = 0; i < fPoints.size()-1; i++) {
			p1 = (Point) fPoints.elementAt(i);
			p2 = (Point) fPoints.elementAt(i+1);
			if (Geom.lineContainsPoint(p1.x, p1.y, p2.x, p2.y, x, y)) {
				return i;
			}
		}
		return -1;
	}

	private void decorate(Graphics g) {
		if (getStartDecoration() != null) {
			Point p1 = (Point)fPoints.elementAt(0);
			Point p2 = (Point)fPoints.elementAt(1);
			getStartDecoration().draw(g, p1.x, p1.y, p2.x, p2.y);
		}
		if (getEndDecoration() != null) {
			Point p3 = (Point)fPoints.elementAt(fPoints.size()-2);
			Point p4 = (Point)fPoints.elementAt(fPoints.size()-1);
			getEndDecoration().draw(g, p4.x, p4.y, p3.x, p3.y);
		}
	}

	/**
	 * Gets the attribute with the given name.
	 * PolyLineFigure maps "ArrowMode"to a
	 * line decoration.
	 *
	 * @deprecated use getAttribute(FigureAttributeConstant) instead
	 */
	public Object getAttribute(String name) {
		return getAttribute(FigureAttributeConstant.getConstant(name));
	}

	/**
	 * Gets the attribute with the given name.
	 * PolyLineFigure maps "ArrowMode"to a
	 * line decoration.
	 */
	public Object getAttribute(FigureAttributeConstant attributeConstant) {
		if (attributeConstant.equals(FigureAttributeConstant.FRAME_COLOR)) {
			return getFrameColor();
		}
		else if (attributeConstant.equals(FigureAttributeConstant.ARROW_MODE)) {
			int value = 0;
			if (getStartDecoration() != null) {
				value |= ARROW_TIP_START;
			}
			if (getEndDecoration() != null) {
				value |= ARROW_TIP_END;
			}
			return new Integer(value);
		}
		return super.getAttribute(attributeConstant);
	}

	/**
	 * Sets the attribute with the given name.
	 * PolyLineFigure interprets "ArrowMode"to set
	 * the line decoration.
	 *
	 * @deprecated use setAttribute(FigureAttributeConstant, Object) instead
	 */
	public void setAttribute(String name, Object value) {
		setAttribute(FigureAttributeConstant.getConstant(name), value);
	}

	/**
	 * Sets the attribute with the given name.
	 * PolyLineFigure interprets "ArrowMode"to set
	 * the line decoration.
	 */
	public void setAttribute(FigureAttributeConstant attributeConstant, Object value) {
		if (attributeConstant.equals(FigureAttributeConstant.FRAME_COLOR)) {
			setFrameColor((Color)value);
			changed();
		}
		else if (attributeConstant.equals(FigureAttributeConstant.ARROW_MODE.getName())) {
			Integer intObj = (Integer)value;
			if (intObj != null) {
				int decoration = intObj.intValue();
				if ((decoration & ARROW_TIP_START) != 0) {
					setStartDecoration(new ArrowTip());
				}
				else {
					setStartDecoration(null);
				}
				if ((decoration & ARROW_TIP_END) != 0) {
					setEndDecoration(new ArrowTip());
				}
				else {
					setEndDecoration(null);
				}
			}
			changed();
		}
		else {
			super.setAttribute(attributeConstant, value);
		}
	}

	public void write(StorableOutput dw) {
		super.write(dw);
		dw.writeInt(fPoints.size());
		Enumeration k = fPoints.elements();
		while (k.hasMoreElements()) {
			Point p = (Point) k.nextElement();
			dw.writeInt(p.x);
			dw.writeInt(p.y);
		}
		dw.writeStorable(fStartDecoration);
		dw.writeStorable(fEndDecoration);
		dw.writeColor(fFrameColor);
	}

	public void read(StorableInput dr) throws IOException {
		super.read(dr);
		int size = dr.readInt();
		fPoints = new Vector(size);
		for (int i=0; i<size; i++) {
			int x = dr.readInt();
			int y = dr.readInt();
			fPoints.addElement(new Point(x,y));
		}
		setStartDecoration((LineDecoration)dr.readStorable());
		setEndDecoration((LineDecoration)dr.readStorable());
		fFrameColor = dr.readColor();
	}

	/**
	 * Creates a locator for the point with the given index.
	 */
	public static Locator locator(int pointIndex) {
		return new PolyLineLocator(pointIndex);
	}

	protected Color getFrameColor() {
		return fFrameColor;
	}

	protected void setFrameColor(Color c) {
		fFrameColor = c;
	}

	/**
	 * Hook method to change the rectangle that will be invalidated
	 */
	protected Rectangle invalidateRectangle(Rectangle r) {
		// SF-bug id: 533953: provide this method to customize invalidated rectangle
		Rectangle parentR = super.invalidateRectangle(r);
		parentR.add(getStartDecoration().displayBox());
		parentR.add(getEndDecoration().displayBox());
		return parentR;
	}
}