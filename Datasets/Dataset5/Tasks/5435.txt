keystore = new Keystore(file, tKeystorePassword.getText(), Globals.KEYSTORE_TYPE);

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

import java.util.HashMap;

import org.eclipse.jface.wizard.IWizardPage;
import org.eclipse.jface.wizard.WizardPage;
import org.eclipse.osgi.util.NLS;
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
import org.eclipse.wst.xml.security.core.utils.Algorithms;
import org.eclipse.wst.xml.security.core.utils.Globals;
import org.eclipse.wst.xml.security.core.utils.IContextHelpIds;
import org.eclipse.wst.xml.security.core.utils.Keystore;
import org.eclipse.wst.xml.security.core.utils.XmlSecurityCertificate;
import org.eclipse.wst.xml.security.core.utils.XmlSecurityImageRegistry;

/**
 * <p>Second alternative page of the Digital Signature Wizard. Lets the user create a new <i>key</i> in an existing
 * <i>Java Keystore</i>. The created key is automatically used to create this XML signature.</p>
 *
 * @author Dominik Schadow
 * @version 0.5.0
 */
public class PageCreateKey extends WizardPage implements Listener {
    /** Wizard page name. */
    public static final String PAGE_NAME = "SignPageCreateKey"; //$NON-NLS-1$
    /** KeyStore name. */
    private String keystoreName;
    /** Path of the opened project. */
    private String project;
    /** Key generation successful. */
    private boolean generatedKey = false;
    /** Open keystore button. */
    private Button bOpen = null;
    /** Create key button. */
    private Button bCreateKey = null;
    /** Button <i>Echo Keystore Password</i>. */
    private Button bEchoKeyStorePassword = null;
    /** Button <i>Echo Key Password</i>. */
    private Button bEchoKeyPassword = null;
    /** Algorithm combo. */
    private Combo cAlgorithm = null;
    /** Key preview label. */
    private Label lPreview = null;
    /** Key generation result label. */
    private Label lResult = null;
    /** Common Name text. */
    private Text tCommonName = null;
    /** Organizational Unit text. */
    private Text tOrganizationalUnit = null;
    /** Organization text. */
    private Text tOrganization = null;
    /** Location text. */
    private Text tLocation = null;
    /** State text. */
    private Text tState = null;
    /** Country text. */
    private Text tCountry = null;
    /** Key alias text. */
    private Text tKeyName = null;
    /** KeyStore textfield. */
    private Text tKeystore = null;
    /** KeyStore password text. */
    private Text tKeystorePassword = null;
    /** Key password text. */
    private Text tKeyPassword = null;
    /** Default label width. */
    private static final int LABELWIDTH = 160;
    /** Default preview textfield height. */
    private static final int TEXTHEIGHT = 40;
    /** Model for the XML Signature Wizard. */
    private Signature signature = null;
    /** The KeyStore containing all required key information. */
    private Keystore keystore = null;

    /**
     * Constructor for PageCreateKey.
     *
     * @param signature The signature wizard model
     * @param project The path of the opened project
     */
    public PageCreateKey(final Signature signature, final String project) {
        super(PAGE_NAME);
        setTitle(Messages.signatureTitle);
        setDescription(Messages.createKeyDescription);

        this.signature = signature;
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
        addListeners();
        setControl(container);
        setPageComplete(false);

        PlatformUI.getWorkbench().getHelpSystem().setHelp(getControl(), IContextHelpIds.WIZARD_SIGNATURE_CREATE_KEY);
    }

