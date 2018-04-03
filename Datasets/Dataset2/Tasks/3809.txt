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
package org.columba.mail.gui.composer;

import javax.swing.JMenuItem;
import javax.swing.JPopupMenu;

import org.columba.core.gui.util.ImageLoader;


/**
 * Popup menu for the attachment view.
 *
 * @author frdietz
 */
public class AttachmentMenu extends JPopupMenu {
    private JMenuItem menuItem;
    private AttachmentController controller;

    /**
     * Creates a popup menu for the attachment view.
     * @param c the attachment controller.
     */
    public AttachmentMenu(AttachmentController c) {
        super();

        this.controller = c;

        initComponents(c);
    }

    /**
     * Inits the components for the popup menu.
     * @param c the attachment controller.
     */
    private void initComponents(AttachmentController c) {
        menuItem = new JMenuItem("Attach File..",
                ImageLoader.getSmallImageIcon("stock_attach-16.png"));
        menuItem.setActionCommand("ADD");
        menuItem.addActionListener(c.getActionListener());
        add(menuItem);
        addSeparator();
        menuItem = new JMenuItem("Remove Selected Attachments",
                ImageLoader.getSmallImageIcon("stock_delete-16.png"));
        menuItem.setActionCommand("REMOVE");
        menuItem.addActionListener(c.getActionListener());
        add(menuItem);
    }
}