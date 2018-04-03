import org.columba.api.gui.frame.IFrameMediator;

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
package org.columba.addressbook.gui.frame;

import javax.swing.event.ListSelectionListener;
import javax.swing.event.TreeSelectionListener;

import org.columba.addressbook.gui.table.TableController;
import org.columba.addressbook.gui.tree.TreeController;
import org.columba.core.gui.frame.IFrameMediator;


/**
 * Mediator responsible for managing subcomponent interaction.
 * 
 * @author fdietz
 */
public interface AddressbookFrameMediator extends IFrameMediator {
    /**
 * Get table controller.
 * 
 * @return                table controller
 */
    TableController getTable();

    /**
 * Add selection listener for table.
 * 
 * @param listener                selection listener
 */
    void addTableSelectionListener(ListSelectionListener listener);

    /**
 * Get tree controller.
 * 
 * @return                tree controller
 */
    TreeController getTree();

    /**
 * Add selection listener for tree.
 * 
 * @param listener                selection listener
 */
    void addTreeSelectionListener(TreeSelectionListener listener);
}