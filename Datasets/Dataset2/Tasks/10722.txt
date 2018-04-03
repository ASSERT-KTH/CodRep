import org.columba.core.main.MainInterface;

// This program is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation; either version 2 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Library General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program; if not, write to the Free Software
// Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

package org.columba.mail.gui.config.account;

import java.awt.Component;
import java.awt.Font;
import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.Insets;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

import javax.swing.BorderFactory;
import javax.swing.Box;
import javax.swing.JButton;
import javax.swing.JCheckBox;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.border.Border;

import org.columba.mail.config.AccountItem;
import org.columba.mail.config.MailConfig;
import org.columba.mail.config.SpecialFoldersItem;
import org.columba.mail.folder.Folder;
import org.columba.mail.gui.tree.util.SelectFolderDialog;
import org.columba.mail.gui.tree.util.TreeNodeList;
import org.columba.mail.util.MailResourceLoader;
import org.columba.main.MainInterface;

public class SpecialFoldersPanel
	extends DefaultPanel
	implements ActionListener {

	private JLabel trashLabel;
	private JButton trashButton;

	private JLabel draftsLabel;
	private JButton draftsButton;

	private JLabel templatesLabel;
	private JButton templatesButton;

	private JLabel sentLabel;
	private JButton sentButton;

	private JLabel inboxLabel;
	private JButton inboxButton;

	private JCheckBox defaultAccountCheckBox;

	private SpecialFoldersItem item;
	private AccountItem accountItem;

	public SpecialFoldersPanel(
		AccountItem accountItem,
		SpecialFoldersItem item) {
		super();

		this.item = item;
		this.accountItem = accountItem;

		initComponents();

		updateComponents(true);

	}

	protected String getPath(String uid) {
		Integer u = new Integer(uid);

		Folder f = (Folder) MainInterface.treeModel.getFolder(u.intValue());

		if (f == null)
			return ""; //$NON-NLS-1$

		return f.getTreePath();
	}

	protected String getUid(String treePath) {
		TreeNodeList list = new TreeNodeList(treePath);
		Folder f = (Folder) MainInterface.treeModel.getFolder(list);

		if (f == null)
			return ""; //$NON-NLS-1$

		Integer i = new Integer(f.getUid());

		return i.toString();
	}

	protected boolean isPopAccount() {
		return accountItem.isPopAccount();
	}

	protected void updateComponents(boolean b) {
		if (b) {
			if (!isPopAccount())
				trashButton.setText(getPath(item.get("trash")));

			draftsButton.setText(getPath(item.get("drafts")));
			templatesButton.setText(getPath(item.get("templates")));
			sentButton.setText(getPath(item.get("sent")));

			if (isPopAccount())
				inboxButton.setText(getPath(item.get("inbox")));

			defaultAccountCheckBox.setSelected(
				item.getBoolean("use_default_account"));

			defaultAccountCheckBox.setEnabled(
				MailConfig.getAccountList().getDefaultAccountUid()
					== accountItem.getInteger("uid"));

			if (defaultAccountCheckBox.isEnabled()
				&& defaultAccountCheckBox.isSelected()) {
				showDefaultAccountWarning();
			} else {
				layoutComponents();
			}
		} else {
			if (!isPopAccount())
				item.set("trash", getUid(trashButton.getText()));

			item.set("drafts", getUid(draftsButton.getText()));
			item.set("templates", getUid(templatesButton.getText()));
			item.set("sent", getUid(sentButton.getText()));

			if (isPopAccount())
				item.set("inbox", getUid(inboxButton.getText()));

			item.set(
				"use_default_account",
				defaultAccountCheckBox.isSelected());

		}
	}

	protected void layoutComponents() {
		setBorder(BorderFactory.createEmptyBorder(5, 5, 5, 5));

		GridBagLayout mainLayout = new GridBagLayout();
		GridBagConstraints mainConstraints = new GridBagConstraints();

		mainConstraints.anchor = GridBagConstraints.NORTHWEST;
		mainConstraints.fill = GridBagConstraints.HORIZONTAL;
		mainConstraints.weightx = 1.0;

		setLayout(mainLayout);

		mainConstraints.gridwidth = GridBagConstraints.REMAINDER;
		mainConstraints.insets = new Insets(0, 10, 5, 0);
		mainLayout.setConstraints(defaultAccountCheckBox, mainConstraints);
		add(defaultAccountCheckBox);

		JPanel folderPanel = new JPanel();
		Border b1 = BorderFactory.createEtchedBorder();
		Border b2 =
			BorderFactory.createTitledBorder(
				b1,
				MailResourceLoader.getString(
					"dialog",
					"account",
					"account_information"));

		Border emptyBorder = BorderFactory.createEmptyBorder(5, 5, 5, 5);
		Border border = BorderFactory.createCompoundBorder(b2, emptyBorder);
		folderPanel.setBorder(border);

		GridBagLayout layout = new GridBagLayout();
		GridBagConstraints c = new GridBagConstraints();
		folderPanel.setLayout(layout);

		c.fill = GridBagConstraints.HORIZONTAL;
		c.anchor = GridBagConstraints.WEST;

		if (isPopAccount()) {

			c.weightx = 0.1;
			c.gridwidth = GridBagConstraints.RELATIVE;
			layout.setConstraints(inboxLabel, c);
			folderPanel.add(inboxLabel);

			c.gridwidth = GridBagConstraints.REMAINDER;
			c.weightx = 0.9;
			layout.setConstraints(inboxButton, c);
			folderPanel.add(inboxButton);

		}

		c.weightx = 0.1;
		c.gridwidth = GridBagConstraints.RELATIVE;
		layout.setConstraints(draftsLabel, c);
		folderPanel.add(draftsLabel);
		c.gridwidth = GridBagConstraints.REMAINDER;
		c.weightx = 0.9;
		layout.setConstraints(draftsButton, c);
		folderPanel.add(draftsButton);

		c.weightx = 0.1;
		c.gridwidth = GridBagConstraints.RELATIVE;
		layout.setConstraints(templatesLabel, c);
		folderPanel.add(templatesLabel);
		c.gridwidth = GridBagConstraints.REMAINDER;
		c.weightx = 0.9;
		layout.setConstraints(templatesButton, c);
		folderPanel.add(templatesButton);

		c.weightx = 0.1;
		c.gridwidth = GridBagConstraints.RELATIVE;
		layout.setConstraints(sentLabel, c);
		folderPanel.add(sentLabel);
		c.gridwidth = GridBagConstraints.REMAINDER;
		c.weightx = 0.9;
		layout.setConstraints(sentButton, c);
		folderPanel.add(sentButton);

		if (!isPopAccount()) {

			c.weightx = 0.1;
			c.gridwidth = GridBagConstraints.RELATIVE;
			layout.setConstraints(trashLabel, c);
			folderPanel.add(trashLabel);
			c.gridwidth = GridBagConstraints.REMAINDER;
			c.weightx = 0.9;
			layout.setConstraints(trashButton, c);
			folderPanel.add(trashButton);
		}

		mainConstraints.gridwidth = GridBagConstraints.REMAINDER;
		mainConstraints.insets = new Insets(0, 0, 0, 0);
		mainLayout.setConstraints(folderPanel, mainConstraints);
		add(folderPanel);

		mainConstraints.gridheight = GridBagConstraints.REMAINDER;
		mainConstraints.weighty = 1.0;
		mainConstraints.fill = GridBagConstraints.VERTICAL;
		Component vglue = Box.createVerticalGlue();
		mainLayout.setConstraints(vglue, mainConstraints);
		add(vglue);

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
		mainConstraints.fill = GridBagConstraints.BOTH;
		mainConstraints.insets = new Insets(0, 0, 0, 0);
		mainConstraints.gridwidth = GridBagConstraints.REMAINDER;
		mainConstraints.weightx = 1.0;
		mainConstraints.weighty = 1.0;
		*/

		JLabel label =
			new JLabel(
				MailResourceLoader.getString(
					"dialog",
					"account",
					"using_default_account_settings"));
		Font newFont = label.getFont().deriveFont(Font.BOLD);
		label.setFont(newFont);
		mainLayout.setConstraints(label, mainConstraints);
		add(label);

	}

	protected void initComponents() {

		defaultAccountCheckBox =
			new JCheckBox(
				MailResourceLoader.getString(
					"dialog",
					"account",
					"use_default_account_settings"));
		defaultAccountCheckBox.setMnemonic(
			MailResourceLoader.getMnemonic(
				"dialog",
				"account",
				"use_default_account_settings"));
		//defaultAccountCheckBox.setEnabled(false);
		defaultAccountCheckBox.setActionCommand("DEFAULT_ACCOUNT");
		defaultAccountCheckBox.addActionListener(this);

		if (isPopAccount()) {
			inboxLabel = new JLabel(MailResourceLoader.getString("dialog", "account", "inbox_folder")); //$NON-NLS-1$
			inboxLabel.setDisplayedMnemonic(MailResourceLoader.getMnemonic("dialog", "account", "inbox_folder")); //$NON-NLS-1$
			inboxButton = new JButton();
			inboxButton.setActionCommand("INBOX"); //$NON-NLS-1$
			inboxButton.addActionListener(this);
			inboxLabel.setLabelFor(inboxButton);
		}

		draftsLabel = new JLabel(MailResourceLoader.getString("dialog", "account", "drafts_folder")); //$NON-NLS-1$
		draftsLabel.setDisplayedMnemonic(MailResourceLoader.getMnemonic("dialog", "account", "drafts_folder")); //$NON-NLS-1$
		draftsButton = new JButton();
		draftsButton.setActionCommand("DRAFTS"); //$NON-NLS-1$
		draftsButton.addActionListener(this);
		draftsLabel.setLabelFor(draftsButton);

		templatesLabel = new JLabel(MailResourceLoader.getString("dialog", "account", "templates_folder")); //$NON-NLS-1$
		templatesLabel.setDisplayedMnemonic(MailResourceLoader.getMnemonic("dialog", "account", "templates_folder")); //$NON-NLS-1$
		templatesButton = new JButton();
		templatesButton.setActionCommand("TEMPLATES"); //$NON-NLS-1$
		templatesButton.addActionListener(this);
		templatesLabel.setLabelFor(templatesButton);

		sentLabel = new JLabel(MailResourceLoader.getString("dialog", "account", "sent_folder")); //$NON-NLS-1$		
		sentLabel.setDisplayedMnemonic(MailResourceLoader.getMnemonic("dialog", "account", "sent_folder")); //$NON-NLS-1$
		sentButton = new JButton();
		sentButton.setActionCommand("SENT"); //$NON-NLS-1$
		sentButton.addActionListener(this);
		sentLabel.setLabelFor(sentButton);

		if (!isPopAccount()) {
			trashLabel = new JLabel(MailResourceLoader.getString("dialog", "account", "trash_folder")); //$NON-NLS-1$			
			trashLabel.setDisplayedMnemonic(MailResourceLoader.getMnemonic("dialog", "account", "trash_folder")); //$NON-NLS-1$
			trashButton = new JButton();
			trashButton.setActionCommand("TRASH"); //$NON-NLS-1$
			trashButton.addActionListener(this);
			trashLabel.setLabelFor(trashButton);

		}

	}

	public void actionPerformed(ActionEvent e) {
		String action = e.getActionCommand();

		if (action.equals("TRASH")) //$NON-NLS-1$
			{
			SelectFolderDialog dialog =
				MainInterface.treeModel.getSelectFolderDialog();

			if (dialog.success()) {
				Folder selectedFolder = dialog.getSelectedFolder();
				String path = selectedFolder.getTreePath();

				trashButton.setText(path);

				//int uid = selectedFolder.getUid();
				//item.setTrash( new Integer(uid).toString() );
			}
		} else if (action.equals("INBOX")) //$NON-NLS-1$
			{
				SelectFolderDialog dialog =
								MainInterface.treeModel.getSelectFolderDialog();

			if (dialog.success()) {
				Folder selectedFolder = dialog.getSelectedFolder();
				String path = selectedFolder.getTreePath();

				inboxButton.setText(path);

				//int uid = selectedFolder.getUid();
				//item.setInbox( new Integer(uid).toString() );
			}
		} else if (action.equals("DRAFTS")) //$NON-NLS-1$
			{
				SelectFolderDialog dialog =
								MainInterface.treeModel.getSelectFolderDialog();

			if (dialog.success()) {
				Folder selectedFolder = dialog.getSelectedFolder();
				String path = selectedFolder.getTreePath();

				draftsButton.setText(path);

				//int uid = selectedFolder.getUid();
				//item.setDrafts( new Integer(uid).toString() );
			}
		} else if (action.equals("TEMPLATES")) //$NON-NLS-1$
			{
				SelectFolderDialog dialog =
								MainInterface.treeModel.getSelectFolderDialog();

			if (dialog.success()) {
				Folder selectedFolder = dialog.getSelectedFolder();
				String path = selectedFolder.getTreePath();

				templatesButton.setText(path);

				//int uid = selectedFolder.getUid();
				//item.setTemplates( new Integer(uid).toString() );
			}
		} else if (action.equals("SENT")) //$NON-NLS-1$
			{
				SelectFolderDialog dialog =
								MainInterface.treeModel.getSelectFolderDialog();

			if (dialog.success()) {
				Folder selectedFolder = dialog.getSelectedFolder();
				String path = selectedFolder.getTreePath();

				sentButton.setText(path);

				//int uid = selectedFolder.getUid();
				//item.setSent( new Integer(uid).toString() );
			}
		} else if (action.equals("DEFAULT_ACCOUNT")) {
			removeAll();

			if (defaultAccountCheckBox.isSelected()) {
				showDefaultAccountWarning();

			} else {
				layoutComponents();

			}

			revalidate();

		}
	}

	public boolean isFinished() {
		boolean result = true;

		/*
		String name = getAccountName();
		String address = getAddress();
		
		if ( name.length() == 0 )
		{
		    result = false;
		    JOptionPane.showMessageDialog( MainInterface.mainFrame,
		                                   "You have to enter a name for this account!");
		}
		else if ( address.length() == 0 )
		{
		    result = false;
		    JOptionPane.showMessageDialog( MainInterface.mainFrame,
		                                   "You have to enter your address!");
		}
		else
		{
		    result = true;
		}
		*/
		return result;
	}

}