offscreenGfx.setColor(new Color(225,225,239));

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
import java.net.URL;
import org.gjt.sp.jedit.jEdit;
import org.gjt.sp.util.Log;

/**
 * This file only uses AWT APIs so that it is displayed faster on startup.
 */
public class SplashScreen extends Canvas
{
	public SplashScreen()
	{
		setCursor(Cursor.getPredefinedCursor(Cursor.WAIT_CURSOR));

		image = getToolkit().getImage(
			getClass().getResource("/org/gjt/sp/jedit/icons/splash.gif"));
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
			image.getHeight(this) + 2);
		win.setSize(size);

		win.setLayout(new BorderLayout());
		win.add(BorderLayout.CENTER,this);

		win.setLocation((screen.width - size.width) / 2,
			(screen.height - size.height) / 2);
		win.validate();
		win.show();

		synchronized(this)
		{
			try
			{
				wait();
			}
			catch(InterruptedException ie)
			{
				Log.log(Log.ERROR,this,ie);
			}
		}
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
		}

		offscreenGfx.setColor(Color.black);
		offscreenGfx.drawRect(0,0,size.width - 1,size.height - 1);

		offscreenGfx.drawImage(image,1,1,this);

		// XXX: This should not be hardcoded
		offscreenGfx.setColor(new Color(87,87,114));
		offscreenGfx.fillRect(8,198,(436 * progress) / 7,16);

		g.drawImage(offscreenImg,0,0,this);

		notify();
	}

	// private members
	private Window win;
	private Image image;
	private Image offscreenImg;
	private Graphics offscreenGfx;
	private int progress;
}