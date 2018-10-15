serviceNameCombo.deselectAll();

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
package org.eclipse.jst.ws.internal.cxf.ui.widgets;

import java.util.Iterator;
import java.util.Map;
import java.util.Set;

import javax.wsdl.Definition;
import javax.wsdl.Service;
import javax.xml.namespace.QName;

import org.eclipse.jdt.core.IPackageFragmentRoot;
import org.eclipse.jdt.core.JavaModelException;
import org.eclipse.jface.viewers.ColumnLabelProvider;
import org.eclipse.jface.viewers.ColumnWeightData;
import org.eclipse.jface.viewers.TableLayout;
import org.eclipse.jface.viewers.TableViewer;
import org.eclipse.jface.viewers.TableViewerColumn;
import org.eclipse.jst.ws.internal.cxf.core.model.WSDL2JavaContext;
import org.eclipse.jst.ws.internal.cxf.core.model.WSDL2JavaDataModel;
import org.eclipse.jst.ws.internal.cxf.ui.CXFUIMessages;
import org.eclipse.jst.ws.internal.cxf.ui.CXFUIPlugin;
import org.eclipse.jst.ws.internal.cxf.ui.dialogs.ResourceSelectionDialog;
import org.eclipse.jst.ws.internal.cxf.ui.viewers.PackageNameColumnLabelProvider;
import org.eclipse.jst.ws.jaxws.core.utils.JDTUtils;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.ModifyEvent;
import org.eclipse.swt.events.ModifyListener;
import org.eclipse.swt.events.PaintEvent;
import org.eclipse.swt.events.PaintListener;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Combo;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.List;
import org.eclipse.swt.widgets.Table;
import org.eclipse.swt.widgets.TableColumn;
import org.eclipse.swt.widgets.TableItem;
import org.eclipse.swt.widgets.Text;
import org.eclipse.ui.dialogs.SelectionDialog;

/**
 * Provides widgets for WSDL2Java preferences, wizards, dialogs. Enables the
 * reuse of widgets in multiple locations. Widgets have there labeling and
 * tooltips set here and where possible listeners are set which update instances
 * of <code>WSDL2JavaContext</code> and <code>WSDL2JavaDataModel</code>.
 * 
 */
public final class WSDL2JavaWidgetFactory {
    private static final String XJC_DV_ARG = "-Xdv"; //$NON-NLS-1$
    private static final String XJC_TS_ARG = "-Xts"; //$NON-NLS-1$
    private static final String XJC_TS_MULTI_ARG = "-Xts:style:multiline"; //$NON-NLS-1$
    private static final String XJC_TS_SIMPLE = "-Xts:style:simple"; //$NON-NLS-1$
    private static final String XJC_LOCATOR_ARG = "-Xlocator"; //$NON-NLS-1$
    private static final String XJC_SYNC_METHODS_ARG = "-Xsync-methods"; //$NON-NLS-1$
    private static final String XJC_MARK_GENERATED_ARG = "-mark-generated"; //$NON-NLS-1$
    private static final String XJC_EPISODE_FILE_ARG = "-episode"; //$NON-NLS-1$

    private WSDL2JavaWidgetFactory() {
    }

    public static Button createGenerateClientButton(Composite parent, final WSDL2JavaContext model) {
        final Button genClientButton = new Button(parent, SWT.CHECK);
        genClientButton.setText(CXFUIMessages.JAVA2WS_GEN_CLIENT_LABEL);
        genClientButton.setToolTipText(CXFUIMessages.WSDL2JAVA_GENERATE_CLIENT_TOOLTIP);
        genClientButton.addSelectionListener(new SelectionAdapter() {
            public void widgetSelected(SelectionEvent e) {
                model.setGenerateClient(genClientButton.getSelection());
            }
        });
        genClientButton.setSelection(model.isGenerateClient());
        return genClientButton;
    }

