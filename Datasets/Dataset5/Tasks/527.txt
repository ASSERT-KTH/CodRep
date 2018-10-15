typeColumn.setText(CXFUIMessages.CXF_RUNTIME_PREFERENCE_PAGE_TYPE_COLUMN_NAME);

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
package org.eclipse.jst.ws.internal.cxf.ui.preferences;

import java.util.Collection;
import java.util.Iterator;
import java.util.Map;

import org.eclipse.jface.preference.PreferencePage;
import org.eclipse.jface.viewers.CheckStateChangedEvent;
import org.eclipse.jface.viewers.CheckboxTableViewer;
import org.eclipse.jface.viewers.ColumnLabelProvider;
import org.eclipse.jface.viewers.ColumnWeightData;
import org.eclipse.jface.viewers.ICheckStateListener;
import org.eclipse.jface.viewers.ISelection;
import org.eclipse.jface.viewers.ISelectionChangedListener;
import org.eclipse.jface.viewers.IStructuredContentProvider;
import org.eclipse.jface.viewers.IStructuredSelection;
import org.eclipse.jface.viewers.SelectionChangedEvent;
import org.eclipse.jface.viewers.StructuredSelection;
import org.eclipse.jface.viewers.TableLayout;
import org.eclipse.jface.viewers.TableViewerColumn;
import org.eclipse.jface.viewers.Viewer;
import org.eclipse.jface.viewers.ViewerComparator;
import org.eclipse.jface.window.Window;
import org.eclipse.jface.wizard.WizardDialog;
import org.eclipse.jst.ws.internal.cxf.core.CXFCorePlugin;
import org.eclipse.jst.ws.internal.cxf.core.model.CXFContext;
import org.eclipse.jst.ws.internal.cxf.core.model.CXFInstall;
import org.eclipse.jst.ws.internal.cxf.core.model.CXFPackage;
import org.eclipse.jst.ws.internal.cxf.core.utils.CXFModelUtils;
import org.eclipse.jst.ws.internal.cxf.ui.CXFUIMessages;
import org.eclipse.jst.ws.internal.cxf.ui.CXFUIPlugin;
import org.eclipse.jst.ws.internal.cxf.ui.widgets.AnnotationsComposite;
import org.eclipse.jst.ws.internal.cxf.ui.widgets.BlankRuntimePreferencesComposite;
import org.eclipse.jst.ws.internal.cxf.ui.widgets.CXF20WSDL2JavaPreferencesComposite;
import org.eclipse.jst.ws.internal.cxf.ui.widgets.CXF21WSDL2JavaPreferencesComposite;
import org.eclipse.jst.ws.internal.cxf.ui.widgets.Java2WSDLRuntimePreferencesComposite;
import org.eclipse.jst.ws.internal.cxf.ui.widgets.Java2WSRuntimePreferencesComposite;
import org.eclipse.jst.ws.internal.cxf.ui.widgets.SpringConfigComposite;
import org.eclipse.jst.ws.internal.cxf.ui.wizards.CXFInstallWizard;
import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.StackLayout;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.graphics.Image;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.TabFolder;
import org.eclipse.swt.widgets.TabItem;
import org.eclipse.swt.widgets.Table;
import org.eclipse.swt.widgets.TableColumn;
import org.eclipse.swt.widgets.TableItem;
import org.eclipse.ui.IWorkbench;
import org.eclipse.ui.IWorkbenchPreferencePage;

public class CXFRuntimePreferencePage extends PreferencePage implements IWorkbenchPreferencePage {
    //    private IStatus CXF_LOCATION_STATUS = new Status(IStatus.OK, CXFUIPlugin.PLUGIN_ID, null);
    //    private IStatus OK_STATUS = new Status(IStatus.OK, CXFUIPlugin.PLUGIN_ID, ""); //$NON-NLS-1$
    //
    private ISelection previousInstall = new StructuredSelection();

    private Button addButton;
    private Button editButton;
    private Button removeButton;

    private CheckboxTableViewer cxfInstallations;

    private Button exportCXFClasspathContainerButton;

    private CXFContext context;

    private Java2WSDLRuntimePreferencesComposite java2WSDLRuntimePreferencesComposite;
    private Java2WSRuntimePreferencesComposite java2WSRuntimePreferencesComposite ;

