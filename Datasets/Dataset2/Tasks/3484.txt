} //}}}

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
import java.lang.reflect.Method;
import javax.swing.*;
import javax.swing.border.*;
import org.gjt.sp.jedit.OperatingSystem;
import org.gjt.sp.util.Log;
//}}}

/**
 * If you wish to have rollovers on your buttons, use this class.
 *
 * Unlike the Swing rollover support, this class works outside of
 * <code>JToolBar</code>s, and does not require undocumented client
 * property hacks or JDK1.4-specific API calls.<p>
 *
 * Note: You should not call <code>setBorder()</code> on your buttons,
 * as they probably won't work properly.
 */
public class RolloverButton extends JButton
{
	//{{{ RolloverButton constructor
	/**
	 * Setup the border (invisible initially)
	 */
	public RolloverButton()
	{
		if(method != null)
		{
			try
			{
				method.invoke(this,new Boolean[] { Boolean.TRUE });
			}
			catch(Exception e)
			{
				Log.log(Log.ERROR,this,e);
			}
		}
		else
		{
			setBorder(new EtchedBorder());
			setBorderPainted(false);
			setMargin(new Insets(0,0,0,0));

			setRequestFocusEnabled(false);

			addMouseListener(new MouseOverHandler());
		}
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

	//{{{ isOpaque() method
	public boolean isOpaque()
	{
		return false;
	} //}}}

	//{{{ setEnabled() method
	public void setEnabled(boolean b)
	{
		super.setEnabled(b);
		if(method == null)
		{
			setBorderPainted(false);
			repaint();
		}
	} //}}}

	//{{{ paint() method
	public void paint(Graphics g)
	{
		if(method != null || isEnabled())
			super.paint(g);
		else
		{
			Graphics2D g2 = (Graphics2D)g;
			g2.setComposite(c);
			super.paint(g2);
		}
	} //}}}

	//{{{ Private members
	private static AlphaComposite c = AlphaComposite.getInstance(
		AlphaComposite.SRC_OVER, 0.5f);

	private static Method method;

	static
	{
		/* if(OperatingSystem.hasJava14())
		{
			try
			{
				method = RolloverButton.class
					.getMethod("setRolloverEnabled",new Class[]
					{ boolean.class });
				Log.log(Log.DEBUG,RolloverButton.class,
					"Java 1.4 setRolloverEnabled() method enabled");
			}
			catch(Exception e)
			{
				Log.log(Log.ERROR,RolloverButton.class,e);
			}
		} */
	}

	//{{{ MouseHandler class
	/**
	 * Make the border visible/invisible on rollovers
	 */
	class MouseOverHandler extends MouseAdapter
	{
		public void mouseEntered(MouseEvent e)
		{
			if (isEnabled())
				setBorderPainted(true);
		}

		public void mouseExited(MouseEvent e)
		{
			setBorderPainted(false);
		}
	} //}}}
}