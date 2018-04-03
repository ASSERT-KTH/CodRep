private String patternString = "";

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
package org.columba.addressbook.gui.util;

import org.columba.addressbook.folder.HeaderItem;
import org.columba.addressbook.folder.HeaderItemList;
import org.columba.addressbook.gui.table.util.TableModelPlugin;

import java.util.List;
import java.util.Vector;

import javax.swing.AbstractListModel;


/**
 * @version         1.0
 * @author
 */
public class AddressbookListModel extends AbstractListModel {
    private List listClone;
    private List list;
    private String patternString = new String();

    public AddressbookListModel() {
        super();
        list = new Vector();
        listClone = new Vector();
    }

    public Object getElementAt(int index) {
        return (HeaderItem) list.get(index);
    }

    public int getSize() {
        return list.size();
    }

    public String getPatternString() {
        return patternString;
    }

    public void setPatternString(String s) throws Exception {
        patternString = s;

        //manipulateModel(TableModelPlugin.STRUCTURE_CHANGE);
    }

    public void clear() {
        list.clear();
    }

    public void addElement(Object item) {
        list.add(item);

        int index = list.indexOf(item);

        fireIntervalAdded(this, index, index);
    }

    public void setHeaderList(HeaderItemList l) {
        System.out.println("list size:" + l.count());

        list = (List) ((Vector) l.getVector()).clone();

        fireContentsChanged(this, 0, list.size() - 1);
    }

    public HeaderItem get(int i) {
        return (HeaderItem) list.get(i);
    }

    public boolean addItem(HeaderItem header) {
        boolean result1 = false;

        Object o = header.get("displayname");

        if (o != null) {
            if (o instanceof String) {
                String item = (String) o;

                //System.out.println("add item?:"+item);
                item = item.toLowerCase();

                String pattern = getPatternString().toLowerCase();

                if (item.indexOf(pattern) != -1) {
                    result1 = true;
                } else {
                    result1 = false;
                }
            } else {
                result1 = false;
            }
        } else {
            result1 = false;
        }

        return result1;
    }

    public Object[] toArray() {
        return list.toArray();
    }

    public void remove(int index) {
        list.remove(index);
        fireIntervalRemoved(this, index, index);
    }

    public void removeElement(Object o) {
        int index = list.indexOf(o);

        remove(index);
    }

    public boolean manipulateModel(int mode) throws Exception {
        listClone = (Vector) ((Vector) list).clone();

        switch (mode) {
        case TableModelPlugin.STRUCTURE_CHANGE: {
            if (getSize() == 0) {
                return false;
            }

            //System.out.println("starting filtering");
            HeaderItem item = null;

            for (int i = 0; i < getSize(); i++) {
                item = (HeaderItem) get(i);

                boolean result = addItem(item);

                //ystem.out.println("item: "+i+" - result: "+result);
                if (!result) {
                    //System.out.println("removing item:"+item);
                    list.remove(item);
                    i--;

                    /*
                    Object uid = list.getUid(i);
                    MessageNode childNode = new MessageNode( header, uid );
                    rootNode.add( childNode );
                    */
                }
            }

            // System.out.println("finished filtering");
            return true;
        }

        case TableModelPlugin.NODES_INSERTED:return true;
        }

        return false;
    }
}