    private CXF20WSDL2JavaPreferencesComposite cxf20WSDL2JavaPreferencesComposite;
    private CXF21WSDL2JavaPreferencesComposite cxf21WSDL2JavaPreferencesComposite;

    private AnnotationsComposite annotationsComposite;

    private SpringConfigComposite springConfigComposite;

    private StackLayout java2WSStackLayout;
    private StackLayout wsdl2javaStackLayout;
    private StackLayout jaxwsStackLayout;
    private StackLayout springConfigStackLayout;

    private Composite java2WSPreferncesGroup;
    private Composite wsdl2JavaPreferencesGroup;
    private Composite jaxwsPreferencesGroup;
    private Composite springConfigPreferncesGroup;

    private Composite java2WSDLPreferencesComposite;
    private Composite java2WSPreferencesComposite;

    private Composite jaxwsPreferencesComposite;

    private Composite wsdl2Java20PreferencesComposite;
    private Composite wsdl2Java21PreferencesComposite;

    private Composite springPreferencesComposite;

    private BlankRuntimePreferencesComposite java2WSBlankPreferencesComposite;
    private BlankRuntimePreferencesComposite wsdl2JavaBlankPreferencesComposite;
    private BlankRuntimePreferencesComposite jaxwsBlankPreferencesComposite;
    private BlankRuntimePreferencesComposite springConfigBlankPreferencesComposite;

    private Image libraryImage;

    public CXFRuntimePreferencePage() {
        libraryImage = CXFUIPlugin.imageDescriptorFromPlugin(CXFUIPlugin.PLUGIN_ID, "icons/obj16/library_obj.gif").createImage(); //$NON-NLS-1$
    }

    public void init(IWorkbench workbench) {
    }

