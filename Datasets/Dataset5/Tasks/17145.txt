CXFCreationCorePlugin.log(ce.getStatus());

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

import java.lang.reflect.InvocationTargetException;
import java.util.List;
import java.util.Map;

import org.eclipse.core.commands.ExecutionException;
import org.eclipse.core.resources.IFile;
import org.eclipse.core.runtime.CoreException;
import org.eclipse.core.runtime.IAdaptable;
import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Status;
import org.eclipse.jdt.core.IMethod;
import org.eclipse.jdt.core.IType;
import org.eclipse.jdt.core.dom.SingleVariableDeclaration;
import org.eclipse.jst.ws.annotations.core.utils.AnnotationUtils;
import org.eclipse.jst.ws.internal.cxf.core.model.Java2WSDataModel;
import org.eclipse.jst.ws.internal.cxf.core.utils.CXFModelUtils;
import org.eclipse.jst.ws.internal.cxf.creation.core.CXFCreationCorePlugin;
import org.eclipse.jst.ws.jaxws.core.utils.JDTUtils;
import org.eclipse.ltk.core.refactoring.Change;
import org.eclipse.ltk.core.refactoring.IUndoManager;
import org.eclipse.ltk.core.refactoring.RefactoringCore;
import org.eclipse.ltk.core.refactoring.RefactoringStatus;
import org.eclipse.ltk.core.refactoring.TextFileChange;
import org.eclipse.text.edits.MultiTextEdit;
import org.eclipse.wst.common.frameworks.datamodel.AbstractDataModelOperation;

/**
 * @author sclarke
 */
public class JAXWSAnnotateJavaCommand extends AbstractDataModelOperation {
    private int numberOfChanges = 0;

    private Java2WSDataModel model;
    private IType javaClassType;
    private IType javaInterfaceType;
    
    public JAXWSAnnotateJavaCommand(Java2WSDataModel model) {
        this.model = model;
    }

    @Override
    public IStatus execute(IProgressMonitor monitor, IAdaptable info) throws ExecutionException {
        IStatus status = Status.OK_STATUS;
        try {
            if (model.isUseServiceEndpointInterface()) {
                annotateInterface(monitor);

                if (model.getFullyQualifiedJavaClassName() != null) {
                    annotateSEIClass(monitor);
                }
            } else if (model.getFullyQualifiedJavaClassName() != null) {
                annotateClass(monitor);
            }
        } catch (CoreException ce) {
            status = ce.getStatus();
            CXFCreationCorePlugin.log(status);
        } catch (InvocationTargetException ite) {
            status = new Status(IStatus.ERROR, CXFCreationCorePlugin.PLUGIN_ID, ite.getLocalizedMessage());
            CXFCreationCorePlugin.log(status);
        } catch (InterruptedException ie) {
            status = new Status(IStatus.ERROR, CXFCreationCorePlugin.PLUGIN_ID, ie.getLocalizedMessage());
            CXFCreationCorePlugin.log(status);
        } 
        return status;
    }
    
    private void annotateInterface(IProgressMonitor monitor) throws CoreException, InvocationTargetException,
            InterruptedException {
        javaInterfaceType = JDTUtils.getType(JDTUtils.getJavaProject(model.getProjectName()), model
                .getFullyQualifiedJavaInterfaceName());

        TextFileChange textFileChange = new TextFileChange("Annotating Interface", 
                (IFile)javaInterfaceType.getResource());
        MultiTextEdit multiTextEdit = new MultiTextEdit();
        textFileChange.setEdit(multiTextEdit);

        CXFModelUtils.getWebServiceAnnotationChange(javaInterfaceType, model, textFileChange);

        IMethod[] typeMethods = JDTUtils.getPublicMethods(javaInterfaceType);
        for (int i = 0; i < typeMethods.length; i++) {
            IMethod method = typeMethods[i];
            Map<String, Boolean> methodAnnotationMap = model.getMethodMap().get(method);
            if (methodAnnotationMap.get(CXFModelUtils.WEB_METHOD)) {
                CXFModelUtils.getWebMethodAnnotationChange(javaInterfaceType, method, 
                		textFileChange);
            }
            if (methodAnnotationMap.get(CXFModelUtils.REQUEST_WRAPPER)) {
                CXFModelUtils.getRequestWrapperAnnotationChange(javaInterfaceType, method, 
                		textFileChange);
            }
            if (methodAnnotationMap.get(CXFModelUtils.RESPONSE_WRAPPER)) {
                CXFModelUtils.getResponseWrapperAnnotationChange(javaInterfaceType, method, 
                		textFileChange);
            }
            if (methodAnnotationMap.get(CXFModelUtils.WEB_PARAM)) {
                List<SingleVariableDeclaration> parameters = AnnotationUtils.getMethodParameters(
                        javaInterfaceType, method);
                for (SingleVariableDeclaration parameter : parameters) {
                    CXFModelUtils.getWebParamAnnotationChange(javaInterfaceType, method, parameter, 
                    		textFileChange);
                }
            } 
        }
        
        CXFModelUtils.getImportsChange(javaInterfaceType.getCompilationUnit(), model, 
        		textFileChange, false);
        
        executeChange(monitor, textFileChange);
    }
    
