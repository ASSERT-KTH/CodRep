final ComposerController composerController = (ComposerController ) getFrameMediator();

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

package org.columba.mail.gui.composer.action;

import java.awt.event.ActionEvent;

import org.columba.core.action.FrameAction;
import org.columba.core.gui.frame.AbstractFrameController;
import org.columba.core.gui.util.ImageLoader;
import org.columba.core.main.MainInterface;
import org.columba.mail.command.ComposerCommandReference;
import org.columba.mail.config.AccountItem;
import org.columba.mail.config.SpecialFoldersItem;
import org.columba.mail.folder.Folder;
import org.columba.mail.gui.composer.ComposerController;
import org.columba.mail.gui.composer.ComposerModel;
import org.columba.mail.gui.composer.command.SaveMessageCommand;
import org.columba.mail.main.MailInterface;
import org.columba.mail.util.MailResourceLoader;

/**
 * @author frd
 *
 * To change this generated comment go to 
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
public class SaveAsTemplateAction extends FrameAction {

	public SaveAsTemplateAction(AbstractFrameController frameController) {
		super(
				frameController,
				MailResourceLoader.getString(
					"menu", "composer", "menu_file_savetemplate"));
		
		// tooltip text
		setTooltipText(
				MailResourceLoader.getString(
					"menu", "composer", "menu_file_savetemplate"));
		
		setSmallIcon(ImageLoader.getSmallImageIcon("stock_news.png"));
		
		// action command
		setActionCommand("SAVETEMPLATE");
		
	}

	/* (non-Javadoc)
	 * @see java.awt.event.ActionListener#actionPerformed(java.awt.event.ActionEvent)
	 */
	public void actionPerformed(ActionEvent evt) {
		
		final ComposerController composerController = (ComposerController ) getFrameController();
		if (composerController.checkState())
			return;

		AccountItem item =
		((ComposerModel)composerController.getModel()).getAccountItem();
		SpecialFoldersItem folderItem = item.getSpecialFoldersItem();
		String str = folderItem.get("templates");
		int destUid = Integer.parseInt(str);
		Folder destFolder = (Folder) MailInterface.treeModel.getFolder(destUid);

		ComposerCommandReference[] r = new ComposerCommandReference[1];
		r[0] = new ComposerCommandReference(
				composerController,
				destFolder);

		SaveMessageCommand c = new SaveMessageCommand(r);

		MainInterface.processor.addOp(c);
	}
}