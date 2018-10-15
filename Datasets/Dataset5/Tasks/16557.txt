ids = Utils.getIds(file.getContents(), "encryption");

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
package org.eclipse.wst.xml.security.ui.decrypt;

import java.io.File;

import org.eclipse.core.resources.IFile;
import org.eclipse.jface.dialogs.DialogPage;
import org.eclipse.jface.dialogs.IDialogSettings;
import org.eclipse.jface.wizard.WizardPage;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.ModifyEvent;
import org.eclipse.swt.events.ModifyListener;
import org.eclipse.swt.layout.FormAttachment;
import org.eclipse.swt.layout.FormData;
import org.eclipse.swt.layout.FormLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Combo;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Event;
import org.eclipse.swt.widgets.FileDialog;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Listener;
import org.eclipse.swt.widgets.Text;
import org.eclipse.ui.PlatformUI;
import org.eclipse.wst.xml.security.core.cryptography.Keystore;
import org.eclipse.wst.xml.security.core.decrypt.Decryption;
import org.eclipse.wst.xml.security.core.utils.Globals;
import org.eclipse.wst.xml.security.core.utils.Utils;
import org.eclipse.wst.xml.security.ui.XSTUIPlugin;
import org.eclipse.wst.xml.security.ui.utils.IContextHelpIds;

/**
 * <p>First and only page of the <strong>XML Decryption Wizard</strong>. Lets the user
 * select or enter the Keystore containing the key used for encryption, the corresponding
 * passwords and the encryption id for the encrypted document part to decrypt.</p>
 *
 * <p>After all information is entered the user can finish the Wizard and the XML fragment
 * identified by the given encryption id will be decrypted and restored in plain text.
 * Any wrong entered information that was not already discovered in the wizard will cause
 * decryption to fail.</p>
 *
 * @author Dominik Schadow
 * @version 0.5.0
 */
public class PageResource extends WizardPage implements Listener {
    /** Wizard page name. */
    public static final String PAGE_NAME = "DecryptPageResource"; //$NON-NLS-1$
    /** Open Keystore button. */
    private Button bOpen = null;
    /** Button <i>Echo Key Password</i>. */
    private Button bEchoKeyPassword = null;
    /** Button <i>Echo Keystore Password</i>. */
    private Button bEchoKeystorePassword = null;
    /** Combo box <i>Encryption ID</i>. */
    private Combo cEncryptionId = null;
    /** Keystore file. */
    private Text tKeystore = null;
    /** Keystore password. */
    private Text tKeystorePassword = null;
    /** Key name. */
    private Text tKeyName = null;
    /** Key password. */
    private Text tKeyPassword = null;
    /** The XML document. */
    private IFile file;
    /** Model for the XML Decryption Wizard. */
    private Decryption decryption = null;
    /** Default label width. */
    private static final int LABELWIDTH = 120;

    /**
     * Constructor for the algorithms page with three parameters.
     *
     * @param decryption The decryption wizard model
     * @param file The selected file
     */
    public PageResource(final Decryption decryption, final IFile file) {
        super(PAGE_NAME);
        setTitle(Messages.decryptionTitle);
        setDescription(Messages.decryptionDescription);

        this.decryption = decryption;
        this.file = file;
    }

    /**
     * Creates the wizard page with the layout settings.
     *
     * @param parent Parent composite
     */
    public void createControl(final Composite parent) {
        Composite container = new Composite(parent, SWT.NULL);
        FormLayout formLayout = new FormLayout();
        container.setLayout(formLayout);

        createPageContent(container);
        determineIds();
        addListeners();
        setControl(container);
        loadSettings();

        PlatformUI.getWorkbench().getHelpSystem().setHelp(getControl(), IContextHelpIds.WIZARD_DECRYPTION_RESOURCE);
    }

