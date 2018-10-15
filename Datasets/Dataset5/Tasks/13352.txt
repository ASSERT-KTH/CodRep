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

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import org.eclipse.wst.xml.vex.core.internal.core.Insets;
import org.eclipse.wst.xml.vex.core.internal.css.CSS;
import org.eclipse.wst.xml.vex.core.internal.css.Styles;
import org.eclipse.wst.xml.vex.core.internal.dom.Element;
import org.eclipse.wst.xml.vex.core.internal.dom.IVEXElement;

/**
 * Container for TableRowBox objects. May correspond to an element with
 * display:table-row-group, display:table-head-group, display:table-foot-group,
 * or may be anonymous.
 */
public class TableRowGroupBox extends AbstractBlockBox {

	/**
	 * Class constructor for non-anonymous table row groups.
	 * 
	 * @param context
	 *            LayoutContext to use.
	 * @param parent
	 *            Parent of this box.
	 * @param element
	 *            Element that generated this box.
	 */
	public TableRowGroupBox(LayoutContext context, BlockBox parent,
			Element element) {
		super(context, parent, element);
	}

	/**
	 * Class constructor for anonymous table row groups.
	 * 
	 * @param context
	 *            LayoutContext to use.
	 * @param parent
	 *            Parent of this box.
	 * @param startOffset
	 *            Start of the range encompassing the table.
	 * @param endOffset
	 *            End of the range encompassing the table.
	 */
	public TableRowGroupBox(LayoutContext context, BlockBox parent,
			int startOffset, int endOffset) {
		super(context, parent, startOffset, endOffset);

	}

	protected List createChildren(final LayoutContext context) {
		// TODO Auto-generated method stub

		// Walk children in range
		// - table-row children get non-anonymous TableRowBox
		// - runs of others get anonymous TableRowBox

		final List children = new ArrayList();

		this.iterateChildrenByDisplayStyle(context.getStyleSheet(),
				childDisplayStyles, new ElementOrRangeCallback() {
					public void onElement(Element child, String displayStyle) {
						children.add(new TableRowBox(context,
								TableRowGroupBox.this, child));
					}

					public void onRange(IVEXElement parent, int startOffset,
							int endOffset) {
						children.add(new TableRowBox(context,
								TableRowGroupBox.this, startOffset, endOffset));
					}
				});

		return children;
	}

	public Insets getInsets(LayoutContext context, int containerWidth) {
		return Insets.ZERO_INSETS;
	}

	public int getMarginBottom() {
		return 0;
	}

	public int getMarginTop() {
		return 0;
	}

	public void paint(LayoutContext context, int x, int y) {

		if (this.skipPaint(context, x, y)) {
			return;
		}

		this.paintChildren(context, x, y);

		this.paintSelectionFrame(context, x, y, true);
	}

	protected int positionChildren(LayoutContext context) {

		Styles styles = context.getStyleSheet().getStyles(
				this.findContainingElement());
		int spacing = styles.getBorderSpacing().getVertical();

		int childY = spacing;
		for (int i = 0; i < this.getChildren().length; i++) {

			TableRowBox child = (TableRowBox) this.getChildren()[i];
			// TODO must force table row margins to be zero
			Insets insets = child.getInsets(context, this.getWidth());

			childY += insets.getTop();

			child.setX(insets.getLeft());
			child.setY(childY);

			childY += child.getHeight() + insets.getBottom() + spacing;
		}
		this.setHeight(childY);

		return -1; // TODO revisit
	}

	// ====================================================== PRIVATE

	private static Set childDisplayStyles = new HashSet();

	static {
		childDisplayStyles.add(CSS.TABLE_ROW);
	}

}