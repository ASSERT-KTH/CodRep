setVisible(true);

/*
 * ErrorListDialog.java - Used to list I/O and plugin load errors
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
import java.awt.*;
import java.awt.event.*;
import java.util.Vector;
import javax.swing.*;
import javax.swing.border.*;
import org.gjt.sp.jedit.*;
import org.gjt.sp.util.Log;
//}}}

public class ErrorListDialog extends EnhancedDialog
{
	//{{{ ErrorEntry class
	public static class ErrorEntry
	{
		String path;
		String[] messages;

		public ErrorEntry(String path, String messageProp, Object[] args)
		{
			this.path = path;

			String message = jEdit.getProperty(messageProp,args);
			if(message == null)
				message = "Undefined property: " + messageProp;

			Log.log(Log.ERROR,this,path + ":");
			Log.log(Log.ERROR,this,message);

			Vector tokenizedMessage = new Vector();
			int lastIndex = -1;
			for(int i = 0; i < message.length(); i++)
			{
				if(message.charAt(i) == '\n')
				{
					tokenizedMessage.addElement(message.substring(
						lastIndex + 1,i));
					lastIndex = i;
				}
			}

			if(lastIndex != message.length())
			{
				tokenizedMessage.addElement(message.substring(
					lastIndex + 1));
			}

			messages = new String[tokenizedMessage.size()];
			tokenizedMessage.copyInto(messages);
		}

		public boolean equals(Object o)
		{
			if(o instanceof ErrorEntry)
			{
				ErrorEntry e = (ErrorEntry)o;
				return e.path.equals(path);
			}
			else
				return false;
		}
	} //}}}

	//{{{ ErrorListDialog constructor
	public ErrorListDialog(Frame frame, String title, String caption,
		Vector messages, boolean pluginError)
	{
		super(frame,title,!pluginError);

		JPanel content = new JPanel(new BorderLayout(12,12));
		content.setBorder(new EmptyBorder(12,12,12,12));
		setContentPane(content);

		Box iconBox = new Box(BoxLayout.Y_AXIS);
		iconBox.add(new JLabel(UIManager.getIcon("OptionPane.errorIcon")));
		iconBox.add(Box.createGlue());
		content.add(BorderLayout.WEST,iconBox);

		JPanel centerPanel = new JPanel(new BorderLayout());

		JLabel label = new JLabel(caption);
		label.setBorder(new EmptyBorder(0,0,6,0));
		centerPanel.add(BorderLayout.NORTH,label);

		JList errors = new JList(messages);
		errors.setCellRenderer(new ErrorListCellRenderer());
		errors.setVisibleRowCount(Math.min(messages.size(),4));

		// need this bullshit scroll bar policy for the preferred size
		// hack to work
		JScrollPane scrollPane = new JScrollPane(errors,
			JScrollPane.VERTICAL_SCROLLBAR_ALWAYS,
			JScrollPane.HORIZONTAL_SCROLLBAR_ALWAYS);
		Dimension size = scrollPane.getPreferredSize();
		size.width = Math.min(size.width,400);
		scrollPane.setPreferredSize(size);

		centerPanel.add(BorderLayout.CENTER,scrollPane);

		content.add(BorderLayout.CENTER,centerPanel);

		Box buttons = new Box(BoxLayout.X_AXIS);
		buttons.add(Box.createGlue());

		ok = new JButton(jEdit.getProperty("common.ok"));
		ok.addActionListener(new ActionHandler());

		if(pluginError)
		{
			pluginMgr = new JButton(jEdit.getProperty("error-list.plugin-manager"));
			pluginMgr.addActionListener(new ActionHandler());
			buttons.add(pluginMgr);
			buttons.add(Box.createHorizontalStrut(6));
		}

		buttons.add(ok);

		buttons.add(Box.createGlue());
		content.add(BorderLayout.SOUTH,buttons);

		getRootPane().setDefaultButton(ok);

		pack();
		setLocationRelativeTo(frame);
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

	//{{{ Private members
	private JButton ok, pluginMgr;
	//}}}

	//{{{ ActionHandler class
	class ActionHandler implements ActionListener
	{
		//{{{ actionPerformed() method
		public void actionPerformed(ActionEvent evt)
		{
			if(evt.getSource() == ok)
				dispose();
			else if(evt.getSource() == pluginMgr)
			{
				org.gjt.sp.jedit.pluginmgr.PluginManager
					.showPluginManager(JOptionPane
					.getFrameForComponent(
					ErrorListDialog.this));
			}
		} //}}}
	} //}}}
}