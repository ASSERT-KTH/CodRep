import org.columba.api.plugin.IExtension;

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
package org.columba.addressbook.gui.dialog.importfilter;

import net.javaprog.ui.wizard.DataModel;
import net.javaprog.ui.wizard.WizardModelEvent;
import net.javaprog.ui.wizard.WizardModelListener;

import org.columba.addressbook.folder.importfilter.DefaultAddressbookImporter;
import org.columba.addressbook.plugin.ImportExtensionHandler;
import org.columba.core.plugin.IExtension;

class AddressbookImporter implements WizardModelListener {
	protected DataModel data;

	public AddressbookImporter(DataModel data) {
		this.data = data;
	}

	public void wizardFinished(WizardModelEvent e) {
		ImportExtensionHandler pluginHandler = (ImportExtensionHandler) data
				.getData("Plugin.handler");
		DefaultAddressbookImporter importer = null;
		Object[] args = new Object[] { data.getData("Location.source"),
				data.getData("Location.destination") };

		try {
			String pluginID = (String) data.getData("Plugin.ID");
			IExtension extension = pluginHandler.getExtension(pluginID);

			importer = (DefaultAddressbookImporter) extension
					.instanciateExtension(args);

			importer.run();
		} catch (Exception ex) {
			ex.printStackTrace();

			if (ex.getCause() != null) {
				ex.getCause().printStackTrace();
			}

			return;
		}
	}

	public void stepShown(WizardModelEvent e) {
	}

	public void wizardCanceled(WizardModelEvent e) {
	}

	public void wizardModelChanged(WizardModelEvent e) {
	}
}