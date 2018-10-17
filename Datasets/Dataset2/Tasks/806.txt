ColumbaLogger.log.info("toolbar-button=" +

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
package org.columba.core.gui.toolbar;

import org.columba.core.action.AbstractColumbaAction;
import org.columba.core.gui.frame.FrameMediator;
import org.columba.core.gui.statusbar.ImageSequenceTimer;
import org.columba.core.logging.ColumbaLogger;
import org.columba.core.main.MainInterface;
import org.columba.core.plugin.ActionPluginHandler;
import org.columba.core.xml.XmlElement;

import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;

import java.util.ListIterator;
import java.util.ResourceBundle;

import javax.swing.Box;
import javax.swing.JToolBar;


/**
 * Toolbar which uses xml files to generate itself.
 * <p>
 * TODO: separate code which creates the toolbar from
 * the swing JToolBar.
 *
 * @author fdietz
 */
public class ToolBar extends JToolBar {
    ResourceBundle toolbarLabels;
    GridBagConstraints gridbagConstraints;
    GridBagLayout gridbagLayout;
    int i;
    XmlElement rootElement;

    //XmlIO xmlFile;
    FrameMediator frameController;

    public ToolBar(XmlElement rootElement, FrameMediator controller) {
        super();
        this.frameController = controller;

        this.rootElement = rootElement;

        createButtons();

        setRollover(true);

        setFloatable(false);
    }

    public boolean getVisible() {
        return Boolean.valueOf(rootElement.getAttribute("visible"))
                      .booleanValue();
    }

    private void createButtons() {
        removeAll();

        ListIterator iterator = rootElement.getElements().listIterator();
        XmlElement buttonElement = null;

        while (iterator.hasNext()) {
            try {
                buttonElement = (XmlElement) iterator.next();

                if (buttonElement.getName().equals("button")) {
                    addButton(((ActionPluginHandler) MainInterface.pluginManager.getHandler(
                            "org.columba.core.action")).getAction(
                            buttonElement.getAttribute("action"),
                            frameController));
                } else if (buttonElement.getName().equals("separator")) {
                    addSeparator();
                }
            } catch (Exception e) {
                ColumbaLogger.log.debug("toolbar-button=" +
                    ((String) buttonElement.getAttribute("action")));

                e.printStackTrace();
            }
        }

        add(Box.createHorizontalGlue());

        ImageSequenceTimer image = frameController.getStatusBar()
                                                  .getImageSequenceTimer();
        add(image);
    }

    public void addButton(AbstractColumbaAction action) {
        ToolbarButton button = new ToolbarButton(action);
        button.setRolloverEnabled(true);

        add(button);
    }
}