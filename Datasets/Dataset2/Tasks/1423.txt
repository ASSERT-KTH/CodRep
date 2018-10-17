import org.columba.core.gui.selection.SelectionChangedEvent;

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

package org.columba.mail.gui.table;

import org.columba.core.gui.util.SelectionChangedEvent;
import org.columba.mail.folder.Folder;

public class TableSelectionChangedEvent extends SelectionChangedEvent {

	private Folder folder;
	private Object[] uids;

	public TableSelectionChangedEvent( Folder folder, Object[] uids) {
		this.folder = folder;
		this.uids = uids;
	}

	/**
	 * @return Folder
	 */
	public Folder getFolder() {
		return folder;
	}

	/**
	 * @return Object[]
	 */
	public Object[] getUids() {
		return uids;
	}

}