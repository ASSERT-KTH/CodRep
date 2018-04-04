import org.columba.core.gui.util.WizardTextField;

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

package org.columba.mail.gui.config.accountwizard;

import java.lang.reflect.Method;

import javax.swing.Box;
import javax.swing.BoxLayout;
import javax.swing.JComboBox;
import javax.swing.JComponent;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JTextField;
import javax.swing.event.DocumentEvent;
import javax.swing.event.DocumentListener;

import net.javaprog.ui.wizard.AbstractStep;
import net.javaprog.ui.wizard.DataModel;
import net.javaprog.ui.wizard.DefaultDataLookup;

import org.columba.core.gui.util.MultiLineLabel;
import org.columba.core.gui.util.wizard.WizardTextField;
import org.columba.mail.util.MailResourceLoader;

class IncomingServerStep extends AbstractStep {
        protected DataModel data;
	protected JTextField loginTextField;
	protected JTextField hostTextField;
	protected JLabel addressLabel;
	protected JComboBox typeComboBox;

	public IncomingServerStep(DataModel data) {
		super(MailResourceLoader.getString(
                                    "dialog",
                                    "accountwizard",
                                    "incomingserver"),
                      MailResourceLoader.getString(
                                    "dialog",
                                    "accountwizard",
                                    "incomingserver_description"));
                this.data = data;
                setCanGoNext(false);
        }
		
        protected JComponent createComponent() {
		JComponent component = new JPanel();
                component.setLayout(new BoxLayout(component, BoxLayout.Y_AXIS));
                component.add(new MultiLineLabel(MailResourceLoader.getString(
                                    "dialog",
                                    "accountwizard",
                                    "incomingserver_text")));
                component.add(Box.createVerticalStrut(40));
                WizardTextField middlePanel = new WizardTextField();
                JLabel nameLabel = new JLabel(MailResourceLoader.getString(
                                    "dialog",
                                    "accountwizard",
                                    "login")); //$NON-NLS-1$
                nameLabel.setDisplayedMnemonic(MailResourceLoader.getMnemonic(
                                    "dialog",
                                    "accountwizard",
                                    "login")); //$NON-NLS-1$
                middlePanel.addLabel(nameLabel);
                loginTextField = new JTextField();
                Method method = null;
                try {
                        method = loginTextField.getClass().getMethod("getText", null);
                } catch (NoSuchMethodException nsme) {}
                data.registerDataLookup("IncomingServer.login", new DefaultDataLookup(loginTextField, method, null));
                DocumentListener fieldListener = new DocumentListener() {
                        public void removeUpdate(DocumentEvent e) {
                                checkFields();
                        }
                        
                        public void insertUpdate(DocumentEvent e) {
                                checkFields();
                        }
                        
                        protected void checkFields() {
                                setCanGoNext(loginTextField.getDocument().getLength() > 0
                                           && hostTextField.getDocument().getLength() > 0);
                        }
                        
                        public void changedUpdate(DocumentEvent e) {}
                };
                loginTextField.getDocument().addDocumentListener(fieldListener);
                nameLabel.setLabelFor(loginTextField);
                middlePanel.addTextField(loginTextField);
                JLabel exampleLabel = new JLabel(MailResourceLoader.getString(
                                    "dialog",
                                    "accountwizard",
                                    "example") + "billgates");
                middlePanel.addExample(exampleLabel);
                addressLabel = new JLabel(MailResourceLoader.getString(
                                    "dialog",
                                    "accountwizard",
                                    "host")); //$NON-NLS-1$
                addressLabel.setDisplayedMnemonic(MailResourceLoader.getMnemonic(
                                    "dialog",
                                    "accountwizard",
                                    "host")); //$NON-NLS-1$)
                middlePanel.addLabel(addressLabel);
                hostTextField = new JTextField();
                data.registerDataLookup("IncomingServer.host", new DefaultDataLookup(hostTextField, method, null));
                hostTextField.getDocument().addDocumentListener(fieldListener);
                addressLabel.setLabelFor(hostTextField);
                middlePanel.addTextField(hostTextField);
                JLabel addressExampleLabel = new JLabel(MailResourceLoader.getString(
                                    "dialog",
                                    "accountwizard",
                                    "example") + "mail.microsoft.com");
                middlePanel.addExample(addressExampleLabel);

                JLabel typeLabel = new JLabel(MailResourceLoader.getString(
                                    "dialog",
                                    "accountwizard",
                                    "type")); //$NON-NLS-1$
                typeLabel.setDisplayedMnemonic(MailResourceLoader.getMnemonic(
                                    "dialog",
                                    "accountwizard",
                                    "type"));
                middlePanel.addLabel(typeLabel);
                typeComboBox = new JComboBox();
                typeLabel.setLabelFor(typeComboBox);
                typeComboBox.addItem("POP3");
                typeComboBox.addItem("IMAP");
                try {
                        method = typeComboBox.getClass().getMethod("getSelectedItem", null);
                } catch (NoSuchMethodException nsme) {}
                data.registerDataLookup("IncomingServer.type", new DefaultDataLookup(typeComboBox, method, null));
                middlePanel.addTextField(typeComboBox);
                middlePanel.addEmptyExample();
                component.add(middlePanel);
                return component;
        }
        
        public void prepareRendering() {}
}