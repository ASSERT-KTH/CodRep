import org.columba.core.pluginhandler.ActionPluginHandler;

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
package org.columba.core.gui.menu;

import org.columba.core.action.AbstractColumbaAction;
import org.columba.core.action.AbstractSelectableAction;
import org.columba.core.action.IMenu;
import org.columba.core.gui.frame.FrameMediator;
import org.columba.core.gui.util.NotifyDialog;
import org.columba.core.io.DiskIO;
import org.columba.core.main.MainInterface;
import org.columba.core.plugin.ActionPluginHandler;
import org.columba.core.util.GlobalResourceLoader;
import org.columba.core.xml.XmlElement;
import org.columba.core.xml.XmlIO;

import java.util.List;
import java.util.ListIterator;
import java.util.logging.Logger;

import javax.swing.JMenu;


/**
 * @author frd
 */
public abstract class AbstractMenuGenerator {

    private static final Logger LOG = Logger.getLogger("org.columba.core.gui.menu");

    protected XmlElement menuRoot;
    protected XmlIO xmlFile;
    protected FrameMediator frameController;

    /**
     *
     */
    public AbstractMenuGenerator(FrameMediator frameController, String path) {
        this.frameController = frameController;

        xmlFile = new XmlIO(DiskIO.getResourceURL(path));
        xmlFile.load();
    }

    public String getString(String sPath, String sName, String sID) {
        return GlobalResourceLoader.getString(sPath, sName, sID);
    }

    // XmlIO.getRoot().getElement("menubar");
    // or
    // XmlIO.getRoot().getElement("menu");
    public abstract XmlElement getMenuRoot();

    // this should be "menubar" or "menu"
    public abstract String getRootElementName();

    public void extendMenuFromFile(String path) {
        XmlIO menuXml = new XmlIO();
        menuXml.setURL(DiskIO.getResourceURL(path));
        menuXml.load();

        ListIterator iterator = menuXml.getRoot()
                                       .getElement(getRootElementName())
                                       .getElements().listIterator();

        while (iterator.hasNext()) {
            extendMenu((XmlElement) iterator.next());
        }
    }

    public void extendMenu(XmlElement menuExtension) {
        XmlElement menu;
        XmlElement extension;
        String menuName = menuExtension.getAttribute("name");
        String extensionName = menuExtension.getAttribute("extensionpoint");

        if (extensionName == null) {
            // new menu
            //
            // !!! Note that we don't append the new menu
            // we insert it before the second last menu in the menubar of core
            // as defined in "core.actions.menu.xml"
            // -> meaning before "Utilities" and "Help" and after "View"
            getMenuRoot().insertElement((XmlElement) menuExtension.clone(),
                getMenuRoot().count() - 2);

            return;
        }

        ListIterator iterator = getMenuRoot().getElements().listIterator();

        while (iterator.hasNext()) {
            menu = ((XmlElement) iterator.next());

            if (menu.getAttribute("name").equals(menuName)) {
                createExtension(menu, (XmlElement) menuExtension.clone(),
                    extensionName);
            }
        }
    }

    private void createExtension(XmlElement menu, XmlElement menuExtension,
        String extensionName) {
        XmlElement extension;
        int insertIndex = 0;

        ListIterator iterator;

        iterator = menu.getElements().listIterator();

        while (iterator.hasNext()) {
            extension = ((XmlElement) iterator.next());

            if (extension.getName().equals("extensionpoint")) {
                if (extension.getAttribute("name").equals(extensionName)) {
                    int size = menuExtension.count();

                    if (size > 0) {
                        menu.insertElement(new XmlElement("separator"),
                            insertIndex);
                    }

                    for (int i = 0; i < size; i++) {
                        menu.insertElement(menuExtension.getElement(0),
                            insertIndex + i + 1);
                    }

                    if (size > 0) {
                        menu.insertElement(new XmlElement("separator"),
                            insertIndex + size + 1);
                    }

                    return;
                }
            } else if (extension.getName().equals("menu")) {
                createExtension(extension, menuExtension, extensionName);
            }

            insertIndex++;
        }
    }

