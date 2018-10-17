ImageLoader.getSmallImageIcon("stock_convert.png"));

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

package org.columba.mail.gui.config.mailboximport;

import net.javaprog.ui.wizard.*;

import org.columba.core.gui.util.ImageLoader;
import org.columba.core.gui.util.NotifyDialog;
import org.columba.core.main.MainInterface;
import org.columba.core.plugin.PluginHandlerNotFoundException;
import org.columba.mail.plugin.ImportPluginHandler;
import org.columba.mail.util.MailResourceLoader;

public class ImportWizardLauncher {
        public ImportWizardLauncher() {}
        
        public void launchWizard() {
		final ImportPluginHandler pluginHandler;
		try {
			pluginHandler = (ImportPluginHandler) MainInterface.pluginManager.getHandler(
							"org.columba.mail.import");
		} catch (PluginHandlerNotFoundException ex) {
			NotifyDialog d = new NotifyDialog();
                        //show neat error message here
			d.showDialog(ex);
                        return;
		}
                DataModel data = new DataModel();
                data.registerDataLookup("Plugin.handler", new DataLookup() {
                        public Object lookupData() {
                               return pluginHandler; 
                        }
                });
                WizardModel model = new DefaultWizardModel(new Step[]{
                        new PluginStep(data),
                        new LocationStep(data)
                });
                model.addWizardModelListener(new MailboxImporter(data));
                Wizard wizard = new Wizard(model, MailResourceLoader.getString(
                                "dialog",
                                "mailboximport",
                                "title"),
                                ImageLoader.getSmallImageIcon("stock_preferences.png"));
                wizard.setSize(500, 400);
                wizard.setLocationRelativeTo(null);
                wizard.setVisible(true);
        }
}