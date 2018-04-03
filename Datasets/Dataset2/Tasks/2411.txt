"filtertoolbar_header"));

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

package org.columba.mail.gui.table;

import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.Insets;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.FocusEvent;
import java.awt.event.FocusListener;

import javax.swing.BorderFactory;
import javax.swing.JButton;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JTextField;
import javax.swing.JToggleButton;

import org.columba.core.gui.util.ImageLoader;
import org.columba.core.gui.util.ToolbarToggleButton;
import org.columba.core.main.MainInterface;
import org.columba.mail.folder.Folder;
import org.columba.mail.gui.table.util.TableModelFilteredView;
import org.columba.mail.util.MailResourceLoader;

public class FilterToolbar extends JPanel implements ActionListener {
	public JToggleButton newButton;
	public JToggleButton oldButton;
	private JToggleButton answeredButton;
	private JToggleButton flaggedButton;
	private JToggleButton expungedButton;
	private JToggleButton draftButton;
	private JToggleButton attachmentButton;
	private JToggleButton secureButton;

	public JButton clearButton;
	public JButton advancedButton;

	//private JComboBox comboBox;
	private JTextField textField;

	private TableController tableController;

	public FilterToolbar(TableController headerTableViewer) {
		super();
		this.tableController = headerTableViewer;

		//setMargin(new Insets(0, 0, 0, 0));

		addCButtons();

		//setBorderPainted(false);
		//setFloatable(false);
	}