    public static Button createGenerateServerButton(Composite parent, final WSDL2JavaContext model) {
        final Button genServerButton = new Button(parent, SWT.CHECK);
        genServerButton.setText(CXFUIMessages.JAVA2WS_GEN_SERVER_LABEL);
        genServerButton.setToolTipText(CXFUIMessages.WSDL2JAVA_GENERATE_SERVER_TOOLTIP);
        genServerButton.addSelectionListener(new SelectionAdapter() {
            public void widgetSelected(SelectionEvent e) {
                model.setGenerateServer(genServerButton.getSelection());
            }
        });
        genServerButton.setSelection(model.isGenerateServer());
        return genServerButton;
    }

    public static Button createGenerateImplementationButton(Composite parent, final WSDL2JavaContext model) {
        final Button genImplementatinButton = new Button(parent, SWT.CHECK);
        genImplementatinButton.setText(CXFUIMessages.JAVA2WS_GEN_IMPLEMENTATION_LABEL);
        genImplementatinButton.setToolTipText(CXFUIMessages.WSDL2JAVA_GENERATE_IMPLEMENTATION_TOOLTIP);
        genImplementatinButton.addSelectionListener(new SelectionAdapter() {
            public void widgetSelected(SelectionEvent e) {
                model.setGenerateImplementation(genImplementatinButton.getSelection());
            }
        });
        genImplementatinButton.setSelection(model.isGenerateImplementation());
        return genImplementatinButton;
    }

    public static Button createProcessSOAPHeadersButton(Composite parent, final WSDL2JavaContext model) {
        final Button processSOAPHeadersButton = new Button(parent, SWT.CHECK);
        processSOAPHeadersButton.setText(CXFUIMessages.WSDL2JAVA_PROCESS_SOAP_HEADERS);
        processSOAPHeadersButton.setToolTipText(CXFUIMessages.WSDL2JAVA_PROCESS_SOAP_HEADERS_TOOLTIP);
        processSOAPHeadersButton.addSelectionListener(new SelectionAdapter() {
            public void widgetSelected(SelectionEvent e) {
                model.setProcessSOAPHeaders(processSOAPHeadersButton.getSelection());
            }
        });
        processSOAPHeadersButton.setSelection(model.isProcessSOAPHeaders());
        return processSOAPHeadersButton;
    }

    public static Button createNamespacePackageMappingButton(Composite parent, final WSDL2JavaContext model) {
        final Button namespacePackageMappingButton = new Button(parent, SWT.CHECK);
        namespacePackageMappingButton
                .setText(CXFUIMessages.WSDL2JAVA_LOAD_DEFAULT_NAMESPACE_PACKAGE_MAPPING);
        namespacePackageMappingButton
                .setToolTipText(CXFUIMessages.WSDL2JAVA_DEFAULT_NAMESPACE_LOADING_TOOLTIP);
        namespacePackageMappingButton.addSelectionListener(new SelectionAdapter() {
            public void widgetSelected(SelectionEvent e) {
                model.setLoadDefaultNamespacePackageNameMapping(namespacePackageMappingButton.getSelection());
            }
        });
        namespacePackageMappingButton.setSelection(model.isLoadDefaultNamespacePackageNameMapping());
        return namespacePackageMappingButton;
    }

    public static Button createExcludesNamespaceMappingButton(Composite parent, final WSDL2JavaContext model) {
        final Button excludesNamespaceMappingButton = new Button(parent, SWT.CHECK);
        excludesNamespaceMappingButton
                .setText(CXFUIMessages.WSDL2JAVA_USE_DEFAULT_EXCLUDES_NAMESPACE_MAPPING);
        excludesNamespaceMappingButton
                .setToolTipText(CXFUIMessages.WSDL2JAVA_EXCLUDE_NAMESPACE_LOADING_TOOLTIP);
        excludesNamespaceMappingButton.addSelectionListener(new SelectionAdapter() {
            public void widgetSelected(SelectionEvent e) {
                model.setLoadDefaultExcludesNamepsaceMapping(excludesNamespaceMappingButton.getSelection());
            }
        });
        excludesNamespaceMappingButton.setSelection(model.isLoadDefaultExcludesNamepsaceMapping());
        return excludesNamespaceMappingButton;
    }
    
