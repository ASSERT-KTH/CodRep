import org.columba.core.gui.mimetype.MimeTypeViewer;

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

package org.columba.core.gui.util;

import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.net.URL;

import javax.swing.JMenuItem;
import javax.swing.JPopupMenu;

import org.columba.mail.gui.mimetype.MimeTypeViewer;

public class URLController implements ActionListener {
    private String address;
    private URL link;

    //TODO (@author fdietz): i18n
    public JPopupMenu createContactMenu(String contact) {
        JPopupMenu popup = new JPopupMenu();
        JMenuItem menuItem = new JMenuItem("Add Contact to Addressbook");
        menuItem.addActionListener(this);
        menuItem.setActionCommand("CONTACT");
        popup.add(menuItem);
        menuItem = new JMenuItem("Compose Message for " + contact);
        menuItem.setActionCommand("COMPOSE");
        menuItem.addActionListener(this);
        popup.add(menuItem);

        return popup;
    }

    //TODO (@author fdietz): i18n
    public JPopupMenu createLinkMenu() {
        JPopupMenu popup = new JPopupMenu();
        JMenuItem menuItem = new JMenuItem("Open");
        menuItem.addActionListener(this);
        menuItem.setActionCommand("OPEN");
        popup.add(menuItem);
        menuItem = new JMenuItem("Open with...");
        menuItem.setActionCommand("OPEN_WITH");
        menuItem.addActionListener(this);
        popup.add(menuItem);
        popup.addSeparator();
        menuItem = new JMenuItem("Open with internal browser");
        menuItem.setActionCommand("OPEN_WITHINTERNALBROWSER");
        menuItem.addActionListener(this);
        popup.add(menuItem);

        return popup;
    }

    public void setAddress(String s) {
        this.address = s;
    }

    public String getAddress() {
        return address;
    }

    public URL getLink() {
        return link;
    }

    public void setLink(URL u) {
        this.link = u;
    }

    /**
     * Composer message for recipient
     * 
     * @param address	email address of recipient
     */
    public void compose(String address) {
    	//IServiceManager.getInstance().createService("");
    	
       // TODO: implement this
    }

    /**
     * Add contact to addressbook.
     * 
     * @param address		new email address
     */
    public void contact(String address) {
    	// TODO: implement this
    }

    public JPopupMenu createMenu(URL url) {
        if (url.getProtocol().equalsIgnoreCase("mailto")) {
            // found email address
            setAddress(url.getFile());

            JPopupMenu menu = createContactMenu(url.getFile());

            return menu;
        } else {
            setLink(url);

            JPopupMenu menu = createLinkMenu();

            return menu;
        }
    }

    public void open(URL url) {
        MimeTypeViewer viewer = new MimeTypeViewer();
        viewer.openURL(url);
    }

    public void openWith(URL url) {
        MimeTypeViewer viewer = new MimeTypeViewer();
        viewer.openWithURL(url);
    }

   
    public void actionPerformed(ActionEvent e) {
        String action = e.getActionCommand();

        if (action.equals("COMPOSE")) {
            compose(getAddress());
        } else if (action.equals("CONTACT")) {
            contact(getAddress());
        } else if (action.equals("OPEN")) {
            open(getLink());
        } else if (action.equals("OPEN_WITH")) {
            openWith(getLink());
        } else if (action.equals("OPEN_WITHINTERNALBROWSER")) {
            //openWithBrowser(getLink());
        }
    }
}