completions,true);

/*
 * ActionBar.java - For invoking actions directly
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
import bsh.NameSpace;
import java.awt.event.*;
import java.awt.*;
import java.util.ArrayList;
import java.util.Arrays;
import javax.swing.event.*;
import javax.swing.*;
import org.gjt.sp.jedit.*;
//}}}

/**
 * Action invocation bar.
 */
public class ActionBar extends JPanel
{
	//{{{ ActionBar constructor
	public ActionBar(final View view, boolean temp)
	{
		setLayout(new BoxLayout(this,BoxLayout.X_AXIS));

		this.view = view;
		this.temp = temp;

		add(Box.createHorizontalStrut(2));

		JLabel label = new JLabel(jEdit.getProperty("view.action.prompt"));
		add(label);
		add(Box.createHorizontalStrut(12));
		add(action = new ActionTextField());
		action.setEnterAddsToHistory(false);
		Dimension max = action.getPreferredSize();
		max.width = Integer.MAX_VALUE;
		action.setMaximumSize(max);
		action.addActionListener(new ActionHandler());
		action.getDocument().addDocumentListener(new DocumentHandler());

		if(temp)
		{
			close = new RolloverButton(GUIUtilities.loadIcon("closebox.gif"));
			close.addActionListener(new ActionHandler());
			close.setToolTipText(jEdit.getProperty(
				"view.action.close-tooltip"));
			add(close);
		}

		// if 'temp' is true, hide search bar after user is done with it
		this.temp = temp;
	} //}}}

	//{{{ getField() method
	public HistoryTextField getField()
	{
		return action;
	} //}}}

	//{{{ goToActionBar() method
	public void goToActionBar()
	{
		repeatCount = view.getInputHandler().getRepeatCount();
		action.setText(null);
		action.grabFocus();
	} //}}}

	//{{{ actionListChanged()
	/**
	 * Called when plugins are added or removed to notify the action bar
	 * that the action list has changed.
	 * @since jEdit 4.2pre2
	 */
	public void actionListChanged()
	{
		actions = null;
	} //}}}

	//{{{ Private members

	private static NameSpace namespace = new NameSpace(
		BeanShell.getNameSpace(),"action bar namespace");

	//{{{ Instance variables
	private View view;
	private boolean temp;
	private int repeatCount;
	private HistoryTextField action;
	private CompletionPopup popup;
	private RolloverButton close;
	private String[] actions;
	//}}}

	//{{{ initActions() method
	private void initActions()
	{
		if(actions != null)
			return;

		actions = jEdit.getActionNames();
		Arrays.sort(actions,new MiscUtilities.StringICaseCompare());
	} //}}}

	//{{{ invoke() method
	private void invoke()
	{
		String cmd;
		if(popup != null)
			cmd = popup.list.getSelectedValue().toString();
		else
		{
			cmd = action.getText().trim();
			int index = cmd.indexOf('=');
			if(index != -1)
			{
				action.addCurrentToHistory();
				String propName = cmd.substring(0,index).trim();
				String propValue = cmd.substring(index + 1).trim();
				String code;
				/* construct a BeanShell snippet instead of
				 * invoking directly so that user can record
				 * property changes in macros. */
				if(propName.startsWith("buffer."))
				{
					if(propName.equals("buffer.mode"))
					{
						code = "buffer.setMode(\""
							+ MiscUtilities.charsToEscapes(
							propValue) + "\");";
					}
					else
					{
						code = "buffer.setStringProperty(\""
							+ MiscUtilities.charsToEscapes(
							propName.substring("buffer.".length())
							) + "\",\""
							+ MiscUtilities.charsToEscapes(
							propValue) + "\");";
					}

					code = code + "\nbuffer.propertiesChanged();";
				}
				else if(propName.startsWith("!buffer."))
				{
					code = "jEdit.setProperty(\""
						+ MiscUtilities.charsToEscapes(
						propName.substring(1)) + "\",\""
						+ MiscUtilities.charsToEscapes(
						propValue) + "\");\n"
						+ "jEdit.propertiesChanged();";
				}
				else
				{
					code = "jEdit.setProperty(\""
						+ MiscUtilities.charsToEscapes(
						propName) + "\",\""
						+ MiscUtilities.charsToEscapes(
						propValue) + "\");\n"
						+ "jEdit.propertiesChanged();"
						+ "EditBus.send(new DockableWindowUpdate(wm,"
						+ "DockableWindowUpdate."
						+ "PROPERTIES_CHANGED,null));";
				}

				Macros.Recorder recorder = view.getMacroRecorder();
				if(recorder != null)
					recorder.record(code);
				BeanShell.eval(view,namespace,code);
				cmd = null;
			}
			else if(cmd.length() != 0)
			{
				String[] completions = getCompletions(cmd);
				if(completions.length != 0)
				{
					cmd = completions[0];
				}
			}
			else
				cmd = null;
		}

		if(popup != null)
		{
			popup.dispose();
			popup = null;
		}

		final String finalCmd = cmd;
		final EditAction act = (finalCmd == null ? null : jEdit.getAction(finalCmd));
		if(temp)
			view.removeToolBar(ActionBar.this);

		SwingUtilities.invokeLater(new Runnable()
		{
			public void run()
			{
				view.getTextArea().grabFocus();
				if(act == null)
				{
					if(finalCmd != null)
					{
						view.getStatus().setMessageAndClear(
							jEdit.getProperty(
							"view.action.no-completions"));
					}
				}
				else
				{
					view.getInputHandler().setRepeatCount(repeatCount);
					view.getInputHandler().invokeAction(act);
				}
			}
		});
	} //}}}

