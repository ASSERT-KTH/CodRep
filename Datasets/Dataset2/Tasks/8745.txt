import org.columba.mail.resourceloader.MailImageLoader;

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

import java.awt.event.ActionEvent;
import java.awt.event.ContainerEvent;
import java.awt.event.ContainerListener;
import java.util.Observable;
import java.util.Observer;
import java.util.logging.Logger;

import javax.swing.text.StyleConstants;

import org.columba.api.gui.frame.IFrameMediator;
import org.columba.core.gui.action.AbstractSelectableAction;
import org.columba.core.xml.XmlElement;
import org.columba.mail.config.MailConfig;
import org.columba.mail.gui.composer.ComposerController;
import org.columba.mail.gui.composer.html.HtmlEditorController;
import org.columba.mail.gui.composer.html.util.FormatInfo;
import org.columba.mail.gui.util.MailImageLoader;
import org.columba.mail.util.MailResourceLoader;


/**
 * Right justify selected paragraph "align="right" in <p>-tag
 *
 * @author fdietz, Karl Peder Olesen (karlpeder)
 */
public class RightJustifyAction extends AbstractSelectableAction
    implements Observer, ContainerListener {

    /** JDK 1.4+ logging framework logger, used for logging. */
    private static final Logger LOG = Logger.getLogger("org.columba.mail.gui.composer.html.action");

    /**
     * @param frameMediator
     * @param name
     */
    public RightJustifyAction(IFrameMediator frameMediator) {
        super(frameMediator,
            MailResourceLoader.getString("menu", "composer",
                "menu_format_right_justify"));

        putValue(SHORT_DESCRIPTION,
            MailResourceLoader.getString("menu", "composer",
                "menu_format_right_justify_tooltip").replaceAll("&", ""));

        putValue(LARGE_ICON,
        		MailImageLoader.getIcon("format-justify-right.png"));
        putValue(SMALL_ICON,
        		MailImageLoader.getSmallIcon("format-justify-right.png"));

        // register for text selection changes
        ComposerController ctrl = (ComposerController) getFrameMediator();
        ctrl.getEditorController().addObserver(this);

        // register for changes to the editor
        ctrl.addContainerListenerForEditor(this);

        // register for changes to editor type (text / html)
        XmlElement optionsElement = MailConfig.getInstance().get("composer_options")
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
     * Method is called when text selection has changed.
     * <p>
     * Set state of togglebutton / -menu to pressed / not pressed
     * when selections change.
     *
     * @see java.util.Observer#update(java.util.Observable, java.lang.Object)
     */
    public void update(Observable arg0, Object arg1) {
        if (arg0 instanceof HtmlEditorController) {
            // check if current text is right aligned - and set state accordingly
            FormatInfo info = (FormatInfo) arg1;
            boolean isAlignRight = info.isAlignRight();

            // notify all observers to change their selection state
            setState(isAlignRight);
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

    /* (non-Javadoc)
     * @see java.awt.event.ActionListener#actionPerformed(java.awt.event.ActionEvent)
     */
    public void actionPerformed(ActionEvent evt) {
        // this action is disabled when the text/plain editor is used
        // -> so, its safe to just cast to HtmlEditorController here
        HtmlEditorController editorController = (HtmlEditorController) ((ComposerController) frameMediator).getEditorController();

        editorController.setAlignment(StyleConstants.ALIGN_RIGHT);
    }

    /**
     * This event could mean that a the editor controller has changed.
     * Therefore this object is re-registered as observer to keep
     * getting information about format changes.
     *
     * @see java.awt.event.ContainerListener#componentAdded(java.awt.event.ContainerEvent)
     */
    public void componentAdded(ContainerEvent e) {
        LOG.info("Re-registering as observer on editor controller");
        ((ComposerController) getFrameMediator()).getEditorController()
         .addObserver(this);
    }

    /* (non-Javadoc)
     * @see java.awt.event.ContainerListener#componentRemoved(java.awt.event.ContainerEvent)
     */
    public void componentRemoved(ContainerEvent e) {
    }
}