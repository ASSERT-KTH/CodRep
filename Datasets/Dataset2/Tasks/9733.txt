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
//All Rights Reserved. Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

package org.columba.mail.gui.composer;

import java.awt.Component;

import javax.swing.ImageIcon;
import javax.swing.JComboBox;
import javax.swing.JLabel;
import javax.swing.JList;
import javax.swing.ListCellRenderer;

import org.columba.core.gui.util.ImageLoader;
import org.columba.mail.config.AccountItem;
import org.columba.ristretto.message.Address;

/**
 * @author frd
 *
 * To change this generated comment edit the template variable "typecomment":
 * Window>Preferences>Java>Templates.
 * To enable and disable the creation of type comments go to
 * Window>Preferences>Java>Code Generation.
 */
public class AccountView extends JComboBox {
    AccountController controller;

    public AccountView(AccountController controller) {
        super();
        this.controller = controller;

        setRenderer(new AccountListRenderer());
    }
}


class AccountListRenderer extends JLabel implements ListCellRenderer {
    protected ImageIcon image1;
    protected ImageIcon image2;

    public AccountListRenderer() {
        setOpaque(true);
        image1 = ImageLoader.getSmallImageIcon("16_computer.png");
        image2 = ImageLoader.getSmallImageIcon("stock_internet-16.png");
    }

    public Component getListCellRendererComponent(JList list, Object value,
        int index, boolean isSelected, boolean cellHasFocus) {
        if (isSelected) {
            setBackground(list.getSelectionBackground());
            setForeground(list.getSelectionForeground());
        } else {
            setBackground(list.getBackground());
            setForeground(list.getForeground());
        }

        if (value != null) {
            AccountItem item = (AccountItem) value;
            String accountName = item.getName();
            Address identity = item.getIdentity().getAddress();

            setText(accountName + ":   " + identity.toString());
            //setText(accountName);
            
            if (item.isPopAccount()) {
                setIcon(image1);
            } else {
                setIcon(image2);
            }
        }

        return this;
    }
}