model.setJavaSourceFolder(JDTUtils.getJavaProjectSourceDirectoryPath(model.getProjectName()).toOSString());

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
package org.eclipse.jst.ws.internal.cxf.consumption.core.commands;

import java.io.IOException;
import java.net.MalformedURLException;
import java.net.URL;
import java.util.HashMap;

import javax.wsdl.Definition;

import org.eclipse.core.commands.ExecutionException;
import org.eclipse.core.runtime.IAdaptable;
import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Status;
import org.eclipse.jst.ws.internal.cxf.consumption.core.CXFConsumptionCorePlugin;
import org.eclipse.jst.ws.internal.cxf.core.CXFCorePlugin;
import org.eclipse.jst.ws.internal.cxf.core.context.WSDL2JavaPersistentContext;
import org.eclipse.jst.ws.internal.cxf.core.model.WSDL2JavaDataModel;
import org.eclipse.jst.ws.jaxws.core.utils.JDTUtils;
import org.eclipse.jst.ws.jaxws.core.utils.WSDLUtils;
import org.eclipse.wst.common.frameworks.datamodel.AbstractDataModelOperation;

/**
 * Loads the <code>WSDL2JavaDataModel</code> with the persisted defaults 
 * from the preferences and with the initial runtime information such as the
 * starting point WSDL URL.
 * 
 */
public class WSDL2JavaClientDefaultingCommand extends AbstractDataModelOperation {
    private WSDL2JavaDataModel model;
    private String projectName;
    private String inputURL;

    /**
     * Constructs a WSDL2JavaClientDefaultingCommand object.
     * @param model the <code>WSDL2JavaDataModel</code> used to pass information
     *              between commands.
     */
    public WSDL2JavaClientDefaultingCommand(WSDL2JavaDataModel model, String projectName, String inputURL) {
        this.model = model;
        this.projectName = projectName;
        this.inputURL = inputURL;
    }

    @Override
    public IStatus execute(IProgressMonitor monitor, IAdaptable info) throws ExecutionException {
    	IStatus status = Status.OK_STATUS;
        WSDL2JavaPersistentContext context = CXFCorePlugin.getDefault().getWSDL2JavaContext();
        model.setCxfRuntimeVersion(context.getCxfRuntimeVersion());
        model.setCxfRuntimeEdition(context.getCxfRuntimeEdition());
        model.setProjectName(projectName);

        model.setIncludedNamespaces(new HashMap<String, String>());
        model.setExcludedNamespaces(new HashMap<String, String>());

        // XJC
        model.setXjcUseDefaultValues(context.isXjcUseDefaultValues());
        model.setXjcToString(context.isXjcToString());
        model.setXjcToStringMultiLine(context.isXjcToStringMultiLine());
        model.setXjcToStringSimple(context.isXjcToStringSimple());
        model.setXjcLocator(context.isXjcLocator());
        model.setXjcSyncMethods(context.isXjcSyncMethods());
        model.setXjcMarkGenerated(context.isXjcMarkGenerated());

        model.setValidate(context.isValidate());
        model.setProcessSOAPHeaders(context.isProcessSOAPHeaders());
        model.setLoadDefaultExcludesNamepsaceMapping(context.isLoadDefaultExcludesNamepsaceMapping());
        model.setLoadDefaultNamespacePackageNameMapping(context.isLoadDefaultNamespacePackageNameMapping());
        model.setUseDefaultValues(context.isUseDefaultValues());
        model.setNoAddressBinding(context.isNoAddressBinding());
        model.setAutoNameResolution(context.isAutoNameResolution());
        
        model.setJavaSourceFolder(JDTUtils.getJavaProjectSourceDirectoryPath(model.getProjectName()));

    	try {
    		URL wsdlUrl = new URL(inputURL);
			model.setWsdlURL(wsdlUrl);
			
			Definition definition = WSDLUtils.readWSDL(model.getWsdlURL());
        	if (definition != null) {
        		String targetNamespace = definition.getTargetNamespace();
        		String packageName = WSDLUtils.getPackageNameFromNamespace(targetNamespace);
        		model.setTargetNamespace(targetNamespace);
        		model.getIncludedNamespaces().put(targetNamespace, packageName);

                String wsdlLocation = WSDLUtils.getWSDLLocation(definition);
                if (wsdlLocation != null) {
                    model.setWsdlLocation(wsdlLocation);
                }
        		
        		model.setWsdlDefinition(definition);
        	}

		} catch (MalformedURLException murle) {
		    status = new Status(IStatus.ERROR, CXFConsumptionCorePlugin.PLUGIN_ID, 
		            murle.getLocalizedMessage());
			CXFConsumptionCorePlugin.log(status);
		} catch (IOException ioe) {
		    status = new Status(IStatus.ERROR, CXFConsumptionCorePlugin.PLUGIN_ID, 
		    		ioe.getLocalizedMessage());
			CXFConsumptionCorePlugin.log(status);
		}
        return status;
    }
    
    public WSDL2JavaDataModel getWSDL2JavaDataModel() {
        return model;
    }
}