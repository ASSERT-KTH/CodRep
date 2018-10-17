setText(shorten(value.toString()));

/*
 * PasteFromListDialog.java - Paste previous/paste deleted dialog
 * :tabSize=8:indentSize=8:noTabs=false:
 * :folding=explicit:collapseFolds=1:
 *
 * Copyright (C) 2003 Slava Pestov
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
import javax.swing.event.*;
import java.awt.*;
import java.awt.event.*;
import org.gjt.sp.jedit.*;
//}}}

public class PasteFromListDialog extends EnhancedDialog
{
	//{{{ PasteFromListDialog constructor
	public PasteFromListDialog(String name, View view, ListModel model)
	{
		super(view,jEdit.getProperty(name + ".title"),true);
		this.view = view;

		JPanel content = new JPanel(new BorderLayout());
		content.setBorder(new EmptyBorder(12,12,12,12));
		setContentPane(content);
		JPanel center = new JPanel(new GridLayout(2,1,2,12));

		clips = new JList(model);
		clips.setCellRenderer(new Renderer());
		clips.setVisibleRowCount(12);

		clips.addMouseListener(new MouseHandler());
		clips.addListSelectionListener(new ListHandler());

		insert = new JButton(jEdit.getProperty("common.insert"));
		cancel = new JButton(jEdit.getProperty("common.cancel"));

		JLabel label = new JLabel(jEdit.getProperty(name + ".caption"));
		label.setBorder(new EmptyBorder(0,0,6,0));
		content.add(BorderLayout.NORTH,label);

		JScrollPane scroller = new JScrollPane(clips);
		scroller.setPreferredSize(new Dimension(500,150));
		center.add(scroller);

		clipText = new JTextArea();
		clipText.setEditable(false);
		scroller = new JScrollPane(clipText);
		scroller.setPreferredSize(new Dimension(500,150));
		center.add(scroller);

		content.add(center, BorderLayout.CENTER);

		JPanel panel = new JPanel();
		panel.setLayout(new BoxLayout(panel,BoxLayout.X_AXIS));
		panel.setBorder(new EmptyBorder(12,0,0,0));
		panel.add(Box.createGlue());
		panel.add(insert);
		panel.add(Box.createHorizontalStrut(6));
		panel.add(cancel);
		panel.add(Box.createGlue());
		content.add(panel, BorderLayout.SOUTH);

		if(model.getSize() >= 1)
			clips.setSelectedIndex(0);
		updateButtons();

		getRootPane().setDefaultButton(insert);
		insert.addActionListener(new ActionHandler());
		cancel.addActionListener(new ActionHandler());

		GUIUtilities.requestFocus(this,clips);

		pack();
		setLocationRelativeTo(view);
		show();
	} //}}}

	//{{{ ok() method
	public void ok()
	{
		Object[] selected = clips.getSelectedValues();
		if(selected == null || selected.length == 0)
		{
			getToolkit().beep();
			return;
		}

		view.getTextArea().setSelectedText(getSelectedClipText());

		dispose();
	} //}}}

	//{{{ cancel() method
	public void cancel()
	{
		dispose();
	} //}}}

	//{{{ Private members

	//{{{ Instance variables
	private View view;
	private JList clips;
	private JTextArea clipText;
	private JButton insert;
	private JButton cancel;
	//}}}

	//{{{ getSelectedClipText()
	private String getSelectedClipText()
	{
		Object[] selected = clips.getSelectedValues();
		StringBuffer clip = new StringBuffer();
		for(int i = 0; i < selected.length; i++)
		{
			if(i != 0)
				clip.append('\n');
			clip.append(selected[i]);
		}
		return clip.toString();
	}
	//}}}

	//{{{ updateButtons() method
	private void updateButtons()
	{
		int selected = clips.getSelectedIndex();
		insert.setEnabled(selected != -1);
	} //}}}

	//{{{ showClipText() method
	private void showClipText()
	{
		Object[] selected = clips.getSelectedValues();
		if(selected == null || selected.length == 0)
			clipText.setText("");
		else
			clipText.setText(getSelectedClipText());
		clipText.setCaretPosition(0);
	}
	//}}}

	//}}}

	//{{{ Renderer class
	class Renderer extends DefaultListCellRenderer
	{
		String shorten(String item)
		{
			StringBuffer buf = new StringBuffer();
			// workaround for Swing rendering labels starting
			// with <html> using the HTML engine
			if(item.toLowerCase().startsWith("<html>"))
				buf.append(' ');
			boolean ws = true;
			for(int i = 0; i < item.length(); i++)
			{
				char ch = item.charAt(i);
				if(Character.isWhitespace(ch))
				{
					if(ws)
						/* do nothing */;
					else
					{
						buf.append(' ');
						ws = true;
					}
				}
				else
				{
					ws = false;
					buf.append(ch);
				}
			}

			if(buf.length() == 0)
				return jEdit.getProperty("paste-from-list.whitespace");
			return buf.toString();
		}

		public Component getListCellRendererComponent(
			JList list, Object value, int index,
			boolean isSelected, boolean cellHasFocus)
		{
			super.getListCellRendererComponent(list,value,index,
				isSelected,cellHasFocus);

			setText(shorten((String)value));

			return this;
		}
	} //}}}

	//{{{ ActionHandler class
	class ActionHandler implements ActionListener
	{
		public void actionPerformed(ActionEvent evt)
		{
			Object source = evt.getSource();
			if(source == insert)
				ok();
			else if(source == cancel)
				cancel();
		}
	} //}}}

	//{{{ ListHandler class
	class ListHandler implements ListSelectionListener
	{
		//{{{ valueChanged() method
		public void valueChanged(ListSelectionEvent evt)
		{
			showClipText();
			updateButtons();
		} //}}}
	} //}}}

	//{{{ MouseHandler class
	class MouseHandler extends MouseAdapter
	{
		public void mouseClicked(MouseEvent evt)
		{
			if(evt.getClickCount() == 2)
				ok();
		}
	} //}}}
}