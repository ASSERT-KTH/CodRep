.getMiscIcon("signature-nokey.png"));

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
package org.columba.mail.gui.util;

import java.awt.BorderLayout;
import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.GridLayout;
import java.awt.Insets;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.KeyEvent;
import java.text.MessageFormat;

import javax.swing.BorderFactory;
import javax.swing.JButton;
import javax.swing.JCheckBox;
import javax.swing.JComponent;
import javax.swing.JDialog;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JPasswordField;
import javax.swing.KeyStroke;

import org.columba.core.gui.base.ButtonWithMnemonic;
import org.columba.core.gui.frame.FrameManager;
import org.columba.core.resourceloader.ImageLoader;
import org.columba.mail.util.MailResourceLoader;

public class PGPPassphraseDialog implements ActionListener {
	private char[] password;

	// private JFrame frame;
	private JDialog dialog;

	private boolean bool = false;

	private JPasswordField passwordField;

	// private JTextField loginTextField;
	private JCheckBox checkbox;

	private boolean save;

	private JButton okButton;

	private JButton cancelButton;

	private JButton helpButton;

	// private JComboBox loginMethodComboBox;
	// String loginMethod;
	public PGPPassphraseDialog() {
	}

	protected JPanel createButtonPanel() {
		JPanel bottom = new JPanel();
		bottom.setLayout(new BorderLayout());

		// bottom.setLayout( new BoxLayout( bottom, BoxLayout.X_AXIS ) );
		bottom.setBorder(BorderFactory.createEmptyBorder(17, 12, 11, 11));

		// bottom.add( Box.createHorizontalStrut());
		cancelButton = new ButtonWithMnemonic(MailResourceLoader.getString(
				"global", "cancel"));

		//$NON-NLS-1$ //$NON-NLS-2$
		cancelButton.addActionListener(this);
		cancelButton.setActionCommand("CANCEL"); //$NON-NLS-1$

		okButton = new ButtonWithMnemonic(MailResourceLoader.getString(
				"global", "ok"));

		//$NON-NLS-1$ //$NON-NLS-2$
		okButton.addActionListener(this);
		okButton.setActionCommand("OK"); //$NON-NLS-1$
		okButton.setDefaultCapable(true);
		dialog.getRootPane().setDefaultButton(okButton);

		helpButton = new ButtonWithMnemonic(MailResourceLoader.getString(
				"global", "help"));

		//$NON-NLS-1$ //$NON-NLS-2$
		JPanel buttonPanel = new JPanel();
		buttonPanel.setLayout(new GridLayout(1, 3, 5, 0));
		buttonPanel.add(okButton);
		buttonPanel.add(cancelButton);
		buttonPanel.add(helpButton);

		// bottom.add( Box.createHorizontalGlue() );
		bottom.add(buttonPanel, BorderLayout.EAST);

		return bottom;
	}

	public void showDialog(String userID, String password, boolean save) {

		// JButton[] buttons = new JButton[2];
		JLabel hostLabel = new JLabel(MessageFormat.format(MailResourceLoader
				.getString("dialog", "password", "enter_passphrase"),
				new Object[] { userID }));

		passwordField = new JPasswordField(password, 40);

		checkbox = new JCheckBox(MailResourceLoader.getString("dialog",
				"password", "save_passphrase"));
		checkbox.setSelected(save);

		dialog = new JDialog(FrameManager.getInstance().getActiveFrame(), true);
		dialog.setTitle(MailResourceLoader.getString("dialog", "password",
				"dialog_title_passphrase"));

		JPanel centerPanel = new JPanel();
		centerPanel.setBorder(BorderFactory.createEmptyBorder(5, 5, 5, 5));

		dialog.getContentPane().add(centerPanel, BorderLayout.CENTER);

		GridBagLayout mainLayout = new GridBagLayout();
		centerPanel.setLayout(mainLayout);

		GridBagConstraints mainConstraints = new GridBagConstraints();

		JLabel iconLabel = new JLabel(ImageLoader
				.getImageIcon("pgp-signature-nokey.png"));
		mainConstraints.anchor = GridBagConstraints.NORTHWEST;
		mainConstraints.weightx = 1.0;
		mainConstraints.gridwidth = GridBagConstraints.RELATIVE;
		mainConstraints.fill = GridBagConstraints.HORIZONTAL;
		mainLayout.setConstraints(iconLabel, mainConstraints);
		centerPanel.add(iconLabel);

		mainConstraints.gridwidth = GridBagConstraints.REMAINDER;
		mainConstraints.anchor = GridBagConstraints.WEST;
		mainConstraints.insets = new Insets(0, 5, 0, 0);
		mainLayout.setConstraints(hostLabel, mainConstraints);
		centerPanel.add(hostLabel);

		mainConstraints.insets = new Insets(5, 5, 0, 0);
		mainLayout.setConstraints(passwordField, mainConstraints);
		centerPanel.add(passwordField);

		mainConstraints.insets = new Insets(5, 5, 0, 0);
		mainLayout.setConstraints(checkbox, mainConstraints);
		centerPanel.add(checkbox);

		JPanel bottomPanel = new JPanel();
		bottomPanel.setLayout(new BorderLayout());

		JPanel buttonPanel = createButtonPanel();
		bottomPanel.add(buttonPanel, BorderLayout.CENTER);

		dialog.getContentPane().add(bottomPanel, BorderLayout.SOUTH);
		dialog.getRootPane().setDefaultButton(okButton);
		dialog.getRootPane().registerKeyboardAction(this, "CANCEL",
				KeyStroke.getKeyStroke(KeyEvent.VK_ESCAPE, 0),
				JComponent.WHEN_IN_FOCUSED_WINDOW);
		dialog.pack();
		dialog.setLocationRelativeTo(null);
		dialog.setVisible(true);
		dialog.requestFocus();
		passwordField.requestFocus();
	}

	public char[] getPassword() {
		return password;
	}

	public boolean success() {
		return bool;
	}

	public boolean getSave() {
		return save;
	}

	public void actionPerformed(ActionEvent e) {
		String action = e.getActionCommand();

		if (action.equals("OK")) {
			password = passwordField.getPassword();

			// user = loginTextField.getText();
			save = checkbox.isSelected();

			// loginMethod = (String) loginMethodComboBox.getSelectedItem();
			bool = true;
			dialog.dispose();
		} else if (action.equals("CANCEL")) {
			bool = false;
			dialog.dispose();
		}
	}
}