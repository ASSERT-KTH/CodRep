import org.columba.core.main.MainInterface;

// This program is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation; either version 2 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Library General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program; if not, write to the Free Software
// Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

package org.columba.mail.gui.config.filter.plugins;

import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.Insets;

import javax.swing.JComboBox;
import javax.swing.JComponent;
import javax.swing.JPanel;

import org.columba.core.plugin.DefaultPlugin;
import org.columba.mail.filter.FilterAction;
import org.columba.mail.gui.config.filter.ActionList;
import org.columba.mail.plugin.FilterActionPluginHandler;
import org.columba.main.MainInterface;

public class DefaultActionRow extends DefaultPlugin {
	
	protected JPanel panel;
	
	protected FilterAction filterAction;

	private JComboBox actionComboBox;

	protected GridBagLayout gridbag = new GridBagLayout();
	protected GridBagConstraints c = new GridBagConstraints();

	protected ActionList actionList;

	protected int count;

	
	public DefaultActionRow(ActionList list, FilterAction action) {
		
		this.filterAction = action;
		this.actionList = list;
		
		panel = new JPanel();
	
		initComponents();
	
		updateComponents(true);
	
		actionComboBox.addActionListener(actionList);
	}
	
	public JPanel getContentPane()
	{
		return panel;
	}

	public void updateComponents(boolean b) {

		if (b) {

			String name = (String) filterAction.getAction();
			actionComboBox.setSelectedItem(name);

		} else {
			String name = (String) actionComboBox.getSelectedItem();
			filterAction.setAction(name);

		}

	}

	public void initComponents() {
		panel.removeAll();

		panel.setLayout(gridbag);

		FilterActionPluginHandler pluginHandler =
			(FilterActionPluginHandler) MainInterface.pluginManager.getHandler(
				"filter_actions");

		actionComboBox = new JComboBox(pluginHandler.getDefaultNames());

		c.fill = GridBagConstraints.NONE;
		c.weightx = 1.0;
		c.insets = new Insets(2, 5, 2, 5);
		c.gridx = 0;
		c.anchor = GridBagConstraints.WEST;
		c.gridwidth = 1;

		gridbag.setConstraints(actionComboBox, c);
		panel.add(actionComboBox);

		count = 0;

		
	}

	public void addComponent(JComponent component) {
		c.gridx = ++count;
		gridbag.setConstraints(component, c);
		panel.add(component);
	}

	/**
	 * Returns the filterAction.
	 * @return FilterAction
	 */
	public FilterAction getFilterAction() {
		return filterAction;
	}

	/**
	 * Sets the filterAction.
	 * @param filterAction The filterAction to set
	 */
	public void setFilterAction(FilterAction filterAction) {
		this.filterAction = filterAction;
	}

}