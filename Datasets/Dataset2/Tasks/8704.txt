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
package org.columba.mail.gui.table.plugins;

import java.awt.Component;

import javax.swing.ImageIcon;
import javax.swing.JTable;

import org.columba.core.gui.util.ImageLoader;
import org.columba.mail.gui.table.model.MessageNode;
import org.columba.mail.util.MailResourceLoader;


public class PriorityRenderer extends DefaultLabelRenderer {
    private ImageIcon image1 = ImageLoader.getSmallImageIcon(
            "priority-high.png");
    private ImageIcon image2 = null;
    private ImageIcon image3 = null;
    private ImageIcon image4 = ImageLoader.getSmallImageIcon("priority-low.png");

    public PriorityRenderer() {
        super();
    }

    public Component getTableCellRendererComponent(JTable table, Object value,
        boolean isSelected, boolean hasFocus, int row, int column) {
        super.getTableCellRendererComponent(table, value, isSelected, hasFocus,
            row, column);

        if (value == null) {
            setText("");

            return this;
        }

        setText("");
        
        Integer priority = (Integer) ((MessageNode) value).getHeader().get("columba.priority");

        Integer in = priority;

        if (in == null) {
            return this;
        }

        int i = in.intValue();

        if (i == 1) {
            //setForeground( Color.red );
            //setText("!!");
            setIcon(image1);

            setToolTipText(MailResourceLoader.getString("header", "column",
                    "priority_highest"));
        } else if (i == 2) {
            //setForeground( Color.red );
            setIcon(image2);
            setToolTipText(MailResourceLoader.getString("header", "column",
                    "priority_high"));

            //setText("!");
        } else if (i == 3) {
            setIcon(null);
        } else if (i == 4) {
            //eteTextForeground( Color.blue );
            setIcon(image3);
            setToolTipText(MailResourceLoader.getString("header", "column",
                    "priority_low"));

            //setText("!");
        } else if (i == 5) {
            //setForeground( Color.blue );
            setIcon(image4);
            setToolTipText(MailResourceLoader.getString("header", "column",
                    "priority_lowest"));

            //setText("!!");
        }

        return this;
    }
}