	public void addCButtons() {
		GridBagLayout layout = new GridBagLayout();
		setLayout(layout);
		GridBagConstraints c = new GridBagConstraints();

		setBorder(BorderFactory.createEmptyBorder(2, 5, 2, 5));

		//addSeparator();
		newButton = new ToolbarToggleButton(
				ImageLoader.getSmallImageIcon("mail-new.png"));
		newButton.setToolTipText(
			MailResourceLoader.getString(
				"menu",
				"mainframe",
				"filtertoolbar_unread"));
		newButton.addActionListener(this);
		newButton.setActionCommand("NEW");
		newButton.setSelected(false);
		newButton.setMargin(new Insets(0, 0, 0, 0));
		c.weightx = 0.0;

		c.anchor = GridBagConstraints.WEST;
		//c.insets = new Insets(0, 10, 0, 0);
		//c.gridx = GridBagConstraints.RELATIVE;
		c.gridwidth = 1;
		layout.setConstraints(newButton, c);
		add(newButton);

		/*
		oldButton = new ToolbarToggleButton(ImageLoader.getSmallImageIcon("mail-read.png"));
		oldButton.setToolTipText( GlobalResourceLoader.getString("menu","mainframe","filtertoolbar_read") );
		oldButton.addActionListener(this);
		oldButton.setActionCommand("OLD");
		//newButton.setSelected(true);
		oldButton.setMargin(new Insets(0, 0, 0, 0));
		layout.setConstraints(oldButton, c);
		add(oldButton);
		*/
		//addSeparator();

		answeredButton = new ToolbarToggleButton(
				ImageLoader.getSmallImageIcon("reply_small.png"));
		answeredButton.addActionListener(this);
		answeredButton.setToolTipText(
			MailResourceLoader.getString(
				"menu",
				"mainframe",
				"filtertoolbar_answered"));
		answeredButton.setActionCommand("ANSWERED");
		answeredButton.setMargin(new Insets(0, 0, 0, 0));
		answeredButton.setSelected(false);

		layout.setConstraints(answeredButton, c);
		add(answeredButton);

		flaggedButton = new ToolbarToggleButton(
				ImageLoader.getSmallImageIcon("mark-as-important-16.png"));
		flaggedButton.setToolTipText(
			MailResourceLoader.getString(
				"menu",
				"mainframe",
				"filtertoolbar_flagged"));
		flaggedButton.setMargin(new Insets(0, 0, 0, 0));
		flaggedButton.addActionListener(this);
		flaggedButton.setActionCommand("FLAGGED");
		flaggedButton.setSelected(false);
		c.insets = new Insets(0, 0, 0, 0);
		layout.setConstraints(flaggedButton, c);
		add(flaggedButton);

		expungedButton = new ToolbarToggleButton(
				ImageLoader.getSmallImageIcon("stock_delete-16.png"));
		expungedButton.setToolTipText(
			MailResourceLoader.getString(
				"menu",
				"mainframe",
				"filtertoolbar_expunged"));
		expungedButton.setMargin(new Insets(0, 0, 0, 0));
		expungedButton.addActionListener(this);
		expungedButton.setActionCommand("EXPUNGED");
		expungedButton.setSelected(false);
		layout.setConstraints(expungedButton, c);
		add(expungedButton);

		attachmentButton = new ToolbarToggleButton(
				ImageLoader.getSmallImageIcon("attachment.png"));
		attachmentButton.setToolTipText(
			MailResourceLoader.getString(
				"menu",
				"mainframe",
				"filtertoolbar_attachment"));
		attachmentButton.setMargin(new Insets(0, 0, 0, 0));
		attachmentButton.addActionListener(this);
		attachmentButton.setActionCommand("ATTACHMENT");
		attachmentButton.setSelected(false);
		layout.setConstraints(attachmentButton, c);
		add(attachmentButton);

		//addSeparator();
		//addSeparator();

		//addSeparator();

		/*
		//HeaderTableItem list = MainInterface.config.getOptionsConfig().getHeaderTableItem();
		HeaderTableItem list = tableController.getHeaderTableItem();
		comboBox = new JComboBox();
		comboBox.setToolTipText( GlobalResourceLoader.getString("menu","mainframe","filtertoolbar_header") );
		String name;
		
		for (int i = 0; i < list.count(); i++)
		{
			name = list.getName(i);
			boolean enabled = list.getEnabled(i);
		
			if (enabled == false)
				continue;
		
			if (!(name.equalsIgnoreCase("status")
				|| name.equalsIgnoreCase("attachment")
				|| name.equalsIgnoreCase("flagged")
				|| name.equalsIgnoreCase("priority")
				|| name.equalsIgnoreCase("date")
				|| name.equalsIgnoreCase("size")))
				comboBox.addItem(name);
		
		}
		
		//comboBox.setMaximumSize(new java.awt.Dimension(100, 25));
		comboBox.setSelectedIndex(0);
		comboBox.addActionListener(this);
		comboBox.setActionCommand("COMBO");
		
		
		*/

		JLabel label = new JLabel(MailResourceLoader.getString(
                                "menu",
                                "mainframe",
                                "filtertoolbar_label"));
		c.insets = new Insets(0, 10, 0, 0);
		layout.setConstraints(label, c);
		add(label);

		//addSeparator();

		textField = new JTextField();
		textField.addActionListener(this);
		textField.setActionCommand("TEXTFIELD");
		textField.addFocusListener(new FocusListener() {
			public void focusGained(FocusEvent e) {}

			public void focusLost(FocusEvent e) {
				TableModelFilteredView model =
					tableController.getView().getTableModelFilteredView();
				try {
					model.setPatternString(textField.getText());
				} catch (Exception ex) {
					ex.printStackTrace();
				}
			}
		});
		//textField.setMaximumSize( new java.awt.Dimension( 600, 25 ) );
		c.weightx = 1.0;
		c.insets = new Insets(0, 5, 0, 0);
		c.fill = GridBagConstraints.BOTH;
		layout.setConstraints(textField, c);
		add(textField);

		//addSeparator();

		clearButton = new JButton(MailResourceLoader.getString(
                                "menu",
                                "mainframe",
                                "filtertoolbar_clear"));
		clearButton.setToolTipText(
			MailResourceLoader.getString(
				"menu",
				"mainframe",
				"filtertoolbar_clear_tooltip"));
		//clearButton.setMaximumSize(new java.awt.Dimension(150, 25));
		attachmentButton.setSelected(false);
		clearButton.setActionCommand("CLEAR");
		clearButton.addActionListener(this);
		c.weightx = 0.0;
		c.insets = new Insets(0, 10, 0, 0);
		c.fill = GridBagConstraints.NONE;
		c.gridwidth = GridBagConstraints.RELATIVE;
		layout.setConstraints(clearButton, c);
		add(clearButton);

		advancedButton = new JButton(MailResourceLoader.getString(
                                "menu",
                                "mainframe",
                                "filtertoolbar_advanced"));
		advancedButton.setToolTipText(
			MailResourceLoader.getString(
				"menu",
				"mainframe",
				"filtertoolbar_advanced_tooltip"));
		//advancedButton.setMaximumSize(new java.awt.Dimension(150, 25));
		attachmentButton.setSelected(false);
		advancedButton.setActionCommand("ADVANCED");
		advancedButton.addActionListener(this);
		c.weightx = 0.0;
		c.fill = GridBagConstraints.NONE;
		c.gridwidth = GridBagConstraints.REMAINDER;
		layout.setConstraints(advancedButton, c);
		add(advancedButton);

		//add( Box.createHorizontalGlue() );

		//addSeparator();

		/*
		addSeparator();
		
		threadButton = new ToolbarToggleButton(ImageLoader.getImageIcon("org/columba/core/images/Export16.gif") );
		threadButton.setEnabled( false );
		threadButton.setMargin( new Insets(0,0,0,0) );
		add(threadButton);
		*/

		/*
		  secureCButton = new JButton(ImageLoader.getImageIcon("org/columba/core/images/secure.jpg") );
		  add(secureCButton);
		*/

		//addSeparator();
	}

