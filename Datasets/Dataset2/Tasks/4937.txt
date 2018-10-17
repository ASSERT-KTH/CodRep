label.setText(item.toString());

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

package org.columba.core.gui.checkabletree;

import java.awt.Color;
import java.awt.Component;
import java.awt.Dimension;
import java.awt.Graphics;

import javax.swing.Icon;
import javax.swing.JCheckBox;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JTree;
import javax.swing.UIManager;
import javax.swing.plaf.ColorUIResource;
import javax.swing.tree.TreeCellRenderer;

/**
 * @author frd
 *
 * To change the template for this generated type comment go to
 * Window - Preferences - Java - Code Generation - Code and Comments
 */
public class CheckRenderer extends JPanel implements TreeCellRenderer {
    private JCheckBox check;
    private TreeLabel label;

    public CheckRenderer() {
        setLayout(null);

        check = new JCheckBox();

        add(check);
        add(label = new TreeLabel());

        check.setBackground(UIManager.getColor("Tree.textBackground"));
        label.setForeground(UIManager.getColor("Tree.textForeground"));
    }

    public Component getTreeCellRendererComponent(JTree tree, Object value,
        boolean isSelected, boolean expanded, boolean leaf, int row,
        boolean hasFocus) {

        CheckableItem item = (CheckableItem) value;
       
        check.setSelected(item.isSelected());
        
        label.setFont(tree.getFont());
        
        label.setText(item.getName());

        label.setSelected(isSelected);
        label.setFocus(hasFocus);

        //FolderTreeNode node = (FolderTreeNode) value;

        label.setIcon(item.getIcon());

        
            check.setSelected(item.isSelected());
       

        //check.setText(node.getName());
        return this;
    }

    public Dimension getPreferredSize() {
        Dimension d_check = check.getPreferredSize();
        Dimension d_label = label.getPreferredSize();

        return new Dimension(d_check.width + d_label.width,
            Math.max(d_check.height, d_label.height));
    }

    public void doLayout() {
        Dimension d_check = check.getPreferredSize();
        Dimension d_label = label.getPreferredSize();
        int y_check = 0;
        int y_label = 0;

        if (d_check.height < d_label.height) {
            y_check = (d_label.height - d_check.height) / 2;
        } else {
            y_label = (d_check.height - d_label.height) / 2;
        }

        check.setLocation(0, y_check);
        check.setBounds(0, y_check, d_check.width, d_check.height);
        label.setLocation(d_check.width, y_label);
        label.setBounds(d_check.width, y_label, d_label.width, d_label.height);
    }

    public void setBackground(Color color) {
        if (color instanceof ColorUIResource) {
            color = null;
        }

        super.setBackground(color);
    }

    public class TreeLabel extends JLabel {
        boolean isSelected;
        boolean hasFocus;

        public TreeLabel() {
        }

        public void setBackground(Color color) {
            if (color instanceof ColorUIResource) {
                color = null;
            }

            super.setBackground(color);
        }

        public void paint(Graphics g) {
            String str;

            if ((str = getText()) != null) {
                if (0 < str.length()) {
                    if (isSelected) {
                        g.setColor(UIManager.getColor(
                                "Tree.selectionBackground"));
                    } else {
                        g.setColor(UIManager.getColor("Tree.textBackground"));
                    }

                    Dimension d = getPreferredSize();
                    int imageOffset = 0;
                    Icon currentI = getIcon();

                    if (currentI != null) {
                        imageOffset = currentI.getIconWidth() +
                            Math.max(0, getIconTextGap() - 1);
                    }

                    g.fillRect(imageOffset, 0, d.width - 1 - imageOffset,
                        d.height);

                    if (hasFocus) {
                        g.setColor(UIManager.getColor(
                                "Tree.selectionBorderColor"));
                        g.drawRect(imageOffset, 0, d.width - 1 - imageOffset,
                            d.height - 1);
                    }
                }
            }

            super.paint(g);
        }

        public Dimension getPreferredSize() {
            Dimension retDimension = super.getPreferredSize();

            if (retDimension != null) {
                retDimension = new Dimension(retDimension.width + 3,
                        retDimension.height);
            }

            return retDimension;
        }

        public void setSelected(boolean isSelected) {
            this.isSelected = isSelected;
        }

        public void setFocus(boolean hasFocus) {
            this.hasFocus = hasFocus;
        }
    }
}