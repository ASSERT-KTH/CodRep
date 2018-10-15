IType type = JDTUtils.findType(javaProject, model.getJavaStartingPoint());

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
package org.eclipse.jst.ws.internal.cxf.creation.core.commands;

import org.eclipse.core.commands.ExecutionException;
import org.eclipse.core.runtime.IAdaptable;
import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Status;
import org.eclipse.jdt.core.IJavaProject;
import org.eclipse.jdt.core.IType;
import org.eclipse.jst.ws.internal.cxf.core.model.Java2WSDataModel;
import org.eclipse.jst.ws.internal.cxf.creation.core.CXFCreationCoreMessages;
import org.eclipse.jst.ws.internal.cxf.creation.core.CXFCreationCorePlugin;
import org.eclipse.jst.ws.jaxws.core.utils.JDTUtils;
import org.eclipse.wst.common.frameworks.datamodel.AbstractDataModelOperation;

public class Java2WSValidateInputCommand extends AbstractDataModelOperation {
    
    private Java2WSDataModel model;

    public Java2WSValidateInputCommand(Java2WSDataModel model) {
        this.model = model;
    }

    @Override
    public IStatus execute(IProgressMonitor monitor, IAdaptable info) throws ExecutionException {
        IStatus status = Status.OK_STATUS;
        IJavaProject javaProject = JDTUtils.getJavaProject(model.getProjectName());
        if (javaProject != null) {
            IType type = JDTUtils.getType(javaProject, model.getJavaStartingPoint());
            if (type == null || !type.exists()) {
                status = new Status(IStatus.ERROR, CXFCreationCorePlugin.PLUGIN_ID, 
                        CXFCreationCoreMessages.bind(CXFCreationCoreMessages.JAVA2WS_SERVICE_IMPL_NOT_FOUND,
                                new Object[] {model.getJavaStartingPoint(), model.getProjectName()}));
            }
            if (type.isBinary()) {
                status = new Status(IStatus.ERROR, CXFCreationCorePlugin.PLUGIN_ID,
                        CXFCreationCoreMessages.JAVA2WS_SERVICE_IMPL_NOT_BINARY);
            }
        }
        return status;
    }
}