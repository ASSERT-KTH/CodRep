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
package org.columba.mail.gui.composer;

import java.awt.Component;

import javax.swing.BorderFactory;
import javax.swing.ImageIcon;
import javax.swing.JComboBox;
import javax.swing.JLabel;
import javax.swing.JList;
import javax.swing.ListCellRenderer;

import org.columba.core.gui.util.ImageLoader;
import org.columba.mail.util.MailResourceLoader;


/**
 * @author frd
 *
 * To change this generated comment edit the template variable "typecomment":
 * Window>Preferences>Java>Templates.
 * To enable and disable the creation of type comments go to
 * Window>Preferences>Java>Code Generation.
 */
public class PriorityView extends JComboBox {
    private static final String[] priorities = {
        MailResourceLoader.getString("dialog", "composer", "highest"),
        MailResourceLoader.getString("dialog", "composer", "high"),
        MailResourceLoader.getString("dialog", "composer", "normal"),
        MailResourceLoader.getString("dialog", "composer", "low"),
        MailResourceLoader.getString("dialog", "composer", "lowest")
    }; //$NON-NLS-1$ //$NON-NLS-2$ //$NON-NLS-3$ //$NON-NLS-4$ //$NON-NLS-5$
    PriorityController controller;

    public PriorityView(PriorityController controller) {
        super(priorities);
        this.controller = controller;

        setRenderer(new ComboBoxRenderer());

        setSelectedIndex(2);
    }

    public void installListener(PriorityController controller) {
        addItemListener(controller);
    }

    class ComboBoxRenderer extends JLabel implements ListCellRenderer {
        private ImageIcon image1 = ImageLoader.getSmallImageIcon(
                "priority-high.png");

        //private ImageIcon image2 = null;
        //private ImageIcon image3 = null;
        private ImageIcon image4 = ImageLoader.getSmallImageIcon(
                "priority-low.png");

        public ComboBoxRenderer() {
            setOpaque(true);
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

            String p = (String) value;

            if (p == null) {
                return this;
            }

            if (p.equals("Highest")) {
                setIcon(image1);
            }
            /*
else if ( p.equals("High") )
  setIcon( image2 );
*/
            /*
else if ( p.equals("Low") )
    setIcon( image3 );
 */
            else if (p.equals("Lowest")) {
                setIcon(image4);
            } else {
                setIcon(null);
            }

            if (getIcon() == null) {
                setBorder(BorderFactory.createEmptyBorder(0,
                        image1.getIconWidth() + getIconTextGap(), 0, 0));
            } else {
                setBorder(BorderFactory.createEmptyBorder(0, 0, 0, 0));
            }

            setText((String) value);

            return this;
        }
    }
}