"menu_format_font_size"),"menu_format_font_size");

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
package org.columba.mail.gui.composer.html.action;

import javax.swing.ButtonGroup;
import javax.swing.JRadioButtonMenuItem;

import org.columba.core.action.IMenu;
import org.columba.core.gui.frame.FrameMediator;
import org.columba.mail.util.MailResourceLoader;


/**
 *
 * Submenu for choosing the font size settings
 * "-2, -1, 0, 1, 2, 3"
 *
 * TODO (@author fdietz): add actionPerformed-method, and enabling/disabling based on html/text
 *
 *
 * @author fdietz
 */
public class FontSizeMenu extends IMenu {
    public final static String[] SIZES = { "-2", "-1", "0", "+1", "+2", "+3" };
    ButtonGroup group;

    /**
 * @param controller
 * @param caption
 */
    public FontSizeMenu(FrameMediator controller) {
        super(controller,
            MailResourceLoader.getString("menu", "composer",
                "menu_format_font_size"));

        initMenu();

        // Enable when implemented
        setEnabled(false);
    }

    protected void initMenu() {
        group = new ButtonGroup();

        for (int i = 0; i < SIZES.length; i++) {
            JRadioButtonMenuItem m = new JRadioButtonMenuItem(SIZES[i]);
            add(m);

            group.add(m);
        }
    }
}