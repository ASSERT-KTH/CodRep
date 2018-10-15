keystore = new Keystore(tKeyStore.getText(), tKeyStorePassword.getText(), Globals.KEYSTORE_TYPE);

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

import java.io.File;

import org.eclipse.jface.dialogs.IDialogSettings;
import org.eclipse.jface.wizard.IWizardPage;
import org.eclipse.jface.wizard.WizardPage;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.ModifyEvent;
import org.eclipse.swt.events.ModifyListener;
import org.eclipse.swt.layout.FormAttachment;
import org.eclipse.swt.layout.FormData;
import org.eclipse.swt.layout.FormLayout;
import org.eclipse.swt.widgets.Button;
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
import org.eclipse.wst.xml.security.core.utils.Keystore;
import org.eclipse.wst.xml.security.core.utils.XmlSecurityImageRegistry;

/**
 * <p>Second default page of the Digital Signature Wizard. Lets the user select an existing <i>key</i> and enter the
 * corresponding information.</p>
 *
 * @author Dominik Schadow
 * @version 0.5.0
 */
public class PageOpenKey extends WizardPage implements Listener {
    /** Wizard page name. */
    public static final String PAGE_NAME = "SignPageOpenKey"; //$NON-NLS-1$
    /** Path of the opened project. */
    private String project;
    /** Open keystore button. */
    private Button bOpen = null;
    /** Button <i>Echo Keystore Password</i>. */
    private Button bEchoKeyStorePassword = null;
    /** Button <i>Echo Key Password</i>. */
    private Button bEchoKeyPassword = null;
    /** Keystore text. */
    private Text tKeyStore = null;
    /** Keystore password text. */
    private Text tKeyStorePassword = null;
    /** Key password text. */
    private Text tKeyPassword = null;
    /** Key alias text. */
    private Text tKeyName = null;
    /** Key algorithm: EC, DSA, RSA. */
    private String keyAlgorithm = "";
    /** Default label width. */
    private static final int LABELWIDTH = 120;
    /** Stored setting for the keystore. */
    private static final String SETTING_KEYSTORE = "sign_keystore";
    /** Stored setting for the key alias. */
    private static final String SETTING_KEY_ALIAS = "sign_key_alias";
    /** Model for the XML Digital Signature Wizard. */
    private Signature signature = null;
    /** The keystore containing all required key information. */
    private Keystore keystore = null;

    /**
     * Constructor for PageOpenKey.
     *
     * @param signature The signature wizard model
     * @param project The path of the opened project
     */
    public PageOpenKey(final Signature signature, final String project) {
        super(PAGE_NAME);
        setTitle(Messages.signatureTitle);
        setDescription(Messages.useKeyDescription);

        this.signature = signature;
        this.project = project;
    }

    /**
     * Creates the wizard page with the layout settings.
     *
     * @param parent The parent composite
     */
    public void createControl(final Composite parent) {
        Composite container = new Composite(parent, SWT.NULL);
        FormLayout formLayout = new FormLayout();
        container.setLayout(formLayout);

        createPageContent(container);
        addListeners();
        setControl(container);
        loadSettings();
        setPageComplete(false);

        PlatformUI.getWorkbench().getHelpSystem().setHelp(getControl(), IContextHelpIds.WIZARD_SIGNATURE_OPEN_KEY);
    }

