IType implType = JDTUtils.findType(model.getProjectName(), selectImplementationCombo.getText());

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
package org.eclipse.jst.ws.internal.cxf.creation.ui.widgets;

import java.util.Arrays;
import java.util.List;

import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Status;
import org.eclipse.jdt.core.ICompilationUnit;
import org.eclipse.jdt.core.IMethod;
import org.eclipse.jdt.core.IType;
import org.eclipse.jdt.core.JavaModelException;
import org.eclipse.jdt.core.Signature;
import org.eclipse.jdt.core.search.IJavaSearchConstants;
import org.eclipse.jface.window.Window;
import org.eclipse.jst.ws.internal.cxf.core.model.Java2WSDataModel;
import org.eclipse.jst.ws.internal.cxf.creation.ui.CXFCreationUIMessages;
import org.eclipse.jst.ws.internal.cxf.creation.ui.CXFCreationUIPlugin;
import org.eclipse.jst.ws.internal.cxf.ui.widgets.Java2WSWidgetFactory;
import org.eclipse.jst.ws.jaxws.core.utils.JDTUtils;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.ModifyEvent;
import org.eclipse.swt.events.ModifyListener;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Combo;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Listener;
import org.eclipse.ui.dialogs.ElementTreeSelectionDialog;
import org.eclipse.wst.command.internal.env.ui.widgets.SimpleWidgetDataContributor;
import org.eclipse.wst.command.internal.env.ui.widgets.WidgetDataEvents;

@SuppressWarnings("restriction")
public class Java2WSInterfaceConfigWidget extends SimpleWidgetDataContributor {
    private IStatus IMPL_SELECTION_STATUS = Status.OK_STATUS;

    private Java2WSDataModel model;
    private IType startingPointType;

    private Combo selectImplementationCombo;
    
    public Java2WSInterfaceConfigWidget() {
    }

    public void setJava2WSDataModel(Java2WSDataModel model) {
        this.model = model;
    }

    public void setJavaStartingPointType(IType startingPointType) {
        this.startingPointType = startingPointType;
    }

    @Override
    public WidgetDataEvents addControls(Composite parent, final Listener statusListener) {
        final Composite composite = new Composite(parent, SWT.NONE);
        GridLayout gridLayout = new GridLayout(3, false);
        composite.setLayout(gridLayout);

        GridData gridData = new GridData(SWT.FILL, SWT.FILL, true, false);
        composite.setLayoutData(gridData);
        
        Java2WSWidgetFactory.createSelectImplementationLabel(composite);
        
        selectImplementationCombo = Java2WSWidgetFactory
            .createSelectImplementationCombo(composite, model, startingPointType);
        gridData = new GridData(SWT.FILL, SWT.FILL, true, false);
        selectImplementationCombo.setLayoutData(gridData);
        
        selectImplementationCombo.addSelectionListener(new SelectionAdapter() {
            @Override
            public void widgetSelected(SelectionEvent event) {
                validateImplementationSelection();
                statusListener.handleEvent(null);
            }
        });
        
        selectImplementationCombo.addModifyListener(new ModifyListener() {

        	public void modifyText(ModifyEvent event) {
            	validateImplementationSelection();
                statusListener.handleEvent(null);
            }
        });
        
        Button browseImplButton = Java2WSWidgetFactory.createBrowseButton(composite);
        gridData = new GridData(SWT.FILL, SWT.FILL, false, false);
        browseImplButton.setLayoutData(gridData);
        
        browseImplButton.addSelectionListener(new SelectionAdapter() {

            @Override
            public void widgetSelected(SelectionEvent e) {
                
                ElementTreeSelectionDialog selectionDialog = Java2WSWidgetFactory.createElementTreeSelectionDialog(
                        composite.getShell(), CXFCreationUIMessages.JAVA2WS_SELECT_IMPL_DIALOG_TITLE,
                        CXFCreationUIMessages.JAVA2WS_SELECT_IMPL_DIALOG_DESCRIPTION,
                        JDTUtils.getJavaProject(model.getProjectName()), IJavaSearchConstants.CLASS);

                int returnCode = selectionDialog.open();
                if (returnCode == Window.OK) {
                    ICompilationUnit selectedCompilationUnit = (ICompilationUnit) selectionDialog.getFirstResult();
                    String selectedImplementation = selectedCompilationUnit.findPrimaryType().getFullyQualifiedName();
                    List<String> impls = Arrays.asList(selectImplementationCombo.getItems());
                    if (!impls.contains(selectedImplementation)) {
                    	selectImplementationCombo.add(selectedImplementation);
                    }
                    selectImplementationCombo.setText(selectedImplementation);
                }
            }
        });
        return this;
    }

    @Override
    public IStatus getStatus() {
        return IMPL_SELECTION_STATUS;
    }
    
	private void validateImplementationSelection() {
        IType implType = JDTUtils.getType(model.getProjectName(), selectImplementationCombo.getText());
        if (implType != null) {
            try {
                IMethod[] seiMethods = startingPointType.getMethods();
                for (IMethod seiMethod : seiMethods) {
                    IMethod[] implMethod = implType.findMethods(seiMethod);
                    if (implMethod == null) {
                    	IMPL_SELECTION_STATUS = new Status(IStatus.ERROR, CXFCreationUIPlugin.PLUGIN_ID,
                    	    CXFCreationUIMessages.bind(CXFCreationUIMessages.WEBSERVICE_ENPOINTINTERFACE_MUST_IMPLEMENT,
                                    getImplementsMessage(startingPointType, seiMethod)));
                        break;
                    }
                    IMPL_SELECTION_STATUS = Status.OK_STATUS;
                }
                model.setServiceEndpointInterfaceName(startingPointType.getFullyQualifiedName());
                model.setFullyQualifiedJavaClassName(selectImplementationCombo.getText());
            } catch (JavaModelException jme) {
                CXFCreationUIPlugin.log(jme.getStatus());
            }
        } else {
        	IMPL_SELECTION_STATUS = new Status(IStatus.ERROR, CXFCreationUIPlugin.PLUGIN_ID,
        	    CXFCreationUIMessages.bind(CXFCreationUIMessages.WEBSERVICE_IMPLEMENTATION_NOT_FOUND,
                    		selectImplementationCombo.getText()));   
        }        
	}

    private String getImplementsMessage(IType seiType, IMethod seiMethod) {
        StringBuilder message = new StringBuilder(seiType.getElementName());
        message.append("."); //$NON-NLS-1$
        message.append(seiMethod.getElementName());
        message.append("("); //$NON-NLS-1$
        String[] parameterTypes = seiMethod.getParameterTypes();
        for (int i = 0; i < parameterTypes.length; i++) {
            String parameterType = Signature.toString(parameterTypes[i]);
            message.append(parameterType);
            if (i < parameterTypes.length - 1) {
                message.append(", "); //$NON-NLS-1$
            }
        }
        message.append(")"); //$NON-NLS-1$
        return message.toString();
    }

}