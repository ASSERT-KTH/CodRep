folder.updateConfiguration();

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

import java.awt.BorderLayout;
import java.awt.GridLayout;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.KeyEvent;

import javax.swing.BorderFactory;
import javax.swing.JButton;
import javax.swing.JComponent;
import javax.swing.JDialog;
import javax.swing.JList;
import javax.swing.JPanel;
import javax.swing.JTabbedPane;
import javax.swing.KeyStroke;
import javax.swing.event.ListSelectionEvent;
import javax.swing.event.ListSelectionListener;

import org.columba.core.gui.util.DialogStore;
import org.columba.core.help.HelpManager;
import org.columba.core.main.MainInterface;
import org.columba.mail.config.AccountItem;
import org.columba.mail.config.IdentityItem;
import org.columba.mail.config.SmtpItem;
import org.columba.mail.folder.imap.IMAPRootFolder;
import org.columba.mail.pop3.POP3ServerController;
import org.columba.mail.util.MailResourceLoader;

public class AccountDialog implements ActionListener, ListSelectionListener {
	private JDialog dialog;

	private AccountItem accountItem;

	private IdentityPanel identityPanel;
	private IncomingServerPanel incomingServerPanel;
	private OutgoingServerPanel outgoingServerPanel;
	private SecurityPanel securityPanel;

	//private SpecialFoldersPanel specialFoldersPanel;

	private ReceiveOptionsPanel receiveOptionsPanel;

	//private PanelChooser panelChooser;

	private JPanel selected = null;

	public AccountDialog(AccountItem item) {
		dialog = DialogStore.getDialog();
		dialog.setTitle(
			MailResourceLoader.getString(
				"dialog",
				"account",
				"preferences_for")
				+ " "
				+ item.getName());
		this.accountItem = item;
		createPanels();
		initComponents();

		//panelChooser.addListSelectionListener(this);

		dialog.pack();
		dialog.setLocationRelativeTo(null);
		dialog.setVisible(true);
	}

	protected void createPanels() {

		IdentityItem identityItem = accountItem.getIdentityItem();
		identityPanel = new IdentityPanel(accountItem, identityItem);

		receiveOptionsPanel = new ReceiveOptionsPanel(dialog, accountItem);

		incomingServerPanel =
			new IncomingServerPanel(dialog, accountItem, receiveOptionsPanel);

		outgoingServerPanel = new OutgoingServerPanel(accountItem);

		/*
		specialFoldersPanel = new SpecialFoldersPanel(accountItem,
				accountItem.getSpecialFoldersItem());
		*/

		securityPanel = new SecurityPanel(accountItem.getPGPItem());
	}

	protected void initComponents() {
		dialog.getContentPane().setLayout(new BorderLayout());

		JPanel mainPanel = new JPanel();
		mainPanel.setLayout(new BorderLayout());
		mainPanel.setBorder(BorderFactory.createEmptyBorder(0, 0, 10, 0));

		JTabbedPane tp = new JTabbedPane();
		tp.setTabLayoutPolicy(JTabbedPane.SCROLL_TAB_LAYOUT);
		tp.setBorder(BorderFactory.createEmptyBorder(0, 5, 0, 5));

		/*
		IdentityItem identityItem = accountItem.getIdentityItem();
		identityPanel = new IdentityPanel( accountItem, identityItem);
		*/

		tp.add(
			MailResourceLoader.getString("dialog", "account", "identity"),
			identityPanel);
		//$NON-NLS-1$

		String incomingServerPanelTitle =
			MailResourceLoader.getString("dialog", "account", "incomingserver");
		if (accountItem.isPopAccount()) {
			incomingServerPanelTitle += " (POP3)";
		} else {
			incomingServerPanelTitle += " (IMAP4)";
		}
		tp.add(incomingServerPanelTitle, incomingServerPanel);

		tp.add(
			MailResourceLoader.getString("dialog", "account", "receiveoptions"),
			receiveOptionsPanel);

		SmtpItem smtpItem = accountItem.getSmtpItem();
		/*
		outgoingServerPanel = new OutgoingServerPanel( smtpItem);
		*/
		tp.add(
			MailResourceLoader.getString("dialog", "account", "outgoingserver"),
			outgoingServerPanel);
		//$NON-NLS-1$

		/*
		specialFoldersPanel =
			new SpecialFoldersPanel(
				accountItem,
				accountItem.getSpecialFoldersItem());
		*/
		/*
		tp.add(MailResourceLoader.getString(
		                                "dialog",
		                                "account",
		                                "specialfolders"),
			specialFoldersPanel);
		*/
		//$NON-NLS-1$

		/*
		securityPanel = new SecurityPanel( accountItem.getPGPItem());
		*/
		tp.add(
			MailResourceLoader.getString("dialog", "account", "security"),
			securityPanel);
		//$NON-NLS-1$

		mainPanel.add(tp, BorderLayout.CENTER);

		dialog.getContentPane().add(mainPanel, BorderLayout.CENTER);
		dialog.getContentPane().add(createButtonPanel(), BorderLayout.SOUTH);
		dialog.getRootPane().registerKeyboardAction(
			this,
			"CANCEL",
			KeyStroke.getKeyStroke(KeyEvent.VK_ESCAPE, 0),
			JComponent.WHEN_IN_FOCUSED_WINDOW);
		dialog.getRootPane().registerKeyboardAction(
			this,
			"HELP",
			KeyStroke.getKeyStroke(KeyEvent.VK_F1, 0),
			JComponent.WHEN_IN_FOCUSED_WINDOW);
	}

