import org.columba.core.resourceloader.ImageLoader;

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

package org.columba.mail.gui.composer.util;

import java.awt.GridBagConstraints;

import javax.swing.BorderFactory;
import javax.swing.Box;
import javax.swing.ImageIcon;
import javax.swing.JLabel;
import javax.swing.UIManager;

import org.columba.core.gui.frame.ContainerInfoPanel;
import org.columba.core.gui.util.ImageLoader;
import org.columba.mail.config.AccountItem;
import org.columba.ristretto.message.Address;

public class IdentityInfoPanel extends ContainerInfoPanel {
    private JLabel label;
    private ImageIcon image1;
    private ImageIcon image2;

    public IdentityInfoPanel() {
        super();
    }

    public void initComponents() {
        super.initComponents();

        image1 = ImageLoader.getSmallImageIcon("16_computer.png");
        image2 = ImageLoader.getSmallImageIcon("stock_internet-16.png");

        gridbagConstraints.gridwidth = GridBagConstraints.RELATIVE;
        gridbagConstraints.gridx = 0;
        gridbagConstraints.weightx = 0.5;

        Box box = Box.createHorizontalBox();
        gridbagLayout.setConstraints(box, gridbagConstraints);
        panel.add(box);

        label = new JLabel("Identity");
        label.setForeground(UIManager.getColor("List.selectionForeground"));
        label.setBorder(BorderFactory.createEmptyBorder(2, 2, 2, 2));
        label.setFont(font);
        label.setIconTextGap(10);
        label.setIcon(image1);

        gridbagConstraints.gridwidth = GridBagConstraints.REMAINDER;
        gridbagConstraints.gridx = 1;

        //gridbagConstraints.insets = new Insets(0, 0, 0, 20);
        gridbagConstraints.anchor = GridBagConstraints.EAST;
        gridbagLayout.setConstraints(label, gridbagConstraints);

        panel.add(label);
    }

    public void resetRenderer() {
        initComponents();
    }

    public void set(AccountItem item) {
        String accountName = item.getName();
        Address identity = item.getIdentity().getAddress();

        if (item.isPopAccount()) {
            label.setIcon(image1);
        } else {
            label.setIcon(image2);
        }

        label.setText(accountName + ":    " + identity.toString());

        revalidate();
        repaint();
    }
}