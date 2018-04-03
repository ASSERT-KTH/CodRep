JavaHelpSupport.enableHelp(wizard, HelpManager.getInstance()

// The contents of this file are subject to the Mozilla Public License Version
// 1.1
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
//The Initial Developers of the Original Code are Frederik Dietz and Timo
// Stich.
//Portions created by Frederik Dietz and Timo Stich are Copyright (C) 2003.
//
//All Rights Reserved.
package org.columba.core.gui.externaltools;

import javax.help.CSH;

import net.javaprog.ui.wizard.DataLookup;
import net.javaprog.ui.wizard.DataModel;
import net.javaprog.ui.wizard.DefaultWizardModel;
import net.javaprog.ui.wizard.JavaHelpSupport;
import net.javaprog.ui.wizard.Step;
import net.javaprog.ui.wizard.Wizard;
import net.javaprog.ui.wizard.WizardModel;

import org.columba.core.externaltools.AbstractExternalToolsPlugin;
import org.columba.core.gui.util.ImageLoader;
import org.columba.core.help.HelpManager;
import org.columba.core.plugin.IExtension;
import org.columba.core.plugin.PluginManager;
import org.columba.core.plugin.exception.PluginHandlerNotFoundException;
import org.columba.core.pluginhandler.ExternalToolsExtensionHandler;

/**
 * Launches external tools wizard.
 * 
 * @author fdietz
 */
public class ExternalToolsWizardLauncher {
	protected DataModel data;

	protected ExternalToolsWizardModelListener listener;

	public void launchWizard(final String pluginID, boolean firstTime) {
		final AbstractExternalToolsPlugin plugin;
		ExternalToolsExtensionHandler handler = null;

		try {
			handler = (ExternalToolsExtensionHandler) PluginManager.getInstance()
					.getHandler(ExternalToolsExtensionHandler.NAME);
		} catch (PluginHandlerNotFoundException e) {
			e.printStackTrace();
		}

		try {
			IExtension extension = handler.getExtension(pluginID);

			plugin = (AbstractExternalToolsPlugin) extension
					.instanciateExtension(null);
		} catch (Exception e1) {
			e1.printStackTrace();

			return;
		}

		data = new DataModel();
		data.registerDataLookup("id", new DataLookup() {
			public Object lookupData() {
				return pluginID;
			}
		});

		data.registerDataLookup("Plugin", new DataLookup() {
			public Object lookupData() {
				return plugin;
			}
		});

		WizardModel model;

		if (firstTime) {
			model = new DefaultWizardModel(new Step[] {
					new DescriptionStep(data), new LocationStep(data) });
		} else {
			model = new DefaultWizardModel(new Step[] { new InfoStep(),
					new DescriptionStep(data), new LocationStep(data) });
		}

		listener = new ExternalToolsWizardModelListener(data);
		model.addWizardModelListener(listener);

		// TODO (@author fdietz): i18n
		Wizard wizard = new Wizard(model, "External Tools Configuration",
				ImageLoader.getSmallImageIcon("stock_preferences.png"));

		CSH.setHelpIDString(wizard, "extending_columba_2");
		JavaHelpSupport.enableHelp(wizard, HelpManager.getHelpManager()
				.getHelpBroker());

		wizard.pack();
		wizard.setLocationRelativeTo(null);
		wizard.setVisible(true);
	}

	public boolean isFinished() {
		return listener.isFinished();
	}

	/**
	 * @return
	 */
	public DataModel getData() {
		return data;
	}
}