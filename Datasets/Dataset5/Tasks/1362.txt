document.set(new String(outputBytes, IXMLSecurityConstants.CHARSET));

/*******************************************************************************
 * Copyright (c) 2009 Dominik Schadow - http://www.xml-sicherheit.de
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     Dominik Schadow - initial API and implementation
 *******************************************************************************/
package org.eclipse.wst.xml.security.ui.commands;

import java.io.ByteArrayInputStream;
import java.io.InputStream;
import java.lang.reflect.InvocationTargetException;

import org.apache.xml.security.c14n.Canonicalizer;
import org.eclipse.core.commands.AbstractHandler;
import org.eclipse.core.commands.ExecutionEvent;
import org.eclipse.core.commands.ExecutionException;
import org.eclipse.core.resources.IFile;
import org.eclipse.core.resources.ResourcesPlugin;
import org.eclipse.core.runtime.IPath;
import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.jface.operation.IRunnableWithProgress;
import org.eclipse.jface.preference.IPreferenceStore;
import org.eclipse.jface.text.IDocument;
import org.eclipse.jface.viewers.ISelection;
import org.eclipse.jface.viewers.IStructuredSelection;
import org.eclipse.osgi.util.NLS;
import org.eclipse.ui.IEditorDescriptor;
import org.eclipse.ui.IEditorPart;
import org.eclipse.ui.IWorkbenchPage;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.handlers.HandlerUtil;
import org.eclipse.ui.part.FileEditorInput;
import org.eclipse.wst.xml.security.core.canonicalize.Canonicalization;
import org.eclipse.wst.xml.security.ui.XSTUIPlugin;
import org.eclipse.wst.xml.security.ui.preferences.PreferenceConstants;
import org.eclipse.wst.xml.security.ui.utils.IXMLSecurityConstants;
import org.eclipse.wst.xml.security.ui.utils.Utils;

/**
 * <p>Command used to start the <b>XML Canonicalization</b> for a new XML Canonicalization for the selected XML document.
 * The canonicalization process differs depending on whether editor content or a file via a view should be canonicalized.</p>
 *
 * <p>This version removes the XML comments and replaces them with an empty line.</p>
 *
 * @author Dominik Schadow
 * @version 0.5.0
 */
public class NewCanonicalizationRemoveCommand extends AbstractHandler {
    /** Canonicalization version (exclusive or inclusive). */
    private String canonVersion;
    /** Canonicalization target (same or new document). */
    private String canonTarget;
    /** The file to canonicalize. */
    private IFile file = null;
    private ExecutionEvent event;

    public Object execute(ExecutionEvent event) throws ExecutionException {
        this.event = event;

        getPreferenceValues();

        createCanonicalization();

        return null;
    }

    private void createCanonicalization() {
        try {
            IDocument document = null;

            if (HandlerUtil.getActivePart(event) instanceof IEditorPart) {
                final IEditorPart editorPart = (IEditorPart) HandlerUtil.getActivePart(event);

                if (editorPart.isDirty()) {
                    if (null != editorPart.getTitle() && editorPart.getTitle().length() > 0) {
                        IRunnableWithProgress op = new IRunnableWithProgress() {
                            public void run(final IProgressMonitor monitor) {
                                editorPart.doSave(monitor);
                            }
                        };
                        try {
                            PlatformUI.getWorkbench().getProgressService().runInUI(XSTUIPlugin.getActiveWorkbenchWindow(),
                                    op, ResourcesPlugin.getWorkspace().getRoot());
                        } catch (InvocationTargetException ite) {
                            Utils.log("Error while saving editor content", ite); //$NON-NLS-1$
                        } catch (InterruptedException ie) {
                            Utils.log("Error while saving editor content", ie); //$NON-NLS-1$
                        }
                    } else {
                        editorPart.doSaveAs();
                    }
                }

                file = (IFile) editorPart.getEditorInput().getAdapter(IFile.class);
                document = (IDocument) editorPart.getAdapter(IDocument.class);
            } else {
                ISelection selection = HandlerUtil.getCurrentSelection(event);
                if (selection instanceof IStructuredSelection) {
                    file = (IFile) ((IStructuredSelection) selection).getFirstElement();
                }
            }

            if (file != null) {
                byte[] outputBytes = canonicalize(file.getContents());

                if (document != null) {
                    if (IXMLSecurityConstants.INTERNAL_CANONICALIZATION.equals(canonTarget)) {
                        document.set(new String(outputBytes, "UTF8")); //$NON-NLS-1$
                    } else {
                        IWorkbenchPage page = HandlerUtil.getActiveWorkbenchWindow(event).getActivePage();

                        if (page != null) {
                            IFile newFile = saveCanonicalizedFile(getCanonicalizedPath(), outputBytes);
                            IEditorDescriptor desc = PlatformUI.getWorkbench().getEditorRegistry().getDefaultEditor(newFile.getName());
                            page.openEditor(new FileEditorInput(newFile), desc.getId());
                        }
                    }
                } else {
                    if (IXMLSecurityConstants.INTERNAL_CANONICALIZATION.equals(canonTarget)) {
                        saveCanonicalizedFile(file.getLocation(), outputBytes);
                    } else {
                        saveCanonicalizedFile(getCanonicalizedPath(), outputBytes);
                    }
                }
            } else {
                MessageDialog.openInformation(HandlerUtil.getActiveShell(event), Messages.XMLCanonicalization,
                        NLS.bind(Messages.RemoveReadOnlyFlag, Messages.NewCanonicalizationRemoveCommand_0));
            }
        } catch (Exception ex) {
            Utils.showErrorDialog(HandlerUtil.getActiveShell(event), Messages.XMLCanonicalization,
                    Messages.ErrorDuringCanonicalization, ex);
            Utils.log("An error occured during canonicalization", ex); //$NON-NLS-1$
        }
    }

