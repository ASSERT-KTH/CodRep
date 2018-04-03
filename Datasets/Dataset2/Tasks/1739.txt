public void updateSelectedGUI() throws Exception {

package org.columba.mail.smtp;

import java.util.Vector;

import org.columba.core.command.DefaultCommandReference;
import org.columba.core.command.Worker;
import org.columba.core.gui.FrameController;
import org.columba.main.MainInterface;
import org.columba.mail.command.FolderCommand;
import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.composer.SendableMessage;
import org.columba.mail.config.AccountItem;
import org.columba.mail.config.MailConfig;
import org.columba.mail.folder.Folder;
import org.columba.mail.folder.command.MoveMessageCommand;
import org.columba.mail.folder.outbox.OutboxFolder;
import org.columba.mail.folder.outbox.SendListManager;

/**
 * @author freddy
 *
 * To change this generated comment edit the template variable "typecomment":
 * Window>Preferences>Java>Templates.
 * To enable and disable the creation of type comments go to
 * Window>Preferences>Java>Code Generation.
 */
public class SendAllMessagesCommand extends FolderCommand {

	protected SendListManager sendListManager = new SendListManager();
	protected OutboxFolder outboxFolder;

	/**
	 * Constructor for SendAllMessagesCommand.
	 * @param frameController
	 * @param references
	 */
	public SendAllMessagesCommand(
		FrameController frameController,
		DefaultCommandReference[] references) {
		super(frameController, references);
	}

	/**
	 * @see org.columba.core.command.Command#updateGUI()
	 */
	public void updateGUI() throws Exception {
	}

	/**
	 * @see org.columba.core.command.Command#execute(Worker)
	 */
	public void execute(Worker worker) throws Exception {
		FolderCommandReference[] r = (FolderCommandReference[]) getReferences();

		outboxFolder = (OutboxFolder) r[0].getFolder();

		Object[] uids = outboxFolder.getUids(worker);

		for (int i = 0; i < uids.length; i++) {
			if (outboxFolder.exists(uids[i]) == true) {
				SendableMessage message =
					(SendableMessage) outboxFolder.getMessage(uids[i], worker);
				sendListManager.add(message);

			}
		}

		int actAccountUid = -1;
		Vector sentList = new Vector();
		boolean open = false;
		SMTPServer smtpServer = null;
		Folder sentFolder = null;
		while (sendListManager.hasMoreMessages()) {
			SendableMessage message = sendListManager.getNextMessage();

			if (message.getAccountUid() != actAccountUid) {

				if (sentList.size() != 0) {

					sentList.clear();
				}

				actAccountUid = message.getAccountUid();

				AccountItem accountItem =
					MailConfig
						.getAccountList()
						.uidGet(actAccountUid);

				sentFolder =
					(Folder) MainInterface.treeModel.getFolder(
						Integer.parseInt(
							accountItem.getSpecialFoldersItem().getSent()));
				smtpServer = new SMTPServer(accountItem);

				open = smtpServer.openConnection();

			}

			if (open) {
				smtpServer.sendMessage(message);

				sentList.add(message.getHeader().get("columba.uid") );

			}
		}

		if (sentList.size() > 0) {
			moveToSentFolder(sentList, sentFolder);

		}
	}

	protected void moveToSentFolder(Vector v, Folder sentFolder) {
		FolderCommandReference[] r = new FolderCommandReference[2];
			r[0] = new FolderCommandReference(outboxFolder, v.toArray() );
			r[1] = new FolderCommandReference(sentFolder);

			MoveMessageCommand c = new MoveMessageCommand(frameController, r);

			MainInterface.processor.addOp(c);
		
	}

}