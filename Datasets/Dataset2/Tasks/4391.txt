public class Root extends AbstractFolder {

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

import org.columba.addressbook.config.AdapterNode;

import org.columba.core.xml.XmlElement;

import org.columba.mail.config.FolderItem;


/**
 * Root treenode, is actually not visible and only needed by
 * the inner structure of Columba.
 * <p>
 * Its only used to have a determined root.
 *
 * @author Timo Stich (tstich@users.sourceforge.net)
 */
public class Root extends FolderTreeNode {
    FolderItem item;

    public Root(XmlElement node) {
        super(new FolderItem(node));
    }

    /**
 * @see org.columba.modules.mail.folder.FolderTreeNode#instanceNewChildNode(AdapterNode, FolderItem)
 */
    public String getDefaultChild() {
        return null;
    }

    /* (non-Javadoc)
 * @see org.columba.mail.folder.FolderTreeNode#getName()
 */
    public String getName() {
        return "Root";
    }
}