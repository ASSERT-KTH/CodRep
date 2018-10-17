import org.columba.core.gui.frame.FrameController;

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
package org.columba.mail.gui.message.command;

import org.columba.core.command.Command;
import org.columba.core.command.DefaultCommandReference;
import org.columba.core.command.Worker;
import org.columba.core.command.WorkerStatusController;
import org.columba.core.gui.FrameController;
import org.columba.core.xml.XmlElement;
import org.columba.mail.command.FolderCommand;
import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.config.MailConfig;
import org.columba.mail.folder.Folder;
import org.columba.mail.gui.frame.MailFrameController;
import org.columba.mail.message.HeaderInterface;
import org.columba.mail.message.MimePart;
import org.columba.mail.message.MimePartTree;

/**
 * @author Timo Stich (tstich@users.sourceforge.net)
 * 
 */
public class ViewMessageCommand extends FolderCommand {

	MimePart bodyPart;
	MimePartTree mimePartTree;
	HeaderInterface header;
	Folder folder;
	Object uid;

	/**
	 * Constructor for ViewMessageCommand.
	 * @param references
	 */
	public ViewMessageCommand(
		FrameController frame,
		DefaultCommandReference[] references) {
		super(frame, references);

		priority = Command.REALTIME_PRIORITY;
		commandType = Command.NORMAL_OPERATION;
	}

	private void getData(
		Folder srcFolder,
		Object uid,
		WorkerStatusController wsc)
		throws Exception {

		this.uid = uid;
		bodyPart = null;

		//AbstractMessage message = srcFolder.getMessage(uid, wsc);
		//header = message.getHeader();
		header = srcFolder.getMessageHeader(uid, wsc);

		mimePartTree = srcFolder.getMimePartTree(uid, wsc);

		// FIXME
		/*
		boolean viewhtml =
			MailConfig
				.getMainFrameOptionsConfig()
				.getWindowItem()
				.getHtmlViewer();
		*/

		
		XmlElement html =
			MailConfig.getMainFrameOptionsConfig().getRoot().getElement(
				"/options/html");
		boolean viewhtml =
			new Boolean(html.getAttribute("prefer")).booleanValue();
		
		//boolean viewhtml = true;
		// Which Bodypart shall be shown? (html/plain)

		if (viewhtml)
			bodyPart = mimePartTree.getFirstTextPart("html");
		else
			bodyPart = mimePartTree.getFirstTextPart("plain");

		if (bodyPart == null) {
			bodyPart = new MimePart();
			bodyPart.setBody(new String("<No Message-Text>"));
		} else
			bodyPart = srcFolder.getMimePart(uid, bodyPart.getAddress(), wsc);

	}

	/**
	 * @see org.columba.core.command.Command#updateGUI()
	 */
	public void updateGUI() throws Exception {

		/*
		boolean hasAttachments = false;
		
		if ((mimePartTree.count() > 1)
			|| (!mimePartTree.get(0).getHeader().contentType.equals("text"))) {
			hasAttachments = true;
		*/
			((MailFrameController) frameController)
						.messageController
						.showMessage(
				header,
				bodyPart,
				mimePartTree);

			/*
			if ((mimePartTree.count() > 1)
				|| (!mimePartTree.get(0).getHeader().contentType.equals("text"))) {
				(
					(
						MailFrameController) frameController)
							.attachmentController
							.setMimePartTree(
					mimePartTree);
			
			} else
				(
					(
						MailFrameController) frameController)
							.attachmentController
							.setMimePartTree(
					null);
			*/
			if (header.getFlags().getSeen() == false) {
				((MailFrameController) frameController)
					.tableController
					.getMarkAsReadTimer()
					.restart((FolderCommandReference)getReferences()[0]);
			}

		}

		/**
		 * @see org.columba.core.command.Command#execute(Worker)
		 */
		public void execute(Worker worker) throws Exception {
			FolderCommandReference[] r =
				(FolderCommandReference[]) getReferences();
			getData((Folder) r[0].getFolder(), r[0].getUids()[0], worker);
		}

	}