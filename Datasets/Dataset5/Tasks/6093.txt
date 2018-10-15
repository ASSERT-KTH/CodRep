signatureWizard.setKeyName(keyName);

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
package org.eclipse.wst.xml.security.core.actions;

import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.lang.reflect.InvocationTargetException;

import org.apache.xml.security.utils.XMLUtils;
import org.eclipse.core.resources.IFile;
import org.eclipse.core.resources.IProject;
import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.jface.action.IAction;
import org.eclipse.jface.dialogs.Dialog;
import org.eclipse.jface.operation.IRunnableWithProgress;
import org.eclipse.jface.preference.IPreferenceStore;
import org.eclipse.jface.text.IDocument;
import org.eclipse.jface.text.ITextSelection;
import org.eclipse.jface.viewers.ISelection;
import org.eclipse.jface.viewers.IStructuredSelection;
import org.eclipse.osgi.util.NLS;
import org.eclipse.ui.IEditorInput;
import org.eclipse.ui.IWorkbenchPart;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.texteditor.ITextEditor;
import org.eclipse.wst.xml.security.core.XmlSecurityPlugin;
import org.eclipse.wst.xml.security.core.preferences.PreferenceConstants;
import org.eclipse.wst.xml.security.core.sign.CreateSignature;
import org.eclipse.wst.xml.security.core.sign.Signature;
import org.eclipse.wst.xml.security.core.utils.Keystore;
import org.eclipse.wst.xml.security.core.utils.PasswordDialog;
import org.eclipse.wst.xml.security.core.utils.Utils;
import org.w3c.dom.Document;
import org.xml.sax.SAXParseException;

/**
 * <p>Action class used to create an <b>XML Signature</b> of the selected XML document (fragment) with
 * predefined settings defined in the preferences of the current workspace (Quick Signature).</p>
 *
 * @author Dominik Schadow
 * @version 0.5.0
 */
public class SignQuickAction extends XmlSecurityActionAdapter {
    /** Active editor. */
    private ITextEditor editor = null;
    /** The file to sign. */
    private IFile file = null;
    /** Document (-fragment) to sign. */
    private String resource;
    /** XPath expression to sign. */
    private String xpath = ""; //$NON-NLS-1$
    /** Signature type. */
    private String signatureType;
    /** Keystore. */
    private Keystore keystore;
    /** Keystore password. */
    private char[] keystorePassword;
    /** Key name. */
    private String keyName;
    /** Key password. */
    private char[] keyPassword;
    /** Canonicalization algorithm. */
    private String canonicalizationAlgorithm;
    /** Transformation algorithm. */
    private String transformationAlgorithm;
    /** Message digest algorithm. */
    private String messageDigestAlgorithm;
    /** Signature algorithm. */
    private String signatureAlgorithm;
    /** Signature ID. */
    private String signatureID;
    /** All necessary preferences are available. */
    private boolean completePrefs = false;
    /** Error message for the logfile. */
    private static final String ERROR_TEXT = "An error occured during quick signing"; //$NON-NLS-1$
    /** Action type. */
    private static final String ACTION = "sign";

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
     * Takes the selected file, selection or editor content and starts the XML Quick Digital
     * Signature. The returned signed XML document is not pretty printed because this would change
     * the hash value of the signed content and verification would fail.<br/> Before any operation
     * on the XML data, the preference store is searched for the necessary settings. Then these
     * settings are verified. If the settings are valid the sign operation begins. If not the user
     * has the possibility to provide valid information.
     *
     * @param action The IAction
     */
    public void run(final IAction action) {
        getPreferenceValues();

        if (checkPreferences()) {
            // Ask the user for the passwords
            PasswordDialog keystorePasswordDialog = new PasswordDialog(getShell(),
                    Messages.keystorePassword, Messages.enterKeystorePassword, ""); //$NON-NLS-3$
            if (keystorePasswordDialog.open() == Dialog.OK) {
                keystorePassword = keystorePasswordDialog.getValue().toCharArray();
            } else {
                return;
            }

            PasswordDialog privateKeyPasswordDialog = new PasswordDialog(getShell(),
                    Messages.keyPassword, Messages.enterKeyPassword, ""); //$NON-NLS-3$
            if (privateKeyPasswordDialog.open() == Dialog.OK) {
                keyPassword = privateKeyPasswordDialog.getValue().toCharArray();
            } else {
                return;
            }

            if (checkPasswords()) {
                try {
                    quickSign();
                } catch (SAXParseException spe) {
                    showError(Messages.parsingError, Messages.parsingErrorText
                            + spe.getLocalizedMessage());
                } catch (FileNotFoundException fnfe) {
                    showError(Messages.keystore, Messages.keystoreNotFound);
                } catch (IOException ioe) {
                    showError(Messages.keystore, Messages.keystoreError + ioe.getLocalizedMessage());
                } catch (Exception ex) {
                    showErrorDialog(Messages.error, Messages.signingError, ex);
                    log(ERROR_TEXT, ex);
                }
            }
        }
    }

