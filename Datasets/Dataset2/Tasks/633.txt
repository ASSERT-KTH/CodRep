ColumbaLogger.log.info(

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

import org.columba.core.action.CheckBoxAction;
import org.columba.core.gui.frame.FrameMediator;
import org.columba.core.logging.ColumbaLogger;
import org.columba.core.xml.XmlElement;

import org.columba.mail.config.MailConfig;
import org.columba.mail.util.MailResourceLoader;

import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

import java.util.Observable;
import java.util.Observer;

import javax.swing.JCheckBoxMenuItem;


/**
 * CheckBox menu item for switching between HTML and text messages.
 * <br>
 * This will change the stored option, which in turn are told to
 * notify observers => editor changes btw. HTML and text etc.
 *
 * @author fdietz, Karl Peder Olesen
 */
public class EnableHtmlAction extends CheckBoxAction implements ActionListener,
    Observer {
    /**
     * @param frameMediator
     * @param name
     */
    public EnableHtmlAction(FrameMediator frameMediator) {
        super(frameMediator,
            MailResourceLoader.getString("menu", "composer",
                "menu_format_enable_html"));
    }

    /**
     * Overwritten to initialize the selection state of the
     * CheckBoxMenuItem.
     *
     * @see org.columba.core.action.CheckBoxAction#setCheckBoxMenuItem(javax.swing.JCheckBoxMenuItem)
     */
    public void setCheckBoxMenuItem(JCheckBoxMenuItem checkBoxMenuItem) {
        /* *20030912, karlpeder* Method signature changed from
         * setCheckBoxMenuItem(JCheckBoxMenuItem,AbstractFrameView).
         * Else it doesn't get called during creation of menu
         */
        super.setCheckBoxMenuItem(checkBoxMenuItem);

        ColumbaLogger.log.debug(
            "Initializing selected state of EnableHtmlAction");

        // enable/disable menuitem, based on configuration text/html state
        XmlElement optionsElement = MailConfig.get("composer_options")
                                              .getElement("/options");
        XmlElement htmlElement = optionsElement.getElement("html");

        //	create default element if not available
        if (htmlElement == null) {
            htmlElement = optionsElement.addSubElement("html");
        }

        String enableHtml = htmlElement.getAttribute("enable", "false");

        if (enableHtml.equals("true")) {
            getCheckBoxMenuItem().setSelected(true);
        } else {
            getCheckBoxMenuItem().setSelected(false);
        }

        // let the menu item listen for changes btw. html and text
        htmlElement.addObserver(this);
    }

    /**
     * Update checked state of menu item if change btw. html and text
     * has been made somewhere.
     *
     * @see java.util.Observer#update(java.util.Observable, java.lang.Object)
     */
    public void update(Observable o, Object arg) {
        XmlElement e = (XmlElement) o;

        if (e.getName().equals("html")) {
            String enableHtml = e.getAttribute("enable", "false");
            getCheckBoxMenuItem().setSelected(Boolean.valueOf(enableHtml)
                                                     .booleanValue());
        }
    }

    /* (non-Javadoc)
     * @see java.awt.event.ActionListener#actionPerformed(java.awt.event.ActionEvent)
     */
    public void actionPerformed(ActionEvent evt) {
        boolean selection = getCheckBoxMenuItem().isSelected();

        XmlElement optionsElement = MailConfig.get("composer_options")
                                              .getElement("/options");
        XmlElement htmlElement = optionsElement.getElement("html");

        //	create default element if not available
        if (htmlElement == null) {
            htmlElement = optionsElement.addSubElement("html");
        }

        // change configuration based on menuitem selection	 
        htmlElement.addAttribute("enable", Boolean.toString(selection));
        htmlElement.notifyObservers(); // notify everyone listening to this option
    }
}