int totalMessageCount = server.getMessageCount(worker);

package org.columba.mail.pop3;

import java.net.URL;
import java.util.Vector;

import org.columba.core.command.Command;
import org.columba.core.command.CommandCancelledException;
import org.columba.core.command.DefaultCommandReference;
import org.columba.core.command.Worker;
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

	public CheckForNewMessagesCommand(DefaultCommandReference[] references) {
		super(references);
	}

	/**
	 * @see org.columba.core.command.Command#execute(Worker)
	 */
	public void execute(Worker worker) throws Exception {

		FetchNewMessagesCommand command =
			new FetchNewMessagesCommand( getReferences());

		POP3CommandReference[] r =
			(POP3CommandReference[]) getReferences(FIRST_EXECUTION);

		server = r[0].getServer();

		command.log("Authenticating...", worker);

		int totalMessageCount = server.getMessageCount();

		try {
			Vector newUIDList = command.fetchUIDList(totalMessageCount, worker);

			Vector messageSizeList = command.fetchMessageSizes(worker);

			Vector newMessagesUIDList = command.synchronize(newUIDList);

			int newMessagesCount = newMessagesUIDList.size();
			if ((newMessagesCount > 0)
				&& (server
					.getAccountItem()
					.getPopItem()
					.getBoolean("enable_sound")))
				playSound();

			if (server
				.getAccountItem()
				.getPopItem()
				.getBoolean("automatically_download_new_messages"))
				command.downloadNewMessages(
					newUIDList,
					messageSizeList,
					newMessagesUIDList,
					worker);

			command.logout(worker);

		} catch (CommandCancelledException e) {
			server.forceLogout();
		}
	}

	protected void playSound() {

		AccountItem item = server.getAccountItem();
		PopItem popItem = item.getPopItem();
		String file = popItem.get("sound_file");

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