    /**
     * Determines the preference values for <i>Quick Signature</i>.
     */
    private void getPreferenceValues() {
        IPreferenceStore store = XmlSecurityPlugin.getDefault().getPreferenceStore();
        resource = store.getString(PreferenceConstants.SIGN_RESOURCE);

        if (resource != null && resource.equals("xpath")) { //$NON-NLS-1$
            xpath = store.getString(PreferenceConstants.SIGN_XPATH);
        }

        signatureType = store.getString(PreferenceConstants.SIGN_TYPE);
        // FIXME
        keystore = null;//store.getString(PreferenceConstants.SIGN_KEYSTORE_FILE);
        keyName = store.getString(PreferenceConstants.SIGN_KEY_ALIAS);
        canonicalizationAlgorithm = store.getString(PreferenceConstants.SIGN_CANON);
        transformationAlgorithm = store.getString(PreferenceConstants.SIGN_TRANS);
        messageDigestAlgorithm = store.getString(PreferenceConstants.SIGN_MDA);
        signatureAlgorithm = store.getString(PreferenceConstants.SIGN_SA);
        signatureID = store.getString(PreferenceConstants.SIGN_ID);
    }

    /**
     * Signs the XML document with the stored settings.
     *
     * @throws Exception to indicate any exceptional condition
     */
    private void quickSign() throws Exception {
        final Signature signatureWizard = new Signature();
        signatureWizard.setResource(resource);
        signatureWizard.setXpath(xpath);
        signatureWizard.setSignatureType(signatureType);
        signatureWizard.setBsp(false);
        signatureWizard.setKeystore(keystore);
        signatureWizard.setKeyAlias(keyName);
        signatureWizard.setKeystorePassword(keystorePassword);
        signatureWizard.setKeyPassword(keyPassword);
        signatureWizard.setCanonicalizationAlgorithm(canonicalizationAlgorithm);
        signatureWizard.setTransformationAlgorithm(transformationAlgorithm);
        signatureWizard.setMessageDigestAlgorithm(messageDigestAlgorithm);
        signatureWizard.setSignatureAlgorithm(signatureAlgorithm);
        signatureWizard.setSignatureId(signatureID);

        IWorkbenchPart workbenchPart = getWorkbenchPart();

        if (workbenchPart != null && workbenchPart instanceof ITextEditor) {
            editor = (ITextEditor) workbenchPart;
        } else {
            editor = null;
        }

        if (editor != null && editor.isEditable()) { // call in editor
            boolean validSelection = false;

            if (editor.isDirty()) {
                saveEditorContent(editor);
            }

            IEditorInput input = editor.getEditorInput();
            final IDocument document = editor.getDocumentProvider().getDocument(input);
            file = (IFile) input.getAdapter(IFile.class);
            final ITextSelection textSelection = (ITextSelection) editor.getSelectionProvider()
                    .getSelection();

            if (resource.equals("selection") && textSelection != null && !textSelection.isEmpty()
                    && textSelection.getLength() > 0 && file != null) {
                validSelection = parseSelection(textSelection.getText());
            }

            if (file != null && resource.equals("selection") && validSelection) { // with text selection
                signatureWizard.setFile(file.getLocation().toString());
                IRunnableWithProgress op = new IRunnableWithProgress() {
                    public void run(final IProgressMonitor monitor) {
                        try {
                            monitor.beginTask(Messages.signatureTaskInfo, 5);
                            CreateSignature content = new CreateSignature();
                            Document doc = content.sign(signatureWizard, textSelection, monitor);

                            if (doc != null) {
                                document.set(Utils.docToString(doc, false));
                            }
                        } catch (final Exception ex) {
                            getShell().getDisplay().asyncExec(new Runnable() {
                                public void run() {
                                    showErrorDialog(Messages.error, Messages.signingError, ex);
                                    log(ERROR_TEXT, ex);
                                }
                            });
                        } finally {
                            monitor.done();
                        }
                    }
                };
                try {
                    PlatformUI.getWorkbench().getProgressService().runInUI(
                            XmlSecurityPlugin.getActiveWorkbenchWindow(), op,
                            XmlSecurityPlugin.getWorkspace().getRoot());
                } catch (InvocationTargetException ite) {
                    log(ERROR_TEXT, ite);
                } catch (InterruptedException ie) {
                    log(ERROR_TEXT, ie);
                }
            } else if (file != null && !resource.equals("selection")) { // without text selection
                signatureWizard.setFile(file.getLocation().toString());
                IRunnableWithProgress op = new IRunnableWithProgress() {
                    public void run(final IProgressMonitor monitor) {
                        try {
                            monitor.beginTask(Messages.signatureTaskInfo, 5);
                            CreateSignature content = new CreateSignature();
                            Document doc = content.sign(signatureWizard, null, monitor);

                            if (doc != null) {
                                document.set(Utils.docToString(doc, false));
                            }
                        } catch (final Exception ex) {
                            getShell().getDisplay().asyncExec(new Runnable() {
                                public void run() {
                                    showErrorDialog(Messages.error, Messages.signingError, ex);
                                    log(ERROR_TEXT, ex);
                                }
                            });
                        } finally {
                            monitor.done();
                        }
                    }
                };
                try {
                    PlatformUI.getWorkbench().getProgressService().runInUI(
                            XmlSecurityPlugin.getActiveWorkbenchWindow(), op,
                            XmlSecurityPlugin.getWorkspace().getRoot());
                } catch (InvocationTargetException ite) {
                    log(ERROR_TEXT, ite);
                } catch (InterruptedException ie) {
                    log(ERROR_TEXT, ie);
                }
            } else if (resource.equals("selection") && !validSelection) { //$NON-NLS-1$
                showInfo(Messages.invalidTextSelection, Messages.invalidTextSelectionText);
            } else {
                showInfo(Messages.quickSignatureImpossible, NLS.bind(Messages.protectedDoc, ACTION));
            }
        } else if (file != null && file.isAccessible() && !file.isReadOnly()) { // call in view
            IProject project = file.getProject();
            if (resource.equals("selection")) { //$NON-NLS-1$
                showInfo(Messages.quickSignatureImpossible, Messages.quickSignatureImpossibleText);
            } else {
                final String filename = file.getLocation().toString();
                signatureWizard.setFile(file.getLocation().toString());
                IRunnableWithProgress op = new IRunnableWithProgress() {
                    public void run(final IProgressMonitor monitor) {
                        try {
                            monitor.beginTask(Messages.signatureTaskInfo, 5);
                            CreateSignature content = new CreateSignature();
                            Document doc = content.sign(signatureWizard, null, monitor);
                            FileOutputStream fos = new FileOutputStream(filename);
                            if (doc != null) {
                                XMLUtils.outputDOM(doc, fos);
                            }
                            fos.flush();
                            fos.close();
                        } catch (final Exception ex) {
                            getShell().getDisplay().asyncExec(new Runnable() {
                                public void run() {
                                    showErrorDialog(Messages.error, Messages.signingError, ex);
                                    log(ERROR_TEXT, ex);
                                }
                            });
                        } finally {
                            monitor.done();
                        }
                    }
                };
                try {
                    PlatformUI.getWorkbench().getProgressService().runInUI(
                            XmlSecurityPlugin.getActiveWorkbenchWindow(), op,
                            XmlSecurityPlugin.getWorkspace().getRoot());
                } catch (InvocationTargetException ite) {
                    log(ERROR_TEXT, ite);
                } catch (InterruptedException ie) {
                    log(ERROR_TEXT, ie);
                }
            }

            project.refreshLocal(IProject.DEPTH_INFINITE, null);
        } else {
            showInfo(Messages.quickSignatureImpossible, NLS.bind(Messages.protectedDoc, ACTION));
        }
    }

