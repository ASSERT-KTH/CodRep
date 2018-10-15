if (element instanceof List<?>) {

/*******************************************************************************
 * Copyright (c) 2009 Shane Clarke.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Shane Clarke - initial API and implementation
 *******************************************************************************/
package org.eclipse.jst.ws.internal.jaxws.ui.views;

/**
 * @author sclarke
 */
import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.Map.Entry;

import org.eclipse.jdt.core.IAnnotation;
import org.eclipse.jdt.core.IMemberValuePair;
import org.eclipse.jdt.core.IType;
import org.eclipse.jdt.core.JavaModelException;
import org.eclipse.jdt.core.search.SearchEngine;
import org.eclipse.jdt.ui.IJavaElementSearchConstants;
import org.eclipse.jdt.ui.ISharedImages;
import org.eclipse.jdt.ui.JavaUI;
import org.eclipse.jface.dialogs.IDialogConstants;
import org.eclipse.jface.viewers.DialogCellEditor;
import org.eclipse.jface.viewers.ISelection;
import org.eclipse.jface.viewers.ISelectionChangedListener;
import org.eclipse.jface.viewers.IStructuredContentProvider;
import org.eclipse.jface.viewers.IStructuredSelection;
import org.eclipse.jface.viewers.LabelProvider;
import org.eclipse.jface.viewers.SelectionChangedEvent;
import org.eclipse.jface.viewers.StructuredSelection;
import org.eclipse.jface.viewers.TableViewer;
import org.eclipse.jface.viewers.Viewer;
import org.eclipse.jface.window.Window;
import org.eclipse.jst.ws.internal.jaxws.ui.JAXWSUIMessages;
import org.eclipse.jst.ws.internal.jaxws.ui.JAXWSUIPlugin;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.graphics.Image;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.swt.widgets.Table;
import org.eclipse.swt.widgets.Text;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.dialogs.SelectionDialog;
import org.eclipse.ui.dialogs.SelectionStatusDialog;

public class AnnotationArrayCellEditor extends DialogCellEditor {
    private Method method;
    private Object[] values;

    private List<Object> originalValues;
    private List<Object> updatedValues;

    private  AnnotationArrayDialog annotationArrayDialog;
    
    boolean cancelled;
    
    public AnnotationArrayCellEditor(Composite parent, Object[] values) {
        super(parent, SWT.NONE);
        this.values = values.clone();
    }

    @Override
    protected Object openDialogBox(Control cellEditorWindow) {
        annotationArrayDialog = new AnnotationArrayDialog(cellEditorWindow.getShell(), values);
        int returnValue = annotationArrayDialog.open();
        
        if (returnValue == Window.OK) {
            cancelled = false;
            return annotationArrayDialog.getResult();
        } if (returnValue == Window.CANCEL) {
            cancelled = true;
        }
        return values;
    }
    
    public void setMethod(Method method) {
        this.method = method;
    }
    
    @Override
    protected void updateContents(Object value) {
        if (value instanceof Object[]) {
            Object[] values = (Object[])value;
            if (values.length > 0) {
                getDefaultLabel().setText("[]{...}");     //$NON-NLS-1$
            } else {
                getDefaultLabel().setText("[]{}"); //$NON-NLS-1$
            }
        }
    }

    @Override
    protected Object doGetValue() {
        if (cancelled || updatedValues == null) {
            return originalValues != null ? originalValues.toArray() : new Object[0];
        }
        return updatedValues.toArray();
    }

    @Override
    protected void doSetValue(Object value) {
        super.doSetValue(value);
        this.values = (Object[])value;
    }

    private class AnnotationArrayDialog extends SelectionStatusDialog {
        private Button addButton;
        private Button removeButton;
        private Button upButton;
        private Button downButton;
        private Table arrayValuesTable;
        private TableViewer arrayValuesTableViewer;
        
        private Map<String, Control> controls = new HashMap<String, Control>();
                
        public AnnotationArrayDialog(Shell parent, Object[] values) {
            super(parent);
            setValues(values);
            setTitle(JAXWSUIMessages.ANNOTATION_ARRAY_CELL_EDITOR_EDIT_ARRAY_VALUES_TITLE);
        }

        private void setValues(Object[] values) {
            try {
                originalValues = new ArrayList<Object>();
                updatedValues = new ArrayList<Object>();
                for (Object value : values) {
                    if (value instanceof IAnnotation) {
                        IAnnotation annotation = (IAnnotation)value;
                        IMemberValuePair[] memberValuePairs = annotation.getMemberValuePairs();
                        if (memberValuePairs.length > 0) {
                            List<Map<String, Object>> aList = new ArrayList<Map<String,Object>>();
                            for (IMemberValuePair memberValuePair : memberValuePairs) {
                                String memberName = memberValuePair.getMemberName();
                                Object memberValue = memberValuePair.getValue();
                                Map<String, Object> mvps = new HashMap<String, Object>();
                                if (memberValuePair.getValueKind() == IMemberValuePair.K_STRING) {
                                    mvps.put(memberName, memberValue);
                                }

                                if (memberValuePair.getValueKind() == IMemberValuePair.K_CLASS) {
                                    mvps.put(memberName, memberValuePair.getValue() + ".class"); //$NON-NLS-1$
                                }
                                aList.add(mvps);
                            }
                            originalValues.add(aList);
                            updatedValues.add(aList);
                        }
                    }
                    if (value.equals(Class.class)) {
                        originalValues.add(value);
                        updatedValues.add(value);                        
                    }
                    if (value instanceof String) {
                        String string = (String)value;
                        originalValues.add(string);
                        updatedValues.add(string);
                    }
                }
            } catch (JavaModelException jme) {
                JAXWSUIPlugin.log(jme.getStatus());
            }
        }
        
        @Override
        protected Control createDialogArea(Composite parent) {
            Composite mainComposite = (Composite) super.createDialogArea(parent);
            
            GridLayout gridLayout = new GridLayout(3, false);
            mainComposite.setLayout(gridLayout);

            GridData gridData = new GridData(SWT.FILL, SWT.BEGINNING, false, false);
            gridData.widthHint = 800;
            mainComposite.setLayoutData(gridData);
            
            Composite typeComposite = new Composite(mainComposite, SWT.NONE);
            gridLayout = new GridLayout(3, false);
            typeComposite.setLayout(gridLayout);
            gridData = new GridData(SWT.FILL, SWT.BEGINNING, true, true);
            typeComposite.setLayoutData(gridData);
            
            final Class<?> componentType = method.getReturnType().getComponentType();
            if (componentType.isAnnotation()) {
                Label compontTypeLabel = new Label(typeComposite, SWT.NONE);
                compontTypeLabel.setText("@" + componentType.getName()); //$NON-NLS-1$
                gridData = new GridData(SWT.FILL, SWT.FILL, true, true);
                gridData.horizontalSpan = 3;
                compontTypeLabel.setLayoutData(gridData);

                Method[] methods = componentType.getDeclaredMethods();
                for (Method method : methods) {
                    Label label = new Label(typeComposite, SWT.NONE);
                    label.setText(method.getName() + ":"); //$NON-NLS-1$
                    createEntryFields(method, typeComposite);
                }
            } else {
                Label label = new Label(typeComposite, SWT.NONE);
                label.setText(componentType.getSimpleName());
                createEntryFields(method, typeComposite);
            }

            Composite buttonComposite = new Composite(mainComposite, SWT.NONE);
            gridLayout = new GridLayout(1, false);
            buttonComposite.setLayout(gridLayout);
            
            addButton = new Button(buttonComposite, SWT.PUSH);
            addButton.setText(JAXWSUIMessages.ANNOTATION_ARRAY_CELL_EDITOR_ADD_LABEL);
            addButton.addSelectionListener(new SelectionAdapter() {
                @Override
                public void widgetSelected(SelectionEvent event) {
                    Set<Entry<String, Control>> entrySet = controls.entrySet();
                    Iterator<Map.Entry<String, Control>> iterator = entrySet.iterator();
                    List<Map<String, Object>> aList = new ArrayList<Map<String,Object>>();
                    while (iterator.hasNext()) {
                        Map.Entry<String, Control> entry = iterator.next();
                        if (entry.getValue() instanceof Text) {
                            Text textField = (Text) entry.getValue();
                            Method method = (Method) textField.getData();
                            if (textField.getText().trim().length() > 0) {
                                if (componentType.isAnnotation()) {
                                    Map<String, Object> memberValuePairs = new HashMap<String, Object>();
                                    memberValuePairs.put(method.getName(), textField.getText());
                                    aList.add(memberValuePairs);
                                } else {
                                    updatedValues.add(textField.getText());
                                }
                            }
                        }
                        if (entry.getValue() instanceof Button) {
                            Button button = (Button)entry.getValue();
                         //   if (button..getStyle() == SWT.CHECK) {
                                Method method = (Method) button.getData();
                                if (componentType.isAnnotation()) {
                                    Map<String, Object> memberValuePairs = new HashMap<String, Object>();
                                    memberValuePairs.put(method.getName(), button.getSelection());
                                    aList.add(memberValuePairs);
                                } else {
                                    updatedValues.add(button.getSelection());
                                }
                        //    }
                        }
                        
                    }
                    if (aList.size() > 0) {
                        updatedValues.add(aList);
                    }
                    arrayValuesTableViewer.refresh();
                }
            });
            gridData = new GridData(SWT.FILL, SWT.FILL, true, false);
            addButton.setLayoutData(gridData);
            
            removeButton = new Button(buttonComposite, SWT.PUSH);
            removeButton.setText(JAXWSUIMessages.ANNOTATION_ARRAY_CELL_EDITOR_REMOVE_LABEL);
            removeButton.addSelectionListener(new SelectionAdapter() {
                @Override
                public void widgetSelected(SelectionEvent event) {
                    ISelection selection = arrayValuesTableViewer.getSelection();
                    if (selection != null && !selection.isEmpty()) {
                        int index = arrayValuesTable.getSelectionIndex();
                        updatedValues.remove(index);
                        arrayValuesTableViewer.refresh();
                    }
                }
            });
            gridData = new GridData(SWT.FILL, SWT.FILL, true, false);
            removeButton.setLayoutData(gridData);
            
            upButton = new Button(buttonComposite, SWT.PUSH);
            upButton.setText(JAXWSUIMessages.ANNOTATION_ARRAY_CELL_EDITOR_UP_LABEL);
            upButton.addSelectionListener(new SelectionAdapter() {
                @Override
                public void widgetSelected(SelectionEvent e) {
                    moveSelectedElememtUp(getSelectedElement(), getTableViewer());
                 }
            });
            
            gridData = new GridData(SWT.FILL, SWT.FILL, true, false);
            upButton.setLayoutData(gridData);
            
            downButton = new Button(buttonComposite, SWT.PUSH);
            downButton.setText(JAXWSUIMessages.ANNOTATION_ARRAY_CELL_EDITOR_DOWN_LABEL);
            downButton.addSelectionListener(new SelectionAdapter() {
                @Override
                public void widgetSelected(SelectionEvent e) {
                    moveSelectedElememtDown(getSelectedElement(), getTableViewer());
                }
            });
            gridData = new GridData(SWT.FILL, SWT.FILL, true, false);
            downButton.setLayoutData(gridData);
            
            Composite valuesComposite = new Composite(mainComposite, SWT.NONE);
            gridLayout = new GridLayout(1, false);
            valuesComposite.setLayout(gridLayout);
            gridData = new GridData(SWT.FILL, SWT.FILL, true, true);
            gridData.widthHint = 200;
            valuesComposite.setLayoutData(gridData);
            
            Label valuesLabel = new Label(valuesComposite, SWT.NONE);
            valuesLabel.setText(method.getName() + ":"); //$NON-NLS-1$
            
            arrayValuesTableViewer = new TableViewer(valuesComposite, SWT.BORDER | SWT.SINGLE | SWT.V_SCROLL 
                    | SWT.H_SCROLL);
            arrayValuesTableViewer.setLabelProvider(new LabelProvider() {
                @Override
                public String getText(Object element) {
                    if (element instanceof List) {
                        String annotationName = method.getReturnType().getComponentType().getSimpleName();
                        annotationName += "("; //$NON-NLS-1$
                        List<Map<String, Object>> valuesList = (List<Map<String, Object>>)element;
                        Iterator<Map<String, Object>> valuesIterator = valuesList.iterator();
                        while (valuesIterator.hasNext()) {
                            Map<String, Object> valuesMap = (Map<String, Object>)valuesIterator.next();
                            Set<Entry<String, Object>> entrySet = valuesMap.entrySet();
                            Iterator<Map.Entry<String, Object>> iterator = entrySet.iterator();
                            while (iterator.hasNext()) {
                                Map.Entry<String, Object> entry = iterator.next();
                                Object value = entry.getValue();
                                boolean isString = (value instanceof String && !value.toString().
                                        endsWith(".class")); //$NON-NLS-1$
                                if (isString) {
                                    annotationName += entry.getKey() + "=\"" + value + "\""; //$NON-NLS-1$ //$NON-NLS-2$
                                } else {
                                    annotationName += entry.getKey() + "=" + value; //$NON-NLS-1$
                                }
                            }
                            if (valuesIterator.hasNext()) {
                                annotationName += ", "; //$NON-NLS-1$
                            }
                        }
                        return annotationName += ")"; //$NON-NLS-1$
                    }
                    return element.toString();
                }

                @Override
                public Image getImage(Object element) {
                    Class<?> returnType = method.getReturnType();
                    if (returnType.getComponentType().isAnnotation()) {
                        return JavaUI.getSharedImages().getImage(ISharedImages.IMG_OBJS_ANNOTATION);
                    } if (returnType.equals(Class.class)) {
                        return JavaUI.getSharedImages().getImage(ISharedImages.IMG_OBJS_CLASS);
                    } else {
                        return PlatformUI.getWorkbench().getSharedImages().getImage(
                                org.eclipse.ui.ISharedImages.IMG_OBJ_FILE);
                    }
                }
            });
            
            arrayValuesTableViewer.addSelectionChangedListener(new ISelectionChangedListener() {
                public void selectionChanged(SelectionChangedEvent event) {
                    int index = arrayValuesTable.getSelectionIndex();
                    int itemCount = arrayValuesTable.getItemCount();
                    
                    if (index == 0 && itemCount <= 1) {
                        upButton.setEnabled(false);
                        downButton.setEnabled(false);
                    }
                    
                    if (index == 0 && itemCount > 1) {
                        upButton.setEnabled(false);
                        downButton.setEnabled(true);
                    }
                    
                    if (index > 0 && index < itemCount - 1) {
                        upButton.setEnabled(true);
                        downButton.setEnabled(true);
                    }
                    
                    if (index > 0 && index == itemCount - 1) {
                        upButton.setEnabled(true);
                        downButton.setEnabled(false);
                    }
                    
                    if (index != -1) {
                        removeButton.setEnabled(true);
                    } else {
                        removeButton.setEnabled(false);
                    }
                }                
            });
            
            arrayValuesTableViewer.setContentProvider(new ArrayValuesContentProvider());

            arrayValuesTable = arrayValuesTableViewer.getTable();
            gridData = new GridData(SWT.FILL, SWT.FILL, true, true);
            arrayValuesTable.setLayoutData(gridData);

            arrayValuesTableViewer.setInput(values);

            upButton.setEnabled(false);
            downButton.setEnabled(false);
            removeButton.setEnabled(false);

            return mainComposite;
        }
        
        public void createEntryFields(Method method, Composite typeComposite) {
           //TODO Handle ENUMS 
            Class<?> returnType = method.getReturnType();
            Object defaultValue = method.getDefaultValue();
            GridData gridData = new GridData(SWT.FILL, SWT.FILL, true, true);
            if (returnType.equals(String.class)) {
                Text text = new Text(typeComposite, SWT.BORDER);
                text.setData(method);
                gridData.horizontalSpan = 2;
                text.setLayoutData(gridData);
                if (defaultValue != null) {
                    text.setText(defaultValue.toString());
                }
                controls.put(method.getName(), text);
            }
            if (returnType.equals(Class.class)) {
                final Text text = new Text(typeComposite, SWT.BORDER);
                text.setData(method);
                gridData = new GridData(SWT.FILL, SWT.FILL, true, true);
                text.setLayoutData(gridData);
                if (defaultValue != null) {
                    Class<?> classValue = (Class<?>)defaultValue;
                    text.setText(classValue.getCanonicalName() + ".class");    
                }
                Button browseClassButton = new Button(typeComposite, SWT.PUSH);
                browseClassButton.setText(JAXWSUIMessages.ANNOTATION_ARRAY_CELL_EDITOR_BROWSE_LABEL);
                browseClassButton.addSelectionListener(new SelectionAdapter() {
                    @Override
                    public void widgetSelected(SelectionEvent e) {
                        SelectionDialog dialog = getClassSelectionDialog();
                        dialog.setTitle(JAXWSUIMessages.ANNOTATION_ARRAY_CELL_EDITOR_SELECT_CLASS_TITLE);
                        if (dialog.open() == IDialogConstants.OK_ID) {
                            Object[] types = dialog.getResult();
                            
                            if (types != null && types.length > 0) {
                                IType type = (IType)types[0];
                                if (type.isBinary()) {
                                    text.setText(type.getClassFile().getElementName());
                                }
                            }
                        }
                    }
                });
                controls.put(method.getName(), text);
            }
            if (returnType.isArray()) {
                Label notSupportLabel = new Label(typeComposite, SWT.NONE);
                notSupportLabel.setText(
                        JAXWSUIMessages.ANNOTATION_ARRAY_CELL_EDITOR_NESTED_ARRAYS_NOT_SUPPORTED);
                gridData = new GridData(SWT.FILL, SWT.FILL, true, true);
                gridData.horizontalSpan = 2;
                notSupportLabel.setLayoutData(gridData);
            }
            if (returnType.equals(Boolean.TYPE)) {
                Button checkbox = new Button(typeComposite, SWT.CHECK);
                checkbox.setData(method);
                gridData.horizontalSpan = 2;
                checkbox.setLayoutData(gridData);
                if (defaultValue != null) {
                    checkbox.setSelection((Boolean)defaultValue);
                }
                controls.put(method.getName(), checkbox);
            }
        }
        
        public Object getSelectedElement() {
            IStructuredSelection selection= (IStructuredSelection) arrayValuesTableViewer.getSelection();
            return selection.getFirstElement();
        }
        
        private TableViewer getTableViewer() {
            return arrayValuesTableViewer;
        }
        
        public void moveSelectedElememtUp(Object selected, TableViewer tableViewer) {
            int selectionIndex = tableViewer.getTable().getSelectionIndex();
            if (selectionIndex > 0) {
                updatedValues.remove(selected);
                updatedValues.add(selectionIndex - 1, selected);
                
                tableViewer.refresh();
                tableViewer.reveal(selected);
                tableViewer.setSelection(new StructuredSelection(selected));
            }
        }
        
        public void moveSelectedElememtDown(Object selected, TableViewer tableViewer) {
            int selectionIndex = tableViewer.getTable().getSelectionIndex();
            int itemCount = tableViewer.getTable().getItemCount();
            if (selectionIndex < itemCount - 1) {
                updatedValues.remove(selected);
                updatedValues.add(selectionIndex + 1, selected);
                
                tableViewer.refresh();
                tableViewer.reveal(selected);
                tableViewer.setSelection(new StructuredSelection(selected));
            }
        }

        private class ArrayValuesContentProvider implements IStructuredContentProvider {
            
            public ArrayValuesContentProvider() {
            }
            
            public Object[] getElements(Object inputElement) {
                return updatedValues.toArray();
            }

            public void dispose() {
            }

            public void inputChanged(Viewer viewer, Object oldInput, Object newInput) {
            }            
        }
        
        public SelectionDialog getClassSelectionDialog() {
            try {
                return JavaUI.createTypeDialog(getShell(), PlatformUI.getWorkbench().getProgressService(), 
                        SearchEngine.createWorkspaceScope(), IJavaElementSearchConstants.CONSIDER_CLASSES, 
                        false, "* "); //$NON-NLS-1$
            } catch (JavaModelException jme) {
                JAXWSUIPlugin.log(jme.getStatus());
            }
            return null;
        }
        
        
        @Override
        public Object[] getResult() {
            return updatedValues.toArray();
        }

        @Override
        protected void computeResult() {
        }
    }

}