	//{{{ getCompletions() method
	private String[] getCompletions(String str)
	{
		initActions();

		str = str.toLowerCase();
		ArrayList returnValue = new ArrayList(actions.length);
		for(int i = 0; i < actions.length; i++)
		{
			if(actions[i].toLowerCase().indexOf(str) != -1)
				returnValue.add(actions[i]);
		}

		return (String[])returnValue.toArray(new String[returnValue.size()]);
	} //}}}

	//{{{ complete() method
	private void complete(boolean insertLongestPrefix)
	{
		String text = action.getText().trim();
		String[] completions = getCompletions(text);
		if(completions.length == 1)
		{
			if(insertLongestPrefix)
				action.setText(completions[0]);
		}
		else if(completions.length != 0)
		{
			if(insertLongestPrefix)
			{
				String prefix = MiscUtilities.getLongestPrefix(
					completions);
				if(prefix.indexOf(text) != -1)
					action.setText(prefix);
			}

			if(popup != null)
				popup.setModel(completions);
			else
				popup = new CompletionPopup(completions);
			return;
		}

		if(popup != null)
		{
			popup.dispose();
			popup = null;
		}
	} //}}}

	//}}}

	//{{{ Inner classes

	//{{{ ActionHandler class
	class ActionHandler implements ActionListener
	{
		public void actionPerformed(ActionEvent evt)
		{
			if(evt.getSource() == close)
				view.removeToolBar(ActionBar.this);
			else
				invoke();
		}
	} //}}}

	//{{{ DocumentHandler class
	class DocumentHandler implements DocumentListener
	{
		//{{{ insertUpdate() method
		public void insertUpdate(DocumentEvent evt)
		{
			if(popup != null)
				complete(false);
		} //}}}

		//{{{ removeUpdate() method
		public void removeUpdate(DocumentEvent evt)
		{
			if(popup != null)
				complete(false);
		} //}}}

		//{{{ changedUpdate() method
		public void changedUpdate(DocumentEvent evt) {}
		//}}}
	} //}}}

	//{{{ ActionTextField class
	class ActionTextField extends HistoryTextField
	{
		boolean repeat;
		boolean nonDigit;

		ActionTextField()
		{
			super("action");
			setSelectAllOnFocus(true);
		}

		public boolean isManagingFocus()
		{
			return false;
		}

		public boolean getFocusTraversalKeysEnabled()
		{
			return false;
		}

		public void processKeyEvent(KeyEvent evt)
		{
			evt = KeyEventWorkaround.processKeyEvent(evt);
			if(evt == null)
				return;

			switch(evt.getID())
			{
			case KeyEvent.KEY_TYPED:
				char ch = evt.getKeyChar();
				if(!nonDigit && Character.isDigit(ch))
				{
					super.processKeyEvent(evt);
					repeat = true;
					repeatCount = Integer.parseInt(action.getText());
				}
				else
				{
					nonDigit = true;
					if(repeat)
						passToView(evt);
					else
						super.processKeyEvent(evt);
				}
				break;
			case KeyEvent.KEY_PRESSED:
				int keyCode = evt.getKeyCode();
				if(evt.isActionKey()
					|| evt.isControlDown()
					|| evt.isAltDown()
					|| evt.isMetaDown()
					|| keyCode == KeyEvent.VK_BACK_SPACE
					|| keyCode == KeyEvent.VK_DELETE
					|| keyCode == KeyEvent.VK_ENTER
					|| keyCode == KeyEvent.VK_TAB
					|| keyCode == KeyEvent.VK_ESCAPE)
				{
					nonDigit = true;
					if(repeat)
					{
						passToView(evt);
						break;
					}
					else if(keyCode == KeyEvent.VK_TAB)
					{
						complete(true);
					}
					else if(keyCode == KeyEvent.VK_ESCAPE)
					{
						evt.consume();
						if(popup != null)
						{
							popup.dispose();
							popup = null;
							action.requestFocus();
						}
						else
						{
							if(temp)
								view.removeToolBar(ActionBar.this);
							view.getEditPane().focusOnTextArea();
						}
						break;
					}
					else if((keyCode == KeyEvent.VK_UP
						|| keyCode == KeyEvent.VK_DOWN)
						&& popup != null)
					{
						popup.list.processKeyEvent(evt);
						break;
					}
				}
				super.processKeyEvent(evt);
				break;
			}
		}

