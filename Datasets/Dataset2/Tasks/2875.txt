private int sortType = EntryCompare.NAME;

/*
 * InstallPanel.java - For installing plugins
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
import java.text.NumberFormat;
import java.util.*;
import org.gjt.sp.jedit.gui.*;
import org.gjt.sp.jedit.io.VFSManager;
import org.gjt.sp.jedit.*;
import org.gjt.sp.util.Log;
//}}}

class InstallPanel extends JPanel
{
	//{{{ InstallPanel constructor
	InstallPanel(PluginManager window, boolean updates)
	{
		super(new BorderLayout(12,12));

		this.window = window;
		this.updates = updates;

		setBorder(new EmptyBorder(12,12,12,12));

		final JSplitPane split = new JSplitPane(
			JSplitPane.VERTICAL_SPLIT,true);

		/* Setup the table */
		table = new JTable(pluginModel = new PluginTableModel());
		table.setShowGrid(false);
		table.setIntercellSpacing(new Dimension(0,0));
		table.setRowHeight(table.getRowHeight() + 2);
		table.setPreferredScrollableViewportSize(new Dimension(500,200));
		table.setRequestFocusEnabled(false);
		table.getSelectionModel().setSelectionMode(ListSelectionModel.SINGLE_SELECTION);
		table.setDefaultRenderer(Object.class, new TextRenderer(
			(DefaultTableCellRenderer)table.getDefaultRenderer(Object.class)));

		TableColumn col1 = table.getColumnModel().getColumn(0);
		TableColumn col2 = table.getColumnModel().getColumn(1);
		TableColumn col3 = table.getColumnModel().getColumn(2);
		TableColumn col4 = table.getColumnModel().getColumn(3);
		TableColumn col5 = table.getColumnModel().getColumn(4);

		col1.setPreferredWidth(30);
		col1.setMinWidth(30);
		col1.setMaxWidth(30);
		col1.setResizable(false);

		col2.setPreferredWidth(180);
		col3.setPreferredWidth(130);
		col4.setPreferredWidth(70);
		col5.setPreferredWidth(70);

		JTableHeader header = table.getTableHeader();
		header.setReorderingAllowed(false);
		header.addMouseListener(new HeaderMouseHandler());

		JScrollPane scrollpane = new JScrollPane(table);
		scrollpane.getViewport().setBackground(table.getBackground());
		split.setTopComponent(scrollpane);

		/* Create description */
		JScrollPane infoPane = new JScrollPane(
			infoBox = new PluginInfoBox());
		infoPane.setPreferredSize(new Dimension(500,100));
		split.setBottomComponent(infoPane);

		SwingUtilities.invokeLater(new Runnable()
		{
			public void run()
			{
				split.setDividerLocation(0.75);
			}
		});

		add(BorderLayout.CENTER,split);

		/* Create buttons */
		Box buttons = new Box(BoxLayout.X_AXIS);

		buttons.add(new InstallButton());
		buttons.add(Box.createHorizontalStrut(12));
		buttons.add(new SelectallButton());
		buttons.add(Box.createGlue());
		buttons.add(new SizeLabel());

		add(BorderLayout.SOUTH,buttons);
	} //}}}

	//{{{ updateModel() method
	public void updateModel()
	{
		pluginModel.clear();
		infoBox.setText(jEdit.getProperty("plugin-manager.list-download"));

		VFSManager.runInAWTThread(new Runnable()
		{
			public void run()
			{
				infoBox.setText(null);
				pluginModel.update();
			}
		});
	} //}}}

	//{{{ Private members

	//{{{ Variables
	private JTable table;
	private PluginTableModel pluginModel;
	private PluginManager window;
	private PluginInfoBox infoBox;

	private boolean updates;
	//}}}

	//{{{ formatSize() method
	private String formatSize(int size)
	{
		NumberFormat df = NumberFormat.getInstance();
		df.setMaximumFractionDigits(1);
		df.setMinimumFractionDigits(0);
		String sizeText;
		if (size < 1048576)
			sizeText = size/1024 + "KB";
		else
			sizeText = df.format(size/1048576d) + "MB";
		return sizeText;
	} //}}}

	//}}}

	//{{{ Inner classes

	//{{{ PluginTableModel class
	class PluginTableModel extends AbstractTableModel
	{
		private ArrayList entries = new ArrayList();
		private int sortType = EntryCompare.CATEGORY;

		//{{{ getColumnClass() method
		public Class getColumnClass(int columnIndex)
		{
			switch (columnIndex)
			{
				case 0: return Boolean.class;
				case 1:
				case 2:
				case 3:
				case 4: return Object.class;
				default: throw new Error("Column out of range");
			}
		} //}}}

		//{{{ getColumnCount() method
		public int getColumnCount()
		{
			return 5;
		} //}}}

		//{{{ getColumnName() method
		public String getColumnName(int column)
		{
			switch (column)
			{
				case 0: return " ";
				case 1: return " "+jEdit.getProperty("install-plugins.info.name");
				case 2: return " "+jEdit.getProperty("install-plugins.info.category");
				case 3: return " "+jEdit.getProperty("install-plugins.info.version");
				case 4: return " "+jEdit.getProperty("install-plugins.info.size");
				default: throw new Error("Column out of range");
			}
		} //}}}

		//{{{ getRowCount() method
		public int getRowCount()
		{
			return entries.size();
		} //}}}

		//{{{ getValueAt() method
		public Object getValueAt(int rowIndex,int columnIndex)
		{
			Object obj = entries.get(rowIndex);
			if(obj instanceof String)
			{
				if(columnIndex == 1)
					return obj;
				else
					return null;
			}
			else
			{
				Entry entry = (Entry)obj;

				switch (columnIndex)
				{
					case 0:
						return new Boolean(
							entry.install);
					case 1:
						return entry.name;
					case 2:
						return entry.set;
					case 3:
						return entry.version;
					case 4:
						return formatSize(entry.size);
					default:
						throw new Error("Column out of range");
				}
			}
		} //}}}

		//{{{ isCellEditable() method
		public boolean isCellEditable(int rowIndex, int columnIndex)
		{
			return (columnIndex == 0);
		} //}}}

		//{{{ setSelectAll() method
		public void setSelectAll(boolean b)
		{
			if(isDownloadingList())
				return;

			int length = getRowCount();
			for (int i = 0; i < length; i++)
			{
				if (b)
					setValueAt(Boolean.TRUE,i,0);
				else
				{
					Entry entry = (Entry)entries.get(i);
					entry.parents = new LinkedList();
					entry.install = false;
				}
			}
			fireTableChanged(new TableModelEvent(this));
		} //}}}

		//{{{ setSortType() method
		public void setSortType(int type)
		{
			sortType = type;
			sort(type);
		} //}}}

		//{{{ setValueAt() method
		public void setValueAt(Object aValue, int row, int column)
		{
			if (column != 0) return;

			Object obj = entries.get(row);
			if(obj instanceof String)
				return;

			Entry entry = (Entry)obj;
			Vector deps = entry.plugin.getCompatibleBranch().deps;
			boolean value = ((Boolean)aValue).booleanValue();
			if (!value)
			{
				if (entry.parents.size() > 0)
				{
					String[] args = {
						entry.name,
						entry.getParentString()
					};
					int result = GUIUtilities.confirm(
						window,"plugin-manager.dependency",
						args,JOptionPane.OK_CANCEL_OPTION,
						JOptionPane.WARNING_MESSAGE);
					if (result != JOptionPane.OK_OPTION)
						return;
					Iterator parentsIter = entry.parents.iterator();
					while(parentsIter.hasNext())
					{
						((Entry)parentsIter.next()).install = false;
					}

					fireTableRowsUpdated(0,getRowCount() - 1);
				}
			}

			for (int i = 0; i < deps.size(); i++)
			{
				PluginList.Dependency dep = (PluginList.Dependency)deps.elementAt(i);
				if (dep.what.equals("plugin"))
				{
					for (int j = 0; j < entries.size(); j++)
					{
						Entry temp = (Entry)entries.get(j);
						if (temp.plugin == dep.plugin)
						{
							if (value)
							{
								temp.parents.add(entry);
								setValueAt(Boolean.TRUE,j,0);
							}
							else
								temp.parents.remove(entry);
						}
					}
				}
			}

			entry.install = Boolean.TRUE.equals(aValue);
			fireTableCellUpdated(row,column);
		} //}}}

		//{{{ sort() method
		public void sort(int type)
		{
			this.sortType = type;

			if(isDownloadingList())
				return;

			Collections.sort(entries,new EntryCompare(type));
			fireTableChanged(new TableModelEvent(this));
		}
		//}}}

		//{{{ isDownloadingList() method
		private boolean isDownloadingList()
		{
			return (entries.size() == 1 && entries.get(0) instanceof String);
		} //}}}

		//{{{ clear() method
		public void clear()
		{
			entries = new ArrayList();
			fireTableChanged(new TableModelEvent(this));
		} //}}}

		//{{{ update() method
		public void update()
		{
			PluginList pluginList = window.getPluginList();

			if (pluginList == null) return;

			entries = new ArrayList();

			for(int i = 0; i < pluginList.pluginSets.size(); i++)
			{
				PluginList.PluginSet set = (PluginList.PluginSet)
					pluginList.pluginSets.get(i);
				for(int j = 0; j < set.plugins.size(); j++)
				{
					PluginList.Plugin plugin = (PluginList.Plugin)
						pluginList.pluginHash.get(set.plugins.get(j));
					PluginList.Branch branch = plugin.getCompatibleBranch();
					String installedVersion =
						plugin.getInstalledVersion();
					if (updates)
					{
						if(branch != null
							&& branch.canSatisfyDependencies()
							&& installedVersion != null
							&& MiscUtilities.compareStrings(branch.version,
							installedVersion,false) > 0)
						{
							entries.add(new Entry(plugin,set.name));
						}
					}
					else
					{
						if(installedVersion == null && plugin.canBeInstalled())
							entries.add(new Entry(plugin,set.name));
					}
				}
			}

			sort(sortType);

			fireTableChanged(new TableModelEvent(this));
		} //}}}
	} //}}}

	//{{{ Entry class
	class Entry
	{
		String name, version, author, date, description, set;
		int size;
		boolean install;
		PluginList.Plugin plugin;
		LinkedList parents = new LinkedList();

		Entry(PluginList.Plugin plugin, String set)
		{
			PluginList.Branch branch = plugin.getCompatibleBranch();
			boolean downloadSource = jEdit.getBooleanProperty("plugin-manager.downloadSource");
			int size = (downloadSource) ? branch.downloadSourceSize : branch.downloadSize;

			this.name = plugin.name;
			this.author = plugin.author;
			this.version = branch.version;
			this.size = size;
			this.date = branch.date;
			this.description = plugin.description;
			this.set = set;
			this.install = false;
			this.plugin = plugin;
		}

		String getParentString()
		{
			StringBuffer buf = new StringBuffer();
			Iterator iter = parents.iterator();
			while(iter.hasNext())
			{
				buf.append(((Entry)iter.next()).name);
				if(iter.hasNext())
					buf.append('\n');
			}
			return buf.toString();
		}
	} //}}}

	//{{{ PluginInfoBox class
	class PluginInfoBox extends JTextArea implements ListSelectionListener
	{
		public PluginInfoBox()
		{
			setEditable(false);
			setLineWrap(true);
			setWrapStyleWord(true);
			table.getSelectionModel().addListSelectionListener(this);
		}


		public void valueChanged(ListSelectionEvent e)
		{
			String text = "";
			if (table.getSelectedRowCount() == 1)
			{
				Entry entry = (Entry)pluginModel.entries
					.get(table.getSelectedRow());
				text = jEdit.getProperty("install-plugins.info",
					new String[] {entry.author,entry.date,entry.description});
			}
			setText(text);
			setCaretPosition(0);
		}
	} //}}}

	//{{{ SizeLabel class
	class SizeLabel extends JLabel implements TableModelListener
	{
		private int size;

		public SizeLabel()
		{
			size = 0;
			setText(jEdit.getProperty("install-plugins.totalSize")+formatSize(size));
			pluginModel.addTableModelListener(this);
		}

		public void tableChanged(TableModelEvent e)
		{
			if (e.getType() == TableModelEvent.UPDATE)
			{
				if(pluginModel.isDownloadingList())
					return;

				size = 0;
				int length = pluginModel.getRowCount();
				for (int i = 0; i < length; i++)
				{
					Entry entry = (Entry)pluginModel
						.entries.get(i);
					if (entry.install)
						size += entry.size;
				}
				setText(jEdit.getProperty("install-plugins.totalSize")+formatSize(size));
			}
		}
	} //}}}

	//{{{ SelectallButton class
	class SelectallButton extends JCheckBox implements ActionListener, TableModelListener
	{
		public SelectallButton()
		{
			super(jEdit.getProperty("install-plugins.select-all"));
			addActionListener(this);
			pluginModel.addTableModelListener(this);
			setEnabled(false);
		}

		public void actionPerformed(ActionEvent evt)
		{
			pluginModel.setSelectAll(isSelected());
		}

		public void tableChanged(TableModelEvent e)
		{
			if(pluginModel.isDownloadingList())
				return;

			setEnabled(pluginModel.getRowCount() != 0);
			if (e.getType() == TableModelEvent.UPDATE)
			{
				int length = pluginModel.getRowCount();
				for (int i = 0; i < length; i++)
					if (!((Boolean)pluginModel.getValueAt(i,0)).booleanValue())
					{
						setSelected(false);
						return;
					}
				if (length > 0)
					setSelected(true);
			}
		}
	} //}}}

	//{{{ InstallButton class
	class InstallButton extends JButton implements ActionListener, TableModelListener
	{
		public InstallButton()
		{
			super(jEdit.getProperty("install-plugins.install"));
			pluginModel.addTableModelListener(this);
			addActionListener(this);
			setEnabled(false);
		}

		public void actionPerformed(ActionEvent evt)
		{
			if(pluginModel.isDownloadingList())
				return;

			boolean downloadSource = jEdit.getBooleanProperty(
				"plugin-manager.downloadSource");
			boolean installUser = jEdit.getBooleanProperty(
				"plugin-manager.installUser");
			Roster roster = new Roster();
			String installDirectory;
			if(installUser)
			{
				installDirectory = MiscUtilities.constructPath(
					jEdit.getSettingsDirectory(),"jars");
			}
			else
			{
				installDirectory = MiscUtilities.constructPath(
					jEdit.getJEditHome(),"jars");
			}

			int length = pluginModel.getRowCount();
			int instcount = 0;
			for (int i = 0; i < length; i++)
			{
				Entry entry = (Entry)pluginModel.entries.get(i);
				if (entry.install)
				{
					entry.plugin.install(roster,installDirectory,downloadSource);
					if (updates)
						entry.plugin.getCompatibleBranch().satisfyDependencies(
						roster,installDirectory,downloadSource);
					instcount++;
				}
			}

			if(roster.isEmpty())
				return;

			boolean cancel = false;
			if (updates && roster.getOperationCount() > instcount)
				if (GUIUtilities.confirm(window,
					"install-plugins.depend",
					null,
					JOptionPane.OK_CANCEL_OPTION,
					JOptionPane.WARNING_MESSAGE) == JOptionPane.CANCEL_OPTION)
					cancel = true;
			
			if (!cancel)
			{
				new PluginManagerProgress(window,roster);
	
				roster.performOperationsInAWTThread(window);
				pluginModel.update();
			}
		}

		public void tableChanged(TableModelEvent e)
		{
			if(pluginModel.isDownloadingList())
				return;

			if (e.getType() == TableModelEvent.UPDATE)
			{
				int length = pluginModel.getRowCount();
				for (int i = 0; i < length; i++)
					if (((Boolean)pluginModel.getValueAt(i,0)).booleanValue())
					{
						setEnabled(true);
						return;
					}
				setEnabled(false);
			}
		}
	} //}}}

	//{{{ EntryCompare class
	static class EntryCompare implements Comparator
	{
		public static final int NAME = 0;
		public static final int CATEGORY = 1;

		private int type;

		public EntryCompare(int type)
		{
			this.type = type;
		}

		public int compare(Object o1, Object o2)
		{
			InstallPanel.Entry e1 = (InstallPanel.Entry)o1;
			InstallPanel.Entry e2 = (InstallPanel.Entry)o2;

			if (type == NAME)
				return e1.name.compareToIgnoreCase(e2.name);
			else
			{
				int result;
				if ((result = e1.set.compareToIgnoreCase(e2.set)) == 0)
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
					pluginModel.sort(EntryCompare.NAME);
					break;
				case 2:
					pluginModel.sort(EntryCompare.CATEGORY);
					break;
				default:
			}
		}
	} //}}}

	//{{{ TextRenderer
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
			return tcr.getTableCellRendererComponent(table,value,isSelected,false,row,column);
		}
	} //}}}

	//}}}
}