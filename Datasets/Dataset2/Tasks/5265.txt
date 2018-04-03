import org.columba.core.gui.frame.FrameController;

/*
 * Created on 11.03.2003
 *
 * To change this generated comment go to 
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
package org.columba.core.gui.action;

import java.awt.event.ActionEvent;
import java.net.MalformedURLException;
import java.net.URL;

import org.columba.core.action.FrameAction;
import org.columba.core.gui.FrameController;
import org.columba.mail.gui.util.URLController;
import org.columba.mail.util.MailResourceLoader;

/**
 * @author frd
 *
 * To change this generated comment go to 
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
public class ShowProjectPageAction extends FrameAction {

	/**
	 * @param frameController
	 * @param name
	 * @param longDescription
	 * @param actionCommand
	 * @param small_icon
	 * @param big_icon
	 * @param mnemonic
	 * @param keyStroke
	 */
	public ShowProjectPageAction(FrameController frameController) {
		super(
			frameController,
			MailResourceLoader.getString(
				"menu",
				"mainframe",
				"menu_help_sourceforge"),
			null,
			"SOURCEFORGE",
			null,
			null,
			'S',
			null);

	}

	/* (non-Javadoc)
	 * @see java.awt.event.ActionListener#actionPerformed(java.awt.event.ActionEvent)
	 */
	public void actionPerformed(ActionEvent evt) {
		URLController c = new URLController();
		try {
			c.open(new URL("http://www.sourceforge.net/projects/columba"));
		} catch (MalformedURLException mue) {
		}
	}

}