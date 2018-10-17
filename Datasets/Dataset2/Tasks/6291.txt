viewHeaderListAction = new ViewHeaderListAction(t.getFrameController());

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

import org.columba.mail.gui.tree.action.ViewHeaderListAction;

import java.awt.Point;
import java.awt.event.InputEvent;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;

import javax.swing.JPopupMenu;
import javax.swing.tree.TreePath;


public class FolderTreeMouseListener extends MouseAdapter {
    private TreeController treeController;
    private ViewHeaderListAction viewHeaderListAction;

    public FolderTreeMouseListener(TreeController t) {
        this.treeController = t;
        viewHeaderListAction = new ViewHeaderListAction(t.getMailFrameController());
    }

    protected JPopupMenu getPopupMenu() {
        return treeController.getPopupMenu();
    }

    // Use PopUpTrigger in both mousePressed and mouseReleasedMethods due to
    // different handling of *nix and windows
    public void mousePressed(MouseEvent e) {
        maybeShowPopup(e);
    }

    public void mouseReleased(MouseEvent e) {
        maybeShowPopup(e);
    }

    public void mouseClicked(MouseEvent event) {
        //if ( SwingUtilities.isLeftMouseButton(event) ) treeController.selectFolder();
        if (event.getModifiers() == InputEvent.BUTTON1_MASK) {
            viewHeaderListAction.actionPerformed(null);
        }

        /*
if ( e.getClickCount() == 1 )
{
    treeController.selectFolder();
}
else if ( e.getClickCount() == 2 )
{
    treeController.expandImapRootFolder();
}
*/
    }

    private void maybeShowPopup(MouseEvent e) {
        if (e.isPopupTrigger()) {
            Point point = e.getPoint();
            TreePath path = treeController.getView().getClosestPathForLocation(point.x,
                    point.y);

            treeController.getView().clearSelection();
            treeController.getView().addSelectionPath(path);

            //treeController.getActionListener().changeActions();
            getPopupMenu().show(e.getComponent(), e.getX(), e.getY());
        }
    }
}