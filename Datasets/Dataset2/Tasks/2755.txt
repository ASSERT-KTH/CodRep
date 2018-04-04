XmlElement parent = folder.getConfiguration().getFolderOptions();

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
package org.columba.mail.folderoptions;

import org.columba.core.plugin.PluginInterface;
import org.columba.core.xml.XmlElement;

import org.columba.mail.config.FolderItem;
import org.columba.mail.folder.MessageFolder;
import org.columba.mail.gui.frame.MailFrameMediator;


/**
 * MessageFolder options plugin abstract class.
 * <p>
 * Plugins implementing this abstract class can load/save
 * their configuration data. They don't need to take care
 * if this data is applied globally or on a per-folder basis.
 * <p>
 * The most interest methods which you need to implement are:
 * <ul>
 *  <li>createDefaultElement(boolean)</li>
 *  <li>loadOptionsFromXml(MessageFolder)</li>
 *  <li>saveOptionsToXml(MessageFolder)</li>
 * </ul>
 * <p>
 * Note, that every {@link MailFrameMediator} keeps its own
 * {@link FolderOptionsController}, which makes sure that
 * all plugins are singletons.
 *
 * @author fdietz
 */
public abstract class AbstractFolderOptionsPlugin implements PluginInterface {
    /**
 * mail frame mediator
 */
    private MailFrameMediator mediator;

    /**
 * name of configuration node
 */
    private String name;

    /**
 * ID of plugin
 */
    private String pluginId;

    /**
 * Constructor
 *
 * @param name      name of plugin
 * @param pluginId        id of plugin used by plugin handler
 * @param mediator  mail frame mediator
 */
    public AbstractFolderOptionsPlugin(String name, String pluginId,
        MailFrameMediator mediator) {
        this.name = name;
        this.pluginId = pluginId;
        this.mediator = mediator;
    }

    /**
* Save configuration of this plugin.
* <p>
*
* Following a simple example of a toolbar configuration:<br>
*
* <pre>
* <toolbar enabled="true" show_icon="true" show_text="false">
*  <button name="Cut"/>
*  <button name="Copy"/>
*  <button name="Paste"/>
*  <button name="Delete"/>
* </toolbar>
* </pre>
*
* @param folder     selected folder
*/
    public abstract void saveOptionsToXml(MessageFolder folder);

    /**
 * Load options of this plugin.
 *
 * @param folder       selected folder
 */
    public abstract void loadOptionsFromXml(MessageFolder folder);

    /**
 * Get frame mediator
 *
 * @return      frame mediator
 */
    public MailFrameMediator getMediator() {
        return mediator;
    }

    /**
 * Get configuration node.
 * <p>
 * Determine if this should be applied globally or
 * on a per-folder basis.
 * <p>
 * This way, plugins don't have to know, if they work
 * on global or local options.
 * <p>
 * Example for the sorting plugin configuration node. This is
 * how it can be found in options.xml and tree.xml:<br>
 * <pre>
 *  <sorting column="Date" order="true" />
 * </pre>
 *
 * @param folder        currently selected folder
 * @return              xml node
 */
    public XmlElement getConfigNode(MessageFolder folder) {
        // global option
        if (folder == null) {
            return FolderItem.getGlobalOptions().getElement(getName());
        }

        // use folder specific options
        XmlElement parent = folder.getFolderItem().getFolderOptions();

        XmlElement child = parent.getElement(getName());

        // create element if not available
        if (child == null) {
            child = createDefaultElement(false);
            parent.addElement(child);
        }

        //      check if this folder is overwriting global options
        if (child.getAttribute("overwrite").equals("true")) {
            // use folder-based options
            return child;
        } else {
            // use global options
            parent = FolderItem.getGlobalOptions();
            child = parent.getElement(getName());

            if (child == null) {
                child = createDefaultElement(true);
                parent.addElement(child);
            }

            return child;
        }
    }

    /**
 * Create default node.
 * <p>
 * Overwrite this method to add plugin-specific information
 * to the parent node.
 * <p>
 * @param  global       true, if this is a global options. False, otherwise
 *
 * @return              xml node
 */
    public XmlElement createDefaultElement(boolean global) {
        XmlElement parent = new XmlElement(getName());

        // only local options have overwrite attribute
        if (!global) {
            parent.addAttribute("overwrite", "false");
        }

        return parent;
    }

    /**
 * Get name of configuration node
 *
 * @return     config name
 */
    public String getName() {
        return name;
    }
}