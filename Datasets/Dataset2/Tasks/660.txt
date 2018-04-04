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

package org.columba.core.gui.statusbar;

import java.awt.event.ActionEvent;
import java.awt.event.KeyEvent;

import javax.swing.KeyStroke;

import org.columba.core.action.FrameAction;
import org.columba.core.gui.FrameController;
import org.columba.core.gui.statusbar.event.WorkerListChangeListener;
import org.columba.core.gui.statusbar.event.WorkerListChangedEvent;
import org.columba.core.gui.util.ImageLoader;
import org.columba.core.main.MainInterface;
import org.columba.mail.util.MailResourceLoader;

public class CancelAction extends FrameAction implements WorkerListChangeListener {

	public CancelAction(FrameController controller) {
		super(
			controller,
			MailResourceLoader.getString(
				"menu",
				"mainframe",
				"menu_file_cancel"),
			MailResourceLoader.getString(
				"menu",
				"mainframe",
				"menu_file_cancel"),
			"",
			"CANCEL_ACTION",
			ImageLoader.getSmallImageIcon("stock_stop-16.png"),
			ImageLoader.getImageIcon("stock_stop.png"),
			'0',
			KeyStroke.getKeyStroke(KeyEvent.VK_CANCEL, 0));
		setEnabled(false);
		MainInterface.processor.getTaskManager().addWorkerListChangeListener(this);
	}

	/* (non-Javadoc)
	 * @see java.awt.event.ActionListener#actionPerformed(java.awt.event.ActionEvent)
	 */
	public void actionPerformed(ActionEvent evt) {
		getFrameController().getStatusBar().cancelDisplayedWorker();
	}

	/* (non-Javadoc)
	 * @see org.columba.core.gui.statusbar.event.WorkerListChangeListener#workerListChanged(org.columba.core.gui.statusbar.event.WorkerListChangedEvent)
	 */
	public void workerListChanged(WorkerListChangedEvent e) {
		if( e.getNewValue() != 0) setEnabled(true);
		else setEnabled(false);
	}

}