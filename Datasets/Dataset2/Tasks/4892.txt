import org.frapuccino.treetable.AbstractTreeTableModel;

/*
 * Created on 06.08.2003
 *
 * To change the template for this generated file go to
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
package org.columba.core.gui.plugin;

import javax.swing.tree.DefaultTreeModel;
import javax.swing.tree.TreePath;

import org.columba.core.plugin.PluginManager;
import org.frappucino.treetable.AbstractTreeTableModel;


/**
 * @author fdietz
 *
 * To change the template for this generated type comment go to
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
public class PluginTreeTableModel extends AbstractTreeTableModel {
    PluginNode root;

    /**
 * @param tree
 * @param columns
 */
    public PluginTreeTableModel(String[] columns) {
        super(columns);

        PluginNode root = new PluginNode();
        root.setId("root");
    }

    public Class getColumnClass(int c) {
        // first column is a tree
        if (c == 0) {
            return tree.getClass();
        }

        if (c == 1) {
            return String.class;
        } else {
            // third column is a JCheckBox column
            return Boolean.class;
        }
    }

    public Object getValueAt(int row, int col) {
        PluginNode node = (PluginNode) tree.getPathForRow(row)
                                           .getLastPathComponent();

        return node;
    }

    public void set(PluginNode root) {
        tree.setRootNode(root);

        ((DefaultTreeModel) tree.getModel()).nodeStructureChanged(root);

        fireTableDataChanged();
    }

    /* (non-Javadoc)
 * @see javax.swing.table.TableModel#setValueAt(java.lang.Object, int, int)
 */
    public void setValueAt(Object value, int row, int col) {
        if (col == 2) {
            // checkbox pressed
            TreePath path = tree.getPathForRow(row);
            PluginNode node = (PluginNode) path.getLastPathComponent();

            if (node.isCategory()) {
                return;
            }

            // enable/disable tree node
            node.setEnabled(((Boolean) value).booleanValue());

            // enable/disable plugin
            String id = node.getId();

            PluginManager.getInstance().setEnabled(id,
                ((Boolean) value).booleanValue());
        }
    }

    /* (non-Javadoc)
 * @see javax.swing.table.TableModel#isCellEditable(int, int)
 */
    public boolean isCellEditable(int row, int col) {
        // enabled/disabled checkbox must be editable
        if (col == 2) {
            return true;
        }

        // tree must be editable, otherwise you can't collapse/expand tree nodes
        if (col == 0) {
            return true;
        }

        return false;
    }
}