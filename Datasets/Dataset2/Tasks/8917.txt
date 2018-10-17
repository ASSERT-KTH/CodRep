.StringCompare());

/*
 * CompleteWord.java - Complete word dialog
 * :tabSize=8:indentSize=8:noTabs=false:
 * :folding=explicit:collapseFolds=1:
 *
 * Copyright (C) 2000, 2001 Slava Pestov
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
import java.awt.*;
import java.awt.event.*;
import java.util.HashSet;
import java.util.TreeSet;
import java.util.Set;
import org.gjt.sp.jedit.syntax.*;
import org.gjt.sp.jedit.textarea.*;
import org.gjt.sp.jedit.*;
//}}}

public class CompleteWord extends JWindow
{
	//{{{ completeWord() method
	public static void completeWord(View view)
	{
		JEditTextArea textArea = view.getTextArea();
		Buffer buffer = view.getBuffer();
		int caretLine = textArea.getCaretLine();
		int caret = textArea.getCaretPosition();

		if(!buffer.isEditable())
		{
			textArea.getToolkit().beep();
			return;
		}

		KeywordMap keywordMap = buffer.getKeywordMapAtOffset(caret);
		String noWordSep = getNonAlphaNumericWordChars(
			buffer,keywordMap);
		String word = getWordToComplete(buffer,caretLine,
			caret,noWordSep);
		if(word == null)
		{
			textArea.getToolkit().beep();
			return;
		}

		Completion[] completions = getCompletions(buffer,word,caret);

		if(completions.length == 0)
		{
			textArea.getToolkit().beep();
		}
		//{{{ if there is only one competion, insert in buffer
		else if(completions.length == 1)
		{
			Completion c = completions[0];

			if(c.text.equals(word))
			{
				textArea.getToolkit().beep();
			}
			else
			{
				textArea.setSelectedText(c.text.substring(
					word.length()));
			}
		} //}}}
		//{{{ show popup if > 1
		else
		{
			String longestPrefix = MiscUtilities.getLongestPrefix(
				completions,
				keywordMap != null
				? keywordMap.getIgnoreCase()
				: false);

			if (word.length() < longestPrefix.length())
			{
				buffer.insert(caret,longestPrefix.substring(
					word.length()));
			}

			textArea.scrollToCaret(false);
			Point location = textArea.offsetToXY(
				caret - word.length());
			location.y += textArea.getPainter().getFontMetrics()
				.getHeight();

			SwingUtilities.convertPointToScreen(location,
				textArea.getPainter());
			new CompleteWord(view,longestPrefix,
				completions,location,noWordSep);
		} //}}}
	} //}}}

	//{{{ CompleteWord constructor
	public CompleteWord(View view, String word, Completion[] completions,
		Point location, String noWordSep)
	{
		super(view);

		this.noWordSep = noWordSep;

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

		this.view = view;
		this.textArea = view.getTextArea();
		this.buffer = view.getBuffer();
		this.word = word;

		words = new JList(completions);

		words.setVisibleRowCount(Math.min(completions.length,8));

		words.addMouseListener(new MouseHandler());
		words.setSelectedIndex(0);
		words.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);
		words.setCellRenderer(new Renderer());

		// stupid scrollbar policy is an attempt to work around
		// bugs people have been seeing with IBM's JDK -- 7 Sep 2000
		JScrollPane scroller = new JScrollPane(words,
			JScrollPane.VERTICAL_SCROLLBAR_ALWAYS,
			JScrollPane.HORIZONTAL_SCROLLBAR_NEVER);

		getContentPane().add(scroller, BorderLayout.CENTER);

		GUIUtilities.requestFocus(this,words);

		pack();
		setLocation(location);
		show();

		KeyHandler keyHandler = new KeyHandler();
		addKeyListener(keyHandler);
		words.addKeyListener(keyHandler);
		view.setKeyEventInterceptor(keyHandler);
	} //}}}

	//{{{ dispose() method
	public void dispose()
	{
		view.setKeyEventInterceptor(null);
		super.dispose();
		SwingUtilities.invokeLater(new Runnable()
		{
			public void run()
			{
				textArea.requestFocus();
			}
		});
	} //}}}

	//{{{ Private members

	//{{{ getNonAlphaNumericWordChars() method
	private static String getNonAlphaNumericWordChars(Buffer buffer,
		KeywordMap keywordMap)
	{
		// figure out what constitutes a word character and what
		// doesn't
		String noWordSep = buffer.getStringProperty("noWordSep");
		if(noWordSep == null)
			noWordSep = "";
		if(keywordMap != null)
		{
			String keywordNoWordSep = keywordMap.getNonAlphaNumericChars();
			if(keywordNoWordSep != null)
				noWordSep = noWordSep + keywordNoWordSep;
		}

		return noWordSep;
	} //}}}

	//{{{ getWordToComplete() method
	private static String getWordToComplete(Buffer buffer, int caretLine,
		int caret, String noWordSep)
	{
		String line = buffer.getLineText(caretLine);
		int dot = caret - buffer.getLineStartOffset(caretLine);
		if(dot == 0)
			return null;

		char ch = line.charAt(dot-1);
		if(!Character.isLetterOrDigit(ch)
			&& noWordSep.indexOf(ch) == -1)
		{
			// attempting to expand non-word char
			return null;
		}

		int wordStart = TextUtilities.findWordStart(line,dot-1,noWordSep);
		String word = line.substring(wordStart,dot);
		if(word.length() == 0)
			return null;

		return word;
	} //}}}

	//{{{ getCompletions() method
	private static Completion[] getCompletions(Buffer buffer, String word,
		int caret)
	{
		// build a list of unique words in all visible buffers
		Set completions = new TreeSet(new MiscUtilities
			.StringICaseCompare());
		Set buffers = new HashSet();

		// only complete current buffer's keyword map
		KeywordMap keywordMap = buffer.getKeywordMapAtOffset(caret);
		String noWordSep = getNonAlphaNumericWordChars(
			buffer,keywordMap);

		View views = jEdit.getFirstView();
		while(views != null)
		{
			EditPane[] panes = views.getEditPanes();
			for(int i = 0; i < panes.length; i++)
			{
				Buffer b = panes[i].getBuffer();
				if(buffers.contains(b))
					continue;

				buffers.add(b);

				// only complete current buffer's keyword map
				KeywordMap _keywordMap;
				if(b == buffer)
					_keywordMap = keywordMap;
				else
					_keywordMap = null;

				int offset = (b == buffer ? caret : 0);

				getCompletions(b,word,keywordMap,noWordSep,
					offset,completions);
			}

			views = views.getNext();
		}

		Completion[] completionArray = (Completion[])completions
			.toArray(new Completion[completions.size()]);

		return completionArray;
	} //}}}

	//{{{ getCompletions() method
	private static void getCompletions(Buffer buffer, String word,
		KeywordMap keywordMap, String noWordSep, int caret,
		Set completions)
	{
		int wordLen = word.length();

		//{{{ try to find matching keywords
		if(keywordMap != null)
		{
			String[] keywords = keywordMap.getKeywords();
			for(int i = 0; i < keywords.length; i++)
			{
				String _keyword = keywords[i];
				if(_keyword.regionMatches(keywordMap.getIgnoreCase(),
					0,word,0,wordLen))
				{
					Completion keyword = new Completion(_keyword,true);
					if(!completions.contains(keyword))
					{
						completions.add(keyword);
					}
				}
			}
		} //}}}

		//{{{ loop through all lines of current buffer
		for(int i = 0; i < buffer.getLineCount(); i++)
		{
			String line = buffer.getLineText(i);
			int start = buffer.getLineStartOffset(i);

			// check for match at start of line

			if(line.startsWith(word) && caret != start + word.length())
			{
				String _word = completeWord(line,0,noWordSep);
				Completion comp = new Completion(_word,false);

				// remove duplicates
				if(!completions.contains(comp))
				{
					completions.add(comp);
				}
			}

			// check for match inside line
			int len = line.length() - word.length();
			for(int j = 0; j < len; j++)
			{
				char c = line.charAt(j);
				if(!Character.isLetterOrDigit(c) && noWordSep.indexOf(c) == -1)
				{
					if(line.regionMatches(j + 1,word,0,wordLen)
						&& caret != start + j + word.length() + 1)
					{
						String _word = completeWord(line,j + 1,noWordSep);
						Completion comp = new Completion(_word,false);

						// remove duplicates
						if(!completions.contains(comp))
						{
							completions.add(comp);
						}
					}
				}
			}
		} //}}}
	} //}}}

	//{{{ completeWord() method
	private static String completeWord(String line, int offset, String noWordSep)
	{
		// '+ 1' so that findWordEnd() doesn't pick up the space at the start
		int wordEnd = TextUtilities.findWordEnd(line,offset + 1,noWordSep);
		return line.substring(offset,wordEnd);
	} //}}}

	//{{{ Instance variables
	private View view;
	private JEditTextArea textArea;
	private Buffer buffer;
	private String word;
	private JList words;
	private String noWordSep;
	//}}}

	//{{{ insertSelected() method
	private void insertSelected()
	{
		textArea.setSelectedText(words.getSelectedValue().toString()
			.substring(word.length()));
		dispose();
	} //}}}

	//}}}

	//{{{ Completion class
	static class Completion
	{
		String text;
		boolean keyword;

		Completion(String text, boolean keyword)
		{
			this.text = text;
			this.keyword = keyword;
		}

		public String toString()
		{
			return text;
		}

		public int hashCode()
		{
			return text.hashCode();
		}

		public boolean equals(Object obj)
		{
			if(obj instanceof Completion)
				return ((Completion)obj).text.equals(text);
			else
				return false;
		}
	} //}}}

	//{{{ Renderer class
	static class Renderer extends DefaultListCellRenderer
	{
		public Component getListCellRendererComponent(JList list, Object value,
			int index, boolean isSelected, boolean cellHasFocus)
		{
			super.getListCellRendererComponent(list,null,index,
				isSelected,cellHasFocus);

			Completion comp = (Completion)value;

			if(index < 9)
				setText((index + 1) + ": " + comp.text);
			else if(index == 9)
				setText("0: " + comp.text);
			else
				setText(comp.text);

			if(comp.keyword)
				setFont(list.getFont().deriveFont(Font.BOLD));
			else
				setFont(list.getFont());

			return this;
		}
	} //}}}

	//{{{ KeyHandler class
	class KeyHandler extends KeyAdapter
	{
		//{{{ keyPressed() method
		public void keyPressed(KeyEvent evt)
		{
			switch(evt.getKeyCode())
			{
			case KeyEvent.VK_TAB:
			case KeyEvent.VK_ENTER:
				insertSelected();
				evt.consume();
				break;
			case KeyEvent.VK_ESCAPE:
				dispose();
				evt.consume();
				break;
			case KeyEvent.VK_UP:
				int selected = words.getSelectedIndex();

				if(selected == 0)
					selected = words.getModel().getSize() - 1;
				else if(getFocusOwner() == words)
					return;
				else
					selected = selected - 1;

				words.setSelectedIndex(selected);
				words.ensureIndexIsVisible(selected);

				evt.consume();
				break;
			case KeyEvent.VK_DOWN:
				/* int */ selected = words.getSelectedIndex();

				if(selected == words.getModel().getSize() - 1)
					selected = 0;
				else if(getFocusOwner() == words)
					return;
				else
					selected = selected + 1;

				words.setSelectedIndex(selected);
				words.ensureIndexIsVisible(selected);

				evt.consume();
				break;
			case KeyEvent.VK_BACK_SPACE:
				if(word.length() == 1)
				{
					textArea.backspace();
					evt.consume();
					dispose();
				}
				else
				{
					word = word.substring(0,word.length() - 1);
					textArea.backspace();
					int caret = textArea.getCaretPosition();

					Completion[] completions
						= getCompletions(buffer,word,
						caret);

					if(completions.length == 0)
					{
						dispose();
						return;
					}

					words.setListData(completions);
					words.setSelectedIndex(0);
					words.setVisibleRowCount(Math.min(completions.length,8));

					pack();

					evt.consume();
				}
				break;
			default:
				if(evt.isActionKey()
					|| evt.isControlDown()
					|| evt.isAltDown()
					|| evt.isMetaDown())
				{
					dispose();
					view.processKeyEvent(evt);
				}
				break;
			}
		} //}}}

		//{{{ keyTyped() method
		public void keyTyped(KeyEvent evt)
		{
			char ch = evt.getKeyChar();
			evt = KeyEventWorkaround.processKeyEvent(evt);
			if(evt == null)
				return;

			if(Character.isDigit(ch))
			{
				int index = ch - '0';
				if(index == 0)
					index = 9;
				else
					index--;
				if(index < words.getModel().getSize())
				{
					words.setSelectedIndex(index);
					textArea.setSelectedText(words.getModel()
						.getElementAt(index).toString()
						.substring(word.length()));
					dispose();
					return;
				}
				else
					/* fall through */;
			}

			// \t handled above
			if(ch != '\b' && ch != '\t')
			{
				/* eg, foo<C+b>, will insert foobar, */
				if(!Character.isLetterOrDigit(ch) && noWordSep.indexOf(ch) == -1)
				{
					insertSelected();
					textArea.userInput(ch);
					dispose();
					return;
				}

				textArea.userInput(ch);

				word = word + ch;
				int caret = textArea.getCaretPosition();
				KeywordMap keywordMap = buffer.getKeywordMapAtOffset(caret);

				Completion[] completions = getCompletions(
					buffer,word,caret);

				if(completions.length == 0)
				{
					dispose();
					return;
				}

				words.setListData(completions);
				words.setSelectedIndex(0);
				words.setVisibleRowCount(Math.min(completions.length,8));
			}
		} //}}}
	} //}}}

	//{{{ MouseHandler class
	class MouseHandler extends MouseAdapter
	{
		public void mouseClicked(MouseEvent evt)
		{
			insertSelected();
		}
	} //}}}
}