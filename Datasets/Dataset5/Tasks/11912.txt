NLS.bind(Messages.RemoveReadOnlyFlag, Messages.NewEncryptionCommand_3));

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

import java.io.FileWriter;
import java.lang.reflect.InvocationTargetException;

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
import org.eclipse.jface.text.IDocument;
import org.eclipse.jface.text.ITextSelection;
import org.eclipse.jface.viewers.ISelection;
import org.eclipse.jface.viewers.IStructuredSelection;
import org.eclipse.jface.wizard.WizardDialog;
import org.eclipse.osgi.util.NLS;
import org.eclipse.ui.IEditorPart;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.handlers.HandlerUtil;
import org.eclipse.ui.texteditor.ITextEditor;
import org.eclipse.wst.xml.security.core.encrypt.CreateEncryption;
import org.eclipse.wst.xml.security.ui.XSTUIPlugin;
import org.eclipse.wst.xml.security.ui.actions.SignNewAction;
import org.eclipse.wst.xml.security.ui.encrypt.NewEncryptionWizard;
import org.eclipse.wst.xml.security.ui.utils.Utils;
import org.w3c.dom.Document;

/**
 * <p>Command used to start the <b>XML Encryption</b> wizard for a new XML Encryption for the selected XML document.
 * The encryption process differs depending on whether editor content or a file via a view should be encrypted.</p>
 *
 * @author Dominik Schadow
 * @version 0.5.0
 */
public class NewEncryptionCommand extends AbstractHandler {
    /** Selected text in the editor. */
    private ITextSelection textSelection = null;
    private ExecutionEvent event;
    /** The file to encrypt. */
    private IFile file = null;

    public Object execute(ExecutionEvent event) throws ExecutionException {
        this.event = event;

        createEncryption();

        return null;
    }

    /**
     * Takes the resource (selected file or editor content) and starts the XML Encryption Wizard. The returned encrypted
     * XML document is pretty printed before the editor or the file is updated.
     */
    private void createEncryption() {
        try {
            NewEncryptionWizard wizard = new NewEncryptionWizard();
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

            if (file != null && file.isAccessible()) {
                if (textSelection != null && org.eclipse.wst.xml.security.core.utils.Utils.parseSelection(textSelection.getText())) {
                    // with valid text selection
                    wizard.init(file, textSelection);
                } else {
                    // without text selection (or invalid)
                    wizard.init(file);
                }

                CreateEncryption encryption = new CreateEncryption();
                String fileLocation = ""; //$NON-NLS-1$

                if (document == null) {
                    fileLocation = file.getLocation().toString();
                }

                encryptData(encryption, wizard, document, fileLocation);

                if (wizard.getModel().getLaunchSignatureWizard()) {
                    launchXMLSignatureWizard();
                }
            } else {
                MessageDialog.openInformation(HandlerUtil.getActiveShell(event), Messages.NewEncryptionCommand_0,
                        NLS.bind(Messages.RemoveReadOnlyFlag, "encrypt")); //$NON-NLS-1$
            }
        } catch (Exception ex) {
            Utils.showErrorDialog(HandlerUtil.getActiveShell(event), Messages.NewEncryptionCommand_0,
                    Messages.NewEncryptionCommand_1, ex);
            Utils.log("An error occured during encrypting", ex); //$NON-NLS-1$
        }
    }

    /**
     * Encrypting an XML resource inside an opened editor (with or without a text selection) or via a view.
     *
     * @param data The resource to encrypt
     * @param wizard The Encryption Wizard
     * @param document The document to encrypt, null if a file is encrypted directly
     * @param filename The filename, empty if editor content is encrypted
     * @throws Exception to indicate any exceptional condition
     */
    private void encryptData(final CreateEncryption data, final NewEncryptionWizard wizard, final IDocument document, final String filename)
            throws Exception {
        WizardDialog dialog = new WizardDialog(HandlerUtil.getActiveShell(event), wizard);
        dialog.create();
        dialog.open();

        if (dialog.getReturnCode() == Dialog.OK && wizard.getModel() != null) {
            Job job = new Job(Messages.NewEncryptionCommand_0) {
                public IStatus run(final IProgressMonitor monitor) {
                    try {
                        monitor.beginTask(Messages.NewEncryptionCommand_2, 3);

                        Document doc = null;

                        if (textSelection != null) {
                            doc = data.encrypt(wizard.getModel(), textSelection.getText(), monitor);
                        } else {
                            doc = data.encrypt(wizard.getModel(), null, monitor);
                        }

                        if (monitor.isCanceled()) {
                            return Status.CANCEL_STATUS;
                        }

                        if (doc != null) {
                            if (document != null) {
                                document.set(org.eclipse.wst.xml.security.core.utils.Utils.docToString(doc, true));
                            } else {
                                FileWriter fw = new FileWriter(filename);
                                fw.write(org.eclipse.wst.xml.security.core.utils.Utils.docToString(doc, true));
                                fw.flush();
                                fw.close();
                            }
                        }
                    } catch (final Exception ex) {
                        HandlerUtil.getActiveShell(event).getDisplay().asyncExec(new Runnable() {
                            public void run() {
                                Utils.showErrorDialog(HandlerUtil.getActiveShell(event), Messages.NewEncryptionCommand_0,
                                        Messages.NewEncryptionCommand_1, ex);
                                Utils.log("An error occured during encrypting", ex); //$NON-NLS-1$
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

        dialog.close();
        wizard.dispose();
    }

    /**
     * Calls the <i>XML Signature Wizard</i> after successfully encrypting the selected resource if the user selected
     * the checkbox in the <i>XML Encryption Wizard</i>.
     */
    private void launchXMLSignatureWizard() {
        SignNewAction sign = new SignNewAction();
        sign.signAfterEncryption(file);
    }

    /**
     * Encrypts the given XML document after successfully signing it.
     *
     * @param signedFile The signed file, now used to encrypt
     */
    public void encryptAfterSignature(final IFile signedFile) {
        this.file = signedFile;

        createEncryption();
    }
}