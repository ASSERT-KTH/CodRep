if (javaElement != null && javaElement instanceof ICompilationUnit) {

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
package org.eclipse.jst.ws.internal.jaxws.ui.annotations.correction;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

import org.eclipse.core.resources.IFile;
import org.eclipse.core.resources.IMarker;
import org.eclipse.core.resources.IResource;
import org.eclipse.core.runtime.CoreException;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.jdt.apt.core.util.EclipseMessager;
import org.eclipse.jdt.core.CorrectionEngine;
import org.eclipse.jdt.core.ICompilationUnit;
import org.eclipse.jdt.core.IJavaElement;
import org.eclipse.jdt.core.IJavaModelMarker;
import org.eclipse.jdt.core.JavaCore;
import org.eclipse.jdt.internal.ui.text.correction.AssistContext;
import org.eclipse.jdt.internal.ui.text.correction.JavaCorrectionProcessor;
import org.eclipse.jdt.internal.ui.text.correction.ProblemLocation;
import org.eclipse.jdt.internal.ui.text.correction.CorrectionMarkerResolutionGenerator.CorrectionMarkerResolution;
import org.eclipse.jdt.ui.text.java.CompletionProposalComparator;
import org.eclipse.jdt.ui.text.java.IInvocationContext;
import org.eclipse.jdt.ui.text.java.IJavaCompletionProposal;
import org.eclipse.jdt.ui.text.java.IProblemLocation;
import org.eclipse.jst.ws.internal.jaxws.ui.JAXWSUIPlugin;
import org.eclipse.ui.IEditorInput;
import org.eclipse.ui.IMarkerResolution;
import org.eclipse.ui.IMarkerResolutionGenerator2;
import org.eclipse.ui.part.FileEditorInput;

@SuppressWarnings("restriction")
public class APTCompileProblemMarkerResolutionGenerator implements IMarkerResolutionGenerator2 {

	private final static IMarkerResolution[] NO_RESOLUTIONS = new IMarkerResolution[0];

	public boolean hasResolutions(IMarker marker) {
		int id = marker.getAttribute(IJavaModelMarker.ID, -1);
        if (id == EclipseMessager.APT_QUICK_FIX_PROBLEM_ID) {
            return true;
        }
		return false;
	}
	
	@SuppressWarnings("unchecked")
	public IMarkerResolution[] getResolutions(IMarker marker) {
		if (!hasResolutions(marker)) {
			return NO_RESOLUTIONS;
		}
		
		ICompilationUnit compilationUnit = getCompilationUnit(marker);
		
		if (compilationUnit != null) {
			IEditorInput editorInput = new FileEditorInput((IFile) compilationUnit.getResource());
			if (editorInput != null) {
				IProblemLocation problemLocation = createProblemLocation(marker);
				if (problemLocation != null) {
					IInvocationContext invocationContext = new AssistContext(compilationUnit,
							problemLocation.getOffset(), problemLocation.getLength());
					
					List<IJavaCompletionProposal> completionProposals = new ArrayList<IJavaCompletionProposal>();
					
					IStatus status = JavaCorrectionProcessor.collectCorrections(invocationContext, 
							new IProblemLocation[] { problemLocation }, completionProposals);
                    
					if (status.isOK()) {
                        Collections.sort(completionProposals, new CompletionProposalComparator());

    					IMarkerResolution[] markerResolutions = new IMarkerResolution[completionProposals.size()];
    					for (int i= 0; i < completionProposals.size(); i++) {
    						markerResolutions[i] = new CorrectionMarkerResolution(compilationUnit, 
    								problemLocation.getOffset(), problemLocation.getLength(), 
    								completionProposals.get(i), marker);
    					}
    					return markerResolutions;
                    }
				}
			}
		}
		return NO_RESOLUTIONS;
	}

	private IProblemLocation createProblemLocation(IMarker marker) {
		try {
			int id = marker.getAttribute(IJavaModelMarker.ID, -1);
			int offset = marker.getAttribute(IMarker.CHAR_START, -1);
			int end = marker.getAttribute(IMarker.CHAR_END, -1);
			int severity = marker.getAttribute(IMarker.SEVERITY, IMarker.SEVERITY_INFO);
			String[] arguments = CorrectionEngine.getProblemArguments(marker);
			String markerType = marker.getType();
			if (id != -1 && offset != -1 && end != -1 && arguments != null) {
				int length = end - offset;
				boolean isError = (severity == IMarker.SEVERITY_ERROR);
				return new ProblemLocation(offset, length, id, arguments, isError, markerType);
			}
		} catch (CoreException ce) {
			JAXWSUIPlugin.log(ce.getStatus());
		}
		return null;
	}

	private ICompilationUnit getCompilationUnit(IMarker marker) {
		IResource resource = marker.getResource();
		if (resource instanceof IFile && resource.isAccessible()) {
			IJavaElement javaElement = JavaCore.create((IFile) resource);
			if (javaElement instanceof ICompilationUnit) {
				return (ICompilationUnit) javaElement;
			}
		}
		return null;
	}
}