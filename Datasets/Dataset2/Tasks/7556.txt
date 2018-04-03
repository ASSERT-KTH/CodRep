public static class NoPluginsPane extends AbstractOptionPane

/*
 * PluginOptions.java - Plugin options dialog
 * :tabSize=8:indentSize=8:noTabs=false:
 * :folding=explicit:collapseFolds=1:
 *
 * Copyright (C) 2003 Slava Pestov
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

package org.gjt.sp.jedit.options;

//{{{ Imports
import java.awt.Dialog;
import java.awt.Frame;
import org.gjt.sp.jedit.gui.OptionsDialog;
import org.gjt.sp.jedit.options.*;
import org.gjt.sp.jedit.*;
import org.gjt.sp.util.Log;
//}}}

public class PluginOptions extends OptionsDialog
{
	//{{{ PluginOptions constructor
	public PluginOptions(Frame frame)
	{
		super(frame,"plugin-options",jEdit.getProperty("plugin-options.last"));
	} //}}}

	//{{{ PluginOptions constructor
	public PluginOptions(Frame frame, String pane)
	{
		super(frame,"plugin-options",pane);
	} //}}}

	//{{{ PluginOptions constructor
	public PluginOptions(Dialog dialog)
	{
		super(dialog,"plugin-options",jEdit.getProperty("plugin-options.last"));
	} //}}}

	//{{{ PluginOptions constructor
	public PluginOptions(Dialog dialog, String pane)
	{
		super(dialog,"plugin-options",pane);
	} //}}}

	//{{{ createOptionTreeModel() method
	protected OptionTreeModel createOptionTreeModel()
	{
		OptionTreeModel paneTreeModel = new OptionTreeModel();
		OptionGroup rootGroup = (OptionGroup) paneTreeModel.getRoot();

		// initialize the Plugins branch of the options tree
		pluginsGroup = new OptionGroup("plugins");
		pluginsGroup.setSort(true);

		// Query plugins for option panes
		EditPlugin[] plugins = jEdit.getPlugins();
		for(int i = 0; i < plugins.length; i++)
		{
			EditPlugin ep = plugins[i];
			if(ep instanceof EditPlugin.Broken)
				continue;

			String className = ep.getClassName();
			if(jEdit.getProperty("plugin." + className + ".activate") == null)
			{
				// Old API
				try
				{
					ep.createOptionPanes(this);
				}
				catch(Throwable t)
				{
					Log.log(Log.ERROR, ep,
						"Error creating option pane");
					Log.log(Log.ERROR, ep, t);
				}
			}
			else
			{
				String optionPane = jEdit.getProperty(
					"plugin." + className + ".option-pane");
				if(optionPane != null)
					pluginsGroup.addOptionPane(optionPane);
				else
				{
					String options = jEdit.getProperty(
						"plugin." + className
						+ ".option-group");
					if(options != null)
					{
						pluginsGroup.addOptionGroup(
							new OptionGroup(
							"plugin." + className,
							jEdit.getProperty("plugin."
							+ className + ".name"),
							options)
						);
					}
				}
			}
		}

		// only add the Plugins branch if there are OptionPanes
		if (pluginsGroup.getMemberCount() == 0)
			pluginsGroup.addOptionPane(new NoPluginsPane());

		rootGroup.addOptionGroup(pluginsGroup);

		return paneTreeModel;
	} //}}}

	//{{{ getDefaultGroup() method
	protected OptionGroup getDefaultGroup()
	{
		return pluginsGroup;
	} //}}}

	//{{{ Private members
	private OptionGroup pluginsGroup;
	//}}}

	//{{{ NoPluginsPane class
	static class NoPluginsPane extends AbstractOptionPane
	{
		public NoPluginsPane()
		{
			super("no-plugins");
		}
	} //}}}
}