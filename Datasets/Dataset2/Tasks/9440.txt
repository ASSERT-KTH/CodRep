portSpinner = new JSpinner(new SpinnerNumberModel(100, 1, 65535, 1));

//The contents of this file are subject to the Mozilla Public License Version 1.1
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
//The Initial Developers of the Original Code are Frederik Dietz and Timo Stich.
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
import java.io.IOException;
import java.net.InetAddress;
import java.util.Arrays;
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
import javax.swing.JLabel;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JRadioButton;
import javax.swing.JSpinner;
import javax.swing.JTextField;
import javax.swing.SpinnerNumberModel;

import org.columba.core.command.ExceptionHandler;
import org.columba.core.gui.util.ButtonWithMnemonic;
import org.columba.core.gui.util.CheckBoxWithMnemonic;
import org.columba.core.gui.util.DefaultFormBuilder;
import org.columba.core.gui.util.LabelWithMnemonic;
import org.columba.core.util.ListTools;
import org.columba.mail.config.AccountItem;
import org.columba.mail.config.SmtpItem;
import org.columba.mail.main.MailInterface;
import org.columba.mail.util.MailResourceLoader;
import org.columba.ristretto.auth.AuthenticationFactory;
import org.columba.ristretto.smtp.SMTPException;
import org.columba.ristretto.smtp.SMTPProtocol;

import com.jgoodies.forms.layout.FormLayout;


/**
 * @author freddy
 * @version
 */
public class OutgoingServerPanel extends DefaultPanel implements ActionListener {

    /** JDK 1.4+ logging framework logger, used for logging. */
    private static final Logger LOG = Logger.getLogger("org.columba.mail.gui.config.account");

    private static final Pattern AUTH_MODE_TOKENIZE_PATTERN = Pattern.compile(
            "([^;]+);?");
    private JLabel hostLabel;
    private JTextField hostTextField;
    private JLabel portLabel;
    private JSpinner portSpinner;
    private JRadioButton esmtpRadioButton;
    private JLabel loginLabel;
    private JTextField loginTextField;
    private JCheckBox secureCheckBox;
    private JCheckBox needAuthCheckBox;
    private JCheckBox bccyourselfCheckBox;
    private JLabel bccanotherLabel;
    private JTextField bccanotherTextField;
    private JButton selectButton;
    private JCheckBox storePasswordCheckBox;
    private JLabel authenticationLabel;
    private JComboBox authenticationComboBox;
    private JCheckBox defaultAccountCheckBox;
    private SmtpItem item;
    private AccountItem accountItem;
    private JButton checkAuthMethods;
    
    public OutgoingServerPanel(AccountItem accountItem) {
        super();

        this.accountItem = accountItem;
        item = accountItem.getSmtpItem();

        initComponents();

        updateComponents(true);
    }

    public String getHost() {
        return hostTextField.getText();
    }

    public String getLogin() {
        return loginTextField.getText();
    }

    public boolean isESmtp() {
        return needAuthCheckBox.isSelected();
    }

