public ImageIcon getIcon() {

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
package org.columba.addressbook.folder;

import javax.swing.ImageIcon;

import org.columba.addressbook.config.FolderItem;
import org.columba.api.command.IWorkerStatusController;
import org.columba.core.resourceloader.IconKeys;
import org.columba.core.resourceloader.ImageLoader;


/**
 * Top-level folder for remote folders.
 * 
 * @author fdietz
 */
public class RemoteRootFolder extends AddressbookTreeNode {
    ImageIcon remoteIcon = ImageLoader.getSmallIcon(IconKeys.SERVER);

    /**
 * Constructor for RemoteRootFolder.
 * @param item
 */
    public RemoteRootFolder(FolderItem item) {
        super(item);
    }

    /**
 * @see org.columba.addressbook.folder.AddressbookTreeNode#createChildren(org.columba.api.command.IWorkerStatusController)
 */
    public void createChildren(IWorkerStatusController worker) {
    }

    public ImageIcon getCollapsedIcon() {
        return remoteIcon;
    }
}