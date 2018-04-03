super((JFrame) mediator.getView().getFrame(), true);

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
package org.columba.mail.gui.config.columns;

import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.Component;
import java.awt.Dimension;
import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.GridLayout;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.KeyEvent;

import javax.swing.BorderFactory;
import javax.swing.Box;
import javax.swing.BoxLayout;
import javax.swing.DefaultListSelectionModel;
import javax.swing.JButton;
import javax.swing.JComponent;
import javax.swing.JDialog;
import javax.swing.JFrame;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.KeyStroke;
import javax.swing.SwingConstants;
import javax.swing.event.ListSelectionEvent;
import javax.swing.event.ListSelectionListener;

import net.javaprog.ui.wizard.plaf.basic.SingleSideEtchedBorder;

import org.columba.core.gui.util.ButtonWithMnemonic;
import org.columba.core.help.HelpManager;
import org.columba.core.xml.XmlElement;
import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.folder.MessageFolder;
import org.columba.mail.folderoptions.ColumnOptionsPlugin;
import org.columba.mail.gui.frame.MailFrameMediator;
import org.columba.mail.util.MailResourceLoader;
import org.frapuccino.checkablelist.CheckableItemImpl;
import org.frapuccino.checkablelist.CheckableItemListTableModel;
import org.frapuccino.checkablelist.CheckableList;


/**
 * Configurabe visible columns of the table.
 * <p>
 * TODO: adding of columns is not working currently
 * 
 * @author fdietz
 */