    /**
     * Fills this wizard page with content. Two groups (<i>KeyStore</i> and <i>Key</i>) and all their widgets are
     * inserted.
     *
     * @param parent The parent composite
     */
    private void createPageContent(final Composite parent) {
        FormLayout layout = new FormLayout();
        layout.marginTop = Globals.MARGIN / 2;
        layout.marginBottom = Globals.MARGIN / 2;
        layout.marginLeft = Globals.MARGIN / 2;
        layout.marginRight = Globals.MARGIN / 2;
        parent.setLayout(layout);

        // Two groups
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

        // Elements for group "KeyStore"
        Label lKeyStore = new Label(gKeyStore, SWT.SHADOW_IN);
        lKeyStore.setText(Messages.name);
        data = new FormData();
        data.width = LABELWIDTH;
        data.top = new FormAttachment(gKeyStore);
        data.left = new FormAttachment(gKeyStore);
        lKeyStore.setLayoutData(data);

        tKeyStore = new Text(gKeyStore, SWT.SINGLE);
        data = new FormData();
        data.top = new FormAttachment(lKeyStore, 0, SWT.CENTER);
        data.left = new FormAttachment(lKeyStore);
        data.width = Globals.SHORT_TEXT_WIDTH;
        tKeyStore.setLayoutData(data);

        bOpen = new Button(gKeyStore, SWT.PUSH);
        bOpen.setText(Messages.open);
        data = new FormData();
        data.top = new FormAttachment(lKeyStore, 0, SWT.CENTER);
        data.left = new FormAttachment(tKeyStore, Globals.MARGIN);
        bOpen.setLayoutData(data);

        Label lKeyStorePassword = new Label(gKeyStore, SWT.SHADOW_IN);
        lKeyStorePassword.setText(Messages.password);
        data = new FormData();
        data.top = new FormAttachment(lKeyStore, Globals.MARGIN);
        data.left = new FormAttachment(gKeyStore);
        data.width = LABELWIDTH;
        lKeyStorePassword.setLayoutData(data);

        tKeyStorePassword = new Text(gKeyStore, SWT.SINGLE);
        tKeyStorePassword.setTextLimit(Globals.KEYSTORE_PASSWORD_MAX_SIZE);
        data = new FormData();
        data.top = new FormAttachment(lKeyStorePassword, 0, SWT.CENTER);
        data.left = new FormAttachment(lKeyStorePassword);
        data.width = Globals.SHORT_TEXT_WIDTH;
        tKeyStorePassword.setEchoChar('*');
        tKeyStorePassword.setLayoutData(data);

        // Elements for group "Key"
        Label lKeyName = new Label(gKey, SWT.SHADOW_IN);
        lKeyName.setText(Messages.name);
        data = new FormData();
        data.top = new FormAttachment(gKey);
        data.left = new FormAttachment(gKey);
        data.width = LABELWIDTH;
        lKeyName.setLayoutData(data);

        tKeyName = new Text(gKey, SWT.SINGLE);
        tKeyName.setTextLimit(Globals.KEY_ALIAS_MAX_SIZE);
        data = new FormData();
        data.top = new FormAttachment(lKeyName, 0, SWT.CENTER);
        data.left = new FormAttachment(lKeyName);
        data.width = Globals.SHORT_TEXT_WIDTH;
        tKeyName.setLayoutData(data);

        Label lKeyPassword = new Label(gKey, SWT.SHADOW_IN);
        lKeyPassword.setText(Messages.password);
        data = new FormData();
        data.top = new FormAttachment(lKeyName, Globals.MARGIN);
        data.left = new FormAttachment(gKey);
        data.width = LABELWIDTH;
        lKeyPassword.setLayoutData(data);

        tKeyPassword = new Text(gKey, SWT.SINGLE);
        tKeyPassword.setTextLimit(Globals.KEY_PASSWORD_MAX_SIZE);
        data = new FormData();
        data.top = new FormAttachment(lKeyPassword, 0, SWT.CENTER);
        data.left = new FormAttachment(lKeyPassword);
        data.width = Globals.SHORT_TEXT_WIDTH;
        tKeyPassword.setEchoChar('*');
        tKeyPassword.setLayoutData(data);

        bEchoKeyStorePassword = new Button(gKeyStore, SWT.PUSH);
        bEchoKeyStorePassword.setImage(XmlSecurityImageRegistry.getImageRegistry().get("echo_password"));
        data = new FormData();
        data.top = new FormAttachment(tKeyStorePassword, 0, SWT.CENTER);
        data.left = new FormAttachment(tKeyStorePassword, Globals.MARGIN);
        bEchoKeyStorePassword.setLayoutData(data);

        bEchoKeyPassword = new Button(gKey, SWT.PUSH);
        bEchoKeyPassword.setImage(XmlSecurityImageRegistry.getImageRegistry().get("echo_password"));
        data = new FormData();
        data.top = new FormAttachment(tKeyPassword, 0, SWT.CENTER);
        data.left = new FormAttachment(tKeyPassword, Globals.MARGIN);
        bEchoKeyPassword.setLayoutData(data);
    }

    /**
     * Adds all listeners for the current wizard page.
     */
    private void addListeners() {
        bOpen.addListener(SWT.Selection, this);
        bEchoKeyStorePassword.addListener(SWT.Selection, this);
        bEchoKeyPassword.addListener(SWT.Selection, this);
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
        tKeyPassword.addModifyListener(new ModifyListener() {
            public void modifyText(final ModifyEvent e) {
                dialogChanged();
            }
        });
        tKeyName.addModifyListener(new ModifyListener() {
            public void modifyText(final ModifyEvent e) {
                dialogChanged();
            }
        });
    }

