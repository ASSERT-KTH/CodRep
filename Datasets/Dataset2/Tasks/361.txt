Thread.sleep(Math.max(0,25 -

/*
 * AboutDialog.java - About jEdit dialog box
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

import javax.swing.border.*;
import javax.swing.*;
import java.awt.event.*;
import java.awt.*;
import java.util.*;
import org.gjt.sp.jedit.*;

public class AboutDialog extends EnhancedDialog
{
	public AboutDialog(View view)
	{
		super(view,jEdit.getProperty("about.title"),true);

		JPanel content = new JPanel(new BorderLayout());
		content.setBorder(new EmptyBorder(12,12,12,12));
		setContentPane(content);

		content.add(BorderLayout.CENTER,new AboutPanel());

		JPanel buttonPanel = new JPanel();
		buttonPanel.setLayout(new BoxLayout(buttonPanel,BoxLayout.X_AXIS));
		buttonPanel.setBorder(new EmptyBorder(12,0,0,0));

		buttonPanel.add(Box.createGlue());
		close = new JButton(jEdit.getProperty("common.close"));
		close.addActionListener(new ActionHandler());
		getRootPane().setDefaultButton(close);
		buttonPanel.add(close);
		buttonPanel.add(Box.createGlue());
		content.add(BorderLayout.SOUTH,buttonPanel);

		pack();
		setResizable(false);
		setLocationRelativeTo(view);
		show();
	}

	public void ok()
	{
		dispose();
	}

	public void cancel()
	{
		dispose();
	}

	// private members
	private JButton close;

	class ActionHandler implements ActionListener
	{
		public void actionPerformed(ActionEvent evt)
		{
			dispose();
		}
	}

	static class AboutPanel extends JComponent
	{
		ImageIcon image;
		Vector text;
		int scrollPosition;
		AnimationThread thread;

		AboutPanel()
		{
			setFont(UIManager.getFont("Label.font"));
			setForeground(new Color(206,206,229));
			image = new ImageIcon(getClass().getResource(
				"/org/gjt/sp/jedit/icons/about.gif"));
			setBorder(new MatteBorder(1,1,1,1,Color.black));

			text = new Vector(50);
			StringTokenizer st = new StringTokenizer(
				jEdit.getProperty("about.text"),"\n");
			while(st.hasMoreTokens())
			{
				text.addElement(st.nextToken());
			}

			scrollPosition = -300;

			thread = new AnimationThread();
		}

		public void paintComponent(Graphics _g)
		{
			Graphics2D g = (Graphics2D)_g;

			image.paintIcon(this,g,1,1);

			FontMetrics fm = g.getFontMetrics();
			int height = fm.getHeight();
			int firstLine = scrollPosition / height;

			int firstLineOffset = height - scrollPosition % height;
			int lastLine = (scrollPosition + 320) / height - 3;

			int y = 50 + firstLineOffset;

			for(int i = firstLine; i <= lastLine; i++)
			{
				if(i >= 0 && i < text.size())
				{
					String line = (String)text.elementAt(i);
					g.drawString(line,130 + (340
						- fm.stringWidth(line)) / 2,y);
				}
				y += fm.getHeight();
			}

			String[] args = { jEdit.getVersion() };
			String version = jEdit.getProperty("about.version",args);
			g.drawString(version,130 + (340 - fm.stringWidth(version)) / 2,
				370);
		}

		public Dimension getPreferredSize()
		{
			return new Dimension(1 + image.getIconWidth(),
				1 + image.getIconHeight());
		}

		public void addNotify()
		{
			super.addNotify();
			thread.start();
		}

		public void removeNotify()
		{
			super.removeNotify();
			thread.stop();
		}

		class AnimationThread extends Thread
		{
			AnimationThread()
			{
				super("About box animation thread");
				setPriority(Thread.MIN_PRIORITY);
			}

			public void run()
			{
				for(;;)
				{
					long start = System.currentTimeMillis();

					scrollPosition++;

					FontMetrics fm = getFontMetrics(getFont());
					int max = text.size() * fm.getHeight();
					if(scrollPosition > max)
						scrollPosition = -300;

					try
					{
						Thread.sleep(Math.max(0,50 -
							(System.currentTimeMillis() - start)));
					}
					catch(InterruptedException ie)
					{
					}

					repaint();
				}
			}
		}
	}
}