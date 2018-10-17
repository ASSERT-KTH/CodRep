public void updateSelectedGUI() throws Exception {

package org.columba.mail.pop3;

import java.net.URL;
import java.util.Vector;

import org.columba.core.command.Command;
import org.columba.core.command.DefaultCommandReference;
import org.columba.core.command.Worker;
import org.columba.core.gui.FrameController;
import org.columba.core.logging.ColumbaLogger;
import org.columba.core.util.PlaySound;
import org.columba.mail.command.POP3CommandReference;
import org.columba.mail.config.AccountItem;
import org.columba.mail.config.PopItem;

/**
 * @author freddy
 *
 * To change this generated comment edit the template variable "typecomment":
 * Window>Preferences>Java>Templates.
 * To enable and disable the creation of type comments go to
 * Window>Preferences>Java>Code Generation.
 */
public class CheckForNewMessagesCommand extends Command {

	POP3Server server;

	public CheckForNewMessagesCommand(
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

		FetchNewMessagesCommand command =
			new FetchNewMessagesCommand(frameController, getReferences());

		POP3CommandReference[] r =
			(POP3CommandReference[]) getReferences(FIRST_EXECUTION);

		server = r[0].getServer();

		Vector newUIDList = command.fetchUIDList();

		Vector messageSizeList = command.fetchMessageSizes();

		Vector newMessagesUIDList = command.synchronize(newUIDList);

		int newMessagesCount = newMessagesUIDList.size();
		if ((newMessagesCount > 0)
			&& (server.getAccountItem().getPopItem().isPlaysound()))
			playSound();

		if (server.getAccountItem().getPopItem().isAutoDownload())
			command.downloadNewMessage(
				newUIDList,
				messageSizeList,
				newMessagesUIDList,
				worker);

		command.logout();
	}

	protected void playSound() {

		AccountItem item = server.getAccountItem();
		PopItem popItem = item.getPopItem();
		String file = popItem.getSoundfile();

		ColumbaLogger.log.info("playing sound file=" + file);

		if (file.equalsIgnoreCase("default")) {
			PlaySound.play("newmail.wav");
		} else {
			try {
				PlaySound.play(new URL(file));
			} catch (Exception ex) {
				ex.printStackTrace();
			}

		}
	}

}