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
package org.columba.chat.ui.presence;

import java.awt.BorderLayout;
import java.awt.event.ItemEvent;
import java.awt.event.ItemListener;

import javax.swing.ImageIcon;
import javax.swing.JComboBox;
import javax.swing.JLabel;
import javax.swing.JPanel;

import org.columba.chat.AlturaComponent;
import org.columba.chat.frame.AlturaFrameMediator;
import org.columba.core.gui.util.ImageLoader;
import org.jivesoftware.smack.packet.Presence;

/**
 * @author fdietz
 *  
 */
public class PresenceComboBox extends JPanel implements ItemListener {
  private AlturaFrameMediator frameMediator;
    
    private JComboBox checkBox;

    private JLabel label;

    private ImageIcon available = ImageLoader.getImageIcon("available.png");

    private ImageIcon extendedaway = ImageLoader
            .getImageIcon("extended-away.png");

    private ImageIcon away = ImageLoader.getImageIcon("away.png");

    private ImageIcon busy = ImageLoader.getImageIcon("busy.png");

    private ImageIcon message = ImageLoader.getImageIcon("message.png");

    private ImageIcon offline = ImageLoader.getImageIcon("offline.png");

    public PresenceComboBox(AlturaFrameMediator frameMediator) {
    	this.frameMediator = frameMediator;
    	
        
    	 checkBox = new JComboBox();

         checkBox.addItem("Available");
         checkBox.addItem("Custom Message...");
         checkBox.addItem("Working");
         checkBox.addItem("Custom Message...");
         //checkBox.addItem("Leave...");

         label = new JLabel();

         label.setIcon(available);

         setLayout(new BorderLayout());

         add(label, BorderLayout.WEST);
         add(checkBox, BorderLayout.CENTER);

         checkBox.addItemListener(this);
         
         addItemListener(this);
    }

    public void addItemListener(ItemListener l) {
        checkBox.addItemListener(l);
    }

  

    /**
     * @see java.awt.event.ItemListener#itemStateChanged(java.awt.event.ItemEvent)
     */
    public void itemStateChanged(ItemEvent e) {
        Object source = e.getItemSelectable();

        int index = ((JComboBox) source).getSelectedIndex();

        Presence p = null;
        switch (index) {
        case 0:
            {
        	 label.setIcon(available);
        	 
                p = new Presence(Presence.Type.AVAILABLE);
                p.setStatus("Available");
                AlturaComponent.connection.sendPacket(p);
                break;
            }
        case 2:
            {
        	 label.setIcon(busy);
        	 
                p = new Presence(Presence.Type.UNAVAILABLE);
                p.setStatus("Away");
                AlturaComponent.connection.sendPacket(p);
                break;
            }
        }
        
        
    }
}