setWindowTitle(Messages.signatureWizard);

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
package org.eclipse.wst.xml.security.core.sign;

import org.eclipse.core.resources.IFile;
import org.eclipse.core.resources.IProject;
import org.eclipse.jface.dialogs.IDialogSettings;
import org.eclipse.jface.resource.ImageDescriptor;
import org.eclipse.jface.text.ITextSelection;
import org.eclipse.jface.viewers.IStructuredSelection;
import org.eclipse.jface.wizard.Wizard;
import org.eclipse.ui.INewWizard;
import org.eclipse.ui.IWorkbench;
import org.eclipse.ui.plugin.AbstractUIPlugin;
import org.eclipse.wst.xml.security.core.XmlSecurityPlugin;


/**
 * <p>This class prepares and adds all wizard pages to the wizard and launches the
 * <i>XML Digital Signature Wizard</i> afterwards.</p>
 *
 * @author Dominik Schadow
 * @version 0.5.0
 */
public class NewSignatureWizard extends Wizard implements INewWizard {
    /** PageResource first wizard page. */
    private PageResource pageResource = null;
    /** PageOpenKey second default wizard page. */
    private PageOpenKey pageOpenKey = null;
    /** PageCreateKey second alternative wizard page. */
    private PageCreateKey pageCreateKey = null;
    /** PageCreateKeystore second alternative wizard page. */
    private PageCreateKeystore pageCreateKeystore = null;
    /** PageAlgorithms third wizard page. */
    private PageAlgorithms pageAlgorithms = null;
    /** The XML document to sign. */
    private IFile xmlDocument;
    /** The text selection in the editor. */
    private ITextSelection xmlSelection;
    /** The Signature model. */
    private Signature signature;
    /** Path of the opened project. */
    private String path;
    /** Name of the opened project. */
    private String name;

    /**
     * Constructor for the wizard launcher.
     */
    public NewSignatureWizard() {
        super();
        signature = new Signature();
        setWindowTitle(Messages.digitalSignatureWizard);
        setDialogSettings(getDigitalSignatureWizardSettings());
        ImageDescriptor image = AbstractUIPlugin.imageDescriptorFromPlugin(XmlSecurityPlugin.getId(),
                "icons/wiz_sig.gif");
        setDefaultPageImageDescriptor(image);
        setNeedsProgressMonitor(true);
    }

    /**
     * Return the settings used for all Digital Signature Wizard pages.
     *
     * @return The IDialogSettings for the Digital Signature Wizard
     */
    private IDialogSettings getDigitalSignatureWizardSettings() {
        IDialogSettings workbenchSettings = XmlSecurityPlugin.getDefault().getDialogSettings();
        IDialogSettings section = workbenchSettings.getSection("DigitalSignatureWizard"); // $NON-NLS-1$
        if (section == null) {
            section = workbenchSettings.addNewSection("DigitalSignatureWizard"); // $NON-NLS-1$
        }
        return section;
    }

    /**
     * Initializes the wizard with a text selection.
     *
     * @param workbench The workbench
     * @param selection The text selection
     */
    public void init(final IWorkbench workbench, final IStructuredSelection selection) {
    }

    /**
     * Initializes the wizard with a selected file.
     *
     * @param project The opened project
     * @param file The selected IFile
     */
    public void init(final IProject project, final IFile file) {
        init(project, file, null);
    }

    /**
     * Initializes the wizard with a selected file and a text selection.
     *
     * @param project The opened project
     * @param file The selected file
     * @param textSelection The text selection
     */
    public void init(final IProject project, final IFile file, final ITextSelection textSelection) {
        xmlDocument = file;
        xmlSelection = textSelection;
        path = project.getLocation().toOSString();
        name = project.getName();
    }

    /**
     * Adds the five pages (<code>PageResource</code>,
     * <code>PageOpenKey</code>, <code>PageCreateKey</code>,
     * <code>PageCreateKeystore</code> and <code>PageAlgorithms</code>)
     * to the wizard.
     */
    public void addPages() {
        if (xmlSelection == null) {
            pageResource = new PageResource(signature, xmlDocument, path, false);
        } else {
            pageResource = new PageResource(signature, xmlDocument, path, true);
        }
        addPage(pageResource);
        pageOpenKey = new PageOpenKey(signature, path);
        addPage(pageOpenKey);
        pageCreateKey = new PageCreateKey(signature, path);
        addPage(pageCreateKey);
        pageCreateKeystore = new PageCreateKeystore(signature, path, name);
        addPage(pageCreateKeystore);
        pageAlgorithms = new PageAlgorithms(signature, xmlDocument);
        addPage(pageAlgorithms);
    }

    /**
     * Checks the currently active wizard page. It is impossible to finish the
     * <i>Digital Signature Wizard</i> from the first or second page. Only the
     * third wizard page can successfully generate a digital signature.
     *
     * @return Wizard completion status
     */
    public boolean canFinish() {
        if (this.getContainer().getCurrentPage() != pageAlgorithms) {
            return false;
        } else {
            return pageAlgorithms.isPageComplete();
        }
    }

    /**
     * Finishes the wizard.
     *
     * @return Finishing status
     */
    public boolean performFinish() {
        pageResource.storeSettings();
        pageOpenKey.storeSettings();
        pageAlgorithms.storeSettings();
        return pageAlgorithms.performFinish();
    }

    /**
     * Returns the Signature Wizard model.
     *
     * @return The model
     */
    public Signature getModel() {
        return signature;
    }

    /**
     * @return the pageResource
     */
    public PageResource getPageResource() {
        return pageResource;
    }

    /**
     * @return the pageOpenKey
     */
    public PageOpenKey getPageOpenKey() {
        return pageOpenKey;
    }

    /**
     * @return the pageCreateKey
     */
    public PageCreateKey getPageCreateKey() {
        return pageCreateKey;
    }

    /**
     * @return the pageCreateKeystore
     */
    public PageCreateKeystore getPageCreateKeystore() {
        return pageCreateKeystore;
    }

    /**
     * @return the pageAlgorithms
     */
    public PageAlgorithms getPageAlgorithms() {
        return pageAlgorithms;
    }
}