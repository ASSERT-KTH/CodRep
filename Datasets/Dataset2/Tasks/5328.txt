public boolean supportsAddFolder(IFolder newFolder) {

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

package org.columba.mail.folder;

import org.columba.mail.config.FolderItem;

/**
 * Top-level folder of all local folders.
 * <p>
 * Only purpose of this folder is to allow for a better structure
 * of the folder hierachy, where local and remote folders are
 * very easy to distinct.
 *
 *  @author fdietz
 */
public class LocalRootFolder extends AbstractFolder implements RootFolder {

    /**
 * Constructor
 * <p>
 * Due to limitations of the current plugin system, every folder
 * which is loaded dynamically needs to have the same constructor
 * behaviour.
 * <p>
 * I've added "String path" for this reason. (fdietz)
 * 
 */
    public LocalRootFolder(FolderItem item, String path) {
        super(item);
    }
    
    /* (non-Javadoc)
 * @see org.columba.mail.folder.RootFolder#getTrashFolder()
 */
    public AbstractFolder getTrashFolder() {
        return findChildWithUID(105, false);
    }

    /* (non-Javadoc)
 * @see org.columba.mail.folder.RootFolder#getInbox()
 */
    public AbstractFolder getInboxFolder() {
        return findChildWithUID(101, false);
    }

    /** {@inheritDoc} */
    public boolean supportsAddFolder(AbstractFolder newFolder) {
        return true;
    }
}