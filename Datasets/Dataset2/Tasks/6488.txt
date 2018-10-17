pluginHandler =  PluginManager.getInstance().getExtensionHandler(

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

import javax.help.CSH;

import net.javaprog.ui.wizard.DataLookup;
import net.javaprog.ui.wizard.DataModel;
import net.javaprog.ui.wizard.DefaultWizardModel;
import net.javaprog.ui.wizard.JavaHelpSupport;
import net.javaprog.ui.wizard.Step;
import net.javaprog.ui.wizard.Wizard;
import net.javaprog.ui.wizard.WizardModel;

import org.columba.api.exception.PluginHandlerNotFoundException;
import org.columba.api.gui.frame.IFrameMediator;
import org.columba.api.plugin.IExtensionHandler;
import org.columba.core.help.HelpManager;
import org.columba.core.plugin.PluginManager;
import org.columba.core.resourceloader.IconKeys;
import org.columba.core.resourceloader.ImageLoader;
import org.columba.mail.util.MailResourceLoader;

/**
 * Responsible for starting the mailbox import wizard.
 */
public class ImportWizardLauncher {
    private IFrameMediator mediator;
	
    public ImportWizardLauncher(IFrameMediator mediator) {
    	this.mediator = mediator;
    }

    public void launchWizard() {
        final IExtensionHandler pluginHandler;

        try {
            pluginHandler =  PluginManager.getInstance().getHandler(
                    "org.columba.mail.import");
        } catch (PluginHandlerNotFoundException ex) {
            throw new RuntimeException(ex);
        }

        DataModel data = new DataModel();
        data.registerDataLookup("Plugin.handler",
            new DataLookup() {
                public Object lookupData() {
                    return pluginHandler;
                }
            });

        WizardModel model = new DefaultWizardModel(new Step[] {
                new PluginStep(data), new LocationStep(mediator, data)
        });
        model.addWizardModelListener(new MailboxImporter(data));

        Wizard wizard = new Wizard(model,
                MailResourceLoader.getString("dialog", "mailboximport", "title"),
                ImageLoader.getIcon(IconKeys.PREFERENCES));
        wizard.setStepListRenderer(null);
        CSH.setHelpIDString(wizard, "organising_and_managing_your_email_1");
        JavaHelpSupport.enableHelp(wizard,
            HelpManager.getInstance().getHelpBroker());
        wizard.pack();
        wizard.setLocationRelativeTo(null);
        wizard.setVisible(true);
    }
}