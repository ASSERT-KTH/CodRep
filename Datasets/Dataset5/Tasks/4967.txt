IType startingPoint = JDTUtils.findType(projectName, model.getJavaStartingPoint());

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
package org.eclipse.jst.ws.internal.cxf.creation.core.commands;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import org.eclipse.core.commands.ExecutionException;
import org.eclipse.core.resources.IProject;
import org.eclipse.core.resources.IResource;
import org.eclipse.core.resources.IResourceChangeEvent;
import org.eclipse.core.resources.ResourcesPlugin;
import org.eclipse.core.runtime.CoreException;
import org.eclipse.core.runtime.IAdaptable;
import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Status;
import org.eclipse.jdt.core.IJavaProject;
import org.eclipse.jdt.core.IType;
import org.eclipse.jdt.core.JavaCore;
import org.eclipse.jst.ws.internal.cxf.core.CXFCorePlugin;
import org.eclipse.jst.ws.internal.cxf.core.context.Java2WSPersistentContext;
import org.eclipse.jst.ws.internal.cxf.core.model.CXFDataModel;
import org.eclipse.jst.ws.internal.cxf.core.model.Java2WSDataModel;
import org.eclipse.jst.ws.internal.cxf.core.resources.JavaResourceChangeListener;
import org.eclipse.jst.ws.internal.cxf.core.resources.WebContentChangeListener;
import org.eclipse.jst.ws.internal.cxf.core.utils.CommandLineUtils;
import org.eclipse.jst.ws.internal.cxf.core.utils.FileUtils;
import org.eclipse.jst.ws.internal.cxf.core.utils.LaunchUtils;
import org.eclipse.jst.ws.internal.cxf.core.utils.SpringUtils;
import org.eclipse.jst.ws.internal.cxf.creation.core.CXFCreationCorePlugin;
import org.eclipse.jst.ws.jaxws.core.utils.JDTUtils;
import org.eclipse.wst.common.frameworks.datamodel.AbstractDataModelOperation;

/**
 * Provides a wrapper around the <code>org.apache.cxf.tools.java2ws.JavaToWS</code> or the
 * <code>org.apache.cxf.tools.java2wsdl.JavaToWSDL</code> command depending on the version
 * of CXF used.
 *
 */
public class Java2WSCommand extends AbstractDataModelOperation {
    private static String JAVA2WSDL_TOOL_CLASS_NAME = "org.apache.cxf.tools.java2wsdl.JavaToWSDL"; //$NON-NLS-1$
    private static String JAVA2WS_TOOL_CLASS_NAME = "org.apache.cxf.tools.java2ws.JavaToWS"; //$NON-NLS-1$
    private String CXF_TOOL_CLASS_NAME;

    private Java2WSDataModel model;
    private String projectName;

    private JavaResourceChangeListener javaResourceChangeListener;
    private WebContentChangeListener webContentChangeListener;

    public Java2WSCommand(Java2WSDataModel model) {
        this.model = model;
        projectName = model.getProjectName();
    }

