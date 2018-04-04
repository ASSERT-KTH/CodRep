import org.columba.core.resourceloader.ImageLoader;

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
package org.columba.mail.gui.config.subscribe;

import javax.swing.Icon;
import javax.swing.ImageIcon;

import org.columba.core.gui.util.ImageLoader;
import org.frapuccino.checkabletree.CheckableItemImpl;


public class ListInfoTreeNode extends CheckableItemImpl {
    protected final static ImageIcon collapsedIcon = ImageLoader.getSmallImageIcon(
            "folder-closed.png");
    protected final static ImageIcon expandedIcon = ImageLoader.getSmallImageIcon(
            "folder-open.png");
    private String mailbox;

    /**
 * 
 */
    public ListInfoTreeNode(String name, String mailbox) {
        super(name);
        this.mailbox = mailbox;
    }

    /**
 * @return Returns the mailbox.
 */
    public String getMailbox() {
        return mailbox;
    }

    /**
 * @param mailbox The mailbox to set.
 */
    public void setMailbox(String mailbox) {
        this.mailbox = mailbox;
    }

    /**
 * @see org.columba.core.gui.checkabletree.CheckableItem#getIcon()
 */
    public Icon getIcon() {
        return collapsedIcon;
    }
}