ColumbaLogger.log.info("item=" + item.toString());

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

import org.columba.addressbook.folder.HeaderItem;
import org.columba.addressbook.folder.HeaderItemList;
import org.columba.addressbook.gui.table.AddressbookTableModel;
import org.columba.addressbook.gui.util.HeaderItemDNDManager;
import org.columba.addressbook.parser.AddressParser;

import org.columba.core.gui.focus.FocusOwner;
import org.columba.core.gui.util.NotifyDialog;
import org.columba.core.logging.ColumbaLogger;
import org.columba.core.main.MainInterface;

import org.columba.mail.util.MailResourceLoader;

import java.awt.dnd.DnDConstants;
import java.awt.dnd.DropTarget;
import java.awt.dnd.DropTargetDragEvent;
import java.awt.dnd.DropTargetDropEvent;
import java.awt.dnd.DropTargetEvent;
import java.awt.dnd.DropTargetListener;

import java.util.Iterator;
import java.util.List;

import javax.swing.JComponent;
import javax.swing.event.TableModelEvent;
import javax.swing.event.TableModelListener;


/**
 * @author frd
 *
 * To change this generated comment edit the template variable "typecomment":
 * Window>Preferences>Java>Templates.
 * To enable and disable the creation of type comments go to
 * Window>Preferences>Java>Code Generation.
 */