    protected JMenu createMenu(XmlElement menuElement) {
        List childs = menuElement.getElements();
        ListIterator it = childs.listIterator();

        // *20031004, karlpeder* Changed from JMenu to CMenu to support mnemonics
        CMenu menu = new CMenu(getString("menu", "mainframe",
                    menuElement.getAttribute("name")));

        createMenuEntries(menu, it);

        return menu;
    }

    protected void createMenuEntries(JMenu menu, ListIterator it) {
        boolean lastWasSeparator = false;

        while (it.hasNext()) {
            XmlElement next = (XmlElement) it.next();
            String name = next.getName();

            if (name.equals("menuitem")) {
                if (next.getAttribute("action") != null) {
                    try {
                        AbstractColumbaAction action = ((ActionPluginHandler) MainInterface.pluginManager.getHandler(
                                "org.columba.core.action")).getAction(next.getAttribute(
                                    "action"), frameController);

                        if (action != null) {
                            // use our custom CMenuItem here
                            // -> in order to support JavaHelp support
                            // -> @see CMenuItem for more details
                            CMenuItem tmp = new CMenuItem(action);

                            // display tooltip in statusbar
                            tmp.addMouseListener(frameController.getMouseTooltipHandler());
                            menu.add(tmp);
                            lastWasSeparator = false;
                        }
                    } catch (Exception e) {
                        NotifyDialog dialog = new NotifyDialog();
                        dialog.showDialog("Error while loading plugin "
                                + next.getAttribute("action")
                                + ". This probably means that the class wasn't found. Compile the plugin to create it.");

                        if (MainInterface.DEBUG) {
                            LOG.severe(e.getMessage() + ": " + next.getAttribute("action"));
                            e.printStackTrace();
                        }
                    }
                } else if (next.getAttribute("checkboxaction") != null) {
                    try {
                        AbstractSelectableAction action = (AbstractSelectableAction) ((ActionPluginHandler) MainInterface.pluginManager.getHandler(
                                "org.columba.core.action")).getAction(next.getAttribute(
                                    "checkboxaction"), frameController);

                        if (action != null) {
                            CCheckBoxMenuItem menuitem = new CCheckBoxMenuItem(action);

                            // display tooltip in statusbar
                            menuitem.addMouseListener(frameController.getMouseTooltipHandler());
                            menu.add(menuitem);

                            lastWasSeparator = false;
                        }
                    } catch (Exception e) {
                        LOG.severe(e.getMessage() + " - " + next.getAttribute("checkboxaction"));
                        e.printStackTrace();
                    }
                } else if (next.getAttribute("imenu") != null) {
                    try {
                        IMenu imenu = ((ActionPluginHandler) MainInterface.pluginManager.getHandler(
                                "org.columba.core.action")).getIMenu(next.getAttribute(
                                    "imenu"), frameController);

                        if (imenu != null) {
                            menu.add(imenu);
                        }

                        lastWasSeparator = false;
                    } catch (Exception e) {
                        e.printStackTrace();
                        LOG.severe(e.getMessage());
                    }
                }
            } else if (name.equals("separator")) {
                if (!lastWasSeparator) {
                    menu.addSeparator();
                }

                lastWasSeparator = true;
            } else if (name.equals("menu")) {
                menu.add(createSubMenu(next));
                lastWasSeparator = false;
            }
        }

        if (lastWasSeparator) {
            menu.remove(menu.getMenuComponentCount() - 1);
        }
    }

    protected JMenu createSubMenu(XmlElement menuElement) {
        List childs = menuElement.getElements();
        ListIterator it = childs.listIterator();

        CMenu menu = new CMenu(getString("menu", "mainframe",
                    menuElement.getAttribute("name")));

        createMenuEntries(menu, it);

        return menu;
    }
}