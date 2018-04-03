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

package org.columba.mail.gui.util;

import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.net.URL;

import javax.swing.JMenuItem;
import javax.swing.JPopupMenu;

import org.columba.addressbook.folder.ContactCard;
import org.columba.addressbook.gui.tree.util.SelectAddressbookFolderDialog;
import org.columba.mail.gui.composer.ComposerController;
import org.columba.mail.gui.mimetype.MimeTypeViewer;
import org.columba.main.MainInterface;

public class URLController implements ActionListener {

	private String address;
	private URL link;

	public JPopupMenu createContactMenu(String contact) {
		JPopupMenu popup = new JPopupMenu();
		JMenuItem menuItem = new JMenuItem("Add Contact to Addressbook");
		menuItem.addActionListener(this);
		menuItem.setActionCommand("CONTACT");
		popup.add(menuItem);
		menuItem = new JMenuItem("Compose Message for " + contact);
		menuItem.setActionCommand("COMPOSE");
		menuItem.addActionListener(this);
		popup.add(menuItem);

		return popup;
	}

	public JPopupMenu createLinkMenu() {
		JPopupMenu popup = new JPopupMenu();
		JMenuItem menuItem = new JMenuItem("Open");
		menuItem.addActionListener(this);
		menuItem.setActionCommand("OPEN");
		popup.add(menuItem);
		menuItem = new JMenuItem("Open with...");
		menuItem.setActionCommand("OPEN_WITH");
		menuItem.addActionListener(this);
		popup.add(menuItem);
		popup.addSeparator();
		menuItem = new JMenuItem("Open with internal browser");
		menuItem.setActionCommand("OPEN_WITHINTERNALBROWSER");
		menuItem.addActionListener(this);
		popup.add(menuItem);

		return popup;
	}

	public void setAddress(String s) {
		this.address = s;
	}

	public String getAddress() {
		return address;
	}

	public URL getLink() {
		return link;
	}

	public void setLink(URL u) {
		this.link = u;
	}

	public void compose(String address) {
		ComposerController controller = new ComposerController();

		controller.getModel().setTo(address);

		controller.showComposerWindow();
	}

	public void contact(String address) {
		SelectAddressbookFolderDialog dialog =
			MainInterface
				.addressbookInterface
				.tree
				.getSelectAddressbookFolderDialog();

		org.columba.addressbook.folder.Folder selectedFolder =
			dialog.getSelectedFolder();

		if (selectedFolder == null)
			return;

		try {

			ContactCard card = new ContactCard();
			card.set("displayname", address);
			card.set("email", "internet", address);

			selectedFolder.add(card);

		} catch (Exception ex) {
			ex.printStackTrace();
		}
	}

	public JPopupMenu createMenu(URL url) {
		if (url.getProtocol().equalsIgnoreCase("mailto")) {
			// found email address

			setAddress(url.getFile());
			JPopupMenu menu = createContactMenu(url.getFile());
			return menu;

		} else {

			setLink(url);
			JPopupMenu menu = createLinkMenu();
			return menu;
		}
	}

	public void open(URL url) {
		MimeTypeViewer viewer = new MimeTypeViewer();
		viewer.openURL(url);
	}

	public void openWith(URL url) {
		MimeTypeViewer viewer = new MimeTypeViewer();
		viewer.openWithURL(url);
	}

	/*
	public void openWithBrowser(URL url) {
		MimeTypeViewer viewer = new MimeTypeViewer();
		viewer.openWithBrowserURL(url);
	}
	*/
	public void actionPerformed(ActionEvent e) {
		String action = e.getActionCommand();
		if (action.equals("COMPOSE")) {
			compose(getAddress());
		} else if (action.equals("CONTACT")) {
			contact(getAddress());
		} else if (action.equals("OPEN")) {
			open(getLink());
		} else if (action.equals("OPEN_WITH")) {
			openWith(getLink());
		} else if (action.equals("OPEN_WITHINTERNALBROWSER")) {
			//openWithBrowser(getLink());
		}
	}
}