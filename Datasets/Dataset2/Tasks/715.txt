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
package org.columba.core.config;

import org.columba.core.logging.ColumbaLogger;
import org.columba.core.xml.XmlElement;

import java.io.File;


public class OptionsXmlConfig extends DefaultXmlConfig {
    //private File file;
    protected ThemeItem themeItem;
    GuiItem guiItem;
    boolean initialVersionWasApplied = false;

    public OptionsXmlConfig(File file) {
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
        // rename "Mail" to "ThreePaneMail
        XmlElement root = getRoot();
        String version = root.getAttribute("version");

        if (initialVersionWasApplied) {
            ColumbaLogger.log.info("converting configuration to new version...");

            XmlElement viewlist = root.getElement("/options/gui/viewlist");

            for (int i = 0; i < viewlist.count(); i++) {
                XmlElement view = viewlist.getElement(i);

                if (view.getAttribute("id").equals("Mail")) {
                    view.addAttribute("id", "ThreePaneMail");
                }
            }
        }
    }

    public GuiItem getGuiItem() {
        if (guiItem == null) {
            guiItem = new GuiItem(getRoot().getElement("/options/gui"));
        }

        return guiItem;
    }

    public ThemeItem getThemeItem() {
        if (themeItem == null) {
            themeItem = new ThemeItem(getRoot().getElement("/options/gui/theme"));
        }

        return themeItem;
    }

    public XmlElement getMimeTypeNode() {
        XmlElement mimeTypes = getRoot().getElement("/options/mimetypes");

        if (mimeTypes == null) {
            getRoot().getElement("options").addElement(new XmlElement(
                    "mimetypes"));
            mimeTypes = getRoot().getElement("/options/mimetypes");
        }

        return mimeTypes;
    }
}