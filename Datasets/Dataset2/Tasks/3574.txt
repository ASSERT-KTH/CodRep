import org.columba.core.gui.frame.FrameController;

/*
 * Created on 12.03.2003
 *
 * To change this generated comment go to 
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
package org.columba.core.gui.menu;

import java.util.ListIterator;

import javax.swing.JMenuBar;

import org.columba.core.gui.FrameController;
import org.columba.core.xml.XmlElement;

/**
 * @author frd
 *
 * To change this generated comment go to 
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
public class MenuBarGenerator extends AbstractMenuGenerator {

	

	/**
	 * @param path
	 */
	public MenuBarGenerator(FrameController frameController, String path) {
		super(frameController, path);

	}

	public void createMenuBar( JMenuBar menuBar) {
		menuBar.removeAll();
		ListIterator it = getMenuRoot().getElements().listIterator();
		while (it.hasNext()) {
			menuBar.add(createMenu((XmlElement) it.next()));
		}
	}

	/* (non-Javadoc)
	 * @see org.columba.core.gui.AbstractMenuGenerator#getMenuRoot()
	 */
	public XmlElement getMenuRoot() {

		return xmlFile.getRoot().getElement("menubar");
	}

	/* (non-Javadoc)
	 * @see org.columba.core.gui.AbstractMenuGenerator#getRootElementName()
	 */
	public String getRootElementName() {
		return "menubar";
	}

	public void extendMenuFromFile(String path) {
		super.extendMenuFromFile(path);

	}

}