import org.columba.core.main.MainInterface;

package org.columba.mail.pop3;

import java.util.Vector;

import org.columba.core.command.Command;
import org.columba.core.command.CommandCancelledException;
import org.columba.core.command.CompoundCommand;
import org.columba.core.command.DefaultCommandReference;
import org.columba.core.command.Worker;
import org.columba.core.command.WorkerStatusController;
import org.columba.core.logging.ColumbaLogger;
import org.columba.mail.command.POP3CommandReference;
import org.columba.mail.filter.Filter;
import org.columba.mail.filter.FilterList;
import org.columba.mail.folder.Folder;
import org.columba.mail.gui.frame.MailFrameController;
import org.columba.mail.gui.table.TableChangedEvent;
import org.columba.mail.message.HeaderInterface;
import org.columba.mail.message.Message;
import org.columba.main.MainInterface;

/**
 * @author freddy
 *
 * To change this generated comment edit the template variable "typecomment":
 * Window>Preferences>Java>Templates.
 * To enable and disable the creation of type comments go to
 * Window>Preferences>Java>Code Generation.
 */
public class FetchNewMessagesCommand extends Command {

	POP3Server server;
	int totalMessageCount;
	int newMessageCount;

	/**
	 * Constructor for FetchNewMessages.
	 * @param frameController
	 * @param references
	 */
	public FetchNewMessagesCommand(DefaultCommandReference[] references) {
		super(references);

		POP3CommandReference[] r =
			(POP3CommandReference[]) getReferences(FIRST_EXECUTION);

		server = r[0].getServer();
	}

	/**
	 * @see org.columba.core.command.Command#execute(Worker)
	 */
	public void execute(Worker worker) throws Exception {
		POP3CommandReference[] r =
			(POP3CommandReference[]) getReferences(FIRST_EXECUTION);

		server = r[0].getServer();

		log("Authenticating...", worker);

		totalMessageCount = server.getMessageCount();

		try {
			Vector newUIDList = fetchUIDList(totalMessageCount, worker);

			Vector messageSizeList = fetchMessageSizes(worker);

			Vector newMessagesUIDList = synchronize(newUIDList);

			downloadNewMessages(
				newUIDList,
				messageSizeList,
				newMessagesUIDList,
				worker);

			logout(worker);

		} catch (CommandCancelledException e) {
			server.forceLogout();
		}

	}

	protected void log(String message, WorkerStatusController worker) {
		worker.setDisplayText(server.getFolderName() + ": " + message);
	}

	public void downloadMessage(
		int index,
		int size,
		Object serverUID,
		Worker worker)
		throws Exception {
		// server message numbers start with 1
		// whereas Vector numbers start with 0
		//  -> always increase fetch number
		Message message = server.getMessage(index + 1, serverUID, worker);
		message.getHeader().set(
			"columba.size",
			new Integer(Math.round(size / 1024)));
		message.getHeader().set("columba.flags.seen", Boolean.FALSE);
		//System.out.println("message:\n" + message.getSource());

		// get inbox-folder from pop3-server preferences
		Folder inboxFolder = server.getFolder();
		Object uid = inboxFolder.addMessage(message, worker);
		Object[] uids = new Object[1];
		uids[0] = uid;

		HeaderInterface[] headerList = new HeaderInterface[1];
		headerList[0] = message.getHeader();
		headerList[0].set("columba.uid", uid);

		TableChangedEvent ev =
			new TableChangedEvent(
				TableChangedEvent.ADD,
				inboxFolder,
				headerList);

		MainInterface.frameModel.tableChanged(ev);

		FilterList list = inboxFolder.getFilterList();
		for (int j = 0; j < list.count(); j++) {
			Filter filter = list.get(j);

			Object[] result = inboxFolder.searchMessages(filter, uids, worker);
			if (result.length != 0) {
				CompoundCommand command =
					filter.getCommand(inboxFolder, result);

				MainInterface.processor.addOp(command);
			}

		}
	}

	protected int calculateTotalSize(
		Vector newUIDList,
		Vector messageSizeList,
		Vector newMessagesUIDList) {
		int totalSize = 0;

		for (int i = 0; i < newMessagesUIDList.size(); i++) {
			Object serverUID = newMessagesUIDList.get(i);

			//ColumbaLogger.log.info("fetch message with UID=" + serverUID);

			//int index = ( (Integer) result.get(serverUID) ).intValue();
			int index = newUIDList.indexOf(serverUID);
			//ColumbaLogger.log.info("vector index=" + index + " server index=" + (index + 1));

			int size = Integer.parseInt((String) messageSizeList.get(index));
			//size = Math.round(size / 1024);

			totalSize += size;
		}

		return totalSize;
	}

	public void downloadNewMessages(
		Vector newUIDList,
		Vector messageSizeList,
		Vector newMessagesUIDList,
		Worker worker)
		throws Exception {
		ColumbaLogger.log.info(
			"need to fetch " + newMessagesUIDList.size() + " messages.");

		int totalSize =
			calculateTotalSize(newUIDList, messageSizeList, newMessagesUIDList);

		worker.setProgressBarMaximum(totalSize);
		worker.setProgressBarValue(0);

		newMessageCount = newMessagesUIDList.size();
		for (int i = 0; i < newMessageCount; i++) {
			Object serverUID = newMessagesUIDList.get(i);

			ColumbaLogger.log.info("fetch message with UID=" + serverUID);

			log(
				"Fetching " + (i + 1) + "/" + newMessageCount + " messages...",
				worker);

			//int index = ( (Integer) result.get(serverUID) ).intValue();
			int index = newUIDList.indexOf(serverUID);
			ColumbaLogger.log.info(
				"vector index=" + index + " server index=" + (index + 1));

			int size = Integer.parseInt((String) messageSizeList.get(index));
			size = Math.round(size / 1024);

			if (server
				.getAccountItem()
				.getPopItem()
				.getBoolean("enable_limit")) {
				// check if message isn't too big to download
				int maxSize =
					server.getAccountItem().getPopItem().getInteger("limit");

				// if message-size is bigger skip download of this message
				if (size > maxSize) {
					ColumbaLogger.log.info(
						"skipping download of message, too big");
					continue;
				}
			}

			downloadMessage(
				index,
				Integer.parseInt((String) messageSizeList.get(index)),
				serverUID,
				worker);
		}

	}

	public Vector synchronize(Vector newUIDList) throws Exception {
		ColumbaLogger.log.info(
			"synchronize local UID-list with remote UID-list");
		// synchronize local UID-list with server 		
		Vector newMessagesUIDList = server.synchronize(newUIDList);

		return newMessagesUIDList;
	}

	public Vector fetchMessageSizes(WorkerStatusController worker)
		throws Exception {

		log("Fetching message size list...", worker);
		// fetch message-size list 		
		Vector messageSizeList = server.getMessageSizeList();
		ColumbaLogger.log.info(
			"fetched message-size-list capacity=" + messageSizeList.size());
		return messageSizeList;

	}

	public Vector fetchUIDList(
		int totalMessageCount,
		WorkerStatusController worker)
		throws Exception {
		// fetch UID list 

		log("Fetch UID list...", worker);

		Vector newUIDList = server.getUIDList(totalMessageCount, worker);
		ColumbaLogger.log.info(
			"fetched UID-list capacity=" + newUIDList.size());

		return newUIDList;
	}

	public void logout(WorkerStatusController worker) throws Exception {
		server.logout();

		ColumbaLogger.log.info("logout");

		log("Logout...", worker);

		if (newMessageCount == 0)
			log("No new messages on server", worker);
	}
}