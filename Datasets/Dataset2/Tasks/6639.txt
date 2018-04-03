label.setText(((Locale) value).getDisplayName((Locale)value));

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

package org.columba.core.gui.config;

import java.awt.Component;
import java.util.Locale;

import javax.swing.DefaultListCellRenderer;
import javax.swing.JLabel;
import javax.swing.JList;

/**
 * Renders locales.
 */
public class LocaleComboBoxRenderer extends DefaultListCellRenderer {
    public LocaleComboBoxRenderer() {}
    
    public Component getListCellRendererComponent(JList list,
        Object value, int index, boolean isSelected,
        boolean hasFocus) {
        
        JLabel label = (JLabel) super.getListCellRendererComponent(list,
                value, index, isSelected, hasFocus);
        label.setText(((Locale) value).getDisplayName());
        return label;
    }
}