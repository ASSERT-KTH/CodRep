super(dialog,

/*
 * InstallPluginsDialog.java - Plugin install dialog box
 * :tabSize=8:indentSize=8:noTabs=false:
 * :folding=explicit:collapseFolds=1:
 *
 * Copyright (C) 2000, 2001, 2002 Slava Pestov
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
import javax.swing.*;
import java.awt.event.*;
import java.awt.*;
import java.util.ArrayList;
import java.util.Vector;
import org.gjt.sp.jedit.gui.*;
import org.gjt.sp.jedit.*;
import org.gjt.sp.util.Log;
//}}}

class InstallPluginsDialog extends EnhancedDialog
{
	static final int INSTALL = 0;
	static final int UPDATE = 1;

	//{{{ InstallPluginsDialog constructor
	InstallPluginsDialog(JDialog dialog, Vector model, int mode)
	{
		super(JOptionPane.getFrameForComponent(dialog),
			(mode == INSTALL
			? jEdit.getProperty("install-plugins.title")
			: jEdit.getProperty("update-plugins.title")),true);

		JPanel content = new JPanel(new BorderLayout(12,12));
		content.setBorder(new EmptyBorder(12,12,12,12));
		setContentPane(content);

		JLabel label = new JLabel(jEdit.getProperty("install-plugins.caption"));
		content.add(BorderLayout.NORTH,label);

		plugins = new JCheckBoxList(model);
		plugins.getSelectionModel().addListSelectionListener(new ListHandler());
		plugins.getModel().addTableModelListener(new TableModelHandler());
		JScrollPane scroller = new JScrollPane(plugins);
		scroller.setPreferredSize(new Dimension(200,0));
		content.add(BorderLayout.WEST,scroller);

		JPanel panel = new JPanel(new BorderLayout());
		panel.setBorder(new TitledBorder(jEdit.getProperty("install-plugins"
			+ ".plugin-info")));

		JPanel labelAndValueBox = new JPanel(new BorderLayout());

		JPanel labelBox = new JPanel(new GridLayout(
			(mode == UPDATE ? 7 : 6),1,0,3));
		labelBox.setBorder(new EmptyBorder(0,0,3,12));
		labelBox.add(new JLabel(jEdit.getProperty("install-plugins"
			+ ".info.name"),SwingConstants.RIGHT));
		labelBox.add(new JLabel(jEdit.getProperty("install-plugins"
			+ ".info.author"),SwingConstants.RIGHT));
		labelBox.add(new JLabel(jEdit.getProperty("install-plugins"
			+ ".info.size"),SwingConstants.RIGHT));
		labelBox.add(new JLabel(jEdit.getProperty("install-plugins"
			+ ".info.latest-version"),SwingConstants.RIGHT));
		if(mode == UPDATE)
		{
			labelBox.add(new JLabel(jEdit.getProperty("install-plugins"
				+ ".info.installed-version"),SwingConstants.RIGHT));
		}
		labelBox.add(new JLabel(jEdit.getProperty("install-plugins"
			+ ".info.updated"),SwingConstants.RIGHT));
		labelBox.add(new JLabel(jEdit.getProperty("install-plugins"
			+ ".info.description"),SwingConstants.RIGHT));
		labelAndValueBox.add(BorderLayout.WEST,labelBox);

		JPanel valueBox = new JPanel(new GridLayout(
			(mode == UPDATE ? 7 : 6),1,0,3));
		valueBox.setBorder(new EmptyBorder(0,0,3,0));
		valueBox.add(name = new JLabel());
		valueBox.add(author = new JLabel());
		valueBox.add(size = new JLabel());
		valueBox.add(latestVersion = new JLabel());
		if(mode == UPDATE)
			valueBox.add(installedVersion = new JLabel());
		valueBox.add(updated = new JLabel());
		valueBox.add(Box.createGlue());
		labelAndValueBox.add(BorderLayout.CENTER,valueBox);

		panel.add(BorderLayout.NORTH,labelAndValueBox);

		description = new JTextArea(6,50);
		description.setEditable(false);
		description.setLineWrap(true);
		description.setWrapStyleWord(true);

		panel.add(BorderLayout.CENTER,new JScrollPane(description));

		content.add(BorderLayout.CENTER,panel);

		panel = new JPanel(new BorderLayout(12,0));

		JPanel panel2 = new JPanel(new GridLayout((mode == INSTALL ? 4 : 2),1));

		Box totalSizeBox = new Box(BoxLayout.X_AXIS);
		totalSizeBox.add(new JLabel(jEdit.getProperty("install-plugins.totalSize")));
		totalSizeBox.add(Box.createHorizontalStrut(12));
		totalSizeBox.add(totalSize = new JLabel());
		panel2.add(totalSizeBox);

		panel2.add(downloadSource = new JCheckBox(
			jEdit.getProperty("install-plugins.downloadSource")));
		downloadSource.setSelected(jEdit.getBooleanProperty("install-plugins"
			+ ".downloadSource.value"));
		downloadSource.addActionListener(new ActionHandler());

		if(mode == INSTALL)
		{
			ButtonGroup grp = new ButtonGroup();
			installUser = new JRadioButton();
			String settings = jEdit.getSettingsDirectory();
			if(settings == null)
			{
				settings = jEdit.getProperty("install-plugins.none");
				installUser.setEnabled(false);
			}
			else
			{
				settings = MiscUtilities.constructPath(settings,"jars");
				installUser.setEnabled(true);
			}
			String[] args = { settings };
			installUser.setText(jEdit.getProperty("install-plugins.user",args));
			grp.add(installUser);
			panel2.add(installUser);

			installSystem = new JRadioButton();
			String jEditHome = jEdit.getJEditHome();
			if(jEditHome == null)
			{
				jEditHome = jEdit.getProperty("install-plugins.none");
				installSystem.setEnabled(false);
			}
			else
			{
				jEditHome = MiscUtilities.constructPath(jEditHome,"jars");
				installSystem.setEnabled(true);
			}
			args[0] = jEditHome;
			installSystem.setText(jEdit.getProperty("install-plugins.system",args));
			grp.add(installSystem);
			panel2.add(installSystem);

			if(installUser.isEnabled())
				installUser.setSelected(true);
			else
				installSystem.setSelected(true);
		}

		panel.add(BorderLayout.NORTH,panel2);

		Box box = new Box(BoxLayout.X_AXIS);

		box.add(Box.createGlue());
		selectAll = new JButton(jEdit.getProperty("install-plugins.select-all"));
		selectAll.addActionListener(new ActionHandler());
		box.add(selectAll);
		box.add(Box.createHorizontalStrut(6));

		install = new JButton(jEdit.getProperty("install-plugins.install"));
		install.setEnabled(false);
		getRootPane().setDefaultButton(install);
		install.addActionListener(new ActionHandler());
		box.add(install);
		box.add(Box.createHorizontalStrut(6));

		cancel = new JButton(jEdit.getProperty("common.cancel"));
		cancel.addActionListener(new ActionHandler());
		box.add(cancel);
		box.add(Box.createHorizontalStrut(6));
		box.add(Box.createGlue());

		panel.add(BorderLayout.SOUTH,box);

		content.add(BorderLayout.SOUTH,panel);

		updateTotalSize();

		pack();
		setLocationRelativeTo(dialog);
		show();
	} //}}}

	//{{{ ok() method
	public void ok()
	{
		jEdit.setBooleanProperty("install-plugins.downloadSource.value",
			downloadSource.isSelected());
		dispose();
	} //}}}

	//{{{ cancel() method
	public void cancel()
	{
		cancelled = true;

		dispose();
	} //}}}

	//{{{ installPlugins() method
	void installPlugins(Roster roster)
	{
		if(cancelled)
			return;

		String installDirectory;
		if(installUser == null || installUser.isSelected())
		{
			installDirectory = MiscUtilities.constructPath(
				jEdit.getSettingsDirectory(),"jars");
		}
		else
		{
			installDirectory = MiscUtilities.constructPath(
				jEdit.getJEditHome(),"jars");
		}

		Object[] selected = plugins.getCheckedValues();
		for(int i = 0; i < selected.length; i++)
		{
			PluginList.Plugin plugin = (PluginList.Plugin)selected[i];
			plugin.install(roster,installDirectory,downloadSource.isSelected());
		}
	} //}}}

	//{{{ Private members

	//{{{ Instance variables
	private JCheckBoxList plugins;
	private JLabel name;
	private JLabel author;
	private JLabel size;
	private JLabel latestVersion;
	private JLabel installedVersion;
	private JLabel updated;
	private JTextArea description;
	private JLabel totalSize;
	private JCheckBox downloadSource;
	private JRadioButton installUser;
	private JRadioButton installSystem;

	private JButton selectAll;
	private JButton install;
	private JButton cancel;

	private boolean cancelled;
	private Thread thread;
	//}}}

	//{{{ updateInfo() method
	private void updateInfo()
	{
		Object selected = plugins.getSelectedValue();
		if(selected instanceof PluginList.Plugin)
		{
			PluginList.Plugin plugin = (PluginList.Plugin)selected;
			PluginList.Branch branch = plugin.getCompatibleBranch();
			name.setText(plugin.name);
			author.setText(plugin.author);
			size.setText(String.valueOf(
				(downloadSource.isSelected()
				? branch.downloadSourceSize
				: branch.downloadSize) / 1024) + " Kb");
			if(branch.obsolete)
				latestVersion.setText(jEdit.getProperty(
					"install-plugins.info.obsolete"));
			else
				latestVersion.setText(branch.version);
			if(installedVersion != null)
				installedVersion.setText(plugin.installedVersion);
			updated.setText(branch.date);

			ArrayList deps = new ArrayList();
			createDependencyList(branch.deps,deps);
			StringBuffer buf = new StringBuffer();
			for(int i = 0; i < deps.size(); i++)
			{
				buf.append("\n- ");
				buf.append(deps.get(i));
			}

			description.setText(plugin.description
				+ (buf.length() == 0 ? ""
				: jEdit.getProperty("install-plugins.info"
				+ ".also-install") + buf.toString()
				+ (branch.obsolete ? jEdit.getProperty(
				"install-plugins.info.obsolete-text") : "")));
			description.setCaretPosition(0);
		}
		else
		{
			name.setText(null);
			author.setText(null);
			latestVersion.setText(null);
			if(installedVersion != null)
				installedVersion.setText(null);
			updated.setText(null);
			description.setText(null);
		}
	} //}}}

	//{{{ createDependencyList() method
	private void createDependencyList(Vector deps, ArrayList append)
	{
		for(int i = 0; i < deps.size(); i++)
		{
			PluginList.Dependency dep = (PluginList.Dependency)
				deps.elementAt(i);
			if(dep.what.equals("plugin")
				&& !dep.isSatisfied())
			{
				if(!append.contains(dep.plugin))
				{
					append.add(dep.plugin);

					PluginList.Branch branch = dep.plugin
						.getCompatibleBranch();
					createDependencyList(branch.deps,append);
				}
			}
		}
	} //}}}

	//{{{ updateTotalSize() method
	private void updateTotalSize()
	{
		ArrayList selectedPlugins = new ArrayList();

		Object[] selected = plugins.getCheckedValues();
		install.setEnabled(selected.length != 0);

		for(int i = 0; i < selected.length; i++)
		{
			PluginList.Plugin plugin = (PluginList.Plugin)selected[i];
			if(!selectedPlugins.contains(plugin))
				selectedPlugins.add(plugin);

			createDependencyList(plugin.getCompatibleBranch().deps,
				selectedPlugins);
		}

		int _totalSize = 0;
		for(int i = 0; i < selectedPlugins.size(); i++)
		{
			PluginList.Branch branch = ((PluginList.Plugin)
				selectedPlugins.get(i)).getCompatibleBranch();
			_totalSize += (downloadSource.isSelected()
				? branch.downloadSourceSize
				: branch.downloadSize);
		}

		totalSize.setText(String.valueOf(_totalSize / 1024) + " Kb");
	} //}}}

	//}}}

	//{{{ ActionHandler class
	class ActionHandler implements ActionListener
	{
		public void actionPerformed(ActionEvent evt)
		{
			Object source = evt.getSource();
			if(source == selectAll)
				plugins.selectAll();
			if(source == install)
				ok();
			else if(source == cancel)
				cancel();
			else if(source == downloadSource)
			{
				updateInfo();
				updateTotalSize();
			}
		}
	} //}}}

	//{{{ ListHandler class
	class ListHandler implements ListSelectionListener
	{
		public void valueChanged(ListSelectionEvent evt)
		{
			updateInfo();
		}
	} //}}}

	//{{{ TableModelHandler class
	class TableModelHandler implements TableModelListener
	{
		public void tableChanged(TableModelEvent e)
		{
			updateTotalSize();
		}
	} //}}}
}