    public static Button createNoAddressBindingButton(Composite parent, final WSDL2JavaContext model) {
        final Button noAddressBindingButton = new Button(parent, SWT.CHECK);
        noAddressBindingButton.setText(CXFUIMessages.bind(CXFUIMessages.WSDL2JAVA_NO_ADDRESS_BINDING,
                model.getCxfRuntimeEdition()));
        noAddressBindingButton.setToolTipText(
                CXFUIMessages.bind(CXFUIMessages.WSDL2JAVA_NO_ADDRESS_BINDING_TOOLTIP, 
                        model.getCxfRuntimeEdition()));
        noAddressBindingButton.addSelectionListener(new SelectionAdapter() {
            public void widgetSelected(SelectionEvent e) {
                model.setNoAddressBinding(noAddressBindingButton.getSelection());
            }
        });
        noAddressBindingButton.setSelection(model.isNoAddressBinding());
        return noAddressBindingButton;
    }

    public static Button createAutoNameResolutionButton(Composite parent, final WSDL2JavaContext model) {
        final Button autoNameResolutionButton = new Button(parent, SWT.CHECK);
        autoNameResolutionButton.setText(CXFUIMessages.WSDL2JAVA_AUTO_NAME_RESOLUTION);
        autoNameResolutionButton.setToolTipText(CXFUIMessages.WSDL2JAVA_AUTO_NAME_RESOLUTION_TOOLTIP);
        autoNameResolutionButton.addSelectionListener(new SelectionAdapter() {
            public void widgetSelected(SelectionEvent e) {
                model.setAutoNameResolution(autoNameResolutionButton.getSelection());
            }
        });
        autoNameResolutionButton.setSelection(model.isAutoNameResolution());
        return autoNameResolutionButton;
    }
    
    public static TableItem createXJCDefaultValuesTableItem(Table xjcArgsTable, final WSDL2JavaContext model) {
        TableItem xjcDefaultValuesItem = new TableItem(xjcArgsTable, SWT.NONE);
        xjcDefaultValuesItem.setText(0, XJC_DV_ARG);
        xjcDefaultValuesItem.setText(1, CXFUIMessages.WSDL2JAVA_XJC_DEFAULT_VALUES);
        xjcDefaultValuesItem.setChecked(model.isXjcUseDefaultValues());
        return xjcDefaultValuesItem;
    }

    public static TableItem createXJCToStringTableItem(Table xjcArgsTable, final WSDL2JavaContext model) {
        TableItem xjcToStringItem = new TableItem(xjcArgsTable, SWT.NONE);
        xjcToStringItem.setText(0, XJC_TS_ARG);
        xjcToStringItem.setText(1, CXFUIMessages.WSDL2JAVA_XJC_TOSTRING);
        xjcToStringItem.setChecked(model.isXjcToString());
        return xjcToStringItem;
    }

    public static TableItem createXJCToStringMultiLineTableItem(Table xjcArgsTable,
            final WSDL2JavaContext model) {
        TableItem xjcToStringMultiLineItem = new TableItem(xjcArgsTable, SWT.NONE);
        xjcToStringMultiLineItem.setText(0, XJC_TS_MULTI_ARG);
        xjcToStringMultiLineItem.setText(1, CXFUIMessages.WSDL2JAVA_XJC_TOSTRING_MULTILINE);
        xjcToStringMultiLineItem.setChecked(model.isXjcToStringMultiLine());
        return xjcToStringMultiLineItem;
    }

    public static TableItem createXJCToStringSimpleTableItem(Table xjcArgsTable, final WSDL2JavaContext model) {
        TableItem xjcToStringSimpleItem = new TableItem(xjcArgsTable, SWT.NONE);
        xjcToStringSimpleItem.setText(0, XJC_TS_SIMPLE);
        xjcToStringSimpleItem.setText(1, CXFUIMessages.WSDL2JAVA_XJC_TOSTRING_SIMPLE);
        xjcToStringSimpleItem.setChecked(model.isXjcToStringSimple());
        return xjcToStringSimpleItem;
    }

