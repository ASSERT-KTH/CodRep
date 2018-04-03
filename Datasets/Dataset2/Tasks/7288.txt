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

package org.columba.mail.pop3;

import java.util.ListIterator;

import org.columba.core.action.IMenu;
import org.columba.core.event.ModelChangeListener;
import org.columba.core.event.ModelChangedEvent;
import org.columba.core.gui.FrameController;
import org.columba.core.main.MainInterface;
import org.columba.mail.util.MailResourceLoader;

public class FetchMessageSubMenu extends IMenu implements ModelChangeListener {
	
	private POP3ServerCollection popServer;

	/**
	 * 
	 */
	public FetchMessageSubMenu(FrameController controller) {
		super(controller, MailResourceLoader.getString(
		"menu",
		"mainframe",
		"menu_file_checkmessage"));
		
		popServer = MainInterface.popServerCollection; 
		popServer.addModelListener(this);
		
		createMenu();
	}


	/* (non-Javadoc)
	 * @see org.columba.core.event.ModelChangeListener#modelChanged(org.columba.core.event.ModelChangedEvent)
	 */
	public void modelChanged(ModelChangedEvent e) {
		switch( e.getMode() ) {
			case  ModelChangedEvent.ADDED  : {				
				add( ((POP3ServerController)e.getData()).getCheckAction() );				
				break;
			}
			
			case ModelChangedEvent.REMOVED : {
				removeAll();				
				createMenu();
				
				break;
			}
		}
	}
	protected void createMenu() {
		ListIterator it = popServer.getServerIterator();
		while( it.hasNext() ) {
			add(((POP3ServerController)it.next()).getCheckAction());
		}
	}
	
}