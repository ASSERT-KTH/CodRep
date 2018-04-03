c.insets = new Insets(2, 2, 2, 2);

//The contents of this file are subject to the Mozilla Public License Version 1.1
//(the "License"); you may not use this file except in compliance with the 
//License. You may obtain a copy of the License at http://www.mozilla.org/MPL/
//
//Software distributed under the License is distributed on an "AS IS" basis,
//WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License 
//for the specific language governing rights and
//limitations under the License.
//
//The Original Code is "The Columba Project"
//
//The Initial Developers of the Original Code are Frederik Dietz and Timo Stich.
//Portions created by Frederik Dietz and Timo Stich are Copyright (C) 2003. 
//
//All Rights Reserved.

package org.columba.mail.gui.config.filter;

import java.awt.BorderLayout;
import java.awt.Component;
import java.awt.Dimension;
import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.GridLayout;
import java.awt.Insets;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.util.Iterator;
import java.util.List;
import java.util.Vector;

import javax.swing.BorderFactory;
import javax.swing.Box;
import javax.swing.JButton;
import javax.swing.JPanel;
import javax.swing.JScrollPane;

import org.columba.core.config.Config;
import org.columba.core.config.TableItem;
import org.columba.core.gui.util.ImageLoader;
import org.columba.core.gui.util.NotifyDialog;
import org.columba.core.main.MainInterface;
import org.columba.core.plugin.AbstractPluginHandler;
import org.columba.core.plugin.PluginHandlerNotFoundException;
import org.columba.mail.filter.Filter;
import org.columba.mail.filter.FilterCriteria;
import org.columba.mail.filter.FilterRule;
import org.columba.mail.gui.config.filter.plugins.DefaultCriteriaRow;
import org.columba.mail.plugin.AbstractFilterPluginHandler;

public class CriteriaList extends JPanel implements ActionListener {

	private Config config;
	private Filter filter;

	private TableItem v;
	private List list;
	private JPanel panel;
	private AbstractPluginHandler pluginHandler;

	public CriteriaList(Filter filter) {
		super();

		try {

			pluginHandler =
				MainInterface.pluginManager.getHandler(
					"org.columba.mail.filter");
		} catch (PluginHandlerNotFoundException ex) {
			NotifyDialog d = new NotifyDialog();
			d.showDialog(ex);
		}

		this.config = MainInterface.config;
		this.filter = filter;

		list = new Vector();

		panel = new JPanel();
		JScrollPane scrollPane = new JScrollPane(panel);
		setBorder(BorderFactory.createEmptyBorder(1, 1, 1, 1));

		scrollPane.setPreferredSize(new Dimension(500, 100));
		setLayout(new BorderLayout());

		add(scrollPane, BorderLayout.CENTER);

		update();
	}

	public void updateComponents(boolean b) {
		if (!b) {
			for (Iterator it = list.iterator(); it.hasNext();) {
				DefaultCriteriaRow row = (DefaultCriteriaRow)  it.next();
			// for (int i = 0; i < list.size(); i++) {
				// DefaultCriteriaRow row = (DefaultCriteriaRow) list.get(i);
				row.updateComponents(false);
			}
		}
	}

	public void add() {

		FilterRule rule = filter.getFilterRule();
		rule.addEmptyCriteria();

		updateComponents(false);
		update();
	}

	public void remove(int i) {

		FilterRule rule = filter.getFilterRule();

		if (rule.count() > 1) {
			updateComponents(false);
			rule.remove(i);
			update();
		}
	}

