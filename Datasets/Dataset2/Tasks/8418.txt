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
import javax.swing.SwingConstants;

import org.columba.core.gui.util.ImageLoader;
import org.columba.mail.gui.table.model.MessageNode;
import org.columba.mail.util.MailResourceLoader;


public class AttachmentRenderer extends DefaultLabelRenderer {
    boolean bool;
    ImageIcon image1;

    public AttachmentRenderer() {
        super();

        setHorizontalAlignment(SwingConstants.CENTER);

        image1 = ImageLoader.getSmallImageIcon("attachment.png");
    }

    public Component getTableCellRendererComponent(JTable table, Object value,
        boolean isSelected, boolean hasFocus, int row, int column) {
        super.getTableCellRendererComponent(table, value, isSelected, hasFocus,
            row, column);

        if (value == null) {
            setIcon(null);

            return this;
        }

        setText("");
        
        boolean hasAttachment = ((Boolean) ((MessageNode) value).getHeader()
                                            .get("columba.attachment")).booleanValue();

        if (hasAttachment) {
            setIcon(image1);

            setToolTipText(MailResourceLoader.getString("header", "column",
                    "attachment"));
        } else {
            setIcon(null);
        }

        return this;
    }
}