int lineNo = buffer.getLineOfOffset(marker.getPosition()) + 1;

/*
 * MarkersMenu.java - Markers menu
 * :tabSize=8:indentSize=8:noTabs=false:
 * :folding=explicit:collapseFolds=1:
 *
 * Copyright (C) 2001 Slava Pestov
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
import javax.swing.event.*;
import javax.swing.*;
import java.awt.event.*;
import java.awt.*;
import java.util.*;
import org.gjt.sp.jedit.*;
import org.gjt.sp.util.Log;
//}}}

public class MarkersMenu extends EnhancedMenu implements MenuListener
{
	//{{{ MarkersMenu constructor
	public MarkersMenu()
	{
		super("markers");
		addMenuListener(this);
	} //}}}

	//{{{ menuSelected() method
	public void menuSelected(MenuEvent evt)
	{
		final View view = GUIUtilities.getView(this);

		if(getMenuComponentCount() != 0)
		{
			for(int i = getMenuComponentCount() - 1;
				i >= 0;
				i--)
			{
				Component comp = getMenuComponent(i);
				if(comp instanceof JSeparator)
					break;
				else
					remove(comp);
			}
		}

		Buffer buffer = view.getBuffer();

		Vector markers = buffer.getMarkers();

		if(markers.size() == 0)
		{
			JMenuItem mi = new JMenuItem(jEdit.getProperty(
				"no-markers.label"));
			mi.setEnabled(false);
			add(mi);
			return;
		}

		int maxItems = jEdit.getIntegerProperty("menu.spillover",20);

		JMenu current = this;

		for(int i = 0; i < markers.size(); i++)
		{
			final Marker marker = (Marker)markers.elementAt(i);
			int lineNo = buffer.getLineOfOffset(marker.getPosition());

			if(current.getItemCount() >= maxItems && i != markers.size() - 1)
			{
				//current.addSeparator();
				JMenu newCurrent = new JMenu(
					jEdit.getProperty(
					"common.more"));
				current.add(newCurrent);
				current = newCurrent;
			}

			JMenuItem mi = new MarkersMenuItem(buffer,
				lineNo,marker.getShortcut());
			mi.addActionListener(new ActionListener()
			{
				public void actionPerformed(ActionEvent evt)
				{
					view.getTextArea().setCaretPosition(
						marker.getPosition());
				}
			});
			current.add(mi);
		}
	} //}}}

	public void menuDeselected(MenuEvent e) {}

	public void menuCanceled(MenuEvent e) {}

	//{{{ MarkersMenuItem class
	static class MarkersMenuItem extends JMenuItem
	{
		//{{{MarkersMenuItem constructor
		MarkersMenuItem(Buffer buffer, int lineNo, char shortcut)
		{
			String text = buffer.getLineText(lineNo).trim();
			if(text.length() == 0)
				text = jEdit.getProperty("markers.blank-line");
			setText(lineNo + ": " + text);

			shortcutProp = "goto-marker.shortcut";
			MarkersMenuItem.this.shortcut = shortcut;
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
		private String shortcutProp;
		private char shortcut;
		private static Font acceleratorFont;
		private static Color acceleratorForeground;
		private static Color acceleratorSelectionForeground;

		//{{{ getShortcut() method
		private String getShortcut()
		{
			if(shortcut == '\0')
				return null;
			else
			{
				String shortcutPrefix = jEdit.getProperty(shortcutProp);

				if(shortcutPrefix == null)
					return null;
				else
				{
					return shortcutPrefix + " " + shortcut;
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
	} //}}}
}