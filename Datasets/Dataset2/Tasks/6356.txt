setVisible(true);

/*
 * EditAbbrevDialog.java - Displayed when editing abbrevs
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
import javax.swing.border.*;
import javax.swing.*;
import java.awt.event.*;
import java.awt.*;
import java.util.*;
import org.gjt.sp.jedit.*;
//}}}

public class EditAbbrevDialog extends JDialog
{
	//{{{ EditAbbrevDialog constructor
	/**
	 * @since jEdit 4.2pre3
	 */
	public EditAbbrevDialog(Frame frame, String abbrev, String expansion,
		Map abbrevs)
	{
		super(frame,jEdit.getProperty("edit-abbrev.title"),true);
		init(abbrev, expansion, abbrevs);
	} //}}}

	//{{{ EditAbbrevDialog constructor
	public EditAbbrevDialog(Dialog dialog, String abbrev, String expansion,
		Map abbrevs)
	{
		super(dialog,jEdit.getProperty("edit-abbrev.title"),true);
		init(abbrev, expansion, abbrevs);
	} //}}}

	//{{{ getAbbrev() method
	public String getAbbrev()
	{
		if(!isOK)
			return null;

		return editor.getAbbrev();
	} //}}}

	//{{{ getExpansion() method
	public String getExpansion()
	{
		if(!isOK)
			return null;

		return editor.getExpansion();
	} //}}}

	//{{{ Private members
	private AbbrevEditor editor;
	private JButton ok;
	private JButton cancel;
	private boolean isOK;
	private String originalAbbrev;
	private Map abbrevs;

	//{{{ init() method
	private void init(String abbrev, String expansion, Map abbrevs)
	{
		this.abbrevs = abbrevs;

		this.originalAbbrev = abbrev;

		JPanel content = new JPanel(new BorderLayout());
		content.setBorder(new EmptyBorder(12,12,12,12));
		setContentPane(content);

		editor = new AbbrevEditor();
		editor.setAbbrev(abbrev);
		editor.setExpansion(expansion);
		editor.setBorder(new EmptyBorder(0,0,12,0));
		content.add(BorderLayout.CENTER,editor);

		Box box = new Box(BoxLayout.X_AXIS);
		box.add(Box.createGlue());
		ok = new JButton(jEdit.getProperty("common.ok"));
		ok.addActionListener(new ActionHandler());
		getRootPane().setDefaultButton(ok);
		box.add(ok);
		box.add(Box.createHorizontalStrut(6));
		cancel = new JButton(jEdit.getProperty("common.cancel"));
		cancel.addActionListener(new ActionHandler());
		box.add(cancel);
		box.add(Box.createGlue());
		content.add(BorderLayout.SOUTH,box);

		KeyListener listener = new KeyHandler();
		addKeyListener(listener);
		editor.getBeforeCaretTextArea().addKeyListener(listener);
		editor.getAfterCaretTextArea().addKeyListener(listener);

		setDefaultCloseOperation(DISPOSE_ON_CLOSE);
		pack();
		setLocationRelativeTo(getParent());
		show();
	} //}}}

	//{{{ checkForExistingAbbrev() method
	private boolean checkForExistingAbbrev()
	{
		String abbrev = editor.getAbbrev();
		if(abbrevs.get(abbrev) != null)
		{
			if(abbrev.equals(originalAbbrev))
				return true;

			int result = GUIUtilities.confirm(this,
				"edit-abbrev.duplicate",null,
				JOptionPane.YES_NO_OPTION,
				JOptionPane.WARNING_MESSAGE);
			return (result == JOptionPane.YES_OPTION);
		}

		return true;
	} //}}}

	//}}}

	//{{{ ActionHandler class
	class ActionHandler implements ActionListener
	{
		public void actionPerformed(ActionEvent evt)
		{
			if(evt.getSource() == ok)
			{
				if(editor.getAbbrev() == null
					|| editor.getAbbrev().length() == 0)
				{
					getToolkit().beep();
					return;
				}

				if(!checkForExistingAbbrev())
					return;

				isOK = true;
			}

			dispose();
		}
	} //}}}

	//{{{ KeyHandler class
	class KeyHandler extends KeyAdapter
	{
		public void keyPressed(KeyEvent evt)
		{
			if(evt.getKeyCode() == KeyEvent.VK_ESCAPE)
				dispose();
		}
	} //}}}
}