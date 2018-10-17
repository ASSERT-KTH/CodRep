"install",roster);

/*
 * PluginManager.java - Plugin manager window
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

package org.gjt.sp.jedit.pluginmgr;

import javax.swing.border.*;
import javax.swing.event.*;
import javax.swing.tree.*;
import javax.swing.*;
import java.awt.event.*;
import java.awt.*;
import java.io.File;
import java.util.*;
import org.gjt.sp.jedit.gui.*;
import org.gjt.sp.jedit.*;
import org.gjt.sp.util.Log;

public class PluginManager extends JDialog
{
	public PluginManager(Frame frame)
	{
		super(frame,jEdit.getProperty("plugin-manager.title"),true);

		JPanel content = new JPanel(new BorderLayout());
		content.setBorder(new EmptyBorder(12,12,12,12));
		setContentPane(content);

		JLabel caption = new JLabel(jEdit.getProperty(
			"plugin-manager.caption"));
		caption.setBorder(new EmptyBorder(0,0,6,0));
		content.add(BorderLayout.NORTH,caption);

		tree = new JTree();
		tree.setCellRenderer(new Renderer());
		tree.setRootVisible(false);
		tree.setVisibleRowCount(16);
		tree.addTreeSelectionListener(new TreeHandler());

		JPanel panel = new JPanel(new BorderLayout());

		panel.add(BorderLayout.CENTER,new JScrollPane(tree));

		JPanel panel2 = new JPanel(new BorderLayout());
		panel2.setBorder(new EmptyBorder(6,0,0,0));
		JPanel labelBox = new JPanel(new GridLayout(3,1,0,3));
		labelBox.setBorder(new EmptyBorder(0,0,0,12));
		labelBox.add(new JLabel(jEdit.getProperty("plugin-manager"
			+ ".info.name"),SwingConstants.RIGHT));
		labelBox.add(new JLabel(jEdit.getProperty("plugin-manager"
			+ ".info.author"),SwingConstants.RIGHT));
		labelBox.add(new JLabel(jEdit.getProperty("plugin-manager"
			+ ".info.version"),SwingConstants.RIGHT));
		panel2.add(BorderLayout.WEST,labelBox);

		JPanel valueBox = new JPanel(new GridLayout(3,1,0,3));
		valueBox.add(name = new JLabel());
		valueBox.add(author = new JLabel());
		valueBox.add(version = new JLabel());
		panel2.add(BorderLayout.CENTER,valueBox);

		panel.add(BorderLayout.SOUTH,panel2);
		content.add(BorderLayout.CENTER,panel);

		JPanel buttons = new JPanel();
		buttons.setLayout(new BoxLayout(buttons,BoxLayout.X_AXIS));
		buttons.setBorder(new EmptyBorder(12,0,0,0));

		buttons.add(Box.createGlue());
		remove = new JButton(jEdit.getProperty("plugin-manager"
			+ ".remove"));
		remove.addActionListener(new ActionHandler());
		buttons.add(remove);
		buttons.add(Box.createHorizontalStrut(6));
		update = new JButton(jEdit.getProperty("plugin-manager"
			+ ".update"));
		update.addActionListener(new ActionHandler());
		buttons.add(update);
		buttons.add(Box.createHorizontalStrut(6));
		install = new JButton(jEdit.getProperty("plugin-manager"
			+ ".install"));
		install.addActionListener(new ActionHandler());
		buttons.add(install);
		buttons.add(Box.createHorizontalStrut(6));
		close = new JButton(jEdit.getProperty("common.close"));
		close.addActionListener(new ActionHandler());
		buttons.add(close);
		buttons.add(Box.createGlue());

		content.add(BorderLayout.SOUTH,buttons);

		updateTree();

		setDefaultCloseOperation(DISPOSE_ON_CLOSE);

		pack();

		setLocationRelativeTo(frame);

		show();
	}

	// private members
	private JTree tree;
	private JLabel name;
	private JLabel author;
	private JLabel version;
	private JButton remove;
	private JButton update;
	private JButton install;
	private JButton close;

	private void updateTree()
	{
		DefaultMutableTreeNode treeRoot = new DefaultMutableTreeNode();
		DefaultTreeModel treeModel = new DefaultTreeModel(treeRoot);

		DefaultMutableTreeNode loadedTree = new DefaultMutableTreeNode(
			jEdit.getProperty("plugin-manager.loaded"),true);
		DefaultMutableTreeNode notLoadedTree = new DefaultMutableTreeNode(
			jEdit.getProperty("plugin-manager.not-loaded"),true);
		DefaultMutableTreeNode newTree = new DefaultMutableTreeNode(
			jEdit.getProperty("plugin-manager.new"),true);

		EditPlugin[] plugins = jEdit.getPlugins();
		for(int i = 0; i < plugins.length; i++)
		{
			EditPlugin plugin = plugins[i];
			String path = plugin.getJAR().getPath();
			if(!new File(path).exists())
			{
				// plugin was deleted
				continue;
			}

			if(plugin instanceof EditPlugin.Broken)
			{
				Entry entry = new Entry(path,plugin.getClassName(),true);
				notLoadedTree.add(new DefaultMutableTreeNode(entry));
			}
			else
			{
				Entry entry = new Entry(path,plugin.getClassName(),false);
				loadedTree.add(new DefaultMutableTreeNode(entry));
			}
		}

		if(notLoadedTree.getChildCount() != 0)
			treeRoot.add(notLoadedTree);

		if(loadedTree.getChildCount() != 0)
			treeRoot.add(loadedTree);

		String[] newPlugins = jEdit.getNotLoadedPluginJARs();
		for(int i = 0; i < newPlugins.length; i++)
		{
			Entry entry = new Entry(newPlugins[i],null,false);
			newTree.add(new DefaultMutableTreeNode(entry));
		}

		if(newTree.getChildCount() != 0)
			treeRoot.add(newTree);

		tree.setModel(treeModel);
		for(int i = 0; i < tree.getRowCount(); i++)
			tree.expandRow(i);

		remove.setEnabled(false);

		name.setText(null);
		author.setText(null);
		version.setText(null);
	}

	class Entry
	{
		String clazz;
		String name, version, author;
		Vector jars;
		boolean broken;

		Entry(String path, String clazz, boolean broken)
		{
			Entry.this.clazz = clazz;
			Entry.this.broken = broken;

			jars = new Vector();
			jars.addElement(path);

			if(clazz == null)
				Entry.this.name = path;
			else
			{
				Entry.this.name = jEdit.getProperty("plugin." + clazz + ".name");
				if(name == null)
					name = clazz;

				Entry.this.version = jEdit.getProperty("plugin." + clazz
					+ ".version");

				Entry.this.author = jEdit.getProperty("plugin." + clazz
					+ ".author");

				String jarsProp = jEdit.getProperty("plugin." + clazz
					+ ".jars");

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
	}

	class ActionHandler implements ActionListener
	{
		public void actionPerformed(ActionEvent evt)
		{
			Object source = evt.getSource();
			if(source == close)
				dispose();
			else if(source == remove)
			{
				TreePath[] selected = tree.getSelectionModel()
					.getSelectionPaths();

				StringBuffer buf = new StringBuffer();
				Roster roster = new Roster();
				for(int i = 0; i < selected.length; i++)
				{
					Object last = ((DefaultMutableTreeNode)
						selected[i].getLastPathComponent())
						.getUserObject();
					if(last instanceof Entry)
					{
						Entry entry = (Entry)last;
						for(int j = 0; j < entry.jars.size(); j++)
						{
							String jar = (String)entry.jars.elementAt(j);
							if(buf.length() != 0)
								buf.append('\n');
							buf.append(jar);
							roster.addOperation(new Roster.Remove(jar));
						}
					}
				}

				String[] args = { buf.toString() };
				if(GUIUtilities.confirm(PluginManager.this,
					"plugin-manager.remove-confirm",args,
					JOptionPane.YES_NO_OPTION,
					JOptionPane.QUESTION_MESSAGE)
					== JOptionPane.YES_OPTION)
				{
					new PluginManagerProgress(PluginManager.this,
						"remove",roster);
					updateTree();
				}
			}
			else if(source == update)
			{
				PluginList list = new PluginListDownloadProgress(PluginManager.this)
					.getPluginList();
				if(list == null)
					return;

				if(jEdit.getSettingsDirectory() == null)
				{
					GUIUtilities.error(PluginManager.this,
						"no-settings",null);
					return;
				}

				Vector plugins = new Vector();
				for(int i = 0; i < list.plugins.size(); i++)
				{
					PluginList.Plugin plugin = (PluginList.Plugin)list
						.plugins.elementAt(i);
					PluginList.Branch branch = plugin.getCompatibleBranch();

					if(branch != null
						&& plugin.installedVersion != null
						&& MiscUtilities.compareStrings(branch.version,
						plugin.installedVersion,false) > 0)
						plugins.addElement(plugin);
				}

				if(plugins.size() == 0)
				{
					GUIUtilities.message(PluginManager.this,
						"plugin-manager.up-to-date",null);
					return;
				}

				Roster roster = new Roster();
				new InstallPluginsDialog(PluginManager.this,
					plugins,InstallPluginsDialog.UPDATE)
					.installPlugins(roster);

				if(roster.isEmpty())
					return;

				new PluginManagerProgress(PluginManager.this,
					"update",roster);

				updateTree();
			}
			else if(source == install)
			{
				PluginList list = new PluginListDownloadProgress(PluginManager.this)
					.getPluginList();
				if(list == null)
					return;

				if(jEdit.getSettingsDirectory() == null
					&& jEdit.getJEditHome() == null)
				{
					GUIUtilities.error(PluginManager.this,"no-settings",null);
					return;
				}

				Vector plugins = new Vector();
				for(int i = 0; i < list.plugins.size(); i++)
				{
					PluginList.Plugin plugin = (PluginList.Plugin)list
						.plugins.elementAt(i);
					if(plugin.installed == null
						&& plugin.canBeInstalled())
						plugins.addElement(plugin);
				}

				Roster roster = new Roster();
				new InstallPluginsDialog(PluginManager.this,
					plugins,InstallPluginsDialog.INSTALL)
					.installPlugins(roster);

				if(roster.isEmpty())
					return;

				new PluginManagerProgress(PluginManager.this,
					"remove",roster);

				updateTree();
			}
		}
	}

	class TreeHandler implements TreeSelectionListener
	{
		public void valueChanged(TreeSelectionEvent evt)
		{
			TreePath selection = evt.getPath();
			DefaultMutableTreeNode node;
			if(selection == null)
			{
				node = null;
			}
			else
			{
				node = (DefaultMutableTreeNode)
					selection.getLastPathComponent();
			}

			name.setText(null);
			author.setText(null);
			version.setText(null);

			if(node != null && node.isLeaf()
				&& node.getUserObject() instanceof Entry)
			{
				remove.setEnabled(true);

				Entry entry = (Entry)node.getUserObject();

				if(entry.clazz != null)
				{
					name.setText(entry.name);
					author.setText(entry.author);
					version.setText(entry.version);
				}
			}
			else
				remove.setEnabled(false);
		}
	}

	class Renderer extends DefaultTreeCellRenderer
	{
		public Component getTreeCellRendererComponent(JTree tree,
			Object value, boolean selected, boolean expanded,
			boolean leaf, int row, boolean hasFocus)
		{
			super.getTreeCellRendererComponent(tree,value,
				selected,expanded,leaf,row,hasFocus);

			setIcon(null);

			return this;
		}
	}
}