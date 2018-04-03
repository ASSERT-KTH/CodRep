model = AddressbookTreeModel.getInstance();

// The contents of this file are subject to the Mozilla Public License Version
// 1.1
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
//The Initial Developers of the Original Code are Frederik Dietz and Timo
// Stich.
//Portions created by Frederik Dietz and Timo Stich are Copyright (C) 2003.
//
//All Rights Reserved.
package org.columba.addressbook.gui.tree;

import javax.swing.JTree;
import javax.swing.ListSelectionModel;

import org.columba.addressbook.folder.AbstractFolder;
import org.columba.addressbook.gui.frame.AddressbookFrameController;
import org.columba.addressbook.gui.tree.util.AddressbookTreeCellRenderer;
import org.columba.addressbook.main.AddressbookInterface;


/**
 * Custom JTree using an appropriate model and renderer.
 *
 * @author fdietz
 */
public class TreeView extends JTree {
    private AddressbookTreeNode root;
    private AddressbookTreeModel model;
    protected AddressbookFrameController frameController;

    public TreeView(AddressbookFrameController frameController) {
        this.frameController = frameController;

        model = AddressbookInterface.addressbookTreeModel;

        setModel(model);

        setShowsRootHandles(true);
        setRootVisible(false);
        expandRow(0);
        
        getSelectionModel().setSelectionMode(ListSelectionModel.SINGLE_SELECTION);

        setCellRenderer(new AddressbookTreeCellRenderer(true));
    }

    public AbstractFolder getRootFolder() {
        return (AbstractFolder) model.getRoot();
    }

    public void removeAll() {
        root.removeAllChildren();
    }

    /**
     * @return FrameController
     */
    public AddressbookFrameController getFrameController() {
        return frameController;
    }
}