    protected void updateComponents(boolean b) {
        if (b) {
            hostTextField.setText(item.get("host"));

            String port = item.get("port");
            portSpinner.setValue(new Integer(port));

            loginTextField.setText(item.get("user"));

            storePasswordCheckBox.setSelected(item.getBoolean("save_password"));

            secureCheckBox.setSelected(item.getBoolean("enable_ssl", false));

            if (!item.get("login_method").equals("NONE")) {
                needAuthCheckBox.setSelected(true);

                storePasswordCheckBox.setEnabled(true);
                loginLabel.setEnabled(true);
                loginTextField.setEnabled(true);

                String loginMethod = item.get("login_method");
                authenticationComboBox.setSelectedItem(loginMethod);
            } else {
                needAuthCheckBox.setSelected(false);

                storePasswordCheckBox.setEnabled(false);
                loginLabel.setEnabled(false);
                loginTextField.setEnabled(false);
                authenticationLabel.setEnabled(false);
                authenticationComboBox.setEnabled(false);
            }

            defaultAccountCheckBox.setEnabled(MailInterface.config.getAccountList()
                                                                  .getDefaultAccountUid() != accountItem.getInteger(
                    "uid"));

            if (defaultAccountCheckBox.isEnabled()
                    && defaultAccountCheckBox.isSelected()) {
                showDefaultAccountWarning();
            } else {
                layoutComponents();
            }
        } else {
            item.set("user", loginTextField.getText());

            item.set("save_password", storePasswordCheckBox.isSelected()); //$NON-NLS-1$

            item.set("port", ((Integer)portSpinner.getValue()).toString());

            item.set("host", hostTextField.getText());

            // *20031025, karlpeder* Fixed bug which meant that it was impossible
            // to disable ssl.
            //item.set("enable_ssl", secureCheckBox.isEnabled());
            item.set("enable_ssl", secureCheckBox.isSelected());

            if (needAuthCheckBox.isSelected()) {
                if (authenticationComboBox.getSelectedIndex() == 0) {
                    item.set("login_method", "DEFAULT");
                } else {
                    String loginMethod = (String) authenticationComboBox.getSelectedItem();
                    item.set("login_method", loginMethod);
                }
            } else {
                item.set("login_method", "NONE"); //$NON-NLS-1$
            }

            item.set("use_default_account", defaultAccountCheckBox.isSelected());
        }
    }

    protected void layoutComponents() {
        //Create a FormLayout instance.
        FormLayout layout = new FormLayout("10dlu, 10dlu, max(60dlu;default), 3dlu, fill:max(150dlu;default):grow, 3dlu, default, 3dlu, default  ",

            // 2 columns
            ""); // rows are added dynamically (no need to define them here)

        JPanel topPanel = new JPanel();
        DefaultFormBuilder builder = new DefaultFormBuilder(this, layout);

        // create EmptyBorder between components and dialog-frame
        builder.setDefaultDialogBorder();

        // skip the first column
        builder.setLeadingColumnOffset(1);

        // Add components to the panel:
        builder.append(defaultAccountCheckBox, 7);
        builder.nextLine();

        builder.appendSeparator(MailResourceLoader.getString("dialog",
                "account", "configuration"));
        builder.nextLine();
        
        //builder.setLeadingColumnOffset(1);

        builder.append(loginLabel, 2);
        builder.append(loginTextField,5);
        builder.nextLine();
        
        builder.append(hostLabel, 2);
        builder.append(hostTextField);
        //builder.nextLine();

        builder.append(portLabel);
        builder.append(portSpinner);
        builder.nextLine();
        
        builder.setLeadingColumnOffset(1);
        
        

        builder.appendSeparator(MailResourceLoader.getString("dialog",
                "account", "security"));
        builder.nextLine();

        
        builder.append(needAuthCheckBox, 8);
        builder.nextLine();

        builder.setLeadingColumnOffset(2);

        JPanel panel = new JPanel();
        FormLayout l = new FormLayout("default, 3dlu, left:pref:grow, 3dlu, left:pref:grow",

            // 2 columns
        		"fill:default:grow"); // rows are added dynamically (no need to define them here)

        // create a form builder
        DefaultFormBuilder b = new DefaultFormBuilder(panel, l);
        b.append(authenticationLabel, authenticationComboBox, checkAuthMethods);
        //b.nextLine();
        //b.append(loginLabel, loginTextField);
        builder.append(panel, 5);
        builder.nextLine();

        /*
         * JPanel panel2 = new JPanel(); l = new FormLayout("max(100;default),
         * 3dlu, left:max(50dlu;default)", // 2 columns ""); // rows are added
         * dynamically (no need to define them here) // create a form builder b =
         * new DefaultFormBuilder(panel2, l); b.append(loginLabel,
         * loginTextField);
         *
         * builder.append(panel2, 3); builder.nextLine();
         */
        //builder.setLeadingColumnOffset(1);
        
        builder.append(secureCheckBox, 6);
        builder.nextLine();
        
        JPanel panel2 = new JPanel();
        FormLayout l2 = new FormLayout(
                "default, 3dlu, left:pref",

                // 2 columns
				"fill:default:grow"); // rows are added dynamically (no need to define them here)

        // create a form builder
        DefaultFormBuilder b2 = new DefaultFormBuilder(panel2, l2);
        b2.setRowGroupingEnabled(true);
        builder.append(panel2, 3);
        builder.nextLine();
        
        
        builder.append(storePasswordCheckBox, 5);
        builder.nextLine();

       // builder.setLeadingColumnOffset(1);

       
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

        JLabel label = new JLabel(MailResourceLoader.getString("dialog",
                    "account", "using_default_account_settings"));
        Font newFont = label.getFont().deriveFont(Font.BOLD);
        label.setFont(newFont);
        mainLayout.setConstraints(label, mainConstraints);
        add(label);
    }

