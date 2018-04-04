import org.columba.core.plugin.exception.PluginLoadingFailedException;

// The contents of this file are subject to the Mozilla Public License Version
// 1.1
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
//The Initial Developers of the Original Code are Frederik Dietz and Timo
// Stich.
//Portions created by Frederik Dietz and Timo Stich are Copyright (C) 2003.
//
//All Rights Reserved.

package org.columba.core.gui.action;

import java.awt.event.ActionEvent;

import org.columba.core.action.AbstractColumbaAction;
import org.columba.core.gui.frame.FrameMediator;
import org.columba.core.gui.frame.FrameModel;
import org.columba.core.gui.util.ImageLoader;
import org.columba.core.plugin.PluginLoadingFailedException;
import org.columba.core.util.GlobalResourceLoader;


/**
 * Opens a new addressbook window.
 *
 * @author frd
 */
public class OpenNewAddressbookWindowAction extends AbstractColumbaAction {
    public OpenNewAddressbookWindowAction(FrameMediator controller) {
        super(controller,
            GlobalResourceLoader.getString(null, null,
                "menu_file_new_addressbook"));

        putValue(SHORT_DESCRIPTION,
            GlobalResourceLoader.getString(null, null,
                "menu_file_new_addressbook_tooltip").replaceAll("&", ""));

        putValue(SMALL_ICON, ImageLoader.getSmallImageIcon("stock_book-16.png"));
        putValue(LARGE_ICON, ImageLoader.getImageIcon("stock_book.png"));
    }

    /*
     * Uses the FrameModel instance in MainInterface to open a new
     * addressbook window.
     */
    public void actionPerformed(ActionEvent evt) {
   

		try {
			FrameModel.getInstance().openView( "Addressbook");
		} catch (PluginLoadingFailedException e) {
			e.printStackTrace();
		}
    }
}