    /**
     * Fills this wizard page with content. Three groups (<i>Keystore</i>, <i>Key</i> and
     * <i>Encryption ID</i>) and all their widgets are inserted.
     *
     * @param parent Parent composite
     */
    private void createPageContent(final Composite parent) {
        FormLayout layout = new FormLayout();
        layout.marginTop = Globals.MARGIN / 2;
        layout.marginBottom = Globals.MARGIN / 2;
        layout.marginLeft = Globals.MARGIN / 2;
        layout.marginRight = Globals.MARGIN / 2;
        parent.setLayout(layout);

        // Three groups
        Group gKeystore = new Group(parent, SWT.SHADOW_ETCHED_IN);
        gKeystore.setLayout(layout);
        gKeystore.setText(Messages.keystore);
        FormData data = new FormData();
        data.top = new FormAttachment(0, 0);
        data.left = new FormAttachment(0, 0);
        data.right = new FormAttachment(Globals.GROUP_NUMERATOR);
        gKeystore.setLayoutData(data);

        Group gKey = new Group(parent, SWT.SHADOW_ETCHED_IN);
        gKey.setLayout(layout);
        gKey.setText(Messages.key);
        data = new FormData();
        data.top = new FormAttachment(gKeystore, Globals.MARGIN, SWT.DEFAULT);
        data.left = new FormAttachment(0, 0);
        data.right = new FormAttachment(Globals.GROUP_NUMERATOR);
        gKey.setLayoutData(data);

        Group gEncryptionId = new Group(parent, SWT.SHADOW_ETCHED_IN);
        gEncryptionId.setLayout(layout);
        gEncryptionId.setText(Messages.encryptionId);
        data = new FormData();
        data.top = new FormAttachment(gKey, Globals.MARGIN, SWT.DEFAULT);
        data.top = new FormAttachment(gKey, Globals.MARGIN, SWT.DEFAULT);
        data.left = new FormAttachment(0, 0);
        data.right = new FormAttachment(Globals.GROUP_NUMERATOR);
        gEncryptionId.setLayoutData(data);

        // Elements for group "Keystore"
        Label lKeystoreName = new Label(gKeystore, SWT.SHADOW_IN);
        lKeystoreName.setText(Messages.name);
        data = new FormData();
        data.width = LABELWIDTH;
        data.top = new FormAttachment(gKeystore);
        data.left = new FormAttachment(gKeystore);
        lKeystoreName.setLayoutData(data);

        tKeystore = new Text(gKeystore, SWT.SINGLE);
        data = new FormData();
        data.width = Globals.SHORT_TEXT_WIDTH;
        data.top = new FormAttachment(lKeystoreName, 0, SWT.CENTER);
        data.left = new FormAttachment(lKeystoreName);
        tKeystore.setLayoutData(data);

        bOpen = new Button(gKeystore, SWT.PUSH);
        bOpen.setText(Messages.selectButton);
        data = new FormData();
        data.top = new FormAttachment(tKeystore, 0, SWT.CENTER);
        data.left = new FormAttachment(tKeystore, Globals.MARGIN);
        bOpen.setLayoutData(data);

        Label lKeystorePassword = new Label(gKeystore, SWT.SHADOW_IN);
        lKeystorePassword.setText(Messages.password);
        data = new FormData();
        data.width = LABELWIDTH;
        data.top = new FormAttachment(lKeystoreName, Globals.MARGIN);
        data.left = new FormAttachment(gKeystore);
        lKeystorePassword.setLayoutData(data);

        tKeystorePassword = new Text(gKeystore, SWT.SINGLE);
        tKeystorePassword.setTextLimit(Globals.KEYSTORE_PASSWORD_MAX_SIZE);
        data = new FormData();
        data.width = Globals.SHORT_TEXT_WIDTH;
        data.top = new FormAttachment(lKeystorePassword, 0, SWT.CENTER);
        data.left = new FormAttachment(lKeystorePassword);
        tKeystorePassword.setEchoChar('*');
        tKeystorePassword.setLayoutData(data);

        bEchoKeystorePassword = new Button(gKeystore, SWT.PUSH);
        bEchoKeystorePassword.setImage(XSTUIPlugin.getDefault().getImageRegistry().get("echo_password"));
        bEchoKeystorePassword.setToolTipText(Messages.echoPassword);
        data = new FormData();
        data.top = new FormAttachment(tKeystorePassword, 0, SWT.CENTER);
        data.left = new FormAttachment(tKeystorePassword, Globals.MARGIN);
        bEchoKeystorePassword.setLayoutData(data);

        // Elements for group "Key"
        Label lKeyName = new Label(gKey, SWT.SHADOW_IN);
        lKeyName.setText(Messages.name);
        data = new FormData();
        data.width = LABELWIDTH;
        data.top = new FormAttachment(gKey);
        data.left = new FormAttachment(gKey);
        lKeyName.setLayoutData(data);

        tKeyName = new Text(gKey, SWT.SINGLE);
        tKeyName.setTextLimit(Globals.KEY_NAME_MAX_SIZE);
        data = new FormData();
        data.width = Globals.SHORT_TEXT_WIDTH;
        data.top = new FormAttachment(lKeyName, 0, SWT.CENTER);
        data.left = new FormAttachment(lKeyName);
        tKeyName.setLayoutData(data);

        Label lKeyPassword = new Label(gKey, SWT.SHADOW_IN);
        lKeyPassword.setText(Messages.password);
        data = new FormData();
        data.width = LABELWIDTH;
        data.top = new FormAttachment(lKeyName, Globals.MARGIN);
        data.left = new FormAttachment(gKey);
        lKeyPassword.setLayoutData(data);

        tKeyPassword = new Text(gKey, SWT.SINGLE);
        tKeyPassword.setTextLimit(Globals.KEYSTORE_PASSWORD_MAX_SIZE);
        data = new FormData();
        data.width = Globals.SHORT_TEXT_WIDTH;
        data.top = new FormAttachment(lKeyPassword, 0, SWT.CENTER);
        data.left = new FormAttachment(lKeyPassword);
        tKeyPassword.setEchoChar('*');
        tKeyPassword.setLayoutData(data);

        bEchoKeyPassword = new Button(gKey, SWT.PUSH);
        bEchoKeyPassword.setImage(XSTUIPlugin.getDefault().getImageRegistry().get("echo_password"));
        bEchoKeyPassword.setToolTipText(Messages.echoPassword);
        data = new FormData();
        data.top = new FormAttachment(tKeyPassword, 0, SWT.CENTER);
        data.left = new FormAttachment(tKeyPassword, Globals.MARGIN);
        bEchoKeyPassword.setLayoutData(data);

        // Elements for group "Encryption ID"
        cEncryptionId = new Combo(gEncryptionId, SWT.READ_ONLY);
        data = new FormData();
        data.top = new FormAttachment(gEncryptionId);
        data.left = new FormAttachment(gEncryptionId);
        data.width = Globals.COMBO_LARGE_WIDTH;
        cEncryptionId.setLayoutData(data);
    }

