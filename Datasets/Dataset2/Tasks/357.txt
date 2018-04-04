import org.columba.core.main.MainInterface;

package org.columba.mail.plugin;

import org.columba.core.xml.XmlElement;
import org.columba.mail.config.MailConfig;
import org.columba.mail.gui.composer.ComposerController;
import org.columba.mail.gui.tree.util.SelectFolderDialog;
import org.columba.main.MainInterface;

/**
 * @author freddy
 *
 * To change this generated comment edit the template variable "typecomment":
 * Window>Preferences>Java>Templates.
 * To enable and disable the creation of type comments go to
 * Window>Preferences>Java>Code Generation.
 */
public class MailDecorator {

	/**
	 * Constructor for MailDecorator.
	 */
	public MailDecorator() {
		super();
	}

	public static XmlElement getConfigElement(String configName) {
		XmlElement root = MailConfig.get(configName);

		return root;
	}
	
	public static void openComposer()
	{
		ComposerController c = new ComposerController();
		c.showComposerWindow();
	}
	
	public SelectFolderDialog getSelectFolderDialog()
	{
		return MainInterface.treeModel.getSelectFolderDialog();
	}
	
}