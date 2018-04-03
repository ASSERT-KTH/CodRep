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
import org.columba.core.gui.frame.FrameMediator;
import org.columba.core.gui.util.NotifyDialog;
import org.columba.core.main.MainInterface;
import org.columba.core.plugin.ActionPluginHandler;
import org.columba.core.xml.XmlElement;

import java.util.List;
import java.util.ListIterator;
import java.util.logging.Logger;

import javax.swing.JCheckBoxMenuItem;
import javax.swing.JPopupMenu;


/**
 * @author frd
 *
 * To change this generated comment go to Window>Preferences>Java>Code
 * Generation>Code and Comments
 */
public class PopupMenuGenerator extends AbstractMenuGenerator {

    private static final Logger LOG = Logger.getLogger("org.columba.core.gui.menu");

    /**
     * @param frameMediator
     * @param path
     */
    public PopupMenuGenerator(FrameMediator frameController, String path) {
        super(frameController, path);
    }

    public void createPopupMenu(JPopupMenu menu) {
        menu.removeAll();
        createPopupMenu(getMenuRoot(), menu);
    }

    /*
     * (non-Javadoc)
     *
     * @see org.columba.core.gui.AbstractMenuGenerator#getMenuRoot()
     */
    public XmlElement getMenuRoot() {
        return xmlFile.getRoot().getElement("menu");
    }

    /*
     * (non-Javadoc)
     *
     * @see org.columba.core.gui.AbstractMenuGenerator#getRootElementName()
     */
    public String getRootElementName() {
        return "menu";
    }

    protected JPopupMenu createPopupMenu(XmlElement menuElement, JPopupMenu menu) {
        List childs = menuElement.getElements();
        ListIterator it = childs.listIterator();

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
                            //use our custom CMenuItem here
                            // -> in order to support JavaHelp support
                            // -> @see CMenuItem for more details
                            CMenuItem tmp = new CMenuItem(action);

                            // display tooltip in statusbar
                            tmp.addMouseListener(frameController.getMouseTooltipHandler());
                            menu.add(tmp);
                            menu.add(tmp);
                        }
                    } catch (Exception e) {
                        NotifyDialog dialog = new NotifyDialog();
                        dialog.showDialog("Error while loading plugin "
                                + next.getAttribute("action")
                                + ". This probably means that the class wasn't found. Compile the plugin to create it.");

                        if (MainInterface.DEBUG) {
                            LOG.severe(e + ": " + next.getAttribute("action"));
                            e.printStackTrace();
                        }
                    }
                } else if (next.getAttribute("checkboxaction") != null) {
                    try {
                        AbstractSelectableAction action = (AbstractSelectableAction) ((ActionPluginHandler) MainInterface.pluginManager.getHandler(
                                "org.columba.core.action")).getAction(next.getAttribute(
                                    "checkboxaction"), frameController);
                        JCheckBoxMenuItem menuitem = new JCheckBoxMenuItem(action);

                        // display tooltip in statusbar
                        menuitem.addMouseListener(frameController.getMouseTooltipHandler());
                        menu.add(menuitem);
                    } catch (Exception e) {
                        e.printStackTrace();
                        LOG.severe(e.getMessage());
                    }
                } else if (next.getAttribute("imenu") != null) {
                    try {
                        menu.add(((ActionPluginHandler) MainInterface.pluginManager.getHandler(
                                "org.columba.core.action")).getIMenu(
                                next.getAttribute("imenu"), frameController));
                    } catch (Exception e) {
                        e.printStackTrace();
                        LOG.severe(e.getMessage());
                    }
                }
            } else if (name.equals("separator")) {
                menu.addSeparator();
            } else if (name.equals("menu")) {
                menu.add(createSubMenu(next));
            }
        }

        return menu;
    }
}