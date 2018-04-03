super(frameController.getView().getFrame(), true);

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
package org.columba.mail.gui.config.search;

import net.javaprog.ui.wizard.plaf.basic.SingleSideEtchedBorder;

import org.columba.core.gui.frame.FrameMediator;
import org.columba.core.gui.util.ButtonWithMnemonic;
import org.columba.core.gui.util.CheckBoxWithMnemonic;
import org.columba.core.gui.util.ImageLoader;
import org.columba.core.gui.util.LabelWithMnemonic;
import org.columba.core.main.MainInterface;

import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.filter.FilterRule;
import org.columba.mail.folder.MessageFolder;
import org.columba.mail.folder.virtual.VirtualFolder;
import org.columba.mail.gui.config.filter.CriteriaList;
import org.columba.mail.gui.frame.MailFrameMediator;
import org.columba.mail.gui.table.command.ViewHeaderListCommand;
import org.columba.mail.gui.tree.util.SelectFolderDialog;
import org.columba.mail.gui.tree.util.TreeNodeList;
import org.columba.mail.main.MailInterface;
import org.columba.mail.util.MailResourceLoader;

import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.Dimension;
import java.awt.Font;
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
import javax.swing.SwingConstants;
import javax.swing.UIManager;
import javax.swing.border.CompoundBorder;


public class SearchFrame extends JDialog implements ActionListener {
    private JLabel folderLabel;
    private JLabel nameLabel;
    private JTextField folderTextField;
    private JButton addButton;

    //private JButton removeButton;
    private JButton selectButton;
    private JButton searchButton;
    private JCheckBox includeSubfolderButton;

    //private AdapterNode vFolderNode;
    private CriteriaList criteriaList;
    private VirtualFolder destFolder;

    //private AbstractFolder folderTreeNode;
    private JComboBox condList;
    private FrameMediator frameController;

    public SearchFrame(FrameMediator frameController,
        MessageFolder folder) {
        super();
        this.frameController = frameController;
        setTitle(MailResourceLoader.getString("dialog", "filter",
                "searchdialog_title"));

        //this.folder = folder;
        //this.vFolderNode = vFolderNode;
        this.destFolder = (VirtualFolder) folder;

        JPanel contentPane = new JPanel(new BorderLayout());

        //contentPane.setBorder(BorderFactory.createEmptyBorder(12, 12, 12, 12));
        //contentPane.add(createTopPanel("Search messages","Specify your search criteria...",ImageLoader.getImageIcon("virtualfolder.png")));
        contentPane.add(createCenterPanel(), BorderLayout.NORTH);

        JPanel bottom = new JPanel(new BorderLayout());
        bottom.setBorder(new SingleSideEtchedBorder(SwingConstants.TOP));

        JPanel buttonPanel = new JPanel(new GridLayout(1, 3, 6, 0));
        buttonPanel.setBorder(BorderFactory.createEmptyBorder(12, 12, 12, 12));
        searchButton = new JButton(MailResourceLoader.getString("dialog",
                    "filter", "search"));
        searchButton.setIcon(ImageLoader.getImageIcon("stock_search-16.png"));
        searchButton.addActionListener(this);
        searchButton.setActionCommand("SEARCH");
        buttonPanel.add(searchButton);

        ButtonWithMnemonic closeButton = new ButtonWithMnemonic(MailResourceLoader.getString(
                    "global", "close"));
        closeButton.addActionListener(this);
        closeButton.setActionCommand("CLOSE");
        buttonPanel.add(closeButton);

        ButtonWithMnemonic helpButton = new ButtonWithMnemonic(MailResourceLoader.getString(
                    "global", "help"));
        helpButton.addActionListener(this);
        helpButton.setActionCommand("HELP");
        helpButton.setEnabled(false);
        buttonPanel.add(helpButton);
        bottom.add(buttonPanel, BorderLayout.EAST);
        contentPane.add(bottom, BorderLayout.SOUTH);
        setContentPane(contentPane);
        getRootPane().setDefaultButton(searchButton);
        getRootPane().registerKeyboardAction(this, "CLOSE",
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
        rootPanel.setBorder(BorderFactory.createEmptyBorder(12, 12, 12, 12));

        JPanel folderPanel = new JPanel();
        folderPanel.setLayout(new BoxLayout(folderPanel, BoxLayout.X_AXIS));
        folderLabel = new LabelWithMnemonic(MailResourceLoader.getString(
                    "dialog", "filter", "choose_folder"));

        folderPanel.add(folderLabel);
        folderPanel.add(Box.createHorizontalStrut(5));
        selectButton = new JButton();
        folderLabel.setLabelFor(selectButton);
        selectButton.setActionCommand("SELECT");
        selectButton.addActionListener(this);
        folderPanel.add(selectButton);
        folderPanel.add(Box.createHorizontalGlue());
        includeSubfolderButton = new CheckBoxWithMnemonic(MailResourceLoader.getString(
                    "dialog", "filter", "include_subfolders"));
        folderPanel.add(includeSubfolderButton);
        rootPanel.add(folderPanel, BorderLayout.NORTH);

        JPanel middleIfPanel = new JPanel();
        middleIfPanel.setLayout(new BorderLayout());
        middleIfPanel.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createTitledBorder(MailResourceLoader.getString(
                        "dialog", "filter", "if")),
                BorderFactory.createEmptyBorder(5, 5, 5, 5)));

