import org.columba.core.gui.base.ButtonWithMnemonic;

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
package org.columba.addressbook.gui.dialog.contact;

import java.awt.BorderLayout;
import java.awt.GridLayout;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.KeyEvent;

import javax.swing.BorderFactory;
import javax.swing.JButton;
import javax.swing.JComponent;
import javax.swing.JDialog;
import javax.swing.JFrame;
import javax.swing.JPanel;
import javax.swing.JTabbedPane;
import javax.swing.KeyStroke;
import javax.swing.SwingConstants;

import net.javaprog.ui.wizard.plaf.basic.SingleSideEtchedBorder;

import org.columba.addressbook.model.IContact;
import org.columba.addressbook.util.AddressbookResourceLoader;
import org.columba.core.gui.util.ButtonWithMnemonic;

import com.jgoodies.forms.layout.CellConstraints;
import com.jgoodies.forms.layout.FormLayout;

/**
 * A dialog for editing a contact's data.
 */
public class ContactDialog extends JDialog implements ActionListener {
    private JTabbedPane centerPane;
    private IdentityPanel identityPanel;
    //private AddressPanel addressPanel;
    private JButton okButton;
    private boolean result = false;
    
    private IContact contact;
    
    public ContactDialog(JFrame frame, IContact contact) {
        super(frame, true);
        this.contact = contact;

        //LOCALIZE
        setTitle(AddressbookResourceLoader.getString("dialog", "contact",
                "add_contact")); //$NON-NLS-1$
        initComponents();
        updateComponents(true);
        
        pack();
        setLocationRelativeTo(null);
        setVisible(true);
    }

    public void updateComponents(boolean b) {
        identityPanel.updateComponents(b);
        //addressPanel.updateComponents(b);
    }

    protected void initComponents() {
        JPanel contentPane = new JPanel(new BorderLayout(0, 0));
        identityPanel = new IdentityPanel(contact);
        identityPanel.dialog = new FullNameDialog(this, identityPanel, contact);

        //LOCALIZE
        //centerPane.add(identityPanel, AddressbookResourceLoader.getString("dialog", "contact", "identity")); //$NON-NLS-1$
        //addressPanel = new AddressPanel();

        //LOCALIZE
        //centerPane.add(addressPanel, "Address & Phone");
        //contentPane.add(identityPanel, BorderLayout.CENTER);
        JPanel bottomPanel = new JPanel(new BorderLayout());
        bottomPanel.setBorder(new SingleSideEtchedBorder(SwingConstants.TOP));

        JPanel buttonPanel = new JPanel(new GridLayout(1, 2, 5, 0));
        buttonPanel.setBorder(BorderFactory.createEmptyBorder(12, 12, 12, 12));
        okButton = new ButtonWithMnemonic(AddressbookResourceLoader.getString(
                    "global", "ok"));
        okButton.setActionCommand("OK");
        okButton.addActionListener(this);
        buttonPanel.add(okButton);
        bottomPanel.add(buttonPanel, BorderLayout.EAST);

        setContentPane(contentPane);

        FormLayout layout = new FormLayout("fill:default:grow",
                "fill:default:grow, default");

        contentPane.setLayout(layout);

        CellConstraints cc = new CellConstraints();
        contentPane.add(identityPanel, cc.xy(1, 1));
        contentPane.add(bottomPanel, cc.xy(1, 2));

        getRootPane().setDefaultButton(okButton);

        JButton cancelButton = new ButtonWithMnemonic(
            AddressbookResourceLoader.getString("global", "cancel"));
        cancelButton.setActionCommand("CANCEL");
        cancelButton.addActionListener(this);
        buttonPanel.add(cancelButton);
        getRootPane().registerKeyboardAction(this, "CANCEL",
            KeyStroke.getKeyStroke(KeyEvent.VK_ESCAPE, 0),
            JComponent.WHEN_IN_FOCUSED_WINDOW);
    }

    public void actionPerformed(ActionEvent event) {
        String action = event.getActionCommand();
        if (action.equals("OK")) {
            result = true;
            updateComponents(false);
        }
        setVisible(false);
    }

    public boolean getResult() {
        return result;
    }
}