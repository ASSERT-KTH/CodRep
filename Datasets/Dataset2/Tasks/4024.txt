if(OperatingSystem.isMacOSLF())

/*
 * RolloverButton.java - Class for buttons that implement rollovers
 * :tabSize=8:indentSize=8:noTabs=false:
 * :folding=explicit:collapseFolds=1:
 *
 * Copyright (C) 2002 Kris Kopicki
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; either version 2
 * of the License, or any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
 */

package org.gjt.sp.jedit.gui;

//{{{ Imports
import java.awt.*;
import java.awt.event.*;
import javax.swing.*;
import javax.swing.border.*;
import org.gjt.sp.jedit.OperatingSystem;
//}}}

/**
 * If you wish to have rollovers on your buttons, use this class.
 *
 * Unlike the Swing rollover support, this class works outside of
 * <code>JToolBars</code>, and does not require undocumented client
 * property hacks (or JDK1.4-specific API calls).<p>
 *
 * Note: You should not call setBorder() on your buttons, as they probably
 * won't work properly.
 */
public class RolloverButton extends JButton
{
	//{{{ RolloverButton constructor
	/**
	 * Setup the border (invisible initially)
	 */
	public RolloverButton()
	{
		if(OperatingSystem.isMacOS())
			setBorder(new EtchedBorder());

		setBorderPainted(false);

		addMouseListener(new MouseOverHandler());
	} //}}}

	//{{{ RolloverButton constructor
	/**
	 * Setup the border (invisible initially)
	 */
	public RolloverButton(Icon icon)
	{
		this();

		setIcon(icon);
	} //}}}

	//{{{ MouseHandler class
	/**
	 * Make the border visible/invisible on rollovers
	 */
	class MouseOverHandler extends MouseAdapter
	{
		public void mouseEntered(MouseEvent e)
		{
			setBorderPainted(true);
		}

		public void mouseExited(MouseEvent e)
		{
			setBorderPainted(false);
		}
	} //}}}
}