    @Override
    protected Control createContents(Composite parent) {
        context = CXFCorePlugin.getDefault().getJava2WSContext();

        final Composite composite = new Composite(parent, SWT.NONE);

        GridLayout mainLayout = new GridLayout();
        composite.setLayout(mainLayout);
        GridData gridData = new GridData(GridData.FILL_BOTH);
        composite.setLayoutData(gridData);

        TabFolder cxfPreferenceTab = new TabFolder(composite, SWT.NONE);
        gridData = new GridData(GridData.FILL_BOTH);
        cxfPreferenceTab.setLayoutData(gridData);

        //CXF Runtime Location
        TabItem runtimeInstalLocationItem = new TabItem(cxfPreferenceTab, SWT.NONE);
        runtimeInstalLocationItem.setText(CXFUIMessages.CXF_RUNTIME_PREFERENCE_PAGE_RUNTIME_HOME_TAB_NAME);
        runtimeInstalLocationItem.setToolTipText(CXFUIMessages.CXF_RUNTIME_PREFERENCE_PAGE_RUNTIME_HOME_TAB_TOOLTIP);

        final Composite runtimeGroup = new Composite(cxfPreferenceTab, SWT.NONE);

        runtimeInstalLocationItem.setControl(runtimeGroup);
        runtimeGroup.setToolTipText(CXFUIMessages.CXF_RUNTIME_PREFERENCE_PAGE_RUNTIME_HOME_TAB_TOOLTIP);

        GridLayout runtimeLoactionlayout = new GridLayout();
        runtimeLoactionlayout.numColumns = 3;
        runtimeLoactionlayout.marginHeight = 10;
        runtimeGroup.setLayout(runtimeLoactionlayout);
        gridData = new GridData(GridData.FILL_BOTH);
        runtimeGroup.setLayoutData(gridData);

        Label runtimeTabDescriptionLabel = new Label(runtimeGroup, SWT.WRAP);
        runtimeTabDescriptionLabel.setText(CXFUIMessages.CXF_RUNTIME_PREFERENCE_PAGE_DESCRIPTION_LABEL);
        gridData = new GridData(GridData.FILL_HORIZONTAL);

        gridData.horizontalSpan = 3;
        gridData.widthHint = 300;
        runtimeTabDescriptionLabel.setLayoutData(gridData);

        Table installTable = new Table(runtimeGroup, SWT.CHECK | SWT.MULTI | SWT.BORDER
                | SWT.FULL_SELECTION);
        installTable.setLinesVisible(true);
        installTable.setHeaderVisible(true);

        TableLayout tableLayout = new TableLayout();
        installTable.setLayout(tableLayout);

        cxfInstallations = new CheckboxTableViewer(installTable);
        cxfInstallations.addCheckStateListener(new ICheckStateListener() {
            public void checkStateChanged(CheckStateChangedEvent event) {
                if (event.getChecked()) {
                    setCheckedInstall(event.getElement());
                } else {
                    setCheckedInstall(null);
                }
            }
        });

        cxfInstallations.addSelectionChangedListener(new ISelectionChangedListener() {

            public void selectionChanged(SelectionChangedEvent event) {
                IStructuredSelection selection = (IStructuredSelection) event.getSelection();
                int noElements = selection.size();
                if (noElements > 1) {
                    editButton.setEnabled(false);
                } else {
                    editButton.setEnabled(true);
                }
                removeButton.setEnabled(!selection.isEmpty());
            }
        });
        TableViewerColumn versionViewerColumn = new TableViewerColumn(cxfInstallations, SWT.LEFT);
        versionViewerColumn.setLabelProvider(new ColumnLabelProvider() {

            @Override
            public String getText(Object element) {
                if (element instanceof CXFInstall) {
                    CXFInstall install = (CXFInstall) element;
                    String version = install.getVersion().toString().trim();
                    return version;
                }
                return ""; //$NON-NLS-1$
            }

            @Override
            public Image getImage(Object element) {
                if (element instanceof CXFInstall) {
                    return libraryImage;
                }
                return null;
            }
        });
        TableColumn versionColumn = versionViewerColumn.getColumn();
        versionColumn.setText(CXFUIMessages.CXF_RUNTIME_PREFERENCE_PAGE_VERSION_COLUMN_NAME);
        versionColumn.pack();

        ColumnWeightData columnWeightData = new ColumnWeightData(50, 50, true);
        tableLayout.addColumnData(columnWeightData);

        TableViewerColumn locationViewerColumn = new TableViewerColumn(cxfInstallations, SWT.LEFT);
        locationViewerColumn.setLabelProvider(new ColumnLabelProvider() {

            @Override
            public String getText(Object element) {
                if (element instanceof CXFInstall) {
                    CXFInstall install = (CXFInstall) element;
                    return install.getLocation().toString().trim();
                }
                return ""; //$NON-NLS-1$
            }
        });

        TableColumn locationColumn = locationViewerColumn.getColumn();
        locationColumn.setText(CXFUIMessages.CXF_RUNTIME_PREFERENCE_PAGE_LOCATION_COLUMN_NAME);
        locationColumn.pack();

        columnWeightData = new ColumnWeightData(50, 150, true);
        tableLayout.addColumnData(columnWeightData);

        TableViewerColumn typeViewerColumn = new TableViewerColumn(cxfInstallations, SWT.LEFT);
        typeViewerColumn.setLabelProvider(new ColumnLabelProvider() {

            @Override
            public String getText(Object element) {
                if (element instanceof CXFInstall) {
                    CXFInstall install = (CXFInstall) element;
                    return install.getType().toString().trim();
                }
                return ""; //$NON-NLS-1$
            }
        });

        TableColumn typeColumn = typeViewerColumn.getColumn();
        typeColumn.setText(CXFUIMessages.CXF_RUNTIME_PREFERENCE_PAGE_LOCATION_TYPE_NAME);
        typeColumn.pack();

        columnWeightData = new ColumnWeightData(50, 100, true);
        tableLayout.addColumnData(columnWeightData);

        gridData = new GridData(SWT.FILL, SWT.FILL, true, true);
        gridData.horizontalSpan = 2;
        gridData.verticalSpan = 5;
        cxfInstallations.getTable().setLayoutData(gridData);

        cxfInstallations.setContentProvider(new IStructuredContentProvider() {

            public Object[] getElements(Object inputElement) {
                if (inputElement instanceof Collection<?>) {
                    return ((Collection<?>) inputElement).toArray();
                }
                return new Object[] {};
            }

            public void dispose() {
            }

            public void inputChanged(Viewer viewer, Object oldInput, Object newInput) {
            }
        });

        cxfInstallations.setComparator(new ViewerComparator() {
            @Override
            public int compare(Viewer viewer, Object obj1, Object obj2) {
                if (obj1 instanceof CXFInstall && obj2 instanceof CXFInstall) {
                    return ((CXFInstall) obj1).getVersion().toString().trim().compareTo(
                            ((CXFInstall) obj2).getVersion().toString().trim());
                }
                return super.compare(viewer, obj1, obj2);
            }
        });

        cxfInstallations.setInput(context.getInstallations().values());

        addButton = new Button(runtimeGroup, SWT.NONE);
        addButton.setText(CXFUIMessages.CXF_RUNTIME_PREFERENCE_PAGE_ADD_BUTTON_LABEL);
        gridData = new GridData(SWT.FILL, SWT.BEGINNING, false, false);
        addButton.setLayoutData(gridData);
        addButton.addSelectionListener(new SelectionAdapter() {
            @Override
            public void widgetSelected(SelectionEvent event) {
                CXFInstallWizard installWizard = new CXFInstallWizard();
                WizardDialog dialog = new WizardDialog(getShell(), installWizard);
                if (dialog.open() == Window.OK) {
                    cxfInstallations.refresh();
                }
            }
        });

        editButton = new Button(runtimeGroup, SWT.NONE);
        editButton.setText(CXFUIMessages.CXF_RUNTIME_PREFERENCE_PAGE_EDIT_BUTTON_LABEL);
        gridData = new GridData(SWT.FILL, SWT.BEGINNING, false, false);
        editButton.setLayoutData(gridData);
        editButton.addSelectionListener(new SelectionAdapter() {
            @Override
            public void widgetSelected(SelectionEvent event) {
                IStructuredSelection selection = (IStructuredSelection) cxfInstallations.getSelection();
                if (selection != null && selection.getFirstElement() instanceof CXFInstall) {
                    cxfInstallations.getCheckedElements();
                    //int selectedInstall = cxfInstallations.getTable().getSelectionIndex();
                    String checkedVersion = getCheckedVersion();
                    CXFInstallWizard installWizard = new CXFInstallWizard((CXFInstall) selection.getFirstElement());
                    WizardDialog dialog = new WizardDialog(getShell(), installWizard);
                    if (dialog.open() == Window.OK) {
                        cxfInstallations.refresh();
                        if (checkedVersion != null) {
                            setCheckedVersion(checkedVersion);
                        }
                    }
                }
            }
        });
        editButton.setEnabled(false);

        removeButton = new Button(runtimeGroup, SWT.NONE);
        removeButton.setText(CXFUIMessages.CXF_RUNTIME_PREFERENCE_PAGE_REMOVE_BUTTON_LABEL);
        gridData = new GridData(SWT.FILL, SWT.BEGINNING, false, false);
        removeButton.setLayoutData(gridData);
        removeButton.addSelectionListener(new SelectionAdapter() {
            @Override
            public void widgetSelected(SelectionEvent event) {
                IStructuredSelection selection = (IStructuredSelection) cxfInstallations.getSelection();
                @SuppressWarnings("unchecked")
                Iterator<CXFInstall> iter = selection.iterator();
                Map<String, CXFInstall> installations = context.getInstallations();
                while (iter.hasNext()) {
                    CXFInstall install = iter.next();
                    installations.remove(install.getVersion());
                }
                context.setInstallations(installations);
                cxfInstallations.refresh();
                if (cxfInstallations.getCheckedElements().length == 0) {
                    setCheckedInstall(null);
                }
            }
        });
        removeButton.setEnabled(false);

        Label paddingLabel = new Label(runtimeGroup, SWT.NONE);
        gridData = new GridData(SWT.FILL, SWT.FILL, false, false);
        gridData.horizontalSpan = 3;
        paddingLabel.setLayoutData(gridData);

        exportCXFClasspathContainerButton = new Button(runtimeGroup, SWT.CHECK);
        exportCXFClasspathContainerButton.setText(
                CXFUIMessages.CXF_RUNTIME_PREFERENCE_PAGE_EXPORT_CXF_CLASSPATH_CONTAINER);
        exportCXFClasspathContainerButton.setSelection(context.isExportCXFClasspathContainer());
        exportCXFClasspathContainerButton.addSelectionListener(new SelectionAdapter() {
            @Override
            public void widgetSelected(SelectionEvent e) {
                context.setExportCXFClasspathContainer(((Button) e.widget).getSelection());
            }
        });
        gridData = new GridData(SWT.FILL, SWT.FILL, false, false);
        gridData.horizontalSpan = 3;
        exportCXFClasspathContainerButton.setLayoutData(gridData);

        if (context.getDefaultRuntimeVersion().length() > 0) {
            exportCXFClasspathContainerButton.setEnabled(true);
        } else {
            exportCXFClasspathContainerButton.setEnabled(false);
        }

        //Java2WS
        TabItem java2WSTabItem = new TabItem(cxfPreferenceTab, SWT.NONE);
        java2WSTabItem.setText(CXFUIMessages.JAVA2WS_PREFERENCES_TAB_NAME);
        java2WSTabItem.setToolTipText(CXFUIMessages.JAVA2WS_PREFERENCES_TAB_TOOLTIP);

        java2WSPreferncesGroup = new Composite(cxfPreferenceTab, SWT.NONE);

        java2WSStackLayout = new StackLayout();
        java2WSPreferncesGroup.setLayout(java2WSStackLayout);

        java2WSDLPreferencesComposite = new Composite(java2WSPreferncesGroup, SWT.NONE);
        GridLayout java2WSGridLayout = new GridLayout(1, true);
        java2WSDLPreferencesComposite.setLayout(java2WSGridLayout);

        java2WSDLRuntimePreferencesComposite = new Java2WSDLRuntimePreferencesComposite(
                java2WSDLPreferencesComposite, SWT.NONE, cxfPreferenceTab);
        java2WSDLRuntimePreferencesComposite.addControls();

        java2WSPreferencesComposite = new Composite(java2WSPreferncesGroup, SWT.NONE);
        GridLayout java2WSDLGridLayout = new GridLayout(1, true);
        java2WSPreferencesComposite.setLayout(java2WSDLGridLayout);

        java2WSRuntimePreferencesComposite = new Java2WSRuntimePreferencesComposite(
                java2WSPreferencesComposite, SWT.NONE, cxfPreferenceTab);
        java2WSRuntimePreferencesComposite.addControls();

        java2WSBlankPreferencesComposite = new BlankRuntimePreferencesComposite(java2WSPreferncesGroup,
                SWT.NONE);

        java2WSTabItem.setControl(java2WSPreferncesGroup);

        //WSDL2Java
        TabItem wsdl2JavaTabItem = new TabItem(cxfPreferenceTab, SWT.NONE);
        wsdl2JavaTabItem.setText(CXFUIMessages.WSDL2JAVA_PREFERENCES_TAB_NAME);
        wsdl2JavaTabItem.setToolTipText(CXFUIMessages.WSDL2JAVA_PREFERENCES_TAB_TOOLTIP);

        wsdl2JavaPreferencesGroup = new Composite(cxfPreferenceTab, SWT.NONE);

        wsdl2javaStackLayout = new StackLayout();
        wsdl2JavaPreferencesGroup.setLayout(wsdl2javaStackLayout);

        wsdl2Java20PreferencesComposite = new Composite(wsdl2JavaPreferencesGroup, SWT.NONE);
        GridLayout wsdl2Java20GridLayout = new GridLayout(1, true);
        wsdl2Java20PreferencesComposite.setLayout(wsdl2Java20GridLayout);

        cxf20WSDL2JavaPreferencesComposite = new CXF20WSDL2JavaPreferencesComposite(
                wsdl2Java20PreferencesComposite, SWT.NONE);
        cxf20WSDL2JavaPreferencesComposite.addControls();

        wsdl2Java21PreferencesComposite = new Composite(wsdl2JavaPreferencesGroup, SWT.NONE);
        GridLayout wsdl2Java21GridLayout = new GridLayout(1, true);
        wsdl2Java21PreferencesComposite.setLayout(wsdl2Java21GridLayout);

        cxf21WSDL2JavaPreferencesComposite = new CXF21WSDL2JavaPreferencesComposite(
                wsdl2Java21PreferencesComposite, SWT.NONE);
        cxf21WSDL2JavaPreferencesComposite.addControls();

        wsdl2JavaBlankPreferencesComposite = new BlankRuntimePreferencesComposite(wsdl2JavaPreferencesGroup,
                SWT.NONE);

        wsdl2JavaTabItem.setControl(wsdl2JavaPreferencesGroup);

        //JAX-WS
        TabItem annotationsTabItem = new TabItem(cxfPreferenceTab, SWT.NONE);
        annotationsTabItem.setText(CXFUIMessages.ANNOTATIONS_PREFERENCES_TAB_NAME);
        annotationsTabItem.setToolTipText(CXFUIMessages.ANNOTATIONS_PREFERENCES_TAB_TOOLTIP);

        jaxwsPreferencesGroup = new Composite(cxfPreferenceTab, SWT.NONE);

        jaxwsStackLayout = new StackLayout();
        jaxwsPreferencesGroup.setLayout(jaxwsStackLayout);

        jaxwsPreferencesComposite = new Composite(jaxwsPreferencesGroup, SWT.NONE);
        GridLayout jaxwsGridLayout = new GridLayout(1, true);
        jaxwsPreferencesComposite.setLayout(jaxwsGridLayout);
        annotationsComposite = new AnnotationsComposite(jaxwsPreferencesComposite,  SWT.SHADOW_IN);

        jaxwsBlankPreferencesComposite = new BlankRuntimePreferencesComposite(jaxwsPreferencesGroup,
                SWT.NONE);

        annotationsTabItem.setControl(jaxwsPreferencesGroup);

        //Spring Config
        TabItem springConfigTabItem = new TabItem(cxfPreferenceTab, SWT.NONE);
        springConfigTabItem.setText(CXFUIMessages.SPRING_CONFIG_PREFERENCES_TAB_NAME);
        springConfigTabItem.setToolTipText(CXFUIMessages.SPRING_CONFIG_PREFERENCES_TAB_TOOLTIP);

        springConfigPreferncesGroup = new Composite(cxfPreferenceTab, SWT.NONE);

        springConfigStackLayout = new StackLayout();
        springConfigPreferncesGroup.setLayout(springConfigStackLayout);

        springPreferencesComposite = new Composite(springConfigPreferncesGroup, SWT.NONE);
        GridLayout springGridLayout = new GridLayout(1, true);
        springPreferencesComposite.setLayout(springGridLayout);
        springConfigComposite = new SpringConfigComposite(springPreferencesComposite, SWT.SHADOW_IN);

        springConfigBlankPreferencesComposite = new BlankRuntimePreferencesComposite(springConfigPreferncesGroup,
                SWT.NONE);

        springConfigTabItem.setControl(springConfigPreferncesGroup);

        CXFInstall defaultInstall = getDefaultInstall();
        if (defaultInstall != null) {
            setSelection(new StructuredSelection(defaultInstall));
        }

        handlePreferenceControls();

        composite.pack();
        return composite;
    }