    public static TableItem createXJCLocatorTableItem(Table xjcArgsTable, final WSDL2JavaContext model) {
        TableItem xjcLocatorItem = new TableItem(xjcArgsTable, SWT.NONE);
        xjcLocatorItem.setText(0, XJC_LOCATOR_ARG);
        xjcLocatorItem.setText(1, CXFUIMessages.WSDL2JAVA_XJC_LOCATOR);
        xjcLocatorItem.setChecked(model.isXjcLocator());
        return xjcLocatorItem;
    }

    public static TableItem createXJCSyncMethodsTableItem(Table xjcArgsTable, final WSDL2JavaContext model) {
        TableItem xjcSyncMethodsItem = new TableItem(xjcArgsTable, SWT.NONE);
        xjcSyncMethodsItem.setText(0, XJC_SYNC_METHODS_ARG);
        xjcSyncMethodsItem.setText(1, CXFUIMessages.WSDL2JAVA_XJC_SYNC_METHODS);
        xjcSyncMethodsItem.setChecked(model.isXjcSyncMethods());
        return xjcSyncMethodsItem;
    }

    public static TableItem createXJCMarkGeneratedTableItem(Table xjcArgsTable, final WSDL2JavaContext model) {
        TableItem xjcMarkGeneratedItem = new TableItem(xjcArgsTable, SWT.NONE);
        xjcMarkGeneratedItem.setText(0, XJC_MARK_GENERATED_ARG);
        xjcMarkGeneratedItem.setText(1, CXFUIMessages.WSDL2JAVA_XJC_MARK_GENERATED);
        xjcMarkGeneratedItem.setChecked(model.isXjcMarkGenerated());
        return xjcMarkGeneratedItem;
    }

    public static TableItem createXJCEpisodeFileTableItem(Table xjcArgsTable, final WSDL2JavaContext model) {
        TableItem xjcEpisodeFileItem = new TableItem(xjcArgsTable, SWT.NONE);
        xjcEpisodeFileItem.setText(0, XJC_EPISODE_FILE_ARG);
        xjcEpisodeFileItem.setText(1, CXFUIMessages.WSDL2JAVA_XJC_EPISODE_FILE);
        return xjcEpisodeFileItem;
    }

    public static Table createXJCArgTable(Composite parent, final WSDL2JavaContext model) {
        Table xjcArgsTable = new Table(parent, SWT.CHECK | SWT.MULTI | SWT.BORDER | SWT.FULL_SELECTION);
        xjcArgsTable.setToolTipText(CXFUIMessages.WSDL2JAVA_XJC_ARGS_TOOLTIP);
        xjcArgsTable.setLinesVisible(true);
        xjcArgsTable.setHeaderVisible(true);

        TableLayout tableLayout = new TableLayout();
        xjcArgsTable.setLayout(tableLayout);

        TableColumn xjcArgColumn = new TableColumn(xjcArgsTable, SWT.NONE);
        xjcArgColumn.setText(CXFUIMessages.WSDL2JAVA_XJC_ARG_COLUMN_NAME);

        ColumnWeightData columnWeightData = new ColumnWeightData(100, 100, true);
        tableLayout.addColumnData(columnWeightData);

        TableColumn descriptionColumn = new TableColumn(xjcArgsTable, SWT.NONE);
        descriptionColumn.setText(CXFUIMessages.WSDL2JAVA_XJC_DESCRIPTION_COLUMN_NAME);
        columnWeightData = new ColumnWeightData(200, 200, true);
        tableLayout.addColumnData(columnWeightData);

        xjcArgsTable.addSelectionListener(new SelectionAdapter() {

            @Override
            public void widgetSelected(SelectionEvent event) {
                if (event.detail == SWT.CHECK) {
                    TableItem tableItem = (TableItem) event.item;
                    String xjcArg = tableItem.getText(0);
                    boolean checked = tableItem.getChecked();
                    if (xjcArg.equals(XJC_DV_ARG)) {
                        model.setXjcUseDefaultValues(checked);
                    }

                    if (xjcArg.equals(XJC_TS_ARG)) {
                        model.setXjcToString(checked);
                    }

                    if (xjcArg.equals(XJC_TS_MULTI_ARG)) {
                        model.setXjcToStringMultiLine(checked);
                    }

                    if (xjcArg.equals(XJC_TS_SIMPLE)) {
                        model.setXjcToStringSimple(checked);
                    }

                    if (xjcArg.equals(XJC_LOCATOR_ARG)) {
                        model.setXjcLocator(checked);
                    }

                    if (xjcArg.equals(XJC_SYNC_METHODS_ARG)) {
                        model.setXjcSyncMethods(checked);
                    }

                    if (xjcArg.equals(XJC_MARK_GENERATED_ARG)) {
                        model.setXjcMarkGenerated(checked);
                    }
                }
            }

        });

        xjcArgColumn.pack();
        descriptionColumn.pack();

        return xjcArgsTable;
    }

