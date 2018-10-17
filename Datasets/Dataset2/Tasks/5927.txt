import org.columba.core.resourceloader.ImageLoader;

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
package org.columba.addressbook.gui.table.renderer;

import java.awt.Component;

import javax.swing.ImageIcon;
import javax.swing.JTable;

import org.columba.core.gui.util.ImageLoader;


/**
 * Renderer for type column. Either displays a contact or a group icon.
 * 
 * @author fdietz
 */
public class TypeRenderer extends DefaultLabelRenderer {
    ImageIcon image1 = ImageLoader.getSmallImageIcon("contact_small.png");
    ImageIcon image2 = ImageLoader.getSmallImageIcon("group_small.png");

    /**
 *  
 */
    public TypeRenderer() {
        super();
    }

    /**
 * @see javax.swing.table.TableCellRenderer#getTableCellRendererComponent(javax.swing.JTable,
 *      java.lang.Object, boolean, boolean, int, int)
 */
    public Component getTableCellRendererComponent(JTable table, Object value,
        boolean isSelected, boolean hasFocus, int row, int column) {
        String str = (String) value;

        if (str.equalsIgnoreCase("contact")) {
            setIcon(image1);
        } else {
            setIcon(image2);
        }

        setText(null);

        return super.getTableCellRendererComponent(table, value, isSelected,
            hasFocus, row, column);
    }
}