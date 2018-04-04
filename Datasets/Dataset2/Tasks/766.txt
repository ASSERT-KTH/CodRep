&& textArea.selectionManager.insideSelection(x,y)

/*
 * JEditTextArea.java - jEdit's text component
 * :tabSize=8:indentSize=8:noTabs=false:
 * :folding=explicit:collapseFolds=1:
 *
 * Copyright (C) 1999, 2004 Slava Pestov
 * Portions copyright (C) 2000 Ollie Rutherfurd
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

package org.gjt.sp.jedit.textarea;

//{{{ Imports
import java.awt.*;
import java.awt.event.*;
import java.lang.reflect.Method;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;
import java.util.Set;
import java.util.TooManyListenersException;
import java.util.TreeSet;
import java.util.Vector;
import javax.swing.*;
import javax.swing.border.*;
import javax.swing.event.*;
import javax.swing.plaf.metal.MetalLookAndFeel;
import javax.swing.text.Segment;
import org.gjt.sp.jedit.*;
import org.gjt.sp.jedit.buffer.*;
import org.gjt.sp.jedit.gui.*;
import org.gjt.sp.jedit.syntax.*;
import org.gjt.sp.util.Log;
//}}}

class MouseHandler extends MouseInputAdapter
{
	//{{{ MouseHandler constructor
	MouseHandler(JEditTextArea textArea)
	{
		this.textArea = textArea;
	} //}}}
	
	//{{{ mousePressed() method
	public void mousePressed(MouseEvent evt)
	{
		control = (OperatingSystem.isMacOS() && evt.isMetaDown())
			|| (!OperatingSystem.isMacOS() && evt.isControlDown());

		// so that Home <mouse click> Home is not the same
		// as pressing Home twice in a row
		textArea.getInputHandler().resetLastActionCount();

		quickCopyDrag = (textArea.isQuickCopyEnabled() &&
			GUIUtilities.isMiddleButton(evt.getModifiers()));

		if(!quickCopyDrag)
		{
			textArea.requestFocus();
			JEditTextArea.focusedComponent = textArea;
		}

		if(!textArea.getBuffer().isLoaded())
			return;

		int x = evt.getX();
		int y = evt.getY();

		dragStart = textArea.xyToOffset(x,y,
			!(textArea.getPainter().isBlockCaretEnabled()
			|| textArea.isOverwriteEnabled()));
		dragStartLine = textArea.getLineOfOffset(dragStart);
		dragStartOffset = dragStart - textArea.getLineStartOffset(
			dragStartLine);

		if(GUIUtilities.isPopupTrigger(evt)
			&& textArea.getRightClickPopup() != null)
		{
			if(textArea.isRightClickPopupEnabled())
				textArea.handlePopupTrigger(evt);
			return;
		}

		dragged = false;

		textArea.blink = true;
		textArea.invalidateLine(textArea.getCaretLine());

		clickCount = evt.getClickCount();

		if(textArea.isDragEnabled()
			&& textArea.insideSelection(x,y)
			&& clickCount == 1 && !evt.isShiftDown())
		{
			maybeDragAndDrop = true;
			textArea.moveCaretPosition(dragStart,false);
			return;
		}
		else
			maybeDragAndDrop = false;

		switch(clickCount)
		{
		case 1:
			doSingleClick(evt);
			break;
		case 2:
			doDoubleClick();
			break;
		default: //case 3:
			doTripleClick();
			break;
		}
	} //}}}

	//{{{ doSingleClick() method
	private void doSingleClick(MouseEvent evt)
	{
		/* if(buffer.insideCompoundEdit())
			buffer.endCompoundEdit(); */
		int x = evt.getX();

		int extraEndVirt = 0;
		if(textArea.chunkCache.getLineInfo(
			textArea.getLastScreenLine()).lastSubregion)
		{
			float dragStartLineWidth = textArea.offsetToXY(
				dragStartLine,
				textArea.getLineLength(dragStartLine)).x;
			if(x > dragStartLineWidth)
			{
				extraEndVirt = (int)(
					(x - dragStartLineWidth)
					/ textArea.charWidth);
				if(!textArea.getPainter().isBlockCaretEnabled()
					&& !textArea.isOverwriteEnabled()
					&& (x - textArea.getHorizontalOffset())
					% textArea.charWidth > textArea.charWidth / 2)
				{
					extraEndVirt++;
				}
			}
		}

		if(control || textArea.isRectangularSelectionEnabled())
		{
			int screenLine = (evt.getY() / textArea.getPainter()
				.getFontMetrics().getHeight());
			if(screenLine > textArea.getLastScreenLine())
				screenLine = textArea.getLastScreenLine();
			ChunkCache.LineInfo info = textArea.chunkCache.getLineInfo(screenLine);
			if(info.lastSubregion && extraEndVirt != 0)
			{
				if(!textArea.isEditable())
				{
					textArea.getToolkit().beep();
					return;
				}

				// control-click in virtual space inserts
				// whitespace and moves caret
				String whitespace = MiscUtilities
					.createWhiteSpace(extraEndVirt,0);
				textArea.getBuffer().insert(dragStart,whitespace);

				dragStart += whitespace.length();
			}
		}

		if(evt.isShiftDown())
		{
			// XXX: getMarkPosition() deprecated!
			textArea.resizeSelection(
				textArea.getMarkPosition(),dragStart,extraEndVirt,
				textArea.isRectangularSelectionEnabled()
				|| control);

			if(!quickCopyDrag)
				textArea.moveCaretPosition(dragStart,false);

			// so that shift-click-drag works
			dragStartLine = textArea.getMarkLine();
			dragStart = textArea.getMarkPosition();
			dragStartOffset = dragStart
				- textArea.getLineStartOffset(dragStartLine);

			// so that quick copy works
			dragged = true;

			return;
		}

		if(!quickCopyDrag)
			textArea.moveCaretPosition(dragStart,false);

		if(!(textArea.isMultipleSelectionEnabled()
			|| quickCopyDrag))
			textArea.selectNone();
	} //}}}

	//{{{ doDoubleClick() method
	private void doDoubleClick()
	{
		// Ignore empty lines
		if(textArea.getLineLength(dragStartLine) == 0)
			return;

		String lineText = textArea.getLineText(dragStartLine);
		String noWordSep = textArea.getBuffer()
			.getStringProperty("noWordSep");
		if(dragStartOffset == textArea.getLineLength(dragStartLine))
			dragStartOffset--;

		boolean joinNonWordChars =
			jEdit.getBooleanProperty("view.joinNonWordChars");
		int wordStart = TextUtilities.findWordStart(lineText,
			dragStartOffset,noWordSep,joinNonWordChars);
		int wordEnd = TextUtilities.findWordEnd(lineText,
			dragStartOffset+1,noWordSep,joinNonWordChars);

		int lineStart = textArea.getLineStartOffset(dragStartLine);
		Selection sel = new Selection.Range(
			lineStart + wordStart,
			lineStart + wordEnd);
		if(textArea.isMultipleSelectionEnabled())
			textArea.addToSelection(sel);
		else
			textArea.setSelection(sel);

		if(quickCopyDrag)
			quickCopyDrag = false;

		textArea.moveCaretPosition(lineStart + wordEnd,false);

		dragged = true;
	} //}}}

	//{{{ doTripleClick() method
	private void doTripleClick()
	{
		int newCaret = textArea.getLineEndOffset(dragStartLine);
		if(dragStartLine == textArea.getLineCount() - 1)
			newCaret--;

		Selection sel = new Selection.Range(
			textArea.getLineStartOffset(dragStartLine),
			newCaret);
		if(textArea.isMultipleSelectionEnabled())
			textArea.addToSelection(sel);
		else
			textArea.setSelection(sel);

		if(quickCopyDrag)
			quickCopyDrag = false;

		textArea.moveCaretPosition(newCaret,false);

		dragged = true;
	} //}}}

	//{{{ mouseDragged() method
	public void mouseDragged(MouseEvent evt)
	{
		if(maybeDragAndDrop)
		{
			textArea.startDragAndDrop(evt,control);
			return;
		}

		if(textArea.isDragInProgress())
			return;

		JPopupMenu popup = textArea.getRightClickPopup();
		if(GUIUtilities.isPopupTrigger(evt)
			|| (popup != null && popup.isVisible()))
			return;

		if(!textArea.getBuffer().isLoaded())
			return;

		TextAreaPainter painter = textArea.getPainter();
		if(evt.getY() < 0)
		{
			int delta = Math.min(-1,evt.getY()
				/ painter.getFontMetrics()
				.getHeight());
			textArea.setFirstLine(textArea.getFirstLine() + delta);
		}
		else if(evt.getY() >= painter.getHeight())
		{
			int delta = Math.max(1,(evt.getY()
				- painter.getHeight()) /
				painter.getFontMetrics()
				.getHeight());
			if(textArea.lastLinePartial)
				delta--;
			textArea.setFirstLine(textArea.getFirstLine() + delta);
		}

		if(quickCopyDrag)
		{
			textArea.setStatusMessage(jEdit.getProperty(
				"view.status.rect-quick-copy"));
			clearStatus = true;
		}

		switch(clickCount)
		{
		case 1:
			doSingleDrag(evt);
			break;
		case 2:
			doDoubleDrag(evt);
			break;
		default: //case 3:
			doTripleDrag(evt);
			break;
		}
	} //}}}

	//{{{ doSingleDrag() method
	private void doSingleDrag(MouseEvent evt)
	{
		dragged = true;

		TextAreaPainter painter = textArea.getPainter();

		int x = evt.getX();
		int y = evt.getY();
		if(y < 0)
			y = 0;
		else if(y >= painter.getHeight())
			y = painter.getHeight() - 1;

		int dot = textArea.xyToOffset(x,y,
			(!painter.isBlockCaretEnabled()
			&& !textArea.isOverwriteEnabled())
			|| quickCopyDrag);
		int dotLine = textArea.getLineOfOffset(dot);
		int extraEndVirt = 0;

		if(textArea.chunkCache.getLineInfo(
			textArea.getLastScreenLine())
			.lastSubregion)
		{
			float dotLineWidth = textArea.offsetToXY(
				dotLine,textArea.getLineLength(dotLine)).x;
			if(x > dotLineWidth)
			{
				extraEndVirt = (int)((x - dotLineWidth) / textArea.charWidth);
				if(!painter.isBlockCaretEnabled()
					&& !textArea.isOverwriteEnabled()
					&& (x - textArea.getHorizontalOffset()) % textArea.charWidth > textArea.charWidth / 2)
					extraEndVirt++;
			}
		}

		textArea.resizeSelection(dragStart,dot,extraEndVirt,
			textArea.isRectangularSelectionEnabled()
			|| control);

		if(quickCopyDrag)
		{
			// just scroll to the dragged location
			textArea.scrollTo(dotLine,dot - textArea.getLineStartOffset(dotLine),false);
		}
		else
		{
			if(dot != textArea.getCaretPosition())
				textArea.moveCaretPosition(dot,false);
			if(textArea.isRectangularSelectionEnabled()
				&& extraEndVirt != 0)
			{
				textArea.scrollTo(dotLine,dot - textArea.getLineStartOffset(dotLine)
					+ extraEndVirt,false);
			}
		}
	} //}}}

	//{{{ doDoubleDrag() method
	private void doDoubleDrag(MouseEvent evt)
	{
		int markLineStart = textArea.getLineStartOffset(dragStartLine);
		int markLineLength = textArea.getLineLength(dragStartLine);
		int mark = dragStartOffset;

		TextAreaPainter painter = textArea.getPainter();

		int pos = textArea.xyToOffset(evt.getX(),
			Math.max(0,Math.min(painter.getHeight(),evt.getY())),
			!(painter.isBlockCaretEnabled()
			|| textArea.isOverwriteEnabled()));
		int line = textArea.getLineOfOffset(pos);
		int lineStart = textArea.getLineStartOffset(line);
		int lineLength = textArea.getLineLength(line);
		int offset = pos - lineStart;

		String lineText = textArea.getLineText(line);
		String markLineText = textArea.getLineText(dragStartLine);
		String noWordSep = textArea.getBuffer()
			.getStringProperty("noWordSep");
		boolean joinNonWordChars =
			jEdit.getBooleanProperty("view.joinNonWordChars");

		if(markLineStart + dragStartOffset > lineStart + offset)
		{
			if(offset != 0 && offset != lineLength)
			{
				offset = TextUtilities.findWordStart(
					lineText,offset,noWordSep,
					joinNonWordChars);
			}

			if(markLineLength != 0)
			{
				mark = TextUtilities.findWordEnd(
					markLineText,mark,noWordSep,
					joinNonWordChars);
			}
		}
		else
		{
			if(offset != 0 && lineLength != 0)
			{
				offset = TextUtilities.findWordEnd(
					lineText,offset,noWordSep,
					joinNonWordChars);
			}

			if(mark != 0 && mark != markLineLength)
			{
				mark = TextUtilities.findWordStart(
					markLineText,mark,noWordSep,
					joinNonWordChars);
			}
		}

		if(lineStart + offset == textArea.getCaretPosition())
			return;

		textArea.resizeSelection(markLineStart + mark,
			lineStart + offset,0,false);
		textArea.moveCaretPosition(lineStart + offset,false);

		dragged = true;
	} //}}}

	//{{{ doTripleDrag() method
	private void doTripleDrag(MouseEvent evt)
	{
		TextAreaPainter painter = textArea.getPainter();
		
		int offset = textArea.xyToOffset(evt.getX(),
			Math.max(0,Math.min(painter.getHeight(),evt.getY())),
			false);
		int mouseLine = textArea.getLineOfOffset(offset);
		int mark;
		int mouse;
		if(dragStartLine > mouseLine)
		{
			mark = textArea.getLineEndOffset(dragStartLine) - 1;
			if(offset == textArea.getLineEndOffset(mouseLine) - 1)
				mouse = offset;
			else
				mouse = textArea.getLineStartOffset(mouseLine);
		}
		else
		{
			mark = textArea.getLineStartOffset(dragStartLine);
			if(offset == textArea.getLineStartOffset(mouseLine))
				mouse = offset;
			else if(offset == textArea.getLineEndOffset(mouseLine) - 1
				&& mouseLine != textArea.getLineCount() - 1)
				mouse = textArea.getLineEndOffset(mouseLine);
			else
				mouse = textArea.getLineEndOffset(mouseLine) - 1;
		}

		mouse = Math.min(textArea.getBuffer().getLength(),mouse);

		if(mouse == textArea.getCaretPosition())
			return;

		textArea.resizeSelection(mark,mouse,0,false);
		textArea.moveCaretPosition(mouse,false);

		dragged = true;
	} //}}}

	//{{{ mouseReleased() method
	public void mouseReleased(MouseEvent evt)
	{
		// middle mouse button drag inserts selection
		// at caret position
		Selection sel = textArea.getSelectionAtOffset(dragStart);
		if(dragged && sel != null)
		{
			Registers.setRegister('%',textArea.getSelectedText(sel));
			if(quickCopyDrag)
			{
				textArea.removeFromSelection(sel);
				Registers.paste(JEditTextArea.focusedComponent,
					'%',sel instanceof Selection.Rect);

				JEditTextArea.focusedComponent.requestFocus();
			}
		}
		else if(!dragged && textArea.isQuickCopyEnabled() &&
			GUIUtilities.isMiddleButton(evt.getModifiers()))
		{
			textArea.requestFocus();
			JEditTextArea.focusedComponent = textArea;

			textArea.setCaretPosition(dragStart,false);
			if(!textArea.isEditable())
				textArea.getToolkit().beep();
			else
				Registers.paste(textArea,'%',control);
		}
		else if(maybeDragAndDrop
			&& !textArea.isMultipleSelectionEnabled())
		{
			textArea.selectNone();
		}

		dragged = false;

		if(clearStatus)
		{
			clearStatus = false;
			textArea.setStatusMessage(null);
		}
	} //}}}

	//{{{ Private members
	private JEditTextArea textArea;
	private int dragStartLine;
	private int dragStartOffset;
	private int dragStart;
	private int clickCount;
	private boolean dragged;
	private boolean quickCopyDrag;
	private boolean clearStatus;
	private boolean control;
	/* with drag and drop on, a mouse down in a selection does not
	immediately deselect */
	private boolean maybeDragAndDrop;
	//}}}
}