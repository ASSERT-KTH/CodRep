if (entry.getPath().isPrefixOf(source.getPath())) {

/*******************************************************************************
 * Copyright (c) 2008, 2009 28msec Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     Gabriel Petrovay (28msec) - initial API and implementation
 *******************************************************************************/
package org.eclipse.wst.xquery.internal.launching;

import java.util.List;

import org.eclipse.core.resources.IMarker;
import org.eclipse.core.resources.ResourcesPlugin;
import org.eclipse.core.runtime.CoreException;
import org.eclipse.dltk.compiler.problem.DefaultProblem;
import org.eclipse.dltk.compiler.problem.IProblem;
import org.eclipse.dltk.compiler.problem.IProblemReporter;
import org.eclipse.dltk.compiler.problem.ProblemCollector;
import org.eclipse.dltk.core.DLTKCore;
import org.eclipse.dltk.core.IBuildpathEntry;
import org.eclipse.dltk.core.IModelElement;
import org.eclipse.dltk.core.IScriptModelMarker;
import org.eclipse.dltk.core.IScriptProject;
import org.eclipse.dltk.core.ISourceModule;
import org.eclipse.dltk.core.ModelException;
import org.eclipse.dltk.core.builder.IBuildContext;
import org.eclipse.dltk.core.builder.IBuildParticipant;
import org.eclipse.dltk.launching.IInterpreterInstall;
import org.eclipse.dltk.launching.ScriptRuntime;
import org.eclipse.wst.xquery.core.semantic.ISemanticValidator;
import org.eclipse.wst.xquery.core.semantic.SemanticCheckError;
import org.eclipse.wst.xquery.launching.ISemanticValidatingInterpreterInstall;

public class XQDTSemanticBuilder implements IBuildParticipant {

    public void build(IBuildContext context) throws CoreException {
        if (context.getBuildType() == IBuildContext.INCREMENTAL_BUILD) {
            ISourceModule source = context.getSourceModule();
            if (!isInBuildpath(source)) {
                return;
            }

            IProblemReporter reporter = context.getProblemReporter();
            if (reporter instanceof ProblemCollector) {
                ProblemCollector pc = (ProblemCollector)reporter;
                List<IProblem> problems = pc.getErrors();
                for (IProblem problem : problems) {
                    if (problem.getID() == IProblem.Syntax) {
                        return;
                    }
                }
            }

            List<SemanticCheckError> errors = check(source);
            if (errors != null) {
                for (SemanticCheckError error : errors) {
                    String fileName = error.getOriginatingFileName();
                    if (fileName.equals(source.getPath().toString())) {
                        context.getProblemReporter().reportProblem(error);
                    } else {
                        IModelElement element = DLTKCore.create(ResourcesPlugin.getWorkspace().getRoot().findMember(
                                fileName));
                        if (element instanceof ISourceModule) {
                            ISourceModule module = (ISourceModule)element;
                            createMarker(module, error);
                        }
                    }
                }
            }
        }
    }

    private void createMarker(ISourceModule module, SemanticCheckError error) throws CoreException {
        IMarker marker = module.getResource().createMarker(DefaultProblem.MARKER_TYPE_PROBLEM);
        marker.setAttribute(IMarker.LINE_NUMBER, error.getSourceLineNumber() + 1);
        marker.setAttribute(IMarker.MESSAGE, error.getMessage());
        marker.setAttribute(IMarker.SEVERITY, IMarker.SEVERITY_ERROR);
        marker.setAttribute(IMarker.PRIORITY, IMarker.PRIORITY_NORMAL);
        marker.setAttribute(IMarker.CHAR_START, error.getSourceStart());
        marker.setAttribute(IMarker.CHAR_END, error.getSourceEnd());
        if (error.getID() != 0) {
            marker.setAttribute(IScriptModelMarker.ID, error.getID());
        }
    }

    private boolean isInBuildpath(ISourceModule source) throws ModelException {
        IScriptProject project = source.getScriptProject();
        IBuildpathEntry[] entries = project.getRawBuildpath();
        for (IBuildpathEntry entry : entries) {
            if (entry.getPath().equals(source.getParent().getPath())) {
                return true;
            }
        }
        return false;
    }

    public List<SemanticCheckError> check(ISourceModule module) throws CoreException {
        IInterpreterInstall install = ScriptRuntime.getInterpreterInstall(module.getScriptProject());
        if (install instanceof ISemanticValidatingInterpreterInstall) {
            ISemanticValidator validator = ((ISemanticValidatingInterpreterInstall)install).getSemanticValidator();
            return validator.check(module);
        }
        return null;
    }

}