final Combo seiCombo = new Combo(parent, SWT.BORDER);

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

import org.eclipse.jdt.core.IJavaProject;
import org.eclipse.jdt.core.IType;
import org.eclipse.jdt.core.ITypeHierarchy;
import org.eclipse.jdt.core.JavaModelException;
import org.eclipse.jdt.ui.JavaElementLabelProvider;
import org.eclipse.jface.viewers.ArrayContentProvider;
import org.eclipse.jface.viewers.CheckboxTableViewer;
import org.eclipse.jst.ws.internal.cxf.core.model.DataBinding;
import org.eclipse.jst.ws.internal.cxf.core.model.Frontend;
import org.eclipse.jst.ws.internal.cxf.core.model.Java2WSContext;
import org.eclipse.jst.ws.internal.cxf.core.model.Java2WSDataModel;
import org.eclipse.jst.ws.internal.cxf.ui.CXFUIMessages;
import org.eclipse.jst.ws.internal.cxf.ui.CXFUIPlugin;
import org.eclipse.jst.ws.jaxws.core.utils.JDTUtils;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.ModifyEvent;
import org.eclipse.swt.events.ModifyListener;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Combo;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Text;

/**
 * Provides widgets for Java2WS preferences, wizards, dialogs. Enables the reuse
 * of widgets in multiple locations. Widgets have there labeling and tooltips
 * set here and where possible listeners are set which update instances of
 * <code>Java2WSContext</code> and <code>Java2WSDataModel</code>.
 * 
 */
public final class Java2WSWidgetFactory {

    private Java2WSWidgetFactory() {
    }

    public static Label createSOAPBindingLabel(Composite parent) {
        Label defaultSoapBinding = new Label(parent, SWT.NONE);
        defaultSoapBinding.setText(CXFUIMessages.JAVA2WS_DEFAULT_SOAPBINDING_LABEL);
        return defaultSoapBinding;
    }

    public static Combo createSOAPBingCombo(Composite parent, final Java2WSContext context) {
        Combo soapBindingCombo = new Combo(parent, SWT.READ_ONLY);
        soapBindingCombo.setToolTipText(CXFUIMessages.JAVA2WS_SOAP12_BINDING_TOOLTIP);
        soapBindingCombo.add("SOAP 1.1"); //$NON-NLS-1$
        soapBindingCombo.add("SOAP 1.2"); //$NON-NLS-1$
        soapBindingCombo.addSelectionListener(new SelectionAdapter() {
            public void widgetSelected(SelectionEvent e) {
                String soapBinding = ((Combo) e.widget).getText();
                if (soapBinding.equals("SOAP 1.2")) { //$NON-NLS-1$
                    context.setSoap12Binding(true);
                } else {
                    context.setSoap12Binding(false);
                }
            }
        });
        if (context.isSoap12Binding()) {
            soapBindingCombo.setText("SOAP 1.2"); //$NON-NLS-1$
        } else {
            soapBindingCombo.setText("SOAP 1.1"); //$NON-NLS-1$
        }

        return soapBindingCombo;
    }

    public static Button createXSDImportsButton(Composite parent, final Java2WSContext context) {
        Button createXSDImports = new Button(parent, SWT.CHECK);
        createXSDImports.setText(CXFUIMessages.JAVA2WS_GEN_XSD_IMPORTS);
        createXSDImports.setToolTipText(CXFUIMessages.JAVA2WS_CREATE_XSD_IMPORTS_TOOLTIP);
        createXSDImports.addSelectionListener(new SelectionAdapter() {
            public void widgetSelected(SelectionEvent e) {
                context.setGenerateXSDImports(((Button) e.widget).getSelection());
            }
        });
        createXSDImports.setSelection(context.isGenerateXSDImports());
        return createXSDImports;
    }

    public static Label createFrontendLabel(Composite parent) {
        Label frontendLabel = new Label(parent, SWT.NONE);
        frontendLabel.setText(CXFUIMessages.CXF_DEFAULT_FRONTEND_LABEL);
        return frontendLabel;
    }