	public void update() {
		panel.removeAll();
		list.clear();

		GridBagLayout gridbag = new GridBagLayout();
		GridBagConstraints c = new GridBagConstraints();
		panel.setLayout(gridbag);

		FilterRule rule = filter.getFilterRule();

		for (int i = 0; i < rule.count(); i++) {
			FilterCriteria criteria = rule.get(i);
			String type = criteria.getType();
			DefaultCriteriaRow column = null;

			c.fill = GridBagConstraints.NONE;
			//c.fill = GridBagConstraints.HORIZONTAL;
			c.gridx = GridBagConstraints.RELATIVE;
			c.gridy = i;
			c.weightx = 1.0;
			c.anchor = GridBagConstraints.NORTHWEST;
			c.insets = new Insets(0, 0, 0, 0);
			c.gridwidth = 1;

			//String className = pluginList.getGuiClassName(type);

			Object[] args = { pluginHandler, this, criteria };

			try {
				column =
					(DefaultCriteriaRow)
						(
							(
								AbstractFilterPluginHandler) pluginHandler)
									.getGuiPlugin(
						type,
						args);
			} catch (Exception ex) {
				ex.printStackTrace();
			}

			/*
			if (type.equalsIgnoreCase("Custom Headerfield")) {
				column = new CustomHeaderfieldCriteriaRow(this, criteria);
				gridbag.setConstraints(column, c);
			} else if (type.equalsIgnoreCase("Date")) {
				column = new DateCriteriaRow(this, criteria);
				gridbag.setConstraints(column, c);
			} else if (type.equalsIgnoreCase("Size")) {
				column = new SizeCriteriaRow(this, criteria);
				gridbag.setConstraints(column, c);
			} else if (type.equalsIgnoreCase("Flags")) {
				column = new FlagsCriteriaRow(this, criteria);
				gridbag.setConstraints(column, c);
			} else if (type.equalsIgnoreCase("Priority")) {
				column = new PriorityCriteriaRow(this, criteria);
				gridbag.setConstraints(column, c);
			} else if (type.equalsIgnoreCase("Body")) {
				column = new BodyCriteriaRow(this, criteria);
				gridbag.setConstraints(column, c);
			} else {
				column = new HeaderCriteriaRow(this, criteria);
				
			}
			*/

			// fall-back if error occurs
			if (column == null) {
				try {
					column =
						(DefaultCriteriaRow)
							(
								(
									AbstractFilterPluginHandler) pluginHandler)
										.getGuiPlugin(
							"Subject",
							args);
				} catch (Exception ex) {
					ex.printStackTrace();
				}
				criteria.setType("Subject");
			}

			gridbag.setConstraints(column.getContentPane(), c);
			list.add(column);

			panel.add(column.getContentPane());

			JButton addButton =
				new JButton(ImageLoader.getSmallImageIcon("stock_add_16.png"));
			addButton.setActionCommand("ADD");
			addButton.setMargin(new Insets(0, 0, 0, 0));
			addButton.addActionListener(new ActionListener() {
				public void actionPerformed(ActionEvent e) {
					add();
				}
			});

			/*
			//c.insets = new Insets(1, 2, 1, 2);
			c.gridx = GridBagConstraints.RELATIVE;
			c.anchor = GridBagConstraints.NORTHEAST;
			c.weightx = 1.0;
			gridbag.setConstraints(addButton, c);
			panel.add(addButton);
			*/

			JButton removeButton =
				new JButton(
					ImageLoader.getSmallImageIcon("stock_remove_16.png"));
			removeButton.setMargin(new Insets(0, 0, 0, 0));
			removeButton.setActionCommand(new Integer(i).toString());
			final int index = i;
			removeButton.addActionListener(new ActionListener() {
				public void actionPerformed(ActionEvent e) {
					remove(index);
				}
			});

			JPanel buttonPanel = new JPanel();
			buttonPanel.setLayout(new GridLayout(0, 2, 2, 2));
			buttonPanel.add(removeButton);
			buttonPanel.add(addButton);

			//c.insets = new Insets(1, 2, 1, 2);
			c.gridx = GridBagConstraints.REMAINDER;
			c.anchor = GridBagConstraints.NORTHEAST;
			gridbag.setConstraints(buttonPanel, c);
			panel.add(buttonPanel);
		}

		c.weighty = 1.0;
		Component box = Box.createVerticalGlue();
		gridbag.setConstraints(box, c);
		panel.add(box);

		validate();
		repaint();
	}

	public void actionPerformed(ActionEvent e) {
		updateComponents(false);
		update();
	}
}