    public static Label createFrontendLabel(Composite parent) {
        Label frontendLabel = new Label(parent, SWT.NONE);
        frontendLabel.setText(CXFUIMessages.CXF_DEFAULT_FRONTEND_LABEL);
        return frontendLabel;
    }

    public static Combo createFrontendCombo(Composite parent, final WSDL2JavaContext model) {
        final Combo frontendCombo = new Combo(parent, SWT.READ_ONLY);
        frontendCombo.setToolTipText(CXFUIMessages.WSDL2JAVA_FRONTEND_TOOLTIP);
        frontendCombo.add(model.getFrontend().getLiteral());
        frontendCombo.setEnabled(false);
        frontendCombo.select(0);
        return frontendCombo;
    }

    public static Label createDatabindingLabel(Composite parent) {
        Label databindingLabel = new Label(parent, SWT.NONE);
        databindingLabel.setText(CXFUIMessages.CXF_DEFAULT_DATABINDING_LABEL);
        return databindingLabel;
    }

    public static Combo createDatabindingCombo(Composite parent, final WSDL2JavaContext model) {
        final Combo databindingCombo = new Combo(parent, SWT.READ_ONLY);
        databindingCombo.setToolTipText(CXFUIMessages.WSDL2JAVA_DATABINDING_TOOLTIP);
        databindingCombo.add(model.getDatabinding().getLiteral());
        databindingCombo.setEnabled(false);
        databindingCombo.select(0);
        return databindingCombo;
    }

    public static Label createWSDLVersionLabel(Composite parent) {
        Label wsdlVersionLabel = new Label(parent, SWT.NONE);
        wsdlVersionLabel.setText(CXFUIMessages.WSDL2JAVA_WSDL_VERSION_LABEL);
        return wsdlVersionLabel;
    }

    public static Combo createWSDLVersionCombo(Composite parent, final WSDL2JavaContext model) {
        final Combo wsdlVersionCombo = new Combo(parent, SWT.READ_ONLY);
        wsdlVersionCombo.setToolTipText(CXFUIMessages.WSDL2JAVA_WSDL_VERSION_TOOLTIP);
        wsdlVersionCombo.add(model.getWsdlVersion());
        wsdlVersionCombo.setEnabled(false);
        wsdlVersionCombo.select(0);
        return wsdlVersionCombo;
    }

    public static Button createDefaultValuesButton(Composite parent, final WSDL2JavaContext model) {
        final Button useDefaultValuesButton = new Button(parent, SWT.CHECK);
        useDefaultValuesButton.setText(CXFUIMessages.WSDL2JAVA_USE_DEFAULT_VALUES);
        useDefaultValuesButton.setToolTipText(CXFUIMessages.WSDL2JAVA_DEFAULT_VALUES_TOOLTIP);
        useDefaultValuesButton.addSelectionListener(new SelectionAdapter() {
            public void widgetSelected(SelectionEvent e) {
                model.setUseDefaultValues(useDefaultValuesButton.getSelection());
            }
        });
        useDefaultValuesButton.setSelection(model.isUseDefaultValues());
        return useDefaultValuesButton;
    }

