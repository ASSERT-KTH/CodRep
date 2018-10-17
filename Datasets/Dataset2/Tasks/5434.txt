Boolean bool = (Boolean) header.get("columba.spam");

// The contents of this file are subject to the Mozilla Public License Version
// 1.1
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
//The Initial Developers of the Original Code are Frederik Dietz and Timo
// Stich.
//Portions created by Frederik Dietz and Timo Stich are Copyright (C) 2003.
//
//All Rights Reserved.
package org.columba.mail.gui.table.plugins;

import java.awt.Component;

import javax.swing.ImageIcon;
import javax.swing.JTable;
import javax.swing.SwingConstants;

import org.columba.mail.gui.table.model.MessageNode;
import org.columba.mail.message.ColumbaHeader;
import org.columba.mail.resourceloader.MailImageLoader;
import org.columba.mail.util.MailResourceLoader;


public class SpamRenderer extends DefaultLabelRenderer {
    ImageIcon image;

    public SpamRenderer() {
        super();

        setHorizontalAlignment(SwingConstants.RIGHT);
        image = MailImageLoader.getSmallIcon("mail-mark-junk.png");
    }

    public void updateUI() {
        super.updateUI();
    }

    public Component getTableCellRendererComponent(JTable table, Object value,
        boolean isSelected, boolean hasFocus, int row, int column) {
    	
    	super.getTableCellRendererComponent(table, value, isSelected,
                hasFocus, row, column);
    	
        if (value == null) {
            setText("");

            return this;
        }

        setText("");
        
        ColumbaHeader header = (ColumbaHeader) ((MessageNode) value).getHeader();

        setIcon(null);
        setToolTipText(MailResourceLoader.getString("header", "column", "nospam"));

        Boolean bool = (Boolean) header.getAttributes().get("columba.spam");

        if (bool != null) {
            if (bool.equals(Boolean.TRUE)) {
                setIcon(image);
                setToolTipText(MailResourceLoader.getString("header", "column",
                        "spam"));
            } else {
                setIcon(null);
            }
        }

        return this;
    }
}