    protected void initComponents() {
        defaultAccountCheckBox = new CheckBoxWithMnemonic(MailResourceLoader.getString(
                    "dialog", "account", "use_default_account_settings"));

        //defaultAccountCheckBox.setEnabled(false);
        defaultAccountCheckBox.setActionCommand("DEFAULT_ACCOUNT");
        defaultAccountCheckBox.addActionListener(this);

        hostLabel = new LabelWithMnemonic(MailResourceLoader.getString(
                    "dialog", "account", "host")); //$NON-NLS-1$

        hostTextField = new JTextField();
        hostLabel.setLabelFor(hostTextField);
        portLabel = new LabelWithMnemonic(MailResourceLoader.getString(
                    "dialog", "account", "port")); //$NON-NLS-1$

        portSpinner = new JSpinner(new SpinnerNumberModel(100, 1, 99999, 1));
        portLabel.setLabelFor(portSpinner);

        needAuthCheckBox = new CheckBoxWithMnemonic(MailResourceLoader.getString(
                    "dialog", "account", "server_needs_authentification")); //$NON-NLS-1$

        needAuthCheckBox.setActionCommand("AUTH"); //$NON-NLS-1$
        needAuthCheckBox.addActionListener(this);

        storePasswordCheckBox = new CheckBoxWithMnemonic(MailResourceLoader.getString(
                    "dialog", "account", "store_password_in_configuration_file"));

        secureCheckBox = new CheckBoxWithMnemonic(MailResourceLoader.getString(
                    "dialog", "account", "use_SSL_for_secure_connection"));

        authenticationLabel = new LabelWithMnemonic(MailResourceLoader.getString(
                    "dialog", "account", "authentication_type"));

        authenticationComboBox = new JComboBox();
        authenticationLabel.setLabelFor(authenticationComboBox);

        updateAuthenticationComboBox();

        checkAuthMethods = new ButtonWithMnemonic(MailResourceLoader.getString(
                    "dialog", "account", "authentication_checkout_methods"));
        checkAuthMethods.setActionCommand("CHECK_AUTHMETHODS");
        checkAuthMethods.addActionListener(this);

        //authenticationComboBox.addActionListener(this);
        authenticationLabel.setLabelFor(authenticationComboBox);

        loginLabel = new LabelWithMnemonic(MailResourceLoader.getString(
                    "dialog", "account", "login"));

        loginTextField = new JTextField();
        loginLabel.setLabelFor(loginTextField);
    }

    /**
     *
     */
    private void updateAuthenticationComboBox() {
        authenticationComboBox.removeAllItems();

        authenticationComboBox.addItem(MailResourceLoader.getString("dialog",
                "account", "authentication_securest"));

        if (accountItem.isPopAccount()) {
            authenticationComboBox.addItem("POP before SMTP");
        }

        String authMethods = accountItem.get("smtpserver",
                "authentication_methods");

        // Add previously fetch authentication modes
        if (authMethods != null) {
            Matcher matcher = AUTH_MODE_TOKENIZE_PATTERN.matcher(authMethods);

            while (matcher.find()) {
                authenticationComboBox.addItem(matcher.group(1));
            }
        }

        authenticationComboBox.setSelectedItem(accountItem.get("smtpserver",
                "login_method"));
    }

