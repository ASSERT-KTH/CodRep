import org.columba.core.main.MainInterface;

// This program is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation; either version 2 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Library General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program; if not, write to the Free Software
// Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

package org.columba.addressbook.main;

import org.columba.core.command.TaskManager;
import org.columba.main.MainInterface;
import org.columba.addressbook.gui.frame.AddressbookView;
import org.columba.addressbook.util.AddressbookResourceLoader;

/**
 * @author frd
 *
 * To change this generated comment edit the template variable "typecomment":
 * Window>Preferences>Java>Templates.
 * To enable and disable the creation of type comments go to
 * Window>Preferences>Java>Code Generation.
 */
public class AddressbookMain {

	public static void main(String[] args) {
		new AddressbookResourceLoader();
		
		MainInterface.addressbookInterface.taskManager = new TaskManager();
		MainInterface.addressbookInterface.frame =
					new AddressbookView();
		//new AddressbookFrame();
	}
}