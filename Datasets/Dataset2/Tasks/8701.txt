import org.columba.core.main.MainInterface;

package org.columba.mail.gui.frame;

import java.util.Enumeration;
import java.util.Hashtable;

import org.columba.core.config.Config;
import org.columba.core.config.ViewItem;
import org.columba.core.xml.XmlElement;
import org.columba.mail.config.MailConfig;
import org.columba.mail.folder.FolderTreeNode;
import org.columba.mail.folder.imap.IMAPFolder;
import org.columba.mail.folder.mh.CachedMHFolder;
import org.columba.mail.folder.outbox.OutboxFolder;
import org.columba.mail.gui.table.TableChangedEvent;
import org.columba.main.MainInterface;

/**
 * @author freddy
 *
 * To change this generated comment edit the template variable "typecomment":
 * Window>Preferences>Java>Templates.
 * To enable and disable the creation of type comments go to
 * Window>Preferences>Java>Code Generation.
 */
public class FrameModel {

	private Hashtable controllers;

	protected XmlElement viewList;

	protected int nextId = 0;

	public FrameModel() {

		controllers = new Hashtable();

		viewList =
			MailConfig.get("mainframeoptions").getElement(
				"/options/gui/viewlist");

		for (int i = 0; i < viewList.count(); i++) {
			XmlElement view = viewList.getElement(i);
			String id = view.getAttribute("id");

			MailFrameController c = new MailFrameController(id);
			c.getView().loadWindowPosition(new ViewItem(view));
			c.getView().setVisible(true);
			register(id, c);

			nextId = Integer.parseInt(id) + 1;
		}
	}

	public void openView() {
		int id = nextId++;

		MailFrameController c =
			new MailFrameController(new Integer(id).toString());
		c.getView().setVisible(true);
		//c.getView().loadWindowPosition(new ViewItem(child));

		register(new Integer(id).toString(), c);
	}
	/**
	 * Registers the View
	 * @param view
	 */
	public void register(String id, MailFrameController controller) {
		controllers.put(id, controller);
	}

	protected void ensureViewConfigurationExists(String key) {
		XmlElement child = getChild(new Integer(key).toString());
		if (child == null) {
			// create new node
			child = new XmlElement("view");
			child.addAttribute("id", new Integer(key).toString());
			XmlElement window = new XmlElement("window");
			window.addAttribute("x", "0");
			window.addAttribute("y", "0");
			window.addAttribute("width", "900");
			window.addAttribute("height", "700");
			window.addAttribute("maximized", "true");
			child.addElement(window);
			XmlElement toolbars = new XmlElement("toolbars");
			toolbars.addAttribute("show_main", "true");
			toolbars.addAttribute("show_filter", "true");
			toolbars.addAttribute("show_folderinfo", "true");
			child.addElement(toolbars);
			XmlElement splitpanes = new XmlElement("splitpanes");
			splitpanes.addAttribute("main", "200");
			splitpanes.addAttribute("header", "200");
			splitpanes.addAttribute("attachment", "100");
			child.addElement(splitpanes);

			viewList.addElement(child);

		}
	}

	public void close() {

		viewList.removeAllElements();

		for (Enumeration e = controllers.keys(); e.hasMoreElements();) {
			String key = (String) e.nextElement();

			MailFrameController frame =
				(MailFrameController) controllers.get(key);

			ensureViewConfigurationExists(key);

			controllers.remove(key);
		}
		
		saveAndExit();
	}

	protected void saveAndExit() {
		try {
			Config.save();
		} catch (Exception ex) {
			ex.printStackTrace();
		}
		MainInterface.popServerCollection.saveAll();

		saveAllFolders();

		System.exit(0);
	}

	/**
	 * Unregister the View from the Model
	 * @param view
	 * @return boolean true if there are no more views for the model
	 */
	public void unregister(String id) {

		MailFrameController controller =
			(MailFrameController) controllers.get(id);

		if (controllers.size() == 1) {
			// last window closed
			//  close application

			viewList.removeAllElements();

			ensureViewConfigurationExists(id);

			saveWindowPosition(id);

			controllers.remove(id);

			saveAndExit();

		} else {
			controllers.remove(id);
		}
	}

	protected XmlElement getChild(String id) {
		for (int i = 0; i < viewList.count(); i++) {
			XmlElement view = viewList.getElement(i);
			String str = view.getAttribute("id");

			if (str.equals(id))
				return view;
		}
		return null;
	}

	public void saveWindowPosition(String id) {
		XmlElement child = getChild(id);

		MailFrameController frame = (MailFrameController) controllers.get(id);
		frame.getView().saveWindowPosition(new ViewItem(child));
	}

	public void saveAllFolders() {
		FolderTreeNode rootFolder =
			(FolderTreeNode) MainInterface.treeModel.getRoot();

		saveFolder(rootFolder);
	}

	public void saveFolder(FolderTreeNode parentFolder) {

		int count = parentFolder.getChildCount();
		FolderTreeNode child;
		FolderTreeNode folder;

		for (Enumeration e = parentFolder.children(); e.hasMoreElements();) {

			child = (FolderTreeNode) e.nextElement();

			if (child instanceof CachedMHFolder) {
				CachedMHFolder mhFolder = (CachedMHFolder) child;
				try {
					mhFolder.save();
				} catch (Exception ex) {
					ex.printStackTrace();
				}
			} else if (child instanceof OutboxFolder) {
				OutboxFolder outboxFolder = (OutboxFolder) child;
				try {
					outboxFolder.save();
				} catch (Exception ex) {
					ex.printStackTrace();
				}
			} else if (child instanceof IMAPFolder) {
				IMAPFolder imapFolder = (IMAPFolder) child;

				try {
					imapFolder.save();
				} catch (Exception ex) {
					ex.printStackTrace();
				}
			}

			saveFolder(child);
		}
	}

	public void tableChanged(TableChangedEvent ev) throws Exception {
		for (Enumeration e = controllers.keys(); e.hasMoreElements();) {
			String key = (String) e.nextElement();

			MailFrameController frame =
				(MailFrameController) controllers.get(key);
			frame.tableController.tableChanged(ev);
		}

	}

	public void updatePop3Menu() {
		for (Enumeration e = controllers.keys(); e.hasMoreElements();) {
			String key = (String) e.nextElement();

			MailFrameController frame =
				(MailFrameController) controllers.get(key);
			frame.getMenu().updatePopServerMenu();
		}
	}

}