    private CXFInstall getDefaultInstall() {
        Collection<CXFInstall> set = context.getInstallations().values();
        Iterator<CXFInstall> setIterator = set.iterator();
        while (setIterator.hasNext()) {
            CXFInstall entry = setIterator.next();
            if (entry.getVersion().toString().trim().equals(context.getDefaultRuntimeVersion())) {
                return entry;
            }
        }
        return null;
    }

    private String getCheckedVersion() {
        Object[] checkedElements = cxfInstallations.getCheckedElements();
        if (checkedElements.length > 0) {
            return ((CXFInstall) checkedElements[0]).getVersion();
        }
        return null;
    }

    private void setCheckedVersion(String version) {
        TableItem[] tableItems = cxfInstallations.getTable().getItems();
        for (TableItem install : tableItems) {
            if (install.getText(0).equals(version)) {
                install.setChecked(true);
            }
        }
    }

    private void setCheckedInstall(Object element) {
        if (element == null) {
            setSelection(new StructuredSelection());
        } else {
            setSelection(new StructuredSelection(element));
        }
    }

    public void setSelection(ISelection selection) {
        if (selection instanceof IStructuredSelection) {
            if (!selection.equals(previousInstall)) {
                previousInstall = selection;
                IStructuredSelection structuredSelection = (IStructuredSelection) selection;
                CXFInstall install = (CXFInstall) structuredSelection.getFirstElement();
                if (install != null) {
                    cxfInstallations.setCheckedElements(new Object[]{ install });
                    cxfInstallations.reveal(install);
                    context.setDefaultRuntimeVersion(install.getVersion());
                    context.setDefaultRuntimeLocation(install.getLocation());
                    context.setDefaultRuntimeType(install.getType());
                    exportCXFClasspathContainerButton.setEnabled(true);
                } else {
                    context.setDefaultRuntimeVersion(""); //$NON-NLS-1$
                    context.setDefaultRuntimeLocation(""); //$NON-NLS-1$
                    context.setDefaultRuntimeType(""); //$NON-NLS-1$
                    exportCXFClasspathContainerButton.setEnabled(false);
                }
                handlePreferenceControls();
            }
        }
    }

