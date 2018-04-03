setVisible(true);

/*
 * SelectLineRange.java - Selects a range of lines
 * :tabSize=8:indentSize=8:noTabs=false:
 * :folding=explicit:collapseFolds=1:
 *
 * Copyright (C) 1999, 2000 Slava Pestov
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
import org.gjt.sp.jedit.textarea.*;
import org.gjt.sp.jedit.*;
//}}}

public class SelectLineRange extends EnhancedDialog implements ActionListener
{
	//{{{ SelectLineRange constructor
	public SelectLineRange(View view)
	{
		super(view,jEdit.getProperty("selectlinerange.title"),true);
		this.view = view;

		JPanel content = new JPanel(new BorderLayout());
		content.setBorder(new EmptyBorder(12,12,12,0));
		setContentPane(content);

		JLabel label = new JLabel(jEdit.getProperty(
			"selectlinerange.caption"));
		label.setBorder(new EmptyBorder(0,0,6,12));
		content.add(BorderLayout.NORTH,label);

		JPanel panel = createFieldPanel();

		content.add(BorderLayout.CENTER,panel);

		panel = new JPanel();
		panel.setLayout(new BoxLayout(panel,BoxLayout.X_AXIS));
		panel.setBorder(new EmptyBorder(6,0,0,12));
		panel.add(Box.createGlue());
		panel.add(Box.createGlue());
		ok = new JButton(jEdit.getProperty("common.ok"));
		ok.addActionListener(this);
		getRootPane().setDefaultButton(ok);
		panel.add(ok);
		panel.add(Box.createHorizontalStrut(6));
		cancel = new JButton(jEdit.getProperty("common.cancel"));
		cancel.addActionListener(this);
		panel.add(cancel);
		panel.add(Box.createGlue());

		content.add(panel,BorderLayout.SOUTH);

		GUIUtilities.requestFocus(this,startField);

		pack();
		setLocationRelativeTo(view);
		show();
	} //}}}

	//{{{ ok() method
	public void ok()
	{
		int startLine;
		int endLine;

		try
		{
			startLine = Integer.parseInt(startField.getText()) - 1;
			endLine = Integer.parseInt(endField.getText()) - 1;
		}
		catch(NumberFormatException nf)
		{
			getToolkit().beep();
			return;
		}

		Buffer buffer = view.getBuffer();

		if(startLine < 0 || endLine >= buffer.getLineCount()
			|| startLine > endLine)
		{
			getToolkit().beep();
			return;
		}

		JEditTextArea textArea = view.getTextArea();
		Selection s = new Selection.Range(
			buffer.getLineStartOffset(startLine),
			buffer.getLineEndOffset(endLine) - 1);
		if(textArea.isMultipleSelectionEnabled())
			textArea.addToSelection(s);
		else
			textArea.setSelection(s);
		textArea.moveCaretPosition(buffer.getLineEndOffset(endLine) - 1);

		dispose();
	} //}}}

	//{{{ cancel() method
	public void cancel()
	{
		dispose();
	} //}}}

	//{{{ actionPerformed() method
	public void actionPerformed(ActionEvent evt)
	{
		Object source = evt.getSource();
		if(source == ok)
			ok();
		else if(source == cancel)
			cancel();
	} //}}}

	//{{{ Private members

	//{{{ Instance variables
	private View view;
	private JTextField startField;
	private JTextField endField;
	private JButton ok;
	private JButton cancel;
	//}}}

	//{{{ createFieldPanel() method
	private JPanel createFieldPanel()
	{
		GridBagLayout layout = new GridBagLayout();
		JPanel panel = new JPanel(layout);

		GridBagConstraints cons = new GridBagConstraints();
		cons.insets = new Insets(0,0,6,12);
		cons.gridwidth = cons.gridheight = 1;
		cons.gridx = cons.gridy = 0;
		cons.fill = GridBagConstraints.BOTH;
		JLabel label = new JLabel(jEdit.getProperty("selectlinerange.start"),
			SwingConstants.RIGHT);
		layout.setConstraints(label,cons);
		panel.add(label);

		startField = new JTextField(10);
		cons.gridx = 1;
		cons.weightx = 1.0f;
		layout.setConstraints(startField,cons);
		panel.add(startField);

		label = new JLabel(jEdit.getProperty("selectlinerange.end"),
			SwingConstants.RIGHT);
		cons.gridx = 0;
		cons.weightx = 0.0f;
		cons.gridy = 1;
		layout.setConstraints(label,cons);
		panel.add(label);

		endField = new JTextField(10);
		cons.gridx = 1;
		cons.weightx = 1.0f;
		layout.setConstraints(endField,cons);
		panel.add(endField);

		return panel;
	} //}}}

	//}}}
}