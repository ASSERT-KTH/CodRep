package org.eclipse.ecf.internal.example.collab.start;

/****************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Composent, Inc. - initial API and implementation
 *****************************************************************************/
package org.eclipse.ecf.example.collab.start;

import java.util.ArrayList;
import java.util.Collection;
import java.util.Iterator;
import org.eclipse.jface.dialogs.IDialogConstants;
import org.eclipse.jface.preference.FieldEditor;
import org.eclipse.jface.resource.JFaceResources;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.DisposeEvent;
import org.eclipse.swt.events.DisposeListener;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.events.SelectionListener;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.List;
import org.eclipse.swt.widgets.Widget;

public class URLListFieldEditor extends FieldEditor {

	private List list;
    private SelectionListener selectionListener;
    private Button removeButton;
    private Composite buttonBox;

    private java.util.List removedConnectionDetails = new ArrayList();
    
    public URLListFieldEditor(String name, String labelText, Composite parent) {
    	init(name,labelText);
    	createControl(parent);
    }
    protected void adjustForNumColumns(int numColumns) {
        Control control = getLabelControl();
        if (control != null) ((GridData) control.getLayoutData()).horizontalSpan = numColumns;
        ((GridData) list.getLayoutData()).horizontalSpan = numColumns - 1;
    }
    protected void createControl(Composite parent) {
        GridLayout layout = new GridLayout();
        layout.numColumns = getNumberOfControls();
        layout.marginWidth = 0;
        layout.marginHeight = 0;
        layout.horizontalSpacing = HORIZONTAL_GAP;
        parent.setLayout(layout);
        doFillIntoGrid(parent, layout.numColumns);
    }

    protected void doFillIntoGrid(Composite parent, int numColumns) {
        Control control = getLabelControl(parent);
        GridData gd = new GridData();
        gd.horizontalSpan = numColumns;
        control.setLayoutData(gd);

        list = getListControl(parent);
        gd = new GridData(GridData.FILL_HORIZONTAL);
        gd.verticalAlignment = GridData.FILL;
        gd.horizontalSpan = numColumns - 1;
        gd.grabExcessHorizontalSpace = true;
        list.setLayoutData(gd);

        buttonBox = getButtonBoxControl(parent);
        gd = new GridData();
        gd.verticalAlignment = GridData.BEGINNING;
        buttonBox.setLayoutData(gd);
    }

    public Composite getButtonBoxControl(Composite parent) {
        if (buttonBox == null) {
            buttonBox = new Composite(parent, SWT.NULL);
            GridLayout layout = new GridLayout();
            layout.marginWidth = 0;
            buttonBox.setLayout(layout);
            createButtons(buttonBox);
            buttonBox.addDisposeListener(new DisposeListener() {
                public void widgetDisposed(DisposeEvent event) {
                    removeButton = null;
                    buttonBox = null;
                }
            });

        } else {
            checkParent(buttonBox, parent);
        }

        selectionChanged();
        return buttonBox;
    }

    private void createButtons(Composite box) {
        removeButton = createPushButton(box, "Remove");
    }

    private Button createPushButton(Composite parent, String key) {
        Button button = new Button(parent, SWT.PUSH);
        button.setText(JFaceResources.getString(key));
        button.setFont(parent.getFont());
        GridData data = new GridData(GridData.FILL_HORIZONTAL);
        int widthHint = convertHorizontalDLUsToPixels(button,
                IDialogConstants.BUTTON_WIDTH);
        data.widthHint = Math.max(widthHint, button.computeSize(SWT.DEFAULT,
                SWT.DEFAULT, true).x);
        button.setLayoutData(data);
        button.addSelectionListener(getSelectionListener());
        return button;
    }

    public List getListControl(Composite parent) {
        if (list == null) {
            list = new List(parent, SWT.BORDER | SWT.SINGLE | SWT.V_SCROLL
                    | SWT.H_SCROLL);
            list.setFont(parent.getFont());
            list.addSelectionListener(getSelectionListener());
            list.addDisposeListener(new DisposeListener() {
                public void widgetDisposed(DisposeEvent event) {
                    list = null;
                }
            });
        } else {
            checkParent(list, parent);
        }
        return list;
    }

    private SelectionListener getSelectionListener() {
        if (selectionListener == null) {
			createSelectionListener();
		}
        return selectionListener;
    }

    public void createSelectionListener() {
        selectionListener = new SelectionAdapter() {
            public void widgetSelected(SelectionEvent event) {
                Widget widget = event.widget;
                if (widget == removeButton) {
                    removePressed();
                } else if (widget == list) {
                    selectionChanged();
                }
            }
        };
    }
    private void removePressed() {
        setPresentsDefaultValue(false);
        int index = list.getSelectionIndex();
        if (index >= 0) {
        	String key = list.getItem(index);
        	ConnectionDetails cd = (ConnectionDetails) list.getData(key);
        	removeConnectionDetails(cd);
            list.remove(index);           
            selectionChanged();
        }
    }
    private void removeConnectionDetails(ConnectionDetails cd) {
		removedConnectionDetails.add(cd);
	}
	private void selectionChanged() {

        int index = list.getSelectionIndex();
        removeButton.setEnabled(index >= 0);
    }


	protected void doLoad() {
		if (list != null) {
			AccountStart as = new AccountStart();
			as.loadConnectionDetailsFromPreferenceStore();
			Collection contents = as.getConnectionDetails();
			for(Iterator i=contents.iterator(); i.hasNext(); ) {
				ConnectionDetails cd = (ConnectionDetails) i.next();
				String uri = cd.getContainerType()+":"+cd.getTargetURI();
				list.add(uri);
				list.setData(uri,cd);
			}
		}
	}

	protected void doStore() {
		for(Iterator i=removedConnectionDetails.iterator(); i.hasNext(); ) {
			ConnectionDetails cd = (ConnectionDetails) i.next();
			AccountStart as = new AccountStart();
			as.removeConnectionDetails(cd);
		}
	}

    public int getNumberOfControls() {
        return 2;
    }
	protected void doLoadDefault() {
	}

}