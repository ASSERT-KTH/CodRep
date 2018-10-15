final String prefId = "org.eclipse.wst.xml.security.ui.preferences.Signature"; //$NON-NLS-1$

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

import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.lang.reflect.InvocationTargetException;

import org.apache.xml.security.utils.XMLUtils;
import org.eclipse.core.commands.AbstractHandler;
import org.eclipse.core.commands.ExecutionEvent;
import org.eclipse.core.commands.ExecutionException;
import org.eclipse.core.resources.IFile;
import org.eclipse.core.resources.ResourcesPlugin;
import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Status;
import org.eclipse.core.runtime.jobs.Job;
import org.eclipse.jface.dialogs.Dialog;
import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.jface.operation.IRunnableWithProgress;
import org.eclipse.jface.preference.IPreferenceStore;
import org.eclipse.jface.text.IDocument;
import org.eclipse.jface.text.ITextSelection;
import org.eclipse.jface.viewers.ISelection;
import org.eclipse.jface.viewers.IStructuredSelection;
import org.eclipse.osgi.util.NLS;
import org.eclipse.ui.IEditorPart;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.handlers.HandlerUtil;
import org.eclipse.ui.texteditor.ITextEditor;
import org.eclipse.wst.xml.security.core.cryptography.Keystore;
import org.eclipse.wst.xml.security.core.sign.CreateSignature;
import org.eclipse.wst.xml.security.core.sign.Signature;
import org.eclipse.wst.xml.security.core.utils.Globals;
import org.eclipse.wst.xml.security.ui.XSTUIPlugin;
import org.eclipse.wst.xml.security.ui.dialogs.MissingPreferenceDialog;
import org.eclipse.wst.xml.security.ui.dialogs.PasswordDialog;
import org.eclipse.wst.xml.security.ui.preferences.PreferenceConstants;
import org.eclipse.wst.xml.security.ui.utils.Utils;
import org.w3c.dom.Document;
import org.xml.sax.SAXParseException;

/**
 * <p>Command used to create an <b>XML Signature</b> of the selected XML document (fragment) with
 * predefined settings defined in the preferences of the current workspace (<b>Quick Signature</b>).</p>
 *
 * @author Dominik Schadow
 * @version 0.5.0
 */
public class QuickSignatureCommand extends AbstractHandler {
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
    /** Keystore path and filename. */
    private String keyFile;
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
    private String signatureId;
    /** All necessary preferences are available. */
    private boolean completePrefs = false;
    private ExecutionEvent event;
    /** Selected text in the editor. */
    private ITextSelection textSelection = null;

    public Object execute(ExecutionEvent event) throws ExecutionException {
        this.event = event;

        getPreferenceValues();

        if (checkPreferences()) {
            createSignature();
        }

        return null;
    }

    private void createSignature() {
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

            textSelection = (ITextSelection) ((ITextEditor)
                    editorPart.getAdapter(ITextEditor.class)).getSelectionProvider().getSelection();
            file = (IFile) editorPart.getEditorInput().getAdapter(IFile.class);
            document = (IDocument) editorPart.getAdapter(IDocument.class);
        } else {
            textSelection = null;
            ISelection selection = HandlerUtil.getCurrentSelection(event);
            if (selection instanceof IStructuredSelection) {
                file = (IFile) ((IStructuredSelection) selection).getFirstElement();
            }
        }

        // Ask the user for the passwords
        PasswordDialog keystorePasswordDialog = new PasswordDialog(HandlerUtil.getActiveShell(event),
                Messages.QuickSignatureCommand_4, Messages.QuickSignatureCommand_1, ""); //$NON-NLS-1$
        if (keystorePasswordDialog.open() == Dialog.OK) {
            keystorePassword = keystorePasswordDialog.getValue().toCharArray();
        } else {
            return;
        }

        PasswordDialog privateKeyPasswordDialog = new PasswordDialog(HandlerUtil.getActiveShell(event),
                Messages.QuickSignatureCommand_4, Messages.QuickSignatureCommand_3, ""); //$NON-NLS-1$
        if (privateKeyPasswordDialog.open() == Dialog.OK) {
            keyPassword = privateKeyPasswordDialog.getValue().toCharArray();
        } else {
            return;
        }