        JPanel ifPanel = new JPanel();
        ifPanel.setBorder(BorderFactory.createEmptyBorder(0, 0, 5, 0));
        ifPanel.setLayout(new BoxLayout(ifPanel, BoxLayout.X_AXIS));

        addButton = new ButtonWithMnemonic(MailResourceLoader.getString(
                    "dialog", "filter", "add_criterion"));
        addButton.setIcon(ImageLoader.getImageIcon("stock_add_16.png"));
        addButton.addActionListener(this);
        addButton.setActionCommand("ADD_CRITERION");

        //ifPanel.add(addButton);
        //ifPanel.add(Box.createRigidArea(new java.awt.Dimension(5, 0)));
        ifPanel.add(Box.createHorizontalGlue());

        nameLabel = new LabelWithMnemonic(MailResourceLoader.getString(
                    "dialog", "filter", "execute_actions"));
        ifPanel.add(nameLabel);

        ifPanel.add(Box.createRigidArea(new java.awt.Dimension(5, 0)));

        String[] cond = {
            MailResourceLoader.getString("dialog", "filter", "all_criteria"),
            MailResourceLoader.getString("dialog", "filter", "any_criteria")
        };
        condList = new JComboBox(cond);

        ifPanel.add(condList);

        middleIfPanel.add(ifPanel, BorderLayout.NORTH);

        criteriaList = new CriteriaList(destFolder.getFilter());
        criteriaList.setPreferredSize(new Dimension(500, 100));
        middleIfPanel.add(criteriaList, BorderLayout.CENTER);

        rootPanel.add(middleIfPanel, BorderLayout.CENTER);

        return rootPanel;
    }

    public JPanel createTopPanel(String title, String description,
        ImageIcon icon) {
        JPanel panel = new JPanel(new BorderLayout());
        panel.setBackground(Color.white);
        panel.setPreferredSize(new Dimension(300, 60));
        panel.setBorder(new CompoundBorder(
                new SingleSideEtchedBorder(SwingConstants.BOTTOM),
                BorderFactory.createEmptyBorder(10, 10, 10, 10)));

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

            if (value.equals("matchall")) {
                condList.setSelectedIndex(0);
            } else {
                condList.setSelectedIndex(1);
            }

            boolean isInclude = Boolean.valueOf(destFolder.getConfiguration().get("property",
                        "include_subfolders")).booleanValue();

            includeSubfolderButton.setSelected(isInclude);

            int uid = destFolder.getConfiguration().getInteger("property",
                    "source_uid");

            MessageFolder f = (MessageFolder) MailInterface.treeModel.getFolder(uid);

            // If f==null because of deleted MessageFolder fallback to Inbox
            if (f == null) {
                uid = 101;
                destFolder.getConfiguration().set("property", "source_uid", uid);
                f = (MessageFolder) MailInterface.treeModel.getFolder(uid);
            }

            selectButton.setText(f.getTreePath());

            criteriaList.updateComponents(b);
        } else {
            // get values from components
            FilterRule filterRule = destFolder.getFilter().getFilterRule();
            int index = condList.getSelectedIndex();

            if (index == 0) {
                filterRule.setCondition("matchall");
            } else {
                filterRule.setCondition("matchany");
            }

            if (includeSubfolderButton.isSelected()) {
                destFolder.getConfiguration().set("property",
                    "include_subfolders", "true");
            } else {
                destFolder.getConfiguration().set("property",
                    "include_subfolders", "false");
            }

            String path = selectButton.getText();
            TreeNodeList list = new TreeNodeList(path);
            MessageFolder folder = (MessageFolder) MailInterface.treeModel.getFolder(list);
            int uid = folder.getUid();
            destFolder.getConfiguration().set("property", "source_uid", uid);

            criteriaList.updateComponents(b);
        }
    }

    public void setSourceFolder(MessageFolder f) {
        selectButton.setText(f.getTreePath());
    }

    public void actionPerformed(ActionEvent e) {
        String action = e.getActionCommand();

        if (action.equals("CLOSE")) {
            updateComponents(false);
            setVisible(false);
        } else if (action.equals("ADD_CRITERION")) {
            criteriaList.add();
        } else if (action.equals("SELECT")) {
            SelectFolderDialog dialog = MailInterface.treeModel.getSelectFolderDialog();

            if (dialog.success()) {
                MessageFolder folder = dialog.getSelectedFolder();
                String path = folder.getTreePath();

                selectButton.setText(path);
            }
        } else if (action.equals("SEARCH")) {
            updateComponents(false);
            setVisible(false);

            try {
                ((VirtualFolder) destFolder).addSearchToHistory();
            } catch (Exception ex) {
                ex.printStackTrace();
            }

            FolderCommandReference[] r = new FolderCommandReference[1];
            r[0] = new FolderCommandReference(destFolder);

            ((MailFrameMediator) frameController).setTreeSelection(r);

            MainInterface.processor.addOp(new ViewHeaderListCommand(
                    frameController, r));

            //frameMediator.treeController.setSelected(destFolder);
        }
    }
}