		private void passToView(final KeyEvent evt)
		{
			if(temp)
				view.removeToolBar(ActionBar.this);
			SwingUtilities.invokeLater(new Runnable()
			{
				public void run()
				{
					view.getTextArea().grabFocus();
					view.getInputHandler().setRepeatCount(repeatCount);
					view.getInputHandler().processKeyEvent(evt);
				}
			});
		}

		public void addNotify()
		{
			super.addNotify();
			repeat = nonDigit = false;
		}
	} //}}}

	//{{{ CompletionPopup class
	class CompletionPopup extends JWindow
	{
		CompletionList list;

		//{{{ CompletionPopup constructor
		CompletionPopup(String[] actions)
		{
			super(view);

			setContentPane(new JPanel(new BorderLayout())
			{
				/**
				 * Returns if this component can be traversed by pressing the
				 * Tab key. This returns false.
				 */
				public boolean isManagingFocus()
				{
					return false;
				}

				/**
				 * Makes the tab key work in Java 1.4.
				 */
				public boolean getFocusTraversalKeysEnabled()
				{
					return false;
				}
			});

			list = new CompletionList(actions);
			list.setVisibleRowCount(8);
			list.addMouseListener(new MouseHandler());
			list.setSelectedIndex(0);
			list.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);

			// stupid scrollbar policy is an attempt to work around
			// bugs people have been seeing with IBM's JDK -- 7 Sep 2000
			JScrollPane scroller = new JScrollPane(list,
				JScrollPane.VERTICAL_SCROLLBAR_ALWAYS,
				JScrollPane.HORIZONTAL_SCROLLBAR_NEVER);

			getContentPane().add(scroller, BorderLayout.CENTER);

			GUIUtilities.requestFocus(this,list);

			pack();
			Point p = new Point(0,-getHeight());
			SwingUtilities.convertPointToScreen(p,action);
			setLocation(p);
			show();

			KeyHandler keyHandler = new KeyHandler();
			addKeyListener(keyHandler);
			list.addKeyListener(keyHandler);
		} //}}}

		//{{{ setModel() method
		void setModel(String[] actions)
		{
			list.setListData(actions);
			list.setSelectedIndex(0);
		} //}}}

		//{{{ MouseHandler class
		class MouseHandler extends MouseAdapter
		{
			public void mouseClicked(MouseEvent evt)
			{
				invoke();
			}
		} //}}}

		//{{{ CompletionList class
		class CompletionList extends JList
		{
			CompletionList(Object[] data)
			{
				super(data);
			}

			// we need this public not protected
			public void processKeyEvent(KeyEvent evt)
			{
				super.processKeyEvent(evt);
			}
		} //}}}

		//{{{ KeyHandler class
		class KeyHandler extends KeyAdapter
		{
			public void keyTyped(KeyEvent evt)
			{
				action.processKeyEvent(evt);
			}

			public void keyPressed(KeyEvent evt)
			{
				int keyCode = evt.getKeyCode();
				if(keyCode == KeyEvent.VK_ESCAPE)
					action.processKeyEvent(evt);
				else if(keyCode == KeyEvent.VK_ENTER)
					invoke();
				else if(keyCode == KeyEvent.VK_UP)
				{
					int selected = list.getSelectedIndex();
					if(selected == 0)
					{
						list.setSelectedIndex(
							list.getModel().getSize()
							- 1);
						evt.consume();
					}
				}
				else if(keyCode == KeyEvent.VK_DOWN)
				{
					int selected = list.getSelectedIndex();
					if(selected == list.getModel().getSize() - 1)
					{
						list.setSelectedIndex(0);
						evt.consume();
					}
				}
			}
		} //}}}
	} //}}}

	//}}}
}