    /**
     * Determines the preference values for canonicalization.
     */
    private void getPreferenceValues() {
        IPreferenceStore store = XSTUIPlugin.getDefault().getPreferenceStore();

        canonVersion = store.getString(PreferenceConstants.CANON_TYPE);
        canonTarget = store.getString(PreferenceConstants.CANON_TARGET);
    }

    /**
     * Returns the path (with filename) for the canonicalized XML document. The new filename consists of the old
     * filename with an added <i>_canon</i> and the file extension <i>xml</i>. If the <i>_canon</i> is already added the
     * new filename consists of <i>_canon[x]</i> with a raising number starting with 2.
     *
     * @return The path of the new file
     */
    private IPath getCanonicalizedPath() {
        IPath path = file.getLocation().removeFileExtension();
        String filename = path.lastSegment();
        path = path.removeLastSegments(1);

        if (filename.endsWith("_canon")) { //$NON-NLS-1$
            filename += "[2].xml"; //$NON-NLS-1$
        } else if (filename.contains("_canon[")) { //$NON-NLS-1$
            int canonNumber = Integer.parseInt(filename.substring(filename.indexOf("[") + 1, filename.indexOf("]"))); //$NON-NLS-1$ //$NON-NLS-2$
            filename = filename.substring(0, filename.indexOf("[") + 1) + (canonNumber + 1) + "].xml"; //$NON-NLS-1$ //$NON-NLS-2$
        } else {
            filename += "_canon.xml"; //$NON-NLS-1$
        }

        path = path.append(filename);

        return path;
    }

    /**
     * Saves the canonicalized XML document in the active folder with the given file name.
     *
     * @param newFilePath The path and filename of the new canonicalized XML document
     * @param outputBytes The canonicalized data
     * @return The new file
     * @throws Exception to indicate any exceptional condition
     */
    private IFile saveCanonicalizedFile(final IPath newFilePath, final byte[] outputBytes) throws Exception {
        IFile newFile = ResourcesPlugin.getWorkspace().getRoot().getFileForLocation(newFilePath);

        if (newFile.exists()) {
            newFile.setContents(new ByteArrayInputStream(outputBytes), true, true, null);
        } else {
            newFile.create(new ByteArrayInputStream(outputBytes), true, null);
        }

        return newFile;
    }

    /**
     * Calls the canonicalization method of the Apache XML Security API and executes the canonicalization.
     *
     * @param stream The XML document to canonicalize as InputStream
     * @return The canonicalized XML
     * @throws Exception Exception during canonicalization
     */
    private byte[] canonicalize(final InputStream stream) throws Exception {
        Canonicalization canonicalization = new Canonicalization();

        return canonicalization.canonicalize(stream, getCanonicalizationAlgorithm());
    }

    /**
     * Determines the canonicalization algorithm (exclusive or inclusive) based on the preference selection. The
     * algorithm type always removes the comments. Version 1.1 is used in case of inclusive canonicalization.
     *
     * @return The canonicalization algorithm to use
     */
    private String getCanonicalizationAlgorithm() {
        String algorithm = ""; //$NON-NLS-1$

        if (IXMLSecurityConstants.EXCLUSIVE_CANONICALIZATION.equals(canonVersion)) {
            algorithm = Canonicalizer.ALGO_ID_C14N_EXCL_OMIT_COMMENTS;
        } else {
            algorithm = Canonicalizer.ALGO_ID_C14N11_OMIT_COMMENTS;
        }

        return algorithm;
    }
}