public class ColumnConfigDialog extends JDialog implements ActionListener,
    ListSelectionListener {
   
    private JButton showButton;
    private JButton hideButton;
    private CheckableList list;
    private int index;
    private XmlElement columns;
    private CheckableItemImpl selection;
    private MailFrameMediator mediator;

    public ColumnConfigDialog(MailFrameMediator mediator, XmlElement columns) {
        super((JFrame) mediator.getView(), true);
        setTitle("Configure Columns");

        this.mediator = mediator;
        this.columns = columns;

        list = new CheckableList();

        list.getSelectionModel().addListSelectionListener(this);

        initComponents();

        updateComponents(true);

        getRootPane().registerKeyboardAction(this, "CLOSE",
            KeyStroke.getKeyStroke(KeyEvent.VK_ESCAPE, 0),
            JComponent.WHEN_IN_FOCUSED_WINDOW);
        pack();
        setLocationRelativeTo(null);
        setVisible(true);
    }

    protected JPanel createButtonPanel() {
        JPanel bottom = new JPanel();
        bottom.setLayout(new BorderLayout());

        bottom.setBorder(BorderFactory.createEmptyBorder(12, 12, 12, 12));

        ButtonWithMnemonic cancelButton = new ButtonWithMnemonic(MailResourceLoader.getString(
                    "global", "cancel"));

        //$NON-NLS-1$ //$NON-NLS-2$
        cancelButton.addActionListener(this);
        cancelButton.setActionCommand("CANCEL"); //$NON-NLS-1$

        ButtonWithMnemonic okButton = new ButtonWithMnemonic(MailResourceLoader.getString(
                    "global", "ok"));

        //$NON-NLS-1$ //$NON-NLS-2$
        okButton.addActionListener(this);
        okButton.setActionCommand("OK"); //$NON-NLS-1$
        okButton.setDefaultCapable(true);
        getRootPane().setDefaultButton(okButton);

        ButtonWithMnemonic helpButton = new ButtonWithMnemonic(MailResourceLoader.getString(
                    "global", "help"));

        // associate with JavaHelp
        HelpManager.getHelpManager().enableHelpOnButton(helpButton,
            "configuring_columba");
        HelpManager.getHelpManager().enableHelpKey(getRootPane(),
            "configuring_columba");

        JPanel buttonPanel = new JPanel();
        buttonPanel.setLayout(new GridLayout(1, 3, 6, 0));
        buttonPanel.add(okButton);
        buttonPanel.add(cancelButton);
        buttonPanel.add(helpButton);

        bottom.add(buttonPanel, BorderLayout.EAST);

        return bottom;
    }

    public void initComponents() {
        getContentPane().setLayout(new BorderLayout());

        JPanel mainPanel = new JPanel();
        mainPanel.setLayout(new BorderLayout(5, 0));
        mainPanel.setBorder(BorderFactory.createEmptyBorder(12, 12, 12, 12));

        showButton = new ButtonWithMnemonic("&Show");

        showButton.setActionCommand("SHOW");
        showButton.addActionListener(this);
        showButton.setEnabled(false);

        hideButton = new ButtonWithMnemonic("&Hide");

        hideButton.setActionCommand("HIDE");
        hideButton.setEnabled(false);
        hideButton.addActionListener(this);

        // top panel
        JPanel topPanel = new JPanel();
        topPanel.setLayout(new BoxLayout(topPanel, BoxLayout.X_AXIS));

        GridBagLayout gridBagLayout = new GridBagLayout();
        GridBagConstraints c = new GridBagConstraints();

        JPanel topBorderPanel = new JPanel();
        topBorderPanel.setLayout(new BorderLayout());
        topBorderPanel.setBorder(BorderFactory.createEmptyBorder(0, 0, 5, 0));
        topBorderPanel.add(topPanel, BorderLayout.CENTER);

        Component glue = Box.createVerticalGlue();
        c.anchor = GridBagConstraints.EAST;
        c.gridwidth = GridBagConstraints.REMAINDER;

        gridBagLayout.setConstraints(glue, c);

        gridBagLayout = new GridBagLayout();
        c = new GridBagConstraints();

        JPanel eastPanel = new JPanel(gridBagLayout);
        mainPanel.add(eastPanel, BorderLayout.EAST);

        c.fill = GridBagConstraints.HORIZONTAL;
        c.weightx = 1.0;
        c.gridwidth = GridBagConstraints.REMAINDER;
        gridBagLayout.setConstraints(showButton, c);
        eastPanel.add(showButton);

        Component strut1 = Box.createRigidArea(new Dimension(30, 5));
        gridBagLayout.setConstraints(strut1, c);
        eastPanel.add(strut1);

        gridBagLayout.setConstraints(hideButton, c);
        eastPanel.add(hideButton);

        Component strut = Box.createRigidArea(new Dimension(30, 5));
        gridBagLayout.setConstraints(strut, c);
        eastPanel.add(strut);

        glue = Box.createVerticalGlue();
        c.fill = GridBagConstraints.BOTH;
        c.weighty = 1.0;
        gridBagLayout.setConstraints(glue, c);
        eastPanel.add(glue);

        JScrollPane scrollPane = new JScrollPane(list);
        scrollPane.setPreferredSize(new Dimension(200, 200));
        scrollPane.getViewport().setBackground(Color.white);
        mainPanel.add(scrollPane, BorderLayout.CENTER);
        getContentPane().add(mainPanel);

        JPanel bottomPanel = new JPanel(new BorderLayout());
        bottomPanel.setBorder(new SingleSideEtchedBorder(SwingConstants.TOP));

        JPanel buttonPanel = createButtonPanel();

        bottomPanel.add(buttonPanel, BorderLayout.EAST);
        getContentPane().add(bottomPanel, BorderLayout.SOUTH);
    }

    private XmlElement findColumn(XmlElement parent, String name) {
        for (int i = 0; i < parent.count(); i++) {
            XmlElement child = parent.getElement(i);

            if (child.getAttribute("name").equals(name)) {
                return child;
            }
        }

        return null;
    }

    public void updateComponents(boolean b) {
        if (b) {
            CheckableItemListTableModel model = new CheckableItemListTableModel();
            String[] stringList = ColumnOptionsPlugin.getColumns();

            for (int j = 0; j < stringList.length; j++) {
                String c = stringList[j];
                CheckableItemImpl item = new CheckableItemImpl(c);
                XmlElement element = findColumn(columns, c);

                if (element != null) {
                    item.setSelected(true);
                } else {
                    item.setSelected(false);
                }

                model.addElement(item);
            }

            list.setModel(model);
        } else {
            CheckableItemListTableModel model = ((CheckableItemListTableModel) list.getModel());

            for (int i = 0; i < model.count(); i++) {
                // get column of list
                CheckableItemImpl column = (CheckableItemImpl) model.getElement(i);

                // find colum
                XmlElement element = findColumn(columns, column.toString());

                if (element != null) {
                    // remove disabled column
                    if (!column.isSelected()) {
                        element.removeFromParent();
                    }
                } else {
                    if (column.isSelected()) {
                        XmlElement newElement = new XmlElement("column");
                        newElement.addAttribute("name", column.toString());
                        newElement.addAttribute("width", "100");
                        columns.addElement(newElement);
                    }
                }
            }
        }
    }

    public void valueChanged(ListSelectionEvent e) {
        if (e.getValueIsAdjusting()) {
            return;
        }

        DefaultListSelectionModel theList = (DefaultListSelectionModel) e.getSource();

        if (!theList.isSelectionEmpty()) {
            index = theList.getAnchorSelectionIndex();

            selection = (CheckableItemImpl) ((CheckableItemListTableModel) list.getModel()).getElement(index);

            updateButtonState();
        }
    }

    private void updateButtonState() {
        if (selection.isSelected()) {
            hideButton.setEnabled(true);
            showButton.setEnabled(false);
        } else {
            showButton.setEnabled(true);
            hideButton.setEnabled(false);
        }
    }

    public void actionPerformed(ActionEvent e) {
        String action = e.getActionCommand();

        if (action.equals("OK")) {
            updateComponents(false);

            setVisible(false);

            ColumnOptionsPlugin plugin = (ColumnOptionsPlugin) mediator.getFolderOptionsController()
                                                                       .getPlugin("ColumnOptions");

            // make sure this configuration is also visually working immediately
            FolderCommandReference[] r = mediator.getTreeSelection();
            plugin.loadOptionsFromXml((MessageFolder) r[0].getFolder());
        } else if (action.equals("CANCEL")) {
            setVisible(false);
        } else if (action.equals("SHOW")) {
            if (selection != null) {
                selection.setSelected(!selection.isSelected());
                ((CheckableItemListTableModel) list.getModel()).updateRow(selection);

                //list.repaint();
                updateButtonState();
            }
        } else if (action.equals("HIDE")) {
            // disable selected item
            if (selection != null) {
                selection.setSelected(!selection.isSelected());
                ((CheckableItemListTableModel) list.getModel()).updateRow(selection);

                //list.repaint();
                updateButtonState();
            }
        }
    }
}