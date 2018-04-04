caption.setBorder(new EmptyBorder(0,0,6,0));

/*
 * BeanShellErrorDialog.java - BeanShell execution error dialog box
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
import javax.swing.*;
import javax.swing.border.*;
import java.awt.*;
import java.awt.event.*;
import org.gjt.sp.jedit.*;
//}}}

public class BeanShellErrorDialog extends EnhancedDialog
{
	//{{{ BeanShellErrorDialog constructor
	public BeanShellErrorDialog(View view, String message)
	{
		super(view,jEdit.getProperty("beanshell-error.title"),true);

		JPanel content = new JPanel(new BorderLayout(12,12));
		content.setBorder(new EmptyBorder(12,12,12,12));
		setContentPane(content);

		Box iconBox = new Box(BoxLayout.Y_AXIS);
		iconBox.add(new JLabel(UIManager.getIcon("OptionPane.errorIcon")));
		iconBox.add(Box.createGlue());
		content.add(BorderLayout.WEST,iconBox);

		JPanel centerPanel = new JPanel(new BorderLayout());

		JPanel caption = new JPanel(new GridLayout(2,1,3,3));
		caption.setBorder(new EmptyBorder(0,0,3,0));
		caption.add(new JLabel(jEdit.getProperty("beanshell-error.message.1")));
		caption.add(new JLabel(jEdit.getProperty("beanshell-error.message.2")));
		centerPanel.add(BorderLayout.NORTH,caption);

		JTextArea textArea = new JTextArea(10,60);
		textArea.setText(message);
		textArea.setLineWrap(true);
		textArea.setWrapStyleWord(true);
		centerPanel.add(BorderLayout.CENTER,new JScrollPane(textArea));

		content.add(BorderLayout.CENTER,centerPanel);

		Box buttons = new Box(BoxLayout.X_AXIS);
		buttons.add(Box.createGlue());
		JButton ok = new JButton(jEdit.getProperty("common.ok"));
		ok.addActionListener(new ActionHandler());
		buttons.add(ok);
		buttons.add(Box.createGlue());
		content.add(BorderLayout.SOUTH,buttons);

		getRootPane().setDefaultButton(ok);

		pack();
		setLocationRelativeTo(view);
		show();
	} //}}}

	//{{{ ok() method
	public void ok()
	{
		dispose();
	} //}}}

	//{{{ cancel() method
	public void cancel()
	{
		dispose();
	} //}}}

	//{{{ ActionHandler class
	class ActionHandler implements ActionListener
	{
		//{{{ actionPerformed() method
		public void actionPerformed(ActionEvent evt)
		{
			dispose();
		} //}}}
	} //}}}
}