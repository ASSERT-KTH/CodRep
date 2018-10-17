AddressbookInterface.addressbookTreeModel = new AddressbookTreeModel(AddressbookConfig.get(

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

package org.columba.addressbook.main;

import org.columba.addressbook.config.AddressbookConfig;
import org.columba.addressbook.gui.tree.AddressbookTreeModel;
import org.columba.addressbook.plugin.FolderPluginHandler;
import org.columba.addressbook.plugin.ImportPluginHandler;
import org.columba.addressbook.shutdown.SaveAllAddressbooksPlugin;
import org.columba.addressbook.util.AddressbookResourceLoader;

import org.columba.core.backgroundtask.TaskInterface;
import org.columba.core.main.DefaultMain;
import org.columba.core.main.MainInterface;
import org.columba.core.plugin.ActionPluginHandler;
import org.columba.core.plugin.MenuPluginHandler;
import org.columba.core.plugin.PluginHandlerNotFoundException;
import org.columba.core.shutdown.ShutdownManager;

/**
 * @author frd
 *
 * To change this generated comment edit the template variable "typecomment":
 * Window>Preferences>Java>Templates.
 * To enable and disable the creation of type comments go to
 * Window>Preferences>Java>Code Generation.
 */
public class AddressbookMain extends DefaultMain {
    /* (non-Javadoc)
     * @see org.columba.core.main.DefaultMain#handleCommandLineParameters(java.lang.String[])
     */
    public void handleCommandLineParameters(String[] args) {
    }

    /* (non-Javadoc)
     * @see org.columba.core.main.DefaultMain#initConfiguration()
     */
    public void initConfiguration() {
        new AddressbookConfig();
    }

    /* (non-Javadoc)
     * @see org.columba.core.main.DefaultMain#initGui()
     */
    public void initGui() {
        MainInterface.addressbookTreeModel = new AddressbookTreeModel(AddressbookConfig.get(
                    "tree").getElement("/tree"));

        /*
        MainInterface.addressbookModel =
                new AddressbookFrameModel(
                        AddressbookConfig.get("options").getElement(
                                "/options/gui/viewlist"));
        */
    }

    /* (non-Javadoc)
     * @see org.columba.core.main.DefaultMain#initPlugins()
     */
    public void initPlugins() {
        MainInterface.pluginManager.registerHandler(new FolderPluginHandler());

        MainInterface.pluginManager.registerHandler(new ImportPluginHandler());

        MainInterface.pluginManager.registerHandler(new MenuPluginHandler(
                "org.columba.addressbook.menu"));

        try {
            ((ActionPluginHandler) MainInterface.pluginManager.getHandler(
                "org.columba.core.action")).addActionList(
                "org/columba/addressbook/action/action.xml");
        } catch (PluginHandlerNotFoundException ex) {
        }

        TaskInterface plugin = new SaveAllAddressbooksPlugin();
        MainInterface.backgroundTaskManager.register(plugin);
        ShutdownManager.getShutdownManager().register(plugin);
    }
}