    public static Label createOutputDirectoryLabel(Composite parent) {
        Label srcDirLabel = new Label(parent, SWT.NONE);
        srcDirLabel.setText(CXFUIMessages.WSDL2JAVA_OUTPUT_DIRECTORY);
        srcDirLabel.setToolTipText(CXFUIMessages.WSDL2JAVA_OUTPUT_DIRECTORY_TOOLTIP);
        return srcDirLabel;
    }

    public static Combo createOutputDirectoryCombo(Composite parent, final WSDL2JavaDataModel model) {
        final Combo outputDirCombo = new Combo(parent, SWT.READ_ONLY);
        outputDirCombo.setToolTipText(CXFUIMessages.WSDL2JAVA_OUTPUT_DIRECTORY_TOOLTIP);
        outputDirCombo.addSelectionListener(new SelectionAdapter() {

            @Override
            public void widgetSelected(SelectionEvent event) {
                String javaSourceFolder = outputDirCombo.getText();
                model.setJavaSourceFolder(javaSourceFolder);
            }
        });

        populateOutputDirectoryCombo(outputDirCombo, model.getProjectName());
        
        return outputDirCombo;
    }

    public static void populateOutputDirectoryCombo(Combo outputDirCombo, String projectName) {
        outputDirCombo.removeAll();
        try {
            IPackageFragmentRoot[] packageFragmentRoots = JDTUtils.getJavaProject(projectName)
                    .getAllPackageFragmentRoots();
            for (int i = 0; i < packageFragmentRoots.length; i++) {
                IPackageFragmentRoot packageFragmentRoot = packageFragmentRoots[i];
                if (packageFragmentRoot.getKind() == IPackageFragmentRoot.K_SOURCE) {
                    outputDirCombo.add(packageFragmentRoot.getResource().getFullPath().toOSString());
                }
            }
            outputDirCombo.select(0);
        } catch (JavaModelException jme) {
            CXFUIPlugin.log(jme.getStatus());
        }
    }
    
    public static Label createPackageNameLabel(Composite parent) {
        Label packageNameLabel = new Label(parent, SWT.NONE);
        packageNameLabel.setText(CXFUIMessages.WSDL2JAVA_PACKAGE_NAME);
        packageNameLabel.setToolTipText(CXFUIMessages.WSDL2JAVA_PACKAGE_NAME_TOOLTIP);
        return packageNameLabel;
    }

    public static Text createPackageNameText(Composite parent, final WSDL2JavaDataModel model) {
        final Text packageNameText = new Text(parent, SWT.BORDER);
        packageNameText.setToolTipText(CXFUIMessages.WSDL2JAVA_PACKAGE_NAME_TOOLTIP);

        packageNameText.addModifyListener(new ModifyListener() {
            public void modifyText(ModifyEvent e) {
                String packageName = packageNameText.getText();
                model.getIncludedNamespaces().put(model.getTargetNamespace(), packageName);
            }
        });

        packageNameText.setText(model.getIncludedNamespaces().get(model.getTargetNamespace()));

        return packageNameText;
    }

    public static Button createNamespacePackageMappingButton(Composite parent) {
        final Button namespaceMappingButton = new Button(parent, SWT.CHECK);
        namespaceMappingButton.setText(CXFUIMessages.WSDL2JAVA_PACKAGE_NAME_OPTIONAL);
        namespaceMappingButton.setToolTipText(CXFUIMessages.WSDL2JAVA_PACKAGE_NAME_OPTIONAL_TOOLTIP);
        return namespaceMappingButton;
    }