    private void handlePreferenceControls() {
        if (context.getDefaultRuntimeLocation().equals("") || context.getDefaultRuntimeVersion().equals("")) { //$NON-NLS-1$ //$NON-NLS-2$
            java2WSStackLayout.topControl = java2WSBlankPreferencesComposite;
            wsdl2javaStackLayout.topControl = wsdl2JavaBlankPreferencesComposite;
            jaxwsStackLayout.topControl = jaxwsBlankPreferencesComposite;
            springConfigStackLayout.topControl = springConfigBlankPreferencesComposite;
        } else if (context.getDefaultRuntimeVersion().compareTo(CXFCorePlugin.CXF_VERSION_2_1) >= 0) {
            java2WSStackLayout.topControl = java2WSPreferencesComposite;
            wsdl2javaStackLayout.topControl = wsdl2Java21PreferencesComposite;
            jaxwsStackLayout.topControl = jaxwsPreferencesComposite;
            springConfigStackLayout.topControl = springPreferencesComposite;
        } else {
            java2WSStackLayout.topControl = java2WSDLPreferencesComposite;
            wsdl2javaStackLayout.topControl = wsdl2Java20PreferencesComposite;
            jaxwsStackLayout.topControl = jaxwsPreferencesComposite;
            springConfigStackLayout.topControl = springPreferencesComposite;
        }
        java2WSPreferncesGroup.layout();
        wsdl2JavaPreferencesGroup.layout();
        jaxwsPreferencesGroup.layout();
        springConfigPreferncesGroup.layout();
        refresh();
    }

