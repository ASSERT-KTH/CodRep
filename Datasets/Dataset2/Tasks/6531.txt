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

package org.columba.mail.gui.config.search;

import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.Component;
import java.awt.Dimension;
import java.awt.Font;
import java.awt.Graphics;
import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.GridLayout;
import java.awt.Insets;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.KeyEvent;

import javax.swing.BorderFactory;
import javax.swing.Box;
import javax.swing.BoxLayout;
import javax.swing.ImageIcon;
import javax.swing.JButton;
import javax.swing.JCheckBox;
import javax.swing.JComboBox;
import javax.swing.JComponent;
import javax.swing.JDialog;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JTextField;
import javax.swing.KeyStroke;
import javax.swing.UIManager;
import javax.swing.border.AbstractBorder;
import javax.swing.border.Border;
import javax.swing.border.CompoundBorder;

import org.columba.core.gui.button.CloseButton;
import org.columba.core.gui.button.HelpButton;
import org.columba.core.gui.util.ImageLoader;
import org.columba.mail.filter.FilterRule;
import org.columba.mail.folder.Folder;
import org.columba.mail.folder.virtual.VirtualFolder;
import org.columba.mail.gui.config.filter.CriteriaList;
import org.columba.mail.gui.frame.MailFrameController;
import org.columba.mail.gui.tree.util.SelectFolderDialog;
import org.columba.mail.gui.tree.util.TreeNodeList;
import org.columba.mail.util.MailResourceLoader;
import org.columba.main.MainInterface;

public class SearchFrame extends JDialog implements ActionListener {

	private JLabel folderLabel;
	private JLabel nameLabel;
	private JTextField folderTextField;

	private JButton addButton;
	//private JButton removeButton;
	private JButton selectButton;

	private JButton searchButton;
	private CloseButton closeButton;
	private HelpButton helpButton;

	private JCheckBox includeSubfolderButton;

	//private AdapterNode vFolderNode;
	private CriteriaList criteriaList;
	private VirtualFolder destFolder;

	//private FolderTreeNode folderTreeNode;

	private JComboBox condList;

	MailFrameController frameController;

	public SearchFrame(MailFrameController frameController, Folder folder) {
		super();
		this.frameController = frameController;
		setTitle(
			MailResourceLoader.getString(
				"dialog",
				"filter",
				"searchdialog_title"));

		//this.folder = folder;
		//this.vFolderNode = vFolderNode;

		this.destFolder = (VirtualFolder) folder;

		JPanel contentPane = new JPanel(new BorderLayout());
		contentPane.setBorder(BorderFactory.createEmptyBorder(12, 12, 11, 11));
		//contentPane.add(createTopPanel("Search messages","Specify your search criteria...",ImageLoader.getImageIcon("virtualfolder.png")));
		contentPane.add(createCenterPanel(), BorderLayout.NORTH);
		JPanel bottom = new JPanel(new BorderLayout());
		bottom.setBorder(BorderFactory.createEmptyBorder(17, 0, 0, 0));
		JPanel buttonPanel = new JPanel(new GridLayout(1, 3, 5, 0));
		searchButton = new JButton("Search");
		searchButton.setIcon(ImageLoader.getImageIcon("stock_search-16.png"));
		searchButton.addActionListener(this);
		searchButton.setActionCommand("SEARCH");
		buttonPanel.add(searchButton);
		closeButton = new CloseButton();
		closeButton.addActionListener(this);
		closeButton.setActionCommand("CLOSE");
		buttonPanel.add(closeButton);
		helpButton = new HelpButton();
		helpButton.addActionListener(this);
		helpButton.setActionCommand("HELP");
		helpButton.setEnabled(false);
		buttonPanel.add(helpButton);
		bottom.add(buttonPanel, BorderLayout.EAST);
		contentPane.add(bottom, BorderLayout.SOUTH);
		setContentPane(contentPane);
		getRootPane().setDefaultButton(searchButton);
		getRootPane().registerKeyboardAction(
			this,
			"CLOSE",
			KeyStroke.getKeyStroke(KeyEvent.VK_ESCAPE, 0),
			JComponent.WHEN_IN_FOCUSED_WINDOW);
		updateComponents(true);
		pack();
		setLocationRelativeTo(null);
		setVisible(true);

	}

