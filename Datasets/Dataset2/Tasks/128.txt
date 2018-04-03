IMAPServer server = new IMAPServer((ImapItem)serverItem);

// The contents of this file are subject to the Mozilla Public License Version
// 1.1
//(the "License"); you may not use this file except in compliance with the
//License. You may obtain a copy of the License at http://www.mozilla.org/MPL/
//
//Software distributed under the License is distributed on an "AS IS" basis,
//WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
//for the specific language governing rights and
//limitations under the License.
//
//The Original Code is "The Columba Project"
//
//The Initial Developers of the Original Code are Frederik Dietz and Timo
// Stich.
//Portions created by Frederik Dietz and Timo Stich are Copyright (C) 2003.
//
//All Rights Reserved.

package org.columba.mail.gui.config.account;

import java.awt.Font;
import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.Insets;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.io.File;
import java.text.MessageFormat;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;
import java.util.logging.Logger;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import javax.swing.BorderFactory;
import javax.swing.JButton;
import javax.swing.JCheckBox;
import javax.swing.JComboBox;
import javax.swing.JDialog;
import javax.swing.JLabel;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JSpinner;
import javax.swing.JTextField;
import javax.swing.SpinnerNumberModel;
import javax.swing.SwingUtilities;

import org.columba.core.config.Config;
import org.columba.core.config.IDefaultItem;
import org.columba.core.gui.base.ButtonWithMnemonic;
import org.columba.core.gui.base.CheckBoxWithMnemonic;
import org.columba.core.gui.base.LabelWithMnemonic;
import org.columba.core.gui.exception.ExceptionHandler;
import org.columba.mail.config.AccountItem;
import org.columba.mail.config.ImapItem;
import org.columba.mail.config.IncomingItem;
import org.columba.mail.config.MailConfig;
import org.columba.mail.config.PopItem;
import org.columba.mail.imap.IMAPServer;
import org.columba.mail.pop3.POP3Store;
import org.columba.mail.util.MailResourceLoader;
import org.columba.ristretto.imap.IMAPProtocol;
import org.columba.ristretto.pop3.POP3Protocol;

import com.jgoodies.forms.builder.DefaultFormBuilder;
import com.jgoodies.forms.layout.FormLayout;

/**
 * @author fdietz
 */
