ColumbaLogger.log.severe("Not yet implemented!");

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
package org.columba.mail.gui.attachment;

import org.columba.core.command.DefaultCommandReference;
import org.columba.core.gui.selection.SelectionHandler;
import org.columba.core.logging.ColumbaLogger;

import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.folder.Folder;
import org.columba.mail.gui.attachment.util.IconPanelSelectionListener;


public class AttachmentSelectionHandler extends SelectionHandler
    implements IconPanelSelectionListener {
    private Folder folder;
    private Object messageUid;
    private AttachmentView view;
    private Integer[] address;
    private boolean useLocalSelection;

    public AttachmentSelectionHandler(AttachmentView view) {
        super("mail.attachment");
        this.view = view;
        view.addIconPanelSelectionListener(this);

        useLocalSelection = false;
    }

    /* (non-Javadoc)
     * @see org.columba.core.gui.selection.SelectionHandler#getSelection()
     */
    public DefaultCommandReference[] getSelection() {
        return new FolderCommandReference[] {
            new FolderCommandReference(folder, new Object[] { messageUid },
                address)
        };
    }

    /* (non-Javadoc)
     * @see org.columba.core.gui.selection.SelectionHandler#setSelection(org.columba.core.command.DefaultCommandReference[])
     */
    public void setSelection(DefaultCommandReference[] selection) {
        ColumbaLogger.log.error("Not yet implemented!");
    }

    public void setMessage(Folder folder, Object messageUid) {
        this.folder = folder;
        this.messageUid = messageUid;
    }

    /* (non-Javadoc)
     * @see org.columba.mail.gui.attachment.util.IconPanelSelectionListener#selectionChanged(int[])
     */
    public void selectionChanged(int[] newselection) {
        useLocalSelection = false;

        if (newselection.length > 0) {
            address = view.getSelectedMimePart().getAddress();
        } else {
            address = null;
        }

        fireSelectionChanged(new AttachmentSelectionChangedEvent(folder,
                messageUid, address));
    }

    public void setLocalReference(FolderCommandReference[] r) {
        // set selection
        setMessage((Folder) r[0].getFolder(), r[0].getUids()[0]);
        useLocalSelection = true;
    }
}