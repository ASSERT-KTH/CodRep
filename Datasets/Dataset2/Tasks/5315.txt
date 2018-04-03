putValue(SMALL_ICON, ImageLoader.getSmallIcon("go-home.png"));

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
package org.columba.core.gui.globalactions;

import java.awt.event.ActionEvent;
import java.net.MalformedURLException;
import java.net.URL;

import org.columba.api.gui.frame.IFrameMediator;
import org.columba.core.gui.action.AbstractColumbaAction;
import org.columba.core.gui.util.URLController;
import org.columba.core.resourceloader.GlobalResourceLoader;
import org.columba.core.resourceloader.ImageLoader;


/**
 * @author frd
 *
 * To change this generated comment go to
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
public class ShowHomepageAction extends AbstractColumbaAction {
    public ShowHomepageAction(IFrameMediator frameMediator) {
        super(frameMediator,
            GlobalResourceLoader.getString(null, null, "menu_help_homepage"));

        // small icon for menu
        putValue(SMALL_ICON, ImageLoader.getImageIcon("stock_home_16.png"));
    }

    /* (non-Javadoc)
     * @see java.awt.event.ActionListener#actionPerformed(java.awt.event.ActionEvent)
     */
    public void actionPerformed(ActionEvent evt) {
        URLController c = new URLController();

        try {
            c.open(new URL("http://columba.sourceforge.net"));
        } catch (MalformedURLException mue) {
        }
    }
}