    public void actionPerformed(ActionEvent e) {
        String action = e.getActionCommand();

        if (e.getSource().equals(authenticationComboBox)) {
            String selection = (String) authenticationComboBox.getSelectedItem();

            loginLabel.setEnabled(true);
            loginTextField.setEnabled(true);
            storePasswordCheckBox.setEnabled(true);
        } else if (action.equals("DEFAULT_ACCOUNT")) {
            removeAll();

            if (defaultAccountCheckBox.isSelected()) {
                showDefaultAccountWarning();
            } else {
                layoutComponents();
            }

            revalidate();
        } else if (action.equals("AUTH")) {
            if (needAuthCheckBox.isSelected()) {
                loginLabel.setEnabled(true);
                loginTextField.setEnabled(true);
                storePasswordCheckBox.setEnabled(true);
                authenticationLabel.setEnabled(true);
                authenticationComboBox.setEnabled(true);
                checkAuthMethods.setEnabled(true);
            } else {
                loginLabel.setEnabled(false);
                loginTextField.setEnabled(false);
                storePasswordCheckBox.setEnabled(false);
                authenticationLabel.setEnabled(false);
                authenticationComboBox.setEnabled(false);
                checkAuthMethods.setEnabled(false);
            }
        } else if (action.equals("CHECK_AUTHMETHODS")) {
            getAuthMechanisms();
        }
    }

    private void getAuthMechanisms() {
        {
            List list = new LinkedList();

            try {
                list = getAuthSMTP();
                LOG.info("Server supported AUTH types: " + list.toString());

                // If the server doesn't support an AUTH -> POP before SMTP is only choice
                ListTools.intersect_astable(list,
                    AuthenticationFactory.getInstance().getSupportedMechanisms());
            }  catch (SMTPException e1) {
                LOG.severe("Server does not support the CAPA command");

                // Let the user choose
                list = AuthenticationFactory.getInstance()
                                            .getSupportedMechanisms();
            } catch (Exception e) {
                // let exception handler process other errors
                new ExceptionHandler().processException(e);
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

                accountItem.set("smtpserver", "authentication_methods",
                    authMethods.toString());
            } else {
                accountItem.set("smtpserver", "authentication_methods", "");
            }

            updateAuthenticationComboBox();
        }
    }

    /**
      * @return
      */
    private List getAuthSMTP() throws IOException, SMTPException {
        List result = new LinkedList();
        SMTPProtocol protocol = new SMTPProtocol(hostTextField.getText(),
        		 ((Integer) portSpinner.getValue()).intValue());

        protocol.openPort();

        String[] capas = protocol.ehlo(InetAddress.getLocalHost());

        LOG.info("Server CAPAs: " + Arrays.asList(capas).toString());

        for (int i = 0; i < capas.length; i++) {
            if (capas[i].startsWith("AUTH")) {
                result = parseAuthCapas(capas[i]);
            }
        }

        return result;
    }

    /**
     * @param string
     * @return
     */
    private List parseAuthCapas(String string) {
        Matcher tokenizer = Pattern.compile("\\b[^\\s]+\\b").matcher(string);
        tokenizer.find();

        List mechanisms = new LinkedList();

        while (tokenizer.find()) {
            mechanisms.add(tokenizer.group());
        }

        return mechanisms;
    }

    public boolean isFinished() {
        boolean result = false;
        String host = getHost();
        boolean esmtp = isESmtp();

        if (host.length() == 0) {
            JOptionPane.showMessageDialog(null,
                MailResourceLoader.getString("dialog", "account",
                    "You_have_to_enter_a_host_name")); //$NON-NLS-1$

            return false;
        } else if (esmtp == true) {
            String login = getLogin();

            if (login.length() == 0) {
                JOptionPane.showMessageDialog(null,
                    MailResourceLoader.getString("dialog", "account",
                        "You_have_to_enter_a_login_name")); //$NON-NLS-1$

                return false;
            }
        }

        return true;
    }
}