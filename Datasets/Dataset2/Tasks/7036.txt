import org.columba.core.gui.frame.FrameController;

/*
 * Created on 12.03.2003
 *
 * To change this generated comment go to 
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
package org.columba.mail.gui.tree;

import javax.swing.JPopupMenu;

import org.columba.core.gui.FrameController;
import org.columba.core.gui.menu.PopupMenuGenerator;
import org.columba.core.xml.XmlElement;

/**
 * @author frd
 *
 * To change this generated comment go to 
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
public class TreeMenu extends JPopupMenu {

	protected PopupMenuGenerator menuGenerator;
	protected FrameController frameController;

	/**
	 * 
	 */
	public TreeMenu(FrameController frameController) {
		this.frameController = frameController;

		menuGenerator =
			new PopupMenuGenerator(
				frameController,
				"org/columba/mail/action/tree_contextmenu.xml");
		menuGenerator.createPopupMenu(this);
	}

	public void extendMenuFromFile(String path) {
		menuGenerator.extendMenuFromFile(path);
		menuGenerator.createPopupMenu(this);
	}

	public void extendMenu(XmlElement menuExtension) {
		menuGenerator.extendMenu(menuExtension);
	}

}