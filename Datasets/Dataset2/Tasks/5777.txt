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

class OutgoingServerStep extends AbstractStep {
        protected DataModel data;
        protected boolean isLastStep;
	private JTextField hostTextField;

	public OutgoingServerStep(DataModel data, boolean isLastStep) {
		super(MailResourceLoader.getString(
                                    "dialog",
                                    "accountwizard",
                                    "outgoingserver"),
                      MailResourceLoader.getString(
                                    "dialog",
                                    "accountwizard",
                                    "outgoingserver_description"));
                this.data = data;
                this.isLastStep = isLastStep;
                setCanGoNext(false);
	}
        
        protected JComponent createComponent() {
		JComponent component = new JPanel();
                component.setLayout(new BoxLayout(component, BoxLayout.Y_AXIS));
                component.add(new MultiLineLabel(MailResourceLoader.getString(
                                    "dialog",
                                    "accountwizard",
                                    "outgoingserver_text")));
                component.add(Box.createVerticalStrut(40));
                WizardTextField middlePanel = new WizardTextField();
                JLabel addressLabel = new JLabel(MailResourceLoader.getString(
                                    "dialog",
                                    "accountwizard",
                                    "host"));
                addressLabel.setDisplayedMnemonic(MailResourceLoader.getMnemonic(
                                    "dialog",
                                    "accountwizard",
                                    "host"));
                middlePanel.addLabel(addressLabel);
                hostTextField = new JTextField();
                Method method = null;
                try {
                        method = hostTextField.getClass().getMethod("getText", null);
                } catch (NoSuchMethodException nsme) {}
                data.registerDataLookup("OutgoingServer.host", new DefaultDataLookup(hostTextField, method, null));
                hostTextField.getDocument().addDocumentListener(new DocumentListener() {
                        public void removeUpdate(DocumentEvent e) {
                                setCanProceed(e.getDocument().getLength() > 0);
                        }
                        
                        public void insertUpdate(DocumentEvent e) {
                                setCanProceed(e.getDocument().getLength() > 0);
                        }
                        
                        protected void setCanProceed(boolean b) {
                                if (isLastStep) {
                                        setCanFinish(b);
                                } else {
                                        setCanGoNext(b);
                                }
                        }
                        
                        public void changedUpdate(DocumentEvent e) {}
                });
                addressLabel.setLabelFor(hostTextField);
                middlePanel.addTextField(hostTextField);
                JLabel addressExampleLabel = new JLabel(MailResourceLoader.getString(
                                    "dialog",
                                    "accountwizard",
                                    "example") + "mail.microsoft.com");
                middlePanel.addExample(addressExampleLabel);
                component.add(middlePanel);
                return component;
	}

        public void prepareRendering() {}
}