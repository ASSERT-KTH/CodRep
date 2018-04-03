import org.columba.core.gui.action.CCheckBoxMenuItem;

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
package org.columba.core.gui.menu;

import java.io.IOException;
import java.io.InputStream;
import java.util.Iterator;
import java.util.logging.Logger;

import javax.swing.JRadioButtonMenuItem;

import org.columba.api.exception.PluginException;
import org.columba.api.exception.PluginHandlerNotFoundException;
import org.columba.api.gui.frame.IFrameMediator;
import org.columba.api.plugin.IExtension;
import org.columba.core.gui.action.AbstractColumbaAction;
import org.columba.core.gui.action.AbstractSelectableAction;
import org.columba.core.gui.base.CCheckBoxMenuItem;
import org.columba.core.gui.base.CMenuItem;
import org.columba.core.logging.Logging;
import org.columba.core.plugin.PluginManager;
import org.columba.core.pluginhandler.ActionExtensionHandler;
import org.jdom.Document;
import org.jdom.Element;
import org.jdom.JDOMException;
import org.jdom.input.SAXBuilder;

/**
 * Generate menu from xml-file.
 * <p>
 * Translation of resources is mostly done in {@link AbstractColumbaAction},
 * for JMenuItem, JCheckboxMenuItem, JRadioButtonMenuItem. But, the menu names,
 * visible on the menubar and the popup menu name are translated here. This is
 * achieved by passing a {@link IFrameMediator} instance, and using its
 * <code>getString()</code> method to pass along the translation to the
 * appropriate resourceloader.
 * <p>
 * Example: <br/>
 * 
 * <pre>
 * ExtendablePopupMenu menu = new MenuXMLDecoder(frameController)
 * 		.createPopupMenu(&quot;org/columba/core/contextmenu.xml&quot;);
 * </pre>
 * 
 * @author fdietz
 * 
 */
public class MenuXMLDecoder {

	private static final String PLACEHOLDERID = "placeholderid";

	private static final Logger LOG = Logger
			.getLogger("org.columba.core.gui.menu");

	private static final String PLACEHOLDER = "placeholder";

	private static final String SEPARATOR = "separator";

	private static final String RADIOBUTTONMENUITEM = "radiobuttonmenuitem";

	private static final String CHECKBOXMENUITEM = "checkboxmenuitem";

	private static final String IMENU = "imenu";

	private static final String ID = "id";

	private static final String MENUITEM = "menuitem";

	private static final String MENU = "menu";

	private static final String MENUBAR = "menubar";

	private ActionExtensionHandler pluginHandler;

	private IFrameMediator mediator;

	public MenuXMLDecoder(IFrameMediator mediator) {
		super();

		this.mediator = mediator;

		try {
			pluginHandler = (ActionExtensionHandler) PluginManager
					.getInstance().getHandler(ActionExtensionHandler.NAME);
		} catch (PluginHandlerNotFoundException e) {
			e.printStackTrace();
		}
	}

	private AbstractColumbaAction getAction(String id, IFrameMediator controller) {
		if (id == null)
			throw new IllegalArgumentException("id == null");
		if (controller == null)
			throw new IllegalArgumentException("controller == null");

		IExtension extension = pluginHandler.getExtension(id);

		AbstractColumbaAction a = null;

		try {
			if (extension != null)
				a = (AbstractColumbaAction) extension
						.instanciateExtension(new Object[] { controller });
		} catch (Exception e) {
			LOG.severe(e.getMessage());
			if (Logging.DEBUG)
				e.printStackTrace();

		}

		return a;

	}

	private IMenu getIMenu(String id, IFrameMediator controller)
			throws Exception {
		IExtension extension = pluginHandler.getExtension(id);

		IMenu menu = null;
		try {
			menu = (IMenu) extension
					.instanciateExtension(new Object[] { controller });
		} catch (PluginException e) {
			e.printStackTrace();
		}

		return menu;
	}

