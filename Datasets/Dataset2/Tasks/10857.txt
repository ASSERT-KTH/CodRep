viewer.open(header, tempFile, false);

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

import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.util.logging.Level;
import java.util.logging.Logger;

import org.columba.core.command.Command;
import org.columba.core.command.DefaultCommandReference;
import org.columba.core.command.Worker;
import org.columba.core.command.WorkerStatusController;
import org.columba.core.io.StreamUtils;
import org.columba.core.io.TempFileStore;
import org.columba.core.main.MainInterface;
import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.folder.MessageFolder;
import org.columba.mail.folder.temp.TempFolder;
import org.columba.mail.gui.message.command.ViewMessageCommand;
import org.columba.mail.gui.messageframe.MessageFrameController;
import org.columba.mail.gui.mimetype.MimeTypeViewer;
import org.columba.mail.main.MailInterface;
import org.columba.ristretto.coder.Base64DecoderInputStream;
import org.columba.ristretto.coder.QuotedPrintableDecoderInputStream;
import org.columba.ristretto.message.MimeHeader;


/**
 * @author freddy
 */
public class OpenAttachmentCommand extends SaveAttachmentCommand {
    private static final Logger LOG = Logger.getLogger("org.columba.mail.gui.attachment.command");
    private File tempFile;

    // true, if showing a message as attachment
    private boolean inline = false;
    private TempFolder tempFolder;
    private Object tempMessageUid;

    private MimeHeader header;
    /**
     * Constructor for OpenAttachmentCommand.
     * @param references command parameters
     */
    public OpenAttachmentCommand(DefaultCommandReference[] references) {
        super(references);

        priority = Command.REALTIME_PRIORITY;
        commandType = Command.NORMAL_OPERATION;
    }

    /**
     * @see org.columba.core.command.Command#updateGUI()
     */
    public void updateGUI() throws Exception {

        if (header.getMimeType().getType().toLowerCase().indexOf("message") != -1) {
            MessageFrameController c = new MessageFrameController();

            FolderCommandReference[] r = new FolderCommandReference[1];
            Object[] uidList = new Object[1];
            uidList[0] = tempMessageUid;

            r[0] = new FolderCommandReference(tempFolder, uidList);

            c.setTreeSelection(r);
            c.setTableSelection(r);

            MainInterface.processor.addOp(new ViewMessageCommand(c, r));

            //inline = true;
            //openInlineMessage(part, tempFile);
        } else {
            //inline = false;
            MimeTypeViewer viewer = new MimeTypeViewer();
            viewer.open(header, tempFile);
        }
    }

    /**
     * @see org.columba.core.command.Command#execute(Worker)
     */
    public void execute(WorkerStatusController worker) throws Exception {
        FolderCommandReference[] r = (FolderCommandReference[]) getReferences();
        MessageFolder folder = (MessageFolder) r[0].getFolder();
        Object[] uids = r[0].getUids();

        Integer[] address = r[0].getAddress();

        header = folder.getMimePartTree(uids[0]).getFromAddress(address).getHeader();
        
        InputStream bodyStream = folder.getMimePartBodyStream(uids[0], address);

        
        if (header.getMimeType().getType().equals("message")) {

            tempFolder = MailInterface.treeModel.getTempFolder();
            try {
                tempMessageUid = tempFolder.addMessage(bodyStream);
            } catch (Exception e) {
                LOG.warning("Could not create temporary email from the attachment.");
            }
            inline = true;

        } else {

            String filename = header.getFileName();
            if (filename != null) {
                tempFile = TempFileStore.createTempFile(filename);
            } else {
                tempFile = TempFileStore.createTempFile();
            }
            inline = false;

        	int encoding = header.getContentTransferEncoding();

            switch (encoding) {
                case MimeHeader.QUOTED_PRINTABLE:
                    bodyStream = new QuotedPrintableDecoderInputStream(bodyStream);
                    break;

                case MimeHeader.BASE64:
                    bodyStream = new Base64DecoderInputStream(bodyStream);
                    break;
                default:
            }

            if (LOG.isLoggable(Level.FINE)) {
                LOG.fine("Storing the attachment to :" + tempFile);
            }

            FileOutputStream fileStream = new FileOutputStream(tempFile);
            StreamUtils.streamCopy(bodyStream, fileStream);
            fileStream.close();
            bodyStream.close();
        }
    }
    
    
    /** {@inheritDoc} */
    protected File getDestinationFile(MimeHeader header) {
        return null;
    }
}