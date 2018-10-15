import org.eclipse.jst.ws.jaxws.core.utils.WSDLUtils;

/*******************************************************************************
 * Copyright (c) 2008 IONA Technologies PLC
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 * IONA Technologies PLC - initial API and implementation
 *******************************************************************************/
package org.eclipse.jst.ws.internal.cxf.ui.viewers;

import java.util.Map;

import org.eclipse.jface.viewers.CellEditor;
import org.eclipse.jface.viewers.EditingSupport;
import org.eclipse.jface.viewers.TableViewer;
import org.eclipse.jst.ws.internal.cxf.core.model.WSDL2JavaDataModel;
import org.eclipse.jst.ws.internal.cxf.core.utils.WSDLUtils;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.events.SelectionListener;
import org.eclipse.swt.widgets.Table;
import org.eclipse.swt.widgets.TableItem;

/**
 * @author sclarke
 */
public class PackageNameEditingSupport extends EditingSupport implements SelectionListener {
    private CellEditor packageNameCellEditor;
    private Table table;
    private Map<String, String> includedNamespaces;

    public PackageNameEditingSupport(TableViewer tableViewer, CellEditor packageNameCellEditor,
            WSDL2JavaDataModel model) {
        super(tableViewer);
        this.table = tableViewer.getTable();
        this.packageNameCellEditor = packageNameCellEditor;
        includedNamespaces = model.getIncludedNamespaces();
        table.addSelectionListener(this);
    }

    @Override
    protected boolean canEdit(Object element) {
        return table.getSelection()[0].getChecked();
    }

    @Override
    protected CellEditor getCellEditor(Object element) {
        return packageNameCellEditor;
    }

    @Override
    protected Object getValue(Object element) {
        if (includedNamespaces.containsKey(element.toString())) {
            return includedNamespaces.get(element.toString());
        }
        return WSDLUtils.getPackageNameFromNamespace(element.toString());
    }

    @Override
    protected void setValue(Object namespace, Object packageName) {
        if (namespace != null && packageName != null) {
            includedNamespaces.put(namespace.toString(), packageName.toString());
            getViewer().update(namespace, null);
        }
    }

    public void widgetSelected(SelectionEvent event) {
        if (event.detail == SWT.CHECK) {
            TableItem item = (TableItem) event.item;
            String namespaceKey = item.getText(0);
            String packageName = item.getText(1);
            if (item.getChecked()) {
                if (!includedNamespaces.containsKey(namespaceKey)) {
                    includedNamespaces.put(namespaceKey, packageName);
                }
            } else {
                if (includedNamespaces.containsKey(namespaceKey)) {
                    includedNamespaces.remove(namespaceKey);
                }
            }
        }
    }

    public void widgetDefaultSelected(SelectionEvent event) {
    }

}