    /**
     * Determines the (error) message for the missing field.
     */
    private void dialogChanged() {
        if (tKeyStore.getText().length() == 0) {
            updateStatus(Messages.selectKeyFile);
            return;
        }
        if (tKeyStorePassword.getText().length() == 0) {
            updateStatus(Messages.enterKeystorePassword);
            return;
        }
        if (tKeyName.getText().length() == 0) {
            updateStatus(Messages.enterKeyAlias);
            return;
        }
        if (tKeyPassword.getText().length() == 0) {
            updateStatus(Messages.enterKeyPassword);
            return;
        }

        if (new File(tKeyStore.getText()).exists()) {
            try {
                keystore = new Keystore(tKeyStore.getText(), tKeyStorePassword.getText(), "JCEKS");
                keystore.load();
                if (!keystore.containsKey(tKeyName.getText())) {
                    setErrorMessage(Messages.verifyKeyAlias);
                    return;
                }
            } catch (Exception ex) {
                setErrorMessage(Messages.verifyAll);
                return;
            }
        } else {
            updateStatus(Messages.keyStoreNotFound);
            return;
        }
        setErrorMessage(null);
        updateStatus(null);
    }

    /**
     * Shows a message to the user to complete the fields on this page.
     *
     * @param message The message for the user
     */
    private void updateStatus(final String message) {
        setMessage(message);
        if (message == null && getErrorMessage() == null) {
            setPageComplete(true);
            saveDataToModel();
        } else {
            setPageComplete(false);
        }
    }

    /**
     * Handles the events from this wizard page.
     *
     * @param e The triggered event
     */
    public void handleEvent(final Event e) {
        if (e.widget == bOpen) {
            openKeystore();
        } else if (e.widget == bEchoKeyStorePassword || e.widget == bEchoKeyPassword) {
            echoPassword(e);
        }
    }

    /**
     * Shows plain text or cipher text in the password field.
     *
     * @param e The triggered event
     */
    private void echoPassword(final Event e) {
        if (e.widget == bEchoKeyStorePassword) {
            if (tKeyStorePassword.getEchoChar() == '*') {
                // show plain text
                tKeyStorePassword.setEchoChar('\0');
            } else {
                // show cipher text
                tKeyStorePassword.setEchoChar('*');
            }
        } else if (e.widget == bEchoKeyPassword) {
            if (tKeyPassword.getEchoChar() == '*') {
                // show plain text
                tKeyPassword.setEchoChar('\0');
            } else {
                // show cipher text
                tKeyPassword.setEchoChar('*');
            }
        }
    }

    /**
     * Opens a FileDialog to select the .jks Keystore file to use in this signing session.
     */
    private void openKeystore() {
        FileDialog dialog = new FileDialog(getShell(), SWT.OPEN);
        dialog.setFilterNames(Globals.KEY_STORE_EXTENSION_NAME);
        dialog.setFilterExtensions(Globals.KEY_STORE_EXTENSION);
        dialog.setFilterPath(project);
        String file = dialog.open();
        if (file != null && file.length() > 0) {
            tKeyStore.setText(file);
        }
    }

    /**
     * Returns the next wizard page after all the necessary data is entered correctly.
     *
     * @return IWizardPage The next wizard page
     */
    public IWizardPage getNextPage() {
        saveDataToModel();
        PageAlgorithms page = ((NewSignatureWizard) getWizard()).getPageAlgorithms();
        page.onEnterPage();
        return page;
    }

    /**
     * Saves the selections on this wizard page to the model. Called on exit of the page.
     */
    private void saveDataToModel() {
        signature.setKeystore(keystore);
        signature.setKeyAlgorithm(keyAlgorithm);
        signature.setKeystorePassword(tKeyStorePassword.getText().toCharArray());
        signature.setKeyPassword(tKeyPassword.getText().toCharArray());
        signature.setKeyAlias(tKeyName.getText());
    }

    /**
     * Loads the stored settings for this wizard page.
     */
    private void loadSettings() {
        String keystore = getDialogSettings().get(SETTING_KEYSTORE);
        String setKeystore = "";
        if (keystore != null) {
            setKeystore = getDialogSettings().get(SETTING_KEYSTORE);
        }
        tKeyStore.setText(setKeystore);

        String keyAlias = getDialogSettings().get(SETTING_KEY_ALIAS);
        String setKeyAlias = "";
        if (keyAlias != null) {
            setKeyAlias = getDialogSettings().get(SETTING_KEY_ALIAS);
        }
        tKeyName.setText(setKeyAlias);
    }

    /**
     * Stores some settings of this wizard page in the current workspace.
     */
    protected void storeSettings() {
        IDialogSettings settings = getDialogSettings();
        settings.put(SETTING_KEYSTORE, tKeyStore.getText());
        settings.put(SETTING_KEY_ALIAS, tKeyName.getText());
    }
}