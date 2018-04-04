Iterator<IFolder> it = folderFacade.getFolderIterator().listIterator();

// The contents of this file are subject to the Mozilla Public License Version
// 1.1
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
//The Initial Developers of the Original Code are Frederik Dietz and Timo
// Stich.
//Portions created by Frederik Dietz and Timo Stich are Copyright (C) 2003.
//
//All Rights Reserved.
package org.columba.mail.gui.composer.contact;

import java.awt.Component;
import java.util.Iterator;

import javax.swing.DefaultListCellRenderer;
import javax.swing.JComboBox;
import javax.swing.JList;

import org.columba.addressbook.facade.IFolderFacade;
import org.columba.addressbook.folder.IFolder;
import org.columba.api.exception.ServiceNotFoundException;
import org.columba.mail.connector.ServiceConnector;

public class FolderComboBox extends JComboBox {

	public FolderComboBox() {
		super();

		IFolderFacade folderFacade = null;
		try {
			folderFacade = ServiceConnector.getFolderFacade();
			Iterator<IFolder> it = folderFacade.getFolderIterator();

			while (it.hasNext()) {
				addItem(it.next());
			}

		} catch (ServiceNotFoundException e) {
			e.printStackTrace();
		}

		setRenderer(new MyListCellRenderer());
	}

	class MyListCellRenderer extends DefaultListCellRenderer {

		MyListCellRenderer() {

		}

		/**
		 * @see javax.swing.DefaultListCellRenderer#getListCellRendererComponent(javax.swing.JList,
		 *      java.lang.Object, int, boolean, boolean)
		 */
		@Override
		public Component getListCellRendererComponent(JList list, Object value,
				int index, boolean isSelected, boolean cellHasFocus) {

			super.getListCellRendererComponent(list, value, index, isSelected,
					cellHasFocus);

			IFolder folder = (IFolder) value;

			setText(folder.getName());
			setIcon(folder.getIcon());

			return this;
		}

	}
}