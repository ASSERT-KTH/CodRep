super("threadedview", "ThreadedViewOptions", mediator);

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

import org.columba.core.config.DefaultItem;
import org.columba.core.xml.XmlElement;

import org.columba.mail.folder.Folder;
import org.columba.mail.gui.frame.MailFrameMediator;
import org.columba.mail.gui.frame.TableViewOwner;
import org.columba.mail.gui.table.TableController;


/**
 * Handles enabled/disabled state of threaded-view.
 * 
 * @author fdietz
 */
public class ThreadedViewOptionsPlugin extends AbstractFolderOptionsPlugin {
    /**
     * Constructor
     * 
     * @param mediator      mail framemediator
     */
    public ThreadedViewOptionsPlugin(MailFrameMediator mediator) {
        super("threadedview", mediator);
    }

    /**
     * @see org.columba.mail.folderoptions.AbstractFolderOptionsPlugin#saveOptionsToXml(org.columba.mail.folder.Folder)
     */
    public void saveOptionsToXml(Folder folder) {
        XmlElement parent = getConfigNode(folder);
        DefaultItem item = new DefaultItem(parent);

        TableController tableController = ((TableViewOwner) getMediator()).getTableController();

        item.set("enabled",
            tableController.getTableModelThreadedView().isEnabled());
    }

    /**
     * @see org.columba.mail.folderoptions.AbstractFolderOptionsPlugin#loadOptionsFromXml(org.columba.mail.folder.Folder)
     */
    public void loadOptionsFromXml(Folder folder) {
        XmlElement parent = getConfigNode(folder);
        DefaultItem item = new DefaultItem(parent);

        boolean enableThreadedView = item.getBoolean("enabled", false);

        TableController tableController = ((TableViewOwner) getMediator()).getTableController();
        
        // enable threaded-view in threaded-table-model
        tableController.getTableModelThreadedView().setEnabled(enableThreadedView);
        
        // enable threaded-view mode in table model
        tableController.getHeaderTableModel().enableThreadedView(enableThreadedView);
        
        // enable custom renderer of view
        tableController.getView().enableThreadedView(enableThreadedView);
    }

    /**
       * @see org.columba.mail.folderoptions.AbstractFolderOptionsPlugin#createDefaultElement()
       */
    public XmlElement createDefaultElement(boolean global) {
        XmlElement parent = super.createDefaultElement(global);
        parent.addAttribute("enabled", "false");

        return parent;
    }
}