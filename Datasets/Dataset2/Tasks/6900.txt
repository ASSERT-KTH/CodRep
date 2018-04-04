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
package org.columba.mail.gui.config.template;

import java.awt.BorderLayout;
import java.awt.Dimension;
import java.awt.GridLayout;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.KeyEvent;
import java.util.Enumeration;
import java.util.Vector;

import javax.swing.BorderFactory;
import javax.swing.JButton;
import javax.swing.JComponent;
import javax.swing.JDialog;
import javax.swing.JFrame;
import javax.swing.JList;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.KeyStroke;
import javax.swing.SwingConstants;
import javax.swing.event.ListSelectionEvent;
import javax.swing.event.ListSelectionListener;

import net.javaprog.ui.wizard.plaf.basic.SingleSideEtchedBorder;

import org.columba.core.gui.util.ButtonWithMnemonic;
import org.columba.core.help.HelpManager;
import org.columba.mail.message.IHeaderList;
import org.columba.mail.util.MailResourceLoader;


/**
 * Asks the user to choose a template from a list.
 *
 * @author fdietz
 */
public class ChooseTemplateDialog extends JDialog implements ActionListener,
    ListSelectionListener {
    boolean result;
    JList list;
    Object uid;
    IHeaderList headerList;
    JButton okButton;

    public ChooseTemplateDialog(JFrame parent, IHeaderList list) {
        super(parent, true);

        this.headerList = list;

        initComponents();

        updateComponents(true);

        pack();
        setLocationRelativeTo(null);
        setVisible(true);
    }

    protected JPanel createButtonPanel() {
        JPanel bottom = new JPanel();
        bottom.setLayout(new BorderLayout());
        bottom.setBorder(new SingleSideEtchedBorder(SwingConstants.TOP));

        //bottom.setLayout( new BoxLayout( bottom, BoxLayout.X_AXIS ) );
        //bottom.add( Box.createHorizontalStrut());
        ButtonWithMnemonic cancelButton = new ButtonWithMnemonic(MailResourceLoader.getString(
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
        okButton.setEnabled(false);
        getRootPane().setDefaultButton(okButton);

        ButtonWithMnemonic helpButton = new ButtonWithMnemonic(MailResourceLoader.getString(
                    "global", "help"));

        // associate with JavaHelp
        HelpManager.getInstance().enableHelpOnButton(helpButton,
            "template_dialog");
        HelpManager.getInstance().enableHelpKey(getRootPane(),
            "template_dialog");

        JPanel buttonPanel = new JPanel();
        buttonPanel.setBorder(BorderFactory.createEmptyBorder(12, 12, 12, 12));
        buttonPanel.setLayout(new GridLayout(1, 3, 6, 0));
        buttonPanel.add(okButton);
        buttonPanel.add(cancelButton);
        buttonPanel.add(helpButton);

        //bottom.add( Box.createHorizontalGlue() );
        bottom.add(buttonPanel, BorderLayout.EAST);

        return bottom;
    }

    protected void initComponents() {
        // pack all UIDs in a list
        Vector v = new Vector();
        Enumeration enumeration = headerList.keys();

        while (enumeration.hasMoreElements()) {
            v.add(enumeration.nextElement());
        }

        list = new JList(v);
        list.addListSelectionListener(this);
        list.setPreferredSize(new Dimension(200, 300));
        list.setCellRenderer(new HeaderCellRenderer(headerList));

        JPanel panel = new JPanel();
        panel.setBorder(BorderFactory.createEmptyBorder(12, 12, 12, 12));
        panel.setLayout(new BorderLayout());

        JScrollPane scrollPane = new JScrollPane(list);
        panel.add(scrollPane, BorderLayout.CENTER);

        getContentPane().setLayout(new BorderLayout());

        getContentPane().add(panel, BorderLayout.CENTER);

        getContentPane().add(createButtonPanel(), BorderLayout.SOUTH);
        getRootPane().registerKeyboardAction(this, "CANCEL",
            KeyStroke.getKeyStroke(KeyEvent.VK_ESCAPE, 0),
            JComponent.WHEN_IN_FOCUSED_WINDOW);
    }

    protected void updateComponents(boolean b) {
        if (b) {
            // model -> view
        } else {
            // view -> model
        }
    }

    public void actionPerformed(ActionEvent arg0) {
        String action = arg0.getActionCommand();

        if (action.equals("CANCEL")) {
            result = false;
            setVisible(false);
        } else if (action.equals("OK")) {
            result = true;
            uid = list.getSelectedValue();
            setVisible(false);
        }
    }

    /**
 * @return
 */
    public boolean isResult() {
        return result;
    }

    /**
 * @return
 */
    public Object getUid() {
        return uid;
    }

    /* (non-Javadoc)
 * @see javax.swing.event.ListSelectionListener#valueChanged(javax.swing.event.ListSelectionEvent)
 */
    public void valueChanged(ListSelectionEvent ev) {
        Object selection = list.getSelectedValue();

        if (selection != null) {
            okButton.setEnabled(true);
        } else {
            okButton.setEnabled(false);
        }
    }
}