	private JPanel createCenterPanel() {

		JPanel rootPanel = new JPanel();
		rootPanel.setLayout(new BorderLayout(0, 10));

		JPanel folderPanel = new JPanel();
		folderPanel.setLayout(new BoxLayout(folderPanel, BoxLayout.X_AXIS));
		folderLabel =
			new JLabel(
				MailResourceLoader.getString(
					"dialog",
					"filter",
					"choose_folder"));
		folderLabel.setDisplayedMnemonic(
			MailResourceLoader.getMnemonic(
				"dialog",
				"filter",
				"choose_folder"));

		folderPanel.add(folderLabel);
		folderPanel.add(Box.createHorizontalStrut(5));
		selectButton = new JButton();
		folderLabel.setLabelFor(selectButton);
		selectButton.setActionCommand("SELECT");
		selectButton.addActionListener(this);
		folderPanel.add(selectButton);
		folderPanel.add(Box.createHorizontalGlue());
		includeSubfolderButton =
			new JCheckBox(
				MailResourceLoader.getString(
					"dialog",
					"filter",
					"include_subfolders"));
		includeSubfolderButton.setMnemonic(
			MailResourceLoader.getMnemonic(
				"dialog",
				"filter",
				"include_subfolders"));
		folderPanel.add(includeSubfolderButton);
		rootPanel.add(folderPanel, BorderLayout.NORTH);

		JPanel middleIfPanel = new JPanel();
		middleIfPanel.setLayout(new BorderLayout());
		Border border =
			BorderFactory.createTitledBorder(
				BorderFactory.createEtchedBorder(),
				"If");
		middleIfPanel.setBorder(
			BorderFactory.createCompoundBorder(
				border,
				BorderFactory.createEmptyBorder(5, 5, 5, 5)));

		JPanel ifPanel = new JPanel();
		ifPanel.setBorder(BorderFactory.createEmptyBorder(0, 0, 5, 0));
		ifPanel.setLayout(new BoxLayout(ifPanel, BoxLayout.X_AXIS));

		addButton =
			new JButton(
				MailResourceLoader.getString(
					"dialog",
					"filter",
					"add_criterion"));
		addButton.setMnemonic(
			MailResourceLoader.getMnemonic(
				"dialog",
				"filter",
				"add_criterion"));
		addButton.setIcon(ImageLoader.getImageIcon("stock_add_16.png"));
		addButton.addActionListener(this);
		addButton.setActionCommand("ADD_CRITERION");
		//ifPanel.add(addButton);

		//ifPanel.add(Box.createRigidArea(new java.awt.Dimension(5, 0)));

		ifPanel.add(Box.createHorizontalGlue());

		nameLabel =
			new JLabel(
				MailResourceLoader.getString(
					"dialog",
					"filter",
					"execute_actions"));
		nameLabel.setDisplayedMnemonic(
			MailResourceLoader.getMnemonic(
				"dialog",
				"filter",
				"execute_actions"));
		ifPanel.add(nameLabel);

		ifPanel.add(Box.createRigidArea(new java.awt.Dimension(5, 0)));

		String[] cond =
			{
				MailResourceLoader.getString(
					"dialog",
					"filter",
					"all_criteria"),
				MailResourceLoader.getString(
					"dialog",
					"filter",
					"any_criteria")};
		condList = new JComboBox(cond);

		ifPanel.add(condList);

		middleIfPanel.add(ifPanel, BorderLayout.NORTH);

		criteriaList =
			new CriteriaList(
				destFolder.getFilterPluginHandler(),
				destFolder.getFilter());
		criteriaList.setPreferredSize(new Dimension(500, 100));
		middleIfPanel.add(criteriaList, BorderLayout.CENTER);

		rootPanel.add(middleIfPanel, BorderLayout.CENTER);

		return rootPanel;
	}

	public JPanel createTopPanel(
		String title,
		String description,
		ImageIcon icon) {
		JPanel panel = new JPanel();
		panel.setBackground(Color.white);
		panel.setPreferredSize(new Dimension(300, 60));
		panel.setLayout(new BorderLayout());
		panel.setBorder(new WizardBottomBorder());
		Border border = panel.getBorder();
		Border margin = BorderFactory.createEmptyBorder(10, 10, 10, 10);
		panel.setBorder(new CompoundBorder(border, margin));
		//panel.setBorder(new WizardBottomBorder());

		JPanel leftPanel = new JPanel();
		leftPanel.setBackground(Color.white);

		GridBagLayout layout = new GridBagLayout();
		leftPanel.setLayout(layout);
		GridBagConstraints c = new GridBagConstraints();

		JLabel titleLabel = new JLabel(title);
		//titleLabel.setAlignmentY(0);
		Font font = UIManager.getFont("Label.font");
		font = font.deriveFont(Font.BOLD);
		titleLabel.setFont(font);
		c.gridy = 0;
		c.anchor = GridBagConstraints.NORTHWEST;
		c.gridwidth = GridBagConstraints.REMAINDER;
		layout.setConstraints(titleLabel, c);
		leftPanel.add(titleLabel);

		c.gridy = 1;
		c.insets = new Insets(0, 20, 0, 0);
		JLabel descriptionLabel = new JLabel(description);
		layout.setConstraints(descriptionLabel, c);
		leftPanel.add(descriptionLabel);

		panel.add(leftPanel, BorderLayout.WEST);

		JLabel iconLabel = new JLabel(icon);
		panel.add(iconLabel, BorderLayout.EAST);

		return panel;
	}

