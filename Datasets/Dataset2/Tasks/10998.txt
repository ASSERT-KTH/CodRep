new InfoStep(),

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
package org.columba.core.gui.externaltools;

import net.javaprog.ui.wizard.DataLookup;
import net.javaprog.ui.wizard.DataModel;
import net.javaprog.ui.wizard.DefaultWizardModel;
import net.javaprog.ui.wizard.Step;
import net.javaprog.ui.wizard.Wizard;
import net.javaprog.ui.wizard.WizardModel;

import org.columba.core.externaltools.AbstractExternalToolsPlugin;
import org.columba.core.main.MainInterface;
import org.columba.core.plugin.ExternalToolsPluginHandler;
import org.columba.core.plugin.PluginHandlerNotFoundException;

/**
 * Launches external tools wizard.
 *
 * @author fdietz
 */
public class ExternalToolsWizardLauncher {

	ExternalToolsWizardModelListener listener;
	
	DataModel data;

	public void launchFirstTimeWizard(String pluginID) {

		final String id = pluginID;
		final AbstractExternalToolsPlugin plugin;
		ExternalToolsPluginHandler handler = null;

		try {
			handler =
				(
					ExternalToolsPluginHandler) MainInterface
						.pluginManager
						.getHandler(
					"org.columba.core.externaltools");
		} catch (PluginHandlerNotFoundException e) {
			e.printStackTrace();
		}

		try {
			plugin =
				(AbstractExternalToolsPlugin) handler.getPlugin(pluginID, null);

		} catch (Exception e1) {

			e1.printStackTrace();

			return;
		}

		data = new DataModel();
		data.registerDataLookup("id", new DataLookup() {
			public Object lookupData() {
				return id;
			}
		});

		data.registerDataLookup("Plugin", new DataLookup() {
			public Object lookupData() {
				return plugin;
			}
		});

		WizardModel model =
			new DefaultWizardModel(
				new Step[] {
					new InfoStep(data),
					new DescriptionStep(data),
					new LocationStep(data)});

		listener = new ExternalToolsWizardModelListener(data);
		model.addWizardModelListener(listener);

		// TODO: i18n
		Wizard wizard = new Wizard(model, "External Tools Configuration", null);

		// TODO: add JavaHelp id
		//CSH.setHelpIDString(wizard, "");
		//JavaHelpSupport.enableHelp(wizard, HelpManager.getHelpBroker());

		wizard.pack();
		wizard.setLocationRelativeTo(null);
		wizard.setVisible(true);
	}

	public void launchWizard(String pluginID) {

		final String id = pluginID;
		final AbstractExternalToolsPlugin plugin;
		ExternalToolsPluginHandler handler = null;

		try {
			handler =
				(
					ExternalToolsPluginHandler) MainInterface
						.pluginManager
						.getHandler(
					"org.columba.core.externaltools");
		} catch (PluginHandlerNotFoundException e) {
			e.printStackTrace();
		}

		try {
			plugin =
				(AbstractExternalToolsPlugin) handler.getPlugin(pluginID, null);

		} catch (Exception e1) {

			e1.printStackTrace();

			return;
		}

		data = new DataModel();
		data.registerDataLookup("id", new DataLookup() {
			public Object lookupData() {
				return id;
			}
		});

		data.registerDataLookup("Plugin", new DataLookup() {
			public Object lookupData() {
				return plugin;
			}
		});

		WizardModel model =
			new DefaultWizardModel(
				new Step[] {
					new DescriptionStep(data),
					new LocationStep(data)});

		listener = new ExternalToolsWizardModelListener(data);
		model.addWizardModelListener(listener);

		// TODO: i18n
		Wizard wizard = new Wizard(model, "External Tools Configuration", null);

		// TODO: add JavaHelp id
		//CSH.setHelpIDString(wizard, "");
		//JavaHelpSupport.enableHelp(wizard, HelpManager.getHelpBroker());

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