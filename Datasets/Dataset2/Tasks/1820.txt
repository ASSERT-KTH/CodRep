import org.columba.core.pluginhandler.ViewPluginHandler;

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
package org.columba.addressbook.gui.frame;

import org.columba.addressbook.gui.table.TableController;
import org.columba.addressbook.gui.tree.TreeController;

import org.columba.core.config.ViewItem;
import org.columba.core.gui.frame.AbstractFrameController;
import org.columba.core.gui.util.NotifyDialog;
import org.columba.core.gui.view.AbstractView;
import org.columba.core.main.MainInterface;
import org.columba.core.plugin.PluginHandlerNotFoundException;
import org.columba.core.plugin.ViewPluginHandler;
import org.columba.core.xml.XmlElement;

import javax.swing.event.ListSelectionListener;
import javax.swing.event.TreeSelectionListener;


/**
 * @author Timo Stich (tstich@users.sourceforge.net)
 *  
 */
public class AddressbookFrameController extends AbstractFrameController
    implements AddressbookFrameMediator {
    
    protected AbstractAddressbookView view;
    protected TreeController tree;
    protected TableController table;

    /**
 * Constructor for AddressbookController.
 */
    public AddressbookFrameController(ViewItem viewItem) {
        super("Addressbook", viewItem);
    }

    /**
 * @see org.columba.core.gui.FrameController#createView()
 */
    protected AbstractView createView() {
        //AddressbookFrameView view = new AddressbookFrameView(this);
        // Load "plugin" view instead
        ViewPluginHandler handler = null;

        try {
            handler = (ViewPluginHandler) MainInterface.pluginManager.getHandler(
                    "org.columba.core.view");
        } catch (PluginHandlerNotFoundException ex) {
            NotifyDialog d = new NotifyDialog();
            d.showDialog(ex);
        }

        // get view using the plugin handler found above
        Object[] args = {this};

        try {
            view = (AbstractAddressbookView) handler.getPlugin(
                getViewItem().getRoot().getAttribute("frame", id), args);
        } catch (Exception ex) {
            ex.printStackTrace();
        }

        view.init(tree.getView(), table.getView());

        view.getFrame().pack();

        view.getFrame().setVisible(true);

        return view;
    }

    /**
 * @see org.columba.core.gui.FrameController#init()
 */
    protected void init() {
        tree = new TreeController(this);
        table = new TableController(this);

        // table should be updated when tree selection changes
        tree.getView().addTreeSelectionListener(table);
    }

    /**
 * @see org.columba.core.gui.FrameController#initInternActions()
 */
    protected void initInternActions() {
    }

    /**
 * @return AddressbookTableController
 */
    public TableController getTable() {
        return table;
    }

    /**
 * @return AddressbookTreeController
 */
    public TreeController getTree() {
        return tree;
    }

    /**
 * @see org.columba.addressbook.gui.frame.AddressbookFrameMediator#addTableSelectionListener(javax.swing.event.ListSelectionListener)
 */
    public void addTableSelectionListener(ListSelectionListener listener) {
        getTable().getView().getSelectionModel().addListSelectionListener(listener);
    }

    /**
 * @see org.columba.addressbook.gui.frame.AddressbookFrameMediator#addTreeSelectionListener(javax.swing.event.TreeSelectionListener)
 */
    public void addTreeSelectionListener(TreeSelectionListener listener) {
        getTree().getView().addTreeSelectionListener(listener);
    }
}