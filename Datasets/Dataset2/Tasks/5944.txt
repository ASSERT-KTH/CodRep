import org.columba.addressbook.model.BasicModelPartial;

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
package org.columba.addressbook.gui.autocomplete;

import java.awt.event.ItemEvent;
import java.awt.event.ItemListener;
import java.awt.event.KeyEvent;
import java.awt.event.KeyListener;
import java.util.List;
import java.util.Vector;

import javax.swing.DefaultComboBoxModel;
import javax.swing.JComboBox;
import javax.swing.JTextField;

import org.columba.addressbook.model.ContactModelPartial;
import org.columba.addressbook.model.HeaderItemPartial;
import org.columba.addressbook.model.IBasicModelPartial;


/**
 * 
 * 
 *  Autocompleter component
 *
 * @author fdietz
 */
public class AddressAutoCompleter implements KeyListener, ItemListener {
    private JComboBox _comboBox = null;
    private JTextField _editor = null;
    int cursor_pos = -1;
    private Object[] _options;

    public AddressAutoCompleter(JComboBox comboBox, Object[] options) {
        _comboBox = comboBox;

        _editor = (JTextField) comboBox.getEditor().getEditorComponent();
        _editor.addKeyListener(this);

        _options = options;
        _comboBox.addItemListener(this);
    }

    public void keyTyped(KeyEvent e) {
    }

    public void keyPressed(KeyEvent e) {
    }

    public void keyReleased(KeyEvent e) {
        char ch = e.getKeyChar();

        if ((ch == KeyEvent.CHAR_UNDEFINED) || Character.isISOControl(ch) ||
                (ch == KeyEvent.VK_DELETE)) {
            return;
        }

        int pos = _editor.getCaretPosition();
        cursor_pos = _editor.getCaretPosition();

        String str = _editor.getText();

        if (str.length() == 0) {
            return;
        }

        autoComplete(str, pos);
    }

    private void autoComplete(String strf, int pos) {
        Object[] opts = getMatchingOptions(strf.substring(0, pos));

        if (_comboBox != null) {
            _comboBox.setModel(new DefaultComboBoxModel(opts));
        }

        if (opts.length > 0) {
            String str = opts[0].toString();

            IBasicModelPartial item = AddressCollector.getInstance().getHeaderItem((String) opts[0]);

            if (item == null) {
                item = new ContactModelPartial(str);
                
            } else {
                item = (IBasicModelPartial) item.clone();
            }

            _editor.setCaretPosition(cursor_pos);

            //_editor.moveCaretPosition(cursor_pos);
            if (_comboBox != null) {
                try {
                    _comboBox.showPopup();
                } catch (Exception ex) {
                    ex.printStackTrace();
                }
            }
        }
    }

    private Object[] getMatchingOptions(String str) {
        _options = AddressCollector.getInstance().getAddresses();

        List v = new Vector();

        for (int k = 0; k < _options.length; k++) {
            String item = _options[k].toString().toLowerCase();

            if (item.startsWith(str.toLowerCase())) {
                v.add(_options[k]);
            }
        }

        if (v.isEmpty()) {
            v.add(str);
        }

        return v.toArray();
    }

    public void itemStateChanged(ItemEvent event) {
        if (event.getStateChange() == ItemEvent.SELECTED) {
            String selected = (String) _comboBox.getSelectedItem();

            IBasicModelPartial item = AddressCollector.getInstance().getHeaderItem(selected);

            if (item == null) {
                item = new ContactModelPartial(selected);
                
            } else {
                item = (IBasicModelPartial) item.clone();
            }

            int pos2 = _editor.getCaretPosition();

            if (cursor_pos != -1) {
                try {
                    _editor.moveCaretPosition(pos2);
                } catch (IllegalArgumentException ex) {
                    ex.printStackTrace();
                }
            }
        }
    }
}