    /**
     * Fills this wizard page with content. Three groups (<i>Distinguished Name</i>, <i>Key</i> and <i>Keystore</i>)
     * and all their widgets are inserted.
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
        Group gDN = new Group(parent, SWT.SHADOW_ETCHED_IN);
        gDN.setLayout(layout);
        gDN.setText(Messages.certificate);
        FormData data = new FormData();
        data.top = new FormAttachment(0, 0);
        data.left = new FormAttachment(0, 0);
        data.right = new FormAttachment(Globals.GROUP_NUMERATOR);
        gDN.setLayoutData(data);

        Group gKey = new Group(parent, SWT.SHADOW_ETCHED_IN);
        gKey.setLayout(layout);
        gKey.setText(Messages.key);
        data = new FormData();
        data.top = new FormAttachment(gDN, Globals.MARGIN, SWT.DEFAULT);
        data.left = new FormAttachment(0, 0);
        data.right = new FormAttachment(Globals.GROUP_NUMERATOR);
        gKey.setLayoutData(data);

        Group gKeyStore = new Group(parent, SWT.SHADOW_ETCHED_IN);
        gKeyStore.setLayout(layout);
        gKeyStore.setText(Messages.keyStore);
        data = new FormData();
        data.top = new FormAttachment(gKey, Globals.MARGIN, SWT.DEFAULT);
        data.left = new FormAttachment(0, 0);
        data.right = new FormAttachment(Globals.GROUP_NUMERATOR);
        gKeyStore.setLayoutData(data);

        // Elements for group "Distinguished Name"
        Label lCommonName = new Label(gDN, SWT.SHADOW_IN);
        lCommonName.setText(Messages.commonName);
        data = new FormData();
        data.width = LABELWIDTH;
        data.top = new FormAttachment(gDN);
        data.left = new FormAttachment(gDN);
        lCommonName.setLayoutData(data);

        tCommonName = new Text(gDN, SWT.SINGLE);
        tCommonName.setTextLimit(Globals.KEY_DATA_LIMIT);
        data = new FormData();
        data.width = Globals.MEDIUM_TEXT_WIDTH;
        data.top = new FormAttachment(lCommonName, 0, SWT.CENTER);
        data.left = new FormAttachment(lCommonName);
        tCommonName.setLayoutData(data);

        Label lOrganizationalUnit = new Label(gDN, SWT.SHADOW_IN);
        lOrganizationalUnit.setText(Messages.organizationalUnit);
        data = new FormData();
        data.width = LABELWIDTH;
        data.top = new FormAttachment(lCommonName, Globals.MARGIN);
        data.left = new FormAttachment(gDN);
        lOrganizationalUnit.setLayoutData(data);

        tOrganizationalUnit = new Text(gDN, SWT.SINGLE);
        tOrganizationalUnit.setTextLimit(Globals.KEY_DATA_LIMIT);
        data = new FormData();
        data.width = Globals.MEDIUM_TEXT_WIDTH;
        data.top = new FormAttachment(lOrganizationalUnit, 0, SWT.CENTER);
        data.left = new FormAttachment(lOrganizationalUnit);
        tOrganizationalUnit.setLayoutData(data);

        Label lOrganization = new Label(gDN, SWT.SHADOW_IN);
        lOrganization.setText(Messages.organization);
        data = new FormData();
        data.width = LABELWIDTH;
        data.top = new FormAttachment(lOrganizationalUnit, Globals.MARGIN);
        data.left = new FormAttachment(gDN);
        lOrganization.setLayoutData(data);

        tOrganization = new Text(gDN, SWT.SINGLE);
        tOrganization.setTextLimit(Globals.KEY_DATA_LIMIT);
        data = new FormData();
        data.width = Globals.MEDIUM_TEXT_WIDTH;
        data.top = new FormAttachment(lOrganization, 0, SWT.CENTER);
        data.left = new FormAttachment(lOrganization);
        tOrganization.setLayoutData(data);

        Label lLocation = new Label(gDN, SWT.SHADOW_IN);
        lLocation.setText(Messages.location);
        data = new FormData();
        data.width = LABELWIDTH;
        data.top = new FormAttachment(lOrganization, Globals.MARGIN);
        data.left = new FormAttachment(gDN);
        lLocation.setLayoutData(data);

        tLocation = new Text(gDN, SWT.SINGLE);
        tLocation.setTextLimit(Globals.KEY_DATA_LIMIT);
        data = new FormData();
        data.width = Globals.MEDIUM_TEXT_WIDTH;
        data.top = new FormAttachment(lLocation, 0, SWT.CENTER);
        data.left = new FormAttachment(lLocation);
        tLocation.setLayoutData(data);

        Label lState = new Label(gDN, SWT.SHADOW_IN);
        lState.setText(Messages.state);
        data = new FormData();
        data.width = LABELWIDTH;
        data.top = new FormAttachment(lLocation, Globals.MARGIN);
        data.left = new FormAttachment(gDN);
        lState.setLayoutData(data);

        tState = new Text(gDN, SWT.SINGLE);
        tState.setTextLimit(Globals.KEY_DATA_LIMIT);
        data = new FormData();
        data.width = Globals.MEDIUM_TEXT_WIDTH;
        data.top = new FormAttachment(lState, 0, SWT.CENTER);
        data.left = new FormAttachment(lState);
        tState.setLayoutData(data);

        Label lCountry = new Label(gDN, SWT.SHADOW_IN);
        lCountry.setText(Messages.country);
        data = new FormData();
        data.width = LABELWIDTH;
        data.top = new FormAttachment(lState, Globals.MARGIN);
        data.left = new FormAttachment(gDN);
        lCountry.setLayoutData(data);

        tCountry = new Text(gDN, SWT.SINGLE);
        tCountry.setTextLimit(Globals.KEY_DATA_LIMIT);
        data = new FormData();
        data.width = Globals.MEDIUM_TEXT_WIDTH;
        data.top = new FormAttachment(lCountry, 0, SWT.CENTER);
        data.left = new FormAttachment(lCountry);
        tCountry.setLayoutData(data);

        lPreview = new Label(gDN, SWT.WRAP);
        data = new FormData();
        data.height = TEXTHEIGHT;
        data.top = new FormAttachment(lCountry, Globals.MARGIN);
        data.left = new FormAttachment(gDN);
        data.right = new FormAttachment(Globals.GROUP_NUMERATOR);
        lPreview.setLayoutData(data);

        // Elements for group "key"
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
        tKeyPassword.setTextLimit(Globals.KEY_PASSWORD_MAX_SIZE);
        data = new FormData();
        data.width = Globals.SHORT_TEXT_WIDTH;
        data.top = new FormAttachment(lKeyPassword, 0, SWT.CENTER);
        data.left = new FormAttachment(lKeyPassword);
        tKeyPassword.setEchoChar('*');
        tKeyPassword.setLayoutData(data);

        Label lKeyAlgorithm = new Label(gKey, SWT.SHADOW_IN);
        lKeyAlgorithm.setText(Messages.keyAlgorithm);
        data = new FormData();
        data.width = LABELWIDTH;
        data.top = new FormAttachment(lKeyPassword, Globals.MARGIN + 4);
        data.left = new FormAttachment(gKey);
        lKeyAlgorithm.setLayoutData(data);

        cAlgorithm = new Combo(gKey, SWT.READ_ONLY);
        data = new FormData();
        data.top = new FormAttachment(lKeyAlgorithm, 0, SWT.CENTER);
        data.left = new FormAttachment(lKeyAlgorithm);
        data.width = Globals.COMBO_WIDTH;
        cAlgorithm.setLayoutData(data);

        bEchoKeyPassword = new Button(gKey, SWT.PUSH);
        bEchoKeyPassword.setImage(XmlSecurityImageRegistry.getImageRegistry().get("echo_password"));
        data = new FormData();
        data.top = new FormAttachment(tKeyPassword, 0, SWT.CENTER);
        data.left = new FormAttachment(tKeyPassword, Globals.MARGIN);
        bEchoKeyPassword.setLayoutData(data);

        // Elements for group "Keystore"
        Label lKeyStore = new Label(gKeyStore, SWT.SHADOW_IN);
        lKeyStore.setText(Messages.name);
        data = new FormData();
        data.width = LABELWIDTH;
        data.top = new FormAttachment(gKeyStore);
        data.left = new FormAttachment(gKeyStore);
        lKeyStore.setLayoutData(data);

        tKeystore = new Text(gKeyStore, SWT.SINGLE);
        data = new FormData();
        data.top = new FormAttachment(lKeyStore, 0, SWT.CENTER);
        data.left = new FormAttachment(lKeyStore);
        data.width = Globals.SHORT_TEXT_WIDTH;
        tKeystore.setLayoutData(data);

        bOpen = new Button(gKeyStore, SWT.PUSH);
        bOpen.setText(Messages.open);
        data = new FormData();
        data.top = new FormAttachment(lKeyStore, 0, SWT.CENTER);
        data.left = new FormAttachment(tKeystore, Globals.MARGIN);
        bOpen.setLayoutData(data);

        Label lKeyStorePassword = new Label(gKeyStore, SWT.SHADOW_IN);
        lKeyStorePassword.setText(Messages.password);
        data = new FormData();
        data.width = LABELWIDTH;
        data.top = new FormAttachment(lKeyStore, Globals.MARGIN);
        data.left = new FormAttachment(gKeyStore);
        lKeyStorePassword.setLayoutData(data);

        tKeystorePassword = new Text(gKeyStore, SWT.SINGLE);
        tKeystorePassword.setTextLimit(Globals.KEYSTORE_PASSWORD_MAX_SIZE);
        data = new FormData();
        data.width = Globals.SHORT_TEXT_WIDTH;
        data.top = new FormAttachment(lKeyStorePassword, 0, SWT.CENTER);
        data.left = new FormAttachment(lKeyStorePassword);
        tKeystorePassword.setEchoChar('*');
        tKeystorePassword.setLayoutData(data);

        bEchoKeyStorePassword = new Button(gKeyStore, SWT.PUSH);
        bEchoKeyStorePassword.setImage(XmlSecurityImageRegistry.getImageRegistry().get("echo_password"));
        data = new FormData();
        data.top = new FormAttachment(tKeystorePassword, 0, SWT.CENTER);
        data.left = new FormAttachment(tKeystorePassword, Globals.MARGIN);
        bEchoKeyStorePassword.setLayoutData(data);

        bCreateKey = new Button(gKeyStore, SWT.PUSH);
        bCreateKey.setText(Messages.createKeyButton);
        bCreateKey.setEnabled(false);
        data = new FormData();
        data.top = new FormAttachment(lKeyStorePassword, Globals.MARGIN * 2);
        data.left = new FormAttachment(gKeyStore);
        bCreateKey.setLayoutData(data);

        lResult = new Label(gKeyStore, SWT.WRAP);
        data = new FormData();
        data.height = TEXTHEIGHT;
        data.top = new FormAttachment(bCreateKey, Globals.MARGIN * 2);
        data.left = new FormAttachment(gKeyStore);
        data.right = new FormAttachment(Globals.GROUP_NUMERATOR);
        lResult.setLayoutData(data);
    }

    /**
     * Adds all listeners for the current wizard page.
     */
    private void addListeners() {
        bOpen.addListener(SWT.Selection, this);
        bCreateKey.addListener(SWT.MouseDown, this);
        bEchoKeyStorePassword.addListener(SWT.Selection, this);
        bEchoKeyPassword.addListener(SWT.Selection, this);
        tCommonName.addModifyListener(new ModifyListener() {
            public void modifyText(final ModifyEvent e) {
                dialogChanged();
            }
        });
        tOrganizationalUnit.addModifyListener(new ModifyListener() {
            public void modifyText(final ModifyEvent e) {
                dialogChanged();
            }
        });
        tOrganization.addModifyListener(new ModifyListener() {
            public void modifyText(final ModifyEvent e) {
                dialogChanged();
            }
        });
        tLocation.addModifyListener(new ModifyListener() {
            public void modifyText(final ModifyEvent e) {
                dialogChanged();
            }
        });
        tState.addModifyListener(new ModifyListener() {
            public void modifyText(final ModifyEvent e) {
                dialogChanged();
            }
        });
        tCountry.addModifyListener(new ModifyListener() {
            public void modifyText(final ModifyEvent e) {
                dialogChanged();
            }
        });
        tKeyName.addModifyListener(new ModifyListener() {
            public void modifyText(final ModifyEvent e) {
                dialogChanged();
            }
        });
        tKeystorePassword.addModifyListener(new ModifyListener() {
            public void modifyText(final ModifyEvent e) {
                dialogChanged();
            }
        });
        tKeyPassword.addModifyListener(new ModifyListener() {
            public void modifyText(final ModifyEvent e) {
                dialogChanged();
            }
        });
        cAlgorithm.addModifyListener(new ModifyListener() {
            public void modifyText(final ModifyEvent e) {
                dialogChanged();
            }
        });
        tKeystore.addModifyListener(new ModifyListener() {
            public void modifyText(final ModifyEvent e) {
                dialogChanged();
            }
        });
    }

