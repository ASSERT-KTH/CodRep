setVisible(true);

/*
 * AddAbbrevDialog.java - Displayed when expanding unknown abbrev
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

import javax.swing.border.*;
import javax.swing.*;
import java.awt.event.*;
import java.awt.*;
import org.gjt.sp.jedit.*;

public class AddAbbrevDialog extends JDialog
{
	public AddAbbrevDialog(View view, String abbrev)
	{
		super(view,jEdit.getProperty("add-abbrev.title"),true);

		this.view = view;

		JPanel content = new JPanel(new BorderLayout());
		content.setBorder(new EmptyBorder(12,12,12,12));
		setContentPane(content);

		editor = new AbbrevEditor();
		editor.setAbbrev(abbrev);
		editor.setBorder(new EmptyBorder(6,0,12,0));
		content.add(BorderLayout.CENTER,editor);

		Box box = new Box(BoxLayout.X_AXIS);
		box.add(Box.createGlue());
		global = new JButton(jEdit.getProperty("add-abbrev.global"));
		global.addActionListener(new ActionHandler());
		box.add(global);
		box.add(Box.createHorizontalStrut(6));
		modeSpecific = new JButton(jEdit.getProperty("add-abbrev.mode"));
		modeSpecific.addActionListener(new ActionHandler());
		box.add(modeSpecific);
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

		if(abbrev == null)
			GUIUtilities.requestFocus(this,editor.getAbbrevField());
		else
			GUIUtilities.requestFocus(this,editor.getBeforeCaretTextArea());

		pack();
		setLocationRelativeTo(view);
		show();
	}

	// private members
	private View view;
	private AbbrevEditor editor;
	private JButton global;
	private JButton modeSpecific;
	private JButton cancel;

	class ActionHandler implements ActionListener
	{
		public void actionPerformed(ActionEvent evt)
		{
			Object source = evt.getSource();
			if(source == global)
			{
				String _abbrev = editor.getAbbrev();
				if(_abbrev == null || _abbrev.length() == 0)
				{
					getToolkit().beep();
					return;
				}
				Abbrevs.addGlobalAbbrev(_abbrev,editor.getExpansion());
				Abbrevs.expandAbbrev(view,false);
			}
			else if(source == modeSpecific)
			{
				String _abbrev = editor.getAbbrev();
				if(_abbrev == null || _abbrev.length() == 0)
				{
					getToolkit().beep();
					return;
				}
				Abbrevs.addModeAbbrev(view.getBuffer().getMode().getName(),
					_abbrev,editor.getExpansion());
				Abbrevs.expandAbbrev(view,false);
			}

			dispose();
		}
	}

	class KeyHandler extends KeyAdapter
	{
		public void keyPressed(KeyEvent evt)
		{
			if(evt.getKeyCode() == KeyEvent.VK_ESCAPE)
				dispose();
		}
	}
}