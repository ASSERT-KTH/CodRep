public void updateSelectedGUI() throws Exception {

package org.columba.mail.pop3;

import java.util.Vector;

import org.columba.core.command.Command;
import org.columba.core.command.CompoundCommand;
import org.columba.core.command.DefaultCommandReference;
import org.columba.core.command.Worker;
import org.columba.core.gui.FrameController;
import org.columba.core.logging.ColumbaLogger;
import org.columba.main.MainInterface;
import org.columba.mail.command.POP3CommandReference;
import org.columba.mail.filter.Filter;
import org.columba.mail.filter.FilterList;
import org.columba.mail.folder.Folder;
import org.columba.mail.gui.frame.MailFrameController;
import org.columba.mail.gui.table.TableChangedEvent;
import org.columba.mail.message.HeaderInterface;
import org.columba.mail.message.Message;

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

	/**
	 * Constructor for FetchNewMessages.
	 * @param frameController
	 * @param references
	 */
	public FetchNewMessagesCommand(
		FrameController frameController,
		DefaultCommandReference[] references) {
		super(frameController, references);
		
		POP3CommandReference[] r =
			(POP3CommandReference[]) getReferences(FIRST_EXECUTION);

		server = r[0].getServer();
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
		POP3CommandReference[] r =
			(POP3CommandReference[]) getReferences(FIRST_EXECUTION);

		server = r[0].getServer();

		Vector newUIDList = fetchUIDList();
		
		Vector messageSizeList = fetchMessageSizes();
		

		Vector newMessagesUIDList = synchronize( newUIDList);
		

		downloadNewMessage( newUIDList, messageSizeList, newMessagesUIDList, worker );
	

		logout();
		
		

	}
	
	public void downloadNewMessage( Vector newUIDList, Vector messageSizeList, Vector newMessagesUIDList, Worker worker ) throws Exception
	{
		ColumbaLogger.log.info(
			"need to fetch " + newMessagesUIDList.size() + " messages.");	
			
		for (int i = 0; i < newMessagesUIDList.size(); i++) {
			Object serverUID = newMessagesUIDList.get(i);

			ColumbaLogger.log.info("fetch message with UID=" + serverUID);

			//int index = ( (Integer) result.get(serverUID) ).intValue();
			int index = newUIDList.indexOf(serverUID);
			ColumbaLogger.log.info(
				"vector index=" + index + " server index=" + (index + 1));

			int size = Integer.parseInt((String) messageSizeList.get(index));
			size = Math.round(size / 1024);

			if ( server.getAccountItem().getPopItem().isLimit() )
			{
				// check if message isn't too big to download
				int maxSize = Integer.parseInt(server.getAccountItem().getPopItem().getLimit());
				
				// if message-size is bigger skip download of this message
				if ( size > maxSize ) 
				{
					ColumbaLogger.log.info(
					"skipping download of message, too big");
					continue;
				}
			}
			// server message numbers start with 1
			// whereas Vector numbers start with 0
			//  -> always increase fetch number
			Message message = server.getMessage(index + 1, serverUID);
			message.getHeader().set("columba.size", new Integer(size));

			//System.out.println("message:\n" + message.getSource());

			// get inbox-folder from pop3-server preferences
			Folder inboxFolder = server.getFolder();
			Object uid = inboxFolder.addMessage(message, worker);
			Object[] uids = new Object[1];
			uids[0] = uid;
			
			HeaderInterface[] headerList = new HeaderInterface[1];
			headerList[0] = message.getHeader();
			headerList[0].set("columba.uid",uid);
			
			TableChangedEvent ev = new TableChangedEvent( TableChangedEvent.ADD, inboxFolder, headerList);
		 
			((MailFrameController)frameController).tableController.tableChanged(ev);
		
			

			FilterList list = inboxFolder.getFilterList();
			for (int j = 0; j < list.count(); j++) {
				Filter filter = list.get(j);

				Object[] result =
					inboxFolder.searchMessages(filter, uids, worker);
				if (result.length != 0) {
					CompoundCommand command =
						filter.getCommand(frameController, inboxFolder, result);

					MainInterface.processor.addOp(command);
				}
				
			}
			

		}
	}
	
	public Vector synchronize( Vector newUIDList ) throws Exception
	{
		ColumbaLogger.log.info(
			"synchronize local UID-list with remote UID-list");
		// synchronize local UID-list with server 		
		Vector newMessagesUIDList = server.synchronize(newUIDList);
		
		
		return newMessagesUIDList;
	}
	
	public Vector fetchMessageSizes() throws Exception
	{
		// fetch message-size list 		
		Vector messageSizeList = server.getMessageSizeList();
		ColumbaLogger.log.info(
			"fetched message-size-list capacity=" + messageSizeList.size());
		return messageSizeList;
		
	}
	
	public Vector fetchUIDList() throws Exception
	{
		// fetch UID list 		
		Vector newUIDList = server.getUIDList();
		ColumbaLogger.log.info(
			"fetched UID-list capacity=" + newUIDList.size());
			
		return newUIDList;
	}
	

	public void logout() throws Exception
	{
		server.logout();

		ColumbaLogger.log.info("logout");
	}
}