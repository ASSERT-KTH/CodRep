public static void add(TableOwner frameController) {

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
package org.columba.mail.gui.frame;

import java.util.Iterator;
import java.util.List;
import java.util.Vector;

import org.columba.mail.gui.table.model.TableModelChangedEvent;

/**
 * Sends update event to {@link TableController}.
 * <p>
 * Don't call <code>tableController.tableChanged(ev)</code> directly.
 * <p>
 * All commands use this static object to notify that the table model
 * has changed.
 * 
 *
 * @author fdietz
 */
public class TableUpdater {

	/**
	 * Listeners list
	 */
	protected static List list = new Vector();

	/**
	 * Notify all tables that the table model has changed.
	 * 
	 * @param ev			event  
	 * @throws Exception
	 */
	public static void tableChanged(TableModelChangedEvent ev)
		throws Exception {
		for (Iterator it = list.iterator(); it.hasNext();) {
			AbstractMailFrameController frame =
				(AbstractMailFrameController) it.next();
			(
				(
					ThreePaneMailFrameController) frame)
						.tableController
						.tableChanged(
				ev);
		}

	}

	/**
	 * Add listener.
	 * 
	 * @param frameController		frame controller with table component
	 */
	public static void add(TableOwnerInterface frameController) {
		list.add(frameController);
	}

}