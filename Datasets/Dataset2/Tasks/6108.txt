pluginHandler = PluginManager.getInstance().getExtensionHandler(

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

import java.awt.Component;

import javax.swing.DefaultListCellRenderer;
import javax.swing.JList;
import javax.swing.UIManager;

import org.columba.api.exception.PluginHandlerNotFoundException;
import org.columba.api.plugin.IExtension;
import org.columba.api.plugin.IExtensionHandler;
import org.columba.core.gui.dialog.ErrorDialog;
import org.columba.core.plugin.PluginManager;


public class PluginListCellRenderer extends DefaultListCellRenderer {
    protected IExtensionHandler pluginHandler;

    public PluginListCellRenderer() {
        super();

        try {
            pluginHandler = PluginManager.getInstance().getHandler(
                    "org.columba.addressbook.import");
        } catch (PluginHandlerNotFoundException ex) {
        	ErrorDialog.createDialog(ex.getMessage(), ex);
        }
    }

    /* (non-Javadoc)
 * @see javax.swing.ListCellRenderer#getListCellRendererComponent(javax.swing.JList, java.lang.Object, int, boolean, boolean)
 */
    public Component getListCellRendererComponent(JList list, Object value,
        int index, boolean isSelected, boolean cellHasFocus) {
        if (isSelected) {
            setBackground(list.getSelectionBackground());
            setForeground(list.getSelectionForeground());
        } else {
            setBackground(list.getBackground());
            setForeground(list.getForeground());
        }

        setBorder((cellHasFocus)
            ? UIManager.getBorder("List.focusCellHighlightBorder") : noFocusBorder);

        // id = org.columba.example.HelloWorld$HelloWorldPlugin
        String id = (String) value;
        IExtension extension = pluginHandler.getExtension(id);
        String userVisibleName = extension.getMetadata().getId();
        setText(userVisibleName);

        return this;
    }
}