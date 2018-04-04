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

import org.columba.core.action.IMenu;
import org.columba.core.gui.frame.FrameMediator;
import org.columba.core.logging.ColumbaLogger;
import org.columba.core.xml.XmlElement;

import org.columba.mail.config.MailConfig;
import org.columba.mail.gui.composer.ComposerController;
import org.columba.mail.gui.composer.html.HtmlEditorController;
import org.columba.mail.gui.composer.html.util.FormatInfo;
import org.columba.mail.util.MailResourceLoader;

import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.ContainerEvent;
import java.awt.event.ContainerListener;

import java.util.Enumeration;
import java.util.Observable;
import java.util.Observer;

import javax.swing.ButtonGroup;
import javax.swing.JRadioButtonMenuItem;
import javax.swing.text.html.HTML;


/**
 * Submenu for formatting text.
 * <p>
 * Possible values are:
 *  - normal
 *  - preformatted
 *  - heading 1
 *  - heading 2
 *  - heading 3
 *  - address
 *
 * Note: This is the place to add further formats like lists, etc.
 *
 * Note: The HtmlEditorView and -Controller must of course also support
 *       new formats when adding them!
 *
 * @author fdietz, Karl Peder Olesen (karlpeder)
 */
public class ParagraphMenu extends IMenu implements Observer, ActionListener,
    ContainerListener {
    /** Supported paragraph styles */
    public final static String[] STYLES = {
        "Normal", "Preformatted", "Heading 1", "Heading 2", "Heading 3",
        "Address"
    };

    /** Html tags corresponding to supported paragraph styles */
    public final static HTML.Tag[] STYLE_TAGS = {
        HTML.Tag.P, HTML.Tag.PRE, HTML.Tag.H1, HTML.Tag.H2, HTML.Tag.H3,
        HTML.Tag.ADDRESS
    };

    /** String representation of html tags */
    public final static String[] STYLE_STRINGS = {
        HTML.Tag.P.toString(), HTML.Tag.PRE.toString(), HTML.Tag.H1.toString(),
        HTML.Tag.H2.toString(), HTML.Tag.H3.toString(),
        HTML.Tag.ADDRESS.toString()
    };
    ButtonGroup group;

    /**
     * @param controller
     * @param caption
     */
    public ParagraphMenu(FrameMediator controller) {
        super(controller,
            MailResourceLoader.getString("menu", "composer",
                "menu_format_paragraph"));

        initMenu();

        // register for text selection changes
        ((ComposerController) controller).getEditorController().addObserver(this);

        // register for changes to the editor
        ((ComposerController) controller).addContainerListenerForEditor(this);

        // register for changes to editor type (text / html)
        XmlElement optionsElement = MailConfig.get("composer_options")
                                              .getElement("/options");
        XmlElement htmlElement = optionsElement.getElement("html");

        if (htmlElement == null) {
            htmlElement = optionsElement.addSubElement("html");
        }

        String enableHtml = htmlElement.getAttribute("enable", "false");
        htmlElement.addObserver(this);

        // set initial enabled state
        setEnabled(Boolean.valueOf(enableHtml).booleanValue());
    }

    /**
     * Initializes the sub menu by creating a menu item for each
     * available paragraph style. All menu items are grouped in a
     * ButtonGroup (as radio buttons).
     */
    protected void initMenu() {
        group = new ButtonGroup();

        for (int i = 0; i < STYLES.length; i++) {
            JRadioButtonMenuItem m = new JRadioButtonMenuItem(STYLES[i]);
            m.setActionCommand(STYLE_STRINGS[i]);
            m.addActionListener(this);
            add(m);

            group.add(m);
        }
    }

    /**
     * Method is called when text selection has changed.
     * <p>
     * Set state of togglebutton / -menu to pressed / not pressed
     * when selections change.
     *
     * @see java.util.Observer#update(java.util.Observable, java.lang.Object)
     */
    public void update(Observable arg0, Object arg1) {
        if (arg0 instanceof HtmlEditorController) {
            // select the menu item corresponding to present format
            FormatInfo info = (FormatInfo) arg1;

            if (info.isHeading1()) {
                selectMenuItem(HTML.Tag.H1);
            } else if (info.isHeading2()) {
                selectMenuItem(HTML.Tag.H2);
            } else if (info.isHeading3()) {
                selectMenuItem(HTML.Tag.H3);
            } else if (info.isPreformattet()) {
                selectMenuItem(HTML.Tag.PRE);
            } else if (info.isAddress()) {
                selectMenuItem(HTML.Tag.ADDRESS);
            } else {
                // select the "Normal" entry as default
                selectMenuItem(HTML.Tag.P);
            }
        } else if (arg0 instanceof XmlElement) {
            // possibly change btw. html and text
            XmlElement e = (XmlElement) arg0;

            if (e.getName().equals("html")) {
                String enableHtml = e.getAttribute("enable", "false");

                // This action should only be enabled in html mode
                setEnabled(Boolean.valueOf(enableHtml).booleanValue());
            }
        }
    }

    /**
     * Private utility to select a given sub menu, given the
     * corresponding html tag.
     * If such a sub menu does not exist - nothing happens
     */
    private void selectMenuItem(HTML.Tag tag) {
        Enumeration enum = group.getElements();

        while (enum.hasMoreElements()) {
            JRadioButtonMenuItem item = (JRadioButtonMenuItem) enum.nextElement();

            if (item.getActionCommand().equals(tag.toString())) {
                item.setSelected(true);

                return; // done
            }
        }
    }

    /**
     * Private utility to return the html tag corresponding to
     * a given string, e.g. p -> HTML.Tag.P
     * <br>
     * Strings / Tags are searched within STYLE_STRINGS
     * and STYLE_TAGS respectively. The search is case insensitive.
     *
     * @param        tagStr        String representation of tag, e.g. p or h1
     * @return        The corresponding Tag object or null if not found
     */
    public HTML.Tag getTagFromString(String tagStr) {
        for (int i = 0; i < STYLE_STRINGS.length; i++) {
            if (STYLE_STRINGS[i].equalsIgnoreCase(tagStr)) {
                // found
                return STYLE_TAGS[i];
            }
        }

        // not found
        return null;
    }

    /* (non-Javadoc)
     * @see java.awt.event.ActionListener#actionPerformed(java.awt.event.ActionEvent)
     */
    public void actionPerformed(ActionEvent arg0) {
        HtmlEditorController ctrl = (HtmlEditorController) ((ComposerController) controller).getEditorController();

        // set paragraph formatting according to the given action
        String action = arg0.getActionCommand();
        HTML.Tag tag = getTagFromString(action);
        ctrl.setParagraphFormat(tag);
    }

    /**
     * This event could mean that a the editor controller has changed.
     * Therefore this object is re-registered as observer to keep
     * getting information about format changes.
     *
     * @see java.awt.event.ContainerListener#componentAdded(java.awt.event.ContainerEvent)
     */
    public void componentAdded(ContainerEvent e) {
        ColumbaLogger.log.debug(
            "Re-registering as observer on editor controller");
        ((ComposerController) getController()).getEditorController()
         .addObserver(this);
    }

    /* (non-Javadoc)
     * @see java.awt.event.ContainerListener#componentRemoved(java.awt.event.ContainerEvent)
     */
    public void componentRemoved(ContainerEvent e) {
    }
}