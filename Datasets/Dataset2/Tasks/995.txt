HelpManager.getInstance().enableHelpOnButton(this, topicID);

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
import javax.swing.ImageIcon;
import javax.swing.JMenuItem;

import org.columba.core.action.AbstractColumbaAction;
import org.columba.core.gui.util.ImageUtil;
import org.columba.core.gui.util.MnemonicSetter;
import org.columba.core.help.HelpManager;


/**
 * Default MenuItem which automatically sets a JavaHelp topic ID
 * based on the AbstractAction name attribute.
 * <p>
 * This is necessary to provide a complete context-specific help.
 *
 *
 * @author fdietz
 */
public class CMenuItem extends JMenuItem {
    /**
     * Creates a menu item with a given action attached.
     * <br>
     * If JavaHelp topic ID is defined for the action, help is enabled
     * for the menu.
     * <br>
     * If the name of the action contains &, the next character is used as
     * mnemonic. If not, the fall-back solution is to use default behaviour,
     * i.e. the mnemonic defined using setMnemonic on the action.
     *
     * @param action        The action to attach to the menu item
     */
    public CMenuItem(Action action) {
        super(action);

        // Enable JavaHelp support if topic id is defined
        String topicID = (String) action.getValue(AbstractColumbaAction.TOPIC_ID);

        if (topicID != null) {
            HelpManager.getHelpManager().enableHelpOnButton(this, topicID);
        }

        // Set text, possibly with a mnemonic if defined using &
        MnemonicSetter.setTextWithMnemonic(this,
            (String) action.getValue(Action.NAME));

        // apply transparent icon
        ImageIcon icon = (ImageIcon) action.getValue(Action.SMALL_ICON);

        if (icon != null) {
            setDisabledIcon(ImageUtil.createTransparentIcon(icon));
        }
    }

    /**
     * Creates a menu item with the specified text.
     * <br>
     * This does <i>not</i> enable JavaHelp support.
     * <br>
     * If the textcontains &, the next character is used as
     * mnemonic. If not, no mnemonic is set.
     *
     * @param        text        Text of menu item
     */
    public CMenuItem(String text) {
        super();
        MnemonicSetter.setTextWithMnemonic(this, text);
    }
}