data.width = Globals.COMBO_LARGE_WIDTH;

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
package org.eclipse.wst.xml.security.core.decrypt;

import java.io.File;

import org.eclipse.core.resources.IFile;
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
import org.eclipse.wst.xml.security.core.utils.Globals;
import org.eclipse.wst.xml.security.core.utils.IContextHelpIds;
import org.eclipse.wst.xml.security.core.utils.Utils;
import org.eclipse.wst.xml.security.core.utils.XmlSecurityImageRegistry;

/**
 * <p>First and only page of the <strong>XML Decryption Wizard</strong>. Lets the user
 * select or enter the KeyStore containing the key used for encryption, the corresponding
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
public class PageAlgorithms extends WizardPage implements Listener {
    /** Wizard page name. */
    public static final String PAGE_NAME = "DecryptPageAlgorithms"; //$NON-NLS-1$
    /** Path of the opened project. */
    private String project;
    /** Button <i>Select...</i> for the KeyStore. */
    private Button bSelectKeyStore = null;
    /** Button <i>Echo Key Password</i>. */
     private Button bEchoKeyPassword = null;
     /** Button <i>Echo KeyStore Password</i>. */
     private Button bEchoKeyStorePassword = null;
    /** Combo box <i>Encryption ID</i>. */
    private Combo cEncryptionId = null;
    /** KeyStore file. */
    private Text tKeyStore = null;
    /** KeyStore password. */
    private Text tKeyStorePassword = null;
    /** Key name. */
    private Text tKeyName = null;
    /** Key password. */
    private Text tKeyPassword = null;
    /** Help message for the user. */
    private String helpMessage = "";
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
     * @param project The path of the opened project
     */
    public PageAlgorithms(final Decryption decryption, final IFile file, final String project) {
        super(PAGE_NAME);
        setTitle(Messages.decryptionTitle);
        setDescription(Messages.decryptionDescription);

        this.decryption = decryption;
        this.file = file;
        this.project = project;
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

        PlatformUI.getWorkbench().getHelpSystem().setHelp(getControl(), IContextHelpIds.WIZARD_DECRYPTION_RESOURCE);
    }

    /**
     * Fills this wizard page with content. Three groups (<i>KeyStore</i>, <i>Key</i> and
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
        Group gKeyStore = new Group(parent, SWT.SHADOW_ETCHED_IN);
        gKeyStore.setLayout(layout);
        gKeyStore.setText(Messages.keyStore);
        FormData data = new FormData();
        data.top = new FormAttachment(0, 0);
        data.left = new FormAttachment(0, 0);
        data.right = new FormAttachment(Globals.GROUP_NUMERATOR);
        gKeyStore.setLayoutData(data);

        Group gKey = new Group(parent, SWT.SHADOW_ETCHED_IN);
        gKey.setLayout(layout);
        gKey.setText(Messages.key);
        data = new FormData();
        data.top = new FormAttachment(gKeyStore, Globals.MARGIN, SWT.DEFAULT);
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

        // Elements for group "KeyStore"
        Label lKeyStoreName = new Label(gKeyStore, SWT.SHADOW_IN);
        lKeyStoreName.setText(Messages.name);
        data = new FormData();
        data.width = LABELWIDTH;
        data.top = new FormAttachment(gKeyStore);
        data.left = new FormAttachment(gKeyStore);
        lKeyStoreName.setLayoutData(data);

        tKeyStore = new Text(gKeyStore, SWT.SINGLE);
        data = new FormData();
        data.width = Globals.SHORT_TEXT_WIDTH;
        data.top = new FormAttachment(lKeyStoreName, 0, SWT.CENTER);
        data.left = new FormAttachment(lKeyStoreName);
        tKeyStore.setLayoutData(data);

        bSelectKeyStore = new Button(gKeyStore, SWT.PUSH);
        bSelectKeyStore.setText(Messages.selectButton);
        data = new FormData();
        data.top = new FormAttachment(tKeyStore, 0, SWT.CENTER);
        data.left = new FormAttachment(tKeyStore, Globals.MARGIN);
        bSelectKeyStore.setLayoutData(data);

        Label lKeyStorePassword = new Label(gKeyStore, SWT.SHADOW_IN);
        lKeyStorePassword.setText(Messages.password);
        data = new FormData();
        data.width = LABELWIDTH;
        data.top = new FormAttachment(lKeyStoreName, Globals.MARGIN);
        data.left = new FormAttachment(gKeyStore);
        lKeyStorePassword.setLayoutData(data);

        tKeyStorePassword = new Text(gKeyStore, SWT.SINGLE);
        tKeyStorePassword.setTextLimit(Globals.KEYSTORE_PASSWORD_MAX_SIZE);
        data = new FormData();
        data.width = Globals.SHORT_TEXT_WIDTH;
        data.top = new FormAttachment(lKeyStorePassword, 0, SWT.CENTER);
        data.left = new FormAttachment(lKeyStorePassword);
        tKeyStorePassword.setEchoChar('*');
        tKeyStorePassword.setLayoutData(data);

        bEchoKeyStorePassword = new Button(gKeyStore, SWT.PUSH);
        bEchoKeyStorePassword.setImage(XmlSecurityImageRegistry.getImageRegistry().get("echo_password"));
        bEchoKeyStorePassword.setToolTipText(Messages.echoPassword);
        data = new FormData();
        data.top = new FormAttachment(tKeyStorePassword, 0, SWT.CENTER);
        data.left = new FormAttachment(tKeyStorePassword, Globals.MARGIN);
        bEchoKeyStorePassword.setLayoutData(data);

        // Elements for group "Key"
        Label lKeyName = new Label(gKey, SWT.SHADOW_IN);
        lKeyName.setText(Messages.name);
        data = new FormData();
        data.width = LABELWIDTH;
        data.top = new FormAttachment(gKey);
        data.left = new FormAttachment(gKey);
        lKeyName.setLayoutData(data);

        tKeyName = new Text(gKey, SWT.SINGLE);
        tKeyName.setTextLimit(Globals.KEY_ALIAS_MAX_SIZE);
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
        bEchoKeyPassword.setImage(XmlSecurityImageRegistry.getImageRegistry().get("echo_password"));
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
        data.width = Globals.COMBO_WIDTH;
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
        bSelectKeyStore.addListener(SWT.Selection, this);
        bEchoKeyPassword.addListener(SWT.Selection, this);
        bEchoKeyStorePassword.addListener(SWT.Selection, this);
        cEncryptionId.addModifyListener(new ModifyListener() {
            public void modifyText(final ModifyEvent e) {
                dialogChanged();
            }
        });
        tKeyStore.addModifyListener(new ModifyListener() {
            public void modifyText(final ModifyEvent e) {
                dialogChanged();
            }
        });
        tKeyStorePassword.addModifyListener(new ModifyListener() {
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
     */
    private void updateStatus(final String message) {
        helpMessage = message;
        setMessage(message);
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
    	if (tKeyStore.getText().length() == 0) {
        	updateStatus(Messages.keyStoreText);
            return;
        } else if (!(new File(tKeyStore.getText()).exists())) {
            updateStatus(Messages.keyStoreNotFound);
            return;
        }

    	if (tKeyName.getText().length() == 0) {
            updateStatus(Messages.keyNameText);
            return;
        }

    	if (cEncryptionId.getText().equals("")) {
            updateStatus(Messages.encryptionIdText);
            return;
        }

    	setErrorMessage(null);
        updateStatus(null);
    }

    /**
     * Handles the events from this wizard page.
     *
     * @param e The triggered event
     */
    public void handleEvent(final Event e) {
        if (e.widget == bSelectKeyStore) {
            openKeyStore();
        } else if (e.widget == bEchoKeyStorePassword) {
            echoPassword(e);
        } else if (e.widget == bEchoKeyPassword) {
            echoPassword(e);
        }
    }

    /**
     * Shows plain text or cipher text in the password field.
     */
    private void echoPassword(final Event e) {
    	if (e.widget == bEchoKeyStorePassword) {
            if (tKeyStorePassword.getEchoChar() == '*') {
                tKeyStorePassword.setEchoChar('\0'); // show plain text
            } else {
                tKeyStorePassword.setEchoChar('*'); // show cipher text
            }
        } else if (e.widget == bEchoKeyPassword) {
            if (tKeyPassword.getEchoChar() == '*') {
            	tKeyPassword.setEchoChar('\0'); // show plain text
            } else {
            	tKeyPassword.setEchoChar('*');// show cipher text
            }
        }
    }

    /**
     * Dialog to select the KeyStore to use for decryption.
     */
    private void openKeyStore() {
        FileDialog dialog = new FileDialog(getShell(), SWT.OPEN);
        dialog.setFilterNames(Globals.KEY_STORE_EXTENSION_NAME);
        dialog.setFilterExtensions(Globals.KEY_STORE_EXTENSION);
        dialog.setFilterPath(project);
        String fileName = dialog.open();

        if (fileName != null && !fileName.equals("")) {
            tKeyStore.setText(fileName);
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
        if (helpMessage == null && getErrorMessage() == null) {
            return true;
        }
        return false;
    }

    /**
     * Saves the selections on this wizard page to the model. Called on exit of the page.
     */
    private void saveDataToModel() {
        decryption.setFile(file.getLocation().toString());
        decryption.setKeyStore(tKeyStore.getText());
        decryption.setKeyStorePassword(tKeyStorePassword.getText());
        decryption.setKeyName(tKeyName.getText());
        decryption.setKeyPassword(tKeyPassword.getText().toCharArray());
        decryption.setEncryptionId(cEncryptionId.getText());
    }
}