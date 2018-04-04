.getInstance().getExtensionHandler(IExtensionHandlerKeys.ORG_COLUMBA_CORE_CONFIG);

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

package org.columba.core.gui.plugin;

import java.awt.BorderLayout;
import java.awt.GridLayout;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.KeyEvent;

import javax.swing.BorderFactory;
import javax.swing.JButton;
import javax.swing.JComponent;
import javax.swing.JDialog;
import javax.swing.JFrame;
import javax.swing.JPanel;
import javax.swing.KeyStroke;
import javax.swing.SwingConstants;

import net.javaprog.ui.wizard.plaf.basic.SingleSideEtchedBorder;

import org.columba.api.exception.PluginException;
import org.columba.api.exception.PluginHandlerNotFoundException;
import org.columba.api.exception.PluginLoadingFailedException;
import org.columba.api.plugin.IExtension;
import org.columba.api.plugin.IExtensionHandler;
import org.columba.api.plugin.IExtensionHandlerKeys;
import org.columba.core.gui.base.ButtonWithMnemonic;
import org.columba.core.help.HelpManager;
import org.columba.core.plugin.PluginManager;
import org.columba.core.resourceloader.GlobalResourceLoader;

/**
 * @author frd
 */

public class ConfigurationDialog extends JDialog implements ActionListener {
	protected JButton okButton;

	protected JButton cancelButton;

	protected JButton helpButton;

	protected String pluginId;

	protected AbstractConfigPlugin plugin;

	protected JPanel pluginPanel;

	public ConfigurationDialog(String pluginId)
			throws PluginHandlerNotFoundException, PluginLoadingFailedException {
		// modal dialog
		super((JFrame) null, true);

		IExtensionHandler h =  PluginManager
				.getInstance().getHandler(IExtensionHandlerKeys.ORG_COLUMBA_CORE_CONFIG);

		IExtension extension = h.getExtension(pluginId);
		try {
			plugin = (AbstractConfigPlugin) extension.instanciateExtension(null);
		} catch (PluginException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}

		pluginPanel = plugin.createPanel();

		initComponents();

		// model->view
		plugin.updateComponents(true);

		pack();
		setLocationRelativeTo(null);
	}

	protected void initComponents() {
		JPanel mainPanel = new JPanel();
		mainPanel.setLayout(new BorderLayout());
		mainPanel.setBorder(BorderFactory.createEmptyBorder(12, 12, 12, 12));
		getContentPane().add(mainPanel);

		// centerpanel
		JPanel centerPanel = new JPanel(new BorderLayout());

		// centerPanel.setBorder(BorderFactory.createEmptyBorder(0, 0, 0, 5));
		centerPanel.add(pluginPanel);
		mainPanel.add(centerPanel, BorderLayout.CENTER);

		JPanel bottomPanel = new JPanel(new BorderLayout());
		bottomPanel.setBorder(new SingleSideEtchedBorder(SwingConstants.TOP));

		JPanel buttonPanel = new JPanel(new GridLayout(1, 3, 6, 0));
		buttonPanel.setBorder(BorderFactory.createEmptyBorder(12, 12, 12, 12));
		okButton = new ButtonWithMnemonic(GlobalResourceLoader.getString(
				"global", "global", "ok"));
		okButton.setActionCommand("OK");
		okButton.addActionListener(this);
		buttonPanel.add(okButton);

		ButtonWithMnemonic cancelButton = new ButtonWithMnemonic(
				GlobalResourceLoader.getString("global", "global", "cancel"));
		cancelButton.setActionCommand("CANCEL");
		cancelButton.addActionListener(this);
		buttonPanel.add(cancelButton);
		helpButton = new ButtonWithMnemonic(GlobalResourceLoader.getString(
				"global", "global", "help"));
		buttonPanel.add(helpButton);

		bottomPanel.add(buttonPanel, BorderLayout.EAST);
		getContentPane().add(bottomPanel, BorderLayout.SOUTH);

		// setContentPane(mainPanel);
		getRootPane().setDefaultButton(okButton);
		getRootPane().registerKeyboardAction(this, "CANCEL",
				KeyStroke.getKeyStroke(KeyEvent.VK_ESCAPE, 0),
				JComponent.WHEN_IN_FOCUSED_WINDOW);

		// associate with JavaHelp
		HelpManager.getInstance().enableHelpOnButton(helpButton,
				"extending_columba_1");
		HelpManager.getInstance().enableHelpKey(getRootPane(),
				"extending_columba_1");
	}

	public void actionPerformed(ActionEvent e) {
		String action = e.getActionCommand();

		if (action.equals("OK")) {
			// view -> model
			plugin.updateComponents(false);

			setVisible(false);
		} else if (action.equals("CANCEL")) {
			setVisible(false);
		}
	}
}