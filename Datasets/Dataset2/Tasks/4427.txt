if (f instanceof VirtualFolder && f.getUid() != 106 && ((IMailFolder)f.getParent()).getUid() != 106) {

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
package org.columba.mail.folder.virtual;

import java.text.MessageFormat;
import java.util.ArrayList;
import java.util.List;

import org.columba.api.command.ICommandReference;
import org.columba.api.command.IWorkerStatusController;
import org.columba.core.command.Command;
import org.columba.core.command.CommandProcessor;
import org.columba.core.folder.IFolderCommandReference;
import org.columba.mail.command.MailFolderCommandReference;
import org.columba.mail.folder.FolderChildrenIterator;
import org.columba.mail.folder.IMailFolder;
import org.columba.mail.util.MailResourceLoader;

public class ActivateVirtualFolderCommand extends Command {

	public ActivateVirtualFolderCommand(ICommandReference reference) {
		super(reference);
	}

	public void execute(IWorkerStatusController worker) throws Exception {
		VirtualFolder vFolder = (VirtualFolder) ((IFolderCommandReference) getReference())
				.getSourceFolder();

		worker.setDisplayText(MessageFormat.format(MailResourceLoader
				.getString("statusbar", "message", "activate_vfolder"),
				new Object[] { vFolder.getName() }));

		vFolder.activate();
	}

	public static void activateAll(IMailFolder root) {
		// Find all VirtualFolders and rewrite the FolderReference
		FolderChildrenIterator it = new FolderChildrenIterator(root);

		// Put all VirtualFolders in one list
		List vfolderList = new ArrayList();

		while (it.hasMoreChildren()) {
			IMailFolder f = it.nextChild();
			if (f instanceof VirtualFolder) {
				CommandProcessor.getInstance().addOp(
						new ActivateVirtualFolderCommand(
								new MailFolderCommandReference(f)));
			}
		}

	}

}