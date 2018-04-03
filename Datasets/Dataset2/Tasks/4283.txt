ColumbaLogger.log.info("saving folder: " + child.getName());

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
package org.columba.mail.shutdown;

import org.columba.core.backgroundtask.TaskInterface;
import org.columba.core.logging.ColumbaLogger;
import org.columba.core.main.MainInterface;

import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.folder.FolderTreeNode;
import org.columba.mail.folder.command.SaveFolderConfigurationCommand;
import org.columba.mail.main.MailInterface;

import java.util.Enumeration;


/**
 * @author freddy
 *
 * To change this generated comment edit the template variable "typecomment":
 * Window>Preferences>Java>Templates.
 * To enable and disable the creation of type comments go to
 * Window>Preferences>Java>Code Generation.
 */
public class SaveAllFoldersPlugin implements TaskInterface {
    public void run() {
        saveAllFolders();
    }

    public void saveAllFolders() {
        FolderTreeNode rootFolder = (FolderTreeNode) MailInterface.treeModel.getRoot();

        saveFolder(rootFolder);
    }

    public void saveFolder(FolderTreeNode parentFolder) {
        int count = parentFolder.getChildCount();
        FolderTreeNode child;
        FolderTreeNode folder;

        for (Enumeration e = parentFolder.children(); e.hasMoreElements();) {
            child = (FolderTreeNode) e.nextElement();

            FolderCommandReference[] r = new FolderCommandReference[1];
            r[0] = new FolderCommandReference(child);

            ColumbaLogger.log.debug("saving folder: " + child.getName());

            MainInterface.processor.addOp(new SaveFolderConfigurationCommand(r));

            saveFolder(child);
        }
    }
}