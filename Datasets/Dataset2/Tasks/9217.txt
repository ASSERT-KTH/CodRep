implements TableOwner {

/*
 * Created on Jun 10, 2003
 *
 * To change the template for this generated file go to
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
package org.columba.mail.gui.frame;

import java.awt.event.KeyEvent;

import javax.swing.KeyStroke;

import org.columba.core.config.ViewItem;
import org.columba.core.gui.frame.AbstractFrameView;
import org.columba.core.gui.util.DialogStore;
import org.columba.core.main.MainInterface;
import org.columba.mail.gui.attachment.AttachmentSelectionHandler;
import org.columba.mail.gui.composer.HeaderController;
import org.columba.mail.gui.infopanel.FolderInfoPanel;
import org.columba.mail.gui.table.FilterToolbar;
import org.columba.mail.gui.table.TableController;
import org.columba.mail.gui.table.action.DownAction;
import org.columba.mail.gui.table.action.UpAction;
import org.columba.mail.gui.table.selection.TableSelectionHandler;
import org.columba.mail.gui.tree.TreeController;
import org.columba.mail.gui.tree.selection.TreeSelectionHandler;

/**
 *
 *  Mail frame controller which contains a tree, table and a message
 *  viewer.
 *
 *  @author fdietz
 * 
 */
public class ThreePaneMailFrameController
	extends AbstractMailFrameController
	implements TableOwnerInterface {

	public TreeController treeController;
	public TableController tableController;

	public HeaderController headerController;
	public FilterToolbar filterToolbar;

	public FolderInfoPanel folderInfoPanel;

	/**
	 * @param viewItem
	 */
	public ThreePaneMailFrameController(ViewItem viewItem) {
		super("ThreePaneMail", viewItem);

		TableUpdater.add(this);

	}

	protected void initActions() {

		tableController.getView().getInputMap().put(
			KeyStroke.getKeyStroke(KeyEvent.VK_UP, 0),
			"UP");
		UpAction upAction = new UpAction(this);
		tableController.getView().getActionMap().put("UP", upAction);

		tableController.getView().getInputMap().put(
			KeyStroke.getKeyStroke(KeyEvent.VK_DOWN, 0),
			"DOWN");
		DownAction downAction = new DownAction(this);
		tableController.getView().getActionMap().put("DOWN", downAction);
		//register the markasread timer as selection listener
		tableController
			.getMailFrameController()
			.registerTableSelectionListener(
			tableController.getMarkAsReadTimer());
	}

	public AbstractFrameView createView() {

		MailFrameView view = new MailFrameView(this);

		view.setFolderInfoPanel(folderInfoPanel);

		view.init(
			treeController.getView(),
			tableController.getView(),
			filterToolbar,
			messageController.getView(),
			statusBar);

		//view.pack();

		return view;
	}

	/**
	 * Save window properties and close the window.
	 */
	public void close() {
		tableController.saveColumnConfig();
		super.close(); // this saves view settings and closes the view
	}

	protected void init() {
		super.init();

		treeController = new TreeController(this, MainInterface.treeModel);

		tableController = new TableController(this);

		folderInfoPanel = new FolderInfoPanel();
		//treeController.getTreeSelectionManager().addFolderSelectionListener(folderInfoPanel);

		filterToolbar = new FilterToolbar(tableController);

		new DialogStore((MailFrameView) view);

		// create selection handlers
		TableSelectionHandler tableHandler =
			new TableSelectionHandler(tableController.getView());
		getSelectionManager().addSelectionHandler(tableHandler);

		TreeSelectionHandler treeHandler =
			new TreeSelectionHandler(treeController.getView());
		getSelectionManager().addSelectionHandler(treeHandler);

		getSelectionManager().addSelectionHandler(
			new AttachmentSelectionHandler(attachmentController.getView()));

		/*
		treeController.getTreeSelectionManager().registerSelectionListener(""
			tableController.getTableSelectionManager());
		*/
		
		tableController.createPopupMenu();
		treeController.createPopupMenu();
		attachmentController.createPopupMenu();

		initActions();

	}

	/* *20030831, karlpeder* Not used, close method is used instead
	public void saveAndClose() {
		tableController.saveColumnConfig();
		super.saveAndClose();
	}
	*/

	/* (non-Javadoc)
	 * @see org.columba.mail.gui.frame.AbstractMailFrameController#hasTable()
	 */
	public boolean hasTable() {
		return true;
	}

	/* (non-Javadoc)
	 * @see org.columba.mail.gui.frame.ViewHeaderListInterface#getTableController()
	 */
	public TableController getTableController() {
		return tableController;
	}

}