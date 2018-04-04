FilterToolbar toolbar = ((AbstractMailView) getMediator().getView()).getFilterToolbar();

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

import org.columba.mail.folder.MessageFolder;
import org.columba.mail.gui.frame.MailFrameMediator;
import org.columba.mail.gui.frame.MailFrameView;
import org.columba.mail.gui.frame.TableViewOwner;
import org.columba.mail.gui.table.FilterToolbar;
import org.columba.mail.gui.table.TableController;
import org.columba.mail.gui.table.model.TableModelFilter;
import org.columba.mail.gui.view.AbstractMailView;


/**
 * Covers all filter options offered by the message list
 * filter toolbar.
 * <p>
 *
 * @author fdietz
 */
public class FilterOptionsPlugin extends AbstractFolderOptionsPlugin {
    /**
 * Constructor
 *
 * @param mediator  mail frame mediator
 */
    public FilterOptionsPlugin(MailFrameMediator mediator) {
        super("filter", "FilterOptions", mediator);
    }

    /**
 * @see org.columba.mail.folderoptions.AbstractFolderOptionsPlugin#saveOptionsToXml(org.columba.mail.folder.Folder)
 */
    public void saveOptionsToXml(MessageFolder folder) {
        XmlElement parent = getConfigNode(folder);
        DefaultItem item = new DefaultItem(parent);

        TableController tableController = ((TableViewOwner) getMediator()).getTableController();

        TableModelFilter model = tableController.getTableModelFilteredView();

        item.set("new_state", model.getNewFlag());

        item.set("answered_state", model.getAnsweredFlag());
        item.set("flagged_state", model.getFlaggedFlag());
        item.set("attachment_state", model.getAttachmentFlag());
        item.set("expunged_state", model.getExpungedFlag());

        item.set("pattern", model.getPatternString());
    }

    /**
 * @see org.columba.mail.folderoptions.AbstractFolderOptionsPlugin#loadOptionsFromXml(org.columba.mail.folder.Folder)
 */
    public void loadOptionsFromXml(MessageFolder folder) {
        XmlElement parent = getConfigNode(folder);
        DefaultItem item = new DefaultItem(parent);

        TableController tableController = ((TableViewOwner) getMediator()).getTableController();
        TableModelFilter model = tableController.getTableModelFilteredView();
        FilterToolbar toolbar = ((AbstractMailView) getMediator().getBaseView()).getFilterToolbar();

        model.setNewFlag(item.getBoolean("new_state"));
        toolbar.enableNew(item.getBoolean("new_state"));

        model.setAnsweredFlag(item.getBoolean("answered_state"));
        toolbar.enableAnswered(item.getBoolean("answered_state"));

        model.setFlaggedFlag(item.getBoolean("flagged_state"));
        toolbar.enableFlagged(item.getBoolean("flagged_state"));

        model.setAttachmentFlag(item.getBoolean("attachment_state"));
        toolbar.enableAttachment(item.getBoolean("attachment_state"));

        model.setExpungedFlag(item.getBoolean("expunged_state"));
        toolbar.enableExpunged(item.getBoolean("expunged_state"));

        String t = item.get("pattern");

        if (t == null) {
            t = "";
        }

        model.setPatternString(t);
        toolbar.setPattern(t);

        // enable filtering
        model.setDataFiltering(true);
    }

    /**
   * @see org.columba.mail.folderoptions.AbstractFolderOptionsPlugin#createDefaultElement()
   */
    public XmlElement createDefaultElement(boolean global) {
        XmlElement parent = super.createDefaultElement(global);
        parent.addAttribute("new_state", "false");
        parent.addAttribute("answered_state", "false");
        parent.addAttribute("flagged_state", "false");
        parent.addAttribute("expunged_state", "false");
        parent.addAttribute("attachment_state", "false");
        parent.addAttribute("pattern", "");

        return parent;
    }
}