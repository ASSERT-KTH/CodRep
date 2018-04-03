lm = font.getLineMetrics(seg.array,

/*
 * BufferPrintable.java - Printable implementation
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

package org.gjt.sp.jedit.print;

//{{{ Imports
import javax.swing.text.*;
import java.awt.font.*;
import java.awt.geom.*;
import java.awt.print.*;
import java.awt.*;
import java.util.*;
import org.gjt.sp.jedit.syntax.*;
import org.gjt.sp.jedit.textarea.ChunkCache;
import org.gjt.sp.jedit.*;
//}}}

class BufferPrintable implements Printable
{
	//{{{ BufferPrintable constructor
	BufferPrintable(Buffer buffer, Font font, boolean header, boolean footer,
		boolean lineNumbers, boolean color)
	{
		this.buffer = buffer;
		this.font = font;
		this.header = header;
		this.footer = footer;
		this.lineNumbers = lineNumbers;

		styles = GUIUtilities.loadStyles(jEdit.getProperty("print.font"),
			jEdit.getIntegerProperty("print.fontsize",10),color);
		styles[Token.NULL] = new SyntaxStyle(textColor,null,font);

		lineList = new ArrayList();
	} //}}}

	//{{{ print() method
	public int print(Graphics _gfx, PageFormat pageFormat, int pageIndex)
		throws PrinterException
	{
		if(pageIndex == currentPage)
			currentLine = currentPageStart;
		else
		{
			if(end)
				return NO_SUCH_PAGE;

			currentPageStart = currentLine;
			currentPage = pageIndex;
		}

		double pageX = pageFormat.getImageableX();
		double pageY = pageFormat.getImageableY();
		double pageWidth = pageFormat.getImageableWidth();
		double pageHeight = pageFormat.getImageableHeight();

		Graphics2D gfx = (Graphics2D)_gfx;

		gfx.setFont(font);

		if(header)
		{
			double headerHeight = paintHeader(gfx,pageX,pageY,pageWidth);
			pageY += headerHeight * 2;
			pageHeight -= headerHeight * 2;
		}

		if(footer)
		{
			double footerHeight = paintFooter(gfx,pageX,pageY,pageWidth,
				pageHeight,pageIndex);
			pageHeight -= footerHeight * 2;
		}

		FontRenderContext frc = gfx.getFontRenderContext();

		// the +1's ensure that 99 gets 3 digits, 103 gets 4 digits,
		// and so on.
		int lineNumberDigits = (int)Math.ceil(Math.log(buffer.getLineCount() + 1)
			/ Math.log(10)) + 1;

		//{{{ now that we know how many chars there are, get the width.
		char[] chars = new char[lineNumberDigits];
		for(int i = 0; i < chars.length; i++)
			chars[i] = ' ';
		double lineNumberWidth = font.getStringBounds(chars,
			0,lineNumberDigits,frc).getWidth();
		//}}}

		//{{{ calculate tab size
		int tabSize = jEdit.getIntegerProperty("print.tabSize",8);
		chars = new char[tabSize];
		for(int i = 0; i < chars.length; i++)
			chars[i] = ' ';
		double tabWidth = font.getStringBounds(chars,
			0,tabSize,frc).getWidth();
		PrintTabExpander e = new PrintTabExpander(pageX,tabWidth);
		//}}}

		Segment seg = new Segment();
		double y = 0.0;

print_loop:	for(;;)
		{
			//{{{ get line text
			if(currentLine == lineList.size())
			{
				buffer.getLineText(currentPhysicalLine,seg);
				LineMetrics lm = font.getLineMetrics(seg.array,
					seg.offset,seg.count,frc);

				Token tokens = buffer.markTokens(currentPhysicalLine)
					.getFirstToken();

				lineList.add(new Integer(++currentPhysicalLine));

				ChunkCache.lineToChunkList(seg,tokens,styles,frc,
					e,(float)(pageWidth - lineNumberWidth),
					lineList);
				if(lineList.size() == currentLine + 1)
					lineList.add(null);
			} //}}}

			y += lm.getHeight();
			if(y >= pageHeight)
				break print_loop;

			Object obj = lineList.get(currentLine++);
			if(obj instanceof Integer)
			{
				//{{{ paint line number
				if(lineNumbers)
				{
					gfx.setFont(font);
					gfx.setColor(lineNumberColor);
					String lineNumberString = String.valueOf(obj);
					gfx.drawString(lineNumberString,
						(float)pageX,(float)(pageY + y));
				} //}}}

				obj = lineList.get(currentLine++);
			}

			if(obj != null)
			{
				ChunkCache.Chunk line = (ChunkCache.Chunk)obj;

				ChunkCache.paintChunkList(line,gfx,
					(float)(pageX + lineNumberWidth),
					(float)(pageY + y),
					(float)(pageWidth - lineNumberWidth),
					Color.white,false);
			}

			if(currentPhysicalLine == buffer.getLineCount()
				&& currentLine == lineList.size())
			{
				end = true;
				break print_loop;
			}
		}

		return PAGE_EXISTS;
	} //}}}

	//{{{ Private members

	//{{{ Static variables
	private static Color headerColor = Color.lightGray;
	private static Color headerTextColor = Color.black;
	private static Color footerColor = Color.lightGray;
	private static Color footerTextColor = Color.black;
	private static Color lineNumberColor = Color.gray;
	private static Color textColor = Color.black;
	//}}}

	//{{{ Instance variables
	private Buffer buffer;
	private Font font;
	private SyntaxStyle[] styles;
	private boolean header;
	private boolean footer;
	private boolean lineNumbers;

	private int currentPage;
	private int currentPageStart;
	private int currentLine;
	private int currentPhysicalLine;
	private boolean end;

	private LineMetrics lm;
	private ArrayList lineList;
	//}}}

	//{{{ paintHeader() method
	private double paintHeader(Graphics2D gfx, double pageX, double pageY,
		double pageWidth)
	{
		String headerText = jEdit.getProperty("print.headerText",
			new String[] { buffer.getPath() });
		FontRenderContext frc = gfx.getFontRenderContext();

		gfx.setColor(headerColor);

		Rectangle2D bounds = font.getStringBounds(headerText,frc);

		Rectangle2D headerBounds = new Rectangle2D.Double(
			pageX,pageY,pageWidth,bounds.getHeight());
		gfx.fill(headerBounds);

		gfx.setColor(headerTextColor);

		lm = font.getLineMetrics(headerText,frc);
		gfx.drawString(headerText,
			(float)(pageX + (pageWidth - bounds.getWidth()) / 2),
			(float)(pageY + lm.getAscent()));

		return headerBounds.getHeight();
	}
	//}}}

	//{{{ paintFooter() method
	private double paintFooter(Graphics2D gfx, double pageX, double pageY,
		double pageWidth, double pageHeight, int pageIndex)
	{
		String footerText = jEdit.getProperty("print.footerText",
			new Object[] { new Date(), new Integer(pageIndex + 1) });
		FontRenderContext frc = gfx.getFontRenderContext();

		gfx.setColor(footerColor);

		Rectangle2D bounds = font.getStringBounds(footerText,frc);
		Rectangle2D footerBounds = new Rectangle2D.Double(
			pageX,pageY + pageHeight - bounds.getHeight(),
			pageWidth,bounds.getHeight());
		gfx.fill(footerBounds);

		gfx.setColor(footerTextColor);

		lm = font.getLineMetrics(footerText,frc);
		gfx.drawString(footerText,
			(float)(pageX + (pageWidth - bounds.getWidth()) / 2),
			(float)(pageY + pageHeight - bounds.getHeight()
			+ lm.getAscent()));

		return footerBounds.getHeight();
	} //}}}

	//}}}

	//{{{ PrintTabExpander class
	static class PrintTabExpander implements TabExpander
	{
		private double pageX;
		private double tabWidth;

		//{{{ PrintTabExpander constructor
		public PrintTabExpander(double pageX, double tabWidth)
		{
			this.pageX = pageX;
			this.tabWidth = tabWidth;
		} //}}}

		//{{{ nextTabStop() method
		public float nextTabStop(float x, int tabOffset)
		{
			int ntabs = (int)((x - pageX) / tabWidth);
			return (float)((ntabs + 1) * tabWidth + pageX);
		} //}}}
	} //}}}
}