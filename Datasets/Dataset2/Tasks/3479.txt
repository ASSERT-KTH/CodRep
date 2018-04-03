super("sorting", "SortingOptions",  mediator);

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
 * Handles sorting state, including sorting order, which can
 * be ascending or descending and the actual column.
 * 
 * @author fdietz
 */
public class SortingOptionsPlugin extends AbstractFolderOptionsPlugin {
    
    /**
     * Constructor
     * 
     * @param mediator      mail framemediator
     */
    public SortingOptionsPlugin(MailFrameMediator mediator) {
        super("sorting", mediator);
    }

    /**
     * @see org.columba.mail.folderoptions.AbstractFolderOptionsPlugin#loadOptionsFromXml(org.columba.core.xml.XmlElement)
     */
    public void loadOptionsFromXml(Folder folder) {
        XmlElement sorting = getConfigNode(folder);
        DefaultItem item = new DefaultItem(sorting);

        String column = item.get("column");

        if (column == null) {
            column = "Date";
        }

        boolean order = item.getBoolean("order", true);

        TableController tableController = ((TableViewOwner) getMediator()).getTableController();

        tableController.getTableModelSorter().setSortingColumn(column);
        tableController.getTableModelSorter().setSortingOrder(order);
    }

    /**
     * @see org.columba.mail.folderoptions.AbstractFolderOptionsPlugin#saveOptionsToXml()
     */
    public void saveOptionsToXml(Folder folder) {
        XmlElement sorting = getConfigNode(folder);
        DefaultItem item = new DefaultItem(sorting);

        TableController tableController = ((TableViewOwner) getMediator()).getTableController();

        String column = tableController.getTableModelSorter().getSortingColumn();
        boolean order = tableController.getTableModelSorter().getSortingOrder();

        sorting.addAttribute("column", column);
        sorting.addAttribute("order", Boolean.toString(order));
    }

    /**
     * @see org.columba.mail.folderoptions.AbstractFolderOptionsPlugin#createDefaultElement()
     */
    public XmlElement createDefaultElement(boolean global) {
        XmlElement sorting = super.createDefaultElement(global);
        sorting.addAttribute("column", "Date");
        sorting.addAttribute("order", "true");

        return sorting;
    }
}