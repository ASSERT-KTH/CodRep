ColumbaLogger.log.fine("converting configuration to new version...");

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
package org.columba.mail.config;

import org.columba.core.config.DefaultXmlConfig;
import org.columba.core.config.GuiItem;
import org.columba.core.config.TableItem;
import org.columba.core.config.ViewItem;
import org.columba.core.config.WindowItem;
import org.columba.core.logging.ColumbaLogger;
import org.columba.core.xml.XmlElement;

import java.io.File;


public class MainFrameOptionsXmlConfig extends DefaultXmlConfig {
    // private File file;
    WindowItem windowItem;
    GuiItem guiItem;
    TableItem headerTableItem;
    ViewItem viewItem;
    boolean initialVersionWasApplied = false;

    public MainFrameOptionsXmlConfig(File file) {
        super(file);
    }

    public boolean load() {
        boolean result = super.load();

        //		apply initial version information
        XmlElement root = getRoot().getElement(0);
        String version = root.getAttribute("version");

        if (version == null) {
            initialVersionWasApplied = true;
            root.addAttribute("version", "1.0");
        }

        convert();

        return result;
    }

    protected void convert() {
        // add initial messageframe treenode
        XmlElement root = getRoot();
        String version = root.getAttribute("version");

        if (initialVersionWasApplied) {
            ColumbaLogger.log.info("converting configuration to new version...");

            XmlElement gui = root.getElement("/options/gui");
            XmlElement messageframe = new XmlElement("messageframe");
            gui.addElement(messageframe);

            XmlElement view = new XmlElement("view");
            messageframe.addElement(view);
            view.addAttribute("id", "messageframe");

            XmlElement window = new XmlElement("window");
            window.addAttribute("width", "640");
            window.addAttribute("height", "480");
            window.addAttribute("maximized", "true");
            view.addElement(window);

            XmlElement toolbars = new XmlElement("toolbars");
            toolbars.addAttribute("main", "true");
            view.addElement(toolbars);

            XmlElement splitpanes = new XmlElement("splitpanes");
            splitpanes.addAttribute("main", "200");
            splitpanes.addAttribute("header", "200");
            splitpanes.addAttribute("attachment", "100");
            view.addElement(splitpanes);
        }
    }

    public TableItem getTableItem() {
        if (headerTableItem == null) {
            headerTableItem = new TableItem(getRoot().getElement("/options/gui/table"));
        }

        return headerTableItem;
    }

    public ViewItem getViewItem() {
        if (viewItem == null) {
            viewItem = new ViewItem(getRoot().getElement("/options/gui/viewlist/view"));
        }

        return viewItem;
    }

    public GuiItem getGuiItem() {
        if (guiItem == null) {
            guiItem = new GuiItem(getRoot().getElement("/options/gui"));
        }

        return guiItem;
    }

    public WindowItem getWindowItem() {
        if (windowItem == null) {
            windowItem = new WindowItem(getRoot().getElement("/options/gui/viewlist/view/window"));
        }

        return windowItem;
    }
}