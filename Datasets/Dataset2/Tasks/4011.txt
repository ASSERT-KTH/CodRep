int count = jEdit.getIntegerProperty("tip.count",0);

/*
 * TipOfTheDay.java - Tip of the day window
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

import javax.swing.border.EmptyBorder;
import javax.swing.*;
import java.awt.event.*;
import java.awt.*;
import java.io.IOException;
import java.net.URL;
import java.util.Random;
import org.gjt.sp.jedit.*;
import org.gjt.sp.util.Log;

public class TipOfTheDay extends EnhancedDialog
{
	public TipOfTheDay(View view)
	{
		super(view,jEdit.getProperty("tip.title"),false);
		setContentPane(new TipPanel());
		setDefaultCloseOperation(DISPOSE_ON_CLOSE);
		pack();
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

	class TipPanel extends JPanel
	{
		TipPanel()
		{
			super(new BorderLayout(12,12));
			setBorder(new EmptyBorder(12,12,12,12));

			JLabel label = new JLabel(jEdit.getProperty("tip.caption"));
			label.setFont(new Font("SansSerif",Font.PLAIN,24));
			label.setForeground(UIManager.getColor("Button.foreground"));
			TipPanel.this.add(BorderLayout.NORTH,label);

			tipText = new JEditorPane();
			tipText.setEditable(false);
			tipText.setContentType("text/html");

			nextTip();

			JScrollPane scroller = new JScrollPane(tipText);
			scroller.setPreferredSize(new Dimension(150,150));
			TipPanel.this.add(BorderLayout.CENTER,scroller);

			ActionHandler actionHandler = new ActionHandler();

			Box buttons = new Box(BoxLayout.X_AXIS);

			showNextTime = new JCheckBox(jEdit.getProperty("tip.show-next-time"),
				jEdit.getBooleanProperty("tip.show"));
			showNextTime.addActionListener(actionHandler);
			buttons.add(showNextTime);

			buttons.add(Box.createHorizontalStrut(6));
			buttons.add(Box.createGlue());

			nextTip = new JButton(jEdit.getProperty("tip.next-tip"));
			nextTip.addActionListener(actionHandler);
			buttons.add(nextTip);

			buttons.add(Box.createHorizontalStrut(6));

			close = new JButton(jEdit.getProperty("common.close"));
			close.addActionListener(actionHandler);
			buttons.add(close);
			TipOfTheDay.this.getRootPane().setDefaultButton(close);

			Dimension dim = nextTip.getPreferredSize();
			dim.width = Math.max(dim.width,close.getPreferredSize().width);
			nextTip.setPreferredSize(dim);
			close.setPreferredSize(dim);

			TipPanel.this.add(BorderLayout.SOUTH,buttons);
		}

		// private members
		private JCheckBox showNextTime;
		private JButton nextTip, close;
		private JEditorPane tipText;
		private int currentTip = -1;

		private void nextTip()
		{
			int count = Integer.parseInt(jEdit.getProperty("tip.count"));
			// so that we don't see the same tip again if the user
			// clicks 'Next Tip'
			int tipToShow = currentTip;
			while(tipToShow == currentTip)
				tipToShow = Math.abs(new Random().nextInt()) % count;
			try
			{
				tipText.setPage(TipOfTheDay.class.getResource(
					"/org/gjt/sp/jedit/tips/tip"
					+ tipToShow + ".html"));
			}
			catch(Exception e)
			{
				Log.log(Log.ERROR,this,e);
			}
		}

		class ActionHandler implements ActionListener
		{
			public void actionPerformed(ActionEvent evt)
			{
				Object source = evt.getSource();
				if(source == showNextTime)
				{
					jEdit.setBooleanProperty("tip.show",showNextTime
						.isSelected());
				}
				else if(source == nextTip)
					nextTip();
				else if(source == close)
					dispose();
			}
		}
	}
}