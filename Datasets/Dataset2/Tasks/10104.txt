import org.columba.core.gui.base.CTabbedPane;

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
package org.columba.addressbook.gui;

import java.awt.BorderLayout;
import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.GridLayout;
import java.awt.Insets;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

import javax.swing.BorderFactory;
import javax.swing.JButton;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JTextField;
import javax.swing.event.ChangeEvent;
import javax.swing.event.ChangeListener;

import org.columba.addressbook.gui.list.AddressbookDNDListView;
import org.columba.addressbook.gui.list.AddressbookListModel;
import org.columba.addressbook.model.HeaderItemList;
import org.columba.addressbook.model.IContactItemMap;
import org.columba.addressbook.util.AddressbookResourceLoader;
import org.columba.core.gui.util.CTabbedPane;
import org.columba.mail.gui.composer.ComposerController;


/**
 * @version         1.0
 * @author
 */
public class AddressbookPanel extends JPanel implements ActionListener,
    ChangeListener {
    private AddressbookDNDListView addressbook;
    private ComposerController composerController;
    private JLabel chooseLabel;
    private JButton chooseButton;
    private JButton toButton;
    private JButton ccButton;
    private JButton bccButton;
    private AddressbookListModel[] list;
    private int[] books;
    private CTabbedPane pane;

    public AddressbookPanel(ComposerController c) {
        this.composerController = c;

        books = new int[2];
        books[0] = 101;
        books[1] = 102;

        /*
list = composerInterface.composerHeader.getListModels();
*/
        init();
    }

    protected void init() {
        setLayout(new BorderLayout());

        pane = new CTabbedPane();

        //pane.setBorder(BorderFactory.createEmptyBorder(0, 5, 0, 5));
        pane.addChangeListener(this);

        add(pane, BorderLayout.CENTER);

        pane.add(AddressbookResourceLoader.getString("dialog",
                "addressbookpanel", "personal_addressbook"), new JPanel()); //$NON-NLS-1$
        pane.add(AddressbookResourceLoader.getString("dialog",
                "addressbookpanel", "collected_addresses"), new JPanel()); //$NON-NLS-1$
    }

    public JPanel createPanel(int uid) {
        JPanel panel = new JPanel();
        panel.setLayout(new BorderLayout());

        addressbook = new AddressbookDNDListView();
        addressbook.setAcceptDrop(false);

        JScrollPane scrollPane = new JScrollPane(addressbook);

        panel.add(scrollPane, BorderLayout.CENTER);

        JPanel topPanel = new JPanel();
        topPanel.setBorder(BorderFactory.createEmptyBorder(5, 5, 5, 5));

        topPanel.setLayout(new BorderLayout());

        JPanel labelPanel = new JPanel();
        labelPanel.setLayout(new GridLayout(1, 3, 5, 5));

        toButton = new JButton(AddressbookResourceLoader.getString("dialog",
                    "addressbookpanel", "to")); //$NON-NLS-1$
        toButton.setActionCommand("TO"); //$NON-NLS-1$
        toButton.addActionListener(this);
        ccButton = new JButton(AddressbookResourceLoader.getString("dialog",
                    "addressbookpanel", "cc")); //$NON-NLS-1$
        ccButton.setActionCommand("CC"); //$NON-NLS-1$
        ccButton.addActionListener(this);
        bccButton = new JButton(AddressbookResourceLoader.getString("dialog",
                    "addressbookpanel", "bcc")); //$NON-NLS-1$
        bccButton.setActionCommand("BCC"); //$NON-NLS-1$
        bccButton.addActionListener(this);
        labelPanel.add(toButton);
        labelPanel.add(ccButton);
        labelPanel.add(bccButton);

        topPanel.add(labelPanel, BorderLayout.NORTH);

        JPanel middlePanel = new JPanel();
        GridBagLayout layout = new GridBagLayout();
        middlePanel.setLayout(layout);

        GridBagConstraints c = new GridBagConstraints();

        JLabel containsLabel = new JLabel(AddressbookResourceLoader.getString(
                    "dialog", "addressbookpanel", "contains")); //$NON-NLS-1$
        containsLabel.setEnabled(false);

        JTextField textField = new JTextField();
        textField.setEnabled(false);

        c.anchor = GridBagConstraints.WEST;
        c.gridx = 0;
        c.insets = new Insets(5, 0, 0, 5);
        c.weightx = 0.0;
        c.gridwidth = GridBagConstraints.RELATIVE;
        layout.setConstraints(containsLabel, c);
        middlePanel.add(containsLabel);

        c.anchor = GridBagConstraints.EAST;
        c.weightx = 1.0;
        c.insets = new Insets(5, 0, 0, 0);
        c.gridwidth = GridBagConstraints.REMAINDER;
        c.gridx = 1;
        c.fill = GridBagConstraints.HORIZONTAL;
        layout.setConstraints(textField, c);
        middlePanel.add(textField);

        topPanel.add(middlePanel, BorderLayout.CENTER);

        panel.add(topPanel, BorderLayout.NORTH);

        // TODO (@author fdietz): addressbookInterface doesn't exist anymore (use AddressbookController instead)

        /*
Folder folder =
        (Folder) MainInterface.addressbookInterface.treeModel.getFolder(uid);


setHeaderList(folder.getHeaderItemList());
*/
        return panel;
    }

    public void setHeaderList(IContactItemMap map) {
      

        addressbook.setHeaderItemList(new HeaderItemList(map));
    }

    public void actionPerformed(ActionEvent ev) {
        String action = ev.getActionCommand();

        /*
if (action.equals("CHOOSE"))
{
        SelectAddressbookFolderDialog dialog =
                MainInterface
                        .addressbookInterface
                        .tree
                        .getSelectAddressbookFolderDialog();

        Folder selectedFolder = dialog.getSelectedFolder();
        HeaderItemList list = selectedFolder.getHeaderItemList();
        setHeaderList(list);

        chooseButton.setText(selectedFolder.getName());
}
else if (action.equals("TO"))
{
        int[] array = addressbook.getSelectedIndices();
        ListModel model = addressbook.getModel();
        HeaderItem item;

        composerInterface.headerController.cleanupHeaderItemList();

        for (int j = 0; j < array.length; j++)
        {
                item = (HeaderItem) model.getElementAt(array[j]);
                HeaderItem item2 = (HeaderItem) item.clone();
                item2.add("field","To");

                try
                {
                        composerInterface.headerController.getAddressbookTableModel().addItem(item2);
                }
                catch ( Exception ex )
                {
                        ex.printStackTrace();
                }
        }
}
else if (action.equals("CC"))
{
        int[] array = addressbook.getSelectedIndices();
        ListModel model = addressbook.getModel();
        HeaderItem item;

        composerInterface.headerController.cleanupHeaderItemList();

        for (int j = 0; j < array.length; j++)
        {
                item = (HeaderItem) model.getElementAt(array[j]);

                HeaderItem item2 = (HeaderItem) item.clone();
                item2.add("field","Cc");

                try
                {
                        composerInterface.headerController.getAddressbookTableModel().addItem(item2);
                }
                catch ( Exception ex )
                {
                        ex.printStackTrace();
                }
        }
}
else if (action.equals("BCC"))
{
        int[] array = addressbook.getSelectedIndices();
        ListModel model = addressbook.getModel();
        HeaderItem item;


        composerInterface.headerController.cleanupHeaderItemList();

        for (int j = 0; j < array.length; j++)
        {
                item = (HeaderItem) model.getElementAt(array[j]);

                HeaderItem item2 = (HeaderItem) item.clone();
                item2.add("field","Bcc");

                try
                {
                        composerInterface.headerController.getAddressbookTableModel().addItem(item2);
                }
                catch ( Exception ex )
                {
                        ex.printStackTrace();
                }
        }
}
*/
    }

    public void stateChanged(ChangeEvent e) {
        int index = pane.getSelectedIndex();
        pane.setComponentAt(index, createPanel(books[index]));
    }
}