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
import javax.swing.JPopupMenu;

import org.columba.core.action.ActionPluginHandler;
import org.columba.core.action.BasicAction;
import org.columba.core.action.CheckBoxAction;
import org.columba.core.gui.FrameController;
import org.columba.core.logging.ColumbaLogger;
import org.columba.core.main.MainInterface;
import org.columba.core.xml.XmlElement;

/**
 * @author frd
 *
 * To change this generated comment go to 
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
public class PopupMenuGenerator extends AbstractMenuGenerator {

	/**
	 * @param frameController
	 * @param path
	 */
	public PopupMenuGenerator(FrameController frameController, String path) {
		super(frameController, path);

	}

	public void createPopupMenu(JPopupMenu menu) {
		menu.removeAll();
		createPopupMenu(getMenuRoot(), menu);

	}

	/* (non-Javadoc)
	 * @see org.columba.core.gui.AbstractMenuGenerator#getMenuRoot()
	 */
	public XmlElement getMenuRoot() {

		return xmlFile.getRoot().getElement("menu");
	}

	/* (non-Javadoc)
	 * @see org.columba.core.gui.AbstractMenuGenerator#getRootElementName()
	 */
	public String getRootElementName() {
		return "menu";
	}

	protected JPopupMenu createPopupMenu(
		XmlElement menuElement,
		JPopupMenu menu) {
		List childs = menuElement.getElements();
		ListIterator it = childs.listIterator();

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
				menu.add(createMenu(next));
			}
		}

		return menu;
	}

}