	public ExtendablePopupMenu createPopupMenu(InputStream is) {
		Document doc = retrieveDocument(is);

		Element menuElement = doc.getRootElement();
		if (menuElement.getName().equals(MenuXMLDecoder.MENU) == false) {
			LOG.severe("root element <menu> expected");
			return null;
		}

		
		ExtendablePopupMenu menu = new ExtendablePopupMenu("id");
		parsePopupMenu(menu, menuElement);

		return menu;
	}

	public ExtendableMenuBar createMenuBar(InputStream is) {

		Document doc = retrieveDocument(is);

		Element menubarElement = doc.getRootElement();
		if (menubarElement.getName().equals(MenuXMLDecoder.MENUBAR) == false) {
			LOG.severe("root element <menubar> expected");
			return null;
		}

		ExtendableMenuBar menuBar = new ExtendableMenuBar();
		Iterator it = menubarElement.getChildren().listIterator();
		while (it.hasNext()) {
			Element menuElement = (Element) it.next();
			if (menuElement.getName().equals(MenuXMLDecoder.MENU)) {

				String menuId = menuElement
						.getAttributeValue(MenuXMLDecoder.ID);

				String menuName = mediator.getString("menu", "mainframe",
						menuId);

				ExtendableMenu menu = new ExtendableMenu(menuId, menuName);
				parseMenu(menu, menuElement);
				menuBar.add(menu);
			}
		}

		return menuBar;
	}

	/**
	 * @param xmlResource
	 * @return
	 */
	private Document retrieveDocument(InputStream is) {
		SAXBuilder builder = new SAXBuilder();
		builder.setIgnoringElementContentWhitespace(true);
		Document doc = null;
		try {
			doc = builder.build(is);
		} catch (JDOMException e) {
			LOG.severe(e.getMessage());
			e.printStackTrace();
		} catch (IOException e) {
			LOG.severe(e.getMessage());
			e.printStackTrace();
		}
		return doc;
	}

	private void parseMenu(ExtendableMenu parentMenu, Element parentElement) {
		Iterator it = parentElement.getChildren().listIterator();
		while (it.hasNext()) {
			Element menuElement = (Element) it.next();
			if (menuElement.getName().equals(MenuXMLDecoder.MENU)) {
				
				String menuId = menuElement
						.getAttributeValue(MenuXMLDecoder.ID);
				String menuName = mediator.getString("menu", "mainframe",
						menuId);

			
				ExtendableMenu menu = new ExtendableMenu(menuId, menuName);
				parseMenu(menu, menuElement);
				parentMenu.add(menu);
			} else if (menuElement.getName().equals(MenuXMLDecoder.MENUITEM)) {
				String id = menuElement.getAttributeValue(MenuXMLDecoder.ID);
				AbstractColumbaAction action = getAction(id, mediator);
				if ( action == null ) continue;
				
				CMenuItem menuItem = new CMenuItem(action);
				menuItem.addMouseListener(mediator.getMouseTooltipHandler());
				parentMenu.add(menuItem);
			} else if (menuElement.getName().equals(
					MenuXMLDecoder.CHECKBOXMENUITEM)) {
				String id = menuElement.getAttributeValue(MenuXMLDecoder.ID);
				AbstractSelectableAction action = (AbstractSelectableAction) getAction(
						id, mediator);
				if ( action == null ) continue;
				
				CCheckBoxMenuItem menuItem = new CCheckBoxMenuItem(action);
				menuItem.addMouseListener(mediator.getMouseTooltipHandler());
				parentMenu.add(menuItem);
			} else if (menuElement.getName().equals(
					MenuXMLDecoder.RADIOBUTTONMENUITEM)) {
				String id = menuElement.getAttributeValue(MenuXMLDecoder.ID);
				AbstractColumbaAction action = getAction(id, mediator);
				if ( action == null ) continue;
				
				JRadioButtonMenuItem menuItem = new JRadioButtonMenuItem(action);
				menuItem.addMouseListener(mediator.getMouseTooltipHandler());
				parentMenu.add(menuItem);
			} else if (menuElement.getName().equals(MenuXMLDecoder.SEPARATOR)) {
				parentMenu.addSeparator();
			} else if (menuElement.getName().equals(MenuXMLDecoder.IMENU)) {
				String id = menuElement.getAttributeValue(MenuXMLDecoder.ID);
				IMenu imenu;
				try {
					imenu = getIMenu(id, mediator);
					if ( imenu == null ) continue;
					
					parentMenu.add(imenu);
				} catch (Exception e) {
					LOG.severe(e.getMessage());
					if (Logging.DEBUG)
						e.printStackTrace();
				}
			} else if (menuElement.getName().equals(MenuXMLDecoder.PLACEHOLDER)) {
				String id = menuElement.getAttributeValue(MenuXMLDecoder.ID);
				parentMenu.addPlaceholder(id);
			}
		}

	}