    public static TableViewerColumn createWSDLNamespaceViewerColumn(TableViewer tableViewer) {
        TableViewerColumn wsdlNamespaceViewerColumn = new TableViewerColumn(tableViewer, SWT.LEFT);
        wsdlNamespaceViewerColumn.setLabelProvider(new ColumnLabelProvider() {

            @Override
            public String getText(Object element) {
                return element.toString();
            }
        });
        TableColumn wsdlNamespaceColumn = wsdlNamespaceViewerColumn.getColumn();
        wsdlNamespaceColumn.setText(CXFUIMessages.WSDL2JAVA_WSDL_NAMESPACE_COLUMN_HEADER);
        wsdlNamespaceColumn.pack();
        return wsdlNamespaceViewerColumn;
    }

    public static TableViewerColumn createPackageNameColumn(TableViewer tableViewer, WSDL2JavaDataModel model) {
        TableViewerColumn packageNameViewerColumn = new TableViewerColumn(tableViewer, SWT.LEFT);
        packageNameViewerColumn.setLabelProvider(new PackageNameColumnLabelProvider(model));

        TableColumn packageNameColumn = packageNameViewerColumn.getColumn();
        packageNameColumn.setText(CXFUIMessages.WSDL2JAVA_PACKAGE_NAME_COLUMN_HEADER);
        packageNameColumn.pack();
        return packageNameViewerColumn;
    }

    public static Label createServiceNameLabel(Composite parent) {
        Label serviceNameLabel = new Label(parent, SWT.NONE);
        serviceNameLabel.setText(CXFUIMessages.WSDL2JAVA_SERVICE_NAME);
        serviceNameLabel.setToolTipText(CXFUIMessages.WSDL2JAVA_SERVICE_NAME_TOOLTIP);
        return serviceNameLabel;
    }

    public static Combo createServiceNameCombo(Composite parent, final WSDL2JavaDataModel model) {
        final Combo serviceNameCombo = new Combo(parent, SWT.BORDER | SWT.READ_ONLY);
        serviceNameCombo.setToolTipText(CXFUIMessages.WSDL2JAVA_SERVICE_NAME_TOOLTIP);

        serviceNameCombo.addSelectionListener(new SelectionAdapter() {
            @Override
            public void widgetSelected(SelectionEvent event) {
                model.setServiceName(serviceNameCombo.getText());
            }
        });

        populateServiceNameCombo(serviceNameCombo, model);

        return serviceNameCombo;
    }
    
    @SuppressWarnings("unchecked")
    public static void populateServiceNameCombo(Combo serviceNameCombo, WSDL2JavaDataModel model) {
        serviceNameCombo.removeAll();
        Definition definition = model.getWsdlDefinition();
        if (definition != null) {
            Map servicesMap = definition.getServices();
            if (servicesMap != null) {
                Set servicesEntrySet = servicesMap.entrySet();
                Iterator servicesIterator = servicesEntrySet.iterator();
                while (servicesIterator.hasNext()) {
                    Map.Entry serviceEntry = (Map.Entry) servicesIterator.next();
                    Service service = (Service) serviceEntry.getValue();
                    QName qName = service.getQName();
                    serviceNameCombo.add(qName.getLocalPart());
                }
                serviceNameCombo.select(-1);
            }
        }
    }

    public static Label createBindingFilesLabel(Composite parent) {
        Label bindingFilesLabel = new Label(parent, SWT.NONE);
        bindingFilesLabel.setText(CXFUIMessages.WSDL2JAVA_BINDING_FILES);
        bindingFilesLabel.setToolTipText(CXFUIMessages.WSDL2JAVA_BINDING_NAME_TOOLTIP);
        return bindingFilesLabel;
    }

    public static List createBindingFilesList(Composite parent) {
        final List bindingFilesList = new List(parent, SWT.MULTI | SWT.BORDER | SWT.H_SCROLL | SWT.V_SCROLL);
        bindingFilesList.setToolTipText(CXFUIMessages.WSDL2JAVA_BINDING_NAME_TOOLTIP);
        return bindingFilesList;
    }

