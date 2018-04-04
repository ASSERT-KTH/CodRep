import org.columba.core.main.MainInterface;

package org.columba.mail.gui.composer.command;

import org.columba.core.command.DefaultCommandReference;
import org.columba.core.command.Worker;
import org.columba.mail.command.ComposerCommandReference;
import org.columba.mail.command.FolderCommand;
import org.columba.mail.composer.SendableMessage;
import org.columba.mail.config.AccountItem;
import org.columba.mail.folder.Folder;
import org.columba.mail.gui.composer.ComposerController;
import org.columba.mail.gui.table.TableChangedEvent;
import org.columba.mail.message.HeaderInterface;
import org.columba.main.MainInterface;

/**
 * @author freddy
 *
 * To change this generated comment edit the template variable "typecomment":
 * Window>Preferences>Java>Templates.
 * To enable and disable the creation of type comments go to
 * Window>Preferences>Java>Code Generation.
 */
public class SaveMessageCommand extends FolderCommand {

	protected Folder folder;
	protected HeaderInterface[] headerList = new HeaderInterface[1];

	/**
	 * Constructor for SaveMessageCommand.
	 * @param frameController
	 * @param references
	 */
	public SaveMessageCommand(DefaultCommandReference[] references) {
		super(references);
	}

	public void updateGUI() throws Exception {

		TableChangedEvent ev =
			new TableChangedEvent(TableChangedEvent.ADD, folder, headerList);

		MainInterface.frameModel.tableChanged(ev);

		MainInterface.treeModel.nodeChanged(folder);
	}

	/**
	 * @see org.columba.core.command.Command#execute(Worker)
	 */
	public void execute(Worker worker) throws Exception {

		ComposerCommandReference[] r =
			(ComposerCommandReference[]) getReferences();

		ComposerController composerController = r[0].getComposerController();

		AccountItem item = composerController.getModel().getAccountItem();

		SendableMessage message =
			composerController.composerInterface.messageComposer.compose(worker);

		folder = (Folder) r[0].getFolder();

		Object uid = folder.addMessage(message, worker);

		// we need this to reflect changes in table-widget
		// -> this is cached in folder anyway, so actually
		// -> we just get the HeaderInterface from a Hashtable
		headerList[0] = folder.getMessageHeader(uid, worker);
	}

}