    public static Combo createFrontendCombo(Composite parent, final Java2WSContext context) {
        final Combo frontendCombo = new Combo(parent, SWT.READ_ONLY);
        frontendCombo.setToolTipText(CXFUIMessages.JAVA2WS_FRONTEND_TOOLTIP);
        frontendCombo.add(Frontend.JAXWS.getLiteral());
        frontendCombo.addSelectionListener(new SelectionAdapter() {
            public void widgetSelected(SelectionEvent e) {
                String frontend = frontendCombo.getText();
                context.setFrontend(Frontend.get(frontend));
                if (frontend.equals(Frontend.JAXWS.getLiteral())) {
                    context.setDatabinding(DataBinding.get(DataBinding.JAXB.getLiteral()));
                }
//                if (frontend.equals("simple")) {
//                    context.setDatabinding("aegis");
//                }
            }
        });
        frontendCombo.setText(context.getFrontend().getLiteral());

        return frontendCombo;
    }

    public static Label createDatabindingLabel(Composite parent) {
        Label databindingLabel = new Label(parent, SWT.NONE);
        databindingLabel.setText(CXFUIMessages.CXF_DEFAULT_DATABINDING_LABEL);
        return databindingLabel;
    }

    public static Combo createDatabindingCombo(Composite parent, final Java2WSContext context) {
        final Combo databindingCombo = new Combo(parent, SWT.READ_ONLY);
        databindingCombo.setToolTipText(CXFUIMessages.JAVA2WS_DATABINDING_TOOLTIP);
        databindingCombo.add(DataBinding.JAXB.getLiteral());
        databindingCombo.addSelectionListener(new SelectionAdapter() {
            public void widgetSelected(SelectionEvent e) {
                context.setDatabinding(DataBinding.get(databindingCombo.getText()));
            }
        });
        databindingCombo.setText(context.getDatabinding().getLiteral());
        return databindingCombo;
    }

    public static Button createGenerateClientButton(Composite parent, final Java2WSContext context) {
        final Button genClientButton = new Button(parent, SWT.CHECK);
        genClientButton.setText(CXFUIMessages.JAVA2WS_GEN_CLIENT_LABEL);
        genClientButton.setToolTipText(CXFUIMessages.JAVA2WS_GENERATE_CLIENT_TOOLTIP);
        genClientButton.addSelectionListener(new SelectionAdapter() {
            public void widgetSelected(SelectionEvent e) {
                context.setGenerateClient(genClientButton.getSelection());
            }
        });
        genClientButton.setSelection(context.isGenerateClient());
        return genClientButton;
    }

    public static Button createGenerateServerButton(Composite parent, final Java2WSContext context) {
        final Button genServerButton = new Button(parent, SWT.CHECK);
        genServerButton.setText(CXFUIMessages.JAVA2WS_GEN_SERVER_LABEL);
        genServerButton.setToolTipText(CXFUIMessages.JAVA2WS_GENERATE_SERVER_TOOLTIP);
        genServerButton.addSelectionListener(new SelectionAdapter() {
            public void widgetSelected(SelectionEvent e) {
                context.setGenerateServer(genServerButton.getSelection());
            }
        });
        genServerButton.setSelection(context.isGenerateServer());
        return genServerButton;
    }

    public static Button createGenerateWrapperFaultBeanButton(Composite parent, final Java2WSContext context) {
        final Button genWrapperFaultButton = new Button(parent, SWT.CHECK);
        genWrapperFaultButton.setText(CXFUIMessages.JAVA2WS_GEN_WRAPPER_FAULT_LABEL);
        genWrapperFaultButton.setToolTipText(CXFUIMessages.JAVA2WS_GENERATE_WRAPPERBEAN_TOOLTIP);
        genWrapperFaultButton.addSelectionListener(new SelectionAdapter() {
            public void widgetSelected(SelectionEvent e) {
                context.setGenerateWrapperFaultBeans(genWrapperFaultButton.getSelection());
            }
        });
        genWrapperFaultButton.setSelection(context.isGenerateWrapperFaultBeans());
        return genWrapperFaultButton;
    }

