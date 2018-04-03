return action.isSelected(GUIUtilities.getView(

/*
 * EnhancedCheckBoxMenuItem.java - Check box menu item
 * Copyright (C) 1999, 2000, 2001 Slava Pestov
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

import javax.swing.*;
import java.awt.event.*;
import java.awt.*;
import org.gjt.sp.jedit.textarea.JEditTextArea;
import org.gjt.sp.jedit.*;
import org.gjt.sp.util.Log;

/**
 * jEdit's custom menu item. It adds support for multi-key shortcuts.
 */
public class EnhancedCheckBoxMenuItem extends JCheckBoxMenuItem
{
	public EnhancedCheckBoxMenuItem(String label, EditAction action)
	{
		super(label);
		this.action = action;

		if(action != null)
		{
			setEnabled(true);
			addActionListener(new EditAction.Wrapper(action));
			shortcutProp1 = action.getName() + ".shortcut";
			shortcutProp2 = action.getName() + ".shortcut2";
		}
		else
			setEnabled(false);

		setModel(new Model());
	}

	public Dimension getPreferredSize()
	{
		Dimension d = super.getPreferredSize();

		String shortcut = getShortcut();

		if(shortcut != null)
		{
			d.width += (getFontMetrics(acceleratorFont)
				.stringWidth(shortcut) + 10);
		}
		return d;
	}

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
				shortcut) + insets.right + insets.left),
				getFont().getSize() + (insets.top - 1)
				/* XXX magic number */);
		}
	}

	public String getActionCommand()
	{
		return getModel().getActionCommand();
	}

	// private members
	private String shortcutProp1;
	private String shortcutProp2;
	private EditAction action;
	private static Font acceleratorFont;
	private static Color acceleratorForeground;
	private static Color acceleratorSelectionForeground;

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
	}

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
	}

	class Model extends DefaultButtonModel
	{
		public boolean isSelected()
		{
			if(!isShowing())
				return false;

			try
			{
				return action.isSelected(EditAction.getView(
					EnhancedCheckBoxMenuItem.this));
			}
			catch(Throwable t)
			{
				Log.log(Log.ERROR,this,t);
				return false;
			}
		}

		public void setSelected(boolean b) {}
	}
}