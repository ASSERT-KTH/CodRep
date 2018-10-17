viewer.openWith(header, tempFile, false);

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
package org.columba.mail.gui.attachment.command;

import org.columba.core.command.Command;
import org.columba.core.command.DefaultCommandReference;
import org.columba.core.io.TempFileStore;

import org.columba.mail.gui.mimetype.MimeTypeViewer;

import org.columba.ristretto.message.LocalMimePart;
import org.columba.ristretto.message.MimeHeader;

import java.io.File;

/**
 * @author freddy
 * @author redsolo
 */
public class OpenWithAttachmentCommand extends SaveAttachmentCommand {
    private File tempFile;
    private MimeHeader header;
    
    /**
     * Creates an Open with attachment command.
     * @param references command parameters.
     */
    public OpenWithAttachmentCommand(DefaultCommandReference[] references) {
        super(references);

        priority = Command.REALTIME_PRIORITY;
        commandType = Command.NORMAL_OPERATION;
    }

    /**
     * @see org.columba.core.command.Command#updateGUI()
     */
    public void updateGUI() throws Exception {
        MimeTypeViewer viewer = new MimeTypeViewer();
        viewer.openWith(header, tempFile);
    }

    /** {@inheritDoc} */
    protected File getDestinationFile(MimeHeader header) {
    	this.header = header; 
        String filename = header.getFileName();

        if (filename != null) {
            tempFile = TempFileStore.createTempFile(filename);
        } else {
            tempFile = TempFileStore.createTempFile();
        }

        return tempFile;
    }
}