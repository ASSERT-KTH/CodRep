r[0] = new FolderCommandReference(dialog.getSelected());

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
package org.columba.mail.gui.tree.util;

import org.columba.core.gui.util.ButtonWithMnemonic;
import org.columba.core.gui.util.DialogStore;
import org.columba.core.main.MainInterface;

import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.folder.Folder;
import org.columba.mail.folder.FolderTreeNode;
import org.columba.mail.gui.tree.command.CreateSubFolderCommand;
import org.columba.mail.main.MailInterface;
import org.columba.mail.util.MailResourceLoader;

import java.awt.BorderLayout;
import java.awt.Dimension;
import java.awt.GridLayout;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.KeyEvent;

import javax.swing.BorderFactory;
import javax.swing.JButton;
import javax.swing.JComponent;
import javax.swing.JDialog;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JTree;
import javax.swing.KeyStroke;
import javax.swing.event.TreeSelectionEvent;
import javax.swing.event.TreeSelectionListener;


public class SelectFolderDialog implements ActionListener,
    TreeSelectionListener {
    private String name;
    private boolean bool = false;

    //public SelectFolderTree tree;
    private JTree tree;
    private JButton okButton;
    private JButton newButton;

    //private TreeController treeController;
    //private TreeModel treeModel;
    private FolderTreeNode selectedFolder;

    //private JFrame frame;
    protected JDialog dialog;

    public SelectFolderDialog() {
        dialog = DialogStore.getDialog(MailResourceLoader.getString("dialog",
                    "folder", "select_folder"));

        name = new String("name");

        init();
    }

    public void init() {
        JPanel contentPane = (JPanel) dialog.getContentPane();
        contentPane.setBorder(BorderFactory.createEmptyBorder(12, 12, 11, 11));

        tree = new JTree(MailInterface.treeModel);
        tree.expandRow(0);
        tree.expandRow(1);
        tree.putClientProperty("JTree.lineStyle", "Angled");
        tree.setShowsRootHandles(true);
        tree.setRootVisible(false);
        tree.addTreeSelectionListener(this);

        FolderTreeCellRenderer renderer = new FolderTreeCellRenderer();
        tree.setCellRenderer(renderer);

        JScrollPane scrollPane = new JScrollPane(tree);
        scrollPane.setPreferredSize(new Dimension(150, 300));
        contentPane.add(scrollPane);

        JPanel bottomPanel = new JPanel(new BorderLayout());
        bottomPanel.setBorder(BorderFactory.createEmptyBorder(17, 0, 0, 0));

        JPanel buttonPanel = new JPanel(new GridLayout(1, 3, 5, 0));
        okButton = new ButtonWithMnemonic(MailResourceLoader.getString("", "ok"));
        okButton.setEnabled(false);
        okButton.setActionCommand("OK");
        okButton.addActionListener(this);
        buttonPanel.add(okButton);
        newButton = new ButtonWithMnemonic(MailResourceLoader.getString(
                    "dialog", "folder", "new_folder"));
        newButton.setEnabled(true);
        newButton.setActionCommand("NEW");
        newButton.addActionListener(this);
        buttonPanel.add(newButton);

        ButtonWithMnemonic cancelButton = new ButtonWithMnemonic(MailResourceLoader.getString(
                    "", "cancel"));
        cancelButton.setActionCommand("CANCEL");
        cancelButton.addActionListener(this);
        buttonPanel.add(cancelButton);
        bottomPanel.add(buttonPanel, BorderLayout.EAST);
        contentPane.add(bottomPanel, BorderLayout.SOUTH);
        dialog.getRootPane().setDefaultButton(okButton);
        dialog.getRootPane().registerKeyboardAction(this, "CANCEL",
            KeyStroke.getKeyStroke(KeyEvent.VK_ESCAPE, 0),
            JComponent.WHEN_IN_FOCUSED_WINDOW);
        dialog.pack();
        dialog.setLocationRelativeTo(null);
        dialog.setVisible(true);
    }

    public boolean success() {
        return bool;
    }

    public Folder getSelectedFolder() {
        return (Folder) selectedFolder;
    }

    public void actionPerformed(ActionEvent e) {
        String action = e.getActionCommand();

        if (action.equals("OK")) {
            //name = textField.getText();
            bool = true;

            dialog.dispose();
        } else if (action.equals("CANCEL")) {
            bool = false;

            dialog.dispose();
        } else if (action.equals("NEW")) {
            CreateFolderDialog dialog = new CreateFolderDialog(tree.getSelectionPath());
            dialog.showDialog();

            String name;

            if (dialog.success()) {
                // ok pressed
                name = dialog.getName();
            } else {
                // cancel pressed
                return;
            }

            FolderCommandReference[] r = new FolderCommandReference[1];
            r[0] = new FolderCommandReference(getSelectedFolder());
            r[0].setFolderName(name);

            MainInterface.processor.addOp(new CreateSubFolderCommand(r));
        }
    }

    /******************************* tree selection listener ********************************/
    public void valueChanged(TreeSelectionEvent e) {
        FolderTreeNode node = (FolderTreeNode) tree.getLastSelectedPathComponent();

        if (node == null) {
            return;
        }

        if (node instanceof Folder) {
            selectedFolder = (Folder) node;
        }

        if (node.supportsAddMessage()) {
            okButton.setEnabled(true);
        } else {
            okButton.setEnabled(false);
        }
    }
}