    /**
     * Determines all available encryption IDs in the XML document.<br>
     * The entry <i>Use first encryption ID</i> is always available and
     * selected per default.
     */
    private void determineIds() {
        String[] ids = null;

        try {
            ids = Utils.getIds(file, "encryption");
        } catch (Exception ex) {
            ids = new String[] {};
        }

        cEncryptionId.setItems(ids);
        cEncryptionId.select(0);
    }

    /**
     * Adds all listeners for the current wizard page.
     */
    private void addListeners() {
        bOpen.addListener(SWT.Selection, this);
        bEchoKeyPassword.addListener(SWT.Selection, this);
        bEchoKeystorePassword.addListener(SWT.Selection, this);
        cEncryptionId.addModifyListener(new ModifyListener() {
            public void modifyText(final ModifyEvent e) {
                dialogChanged();
            }
        });
        tKeystore.addModifyListener(new ModifyListener() {
            public void modifyText(final ModifyEvent e) {
                dialogChanged();
            }
        });
        tKeystorePassword.addModifyListener(new ModifyListener() {
            public void modifyText(final ModifyEvent e) {
                dialogChanged();
            }
        });
        tKeyName.addModifyListener(new ModifyListener() {
            public void modifyText(final ModifyEvent e) {
                dialogChanged();
            }
        });
        tKeyPassword.addModifyListener(new ModifyListener() {
            public void modifyText(final ModifyEvent e) {
                dialogChanged();
            }
        });
    }

    /**
     * Shows a message to the user to complete the fields on this page.
     *
     * @param message The message for the user
     * @param status The status type of the message
     */
    private void updateStatus(final String message, final int status) {
        setMessage(message, status);
        if (message == null && getErrorMessage() == null) {
            setPageComplete(true);
            saveDataToModel();
        } else {
            setPageComplete(false);
        }
    }

