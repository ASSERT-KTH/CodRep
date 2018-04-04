import org.columba.core.resourceloader.ImageLoader;

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
package org.columba.chat.ui.roaster;

import java.awt.Component;
import java.awt.Font;

import javax.swing.ImageIcon;
import javax.swing.JTree;
import javax.swing.tree.DefaultMutableTreeNode;
import javax.swing.tree.DefaultTreeCellRenderer;

import org.columba.chat.jabber.BuddyStatus;
import org.columba.core.gui.util.ImageLoader;
import org.jivesoftware.smack.RosterGroup;
import org.jivesoftware.smack.packet.Presence;

/**
 * @author fdietz
 *  
 */
public class RoasterTreeRenderer extends DefaultTreeCellRenderer {

    private ImageIcon available = ImageLoader.getImageIconResource("available.png");

    private ImageIcon extendedaway = ImageLoader
            .getImageIconResource("extended-away.png");

    private ImageIcon away = ImageLoader.getImageIconResource("away.png");

    private ImageIcon busy = ImageLoader.getImageIconResource("busy.png");

    private ImageIcon message = ImageLoader.getImageIconResource("message.png");

    private ImageIcon offline = ImageLoader.getImageIconResource("offline.png");

    /**
     *  
     */
    public RoasterTreeRenderer() {
        super();

    }

    /**
     * @see javax.swing.tree.TreeCellRenderer#getTreeCellRendererComponent(javax.swing.JTree,
     *      java.lang.Object, boolean, boolean, boolean, int, boolean)
     */
    public Component getTreeCellRendererComponent(JTree arg0, Object arg1,
            boolean arg2, boolean arg3, boolean arg4, int arg5, boolean arg6) {

        super.getTreeCellRendererComponent(arg0, arg1, arg2, arg3, arg4, arg5,
                arg6);

        Object o = ((DefaultMutableTreeNode) arg1).getUserObject();

        setIcon(null);
        
        if (o instanceof BuddyStatus) {
            // contact
            BuddyStatus entry = (BuddyStatus) o;
            Presence.Mode mode = entry.getPresenceMode();

            String name = entry.getName();
            Presence.Mode presence = entry.getPresenceMode();

            setFont( getFont().deriveFont(Font.PLAIN));

            if (presence != null) {
                if (presence.equals(Presence.Mode.AVAILABLE)) {
                    setIcon(available);
                } else if (presence.equals(Presence.Mode.AWAY)) {
                    setIcon(offline);
                }
                if (presence.equals(Presence.Mode.EXTENDED_AWAY)) {
                    setIcon(extendedaway);
                }
                if (presence.equals(Presence.Mode.CHAT)) {

                }
                if (presence.equals(Presence.Mode.DO_NOT_DISTURB)) {
                    setIcon(busy);
                }

            }

            StringBuffer buf = new StringBuffer();
            if (name != null)
                buf.append(name + " (" + entry.getJabberId() + ")");
            else
                buf.append(entry.getJabberId());

            if (presence != null) {
                buf.append(" - " + presence.toString());
                if (presence.equals(Presence.Mode.EXTENDED_AWAY)) {
                    setToolTipText(entry.getStatusMessage());
                } else {
                    setToolTipText(presence.toString());
                }
            }

            setText(buf.toString());
        } else if (o instanceof RosterGroup) {
            // group
            RosterGroup group = (RosterGroup) o;
            
            setFont( getFont().deriveFont(Font.BOLD));
            setText(group.getName());
            
        } else {
            setFont( getFont().deriveFont(Font.BOLD));
            setText(arg1.toString());
        }

        return this;
    }
}