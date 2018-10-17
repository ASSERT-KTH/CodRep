public class EnhancedButton extends RolloverButton

/*
 * EnhancedButton.java - Tool bar button
 * :tabSize=8:indentSize=8:noTabs=false:
 * :folding=explicit:collapseFolds=1:
 *
 * Copyright (C) 1999, 2001, 2002 Slava Pestov
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
import org.gjt.sp.jedit.EditAction;
import org.gjt.sp.jedit.GUIUtilities;
//}}}

public class EnhancedButton extends JButton
{
	//{{{ EnhancedButton constructor
	public EnhancedButton(Icon icon, String toolTip, EditAction action)
	{
		super(icon);

		this.action = action;

		if(action != null)
		{
			setEnabled(true);
			addActionListener(new EditAction.Wrapper(action));
			addMouseListener(new MouseHandler());
		}
		else
			setEnabled(false);

		setToolTipText(toolTip);

		Insets zeroInsets = new Insets(0,0,0,0);
		setMargin(zeroInsets);
		setRequestFocusEnabled(false);
	} //}}}

	//{{{ isFocusTraversable() method
	public boolean isFocusTraversable()
	{
		return false;
	} //}}}

	//{{{ Private members
	private EditAction action;
	//}}}

	//{{{ MouseHandler class
	class MouseHandler extends MouseAdapter
	{
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