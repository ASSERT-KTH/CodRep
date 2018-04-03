((AbstractMailView) frameMediator.getView()).showToolbar();

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
package org.columba.core.gui.action;

import org.columba.core.action.AbstractSelectableAction;
import org.columba.core.gui.frame.FrameMediator;
import org.columba.core.util.GlobalResourceLoader;

import org.columba.mail.gui.frame.MailFrameView;
import org.columba.mail.gui.view.AbstractMailView;

import java.awt.event.ActionEvent;


/**
 * Columba action for hiding/showing the toolbar action.
 */
public class ViewToolbarAction extends AbstractSelectableAction {
    /**
     * Creates a view toolbar action.
     * @param controller the frame controller
     */
    public ViewToolbarAction(FrameMediator controller) {
        super(controller,
            GlobalResourceLoader.getString(null, null, "menu_view_showtoolbar"));

        // tooltip text
        putValue(SHORT_DESCRIPTION,
            GlobalResourceLoader.getString(null, null, "menu_view_showtoolbar")
                                .replaceAll("&", ""));

        setState(frameMediator.isToolbarEnabled(AbstractMailView.MAIN_TOOLBAR));
    }

    /**
     * Shows the toolbar.
     * @param evt the event
     */
    public void actionPerformed(ActionEvent evt) {
        ((AbstractMailView) frameMediator.getBaseView()).showToolbar();
    }
}