    /**
     * Determines the (error) message for the missing field.
     */
    private void dialogChanged() {
        if (tCommonName.getText().length() > 0) {
            lPreview.setText("CN=" + tCommonName.getText()); //$NON-NLS-1$
        } else {
            lPreview.setText(""); //$NON-NLS-1$
            updateStatus(Messages.enterCommonName);
            return;
        }
        if (tOrganizationalUnit.getText().length() > 0) {
            lPreview.setText("CN=" + tCommonName.getText() //$NON-NLS-1$
                    + ", OU=" + tOrganizationalUnit.getText()); //$NON-NLS-2$
        }
        if (tOrganization.getText().length() > 0) {
            lPreview.setText("CN=" + tCommonName.getText() //$NON-NLS-1$
                    + ", OU=" + tOrganizationalUnit.getText() //$NON-NLS-2$
                    + ", O=" + tOrganization.getText()); //$NON-NLS-1$
        }
        if (tLocation.getText().length() > 0) {
            lPreview.setText("CN=" + tCommonName.getText() //$NON-NLS-1$
                    + ", OU=" + tOrganizationalUnit.getText() //$NON-NLS-2$
                    + ", O=" + tOrganization.getText() //$NON-NLS-1$
                    + ", L=" + tLocation.getText()); //$NON-NLS-2$
        }
        if (tState.getText().length() > 0) {
            lPreview.setText("CN=" + tCommonName.getText() //$NON-NLS-1$
                    + ", OU=" + tOrganizationalUnit.getText() //$NON-NLS-1$
                    + ", O=" + tOrganization.getText() //$NON-NLS-1$
                    + ", L=" + tLocation.getText() //$NON-NLS-1$
                    + ", ST=" + tState.getText()); //$NON-NLS-1$
        }
        if (tCountry.getText().length() > 0) {
            lPreview.setText("CN=" + tCommonName.getText() //$NON-NLS-1$
                    + ", OU=" + tOrganizationalUnit.getText() //$NON-NLS-1$
                    + ", O=" + tOrganization.getText() //$NON-NLS-1$
                    + ", L=" + tLocation.getText() //$NON-NLS-1$
                    + ", ST=" + tState.getText() //$NON-NLS-1$
                    + ", C=" + tCountry.getText()); //$NON-NLS-1$
        }
        if (tKeyName.getText().length() < Globals.KEY_ALIAS_MIN_SIZE) {
            updateStatus(Messages.enterNewKeyAlias);
            return;
        }
        if (tKeyPassword.getText().length() < Globals.KEY_PASSWORD_MIN_SIZE) {
            updateStatus(Messages.enterNewKeyPassword);
            return;
        }
        if (cAlgorithm.getSelectionIndex() < 0) {
            updateStatus(Messages.selectKeyAlgorithm);
            return;
        }
        if (tKeystore.getText().length() == 0) {
            updateStatus(Messages.selectKeyFile);
            return;
        }
        if (tKeystorePassword.getText().length() == 0) {
            updateStatus(Messages.enterKeystorePassword);
            return;
        }

        if (tKeystore.getText().length() > 0 && tKeystorePassword.getText().length() > 0
                && tKeyName.getText().length() > 0) {
            String file = tKeystore.getText();
            keystoreName = file.substring(file.lastIndexOf(System.getProperty("file.separator")) + 1);

            try {
                keystore = new Keystore(file, tKeystorePassword.getText(), "JCEKS");
                boolean loaded = keystore.load();

                if (loaded) {
                    if (keystore.containsKey(tKeyName.getText())) {
                        setErrorMessage(Messages.keyExistsInKeystore);
                        return;
                    }
                } else {
                    setErrorMessage(Messages.verifyKeystorePassword);
                    return;
                }
            } catch (Exception e) {
                setErrorMessage(Messages.verifyAll);
                return;
            }
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
        if (!generatedKey && message == null) {
            bCreateKey.setEnabled(true);
        } else {
            bCreateKey.setEnabled(false);
        }
        setPageComplete(generatedKey);
    }

    /**
     * Handles the events from this wizard page.
     *
     * @param e The triggered event
     */
    public void handleEvent(final Event e) {
        if (e.widget == bOpen) {
            openKeystore();
        } else if (e.widget == bCreateKey) {
            try {
                generateCertificate();
                updateStatus(null);
            } catch (Exception e1) {
                updateStatus(Messages.keyGenerationFailed);
            }
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
            if (tKeystorePassword.getEchoChar() == '*') {
                // show plain text
                tKeystorePassword.setEchoChar('\0');
            } else {
                // show cipher text
                tKeystorePassword.setEchoChar('*');
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
            tKeystore.setText(file);
        }
    }

    /**
     * Generates the certificate based on the entered data and shows the user an information text about the result.
     *
     * @throws Exception to indicate any exceptional condition
     */
    private void generateCertificate() throws Exception {
        HashMap<String, String> certificateData = new HashMap<String, String>();
        certificateData.put("keystore", tKeystore.getText()); //$NON-NLS-1$
        certificateData.put("alias", tKeyName.getText()); //$NON-NLS-1$
        certificateData.put("keyalg", cAlgorithm.getText()); //$NON-NLS-1$
        certificateData.put("CN", tCommonName.getText()); //$NON-NLS-1$
        certificateData.put("OU", tOrganizationalUnit.getText()); //$NON-NLS-1$
        certificateData.put("O", tOrganization.getText()); //$NON-NLS-1$
        certificateData.put("L", tLocation.getText()); //$NON-NLS-1$
        certificateData.put("ST", tState.getText()); //$NON-NLS-1$
        certificateData.put("C", tCountry.getText()); //$NON-NLS-1$
        certificateData.put("keypass", tKeyPassword.getText()); //$NON-NLS-1$
        certificateData.put("storepass", tKeystorePassword.getText()); //$NON-NLS-1$

        XmlSecurityCertificate certificate = new XmlSecurityCertificate();
        generatedKey = keystore.generateCertificate(tKeyName.getText(), certificate);

        if (generatedKey) {
            lResult.setText(NLS.bind(Messages.keyGenerated, keystoreName));
            updateStatus(null);
        } else {
            lResult.setText(Messages.keyGenerationFailed);
        }
    }

    /**
     * Called on enter of the page to fill the certificate type combo box based on the Basic Security Profile selection
     * on the first wizard page. Preselects a default value in the combo box.
     */
    public void onEnterPage() {
        if (signature.getBsp()) { // BSP selected
            cAlgorithm.setItems(Algorithms.CERTIFICATE_ALGORITHMS_RSA);
            cAlgorithm.select(0);
        } else { // BSP not selected
            cAlgorithm.setItems(Algorithms.CERTIFICATE_ALGORITHMS);
            cAlgorithm.select(0);
        }
        setMessage(null);
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
        signature.setKeystorePassword(tKeystorePassword.getText().toCharArray());
        signature.setKeyPassword(tKeyPassword.getText().toCharArray());
        signature.setKeyAlias(tKeyName.getText());
        if (cAlgorithm.getText().equals("DSA")) {
            signature.setKeyAlgorithm("SHA1withDSA");
        } else if (cAlgorithm.getText().equals("EC")) {
            signature.setKeyAlgorithm("SHA1withECDSA");
        } else if (cAlgorithm.getText().equals("RSA")) {
            signature.setKeyAlgorithm("SHA1withRSA");
        }
    }
}