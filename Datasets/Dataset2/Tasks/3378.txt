import org.columba.core.gui.action.AbstractColumbaAction;

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
package org.columba.core.gui.menu;

import javax.swing.Action;
import javax.swing.Icon;
import javax.swing.JButton;

import org.columba.core.action.AbstractColumbaAction;
import org.columba.core.help.HelpManager;


/**
 * Default Button which automatically sets a JavaHelp topic ID
 * based on the AbstractAction name attribute.
 * <p>
 * This is necessary to provide a complete context-specific help.
 *
 * @author fdietz
 */
public class CButton extends JButton {
    public CButton() {
        super();
    }

    public CButton(Icon icon) {
        super(icon);
    }

    public CButton(Action action) {
        super(action);

        String topicID = (String) action.getValue(AbstractColumbaAction.TOPIC_ID);

        if (topicID != null) {
            HelpManager.getInstance().enableHelpOnButton(this, topicID);
        }
    }
}