    /**
     * Checks if the preferences contain all necessary information. Shows a dialog with a warning
     * message and a link to the preference page.<br/> If the preference dialog was closed with the
     * OK button the necessary preference settings are automatically verified again.
     *
     * @return Preferences OK or not
     */
    private boolean checkPreferences() {
        final String title = Messages.quickSignatureTitle;
        final String prefId = "org.eclipse.wst.xml.security.core.preferences.Signatures";
        int result = 2;

        if (resource == null || resource.equals("")) {
            result = showMissingParameterDialog(title, NLS.bind(Messages.missingParameter,
                    Messages.missingResource), prefId);
        } else if (resource != null && resource.equals("xpath") && (xpath == null || xpath.equals(""))) {
            result = showMissingParameterDialog(title, NLS.bind(Messages.missingParameter,
                    Messages.missingXPathExpression), prefId);
        } else if (signatureType == null || signatureType.equals("")) {
            result = showMissingParameterDialog(title, NLS.bind(Messages.missingParameter,
                    Messages.missingSignatureType), prefId);
        } else if (keystore == null) {
            result = showMissingParameterDialog(title, NLS.bind(Messages.missingParameter,
                    Messages.missingKeystoreFile), prefId);
        } else if (keyName == null || keyName.equals("")) {
            result = showMissingParameterDialog(title, NLS.bind(Messages.missingParameter,
                    Messages.missingKeyName), prefId);
        } else if (canonicalizationAlgorithm == null || canonicalizationAlgorithm.equals("")) {
            result = showMissingParameterDialog(title, NLS.bind(Messages.missingParameter,
                    Messages.missingCanonicalizationAlgorithm), prefId);
        } else if (transformationAlgorithm != null && transformationAlgorithm.equals("")) {
            result = showMissingParameterDialog(title, NLS.bind(Messages.missingParameter,
                    Messages.missingTransformationAlgorithm), prefId);
        } else if (messageDigestAlgorithm == null || messageDigestAlgorithm.equals("")) {
            result = showMissingParameterDialog(title, NLS.bind(Messages.missingParameter,
                    Messages.missingMDAlgorithm), prefId);
        } else if (signatureAlgorithm == null || signatureAlgorithm.equals("")) {
            result = showMissingParameterDialog(title, NLS.bind(Messages.missingParameter,
                    Messages.missingSignatureAlgorithm), prefId);
        } else if (signatureID == null || signatureID.equals("")) {
            result = showMissingParameterDialog(title, NLS.bind(Messages.missingParameter,
                    Messages.missingSignatureId), prefId);
        } else {
            completePrefs = true;
        }

        if (result == 0) {
            completePrefs = false;
            getPreferenceValues();
            checkPreferences();
        }

        return completePrefs;
    }

    /**
     * Checks the entered passwords for the Keystore and private key.
     *
     * @return Password is OK or not
     */
    private boolean checkPasswords() {
        if (keystorePassword == null || keystorePassword.length == 0) {
            showInfo(Messages.quickSignatureTitle, Messages.missingKeystorePassword);
            return false;
        } else if (keyPassword == null || keyPassword.length == 0) {
            showInfo(Messages.quickSignatureTitle, Messages.missingKeyPassword);
            return false;
        }

        return true;
    }
}