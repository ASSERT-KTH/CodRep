import org.columba.core.gui.frame.FrameController;

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

import org.columba.core.action.ActionPluginHandler;
import org.columba.core.action.BasicAction;
import org.columba.core.action.CheckBoxAction;
import org.columba.core.gui.FrameController;
import org.columba.core.gui.util.CMenu;
import org.columba.core.io.DiskIO;
import org.columba.core.logging.ColumbaLogger;
import org.columba.core.main.MainInterface;
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
	protected FrameController frameController;

	/**
	 * 
	 */
	public AbstractMenuGenerator(
		FrameController frameController,
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

		int insertIndex = 0;

		while (iterator.hasNext()) {
			menu = ((XmlElement) iterator.next());
			if (menu.getAttribute("name").equals(menuName)) {

				iterator = menu.getElements().listIterator();
				while (iterator.hasNext()) {
					extension = ((XmlElement) iterator.next());
					if (extension.getName().equals("extensionpoint")) {
						if (extension
							.getAttribute("name")
							.equals(extensionName)) {
							int size = menuExtension.count();
							for (int i = 0; i < size; i++) {
								menu.insertElement(
									menuExtension.getElement(0),
									insertIndex + i);
							}
							return;
						}
					}
					insertIndex++;
				}
			}
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

						menu.add(action);

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
						JCheckBoxMenuItem menuitem =
							new JCheckBoxMenuItem(action);
						menu.add(menuitem);
						action.setCheckBoxMenuItem(menuitem);
					} catch (Exception e) {
						ColumbaLogger.log.error(e);
					}
				} else if (next.getAttribute("imenu") != null) {
					try {
						menu.add(
							(
								(
									ActionPluginHandler) MainInterface
										.pluginManager
										.getHandler(
									"org.columba.core.action")).getIMenu(
								next.getAttribute("imenu"),
								frameController));
					} catch (Exception e) {
						ColumbaLogger.log.error(e);
					}
				}

			} else if (name.equals("separator")) {

				menu.addSeparator();

			} else if (name.equals("menu")) {
				menu.add(createSubMenu(next));
			}
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