    @Override
    public IStatus execute(IProgressMonitor monitor, IAdaptable info) throws ExecutionException {
        IStatus status = Status.OK_STATUS;
        IType startingPoint = JDTUtils.getType(projectName, model.getJavaStartingPoint());
        javaResourceChangeListener = new JavaResourceChangeListener(JDTUtils
                .getJavaProjectSourceDirectoryPath(startingPoint));
        webContentChangeListener = new WebContentChangeListener(projectName);

        ResourcesPlugin.getWorkspace().addResourceChangeListener(javaResourceChangeListener,
                IResourceChangeEvent.POST_CHANGE);
        ResourcesPlugin.getWorkspace().addResourceChangeListener(webContentChangeListener,
                IResourceChangeEvent.POST_CHANGE);

        if (model.getDefaultRuntimeVersion().compareTo(CXFCorePlugin.CXF_VERSION_2_1) >= 0) {
            CXF_TOOL_CLASS_NAME = JAVA2WS_TOOL_CLASS_NAME;
        } else {
            CXF_TOOL_CLASS_NAME = JAVA2WSDL_TOOL_CLASS_NAME;
        }

        String[] progArgs = CommandLineUtils.getJava2WSProgramArguments(model);

        try {
            IProject project = FileUtils.getProject(projectName);
            IJavaProject javaProject = JavaCore.create(project);
            LaunchUtils.launch(javaProject, CXF_TOOL_CLASS_NAME, progArgs);
            FileUtils.copyJ2WFilesFromTmp(model);

            if (model.isGenerateWSDL()) {
                SpringUtils.loadSpringConfigInformationFromWSDL(model);
            }

            if (isImplementationSelected() || isGenerateServer()) {
                SpringUtils.createJAXWSEndpoint(model);
            }

        } catch (CoreException ce) {
            status = ce.getStatus();
            CXFCreationCorePlugin.log(status);
        } catch (IOException ioe) {
            status = new Status(IStatus.ERROR, CXFCreationCorePlugin.PLUGIN_ID, ioe.getLocalizedMessage());
            CXFCreationCorePlugin.log(status);
        } finally {
            ResourcesPlugin.getWorkspace().removeResourceChangeListener(javaResourceChangeListener);
            ResourcesPlugin.getWorkspace().removeResourceChangeListener(webContentChangeListener);
            FileUtils.refreshProject(projectName, monitor);
        }

        return status;
    }

    private boolean isImplementationSelected() {
        return model.getFullyQualifiedJavaClassName() != null &&
        model.getFullyQualifiedJavaClassName().trim().length() > 0;
    }

    private boolean isGenerateServer() {
        if (model.isGenerateServer()) {
            model.setFullyQualifiedJavaClassName(model.getFullyQualifiedJavaInterfaceName() + "Impl");
            return true;
        }
        return false;
    }

    @Override
    public IStatus undo(IProgressMonitor monitor, IAdaptable info) throws ExecutionException {
        IStatus status = Status.OK_STATUS;
        List<IResource> changedResources = new ArrayList<IResource>();
        changedResources.addAll(javaResourceChangeListener.getChangedResources());
        changedResources.addAll(webContentChangeListener.getChangedResources());
        if (changedResources.size() > 0) {
            for (IResource resource : changedResources) {
                try {
                    resource.delete(true, monitor);
                } catch (CoreException ce) {
                    status = ce.getStatus();
                    CXFCreationCorePlugin.log(status);
                }
            }
        }
        Java2WSPersistentContext context = CXFCorePlugin.getDefault().getJava2WSContext();
        model.setGenerateClient(context.isGenerateClient());
        model.setGenerateServer(context.isGenerateServer());
        model.setGenerateWrapperFaultBeans(context.isGenerateWrapperFaultBeans());
        model.setGenerateWSDL(context.isGenerateWSDL());
        model.setSoap12Binding(context.isSoap12Binding());
        model.setGenerateXSDImports(context.isGenerateXSDImports());
        return status;
    }

    public CXFDataModel getCXFDataModel() {
        return model;
    }

    //ANT Environment Mappings
    public void setGenerateClient(Boolean generateClient) {
        model.setGenerateClient(generateClient);
    }

    public void setGenerateServer(Boolean generateServer) {
        model.setGenerateServer(generateServer);
    }

    public void setGenerateWrapperFaultBeans(Boolean generateWrapperFaultBeans) {
        model.setGenerateWrapperFaultBeans(true);
    }

    public void setGenerateWSDL(Boolean generateWSDL) {
        model.setGenerateWSDL(generateWSDL);
    }

    public void setWsdlFileName(String wsdlFileName) {
        model.setWsdlFileName(wsdlFileName);
    }

    public void setGenerateXSDImports(Boolean generateXSDImports) {
        model.setGenerateXSDImports(generateXSDImports);
    }

    public void setUseSOAP12Binding(Boolean useSOAP12Binding) {
        model.setSoap12Binding(useSOAP12Binding);
    }
}
 No newline at end of file