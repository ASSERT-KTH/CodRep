new FolderOptionsDialog((MessageFolder) folder,true,

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
package org.columba.mail.gui.tree.action;

import org.columba.core.action.AbstractColumbaAction;
import org.columba.core.gui.frame.FrameMediator;
import org.columba.core.gui.selection.SelectionChangedEvent;
import org.columba.core.gui.selection.SelectionListener;
import org.columba.core.gui.util.ImageLoader;

import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.folder.MessageFolder;
import org.columba.mail.folder.AbstractFolder;
import org.columba.mail.gui.config.folder.FolderOptionsDialog;
import org.columba.mail.gui.frame.AbstractMailFrameController;
import org.columba.mail.gui.frame.MailFrameMediator;
import org.columba.mail.gui.tree.selection.TreeSelectionChangedEvent;
import org.columba.mail.util.MailResourceLoader;

import java.awt.event.ActionEvent;


/**
 * Opens MessageFolder Options Dialog.
 *
 * @author fdietz
 */
public class FolderOptionsAction extends AbstractColumbaAction
    implements SelectionListener {
    /**
 * @param frameMediator
 * @param name
 */
    public FolderOptionsAction(FrameMediator frameMediator) {
        super(frameMediator,
            MailResourceLoader.getString("menu", "mainframe",
                "menu_folder_folderoptions"));

        // icon for menu
        putValue(SMALL_ICON,
            ImageLoader.getSmallImageIcon("16_configure_folder.png"));

        setEnabled(false);

        ((MailFrameMediator) frameMediator).registerTreeSelectionListener(this);
    }

    /* (non-Javadoc)
 * @see java.awt.event.ActionListener#actionPerformed(java.awt.event.ActionEvent)
 */
    public void actionPerformed(ActionEvent evt) {
        // it is safe here to cast to AbstractMailFrameControlller
        FolderCommandReference[] r = (FolderCommandReference[]) ((AbstractMailFrameController) frameMediator).getTreeSelection();

        // only use the first selected folder		
        AbstractFolder folder = r[0].getFolder();

        // cast to Folder
        new FolderOptionsDialog((MessageFolder) folder,
            (AbstractMailFrameController) frameMediator);
    }

    public void selectionChanged(SelectionChangedEvent e) {
        AbstractFolder[] r = ((TreeSelectionChangedEvent) e).getSelected();

        if ((r.length > 0) && r[0] instanceof MessageFolder) {
            setEnabled(true);
        } else {
            setEnabled(false);
        }
    }
}