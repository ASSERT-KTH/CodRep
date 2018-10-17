import org.columba.core.gui.frame.FrameController;

/*
 * Created on 26.03.2003
 *
 * To change this generated comment go to 
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
package org.columba.addressbook.gui.menu;

import org.columba.addressbook.util.AddressbookResourceLoader;
import org.columba.core.gui.FrameController;
import org.columba.core.gui.menu.MenuBarGenerator;

/**
 * @author frd
 *
 * To change this generated comment go to 
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
public class AddressbookMenuBarGenerator extends MenuBarGenerator {

	/**
	 * @param frameController
	 * @param path
	 */
	public AddressbookMenuBarGenerator(
		FrameController frameController,
		String path) {
		super(frameController, path);

	}

	/* (non-Javadoc)
		 * @see org.columba.core.gui.menu.AbstractMenuGenerator#getString(java.lang.String, java.lang.String, java.lang.String)
		 */
	public String getString(String sPath, String sName, String sID) {

		return AddressbookResourceLoader.getString(sPath, sName, sID);
	}

}