public class HeaderController implements TableModelListener, DropTargetListener,
    FocusOwner {
    ComposerController controller;
    HeaderView view;
    DropTarget dropTarget = null;
    DropTarget dropTarget2 = null;
    boolean acceptDrop = true;

    public HeaderController(ComposerController controller) {
        this.controller = controller;

        view = new HeaderView(this);

        //view.getTable().addKeyListener(this);
        // register at focus manager
        MainInterface.focusManager.registerComponent(this);

        dropTarget = new DropTarget(view.getTable(), this);
        dropTarget2 = new DropTarget(view, this);

        appendRow();
    }

    public boolean checkState() {
        int count = view.getTable().getRowCount();

        for (int i = 0; i < count; i++) {
            HeaderItem item = getAddressbookTableModel().getHeaderItem(i);

            if (isValid(item)) {
                return true;
            }
        }

        System.out.println("no recipient");

        NotifyDialog dialog = new NotifyDialog();
        dialog.showDialog(MailResourceLoader.getString("menu", "mainframe",
                "composer_no_recipients_found")); //$NON-NLS-1$

        return false;
    }

    protected boolean isValid(HeaderItem headerItem) {
        if (headerItem.isContact()) {
            String address = (String) headerItem.get("email;internet");

            if (AddressParser.isValid(address)) {
                return true;
            }

            address = (String) headerItem.get("displayname");

            if (AddressParser.isValid(address)) {
                return true;
            }
        } else {
            return true;
        }

        return false;
    }

    public AddressbookTableModel getAddressbookTableModel() {
        return view.getAddressbookTableModel();
    }

    public void installListener() {
        //view.table.getModel().addTableModelListener(this);
    }

    public void appendRow() {
        view.getTable().appendRow();
    }

    public void editLastRow() {
        view.getTable().editLastRow();
    }

    public void cleanupHeaderItemList() {
        view.getTable().cleanupHeaderItemList();
    }

    protected void addVectorToTable(List v, int index) {
        for (Iterator it = v.iterator(); it.hasNext();) {
            try {
                HeaderItem item = (HeaderItem) it.next();

                //		for (int i = 0; i < v.size(); i++) {
                //			try {
                //				
                //				HeaderItem item = (HeaderItem) v.get(i);
                ColumbaLogger.log.debug("item=" + item.toString());

                String field = (String) item.get("field");

                if (field == null) {
                    String str = "";

                    if (index == 0) {
                        str = "To";
                    } else if (index == 1) {
                        str = "Cc";
                    } else if (index == 2) {
                        str = "Bcc";
                    }

                    item.add("field", str);
                }

                view.getAddressbookTableModel().addItem(item);
            } catch (Exception ex) {
                ex.printStackTrace();
            }
        }
    }

    public void updateComponents(boolean b) {
        if (b) {
            view.getAddressbookTableModel().setHeaderList(null);

            addVectorToTable(controller.getModel().getToList(), 0);

            addVectorToTable(controller.getModel().getCcList(), 1);

            addVectorToTable(controller.getModel().getBccList(), 2);

            appendRow();
        } else {
            controller.getModel().getToList().clear();
            controller.getModel().getToList().clear();
            controller.getModel().getToList().clear();

            for (int i = 0; i < view.table.getRowCount(); i++) {
                HeaderItem item = (HeaderItem) view.getAddressbookTableModel()
                                                   .getHeaderItem(i);
                String field = (String) item.get("field");

                if (field == null) {
                    item.add("field", "To");
                    controller.getModel().getToList().add(item);

                    continue;
                }

                if (field.equals("To")) {
                    controller.getModel().getToList().add(item);
                } else if (field.equals("Cc")) {
                    controller.getModel().getCcList().add(item);
                } else if (field.equals("Bcc")) {
                    controller.getModel().getBccList().add(item);
                }
            }
        }
    }

    public HeaderItemList[] getHeaderItemLists() {
        HeaderItemList[] lists = new HeaderItemList[3];
        lists[0] = new HeaderItemList();
        lists[1] = new HeaderItemList();
        lists[2] = new HeaderItemList();

        for (int i = 0; i < view.table.getRowCount(); i++) {
            HeaderItem item = (HeaderItem) view.getAddressbookTableModel()
                                               .getHeaderItem(i);
            String field = (String) item.get("field");

            if (field == null) {
                item.add("field", "To");
                lists[0].add(item);

                continue;
            }

            if (field.equals("To")) {
                lists[0].add(item);
            } else if (field.equals("Cc")) {
                lists[1].add(item);
            } else if (field.equals("Bcc")) {
                lists[2].add(item);
            }
        }

        return lists;
    }

    public void setHeaderItemLists(HeaderItemList[] lists) {
        ((ComposerModel) controller.getModel()).setToList(lists[0].getVector());

        ((ComposerModel) controller.getModel()).setCcList(lists[1].getVector());

        ((ComposerModel) controller.getModel()).setBccList(lists[2].getVector());

        updateComponents(true);
    }

    public void tableChanged(TableModelEvent e) {
        /*
        int row = e.getFirstRow();
        int column = e.getColumn();
        String columnName = model.getColumnName(column);
        Object data = model.getValueAt(row, column);
        */
        /*
        ComposerModel model = controller.getModel();
        model.getToList().clear();
        model.getCcList().clear();
        model.getBccList().clear();

        for (int i = 0; i < view.table.getRowCount(); i++) {
                HeaderItem item =
                        (HeaderItem) view.getAddressbookTableModel().getHeaderItem(i);
                String field = (String) item.get("field");

                if (field.equals("To")) {
                        model.getToList().add(item);
                } else if (field.equals("Cc")) {
                        model.getCcList().add(item);
                } else if (field.equals("Bcc")) {
                        model.getBccList().add(item);
                }
        }

        */
    }

    public void removeSelected() {
        view.removeSelected();
    }

    /****************** Key Listener ****************************/

    /*
    public void keyPressed(KeyEvent k) {
            switch (k.getKeyCode()) {
                    case (KeyEvent.VK_DELETE) :
                            {
                                    if (view.count() > 1)
                                            removeSelected();
                                    break;
                            }
            }
    }

    public void keyReleased(KeyEvent k) {
    }
    public void keyTyped(KeyEvent k) {
    }
    */

    /***************************** DND *****************************/
    public void dragEnter(DropTargetDragEvent event) {
        // debug messages for diagnostics
        if (acceptDrop) {
            event.acceptDrag(DnDConstants.ACTION_COPY_OR_MOVE);
        } else {
            event.acceptDrag(DnDConstants.ACTION_COPY);
        }
    }

    public void dragExit(DropTargetEvent event) {
    }

    public void dragOver(DropTargetDragEvent event) {
    }

    public void drop(DropTargetDropEvent event) {
        if (!acceptDrop) {
            event.rejectDrop();

            //clearSelection();
            return;
        }

        System.out.println("dropping contact");

        HeaderItem[] items = HeaderItemDNDManager.getInstance()
                                                 .getHeaderItemList();

        //view.requestFocus();
        int row = view.getTable().getEditingRow();
        int column = view.getTable().getEditingColumn();
        System.out.println("row=" + row + " column=" + column);

        if ((row != -1) && (column != -1)) {
            view.getTable().getCellEditor(row, column).stopCellEditing();
            view.getTable().clearSelection();
            view.getTable().requestFocus();
        }

        cleanupHeaderItemList();

        for (int i = 0; i < items.length; i++) {
            try {
                HeaderItem item = (HeaderItem) items[i].clone();

                item.add("field", "To");
                System.out.println("add dnd contact:" +
                    (String) item.get("displayname"));
                getAddressbookTableModel().addItem(item);
            } catch (Exception ex) {
                ex.printStackTrace();
            }
        }

        event.getDropTargetContext().dropComplete(true);

        view.getTable().appendRow();
    }

    public void dropActionChanged(DropTargetDragEvent event) {
    }

    /* (non-Javadoc)
     * @see org.columba.core.gui.focus.FocusOwner#copy()
     */

    /***************** FocusOwner implementation ***************************/
    public void copy() {
        // not supported by gui component
    }

    public void cut() {
        view.removeSelected();
    }

    public void delete() {
        view.removeSelected();
    }

    public JComponent getComponent() {
        return view.getTable();
    }

    public boolean isCopyActionEnabled() {
        // not supported by gui component
        return false;
    }

    public boolean isCutActionEnabled() {
        if (view.getSelectedCount() > 0) {
            return true;
        }

        return false;
    }

    public boolean isDeleteActionEnabled() {
        if (view.getSelectedCount() > 0) {
            return true;
        }

        return false;
    }

    public boolean isPasteActionEnabled() {
        // not supported by gui component
        return false;
    }

    public boolean isRedoActionEnabled() {
        // not supported by gui component
        return false;
    }

    public boolean isSelectAllActionEnabled() {
        return true;
    }

    public boolean isUndoActionEnabled() {
        // not supported by gui component
        return false;
    }

    public void paste() {
        // not supported by gui component
    }

    public void redo() {
        // not supported by gui component
    }

    public void selectAll() {
        view.getTable().selectAll();
    }

    public void undo() {
        // not supported by gui component
    }
}