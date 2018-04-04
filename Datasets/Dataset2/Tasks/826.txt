public void updateSelectedGUI() throws Exception {

package org.columba.mail.pop3;

import org.columba.core.command.Command;
import org.columba.core.command.DefaultCommandReference;
import org.columba.core.command.Worker;
import org.columba.core.gui.FrameController;
import org.columba.mail.command.POP3CommandReference;

/**
 * @author freddy
 *
 * To change this generated comment edit the template variable "typecomment":
 * Window>Preferences>Java>Templates.
 * To enable and disable the creation of type comments go to
 * Window>Preferences>Java>Code Generation.
 */
public class FetchMessagesCommand extends Command {

	POP3Server server;
	Object[] uids;
	
	/**
	 * Constructor for FetchCommand.
	 * @param frameController
	 * @param references
	 */
	public FetchMessagesCommand(
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
		POP3CommandReference[] r = (POP3CommandReference[]) getReferences(FIRST_EXECUTION); 
		
		server = r[0].getServer();
		uids = r[0].getUids();
		
		//server.getMessages(uids);
	}

}