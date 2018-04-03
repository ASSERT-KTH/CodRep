import org.columba.core.filter.Filter;

/*
 * Created on 2003-nov-08
 */
package org.columba.mail.gui.config.filter;

import java.awt.Component;
import java.awt.datatransfer.DataFlavor;
import java.awt.datatransfer.Transferable;

import javax.swing.JComponent;
import javax.swing.JScrollPane;
import javax.swing.TransferHandler;

import org.columba.core.facade.DialogFacade;
import org.columba.mail.filter.Filter;


/**
 * A <code>TransferHandler</code> that handles the transfering of filters between two filter dialogs.
 * <p>
 * Note that the transfer handler will only allow to move filters within a component, whereas
 * it is possible to either move or copy filters between two different components.
 *
 * @author Erik Mattsson
 */
public class FilterTransferHandler extends TransferHandler {
    private JComponent transferSource;

    /**
 * Creates a FilterTransferHandler.
 * @param src the source component.
 */
    public FilterTransferHandler(JComponent src) {
        transferSource = src;
    }

    /** {@inheritDoc} */
    public boolean canImport(JComponent comp, DataFlavor[] transferFlavors) {
        boolean canHandleOneOfDataFlavors = false;

        if (canHandleImport(comp)) {
            for (int k = 0;
                    (k < transferFlavors.length) ||
                    (!canHandleOneOfDataFlavors); k++) {
                if (transferFlavors[k].equals(ObjectArrayTransfer.FLAVOR)) {
                    canHandleOneOfDataFlavors = true;
                }
            }
        }

        return canHandleOneOfDataFlavors;
    }

    /** {@inheritDoc} */
    protected Transferable createTransferable(JComponent c) {
        if (!canHandleExport(c)) {
            return null;
        }

        Transferable transferable = null;
        FilterListTable filterTable = getFilterListTable(c);

        if (filterTable != null) {
            FilterListDataModel model = (FilterListDataModel) filterTable.getModel();

            int[] selectedRows = filterTable.getSelectedRows();
            Object[] selectedFilters = new Object[selectedRows.length];

            for (int i = 0; i < selectedFilters.length; i++) {
                selectedFilters[i] = model.getFilter(selectedRows[i]).clone();
            }

            transferable = new ObjectArrayTransfer(filterTable, selectedFilters);
        }

        return transferable;
    }

    /** {@inheritDoc} */
    protected void exportDone(JComponent source, Transferable data, int action) {
        if (!canHandleExport(source)) {
            return;
        }

        if (!((action == COPY_OR_MOVE) || (action == MOVE))) {
            return;
        }

        FilterListTable list = getFilterListTable(source);

        if (list != null) {
            try {
                Object transferable = data.getTransferData(ObjectArrayTransfer.FLAVOR);

                if (!(transferable instanceof ObjectArrayTransfer)) {
                    return;
                }

                ObjectArrayTransfer arrayTransferable = (ObjectArrayTransfer) transferable;

                if (!source.equals(arrayTransferable.getSource())) {
                    return;
                }

                Object[] filters = arrayTransferable.getData();
                FilterListDataModel model = (FilterListDataModel) list.getModel();

                for (int i = 0; i < filters.length; i++) {
                    model.removeFilter((Filter) filters[i]);
                }
            } catch (Exception e) {
                DialogFacade.showExceptionDialog(e);
            }
        }
    }

    /**
 * Returns the source actions that the specified component can handle.
 * If the source component is the same as the specified component, then there
 * should only be possible to move the filter not copy it.
 * {@inheritDoc} */
    public int getSourceActions(JComponent c) {
        /*if ( c == transferSource )
        return MOVE;
*/
        if (canHandleImport(c)) {
            return COPY_OR_MOVE;
        } else {
            return NONE;
        }
    }

    /** {@inheritDoc} */
    public boolean importData(JComponent comp, Transferable t) {
        if (!canHandleImport(comp)) {
            return false;
        }

        FilterListTable list = getFilterListTable(comp);

        if (list != null) {
            FilterListDataModel model = (FilterListDataModel) list.getModel();

            try {
                Object obj = t.getTransferData(ObjectArrayTransfer.FLAVOR);

                if (!(obj instanceof ObjectArrayTransfer)) {
                    return false;
                }

                ObjectArrayTransfer at = (ObjectArrayTransfer) obj;
                Object[] filters = at.getData();

                // block transfer to self!
                if (comp.equals(at.getSource())) {
                    return false;
                }

                // if it is in a table, then we need to insert it at the selected position.
                if (comp instanceof FilterListTable) {
                    int selectedRow = list.getSelectedRow();

                    int i;

                    for (i = (filters.length - 1); i >= 0; i--) {
                        model.insertFilter((Filter) filters[i], selectedRow);
                    }

                    list.getSelectionModel().clearSelection();
                }
                // if it is in a scroll pane, then we add to the end of the list.
                else if (comp instanceof JScrollPane) {
                    for (int i = 0; i < filters.length; i++) {
                        model.addFilter((Filter) filters[i]);
                    }
                }
            } catch (Exception e) {
                DialogFacade.showExceptionDialog(e);
            }
        }

        return true;
    }

    /**
 * Returns true if this handler can import data from the specified component.
 * @param component the component that is exporting the data.
 * @return true if this handler can import data from the specified component.
 */
    private boolean canHandleImport(JComponent component) {
        return ((component instanceof FilterListTable) ||
        (component instanceof JScrollPane));
    }

    /**
 * Returns true if this handler can export data to the specified component.
 * @param component the component that is importing the data.
 * @return true if this handler can export data to the specified component.
 */
    private boolean canHandleExport(JComponent component) {
        return (component instanceof FilterListTable);
    }

    /**
 * Returns the <code>FilterListTable</code> from the component.
 * This is a utility method to simplify the retrieving of a FilterListTable.
 * Since the table and the JScollPane is a valid importer, then we need a
 * method that returns the table when adding filters to it.
 * @param comp a JComponent that either is a <code>JScrollPane</code> or a <code>FilterListTable</code>
 * @return a FilterListTable; or null if the component doesnt contain a <code>FilterListTable</code>.
 */
    private FilterListTable getFilterListTable(JComponent comp) {
        Component tableComponent = null;

        if (comp instanceof JScrollPane) {
            tableComponent = ((JScrollPane) comp).getViewport().getView();
        } else if (comp instanceof FilterListTable) {
            tableComponent = comp;
        }

        return (FilterListTable) tableComponent;
    }
}