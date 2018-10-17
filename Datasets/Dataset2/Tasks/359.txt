addItem(new ColorItem(Color.black, "None"));

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
package org.columba.core.gui.util;

import java.awt.Color;
import java.awt.event.ItemEvent;
import java.awt.event.ItemListener;

import javax.swing.ComboBoxModel;
import javax.swing.JColorChooser;
import javax.swing.JComboBox;

/**
 * A JComboBox that displays Colors.
 * @author redsolo
 */
public class ColorComboBox extends JComboBox implements ItemListener {

    private boolean codeSelectionUpdate = false;

    /**
     * Constructs a color combobo.x
     */
    public ColorComboBox() {
        super();

        // Add the default colors items.
        addItem(new ColorItem(Color.black, "Black"));
        addItem(new ColorItem(Color.blue, "Blue"));
        addItem(new ColorItem(Color.gray, "Gray"));
        addItem(new ColorItem(Color.green, "Green"));
        addItem(new ColorItem(Color.red, "Red"));
        addItem(new ColorItem(Color.yellow, "Yellow"));
        addItem(new ColorItem(Color.black, "Custom"));

        setRenderer(new ColorItemRenderer());

        addItemListener(this);
    }

    /**
     * Selects the combobox item with the specified color name.
     * @param name the name of the color to select.
     */
    public void setSelectedColor(String name) {
        codeSelectionUpdate = true;
        ComboBoxModel model = getModel();
        if (name == null) {
            setSelectedIndex(0);
        } else {
            for (int i = 0; i < model.getSize(); i++) {
                ColorItem object = (ColorItem) model.getElementAt(i);

                if (object.getName().equalsIgnoreCase(name)) {
                    setSelectedIndex(i);

                    break;
                }
            }
        }
        codeSelectionUpdate = false;
    }

    /**
     * Sets the color for the Custom color item.
     * @param color the new color for the Custom color.
     */
    public void setCustomColor(Color color) {
        ColorItem item = (ColorItem) getModel().getElementAt(getModel().getSize() - 1);
        item.setColor(color);
        repaint();
    }

    /**
     * Sets the color for the Custom color item.
     * @param rgb the new color, in rgb value, for the Custom color.
     */
    public void setCustomColor(int rgb) {
        setCustomColor(ColorFactory.getColor(rgb));
    }

    /**
     * Returns the selected coloritem.
     * @return the selected coloritem.
     */
    public ColorItem getSelectedColorItem() {
        return (ColorItem) getSelectedItem();
    }

    /** {@inheritDoc} */
    public void itemStateChanged(ItemEvent e) {

        if ((!codeSelectionUpdate) && (e.getStateChange() == ItemEvent.SELECTED)) {
            ColorItem item = (ColorItem) getSelectedItem();

            if (item.getName().equalsIgnoreCase("custom")) {
                Color newColor = JColorChooser.showDialog(null,
                        "Choose Background Color", item.getColor());

                item.setColor(newColor);
                repaint();
            }
        }
    }
}