	public void updateComponents(boolean b) {
		if (b) {

			FilterRule filterRule = destFolder.getFilter().getFilterRule();
			String value = filterRule.getCondition();
			if (value.equals("matchall"))
				condList.setSelectedIndex(0);
			else
				condList.setSelectedIndex(1);

			boolean isInclude =
				(new Boolean(destFolder
					.getFolderItem()
					.get("property", "include_subfolders")))
					.booleanValue();

			boolean value2 = isInclude;
			if (value2 == true)
				includeSubfolderButton.setSelected(true);
			else
				includeSubfolderButton.setSelected(false);

			int uid =
				destFolder.getFolderItem().getInteger("property", "source_uid");
			Folder f = (Folder) MainInterface.treeModel.getFolder(uid);
			String treePath = f.getTreePath();

			selectButton.setText(treePath);

			criteriaList.updateComponents(b);

		} else {
			// get values from components

			FilterRule filterRule = destFolder.getFilter().getFilterRule();
			int index = condList.getSelectedIndex();
			if (index == 0)
				filterRule.setCondition("matchall");
			else
				filterRule.setCondition("matchany");

			if (includeSubfolderButton.isSelected())
				destFolder.getFolderItem().set(
					"property",
					"include_subfolders",
					"true");
			else
				destFolder.getFolderItem().set(
					"property",
					"include_subfolders",
					"false");

			String path = selectButton.getText();
			TreeNodeList list = new TreeNodeList(path);
			Folder folder = (Folder) MainInterface.treeModel.getFolder(list);
			int uid = folder.getUid();
			destFolder.getFolderItem().set("property", "source_uid", uid);

			criteriaList.updateComponents(b);
		}

	}

	public void setSourceFolder(Folder f) {
		String treePath = f.getTreePath();

		selectButton.setText(treePath);
		System.out.println("selected path:" + treePath);
	}

	public void actionPerformed(ActionEvent e) {
		String action = e.getActionCommand();

		if (action.equals("CLOSE")) {

			updateComponents(false);
			setVisible(false);
		} else if (action.equals("ADD_CRITERION")) {
			//System.out.println( "add" );

			criteriaList.add();

		} else if (action.equals("SELECT")) {

			SelectFolderDialog dialog =
				MainInterface.treeModel.getSelectFolderDialog();

			if (dialog.success()) {
				Folder folder = dialog.getSelectedFolder();
				String path = folder.getTreePath();

				selectButton.setText(path);
			}

		} else if (action.equals("SEARCH")) {
			updateComponents(false);

			setVisible(false);

			frameController.treeController.setSelected(destFolder);
			
			// FIXME
			/*
			try {
				searchFilter.applySearch();
				if (!(MainInterface
					.treeViewer
					.getSelected()
					.equals(destFolder)))
					MainInterface.treeViewer.setSelected(destFolder);
			} catch (Exception ex) {
				ex.printStackTrace();
			}
			*/

			/*
			if ( destFolder.getUid() == 106 )
				searchFilter.addSearchToHistory();
			*/

		}

	}

	public class WizardBottomBorder extends AbstractBorder {
		protected Insets borderInsets = new Insets(0, 0, 0, 2);
		public void paintBorder(
			Component c,
			Graphics g,
			int x,
			int y,
			int w,
			int h) {
			g.setColor(UIManager.getColor("Button.darkShadow"));
			g.drawLine(x, y + h - 2, x + w - 1, y + h - 2);
			g.setColor(Color.white);
			g.drawLine(x, y + h - 1, x + w - 1, y + h - 1);
		}
		public Insets getBorderInsets(Component c) {
			return borderInsets;
		}
	}

	public class WizardTopBorder extends AbstractBorder {
		protected Insets borderInsets = new Insets(2, 0, 0, 0);
		public void paintBorder(
			Component c,
			Graphics g,
			int x,
			int y,
			int w,
			int h) {
			g.setColor(UIManager.getColor("Button.darkShadow"));
			g.drawLine(x, y, x + w - 1, y);
			g.setColor(Color.white);
			g.drawLine(x, y + 1, x + w - 1, y + 1);
		}
		public Insets getBorderInsets(Component c) {
			return borderInsets;
		}
	}

}