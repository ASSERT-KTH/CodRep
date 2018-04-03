destFolder.addMessage(rawString);

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
package org.columba.mail.folder.mailboximport;

import java.io.File;
import java.io.FileNotFoundException;

import javax.swing.JOptionPane;

import org.columba.core.command.WorkerStatusController;
import org.columba.core.gui.util.ExceptionDialog;
import org.columba.core.gui.util.ImageLoader;
import org.columba.core.gui.util.NotifyDialog;
import org.columba.mail.folder.Folder;

public abstract class DefaultMailboxImporter {
	public static int TYPE_FILE = 0;
	public static int TYPE_DIRECTORY = 1;

	protected Folder destinationFolder;
	protected File[] sourceFiles;
	//protected TempFolder tempFolder;
	protected int counter;

	public DefaultMailboxImporter(
		Folder destinationFolder,
		File[] sourceFiles) {

		this.destinationFolder = destinationFolder;
		this.sourceFiles = sourceFiles;

		init();
	}

	public void init() {
		counter = 0;
		//tempFolder = new TempFolder();
	}

	/*********** overwrite the following methods **************************/

	/**
	 * overwrite this method to specify type
	 * the wizard dialog will open the correct file/directory dialog automatically
	 */
	public int getType() {
		return TYPE_FILE;
	}

	/**
	 * this method does all the import work
	 */
	public abstract void importMailboxFile(
		File file,
		WorkerStatusController worker,
		Folder destFolder)
		throws Exception;

	/**
	 * enter a description which will be shown
	 * to the user here
	 */
	public String getDescription() {
		return "";
	}

	/*********** intern methods (no need to overwrite these) ****************/

	public void setSourceFiles(File[] files) {
		this.sourceFiles = files;
	}

	/**
	 * set destination folder
	 */
	public void setDestinationFolder(Folder folder) {
		destinationFolder = folder;
	}

	/**
	 *  counter for successfully imported messages
	 */
	public int getCount() {
		return counter;
	}

	/**
	 *  this method calls your overwritten importMailbox(File)-method
	 *  and handles exceptions
	 */
	public void run(WorkerStatusController worker) {

		worker.setDisplayText("Importing messages...");

		importMailbox(worker);

		if (getCount() == 0) {
			NotifyDialog dialog = new NotifyDialog();
			dialog.showDialog(
				"Message import failed! No messages were added to your folder.\nThis means that the parser didn't throw any exception even if it didn't recognize the mailbox format or simple the messagebox didn't contain any messages.");

			return;
		} else if (getCount() > 0) {

			JOptionPane.showMessageDialog(
				null,
				"Message import was successfull!",
				"Information",
				JOptionPane.INFORMATION_MESSAGE,
				ImageLoader.getImageIcon("stock_dialog_info_48.png"));

		}

	}

	/**
	 * 
	 * Import all mailbox files in Columba
	 * 
	 * This method makes use of the importMailbox method
	 * you have to overwrite and simple iterates over all
	 * given files/directories
	 * 
	 * 
	 * @param worker
	 */
	public void importMailbox(WorkerStatusController worker) {
		File[] listing = getSourceFiles();

		for (int i = 0; i < listing.length; i++) {
			if (worker.cancelled())
				return;

			try {

				importMailboxFile(listing[i], worker, getDestinationFolder());
			} catch (Exception ex) {
				if (ex instanceof FileNotFoundException) {
					NotifyDialog dialog = new NotifyDialog();
					dialog.showDialog("Source File not found:");
				} else {
					ExceptionDialog dialog = new ExceptionDialog();
					dialog.showDialog(ex);
				}
			}

		}
	}

	/**
	 * use this method to save a message to the specified destination folder
	 */
	protected void saveMessage(
		String rawString,
		WorkerStatusController worker,
		Folder destFolder)
		throws Exception {
		destFolder.addMessage(rawString, worker);

		counter++;

		worker.setDisplayText("Importing messages: " + getCount());

	}

	/**
	 * @return Folder
	 */
	public Folder getDestinationFolder() {
		return destinationFolder;
	}

	/**
	 * @return File[]
	 */
	public File[] getSourceFiles() {
		return sourceFiles;
	}

}