public class IncomingServerPanel extends DefaultPanel implements
        ActionListener {
    
    /** JDK 1.4+ logging framework logger, used for logging. */
    private static final Logger LOG = Logger
            .getLogger("org.columba.mail.gui.config.account");
    
    private static final Pattern AUTH_MODE_TOKENIZE_PATTERN = Pattern
            .compile("(\\d+);?");
    
    private JLabel loginLabel;
    private JTextField loginTextField;
    private JLabel passwordLabel;
    private JTextField passwordTextField;
    private JLabel hostLabel;
    private JTextField hostTextField;
    private JLabel portLabel;
    private JSpinner portSpinner;
    private JLabel typeLabel;
    private JComboBox typeComboBox;
    private JCheckBox storePasswordCheckBox;
    private JCheckBox secureCheckBox;
    private JLabel authenticationLabel;
    private JComboBox authenticationComboBox;
    private JLabel typeDescriptionLabel;
    private PopAttributPanel popPanel;
    private ImapAttributPanel imapPanel;
    
    private IDefaultItem serverItem = null;
    private AccountItem accountItem;
    
    private JCheckBox defaultAccountCheckBox;
    private ReceiveOptionsPanel receiveOptionsPanel;
    private JButton checkAuthMethods;
    private JComboBox sslComboBox;
    
    //private ConfigFrame frame;
    private JDialog dialog;
    
    public IncomingServerPanel(JDialog dialog, AccountItem account,
            ReceiveOptionsPanel receiveOptionsPanel) {
        super();
        
        this.dialog = dialog;
        
        this.accountItem = account;
        this.receiveOptionsPanel = receiveOptionsPanel;
        
        if (account.isPopAccount()) {
            serverItem = account.getPopItem();
        } else {
            serverItem = account.getImapItem();
        }
        
        initComponents();
        
        updateComponents(true);
    }
    
    public String getHost() {
        return hostTextField.getText();
    }
    
    public String getLogin() {
        return loginTextField.getText();
    }
    
    public boolean isPopAccount() {
        return accountItem.isPopAccount();
    }
    
    protected void updateComponents(boolean b) {
        if (b) {
            loginTextField.setText(serverItem.get(IncomingItem.USER));
            passwordTextField.setText(serverItem.get(IncomingItem.PASSWORD));
            hostTextField.setText(serverItem.get(IncomingItem.HOST));
            String port = serverItem.get(IncomingItem.PORT);
            portSpinner.setValue(new Integer(port));
            
            storePasswordCheckBox.setSelected(serverItem
                    .getBoolean(IncomingItem.SAVE_PASSWORD));
            
            defaultAccountCheckBox.setSelected(serverItem
                    .getBoolean(IncomingItem.USE_DEFAULT_ACCOUNT));
            
            try {
                authenticationComboBox.setSelectedItem(new Integer(serverItem
                        .get(IncomingItem.LOGIN_METHOD)));
            } catch (NumberFormatException e) {
            }
            
            // disable the actionlistener for this period
            // to avoid an unwanted port check
            secureCheckBox.removeActionListener(this);
            sslComboBox.removeActionListener(this);
            
            secureCheckBox.setSelected(serverItem.getBooleanWithDefault(IncomingItem.ENABLE_SSL,
                    false));
            
            sslComboBox.setSelectedIndex(serverItem.getIntegerWithDefault(IncomingItem.SSL_TYPE, 1));
            sslComboBox.setEnabled(secureCheckBox.isSelected());
            // reactivate
            secureCheckBox.addActionListener(this);
            sslComboBox.addActionListener(this);
            
            defaultAccountCheckBox.setEnabled(
                MailConfig.getInstance().getAccountList().getDefaultAccountUid() !=
                    accountItem.getInteger(IncomingItem.UID));
            
            if (defaultAccountCheckBox.isEnabled() && defaultAccountCheckBox.isSelected()) {
                showDefaultAccountWarning();
            } else {
                layoutComponents();
            }
        } else {
            serverItem.setString(IncomingItem.USER, loginTextField.getText());
            serverItem.setString(IncomingItem.HOST, hostTextField.getText());
            serverItem.setString(IncomingItem.PASSWORD, passwordTextField.getText());
            serverItem.setString(IncomingItem.PORT, ((Integer) portSpinner.getValue()).toString());
            
            serverItem.setBoolean(IncomingItem.SAVE_PASSWORD, storePasswordCheckBox.isSelected());
            
            serverItem.setBoolean(IncomingItem.ENABLE_SSL, secureCheckBox.isSelected());
            serverItem.setInteger(IncomingItem.SSL_TYPE, sslComboBox.getSelectedIndex());
            
            // if securest write DEFAULT
            serverItem.setString(IncomingItem.LOGIN_METHOD,
                    authenticationComboBox.getSelectedItem().toString());
            
            serverItem.setBoolean(IncomingItem.USE_DEFAULT_ACCOUNT, defaultAccountCheckBox
                    .isSelected());
            
            serverItem.getRoot().notifyObservers();
        }
    }
    
    protected void showDefaultAccountWarning() {
        setBorder(BorderFactory.createEmptyBorder(5, 5, 5, 5));
        
        GridBagLayout mainLayout = new GridBagLayout();
        GridBagConstraints mainConstraints = new GridBagConstraints();
        
        setLayout(mainLayout);
        
        mainConstraints.gridwidth = GridBagConstraints.REMAINDER;
        mainConstraints.anchor = GridBagConstraints.NORTHWEST;
        mainConstraints.weightx = 1.0;
        mainConstraints.insets = new Insets(0, 10, 5, 0);
        mainLayout.setConstraints(defaultAccountCheckBox, mainConstraints);
        add(defaultAccountCheckBox);
        
        mainConstraints = new GridBagConstraints();
        mainConstraints.weighty = 1.0;
        mainConstraints.gridwidth = GridBagConstraints.REMAINDER;
        
        /*
         * mainConstraints.fill = GridBagConstraints.BOTH;
         * mainConstraints.insets = new Insets(0, 0, 0, 0);
         * mainConstraints.gridwidth = GridBagConstraints.REMAINDER;
         * mainConstraints.weightx = 1.0; mainConstraints.weighty = 1.0;
         */
        JLabel label = new JLabel(MailResourceLoader.getString("dialog",
                "account", "using_default_account_settings"));
        Font newFont = label.getFont().deriveFont(Font.BOLD);
        label.setFont(newFont);
        mainLayout.setConstraints(label, mainConstraints);
        add(label);
    }
    
    protected void layoutComponents() {
        // Create a FormLayout instance.
        FormLayout layout = new FormLayout(
                "10dlu, max(70dlu;default), 3dlu, fill:max(150dlu;default):grow, 3dlu, default, 3dlu, default",
                
                // 2 columns
                ""); // rows are added dynamically (no need to
        // define them here)
        
        JPanel topPanel = new JPanel();
        
        // create a form builder
        DefaultFormBuilder builder = new DefaultFormBuilder(this, layout);
        
        // create EmptyBorder between components and dialog-frame
        builder.setDefaultDialogBorder();
        
        //		skip the first column
        builder.setLeadingColumnOffset(1);
        
        // Add components to the panel:
        builder.append(defaultAccountCheckBox, 7);
        builder.nextLine();
        
        builder.appendSeparator(MailResourceLoader.getString("dialog",
                "account", "configuration"));
        builder.nextLine();
        
        builder.append(loginLabel, 1);
        builder.append(loginTextField, 5);
        builder.nextLine();
        
        builder.append(hostLabel, 1);
        builder.append(hostTextField);
        //builder.nextLine();
        
        builder.append(portLabel);
        builder.append(portSpinner);
        builder.nextLine();
        
        builder.appendSeparator(MailResourceLoader.getString("dialog",
                "account", "security"));
        builder.nextLine();
        
        JPanel panel = new JPanel();
        FormLayout l = new FormLayout(
                "default, 3dlu, fill:pref:grow, 3dlu, fill:pref:grow",
                
                // 2 columns
                "fill:default:grow"); // rows are added dynamically (no need to
        // define them here)
        
        // create a form builder
        DefaultFormBuilder b = new DefaultFormBuilder(panel, l);
        b.append(authenticationLabel, authenticationComboBox, checkAuthMethods);
        builder.append(panel, 3);
        builder.nextLine();
        
        builder.append(secureCheckBox, 3);
        builder.nextLine();
        
        JPanel panel2 = new JPanel();
        FormLayout l2 = new FormLayout("default, 3dlu, left:pref",
                
                // 2 columns
                "fill:default:grow"); // rows are added dynamically (no need to
        // define them here)
        
        // create a form builder
        DefaultFormBuilder b2 = new DefaultFormBuilder(panel2, l2);
        b2.setRowGroupingEnabled(true);
        b2.append(secureCheckBox, sslComboBox);
        builder.append(panel2, 3);
        builder.nextLine();
        
        builder.append(storePasswordCheckBox, 3);
        builder.nextLine();
        
        /*
         * builder.append(sslLabel, 3); builder.nextLine();
         *
         * builder.append(disableSSLConnectionRadioButton, 2);
         * builder.nextLine(); builder.append(enableSSLConnectionRadioButton,
         * 2); builder.nextLine();
         * builder.append(enableSTARTTLSExtensionRadioButton, 2);
         * builder.nextLine();
         */
    }
    
    protected void initComponents() {
        defaultAccountCheckBox = new CheckBoxWithMnemonic(MailResourceLoader
                .getString("dialog", "account", "use_default_account_settings"));
        
        defaultAccountCheckBox.setActionCommand("DEFAULT_ACCOUNT");
        defaultAccountCheckBox.addActionListener(this);
        
        //defaultAccountCheckBox.setEnabled(false);
        typeLabel = new LabelWithMnemonic(MailResourceLoader.getString(
                "dialog", "account", "server_type"));
        
        typeComboBox = new JComboBox();
        typeComboBox.addItem("POP3");
        typeComboBox.addItem("IMAP4");
        
        if (accountItem.isPopAccount()) {
            typeComboBox.setSelectedIndex(0);
        } else {
            typeComboBox.setSelectedIndex(1);
        }
        
        typeLabel.setLabelFor(typeComboBox);
        typeComboBox.setEnabled(false);
        
        //TODO: i18n?
        typeDescriptionLabel = new JLabel(
                "Description: To connect to and fetch new messages from a POP3-server.");
        typeDescriptionLabel.setEnabled(false);
        
        loginLabel = new LabelWithMnemonic(MailResourceLoader.getString(
                "dialog", "account", "login"));
        
        loginTextField = new JTextField();
        loginLabel.setLabelFor(loginTextField);
        passwordLabel = new LabelWithMnemonic(MailResourceLoader.getString(
                "dialog", "account", IncomingItem.PASSWORD));
        
        passwordTextField = new JTextField();
        
        hostLabel = new LabelWithMnemonic(MailResourceLoader.getString(
                "dialog", "account", IncomingItem.HOST));
        
        hostTextField = new JTextField();
        hostLabel.setLabelFor(hostTextField);
        
        portLabel = new LabelWithMnemonic(MailResourceLoader.getString(
                "dialog", "account", IncomingItem.PORT));
        
        portSpinner = new JSpinner(new SpinnerNumberModel(100, 1, 65535, 1));
        portSpinner.setEditor(new JSpinner.NumberEditor(portSpinner,"#####"));
        portLabel.setLabelFor(portSpinner);
        
        storePasswordCheckBox = new CheckBoxWithMnemonic(
                MailResourceLoader.getString("dialog", "account",
                "store_password_in_configuration_file"));
        
        storePasswordCheckBox.setActionCommand("SAVE");
        storePasswordCheckBox.addActionListener(this);
        
        secureCheckBox = new CheckBoxWithMnemonic(MailResourceLoader.getString(
                "dialog", "account", "use_SSL_for_secure_connection"));
        secureCheckBox.setActionCommand("SSL");
        secureCheckBox.addActionListener(this);
        
        authenticationLabel = new LabelWithMnemonic(
                MailResourceLoader.getString("dialog", "account", 
                "authentication_type"));
        
        authenticationComboBox = new JComboBox();
        authenticationComboBox.setRenderer( new AuthenticationListCellRenderer() );
        authenticationLabel.setLabelFor(authenticationComboBox);
        
        updateAuthenticationComboBox();
        
        checkAuthMethods = new ButtonWithMnemonic(MailResourceLoader.getString(
                "dialog", "account", "authentication_checkout_methods"));
        checkAuthMethods.setActionCommand("CHECK_AUTHMETHODS");
        checkAuthMethods.addActionListener(this);
        
        sslComboBox = new JComboBox();
        if (isPopAccount()) {
            sslComboBox.addItem(MailResourceLoader.getString("dialog",
                    "account", "pop3s_in_checkbox"));
        } else {
            sslComboBox.addItem(MailResourceLoader.getString("dialog",
                    "account", "imaps_in_checkbox"));
        }
        sslComboBox.addItem(MailResourceLoader.getString("dialog", "account",
                "tls_in_checkbox"));
        sslComboBox.setActionCommand("SSL");
        sslComboBox.addActionListener(this);
    }
    
    private void updateAuthenticationComboBox() {
        authenticationComboBox.removeAllItems();
        
        authenticationComboBox.addItem(new Integer(0));
        
        String authMethods;
        if (isPopAccount()) {
            authMethods = accountItem.getString(IncomingItem.POPSERVER,
                    "authentication_methods");
        } else {
            authMethods = accountItem.getString("imapserver",
                    "authentication_methods");
        }
        // Add previously fetch authentication modes
        if (authMethods != null) {
            Matcher matcher = AUTH_MODE_TOKENIZE_PATTERN.matcher(authMethods);
            
            while (matcher.find()) {
                authenticationComboBox.addItem(new Integer(matcher.group(1)));
            }
        }
    }
    
    public void actionPerformed(ActionEvent e) {
        String action = e.getActionCommand();
        
        if (action.equals("SERVER")) {//$NON-NLS-1$
            LOG.info("selection changed");
        } else if (action.equals("DEFAULT_ACCOUNT")) {
            removeAll();
            receiveOptionsPanel.removeAll();
            
            if (defaultAccountCheckBox.isSelected()) {
                showDefaultAccountWarning();
                receiveOptionsPanel.showDefaultAccountWarning();
            } else {
                layoutComponents();
                receiveOptionsPanel.layoutComponents();
            }
            
            revalidate();
            receiveOptionsPanel.revalidate();
        } else if (action.equals("CHECK_AUTHMETHODS")) {
            fetchAuthMechanisms();
        } else if (action.equals("SSL")) {
            sslComboBox.setEnabled(secureCheckBox.isSelected());
            
            if (secureCheckBox.isSelected()) {
                // Update the Port
                if (sslComboBox.getSelectedIndex() == IncomingItem.TLS) {
                    // Default Port
                    if (isPopAccount()) {
                        if (((Integer) portSpinner.getValue()).intValue() != POP3Protocol.DEFAULT_PORT) {
                            portSpinner.setValue(new Integer(
                                    POP3Protocol.DEFAULT_PORT));
                            showPortChangeMessageBox();
                        }
                    } else {
                        if (((Integer) portSpinner.getValue()).intValue() != IMAPProtocol.DEFAULT_PORT) {
                            portSpinner.setValue(new Integer(
                                    IMAPProtocol.DEFAULT_PORT));
                            showPortChangeMessageBox();
                        }
                    }
                } else {
                    // POP3s / IMAPs
                    if (isPopAccount()) {
                        if (((Integer) portSpinner.getValue()).intValue() != POP3Protocol.DEFAULT_SSL_PORT) {
                            portSpinner.setValue(new Integer(
                                    POP3Protocol.DEFAULT_SSL_PORT));
                            showPortChangeMessageBox();
                        }
                    } else {
                        if (((Integer) portSpinner.getValue()).intValue() != IMAPProtocol.DEFAULT_SSL_PORT) {
                            portSpinner.setValue(new Integer(
                                    IMAPProtocol.DEFAULT_SSL_PORT));
                            showPortChangeMessageBox();
                        }
                    }
                }
            } else {
                // Check for default Ports
                if (isPopAccount()) {
                    if (((Integer) portSpinner.getValue()).intValue() != POP3Protocol.DEFAULT_PORT) {
                        portSpinner.setValue(new Integer(POP3Protocol.DEFAULT_PORT));
                        showPortChangeMessageBox();
                    }
                } else {
                    if (((Integer) portSpinner.getValue()).intValue() != IMAPProtocol.DEFAULT_PORT) {
                        portSpinner.setValue(new Integer(IMAPProtocol.DEFAULT_PORT));
                        showPortChangeMessageBox();
                    }
                }
            }
        } else if (action.equals("SAVE")) {
            if (!storePasswordCheckBox.isSelected()) {
                return;
            } else {
                File configPath = Config.getInstance().getConfigDirectory();
                File defaultConfigPath = Config.getDefaultConfigPath();
                while (!configPath.equals(defaultConfigPath)) {
                    configPath = configPath.getParentFile();
                    if (configPath == null) {
                        JOptionPane.showMessageDialog(dialog, MailResourceLoader.getString(
                                "dialog",IncomingItem.PASSWORD, "warn_save_msg"),
                                MailResourceLoader.getString(
                                "dialog", IncomingItem.PASSWORD, "warn_save_title"),
                                JOptionPane.WARNING_MESSAGE);
                        return;
                    }
                }
            }
        }
    }
    
    /**
     *
     */
    private void showPortChangeMessageBox() {
        Runnable doHelloWorld = new Runnable() {
            public void run() {
                JOptionPane.showMessageDialog(dialog, 
                        MailResourceLoader.getString(
                        "dialog", "account", "change_port_ssl"),
                        "Information", JOptionPane.INFORMATION_MESSAGE);
            }
        };
        
        SwingUtilities.invokeLater(doHelloWorld);
    }
    
    private IDefaultItem getCurrentDialogSettings() {
        IDefaultItem server = null;
        
        if (accountItem.isPopAccount()) {
            server = (IDefaultItem)accountItem.getPopItem().clone();
        } else {
            server = (IDefaultItem)accountItem.getImapItem().clone();
        }
        
        server.setString(IncomingItem.USER, loginTextField.getText());
        server.setString(IncomingItem.HOST, hostTextField.getText());
        server.setString(IncomingItem.PASSWORD, passwordTextField.getText());
        server.setString(IncomingItem.PORT, ((Integer) portSpinner.getValue()).toString());
        
        server.setBoolean(IncomingItem.ENABLE_SSL, secureCheckBox.isSelected());
        server.setInteger(IncomingItem.SSL_TYPE, sslComboBox.getSelectedIndex());
        
        return server;
    }
    
    private void fetchAuthMechanisms() {
        List list = new LinkedList();
        IDefaultItem serverItem = getCurrentDialogSettings();

        if (isPopAccount()) {
            //user may have changed hostname. use dialog settings instead of
            //stored settings

            POP3Store store = new POP3Store((PopItem)serverItem/*accountItem.getPopItem()*/);

            try {
                list = store.checkSupportedAuthenticationMethods();
            } catch (Exception e) {
                //let exception handler process other errors
                new ExceptionHandler().processException(e);
            }
        } else {
            IMAPServer server = new IMAPServer(/*accountItem.getImapItem()*/(ImapItem)serverItem,null);

            try {
                list = server.checkSupportedAuthenticationMethods();
            } catch (Exception e) {
                //let exception handler process other errors
                new ExceptionHandler().processException(e);
            }

        }

        // Save the authentication modes
        if (list.size() > 0) {
            StringBuffer authMethods = new StringBuffer();
            Iterator it = list.iterator();
            authMethods.append(it.next());

            while (it.hasNext()) {
                authMethods.append(';');
                authMethods.append(it.next());
            }

            if (isPopAccount()) {
                accountItem.setString(IncomingItem.POPSERVER, "authentication_methods", 
                        authMethods.toString());
            } else {
                accountItem.setString("imapserver", "authentication_methods", 
                        authMethods.toString());
            }

        }

        updateAuthenticationComboBox();
    }
    
    public boolean isFinished() {
        String host = getHost();
        String login = getLogin();
        
        if (host.length() == 0) {
            JOptionPane.showMessageDialog(null, MailResourceLoader.getString(
                    "dialog", "account", "You_have_to_enter_a_host_name"));
            
            //$NON-NLS-1$
            return false;
        } else if (login.length() == 0) {
            JOptionPane.showMessageDialog(null, MailResourceLoader.getString(
                    "dialog", "account", "You_have_to_enter_a_login_name"));
            
            //$NON-NLS-1$
            return false;
        } else if (defaultAccountCheckBox.isSelected()) {
            AccountItem defaultAccount =
                    MailConfig.getInstance().getAccountList().getDefaultAccount();
            
            if (defaultAccount.getAccountType() !=
                    accountItem.getAccountType()) {
                
                String errorMessage = MailResourceLoader.getString(
                        "dialog", "account", "cannot_use_default_account");
                
                Object[] accountType = new Object[]{
                    defaultAccount.getAccountTypeDescription()
                };
                
                errorMessage = MessageFormat.format(errorMessage,accountType);
                
                JOptionPane.showMessageDialog(null, errorMessage);
                
                return false;
            }
        }
        
        return true;
    }
}