	/*
	protected void initComponents()
	{
		dialog.getContentPane().setLayout(new BorderLayout());
		
		
		
		dialog.getContentPane().add( identityPanel, BorderLayout.CENTER );
		selected = identityPanel;
		
		panelChooser = new PanelChooser();
		dialog.getContentPane().add( panelChooser, BorderLayout.WEST );
		
		JPanel bottomPanel = new JPanel();
		bottomPanel.setBorder( new WizardTopBorder() );
		bottomPanel.setLayout( new BorderLayout() );
		
		JPanel buttonPanel = createButtonPanel();
		bottomPanel.add( buttonPanel, BorderLayout.CENTER );
		
		dialog.getContentPane().add( bottomPanel, BorderLayout.SOUTH );
		
	}
	*/

	protected JPanel createButtonPanel() {
		JPanel bottom = new JPanel();
		bottom.setLayout(new BorderLayout());
		//bottom.setLayout( new BoxLayout( bottom, BoxLayout.X_AXIS ) );
		bottom.setBorder(BorderFactory.createEmptyBorder(17, 12, 11, 11));

		//bottom.add( Box.createHorizontalStrut());

		JButton cancelButton =
			new JButton(MailResourceLoader.getString("global", "cancel"));
		//$NON-NLS-1$ //$NON-NLS-2$
		cancelButton.addActionListener(this);
		cancelButton.setActionCommand("CANCEL"); //$NON-NLS-1$

		JButton okButton =
			new JButton(MailResourceLoader.getString("global", "ok"));
		//$NON-NLS-1$ //$NON-NLS-2$
		okButton.addActionListener(this);
		okButton.setActionCommand("OK"); //$NON-NLS-1$
		okButton.setDefaultCapable(true);
		dialog.getRootPane().setDefaultButton(okButton);

		JButton helpButton =
			new JButton(MailResourceLoader.getString("global", "help"));
		// associate with JavaHelp
		HelpManager.enableHelpOnButton(helpButton, "configuring_columba");

		JPanel buttonPanel = new JPanel();
		buttonPanel.setLayout(new GridLayout(1, 3, 5, 0));
		buttonPanel.add(okButton);
		buttonPanel.add(cancelButton);
		buttonPanel.add(helpButton);

		//bottom.add( Box.createHorizontalGlue() );

		bottom.add(buttonPanel, BorderLayout.EAST);

		return bottom;
	}

	public void actionPerformed(ActionEvent e) {
		String action = e.getActionCommand();

		if (action.equals("OK")) //$NON-NLS-1$
			{

			identityPanel.updateComponents(false);
			incomingServerPanel.updateComponents(false);
			receiveOptionsPanel.updateComponents(false);
			outgoingServerPanel.updateComponents(false);
			securityPanel.updateComponents(false);
			/*
			specialFoldersPanel.updateComponents(false);
			*/

			if (accountItem.isPopAccount()) {

				int uid = accountItem.getUid();
				POP3ServerController c =
					MainInterface.popServerCollection.uidGet(uid);
				c.restartTimer();

				//MainInterface.popServerCollection.enableMailCheckIcon();
			} else {
				// update tree label
				int uid = accountItem.getUid();

				IMAPRootFolder folder =
					(IMAPRootFolder) MainInterface.treeModel.getImapFolder(uid);
				folder.restartTimer();

				//folder.setName(accountItem.getName());

				//folder.restartTimer();

			}

			dialog.setVisible(false);
		} else if (action.equals("CANCEL")) //$NON-NLS-1$
			{
			dialog.setVisible(false);
		} else if (action.equals("HELP")) {
			/*
			URLController c = new URLController();
			try {
				c.open(
					new URL("http://columba.sourceforge.net/phpwiki/index.php/Configure%20Columba"));
			} catch (MalformedURLException mue) {
			}
			*/

		}

	}

	protected void setSelection(JPanel panel) {
		dialog.getContentPane().remove(selected);
		dialog.getContentPane().add(panel, BorderLayout.CENTER);
		dialog.validate();
		dialog.repaint();
		selected = panel;
	}

	public void valueChanged(ListSelectionEvent e) {
		JList lsm = (JList) e.getSource();
		switch (lsm.getSelectedIndex()) {
			case 0 :
				setSelection(identityPanel);
				break;
			case 1 :
				setSelection(incomingServerPanel);
				break;
			case 2 :
				setSelection(outgoingServerPanel);
				break;
			case 3 :
				setSelection(securityPanel);
				break;
				/*
				case 4 :
					setSelection(securityPanel);
					break;
				*/
		}
	}
}