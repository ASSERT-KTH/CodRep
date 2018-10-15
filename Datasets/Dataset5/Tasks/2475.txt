showInfo(Messages.signaturesView, Messages.noSignaturesInDocument);

/*******************************************************************************
 * Copyright (c) 2008 Dominik Schadow - http://www.xml-sicherheit.de
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     Dominik Schadow - initial API and implementation
 *******************************************************************************/
package org.eclipse.wst.xml.security.core.actions;

import java.util.ArrayList;

import org.apache.xml.security.keys.keyresolver.KeyResolverException;
import org.apache.xml.security.signature.XMLSignatureException;
import org.eclipse.core.resources.IFile;
import org.eclipse.jface.action.IAction;
import org.eclipse.jface.viewers.ISelection;
import org.eclipse.jface.viewers.IStructuredSelection;
import org.eclipse.osgi.util.NLS;
import org.eclipse.ui.IViewPart;
import org.eclipse.ui.IWorkbenchPage;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.texteditor.ITextEditor;
import org.eclipse.wst.xml.security.core.verify.SignatureView;
import org.eclipse.wst.xml.security.core.verify.VerificationResult;
import org.eclipse.wst.xml.security.core.verify.VerifyDocument;

/**
 * <p>Action class used to start the <b>XML Signatures</b> View of the XML Security Tools to
 * verify all XML Signatures contained in the selected XML document.</p>
 *
 * @author Dominik Schadow
 * @version 0.5.0
 */
public class VerifyNewAction extends XmlSecurityActionAdapter {
    /** Active editor. */
    private ITextEditor editor = null;
    /** The file to verify. */
    private IFile file = null;
    /** Error message for the logfile. */
    private static final String ERROR_TEXT = "An error occured during verification"; //$NON-NLS-1$
    /** Action type. */
    private static final String ACTION = "verify";

    /**
     * Called when the selection in the active workbench part changes.
     *
     * @param action The executed action
     * @param selection The selection
     */
    public void selectionChanged(final IAction action, final ISelection selection) {
        if (selection instanceof IStructuredSelection) {
            file = (IFile) ((IStructuredSelection) selection).getFirstElement();
        }
    }

    /**
     * Called when clicked on the <i>New Verification...</i> entry in the plug-ins context menu.
     *
     * @param action The IAction
     */
    public void run(final IAction action) {
        createVerification();
    }

    /**
     * Takes the resource (selected file or editor content) and verifies all contained signatures.
     * The selected XML document is not changed at all.
     */
    private void createVerification() {
        VerifyDocument verify = new VerifyDocument();
        ArrayList<VerificationResult> results = new ArrayList<VerificationResult>();

        try {
            if (file != null) { // call in view
                results = verify.verify(file.getLocation().toString());
            } else { // call in editor
                if (editor.isDirty()) {
                    saveEditorContent(editor);
                }

                file = (IFile) editor.getEditorInput().getAdapter(IFile.class);
                if (file != null) {
                    results = verify.verify(file.getLocation().toString());
                } else {
                    showInfo(Messages.verificationImpossible,
                        NLS.bind(Messages.protectedDoc, ACTION));
                }
            }

            if (results.size() == 0) {
                showInfo(Messages.refreshImpossible, Messages.noSignaturesInDocument);
            }

            // show results
            IWorkbenchPage page = PlatformUI.getWorkbench().getActiveWorkbenchWindow().getActivePage();
            IViewPart vp = page.showView(SignatureView.ID);
            if (vp instanceof SignatureView) {
                ((SignatureView) vp).setInput(results);
            }
        } catch (XMLSignatureException xmlse) {
            showError(Messages.error, Messages.invalidValueElement + xmlse.getLocalizedMessage());
        } catch (KeyResolverException kre) {
            showError(Messages.error, Messages.invalidCertificate + kre.getLocalizedMessage());
        } catch (Exception ex) {
            showErrorDialog(Messages.error, Messages.verificationError, ex);
            log(ERROR_TEXT, ex);
        }
    }
}