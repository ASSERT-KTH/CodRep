class HelpSearchPanel extends JPanel

/*
 * HelpSearchPanel.java - Help search GUI
 * :tabSize=8:indentSize=8:noTabs=false:
 * :folding=explicit:collapseFolds=1:
 *
 * Copyright (C) 2002 Slava Pestov
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

package org.gjt.sp.jedit.help;

//{{{ Imports
import javax.swing.*;
import java.awt.event.*;
import java.awt.*;
import java.util.*;
import org.gjt.sp.jedit.gui.*;
import org.gjt.sp.jedit.io.VFSManager;
import org.gjt.sp.jedit.*;
import org.gjt.sp.util.Log;
//}}}

public class HelpSearchPanel extends JPanel
{
	//{{{ HelpSearchPanel constructor
	public HelpSearchPanel(HelpViewer helpViewer)
	{
		super(new BorderLayout(6,6));

		this.helpViewer = helpViewer;

		Box box = new Box(BoxLayout.X_AXIS);
		box.add(new JLabel(jEdit.getProperty("helpviewer.search.caption")));
		box.add(Box.createHorizontalStrut(6));
		box.add(searchField = new HistoryTextField("helpviewer.search"));
		searchField.addActionListener(new ActionHandler());

		add(BorderLayout.NORTH,box);

		results = new JList();
		results.addMouseListener(new MouseHandler());
		results.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);
		results.setCellRenderer(new ResultRenderer());
		add(BorderLayout.CENTER,new JScrollPane(results));
	} //}}}

	//{{{ Private members
	private HelpViewer helpViewer;
	private HistoryTextField searchField;
	private JList results;
	private HelpIndex index;

	private HelpIndex getHelpIndex()
	{
		if(index == null)
		{
			index = new HelpIndex();
			try
			{
				index.indexEditorHelp();
			}
			catch(Exception e)
			{
				index = null;
				Log.log(Log.ERROR,this,e);
				GUIUtilities.error(helpViewer,"helpviewer.search.error",
					new String[] { e.toString() });
			}
		}

		return index;
	} //}}}

	//{{{ ResultIcon class
	static class ResultIcon implements Icon
	{
		private static RenderingHints renderingHints;

		static
		{
			HashMap hints = new HashMap();

			hints.put(RenderingHints.KEY_RENDERING, RenderingHints.VALUE_RENDER_QUALITY);
			hints.put(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);

			renderingHints = new RenderingHints(hints);
		}

		private int rank;

		ResultIcon(int rank)
		{
			this.rank = rank;
		}

		public int getIconWidth()
		{
			return 40;
		}

		public int getIconHeight()
		{
			return 9;
		}

		public void paintIcon(Component c, Graphics g, int x, int y)
		{
			Graphics2D g2d = (Graphics2D)g.create();
			g2d.setRenderingHints(renderingHints);

			for(int i = 0; i < 4; i++)
			{
				if(rank > i)
					g2d.setColor(UIManager.getColor("Label.foreground"));
				else
					g2d.setColor(UIManager.getColor("Label.disabledForeground"));
				g2d.fillOval(x+i*10,y,9,9);
			}
		}
	} //}}}

	//{{{ ResultRenderer class
	class ResultRenderer extends DefaultListCellRenderer
	{
		public Component getListCellRendererComponent(
			JList list,
			Object value,
			int index,
			boolean isSelected,
			boolean cellHasFocus)
		{
			super.getListCellRendererComponent(list,null,index,
				isSelected,cellHasFocus);

			if(value instanceof String)
			{
				setIcon(null);
				setText((String)value);
			}
			else
			{
				Result result = (Result)value;
				setIcon(new ResultIcon(result.rank));
				setText(result.title);
			}

			return this;
		}
	} //}}}

	//{{{ Result class
	static class Result
	{
		String file;
		String title;
		int rank;

		Result(HelpIndex.HelpFile file, int count)
		{
			this.file = file.file;
			this.title = file.title;
			rank = count;
		}
	} //}}}

	//{{{ ResultCompare class
	static class ResultCompare implements Comparator
	{
		public int compare(Object o1, Object o2)
		{
			Result r1 = (Result)o1;
			Result r2 = (Result)o2;
			if(r1.rank == r2.rank)
				return r1.title.compareTo(r2.title);
			else
				return r2.rank - r1.rank;
		}
	} //}}}

	//{{{ ActionHandler class
	class ActionHandler implements ActionListener
	{
		public void actionPerformed(ActionEvent evt)
		{
			final HelpIndex index = getHelpIndex();
			if(index == null)
				return;

			results.setListData(new String[] { jEdit.getProperty(
				"helpviewer.searching") });

			final String text = searchField.getText();
			final Vector resultModel = new Vector();

			VFSManager.runInWorkThread(new Runnable()
			{
				public void run()
				{
					StringTokenizer st = new StringTokenizer(text,",.;:-? ");

					// we later use this to compute a relative ranking
					int maxRank = 0;

					while(st.hasMoreTokens())
					{
						String word = st.nextToken().toLowerCase();
						HelpIndex.Word lookup = index.lookupWord(word);
						if(lookup == null)
							continue;

						for(int i = 0; i < lookup.occurCount; i++)
						{
							HelpIndex.Word.Occurrence occur = lookup.occurrences[i];

							boolean ok = false;

							HelpIndex.HelpFile file = index.getFile(occur.file);
							for(int j = 0; j < resultModel.size(); j++)
							{
								Result result = (Result)resultModel.elementAt(j);
								if(result.file.equals(file.file))
								{
									result.rank += occur.count;
									result.rank += 20; // multiple files w/ word bonus
									maxRank = Math.max(result.rank,maxRank);
									ok = true;
									break;
								}
							}

							if(!ok)
							{
								maxRank = Math.max(occur.count,maxRank);
								resultModel.addElement(new Result(file,occur.count));
							}
						}
					}

					if(maxRank != 0)
					{
						// turn the rankings into relative rankings, from 1 to 4
						for(int i = 0; i < resultModel.size(); i++)
						{
							Result result = (Result)resultModel.elementAt(i);
							result.rank = (int)Math.ceil((double)result.rank * 4 / maxRank);
						}

						Collections.sort(resultModel,new ResultCompare());
					}
				}
			});

			VFSManager.runInAWTThread(new Runnable()
			{
				public void run()
				{
					if(resultModel.size() == 0)
					{
						results.setListData(new String[] {
							jEdit.getProperty(
							"helpviewer.no-results") });

						getToolkit().beep();
					}
					else
						results.setListData(resultModel);
				}
			});

		}
	} //}}}

	//{{{ MouseHandler class
	public class MouseHandler extends MouseAdapter
	{
		public void mouseReleased(MouseEvent evt)
		{
			int row = results.locationToIndex(evt.getPoint());
			if(row != -1)
			{
				Result result = (Result)results.getModel()
					.getElementAt(row);
				helpViewer.gotoURL(result.file,true);
			}
		}
	} //}}}
}