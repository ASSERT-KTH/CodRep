import org.columba.api.gui.frame.IFrameMediator;

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

package org.columba.mail.gui.message.filter;

import org.columba.core.gui.frame.IFrameMediator;
import org.columba.mail.command.IMailFolderCommandReference;
import org.columba.mail.command.MailFolderCommandReference;
import org.columba.mail.folder.IMailbox;
import org.columba.mail.folder.temp.TempFolder;
import org.columba.mail.gui.frame.MailFrameMediator;
import org.columba.mail.gui.message.viewer.Rfc822MessageViewer;
import org.columba.mail.gui.table.selection.TableSelectionHandler;
import org.columba.mail.gui.tree.FolderTreeModel;
import org.columba.mail.message.IColumbaMessage;

/**
 * Should be used by every filter, which alters the message contents. This
 * is done the following way:
 * <p>
 * A new message is created and added to a temporary folder. All references of
 * the sources folder are re-mapped to the message in the temporary folder.
 * <p>
 *
 * @author fdietz
 */
public abstract class AbstractFilter implements Filter {

    private MailFrameMediator mediator;
    private Rfc822MessageViewer messageController;
    
    public AbstractFilter(MailFrameMediator mediator, Rfc822MessageViewer messageViewer) {
        this.mediator = mediator;
        this.messageController = messageViewer;
    }
    /**
     * @return 
     * @see org.columba.mail.gui.message.filter.Filter#filter(IMailbox, java.lang.Object)
     */
    public IMailFolderCommandReference filter(IMailbox folder, Object uid, IColumbaMessage message) throws Exception {
//      map selection to this temporary message
        TempFolder tempFolder = FolderTreeModel.getInstance().getTempFolder();

        // add message to temporary folder
        uid = tempFolder.addMessage(message);

        
        // create reference to this message
        MailFolderCommandReference local = new MailFolderCommandReference(tempFolder,
                new Object[] {uid});

        // if we don't use this here - actions like reply would only work
        // on the
        // the encrypted message
        TableSelectionHandler h1 = ((TableSelectionHandler) mediator
                .getSelectionManager().getHandler("mail.table"));

        h1.setLocalReference(local);

        // this is needed to be able to open attachments of the decrypted
        // message
        messageController.setAttachmentSelectionReference(local);
        
        return local;
    }

    /**
     * @return Returns the mediator.
     */
    public IFrameMediator getMediator() {
        return mediator;
    }
}