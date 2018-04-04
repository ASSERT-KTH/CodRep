import org.columba.core.gui.action.CRadioButtonMenuItem;

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
//All Rights Reserved.undation, Inc., 59 Temple Place - Suite 330, Boston, MA
// 02111-1307, USA.
package org.columba.mail.gui.charset;

import java.nio.charset.Charset;

import org.columba.core.gui.base.CRadioButtonMenuItem;
import org.columba.mail.util.MailResourceLoader;


/**
 * A menu item for displaying charsets.
 */

public class CharsetMenuItem extends CRadioButtonMenuItem {
    protected Charset charset;

    /**
 * Creates a new menu item for the given charset.
 */
    public CharsetMenuItem(Charset charset) {
        super("");
        setCharset(charset);
    }

    /**
 * Returns the charset associated with this menu item.
 */
    public Charset getCharset() {
        return charset;
    }

    /**
 * Sets the charset associated with this menu item. This is used for the
 * selectedMenuItem property in CharacterEncodingSubMenu. This method
 * adapts the display text accordingly.
 */
    public void setCharset(Charset charset) {
        this.charset = charset;

        String charsetName;

        if (charset == null) {
            charsetName = "auto";
        } else {
            charsetName = charset.name();
        }

        setText(MailResourceLoader.getString("menu", "mainframe",
                "menu_view_charset_" + charsetName));
    }
}