    private void annotateClass(IProgressMonitor monitor) throws CoreException, InvocationTargetException,
            InterruptedException {
        javaClassType = JDTUtils.getType(JDTUtils.getJavaProject(model.getProjectName()), model
                .getFullyQualifiedJavaClassName());

        TextFileChange textFileChange = new TextFileChange("Annotating Class", 
                (IFile)javaClassType.getCompilationUnit().getResource());
        MultiTextEdit multiTextEdit = new MultiTextEdit();
        textFileChange.setEdit(multiTextEdit);
        
        CXFModelUtils.getWebServiceAnnotationChange(javaClassType, model, textFileChange);

        IMethod[] typeMethods = JDTUtils.getPublicMethods(javaClassType);
        for (int i = 0; i < typeMethods.length; i++) {
            IMethod method = typeMethods[i];
            Map<String, Boolean> methodAnnotationMap = model.getMethodMap().get(method);
            if (methodAnnotationMap.get(CXFModelUtils.WEB_METHOD)) {
                CXFModelUtils.getWebMethodAnnotationChange(javaClassType, method, textFileChange);
            }
            if (methodAnnotationMap.get(CXFModelUtils.REQUEST_WRAPPER)) {
                CXFModelUtils.getRequestWrapperAnnotationChange(javaClassType, method, 
                		textFileChange);
            }
            if (methodAnnotationMap.get(CXFModelUtils.RESPONSE_WRAPPER)) {
                CXFModelUtils.getResponseWrapperAnnotationChange(javaClassType, method, 
                		textFileChange);
            }
            if (methodAnnotationMap.get(CXFModelUtils.WEB_PARAM)) {
                List<SingleVariableDeclaration> parameters = AnnotationUtils.getMethodParameters(
                        javaClassType, method);
                for (SingleVariableDeclaration parameter : parameters) {
                    CXFModelUtils.getWebParamAnnotationChange(javaClassType, method, parameter, 
                    		textFileChange);
                }
            } 
        }
        
        CXFModelUtils.getImportsChange(javaClassType.getCompilationUnit(), model, 
        		textFileChange, false);
        
        executeChange(monitor, textFileChange);
    }

    private void annotateSEIClass(IProgressMonitor monitor) throws CoreException, InvocationTargetException,
            InterruptedException {
        javaClassType = JDTUtils.getType(JDTUtils.getJavaProject(model.getProjectName()), model
                .getFullyQualifiedJavaClassName());

        TextFileChange textFileChange = new TextFileChange("Annotation Changes",
                (IFile)javaClassType.getCompilationUnit().getResource());
        MultiTextEdit multiTextEdit = new MultiTextEdit();
        textFileChange.setEdit(multiTextEdit);

        CXFModelUtils.getWebServiceAnnotationChange(javaClassType, model, textFileChange);
        
        CXFModelUtils.getImportsChange(javaClassType.getCompilationUnit(), model, 
        		textFileChange, true);

        executeChange(monitor, textFileChange);
    }
    
    private void executeChange(IProgressMonitor monitor, Change change) {
        if (change == null) {
            return;
        }

        IUndoManager manager= RefactoringCore.getUndoManager();
        boolean successful = false;
        Change undoChange = null;
        try {
            change.initializeValidationData(monitor);
            RefactoringStatus valid = change.isValid(monitor);
            if (valid.isOK()) {
                manager.aboutToPerformChange(change);
                undoChange = change.perform(monitor);
                successful = true;
                numberOfChanges++;
            }
        } catch (CoreException ce) {
            ce.printStackTrace();
        } finally {
            manager.changePerformed(change, successful);
        }
        if (undoChange != null) {
            undoChange.initializeValidationData(monitor);
            manager.addUndo(undoChange.getName(), undoChange);
        }
    }
    
    @Override
    public IStatus undo(IProgressMonitor monitor, IAdaptable info) throws ExecutionException {
        IStatus status = Status.OK_STATUS;
        
        IUndoManager manager= RefactoringCore.getUndoManager();

        if (manager.anythingToUndo()) {
            try {
                for (int i = 0; i < numberOfChanges; i++) {
                    manager.performUndo(null, monitor);
                }
            } catch (CoreException ce) {
                status = ce.getStatus();
                CXFCreationCorePlugin.log(status);
            }
        }
        return status;
    }
}