	public void update() throws Exception {
		/*
		TableChangedEvent ev = new TableChangedEvent( TableChangedEvent.UPDATE );
		 
		tableController.tableChanged(ev);
		*/
		tableController
			.getHeaderTableModel()
			.getTableModelFilteredView()
			.setDataFiltering(true);
	}

	public void actionPerformed(ActionEvent e) {
		String action = e.getActionCommand();

		try {

			//TableModelFilteredView model = MainInterface.tableController.getHeaderTable().getTableModelFilteredView();
			TableModelFilteredView model =
				tableController.getView().getTableModelFilteredView();

			if (action.equals("ADVANCED")) {

				Folder searchFolder =
					(Folder) MainInterface.treeModel.getFolder(106);

				Folder folder =
					(Folder) tableController
						.getMailFrameController()
						.getTableSelection()[0]
						.getFolder();

				if (folder == null)
					return;

				org.columba.mail.gui.config.search.SearchFrame frame =
					new org.columba.mail.gui.config.search.SearchFrame(
						tableController.getMailFrameController(),
						searchFolder);

				frame.setSourceFolder(folder);
				frame.setVisible(true);

			} else if (action.equals("NEW")) {
				model.setNewFlag(!model.getNewFlag());
				update();
			} else if (action.equals("ANSWERED")) {
				model.setAnsweredFlag(!model.getAnsweredFlag());
				update();
			} else if (action.equals("FLAGGED")) {
				model.setFlaggedFlag(!model.getFlaggedFlag());
				update();
			} else if (action.equals("EXPUNGED")) {
				model.setExpungedFlag(!model.getExpungedFlag());
				update();
			} else if (action.equals("ATTACHMENT")) {
				model.setAttachmentFlag(!model.getAttachmentFlag());
				update();
			} else if (action.equals("TEXTFIELD")) {
				model.setPatternString(textField.getText());
				update();
			} else if (action.equals("CLEAR")) {
				if (model == null) {
					return;
				}

				model.setNewFlag(false);
				//model.setOldFlag(true);
				model.setAnsweredFlag(false);
				model.setFlaggedFlag(false);
				model.setExpungedFlag(false);
				model.setAttachmentFlag(false);
				model.setPatternString("");

				textField.setText("");

				newButton.setSelected(false);
				//oldButton.setSelected(true);
				answeredButton.setSelected(false);
				flaggedButton.setSelected(false);
				expungedButton.setSelected(false);
				attachmentButton.setSelected(false);

				tableController
					.getHeaderTableModel()
					.getTableModelFilteredView()
					.setDataFiltering(true);

			}
		} catch (Exception ex) {
			ex.printStackTrace();
		}
	}
}