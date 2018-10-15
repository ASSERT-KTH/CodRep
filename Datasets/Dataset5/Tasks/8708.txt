package org.eclipse.ecf.internal.example.collab.ui;

/****************************************************************************
* Copyright (c) 2004 Composent, Inc. and others.
* All rights reserved. This program and the accompanying materials
* are made available under the terms of the Eclipse Public License v1.0
* which accompanies this distribution, and is available at
* http://www.eclipse.org/legal/epl-v10.html
*
* Contributors:
*    Composent, Inc. - initial API and implementation
*****************************************************************************/

package org.eclipse.ecf.example.collab.ui;

import java.io.File;

import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.example.collab.share.User;
import org.eclipse.swt.dnd.DND;
import org.eclipse.swt.dnd.DropTarget;
import org.eclipse.swt.dnd.DropTargetEvent;
import org.eclipse.swt.dnd.DropTargetListener;
import org.eclipse.swt.dnd.FileTransfer;
import org.eclipse.swt.dnd.TextTransfer;
import org.eclipse.swt.dnd.Transfer;
import org.eclipse.swt.widgets.Control;

class ChatDropTarget implements DropTargetListener {
    private final LineChatClientView view;
    DropTarget dropTarget = null;
    TextTransfer textTransfer = null;
    FileTransfer fileTransfer = null;
    ChatComposite composite = null;
    User selectedUser = null;
    public ChatDropTarget(LineChatClientView view, Control control, ChatComposite comp) {
        dropTarget = new DropTarget(control, DND.DROP_MOVE | DND.DROP_COPY
                | DND.DROP_DEFAULT);
        this.view = view;
        textTransfer = TextTransfer.getInstance();
        fileTransfer = FileTransfer.getInstance();
        Transfer[] types = new Transfer[] { fileTransfer, textTransfer };
        dropTarget.setTransfer(types);
        dropTarget.addDropListener(this);
        composite = comp;
    }
    public void dragEnter(DropTargetEvent event) {
        if (event.detail == DND.DROP_DEFAULT) {
            if ((event.operations & DND.DROP_COPY) != 0) {
                event.detail = DND.DROP_COPY;
            } else {
                event.detail = DND.DROP_NONE;
            }
        }
        // will accept text but prefer to have files dropped
        for (int i = 0; i < event.dataTypes.length; i++) {
            if (fileTransfer.isSupportedType(event.dataTypes[i])) {
                event.currentDataType = event.dataTypes[i];
                // files should only be copied
                if (event.detail != DND.DROP_COPY) {
                    event.detail = DND.DROP_NONE;
                }
                break;
            }
        }
    }
    public void dragOver(DropTargetEvent event) {
        event.feedback = DND.FEEDBACK_SELECT | DND.FEEDBACK_SCROLL;
    }
    public void dragOperationChanged(DropTargetEvent event) {
        if (event.detail == DND.DROP_DEFAULT) {
            if ((event.operations & DND.DROP_COPY) != 0) {
                event.detail = DND.DROP_COPY;
            } else {
                event.detail = DND.DROP_NONE;
            }
        }
        // allow text to be moved but files should only be copied
        if (fileTransfer.isSupportedType(event.currentDataType)) {
            if (event.detail != DND.DROP_COPY) {
                event.detail = DND.DROP_NONE;
            }
        }
    }
    public void dragLeave(DropTargetEvent event) {
    }
    public void dropAccept(DropTargetEvent event) {
    }
    public void drop(DropTargetEvent event) {
        if (fileTransfer.isSupportedType(event.currentDataType)) {
            String[] files = (String[]) event.data;
            for (int i = 0; i < files.length; i++) {
                ID target = (selectedUser == null) ? null : selectedUser
                        .getUserID();
                // Send file to user
                File file = new File(files[i]);
                if (file.exists() && !file.isDirectory()
                        && composite != null) {
                    composite.sendFile(file.getPath(), this.view.downloaddir
                            + File.separatorChar + file.getName(), null, target,false);
                    
                }
            }
        }
    }
}
 No newline at end of file