	private void parsePopupMenu(ExtendablePopupMenu parentMenu,
			Element parentElement) {
		Iterator it = parentElement.getChildren().listIterator();
		while (it.hasNext()) {
			Element menuElement = (Element) it.next();
			if (menuElement.getName().equals(MenuXMLDecoder.MENU)) {
				
				String menuId = menuElement
						.getAttributeValue(MenuXMLDecoder.ID);
				String menuName = mediator.getString("menu", "mainframe",
						menuId);

			
				ExtendableMenu menu = new ExtendableMenu(menuId, menuName);
				parseMenu(menu, menuElement);
				parentMenu.add(menu);
			} else if (menuElement.getName().equals(MenuXMLDecoder.MENUITEM)) {
				String id = menuElement.getAttributeValue(MenuXMLDecoder.ID);
				AbstractColumbaAction action = getAction(id, mediator);
				CMenuItem menuItem = new CMenuItem(action);
				menuItem.addMouseListener(mediator.getMouseTooltipHandler());
				parentMenu.add(menuItem);
			} else if (menuElement.getName().equals(
					MenuXMLDecoder.CHECKBOXMENUITEM)) {
				String id = menuElement.getAttributeValue(MenuXMLDecoder.ID);
				AbstractSelectableAction action = (AbstractSelectableAction) getAction(
						id, mediator);
				CCheckBoxMenuItem menuItem = new CCheckBoxMenuItem(action);
				menuItem.addMouseListener(mediator.getMouseTooltipHandler());
				parentMenu.add(menuItem);
			} else if (menuElement.getName().equals(
					MenuXMLDecoder.RADIOBUTTONMENUITEM)) {
				String id = menuElement.getAttributeValue(MenuXMLDecoder.ID);
				AbstractColumbaAction action = getAction(id, mediator);
				JRadioButtonMenuItem menuItem = new JRadioButtonMenuItem(action);
				menuItem.addMouseListener(mediator.getMouseTooltipHandler());
				parentMenu.add(menuItem);
			} else if (menuElement.getName().equals(MenuXMLDecoder.SEPARATOR)) {
				parentMenu.addSeparator();
			} else if (menuElement.getName().equals(MenuXMLDecoder.IMENU)) {
				String id = menuElement.getAttributeValue(MenuXMLDecoder.ID);
				IMenu imenu;
				try {
					imenu = getIMenu(id, mediator);
					parentMenu.add(imenu);
				} catch (Exception e) {
					e.printStackTrace();
				}
			} else if (menuElement.getName().equals(MenuXMLDecoder.PLACEHOLDER)) {
				String id = menuElement.getAttributeValue(MenuXMLDecoder.ID);
				parentMenu.addPlaceholder(id);
			}
		}

	}