        if (checkPasswords()) {
            try {
                if (loadKeystore()) {
                    if (file != null && file.isAccessible()) {
                        signData(document);
                    } else {
                        MessageDialog.openInformation(HandlerUtil.getActiveShell(event), Messages.QuickSignatureCommand_4,
                                NLS.bind(Messages.RemoveReadOnlyFlag, Messages.QuickSignatureCommand_5));
                    }
                } else {
                    MessageDialog.openError(HandlerUtil.getActiveShell(event), Messages.QuickSignatureCommand_4,
                            Messages.QuickSignatureCommand_6);
                }
            } catch (SAXParseException spe) {
                Utils.showErrorDialog(HandlerUtil.getActiveShell(event), Messages.QuickSignatureCommand_4,
                        Messages.QuickSignatureCommand_7, spe);
            } catch (FileNotFoundException fnfe) {
                MessageDialog.openError(HandlerUtil.getActiveShell(event), Messages.QuickSignatureCommand_4,
                        Messages.QuickSignatureCommand_8);
            } catch (IOException ioe) {
                Utils.showErrorDialog(HandlerUtil.getActiveShell(event), Messages.QuickSignatureCommand_4,
                        Messages.QuickSignatureCommand_9, ioe);
            } catch (Exception ex) {
                Utils.showErrorDialog(HandlerUtil.getActiveShell(event), Messages.QuickSignatureCommand_4,
                        Messages.QuickSignatureCommand_10, ex);
                Utils.log("An error occured during quick signing", ex); //$NON-NLS-1$
            }
        }
    }

    private void signData(final IDocument document) {
        final CreateSignature signature = new CreateSignature();
        final Signature data = new Signature();
        data.setResource(resource);
        data.setXpath(xpath);
        data.setSignatureType(signatureType);
        data.setBsp(false);
        data.setKeystore(keystore);
        data.setKeyName(keyName);
        data.setKeystorePassword(keystorePassword);
        data.setKeyPassword(keyPassword);
        data.setCanonicalizationAlgorithm(canonicalizationAlgorithm);
        data.setTransformationAlgorithm(transformationAlgorithm);
        data.setMessageDigestAlgorithm(messageDigestAlgorithm);
        data.setSignatureAlgorithm(signatureAlgorithm);
        data.setSignatureId(signatureId);
        data.setFile(file.getLocation().toOSString());

        Job job = new Job(Messages.QuickSignatureCommand_4) {
            public IStatus run(final IProgressMonitor monitor) {
                try {
                    monitor.beginTask(Messages.NewSignatureCommand_7, 5);

                    Document doc = null;

                    if (textSelection != null) {
                        doc = signature.sign(data, textSelection.getText(), monitor);
                    } else {
                        doc = signature.sign(data, null, monitor);
                    }

                    if (monitor.isCanceled()) {
                        return Status.CANCEL_STATUS;
                    }

                    if (doc != null) {
                        if (document != null) {
                            document.set(org.eclipse.wst.xml.security.core.utils.Utils.docToString(doc, false));
                        } else {
                            FileOutputStream fos = new FileOutputStream(file.getLocation().toOSString());
                            XMLUtils.outputDOM(doc, fos);
                            fos.flush();
                            fos.close();
                        }
                    }
                } catch (final Exception ex) {
                    HandlerUtil.getActiveShell(event).getDisplay().asyncExec(new Runnable() {
                        public void run() {
                            Utils.showErrorDialog(HandlerUtil.getActiveShell(event), Messages.QuickSignatureCommand_4,
                                    Messages.NewSignatureCommand_8, ex);
                            Utils.log("An error occured during signing", ex); //$NON-NLS-1$
                        }
                    });
                } finally {
                    monitor.done();
                }

                return Status.OK_STATUS;
            }
        };
        job.setUser(true);
        job.schedule();
    }

    /**
     * Loads the entered key in the selected keystore.
     *
     * @return Keystore/ key information correct or not
     *
     * @throws Exception to indicate any exceptional condition
     */
    private boolean loadKeystore() throws Exception {
        try {
            keystore = new Keystore(keyFile, keystorePassword.toString(), Globals.KEYSTORE_TYPE);
            keystore.load();

            if (!keystore.containsKey(keyName)) {
                return false;
            }

            if (keystore.getPrivateKey(keyName, keyPassword) == null) {
                return false;
            }

            return true;
        } catch (Exception ex) {
            Utils.log("An error occured during quick signing", ex); //$NON-NLS-1$
            return false;
        }
    }

    /**
     * Determines the preference values for <i>Quick Signature</i>.
     */
    private void getPreferenceValues() {
        IPreferenceStore store = XSTUIPlugin.getDefault().getPreferenceStore();
        resource = store.getString(PreferenceConstants.SIGN_RESOURCE);

        if (resource != null && resource.equals("xpath")) { //$NON-NLS-1$
            xpath = store.getString(PreferenceConstants.SIGN_XPATH);
        }

        signatureType = store.getString(PreferenceConstants.SIGN_TYPE);
        keyFile = store.getString(PreferenceConstants.SIGN_KEYSTORE_FILE);
        keyName = store.getString(PreferenceConstants.SIGN_KEY_NAME);
        canonicalizationAlgorithm = store.getString(PreferenceConstants.SIGN_CANON);
        transformationAlgorithm = store.getString(PreferenceConstants.SIGN_TRANS);
        messageDigestAlgorithm = store.getString(PreferenceConstants.SIGN_MDA);
        signatureAlgorithm = store.getString(PreferenceConstants.SIGN_SA);
        signatureId = store.getString(PreferenceConstants.SIGN_ID);
    }

    /**
     * Checks if the preferences contain all necessary information. Shows a dialog with a warning
     * message and a link to the preference page.<br/> If the preference dialog was closed with the
     * OK button the necessary preference settings are automatically verified again.
     *
     * @return Preferences OK or not
     */
    private boolean checkPreferences() {
        final String title = Messages.QuickSignatureCommand_4;
        final String prefId = "org.eclipse.wst.xml.security.ui.preferences.Signatures"; //$NON-NLS-1$
        int result = 2;

        if (resource == null || "".equals(resource)) { //$NON-NLS-1$
            result = showMissingParameterDialog(title, NLS.bind(Messages.MissingParameter,
                    Messages.QuickSignatureCommand_11), prefId);
        } else if (resource != null && "xpath".equals(resource) && (xpath == null || "".equals(xpath))) { //$NON-NLS-1$ //$NON-NLS-2$
            result = showMissingParameterDialog(title, NLS.bind(Messages.MissingParameter,
                    Messages.QuickSignatureCommand_12), prefId);
        } else if (signatureType == null || "".equals(signatureType)) { //$NON-NLS-1$
            result = showMissingParameterDialog(title, NLS.bind(Messages.MissingParameter,
                    Messages.QuickSignatureCommand_13), prefId);
        } else if (keyFile == null || "".equals(keyFile)) { //$NON-NLS-1$
            result = showMissingParameterDialog(title, NLS.bind(Messages.MissingParameter,
                    Messages.QuickSignatureCommand_14), prefId);
        } else if (keyName == null || "".equals(keyName)) { //$NON-NLS-1$
            result = showMissingParameterDialog(title, NLS.bind(Messages.MissingParameter,
                    Messages.QuickSignatureCommand_15), prefId);
        } else if (canonicalizationAlgorithm == null || "".equals(canonicalizationAlgorithm)) { //$NON-NLS-1$
            result = showMissingParameterDialog(title, NLS.bind(Messages.MissingParameter,
                    Messages.QuickSignatureCommand_16), prefId);
        } else if (transformationAlgorithm != null && "".equals(transformationAlgorithm)) { //$NON-NLS-1$
            result = showMissingParameterDialog(title, NLS.bind(Messages.MissingParameter,
                    Messages.QuickSignatureCommand_17), prefId);
        } else if (messageDigestAlgorithm == null || "".equals(messageDigestAlgorithm)) { //$NON-NLS-1$
            result = showMissingParameterDialog(title, NLS.bind(Messages.MissingParameter,
                    Messages.QuickSignatureCommand_18), prefId);
        } else if (signatureAlgorithm == null || "".equals(signatureAlgorithm)) { //$NON-NLS-1$
            result = showMissingParameterDialog(title, NLS.bind(Messages.MissingParameter,
                    Messages.QuickSignatureCommand_19), prefId);
        } else if (signatureId == null || "".equals(signatureId)) { //$NON-NLS-1$
            result = showMissingParameterDialog(title, NLS.bind(Messages.MissingParameter,
                    Messages.MissingSignatureId), prefId);
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
     * Checks the entered passwords for the keystore and private key.
     *
     * @return Both passwords are OK
     */
    private boolean checkPasswords() {
        if (keystorePassword == null || keystorePassword.length == 0) {
            MessageDialog.openInformation(HandlerUtil.getActiveShell(event), Messages.QuickSignatureCommand_4,
                    Messages.QuickSignatureCommand_1);
            return false;
        } else if (keyPassword == null || keyPassword.length == 0) {
            MessageDialog.openInformation(HandlerUtil.getActiveShell(event), Messages.QuickSignatureCommand_4,
                    Messages.QuickSignatureCommand_3);
            return false;
        }

        return true;
    }

    /**
     * Shows a dialog with a message for a missing preference parameter.
     *
     * @param title The title of the message box
     * @param message The message to display
     * @param prefId The preference page id to show
     * @return The clicked button in the preferences dialog
     */
    private int showMissingParameterDialog(final String title, final String message, final String prefId) {
        MissingPreferenceDialog dialog = new MissingPreferenceDialog(HandlerUtil.getActiveShell(event), title, message, prefId);
        return dialog.open();
    }
}