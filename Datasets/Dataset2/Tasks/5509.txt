import org.columba.core.resourceloader.ImageLoader;

// This program is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation; either version 2 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Library General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program; if not, write to the Free Software
// Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
package org.columba.mail.gui.config.accountlist;

import java.awt.Component;
import java.awt.Font;

import javax.swing.BorderFactory;
import javax.swing.ImageIcon;
import javax.swing.JLabel;
import javax.swing.JTable;
import javax.swing.UIManager;
import javax.swing.border.Border;
import javax.swing.table.TableCellRenderer;

import org.columba.core.gui.util.ImageLoader;


public class StringAccountRenderer extends JLabel implements TableCellRenderer {
    private Border unselectedBorder = null;
    private Border selectedBorder = null;
    private boolean isBordered = true;
    private Font plainFont;
    private Font boldFont;
    private ImageIcon image1 = ImageLoader.getSmallImageIcon("16_computer.png");
    private ImageIcon image2 = ImageLoader.getSmallImageIcon("stock_internet-16.png");
    private boolean b;

    public StringAccountRenderer(boolean b) {
        super();
        this.b = b;

        this.isBordered = true;

        setOpaque(true); //MUST do this for background to show up.

        boldFont = UIManager.getFont("Label.font");
        boldFont = boldFont.deriveFont(Font.BOLD);

        plainFont = UIManager.getFont("Label.font");
    }

    public Component getTableCellRendererComponent(JTable table, Object value,
        boolean isSelected, boolean hasFocus, int row, int column) {
        //super.getTableCellRendererComponent( table, value, isSelected, hasFocus, row, column );
        if (isBordered) {
            if (isSelected) {
                if (selectedBorder == null) {
                    selectedBorder = BorderFactory.createMatteBorder(2, 5, 2,
                            5, table.getSelectionBackground());
                }

                //setBorder(selectedBorder);
                setBackground(table.getSelectionBackground());
                setForeground(table.getSelectionForeground());
            } else {
                if (unselectedBorder == null) {
                    unselectedBorder = BorderFactory.createMatteBorder(2, 5, 2,
                            5, table.getBackground());
                }

                setBackground(table.getBackground());

                //setBorder(unselectedBorder);
                setForeground(table.getForeground());
            }
        }

        String str = null;

        try {
            str = (String) value;
        } catch (ClassCastException ex) {
            System.out.println(" filter renderer: " + ex.getMessage());
            str = "";
        }

        if (b == true) {
            if (str.equalsIgnoreCase("POP3")) {
                setIcon(image1);
            } else if (str.equalsIgnoreCase("IMAP4")) {
                setIcon(image2);
            }
        }

        setText(str);

        return this;
    }
}