	/**
	 * Extend menubar from xml resource.
	 * 
	 * @param menubar
	 *            menubar
	 * @param xmlResource
	 *            xml resource to retrieve menu structure
	 */
	public void extendMenuBar(ExtendableMenuBar menubar, InputStream is) {
		Document doc = retrieveDocument(is);
		Element menubarElement = doc.getRootElement();
		if (menubarElement.getName().equals(MenuXMLDecoder.MENUBAR) == false) {
			LOG.severe("root element <menubar> expected");
			return;
		}

		Iterator it = menubarElement.getChildren().listIterator();
		while (it.hasNext()) {
			Element menuElement = (Element) it.next();
			if (menuElement.getName().equals(MenuXMLDecoder.MENU)) {
			
				String menuId = menuElement
						.getAttributeValue(MenuXMLDecoder.ID);
				String placeholderId = menuElement
						.getAttributeValue(MenuXMLDecoder.PLACEHOLDERID);

				String menuName = mediator.getString("menu", "mainframe",
						menuId);

				LOG.finest("menu:"+menuId);
				
			
				ExtendableMenu menu = menubar.getMenu(menuId);
				if (menu == null) {
					LOG.finest("--> creating new menu");
					// create new menu
					menu = new ExtendableMenu(menuId, menuName);
					menubar.insert(menu);
					parseMenu(menu, menuElement);
				} else {
					// extend existing menu
					extendMenu(menubar, menu, menuElement, placeholderId);
				}
			}
		}

	}

	public void extendMenu(ExtendableMenuBar menubar,
			ExtendableMenu parentMenu, Element parentElement,
			String placeholderId) {
		LOG.finest("current placeholder="+placeholderId);
		
		Iterator it = parentElement.getChildren().listIterator();
		while (it.hasNext()) {
			Element menuElement = (Element) it.next();
			if (menuElement.getName().equals(MenuXMLDecoder.MENU)) {
				
				String menuId = menuElement
						.getAttributeValue(MenuXMLDecoder.ID);
				String menuName = mediator.getString("menu", "mainframe",
						menuId);

				LOG.finest("menu="+menuId);
				
			
				ExtendableMenu menu = menubar.getMenu(menuId);
				if (menu == null) {
					// create new menu
					menu = new ExtendableMenu(menuId, menuName);
					parseMenu(menu, menuElement);
					parentMenu.insert(menu, placeholderId);
				} else {
					// extend existing menu
					extendMenu(menubar, menu, menuElement, placeholderId);
				}

			} else if (menuElement.getName().equals(MenuXMLDecoder.MENUITEM)) {
				String id = menuElement.getAttributeValue(MenuXMLDecoder.ID);
				LOG.finest("menuitem="+id);
				AbstractColumbaAction action = getAction(id, mediator);
				CMenuItem menuItem = new CMenuItem(action);
				menuItem.addMouseListener(mediator.getMouseTooltipHandler());
				parentMenu.insert(menuItem, placeholderId);
			} else if (menuElement.getName().equals(
					MenuXMLDecoder.CHECKBOXMENUITEM)) {
				String id = menuElement.getAttributeValue(MenuXMLDecoder.ID);
				AbstractSelectableAction action = (AbstractSelectableAction) getAction(
						id, mediator);
				CCheckBoxMenuItem menuItem = new CCheckBoxMenuItem(action);
				menuItem.addMouseListener(mediator.getMouseTooltipHandler());
				parentMenu.insert(menuItem, placeholderId);
			} else if (menuElement.getName().equals(
					MenuXMLDecoder.RADIOBUTTONMENUITEM)) {
				String id = menuElement.getAttributeValue(MenuXMLDecoder.ID);
				AbstractColumbaAction action = getAction(id, mediator);
				JRadioButtonMenuItem menuItem = new JRadioButtonMenuItem(action);
				menuItem.addMouseListener(mediator.getMouseTooltipHandler());
				parentMenu.insert(menuItem, placeholderId);
			} else if (menuElement.getName().equals(MenuXMLDecoder.SEPARATOR)) {
				parentMenu.insertSeparator(placeholderId);
			} else if (menuElement.getName().equals(MenuXMLDecoder.IMENU)) {
				String id = menuElement.getAttributeValue(MenuXMLDecoder.ID);
				IMenu imenu;
				try {
					imenu = getIMenu(id, mediator);
					parentMenu.insert(imenu, placeholderId);
				} catch (Exception e) {
					LOG.severe(e.getMessage());
					if (Logging.DEBUG)
						e.printStackTrace();
				}
			} else if (menuElement.getName().equals(MenuXMLDecoder.PLACEHOLDER)) {
				String id = menuElement.getAttributeValue(MenuXMLDecoder.ID);
				parentMenu.insertPlaceholder(id, placeholderId);
			}
		}
	}
}