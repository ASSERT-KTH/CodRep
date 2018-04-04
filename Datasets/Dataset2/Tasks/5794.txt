private String selectedLeaf = "";

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
package org.columba.mail.gui.tree;

import org.columba.core.xml.XmlElement;

import org.columba.mail.config.FolderItem;
import org.columba.mail.folder.Folder;
import org.columba.mail.folder.FolderTreeNode;
import org.columba.mail.gui.frame.AbstractMailFrameController;

import javax.swing.BorderFactory;
import javax.swing.JTextField;
import javax.swing.ToolTipManager;
import javax.swing.tree.TreePath;


/**
 * this class does all the dirty work for the TreeController
 */
public class TreeView extends DndTree {
    private String selectedLeaf = new String();
    private JTextField textField;

    public TreeView(AbstractMailFrameController frameController, TreeModel model) {
        super(frameController, model);

        ToolTipManager.sharedInstance().registerComponent(this);

        putClientProperty("JTree.lineStyle", "Angled");

        setShowsRootHandles(true);
        setRootVisible(false);

        setBorder(BorderFactory.createEmptyBorder(2, 0, 2, 0));

        FolderTreeNode root = (FolderTreeNode) treeModel.getRoot();

        expand(root);

        repaint();
    }

    public Folder getSelected() {
        return null;
    }

    public void expand(FolderTreeNode parent) {
        // get configuration from tree.xml file
        FolderItem item = parent.getFolderItem();

        XmlElement property = item.getElement("property");

        if (property != null) {
            String expanded = property.getAttribute("expanded");

            if (expanded == null) {
                expanded = "true";
            }

            // expand folder 
            int row = getRowForPath(new TreePath(parent.getPath()));

            if (expanded.equals("true")) {
                expandRow(row);
            }
        }

        // recursivly expand all children
        for (int i = 0; i < parent.getChildCount(); i++) {
            FolderTreeNode child = (FolderTreeNode) parent.getChildAt(i);
            expand(child);
        }
    }
}