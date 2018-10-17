public void mouseReleased(MouseEvent evt)

/*
 * EnhancedMenuItem.java - Menu item with user-specified accelerator string
 * :tabSize=8:indentSize=8:noTabs=false:
 * :folding=explicit:collapseFolds=1:
 *
 * Copyright (C) 1999, 2000, 2001, 2002 Slava Pestov
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
import javax.swing.*;
import java.awt.event.*;
import java.awt.*;
import org.gjt.sp.jedit.textarea.JEditTextArea;
import org.gjt.sp.jedit.*;
//}}}

/**
 * jEdit's custom menu item. It adds support for multi-key shortcuts.
 */
public class EnhancedMenuItem extends JMenuItem
{
	//{{{ EnhancedMenuItem constructor
	/**
	 * Creates a new menu item. Most plugins should call
	 * GUIUtilities.loadMenuItem() instead.
	 * @param label The menu item label
	 * @param action The edit action
	 * @param actionCommand The action command
	 */
	public EnhancedMenuItem(String label, EditAction action)
	{
		super(label);

		this.action = action;

		if(action != null)
		{
			setEnabled(true);
			addActionListener(new EditAction.Wrapper(action));
			shortcutProp1 = action.getName() + ".shortcut";
			shortcutProp2 = action.getName() + ".shortcut2";

			addMouseListener(new MouseHandler());
		}
		else
			setEnabled(false);
	} //}}}

	//{{{ getPreferredSize() method
	public Dimension getPreferredSize()
	{
		Dimension d = super.getPreferredSize();

		String shortcut = getShortcut();

		if(shortcut != null)
		{
			d.width += (getFontMetrics(acceleratorFont)
				.stringWidth(shortcut) + 15);
		}
		return d;
	} //}}}

	//{{{ paint() method
	public void paint(Graphics g)
	{
		super.paint(g);

		String shortcut = getShortcut();

		if(shortcut != null)
		{
			g.setFont(acceleratorFont);
			g.setColor(getModel().isArmed() ?
				acceleratorSelectionForeground :
				acceleratorForeground);
			FontMetrics fm = g.getFontMetrics();
			Insets insets = getInsets();
			g.drawString(shortcut,getWidth() - (fm.stringWidth(
				shortcut) + insets.right + insets.left + 5),
				getFont().getSize() + (insets.top - 1)
				/* XXX magic number */);
		}
	} //}}}

	//{{{ Private members

	//{{{ Instance variables
	private String shortcutProp1;
	private String shortcutProp2;
	private EditAction action;
	private static Font acceleratorFont;
	private static Color acceleratorForeground;
	private static Color acceleratorSelectionForeground;
	//}}}

	//{{{ getShortcut() method
	private String getShortcut()
	{
		if(action == null)
			return null;
		else
		{
			String shortcut1 = jEdit.getProperty(shortcutProp1);
			String shortcut2 = jEdit.getProperty(shortcutProp2);

			if(shortcut1 == null || shortcut1.length() == 0)
			{
				if(shortcut2 == null || shortcut2.length() == 0)
					return null;
				else
					return shortcut2;
			}
			else
			{
				if(shortcut2 == null || shortcut2.length() == 0)
					return shortcut1;
				else
					return shortcut1 + " or " + shortcut2;
			}
		}
	} //}}}

	//{{{ Class initializer
	static
	{
		acceleratorFont = UIManager.getFont("MenuItem.acceleratorFont");
		acceleratorFont = new Font("Monospaced",
			acceleratorFont.getStyle(),
			acceleratorFont.getSize());
		acceleratorForeground = UIManager
			.getColor("MenuItem.acceleratorForeground");
		acceleratorSelectionForeground = UIManager
			.getColor("MenuItem.acceleratorSelectionForeground");
	} //}}}

	//}}}

	//{{{ MouseHandler class
	class MouseHandler extends MouseAdapter
	{
		public void mouseClicked(MouseEvent evt)
		{
			GUIUtilities.getView((Component)evt.getSource())
				.getStatus().setMessage(null);
		}

		public void mouseEntered(MouseEvent evt)
		{
			String msg = action.getMouseOverText();
			if(msg != null)
			{
				GUIUtilities.getView((Component)evt.getSource())
					.getStatus().setMessage(msg);
			}
		}

		public void mouseExited(MouseEvent evt)
		{
			GUIUtilities.getView((Component)evt.getSource())
				.getStatus().setMessage(null);
		}
	} //}}}
}