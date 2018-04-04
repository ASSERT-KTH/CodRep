image.getHeight(this) - fm.getDescent() - 6);

/*
 * SplashScreen.java - Splash screen
 * Copyright (C) 1998, 1999, 2000, 2001 Slava Pestov
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

import java.awt.*;
import org.gjt.sp.jedit.jEdit;
import org.gjt.sp.util.Log;

/**
 * The splash screen displayed on startup.<p>
 *
 * This file only uses AWT APIs so that it can be displayed as soon as possible
 * after jEdit is launched.
 */
public class SplashScreen extends Canvas
{
	public SplashScreen()
	{
		setCursor(Cursor.getPredefinedCursor(Cursor.WAIT_CURSOR));
		setBackground(Color.white);

		Font font = new Font("Dialog",Font.PLAIN,10);
		setFont(font);
		fm = getFontMetrics(font);

		image = getToolkit().getImage(
			getClass().getResource("/org/gjt/sp/jedit/icons/splash.png"));
		MediaTracker tracker = new MediaTracker(this);
		tracker.addImage(image,0);

		try
		{
			tracker.waitForAll();
		}
		catch(Exception e)
		{
			Log.log(Log.ERROR,this,e);
		}

		win = new Window(new Frame());

		Dimension screen = getToolkit().getScreenSize();
		Dimension size = new Dimension(image.getWidth(this) + 2,
			image.getHeight(this) + 2 + PROGRESS_HEIGHT);
		win.setSize(size);

		win.setLayout(new BorderLayout());
		win.add(BorderLayout.CENTER,this);

		win.setLocation((screen.width - size.width) / 2,
			(screen.height - size.height) / 2);
		win.validate();
		win.show();

		/*synchronized(this)
		{
			try
			{
				wait();
			}
			catch(InterruptedException ie)
			{
				Log.log(Log.ERROR,this,ie);
			}
		}*/
	}

	public void dispose()
	{
		win.dispose();
	}

	public synchronized void advance()
	{
		progress++;
		repaint();

		// wait for it to be painted to ensure progress is updated
		// continuously
		try
		{
			wait();
		}
		catch(InterruptedException ie)
		{
			Log.log(Log.ERROR,this,ie);
		}
	}

	public void update(Graphics g)
	{
		paint(g);
	}

	public synchronized void paint(Graphics g)
	{
		Dimension size = getSize();

		if(offscreenImg == null)
		{
			offscreenImg = createImage(size.width,size.height);
			offscreenGfx = offscreenImg.getGraphics();
			offscreenGfx.setFont(getFont());
		}

		offscreenGfx.setColor(Color.gray);
		offscreenGfx.drawRect(0,0,size.width - 1,size.height - 1);

		offscreenGfx.drawImage(image,1,1,this);

		// XXX: This should not be hardcoded
		offscreenGfx.setColor(new Color(168,173,189));
		offscreenGfx.fillRect(1,image.getHeight(this) + 1,
			((win.getWidth() - 2) * progress) / 5,PROGRESS_HEIGHT);

		offscreenGfx.setColor(Color.gray);

		String str = "Version " + jEdit.getVersion();

		offscreenGfx.drawString(str,
			(getWidth() - fm.stringWidth(str)) / 2,
			image.getHeight(this)+1 - fm.getDescent() - 10);

		g.drawImage(offscreenImg,0,0,this);

		notify();
	}

	// private members
	private FontMetrics fm;
	private Window win;
	private Image image;
	private Image offscreenImg;
	private Graphics offscreenGfx;
	private int progress;
	private static final int PROGRESS_HEIGHT = 20;
}