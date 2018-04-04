hostTextField.requestFocus();

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

import java.awt.event.ActionListener;

import javax.swing.BorderFactory;
import javax.swing.Box;
import javax.swing.BoxLayout;
import javax.swing.ImageIcon;
import javax.swing.JComponent;
import javax.swing.JDialog;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JTextField;

import org.columba.core.gui.util.MultiLineLabel;
import org.columba.core.gui.util.wizard.DefaultWizardPanel;
import org.columba.core.gui.util.wizard.WizardTextField;
import org.columba.mail.util.MailResourceLoader;

public class OutgoingServerPanel extends DefaultWizardPanel {
	private JLabel hostLabel;
	private JTextField hostTextField;

	public OutgoingServerPanel(
		JDialog dialog,
		ActionListener listener,
		String title,
		String description,
		ImageIcon icon) {
		super(dialog, listener, title, description, icon);
	}

	public OutgoingServerPanel(
		JDialog dialog,
		ActionListener listener,
		String title,
		String description,
		ImageIcon icon,
		boolean b) {
		super(dialog, listener, title, description, icon);
		
		JPanel panel = this;
			panel.setLayout(new BoxLayout(panel, BoxLayout.Y_AXIS));
			panel.setBorder(BorderFactory.createEmptyBorder(30, 30, 20, 30));

			MultiLineLabel label = new MultiLineLabel(MailResourceLoader.getString("dialog", "accountwizard", "please_specify_your_outgoing_mail_server_properties")); //$NON-NLS-1$

			panel.add(label);

			panel.add(Box.createRigidArea(new java.awt.Dimension(0, 40)));

			WizardTextField middlePanel = new WizardTextField();

			JLabel addressLabel = new JLabel(MailResourceLoader.getString("dialog", "accountwizard", "host_smtp_server")); //$NON-NLS-1$
			addressLabel.setDisplayedMnemonic(
				MailResourceLoader.getMnemonic(
					"dialog",
					"accountwizard",
					"host_smtp_server"));
			middlePanel.addLabel(addressLabel);
			hostTextField = new JTextField("");
			hostTextField.requestFocusInWindow();
			addressLabel.setLabelFor(hostTextField);
			//register(hostTextField);
			middlePanel.addTextField(hostTextField);
			JLabel addressExampleLabel = new JLabel(MailResourceLoader.getString("dialog", "accountwizard", "example__mail.microsoft.com")); //$NON-NLS-1$
			middlePanel.addExample(addressExampleLabel);

			panel.add(middlePanel);
	}

	public String getHost() {
		return hostTextField.getText();
	}

	public JTextField getIncomingHostTextField() {
		/*
		IncomingServerPanel p = (IncomingServerPanel) prevPanel;
		
		JTextField host = p.getIncomingHostTextField();
		
		return host;
		*/

		return null;
	}

	public void select() {
		hostTextField.setCaretPosition(hostTextField.getText().length());
		hostTextField.selectAll();
	}

	/*
	public void setPrev(DefaultWizardPanel panel)
	{
		
		prevPanel = panel;
	
		getIncomingHostTextField()
			.getDocument()
			.addDocumentListener(new DocumentListener()
		{
			public void insertUpdate(DocumentEvent e)
			{
				update();
			}
	
			public void removeUpdate(DocumentEvent e)
			{
				update();
			}
	
			public void changedUpdate(DocumentEvent e)
			{
				update();
				//Plain text components don't fire these events
			}
			public void update()
			{
	
				hostTextField.setText(getIncomingHostTextField().getText());
			}
		});
		
	}

	*/
	
	/*
	protected JPanel createPanel(ActionListener listener) {
		JPanel panel = new JPanel();
		panel.setLayout(new BoxLayout(panel, BoxLayout.Y_AXIS));
		panel.setBorder(BorderFactory.createEmptyBorder(30, 30, 20, 30));

		MultiLineLabel label = new MultiLineLabel(MailResourceLoader.getString("dialog", "accountwizard", "please_specify_your_outgoing_mail_server_properties")); //$NON-NLS-1$

		panel.add(label);

		panel.add(Box.createRigidArea(new java.awt.Dimension(0, 40)));

		WizardTextField middlePanel = new WizardTextField();

		JLabel addressLabel = new JLabel(MailResourceLoader.getString("dialog", "accountwizard", "host_smtp_server")); //$NON-NLS-1$
		addressLabel.setDisplayedMnemonic(
			MailResourceLoader.getMnemonic(
				"dialog",
				"accountwizard",
				"host_smtp_server"));
		middlePanel.addLabel(addressLabel);
		hostTextField = new JTextField("");
		addressLabel.setLabelFor(hostTextField);
		//register(hostTextField);
		middlePanel.addTextField(hostTextField);
		JLabel addressExampleLabel = new JLabel(MailResourceLoader.getString("dialog", "accountwizard", "example__mail.microsoft.com")); //$NON-NLS-1$
		middlePanel.addExample(addressExampleLabel);

		panel.add(middlePanel);

		return panel;
	}
	*/

	/**
	 * @see org.columba.core.gui.util.wizard.DefaultWizardPanel#getFocusComponent()
	 */
	public JComponent getFocusComponent() {
		return hostTextField;
	}

}