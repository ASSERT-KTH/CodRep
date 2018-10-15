public static final String getMARKER_TYPE() {

/*******************************************************************************
 * Copyright (c) 2005, 2007 committers of openArchitectureWare and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     committers of openArchitectureWare - initial API and implementation
 *******************************************************************************/

package org.eclipse.xtend.shared.ui.core.builder;

import java.lang.reflect.InvocationTargetException;

import org.eclipse.core.filebuffers.FileBuffers;
import org.eclipse.core.filebuffers.ITextFileBuffer;
import org.eclipse.core.filebuffers.ITextFileBufferManager;
import org.eclipse.core.filebuffers.LocationKind;
import org.eclipse.core.resources.IFile;
import org.eclipse.core.resources.IMarker;
import org.eclipse.core.resources.IResource;
import org.eclipse.core.runtime.CoreException;
import org.eclipse.core.runtime.IPath;
import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.core.runtime.NullProgressMonitor;
import org.eclipse.jface.text.BadLocationException;
import org.eclipse.jface.text.IDocument;
import org.eclipse.ui.actions.WorkspaceModifyOperation;
import org.eclipse.xtend.expression.AnalysationIssue;
import org.eclipse.xtend.shared.ui.Activator;
import org.eclipse.xtend.shared.ui.internal.XtendLog;

public class XtendXpandMarkerManager {

    static final String getMARKER_TYPE() {
        return Activator.getId() + ".problem";
    }

    public static void addMarker(final IFile file, final AnalysationIssue issue) {
        try {
            final IMarker marker = file.createMarker(getMARKER_TYPE());
            final int severity = IMarker.SEVERITY_ERROR;
            int start = -1, end = -1;
            if (issue.getElement() != null) {
                start = issue.getElement().getStart();
                end = issue.getElement().getEnd();
            }
            internalAddMarker(file, marker, issue.getMessage(), severity, start, end);
        } catch (final CoreException e) {
        }
    }

    public static void addErrorMarker(final IFile file, final String message, final int severity, final int start,
            final int end) {
        try {
            final IMarker marker = file.createMarker(getMARKER_TYPE());
            internalAddMarker(file, marker, message, severity, start, end);
        } catch (final CoreException e) {
            XtendLog.logError(e);
        }
    }

    public static void addWarningMarker(final IFile file, final String message, final int severity, final int start,
            final int end) {
        try {
            final IMarker marker = file.createMarker(getMARKER_TYPE());
            internalAddMarker(file, marker, message, severity, start, end);
        } catch (final CoreException e) {
        }
    }

    private final static void internalAddMarker(final IFile file, final IMarker marker, final String message,
            final int severity, final int start, final int end) {
        try {
            new WorkspaceModifyOperation() {

                @Override
                protected void execute(final IProgressMonitor monitor) throws CoreException, InvocationTargetException,
                        InterruptedException {

                    try {
                        marker.setAttribute(IMarker.MESSAGE, message);
                        marker.setAttribute(IMarker.SEVERITY, severity);
                        int s = start;
                        if (start == -1) {
                            s = 1;
                        }
                        int e = end;
                        if (end <= start) {
                            e = start + 1;
                        }
                        marker.setAttribute(IMarker.CHAR_START, s);
                        marker.setAttribute(IMarker.CHAR_END, e);
                        final ITextFileBufferManager mgr = FileBuffers.getTextFileBufferManager();
                        if (mgr != null) {
                            final IPath location = file.getFullPath();
                            try {
                                mgr.connect(location,LocationKind.NORMALIZE, new NullProgressMonitor());
                                final ITextFileBuffer buff = mgr.getTextFileBuffer(file.getFullPath(), LocationKind.NORMALIZE);
                                if (buff != null) {
                                    final IDocument doc = buff.getDocument();
                                    final int line = doc.getLineOfOffset(start);
                                    if (line > 0) {
                                        marker.setAttribute(IMarker.LINE_NUMBER, doc.getLineOfOffset(start));
                                        marker.setAttribute(IMarker.LOCATION, "line: " + line);
                                    }
                                }
                            } finally {
                                mgr.disconnect(location,LocationKind.NORMALIZE, new NullProgressMonitor());
                            }
                        }
                    } catch (final CoreException e) {
                    	XtendLog.logError(e);
                    } catch (final BadLocationException e) {
                    	XtendLog.logError(e);
                    }
                }
            }.run(new NullProgressMonitor());
        } catch (final Exception e) {
            XtendLog.logError(e);
        }
    }

    public static void deleteMarkers(final IResource file) {
        try {
        	if (file.exists()) {
                new WorkspaceModifyOperation() {

                    @Override
                    protected void execute(final IProgressMonitor monitor) throws CoreException,
                            InvocationTargetException, InterruptedException {
                        file.deleteMarkers(getMARKER_TYPE(), true, IResource.DEPTH_INFINITE);
                    }

                }.run(new NullProgressMonitor());
            }
        } catch (final Exception ce) {
            XtendLog.logError(ce);
        }
    }
}