if (textSelection == null || textSelection.trim().length() == 0) {

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
package org.eclipse.wst.xml.security.ui.actions;

import java.io.IOException;
import java.io.StringReader;
import java.lang.reflect.InvocationTargetException;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import javax.xml.parsers.ParserConfigurationException;
import javax.xml.parsers.SAXParserFactory;

import org.eclipse.core.resources.ResourcesPlugin;
import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Status;
import org.eclipse.jface.action.IAction;
import org.eclipse.jface.dialogs.ErrorDialog;
import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.jface.operation.IRunnableWithProgress;
import org.eclipse.jface.viewers.ISelection;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.ui.IObjectActionDelegate;
import org.eclipse.ui.IWorkbenchPart;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.texteditor.ITextEditor;
import org.eclipse.wst.xml.security.ui.XSTUIPlugin;
import org.eclipse.wst.xml.security.ui.dialogs.MissingPreferenceDialog;
import org.xml.sax.InputSource;
import org.xml.sax.SAXException;
import org.xml.sax.XMLReader;

/**
 * <p>Base class of all actions in the XML Security Tools. Contains common methods
 * for saving the editor content, logging and error/ information dialog handling.</p>
 *
 * @author Dominik Schadow
 * @version 0.5.0
 */
public abstract class XmlSecurityActionAdapter implements IObjectActionDelegate {
    /** Active Workbench Part. */
    private IWorkbenchPart workbenchPart = null;
    /** The current shell. */
    private Shell shell = null;

    /**
     * Called when the action is executed. Must be overwritten in subclasses.
     *
     * @param action The executed action
     */
    public abstract void run(final IAction action);

    /**
     * Called when the selection in the active workbench part changes.
     *
     * @param action The executed action
     * @param selection The selection
     */
    public abstract void selectionChanged(final IAction action, final ISelection selection);

    /**
     * Returns the current shell.
     *
     * @return The shell
     */
    public Shell getShell() {
        return shell;
    }

    /**
     * Returns the current workbench part.
     *
     * @return The workbench part
     */
    public IWorkbenchPart getWorkbenchPart() {
        return workbenchPart;
    }

    /**
     * Sets the active part of the workbench.
     *
     * @param action The executed IAction
     * @param workbenchPart The IWorkbenchPart
     */
    public void setActivePart(final IAction action, final IWorkbenchPart workbenchPart) {
        this.workbenchPart = workbenchPart;
        shell = workbenchPart.getSite().getShell();
    }

    /**
     * Writes the message with status <i>error</i> into the workbench log file.
     *
     * @param message The message to log
     * @param ex The exception to log
     */
    protected void log(final String message, final Exception ex) {
        IStatus status = new Status(IStatus.ERROR, XSTUIPlugin.getDefault().getBundle().getSymbolicName(), 0, message, ex);
        XSTUIPlugin.getDefault().getLog().log(status);
    }

    /**
     * Shows an information dialog with a message.
     *
     * @param title The title of the message box
     * @param message The message to display
     */
    protected void showInfo(final String title, final String message) {
        MessageDialog.openInformation(shell, title, message);
    }

    /**
     * Shows an error dialog with a message.
     *
     * @param title The title of the message box
     * @param message The message to display
     */
    protected void showError(final String title, final String message) {
        MessageDialog.openError(shell, title, message);
    }

    /**
     * Shows an error dialog with an details button for detailed error information.
     *
     * @param title The title of the message box
     * @param message The message to display
     * @param ex The exception
     */
    protected void showErrorDialog(final String title, final String message, final Exception ex) {
        String reason = ex.getMessage();
        if (reason == null || "".equals(reason)) {
            reason = Messages.errorReasonUnavailable;
        }

        IStatus status = new Status(IStatus.ERROR, XSTUIPlugin.getDefault().getBundle().getSymbolicName(), 0, reason, ex);

        ErrorDialog.openError(shell, title, message, status);
    }

    /**
     * Shows a dialog with a message for a missing preference parameter.
     *
     * @param title The title of the message box
     * @param message The message to display
     * @param prefId The preference page id to show
     * @return The clicked button in the preferences dialog
     */
    protected int showMissingParameterDialog(final String title, final String message, final String prefId) {
        MissingPreferenceDialog dialog = new MissingPreferenceDialog(shell, title, message, prefId);
        return dialog.open();
    }

    /**
     * Called when there is a text selection and either the XML Signature Wizard or the XML Encryption Wizard is called.
     * If the selection is invalid, the radio button in the wizard is disabled. This method returns always
     * <code>true</code> if only element content (no &gt; or &lt; included) is selected.
     *
     * @param textSelection The text selection as a String value
     * @return true or false which activates or deactivates the selection radio button in the wizard
     */
    protected boolean parseSelection(final String textSelection) {
        if (textSelection == null || textSelection.length() == 0) {
            return false;
        }

        Pattern p = Pattern.compile("[^<>]+");
        Matcher m = p.matcher(textSelection);

        // a tag (or parts of it) are selected
        if (!m.matches()) {
            SAXParserFactory spf = SAXParserFactory.newInstance();
            spf.setNamespaceAware(true);
            try {
                XMLReader xmlReader = spf.newSAXParser().getXMLReader();
                xmlReader.setErrorHandler(null);
                xmlReader.parse(new InputSource(new StringReader(textSelection)));
            } catch (IOException e) {
                return false;
            } catch (SAXException e) {
                return false;
            } catch (ParserConfigurationException e) {
                return false;
            }

            return true;
        }

        // only element content, no < or > selected, always return true
        return true;
    }

    /**
     * Saves the unsaved content of the active editor.
     *
     * @param openedEditor The opened editor
     */
    protected void saveEditorContent(final ITextEditor openedEditor) {
        if (null != openedEditor.getTitle() && openedEditor.getTitle().length() > 0) {
            IRunnableWithProgress op = new IRunnableWithProgress() {
                public void run(final IProgressMonitor monitor) {
                    openedEditor.doSave(monitor);
                }
            };
            try {
                PlatformUI.getWorkbench().getProgressService().runInUI(XSTUIPlugin.getActiveWorkbenchWindow(),
                        op, ResourcesPlugin.getWorkspace().getRoot());
            } catch (InvocationTargetException ite) {
                log("Error while saving editor content", ite); //$NON-NLS-1$
            } catch (InterruptedException ie) {
                log("Error while saving editor content", ie); //$NON-NLS-1$
            }
        } else {
            openedEditor.doSaveAs();
        }
    }
}