import org.columba.addressbook.model.HeaderItem;

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
package org.columba.addressbook.gui.list;

import org.columba.addressbook.folder.HeaderItem;


/**
 * @author frd
 *
 * To change this generated comment edit the template variable "typecomment":
 * Window>Preferences>Java>Templates.
 * To enable and disable the creation of type comments go to
 * Window>Preferences>Java>Code Generation.
 */
public class HeaderItemDNDManager {
    private static HeaderItemDNDManager instance;
    HeaderItem[] array;

    public static HeaderItemDNDManager getInstance() {
        if (instance == null) {
            instance = new HeaderItemDNDManager();
        }

        return instance;
    }

    public void setHeaderItemList(HeaderItem[] array) {
        this.array = array;
    }

    public HeaderItem[] getHeaderItemList() {
        return this.array;
    }
}