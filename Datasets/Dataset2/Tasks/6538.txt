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

package org.columba.addressbook.gui.dialog.contact;

import java.awt.BorderLayout;
import java.awt.Insets;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.util.Enumeration;
import java.util.Hashtable;
import java.util.Iterator;
import java.util.List;
import java.util.Vector;

import javax.swing.JButton;
import javax.swing.JCheckBoxMenuItem;
import javax.swing.JMenuItem;
import javax.swing.JPanel;
import javax.swing.JPopupMenu;
import javax.swing.SwingConstants;
import javax.swing.event.DocumentEvent;
import javax.swing.event.DocumentListener;
import javax.swing.text.Document;
import javax.swing.text.JTextComponent;

import org.columba.addressbook.model.IContact;
import org.columba.core.gui.util.ImageLoader;

/**
 * @author fdietz
 */
public class AttributComboBox extends JPanel
        implements ActionListener, DocumentListener {
    //JLabel label;
    private JButton button;
    private JPopupMenu menu;
    private List list;
    private String selection;
    private Hashtable table;
    private JTextComponent textField;
    private String name;
    private List menuList;
    
    private IContact contact;
    
    public AttributComboBox(String name, List list, JTextComponent textField,
            IContact contact) {
        super();
        
        this.name = name;
        this.textField = textField;
        this.contact = contact;
        
        textField.getDocument().addDocumentListener(this);
        
        table = new Hashtable();
        
        this.list = list;
        
        menuList = new Vector();
        
        initComponents();
    }
    
    public Hashtable getResultTable() {
        return table;
    }
    
    public void setResultTable(Hashtable table) {
        this.table = table;
    }
    
    public void updateComponents(boolean b) {
        if (b) {
            for (Iterator it = list.iterator(); it.hasNext();) {
                String str = (String) it.next();
                table.put(str, contact.get(name, str));
            }
            
            //			for (int i = 0; i < list.size(); i++)
            //			{
            //				String str = (String) list.get(i);
            //				table.put(str, card.get(name, str));
            //
            //			}
            for (Iterator it = menuList.iterator(); it.hasNext();) {
                JMenuItem item = (JMenuItem) it.next();
                
                //			for (int i = 0; i < menuList.size(); i++)
                //			{
                //				JMenuItem item = (JMenuItem) menuList.get(i);
                String s = (String) table.get(item.getActionCommand());
                
                if ((s != null)) {
                    if (s.length() != 0) {
                        item.setSelected(true);
                    } else {
                        item.setSelected(false);
                    }
                } else {
                    item.setSelected(false);
                }
            }
            
            String s = (String) table.get((String) list.get(0));
            
            if (s != null) {
                textField.setText(s);
            } else {
                textField.setText(null);
            }
        } else {
            for (Enumeration e = table.keys(); e.hasMoreElements();) {
                String key = (String) e.nextElement();
                String value = (String) table.get(key);
                contact.set(name, key, value);
            }
        }
    }
    
    protected void initComponents() {
        setLayout(new BorderLayout());
        
                /*
                 * label = new JLabel(name + " (" + (String) list.get(0) + ")");
                 * add(label, BorderLayout.WEST); Component box =
                 * Box.createHorizontalStrut(20); add(box, BorderLayout.CENTER);
                 */
        //button = new ArrowButton(0);
        button = new JButton(name + " (" + (String) list.get(0) + "):",
                ImageLoader.getSmallImageIcon("stock_down-16.png"));
        button.setActionCommand("BUTTON");
        button.setMargin(new Insets(0, 0, 0, 0));
        
        //button.setMargin(new Insets(2, 5, 2, 0));
        button.setHorizontalTextPosition(SwingConstants.LEADING);
        
        //button.setIconTextGap(20);
        button.addActionListener(this);
        add(button, BorderLayout.WEST);
        
        menu = new JPopupMenu();
        
        selection = (String) list.get(0);
        
        for (Iterator it = list.iterator(); it.hasNext();) {
            String next = (String) it.next();
            JCheckBoxMenuItem menuItem = new JCheckBoxMenuItem(next);
            menuItem.setActionCommand(next);
            
            //		for (int i = 0; i < list.size(); i++)
            //		{
            //			JCheckBoxMenuItem menuItem = new JCheckBoxMenuItem((String)
            // list.get(i));
            //			menuItem.setActionCommand((String) list.get(i));
            menuItem.addActionListener(this);
            menu.add(menuItem);
            menuList.add(menuItem);
        }
    }
    
    public void actionPerformed(ActionEvent event) {
        String action = event.getActionCommand();
        
        if (action.equals("BUTTON")) {
            for (Iterator it = menuList.iterator(); it.hasNext();) {
                JMenuItem item = (JMenuItem) it.next();
                
                //			for (int i = 0; i < menuList.size(); i++)
                //			{
                //				JMenuItem item = (JMenuItem) menuList.get(i);
                String s = (String) table.get(item.getActionCommand());
                
                if ((s != null)) {
                    if (s.length() != 0) {
                        item.setSelected(true);
                    } else {
                        item.setSelected(false);
                    }
                } else {
                    item.setSelected(false);
                }
            }
            
            //menu.show(button, button.getX(), button.getY());
            menu.show(button, button.getWidth(), 0);
        } else {
            button.setText(name + " (" + action + "):");
            selection = action;
            
            String s = (String) table.get(action);
            
            if (s != null) {
                textField.setText(s);
            } else {
                textField.setText(null);
            }
        }
    }
    
    public String getSelected() {
        return selection;
    }
    
    public void insertUpdate(DocumentEvent e) {
        updateDoc(e.getDocument());
    }
    
    public void removeUpdate(DocumentEvent e) {
        updateDoc(e.getDocument());
    }
    
    public void changedUpdate(DocumentEvent e) {
        updateDoc(e.getDocument());
    }
    
    public void updateDoc(Document doc) {
        String s = getSelected();
        
        table.put(s, textField.getText());
    }
}