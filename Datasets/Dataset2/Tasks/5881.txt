import org.columba.core.action.AbstractColumbaAction;

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
package org.columba.mail.gui.frame;

import org.columba.core.action.FrameAction;
import org.columba.core.gui.statusbar.StatusBar;

import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;

import javax.swing.AbstractButton;
import javax.swing.Action;


/**
 * @author Timo Stich (tstich@users.sourceforge.net)
 *
 */
public class TooltipMouseHandler extends MouseAdapter {
    private StatusBar statusBar;

    /**
     * Constructor for MouseHandler.
     */
    public TooltipMouseHandler(StatusBar statusBar) {
        super();
        this.statusBar = statusBar;
    }

    /**
     * Called when the mouse is placed over e.g. a menu or a toolbar
     * button. Either the tooltip text (preferred) or SHORT_DESCRIPTION
     * is fetched from the action associated with the menu/button if
     * possible, and displayed in the status bar.
     */
    public void mouseEntered(MouseEvent evt) {
        if (evt.getSource() instanceof AbstractButton) {
            AbstractButton button = (AbstractButton) evt.getSource();
            Action action = button.getAction();

            if (action != null) {
                String message = (String) action.getValue(Action.SHORT_DESCRIPTION);
                statusBar.displayTooltipMessage(message);
            }
        }
    }

    /**
     * Called when the mouse is moved away from e.g. a menu or a toolbar
     * button. Clears the text displayed in the status bar.
     */
    public void mouseExited(MouseEvent e) {
        // clear the tooltip message previously displayed in the status bar
        statusBar.displayTooltipMessage("");
    }

    /**
     * Called when the mouse is pressed on e.g. a menu or a toolbar
     * button. Clears the text displayed in the status bar.
     */
    public void mousePressed(MouseEvent e) {
        // clear the tooltip message previously displayed in the status bar
        statusBar.displayTooltipMessage("");
    }
}