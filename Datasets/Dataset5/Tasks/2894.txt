// WSDL2JavaWidgetFactory.createAutoNameResolutionButton(wsdl2javaGroup, model);

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

import org.eclipse.jst.ws.internal.cxf.core.CXFCorePlugin;
import org.eclipse.jst.ws.internal.cxf.core.model.WSDL2JavaDataModel;
import org.eclipse.jst.ws.internal.cxf.creation.ui.CXFCreationUIMessages;
import org.eclipse.jst.ws.internal.cxf.ui.widgets.WSDL2JavaWidgetFactory;
import org.eclipse.swt.SWT;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Listener;
import org.eclipse.swt.widgets.Table;
import org.eclipse.wst.command.internal.env.ui.widgets.SimpleWidgetDataContributor;
import org.eclipse.wst.command.internal.env.ui.widgets.WidgetDataEvents;

/**
 * @author sclarke
 */
@SuppressWarnings("restriction")
public class WSDL2JavaDefaultsConfigWidget extends SimpleWidgetDataContributor {
    private WSDL2JavaDataModel model;
    
    public WSDL2JavaDefaultsConfigWidget() {
    }
    
    public void setWSDL2JavaDataModel(WSDL2JavaDataModel model) {
        this.model = model;
    }
    
    @Override
    public WidgetDataEvents addControls(final Composite parent, final Listener statusListener) {
        final Composite mainComposite = new Composite(parent, SWT.NONE);
        GridLayout gridLayout = new GridLayout(1, false);
        mainComposite.setLayout(gridLayout);

        GridData gridData = new GridData(SWT.FILL, SWT.FILL, true, true);
        mainComposite.setLayoutData(gridData);

        Group wsdl2javaGroup = new Group(mainComposite, SWT.SHADOW_IN);
        wsdl2javaGroup.setText(CXFCreationUIMessages.WSDL2JAVA_GROUP_LABEL);
        GridLayout wsdl2javalayout = new GridLayout(1, true);
        wsdl2javaGroup.setLayout(wsdl2javalayout);
        gridData = new GridData(SWT.FILL, SWT.FILL, true, false);
        wsdl2javaGroup.setLayoutData(gridData);

        WSDL2JavaWidgetFactory.createGenerateServerButton(wsdl2javaGroup, model);
        WSDL2JavaWidgetFactory.createGenerateImplementationButton(wsdl2javaGroup, model);

        if (model.getCxfRuntimeVersion().compareTo(CXFCorePlugin.CXF_VERSION_2_1) >= 0) {
            WSDL2JavaWidgetFactory.createDefaultValuesButton(wsdl2javaGroup, model);
        }

        WSDL2JavaWidgetFactory.createProcessSOAPHeadersButton(wsdl2javaGroup, model);

        WSDL2JavaWidgetFactory.createNamespacePackageMappingButton(wsdl2javaGroup, model);

        WSDL2JavaWidgetFactory.createExcludesNamespaceMappingButton(wsdl2javaGroup, model);
        
        WSDL2JavaWidgetFactory.createAutoNameResolutionButton(wsdl2javaGroup, model);
        
        if (model.getCxfRuntimeVersion().compareTo(CXFCorePlugin.CXF_VERSION_2_1) >= 0) {
            WSDL2JavaWidgetFactory.createNoAddressBindingButton(wsdl2javaGroup, model);
        }
        
        Group xjcArgGroup = new Group(mainComposite, SWT.SHADOW_IN);
        xjcArgGroup.setText(CXFCreationUIMessages.WSDL2JAVA_XJC_ARG_GROUP_LABEL);
        GridLayout xjcArgLayout = new GridLayout(1, true);
        xjcArgGroup.setLayout(xjcArgLayout);
        gridData = new GridData(SWT.FILL, SWT.FILL, true, false);
        xjcArgGroup.setLayoutData(gridData);

        Table xjcArgsTable = WSDL2JavaWidgetFactory.createXJCArgTable(xjcArgGroup, model);
        gridData = new GridData(SWT.FILL, SWT.FILL, true, true);
        gridData.horizontalSpan = 3;
        gridData.verticalSpan = 6;
        xjcArgsTable.setLayoutData(gridData);

        WSDL2JavaWidgetFactory.createXJCDefaultValuesTableItem(xjcArgsTable, model);
        WSDL2JavaWidgetFactory.createXJCToStringTableItem(xjcArgsTable, model);
        WSDL2JavaWidgetFactory.createXJCToStringMultiLineTableItem(xjcArgsTable, model);
        WSDL2JavaWidgetFactory.createXJCToStringSimpleTableItem(xjcArgsTable, model);
        WSDL2JavaWidgetFactory.createXJCLocatorTableItem(xjcArgsTable, model);
        WSDL2JavaWidgetFactory.createXJCSyncMethodsTableItem(xjcArgsTable, model);
        WSDL2JavaWidgetFactory.createXJCMarkGeneratedTableItem(xjcArgsTable, model);

        return this;
    }

}