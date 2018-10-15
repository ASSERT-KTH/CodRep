Verification.showVerificationResult(result);

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

import java.lang.reflect.InvocationTargetException;
import java.util.ArrayList;

import org.apache.xml.security.keys.keyresolver.KeyResolverException;
import org.apache.xml.security.signature.XMLSignatureException;
import org.eclipse.core.commands.AbstractHandler;
import org.eclipse.core.commands.ExecutionEvent;
import org.eclipse.core.commands.ExecutionException;
import org.eclipse.core.resources.IFile;
import org.eclipse.core.resources.ResourcesPlugin;
import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.jface.operation.IRunnableWithProgress;
import org.eclipse.jface.preference.IPreferenceStore;
import org.eclipse.jface.viewers.ISelection;
import org.eclipse.jface.viewers.IStructuredSelection;
import org.eclipse.osgi.util.NLS;
import org.eclipse.ui.IEditorPart;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.handlers.HandlerUtil;
import org.eclipse.wst.xml.security.core.verify.VerificationResult;
import org.eclipse.wst.xml.security.core.verify.VerifySignature;
import org.eclipse.wst.xml.security.ui.XSTUIPlugin;
import org.eclipse.wst.xml.security.ui.dialogs.MissingPreferenceDialog;
import org.eclipse.wst.xml.security.ui.preferences.PreferenceConstants;
import org.eclipse.wst.xml.security.ui.utils.Utils;
import org.eclipse.wst.xml.security.ui.verify.Verification;

/**
 * <p>Command used to start the verification of the given <b>XML Signature</b> with predefined
 * settings defined in the preferences (<b>Quick Verification</b>).</p>
 *
 * @author Dominik Schadow
 * @version 0.5.0
 */
public class QuickVerificationCommand extends AbstractHandler {
    /** Signature ID. */
    private String signatureId;
    /** All required preferences are available. */
    private boolean preferencesComplete = false;
    private ExecutionEvent event;
    /** The file to verify. */
    private IFile file = null;

    public Object execute(ExecutionEvent event) throws ExecutionException {
        this.event = event;

        getPreferenceValues();

        if (checkPreferences()) {
            try {
                createVerification();
            } catch (XMLSignatureException xmlse) {
                Utils.showErrorDialog(HandlerUtil.getActiveShell(event), Messages.QuickVerificationCommand_0,
                        Messages.QuickVerificationCommand_1, xmlse);
            } catch (KeyResolverException kre) {
                Utils.showErrorDialog(HandlerUtil.getActiveShell(event), Messages.QuickVerificationCommand_0,
                        Messages.QuickVerificationCommand_2, kre);
            } catch (Exception ex) {
                Utils.showErrorDialog(HandlerUtil.getActiveShell(event), Messages.QuickVerificationCommand_0,
                        Messages.QuickVerificationCommand_3, ex);
                Utils.log("An error occured during quick verification", ex); //$NON-NLS-1$
            }
        }

        return null;
    }

    /**
     * Verifies the XML document with the stored settings.
     *
     * @throws Exception to indicate any exceptional condition
     */
    private void createVerification() throws Exception {
        VerifySignature verify = new VerifySignature();
        ArrayList<VerificationResult> results = new ArrayList<VerificationResult>();

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
        } else {
            ISelection selection = HandlerUtil.getCurrentSelection(event);
            if (selection instanceof IStructuredSelection) {
                file = (IFile) ((IStructuredSelection) selection).getFirstElement();
            }
        }

        if (file != null && file.isAccessible()) {
            results = verify.verify(file.getLocation().toString(), signatureId);
        } else {
            MessageDialog.openInformation(HandlerUtil.getActiveShell(event), Messages.QuickVerificationCommand_0,
                    NLS.bind(Messages.RemoveReadOnlyFlag, Messages.QuickVerificationCommand_5));
        }

        if (results.size() == 1) {
            VerificationResult result = (VerificationResult) results.get(0);
            if (result.getSignature() != null) {
                Verification.showVerificationResult(result, HandlerUtil.getActiveShell(event));
            } else {
                MessageDialog.openError(HandlerUtil.getActiveShell(event), Messages.QuickVerificationCommand_0,
                        NLS.bind(Messages.QuickVerificationCommand_4, signatureId));
            }
        } else {
            MessageDialog.openError(HandlerUtil.getActiveShell(event), Messages.QuickVerificationCommand_0,
                    NLS.bind(Messages.QuickVerificationCommand_4, signatureId));
        }
    }

    /**
     * Determines the preference values for <i>Quick Verification</i>.
     */
    private void getPreferenceValues() {
        IPreferenceStore store = XSTUIPlugin.getDefault().getPreferenceStore();
        signatureId = store.getString(PreferenceConstants.SIGN_ID);
    }

    /**
     * Checks if the preferences contain all necessary information. Shows a dialog with a warning
     * message and a link to the preference page.<br/> If the preference dialog was closed with the
     * OK button the necessary preference informations are automatically verified again.
     *
     * @return Preferences OK or not
     */
    private boolean checkPreferences() {
        final String prefId = "org.eclipse.wst.xml.security.ui.preferences.Signatures"; //$NON-NLS-1$
        int result = 2;

        if (signatureId == null || "".equals(signatureId)) { //$NON-NLS-1$
            MissingPreferenceDialog dialog = new MissingPreferenceDialog(HandlerUtil.getActiveShell(event),
                    Messages.QuickVerificationCommand_0, NLS.bind(Messages.MissingParameter,
                            Messages.MissingSignatureId), prefId);
            result = dialog.open();
        } else {
            preferencesComplete = true;
        }

        if (result == MissingPreferenceDialog.OK) {
            preferencesComplete = false;
            getPreferenceValues();
            checkPreferences();
        }

        return preferencesComplete;
    }
}