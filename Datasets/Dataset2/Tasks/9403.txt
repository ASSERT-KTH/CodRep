String str = "";

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
package org.columba.addressbook.gui.table;

import org.columba.addressbook.config.AdapterNode;

import org.columba.core.config.DefaultXmlConfig;

import java.util.List;
import java.util.Vector;

import javax.swing.table.AbstractTableModel;


public class GroupTableModel extends AbstractTableModel {
    private AdapterNode node;
    private List groupList;
    private String[] columnNames = {
        "Display Name", "Address", "First Name", "Last Name"
    };
    private int count;

    //private AddressbookXmlConfig config;
    protected DefaultXmlConfig config;

    public GroupTableModel(DefaultXmlConfig config) {
        super();

        //this.config = config;
        count = 0;
        groupList = new Vector();
    }

    public void setNode(AdapterNode n) {
        node = n;

        update();
    }

    public void update() {
        /*
        AdapterNode listNode = node.getChild("grouplist");
        count = listNode.getChildCount();

        GroupItem item = config.getGroupItem( node );
        if ( item != null ) System.out.println("item found") ;

        Vector ve = item.getListNodes();
        int uid;
        AdapterNode n, itemNode;

        groupList.clear();

        for ( int i=0; i<ve.size(); i++ )
        {
            n = ( AdapterNode ) ve.get(i);
            uid = (new Integer( n.getValue() ) ).intValue();
            itemNode = config.getNode( uid );
            groupList.addElement( itemNode );
        }

        fireTableDataChanged();
        */
    }

    public int getColumnCount() {
        return columnNames.length;
    }

    public int getRowCount() {
        return count;
    }

    public String getColumnName(int col) {
        String s = (String) columnNames[col];

        return s;
    }

    protected int getColumnNumber(String str) {
        for (int i = 0; i < getColumnCount(); i++) {
            if (str.equals(getColumnName(i))) {
                return i;
            }
        }

        return -1;
    }

    public Object getValueAt(int row, int col) {
        AdapterNode contact;

        contact = (AdapterNode) groupList.get(row);

        if (contact == null) {
            return "";
        }

        AdapterNode child = null;
        String str = new String("");

        if (contact.getName().equals("contact")) {
            if (col == 0) {
                child = contact.getChild("displayname");

                str = child.getValue();
            } else if (col == 1) {
                child = contact.getChild("address");

                str = child.getCDATAValue();
            } else if (col == 2) {
                child = contact.getChild("firstname");
                str = child.getValue();
            }

            if (col == 3) {
                child = contact.getChild("lastname");
                str = child.getValue();
            }

            /*

            if ( col == 1 )
            {
              child = contact.getChild("firstname");

              str = child.getValue();
            }
            else if ( col == 0 )
            {
              child = contact.getChild("lastname");
              str = child.getValue();
            }
            if ( col == 2 )
            {
              child = contact.getChild("address");
              str = child.getCDATAValue();
            }
            */
        }

        return str;
    }

    public Class getColumnClass(int c) {
        return getValueAt(0, c).getClass();
    }
}