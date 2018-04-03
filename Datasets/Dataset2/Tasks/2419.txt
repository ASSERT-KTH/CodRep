if(OperatingSystem.hasScreenMenuBar() && shortcut != null)

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
		this.action = action;
		this.shortcut = getShortcut();
		if(OperatingSystem.isMacOSLF() && shortcut != null)
		{
			setText(label + " (" + shortcut + ")");
			shortcut = null;
		}
		else
			setText(label);

		if(action != null)
		{
			setEnabled(true);
			addActionListener(new EditAction.Wrapper(action));
			addMouseListener(new MouseHandler());
		}
		else
			setEnabled(false);
	} //}}}

	//{{{ getPreferredSize() method
	public Dimension getPreferredSize()
	{
		Dimension d = super.getPreferredSize();

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
				getFont().getSize() + (insets.top - 
				(OperatingSystem.isMacOSLF() ? 0 : 1))
				/* XXX magic number */);
		}
	} //}}}

	//{{{ Package-private members
	static Font acceleratorFont;
	static Color acceleratorForeground;
	static Color acceleratorSelectionForeground;
	//}}}

	//{{{ Private members

	//{{{ Instance variables
	private String shortcut;
	private EditAction action;
	//}}}

	//{{{ getShortcut() method
	private String getShortcut()
	{
		if(action == null)
			return null;
		else
		{
			String shortcut1 = jEdit.getProperty(action.getName() + ".shortcut");
			String shortcut2 = jEdit.getProperty(action.getName() + ".shortcut2");

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
		String shortcutFont;
		if (OperatingSystem.isMacOSLF())
			shortcutFont = "Lucida Grande";
		else
			shortcutFont = "Monospaced";
		
		acceleratorFont = UIManager.getFont("MenuItem.acceleratorFont");
		if(acceleratorFont == null)
			acceleratorFont = new Font(shortcutFont,Font.PLAIN,12);
		else
		{
			acceleratorFont = new Font(shortcutFont,
				acceleratorFont.getStyle(),
				acceleratorFont.getSize());
		}
		acceleratorForeground = UIManager
			.getColor("MenuItem.acceleratorForeground");
		if(acceleratorForeground == null)
			acceleratorForeground = Color.black;

		acceleratorSelectionForeground = UIManager
			.getColor("MenuItem.acceleratorSelectionForeground");
		if(acceleratorSelectionForeground == null)
			acceleratorSelectionForeground = Color.black;
	} //}}}

	//}}}

	//{{{ MouseHandler class
	class MouseHandler extends MouseAdapter
	{
		boolean msgSet = false;

		public void mouseReleased(MouseEvent evt)
		{
			if(msgSet)
			{
				GUIUtilities.getView((Component)evt.getSource())
					.getStatus().setMessage(null);
				msgSet = false;
			}
		}

		public void mouseEntered(MouseEvent evt)
		{
			String msg = action.getMouseOverText();
			if(msg != null)
			{
				GUIUtilities.getView((Component)evt.getSource())
					.getStatus().setMessage(msg);
				msgSet = true;
			}
		}

		public void mouseExited(MouseEvent evt)
		{
			if(msgSet)
			{
				GUIUtilities.getView((Component)evt.getSource())
					.getStatus().setMessage(null);
				msgSet = false;
			}
		}
	} //}}}
}