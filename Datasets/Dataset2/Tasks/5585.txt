defaultTextIconGap);

package org.columba.core.gui.themes.thincolumba;

import java.awt.Color;
import java.awt.Dimension;
import java.awt.Graphics;

import javax.swing.Icon;
import javax.swing.JComponent;
import javax.swing.JMenuItem;
import javax.swing.plaf.ComponentUI;
import javax.swing.plaf.basic.BasicMenuItemUI;

import org.columba.core.gui.util.EmptyIcon;

/**
 * @author freddy
 *
 * To change this generated comment edit the template variable "typecomment":
 * Window>Preferences>Java>Templates.
 * To enable and disable the creation of type comments go to
 * Window>Preferences>Java>Code Generation.
 */
public class ThinMenuItemUI extends BasicMenuItemUI {

	public static ComponentUI createUI(JComponent c) {
		return new ThinMenuItemUI();
	}

	protected Dimension getPreferredMenuItemSize(
		JComponent c,
		Icon checkIcon,
		Icon arrowIcon,
		int defaultTextIconGap) {
		JMenuItem b = (JMenuItem) c;
		Icon icon = (Icon) b.getIcon();

		if (icon == null)
			b.setIcon(new EmptyIcon());
		Dimension d =
			super.getPreferredMenuItemSize(
				c,
				checkIcon,
				arrowIcon,
				defaultTextIconGap - 8);

		return d;
	}

	public void paint(Graphics g, JComponent c) {
		ThinUtilities.enableAntiAliasing(g);

		super.paint(g, c);
	}

}