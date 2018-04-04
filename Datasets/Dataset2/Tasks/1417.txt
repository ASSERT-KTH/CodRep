tcr.setForeground(UIManager.getColor("Table.foreground"));

/*
 * ManagePanel.java - Manages plugins
 * :tabSize=8:indentSize=8:noTabs=false:
 * :folding=explicit:collapseFolds=1:
 *
 * Copyright (C) 2002 Kris Kopicki
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

package org.gjt.sp.jedit.pluginmgr;

//{{{ Imports
import javax.swing.border.*;
import javax.swing.event.*;
import javax.swing.table.*;
import javax.swing.*;
import java.awt.event.*;
import java.awt.*;
import java.io.File;
import java.net.URL;
import java.util.*;
import org.gjt.sp.jedit.gui.*;
import org.gjt.sp.jedit.help.*;
import org.gjt.sp.jedit.*;
import org.gjt.sp.util.Log;
//}}}

public class ManagePanel extends JPanel
{
	//{{{ ManagePanel constructor
	public ManagePanel(PluginManager window)
	{
		super(new BorderLayout(12,12));

		this.window = window;

		setBorder(new EmptyBorder(12,12,12,12));

		/* Create the plugin table */
		table = new JTable(pluginModel = new PluginTableModel());
		table.setShowGrid(false);
		table.setIntercellSpacing(new Dimension(0,0));
		table.setRowHeight(table.getRowHeight() + 2);
		table.setPreferredScrollableViewportSize(new Dimension(500,300));
		table.setRequestFocusEnabled(false);
		table.setDefaultRenderer(Object.class, new TextRenderer(
			(DefaultTableCellRenderer)table.getDefaultRenderer(Object.class)));

		TableColumn col1 = table.getColumnModel().getColumn(0);
		TableColumn col2 = table.getColumnModel().getColumn(1);
		TableColumn col3 = table.getColumnModel().getColumn(2);
		TableColumn col4 = table.getColumnModel().getColumn(3);

		col1.setPreferredWidth(50);
		col2.setPreferredWidth(300);
		col3.setPreferredWidth(100);
		col4.setPreferredWidth(100);

		JTableHeader header = table.getTableHeader();
		header.setReorderingAllowed(false);
		header.addMouseListener(new HeaderMouseHandler());

		JScrollPane scrollpane = new JScrollPane(table);
		scrollpane.getViewport().setBackground(table.getBackground());
		add(BorderLayout.CENTER,scrollpane);

		/* Create button panel */
		Box buttons = new Box(BoxLayout.X_AXIS);

		buttons.add(new RemoveButton());
		buttons.add(Box.createGlue());
		buttons.add(new HelpButton());

		add(BorderLayout.SOUTH,buttons);
	} //}}}

	//{{{ update() method
	public void update()
	{
		pluginModel.update();
	} //}}}

	//{{{ Private members

	//{{{ Variables
	private JTable table;
	private PluginTableModel pluginModel;
	private JButton remove;
	private JButton help;
	private PluginManager window;
	//}}}

	//{{{ Inner classes

	//{{{ Entry class
	class Entry
	{
		static final String ERROR = "error";
		static final String LOADED = "loaded";
		static final String NOT_LOADED = "not-loaded";

		String clazz;
		String name, version, author, status, docs;
		Vector jars;
		String path;
		boolean broken;

		Entry(String path, String clazz, boolean broken)
		{
			Entry.this.clazz = clazz;
			Entry.this.broken = broken;

			this.path = path;

			jars = new Vector();
			jars.addElement(path);

			if(clazz == null)
			{
				this.name = new File(path).getName();
				this.status = NOT_LOADED;
			}
			else
			{
				Entry.this.name = jEdit.getProperty("plugin."+clazz+".name");
				if(name == null)
					name = clazz;

				Entry.this.version = jEdit.getProperty("plugin."+clazz+".version");

				Entry.this.author = jEdit.getProperty("plugin."+clazz+".author");

				if (broken)
					this.status = ERROR;
				else
					this.status = LOADED;

				this.docs = jEdit.getProperty("plugin."+clazz+".docs");

				String jarsProp = jEdit.getProperty("plugin."+clazz+".jars");

				if(jarsProp != null)
				{
					String directory = MiscUtilities.getParentOfPath(path);

					StringTokenizer st = new StringTokenizer(jarsProp);
					while(st.hasMoreElements())
					{
						jars.addElement(MiscUtilities.constructPath(
							directory,st.nextToken()));
					}
				}
			}
		}

		public String toString()
		{
			return Entry.this.name;
		}
	} //}}}

	//{{{ PluginTableModel class
	class PluginTableModel extends AbstractTableModel
	{
		private ArrayList entries;
		private int sortType = EntryCompare.NAME;

		//{{{ Constructor
		public PluginTableModel()
		{
			update();
		} //}}}

		//{{{ getColumnCount() method
		public int getColumnCount()
		{
			return 4;
		} //}}}

		//{{{ getColumnClass() method
		public Class getColumnClass(int columnIndex)
		{
			switch (columnIndex)
			{
				case 0: return Boolean.class;
				case 1:
				case 2:
				case 3: return Object.class;
				default: throw new Error("Column out of range");
			}
		} //}}}

		//{{{ getColumnName() method
		public String getColumnName(int column)
		{
			switch (column)
			{
				case 0:
					return jEdit.getProperty("manage-plugins.info.enabled");
				case 1:
					return jEdit.getProperty("manage-plugins.info.name");
				case 2:
					return jEdit.getProperty("manage-plugins.info.version");
				case 3:
					return jEdit.getProperty("manage-plugins.info.status");
				default:
					throw new Error("Column out of range");
			}
		} //}}}

		//{{{ getEntry() method
		public Entry getEntry(int rowIndex)
		{
			return (Entry)entries.get(rowIndex);
		} //}}}

		//{{{ getRowCount() method
		public int getRowCount()
		{
			return entries.size();
		} //}}}

		//{{{ getValueAt() method
		public Object getValueAt(int rowIndex,int columnIndex)
		{
			Entry entry = (Entry)entries.get(rowIndex);
			switch (columnIndex)
			{
				case 0:
					return new Boolean(
						!entry.status.equals(
						Entry.NOT_LOADED));
				case 1:
					return entry.name;
				case 2:
					return entry.version;
				case 3:
					return jEdit.getProperty("plugin-manager.status."
						+ entry.status);
				default:
					throw new Error("Column out of range");
			}
		} //}}}

		//{{{ isCellEditable() method
		public boolean isCellEditable(int rowIndex, int columnIndex)
		{
			return columnIndex == 0;
		} //}}}

		//{{{ setValueAt() method
		public void setValueAt(Object value, int rowIndex,
			int columnIndex)
		{
			Entry entry = (Entry)entries.get(rowIndex);
			if(columnIndex == 0)
			{
				PluginJAR jar = jEdit.getPluginJAR(entry.path);
				if(jar == null)
				{
					if(!value.equals(Boolean.TRUE))
						return;

					jEdit.addPluginJAR(entry.path);
					jar = jEdit.getPluginJAR(entry.path);
					if(jar != null)
					{
						jar.checkDependencies();
						jar.activatePluginIfNecessary();
					}
				}
				else
				{
					if(!value.equals(Boolean.FALSE))
						return;

					unloadPluginJAR(jar);
				}
			}

			update();
		} //}}}

		//{{{ setSortType() method
		public void setSortType(int type)
		{
			sortType = type;
			sort(type);
		} //}}}

		//{{{ sort() method
		public void sort(int type)
		{
			Collections.sort(entries,new EntryCompare(type));
			fireTableChanged(new TableModelEvent(this));
		}
		//}}}

		//{{{ update() method
		public void update()
		{
			EditPlugin[] plugins = jEdit.getPlugins();
			entries = new ArrayList();
			for(int i = 0; i < plugins.length; i++)
			{
				EditPlugin plugin = plugins[i];
				String path = plugin.getPluginJAR().getPath();
				if(!new File(path).exists())
				{
					continue;
				}

				if(plugin instanceof EditPlugin.Broken)
					entries.add(new Entry(path,plugin.getClassName(),true));
				else
					entries.add(new Entry(path,plugin.getClassName(),false));
			}

			String[] newPlugins = jEdit.getNotLoadedPluginJARs();
			for(int i = 0; i < newPlugins.length; i++)
			{
				entries.add(new Entry(newPlugins[i],null,true));
			}

			sort(sortType);

			fireTableChanged(new TableModelEvent(this));
		} //}}}

		//{{{ unloadPluginJAR() method
		/**
		 * This should go into a public method somewhere.
		 */
		private void unloadPluginJAR(PluginJAR jar)
		{
			String[] dependents = jar.getDependentPlugins();
			for(int i = 0; i < dependents.length; i++)
			{
				PluginJAR _jar = jEdit.getPluginJAR(
					dependents[i]);
				if(_jar != null)
				{
					unloadPluginJAR(_jar);
				}
			}

			jEdit.removePluginJAR(jar,false);
		} //}}}
	} //}}}

	//{{{ TextRenderer class
	class TextRenderer extends DefaultTableCellRenderer
	{
		private DefaultTableCellRenderer tcr;

		public TextRenderer(DefaultTableCellRenderer tcr)
		{
			this.tcr = tcr;
		}

		public Component getTableCellRendererComponent(JTable table, Object value,
			boolean isSelected, boolean hasFocus, int row, int column)
		{
			Entry entry = pluginModel.getEntry(row);
			if (entry.status.equals(Entry.ERROR))
				tcr.setForeground(Color.red);
			else
				tcr.setForeground(Color.black);
			return tcr.getTableCellRendererComponent(table,value,isSelected,false,row,column);
		}
	} //}}}

	//{{{ RemoveButton class
	class RemoveButton extends JButton implements ListSelectionListener, ActionListener
	{
		public RemoveButton()
		{
			super(jEdit.getProperty("manage-plugins.remove"));
			table.getSelectionModel().addListSelectionListener(this);
			addActionListener(this);
			setEnabled(false);
		}

		public void actionPerformed(ActionEvent evt)
		{
			int[] selected = table.getSelectedRows();

			StringBuffer buf = new StringBuffer();
			Roster roster = new Roster();
			for(int i = 0; i < selected.length; i++)
			{
				Entry entry = pluginModel.getEntry(selected[i]);
				for(int j = 0; j < entry.jars.size(); j++)
				{
					String jar = (String)entry.jars.elementAt(j);
					if(buf.length() != 0)
						buf.append('\n');
					buf.append(jar);
					roster.addRemove(jar);
				}
			}

			String[] args = { buf.toString() };
			if(GUIUtilities.confirm(window,
				"plugin-manager.remove-confirm",args,
				JOptionPane.YES_NO_OPTION,
				JOptionPane.QUESTION_MESSAGE)
				== JOptionPane.YES_OPTION)
			{
				roster.performOperationsInAWTThread(window);
				pluginModel.update();
			}
		}

		public void valueChanged(ListSelectionEvent e)
		{
			if (table.getSelectedRowCount() == 0)
				setEnabled(false);
			else
				setEnabled(true);
		}
	} //}}}

	//{{{ HelpButton class
	class HelpButton extends JButton implements ListSelectionListener, ActionListener
	{
		private URL docURL;

		public HelpButton()
		{
			super(jEdit.getProperty("manage-plugins.help"));
			table.getSelectionModel().addListSelectionListener(this);
			addActionListener(this);
			setEnabled(false);
		}

		public void actionPerformed(ActionEvent evt)
		{
			new HelpViewer(docURL);
		}

		public void valueChanged(ListSelectionEvent e)
		{
			if (table.getSelectedRowCount() == 1)
			{
				try {
					Entry entry = pluginModel.getEntry(table.getSelectedRow());
					String label = entry.clazz;
					String docs = entry.docs;
					PluginJAR jar = jEdit.getPlugin(label)
						.getPluginJAR();
					if(jar != null && label != null && docs != null)
					{
						URL url = jar.getClassLoader()
							.getResource(docs);
						if(url != null)
						{
							docURL = url;
							setEnabled(true);
							return;
						}
					}
				} catch (Exception ex) {}
			}
			setEnabled(false);
		}
	} //}}}

	//{{{ EntryCompare class
	static class EntryCompare implements Comparator
	{
		public static final int NAME = 0;
		public static final int STATUS = 2;

		private int type;

		public EntryCompare(int type)
		{
			this.type = type;
		}

		public int compare(Object o1, Object o2)
		{
			Entry e1 = (Entry)o1;
			Entry e2 = (Entry)o2;

			if (type == NAME)
				return e1.name.compareToIgnoreCase(e2.name);
			else
			{
				int result;
				if ((result = e1.status.compareToIgnoreCase(e2.status)) == 0)
					return e1.name.compareToIgnoreCase(e2.name);
				return result;
			}
		}
	} //}}}

	//{{{ HeaderMouseHandler class
	class HeaderMouseHandler extends MouseAdapter
	{
		public void mouseClicked(MouseEvent evt)
		{
			switch(table.getTableHeader().columnAtPoint(evt.getPoint()))
			{
				case 1:
					pluginModel.setSortType(EntryCompare.NAME);
					break;
				case 2:
					pluginModel.setSortType(EntryCompare.STATUS);
					break;
				default:
			}
		}
	} //}}}

	//}}}
}