    public static Button createGenerateWSDLButton(Composite parent, final Java2WSContext context) {
        final Button genWSDLButton = new Button(parent, SWT.CHECK);
        genWSDLButton.setText(CXFUIMessages.JAVA2WS_GEN_WSDL_LABEL);
        genWSDLButton.setToolTipText(CXFUIMessages.JAVA2WS_GENERATE_WSDL_TOOLTIP);
        genWSDLButton.addSelectionListener(new SelectionAdapter() {
            public void widgetSelected(SelectionEvent e) {
                context.setGenerateWSDL(genWSDLButton.getSelection());
            }
        });
        genWSDLButton.setSelection(context.isGenerateWSDL());
        return genWSDLButton;
    }

    public static Label createWSDLFileNameLabel(Composite parent) {
        Label wsdlFileNameLabel = new Label(parent, SWT.NONE);
        wsdlFileNameLabel.setText(CXFUIMessages.JAVA2WS_WSDL_FILE_NAME);
        return wsdlFileNameLabel;

    }

    public static Text createWSDLFileNameText(Composite parent, final Java2WSDataModel model) {
        final Text wsdlFileText = new Text(parent, SWT.BORDER);
        wsdlFileText.setToolTipText(CXFUIMessages.JAVA2WS_OUTPUT_FILE_TOOLTIP);
        wsdlFileText.addModifyListener(new ModifyListener() {
            public void modifyText(ModifyEvent e) {
                model.setWsdlFileName(wsdlFileText.getText());
            }
        });
        wsdlFileText.setText(model.getWsdlFileName());
        return wsdlFileText;
    }

    public static Button createUseSEIButton(Composite parent) {
        Button useSEIButton = new Button(parent, SWT.CHECK);
        useSEIButton.setText(CXFUIMessages.JAVA2WS_USE_SEI_BUTTON);
        return useSEIButton;
    }

    public static Label createInformationLabel(Composite parent, IType startingPointType) {
        Label infoLabel = new Label(parent, SWT.WRAP);
        infoLabel.setText(CXFUIMessages.bind(CXFUIMessages.JAVA2WS_USE_SEI_INFO_LABEL, startingPointType
                .getElementName()));
        return infoLabel;
    }

    public static Label createPaddingLabel(Composite parent) {
        return new Label(parent, SWT.NONE);
    }

    public static Button createSelectSEIButton(Composite parent) {
        Button selectSEIButton = new Button(parent, SWT.RADIO);
        selectSEIButton.setText(CXFUIMessages.JAVA2WS_SELECT_SEI_LABEL);
        return selectSEIButton;
    }

    public static Label createSelectSEILabel(Composite parent) {
        Label selectSEILabel = new Label(parent, SWT.NONE);
        selectSEILabel.setText(CXFUIMessages.JAVA2WS_SELECT_SEI_LABEL);
        return selectSEILabel;
    }

    public static Combo createSelectSEICombo(Composite parent, final Java2WSDataModel model,
            IType javaStartingPointType) {
        final Combo seiCombo = new Combo(parent, SWT.READ_ONLY);
        seiCombo.setToolTipText(CXFUIMessages.JAVA2WS_SELECT_SEI_TOOLTIP);

        IJavaProject javaProject = JDTUtils.getJavaProject(model.getProjectName());
        try {
            ITypeHierarchy typeHierarchy = javaStartingPointType.newTypeHierarchy(javaProject, null);
            IType[] allInterfaces = typeHierarchy.getAllInterfaces();
            for (int i = 0; i < allInterfaces.length; i++) {
                IType itype = allInterfaces[i];
                if (!itype.isBinary() && itype.getResource().getProject().equals(javaProject.getProject())) {
                    seiCombo.add(itype.getFullyQualifiedName());
                }
            }
        } catch (JavaModelException jme) {
            CXFUIPlugin.log(jme.getStatus());
        }

        seiCombo.addSelectionListener(new SelectionAdapter() {
            @Override
            public void widgetSelected(SelectionEvent event) {
                String seiInterfaceName = seiCombo.getText();
                model.setFullyQualifiedJavaInterfaceName(seiInterfaceName);
            }
        });

        seiCombo.select(-1);
        return seiCombo;
    }

