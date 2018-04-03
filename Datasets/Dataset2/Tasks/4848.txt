icon = ImageLoader.getUnsafeImageIcon("mime/gnome-text.png");

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
package org.columba.mail.gui.attachment.util;

import java.util.logging.Level;
import java.util.logging.Logger;

import javax.swing.ImageIcon;

import org.columba.core.gui.util.ImageLoader;


/**
 * Imageloader using a content-type and subtype to determine
 * the image name.
 * <p>
 * Automatically falls back to the default icon.
 *
 * @author fdietz
 */
public final class AttachmentImageIconLoader {

    private static final Logger LOG = Logger.getLogger("org.columba.mail.gui.attachment.util");

    /**
     * Utility constructor.
     */
    private AttachmentImageIconLoader() {
    }

    /**
     * Returns the image icon for the content type.
     * @param contentType content type
     * @param contentSubtype content sub type
     * @return an Image Icon for the content type.
     */
    public static ImageIcon getImageIcon(String contentType, String contentSubtype) {
        StringBuffer buf = new StringBuffer();
        buf.append("mime/gnome-");
        buf.append(contentType);
        buf.append("-");
        buf.append(contentSubtype);
        buf.append(".png");

        if (LOG.isLoggable(Level.FINE)) {
            LOG.fine("Locating image icon " + buf.toString());
        }

        ImageIcon icon = ImageLoader.getUnsafeImageIcon(buf.toString());

        if (icon == null) {
            icon = ImageLoader.getUnsafeImageIcon("mime/gnome-"+contentType + ".png");
        }

        if (icon == null) {
            icon = ImageLoader.getImageIcon("text.png");
        }

        return icon;
    }
}