    public static Button createAddBindingFileButton(final Composite parent, final WSDL2JavaDataModel model,
            final List bindingFilesList) {
        Button addBindingFileButton = new Button(parent, SWT.PUSH);
        addBindingFileButton.setText(CXFUIMessages.WSDL2JAVA_BINDING_FILES_ADD);
        addBindingFileButton.addSelectionListener(new SelectionAdapter() {

            @Override
            public void widgetSelected(SelectionEvent event) {
                ResourceSelectionDialog selectionDialog = new ResourceSelectionDialog(
                        parent.getShell(),
                        "xml", //$NON-NLS-1$ 
                        CXFUIMessages.WSDL2JAVA_BINDING_FILE_DIALOG_FILTER_NAME,
                        CXFUIMessages.WSDL2JAVA_BINDING_FILE_DIALOG_TITLE);
                selectionDialog.setMessage(CXFUIMessages.WSDL2JAVA_BINDING_FILE_DIALOG_MESSAGE);
                if (selectionDialog.open() == SelectionDialog.OK) {
                    String result = selectionDialog.getResult()[0].toString();
                    if (!model.getBindingFiles().contains(result)) {
                        model.getBindingFiles().add(result);
                        bindingFilesList.add(result);
                    }
                }
            }
        });
        return addBindingFileButton;
    }

    public static Button createRemoveBindingFileButton(Composite parent, final WSDL2JavaDataModel model,
            final List bindingFilesList) {
        final Button removeBindingFileButton = new Button(parent, SWT.PUSH);
        removeBindingFileButton.setText(CXFUIMessages.WSDL2JAVA_BINDING_FILES_REMOVE);
        removeBindingFileButton.setEnabled(false);
        removeBindingFileButton.addSelectionListener(new SelectionAdapter() {

            @Override
            public void widgetSelected(SelectionEvent event) {
                String[] selectedBindingFiles = bindingFilesList.getSelection();
                for (String bindingFile : selectedBindingFiles) {
                    bindingFilesList.remove(bindingFile);
                    model.getBindingFiles().remove(bindingFile);
                }

                if (bindingFilesList.getItemCount() == 0) {
                    removeBindingFileButton.setEnabled(false);
                }
            }
        });

        bindingFilesList.addPaintListener(new PaintListener() {
            public void paintControl(PaintEvent event) {
                if (bindingFilesList.getItemCount() == 0) {
                    removeBindingFileButton.setEnabled(false);
                } else {
                    removeBindingFileButton.setEnabled(true);
                }
            }
        });

        return removeBindingFileButton;
    }

    public static Label createPaddingLabel(Composite parent) {
        return new Label(parent, SWT.NONE);
    }

    public static Label createXMLCatalogLabel(Composite parent) {
        Label xmlCatalogLabel = new Label(parent, SWT.NONE);
        xmlCatalogLabel.setText(CXFUIMessages.WSDL2JAVA_XML_CATLOG);
        xmlCatalogLabel.setToolTipText(CXFUIMessages.WSDL2JAVA_XML_CATALOG_TOOLTIP);
        return xmlCatalogLabel;
    }

    public static Text createXMLCatalogText(Composite parent, final WSDL2JavaDataModel model) {
        final Text xmlCatalogText = new Text(parent, SWT.BORDER);
        xmlCatalogText.setToolTipText(CXFUIMessages.WSDL2JAVA_XML_CATALOG_TOOLTIP);
        xmlCatalogText.addModifyListener(new ModifyListener() {
            public void modifyText(ModifyEvent e) {
                String xmlCatalog = xmlCatalogText.getText();
                model.setCatalogFile(xmlCatalog);
            }
        });

        return xmlCatalogText;
    }

    public static Button createXMLCatalogBrowseButton(Composite parent) {
        Button xmlCatalogBrowseButton = new Button(parent, SWT.PUSH);
        xmlCatalogBrowseButton.setText(CXFUIMessages.WSDL2JAVA_XML_CATLOG_BROWSE);
        return xmlCatalogBrowseButton;
    }

}