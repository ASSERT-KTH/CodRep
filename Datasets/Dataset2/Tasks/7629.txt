ColumbaLogger.log.error(e + ": "+ next.getAttribute("action"));

/*
 * Created on 12.03.2003
 *
 * To change this generated comment go to
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
package org.columba.core.gui.menu;

import java.util.List;
import java.util.ListIterator;

import javax.swing.JCheckBoxMenuItem;
import javax.swing.JMenu;

import org.columba.core.action.BasicAction;
import org.columba.core.action.CheckBoxAction;
import org.columba.core.action.IMenu;
import org.columba.core.gui.frame.AbstractFrameController;
import org.columba.core.gui.util.CMenu;
import org.columba.core.io.DiskIO;
import org.columba.core.logging.ColumbaLogger;
import org.columba.core.main.MainInterface;
import org.columba.core.plugin.ActionPluginHandler;
import org.columba.core.util.GlobalResourceLoader;
import org.columba.core.xml.XmlElement;
import org.columba.core.xml.XmlIO;

/**
 * @author frd
 *
 * To change this generated comment go to
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
public abstract class AbstractMenuGenerator {

	protected XmlElement menuRoot;
	protected XmlIO xmlFile;
	protected AbstractFrameController frameController;

	/**
	 *
	 */
	public AbstractMenuGenerator(
		AbstractFrameController frameController,
		String path) {
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

		ListIterator iterator =
			menuXml
				.getRoot()
				.getElement(getRootElementName())
				.getElements()
				.listIterator();
		while (iterator.hasNext()) {
			extendMenu((XmlElement) iterator.next());
		}

	}

	public void extendMenu(XmlElement menuExtension) {

		XmlElement menu, extension;
		String menuName = menuExtension.getAttribute("name");
		String extensionName = menuExtension.getAttribute("extensionpoint");
		if (extensionName == null) {
			// new menu
			getMenuRoot().insertElement(
				(XmlElement) menuExtension.clone(),
				getMenuRoot().count() - 1);
			return;
		}

		ListIterator iterator = getMenuRoot().getElements().listIterator();
		while (iterator.hasNext()) {
			menu = ((XmlElement) iterator.next());
			if (menu.getAttribute("name").equals(menuName)) {
				createExtension(
					menu,
					(XmlElement) menuExtension.clone(),
					extensionName);
			}
		}

	}

	private void createExtension(
		XmlElement menu,
		XmlElement menuExtension,
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
					if (size > 0)
						menu.insertElement(
							new XmlElement("separator"),
							insertIndex);
					for (int i = 0; i < size; i++) {
						menu.insertElement(
							menuExtension.getElement(0),
							insertIndex + i + 1);
					}
					if (size > 0)
						menu.insertElement(
							new XmlElement("separator"),
							insertIndex + size + 1);
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

		JMenu menu =
			new JMenu(
				getString(
					"menu",
					"mainframe",
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
						BasicAction action =
							(
								(
									ActionPluginHandler) MainInterface
										.pluginManager
										.getHandler(
									"org.columba.core.action")).getAction(
								next.getAttribute("action"),
								frameController);
						if (action != null) {
							menu.add(action);
							lastWasSeparator = false;
						}

					} catch (Exception e) {
						ColumbaLogger.log.error(e);
					}
				} else if (next.getAttribute("checkboxaction") != null) {
					try {
						CheckBoxAction action =
							(CheckBoxAction)
								(
									(
										ActionPluginHandler) MainInterface
											.pluginManager
											.getHandler(
										"org.columba.core.action")).getAction(
								next.getAttribute("checkboxaction"),
								frameController);
						if (action != null) {
							JCheckBoxMenuItem menuitem =
								new JCheckBoxMenuItem(action);
							menu.add(menuitem);
							action.setCheckBoxMenuItem(menuitem);
							lastWasSeparator = false;
						}
					} catch (Exception e) {
						ColumbaLogger.log.error(e+" - "+ next.getAttribute("checkboxaction"));
					}
				} else if (next.getAttribute("imenu") != null) {
					try {
						IMenu imenu =
							(
								(
									ActionPluginHandler) MainInterface
										.pluginManager
										.getHandler(
									"org.columba.core.action")).getIMenu(
								next.getAttribute("imenu"),
								frameController);
					
						if ( imenu != null )
							menu.add(imenu);

						lastWasSeparator = false;

					} catch (Exception e) {
						e.printStackTrace();
						ColumbaLogger.log.error(e);
					}
				}

			} else if (name.equals("separator")) {
				if (!lastWasSeparator)
					menu.addSeparator();

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

		CMenu menu =
			new CMenu(
				getString(
					"menu",
					"mainframe",
					menuElement.getAttribute("name")));

		createMenuEntries(menu, it);

		return menu;
	}

}