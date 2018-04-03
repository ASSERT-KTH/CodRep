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

package org.columba.mail.gui.tree.action;

import org.columba.core.action.InternAction;
import org.columba.core.gui.FrameController;
import org.columba.core.gui.util.SelectionChangedEvent;
import org.columba.core.gui.util.SelectionListener;
import org.columba.core.main.MainInterface;
import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.gui.table.command.ViewHeaderListCommand;

public class ViewHeaderListAction extends InternAction implements SelectionListener {

	/**
	 * @param controller
	 */
	public ViewHeaderListAction(FrameController controller) {
		super(controller);
		
		controller.getSelectionManager().registerSelectionListener("mail.tree",this);
	}

	/* (non-Javadoc)
	 * @see org.columba.core.gui.util.SelectionListener#selectionChanged(org.columba.core.gui.util.SelectionChangedEvent)
	 */
	public void selectionChanged(SelectionChangedEvent e) {
		FolderCommandReference[] references  = (FolderCommandReference[]) getFrameController().getSelectionManager().getSelection("mail.tree");
		if( references.length == 1) {
			MainInterface.processor.addOp(
				new ViewHeaderListCommand(
					getFrameController(),references));
		
		}
	}

}