    //    private void updateStatus() {
    //        //    CXF_LOCATION_STATUS = checkRuntimeExist(cxfHomeDirText.getText());
    //        applyStatusToPage(findMostSevere());
    //    }

    //    private void applyStatusToPage(IStatus status) {
    //        String message = status.getMessage();
    //        if (status.getSeverity() > IStatus.OK) {
    //            setErrorMessage(message);
    //        } else {
    //            setMessage(getTitle());
    //            setErrorMessage(null);
    //        }
    //
    //    }
    //
    //    private IStatus findMostSevere() {
    //        return CXF_LOCATION_STATUS;
    //    }

    private void setDefaults() {
        exportCXFClasspathContainerButton.setSelection(CXFModelUtils.getDefaultBooleanValue(
                CXFPackage.CXF_CONTEXT, CXFPackage.CXF_CONTEXT__EXPORT_CXF_CLASSPATH_CONTAINER));

        java2WSDLRuntimePreferencesComposite.setDefaults();
        java2WSRuntimePreferencesComposite.setDefaults();
        cxf20WSDL2JavaPreferencesComposite.setDefaults();
        cxf21WSDL2JavaPreferencesComposite.setDefaults();
        annotationsComposite.setDefaults();
        springConfigComposite.setDefaults();
    }

    private void refresh() {
        if (context.getDefaultRuntimeVersion().compareTo(CXFCorePlugin.CXF_VERSION_2_1) >= 0) {
            java2WSRuntimePreferencesComposite.refresh();
            cxf21WSDL2JavaPreferencesComposite.refresh();
        } else {
            java2WSDLRuntimePreferencesComposite.refresh();
            cxf20WSDL2JavaPreferencesComposite.refresh();
        }
    }

    private void storeValues() {
        context.setExportCXFClasspathContainer(exportCXFClasspathContainerButton.getSelection());

        if (context.getDefaultRuntimeVersion().compareTo(CXFCorePlugin.CXF_VERSION_2_1) >= 0) {
            java2WSRuntimePreferencesComposite.storeValues();
            cxf21WSDL2JavaPreferencesComposite.storeValues();
        } else {
            java2WSDLRuntimePreferencesComposite.storeValues();
            cxf20WSDL2JavaPreferencesComposite.storeValues();
        }
        annotationsComposite.storeValues();
        springConfigComposite.storeValues();
    }

    @Override
    protected void performApply() {
        super.performApply();
    }

    @Override
    public boolean performCancel() {
        return super.performCancel();
    }

    @Override
    protected void performDefaults() {
        super.performDefaults();
        setDefaults();
    }

    @Override
    public boolean performOk() {
        storeValues();
        return true;
    }

    @Override
    public void dispose() {
        super.dispose();
        if (libraryImage != null) {
            libraryImage.dispose();
            libraryImage = null;
        }
    }

}
 No newline at end of file