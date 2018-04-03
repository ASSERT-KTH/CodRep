import org.columba.core.main.MainInterface;

package org.columba.mail.filter.plugins;

import org.columba.core.command.Command;
import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.filter.FilterAction;
import org.columba.mail.folder.Folder;
import org.columba.mail.folder.command.ExpungeFolderCommand;
import org.columba.mail.folder.command.MarkMessageCommand;
import org.columba.main.MainInterface;

/**
 * @author freddy
 *
 * To change this generated comment edit the template variable "typecomment":
 * Window>Preferences>Java>Templates.
 * To enable and disable the creation of type comments go to
 * Window>Preferences>Java>Code Generation.
 */
public class DeleteMessageAction extends AbstractFilterAction {

	

	/**
	 * @see org.columba.modules.mail.filter.action.AbstractFilterAction#execute()
	 */
	public Command getCommand( FilterAction filterAction, Folder srcFolder, Object[] uids) throws Exception {
		FolderCommandReference[] r = new FolderCommandReference[1];
		r[0] = new FolderCommandReference(srcFolder, uids);
		r[0].setMarkVariant(MarkMessageCommand.MARK_AS_EXPUNGED);

		MarkMessageCommand c = new MarkMessageCommand( r);

		MainInterface.processor.addOp(c);

		r = new FolderCommandReference[1];
		r[0] = new FolderCommandReference(srcFolder);

		return new ExpungeFolderCommand(r);
	}

}