    /**
     * Determines the (error) message for the missing field.
     */
    private void dialogChanged() {
    	if (tKeystore.getText().length() == 0) {
        	updateStatus(Messages.missingKeystore, DialogPage.INFORMATION);
            return;
        } else if (!(new File(tKeystore.getText()).exists())) {
            updateStatus(Messages.keystoreNotFound, DialogPage.ERROR);
            return;
        }

        if (tKeystorePassword.getText().length() == 0) {
            updateStatus(Messages.missingKeystorePassword, DialogPage.INFORMATION);
            return;
        }

    	if (tKeyName.getText().length() == 0) {
            updateStatus(Messages.missingKeyName, DialogPage.INFORMATION);
            return;
        }

        if (tKeyPassword.getText().length() == 0) {
            updateStatus(Messages.missingKeyPassword, DialogPage.INFORMATION);
            return;
        }

        if (new File(tKeystore.getText()).exists()) {
            try {
                Keystore keystore = new Keystore(tKeystore.getText(), tKeystorePassword.getText(), Globals.KEYSTORE_TYPE);
                keystore.load();
                if (!keystore.containsKey(tKeyName.getText())) {
                    updateStatus(Messages.verifyKeyName, DialogPage.ERROR);
                    return;
                }

                if (keystore.getSecretKey(tKeyName.getText(), tKeyPassword.getText().toCharArray()) == null) {
                    updateStatus(Messages.verifyKeyPassword, DialogPage.ERROR);
                    return;
                }
            } catch (Exception ex) {
                updateStatus(Messages.verifyAll, DialogPage.ERROR);
                return;
            }
        } else {
            updateStatus(Messages.keystoreNotFound, DialogPage.ERROR);
            return;
        }

    	if (cEncryptionId.getText().equals("")) {
            updateStatus(Messages.missingEncryptionId, DialogPage.INFORMATION);
            return;
        }

        updateStatus(null, DialogPage.NONE);
    }

    /**
     * Handles the events from this wizard page.
     *
     * @param e The triggered event
     */
    public void handleEvent(final Event e) {
        if (e.widget == bOpen) {
            openKeystore();
        } else if (e.widget == bEchoKeystorePassword) {
            echoPassword(e);
        } else if (e.widget == bEchoKeyPassword) {
            echoPassword(e);
        }
    }

    /**
     * Shows plain text (\0) or cipher text (*) in the password field.
     *
     * @param e The triggered event
     */
    private void echoPassword(final Event e) {
        if (e.widget == bEchoKeystorePassword) {
            if (tKeystorePassword.getEchoChar() == '*') {
                tKeystorePassword.setEchoChar('\0');
            } else {
                tKeystorePassword.setEchoChar('*');
            }
            tKeystorePassword.redraw();
        } else if (e.widget == bEchoKeyPassword) {
            if (tKeyPassword.getEchoChar() == '*') {
                tKeyPassword.setEchoChar('\0');
            } else {
                tKeyPassword.setEchoChar('*');
            }
            tKeyPassword.redraw();
        }
    }

    /**
     * Dialog to select the Keystore to use in this decryption operation.
     */
    private void openKeystore() {
        FileDialog dialog = new FileDialog(getShell(), SWT.OPEN);
        dialog.setFilterNames(Globals.KEY_STORE_EXTENSION_NAME);
        dialog.setFilterExtensions(Globals.KEY_STORE_EXTENSION);
        dialog.setFilterPath(file.getLocation().removeFileExtension().removeLastSegments(1).toString());
        String fileName = dialog.open();

        if (fileName != null && !fileName.equals("")) {
            tKeystore.setText(fileName);
        }
    }

    /**
     * Sets the completed field on the wizard class when all the data is entered and
     * the wizard can be finished.
     *
     * @return Page is completed or not
     */
    public boolean isPageComplete() {
        saveDataToModel();
        if (getMessage() == null && getErrorMessage() == null) {
            return true;
        }
        return false;
    }

    /**
     * Saves the selections on this wizard page to the model. Called on exit of the page.
     */
    private void saveDataToModel() {
        decryption.setFile(file.getLocation().toString());
        decryption.setKeystore(tKeystore.getText());
        decryption.setKeystorePassword(tKeystorePassword.getText());
        decryption.setKeyName(tKeyName.getText());
        decryption.setKeyPassword(tKeyPassword.getText().toCharArray());
        decryption.setEncryptionId(cEncryptionId.getText());

        storeSettings();
    }

    /**
     * Loads the stored settings for this wizard page.
     */
    private void loadSettings() {
        String previousKeystore = getDialogSettings().get(NewDecryptionWizard.SETTING_KEYSTORE);
        if (previousKeystore == null) {
            previousKeystore = "";
        }
        tKeystore.setText(previousKeystore);

        String previousKey = getDialogSettings().get(NewDecryptionWizard.SETTING_KEY_NAME);
        if (previousKey == null) {
            previousKey = "";
        }
        tKeyName.setText(previousKey);
    }

    /**
     * Stores some settings of this wizard page in the current workspace.
     */
    private void storeSettings() {
        IDialogSettings settings = getDialogSettings();
        settings.put(NewDecryptionWizard.SETTING_KEYSTORE, tKeystore.getText());
        settings.put(NewDecryptionWizard.SETTING_KEY_NAME, tKeyName.getText());
    }
}