    public static Button createExtractSEIButton(Composite parent) {
        Button extractSEIButton = new Button(parent, SWT.RADIO);
        extractSEIButton.setText(CXFUIMessages.JAVA2WS_EXTRACT_SEI_LABEL);
        return extractSEIButton;
    }

    public static Label createExtractSEILabel(Composite parent) {
        Label extractSEILabel = new Label(parent, SWT.NONE);
        extractSEILabel.setText(CXFUIMessages.JAVA2WS_EXTRACT_SEI_LABEL);
        return extractSEILabel;
    }

    public static Text createSEIInterfaceNameText(Composite parent) {
        Text seiInterfaceNameText = new Text(parent, SWT.BORDER);
        seiInterfaceNameText.setToolTipText(CXFUIMessages.JAVA2WS_EXTRACT_SEI_TOOLTIP);
        return seiInterfaceNameText;
    }

    public static Label createMemebersToExtractLabel(Composite parent) {
        Label seiMembersToExtractLabel = new Label(parent, SWT.NONE);
        seiMembersToExtractLabel.setText(CXFUIMessages.JAVA2WS_EXTRACT_MEMBERS_LABEL);
        return seiMembersToExtractLabel;
    }

    public static CheckboxTableViewer createSEIMembersToExtractTableViewer(Composite parent) {
        CheckboxTableViewer seiMembersToExtractTableViewer = CheckboxTableViewer.newCheckList(parent,
                SWT.BORDER | SWT.V_SCROLL | SWT.H_SCROLL);
        seiMembersToExtractTableViewer.setLabelProvider(new JavaElementLabelProvider());
        seiMembersToExtractTableViewer.setContentProvider(new ArrayContentProvider());
        return seiMembersToExtractTableViewer;
    }

    public static Button createSelectAllButton(Composite parent) {
        Button selectAllButton = new Button(parent, SWT.PUSH);
        selectAllButton.setText(CXFUIMessages.JAVA2WS_SELECT_ALL_BUTTON);
        return selectAllButton;
    }

    public static Button createDeselectAllButton(Composite parent) {
        Button deselectAllButton = new Button(parent, SWT.PUSH);
        deselectAllButton.setText(CXFUIMessages.JAVA2WS_DESELECT_ALL_BUTTON);
        return deselectAllButton;
    }
    
    public static Label createSelectImplementationLabel(Composite parent) {
        Label selectImplementationLabel = new Label(parent, SWT.NONE);
        selectImplementationLabel.setText(CXFUIMessages.JAVA2WS_SELECT_IMPLEMENTATION);
        return selectImplementationLabel;
    }
    
    public static Combo createSelectImplementationCombo(Composite parent, 
            final Java2WSDataModel model, IType javaStartingPointType) {
        final Combo selectImplementationCombo = new Combo(parent, SWT.READ_ONLY);
        selectImplementationCombo.setToolTipText(CXFUIMessages.JAVA2WS_SELECT_IMPLEMENTATION_TOOLTIP);

        IJavaProject javaProject = JDTUtils.getJavaProject(model.getProjectName());
        try {
            ITypeHierarchy typeHierarchy = javaStartingPointType.newTypeHierarchy(javaProject, null);
            IType[] allImplementations = typeHierarchy.getAllSubtypes(javaStartingPointType);
            for (int i = 0; i < allImplementations.length; i++) {
                IType itype = allImplementations[i];
                if (!itype.isBinary() && itype.getResource().getProject().equals(javaProject.getProject())) {
                    String packageName = itype.getPackageFragment().getElementName();
                    if (packageName.trim().length() > 0) {
                        packageName += "."; //$NON-NLS-1$
                    }
                    String qualifiedName = packageName + itype.getPrimaryElement().getElementName();
                    selectImplementationCombo.add(qualifiedName);
                }
            }
        } catch (JavaModelException jme) {
            CXFUIPlugin.log(jme.getStatus());
        }

        selectImplementationCombo.addSelectionListener(new SelectionAdapter() {
            @Override
            public void widgetSelected(SelectionEvent event) {
                String implementationName = selectImplementationCombo.getText();
                model.setFullyQualifiedJavaClassName(implementationName);
            }
        });

        selectImplementationCombo.select(-1);
        return selectImplementationCombo;
    }

}