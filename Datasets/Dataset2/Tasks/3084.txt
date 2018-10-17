AdapterNode node = MailInterface.config.getFolderConfig().addEmptyFilterNode( getFolder().getNode() );

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
//All Rights Reserved.undation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
package org.columba.mail.filter;

import org.columba.core.config.DefaultItem;
import org.columba.core.xml.XmlElement;

/**
 * A list of filters.
 *
 */
public class FilterList extends DefaultItem {

    /** The name of this object when stored in a XML document. */
    public static final String XML_NAME = "filterlist";

    //private Vector list;
    // private Folder folder;
    /**
     * Creates a FilterList with the specified element as the root.
     * @param root the element to use as the root.
     */
    public FilterList(XmlElement root) {
        super(root);
    }

    /**
     * Creates an empty filter list.
     */
    public FilterList() {
        super(new XmlElement(FilterList.XML_NAME));
    }

    /**
     * Returns an empty default filter.
     * @return an empty default Filter.
     */
    public static Filter createEmptyFilter() {
        XmlElement filter = new XmlElement("filter");
        filter.addAttribute("description", "new filter");
        filter.addAttribute("enabled", "true");

        XmlElement rules = new XmlElement("rules");
        rules.addAttribute("condition", "matchall");

        XmlElement criteria = new XmlElement("criteria");
        criteria.addAttribute("type", "Subject");
        criteria.addAttribute("headerfield", "Subject");
        criteria.addAttribute("criteria", "contains");
        criteria.addAttribute("pattern", "pattern");
        rules.addElement(criteria);
        filter.addElement(rules);

        XmlElement actionList = new XmlElement("actionlist");
        XmlElement action = new XmlElement("action");

        /*
        action.addAttribute(
                "class",
                "org.columba.mail.filter.action.MarkMessageAsReadFilterAction");
        */
        action.addAttribute("type", "Mark Message");
        action.addAttribute("markvariant", "read");

        actionList.addElement(action);
        filter.addElement(actionList);

        //XmlElement.printNode(getRoot(),"");
        return new Filter(filter);

        /*
        //AdapterNode filterListNode = getFilterListNode();

        AdapterNode node = MailConfig.getFolderConfig().addEmptyFilterNode( getFolder().getNode() );
        Filter filter = new Filter( node );

        add( filter );

        return filter;
        */
    }

    /**
     * Adds the filter to this list.
     * @param f the filter.
     */
    public void add(Filter f) {
        if (f != null) {
            getRoot().addElement(f.getRoot());
        }

        //list.add(f);
    }

    /**
     * Adds all filters in the supplied list to this filter list.
     * @param list a list containing other filters to add to this list.
     */
    public void addAll(FilterList list) {
        int size = list.count();

        for (int i = 0; i < size; i++) {
            Filter newFilter = list.get(i);
            add(newFilter);
        }
    }

    /**
     * Remove the <code>Filter</code> from the list.
     * @param f the filter to remove.
     */
    public void remove(Filter f) {
        if (f != null) {
            getRoot().getElements().remove(f.getRoot());
        }
    }

    /**
     * Inserts the filter into the specified index in the list.
     * @param filter filter to add.
     * @param index the index where to insert the filter.
     */
    public void insert(Filter filter, int index) {
        if (filter != null) {
            getRoot().insertElement(filter.getRoot(), index);
        }
    }

    /**
     * Moves the specified filter up in the list.
     * @param filter the filter to move up.
     */
    public void moveUp(Filter filter) {
        move(indexOf(filter), -1);
    }

    /**
     * Moves the specified filter down in the list.
     * @param filter the filter to move down.
     */
    public void moveDown(Filter filter) {
        move(indexOf(filter), 1);
    }

    /**
     * Moves the specified filter a number of positions in the list.
     * @param filter the filter to move.
     * @param nrOfPositions the number of positions to move in the list, can be negative.
     */
    public void move(Filter filter, int nrOfPositions) {
        move(indexOf(filter), nrOfPositions);
    }

    /**
     * Moves the filter at the specified index a number of positions in the list.
     * @param filterIndex the filters index.
     * @param nrOfPositions the number of positions to move in the list, can be negative.
     */
    public void move(int filterIndex, int nrOfPositions) {
        if ((filterIndex >= 0) && (filterIndex < count())) {
            XmlElement filterXML = getRoot().getElement(filterIndex);
            int newFilterIndex = filterIndex + nrOfPositions;

            if (newFilterIndex < 0) {
                newFilterIndex = 0;
            }

            getRoot().removeElement(filterIndex);

            if (newFilterIndex > count()) {
                getRoot().addElement(filterXML);
            } else {
                getRoot().insertElement(filterXML, newFilterIndex);
            }
        }
    }

    /**
     * Returns the index in this list of the first occurrence of the specified
     * filter, or -1 if this list does not contain this element.
     * @param filter filter to search for.
     * @return the index in this list of the first occurrence of the specified filter,
     * or -1 if this list does not contain this element.
     */
    public int indexOf(Filter filter) {
        int index = -1;

        if (filter != null) {
            int childCount = getChildCount();

            for (int i = 0; (index == -1) && (i < childCount); i++) {
                if (getRoot().getElement(i).equals(filter.getRoot())) {
                    index = i;
                }
            }
        }

        return index;
    }

    /**
     * Returns the number of filters in this list.
     * @return the number of filters in this list.
     */
    public int count() {
        return getChildCount();
    }

    /**
     * Returns the filter at the specified position in the list.
     * @param index the index
     * @return a Filter
     */
    public Filter get(int index) {
        Filter filter = new Filter(getRoot().getElement(index));

        return filter;
    }

    /**
     * Removes the filter at the specified list index.
     * @param index the index of the filter to remove from this list.
     */
    public void remove(int index) {
        getRoot().removeElement(index);
    }
}