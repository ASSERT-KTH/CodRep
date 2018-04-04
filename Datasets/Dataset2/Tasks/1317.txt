public class FolderItem extends DefaultItem implements IFolderItem {

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
//All Rights Reserved.oundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
package org.columba.mail.config;

import org.columba.core.config.DefaultItem;
import org.columba.core.xml.XmlElement;


public class FolderItem extends DefaultItem {
    public FolderItem(XmlElement root) {
        super(root);
    }

    /**
    * Get folder-based configuration.
    *
    * @return      parent xml-node storing the configuration
    */
    public XmlElement getFolderOptions() {
        XmlElement property = getElement("property");

        return property;
    }

    /**
     * Get global folder options.
     *
     * @return      xml parent node
     */
    public static XmlElement getGlobalOptions() {
        //      use global table options
        XmlElement tableElement = MailConfig.getInstance().get("options")
                                                      .getElement("/options/gui/table");

        return tableElement;
    }
}